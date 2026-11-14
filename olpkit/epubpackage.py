"""Data-driven packaging adapted from the released Gujarati EPUB producer.

Source: KokunoYumeto/OpenLogic-gu-Gujr-IN at
085336b59ab402c2daae25216371b9ecae08ceb7, tools/build_full_epub.py.
This packages already-converted HTML; it is not a LaTeX converter or release gate.
"""
from datetime import datetime
import hashlib
import io
import json
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import unquote
import zipfile

from lxml import etree, html

from .xhtml import XHTML, MATHML, EPUB, XML, clone_xhtml, local_name, make_container, text_without_annotations

OPF='http://www.idpf.org/2007/opf'
DC='http://purl.org/dc/elements/1.1/'
MEDIA={'.xhtml':'application/xhtml+xml','.css':'text/css','.svg':'image/svg+xml',
       '.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.ttf':'font/ttf','.otf':'font/otf'}


def digest(data):return hashlib.sha256(data).hexdigest()


def safe_name(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or p.as_posix()!=name:
        raise ValueError('unsafe package member')
    return name


def math_signature(node, anchor_owners=None):
    # HTML exposes namespace declarations as attributes; XML stores them in
    # nsmap. Compare actual mathematical attributes after namespace conversion.
    attributes = []
    for name, value in node.attrib.items():
        if name == 'xmlns' or name.startswith('xmlns:'):
            continue
        if name.startswith('xml:'):
            name = '{' + XML + '}' + name[4:]
        if name == 'href' and anchor_owners is not None:
            member, separator, fragment = value.partition('#')
            ident = unquote(fragment)
            if separator and ident in anchor_owners and member in ('', anchor_owners[ident]):
                value = '#' + ident
        attributes.append((name, value))
    return [local_name(str(node.tag)),sorted(attributes),node.text,
            [[math_signature(child,anchor_owners),child.tail] for child in node if isinstance(child.tag,str)]]


def package_html(source_bytes, profile, expected_units, assets, supplements):
    """Return EPUB bytes and measured preservation facts without file-system writes.

    All edition text is input data. Assets map package-relative paths to bytes;
    profile.resource_map maps each source image URL to one such path. Supplement
    XHTML (credits, licences, edition notice) is already localized by its owner.
    """
    required=('language','direction','title','creator','identifier','source','description','rights',
              'modified','navigation_title','opening_title','notes_title','unit_prefix','css',
              'resource_map','image_descriptions','required_supplements')
    if any(k not in profile for k in required):raise ValueError('incomplete EPUB edition data')
    if profile['direction'] not in ('ltr','rtl') or not profile['language']:
        raise ValueError('explicit language and direction required')
    if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',profile['modified']):
        raise ValueError('EPUB modification time must be explicit UTC')
    moment=datetime.strptime(profile['modified'],'%Y-%m-%dT%H:%M:%SZ')
    if moment.year<1980:raise ValueError('ZIP timestamp precedes 1980')
    if len(expected_units)!=len(set(expected_units)) or not expected_units:
        raise ValueError('unit order must be a nonempty unique list')
    credit_ids=profile.get('required_credit_ids',[])
    if (not profile['required_supplements'] and not credit_ids) or not set(profile['required_supplements']).issubset(supplements):
        raise ValueError('required localized credit/notice documents absent')
    parser=html.HTMLParser(encoding='utf-8',huge_tree=True)
    source=html.document_fromstring(source_bytes,parser=parser)
    if source.get('lang') not in (None,profile['language']) or source.get('dir') not in (None,profile['direction']):
        raise ValueError('input language or direction conflicts with edition data')
    if source.xpath('.//script|.//svg'):raise ValueError('scripts or unbound inline vectors are not package inputs')
    body=source.find('body')
    if body is None or (body.text or '').strip():raise ValueError('body content must have explicit block elements')
    for ident in credit_ids:
        credits=body.xpath('.//*[@id=$id]',id=ident)
        if len(credits)!=1 or not text_without_annotations(credits[0]):
            raise ValueError('required in-book credit/notice absent or empty')
    navs=body.xpath('.//nav[@id="TOC"]')
    if len(navs)!=1:raise ValueError('one source table of contents is required')
    nav=navs[0]
    # Native book front matter may contain the contents inside a page wrapper.
    # Preserve its following text while separating the EPUB navigation document.
    parent=nav.getparent();previous=nav.getprevious()
    if nav.tail:
        if previous is None:parent.text=(parent.text or '')+nav.tail
        else:previous.tail=(previous.tail or '')+nav.tail
        nav.tail=None
    parent.remove(nav)
    visible=text_without_annotations(body)
    input_math=nav.xpath('.//math')+body.xpath('.//math')
    for math in input_math:
        if not any(a.get('encoding','').lower() in ('application/x-tex','text/x-tex','application/x-latex')
                   and ''.join(a.itertext()).strip() for a in math.iter('annotation')):
            raise ValueError('MathML formula lacks its nonempty TeX annotation')
    prefix=profile['unit_prefix']
    observed_units=[e.get('id')[len(prefix):] for e in body.xpath('.//*[@id]') if e.get('id').startswith(prefix)]
    if observed_units!=expected_units:raise ValueError('source unit order or coverage differs')

    def document(title):
        root=etree.Element('{'+XHTML+'}html',nsmap={None:XHTML,'epub':EPUB})
        root.set('lang',profile['language']);root.set('{'+XML+'}lang',profile['language']);root.set('dir',profile['direction'])
        head=etree.SubElement(root,'{'+XHTML+'}head');etree.SubElement(head,'{'+XHTML+'}title').text=title
        etree.SubElement(head,'{'+XHTML+'}link',rel='stylesheet',href='styles/reader.css')
        return root,etree.SubElement(root,'{'+XHTML+'}body')

    chunks=[];current=[]
    for child in body:
        if not isinstance(child.tag,str):continue
        boundary=child.tag in ('h1','h2') or 'footnotes' in child.get('class','').split()
        if boundary and current:chunks.append(current);current=[]
        current.append(child)
    if current:chunks.append(current)
    docs=[]
    for i,children in enumerate(chunks,1):
        headings=[c for c in children if c.tag in ('h1','h2')]
        title=text_without_annotations(headings[0]) if headings else profile['opening_title' if i==1 else 'notes_title']
        root,target=document(title)
        for child in children:target.append(clone_xhtml(child))
        docs.append((f'chapter-{i:03}.xhtml',root,target))
    navroot,navbody=document(profile['navigation_title']);toc=clone_xhtml(nav)
    toc.set('{'+EPUB+'}type','toc');navbody.append(toc)
    for node in toc.xpath('.//*[local-name()="ul"]'):node.tag='{'+XHTML+'}ol'
    documents={'nav.xhtml':navroot,**{name:root for name,root,_ in docs}}
    for name,data in supplements.items():
        safe_name(name)
        if not name.endswith('.xhtml') or name in documents:raise ValueError('invalid supplement member')
        node=etree.fromstring(data,parser=etree.XMLParser(resolve_entities=False,no_network=True))
        if node.tag!='{'+XHTML+'}html' or node.get('lang')!=profile['language'] or node.get('dir')!=profile['direction']:
            raise ValueError('supplement is not localized XHTML')
        if node.xpath('.//*[local-name()="script"]'):raise ValueError('scripted supplement is not permitted')
        documents[name]=node
    id_owner={}
    for name,node in documents.items():
        for element in node.xpath('.//*[@id]'):
            ident=element.get('id')
            if ident in id_owner:raise ValueError('duplicate document identifier: '+ident)
            id_owner[ident]=name
    expected_math=[math_signature(m,id_owner) for m in input_math]
    files={}
    for name,data in assets.items():
        safe_name(name)
        if PurePosixPath(name).suffix.lower() not in ('.svg','.png','.jpg','.jpeg','.ttf','.otf') or name in documents:
            raise ValueError('invalid or colliding resource member')
        files[name]=data
    for name,node in documents.items():
        for image in node.xpath('.//*[local-name()="img"]'):
            original=image.get('src','');mapped=profile['resource_map'].get(original)
            if mapped is None and original in assets:mapped=original
            if mapped not in assets:raise ValueError('unregistered image resource')
            image.set('src',mapped)
            decorative=image.get('role')=='presentation' and image.get('alt')==''
            if not image.get('alt') and not decorative:
                figures=image.xpath('ancestor::*[local-name()="figure"]')
                captions=figures[-1].xpath('.//*[local-name()="figcaption"]') if figures else []
                alt=text_without_annotations(captions[0]) if captions else profile['image_descriptions'].get(original)
                if not alt:raise ValueError('image description absent')
                image.set('alt',alt)
        for element in node.xpath('.//*[@href]'):
            href=element.get('href')
            if href.startswith('#'):
                ident=unquote(href[1:])
                if ident not in id_owner:raise ValueError('unresolved fragment: '+ident)
                element.set('href',id_owner[ident]+'#'+ident)
            if element.get('role')=='doc-noteref':element.set('{'+EPUB+'}type','noteref')
        for element in node.xpath('.//*[@id]'):
            if re.fullmatch(r'fn\d+',element.get('id','')):element.set('{'+EPUB+'}type','footnote')
    actual_text=' '.join(text_without_annotations(target) for _,_,target in docs)
    if visible!=' '.join(actual_text.split()):raise ValueError('visible content changed during packaging')
    actual_math=[math_signature(m,id_owner) for node in [navroot]+[n for _,n,_ in docs]
                 for m in node.iter('{'+MATHML+'}math')]
    if expected_math!=actual_math:
        first=next((i for i,(a,b) in enumerate(zip(expected_math,actual_math)) if a!=b),None)
        raise ValueError(f'MathML structure or annotation changed: {len(expected_math)} input, '
                         f'{len(actual_math)} output formulas; first mismatch {first}')
    # A non-linear navigation document must also be reachable by an ordinary
    # link. Keep that localized navigation affordance outside the retained
    # mathematical text; do not prepend it to a source heading or change titles.
    contents_link=etree.SubElement(docs[0][2],'{'+XHTML+'}p',attrib={'class':'olp-contents-link'})
    etree.SubElement(contents_link,'{'+XHTML+'}a',href='nav.xhtml').text=profile['navigation_title']
    files['styles/reader.css']=profile['css'].encode('utf-8')
    for url in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',profile['css']):
        member=posixpath.normpath(posixpath.join('styles',unquote(url.strip())))
        if member not in assets:raise ValueError('CSS resource is not in the asset inventory')
    for name,node in documents.items():
        for element in node.xpath('.//*[@href or @src]'):
            value=element.get('src') or element.get('href')
            if value.startswith(('https:','http:','mailto:')) and element.get('src') is None:continue
            member,_,fragment=value.partition('#');member=unquote(member);safe_name(member)
            if member not in files and member not in documents:raise ValueError('unresolved package link: '+member)
            if fragment and id_owner.get(unquote(fragment))!=member:raise ValueError('fragment points at the wrong document')
        files[name]=etree.tostring(node,encoding='utf-8',xml_declaration=True,doctype='<!DOCTYPE html>')
    package=etree.Element('{'+OPF+'}package',nsmap={None:OPF,'dc':DC},version='3.0')
    package.set('unique-identifier','publication-id');package.set('{'+XML+'}lang',profile['language'])
    metadata=etree.SubElement(package,'{'+OPF+'}metadata')
    for name in ('identifier','title','language','creator','source','description','rights'):
        element=etree.SubElement(metadata,'{'+DC+'}'+name);element.text=profile[name]
        if name=='identifier':element.set('id','publication-id')
    etree.SubElement(metadata,'{'+OPF+'}meta',property='dcterms:modified').text=profile['modified']
    manifest=etree.SubElement(package,'{'+OPF+'}manifest');href_ids={}
    for i,name in enumerate(sorted(files),1):
        ident='item-'+str(i);href_ids[name]=ident
        item=etree.SubElement(manifest,'{'+OPF+'}item',id=ident,href=name)
        item.set('media-type',MEDIA[PurePosixPath(name).suffix.lower()]);properties=[]
        if name=='nav.xhtml':properties.append('nav')
        if name in documents and list(documents[name].iter('{'+MATHML+'}math')):properties.append('mathml')
        if properties:item.set('properties',' '.join(properties))
    spine=etree.SubElement(package,'{'+OPF+'}spine');spine.set('page-progression-direction',profile['direction'])
    for name in ['nav.xhtml']+[n for n,_,_ in docs]+list(supplements):
        etree.SubElement(spine,'{'+OPF+'}itemref',idref=href_ids[name],linear='no' if name=='nav.xhtml' else 'yes')
    members={'META-INF/container.xml':make_container(),**{'OEBPS/'+n:b for n,b in files.items()},
             'OEBPS/package.opf':etree.tostring(package,encoding='utf-8',xml_declaration=True)}
    stream=io.BytesIO();zip_time=(moment.year,moment.month,moment.day,moment.hour,moment.minute,moment.second)
    with zipfile.ZipFile(stream,'w') as archive:
        item=zipfile.ZipInfo('mimetype',zip_time);item.compress_type=zipfile.ZIP_STORED
        archive.writestr(item,b'application/epub+zip')
        for name,data in sorted(members.items()):
            item=zipfile.ZipInfo(name,zip_time);item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16
            archive.writestr(item,data,compresslevel=9)
    output=stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(output)) as archive:
        if archive.testzip() is not None:raise ValueError('EPUB archive CRC failure')
    return output,{'source_html_sha256':digest(source_bytes),'profile_sha256':digest(json.dumps(profile,ensure_ascii=False,sort_keys=True).encode()),
                   'epub_sha256':digest(output),'epub_bytes':len(output),'unit_order':expected_units,
                   'mathml_formulas':len(expected_math),'visible_text_preserved':True,'mathml_structure_preserved':True,
                   'added_navigation_links':[{'destination':'nav.xhtml','text':profile['navigation_title']}],
                   'assets':{n:digest(b) for n,b in assets.items()},'supplements':{n:digest(b) for n,b in supplements.items()},
                   'release_ready':False,'remaining':'Input/source binding, numbering, credits, visual inspection and EPUBCheck are external gates.'}
