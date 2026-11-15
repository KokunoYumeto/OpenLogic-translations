"""Convert the entire selected book body, retaining every native diagram."""
from pathlib import Path
import json,re,subprocess,shutil,collections
from urllib.parse import unquote
from lxml import html
from .bookcontext import sha,_one,source_caption
from .figureassets import expand_external_figures,combine_exports,initial_asset_width
from .figurebinding import prepare_figures,bind_figures,attach_long_descriptions
from .theoremblocks import native_theorems,reconcile_theorem_source,prepare_theorems,bind_theorems
from .mathsource import SourceMath
from .mathdisplay import DisplayAdapter,bind_mathml
from .references import bind_references
from .glossary import bind_glossary
from .bibliography import bind_bibliography
from .bookphotos import bind_photos
from .selective import explicit_group_end
from .macrophases import COMMAND,mask_comments


def pandoc_import_scopes(text):
    """Use one group notation for synthetic import wrappers, retaining their bodies.

    Pandoc misparses an explicit begin/endgroup nested in a brace-scoped chapter.
    Only identified document imports already inside native brace groups are
    adapted; authored math, macro arguments and inner scopes remain unchanged.
    """
    pattern=r'\\hypertarget\{(olp-unit-\d+)\}\{\}(\\begingroup)\\def\\ol@sectioncs\{[A-Za-z]+\}'
    edits=[];rows=[];code=mask_comments(text);pos=0;depth=0
    for hit in re.finditer(pattern,text):
        start,end=hit.span(2);stop,finish=explicit_group_end(text,end)
        # Leave ordinary explicit import scopes alone: some of their bodies
        # contain further explicit layout scopes. The failing case is a native
        # brace wrapper surrounding an imported document block.
        while pos<hit.start():
            if code[pos]=='\\':
                command=COMMAND.match(code,pos);pos=command.end()
                if command[1] in ('verb','Verb'):
                    if code[pos:pos+1]=='*':pos+=1
                    delimiter=code[pos:pos+1];close=code.find(delimiter,pos+1)
                    if not delimiter or close<0:raise ValueError('unclosed verbatim before import')
                    pos=close+1
                elif command[1]=='string':
                    literal=COMMAND.match(code,pos)
                    pos=literal.end() if literal else pos+1
                continue
            if code[pos]=='{':depth+=1
            elif code[pos]=='}':depth-=1
            pos+=1
        if depth<=0:continue
        edits.extend([(start,end,'{'),(stop,finish,'}')])
        rows.append({'unit':hit[1],'start':start,'end':finish,
                     'unchanged_body_sha256':sha(text[end:stop].encode())})
    edits.sort()
    if any(a[1]>b[0] for a,b in zip(edits,edits[1:])):raise ValueError('overlapping import scope adaptation')
    result=text
    for start,end,replacement in reversed(edits):result=result[:start]+replacement+result[end:]
    return result,{'input_sha256':sha(text.encode()),'output_sha256':sha(result.encode()),
                  'imports':rows,'scope':'Synthetic document import group notation only; no source prose or mathematical edits.'}


def build_body(inputs,context,profile,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    style=inputs.text('sty/open-logic.sty')
    default_width,width_evidence=initial_asset_width(inputs.text('sty/open-logic-book.cls'),style)
    math,external=expand_external_figures(context['math_source'],read=inputs.bytes,
        default_width_percent=default_width,
        evidence={**width_evidence,'assembly_sha256':sha((inputs.root/'ASSEMBLY.json').read_bytes())})
    exports=[]
    for row in profile['figure_exports']:
        directory=Path(row['directory']);data=(directory/'NATIVE_FIGURES.json').read_bytes()
        if sha(data)!=row['receipt_sha256']:raise ValueError('native figure export identity changed')
        record=json.loads(data)
        if record.get('status')!='vectors_exported_pending_visual_and_semantic_checks':
            raise ValueError('native diagram export is not complete')
        exports.append((directory,record))
    assets=output/'assets/native'
    exported=combine_exports(math,exports,assets,external=external)
    prepared,figure_receipt=prepare_figures(math,'book-math-context.tex',exported,assets)
    native_thm=inputs.witness_text('thm');native_records=native_theorems(native_thm)
    reconcile_theorem_source(context['projected_source'],native_records)
    name_record=inputs.witness_json('names');names={k:v[0] for k,v in name_record['names'].items()}
    token_config=inputs.text(profile['token_base_source'])
    names['proof']=source_caption(token_config,profile['babel'],'proof')
    book_class=inputs.text('sty/open-logic-book.cls')
    symbol=_one(r'\\gdef\\proofSymbol\{\\ensuremath\{([^{}]+)\}\}',book_class,'proof symbol')[1]
    prepared,theorems=prepare_theorems(prepared,native_records,names,
        evidence={'native_thm_sha256':sha(native_thm.encode()),'source_projection_sha256':sha(context['projected_source'].encode()),
                  'native_pdf_sha256':sha(inputs.witness('pdf')),'names_source_sha256':sha(token_config.encode()),
                  'book_class_sha256':sha(book_class.encode())},proof_symbol=symbol)
    prepared,display=DisplayAdapter(proof_label_styles=context['display']['proof_label_styles'],
        math_font_sizes=context['display']['math_font_sizes'],
        native_references=context['references']).prepare(prepared,'book-body.tex')
    notation=SourceMath(resolver=inputs.resolve)
    notation.formula_library(inputs.text('sty/open-logic-formulas.sty'),'sty/open-logic-formulas.sty')
    for name in profile['notation_configuration']:notation.configure(inputs.text(name),name)
    fonts,font_records=notation.font_preamble()
    prepared,scope_report=pandoc_import_scopes(prepared)
    command=[shutil.which('pandoc'),'-f','latex','-t','html5','--mathml']
    run=subprocess.run(command,input=fonts+'\n'+context['prose_macro_definitions']+'\n'+prepared,
        capture_output=True,encoding='utf-8',timeout=90)
    if run.returncode or run.stderr:raise ValueError('body conversion has diagnostics: '+run.stderr[:1000])
    doc=html.fromstring(run.stdout)
    bindings={'import_scopes':scope_report,'display':bind_mathml(doc,display),'references':bind_references(doc,context['references']),
        'theorems':bind_theorems(doc,theorems),'glossary':bind_glossary(doc,context['glossary']),
        'bibliography':bind_bibliography(doc,context['bibliography'],context['citations']),
        'photographs':bind_photos(doc,context['photos'])}
    for row in context['photos']['photos']:
        data=inputs.bytes(row['asset'])
        if sha(data)!=row['asset_sha256']:raise ValueError('photo bytes changed')
        dest=output/row['output_asset'];dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists() or dest.read_bytes()!=data:dest.write_bytes(data)
    description_sets=[]
    for key in profile['diagram_description_witnesses']:
        record=inputs.witness_json(key)
        if description_sets and record['labels']!=description_sets[0]['labels']:
            raise ValueError('diagram navigation labels disagree')
        description_sets.append(record)
    descriptions={}
    for row in exported['figures']:
        matches=[r['descriptions'][row['source_sha256']] for r in description_sets if row['source_sha256'] in r['descriptions']]
        if len(matches)!=1:raise ValueError('diagram description missing or ambiguous')
        desc=matches[0]
        if row['origin_index'] not in desc['occurrence_indices']:raise ValueError('description occurrence differs')
        key=row['source_sha256']
        if key not in descriptions:descriptions[key]={**desc,'original_occurrence_indices':desc['occurrence_indices'],'occurrence_indices':[]}
        descriptions[key]['occurrence_indices'].append(row['index'])
    figure_name=names['figure']
    bindings['figures']=bind_figures(doc,figure_receipt,asset_prefix='assets/native',fallback_alt=figure_name,
        descriptions={key:r['alt_text'] for key,r in descriptions.items()})
    bindings['diagram_descriptions']=attach_long_descriptions(doc,figure_receipt,descriptions,
        labels=description_sets[0]['labels'],figure_label=figure_name)
    images=doc.xpath('.//span[@class="olp-native-figure"]')
    if [n.get('data-source-sha256') for n in images]!=[r['source_sha256'] for r in exported['figures']]:
        raise ValueError('full diagram order differs from source')
    if doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," math ") and not(.//math)]'):
        raise ValueError('unconverted mathematical expression')
    ids=collections.Counter(doc.xpath('//@id'))
    for href in doc.xpath('//@href[starts-with(.,"#")]'):
        if ids[unquote(href[1:])]!=1:raise ValueError('body reference missing or ambiguous')
    data=html.tostring(doc,encoding='utf-8')
    if any(marker in data for marker in [b'OLPNATIVEFIG',b'OLPXREF',b'OLPDISPLAY',b'OLPTHEOREM']):
        raise ValueError('unbound conversion marker')
    return data,{'schema':'olpkit.book-body.v1','body_sha256':sha(data),'bindings':bindings,
        'mathml_formulas':len(doc.xpath('//math')),'figures':len(images),'external_figures':external,
        'font_records':font_records,'pandoc_warnings':0,'new_tex_runs':0,'reader_complete':False}
