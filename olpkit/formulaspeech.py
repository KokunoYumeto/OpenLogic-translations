"""Index actual reader formulas for source-grounded, language-owned speech."""
import hashlib
from lxml import html
from .xhtml import text_without_annotations


def index_formulas(reader_bytes, language):
    doc=html.document_fromstring(reader_bytes,parser=html.HTMLParser(encoding='utf-8',huge_tree=True))
    if doc.get('lang')!=language:raise ValueError('reader speech language differs')
    formulas={};order=[];contexts={};preceding=None
    context_tags={'p','h1','h2','h3','h4','h5','h6','li','td','th','figcaption','caption'}
    for node in doc.iter():
        if node.get('data-unit-id'):preceding=node.get('data-unit-id')
        if node.tag!='math':continue
        annotations=[a for a in node.iter('annotation') if a.get('encoding','').lower() in
                     ('application/x-tex','text/x-tex','application/x-latex')]
        if len(annotations)!=1:raise ValueError('one exact TeX annotation required per formula')
        tex=''.join(annotations[0].itertext())
        if not tex.strip():raise ValueError('empty TeX annotation')
        key=hashlib.sha256(tex.encode('utf-8')).hexdigest()
        parent=next((p for p in node.iterancestors() if p.tag in context_tags),node)
        context=text_without_annotations(parent)[:800]
        context_id=hashlib.sha256(context.encode('utf-8')).hexdigest()
        contexts[context_id]=context
        row={'occurrence_id':'formula-'+str(len(order)+1).zfill(6),'formula_sha256':key,
             'preceding_import_locator':preceding,'context_id':context_id,
             'in_navigation':bool(node.xpath('ancestor::nav')),'display':node.get('display','inline')}
        if key not in formulas:formulas[key]={'tex':tex,'occurrence_ids':[]}
        formulas[key]['occurrence_ids'].append(row['occurrence_id']);order.append(row)
    return {'schema':'olpkit.formula-speech-input.v1','language':language,
            'reader_sha256':hashlib.sha256(reader_bytes).hexdigest(),'formulas':formulas,'occurrences':order,'contexts':contexts,
            'unique_formulas':len(formulas),'formula_occurrences':len(order),
            'locator_limit':'A preceding import is a locator only. Deferred exercises, footnotes, book front/back matter and navigation require their actual source context.',
            'spoken_text_produced':False}
