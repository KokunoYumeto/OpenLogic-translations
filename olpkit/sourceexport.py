"""Source exports from immutable assemblies; never expand mathematical prose.

The embedding method follows the existing Bengali/Javanese SLC exporters.
Exports here are private candidates until their own clean rebuild and gates pass.
"""
from fnmatch import fnmatchcase
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from .assembly import digest, json_bytes
from .build import build_job, load_build_product, verify_assembly
from .cache import relative_path
from .importlock import select_lock
from .schemas import ROOT
from .structure import without_comments


IMPORT = re.compile(r'\\olimport(\*)?[ \t]*(?:\[([^][]*)\][ \t]*)?\{([^{}\n]+)\}(?:\[([^][]*)\])?')
BOOK_INPUT = re.compile(r'(\\(?:input|include|loadglsentries|IfFileExists)\s*\{)([^{}]*)(\})')
ABOUT = r'\olpath/locale/\ollangid/content/open-logic-about'
NUMBERED_SUMMARY = re.compile(
    r'(\\edef\s*\\slcSummaryFile\s*\{)include/summary-(\\number\s*\\value\{chapter\}\.tex)(\})'
)
DISPATCH = r'''\makeatletter
\NewDocumentCommand \olpkitEmbeddedImport {m O{section}}{%
  \begingroup
  \def\ol@sectioncs{#2}%
  \def\olfilename{#1}%
  \subfile{#1}%
  \endgroup}
\NewDocumentCommand \olpkitMissingImport {m}{%
  \errmessage{olpkit: #1}}
\makeatother
'''


def code_lines(text, transform):
    """Transform executable text while preserving comments and escaped percent signs."""
    result = []
    for line in text.splitlines(keepends=True):
        cut = len(line)
        for match in re.finditer('%', line):
            prefix = line[:match.start()]
            if (len(prefix) - len(prefix.rstrip('\\'))) % 2 == 0:
                cut = match.start()
                break
        result.append(transform(line[:cut]) + line[cut:])
    return ''.join(result)


def retarget_imports(text, source_path, modules, excluded):
    def replace(match):
        star, directory, name, section = match.groups()
        if name == ABOUT:
            target = 'content/open-logic-about.tex'
        else:
            if any('\\' in part for part in (directory or '', name)):
                raise ValueError('unresolved import expression: ' + source_path)
            base = 'content' if star and directory else str(PurePosixPath(source_path).parent)
            target = posixpath.normpath(posixpath.join(base, directory or '', name))
            if not target.endswith('.tex'):
                target += '.tex'
            relative_path(target)
            if not target.startswith('content/'):
                raise ValueError('import escapes content: ' + target)
        if target not in modules:
            # Preserve the conditional branch. Execution is an error, never silent omission.
            excluded.add((source_path, target))
            return r'\olpkitMissingImport{' + target + '}'
        return r'\olpkitEmbeddedImport{' + modules[target] + '}' + ('[' + section + ']' if section else '')
    changed=code_lines(text, lambda line: IMPORT.sub(replace, line))
    if re.search(r'\\olimport\b',without_comments(changed)):
        raise ValueError('unparsed import in '+source_path)
    return changed


def book_name(name):
    relative_path(name)
    return 'olpkit-book-' + name.removesuffix('.tex').replace('/', '-') + '.tex'


def retarget_book_inputs(text, names):
    def replace(match):
        left, name, right = match.groups()
        target = name if name.endswith('.tex') else name + '.tex'
        if target in names:
            name = names[target]
        elif '\\' in name and not name.startswith('\\'):
            prefix = name.split('\\', 1)[0]
            matches = [p for p in names if p.startswith(prefix)]
            if matches:
                name = 'olpkit-book-' + name.replace('/', '-')
                if not name.endswith('.tex'):
                    name += '.tex'
            elif name.startswith('include/'):
                raise ValueError('unresolved dynamic book input: ' + name)
        elif name.startswith('include/'):
            raise ValueError('book input was not embedded: ' + name)
        return left + name + right
    def retarget_line(line):
        def summary_path(match):
            if not any(re.fullmatch(r'include/summary-\d+\.tex', name) for name in names):
                raise ValueError('numbered summary inputs were not embedded')
            return match[1] + 'olpkit-book-include-summary-' + match[2] + match[3]
        return NUMBERED_SUMMARY.sub(summary_path, BOOK_INPUT.sub(replace, line))
    return code_lines(text, retarget_line)


def embed(name, text):
    if r'\end{filecontents' in text:
        raise ValueError('nested filecontents in ' + name)
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
        raise ValueError('unsafe embedded filename')
    return '\\begin{filecontents*}[overwrite]{' + name + '}\n' + text + ('' if text.endswith('\n') else '\n') + '\\end{filecontents*}\n'


def cumulative(source, assembly, imports, profile):
    source = Path(source).resolve()
    verify_assembly(source, assembly)
    if assembly.get('unreconciled_legacy_inputs'):
        raise ValueError('unreconciled source overlays')
    book = assembly['book_directory']
    relative_path(book)
    locale = assembly['locale']
    states = {u['path']: u for u in assembly['units']}
    modules = {}
    for uid, path in imports:
        if path in modules or states.get(path, {}).get('id') != uid:
            raise ValueError('duplicate or mismatched imported identity: ' + path)
        if states[path]['state'] != 'current' or states[path]['english_fill']:
            raise ValueError('imported translation is not current: ' + path)
        modules[path] = 'olpkit-' + uid.lower() + '.tex'
    if not modules:
        raise ValueError('empty import scope')
    driver = profile['driver']
    relative_path(driver)
    if driver != build_job(assembly) + '.tex':
        raise ValueError('export driver differs from the assembled native book')
    book_files = sorted(p[len(book)+1:] for p in assembly['files'] if p.startswith(book + '/')
                        and any(len(PurePosixPath(p[len(book)+1:]).parts)==len(pattern.split('/'))
                                and fnmatchcase(p[len(book)+1:],pattern) for pattern in profile['text_patterns']))
    if driver not in book_files:
        raise ValueError('screen driver not included')
    names = {p: book_name(p) for p in book_files if p != driver}
    if len(set(names.values())) != len(names):
        raise ValueError('embedded book filename collision')
    sections, evidence, excluded = [], [], set()
    def read(path):
        relative_path(path)
        if path not in assembly['files']:
            raise ValueError('unrecorded source input: ' + path)
        return (source/path).read_bytes().decode('utf-8-sig')
    def record(path, name, original, transformed):
        sections.append(embed(name, transformed))
        evidence.append({'path':path, 'embedded':name, 'source_sha256':assembly['files'][path]['sha256'],
                         'transformed_sha256':digest(transformed.encode('utf-8'))})
    for path, name in modules.items():
        actual = 'locale/' + locale + '/' + path
        text = read(actual)
        record(actual, name, text, retarget_imports(text, path, modules, excluded))
    for path, name in names.items():
        actual = book + '/' + path
        text = read(actual)
        changed = retarget_imports(text, '', modules, excluded)
        record(actual, name, text, retarget_book_inputs(changed, names))
    original = read(book + '/' + driver)
    rendered = retarget_book_inputs(retarget_imports(original, '', modules, excluded), names)
    anchor = r'\begin{document}'
    if without_comments(rendered).count(anchor) != 1:
        raise ValueError('screen driver must have one document start')
    rendered = code_lines(rendered, lambda line: line.replace(anchor, DISPATCH + anchor))
    sections.append(rendered)
    data = '\n'.join(sections).encode('utf-8')
    return data, {'units':len(modules), 'book_files':len(names), 'embedded':evidence,
                  'conditional_imports_outside_lock':[{'source':s,'target':t} for s,t in sorted(excluded)],
                  'driver':book + '/' + driver, 'driver_source_sha256':digest(original.encode('utf-8')),
                  'tex_runs':0, 'rendered_equivalence':'pending clean cumulative rebuild'}


def deterministic_zip(files):
    stream = io.BytesIO()
    folded = set()
    with ZipFile(stream, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, body in sorted(files.items()):
            relative_path(name)
            if name.casefold() in folded:
                raise ValueError('archive filename collision')
            folded.add(name.casefold())
            info = ZipInfo(name, date_time=(1980,1,1,0,0,0))
            info.create_system=3;info.external_attr=0o100644 << 16
            archive.writestr(info, body, compress_type=ZIP_DEFLATED, compresslevel=9)
    data=stream.getvalue()
    with ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(files):
            raise ValueError('source ZIP verification failed')
    return data


def source_package(source, assembly, build_path, policy, instructions, cumulative_body, cumulative_name, driver_inputs=()):
    """Use recorded source inputs plus explicit attribution and BibTeX dependencies."""
    from .credits import inspect_credits
    from .recorder import read_inputs, input_hashes
    source=Path(source).resolve();build_path=Path(build_path).resolve()
    verify_assembly(source,assembly)
    build=json.loads(build_path.read_text(encoding='utf-8'))
    if build.get('status')!='compiled_pending_remaining_gates' or not build.get('commands'):
        raise ValueError('source ZIP requires a successful recorded translated build')
    if any(c.get('exit_code')!=0 or c.get('timed_out') for c in build['commands']):
        raise ValueError('source ZIP build commands failed')
    if build['assembly_sha256']!=digest(json_bytes(assembly)):
        raise ValueError('source ZIP build belongs to another assembly')
    if (build_path.parent/build['build_tree']).resolve()!=source:
        raise ValueError('source ZIP build tree differs')
    for gate in ('G-IMPORT','G-UNITS','G-LOG','G-BOX'):
        if build['gates'].get(gate,{}).get('status')!='pass':
            raise ValueError('source ZIP build gate is not passing: '+gate)
    pdf=(build_path.parent/build['pdf']['path']).resolve()
    if not pdf.is_relative_to(build_path.parent) or digest(pdf.read_bytes())!=build['pdf']['sha256']:
        raise ValueError('source ZIP PDF witness differs')
    book=assembly['book_directory'];job=Path(book)/build_job(assembly)
    fls=source/job.with_suffix('.fls')
    if digest(fls.read_bytes())!=build['recorder_sha256']:
        raise ValueError('source ZIP recorder witness differs')
    actual=input_hashes(read_inputs(fls,source/book),source)
    if actual!=build['recorder_inputs']:
        raise ValueError('source ZIP recorded input hashes differ from current files')
    credits=inspect_credits(source,policy)
    if credits['issues'] or any(c['state']=='unresolved' for c in policy['components']):
        raise ValueError('component source notices are incomplete or changed')
    files={};reasons={}
    def add(name,reason,expected=None):
        relative_path(name);p=(source/name).resolve()
        if not p.is_relative_to(source):raise ValueError('archive source escapes tree')
        body=p.read_bytes()
        if expected and digest(body)!=expected:raise ValueError('archive source changed: '+name)
        if name in files and files[name]!=body:raise ValueError('archive member collision')
        files[name]=body;reasons.setdefault(name,[]).append(reason)
    for row in build['recorder_inputs']:
        if row['kind']!='assembled-tree':continue
        name=row['path'];relative_path(name)
        if name in assembly['files']:
            if row['sha256']!=assembly['files'][name]['sha256']:
                raise ValueError('recorder source differs from assembly: '+name)
            add(name,'TeX recorder input',row['sha256'])
        elif name.endswith('.xmpdata'):
            add(name,'generated reader metadata',row['sha256'])
        elif name in {job.with_suffix('.pcr').as_posix(), job.with_suffix('.prb').as_posix()}:
            # OLP regenerates the photo-credit list and deferred exercises.
            continue
        elif Path(name).suffix not in {'.aux','.bbl','.gls','.toc','.out','.idx','.ind','.ilg','.glo','.ist'}:
            raise ValueError('unclassified generated recorder input: '+name)
    for name in driver_inputs:
        relative_path(name)
        path=book+'/'+name
        if path not in assembly['files']:
            raise ValueError('unrecorded PDF driver input: '+path)
        add(path,'PDF driver input',assembly['files'][path]['sha256'])
    for unit, paths in build['content_inputs'].items():
        if not paths or any(p not in files for p in paths):
            raise ValueError('recorded source unit missing from ZIP: '+unit)
    for component in policy['components']:
        for notice in component.get('files',[]):add(notice['path'],'component notice',notice['sha256'])
    aux=(source/job.with_suffix('.aux')).read_text(encoding='utf-8')
    for kind,names in re.findall(r'\\(bibdata|bibstyle)\{([^}]+)\}',aux):
        suffix='.bib' if kind=='bibdata' else '.bst'
        for name in names.split(','):
            name=name.strip()
            if not name.endswith(suffix):name+=suffix
            if name.startswith('../'):
                # BibTeX runs from the book directory and may address a pinned shared bibliography.
                requested=posixpath.normpath(posixpath.join(book,name))
                relative_path(requested)
                candidates=[requested] if requested in assembly['files'] else []
            else:
                relative_path(name)
                candidates=[p for p in assembly['files'] if p==name or p==book+'/'+name or p=='bib/'+name]
            if len(candidates)!=1:raise ValueError('unresolved bibliography dependency: '+name)
            path=candidates[0];add(path,'BibTeX input',assembly['files'][path]['sha256'])
    if not instructions.strip():raise ValueError('localized build instructions are required')
    if 'BUILD.md' in files:raise ValueError('BUILD.md conflicts with recorded input')
    files['BUILD.md']=instructions
    files[book+'/'+cumulative_name]=cumulative_body
    original_xmp=job.with_suffix('.xmpdata').as_posix()
    if original_xmp in files:files[book+'/'+Path(cumulative_name).with_suffix('.xmpdata').name]=files[original_xmp]
    files['SOURCE-SHA256SUMS.txt']=''.join(digest(body)+'  '+name+'\n' for name,body in sorted(files.items())).encode('utf-8')
    return deterministic_zip(files), {'members':len(files),'member_reasons':reasons,
        'files':{n:{'bytes':len(b),'sha256':digest(b)} for n,b in sorted(files.items())},
        'build_sha256':digest(build_path.read_bytes()),'pdf_sha256':build['pdf']['sha256'],
        'credit_policy_sha256':digest(json_bytes(policy)),
        'clean_archive_rebuild':'pending','cumulative_rebuild':'pending'}


def export_import_lock(assembly, profile):
    """Bind imports to the native book, retaining other assets in the assembly."""
    _, book = load_build_product(assembly['product'])
    if profile['book'] != book['id']:
        raise ValueError('export profile belongs to a different native book')
    required = ('olp', book['source_id'], 'photos', 'portraits')
    pins = {name:assembly['sources'][name]['commit'] for name in required}
    return select_lock(ROOT/'data/books'/book['id'], pins)


def export_command(source, product, out, profile_path=None, build_path=None, credit_path=None, instructions_path=None):
    source=Path(source).resolve();out=Path(out).resolve()
    boundary=(ROOT.parent/'out').resolve()
    if out==boundary or not out.is_relative_to(boundary) or out.exists():
        raise ValueError('export needs a fresh named output folder')
    assembly=json.loads((source/'ASSEMBLY.json').read_text(encoding='utf-8'))
    default_profile=ROOT/'data/exports'/f"{assembly['product']}.json"
    locale_profile=default_profile.with_stem(f"{default_profile.stem}-{assembly['locale']}")
    profile_path=Path(profile_path) if profile_path else locale_profile if locale_profile.is_file() else default_profile
    profile=json.loads(profile_path.read_text(encoding='utf-8'))
    _, imports, lock=export_import_lock(assembly, profile)
    body,report=cumulative(source,assembly,imports,profile)
    filename=profile['stem']+'-'+assembly['locale']+'.tex'
    relative_path(filename)
    outputs={filename:body}
    if product=='source-zip':
        if not all([build_path,credit_path,instructions_path]):
            raise ValueError('source ZIP requires --build, --credits and localized --instructions')
        policy=json.loads(Path(credit_path).read_text(encoding='utf-8'))
        packed,package_report=source_package(
            source,assembly,build_path,policy,Path(instructions_path).read_bytes(),body,filename,
            profile.get('driver_inputs',())
        )
        outputs[profile['stem']+'-'+assembly['locale']+'-source.zip']=packed
        report['package']=package_report
    report.update(schema='olpkit.source-export.v1', product=product, locale=assembly['locale'],
                  assembly_sha256=digest(json_bytes(assembly)), import_lock_sha256=lock['lock_sha256'],
                  profile_sha256=digest(profile_path.read_bytes()), release_ready=False,
                  outputs={n:{'bytes':len(b),'sha256':digest(b)} for n,b in outputs.items()})
    out.mkdir(parents=True)
    for name,data in outputs.items():(out/name).write_bytes(data)
    (out/'EXPORT.json').write_bytes(json_bytes(report))
    print(f"{report['units']} embedded source units; {report['book_files']} book files; cumulative rebuild pending")
    return 0
