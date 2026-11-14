import hashlib
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from olpkit.nativefigures import extract_tikz, export_native_figures


class NativeFigureTests(unittest.TestCase):
    def test_only_live_diagrams_are_extracted_with_exact_offsets(self):
        picture = r'\begin{tikzpicture}\node{$q_0$};\end{tikzpicture}'
        source = (r'\newcommand{\unused}{'+picture+'}\n' +
                  '% '+picture+'\n'+r'\begin{verbatim}'+picture+r'\end{verbatim}' +
                  'before{'+picture+'}after'+picture)
        rows = extract_tikz(source)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row['source_tex'], picture)
            self.assertEqual(source[row['char_start']:row['char_end']], picture)
            self.assertEqual(row['source_sha256'], hashlib.sha256(picture.encode()).hexdigest())

    def test_placement_and_labels_are_not_normalized(self):
        source = '\\begin{tikzpicture}[->]\n  \\node[initial,state] (A) {$q_{10}$};\n% comment\n\\end{tikzpicture}'
        self.assertEqual(extract_tikz(source)[0]['source_tex'], source)

    def test_unclosed_picture_fails(self):
        with self.assertRaisesRegex(ValueError, 'unclosed environment'):
            extract_tikz(r'\begin{tikzpicture}\node{x};')


class NativeFigureResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'driver.tex').write_text(r'\documentclass{article}\begin{document}\end{document}')
        self.output = self.root / 'out'
        self.picture = r'\begin{tikzpicture}\node{x};\end{tikzpicture}'
        self.verify = patch('olpkit.nativefigures.verify_assembly').start()
        self.addCleanup(patch.stopall)
        self.slot = patch('olpkit.nativefigures.TeXSlot').start()
        self.slot.return_value.__enter__.return_value.acquired = False
        self.slot.return_value.__enter__.return_value.abandoned = False
        self.engine = patch('olpkit.nativefigures.run_job').start()

    def export(self, **kwargs):
        return export_native_figures(self.source, {}, self.picture, 'driver.tex', self.output,
                                     epoch=123, context_evidence={'checked': 'native'}, **kwargs)

    def test_resume_preserves_receipt_and_prepared_files(self):
        self.export()
        receipt = (self.output / 'NATIVE_FIGURES.json').read_bytes()
        prepared = {p.name: p.read_bytes() for p in self.output.glob('*.tex')}
        result = self.export(resume=True)
        self.assertEqual(result['status'], 'slot_occupied')
        self.assertEqual((self.output / result['resumed_from']['file']).read_bytes(), receipt)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.glob('*.tex')}, prepared)
        self.assertEqual(self.slot.call_count, 2)
        self.engine.assert_not_called()

    def test_changed_source_or_prepared_bytes_cannot_acquire_slot(self):
        self.export()
        before = (self.output / 'NATIVE_FIGURES.json').read_bytes()
        (self.output / 'figure-001.tex').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            self.export(resume=True)
        self.assertEqual(self.slot.call_count, 1)
        self.assertEqual((self.output / 'NATIVE_FIGURES.json').read_bytes(), before)

    def test_started_attempt_or_stray_output_cannot_resume(self):
        self.export()
        receipt = self.output / 'NATIVE_FIGURES.json'
        previous = json.loads(receipt.read_bytes())
        previous['tex_runs'] = 1
        receipt.write_text(json.dumps(previous))
        with self.assertRaisesRegex(ValueError, 'zero engine'):
            self.export(resume=True)
        previous['tex_runs'] = 0
        receipt.write_text(json.dumps(previous))
        (self.output / 'native-figures.pdf').write_bytes(b'partial')
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            self.export(resume=True)
        self.assertEqual(self.slot.call_count, 1)

    def test_existing_attempt_and_concurrent_invocation_are_not_overwritten(self):
        self.export()
        with self.assertRaisesRegex(ValueError, 'preserve existing'):
            self.export()
        (self.output / '.olpkit-native-figures.lock').write_text('owner')
        with self.assertRaisesRegex(ValueError, 'another invocation'):
            self.export(resume=True)
        self.assertEqual((self.output / '.olpkit-native-figures.lock').read_text(), 'owner')
        self.assertEqual(self.slot.call_count, 1)


if __name__ == '__main__': unittest.main()
