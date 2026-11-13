"""Check explicit component notices and actual reader attribution.

A notice check is not a legal opinion, linguistic review or permission grant.
Requirements come from a separately reviewed policy, never from the output alone.
"""
import json
from pathlib import Path
import unicodedata

from .assembly import digest,json_bytes
from .cache import relative_path
from .pdfaudit import extracted_text,file_record
from .schemas import validate_schema


CATEGORIES={'original-text','book','translation','portraits','photographs','fonts','bundled-packages'}


def normalized(text):
    # Preserve names, spelling, punctuation and accents. Only whitespace is folded.
    return ' '.join(unicodedata.normalize('NFC',text).split())


def member(root,name):
    relative_path(name)
    p=(root/name).resolve()
    if not p.is_relative_to(root) or p.is_symlink():
        raise ValueError('credit input escapes source tree: '+name)
    return p


def inspect_credits(source,policy,pdf=None,build=None):
    validate_schema('credit-policy',policy)
    categories={c['category'] for c in policy['components']}
    if categories!=CATEGORIES:
        raise ValueError('credit policy must account for all seven component categories')
    ids=[c['id'] for c in policy['components']]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate credit component')
    source=Path(source).resolve();assembly=source/'ASSEMBLY.json'
    report=json.loads(assembly.read_text(encoding='utf-8-sig'))
    if report['locale']!=policy['locale'] or report['product']!=policy['product']:
        raise ValueError('credit policy belongs to a different edition/product')
    pins={k:v['commit'] for k,v in report['sources'].items()}
    if pins!=policy['pins']:raise ValueError('credit policy belongs to different source pins')
    issues=[];unmeasured=[];files=[];readers=[]
    pdf_record=None;pages=[]
    if build and not pdf:raise ValueError('a PDF is required with a build receipt')
    if pdf:
        pdf_record=file_record(pdf);text,warnings=extracted_text(pdf)
        pages=[normalized(s) for s in text.decode('utf-8').split('\f')]
        if warnings.strip():unmeasured.append({'kind':'pdf_extraction_warning','detail':warnings})
        if not build:
            unmeasured.append({'kind':'pdf_not_bound_to_source','detail':'No build receipt supplied.'})
        else:
            receipt=Path(build).resolve();b=json.loads(receipt.read_text(encoding='utf-8-sig'))
            declared=(receipt.parent/b['pdf']['path']).resolve()
            if declared!=Path(pdf).resolve() or b['pdf']['sha256']!=pdf_record['sha256']:
                raise ValueError('credit PDF differs from build receipt')
            if not b.get('commands') or any(c.get('exit_code')!=0 or c.get('timed_out') for c in b['commands']):
                raise ValueError('credit PDF has no successful build commands')
            if (receipt.parent/'source').resolve()!=source or b.get('assembly_sha256')!=digest(json_bytes(report)):
                raise ValueError('credit build does not bind the supplied source assembly')
            if b.get('source_inputs')!=report['files']:
                raise ValueError('credit build input manifest differs from assembly')
            for name,item in report['files'].items():
                p=member(source,name)
                if not p.is_file() or digest(p.read_bytes())!=item['sha256']:
                    issues.append({'kind':'built_input_changed','path':name})
    for component in policy['components']:
        cid=component['id'];state=component['state']
        if state=='unresolved':
            unmeasured.append({'component':cid,'kind':'unresolved_component','detail':component['reason']})
        if state=='not-applicable':
            if component['files'] or component['reader_checks']:
                raise ValueError('not-applicable component has requirements: '+cid)
            continue
        if state=='specified' and not component['files']:
            raise ValueError('specified component lacks its source notice: '+cid)
        for expected in component['files']:
            name=expected['path'];p=member(source,name)
            actual=digest(p.read_bytes()) if p.is_file() else None
            passed=actual==expected['sha256']
            files.append({'component':cid,'path':name,'expected_sha256':expected['sha256'],
                          'actual_sha256':actual,'pass':passed,'witness':expected['witness']})
            if not passed:issues.append({'component':cid,'kind':'notice_missing_or_changed','path':name})
        for check in component['reader_checks']:
            if not pdf:
                unmeasured.append({'component':cid,'kind':'reader_not_inspected','check':check['id']})
                continue
            matches=[i+1 for i,p in enumerate(pages) if all(normalized(s) in p for s in check['all_of'])]
            readers.append({'component':cid,'id':check['id'],'pages':matches,'pass':bool(matches)})
            if not matches:issues.append({'component':cid,'kind':'reader_credit_absent','check':check['id']})
    status='fail' if issues else ('incomplete' if unmeasured else 'pass')
    return {'schema':'olpkit.credits.v1','status':status,'policy_sha256':digest(json_bytes(policy)),
            'assembly':file_record(assembly),'pdf':pdf_record,'files':files,'reader_checks':readers,
            'issues':issues,'unmeasured':unmeasured,
            'limits':['Checks the separately specified notices, not copyright clearance.',
                      'Reader checks use actual PDF text and require the listed fragments together on a page.',
                      'Policy completeness still requires component provenance review; no language or mathematical certification.']}


def credits_command(source,policy_path,out,pdf=None,build=None):
    out=Path(out)
    if out.exists():raise ValueError('credit output exists; preserve the earlier evidence')
    policy=json.loads(Path(policy_path).read_text(encoding='utf-8-sig'))
    result=inspect_credits(source,policy,pdf,build)
    out.mkdir(parents=True);(out/'REPORT.json').write_bytes(json_bytes(result))
    print(f"G-CREDIT: {result['status']}; {len(result['files'])} notices; "
          f"{len(result['issues'])} defects; {len(result['unmeasured'])} unmeasured requirements")
    return 0 if result['status']=='pass' else 1
