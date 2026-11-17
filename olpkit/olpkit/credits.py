"""Check explicit component notices and actual reader attribution.

A notice check is not a legal opinion, linguistic review or permission grant.
Requirements come from a separately reviewed policy, never from the output alone.
"""
import json
from pathlib import Path
import re
import unicodedata
import tomllib

from .assembly import GitSnapshot, digest, json_bytes
from .cache import relative_path
from .pdfaudit import extracted_text,file_record
from .schemas import ROOT, validate_schema


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


def font_notices(index, build):
    root = ROOT / 'data/font-notices'
    manifest = member(root,index['path']).read_bytes()
    if digest(manifest)!=index['sha256']:
        raise ValueError('font notice manifest changed')
    packages = json.loads(manifest)
    licensed = {}
    outputs = {'licenses/fonts/manifest.json':manifest}
    for package, record in packages.items():
        if not re.fullmatch(r'[a-z0-9-]+',package) or not record['notices']:
            raise ValueError('missing or invalid font notice package')
        for name, hash_value in record['fonts'].items():
            if name in licensed:
                raise ValueError('ambiguous source for font '+name)
            licensed[name]=hash_value
        for name, hash_value in record['notices'].items():
            body=member(root,package+'/'+name).read_bytes()
            if digest(body)!=hash_value:
                raise ValueError('font licence differs from its witness: '+package+'/'+name)
            outputs['licenses/fonts/'+package+'/'+name]=body
    outlines={(Path(item['path']).name,item['sha256']) for item in build['recorder_inputs']
              if Path(item['path']).suffix.lower() in {'.otf','.ttf','.ttc','.pfb','.pfa'}}
    if set(licensed.items()) != outlines:
        raise ValueError('native font programs differ from the licensed inventory')
    return outputs


def photo_checks(source, assembly, build, policy, pages):
    """Check each native photo attribution against its own source and reader paragraph."""
    from .bookphotos import credit_rows
    from .macrophases import mask_comments
    from .build import build_job
    pcr=assembly["book_directory"]+"/"+build_job(assembly)+".pcr"
    observed={r["path"]:r["sha256"] for r in build["recorder_inputs"] if r["kind"]=="assembled-tree"}
    raw=member(source,pcr).read_bytes()
    if observed.get(pcr)!=digest(raw):
        raise ValueError("settled photo-credit list differs from TeX recorder")
    rows=credit_rows(raw.decode("utf-8-sig"))
    checks={r["photo_key"]:r for r in policy if "photo_key" in r}
    if {r["key"] for r in rows} != set(checks) or len(checks)!=len(policy):
        raise ValueError("reader photo policy and actual photo list differ")
    full=" ".join(pages)
    spans=[]
    for row in rows:
        lead=normalized(checks[row["key"]]["paragraph_lead"])
        starts=list(re.finditer(re.escape(lead)+r"\s+\d+\s*:",full))
        if len(starts)!=1:
            raise ValueError("cannot identify unique reader credit paragraph for "+row["key"])
        spans.append(starts[0].start())
    if spans!=sorted(spans):
        raise ValueError("photo-credit paragraphs differ from native order")
    spans.append(len(full))
    result=[]
    for i,row in enumerate(rows):
        check=checks[row["key"]]
        name=row["key"].removeprefix("photo-")
        original="assets/photos/"+name+"/"+name+"-credit.tex"
        translated="locale/"+assembly["locale"]+"/photocredits/"+name+"-credit.tex"
        left=member(source,original).read_bytes()
        right=member(source,translated).read_bytes()
        def links(data):
            return re.findall(r"\\href\s*\{([^{}]+)\}",mask_comments(data))
        def notice(data):
            return re.sub(r"\s+","",mask_comments(data).replace(r"\copyright",r"\textcircled{C}"))
        paragraph=full[spans[i]:spans[i+1]]
        ok=(observed.get(original)==digest(left) and observed.get(translated)==digest(right)
            and notice(right.decode("utf-8-sig"))==notice(row["credit_tex"])
            and links(left.decode("utf-8-sig"))==links(right.decode("utf-8-sig"))
            and all(normalized(s) in paragraph for s in check["all_of"]))
        result.append({"id":check["id"],"photo":row["key"],"pass":ok,
                       "original_sha256":digest(left),"translation_sha256":digest(right),
                       "pcr_sha256":digest(raw)})
    return result


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
        if state=='specified' and not component['files'] and 'font_manifest' not in component:
            raise ValueError('specified component lacks its source notice: '+cid)
        if 'font_manifest' in component:
            if component['category']!='fonts':
                raise ValueError('only font components may specify a font manifest')
            if build:
                try:
                    notices=font_notices(component['font_manifest'],b)
                except (ValueError, OSError) as error:
                    issues.append({'component':cid,'kind':'font_notice_mismatch','detail':str(error)})
                else:
                    files.extend({'component':cid,'path':name,'sha256':digest(body),'pass':True}
                                 for name,body in notices.items())
            else:
                unmeasured.append({'component':cid,'kind':'native_font_recorder_required'})
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
        photos=[r for r in component['reader_checks'] if 'photo_key' in r]
        if photos and build and pdf:
            bindings=photo_checks(source,report,b,photos,pages)
            readers.extend(bindings)
            issues.extend({'component':cid,'kind':'photo_credit_mismatch','check':r['id']}
                          for r in bindings if not r['pass'])
    status='fail' if issues else ('incomplete' if unmeasured else 'pass')
    return {'schema':'olpkit.credits.v1','status':status,'policy_sha256':digest(json_bytes(policy)),
            'assembly':file_record(assembly),'pdf':pdf_record,'files':files,'reader_checks':readers,
            'issues':issues,'unmeasured':unmeasured,
            'limits':['Checks the separately specified notices, not copyright clearance.',
                      'Reader checks use actual PDF text and require the listed fragments together on a page.',
                      'Policy completeness still requires component provenance review; no language or mathematical certification.']}


def rebind_source_links(original, upstream, before, after):
    """Update exact source URLs and the revision labels printed by matching TeX links."""
    base = re.escape(upstream.encode()) + rb'/(?:blob|tree)/'
    source_url = base + re.escape(before.encode())
    display = re.compile(rb'(\\href\{' + source_url + rb'\}\{)([a-f0-9]{7,40})\}')
    labels = set()

    def update_display(match):
        label = match[2].decode('ascii')
        if not before.startswith(label):
            return match[0]
        labels.add(label)
        return match[1] + after[:len(label)].encode('ascii') + b'}'

    original = display.sub(update_display, original)
    links = re.compile(source_url + rb'(?=[/}#)\s"]|$)')
    return links.sub(lambda m: m[0][:-len(before)] + after.encode('ascii'), original), labels


def edition_credit_paths(assembly):
    from .build import load_build_product
    from .importlock import pin_key
    _, book = load_build_product(assembly["product"])
    locale = assembly["locale"]
    if not re.fullmatch(r"[a-zA-Z0-9-]+", locale):
        raise ValueError("Invalid credit policy locale")
    filename = book["source_id"] + "-" + locale + ".json"
    pins = {key: row["commit"] for key, row in assembly["sources"].items()}
    root = ROOT / "data" / "credits"
    return root / "pins" / pin_key(pins) / filename, root / filename


def previous_credit_policy(previous):
    previous = Path(previous)
    if previous.is_file():
        return json.loads(previous.read_bytes())
    manifest = json.loads((previous / "WEB-EDITION.json").read_bytes())
    def read(name):
        raw = (previous / name).read_bytes()
        if digest(raw) != manifest["inputs"].get(name):
            raise ValueError("Published credit input differs from release manifest: " + name)
        return json.loads(raw)
    assembly = read("source/ASSEMBLY.json")
    subset = read("web/credits.json")
    scoped, fallback = edition_credit_paths(assembly)
    policy = json.loads((scoped if scoped.is_file() else fallback).read_bytes())
    checks = [{"id": c["id"], "reader_checks": c.get("reader_checks", [])} for c in policy["components"]]
    pins = {key: row["commit"] for key, row in assembly["sources"].items()}
    if (subset != {"components": checks} or policy["pins"] != pins
            or policy["locale"] != assembly["locale"] or policy["product"] != assembly["product"]):
        raise ValueError("Published credit checks differ from the registered policy for this edition")
    return policy


def rebind_credit_policy(source, previous, repo, out=None):
    source = Path(source).resolve()
    policy = previous_credit_policy(previous)
    validate_schema('credit-policy', policy)
    assembly = json.loads((source / 'ASSEMBLY.json').read_bytes())
    pins = {key: row['commit'] for key, row in assembly['sources'].items()}
    if (policy['locale'] != assembly['locale'] or policy['product'] != assembly['product']
            or policy['pins'].keys() != pins.keys()
            or any(value != pins[key] for key, value in policy['pins'].items() if key != 'olp')):
        raise ValueError('Expected the same edition, textbook and companion source revisions')
    old_pin = policy['pins']['olp']
    snapshot = GitSnapshot(repo, assembly['edition_commit'])
    contract = tomllib.loads(snapshot.read_many(['olp-edition.toml'])['olp-edition.toml'].decode('utf-8-sig'))
    if any(contract['pins'][key]['commit'] != value for key, value in pins.items()):
        raise ValueError('Assembled sources differ from the edition contract')
    edition = contract['repository'].removesuffix('.git').rstrip('/')
    upstream = contract['pins']['olp']['repository'].removesuffix('.git').rstrip('/')
    book = GitSnapshot(repo, assembly['book_commit'])
    previous_snapshots = {}
    updated_labels = set()
    for component in policy['components']:
        for notice in component['files']:
            content = member(source, notice['path']).read_bytes()
            if digest(content) == notice['sha256']:
                continue
            entry = assembly['files'][notice['path']]
            match = re.fullmatch(re.escape(edition) + r'/blob/([a-f0-9]{40})/(.+)', notice['witness'])
            if (not match or match[2] != entry['path'] or entry['source'] != 'book'
                    or entry['commit'] != book.commit):
                raise ValueError('Review the changed credit notice: ' + notice['path'])
            if match[1] not in previous_snapshots:
                previous_snapshots[match[1]] = GitSnapshot(repo, match[1])
            original = previous_snapshots[match[1]].read_many([match[2]])[match[2]]
            rebound, printed_labels = rebind_source_links(original, upstream, old_pin, pins['olp'])
            if (digest(original) != notice['sha256'] or book.read_many([match[2]])[match[2]] != content
                    or rebound != content):
                raise ValueError('Credit wording changed beyond its source revision: ' + notice['path'])
            updated_labels.update(printed_labels)
            notice.update(sha256=digest(content), witness=edition + '/blob/' + book.commit + '/' + match[2])
    for component in policy['components']:
        for check in component['reader_checks']:
            check['all_of'] = [pins['olp'][:len(term)] if term in updated_labels else term
                               for term in check['all_of']]
    policy['pins'] = pins
    output = Path(out) if out is not None else edition_credit_paths(assembly)[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    from .syncaccept import save_acceptance
    save_acceptance(output, json_bytes(policy))
    print('Credit policy recorded in ' + str(output))
    return 0


def credits_command(source,policy_path,out,pdf=None,build=None):
    out=Path(out)
    if out.exists():raise ValueError('credit output exists; preserve the earlier evidence')
    policy=json.loads(Path(policy_path).read_text(encoding='utf-8-sig'))
    result=inspect_credits(source,policy,pdf,build)
    out.mkdir(parents=True);(out/'REPORT.json').write_bytes(json_bytes(result))
    print(f"G-CREDIT: {result['status']}; {len(result['files'])} notices; "
          f"{len(result['issues'])} defects; {len(result['unmeasured'])} unmeasured requirements")
    return 0 if result['status']=='pass' else 1
