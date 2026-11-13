"""Immutable book import witnesses, selected by the complete source pin set."""
import json
from pathlib import Path
import re

from .assembly import digest, json_bytes
from .recorder import load_imports


SOURCES = {'olp', 'slc', 'photos', 'portraits'}


def pin_key(pins):
    if set(pins) != SOURCES or any(not isinstance(v, str) or not re.fullmatch(r'[0-9a-f]{40}', v) for v in pins.values()):
        raise ValueError('import lock requires the four exact source pins')
    return digest(json_bytes(pins))


def read_lock(folder, pins):
    folder = Path(folder)
    meta = json.loads((folder / 'imports.json').read_text(encoding='utf-8'))
    if meta.get('schema') != 'olpkit.imports.v1' or meta.get('pins') != pins:
        raise ValueError('imports.lock belongs to different source pins')
    body = (folder / 'imports.lock').read_bytes()
    if digest(body) != meta.get('lock_sha256'):
        raise ValueError('imports.lock hash differs')
    rows = load_imports(folder / 'imports.lock')
    if not rows or len(rows) != meta.get('units'):
        raise ValueError('imports.lock unit count differs')
    for field in ('recorder_sha256', 'reference_pdf_sha256'):
        if not re.fullmatch(r'[0-9a-f]{64}', str(meta.get(field, ''))):
            raise ValueError('import lock lacks its English reference witness: ' + field)
    return rows, meta


def select_lock(root, pins):
    root = Path(root)
    scoped = root / 'pins' / pin_key(pins)
    if scoped.exists():
        rows, meta = read_lock(scoped, pins)
        return scoped, rows, meta
    # Retain the original reference and all existing consumers unchanged.
    legacy = root / 'imports.json'
    if legacy.is_file() and json.loads(legacy.read_text(encoding='utf-8')).get('pins') == pins:
        rows, meta = read_lock(root, pins)
        return root, rows, meta
    raise ValueError('no import lock for these source pins; build their English reference')


def write_lock(root, body, meta):
    """Keep the first reference witness; never replace another pin set."""
    root = Path(root)
    scoped = root / 'pins' / pin_key(meta['pins'])
    try:
        current, _, old = select_lock(root, meta['pins'])
    except ValueError as error:
        if not str(error).startswith('no import lock for these source pins;'):
            raise
    else:
        if old['lock_sha256'] != digest(body):
            raise ValueError('existing import lock differs; preserve it for explicit source-sync review')
        return current
    if digest(body) != meta.get('lock_sha256'):
        raise ValueError('new imports.lock hash differs')
    scoped.mkdir(parents=True, exist_ok=False)
    (scoped / 'imports.lock').write_bytes(body)
    (scoped / 'imports.json').write_bytes(json_bytes(meta))
    read_lock(scoped, meta['pins'])
    return scoped
