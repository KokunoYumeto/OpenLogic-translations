"""Bind translated textbook layers to their own source and private choice records.

These checks establish byte identity and coverage, not linguistic acceptance.
Private review contents are never copied into the assembled source tree.
"""
from fnmatch import fnmatchcase
import hashlib
import json
from pathlib import Path
import re
import tomllib

from .cache import relative_path
from .edition import git_blob
from .schemas import validate_schema


def digest(body):
    return hashlib.sha256(body).hexdigest()


def validate_book_contract(contract, registered, edition, profile):
    validate_schema('book', contract)
    validate_schema('book', registered)
    for field in ('id', 'source_id', 'repository', 'commit', 'drivers', 'book_units'):
        if contract[field] != registered[field]:
            raise ValueError('book contract differs from registered '+field)
    source = contract['source_id']
    if (profile['book'] != contract['id'] or profile['source_id'] != source
            or edition['pins'].get(source) != {'repository': contract['repository'],
                                              'commit': contract['commit']}):
        raise ValueError('book contract and edition source pins differ')


def bind_book_units(contract, source_files, targets, ledger, review_root, target_root):
    """Check every registered book unit, including exact retained/reused units."""
    relative_path(target_root)
    expected = set()
    for pattern in contract['book_units']:
        relative_path(pattern)
        matches = {p for p in source_files if fnmatchcase(p, pattern)}
        if not matches:
            raise ValueError('registered book unit pattern matches no source: '+pattern)
        expected.update(matches)
    rows = [json.loads(s) for s in ledger.decode('utf-8-sig').splitlines() if s.strip()]
    keyed = {}
    prefix = contract['source_id'].upper()+':'
    for row in rows:
        uid = row.get('id', '')
        if not uid.startswith(prefix):
            raise ValueError('book unit belongs to a different source')
        path = uid[len(prefix):];relative_path(path)
        if path in keyed:
            raise ValueError('duplicate book unit: '+uid)
        keyed[path] = row
    if set(keyed) != expected:
        raise ValueError('book ledger does not cover the exact registered source units')
    root = Path(review_root).resolve()
    checked_reviews = {}
    receipts = []
    for path in sorted(expected):
        row = keyed[path];uid = row['id'];original = source_files[path]
        if (row.get('source_revision') != contract['commit']
                or row.get('source_git_blob') != git_blob(original)
                or row.get('source_sha256') != digest(original)):
            raise ValueError(uid+': book source bytes or pin differ')
        target_path = target_root+'/'+path
        if row.get('target_path') != target_path or target_path not in targets:
            raise ValueError(uid+': book target absent or routed to another book')
        body = targets[target_path]
        if row.get('target_sha256') != digest(body):
            raise ValueError(uid+': book target bytes differ')
        disposition = row.get('disposition')
        if disposition not in ('translated', 'reused-exact', 'retained-verbatim'):
            raise ValueError(uid+': unknown book disposition')
        if disposition == 'retained-verbatim' and original != body:
            raise ValueError(uid+': retained book unit changed')
        if (not isinstance(row.get('model'), str) or not row['model']
                or row.get('reasoning_effort') not in ('low','medium','high','xhigh','max','ultra')):
            raise ValueError(uid+': book unit model/effort absent')
        evidence = {}
        for kind in ('review', 'editorial'):
            field = 'private_'+kind+'_record'
            if field not in row and kind == 'editorial':
                continue
            name = row.get(field, '');relative_path(name)
            p = root/name
            if p.is_symlink() or not p.resolve().is_relative_to(root):
                raise ValueError(uid+': private review escapes its root')
            expected_hash = row.get('private_'+kind+'_sha256', '')
            if not re.fullmatch('[0-9a-f]{64}', expected_hash):
                raise ValueError(uid+': private review hash absent')
            if name not in checked_reviews:
                checked_reviews[name] = digest(p.read_bytes())
            if expected_hash != checked_reviews[name]:
                raise ValueError(uid+': private review bytes differ')
            evidence[kind+'_sha256'] = expected_hash
        receipts.append({'id': uid, 'path': path, 'target_path': target_path,
                         'source_blob':git_blob(original), 'source_sha256':digest(original),
                         'target_sha256':digest(body), 'disposition':disposition,
                         'model':row['model'], 'effort':row['reasoning_effort'], **evidence})
    return {'ledger_sha256':digest(ledger), 'units':receipts,
            'coverage':len(receipts), 'private_review_files_checked':len(checked_reviews),
            'linguistic_acceptance':'not established by byte and coverage checks'}


def load_book_layer(snapshot, profile, registered, edition, source_files, ledger_path):
    path = profile['book_contract'];relative_path(path)
    body = snapshot.read_many([path])[path]
    contract = tomllib.loads(body.decode('utf-8-sig'))
    validate_book_contract(contract, registered, edition, profile)
    if ledger_path is None:
        raise ValueError('native book contract requires --book-ledger with actual choice evidence')
    ledger_path = Path(ledger_path)
    target_root = str(Path(path).parent).replace('\\', '/')
    names = [p for p in snapshot.entries if p.startswith(target_root+'/')]
    if any(p.startswith(target_root+'/content/') for p in names):
        raise ValueError('textbook layer contains copied content')
    targets = snapshot.read_many(names)
    report = bind_book_units(contract, source_files, targets, ledger_path.read_bytes(),
                             ledger_path.parent, target_root)
    report.update(contract_path=path, contract_sha256=digest(body),
                  source_id=contract['source_id'], source_commit=contract['commit'])
    return report


def check_assembled_book_layer(report, files, book_directory):
    for row in report['units']:
        path = book_directory+'/'+row['path']
        if path not in files or digest(files[path]) != row['target_sha256']:
            raise ValueError(row['id']+': complete book target not preserved in assembly')
