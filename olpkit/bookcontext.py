"""Assemble the source-bound book conversion context from edition data.

All reader prose, terminology, names and notation come from immutable source
inputs. Native build witnesses are explicit hashed inputs, never cache guesses.
This stage executes no TeX and writes no files.
"""
import hashlib,json,re,subprocess
from pathlib import Path
from .bookprojection import BookProjection,source_input_name
from .importlock import select_lock
from .schemas import ROOT
from .texttokens import TextTokens
from .mathsource import SourceMath,parse_definition
from .glossary import read_entries,native_order,glossary_tex
from .bookphotos import prepare_photos
from .bibliography import read_citation_labels,read_bibliography,bibliography_tex,expand_citations
from .references import References,read_aux
from .mathdisplay import DisplayAdapter
from .macrophases import mask_comments
from .bookinsertions import glossary_insertion,insert_glossary,insert_bibliography,literal_definitions,bibliography_helpers


def sha(data):return hashlib.sha256(data).hexdigest()


class BookInputs:
    def __init__(self,source,profile):
        self.root=Path(source).resolve();self.profile=profile
        self.assembly=json.loads((self.root/'ASSEMBLY.json').read_bytes())
        self.book=self.assembly['book_directory'];self.locale=self.assembly['locale'];self.inputs={}
        if profile['locale']!=self.locale:raise ValueError('export profile locale differs from assembly')

    def bytes(self,name):
        path=(self.root/name).resolve()
        if not path.is_relative_to(self.root) or name not in self.assembly['files']:
            raise ValueError('unrecorded book input')
        data=path.read_bytes()
        if sha(data)!=self.assembly['files'][name]['sha256']:raise ValueError('book input changed: '+name)
        self.inputs[name]={'sha256':sha(data),'bytes':len(data)}
        return data

    def text(self,name):return self.bytes(name).decode('utf-8-sig')

    def resolve(self,value,parent):
        name=source_input_name(value,self.book,self.locale,self.assembly['files'])
        return name,self.text(name)

    def witness(self,key):
        row=self.profile['witnesses'][key];data=Path(row['path']).read_bytes()
        if sha(data)!=row['sha256']:raise ValueError('native witness changed: '+key)
        return data

    def witness_json(self,key):return json.loads(self.witness(key))

    def witness_text(self,key,expected_sha256=None):
        # Verify exact file bytes first. A supplied projection hash determines
        # whether the producer used exact newlines or text-mode LF decoding.
        text=self.witness(key).decode('utf-8-sig')
        normalized=text.replace('\r\n','\n')
        if expected_sha256 is not None:
            for candidate in (text,normalized):
                if sha(candidate.encode())==expected_sha256:return candidate
            raise ValueError('native text witness differs from its recorded projection: '+key)
        return normalized

    def package(self,name):
        row=self.profile['packages'][name]
        path=Path(subprocess.check_output(['kpsewhich',name],text=True).strip())
        data=path.read_bytes()
        if sha(data)!=row['sha256']:raise ValueError('native package changed: '+name)
        return data


def _one(pattern,text,what):
    rows=list(re.finditer(pattern,text))
    if len(rows)!=1:raise ValueError('native '+what+' missing or ambiguous')
    return rows[0]


def source_caption(text,language,name):
    """Read one literal native label from either supported Babel spelling.

    Ambiguous or computed definitions require explicit reconciliation; this is
    not a TeX interpreter and does not choose between competing definitions.
    """
    pattern=(r'\\setlocalecaption\{'+re.escape(language)+r'\}\{'+re.escape(name)+r'\}\{([^{}]+)\}'
             r'|\\renewcommand\{\\'+re.escape(name)+r'name\}\{([^{}]+)\}')
    row=_one(pattern,mask_comments(text),name+' caption')
    return next(value for value in row.groups() if value is not None)


def build_context(source,profile):
    inputs=BookInputs(source,profile);a=inputs.assembly;b=inputs.book
    pins={k:v['commit'] for k,v in a['sources'].items()}
    _,imports,lock=select_lock(ROOT/'data/books'/profile['book'],pins)
    prior=inputs.witness_json('projection_receipt')
    original=inputs.witness_text('projection_source',prior['projected_sha256'])
    if sha(original.encode())!=prior['projected_sha256']:
        raise ValueError('native projection receipt does not bind its source')
    for name,row in prior['inputs'].items():
        if sha(inputs.bytes(name))!=row['sha256']:raise ValueError('projection input differs: '+name)
    projected,projection=BookProjection(inputs.root,a,imports,mark_units=True).project(
        profile['entry'],profile['projection_configuration'])
    unmark=lambda t:re.sub(r'\\hypertarget\{olp-unit-\d+\}\{\}','',t)
    if unmark(projected)!=original or projection['initial_selection']!=prior['initial_selection']:
        raise ValueError('source projection differs from the native-bound witness')
    if [{k:v for k,v in r.items() if k!='html_id'} for r in projection['unit_order']]!=prior['unit_order']:
        raise ValueError('executed imports differ from native order')
    tokens=TextTokens(modern_xparse=profile['modern_xparse'],resolver=inputs.resolve)
    tokens.configure_native(inputs.text('sty/open-logic-tokenize.sty'),'sty/open-logic-tokenize.sty')
    for name in profile['notation_configuration']:tokens.configure(inputs.text(name),name)
    text,token_receipt=tokens.expand(projected,'book-projection.tex')
    if unmark(text)!=inputs.witness_text('token_source',sha(unmark(text).encode())):
        raise ValueError('resolved text differs from the native-bound token witness')
    names=inputs.witness_json('names');reconciliation=inputs.witness_json('reconciliation')
    native_aux=inputs.witness_text('aux');labels=read_aux(native_aux)
    if sha(inputs.witness('pdf'))!=reconciliation['inputs']['native_pdf_sha256']:
        raise ValueError('PDF identity differs from reconciliation')
    if sha(native_aux.encode())!=reconciliation['inputs']['aux_sha256']:
        raise ValueError('auxiliary identity differs from reconciliation')
    if sha((inputs.root/'ASSEMBLY.json').read_bytes())!=reconciliation['inputs']['assembly_sha256']:
        raise ValueError('assembly differs from native reconciliation')

    helper='';definition_body=None
    if profile['glossary'].get('definition_source'):
        helper=inputs.text(profile['glossary']['definition_source'])
        hit=_one(r'\\NewDocumentCommand\\slcterm',helper,'glossary declaration')
        _,name,definition=parse_definition(helper,hit.start(),hit.start()+len(r'\NewDocumentCommand'),
            'NewDocumentCommand',{'source':profile['glossary']['definition_source']})
        if name!='slcterm' or re.sub(r'\s+','',definition.spec)!='O{}mmmm':raise ValueError('unsupported glossary declaration')
        definition_body=definition.body
    glossary_source=inputs.text(profile['glossary']['source'])
    entries=read_entries(glossary_source,slcterm_definition=definition_body)
    order=native_order(inputs.witness_text('gls'))
    shim=inputs.text(profile['prose_definition_source'])
    title_rows=list(re.finditer(r'\\newcommand\*\{\\olpBookGlossary\}\{([^{}]+)\}',mask_comments(shim)))
    if len(title_rows)>1:raise ValueError('native glossary title ambiguous')
    insertion=glossary_insertion(text,title_rows[0][1] if title_rows else None)
    title=insertion['title']
    package=inputs.package('glossaries.sty')
    if br'\newcommand{\glssentencecase}[1]{\makefirstuc{#1}}' not in package:
        raise ValueError('native glossary case rule changed')
    def sentence_case(value):
        first=value[:1]
        if not first or not (re.fullmatch('[a-zA-Z]',first) or first.upper()==first):
            raise ValueError('locale-specific initial case requires an explicit native rule')
        return first.upper()+value[1:]
    glossary,glossary_receipt=glossary_tex(entries,order,title,sentence_case=sentence_case,
        evidence={'source_sha256':sha(glossary_source.encode()),'native_gls_sha256':sha(inputs.witness('gls')),
                  'helper_sha256':sha(helper.encode()),'sentence_case_package_sha256':sha(package)})
    glossary,glossary_tokens=tokens.expand(glossary,'book-glossary.tex')
    text=insert_glossary(text,insertion,glossary)
    glossary_receipt['insertion']=insertion

    locale=inputs.text(profile['locale_source']);babel=profile['babel']
    credits_title=_one(r'\\setlocalecaption\{'+re.escape(babel)+r'\}\{photocredits\}\{([^{}]+)\}',locale,'photo credit title')[1]
    width=_one(r'\\setlength\{\\olphotowidth\}\{(\.\d+)\\textwidth\}',text,'biography photo width')
    if width.start()>=text.index(r'\olphoto{'):raise ValueError('photo width is not in force')
    text,photos=prepare_photos(text,labels,inputs.witness_text('pcr'),read=inputs.bytes,
        localized_credit_directory=profile['photo_credit_directory'],figure_label=names['names']['figure'][0],
        credits_title=credits_title,page_label=names['names']['page'][0],width_percent=float(width[1])*100,
        evidence={'pcr_sha256':sha(inputs.witness('pcr')),'locale_sha256':sha(locale.encode()),
                  'source_width_command':width[0],'source_width_offset':width.start()})
    recorder=inputs.witness_text('fls')
    for photo in photos['photos']:
        if not any(photo['name']+'-small.png' in line and line.startswith('INPUT ') for line in recorder.splitlines()):
            raise ValueError('selected biography asset not present in native recorder')
    package=inputs.package('natbib.sty')
    for signature in [br'\newcommand\NAT@open{(}',br'\newcommand\NAT@close{)}',br'\newcommand\NAT@sep{;}',br'\newcommand\NAT@aysep{,}',br'\newcommand\NAT@yrsep{,}',br'\newcommand\NAT@cmt{, }']:
        if signature not in package:raise ValueError('native citation punctuation changed')
    if r'\setcitestyle{authoryear}' not in inputs.text('sty/open-logic.sty'):
        raise ValueError('native author-year citation style absent')
    bbl=inputs.witness_text('bbl');citation_labels=read_citation_labels(native_aux)
    citation_evidence={'native_aux_sha256':sha(native_aux.encode()),'native_bbl_sha256':sha(bbl.encode()),
        'package_sha256':sha(package),'actual_bib_sha256':sha(inputs.bytes(profile['bibliography_source'])),
        'actual_bst_sha256':sha(inputs.bytes(profile['bibliography_style']))}
    bibliography=read_bibliography(bbl,citation_labels,evidence=citation_evidence)
    token_config=inputs.text(profile['token_base_source'])
    bibtitle=source_caption(token_config,babel,'bib')
    text,bibliography['insertion']=insert_bibliography(text,bibliography_tex(bibliography,bibtitle),
        source=profile['bibliography_source'],style=profile['bibliography_style'])
    text,citations=expand_citations(text,citation_labels,
        style={'open':'(','close':')','separator':';','author_year':',','year_separator':',','note_separator':', '},evidence=citation_evidence)
    definitions='\n'.join(re.findall(r'\\newcommand\*\{\\olpBook\w+\}\{[^{}]+\}',shim))
    definitions+='\n'+bibliography_helpers(bbl)
    for row in profile.get('prose_macro_sources',[]):
        definitions+='\n'+literal_definitions(inputs.text(row['source']),row['names'])
    references=References(labels,names['names'],evidence=reconciliation,pair_conjunction=names['pair_conjunction'],parenthesized_types=('enumi','enumii'))
    text,reference_receipt=references.prepare(text,'book-with-front-back-matter.tex')
    if reference_receipt['references_without_source_anchor']:raise ValueError('reference target absent from selected book')
    notation=SourceMath(resolver=inputs.resolve)
    notation.formula_library(inputs.text('sty/open-logic-formulas.sty'),'sty/open-logic-formulas.sty')
    for name in profile['notation_configuration']:notation.configure(inputs.text(name),name)
    math,notation_receipt=notation.expand(text,'book-with-references.tex')
    display_settings=inputs.witness_json('display_settings')
    _,display=DisplayAdapter(proof_label_styles=display_settings['proof_label_styles'],math_font_sizes=display_settings['math_font_sizes']).prepare(math,'book-math-context.tex')
    return {'math_source':math,'projected_source':projected,'prose_macro_definitions':definitions,'projection':projection,'tokens':token_receipt,
        'glossary':glossary_receipt,'glossary_tokens':glossary_tokens,'references':reference_receipt,
        'bibliography':bibliography,'citations':citations,'photos':photos,'notation':notation_receipt,'display':display,
        'inputs':inputs.inputs,'import_lock_sha256':lock['lock_sha256'],'reader_complete':False}
