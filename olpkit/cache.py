"""Fetch exact source pins; assembly consumes verified exports without Git/network."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import tomllib

from .edition import git_blob
from .schemas import ROOT, validate_schema


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative_path(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or path.as_posix() != name
            or '..' in path.parts or '\\' in name or ':' in name
            or any(p.lower() == '.git' or p.endswith((' ', '.')) for p in path.parts)
            or any(re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', p) for p in path.parts)):
        raise ValueError('unsafe cache member: ' + name)
    return path


def run_git(directory, *args, allow_missing=False):
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GIT_NO_LAZY_FETCH': '1'}
    result = subprocess.run(['git', '--git-dir', str(directory), '-c', 'gc.auto=0',
                             '-c', 'maintenance.auto=false', *args],
                            capture_output=True, env=env, timeout=300)
    if result.returncode and not allow_missing:
        # Do not copy remote/config output into a log: it could contain credentials.
        raise ValueError(f'Git {args[0]} failed for {directory.name} (exit {result.returncode})')
    return result


def tree_entries(directory, pin):
    entries, submodules = {}, {}
    folded = set()
    for row in run_git(directory, 'ls-tree', '-rz', '--full-tree', pin).stdout.split(b'\0'):
        if not row:
            continue
        meta, encoded = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        name = encoded.decode('utf-8')
        relative_path(name)
        if name.casefold() in folded:
            raise ValueError('case-colliding source paths: ' + name)
        folded.add(name.casefold())
        if mode == '160000' and kind == 'commit':
            submodules[name] = oid
        elif kind == 'blob' and mode in {'100644', '100755'}:
            entries[name] = {'blob': oid, 'mode': mode}
        else:
            raise ValueError('unsupported source member: ' + name)
    return entries, submodules


def cache_manifest(folder):
    """Hash file bytes and names; no timestamps or workstation paths."""
    return {p.relative_to(folder).as_posix(): {'bytes': p.stat().st_size,
             'sha256': digest(p.read_bytes())}
            for p in sorted(folder.rglob('*')) if p.is_file()}


def export_blobs(bare, expected, payload, stage):
    """Read raw Git blobs: ignore checkout filters, EOL rules and export-ignore."""
    env = {**os.environ,'GIT_TERMINAL_PROMPT':'0','GIT_NO_LAZY_FETCH':'1'}
    files = {}
    with tempfile.TemporaryFile(dir=stage) as errors:
        process = subprocess.Popen(['git','--git-dir',str(bare),'cat-file','--batch'],
                                   stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,env=env)
        try:
            for name, meta in sorted(expected.items()):
                process.stdin.write((meta['blob']+'\n').encode('ascii'))
                process.stdin.flush()
                header = process.stdout.readline(200).decode('ascii').strip().split()
                if len(header) != 3 or header[:2] != [meta['blob'],'blob']:
                    raise ValueError('could not read pinned source blob: '+name)
                size = remaining = int(header[2])
                sha = hashlib.sha256()
                git_sha = hashlib.sha1(b'blob '+str(size).encode()+b'\0')
                target = payload.joinpath(*PurePosixPath(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('wb') as output:
                    while remaining:
                        chunk = process.stdout.read(min(remaining,1024*1024))
                        if not chunk:
                            raise ValueError('truncated pinned source blob: '+name)
                        output.write(chunk)
                        sha.update(chunk)
                        git_sha.update(chunk)
                        remaining -= len(chunk)
                if process.stdout.read(1) != b'\n' or git_sha.hexdigest() != meta['blob']:
                    raise ValueError('source blob protocol or hash mismatch: '+name)
                files[name] = {**meta,'bytes':size,'sha256':sha.hexdigest()}
            process.stdin.close()
            if process.wait(timeout=30):
                raise ValueError('pinned source export failed')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            process.stdout.close()
            if not process.stdin.closed:
                process.stdin.close()
    return files


def verify_export(folder, manifest, expected=None):
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError('missing or linked source export')
    actual = {}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError('linked member in source export')
        if not path.is_file():
            continue
        name = path.relative_to(folder).as_posix()
        relative_path(name)
        content = path.read_bytes()
        actual[name] = {'bytes': len(content), 'sha256': digest(content), 'blob': git_blob(content)}
    required = manifest['files']
    if set(actual) != set(required):
        raise ValueError('source export file set differs from its manifest')
    if expected is not None and set(actual) != set(expected):
        raise ValueError('source export omits pinned Git files')
    for name, entry in actual.items():
        if any(entry[k] != required[name][k] for k in entry):
            raise ValueError('source export bytes differ: ' + name)
        if expected is not None and entry['blob'] != expected[name]['blob']:
            raise ValueError('source export differs from pinned Git blob: ' + name)
    return actual


def remove_own_stage(path, parent):
    resolved, boundary = path.resolve(), parent.resolve()
    if resolved.parent != boundary or not resolved.name.startswith('fetch-'):
        raise ValueError('refusing cleanup outside the generated cache staging directory')
    # This function is only passed a directory created by this invocation.
    for item in resolved.rglob('*'):
        if item.is_file() and not item.is_symlink():
            item.chmod(stat.S_IWRITE | stat.S_IREAD)
    shutil.rmtree(resolved)


class SourceCache:
    def __init__(self, root, sources=None):
        self.root = Path(root).resolve()
        data = sources if sources is not None else tomllib.loads((ROOT/'data/sources.toml').read_text(encoding='utf-8'))
        self.sources = {key: value for key, value in data.items() if key != 'schema_version'}

    def locations(self, source, pin):
        if source not in self.sources or not re.fullmatch('[0-9a-f]{40}', pin):
            raise ValueError('unknown source or non-full source pin')
        spec = self.sources[source]
        relative_path(spec['cache'])
        if '/' in spec['cache']:
            raise ValueError('cache repository must be a direct child')
        return (self.root/spec['cache'], self.root/'exports'/source/pin,
                self.root/'manifests'/f'{source}-{pin}.json')

    def require(self, source, pin):
        """Read-only, no Git calls or fallback fetch; suitable for assembly."""
        _, folder, receipt = self.locations(source, pin)
        if not receipt.is_file():
            raise ValueError(f'{source} at {pin}: run fetch before assembly')
        record = json.loads(receipt.read_text(encoding='utf-8'))
        if record['source'] != source or record['commit'] != pin or record['repository'] != self.sources[source]['repository']:
            raise ValueError('cache receipt identifies a different source')
        verify_export(folder, record)
        return folder, record

    def fetch(self, source, pin):
        bare, export, receipt = self.locations(source, pin)
        spec = self.sources[source]
        self.root.mkdir(parents=True, exist_ok=True)
        if bare.is_symlink() or not bare.resolve().is_relative_to(self.root):
            raise ValueError('unsafe bare cache location')
        if not bare.exists():
            result = subprocess.run(['git', 'init', '--bare', str(bare)], capture_output=True)
            if result.returncode:
                raise ValueError('could not initialize source cache')
            run_git(bare, 'remote', 'add', 'origin', spec['repository'])
        remote = run_git(bare, 'remote', 'get-url', 'origin').stdout.decode().strip()
        if remote.removesuffix('.git').casefold() != spec['repository'].removesuffix('.git').casefold():
            raise ValueError('cached source remote does not match the declared repository')
        downloads = 0
        if run_git(bare, 'cat-file', '-e', pin+'^{commit}', allow_missing=True).returncode:
            run_git(bare, 'fetch', '--no-tags', '--depth=1', 'origin', pin)
            downloads += 1
        if run_git(bare, 'rev-parse', '--verify', pin+'^{commit}').stdout.decode().strip() != pin:
            raise ValueError('source pin is not the requested commit')
        missing = run_git(bare, 'rev-list', '--objects', '--missing=print', pin).stdout
        if any(line.startswith(b'?') for line in missing.splitlines()):
            # Existing partial clones may have the commit but not its blob/tree objects.
            # Fetch once in bulk. Assembly must never cause implicit per-blob network IO.
            run_git(bare, 'fetch', '--refetch', '--no-filter', '--no-tags', '--depth=1', 'origin', pin)
            downloads += 1
        expected, submodules = tree_entries(bare, pin)
        if receipt.exists() or export.exists():
            if not receipt.exists() or not export.exists():
                raise ValueError('incomplete cache export; preserve it and inspect before retrying')
            record = json.loads(receipt.read_text(encoding='utf-8'))
            if (record.get('source'), record.get('commit'), record.get('repository')) != (source,pin,spec['repository']):
                raise ValueError('cache receipt identifies a different source')
            verify_export(export, record, expected)
            return {'source':source,'commit':pin,'network_fetches':downloads,'export_created':False,
                    'files':len(expected),'manifest_sha256':digest(receipt.read_bytes())}
        incoming = self.root/'incoming'
        incoming.mkdir(exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='fetch-', dir=incoming))
        try:
            payload = stage/'tree'
            payload.mkdir()
            files = export_blobs(bare,expected,payload,stage)
            record = {'schema':'olpkit.source-cache.v1','source':source,'repository':spec['repository'],
                      'commit':pin,'files':files,'gitlinks':submodules}
            body = (json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
            export.parent.mkdir(parents=True, exist_ok=True)
            receipt.parent.mkdir(parents=True, exist_ok=True)
            payload.rename(export)
            for path in export.rglob('*'):
                if path.is_file():
                    path.chmod(stat.S_IREAD)
            receipt.write_bytes(body)
            return {'source':source,'commit':pin,'network_fetches':downloads,'export_created':True,
                    'files':len(expected),'manifest_sha256':digest(body)}
        finally:
            remove_own_stage(stage, incoming)


def fetch_edition(repo, metadata_dir, cache_root):
    metadata = Path(metadata_dir or repo).resolve()
    edition = tomllib.loads((metadata/'olp-edition.toml').read_text(encoding='utf-8-sig'))
    validate_schema('olp-edition',edition)
    cache = SourceCache(cache_root)
    result = []
    for source, pin in edition['pins'].items():
        if source not in cache.sources or pin['repository'] != cache.sources[source]['repository']:
            raise ValueError('edition source is not in the explicit source registry: '+source)
        result.append(cache.fetch(source,pin['commit']))
    print(json.dumps({'sources':result},ensure_ascii=False))
    return result
