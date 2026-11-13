"""Convert existing manifests without translating or assigning invented authorship."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tomllib

from .schemas import ROOT, validate_schema


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_tree(cache, pin):
    output = subprocess.run(['git', '--git-dir', str(cache), 'ls-tree', '-rz', pin, '--', 'content'], check=True, capture_output=True).stdout
    result = {}
    for entry in output.split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        path = path.decode('utf-8')
        if kind == 'blob' and path.endswith('.tex'):
            result[path] = oid
    return result


def safe_path(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('unsafe relative path: ' + relative)
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('path escapes the edition: ' + relative)
    return result


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def read_manifest(repo, adapter):
    path = safe_path(repo, adapter['manifest'])
    data = path.read_bytes()
    if adapter['format'] == 'jsonl':
        rows = [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]
        pins = {row[adapter['pin_key']] for row in rows}
        if len(pins) != 1:
            raise ValueError('source manifest does not have one coherent pin')
        pin = pins.pop()
    else:
        manifest = json.loads(data.decode('utf-8-sig'))
        rows = manifest['units']
        pin = manifest[adapter['pin_key']]
    return rows, pin, sha256(data)


def value_at(row, path):
    for key in path.split('.'):
        row = row[key]
    return row


def toml_string(value):
    return json.dumps(value, ensure_ascii=False)


def render_edition(data):
    """Render the initial simple contract; later owner settings stay owner-managed."""
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            continue
        lines.append(f'{key} = {toml_string(value)}')
    for table in ['paths', 'conversion']:
        lines.append(f'\n[{table}]')
        for key, value in data[table].items():
            lines.append(f'{key} = {toml_string(value)}')
    for name, pin in data['pins'].items():
        lines.append(f'\n[pins.{name}]')
        for key, value in pin.items():
            lines.append(f'{key} = {toml_string(value)}')
    return '\n'.join(lines) + '\n'


def make_contract(repo, adapter_name, cache):
    repo = Path(repo).resolve()
    if not adapter_name.isidentifier():
        raise ValueError('invalid adapter name')
    adapter = tomllib.loads((ROOT / 'data/imports' / (adapter_name + '.toml')).read_text(encoding='utf-8'))
    rows, pin, manifest_hash = read_manifest(repo, adapter)
    blobs = source_tree(cache, pin)
    registry = dict(line.split('\t')[::-1] for line in (ROOT / 'data/units/olp-units.tsv').read_text(encoding='utf-8').splitlines()[1:])
    units = []
    for row in rows:
        path = value_at(row, adapter['source_path_key']).removeprefix(adapter.get('strip_source_prefix', ''))
        uid = value_at(row, adapter['id_key'])
        if registry.get(path) != uid or path not in blobs:
            raise ValueError(f'{uid}: source path or stable identity does not match the registry')
        relative = path.removeprefix('content/')
        target_path = safe_path(repo, adapter['content'] + '/' + relative)
        target = target_path.read_bytes()
        expected_target = value_at(row, adapter['target_hash_key']).lower() if adapter.get('target_hash_key') else None
        target_hash = sha256(target)
        if expected_target and expected_target != target_hash:
            raise ValueError(f'{uid}: target bytes differ from the inherited manifest')
        source_path = safe_path(repo, adapter['source_content'] + '/' + relative)
        source = source_path.read_bytes()
        expected_source = value_at(row, adapter['source_hash_key']).lower()
        if sha256(source) != expected_source or git_blob(source) != blobs[path]:
            raise ValueError(f'{uid}: local English bytes do not equal the inherited hash and pinned Git blob')
        by = row.get('by') or {'model': None, 'effort': None, 'date': None, 'method': 'inherited', 'evidence': adapter['manifest']}
        units.append({'id':uid, 'src':'olp', 'path':path, 'src_blob':blobs[path], 'src_sha256':expected_source, 'tr_sha256':target_hash, 'state':'current', 'by':by})
    if len(units) != len(blobs) or len({u['path'] for u in units}) != len(blobs):
        raise ValueError('manifest is not one-to-one with the complete content tree')
    data = {k:adapter[k] for k in ['locale','language_tag','script','babel','engine','repository']}
    data.update(schema_version=1, products=['olp-complete', 'slc-screen-pdf'], paths={'content':adapter['content'], 'source_content':adapter['source_content']}, conversion={'source_manifest':adapter['manifest'], 'source_manifest_sha256':manifest_hash, 'attribution_policy':'preserve-recorded-else-unresolved'})
    if adapter.get('engine_reason'):
        data['engine_reason'] = adapter['engine_reason']
    data['pins'] = {'olp':{'repository':'https://github.com/OpenLogicProject/OpenLogic','commit':pin}, **adapter['pins']}
    validate_schema('olp-edition',data)
    for unit in units:
        validate_schema('unit',unit)
    return data, sorted(units,key=lambda row:row['id'])


def import_manifest(repo, adapter, out, cache):
    data, units = make_contract(repo,adapter,cache)
    output = Path(out or repo).resolve()
    files = {'olp-edition.toml':render_edition(data).encode('utf-8'), 'units.jsonl':b''.join((json.dumps(u,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8') for u in units)}
    for name, body in files.items():
        path = output/name
        if path.exists() and path.read_bytes() != body:
            raise ValueError(f'{name} already differs; preserve owner edits and choose a new output folder')
    output.mkdir(parents=True,exist_ok=True)
    for name, body in files.items():
        (output/name).write_bytes(body)
    print(f'imported {len(units)} units; wrote only olp-edition.toml and units.jsonl')
    return validate_edition(repo,output,cache)


def validate_edition(repo, metadata_dir, cache):
    root = Path(repo).resolve()
    metadata = Path(metadata_dir or repo).resolve()
    data = tomllib.loads((metadata/'olp-edition.toml').read_text(encoding='utf-8-sig'))
    validate_schema('olp-edition',data)
    units = [json.loads(line) for line in (metadata/'units.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    for unit in units:
        validate_schema('unit',unit)
    active = [u for u in units if u['src']=='olp' and u['state']!='retired']
    if len({(u['src'],u['path']) for u in units}) != len(units) or len({u['id'] for u in units}) != len(units):
        raise ValueError('duplicate unit identity or source path')
    blobs = source_tree(cache,data['pins']['olp']['commit'])
    if {u['path'] for u in active} != set(blobs):
        raise ValueError('ledger omits or adds content paths at the pin')
    registry = dict(line.split('\t')[::-1] for line in (ROOT/'data/units/olp-units.tsv').read_text(encoding='utf-8').splitlines()[1:])
    counts = {'current':0,'stale':0,'new':0};matched=0;unknown=0
    for unit in active:
        if registry.get(unit['path']) != unit['id']:
            raise ValueError(unit['id']+': stable unit ID differs from registry')
        relative = unit['path'].removeprefix('content/')
        path = safe_path(root,data['paths']['content']+'/'+relative)
        observed_state = 'new' if unit['tr_sha256'] is None else ('current' if unit['src_blob']==blobs[unit['path']] else 'stale')
        if unit['state'] != observed_state:
            raise ValueError(unit['id']+': declared state differs from source blob or target presence')
        counts[observed_state] += 1
        if observed_state == 'new':
            if path.exists():
                raise ValueError(unit['id']+': unrecorded target exists for a new unit')
            continue
        if not path.exists() or sha256(path.read_bytes()) != unit['tr_sha256']:
            raise ValueError(unit['id']+': translated file differs from ledger')
        matched += 1
        source = safe_path(root,data['paths']['source_content']+'/'+relative).read_bytes()
        if git_blob(source) != blobs[unit['path']]:
            raise ValueError(unit['id']+': local source differs from edition pin')
        if observed_state == 'current' and sha256(source) != unit['src_sha256']:
            raise ValueError(unit['id']+': source SHA-256 differs from ledger')
        unknown += unit['by']['model'] is None
    print(f'olp-edition.toml valid; {len(active)} content units: {counts["current"]} current, {counts["stale"]} stale, {counts["new"]} new; {matched} of {len(active)} translated files equal the ledger')
    if unknown:
        print(f'Historical per-unit model attribution unresolved: {unknown}; conversion does not assert translation authorship.')
    return {'units':len(active),**counts,'matched':matched,'unresolved_attribution':unknown}
