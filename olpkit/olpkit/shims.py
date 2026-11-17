"""Exact, conditional upstream build patches; no target-language rewriting."""
import hashlib
from pathlib import Path
import tomllib

from .cache import relative_path
from .schemas import ROOT, validate_schema


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_shims(directory=None):
    folder = Path(directory) if directory else ROOT/'data/shims'
    result = []
    identifiers = set()
    for path in sorted(folder.glob('*.toml')):
        data = path.read_bytes()
        record = tomllib.loads(data.decode('utf-8'))
        validate_schema('shim',record)
        relative_path(record['path'])
        if record['id'] in identifiers:
            raise ValueError('duplicate shim identity: '+record['id'])
        identifiers.add(record['id'])
        result.append((record,digest(data)))
    return result


def edition_shims(context, directory=None):
    for key in ('locale', 'engine', 'script'):
        if not context.get(key):
            raise ValueError('shim context missing ' + key)
    return [(shim, checksum) for shim, checksum in load_shims(directory)
            if any(all(context.get(key) == value for key, value in condition.items())
                   for condition in shim['conditions'])]


def upstream_settings(files, records):
    """Use a setting only when the pinned source both declares and consumes it."""
    settings = {}
    for shim, _ in records:
        hook = shim.get('upstream_setting')
        if not hook:
            continue
        lines = [line.partition(b'%')[0].strip() for line in files[shim['path']].splitlines()]
        declaration = ('\\providecommand*{\\' + hook['name'] + '}{').encode()
        definitions = sum(line.startswith(declaration) for line in lines)
        uses = lines.count(hook['use'].encode())
        if definitions == uses == 0:
            continue
        if definitions != 1 or uses != 1:
            raise ValueError(shim['id'] + ': upstream hook declaration or use differs')
        settings[shim['id']] = hook
    return settings


def apply_shims(files, context, directory=None, *, require_file_hashes=False):
    output, receipts, _ = localize_sources(files, context, directory, require_file_hashes=require_file_hashes)
    return output, receipts


def localize_sources(files, context, directory=None, *, require_file_hashes=False):
    """Return copied bytes, patch receipts and settings for the localized drivers.

    Preconditions are checked across the whole plan before returning anything.
    For an exact-file correction, the declared output digest also identifies
    an upstream source that already contains the correction.
    """
    records = edition_shims(context, directory)
    for shim, _ in records:
        if shim['path'] not in files:
            raise ValueError(shim['id'] + ': upstream file absent: ' + shim['path'])
    settings = upstream_settings(files, records)
    output = dict(files)
    receipts = []
    for shim, data_hash in records:
        name = shim['path']
        if require_file_hashes and 'input_sha256' not in shim:
            raise ValueError(shim['id']+': expected exact input and output file hashes')
        if shim['id'] in settings:
            continue
        before,after = shim['before'].encode('utf-8'),shim['after'].encode('utf-8')
        old = output[name]
        old_hash = digest(old)
        receipt = {'id':shim['id'],'path':name,'before_sha256':old_hash,
                   'shim_sha256':data_hash,'reason':shim['reason'],'evidence':shim['evidence']}
        if 'input_sha256' in shim:
            if old_hash == shim['output_sha256']:
                receipts.append({**receipt,'matches':0,'after_sha256':old_hash,'upstream_corrected':True})
                continue
            if old_hash != shim['input_sha256']:
                raise ValueError(shim['id']+': source revision differs; review '+name)
        if 'alternate_before' in shim:
            alternative = shim['alternate_before'].encode('utf-8')
            candidates = [match for match in (before, alternative) if match in old]
            if len(candidates) != 1:
                raise ValueError(shim['id'] + ': expected exactly one supported source form')
            before = candidates[0]
        observed = output[name].count(before)
        if observed != 1:
            raise ValueError(f'{shim["id"]}: expected exactly one literal match, found {observed} in {name}')
        output[name] = old.replace(before,after,1)
        new_hash = digest(output[name])
        if 'output_sha256' in shim and new_hash != shim['output_sha256']:
            raise ValueError(shim['id']+': corrected file digest differs')
        receipts.append({**receipt,'matches':observed,'after_sha256':new_hash})
    return output, receipts, settings
