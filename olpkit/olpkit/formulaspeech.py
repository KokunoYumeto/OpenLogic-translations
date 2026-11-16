"""Index actual reader formulas for source-grounded, language-owned speech."""
import hashlib,json,copy
from lxml import html
from .xhtml import text_without_annotations
from .epubpackage import math_signature
from .assembly import digest, json_bytes


def table_context(node, row_cache):
    """Identify the HTML row and cell; an isolated A may be capital alpha."""
    cell = next((ancestor for ancestor in node.iterancestors() if ancestor.tag in ('td', 'th')), None)
    if cell is None or cell.getparent().tag != 'tr':
        return None
    row = cell.getparent()
    if row not in row_cache:
        cells = [child for child in row if child.tag in ('td', 'th')]
        descriptions = []
        for child in cells:
            text = text_without_annotations(child)
            tex = [a.text or '' for a in child.xpath('.//math//annotation')]
            descriptions.append({'kind': child.tag, 'text': text[:800],
                                 'content_sha256': digest(json_bytes([text, tex])),
                                 'colspan': child.get('colspan', '1'), 'rowspan': child.get('rowspan', '1')})
        row_cache[row] = (digest(json_bytes(descriptions)), descriptions, {c: i for i, c in enumerate(cells)})
    key, descriptions, indexes = row_cache[row]
    return key, descriptions, indexes[cell]


def index_formulas(reader_bytes, language):
    doc=html.document_fromstring(reader_bytes,parser=html.HTMLParser(encoding='utf-8',huge_tree=True))
    if doc.get('lang')!=language:raise ValueError('reader speech language differs')
    formulas={};order=[];contexts={};preceding=None
    row_cache={};table_rows={};table_locations={}
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
        table = table_context(node, row_cache)
        if table is not None:
            row_key, cells, column = table
            table_rows[row_key] = cells
            table_locations[row['occurrence_id']] = {'row': row_key, 'cell': column}
    return {'schema':'olpkit.formula-speech-input.v1','language':language,
            'reader_sha256':hashlib.sha256(reader_bytes).hexdigest(),'formulas':formulas,'occurrences':order,'contexts':contexts,
            'unique_formulas':len(formulas),'formula_occurrences':len(order),
            'table_context':{'rows':table_rows,'occurrences':table_locations},
            'locator_limit':'A preceding import is a locator only. Deferred exercises, footnotes, book front/back matter and navigation require their actual source context.',
            'spoken_text_produced':False}


def bind_speech(reader_bytes, input_bytes, store_bytes):
    """Attach language-owned readings only to the exact reviewed occurrences.

    This verifies coverage and provenance links, not linguistic expertise or
    assistive-technology behavior. Neither MathML nor TeX is replaced by speech.
    """
    packet=json.loads(input_bytes);store=json.loads(store_bytes)
    digest=lambda data:hashlib.sha256(data).hexdigest()
    if store.get('input_sha256')!=digest(input_bytes):raise ValueError('speech input identity differs')
    if store.get('language')!=packet['language']:raise ValueError('speech language differs')
    if not store.get('model') or not store.get('reasoning_effort'):
        raise ValueError('speech producer provenance absent')
    current=index_formulas(reader_bytes,packet['language'])
    for key in ('formulas','occurrences','contexts'):
        if current[key]!=packet[key]:raise ValueError('speech '+key+' changed; review required')
    if 'table_context' in packet and current['table_context'] != packet['table_context']:
        raise ValueError('speech table context changed; review required')
    rules=store.get('rules',{});rows=store.get('formulas',{})
    if set(rows)!=set(packet['formulas']):raise ValueError('speech formula coverage differs')
    for key,rule in rules.items():
        if not all(field in rule for field in ('explanation','canon_passages','rationale',
                    'rejected_alternatives','uncertainty','editorial_confidence')):
            raise ValueError('incomplete speech decision: '+key)
        if not rule['canon_passages']:raise ValueError('speech rule has no canon passage')
        for passage in rule['canon_passages']:
            if not all(passage.get(k) for k in ('passage_id','source_id','source_sha256','locator','excerpt','use')):
                raise ValueError('speech canon locator incomplete')
    for key,source in packet['formulas'].items():
        row=rows[key]
        if row.get('tex')!=source['tex'] or digest(row['tex'].encode())!=key:
            raise ValueError('speech TeX identity differs')
        if row.get('occurrence_ids')!=source['occurrence_ids']:
            raise ValueError('speech occurrence coverage differs')
        if not row.get('rule_ids') or not set(row['rule_ids'])<=set(rules):
            raise ValueError('speech rule link absent')
        variants=row.get('contextual_variants',{})
        if not set(variants)<=set(row['occurrence_ids']):raise ValueError('speech variant occurrence absent')
        for speech in [row.get('spoken_text'),*variants.values()]:
            if not isinstance(speech,str) or not speech.strip():raise ValueError('empty spoken text')
    doc=html.document_fromstring(reader_bytes,parser=html.HTMLParser(encoding='utf-8',huge_tree=True))
    before_text=text_without_annotations(doc)
    formulas=doc.xpath('//math');before_math=[math_signature(n) for n in formulas]
    variants=0
    for node,occurrence in zip(formulas,packet['occurrences']):
        if any(k in node.attrib for k in ('aria-label','alttext')):raise ValueError('speech already attached')
        row=rows[occurrence['formula_sha256']];oid=occurrence['occurrence_id']
        speech=row.get('contextual_variants',{}).get(oid,row['spoken_text'])
        variants+=oid in row.get('contextual_variants',{})
        node.set('alttext',speech);node.set('aria-label',speech)
    if before_text!=text_without_annotations(doc):raise ValueError('speech binding changed reader prose')
    for before,node in zip(before_math,formulas):
        clone=copy.deepcopy(node);clone.attrib.pop('aria-label');clone.attrib.pop('alttext')
        if math_signature(clone)!=before:raise ValueError('speech binding changed mathematical content')
    result=html.tostring(doc,encoding='utf-8',doctype='<!DOCTYPE html>')
    return result,{'schema':'olpkit.formula-speech-binding.v1','language':store['language'],
        'input_packet_sha256':digest(input_bytes),'store_sha256':digest(store_bytes),
        'reader_sha256':digest(reader_bytes),'bound_reader_sha256':digest(result),
        'formula_occurrences':len(formulas),'with_spoken_text':len(formulas),
        'unique_formulas':len(rows),'contextual_variants':variants,'canon_rule_links_complete':True,
        'original_prose_preserved':True,'mathematics_and_annotations_preserved':True,
        'model':store['model'],'reasoning_effort':store['reasoning_effort'],
        'assistive_technology_check':'pending','release_ready':False}
