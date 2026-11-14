"""Native front matter, artwork, contents and figure numbering for web exports."""
from pathlib import Path
import re,subprocess,collections
from urllib.parse import unquote
from lxml import html
from .bookcontext import sha,_one
from .bookfront import native_frontmatter
from .bookart import bind_book_art
from .bookheadings import read_contents,bind_headings
from .bookcaptions import bind_captions
from .references import read_aux
from .mathsource import SourceMath
from .texttokens import TextTokens


def finish_book(inputs,body_bytes,profile,output):
    output=Path(output);b=inputs.book;a=inputs.assembly;f=profile['frontmatter']
    native_manifest=inputs.witness_json('native_source_manifest')
    def same_native(name):
        data=inputs.bytes(name)
        if sha(data)!=native_manifest['files'][name]['sha256']:
            raise ValueError('native front-matter/art input differs: '+name)
        return data.decode('utf-8-sig')
    projection,definitions,front=native_frontmatter(same_native('sty/open-logic-book.cls'),
        same_native(f['metadata']),same_native(profile['locale_source']),same_native(f['cover_text']),
        inputs.text(f['driver']),language=profile['babel'],evidence={'source_inputs':dict(inputs.inputs)})
    definitions=re.sub(r'(\[width=)(\.\d+cm\])',r'\g<1>0\2',definitions)
    def pandoc(text):
        run=subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],input=text,
            encoding='utf-8',capture_output=True,timeout=90)
        if run.returncode or run.stderr:raise ValueError('native book conversion diagnostics: '+run.stderr[:1000])
        return html.fromstring(run.stdout)
    doc=html.fromstring(body_bytes.decode('utf-8'))
    for i,node in enumerate(list(pandoc(definitions+'\n'+projection))):doc.insert(i,node)
    def resolve_art(raw):
        name=raw.replace(r'\OLPassetversion',f['asset_version'])
        name=name.removeprefix(r'\olpath/') if name.startswith(r'\olpath/') else b+'/'+name
        matches=[n for n in [name,name+'.pdf',name+'.png'] if n in a['files']]
        if len(matches)!=1:raise ValueError('native artwork source absent or ambiguous')
        name=matches[0];data=inputs.bytes(name)
        if sha(data)!=native_manifest['files'][name]['sha256']:raise ValueError('native artwork differs')
        return inputs.root/name,sha(data)
    after=inputs.text(profile['prose_definition_source'])
    width=float(_one(r'\\newcommand\*\{\\olpCoverPortraitWidth\}\{([0-9.]+)\}',after,'cover portrait width')[1])*100
    art=bind_book_art(doc,resolve=resolve_art,output=output,cover_width_percent=width,
        evidence={'native_manifest_sha256':sha(inputs.witness('native_source_manifest')),
                  'cover_width_source_sha256':sha(after.encode()),'asset_mode':f['asset_version']},
        rasterize_pdf_hashes=f['decorative_raster_hashes'])
    toc=inputs.witness_text('toc');rows=read_contents(toc,language_wrapper='bbl@ensure@'+profile['babel'])
    notation=SourceMath(resolver=inputs.resolve)
    notation.formula_library(inputs.text('sty/open-logic-formulas.sty'),'sty/open-logic-formulas.sty')
    for name in profile['notation_configuration']:notation.configure(inputs.text(name),name)
    fonts,_=notation.font_preamble()
    titles='\n'.join(r'\begin{olpnativetoctitle}'+row['title_tex']+r'\end{olpnativetoctitle}' for row in rows)
    titles,_=notation.expand(titles,'native-toc-titles.tex')
    title_doc=pandoc(fonts+'\n'+titles)
    rendered=title_doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpnativetoctitle ")]')
    rendered=[n[0] if len(n)==1 and n[0].tag=='p' else n for n in rendered]
    config=inputs.text(profile['token_base_source']);env=inputs.text('sty/open-logic-book-envs.sty')
    if r'\newenvironment{reading}{\paragraph{\readingname}\par}{}' not in env:
        raise ValueError('native reading heading changed')
    problems=_one(r'\\setlocalecaption\{'+re.escape(profile['babel'])+r'\}\{problems\}\{([^{}]+)\}',config,'exercise heading')[1]
    contents=_one(r'\\renewcommand\{\\contentsname\}\{([^{}]+)\}',config,'contents heading')[1]
    headings=bind_headings(doc,rows,rendered,reading_title=front['captions']['readingname'],
        problems_title=problems,contents_title=contents,evidence={'native_toc_sha256':sha(toc.encode()),
        'native_reading_environment_sha256':sha(env.encode()),'locale_config_sha256':sha(config.encode())})
    aux=read_aux(inputs.witness_text('aux'))
    caption_rows=[(key,row) for key,row in aux.items() if row.get('kind') in ('figure','table') and not key.startswith('photo-')]
    captions='\n'.join(r'\begin{olpnativecaption}'+row['title_tex']+r'\end{olpnativecaption}' for key,row in caption_rows)
    tokens=TextTokens(modern_xparse=profile['modern_xparse'],resolver=inputs.resolve)
    tokens.configure_native(inputs.text('sty/open-logic-tokenize.sty'),'sty/open-logic-tokenize.sty')
    for name in profile['notation_configuration']:tokens.configure(inputs.text(name),name)
    captions,_=tokens.expand(captions,'native-captions.tex');captions,_=notation.expand(captions,'native-captions.tex')
    caption_doc=pandoc(fonts+'\n'+captions)
    rendered_captions=caption_doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpnativecaption ")]')
    if len(rendered_captions)!=len(caption_rows):raise ValueError('caption title rendering incomplete')
    nameref=inputs.package('nameref.sty')
    if br'\def\NR@strip@period#1.\@empty#2\@nil{#1}' not in nameref:
        raise ValueError('native caption terminal-period elision rule changed')
    caption_report=bind_captions(doc,aux,{key:title for (key,row),title in zip(caption_rows,rendered_captions)},
        names={'figure':front['captions']['figurename'],'table':front['captions']['tablename']},
        evidence={'native_aux_sha256':sha(inputs.witness('aux')),'nameref_source_sha256':sha(nameref)},
        native_aux_drops_terminal_period=True)
    ids=collections.Counter(doc.xpath('//@id'))
    for href in doc.xpath('//@href[starts-with(.,"#")]'):
        if ids[unquote(href[1:])]!=1:raise ValueError('native numbered link has no unique target')
    for src in doc.xpath('//img/@src'):
        path=(output/src).resolve()
        if not path.is_relative_to(output.resolve()) or not path.is_file():raise ValueError('book image absent')
    data=html.tostring(doc,encoding='utf-8')
    if b'OLPBOOKTOC' in data:raise ValueError('contents insertion unresolved')
    return data,{'front':front,'headings':headings,'captions':caption_report,'art':art,
        'body_sha256':sha(data),'reader_complete':False}
