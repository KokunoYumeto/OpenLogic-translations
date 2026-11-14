import unittest,tempfile
from pathlib import Path
from olpkit.webexport import export_web


class WebExportBoundaryTests(unittest.TestCase):
    def test_existing_outputs_and_frozen_source_are_not_modified(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'source';source.mkdir();keep=source/'accepted.tex';keep.write_text('accepted source')
            with self.assertRaisesRegex(ValueError,'already exists'):
                export_web(source,'epub',source,None)
            with self.assertRaisesRegex(ValueError,'frozen source'):
                export_web(source,'epub',source/'new-output',None)
            self.assertEqual(keep.read_text(),'accepted source')
            self.assertFalse((source/'new-output').exists())

    def test_explicit_profile_and_correct_product_required(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'source';out=Path(td)/'out'
            with self.assertRaisesRegex(ValueError,'explicit'):
                export_web(source,'epub',out,None)
            with self.assertRaisesRegex(ValueError,'requires the accessible'):
                export_web(source,'epub',out,None,check_speech=True)
            self.assertFalse(out.exists())
