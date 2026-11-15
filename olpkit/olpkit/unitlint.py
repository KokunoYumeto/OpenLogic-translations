"""Batch comparisons of immutable units; findings never rewrite translations.

Literal TeX structure and token counts are necessary checks, not a semantic or
canon-use certificate. Unconfigured orthography remains explicitly unchecked.
"""
from collections import Counter
import csv
import io
import json
from pathlib import Path
import re
import tomllib
from .orthography import inspect_orthography

from .assembly import GitSnapshot,assemble_units,digest,json_bytes
from .cache import SourceCache,relative_path
from .schemas import ROOT,validate_schema
from .structure import signature,without_comments,argument,COMMAND

CONTRACT_BYTES = (ROOT/'data/unit-contract.toml').read_bytes()
CONTRACT = tomllib.loads(CONTRACT_BYTES.decode('utf-8'))
KEEP = tuple(CONTRACT['tokens']['keep'])
if not KEEP or len(set(KEEP))!=len(KEEP) or any(not re.fullmatch(r'[a-z][a-z0-9-]*',k) for k in KEEP):
    raise ValueError('invalid kept-token data contract')
IDENTIFIERS = {'olfileid','olchapterid','olpartid'}
EXCEPTION_FIELDS = ['unit','rule','source_sha256','target_sha256','finding_sha256','reason','evidence']


def kept_tokens(text):
    text=without_comments(text)
    counts=Counter({k:0 for k in KEEP})
    for match in re.finditer(r'!![A-Za-z^]*\s*\{([^{}]+)\}',text):
        if match[1] in counts:counts[match[1]]+=1
    for match in re.finditer(r'\\(?:use|print)token\s*\{[^{}]*\}\s*\{([^{}]+)\}',text):
        if match[1] in counts:counts[match[1]]+=1
    return dict(counts)


def stored_marks(text):
    text=without_comments(text);marks=[]
    for match in COMMAND.finditer(text):
        if match[1] not in IDENTIFIERS:continue
        pos=match.end()
        while pos<len(text) and text[pos].isspace():pos+=1
        value=None
        if pos<len(text) and text[pos]=='[':value,_=argument(text,pos,'[',']')
        marks.append([match[1],value])
    return marks


def unit_findings(source,target,locale,orthography=None,english=False):
    """Return measured differences only; evidence-bound exceptions are separate."""
    en=source.decode('utf-8-sig');tr=target.decode('utf-8-sig')
    a,b=signature(en),signature(tr);findings=[]
    def add(rule,original,actual):
        value={'rule':rule,'source':original,'target':actual}
        value['finding_sha256']=digest(json_bytes(value));findings.append(value)
    for key in ('identifiers','imports','labels','environments','citations','references','tags'):
        if a[key]!=b[key]:add(key,a[key],b[key])
    if not english:
        marks=stored_marks(tr)
        if any(value!=locale for _,value in marks):
            add('locale-mark',[[name,locale] for name,_ in marks],marks)
    tokens_a,tokens_b=kept_tokens(en),kept_tokens(tr)
    for key in KEEP:
        if tokens_a[key]!=tokens_b[key]:add('token:'+key,tokens_a[key],tokens_b[key])
    if a['footnotes']!=b['footnotes']:add('footnotes',a['footnotes'],b['footnotes'])
    note_commands = CONTRACT['notes']['commands']
    notes = [Counter(m[1] for m in COMMAND.finditer(without_comments(text)) if m[1] in note_commands)
             for text in (en, tr)]
    if notes[0] != notes[1]:
        add('note-commands', dict(notes[0]), dict(notes[1]))
    for rule, source, target in inspect_orthography(tr, orthography):
        add(rule, source, target)
    return findings,{'source':tokens_a,'target':tokens_b}


def apply_exceptions(findings,body):
    if body is None:return findings,[]
    reader=csv.DictReader(io.StringIO(body.decode('utf-8-sig')),delimiter='\t')
    if reader.fieldnames!=EXCEPTION_FIELDS:raise ValueError('exception columns differ from the exact contract')
    accepted=[];seen=set()
    for row in reader:
        if None in row or any(not row.get(k,'').strip() for k in EXCEPTION_FIELDS):
            raise ValueError('incomplete exception record')
        key=tuple(row[k] for k in EXCEPTION_FIELDS[:5])
        if key in seen:raise ValueError('duplicate exception record')
        seen.add(key)
        matching=[f for f in findings if tuple(f[k] for k in EXCEPTION_FIELDS[:5])==key]
        if len(matching)!=1:raise ValueError('exception is stale or does not identify exactly one observed finding: '+row['unit']+'/'+row['rule'])
        matching[0]['exception']={'reason':row['reason'],'evidence':row['evidence']}
        accepted.append(row)
    return findings,accepted


def classify_exceptions(findings,body):
    """Retain legacy decisions without silently upgrading them to waivers."""
    if body is None:return findings,[],None
    header=next(csv.reader(io.StringIO(body.decode('utf-8-sig')),delimiter='\t'),[])
    if header==['unit','rule','reason']:
        legacy=list(csv.DictReader(io.StringIO(body.decode('utf-8-sig')),delimiter='\t'))
        return findings,[],{'status':'unbound_legacy_records','records':legacy,
                            'required':'Bind each justified observed finding to exact source, target and finding hashes.'}
    checked,accepted=apply_exceptions(findings,body)
    return checked,accepted,None


def write_reports(folder,locale,report,check=False):
    folder=Path(folder).resolve();boundary=(ROOT.parent/'out').resolve()
    if folder==boundary or not folder.is_relative_to(boundary):raise ValueError('lint output must be a named builder output child')
    def tsv(fields,rows):
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(rows);return stream.getvalue().encode('utf-8')
    rows=[]
    for f in report['findings']:
        rows.append({k:f[k] for k in ['unit','path','rule','source_sha256','target_sha256','finding_sha256']}|
                    {'source':json.dumps(f['source'],ensure_ascii=False),'target':json.dumps(f['target'],ensure_ascii=False),
                     'exception_reason':f.get('exception',{}).get('reason',''),'exception_evidence':f.get('exception',{}).get('evidence','')})
    fields=['unit','path','rule','source_sha256','target_sha256','finding_sha256','source','target','exception_reason','exception_evidence']
    tokens=[{'unit':u['id'],'path':u['path'],'token':k,'source':u['tokens']['source'][k],
             'target':u['tokens']['target'][k]} for u in report['units'] if 'tokens' in u for k in KEEP]
    outputs={f'LINT_{locale}.tsv':tsv(fields,rows),f'TOKENS_{locale}.tsv':tsv(['unit','path','token','source','target'],tokens),
             'LINT.json':json_bytes(report)}
    if folder.exists():
        if set(p.name for p in folder.iterdir())!=set(outputs) or any((folder/n).read_bytes()!=b for n,b in outputs.items()):
            raise ValueError('existing lint evidence differs; preserve it and choose a new output folder')
    elif check:raise ValueError('lint output absent')
    else:
        folder.mkdir(parents=True)
        for name,b in outputs.items():(folder/name).write_bytes(b)


def lint_units(repo,ref,cache_root,out,english=False,olp_pin=None,scope=None,check=False,tokens_only=False,
               *,metadata_dir=None,contract_hashes=None):
    registry=dict(line.split('\t')[::-1] for line in (ROOT/'data/units/olp-units.tsv').read_text().splitlines()[1:])
    cache=SourceCache(cache_root);snap=None;orthography=None;exceptions=None
    if english:
        if repo:raise ValueError('English self-comparison does not take a translation repository')
        locale='en';pin=olp_pin or '9620cc73f9c8e0ad003c514a5d3748f29611c4c0'
    else:
        if not repo:raise ValueError('translation lint requires --repo')
        snap=GitSnapshot(repo,ref)
        names=['olp-edition.toml','units.jsonl']
        if metadata_dir:
            root=Path(metadata_dir).resolve()
            contract={}
            for name in names:
                member=root/name
                if member.is_symlink() or not member.resolve().is_relative_to(root):
                    raise ValueError('linked edition contract')
                contract[name]=member.read_bytes()
        else:
            contract=snap.read_many(names)
        if contract_hashes is not None and {n:digest(raw) for n,raw in contract.items()}!=contract_hashes:
            raise ValueError('unit lint contract differs from the built assembly')
        edition=tomllib.loads(contract['olp-edition.toml'].decode('utf-8-sig'));validate_schema('olp-edition',edition)
        locale=edition['locale'];pin=edition['pins']['olp']['commit']
        for name in ['lang/orthography.json','lang/lint-exceptions.tsv']:
            if name in snap.entries:
                body=snap.read_many([name])[name]
                if name.endswith('.json'):
                    orthography=json.loads(body);validate_schema('orthography',orthography)
                    if orthography['locale']!=locale:raise ValueError('orthography locale differs')
                else:exceptions=body
    source_root,source_record=cache.require('olp',pin)
    source={n:(source_root/n).read_bytes() for n in source_record['files'] if n.startswith('content/') and n.endswith('.tex')}
    if set(source)!=set(registry):raise ValueError('source content does not equal the stable registry')
    if english:targets=source;unit_states={n:'source' for n in source}
    else:
        prefix=edition['paths']['content']+'/'
        targets=snap.read_many([n for n in snap.entries if n.startswith(prefix) and n.endswith('.tex')])
        units=[json.loads(line) for line in contract['units.jsonl'].decode('utf-8-sig').splitlines() if line.strip()]
        # This validates every raw source/target hash. Do not lint the assembled
        # return: it inserts missing marks which this check must detect in Git.
        _,verified=assemble_units(edition,units,source,targets,registry)
        unit_states={v['path']:v['state'] for v in verified}
        targets={'content/'+n[len(prefix):]:b for n,b in targets.items()}
    selected=set(source)
    if scope:
        selected=set(Path(scope).read_text(encoding='utf-8').splitlines())
        selected={line.split('\t')[-1] for line in selected}
        if not selected or not selected<=set(source):raise ValueError('scope contains an absent source unit')
    findings=[];records=[]
    for path in sorted(source,key=lambda n:registry[n]):
        row={'id':registry[path],'path':path,'state':unit_states[path],'in_scope':path in selected,
             'source_sha256':digest(source[path]),'target_sha256':digest(targets[path]) if path in targets else None}
        if path not in targets:
            row['checks']='untranslated';records.append(row);continue
        try:found,row['tokens']=unit_findings(source[path],targets[path],locale,orthography,english)
        except (ValueError,UnicodeDecodeError) as error:
            value={'rule':'parse','source':'valid literal TeX structure and UTF-8','target':str(error)}
            value['finding_sha256']=digest(json_bytes(value));found=[value]
        for f in found:findings.append({'unit':row['id'],'path':path,'source_sha256':row['source_sha256'],
                                       'target_sha256':row['target_sha256'],'in_scope':row['in_scope'],**f})
        records.append(row)
    findings,accepted,legacy=classify_exceptions(findings,exceptions)
    counts=Counter(f['rule'] for f in findings if f['in_scope'])
    unresolved=[f for f in findings if f['in_scope'] and 'exception' not in f]
    absent=sum(r['in_scope'] and r['state']=='new' for r in records)
    stale=sum(r['in_scope'] and r['state']=='stale' for r in records)
    ortho_status='source_self_comparison' if english else ('configured' if orthography and orthography['rules'] else 'not_configured')
    report={'schema':'olpkit.unit-lint.v1','locale':locale,'source_commit':pin,'edition_commit':snap.commit if snap else None,
            'kept_tokens':list(KEEP),'unit_contract_sha256':digest(CONTRACT_BYTES),
            'units':records,'findings':findings,'exceptions':accepted,'selected_units':len(selected),'counts':dict(sorted(counts.items())),
            'unresolved_findings':len(unresolved),'untranslated':absent,'stale':stale,'orthography_status':ortho_status,
            'orthography_sha256':digest(json_bytes(orthography)) if orthography else None,
            'unbound_exceptions':legacy,
            'limits':['Literal syntax and token occurrences only; no macro expansion or semantic/canon-use certification.',
                      'Added unmarked prose or notes require source comparison; footnote/environment differences are indicators.',
                      'No TeX compilation or visual review performed.'],
            'pass':not unresolved and not absent and not stale and ortho_status!='not_configured' and legacy is None}
    write_reports(out,locale,report,check)
    if tokens_only:
        for k in KEEP:print(f'{locale} {k}: source '+str(sum(r.get('tokens',{}).get('source',{}).get(k,0) for r in records))+'; target '+str(sum(r.get('tokens',{}).get('target',{}).get(k,0) for r in records)))
    else:
        print(f'{len(selected)} units: {len(unresolved)} differences; {len(accepted)} exact exceptions; orthography {ortho_status}')
        print(json.dumps(report['counts'],sort_keys=True))
    return int(not report['pass'])
