"""Verify named vendored trees against explicitly pinned source components."""
from collections import Counter
import json
from pathlib import Path

from .assembly import digest,json_bytes
from .cache import SourceCache,relative_path
from .schemas import ROOT,validate_schema


def compare_files(actual,base,components):
    """No unknown extras, overlapping mounts or incomplete components pass."""
    mounts=[]
    for component in components:
        mount=component['mount'];relative_path(mount)
        if any(mount==old or mount.startswith(old+'/') or old.startswith(mount+'/') for old in mounts):
            raise ValueError('overlapping vendored component mounts')
        mounts.append(mount)
    records=[];failures=[];seen={m:set() for m in mounts}
    for name,data in sorted(actual.items()):
        relative_path(name);source='olp';expected=base.get(name);pin=None
        for component in components:
            prefix=component['mount']+'/'
            if name.startswith(prefix):
                key=name[len(prefix):];expected=component['files'].get(key)
                source=component['source'];pin=component['commit'];seen[component['mount']].add(key);break
        if expected is None:failures.append({'path':name,'reason':'unregistered extra'})
        elif data!=expected:failures.append({'path':name,'reason':'bytes differ','source':source})
        records.append({'path':name,'source':source,'component_commit':pin,'sha256':digest(data)})
    for component in components:
        missing=set(component['files'])-seen[component['mount']]
        failures.extend({'path':component['mount']+'/'+p,'reason':'declared component member absent'} for p in sorted(missing))
    if not actual:failures.append({'path':'','reason':'empty vendored tree'})
    return {'files':records,'failures':failures,'counts':dict(Counter(r['source'] for r in records)),
            'pass':not failures,'scope':'Every present base file and the exact declared component member set; not a claim that every upstream archive file is vendored.'}


def verify(repo,directory,pin,cache_root,component_file=None,output=None):
    root=Path(repo).resolve();relative_path(directory);folder=(root/directory).resolve()
    if folder==root or not folder.is_relative_to(root):raise ValueError('vendored directory escapes its named repository')
    cache=SourceCache(cache_root);base_folder,base_record=cache.require('olp',pin)
    base={n:(base_folder/n).read_bytes() for n in base_record['files']}
    components=[];declarations=[]
    if component_file:
        declarations=json.loads(Path(component_file).read_text(encoding='utf-8-sig'))
        validate_schema('vendored-components',declarations)
        for row in declarations:
            path,record=cache.require(row['source'],row['commit'])
            members=row.get('members',record['files'])
            for name in members:
                relative_path(name)
                if name not in record['files']:raise ValueError('declared component member absent from pinned source: '+name)
            components.append({**row,'files':{n:(path/n).read_bytes() for n in members}})
    actual={}
    for path in folder.rglob('*'):
        if path.is_symlink() or not path.resolve().is_relative_to(folder):raise ValueError('linked vendored input')
        if path.is_file():actual[path.relative_to(folder).as_posix()]=path.read_bytes()
    report={'schema':'olpkit.vendored.v1','source_commit':pin,'components':declarations,**compare_files(actual,base,components)}
    if output:
        dest=Path(output).resolve();boundary=(ROOT.parent/'out').resolve()
        if not dest.is_relative_to(boundary) or dest==boundary:raise ValueError('vendored report must be under named builder outputs')
        body=json_bytes(report)
        if dest.exists() and dest.read_bytes()!=body:raise ValueError('existing vendored report differs; preserve it')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
    if not report['pass']:raise ValueError('vendored mismatches: '+json.dumps(report['failures'][:10]))
    print(f'{len(actual)} of {len(actual)} files equal pinned sources; '+json.dumps(report['counts'],sort_keys=True))
    return report
