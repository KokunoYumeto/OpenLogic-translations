import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from reportlab.pdfgen import canvas

from olpkit.pdfscale import inspect_scale, scale_command


def fixture(path, *, latin_size=12, second_x=False, reference_baseline=140, line=False):
    c = canvas.Canvas(str(path), pagesize=(300, 200))
    c.setFont('Helvetica', latin_size); c.drawString(50, 140, 'xx' if second_x else 'x')
    c.setFont('Helvetica', 12); c.drawString(120, reference_baseline, 'H')
    if line: c.line(46, 130, 70, 130)
    c.save()
    return {'schema_version': 1, 'locale': 'fixture',
            'pdf_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'page': 1,
            'latin': {'glyph': 'x', 'font': 'Helvetica', 'box': [45, 25, 90, 80]},
            'reference': {'glyph': 'H', 'font': 'Helvetica', 'box': [115, 25, 160, 80]}}


def language():
    return {'locale': 'fixture', 'scale': {'reference_glyph': 'H', 'minimum': .55, 'maximum': .85,
            'decision_date': '2026-11-14', 'rationale': 'Synthetic test interval, not a language recommendation.',
            'evidence': ['Synthetic Helvetica x/H fixture.']}}


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.pdf = self.root/'specimen.pdf'

    def test_visible_height_not_nominal_size(self):
        s = fixture(self.pdf); r = inspect_scale(self.pdf, s, language(), render_dir=self.root)
        self.assertEqual(r['status'], 'pass')
        self.assertAlmostEqual(r['measurements']['latin']['nominal_size_pt'], 12)
        self.assertAlmostEqual(r['measurements']['reference']['nominal_size_pt'], 12)
        self.assertLess(r['ratio'], .85)
        self.assertTrue((self.root/'latin.png').is_file())
        self.assertFalse(r['release_ready'])

    def test_oversized_latin_fails(self):
        s = fixture(self.pdf, latin_size=24); r = inspect_scale(self.pdf, s, language())
        self.assertEqual(r['status'], 'fail')
        self.assertEqual(r['issues'][0]['kind'], 'ratio_outside_language_range')

    def test_no_range_is_not_pass(self):
        s = fixture(self.pdf); r = inspect_scale(self.pdf, s, {'locale': 'fixture'})
        self.assertEqual(r['status'], 'incomplete')
        self.assertIn('ratio', r)

    def test_ambiguity_and_drawing_are_not_ink(self):
        for kwargs, kind in [({'second_x': True}, 'ambiguous_glyphs'),
                             ({'line': True}, 'nontext_drawing_in_cell')]:
            with self.subTest(kwargs=kwargs):
                s = fixture(self.pdf, **kwargs); r = inspect_scale(self.pdf, s, language())
                self.assertEqual(r['status'], 'fail'); self.assertEqual(r['issues'][0]['kind'], kind)

    def test_baselines_must_be_one_specimen_line(self):
        s = fixture(self.pdf, reference_baseline=137); r = inspect_scale(self.pdf, s, language())
        self.assertEqual(r['issues'][0]['kind'], 'specimen_not_on_one_baseline')

    def test_image_in_specimen_is_not_glyph_ink(self):
        import fitz
        from PIL import Image
        s = fixture(self.pdf)
        image = self.root/'dot.png'; Image.new('RGB', (3, 3), 'black').save(image)
        with fitz.open(self.pdf) as doc:
            doc[0].insert_image(fitz.Rect(72, 40, 75, 43), filename=str(image))
            data = doc.tobytes()
        self.pdf.write_bytes(data); s['pdf_sha256'] = hashlib.sha256(data).hexdigest()
        r = inspect_scale(self.pdf, s, language())
        self.assertEqual(r['status'], 'fail')
        self.assertEqual(r['issues'][0]['kind'], 'image_in_cell')

    def test_wrong_font_and_wrong_glyph_fail(self):
        for field, value in [('font', 'UnknownFont'), ('glyph', 'J')]:
            s = fixture(self.pdf); s['reference'][field] = value; p = language()
            if field == 'glyph': p['scale']['reference_glyph'] = value
            r = inspect_scale(self.pdf, s, p)
            self.assertEqual(r['status'], 'fail')

    def test_specimen_identity_and_region_checks(self):
        for field, value in [('pdf_sha256', '0'*64), ('page', 2), ('locale', 'other')]:
            s = fixture(self.pdf); s[field] = value
            with self.assertRaises(ValueError): inspect_scale(self.pdf, s, language())
        s = fixture(self.pdf); s['reference']['box'] = s['latin']['box']
        with self.assertRaisesRegex(ValueError, 'overlap'): inspect_scale(self.pdf, s, language())

    def test_boundary_uncertainty_is_not_pass(self):
        s = fixture(self.pdf); measured = inspect_scale(self.pdf, s, language()); p = language()
        p['scale']['minimum'] = measured['ratio']-.001; p['scale']['maximum'] = measured['ratio']+.001
        r = inspect_scale(self.pdf, s, p)
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(r['issues'][0]['kind'], 'raster_uncertainty_crosses_range_boundary')

    def test_range_requires_dated_evidence_and_matching_reference(self):
        s = fixture(self.pdf)
        for mutation in ['no_evidence', 'reference', 'reversed']:
            p = language()
            if mutation == 'no_evidence': p['scale'].pop('evidence')
            elif mutation == 'reference': p['scale']['reference_glyph'] = 'q'
            else: p['scale']['minimum'] = 2
            with self.assertRaises(ValueError): inspect_scale(self.pdf, s, p)

    def test_command_and_preservation(self):
        s = fixture(self.pdf); (self.root/'specimen.json').write_text(json.dumps(s))
        (self.root/'language.toml').write_text('locale="fixture"\n[scale]\nreference_glyph="H"\nminimum=0.55\nmaximum=0.85\ndecision_date="2026-11-14"\nrationale="Synthetic test only"\nevidence=["Test fixture"]\n')
        args = [self.pdf, self.root/'specimen.json', self.root/'language.toml', self.root/'out']
        self.assertEqual(scale_command(*args), 0)
        self.assertTrue((self.root/'out/REPORT.json').is_file())
        with self.assertRaisesRegex(ValueError, 'preserve'): scale_command(*args)


if __name__ == '__main__': unittest.main()
