"""Read-only edition sync packets with exact current targets and language rules."""
import csv
import io
import json
from pathlib import Path
import re
import tomllib

from .assembly import GitSnapshot, assemble_units, digest, json_bytes
from .cache import SourceCache, relative_path
from .edition import git_blob
from .schemas import ROOT, validate_schema


def term_rows(body, hunks):
    text=body.decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(text), delimiter='\t')
    if not reader.fieldnames or 'english' not in reader.fieldnames:
        raise ValueError('termbase needs an explicit english column')
    # Match only changed hunk text, not headers or context. Token labels remain visible.
    changed='\n'.join(line[1:] for line in hunks.splitlines()
                      if line.startswith(('+','-')) and not line.startswith(('+++','---')))
    found=[]
    for number,row in enumerate(reader,2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError('malformed termbase row '+str(number))
        term=row['english'].strip()
        if not term:raise ValueError('empty English term in termbase row '+str(number))
        if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',changed,re.I):
            found.append({'line':number,'fields':row})
    return found


def checked_delta(plan, old, new):
    if plan.get('schema')!='olpkit.upstream-delta.v1':
        raise ValueError('unsupported upstream delta schema')
    entries=plan['files'];seen=set()
    changed={p for p in old.keys() | new.keys() if old.get(p)!=new.get(p)}
    if {e['path'] for e in entries}!=changed:
        raise ValueError('plan does not cover the exact upstream change set')
    for entry in entries:
        path=entry['path'];relative_path(path)
        if path in seen:raise ValueError('duplicate upstream delta path')
        seen.add(path)
        if entry['status']!='M' or entry['old_path'] not in (None,path):
            raise ValueError('this sync requires explicit migration handling for added, deleted or renamed files')
        for label,tree in [('old',old),('new',new)]:
            body=tree[path]
            if digest(body)!=entry[label+'_sha256'] or git_blob(body)!=entry[label+'_blob']:
                raise ValueError('upstream delta bytes differ: '+path)
        expected='content_unit' if path.startswith('content/') and path.endswith('.tex') else 'build_file'
        if entry['kind']!=expected:raise ValueError('upstream delta kind differs: '+path)
    return entries


def make_packets(plan, edition, units, targets, old, new, terms, orthography):
    entries=checked_delta(plan,old,new)
    if edition['pins']['olp']['commit']!=plan['from']:
        raise ValueError('edition source pin differs from sync starting pin')
    by_path={u['path']:u for u in units if u['src']=='olp' and u['state']!='retired'}
    packets={};summaries=[]
    for entry in entries:
        if entry['kind']!='content_unit':continue
        path=entry['path'];unit=by_path[path]
        if unit['id']!=entry['unit_id']:raise ValueError('sync unit identity differs from the ledger')
        target_path=edition['paths']['content']+'/'+path.removeprefix('content/')
        target=targets[target_path]
        if digest(target)!=unit['tr_sha256'] or unit['src_blob']!=entry['old_blob']:
            raise ValueError('sync target or source differs from current ledger: '+unit['id'])
        packet={'schema':'olpkit.sync-packet.v1','unit':unit['id'],'path':path,
                'from':plan['from'],'to':plan['to'],'upstream_change':entry,
                'source_before':old[path].decode('utf-8-sig'),
                'source_after':new[path].decode('utf-8-sig'),
                'target_path':target_path,'target_text':target.decode('utf-8-sig'),
                'target_sha256':digest(target),'current_ledger':unit,
                'relevant_terms':term_rows(terms,entry['hunks']),
                'termbase_sha256':digest(terms),'orthography_sha256':digest(orthography),
                'orthography_file':'language/'+edition['paths']['orthography'].split('/')[-1],
                'disposition':None,'canon_use':'Not inferred from term rows. Record actual passages consulted during this sync.',
                'conflict_policy':'Keep both source readings and the current target; an existing correction needs an explicit disposition. No automatic replacement.'}
        packets['packets/'+unit['id']+'.json']=json_bytes(packet)
        summaries.append({'id':unit['id'],'path':path,'current_target_sha256':digest(target),
                          'relevant_term_rows':len(packet['relevant_terms']),'packet_sha256':digest(packets['packets/'+unit['id']+'.json'])})
    return packets,summaries


def edition_command(repo, ref, plan_path, cache_root, out):
    out=Path(out).resolve();boundary=(ROOT.parent/'sync').resolve()
    if out==boundary or not out.is_relative_to(boundary) or out.exists():
        raise ValueError('sync edition needs a fresh named sync output folder')
    plan_path=Path(plan_path)
    if plan_path.is_dir():plan_path=plan_path/'UPSTREAM_DELTA.json'
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    snapshot=GitSnapshot(repo,ref)
    metadata=snapshot.read_many(['olp-edition.toml','units.jsonl'])
    edition=tomllib.loads(metadata['olp-edition.toml'].decode('utf-8-sig'))
    validate_schema('olp-edition',edition)
    units=[json.loads(line) for line in metadata['units.jsonl'].decode('utf-8-sig').splitlines() if line.strip()]
    if edition['pins']['olp']['commit']!=plan['from']:
        raise ValueError('edition source pin differs from sync starting pin')
    cache=SourceCache(cache_root)
    trees={}
    for which,pin in [('old',plan['from']),('new',plan['to'])]:
        folder,manifest=cache.require('olp',pin)
        trees[which]={p:(folder/p).read_bytes() for p in manifest['files']}
    language_paths=[edition['paths']['termbase'],edition['paths']['orthography']]
    for path in language_paths:relative_path(path)
    language=snapshot.read_many(language_paths)
    target_names=[edition['paths']['content']+'/'+u['path'].removeprefix('content/')
                  for u in units if u['src']=='olp' and u['state'] not in ('retired','new')]
    targets=snapshot.read_many(target_names)
    registry=dict(line.split('\t')[::-1] for line in (ROOT/'data/units/olp-units.tsv').read_text().splitlines()[1:])
    # Reuse the full 722-unit identity/hash validation; none of its marked copies are written.
    english={p:b for p,b in trees['old'].items() if p.startswith('content/') and p.endswith('.tex')}
    _,verified=assemble_units(edition,units,english,targets,registry)
    packets,summary=make_packets(plan,edition,units,targets,trees['old'],trees['new'],
                                 language[language_paths[0]],language[language_paths[1]])
    files={**packets,'UPSTREAM_DELTA.json':json_bytes(plan)}
    for name,body in language.items():files['language/'+name.split('/')[-1]]=body
    report={'schema':'olpkit.sync-edition.v1','edition':edition['language_tag'],'edition_commit':snapshot.commit,
            'from':plan['from'],'to':plan['to'],'source_plan_sha256':digest(plan_path.read_bytes()),
            'verified_current_units':len(verified),'packets':summary,
            'build_files':[e for e in plan['files'] if e['kind']=='build_file'],
            'metadata_hashes':{p:digest(b) for p,b in metadata.items()},
            'language_evidence':{p:digest(b) for p,b in language.items()},
            'source_unit_changes':0,'TeX_runs':0,'accepted_sync':False,
            'next':'Existing owner resolves each disposition with source/canon evidence, then accept/build/release. Packet creation is not a completed sync.'}
    files['SYNC_EDITION.json']=json_bytes(report)
    out.mkdir(parents=True)
    for name,body in files.items():
        relative_path(name);p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
    print(f"{edition['language_tag']}: {len(summary)} sync packets; {len(verified)} current targets verified; no source edits")
    return 0
