"""Paint-order and raster corroboration for two G-LINK background cases."""
from collections import Counter
from hashlib import sha256

import fitz

from .pdfaudit import contrast, rgb

WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
LOGO_URI = 'http://openlogicproject.org/'
LOGO_FORM_SHA256 = 'a9d96c1fe3bd78f60652124e75d29a385d931ac3299e46d45ec0aedb167610d9'
UNKNOWN_FILL = 'non-white vector fill overlaps link background'
UNKNOWN_NO_TEXT = 'link has no extractable painted text'
PAINT_TYPES = {'fill-path','stroke-path','fill-image','fill-shade'}


def painted_rgb(value):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ValueError('expected explicit three-component RGB paint')
    return tuple(round(component,6) for component in rgb(value))


def operations_in(page,rect):
    return [(i,k) for i,(k,b) in enumerate(page.get_bboxlog()) if rect.intersects(fitz.Rect(b))]


def sample_colors(page,rect):
    pix = page.get_pixmap(matrix=fitz.Matrix(6,6),clip=rect,annots=False,
                          colorspace=fitz.csRGB,alpha=False)
    return Counter(zip(*(iter(pix.samples),)*3)).most_common(2)


def raster_check(page,rect,foreground,background):
    colors = sample_colors(page,rect)
    if len(colors)!=2:
        raise ValueError('render did not show both foreground and background')
    measured = [c for c,_ in colors]
    expected = [foreground,background]
    paired = []
    for color in expected:
        # Rasterization is a cross-check, with one 8-bit step for ICC/device
        # conversion. It never changes the strict serialized color match.
        matches = [m for m in measured if all(abs(a-round(b*255))<=1
                                               for a,b in zip(m,color))]
        if len(matches)!=1:
            raise ValueError(f'rendered palette does not confirm the paint pair: {colors!r}')
        paired.append(matches[0])
    ratio = contrast(*(tuple(c/255 for c in color) for color in paired))
    return {'foreground_rgb8':paired[0],'background_rgb8':paired[1],'contrast':ratio}


def flat_fill_link(page,rect,paint_rgb):
    operations = operations_in(page,rect)
    overlaps = [(i,k) for i,k in operations if k in PAINT_TYPES]
    if len(overlaps)!=1 or overlaps[0][1]!='fill-path':
        raise ValueError('expected one paint operation behind the link')
    sequence = overlaps[0][0]
    fill = next((d for d in page.get_drawings(extended=True) if d.get('seqno')==sequence),None)
    if (fill is None or fill.get('level')!=0 or fill.get('fill_opacity')!=1
            or fill.get('type')!='f' or len(fill['items'])!=1
            or fill['items'][0][0]!='re' or not fill['items'][0][1].contains(rect)):
        raise ValueError('paint behind link is not a single opaque enclosing rectangle')
    traces = []
    for trace in page.get_texttrace():
        for ch in trace['chars']:
            box = fitz.Rect(ch[3])
            center = (box.tl+box.br)/2
            if center in rect and chr(ch[0]).strip():
                if not fill['items'][0][1].contains(box):
                    raise ValueError('linked glyph extends outside the background fill')
                traces.append(trace)
    if not traces or any(t.get('type')!=0 or t.get('opacity')!=1 or t['seqno']<=sequence
                         or painted_rgb(t['color'])!=paint_rgb for t in traces):
        raise ValueError('linked glyph paint/order does not confirm the text color')
    background = painted_rgb(fill['fill'])
    rendered = raster_check(page,rect,paint_rgb,background)
    return {'kind':'text-on-flat-fill','foreground':paint_rgb,'background':background,
            'background_sequence':sequence,'text_sequences':sorted({t['seqno'] for t in traces}),
            'paint_contrast':contrast(paint_rgb,background),'raster':rendered}


def vector_logo(pdf,page,rect,destination):
    if destination!=LOGO_URI:
        raise ValueError('no evidence-bound vector-link policy for this destination')
    forms = [xref for xref,_,parent,_ in page.get_xobjects() if not parent
             and sha256(pdf.xref_stream(xref)).hexdigest()==LOGO_FORM_SHA256]
    if len(forms)!=1:
        raise ValueError('pinned Open Logic vector form is absent or ambiguous')
    operations = operations_in(page,rect)
    if [kind for _,kind in operations]!=['stroke-path','fill-path']:
        raise ValueError('expected only the logo stroke and fill in the link area')
    drawings = page.get_drawings(extended=True)
    stroke,fill = [next(d for d in drawings if d.get('seqno')==i) for i,_ in operations]
    if not any(d['type']=='group' and d.get('opacity')==1 and d.get('isolated')
               and d.get('blendmode')=='Normal'
               and all(abs(a-b)<.002 for a,b in zip(d['rect'],rect)) for d in drawings):
        raise ValueError('logo form is not isolated in the link rectangle')
    if (stroke.get('type')!='s' or stroke.get('stroke_opacity')!=1
            or painted_rgb(stroke['color'])!=BLACK or stroke['items'][0][0]!='re'
            or fill.get('type')!='f' or fill.get('fill_opacity')!=1 or painted_rgb(fill['fill'])!=BLACK
            or not rect.contains(stroke['rect']) or not rect.contains(fill['rect'])):
        raise ValueError('logo is not black-only vector paint on unpainted paper')
    rendered = raster_check(page,rect,BLACK,WHITE)
    return {'kind':'pinned-vector-logo','form_stream_sha256':LOGO_FORM_SHA256,
            'foreground':BLACK,'background':WHITE,'paint_sequences':[i for i,_ in operations],
            'paint_contrast':contrast(BLACK,WHITE),'raster':rendered}


def measure_unresolved(path,observations,unknown,threshold):
    """Measure only flat text backings and the identified Open Logic vector link."""
    by_area = {}
    for item in unknown:
        by_area.setdefault((item['page'],item.get('index')),[]).append(item)
    observations = {(item['page'],item['index']):item for item in observations}
    unresolved, issues, measurements = [], [], []
    with fitz.open(path) as pdf:
        for key, entries in by_area.items():
            observation = observations.get(key)
            if observation is None:
                unresolved.extend(entries)
                continue
            reasons = {item['reason'] for item in entries}
            page = pdf[key[0]-1]
            rect = fitz.Rect(observation['rect'])
            try:
                if reasons=={UNKNOWN_FILL} and len(observation['text_rgb'])==1:
                    result = flat_fill_link(page,rect,tuple(observation['text_rgb'][0]))
                elif (not observation['text'] and UNKNOWN_NO_TEXT in reasons
                      and reasons <= {UNKNOWN_FILL,UNKNOWN_NO_TEXT}):
                    result = vector_logo(pdf,page,rect,observation['destination'])
                else:
                    unresolved.extend(entries)
                    continue
            except (ValueError,KeyError,StopIteration) as error:
                unresolved.extend({**item,'render_evidence':str(error)} for item in entries)
                continue
            minimum = min(result['paint_contrast'],result['raster']['contrast'])
            observation['minimum_contrast'] = minimum
            result.update(page=key[0],index=key[1],minimum_contrast=minimum)
            measurements.append(result)
            if minimum<threshold:
                issues.append({'page':key[0],'index':key[1],'rule':'contrast',
                               'minimum':minimum,'background':result['background']})
    return unresolved, issues, measurements
