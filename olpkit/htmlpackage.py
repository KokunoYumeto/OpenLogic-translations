"""Wrap a source-bound book body without replacing its text or mathematics."""
from collections import Counter
import hashlib
from urllib.parse import unquote
from lxml import etree, html
from .xhtml import text_without_annotations
from .epubpackage import math_signature, safe_name


def reader_html(body_bytes, profile, unit_rows, assets):
    required=('language','direction','title','css','required_credit_ids')
    if any(k not in profile for k in required) or profile['direction'] not in ('ltr','rtl'):
        raise ValueError('explicit reader edition data required')
    source=html.fromstring(body_bytes.decode('utf-8'))
    if source.tag!='div' or (source.text or '').strip():
        raise ValueError('source must be a book body with block children')
    before=text_without_annotations(source)
    before_math=[math_signature(n) for n in source.xpath('.//math')]
    ids=Counter(source.xpath('.//@id'))
    if any(n!=1 for n in ids.values()):raise ValueError('duplicate reader identifier')
    actual=source.xpath('.//@id[starts-with(.,"olp-unit-")]')
    expected=[r['html_id'] for r in unit_rows]
    if not expected or actual!=expected or len(set(actual))!=len(actual):
        raise ValueError('executed import order or coverage differs')
    for row in unit_rows:
        node=source.xpath('.//*[@id=$id]',id=row['html_id'])[0]
        node.set('data-unit-id',row['unit'])
        node.set('data-source-sha256',row['sha256'])
    navs=source.xpath('.//nav[contains(concat(" ",normalize-space(@class)," ")," olp-book-contents ")]')
    if len(navs)!=1:raise ValueError('native book contents absent or duplicated')
    if navs[0].get('id') not in (None,'TOC') or ids.get('TOC',0):
        raise ValueError('reserved contents identifier conflicts')
    navs[0].set('id','TOC')
    if not profile['required_credit_ids']:raise ValueError('native credit blocks must be identified')
    for ident in profile['required_credit_ids']:
        nodes=source.xpath('.//*[@id=$id]',id=ident)
        if len(nodes)!=1 or not text_without_annotations(nodes[0]):raise ValueError('native credit block absent or empty')
    for image in source.xpath('.//img'):
        src=image.get('src','');safe_name(src)
        if src not in assets:raise ValueError('missing image bytes')
        if not image.get('alt') and not (image.get('role')=='presentation' and image.get('alt')==''):
            raise ValueError('substantive image lacks a description')
    for href in source.xpath('.//@href[starts-with(.,"#")]'):
        if href!='#TOC' and ids.get(unquote(href[1:]),0)!=1:raise ValueError('unresolved local reader link')
    root=etree.Element('html',lang=profile['language'],dir=profile['direction'])
    head=etree.SubElement(root,'head')
    etree.SubElement(head,'meta',charset='utf-8')
    etree.SubElement(head,'meta',name='viewport',content='width=device-width, initial-scale=1')
    etree.SubElement(head,'title').text=profile['title']
    etree.SubElement(head,'style').text=profile['css']
    body=etree.SubElement(root,'body')
    for child in list(source):body.append(child)
    if before!=text_without_annotations(body):raise ValueError('reader text changed')
    if before_math!=[math_signature(n) for n in body.xpath('.//math')]:raise ValueError('reader mathematics changed')
    data=html.tostring(root,encoding='utf-8',doctype='<!DOCTYPE html>')
    return data,{'schema':'olpkit.html-package.v1','input_sha256':hashlib.sha256(body_bytes).hexdigest(),
        'html_sha256':hashlib.sha256(data).hexdigest(),'units':len(unit_rows),'mathml_formulas':len(before_math),
        'text_preserved':True,'mathml_preserved':True,'images':len(body.xpath('.//img')),
        'language':profile['language'],'direction':profile['direction'],'release_ready':False}
