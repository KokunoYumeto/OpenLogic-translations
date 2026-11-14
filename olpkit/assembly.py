"""Assemble pinned sources and canonical translations without running TeX.

Legacy input locations are declared in data. Textbook prose patches are never
executed: unresolved overlays remain an explicit native-equivalence limitation.
"""
from collections import Counter
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib

from .cache import SourceCache, relative_path
from .drivers import generate_drivers
from .edition import git_blob
from .schemas import ROOT, validate_schema
from .shims import apply_shims


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+'\n').encode('utf-8')


class GitSnapshot:
    """Read selected raw blobs at one immutable commit; never lazy-fetch."""
    def __init__(self, repo, ref):
        self.repo = Path(repo).resolve()
        self.env = {**os.environ, 'GIT_TERMINAL_PROMPT':'0', 'GIT_NO_LAZY_FETCH':'1'}
        if not ref or ref.startswith('-') or any(c in ref for c in '\r\n\0'):
            raise ValueError('invalid edition reference')
        self.commit = self.run('rev-parse', '--verify', ref+'^{commit}').decode().strip()
        self.entries = {}
        for row in self.run('ls-tree', '-rz', '--full-tree', self.commit).split(b'\0'):
            if row:
                meta, name = row.split(b'\t', 1)
                mode, kind, oid = meta.decode().split()
                self.entries[name.decode('utf-8')] = (mode, kind, oid)

    def run(self, *args):
        p = subprocess.run(['git', '-C', str(self.repo), '-c', 'gc.auto=0',
                            '-c', 'maintenance.auto=false', *args],
                           capture_output=True, env=self.env, timeout=120)
        if p.returncode:
            raise ValueError('local Git '+args[0]+' failed for '+self.repo.name)
        return p.stdout

    def read_many(self, names):
        names = sorted(set(names))
        for name in names:
            relative_path(name)
            if name not in self.entries:
                raise ValueError('pinned edition input absent: '+name)
            mode, kind, _ = self.entries[name]
            if kind!='blob' or mode not in ('100644', '100755'):
                raise ValueError('unsupported edition input: '+name)
        outputs = {}
        p = subprocess.Popen(['git','-C',str(self.repo),'cat-file','--batch'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, env=self.env)
        try:
            for name in names:
                oid = self.entries[name][2]
                p.stdin.write((oid+'\n').encode()); p.stdin.flush()
                header = p.stdout.readline(200).decode().strip().split()
                if len(header)!=3 or header[:2]!=[oid,'blob']:
                    raise ValueError('local blob absent; explicitly fetch before assembly: '+name)
                size = int(header[2])
                # A malformed member must not allocate an unbounded process buffer.
                if size>100_000_000:
                    raise ValueError('edition member exceeds the assembly file limit: '+name)
                data = p.stdout.read(size)
                if len(data)!=size or p.stdout.read(1)!=b'\n' or git_blob(data)!=oid:
                    raise ValueError('edition blob differs: '+name)
                outputs[name] = data
            p.stdin.close()
            if p.wait(timeout=20):
                raise ValueError('local edition blob read failed')
        finally:
            if p.poll() is None:
                p.kill(); p.wait(timeout=10)
            p.stdout.close()
            if not p.stdin.closed:
                p.stdin.close()
        return outputs


def locale_marks(data, locale):
    """Insert only OLP locale flags; preserve wording and ignore commented code."""
    text = data.decode('utf-8-sig')
    count = 0
    pattern = re.compile(r'\\ol(?:file|chapter|part)id(?![A-Za-z])(?:\[([^\]\r\n]*)\])?')
    lines = []
    for line in text.splitlines(keepends=True):
        comment = re.search(r'(?<!\\)(?:\\\\)*%', line)
        split = comment.start() if comment else len(line)
        def mark(match):
            nonlocal count
            if match.group(1) not in (None, locale):
                raise ValueError('canonical unit contains a different locale marker')
            if match.group(1) is None:
                count += 1
                return match.group(0)+'['+locale+']'
            return match.group(0)
        lines.append(pattern.sub(mark,line[:split])+line[split:])
    # Preserve a BOM if it existed; only the locale flag is an assembly change.
    result = ''.join(lines).encode('utf-8')
    return (b'\xef\xbb\xbf'+result if data.startswith(b'\xef\xbb\xbf') else result),count


def assemble_units(edition, units, english, targets, registry):
    """Validate the entire pinned unit set, including explicit untranslated slots."""
    active = [u for u in units if u['src']=='olp' and u['state']!='retired']
    for u in units:
        validate_schema('unit',u)
    if len({u['id'] for u in units})!=len(units) or len({(u['src'],u['path']) for u in units})!=len(units):
        raise ValueError('duplicate unit identity or source path')
    expected = {p for p in english if p.startswith('content/') and p.endswith('.tex')}
    if {u['path'] for u in active}!=expected:
        raise ValueError('ledger does not cover the exact pinned content tree')
    expected_targets = {edition['paths']['content']+'/'+p.removeprefix('content/') for p in expected}
    if set(targets)-expected_targets:
        raise ValueError('canonical target tree contains units outside the pinned source ledger')
    output, receipts = {}, []
    for u in sorted(active,key=lambda x:x['id']):
        path = u['path']; relative_path(path)
        if registry.get(path)!=u['id']:
            raise ValueError(u['id']+': unit identity differs from registry')
        original = english[path]
        target_path = edition['paths']['content']+'/'+path.removeprefix('content/')
        current = u['src_blob']==git_blob(original)
        observed = 'new' if u['tr_sha256'] is None else ('current' if current else 'stale')
        if observed!=u['state']:
            raise ValueError(u['id']+': state differs from source pin or recorded target')
        if current and u['src_sha256']!=digest(original):
            raise ValueError(u['id']+': source SHA-256 differs from pinned bytes')
        if observed=='new':
            if target_path in targets:
                raise ValueError(u['id']+': unrecorded target exists for a new unit')
            body,marks = original,0
        else:
            if target_path not in targets or digest(targets[target_path])!=u['tr_sha256']:
                raise ValueError(u['id']+': translated bytes differ from ledger')
            body,marks = locale_marks(targets[target_path],edition['locale'])
        output[path] = body
        receipts.append({'id':u['id'],'path':path,'state':observed,
                         'source_sha256':digest(original),'target_sha256':u['tr_sha256'],
                         'assembled_sha256':digest(body),'locale_flags_inserted':marks,
                         'english_fill':observed=='new'})
    return output,receipts


class AssemblyTree:
    def __init__(self):
        self.files = {}
        self.origins = {}
        self.folded = {}

    def add(self, path, data, origin, replace=False):
        relative_path(path)
        if path.casefold() in self.folded and self.folded[path.casefold()]!=path:
            raise ValueError('case-colliding assembly path: '+path)
        if path in self.files and not replace:
            raise ValueError('unaccounted assembly collision: '+path)
        previous = self.origins.get(path)
        self.files[path] = data
        self.origins[path] = {**origin,'bytes':len(data),'sha256':digest(data)}
        if previous:
            self.origins[path]['replaces'] = previous
        self.folded[path.casefold()] = path


def write_assembly(tree, report, folder, check=False):
    folder = Path(folder).resolve()
    boundary = (ROOT.parent/'out').resolve()
    if folder==boundary or not folder.is_relative_to(boundary):
        raise ValueError('assembly output must be a named child of the builder output directory')
    outputs = {**tree.files, 'ASSEMBLY.json':json_bytes(report)}
    if folder.exists():
        actual = {}
        for p in folder.rglob('*'):
            if p.is_symlink() or not p.resolve().is_relative_to(folder):
                raise ValueError('linked assembly output member')
            if p.is_file():
                actual[p.relative_to(folder).as_posix()] = p
        if set(actual)!=set(outputs) or any(actual[n].read_bytes()!=b for n,b in outputs.items() if n in actual):
            raise ValueError('existing assembly differs; preserve it and use a new output folder')
        return
    if check:
        raise ValueError('assembly output absent')
    folder.mkdir(parents=True)
    for name,body in outputs.items():
        target = folder/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)


def assemble_command(repo, ref, edition_ref, metadata_dir, cache_root, out,
                     product='slc-screen-pdf', check=False, data_root=None, book_ledger=None):
    data_root = Path(data_root) if data_root else ROOT/'data'
    book_snapshot = GitSnapshot(repo,ref)
    edition_snapshot = GitSnapshot(repo,edition_ref or ref)
    if metadata_dir:
        metadata = Path(metadata_dir).resolve()
        contract_files = {}
        for name in ('olp-edition.toml','units.jsonl'):
            path = metadata/name
            if path.is_symlink() or not path.resolve().is_relative_to(metadata):
                raise ValueError('linked edition contract')
            contract_files[name] = path.read_bytes()
    else:
        contract_files = edition_snapshot.read_many(['olp-edition.toml','units.jsonl'])
    edition = tomllib.loads(contract_files['olp-edition.toml'].decode('utf-8-sig'))
    validate_schema('olp-edition',edition)
    if product not in edition['products']:
        raise ValueError('product is not declared by the edition')
    # Products may have distinct book layers for the same language. Keep the
    # established single-product profiles as an exact backwards-compatible fallback.
    profile_path = data_root/'assembly'/edition['locale']/(product+'.json')
    if not profile_path.is_file():profile_path = data_root/'assembly'/(edition['locale']+'.json')
    profile_bytes = profile_path.read_bytes()
    profile = json.loads(profile_bytes)
    validate_schema('assembly-profile',profile)
    if profile['locale']!=edition['locale'] or profile['product']!=product:
        raise ValueError('assembly profile differs from the requested edition/product')
    units = [json.loads(s) for s in contract_files['units.jsonl'].decode('utf-8-sig').splitlines() if s.strip()]
    cache = SourceCache(cache_root)
    sources, source_receipts = {}, {}
    for source,pin in edition['pins'].items():
        if source not in cache.sources or pin['repository']!=cache.sources[source]['repository']:
            raise ValueError('unregistered assembly source: '+source)
        folder,receipt = cache.require(source,pin['commit'])
        sources[source] = (folder,receipt)
        source_receipts[source] = {'commit':pin['commit'],
                                  'manifest_sha256':digest(cache.locations(source,pin['commit'])[2].read_bytes())}
    book = tomllib.loads((data_root/'books'/(profile['book']+'.toml')).read_text(encoding='utf-8'))
    book_layer = None
    if 'book_contract' in profile:
        from .booklayer import load_book_layer
        folder,receipt = sources[profile['source_id']]
        source_files = {name:(folder/name).read_bytes() for name in receipt['files']}
        book_layer = load_book_layer(book_snapshot,profile,book,edition,source_files,book_ledger)
    else:
        if book_ledger is not None:
            raise ValueError('--book-ledger requires a native book contract')
        manifest = json.loads(book_snapshot.read_many([profile['manifest']])[profile['manifest']])
        for source,field in profile['manifest_pins'].items():
            if manifest['sources'][field]['commit']!=edition['pins'][source]['commit']:
                raise ValueError('book and edition pins differ: '+source)
    tree = AssemblyTree()
    olp_folder,olp_receipt = sources['olp']
    english = {name:(olp_folder/name).read_bytes() for name in olp_receipt['files']}
    patched,shims = apply_shims(english,edition,data_root/'shims')
    for name,body in patched.items():
        if any(fnmatchcase(name,p) for p in profile['upstream_include']):
            tree.add(name,body,{'source':'olp','commit':edition['pins']['olp']['commit'],
                               'path':name,'source_sha256':digest(english[name]),
                               'shims':[s['id'] for s in shims if s['path']==name]})
    prefix = 'locale/'+edition['locale']
    book_prefix = prefix+'/courses/'+profile['book']
    for asset in profile['assets']:
        folder,receipt = sources[asset['source']]
        for name in sorted(receipt['files']):
            if any(fnmatchcase(name,p) for p in asset['include']):
                tree.add(asset['to']+'/'+name,(folder/name).read_bytes(),
                         {'source':asset['source'],'commit':receipt['commit'],'path':name})
    target_root = edition['paths']['content']+'/'
    target_names = [p for p in edition_snapshot.entries if p.startswith(target_root) and p.endswith('.tex')]
    targets = edition_snapshot.read_many(target_names)
    registry = dict(line.split('\t')[::-1] for line in (data_root/'units/olp-units.tsv').read_text(encoding='utf-8').splitlines()[1:])
    unit_files,unit_receipts = assemble_units(edition,units,english,targets,registry)
    receipt_by_path = {u['path']:u for u in unit_receipts}
    for path,body in unit_files.items():
        row = receipt_by_path[path]
        tree.add(prefix+'/'+path,body,{'source':'english-fill' if row['english_fill'] else 'edition',
                                     'commit':edition['pins']['olp']['commit'] if row['english_fill'] else edition_snapshot.commit,
                                     'path':path if row['english_fill'] else target_root+path.removeprefix('content/'),
                                     'unit':row['id'],'locale_flags_inserted':row['locale_flags_inserted']})
    transfers = []
    for transfer in profile['files']:
        snapshot = edition_snapshot if transfer['source']=='edition' else book_snapshot
        name = transfer['from']; relative_path(name)
        data = snapshot.read_many([name])[name]
        original_hash = digest(data)
        changes = []
        for change in transfer.get('transforms',[]):
            before,after = change['before'].encode(),change['after'].encode()
            if data.count(before)!=change['matches']:
                raise ValueError('assembly alias '+change['id']+': expected '+str(change['matches'])+' matches')
            data = data.replace(before,after)
            changes.append(change['id'])
        destination = transfer['to'].replace('{locale}',edition['locale']).replace('{book}',profile['book'])
        tree.add(destination,data,{'source':transfer['source'],'commit':snapshot.commit,'path':name,
                                   'source_sha256':original_hash,'transforms':changes})
        transfers.append({'from':name,'to':destination,'transforms':changes})
    for rule in profile['trees']:
        snapshot = edition_snapshot if rule['source']=='edition' else book_snapshot
        names = sorted(p for p in snapshot.entries if p.startswith(rule['from']+'/') and
                       any(fnmatchcase(p[len(rule['from'])+1:],g) for g in rule['include']))
        if not names:
            raise ValueError('assembly input tree empty: '+rule['from'])
        for name,body in snapshot.read_many(names).items():
            relative = name[len(rule['from'])+1:]
            if relative.startswith('content/'):
                raise ValueError('textbook layer contains copied content')
            destination = rule['to'].replace('{locale}',edition['locale']).replace('{book}',profile['book'])+'/'+relative
            tree.add(destination,body,{'source':rule['source'],'commit':snapshot.commit,'path':name})
    slc_folder,_ = sources[profile['source_id']]
    driver_sources = {name:(slc_folder/name).read_bytes() for name in book['drivers']}
    drivers,driver_report = generate_drivers(edition,driver_sources,profile['book'],data_root)
    for name,body in drivers.items():
        tree.add(book_prefix+'/'+name,body,{'source':'generated-driver','driver_report_sha256':digest(json_bytes(driver_report))})
    for name in profile['required_book_files']:
        if book_prefix+'/'+name not in tree.files:
            raise ValueError('translated book input absent: '+name)
    if book_layer:
        from .booklayer import check_assembled_book_layer
        check_assembled_book_layer(book_layer,tree.files,book_prefix)
    obligations = []
    for name in profile['legacy_overlays']:
        if name in book_snapshot.entries:
            body = book_snapshot.read_many([name])[name]
            obligations.append({'path':name,'sha256':digest(body),'bytes':len(body),
                                'action':'reconcile into canonical units/tokens; not executed by assembly'})
    report = {'schema':'olpkit.assembly.v1','product':product,'locale':edition['locale'],
              'edition_commit':edition_snapshot.commit,'book_commit':book_snapshot.commit,
              'contract_hashes':{n:digest(b) for n,b in contract_files.items()},
              'assembly_profile_sha256':digest(profile_bytes),'sources':source_receipts,
              'book_directory':book_prefix,'files':tree.origins,'units':unit_receipts,
              'coverage':dict(Counter(u['state'] for u in unit_receipts)),
              'english_fill_count':sum(u['english_fill'] for u in unit_receipts),
              'shims':shims,'drivers':driver_report,'aliases':transfers,
              'unreconciled_legacy_inputs':obligations,
              'implementation_sha256':{name:digest((Path(__file__).parent/name).read_bytes())
                                       for name in ('assembly.py','cache.py','drivers.py','shims.py','schemas.py')},
              'native_reader_equivalence':'not checked; assembly is not a rendered release',
              'network_fetches':0,'tex_runs':0}
    if 'driver' in profile:report['driver']=profile['driver']
    if book_layer:
        report['book_layer']=book_layer
        report['implementation_sha256']['booklayer.py']=digest((Path(__file__).parent/'booklayer.py').read_bytes())
    write_assembly(tree,report,out,check)
    print(f'assembled {len(tree.files)} files; {len(unit_receipts)} units; '
          f'{report["english_fill_count"]} English fill-ins; {len(shims)} shims; '
          f'{len(obligations)} legacy inputs still require source reconciliation')
    return report
