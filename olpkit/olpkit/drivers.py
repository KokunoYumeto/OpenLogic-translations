"""Generate textbook drivers from pinned upstream bytes and explicit locale data."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tomllib

from .cache import SourceCache, relative_path
from .schemas import ROOT, validate_schema


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_toml(path):
    return tomllib.loads(path.read_text(encoding='utf-8-sig'))


def merge_fonts(base, overrides, reasons, prefix='fonts'):
    result = deepcopy(base)
    for key,value in overrides.items():
        field = prefix+'.'+key
        if isinstance(value,dict):
            result[key] = merge_fonts(result.get(key,{}),value,reasons,field)
        else:
            if key in result and result[key]!=value and not any(field==r or field.startswith(r+'.') for r in reasons):
                raise ValueError('font override needs an explicit reason: '+field)
            result[key] = value
    return result


def render_template(text, values):
    def lookup(match):
        field = match.group(1)
        value = values
        for key in field.split('.'):
            if not isinstance(value,dict) or key not in value:
                raise ValueError('preamble data missing '+field)
            value = value[key]
        if isinstance(value,bool) or not isinstance(value,(str,int,float)):
            raise ValueError('preamble field is not a scalar: '+field)
        return str(value)
    result = re.sub(r'@@([A-Za-z0-9_.]+)@@',lookup,text)
    if '@@' in result:
        raise ValueError('unresolved preamble placeholder')
    return result


def generate_drivers(edition, source_files, book_id='sets-logic-computation', data_root=None):
    data_root = Path(data_root) if data_root else ROOT/'data'
    validate_schema('olp-edition',edition)
    if not re.fullmatch('[a-z0-9-]+',book_id):
        raise ValueError('invalid book identifier')
    book = read_toml(data_root/'books'/(book_id+'.toml'))
    validate_schema('book',book)
    policy_name=book.get('driver_policies',{}).get(edition['locale'],book.get('driver_policy'))
    if not policy_name:raise ValueError('localized driver policy is not yet recorded for '+book_id)
    policy_path = data_root/'books'/policy_name
    policy = read_toml(policy_path)
    validate_schema('driver-policy',policy)
    if policy['source_commit']!=book['commit'] or edition['pins'][book['source_id']]['commit']!=book['commit']:
        raise ValueError('driver policy and edition book pins differ')
    language_path = data_root/'languages'/(edition['locale']+'.toml')
    language_bytes = language_path.read_bytes()
    language = tomllib.loads(language_bytes.decode('utf-8'))
    validate_schema('language',language)
    from .pdfaudit import contrast
    link_colour=tuple(int(language['links']['color'][i:i+2],16)/255 for i in (0,2,4))
    if contrast(link_colour)<language['links']['minimum_contrast']:
        raise ValueError('declared link colour does not meet required contrast on white paper')
    for key in ('locale','engine','script','babel'):
        if language[key]!=edition[key]:
            raise ValueError('language preamble profile differs from edition '+key)
    values = deepcopy(language)
    reasons = {r['field'] for r in edition.get('overrides',[])}
    values['fonts'] = merge_fonts(language['fonts'],edition.get('fonts',{}),reasons)
    outputs = {}
    templates = []
    for phase in ('before_class','before_olp','after_olp'):
        parts = []
        for filename in policy.get('preamble',{}).get(phase,language['preamble'][phase]):
            relative_path(filename)
            template = (data_root/'preambles'/filename).read_bytes()
            parts.append(render_template(template.decode('utf-8'),values))
            templates.append({'path':'preambles/'+filename,'sha256':digest(template)})
        outputs['olpkit-'+phase.replace('_','-')+'.tex'] = ''.join(parts).encode('utf-8')
    transformations = []
    filenames = set()
    for driver in policy['files']:
        name = driver['path']
        relative_path(name)
        if name in filenames:
            raise ValueError('duplicate driver in policy: '+name)
        filenames.add(name)
        source = source_files[name]
        if digest(source)!=driver['sha256']:
            raise ValueError(name+': upstream driver changed; review its transformations and reader labels')
        result = source
        identifiers = set()
        for change in driver['transforms']:
            if change['id'] in identifiers:
                raise ValueError('duplicate driver transformation: '+change['id'])
            identifiers.add(change['id'])
            old,new = change['before'].encode('utf-8'),change['after'].encode('utf-8')
            count = result.count(old)
            if count!=change['matches']:
                raise ValueError(f'{name}/{change["id"]}: expected {change["matches"]} matches, found {count}')
            result = result.replace(old,new)
            transformations.append({'file':name,'id':change['id'],'kind':change['kind'],'matches':count,
                                    'reason':change['reason']})
        for change in driver['transforms']:
            if change['kind']=='label' and change['before'].encode() in result:
                raise ValueError(name+': a mapped reader label remains untranslated')
        header = ('% Generated from upstream '+name+' at '+book['commit']+'.\n'
                  '% Localized settings are loaded from the accompanying preamble files.\n').encode()
        outputs[name] = header+result
    report = {'schema':'olpkit.drivers.v1','book':book_id,'book_pin':book['commit'],'locale':edition['locale'],
              'language_data_sha256':digest(language_bytes),'policy':'books/'+policy_name,'policy_sha256':digest(policy_path.read_bytes()),
              'templates':templates,'evidence':language['evidence'],'transformations':transformations,
              'untranslated_driver_labels':0,'rendered_equivalence':'not checked by generation',
              'outputs':{name:{'bytes':len(data),'sha256':digest(data)} for name,data in sorted(outputs.items())}}
    return outputs,report


def write_drivers(outputs, report, folder, check=False):
    folder = Path(folder).resolve()
    boundary = (ROOT.parent/'out').resolve()
    if folder==boundary or not folder.is_relative_to(boundary):
        raise ValueError('driver staging must be a named child of the builder output directory')
    outputs = {**outputs,'DRIVERS.json':(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8')}
    for name,data in outputs.items():
        relative_path(name)
        path = folder/name
        if not path.resolve().is_relative_to(folder):
            raise ValueError('generated driver path escapes its staging directory')
        if check:
            if not path.is_file() or path.read_bytes()!=data:
                raise ValueError('generated driver differs: '+name)
        elif path.exists() and path.read_bytes()!=data:
            raise ValueError('existing driver differs; preserve it and use a new staging directory: '+name)
    if not check:
        folder.mkdir(parents=True,exist_ok=True)
        for name,data in outputs.items():
            path=folder/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    print('0 untranslated strings (mapped driver labels; book text is checked separately)')


def drivers_command(repo, metadata_dir, cache_root, out, check=False, book_id='sets-logic-computation'):
    metadata = Path(metadata_dir or repo).resolve()
    edition = read_toml(metadata/'olp-edition.toml')
    validate_schema('olp-edition',edition)
    if not re.fullmatch('[a-z0-9-]+',book_id):
        raise ValueError('invalid book identifier')
    book=read_toml(ROOT/'data/books'/(book_id+'.toml'))
    validate_schema('book',book)
    source,_ = SourceCache(cache_root).require(book['source_id'],edition['pins'][book['source_id']]['commit'])
    originals={name:(source/name).read_bytes() for name in book['drivers']}
    outputs,report=generate_drivers(edition,originals,book_id)
    write_drivers(outputs,report,out,check)
    return report
