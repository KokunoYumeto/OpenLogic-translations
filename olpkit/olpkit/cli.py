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


def main(argv=None):
    p=argparse.ArgumentParser(prog='olpkit');sub=p.add_subparsers(dest='command',required=True)
    normalize=sub.add_parser('normalize');normalize.add_argument('--unit',required=True);normalize.add_argument('--policy',required=True);normalize.add_argument('--out')
    units=sub.add_parser('units').add_subparsers(dest='action',required=True);r=units.add_parser('registry');r.add_argument('--check',action='store_true')
    sync=sub.add_parser('sync').add_subparsers(dest='action',required=True);q=sync.add_parser('plan');q.add_argument('--from',dest='from_ref');q.add_argument('--to',dest='to_ref');q.add_argument('--out');q.add_argument('--check',metavar='FOLDER')
    v=sync.add_parser('verify-vendored');v.add_argument('--repo',required=True);v.add_argument('--dir',required=True);v.add_argument('--commit',required=True);v.add_argument('--components');v.add_argument('--out')
    e=sync.add_parser('edition');e.add_argument('--repo',required=True);e.add_argument('--ref',default='HEAD');e.add_argument('--plan',required=True);e.add_argument('--out',required=True)
    accept = sync.add_parser('accept', help='accept reviewed hub packets against a compiled candidate')
    for option in ('repo', 'packet', 'review', 'build', 'out'):
        accept.add_argument('--' + option, required=True)
    accept.add_argument('--ref', default='HEAD')
    verify = sync.add_parser('verify', help='verify one fully built product against the committed edition and sync packet')
    for option in ('repo', 'packet', 'review', 'acceptance', 'build', 'source-export', 'package-check', 'out'):
        verify.add_argument('--' + option, required=True)
    verify.add_argument('--ref', default='HEAD')
    verify.add_argument('--accepted-build', help='native build used by sync accept when the final book layout changed')
    release = sync.add_parser('release', help='stage or publish a verified product to its edition repository')
    release.add_argument('--job', required=True, help='release inputs and localized metadata')
    release.add_argument('--out', required=True, help='release staging and public readback directory')
    release.add_argument('--publish', action='store_true', help='publish the staged assets and check public downloads')
    lint=sub.add_parser('lint').add_subparsers(dest='action',required=True);l=lint.add_parser('structure');l.add_argument('--en',required=True);l.add_argument('--tr',required=True);l.add_argument('--json',action='store_true')
    for action in ('units','tokens'):
        l=lint.add_parser(action);l.add_argument('--repo');l.add_argument('--ref',default='HEAD');l.add_argument('--english',action='store_true');l.add_argument('--olp-pin');l.add_argument('--scope');l.add_argument('--out',required=True);l.add_argument('--check',action='store_true')
    edition=sub.add_parser('edition').add_subparsers(dest='action',required=True)
    e=edition.add_parser('validate');e.add_argument('--repo',required=True);e.add_argument('--metadata-dir')
    e=edition.add_parser('import-manifest');e.add_argument('--repo',required=True);e.add_argument('--adapter',required=True);e.add_argument('--out')
    fetch=sub.add_parser('fetch')
    source=fetch.add_mutually_exclusive_group(required=True)
    source.add_argument('--repo')
    source.add_argument('--product',help='fetch the pinned inputs for an English textbook')
    fetch.add_argument('--metadata-dir')
    fetch.add_argument('--olp-pin',help='full Open Logic commit for the English textbook')
    drivers=sub.add_parser('drivers');drivers.add_argument('--repo',required=True);drivers.add_argument('--metadata-dir');drivers.add_argument('--out',required=True);drivers.add_argument('--check',action='store_true');drivers.add_argument('--book',default='sets-logic-computation')
    assembly=sub.add_parser('assemble');assembly.add_argument('--repo',required=True);assembly.add_argument('--ref',default='HEAD');assembly.add_argument('--edition-ref');assembly.add_argument('--metadata-dir');assembly.add_argument('--product',default='slc-screen-pdf');assembly.add_argument('--out',required=True);assembly.add_argument('--check',action='store_true')
    build=sub.add_parser('build');build.add_argument('--repo');build.add_argument('--ref',default='HEAD');build.add_argument('--edition-ref');build.add_argument('--metadata-dir');build.add_argument('--product',default='slc-screen-pdf');build.add_argument('--out',required=True);build.add_argument('--english',action='store_true');build.add_argument('--olp-pin');build.add_argument('--resume',action='store_true')
    assembly.add_argument('--book-ledger');build.add_argument('--book-ledger')
    build.add_argument('--web-profile', help='Numbered web edition profile bound to the native PDF')
    export=sub.add_parser('export');export.add_argument('--source',required=True);export.add_argument('--product',choices=['cumulative-tex','source-zip','html','epub','accessible'],required=True);export.add_argument('--out',required=True);export.add_argument('--profile');export.add_argument('--build');export.add_argument('--credits');export.add_argument('--instructions');export.add_argument('--check-numbers',action='store_true');export.add_argument('--check-speech',action='store_true')
    figures=sub.add_parser('figures');figures.add_argument('--source',required=True);figures.add_argument('--context',required=True);figures.add_argument('--profile',required=True);figures.add_argument('--out',required=True);figures.add_argument('--resume',action='store_true')
    pdf=sub.add_parser('pdf').add_subparsers(dest='action',required=True)
    for action in ('compare','links','glyphs'):
        q=pdf.add_parser(action);q.add_argument('--first',required=True);q.add_argument('--second');q.add_argument('--first-build');q.add_argument('--second-build');q.add_argument('--out',required=True)
    check=sub.add_parser('check').add_subparsers(dest='action',required=True)
    product_check = check.add_parser('product', help='verify a book at its existing upstream pin')
    for name in ('repo', 'olp-pin', 'build', 'source-export', 'package-check', 'out'):
        product_check.add_argument('--' + name, required=True)
    product_check.add_argument('--ref', default='HEAD')
    q=check.add_parser('package',help='rebuild the modular and cumulative sources from the exported ZIP')
    q.add_argument('--export',required=True);q.add_argument('--build',required=True);q.add_argument('--out',required=True)
    q.add_argument('--mode', choices=['both','modular','cumulative'], default='both')
    q=check.add_parser('build');q.add_argument('--build',required=True);q.add_argument('--repo',required=True);q.add_argument('--metadata-dir')
    q.add_argument('--web-profile')
    for web_command in (build, q, verify, product_check):
        web_command.add_argument('--web-product', choices=('epub', 'accessible'), default='accessible',
                                 help='Verify the ordinary EPUB or the edition with complete formula speech')
    q=check.add_parser('credits');q.add_argument('--source',required=True);q.add_argument('--policy',required=True);q.add_argument('--out',required=True);q.add_argument('--pdf');q.add_argument('--build')
    q=check.add_parser('scale');q.add_argument('--pdf',required=True);q.add_argument('--specimen',required=True);q.add_argument('--language-data',required=True);q.add_argument('--out',required=True)
    status=sub.add_parser('status',help='compare committed source, translation and released product inputs')
    status.add_argument('--repo',required=True)
    status.add_argument('--ref',default='HEAD',help='edition commit to inspect')
    status.add_argument('--upstream',default=UPSTREAM,help='local upstream Git checkout or bare cache')
    status.add_argument('--to',help='compare the edition with this upstream revision')
    status.add_argument('--receipt',action='append',default=[],help='downloaded release.json; repeat per product')
    status.add_argument('--json',action='store_true')
    profile=sub.add_parser('web-profile',help='bind an existing language profile to an equivalent native book build')
    profile.add_argument('--build', required=True)
    profile.add_argument('--template', required=True)
    profile.add_argument('--sync-inputs', help='verified sync receipt, edition metadata, credit policy and book decisions')
    profile.add_argument('--out', required=True)
    speech = sub.add_parser('speech-sync', help='carry checked math readings between numbered HTML readers')
    for name in ('previous-reader', 'previous-packet', 'previous-store', 'reader', 'out'):
        speech.add_argument('--' + name, required=True)
    speech.add_argument('--review', help='editorial decisions for every changed occurrence')
    speech.add_argument('--previous-source-map', help='source locations bound to the previous speech store')
    offline = sub.add_parser('package-html', help='bundle a checked HTML reader with its local images and fonts')
    offline.add_argument('--export', required=True, help='paired HTML and EPUB export receipt')
    offline.add_argument('--out', required=True, help='destination ZIP file')
    web_source = sub.add_parser('package-web-source', help='bundle the editable textbook and its HTML/EPUB builder')
    for name in ('build', 'profile', 'source-export', 'web-export', 'pdf-profile', 'builder-licence', 'instructions', 'out'):
        web_source.add_argument('--' + name, required=True)
    a=p.parse_args(argv)
    try:
        if a.command=='package-web-source':
            from .websource import package
            return package(a)
        if a.command=='package-html':
            from .htmlarchive import package_html_reader
            return package_html_reader(a.export, a.out)
        if a.command=='speech-sync':
            from .speechsync import sync_speech
            return sync_speech(a)
        if a.command=='web-profile':
            from .webprofile import source_equivalent_profile
            return source_equivalent_profile(a.build,a.template,a.out,sync_inputs=a.sync_inputs)
        if a.command=='status':
            from .status import status_command
            return status_command(a.repo,a.ref,a.upstream,a.to,a.receipt,a.json)
        if a.command=='normalize':
            from .orthography import normalize_command
            return normalize_command(a.unit,a.policy,a.out)
        elif a.command=='figures':
            from .nativefigures import figures_command
            return figures_command(a.source,a.context,a.profile,a.out,resume=a.resume)
        elif a.command=='export':
            if a.product in ('html','epub','accessible'):
                from .webexport import export_web
                return export_web(a.source,a.product,a.out,a.profile,check_numbers=a.check_numbers,check_speech=a.check_speech)
            if a.check_speech or a.check_numbers:raise ValueError('reader checks require a web export product')
            from .sourceexport import export_command
            return export_command(a.source,a.product,a.out,a.profile,a.build,a.credits,a.instructions)
        elif a.command=='check':
            if a.action=='product':
                from .syncverify import verify_pinned_product
                return verify_pinned_product(a, CACHE)
            if a.action=='package':
                from .packagecheck import verify_package
                return verify_package(a.export,a.build,a.out,mode_choice=a.mode)
            if a.action=='build':
                from .buildchecks import verify_native_build
                report=verify_native_build(a.build,a.repo,CACHE,a.metadata_dir,a.web_profile,a.web_product)
                if any(gate['status']=='slot_occupied' for gate in report['gates'].values()):
                    return 75
                return int(any(gate['status']!='pass' for gate in report['gates'].values()))
            if a.action=='scale':
                from .pdfscale import scale_command
                return scale_command(a.pdf,a.specimen,a.language_data,a.out)
            from .credits import credits_command
            return credits_command(a.source,a.policy,a.out,a.pdf,a.build)
        elif a.command=='pdf':
            from .pdfaudit import pdf_command
            return pdf_command(a.action,a.first,a.second,a.out,a.first_build,a.second_build)
        elif a.command=='units':registry(a.check)
        elif a.command=='sync' and a.action=='plan':
            if not a.check and not all([a.from_ref,a.to_ref]):raise ValueError('plan requires --from and --to, or --check FOLDER')
            if not a.check and not a.out:
                record,_=delta(a.from_ref,a.to_ref)
                if record['files']:raise ValueError('a nonempty sync plan requires --out')
                print('0 changed files');return 0
            plan(a.from_ref,a.to_ref,a.check or a.out,bool(a.check))
        elif a.command=='sync' and a.action=='edition':
            from .syncedition import edition_command
            return edition_command(a.repo,a.ref,a.plan,CACHE,a.out)
        elif a.command=='sync' and a.action=='accept':
            from .syncaccept import accept
            return accept(a.repo, a.ref, a.packet, a.review, a.build, a.out, CACHE)
        elif a.command=='sync' and a.action=='verify':
            from .syncverify import verify_product
            return verify_product(a, CACHE)
        elif a.command=='sync' and a.action=='release':
            from .syncrelease import publish
            return publish(a.job, a.out, a.publish)
        elif a.command=='sync':
            from .vendored import verify
            verify(a.repo,a.dir,commit(a.commit),CACHE,a.components,a.out)
        elif a.command=='drivers':
            from .drivers import drivers_command
            drivers_command(a.repo,a.metadata_dir,CACHE,a.out,a.check,a.book)
        elif a.command=='assemble':
            from .assembly import assemble_command
            assemble_command(a.repo,a.ref,a.edition_ref,a.metadata_dir,CACHE,a.out,a.product,a.check,book_ledger=a.book_ledger)
        elif a.command=='build':
            from .build import build_command
            return build_command(a.repo,a.ref,a.edition_ref,a.metadata_dir,CACHE,a.out,a.product,a.english,a.olp_pin,a.resume,book_ledger=a.book_ledger,web_profile=a.web_profile,web_product=a.web_product)
        elif a.command=='lint' and a.action in ('units','tokens'):
            from .unitlint import lint_units
            return lint_units(a.repo,a.ref,CACHE,a.out,a.english,a.olp_pin,a.scope,a.check,a.action=='tokens')
        elif a.command=='fetch':
            if a.product:
                if not a.olp_pin or a.metadata_dir:
                    raise ValueError('English textbook fetch requires --product and --olp-pin')
                from .build import fetch_reference
                fetch_reference(CACHE,a.olp_pin,a.product)
            else:
                if a.olp_pin:
                    raise ValueError('edition fetch uses the pins in olp-edition.toml')
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
