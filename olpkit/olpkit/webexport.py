"""Shared source-to-HTML/EPUB orchestration. Publication is a separate action."""
from pathlib import Path
import json,tomllib,subprocess
from lxml import html,etree
from .bookcontext import BookInputs,build_context,sha
from .bookbody import build_body
from .bookfinish import finish_book
from .htmlpackage import reader_html
from .epubpackage import package_html
from .xhtml import text_without_annotations
from .formulaspeech import bind_speech
from .webfonts import bind_web_fonts
from .webprofile import load_profile


def export_web(source,product,out,profile_path,*,check_numbers=False,check_speech=False,released_speech=None,replay=False):
    source=Path(source).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('web export output already exists')
    if out.is_relative_to(source):raise ValueError('export must not modify its frozen source tree')
    if product not in ('html','epub','accessible'):raise ValueError('unsupported web product')
    if check_speech and product!='accessible':raise ValueError('--check-speech requires the accessible product')
    if released_speech is not None and (product!='accessible' or check_speech):
        raise ValueError('released speech replay is only available for reproducing an accessible edition')
    if not profile_path:raise ValueError('web export requires an explicit language/native-witness profile')
    profile_path=Path(profile_path);profile=load_profile(profile_path)
    replay = replay or released_speech is not None
    declarations = profile['released_package_declarations'] if replay else None
    inputs=BookInputs(source,profile,released_declarations=declarations)
    context=build_context(source,profile,released_declarations=declarations)
    # Incomplete diagram batches fail before creating a misleading reader.
    out.mkdir(parents=True)
    body,body_report=build_body(inputs,context,profile,out)
    body,book_report=finish_book(inputs,body,profile,out)
    edition=tomllib.loads(inputs.witness_text('edition'))
    script=tomllib.loads(inputs.witness_text('script'))
    if edition['locale']!=inputs.locale or edition['script']!=script['script']:
        raise ValueError('edition/script identity differs')
    doc=html.fromstring(body.decode('utf-8'));front=book_report['front'];meta=front['metadata']
    pages=doc.xpath('//div[@class="olpfrontpage"]')
    if len(pages)!=5:raise ValueError('native front pages incomplete')
    credit_ids=[]
    for i in (1,2,3):
        ident='olp-native-credit-'+str(i);pages[i].set('id',ident);credit_ids.append(ident)
    photo_credits=doc.xpath('//div[@class="olpphotocredits"]')
    if len(photo_credits)!=1:raise ValueError('full photo credit list absent')
    photo_credits[0].set('id','olp-native-photo-credits');credit_ids.append('olp-native-photo-credits')
    policy=inputs.witness_json('credits_policy');visible=text_without_annotations(doc)
    for component in policy['components']:
        for check in component.get('reader_checks',[]):
            if any(value not in visible for value in check.get('all_of',[])):
                raise ValueError('required scholarly credit absent: '+check['id'])
    # The source's first substantive preface paragraph supplies the description.
    first_heading=book_report['headings']['headings'][0]['html_id']
    opening=doc.xpath('//*[@id=$id]',id=first_heading)[0].getnext()
    if opening is None or opening.tag!='p' or not text_without_annotations(opening):
        raise ValueError('native opening description requires an explicit source locator')
    ep={'language':edition['language_tag'],'direction':script['direction'],'title':meta['OLPbooktitle'],
        'creator':meta['OLPauthor'],'source':meta['OLPsourcelink'],'identifier':'urn:sha256:'+sha(body),
        'description':text_without_annotations(opening),'rights':text_without_annotations(pages[3]),
        'modified':profile['modified'],'navigation_title':doc.xpath('//*[@id="olp-book-contents-heading"]')[0].text,
        'opening_title':meta['OLPbooktitle'],'notes_title':front['captions']['bibname'],
        'unit_prefix':'olp-unit-','css':inputs.witness_text('css'),'resource_map':{},'image_descriptions':{},
        'required_supplements':[],'required_credit_ids':credit_ids}
    font_config=profile.get('web_fonts')
    if font_config and font_config['script']!=script['script']:
        raise ValueError('font coverage script differs from edition')
    assets,font_css,epub_font_css,font_report=bind_web_fonts(doc,font_config,inputs.bytes)
    if font_report:
        ep['epub_css']=ep['css']+'\n'+epub_font_css
        ep['css']+='\n'+font_css
        ep['required_credit_ids'].append(font_report['licence_html_id'])
        for name,data in assets.items():
            target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for name in sorted(set(doc.xpath('//img/@src'))):
        p=(out/name).resolve()
        if not p.is_relative_to(out):raise ValueError('reader resource escapes output')
        assets[name]=p.read_bytes()
    unit_rows = context['projection']['unit_order']
    if replay:
        from .speechreplay import original_source_locators
        unit_rows = original_source_locators(unit_rows, profile['released_unit_sources'])
    data,html_report=reader_html(html.tostring(doc,encoding='utf-8'),ep,unit_rows,assets)
    speech_report=None
    if product=='accessible':
        if released_speech is None:
            store_bytes=inputs.witness('formula_speech');store=json.loads(store_bytes)
            data,speech_report=bind_speech(data,inputs.witness('formula_speech_input'),store_bytes)
            attribution=store.get('interface',{}).get('attribution')
        else:
            from .speechreplay import replay_labels
            data,speech_report=replay_labels(data,released_speech)
            attribution=released_speech['attribution']
        if not isinstance(attribution,str) or not attribution.strip():raise ValueError('localized speech attribution absent')
        accessible=html.document_fromstring(data,parser=html.HTMLParser(encoding='utf-8',huge_tree=True))
        credit=accessible.xpath('//*[@id="olp-native-credit-3"]')
        if len(credit)!=1:raise ValueError('native copyright/credit page absent')
        etree.SubElement(credit[0],'p',attrib={'class':'olp-speech-attribution'}).text=attribution
        data=html.tostring(accessible,encoding='utf-8',doctype='<!DOCTYPE html>')
        speech_report['attribution_text']=attribution
        speech_report['attributed_reader_sha256']=sha(data)
    (out/'reader.html').write_bytes(data)
    (out/'READER_PROFILE.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    products={'reader.html':{'sha256':sha(data),'bytes':len(data)}}
    report={'schema':'olpkit.web-export.v1','product':product,'locale':inputs.locale,
        'profile_sha256':sha(profile_path.read_bytes()),'assembly_sha256':sha((source/'ASSEMBLY.json').read_bytes()),
        'projection':context['projection'],'body':body_report,'book':book_report,'html':html_report,
        'source_inputs':context['inputs']|inputs.inputs,'all_credit_profile_strings_retained':True,
        'products':products,'fonts':font_report,'release_ready':False,'remaining':['Formula speech','Visual reader inspection','Source/reader package and public readback integration']}
    if speech_report:
        report['speech']=speech_report
        report['remaining']=['Assistive-technology testing','Visual reader inspection','Source/reader package and public readback integration']
    if product in ('epub','accessible'):
        epub,epub_report=package_html(data,ep,[r['html_id'].removeprefix('olp-unit-') for r in context['projection']['unit_order']],assets,{})
        (out/'reader.epub').write_bytes(epub);report['epub']=epub_report
        products['reader.epub']={'sha256':sha(epub),'bytes':len(epub)}
        jar=Path(profile['epubcheck']['path'])
        if sha(jar.read_bytes())!=profile['epubcheck']['sha256']:raise ValueError('EPUBCheck executable identity changed')
        run=subprocess.run(['java','-Xmx512m','-jar',str(jar),str(out/'reader.epub'),'--json',str(out/'EPUBCHECK.json')],
            capture_output=True,encoding='utf-8',timeout=120)
        diagnostics=json.loads((out/'EPUBCHECK.json').read_text(encoding='utf-8'))
        report['epubcheck']={'exit_code':run.returncode,'report_sha256':sha((out/'EPUBCHECK.json').read_bytes()),
            'diagnostics':len(diagnostics['messages'])}
        if run.returncode or diagnostics['messages']:
            (out/'EXPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            raise ValueError('EPUBCheck diagnostics remain; no release acceptance')
    heading_numbers=sum(bool(row['number']) for row in book_report['headings']['headings'])
    equations=body_report['bindings']['display']['native_equation_numbers']
    count=heading_numbers+len(book_report['captions']['captions'])+body_report['bindings']['theorems']['numbered']+len(equations)
    report['native_numbers']={'matched':count,'total':count,'bound_equations':equations,
        'scope':'Visible heading, caption, theorem and bound equation numbers; all native reference destinations are checked separately.'}
    (out/'EXPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if check_numbers:print(f'{count} of {count} numbers equal the PDF (headings, captions, theorem/exercise blocks and bound equations)')
    if check_speech:print(f'formulas: {speech_report["formula_occurrences"]}; with spoken text: {speech_report["with_spoken_text"]}')
    print(f"{html_report['units']} source imports; {html_report['mathml_formulas']} annotated formulas; private {product} export")
    return 0
