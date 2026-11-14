"""Bind reader headings and navigation to the actual native book contents."""
import re,unicodedata,copy
from .macrophases import group,skip_space,digest


def read_contents(text, *, language_wrapper=None):
    rows=[]
    for line in text.splitlines():
        if not line.startswith(r'\contentsline'):continue
        pos=len(r'\contentsline');fields=[]
        for _ in range(4):v,pos=group(line,pos);fields.append(v)
        kind,title,page,destination=fields;number='';native_title=title
        m=re.match(r'\\(partnumberline|chapternumberline|numberline)\b',title)
        if m:
            number,end=group(title,m.end());title=title[end:]
            if not re.fullmatch(r'[A-Za-z\d.]+',number):raise ValueError('unsupported native heading number')
        if language_wrapper and title.startswith('\\'+language_wrapper):
            unwrapped,end=group(title,len(language_wrapper)+1)
            if title[end:].strip():raise ValueError('additional content after native language wrapper')
            title=unwrapped
        if kind not in ('part','chapter','appendix','section','subsection','subsubsection','paragraph'):
            raise ValueError('unsupported native contents kind')
        rows.append({'kind':kind,'title_tex':title,'native_title_tex':native_title,'number':number,'page':page,'destination':destination})
    if not rows or len({r['destination'] for r in rows})!=len(rows):raise ValueError('native contents missing/duplicated')
    return rows


def visible_text(node):
    clone=copy.deepcopy(node)
    for n in clone.xpath('.//*[local-name()="annotation"]'):n.getparent().remove(n)
    return re.sub(r'\s+',' ',unicodedata.normalize('NFC',''.join(clone.itertext()))).strip()


def bind_headings(document, native_rows, native_rendered_titles, *, reading_title, problems_title, contents_title, evidence):
    from lxml import etree
    if not evidence or not all((reading_title,problems_title,contents_title)):
        raise ValueError('native heading configuration required')
    if len(native_rows)!=len(native_rendered_titles):raise ValueError('native title render count differs')
    reading=document.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," reading ")]')
    for i,node in enumerate(reading,1):
        if node.xpath('./h6'):raise ValueError('reading heading already present')
        h=etree.Element('h6',id='olp-reading-'+str(i));h.text=reading_title;node.insert(0,h)
    nodes=[n for n in document.xpath('//h1|//h2|//h3|//h4|//h5|//h6')
           if not n.xpath('ancestor::*[@id="olp-diagram-descriptions"]')
           and not n.xpath('ancestor::*[contains(concat(" ",normalize-space(@class)," ")," olpbookcover ")]')]
    if len(nodes)!=len(native_rows):raise ValueError('source/native heading coverage differs')
    level={'part':'h1','chapter':'h2','appendix':'h2','section':'h3','subsection':'h4','subsubsection':'h5','paragraph':'h6'}
    checked=[]
    for node,row,title in zip(nodes,native_rows,native_rendered_titles):
        if node.tag!=level[row['kind']]:raise ValueError('native heading hierarchy differs')
        expected=visible_text(title);actual=visible_text(node)
        if not actual and row['kind']=='section' and expected==problems_title:
            node.text=problems_title;actual=visible_text(node)
        if actual!=expected:raise ValueError('native heading title differs: '+repr((actual,expected)))
        if not node.get('id'):raise ValueError('reader heading anchor absent')
        if row['number']:
            prefix=etree.Element('span',attrib={'class':'olp-heading-number'});prefix.text=row['number']+' '
            prefix.tail=node.text;node.text=None;node.insert(0,prefix)
        checked.append({**row,'html_id':node.get('id'),'title_plain':expected,'number_matches':True})
    placeholders=document.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpbooktoc ")]')
    if len(placeholders)!=1:raise ValueError('book contents insertion absent/ambiguous')
    nav=placeholders[0];nav.clear();nav.tag='nav';nav.set('class','olp-book-contents');nav.set('aria-labelledby','olp-book-contents-heading')
    etree.SubElement(nav,'h2',id='olp-book-contents-heading').text=contents_title
    root=etree.SubElement(nav,'ol');stack=[(min(int(level[r['kind']][1:]) for r in checked),root)]
    for row,title in zip(checked,native_rendered_titles):
        depth=int(level[row['kind']][1:])
        while len(stack)>1 and stack[-1][0]>depth:stack.pop()
        parent=stack[-1][1]
        if stack[-1][0]<depth and len(parent):
            nested=etree.SubElement(parent[-1],'ol');stack.append((depth,nested));parent=nested
        elif stack[-1][0]<depth:stack.append((depth,parent))
        item=etree.SubElement(parent,'li');link=etree.SubElement(item,'a',href='#'+row['html_id'])
        link.text=(row['number']+' ' if row['number'] else '')+(title.text or '')
        for child in title:link.append(copy.deepcopy(child))
    return {'schema':'olpkit.book-headings.v1','headings':checked,'native_reading_headings':len(reading),
            'all_titles_and_numbers_match':True,'native_evidence':evidence,'reader_complete':False}
