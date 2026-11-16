import hashlib
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from olpkit.nativefigures import extract_tikz,extract_native_figures, export_native_figures


class NativeFigureTests(unittest.TestCase):
    def test_float_typography_preserves_source_and_skips_literal_float_commands(self):
        picture = r'\begin{tikzpicture}\node{A};\end{tikzpicture}'
        source = (r'\newcommand{\unused}{\begin{figure}}' + picture
                  + r'\begin{figure*}\verb|\end{figure*}|' + picture + r'\end{figure*}'
                  + r'\begin{verbatim}\begin{figure}\end{verbatim}' + picture)
        rows = extract_native_figures(source, preserve_float_typography=True)
        self.assertEqual([r.get('float_environment') for r in rows], [None, 'figure*', None])
        self.assertEqual([r['source_tex'] for r in rows], [picture]*3)
    def test_tableau_branches_justifications_and_closures_are_exact_source(self):
        tableau=r'\begin{oltableau}[A, just={Hypothesis}[B, close][C[D, close]]]\end{oltableau}'
        tikz=r'\begin{tikzpicture}\node{x};\end{tikzpicture}'
        source='Before'+tikz+'Middle'+tableau+'After'
        rows=extract_native_figures(source)
        self.assertEqual([r['environment'] for r in rows],['tikzpicture','oltableau'])
        self.assertEqual([r['source_tex'] for r in rows],[tikz,tableau])
        self.assertEqual(len(extract_tikz(source)),1)
        self.assertNotIn('environment',extract_tikz(source)[0])
        self.assertEqual(extract_native_figures(source,('oltableau',))[0]['index'],1)
        for row in rows:self.assertEqual(source[row['char_start']:row['char_end']],row['source_tex'])

    def test_tableaux_in_definitions_comments_or_verbatim_are_not_executed(self):
        tableau=r'\begin{oltableau}[A,close]\end{oltableau}'
        source=r'\newcommand{\unused}{'+tableau+'}\n% '+tableau+'\n'+r'\begin{verbatim}'+tableau+r'\end{verbatim}'+tableau
        self.assertEqual([r['source_tex'] for r in extract_native_figures(source)],[tableau])
        with self.assertRaisesRegex(ValueError,'unsupported native'):
            extract_native_figures(tableau,('document',))
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

    def test_float_reset_is_scoped_to_the_export_batch(self):
        original = self.picture
        self.picture = r'\begin{figure*}' + original + r'\end{figure*}' + original
        result = self.export(preserve_float_typography=True)
        batch = (self.output/'native-figures.tex').read_text()
        self.assertEqual(batch.count(r'\csname @floatboxreset\endcsname'), 1)
        self.assertIn(r'\expandafter\def\csname @captype\endcsname{figure}', batch)
        self.assertIn(original+'\n'+r'\endgroup'+'\n\n'+original, batch)
        for row in result['figures']:
            self.assertEqual((self.output/row['source_file']).read_text(), original)

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

    def test_tableau_preview_is_separate_and_cannot_resume_as_tikz(self):
        self.picture=r'\begin{oltableau}[A,just={Given}[B,close][C]]\end{oltableau}'
        result=self.export(environments=('oltableau',))
        self.assertEqual(result['environments'],['oltableau'])
        tex=(self.output/'native-figures.tex').read_text()
        self.assertIn(r'\PreviewEnvironment{oltableau}',tex)
        self.assertNotIn(r'\PreviewEnvironment{tikzpicture}',tex)
        self.assertIn(self.picture,tex)
        self.picture=r'\begin{tikzpicture}\node{x};\end{tikzpicture}'
        with self.assertRaisesRegex(ValueError,'environments changed'):self.export(resume=True)
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

    def test_xelatex_selects_its_native_preview_backend_and_resumes(self):
        first = self.export(engine='xelatex')
        self.assertEqual(first['engine'], 'xelatex')
        self.assertEqual(first['preview_backend'], 'xetex')
        self.assertIn(r'\usepackage[active,tightpage,xetex]{preview}',
                      (self.output / 'native-figures.tex').read_text())
        self.export(engine='xelatex', resume=True)
        self.engine.assert_not_called()
        with self.assertRaisesRegex(ValueError, 'identity changed: engine'):
            self.export(engine='pdflatex', resume=True)
        self.assertEqual(self.slot.call_count, 2)

    def test_legacy_receipt_is_pdftex_only(self):
        self.export()
        path = self.output / 'NATIVE_FIGURES.json'
        old = json.loads(path.read_bytes())
        del old['engine'], old['preview_backend']
        path.write_text(json.dumps(old))
        with self.assertRaisesRegex(ValueError, 'identity changed: engine'):
            self.export(engine='xelatex', resume=True)
        self.export(resume=True)
        self.engine.assert_not_called()

    def test_xelatex_command_remains_one_guarded_resource_bounded_job(self):
        self.slot.return_value.__enter__.return_value.acquired = True
        self.engine.return_value = {'exit_code': 1, 'timed_out': False}
        with patch('olpkit.nativefigures.shutil.which', return_value='xelatex.exe') as which:
            with self.assertRaisesRegex(ValueError, 'see xelatex.txt'):
                self.export(engine='xelatex')
            which.assert_called_once_with('xelatex')
        self.engine.assert_called_once()
        args, kwargs = self.engine.call_args
        self.assertEqual(args[0][0], 'xelatex.exe')
        self.assertIn('-no-shell-escape', args[0])
        self.assertEqual(args[2].name, 'xelatex.txt')
        self.assertEqual(kwargs['timeout'], 180)
        result = json.loads((self.output / 'NATIVE_FIGURES.json').read_bytes())
        self.assertEqual(result['commands'][0]['tool'], 'xelatex')
        self.assertEqual(result['tex_runs'], 1)
        self.assertTrue(result['mutex_acquired'])

    def test_xdv_or_engine_transcript_prevents_resume(self):
        self.export(engine='xelatex')
        for name in ('native-figures.xdv', 'xelatex.txt'):
            stray = self.output / name
            stray.write_bytes(b'partial')
            with self.assertRaisesRegex(ValueError, 'contradicts'):
                self.export(engine='xelatex', resume=True)
            stray.unlink()
        self.assertEqual(self.slot.call_count, 1)

    def test_unknown_engine_fails_before_output_or_slot(self):
        with self.assertRaisesRegex(ValueError, 'unsupported native figure engine'):
            self.export(engine='unrecognized')
        self.assertFalse(self.output.exists())
        self.slot.assert_not_called()


if __name__ == '__main__': unittest.main()
