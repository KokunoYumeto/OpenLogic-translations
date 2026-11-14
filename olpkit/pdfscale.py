"""Measure visible specimen ink, never infer script balance from font size."""
import hashlib
import json
from pathlib import Path
import re
import tomllib

import fitz
from PIL import Image, ImageOps

from .schemas import validate_schema


def digest(data):
    return hashlib.sha256(data).hexdigest()


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
              'status': 'incomplete', 'dpi': 600, 'measurements': {}, 'issues': [],
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
        origins = []
        for name, rect in regions.items():
            if rect.is_empty or rect.is_infinite or not page.rect.contains(rect):
                raise ValueError('scale specimen cell is outside the page')
            item = specimen[name]
            glyphs = [(span, char) for span in traces for char in span['chars']
                      if fitz.Rect(char[3]).intersects(rect)]
            if len(glyphs) != 1:
                report['issues'].append({'cell': name, 'kind': 'ambiguous_glyphs', 'count': len(glyphs)})
                continue
            span, char = glyphs[0]
            font = re.sub(r'^[A-Z]{6}\+', '', span['font'])
            if (chr(char[0]) != item['glyph'] or font != item['font']
                    or char[1] == 0 or span.get('opacity', 1) != 1
                    or span['dir'] != (1.0, 0.0) or span['type'] != 0
                    or not rect.contains(fitz.Rect(char[3]))):
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
            pix = page.get_pixmap(dpi=600, colorspace=fitz.csGRAY, alpha=False, clip=rect, annots=False)
            img = Image.frombytes('L', (pix.width, pix.height), pix.samples)
            mask = ImageOps.invert(img).point(lambda x: 255 if x >= 128 else 0)
            bounds = mask.getbbox()
            if not bounds or bounds[0] == 0 or bounds[1] == 0 or bounds[2] == pix.width or bounds[3] == pix.height:
                report['issues'].append({'cell': name, 'kind': 'missing_or_clipped_ink'})
                continue
            height = bounds[3] - bounds[1]
            if height < 20:
                report['issues'].append({'cell': name, 'kind': 'insufficient_pixel_resolution'})
                continue
            origins.append(char[2][1])
            png = pix.tobytes('png')
            if render_dir is not None:
                (Path(render_dir)/(name+'.png')).write_bytes(png)
            report['measurements'][name] = {'glyph': item['glyph'], 'font': font,
                'nominal_size_pt': span['size'], 'baseline_pt': char[2][1],
                'ink_height_px': height, 'ink_height_pt': height * 72 / 600,
                'ink_bounds_px': list(bounds), 'image_sha256': digest(png)}
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
