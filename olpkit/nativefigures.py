"""Native vector figures bound to editable source and the actual book preamble.

Adapted from the recovered Gujarati native-figure manifest approach. Source
matching and all recorded dependencies are mandatory; no guessed graph labels
or source-language literals are supplied by Python. Export is one guarded batch,
without copying the assembled tree or invoking a TeX engine per diagram.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

from .build import verify_assembly, log_checks
from .macrophases import COMMAND, group, mask_comments
from .process import TeXSlot, run_job, MEMORY_LIMIT, TEX_MUTEX
from .recorder import read_inputs, input_hashes
from .selective import definition_end, environment_end


def sha(data): return hashlib.sha256(data).hexdigest()


NATIVE_ENVIRONMENTS = ('tikzpicture', 'oltableau')


def extract_native_figures(text, environments=NATIVE_ENVIRONMENTS):
    """Keep definition bodies/verbatim opaque and exact active source slices."""
    if (not environments or len(set(environments))!=len(environments)
            or not set(environments)<=set(NATIVE_ENVIRONMENTS)):
        raise ValueError('unsupported native figure environments')
    code = mask_comments(text)
    rows = []
    pos = 0
    while pos < len(code):
        if code[pos] != '\\':
            pos += 1
            continue
        match = COMMAND.match(code, pos)
        start = pos
        pos = match.end()
        end = definition_end(code, start, pos, match[1])
        if end is not None:
            pos = end
            continue
        if match[1] in ('verb', 'Verb'):
            if code[pos:pos+1] == '*': pos += 1
            delimiter = code[pos:pos+1]
            end = code.find(delimiter, pos+1) if delimiter else -1
            if end < 0: raise ValueError('unclosed figure-stage verbatim')
            pos = end+1
            continue
        if match[1] != 'begin': continue
        env, at = group(code, pos)
        if env not in (*environments, 'verbatim', 'Verbatim', 'lstlisting', 'minted'): continue
        _, end = environment_end(code, at, env)
        if env in environments:
            source = text[start:end]
            rows.append({'index': len(rows)+1, 'char_start': start, 'char_end': end,
                         'line': text[:start].count('\n')+1,
                         'source_sha256': sha(source.encode('utf-8')), 'source_tex': source,
                         'environment':env})
        pos = end
    return rows


def extract_tikz(text):
    """Preserve the exact historical TikZ-only extraction contract."""
    return [{k:v for k,v in row.items() if k!='environment'}
            for row in extract_native_figures(text,('tikzpicture',))]


PREVIEW_BACKENDS = {'pdflatex': 'pdftex', 'xelatex': 'xetex'}


def figures_command(source, context_path, profile_path, output, *, resume=False):
    """Run the same source-bound native exporter for any configured edition."""
    folder=Path(source).resolve()
    profile_bytes=Path(profile_path).read_bytes()
    profile=json.loads(profile_bytes)
    if profile.get('schema')!='olpkit.native-figure-profile.v1':
        raise ValueError('unsupported native figure profile')
    context_bytes=Path(context_path).read_bytes()
    if sha(context_bytes)!=profile['context_sha256']:
        raise ValueError('native figure context changed')
    assembly_bytes=(folder/'ASSEMBLY.json').read_bytes()
    if sha(assembly_bytes)!=profile['assembly_sha256']:
        raise ValueError('native figure assembly changed')
    assembly=json.loads(assembly_bytes)
    driver=profile['driver']
    if driver not in assembly['files']:
        raise ValueError('native figure driver is not an assembled input')
    witnesses=[]
    for row in profile['witnesses']:
        path=Path(row['path']);data=path.read_bytes()
        if sha(data)!=row['sha256']:
            raise ValueError('native figure witness changed: '+path.name)
        witnesses.append({'path':str(path),'sha256':sha(data),'bytes':len(data)})
    if not witnesses or not profile.get('configuration_evidence'):
        raise ValueError('native figure configuration evidence is required')
    environments=profile['environments']
    # Validate before preparing an output folder, including unknown environments.
    text=context_bytes.decode('utf-8-sig')
    extract_native_figures(text,environments)
    epoch=profile['source_date_epoch']
    if type(epoch) is not int or epoch<0:
        raise ValueError('invalid native figure source date epoch')
    evidence={**profile['configuration_evidence'],'profile_sha256':sha(profile_bytes),
              'context_input_sha256':sha(context_bytes),'verified_witnesses':witnesses}
    result=export_native_figures(folder,assembly,text,driver,output,epoch=epoch,
        context_evidence=evidence,engine=profile['engine'],resume=resume,environments=tuple(environments))
    print(json.dumps({key:result.get(key) for key in ('status','tex_runs','mutex_acquired','pdf','error')}))
    return 0 if result['status']=='vectors_exported_pending_visual_and_semantic_checks' else 2


def export_native_figures(folder, assembly, source, driver, output, *, epoch, context_evidence,
                          engine='pdflatex', resume=False, environments=('tikzpicture',)):
    """Serialize one output directory; resume only a proven unstarted attempt."""
    if engine not in PREVIEW_BACKENDS:
        raise ValueError('unsupported native figure engine: '+engine)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    lock = output / '.olpkit-native-figures.lock'
    try:
        with lock.open('xb') as stream: stream.write(str(os.getpid()).encode())
    except FileExistsError:
        raise ValueError('another invocation owns this figure directory; do not restart it') from None
    try:
        return _export_native_figures(folder, assembly, source, driver, output,
                                      epoch=epoch, context_evidence=context_evidence,
                                      engine=engine, resume=resume,environments=environments)
    finally:
        lock.unlink()


def _export_native_figures(folder, assembly, source, driver, output, *, epoch, context_evidence, engine, resume,environments=('tikzpicture',)):
    """Export exact active native figures under a verified book configuration.

    context_evidence must identify the actual applied configuration and local
    definition comparison. Arbitrary unit-local macro execution is not inferred.
    Caller retains source context evidence and completes visual/accessibility QA.
    """
    folder = Path(folder).resolve()
    output = Path(output).resolve()
    native_driver = (folder / driver).resolve()
    if not native_driver.is_relative_to(folder): raise ValueError('driver outside assembled tree')
    if not context_evidence: raise ValueError('native figure context evidence is required')
    verify_assembly(folder, assembly)
    original = native_driver.read_text(encoding='utf-8-sig')
    if original.count(r'\begin{document}') != 1: raise ValueError('ambiguous native book preamble')
    figures = extract_tikz(source) if tuple(environments)==('tikzpicture',) else extract_native_figures(source,environments)
    if not figures: raise ValueError('no active native figures in selected environments')
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / 'NATIVE_FIGURES.json'
    if receipt_path.exists() and not resume:
        raise ValueError('preserve existing figure attempt; resume only an unstarted occupied slot')
    if resume and not receipt_path.is_file():
        raise ValueError('resume requires the previous occupied-slot receipt')
    preamble = original.split(r'\begin{document}', 1)[0]
    job = 'native-figures'
    backend = PREVIEW_BACKENDS[engine]
    batch = (preamble + '\n' + r'\usepackage[active,tightpage,' + backend + r']{preview}' + '\n' +
             '\n'.join(r'\PreviewEnvironment{'+env+'}' for env in environments) + '\n' + r'\setlength\PreviewBorder{2pt}' + '\n' +
             r'\begin{document}' + '\n' + '\n\n'.join(row['source_tex'] for row in figures) +
             '\n' + r'\end{document}' + '\n')
    tex = output / (job + '.tex')
    prepared = {tex.name: batch.encode('utf-8')}
    for row in figures:
        name = f'figure-{row["index"]:03d}.tex'
        prepared[name] = row['source_tex'].encode('utf-8')
        row['source_file'] = name
        del row['source_tex']
    result = {'schema': 'olpkit.native-figures.v1', 'status': 'prepared',
              'source_sha256': sha(source.encode('utf-8')), 'driver': driver,
              'driver_sha256': sha(native_driver.read_bytes()), 'preamble_sha256': sha(preamble.encode('utf-8')),
              'batch_sha256': sha(prepared[tex.name]), 'configuration_evidence': context_evidence,
              'source_date_epoch': epoch,
              'engine': engine, 'preview_backend': backend,
              'assembly_sha256': sha(json.dumps(assembly, sort_keys=True).encode('utf-8')),
              'figures': figures, 'mutex': TEX_MUTEX, 'mutex_acquired': False,
              'memory_limit_bytes': MEMORY_LIMIT, 'commands': [], 'tex_runs': 0,
              'visual_qa': 'pending', 'accessibility_descriptions': 'pending', 'publishable': False}
    if tuple(environments)!=('tikzpicture',):result['environments']=list(environments)
    if resume:
        original_receipt = receipt_path.read_bytes()
        previous = json.loads(original_receipt)
        if previous.get('environments',['tikzpicture'])!=list(environments):
            raise ValueError('prepared native figure environments changed')
        if (previous.get('schema') != result['schema'] or previous.get('status') != 'slot_occupied'
                or previous.get('commands') != [] or previous.get('mutex_acquired') is not False
                or previous.get('tex_runs') != 0 or previous.get('pdf')):
            raise ValueError('resume requires an occupied-slot receipt with zero engine commands')
        # Receipts written before engine selection used pdfLaTeX exclusively.
        for key, legacy in (('engine', 'pdflatex'), ('preview_backend', 'pdftex')):
            if previous.get(key, legacy) != result[key]:
                raise ValueError('prepared figure identity changed: '+key)
        for key in ('source_sha256', 'driver', 'driver_sha256', 'preamble_sha256',
                    'batch_sha256', 'configuration_evidence', 'figures', 'mutex', 'memory_limit_bytes'):
            if previous.get(key) != result[key]:
                raise ValueError('prepared figure identity changed: '+key)
        # Older zero-command receipts precede these fields: neither setting has
        # been applied by an engine. All recorded source/configuration identities
        # and the live assembly are still verified before adoption.
        for key in ('source_date_epoch', 'assembly_sha256'):
            if key in previous and previous[key] != result[key]:
                raise ValueError('prepared figure identity changed: '+key)
        for name, data in prepared.items():
            if not (output / name).is_file() or (output / name).read_bytes() != data:
                raise ValueError('prepared figure bytes changed: '+name)
        if (any((output / (job+suffix)).exists() for suffix in ('.pdf', '.log', '.fls', '.xdv'))
                or any((output / (name+'.txt')).exists() for name in PREVIEW_BACKENDS)
                or list(output.glob('figure-*.svg'))):
            raise ValueError('engine/vector output contradicts unstarted figure receipt')
        history = output / 'attempts'
        history.mkdir(exist_ok=True)
        archived = history / ('NATIVE_FIGURES-'+sha(original_receipt)+'.json')
        if archived.exists() and archived.read_bytes() != original_receipt:
            raise ValueError('figure attempt archive identity differs')
        if receipt_path.read_bytes() != original_receipt:
            raise ValueError('figure receipt changed during resume')
        archived.write_bytes(original_receipt)
        result['resumed_from'] = {'file': str(archived.relative_to(output)), 'sha256': sha(original_receipt)}
    else:
        for name, data in prepared.items():
            if (output / name).exists():
                raise ValueError('unrecorded prepared figure file exists: '+name)
        for name, data in prepared.items(): (output / name).write_bytes(data)
    def save(): receipt_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        with TeXSlot() as slot:
            result['mutex_acquired'] = slot.acquired
            result['mutex_abandoned'] = slot.abandoned
            if not slot.acquired:
                result['status'] = 'slot_occupied'
                return result
            executable = shutil.which(engine)
            if not executable: raise ValueError('native '+engine+' executable absent')
            env = {**os.environ, 'SOURCE_DATE_EPOCH': str(epoch), 'FORCE_SOURCE_DATE': '1',
                   'openin_any': 'a', 'openout_any': 'p'}
            args = [executable, '--disable-installer', '-no-shell-escape', '-interaction=nonstopmode',
                    '-halt-on-error', '-file-line-error', '-recorder', '-jobname='+job,
                    '-output-directory='+output.as_posix(), r'\tracinglostchars=3\input{'+tex.as_posix()+'}']
            result['tex_runs'] = 1
            command = run_job(args, native_driver.parent, output / (engine+'.txt'), env=env, timeout=180)
            result['commands'].append({'tool': engine, **command})
            if command['exit_code'] or command['timed_out']:
                raise ValueError('native figure batch failed; see '+engine+'.txt')
        from pypdf import PdfReader
        pdf = output / (job + '.pdf')
        reader = PdfReader(pdf)
        if len(reader.pages) != len(figures): raise ValueError('native diagram/page count mismatch')
        checks = log_checks((output / (job+'.log')).read_text(encoding='utf-8', errors='replace'))
        result['log_checks'] = checks
        if any(item in checks['issues'] for item in ('tex_error', 'missing_character', 'undefined_token', 'undefined_reference')):
            raise ValueError('native figure batch has unresolved source/glyph errors')
        result['pdf'] = {'file': pdf.name, 'pages': len(reader.pages), 'bytes': pdf.stat().st_size, 'sha256': sha(pdf.read_bytes())}
        result['inputs'] = input_hashes(read_inputs(output / (job+'.fls'), native_driver.parent), folder)
        converter = shutil.which('pdftocairo')
        if not converter: raise ValueError('native PDF-to-SVG converter absent')
        result['vector_converter'] = subprocess.run([converter, '-v'], capture_output=True, encoding='utf-8', check=True).stderr.splitlines()[0]
        for row in figures:
            asset = output / f'figure-{row["index"]:03d}.svg'
            run = subprocess.run([converter, '-svg', '-f', str(row['index']), '-l', str(row['index']), str(pdf), str(asset)],
                                 capture_output=True, encoding='utf-8', timeout=30)
            if run.returncode: raise ValueError('PDF-to-SVG conversion failed')
            data = asset.read_bytes()
            svg = ET.fromstring(data)
            if svg.tag != '{http://www.w3.org/2000/svg}svg': raise ValueError('not an SVG')
            if svg.findall('.//{http://www.w3.org/2000/svg}image'): raise ValueError('raster in native figure')
            if svg.findall('.//{http://www.w3.org/2000/svg}script'): raise ValueError('script in native figure')
            row.update({'asset': asset.name, 'svg_sha256': sha(data), 'svg_bytes': len(data),
                        'width': svg.get('width'), 'height': svg.get('height'), 'viewBox': svg.get('viewBox')})
        verify_assembly(folder, assembly)
        result['status'] = 'vectors_exported_pending_visual_and_semantic_checks'
        return result
    except Exception as error:
        result['status'] = 'failed'
        result['error'] = str(error)
        raise
    finally:
        save()
