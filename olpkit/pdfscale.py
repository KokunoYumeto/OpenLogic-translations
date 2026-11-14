"""Measure visible specimen ink, never infer script balance from font size."""
import hashlib
import io
import json
from pathlib import Path
import re
import tomllib

import fitz
from PIL import Image, ImageOps

from .schemas import validate_schema


def digest(data):
    return hashlib.sha256(data).hexdigest()


def outline_locator(doc, page):
    """Resolve actual embedded glyph bounds, including CID-keyed CFF fonts."""
    from fontTools.ttLib import TTFont
    from fontTools.cffLib import CFFFontSet
    from fontTools.pens.boundsPen import BoundsPen
    fonts = {}
    for row in page.get_fonts(full=True):
        name = re.sub(r'^[A-Z]{6}\+', '', row[3])
        fonts.setdefault(name, set()).add(row[0])
    cache = {}
    def locate(span, char):
        name = re.sub(r'^[A-Z]{6}\+', '', span['font'])
        ids = fonts.get(name, set())
        if len(ids) != 1: return None
        xref = next(iter(ids)); key = (xref, char[1])
        if key not in cache:
            _, ext, _, body = doc.extract_font(xref)
            bounds = None; unit = None
            if ext in ('ttf', 'otf'):
                font = TTFont(io.BytesIO(body)); order = font.getGlyphOrder()
                if char[1] < len(order):
                    glyphs = font.getGlyphSet(); pen = BoundsPen(glyphs)
                    glyphs[order[char[1]]].draw(pen); bounds = pen.bounds
                    unit = 1 / font['head'].unitsPerEm
                font.close()
            elif ext in ('cff', 'cid'):
                font = CFFFontSet(); font.decompile(io.BytesIO(body), None)
                top = font[font.fontNames[0]]
                # MuPDF reports the CID, not the subset charset array index.
                if hasattr(top, 'ROS'):
                    candidates = [n for n in top.charset if re.fullmatch(r'cid[0-9]+', n)
                                  and int(n[3:]) == char[1]]
                else:
                    candidates = top.charset[char[1]:char[1]+1]
                matrix = top.FontMatrix
                if len(candidates) == 1 and matrix[1:3] == [0, 0] and matrix[4:] == [0, 0] and matrix[0] == matrix[3]:
                    pen = BoundsPen(None); top.CharStrings[candidates[0]].draw(pen)
                    bounds = pen.bounds; unit = matrix[3]
            cache[key] = (bounds, unit, digest(body))
        bounds, unit, font_hash = cache[key]
        if bounds is None or unit is None: return None
        factor = unit * span['size']; x, y = char[2]
        rectangle = fitz.Rect(x + bounds[0]*factor, y - bounds[3]*factor,
                              x + bounds[2]*factor, y - bounds[1]*factor)
        return rectangle, font_hash
    return locate


def inspect_scale(pdf, specimen, language, *, render_dir=None):
    validate_schema('scale-specimen', specimen)
    if specimen['locale'] != language['locale']:
        raise ValueError('scale specimen belongs to a different language')
    pdf = Path(pdf)
    pdf_hash = digest(pdf.read_bytes())
    if pdf_hash != specimen['pdf_sha256']:
        raise ValueError('scale specimen PDF hash differs')
    policy = language.get('scale')
    if policy is not None:
        validate_schema('font-scale', policy)
        if policy['minimum'] >= policy['maximum']:
            raise ValueError('font-scale range is empty or reversed')
        if policy['reference_glyph'] != specimen['reference']['glyph']:
            raise ValueError('specimen reference differs from the language decision')
    report = {'schema': 'olpkit.pdf-scale.v1', 'locale': specimen['locale'],
              'pdf_sha256': pdf_hash, 'specimen_sha256': digest(json.dumps(specimen, sort_keys=True).encode()),
              'status': 'incomplete', 'dpi': 2400, 'measurements': {}, 'issues': [],
              'policy': policy, 'release_ready': False,
              'limits': ['Measures only the identified specimen line, not the whole reader.',
                         'No human judgment, approved range, build equivalence or visual review is inferred.']}
    with fitz.open(pdf) as doc:
        if specimen['page'] > len(doc):
            raise ValueError('scale specimen page is absent')
        page = doc[specimen['page'] - 1]
        if page.rotation:
            raise ValueError('scale specimen must use an unrotated page')
        regions = {name: fitz.Rect(specimen[name]['box']) for name in ('latin', 'reference')}
        if regions['latin'].intersects(regions['reference']):
            raise ValueError('scale specimen cells overlap')
        traces = page.get_texttrace()
        ink_bounds = outline_locator(doc, page)
        origins = []
        for name, rect in regions.items():
            if rect.is_empty or rect.is_infinite or not page.rect.contains(rect):
                raise ValueError('scale specimen cell is outside the page')
            item = specimen[name]
            context = item.get('context')
            if context:
                text, index = context['text'], context['index']
                if (set(text) != {item['glyph']} or not 1 <= index < len(text)-1):
                    raise ValueError('context must select an interior glyph in a repeated specimen run')
                runs = [s for s in traces if ''.join(chr(c[0]) for c in s['chars']) == text
                        and re.sub(r'^[A-Z]{6}\+', '', s['font']) == item['font']
                        and fitz.Rect(s['chars'][index][3]).intersects(rect)]
                glyphs = [(s, s['chars'][index]) for s in runs]
                if len(runs) == 1:
                    run = runs[0]; target = run['chars'][index]; target_box = fitz.Rect(target[3])
                    # The two neighbours must have the identical contextual form.
                    # This excludes initial/final forms with different extenders.
                    def actual_intersects(s, c):
                        ink = ink_bounds(s, c)
                        return (ink[0] if ink else fitz.Rect(c[3])).intersects(rect)
                    if (any(run['chars'][j][1] != context['glyph_id'] for j in (index-1,index,index+1))
                            or abs(rect.x0-target_box.x0) > .02 or abs(rect.x1-target_box.x1) > .02
                            or any(actual_intersects(s,c) for s in traces if s is not run for c in s['chars'])):
                        report['issues'].append({'cell': name, 'kind': 'context_not_isolated'})
                        continue
            else:
                glyphs = [(span, char) for span in traces for char in span['chars']
                          if fitz.Rect(char[3]).intersects(rect)]
            if len(glyphs) != 1:
                report['issues'].append({'cell': name, 'kind': 'ambiguous_glyphs', 'count': len(glyphs)})
                continue
            span, char = glyphs[0]
            outline = ink_bounds(span, char)
            if context and outline is None:
                report['issues'].append({'cell': name, 'kind': 'context_outline_unresolved'})
                continue
            font = re.sub(r'^[A-Z]{6}\+', '', span['font'])
            if (chr(char[0]) != item['glyph'] or font != item['font']
                    or char[1] == 0 or span.get('opacity', 1) != 1
                    or span['dir'] != (1.0, 0.0) or span['type'] != 0
                    or (not context and not rect.contains(fitz.Rect(char[3])))
                    or (context and not (rect.y0 < outline[0].y0 < outline[0].y1 < rect.y1))):
                report['issues'].append({'cell': name, 'kind': 'glyph_identity_or_geometry',
                                         'observed_character': char[0], 'observed_font': font})
                continue
            # A border, rule or decorative shape is not part of the reference ink.
            def painted_drawing_bounds(d):
                padding = max(d.get('width') or 0, .02) / 2
                return fitz.Rect(d['rect']) + (-padding, -padding, padding, padding)
            if any(rect.intersects(painted_drawing_bounds(d)) for d in page.get_drawings()):
                report['issues'].append({'cell': name, 'kind': 'nontext_drawing_in_cell'})
                continue
            if any(rect.intersects(fitz.Rect(d['bbox'])) for d in page.get_image_info()):
                report['issues'].append({'cell': name, 'kind': 'image_in_cell'})
                continue
            pix = page.get_pixmap(dpi=report['dpi'], colorspace=fitz.csGRAY, alpha=False, clip=rect, annots=False)
            img = Image.frombytes('L', (pix.width, pix.height), pix.samples)
            mask = ImageOps.invert(img).point(lambda x: 255 if x >= 128 else 0)
            bounds = mask.getbbox()
            if (not bounds or bounds[1] == 0 or bounds[3] == pix.height
                    or (not context and (bounds[0] == 0 or bounds[2] == pix.width))):
                report['issues'].append({'cell': name, 'kind': 'missing_or_clipped_ink'})
                continue
            height = bounds[3] - bounds[1]
            if outline and abs(height - outline[0].height * report['dpi'] / 72) > 3:
                report['issues'].append({'cell': name, 'kind': 'ink_disagrees_with_embedded_outline'})
                continue
            if height < 20:
                report['issues'].append({'cell': name, 'kind': 'insufficient_pixel_resolution'})
                continue
            origins.append(char[2][1])
            png = pix.tobytes('png')
            if render_dir is not None:
                (Path(render_dir)/(name+'.png')).write_bytes(png)
            report['measurements'][name] = {'glyph': item['glyph'], 'font': font,
                'nominal_size_pt': span['size'], 'baseline_pt': char[2][1],
                'ink_height_px': height, 'ink_height_pt': height * 72 / report['dpi'],
                'ink_bounds_px': list(bounds), 'image_sha256': digest(png),
                'glyph_id': char[1], 'context': context}
            if outline:
                report['measurements'][name]['embedded_font_sha256'] = outline[1]
                report['measurements'][name]['outline_height_pt'] = outline[0].height
        if report['issues']:
            report['status'] = 'fail'
            return report
        if abs(origins[0] - origins[1]) > 0.5:
            report['status'] = 'fail'
            report['issues'].append({'kind': 'specimen_not_on_one_baseline'})
            return report
        x, ref = (report['measurements'][n]['ink_height_px'] for n in ('latin', 'reference'))
        report['ratio'] = x / ref
        # One pixel on each edge avoids certifying a borderline raster result.
        report['ratio_bounds'] = [(x-2)/(ref+2), (x+2)/(ref-2)]
        if policy is None:
            report['issues'].append({'kind': 'language_range_not_recorded'})
        elif policy['minimum'] <= report['ratio_bounds'][0] and report['ratio_bounds'][1] <= policy['maximum']:
            report['status'] = 'pass'
        elif report['ratio_bounds'][1] < policy['minimum'] or report['ratio_bounds'][0] > policy['maximum']:
            report['status'] = 'fail'
            report['issues'].append({'kind': 'ratio_outside_language_range'})
        else:
            report['issues'].append({'kind': 'raster_uncertainty_crosses_range_boundary'})
    return report


def scale_command(pdf, specimen_path, language_path, out):
    out = Path(out)
    if out.exists():
        raise ValueError('preserve the earlier scale measurement; choose a new output folder')
    specimen_bytes = Path(specimen_path).read_bytes()
    language_bytes = Path(language_path).read_bytes()
    specimen = json.loads(specimen_bytes.decode('utf-8'))
    language = tomllib.loads(language_bytes.decode('utf-8'))
    out.mkdir(parents=True)
    report = inspect_scale(pdf, specimen, language, render_dir=out)
    report['specimen_file_sha256'] = digest(specimen_bytes)
    report['language_data_sha256'] = digest(language_bytes)
    (out/'REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status','locale','ratio','ratio_bounds','policy','issues') if k in report}))
    return int(report['status'] != 'pass')
