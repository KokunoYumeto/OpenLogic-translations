"""Reconcile every native figure/table caption without replacing its prose."""
from .bookheadings import visible_text
from .references import plain_number


def bind_captions(document, labels, native_titles, *, names, evidence, native_aux_drops_terminal_period=False):
    from lxml import etree
    if not evidence:raise ValueError('native caption evidence required')
    rows=[];seen=[]
    for key,row in labels.items():
        kind=row.get('kind')
        if kind not in ('figure','table'):continue
        anchors=document.xpath('//*[@id=$id]',id=key)
        if len(anchors)!=1:raise ValueError('native caption anchor missing/duplicate')
        anchor=anchors[0];containers=list(anchor.iterancestors('figure' if kind=='figure' else 'table'))
        if kind=='table' and not containers:
            parent=anchor.getparent();candidate=parent.getprevious()
            if parent.tag!='p' or len(parent)!=1 or visible_text(parent) or candidate is None or candidate.tag!='table':
                raise ValueError('detached table label has no unique adjacent table')
            candidate.set('id',key);parent.getparent().remove(parent);containers=[candidate]
        if len(containers)!=1:raise ValueError('native caption container missing/ambiguous')
        container=containers[0];captions=container.findall('figcaption' if kind=='figure' else 'caption')
        if len(captions)!=1 or container in seen:raise ValueError('native caption missing/duplicated')
        seen.append(container);caption=captions[0]
        number=plain_number(row['number_tex']);prefix=names[kind]+' '+number+': '
        current=visible_text(caption)
        if 'olp-book-photo' in container.get('class','').split():
            if not current.startswith(prefix):raise ValueError('photo native caption number differs')
            rows.append({'key':key,'kind':kind,'number':number,'preexisting_photo_number_verified':True});continue
        if key not in native_titles:raise ValueError('native rendered caption title missing')
        expected=visible_text(native_titles[key]);period=False
        if current!=expected:
            period=native_aux_drops_terminal_period and current.endswith('.') and current[:-1]==expected
            if not period:raise ValueError('native caption text differs: '+repr((key,current,expected)))
        label=etree.Element('span',attrib={'class':'olp-caption-number'});label.text=prefix
        label.tail=caption.text;caption.text=None;caption.insert(0,label)
        rows.append({'key':key,'kind':kind,'number':number,'caption_text_matches':True,
                     'native_aux_terminal_period_elision':bool(period)})
    actual=document.xpath('//figure[figcaption]|//table[caption]')
    if len(actual)!=len(seen) or set(actual)!=set(seen):raise ValueError('caption/native label coverage differs')
    return {'schema':'olpkit.book-captions.v1','captions':rows,'all_caption_numbers_match':True,
            'native_evidence':evidence,'reader_complete':False}
