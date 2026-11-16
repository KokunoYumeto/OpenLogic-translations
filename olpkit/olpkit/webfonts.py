"""Embed the edition's actual open font bytes and their original licence."""
from pathlib import PurePosixPath
from io import BytesIO
import hashlib,re
from lxml import etree
from fontTools.ttLib import TTFont
from fontTools.unicodedata import script_extension
from .xhtml import text_without_annotations


def bind_web_fonts(document, config, read):
    if not config:return {},'', '',None
    family=config['family']
    script=config['script']
    if not re.fullmatch(r'[A-Z][a-z]{3}',script):raise ValueError('explicit ISO script required for font coverage')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9 -]+',family):raise ValueError('unsafe CSS font family')
    faces=config['faces'];weights=[r['weight'] for r in faces]
    if not faces or len(weights)!=len(set(weights)) or any(w not in (400,700) for w in weights):
        raise ValueError('explicit regular/bold source font faces required')
    ident='olp-web-font-licence'
    if document.xpath('.//*[@id=$id]',id=ident):raise ValueError('font licence identifier already exists')
    licence=read(config['licence_source'])
    if 'title_source' in config:
        title_path=config['title_source']
        title_source=read(title_path)
        heading=title_source.decode('utf-8-sig').splitlines()[0]
        if not heading.startswith('# ') or not heading[2:].strip():raise ValueError('native font notice heading absent')
        title=heading[2:].strip()
    else:
        # The embedded family name is checked against every font face below.
        title_path=faces[0]['source']
        title_source=read(title_path)
        title=family
    if not licence.strip():raise ValueError('native font licence absent')
    assets={};html_css=[];epub_css=[];rows=[]
    text=text_without_annotations(document)+title+licence.decode('utf-8-sig')
    required={ord(c) for c in set(text) if script in script_extension(c)}
    for row in faces:
        source=row['source'];data=read(source);digest=hashlib.sha256(data).hexdigest()
        if PurePosixPath(source).suffix!='.ttf':raise ValueError('unsupported native web font')
        with TTFont(BytesIO(data)) as font:
            actual=font['name'].getDebugName(16) or font['name'].getDebugName(1)
            if actual!=family:raise ValueError('font family differs from source metadata')
            missing=required-set(font.getBestCmap())
            if missing:raise ValueError('native web font lacks used '+script+' characters: '+','.join(hex(c) for c in sorted(missing)))
        asset='assets/fonts/'+PurePosixPath(source).stem+'-'+digest[:12]+'.ttf'
        assets[asset]=data
        for prefix,css in (('',html_css),('../',epub_css)):
            css.append('@font-face{font-family:"'+family+'";font-style:normal;font-weight:'+str(row['weight'])+
                       ';src:url("'+prefix+asset+'") format("truetype");}')
        rows.append({'source':source,'asset':asset,'sha256':digest,'bytes':len(data),'weight':row['weight'],
                     'script':script,'required_script_characters':len(required),'missing_script_characters':0})
    declaration='body{font-family:"'+family+'",serif;}'
    html_css.append(declaration);epub_css.append(declaration)
    section=etree.SubElement(document,'section',id=ident,attrib={'class':'olp-font-licence'})
    etree.SubElement(section,'h1').text=title
    etree.SubElement(section,'pre',lang='en').text=licence.decode('utf-8-sig')
    report={'family':family,'script':script,'faces':rows,'licence_source':config['licence_source'],
            'licence_sha256':hashlib.sha256(licence).hexdigest(),'title_source':title_path,
            'title_source_sha256':hashlib.sha256(title_source).hexdigest(),'licence_html_id':ident,
            'native_licence_text_preserved':True}
    return assets,'\n'.join(html_css),'\n'.join(epub_css),report
