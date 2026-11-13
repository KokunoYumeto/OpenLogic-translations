"""Read TeX recorder inputs and compare exact source-unit identities."""
import hashlib
from pathlib import Path
import re


def read_inputs(path,cwd):
    base=Path(cwd).resolve();inputs=set()
    for line in Path(path).read_text(encoding='utf-8',errors='replace').splitlines():
        if line.startswith('PWD '):base=Path(line[4:]).resolve()
        if line.startswith('INPUT '):
            name=line[6:].strip('"');p=Path(name)
            inputs.add((p if p.is_absolute() else base/p).resolve())
    return sorted(inputs)


def content_inputs(inputs,root,locale=None):
    root=Path(root).resolve();found={};wrong=[]
    for path in inputs:
        if not path.is_relative_to(root):continue
        relative=path.relative_to(root).as_posix()
        match=re.fullmatch(r'(?:locale/([^/]+)/)?(content/.+\.tex)',relative)
        if match:
            language,unit=match.groups()
            if (locale is None and language is not None) or (locale is not None and language!=locale):
                wrong.append(relative)
            found.setdefault(unit,[]).append(relative)
    return found,wrong


def load_imports(path):
    records=[]
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        uid,name=line.split('\t')
        if not re.fullmatch(r'OLP-\d{4}',uid) or not name.startswith('content/'):
            raise ValueError('invalid import identity')
        records.append((uid,name))
    if len(set(uid for uid,_ in records))!=len(records) or len(set(n for _,n in records))!=len(records):
        raise ValueError('duplicate imports.lock identity')
    return records


def compare_imports(found,wrong,expected):
    names={name for _,name in expected}
    return {'pass':set(found)==names and not wrong,'expected':len(names),'observed':len(found),
            'missing':sorted(names-set(found)),'extra':sorted(set(found)-names),'wrong_language_inputs':wrong}


def input_hashes(inputs,root):
    """Retain exact identities without exporting workstation-specific paths."""
    root=Path(root).resolve();records=[]
    for path in inputs:
        if not path.is_file():continue
        body=path.read_bytes()
        local=path.is_relative_to(root)
        records.append({'path':path.relative_to(root).as_posix() if local else path.name,
                        'kind':'assembled-tree' if local else 'toolchain',
                        'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
    return sorted(records,key=lambda x:(x['kind'],x['path'],x['sha256']))
