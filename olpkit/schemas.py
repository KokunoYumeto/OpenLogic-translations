"""Strict public metadata schemas. Structural currency is not semantic approval."""
import json
from pathlib import Path
from functools import lru_cache

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=8)
def validator(name):
    schema = json.loads((ROOT / 'schemas' / (name + '.schema.json')).read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_schema(name, value):
    errors = sorted(validator(name).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        path = '.'.join(str(x) for x in error.path) or '<root>'
        raise ValueError(f'{name}: {path}: {error.message}')
