"""Guarded, recorded textbook compilation; no release or translation side effects."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import tomllib

from .assembly import assemble_command,AssemblyTree,GitSnapshot,json_bytes,digest,write_assembly
from .cache import SourceCache,run_git,relative_path
from .process import TeXSlot,run_job,MEMORY_LIMIT,TEX_MUTEX
from .recorder import read_inputs,content_inputs,load_imports,compare_imports,input_hashes
from .schemas import ROOT,validate_schema
from .edition import git_blob
from .importlock import select_lock,write_lock,pin_key


GATES=('G-UNITS','G-STRUCT','G-NOTE','G-TOKEN','G-ORTHO','G-ALONE','G-IMPORT','G-LOG',
       'G-BOX','G-GLYPH','G-TABLE','G-SCALE','G-LINK','G-CREDIT','G-SAME','G-EPUB','G-HUB')


def load_build_product(product,data_root=None):
    """Resolve a registered book rather than assuming every textbook is SLC."""
    if not re.fullmatch(r'[a-z][a-z0-9-]*',product):raise ValueError('invalid build product')
    data_root=Path(data_root) if data_root else ROOT/'data'
    path=data_root/'build-products'/(product+'.json')
    if not path.is_file():raise ValueError('build product not yet implemented: '+product)
    data=json.loads(path.read_text(encoding='utf-8'));validate_schema('build-product',data)
    book=tomllib.loads((data_root/'books'/(data['book']+'.toml')).read_text(encoding='utf-8'))
    validate_schema('book',book)
    if book['id']!=data['book']:raise ValueError('build book identity differs')
    source=book['source_id'];required={source,'photos','portraits'}
    registered=tomllib.loads((data_root/'sources.toml').read_text(encoding='utf-8'))
    if (source not in registered or registered[source]['repository']!=book['repository']
            or set(data['reference_pins'])!=required
            or data['reference_pins'][source]!=book['commit']):
        raise ValueError('build product source pins differ from its registered book')
    mounts={'olp':'',source:'courses/'+book['id'],'photos':'assets/photos','portraits':'assets/portraits'}
    if data['reference_mounts']!=mounts:raise ValueError('build product mounts differ from its sources')
    driver=data.get('driver','slc-screen.tex')
    if driver not in book['drivers']:raise ValueError('build driver is not declared by the book')
    return data,book


def build_job(report):
    driver=report.get('driver','slc-screen.tex')
    if not isinstance(driver,str) or not re.fullmatch(r'[a-z][a-z0-9-]*\.tex',driver):
        raise ValueError('invalid native book driver')
    return driver[:-4]


def log_checks(text):
    compact=' '.join(text.split())
    patterns={
        'undefined_reference':r'(?:There were undefined (?:references|citations)|(?:Reference|Citation) .{0,200}? undefined)',
        'rerun':r'(?:Label\(s\) may have changed|Rerun to get (?:cross-references|outlines) right|Please rerun LaTeX)',
        'duplicate_label':r'(?:multiply defined|destination with the same identifier)',
        'undefined_token':r'Token .{0,200}? undefined',
        'unmarked_import':r'requested but not marked',
        'missing_character':r'Missing character:',
        'tex_error':r'(?:^! |^.+:\d+: (?:Undefined control sequence|LaTeX Error))',
    }
    issues=[key for key,p in patterns.items() if re.search(p,text if key=='tex_error' else compact,re.M)]
    boxes=[float(x) for x in re.findall(r'Overfull\s+\\[hv]box\s*\(([\d.]+)pt too (?:wide|high)\)',text)]
    return {'issues':issues,'overfull_count':len(boxes),'maximum_overfull_pt':max(boxes,default=0),
            'overfull_over_2pt':[v for v in boxes if v>2]}


def bibliography_key(aux):
    return digest('\n'.join(line for line in aux.splitlines() if line.startswith(('\\citation','\\bibdata','\\bibstyle'))).encode())


def auxiliary_hashes(book,job):
    return {s:digest((book/(job+s)).read_bytes()) for s in ('.aux','.toc','.out','.bbl','.gls') if (book/(job+s)).is_file()}


def verify_assembly(folder,report):
    for name,item in report['files'].items():
        relative_path(name);p=(folder/name).resolve()
        if not p.is_relative_to(folder.resolve()) or not p.is_file() or digest(p.read_bytes())!=item['sha256']:
            raise ValueError('assembled input changed: '+name)


def record_pdf_glyphs(output,result):
    """Bind actual encoded-glyph inspection to the completed build's PDF."""
    from .pdfaudit import inspect_glyphs
    output=Path(output).resolve();pdf=(output/result['pdf']['path']).resolve()
    if not pdf.is_relative_to(output) or digest(pdf.read_bytes())!=result['pdf']['sha256']:
        raise ValueError('PDF bytes changed before glyph inspection')
    report=inspect_glyphs(pdf);payload=json_bytes(report);path=output/'G-GLYPH.json'
    path.write_bytes(payload)
    status=report['status']
    if status=='pass' and result['gates'].get('G-LOG',{}).get('status')!='pass':status='partial'
    result['gates']['G-GLYPH']={'status':status,'report':path.name,'sha256':digest(payload),
        'unmapped_trace_glyphs':report['unmapped_trace_glyphs'],
        'notdef_glyphs':report['notdef_glyphs'],
        'poppler_invalid_characters':report['poppler_invalid_characters'],
        'private_use_glyphs':report['private_use_glyphs'],
        'scope':'Actual PDF encoding plus existing build-log gate; source/visual glyph meaning remains a separate check.'}
    result['release_ready']=False
    (output/'BUILD.json').write_bytes(json_bytes(result))
    return status=='pass'


def record_pdf_links(output,result,minimum_contrast=7,expected_color=None,*,xdvipdfmx=False):
    """Inspect the built PDF after the TeX slot has been released."""
    from .pdfaudit import inspect_links
    output=Path(output).resolve();pdf=(output/result['pdf']['path']).resolve()
    if not pdf.is_relative_to(output) or digest(pdf.read_bytes())!=result['pdf']['sha256']:
        raise ValueError('PDF bytes changed before link inspection')
    links=inspect_links(pdf,minimum_contrast,progress=lambda n:print(f'PDF links: inspected page {n}',flush=True),
                        expected_color=expected_color,xdvipdfmx=xdvipdfmx)
    payload=json_bytes(links);path=output/'G-LINK.json';path.write_bytes(payload)
    result['gates']['G-LINK']={'status':links['status'],'report':path.name,'sha256':digest(payload),
                             'link_areas':links['link_areas'],'citation_areas':links['citation_areas'],
                             'issues':len(links['issues']),'unmeasured':len(links['unmeasured'])}
    result['release_ready']=False
    (output/'BUILD.json').write_bytes(json_bytes(result))
    return links['status']=='pass'


def record_pdf_credits(output,result,policy_path):
    """Record notice and reader checks without calling missing policy a pass."""
    from .credits import inspect_credits
    output=Path(output).resolve();policy_path=Path(policy_path)
    if not policy_path.is_file():
        result['gates']['G-CREDIT']={'status':'incomplete','reason':'Component credit policy not configured.'}
        (output/'BUILD.json').write_bytes(json_bytes(result))
        return False
    policy=json.loads(policy_path.read_text(encoding='utf-8'))
    credits=inspect_credits(output/'source',policy,output/result['pdf']['path'],output/'BUILD.json')
    payload=json_bytes(credits);path=output/'G-CREDIT.json';path.write_bytes(payload)
    result['gates']['G-CREDIT']={'status':credits['status'],'report':path.name,'sha256':digest(payload),
                               'notices':len(credits['files']),'issues':len(credits['issues']),
                               'unmeasured':len(credits['unmeasured'])}
    result['release_ready']=False
    (output/'BUILD.json').write_bytes(json_bytes(result))
    return credits['status']=='pass'


def validate_unstarted_attempt(previous,report,engine,epoch):
    """Only a zero-command occupied-slot attempt can reuse its prepared tree."""
    if (previous.get('schema')!='olpkit.build.v1' or previous.get('status')!='slot_occupied'
            or previous.get('commands')!=[] or previous.get('mutex_acquired') is not False
            or previous.get('passes')!=0 or previous.get('pdf')):
        raise ValueError('resume requires an occupied-slot receipt with no engine commands')
    if (previous.get('assembly_sha256')!=digest(json_bytes(report))
            or previous.get('source_inputs')!=report['files']
            or previous.get('engine')!=engine or previous.get('source_date_epoch')!=epoch
            or previous.get('book_directory')!=report['book_directory']
            or previous.get('build_tree')!='source'):
        raise ValueError('prepared build identity changed; do not resume this tree')


def copy_build_input(source, destination):
    # LuaTeX includes the font's mtime in its shared HarfBuzz cache.
    if destination.suffix.lower() in {".otf", ".ttf"}:
        shutil.copy2(source, destination)
    else:
        shutil.copyfile(source, destination)


def compile_book(folder,report,engine,epoch,output,expected=None,reference=False,resume=False):
    """Serialize a build directory and preserve any resumable zero-engine receipt."""
    folder=Path(folder);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    lock=output/'.olpkit-build.lock'
    try:
        with lock.open('xb') as stream:stream.write(str(os.getpid()).encode())
    except FileExistsError:
        raise ValueError('another invocation owns this build directory; do not restart it') from None
    try:
        receipt=output/'BUILD.json'
        if resume:
            if not receipt.is_file():raise ValueError('resume requires the previous occupied-slot receipt')
            original=receipt.read_bytes();previous=json.loads(original)
            validate_unstarted_attempt(previous,report,engine,epoch)
            verify_assembly(folder,report)
            history=output/'attempts';history.mkdir(exist_ok=True)
            archived=history/('BUILD-'+digest(original)+'.json')
            if archived.exists() and archived.read_bytes()!=original:
                raise ValueError('attempt archive identity differs')
            if receipt.read_bytes()!=original:raise ValueError('build receipt changed during resume')
            receipt.replace(archived)
        elif receipt.exists():
            raise ValueError('a build receipt already exists; use --resume only for a zero-engine occupied slot')
        return _compile_book(folder,report,engine,epoch,output,expected,reference)
    finally:
        lock.unlink()


def settle_tex(folder, book, job, engine, epoch, output, result, save):
    """Compile an existing driver inside the caller's TeX slot, with bounded child jobs."""
    if engine not in ('xelatex', 'pdflatex', 'lualatex') or not re.fullmatch(r'[a-z][a-z0-9-]*', job):
        raise ValueError('unexpected native engine or driver name')
    env={**os.environ,'SOURCE_DATE_EPOCH':str(epoch),'FORCE_SOURCE_DATE':'1',
         'BSTINPUTS':str(folder/'bib')+os.pathsep,'openin_any':'a','openout_any':'p'}
    # Restrict tool side effects to this staging tree; installer and shell escape stay off.
    deadline=time.monotonic()+1200
    def invoke(tool,args):
        executable=shutil.which(tool)
        if not executable:raise ValueError('build executable absent: '+tool)
        remaining=deadline-time.monotonic()
        if remaining<=0:raise ValueError('whole build exceeded twenty minutes')
        number=len(result['commands'])+1;log=output/(f'{number:02d}-'+tool+'.txt')
        command=run_job([executable,*args],book,log,env=env,timeout=min(240,remaining))
        result['commands'].append({'tool':tool,'arguments':args,'log':log.name,**command});save()
        print(json.dumps({'tool':tool,'step':number,'exit':command['exit_code'],'seconds':command['seconds']}),flush=True)
        if command['timed_out'] or command['exit_code']!=0:raise ValueError(tool+' failed; inspect '+log.name)
        return log.read_text(encoding='utf-8',errors='replace')
    version=invoke(engine,['--version']);result['engine_version']=version.splitlines()[0]
    options=['--disable-installer'] if 'MiKTeX' in version else []
    args=options+['-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error',
                  '-recorder','-jobname='+job,r'\tracinglostchars=3\input{'+job+'.tex}']
    bib_key=index_key=None;settled=False
    for number in range(1,8):
        before=auxiliary_hashes(book,job)
        invoke(engine,args);result['passes']=number
        checks=log_checks((book/(job+'.log')).read_text(encoding='utf-8',errors='replace'))
        if any(x in checks['issues'] for x in ('missing_character','undefined_token','unmarked_import','tex_error')):
            raise ValueError('deterministic TeX defect: '+', '.join(checks['issues']))
        ran_aux=False
        aux=(book/(job+'.aux')).read_text(encoding='utf-8',errors='replace')
        key=bibliography_key(aux)
        if '\\bibdata' in aux and key!=bib_key:
            invoke('bibtex',options+[job]);bib_key=key;ran_aux=True
        glo=book/(job+'.glo')
        if glo.is_file() and glo.stat().st_size and digest(glo.read_bytes())!=index_key:
            invoke('makeindex',['-s',job+'.ist','-t',job+'.glg','-o',job+'.gls',job+'.glo'])
            index_key=digest(glo.read_bytes());ran_aux=True
        if not checks['issues'] and not ran_aux and before==auxiliary_hashes(book,job):
            settled=True;break
    if not settled:raise ValueError('build did not settle within seven TeX passes')
    return checks


def _compile_book(folder,report,engine,epoch,output,expected=None,reference=False):
    """Compile once per validated input batch; every tool stays under the slot."""
    folder=Path(folder).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    verify_assembly(folder,report)
    book=folder/report['book_directory'];job=build_job(report);driver=book/(job+'.tex')
    if not driver.is_file():raise ValueError('book driver absent')
    result={'schema':'olpkit.build.v1','status':'not_started','engine':engine,'source_date_epoch':epoch,
            'memory_limit_bytes':MEMORY_LIMIT,'mutex':TEX_MUTEX,'mutex_acquired':False,'commands':[],
            'passes':0,'gates':{g:{'status':'not_implemented'} for g in GATES},
            'assembly_sha256':digest(json_bytes(report)),'source_inputs':report['files'],
            'release_ready':False,'build_tree':'source','book_directory':report['book_directory']}
    receipt=output/'BUILD.json';started=time.monotonic()
    def save():
        result['elapsed_seconds']=round(time.monotonic()-started,3);receipt.write_bytes(json_bytes(result))
    if receipt.exists():raise ValueError('a build receipt already exists; preserve it and choose a new output directory')
    try:
        if report.get('unreconciled_legacy_inputs'):
            raise ValueError('source migration is pending; native prose overlays cannot be silently omitted')
        with TeXSlot() as slot:
            result['mutex_acquired']=slot.acquired;result['mutex_abandoned']=slot.abandoned
            if not slot.acquired:
                result['status']='slot_occupied';print('TeX slot occupied; no engine started',flush=True);return result
            checks = settle_tex(folder, book, job, engine, epoch, output, result, save)
            pdf=book/(job+'.pdf');fls=book/(job+'.fls')
            if not pdf.is_file() or not fls.is_file():raise ValueError('PDF or recorder output absent')
            inputs=read_inputs(fls,book);found,wrong=content_inputs(inputs,folder,None if reference else report['locale'])
            result['content_inputs']={k:v for k,v in sorted(found.items())}
            if reference:
                known={line.split('\t')[1] for line in (ROOT/'data/units/olp-units.tsv').read_text().splitlines()[1:]}
                imported={'pass':bool(found) and not wrong and set(found)<=known,'observed':len(found),'wrong_language_inputs':wrong}
            else:imported=compare_imports(found,wrong,expected)
            result['gates']['G-IMPORT']={'status':'pass' if imported['pass'] else 'fail',**imported}
            if not imported['pass']:raise ValueError('recorder content imports differ from the pinned book lock')
            if reference:unit_ok=True
            else:
                states={u['path']:u['state'] for u in report['units']};unit_ok=all(states.get(p)=='current' for p in found)
            result['gates']['G-UNITS']={'status':'pass' if unit_ok else 'fail','checked_imported_units':len(found)}
            result['gates']['G-LOG']={'status':'pass','issues':checks['issues']}
            result['gates']['G-BOX']={'status':'pass' if not checks['overfull_over_2pt'] else 'fail',**checks}
            result['gates']['G-GLYPH']={'status':'partial','log_missing_character_errors':0,'PDF_glyph_inspection':'pending'}
            result['recorder_inputs']=input_hashes(inputs,folder)
            result['pdf']={'path':pdf.relative_to(output).as_posix(),'bytes':pdf.stat().st_size,'sha256':digest(pdf.read_bytes())}
            result['log_sha256']=digest((book/(job+'.log')).read_bytes());result['recorder_sha256']=digest(fls.read_bytes())
            verify_assembly(folder,report)
            if not unit_ok:raise ValueError('imported translations are not all current')
            if not reference and checks['overfull_over_2pt']:raise ValueError('overfull boxes exceed 2pt')
            result['status']='reference_compiled' if reference else 'compiled_pending_remaining_gates'
            return result
    except Exception as error:
        result['status']='failed';result['error']=str(error);raise
    finally:save()


def reference_tree(cache_root,olp_pin,out,check=False,product='slc-screen-pdf'):
    data,_=load_build_product(product)
    pin_key({'olp':olp_pin,**data['reference_pins']})
    cache=SourceCache(cache_root);tree=AssemblyTree();sources={}
    for source,pin in {'olp':olp_pin,**data['reference_pins']}.items():
        source_folder,record=cache.require(source,pin);sources[source]=pin
        prefix=data['reference_mounts'][source]
        for name in record['files']:
            if name.startswith('.') or name.endswith('~') or name in ['CHANGELOG.md','Makefile','makereadme']:continue
            dest=(prefix+'/' if prefix else '')+name
            tree.add(dest,(source_folder/name).read_bytes(),{'source':source,'commit':pin,'path':name})
    extra = data['reference_dependency']
    packages = ROOT / 'data' / 'reference-packages'
    witnesses = json.loads((packages / 'sources.json').read_bytes())
    matches = [item for item in witnesses if (item['repository'], item['commit']) ==
               (extra['repository'], extra['commit'])]
    if len(matches) != 1 or set(matches[0]['files']) != set(extra['files']):
        raise ValueError('Reference package has no matching complete source distribution')
    for name, evidence in matches[0]['files'].items():
        body = (packages / relative_path(evidence['file'])).read_bytes()
        if digest(body) != evidence['sha256'] or git_blob(body) != evidence['git_blob']:
            raise ValueError('Reference package differs from its pinned source: ' + name)
        tree.add('courses/' + data['book'] + '/' + Path(name).name, body,
                 {'source': 'package-witness', 'commit': extra['commit'], 'path': name})
    report={'schema':'olpkit.reference-assembly.v1','book_directory':'courses/'+data['book'],
            'pins':sources,'files':tree.origins,'unreconciled_legacy_inputs':[]}
    if 'driver' in data:report['driver']=data['driver']
    write_assembly(tree,report,out,check);return report


def build_command(repo,ref,edition_ref,metadata_dir,cache_root,out,product='slc-screen-pdf',english=False,olp_pin=None,resume=False,book_ledger=None,web_profile=None,web_product="accessible"):
    product_data,book=load_build_product(product)
    if not out:raise ValueError('build requires an explicit named --out directory')
    output=Path(out).resolve();boundary=(ROOT.parent/'out').resolve()
    if output==boundary or not output.is_relative_to(boundary):raise ValueError('build output escapes named builder outputs')
    if output.exists() and not resume:raise ValueError('build output already exists; preserve it or resume an unstarted build')
    if resume and not output.is_dir():raise ValueError('resume requires an existing prepared build directory')
    source=output/'source';lock_dir=ROOT/'data/books'/book['id']
    if english:
        if not olp_pin:raise ValueError('English reference requires an explicit full --olp-pin')
        report=reference_tree(cache_root,olp_pin,source,resume,product);engine='pdflatex';expected=None
    else:
        if not repo:raise ValueError('translation build requires --repo')
        edition=tomllib.loads((GitSnapshot(repo,edition_ref or ref).read_many(['olp-edition.toml'])['olp-edition.toml']
                              if not metadata_dir else (Path(metadata_dir)/'olp-edition.toml').read_bytes()).decode('utf-8-sig'))
        engine=edition['engine'];olp_pin=edition['pins']['olp']['commit']
        _,expected,_=select_lock(lock_dir,{s:edition['pins'][s]['commit'] for s in ('olp',book['source_id'],'portraits','photos')})
        report=assemble_command(repo,ref,edition_ref,metadata_dir,cache_root,source,product,check=resume,book_ledger=book_ledger)
    if build_job(report)+'.tex'!=product_data.get('driver','slc-screen.tex'):
        raise ValueError('assembled driver differs from requested build product')
    bare=SourceCache(cache_root).locations('olp',olp_pin)[0]
    epoch=int(run_git(bare,'show','-s','--format=%ct',olp_pin).stdout.decode().strip())
    result=compile_book(source,report,engine,epoch,output,expected,english,resume)
    if not english and result.get('pdf'):
        from .buildchecks import verify_native_build
        result=verify_native_build(output,repo,cache_root,metadata_dir,web_profile,web_product)
        if any(gate['status']=='slot_occupied' for gate in result['gates'].values()):
            return 75
        if any(gate['status']!='pass' for gate in result['gates'].values()):
            print('See BUILD.json for outstanding acceptance checks.',flush=True)
            return 1
    if english and result['status']=='reference_compiled':
        registry=dict(line.split('\t')[::-1] for line in (ROOT/'data/units/olp-units.tsv').read_text().splitlines()[1:])
        rows=sorted(((registry[p],p) for p in result['content_inputs']))
        body=''.join(uid+'\t'+path+'\n' for uid,path in rows).encode()
        meta={'schema':'olpkit.imports.v1','pins':report['pins'],'lock_sha256':digest(body),
              'units':len(rows),'recorder_sha256':result['recorder_sha256'],'reference_pdf_sha256':result['pdf']['sha256']}
        write_lock(lock_dir,body,meta)
    return 75 if result['status']=='slot_occupied' else 0
