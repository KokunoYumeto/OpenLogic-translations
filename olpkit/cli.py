import argparse
import csv
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

from .structure import differences

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('OLPKIT_CACHE', str(ROOT.parent / 'cache')))
UPSTREAM = CACHE / 'OpenLogic.git'
BASE = '9620cc73f9c8e0ad003c514a5d3748f29611c4c0'
CURRENT = '1e960beff9ed7835bf3e3f1335e21af3439cd107'


def git(*args):
    return subprocess.run(['git', '--git-dir', str(UPSTREAM), *args], check=True, capture_output=True).stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def commit(ref):
    if not ref or ref.startswith('-'):
        raise ValueError('expected a commit reference')
    return git('rev-parse', '--verify', ref + '^{commit}').decode().strip()


def tree(ref):
    result = {}
    for line in git('ls-tree', '-rz', ref).split(b'\0'):
        if not line:
            continue
        meta, path = line.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind == 'blob':
            result[path.decode('utf-8')] = oid
    return result


def blob(oid):
    return git('cat-file', 'blob', oid) if oid else b''


def manifest_maps():
    folder = CACHE / 'edition-manifests'
    jv = json.loads((folder / 'jv.json').read_text(encoding='utf-8'))
    gu = json.loads((folder / 'gu.json').read_text(encoding='utf-8'))
    maps = {'jv': {x['english']['path'].removeprefix('upstream/'): x['id'] for x in jv['units']}, 'gu': {x['path']: x['id'] for x in gu['units']}}
    for locale in ['bn', 'mr']:
        rows = [json.loads(s) for s in (folder / (locale + '.jsonl')).read_text(encoding='utf-8').splitlines() if s.strip()]
        maps[locale] = {x['source_path']: x['unit_id'] for x in rows}
    return maps


def registry(check=False):
    maps = manifest_maps()
    source = {p for p in tree(BASE) if p.startswith('content/') and p.endswith('.tex')}
    canonical = maps['jv']
    if set(canonical) != source or len(canonical) != 722 or set(canonical.values()) != {f'OLP-{i:04d}' for i in range(1, 723)}:
        raise ValueError('canonical unit identities do not match the source tree')
    rows = ['id\tpath'] + [f'{unit}\t{path}' for path, unit in sorted(canonical.items(), key=lambda x: x[1])]
    agreement = ['repository\trows_compared\tunit_id_differences\tmissing_paths\textra_paths']
    names = {'jv':'OpenLogic-jv-Latn-ID','gu':'OpenLogic-gu-Gujr-IN','bn':'OpenLogic-bn-Beng-IN','mr':'OpenLogic-mr-Deva-IN'}
    for locale, mapping in maps.items():
        common = set(mapping) & source
        agreement.append(f'{names[locale]}\t{len(common)}\t{sum(mapping[p] != canonical[p] for p in common)}\t{len(source-set(mapping))}\t{len(set(mapping)-source)}')
    outputs = {ROOT/'data/units/olp-units.tsv': ('\n'.join(rows)+'\n').encode(), ROOT/'data/units/UNIT_ID_AGREEMENT.tsv': ('\n'.join(agreement)+'\n').encode()}
    for path, data in outputs.items():
        if check:
            if not path.exists() or path.read_bytes() != data:
                raise ValueError(f'generated registry differs: {path.name}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print('722 units; numbers OLP-0001 to OLP-0722 unique; paths equal content/**/*.tex at 9620cc73')
    return canonical


def delta(from_ref, to_ref):
    before, after = commit(from_ref), commit(to_ref)
    oldtree, newtree = tree(before), tree(after)
    ids = manifest_maps()['jv']
    scope = set((CACHE/'edition-manifests/slc-scope.txt').read_text(encoding='utf-8').splitlines())
    instructions = json.loads((ROOT/'data/sync-instructions.json').read_text(encoding='utf-8'))
    files = []
    packets = {}
    next_id = max(int(x.split('-')[1]) for x in ids.values()) + 1
    for line in git('diff', '--name-status', '-M', before, after, '--', 'content', 'sty', 'include', 'bib', 'assets', 'open-logic-config.sty', 'open-logic-locale.sty').decode().splitlines():
        parts = line.split('\t');status=parts[0];oldpath=parts[1];path=parts[-1]
        old_oid, new_oid = oldtree.get(oldpath), newtree.get(path)
        en0, en1 = blob(old_oid), blob(new_oid)
        is_unit = path.startswith('content/') and path.endswith('.tex')
        uid = ids.get(oldpath) or ids.get(path)
        if is_unit and not uid:
            uid = f'OLP-{next_id:04d}';next_id += 1
        hunks = git('diff', '--no-ext-diff', '--no-color', '--no-renames', before, after, '--', oldpath, path).decode('utf-8')
        instruction = instructions.get(path, {'class':'unclassified','check':'Compare the complete source change and its target context; classification requires review.'})
        record = {'path':path,'old_path':oldpath,'unit_id':uid if is_unit else None,'kind':'content_unit' if is_unit else 'build_file','status':status,'old_blob':old_oid,'new_blob':new_oid,'old_sha256':digest(en0) if old_oid else None,'new_sha256':digest(en1) if new_oid else None,'hunks':hunks,'textbooks':['slc'] if path in scope else [],'required_build_files':['sty/open-logic.sty'] if path=='content/proof-theory/proof-search/tableaux.tex' else [],**instruction}
        files.append(record)
        if is_unit:
            packets[uid+'.md']=(f'# {uid}: {path}\n\nClassification: {record["class"]}\n\n{record["check"]}\n\nRecord a disposition: carried, patched, retranslated, source-only, build-only or conflict. Preserve existing corrections and consult the edition canon for wording. Record both readings and a reason for conflicts.\n\n## English before\n\n```latex\n'+en0.decode('utf-8')+'\n```\n\n## English after\n\n```latex\n'+en1.decode('utf-8')+'\n```\n\n## Upstream difference\n\n```diff\n'+hunks+'\n```\n').encode('utf-8')
    return {'schema':'olpkit.upstream-delta.v1','repository':'https://github.com/OpenLogicProject/OpenLogic','from':before,'to':after,'files':files}, packets


def plan(from_ref, to_ref, out, check=False):
    folder=Path(out)
    if check:
        existing=json.loads((folder/'UPSTREAM_DELTA.json').read_text(encoding='utf-8'));from_ref=existing['from'];to_ref=existing['to']
    record, packets=delta(from_ref,to_ref)
    outputs={folder/'UPSTREAM_DELTA.json':json_bytes(record),**{folder/'packets'/name:data for name,data in packets.items()}}
    for path,data in outputs.items():
        if check:
            if not path.exists() or path.read_bytes()!=data:raise ValueError(f'delta/packet differs from live git blobs: {path.name}')
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if check:
        actual={p.name for p in (folder/'packets').glob('*.md')}
        if actual!=set(packets):raise ValueError('packet set contains missing or unexpected units')
        n=sum(bool(x['old_blob'])+bool(x['new_blob']) for x in record['files'])
        print(f'{n} of {n} blob ids equal git; {len(packets)} packets complete; imported by slc: {sum("slc" in x["textbooks"] for x in record["files"])}')
    else:
        units=[x for x in record['files'] if x['kind']=='content_unit'];builds=[x for x in record['files'] if x['kind']=='build_file']
        if not record['files']:print('0 changed files');return
        counts={s:sum(x['status'].startswith(s) for x in units) for s in ['M','A','D','R']}
        print(f'{len(record["files"])} changed files: {counts["M"]} content units modified, {counts["A"]} added, {counts["D"]} deleted, {counts["R"]} renamed; {len(builds)} build file'+('s' if len(builds)!=1 else '')+' ('+', '.join(x['path'] for x in builds)+')')


def verify_vendored(repo,directory,ref):
    root=Path(repo).resolve();folder=(root/directory).resolve()
    if not folder.is_relative_to(root):raise ValueError('vendored directory escapes the repository')
    expected=tree(commit(ref));failures=[];count=0
    for path in folder.rglob('*'):
        if not path.is_file():continue
        rel=path.relative_to(folder).as_posix();count+=1
        if rel not in expected or path.read_bytes()!=blob(expected[rel]):failures.append(rel)
    if not count:raise ValueError('vendored directory is empty or missing')
    if failures:raise ValueError(f'{len(failures)} vendored files differ or are not upstream: '+', '.join(failures[:12]))
    print(f'{count} of {count} files equal upstream')


def main(argv=None):
    p=argparse.ArgumentParser(prog='olpkit');sub=p.add_subparsers(dest='command',required=True)
    units=sub.add_parser('units').add_subparsers(dest='action',required=True);r=units.add_parser('registry');r.add_argument('--check',action='store_true')
    sync=sub.add_parser('sync').add_subparsers(dest='action',required=True);q=sync.add_parser('plan');q.add_argument('--from',dest='from_ref');q.add_argument('--to',dest='to_ref');q.add_argument('--out');q.add_argument('--check',metavar='FOLDER')
    v=sync.add_parser('verify-vendored');v.add_argument('--repo',required=True);v.add_argument('--dir',required=True);v.add_argument('--commit',required=True)
    lint=sub.add_parser('lint').add_subparsers(dest='action',required=True);l=lint.add_parser('structure');l.add_argument('--en',required=True);l.add_argument('--tr',required=True);l.add_argument('--json',action='store_true')
    edition=sub.add_parser('edition').add_subparsers(dest='action',required=True)
    e=edition.add_parser('validate');e.add_argument('--repo',required=True);e.add_argument('--metadata-dir')
    e=edition.add_parser('import-manifest');e.add_argument('--repo',required=True);e.add_argument('--adapter',required=True);e.add_argument('--out')
    fetch=sub.add_parser('fetch');fetch.add_argument('--repo',required=True);fetch.add_argument('--metadata-dir')
    drivers=sub.add_parser('drivers');drivers.add_argument('--repo',required=True);drivers.add_argument('--metadata-dir');drivers.add_argument('--out',required=True);drivers.add_argument('--check',action='store_true');drivers.add_argument('--book',default='sets-logic-computation')
    assembly=sub.add_parser('assemble');assembly.add_argument('--repo',required=True);assembly.add_argument('--ref',default='HEAD');assembly.add_argument('--edition-ref');assembly.add_argument('--metadata-dir');assembly.add_argument('--product',default='slc-screen-pdf');assembly.add_argument('--out',required=True);assembly.add_argument('--check',action='store_true')
    a=p.parse_args(argv)
    try:
        if a.command=='units':registry(a.check)
        elif a.command=='sync' and a.action=='plan':
            if not a.check and not all([a.from_ref,a.to_ref,a.out]):raise ValueError('plan requires --from, --to and --out, or --check FOLDER')
            plan(a.from_ref,a.to_ref,a.check or a.out,bool(a.check))
        elif a.command=='sync':verify_vendored(a.repo,a.dir,a.commit)
        elif a.command=='drivers':
            from .drivers import drivers_command
            drivers_command(a.repo,a.metadata_dir,CACHE,a.out,a.check,a.book)
        elif a.command=='assemble':
            from .assembly import assemble_command
            assemble_command(a.repo,a.ref,a.edition_ref,a.metadata_dir,CACHE,a.out,a.product,a.check)
        elif a.command=='fetch':
            from .cache import fetch_edition
            fetch_edition(a.repo,a.metadata_dir,CACHE)
        elif a.command=='edition':
            from .edition import import_manifest,validate_edition
            if a.action=='import-manifest':import_manifest(a.repo,a.adapter,a.out,UPSTREAM)
            else:validate_edition(a.repo,a.metadata_dir,UPSTREAM)
        else:
            d=differences(Path(a.en).read_text(encoding='utf-8-sig'),Path(a.tr).read_text(encoding='utf-8-sig'))
            if a.json:print(json.dumps(d,ensure_ascii=False,indent=2))
            print(f'{len(d)} differences'+(': '+', '.join(x['rule'] for x in d) if d else ''))
            return int(bool(d))
    except (ValueError,FileNotFoundError,subprocess.CalledProcessError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 1
    return 0
