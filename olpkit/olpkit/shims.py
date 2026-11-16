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


def apply_shims(files, context, directory=None, *, require_file_hashes=False):
    """Return copied bytes and provenance; leave caller inputs/cache untouched.

    Preconditions are checked across the whole plan before returning anything.
    For an exact-file correction, the declared output digest also identifies
    an upstream source that already contains the correction.
    """
    for key in ('locale','engine','script'):
        if not context.get(key):
            raise ValueError('shim context missing '+key)
    output = dict(files)
    receipts = []
    for shim, data_hash in load_shims(directory):
        if not any(all(context.get(key)==value for key,value in condition.items())
                   for condition in shim['conditions']):
            continue
        name = shim['path']
        if name not in output:
            raise ValueError(shim['id']+': upstream file absent: '+name)
        if require_file_hashes and 'input_sha256' not in shim:
            raise ValueError(shim['id']+': expected exact input and output file hashes')
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
        observed = output[name].count(before)
        if observed != 1:
            raise ValueError(f'{shim["id"]}: expected exactly one literal match, found {observed} in {name}')
        output[name] = old.replace(before,after,1)
        new_hash = digest(output[name])
        if 'output_sha256' in shim and new_hash != shim['output_sha256']:
            raise ValueError(shim['id']+': corrected file digest differs')
        receipts.append({**receipt,'matches':observed,'after_sha256':new_hash})
    return output,receipts
