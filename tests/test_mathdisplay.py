import shutil
import subprocess
import unittest

from olpkit.mathdisplay import DisplayAdapter, bind_mathml, restore_annotations


class DisplayTests(unittest.TestCase):
    def test_intertext_preserves_every_prose_and_math_piece_in_order(self):
        source = r'Before\begin{align*}a&=b\\\intertext{Prose {nested} $c$.}d&=e\\\intertext{Next.}f&=g\end{align*}After'
        result, receipt = DisplayAdapter().prepare(source, 'fixture')
        expected = ('Before'+r'\begin{align*}a&=b\\\end{align*}'+'\n\nProse {nested} $c$.\n\n'+
                    r'\begin{align*}d&=e\\\end{align*}'+'\n\nNext.\n\n'+r'\begin{align*}f&=g\end{align*}After')
        self.assertEqual(result, expected)
        for item in receipt['events'][0]['prose_segments']:
            self.assertEqual(source[item['char_start']:item['char_end']], item['prose'])

    def test_numbered_alignment_cannot_silently_restart_numbering(self):
        with self.assertRaisesRegex(ValueError, 'PDF-derived'):
            DisplayAdapter().prepare(r'\begin{align}a&=b\\\intertext{Prose.}c&=d\end{align}', 'fixture')

    def test_definitions_and_tikz_are_not_executed(self):
        source = (r'\newcommand{\unused}{\begin{align*}a\intertext{hidden}\end{align*}}'
                  r'\DeclareRobustCommand{\VDash}{\mathrel{||}\joinrel\Relbar}'
                  r'\begin{tikzpicture}\node{$\nicefrac12$};\end{tikzpicture}')
        result, receipt = DisplayAdapter().prepare(source, 'fixture')
        self.assertEqual(result, source)
        self.assertFalse(receipt['markers'])
        self.assertFalse(receipt['events'])

    def test_balanced_fraction_and_exact_annotation_roundtrip(self):
        source = r'$\nicefrac{a_{n+1}}{1+\nicefrac12}$'
        result, receipt = DisplayAdapter().prepare(source, 'fixture')
        self.assertEqual(len(receipt['markers']), 2)
        self.assertEqual(restore_annotations(result, receipt['markers']), source)
        for row in receipt['markers'].values():
            self.assertEqual(source[row['char_start']:row['char_end']], row['original_tex'])

    def test_nested_math_escapes_and_original_text_are_preserved(self):
        source = r'$x\text{cost \$5, $a_{n}$ and $\nicefrac12$; café.}$'
        result, receipt = DisplayAdapter().prepare(source, 'fixture')
        self.assertEqual(restore_annotations(result, receipt['markers']), source)
        self.assertIn(r'cost \$5', result)

    def test_reserved_marker_is_not_ambiguous(self):
        with self.assertRaisesRegex(ValueError, 'reserved'):
            DisplayAdapter().prepare('OLPDISPLAY000000', 'fixture')

    def test_small_array_requires_actual_font_and_supported_columns(self):
        source = r'$\small\begin{array}{@{}cc@{}}a&b\end{array}$'
        with self.assertRaisesRegex(ValueError, 'native edition data'):
            DisplayAdapter().prepare(source, 'fixture')
        with self.assertRaisesRegex(ValueError, 'column specification'):
            DisplayAdapter(math_font_sizes={'small':'91.3242%'}).prepare(source.replace('@{}cc@{}','p{3cm}c'),'fixture')
        with self.assertRaisesRegex(ValueError, 'continues beyond'):
            DisplayAdapter(math_font_sizes={'small':'91.3242%'}).prepare(source[:-1]+'x$', 'fixture')


@unittest.skipUnless(shutil.which('pandoc'), 'Pandoc required')
class PandocDisplayTests(unittest.TestCase):
    def render(self, source, **options):
        from lxml import html
        prepared, receipt = DisplayAdapter(**options).prepare(source, 'fixture')
        result = subprocess.run(['pandoc', '-f', 'latex', '-t', 'html5', '--mathml'],
                                input=prepared, encoding='utf-8', capture_output=True, check=True)
        self.assertNotIn('[WARNING]', result.stderr)
        doc = html.fromstring(result.stdout)
        binding = bind_mathml(doc, receipt)
        self.assertEqual(binding['unbound'], [])
        self.assertNotIn('OLPDISPLAY', html.tostring(doc, encoding='unicode'))
        return doc, receipt

    def test_bevelled_nested_fractions_and_annotations(self):
        source = r'$\nicefrac{a}{1+\nicefrac12}$'
        doc, _ = self.render(source)
        self.assertEqual([node.get('bevelled') for node in doc.xpath('//mfrac')], ['true', 'true'])
        self.assertEqual(doc.xpath('//annotation')[0].text, source[1:-1])

    def test_double_turnstile_is_not_the_single_horizontal_bar_symbol(self):
        source = r'$M\mathrel{||}\joinrel\Relbar A$'
        doc, _ = self.render(source)
        self.assertEqual(doc.xpath('//mo/text()'), ['||', '='])
        self.assertEqual(doc.xpath('//mspace/@width'), ['-0.166667em'])
        self.assertEqual(doc.xpath('//annotation')[0].text, source[1:-1])

    def test_literal_uniqueness_mark_and_nested_text_math(self):
        source = r'$\exists\mathexclaim x\text{ iff $x_{n}=0$; café.}$'
        doc, _ = self.render(source)
        self.assertIn('!', ''.join(doc.xpath('//mi/text()|//mo/text()')))
        self.assertIn('café', ''.join(doc.xpath('//mtext/text()')))
        self.assertEqual(doc.xpath('//annotation')[0].text, source[1:-1])

    def test_multline_alignment_keeps_its_requested_row_positions(self):
        source = r'\begin{multline*}\shoveleft{a+b}\\\shoveright{\nicefrac12}\end{multline*}'
        doc, _ = self.render(source)
        self.assertEqual(doc.xpath('//mtd/@columnalign'), ['left', 'right'])
        self.assertEqual(len(doc.xpath('//mfrac[@bevelled="true"]')), 1)

    def test_missing_rendered_marker_is_a_failure(self):
        from lxml import html
        _, receipt = DisplayAdapter().prepare(r'$\nicefrac12$', 'fixture')
        with self.assertRaisesRegex(ValueError, 'unconverted display markers'):
            bind_mathml(html.fromstring('<p>Missing equation</p>'), receipt)

    def test_partial_function_arrow_keeps_stroke_in_shaft_and_source_annotation(self):
        source = r'$f\colon A\mathrel{\ooalign{\hfil$\mapstochar\mkern 5mu$\hfil\cr$\to$}}B$'
        doc, _ = self.render(source)
        self.assertIn('\u21f8', doc.xpath('//mo/text()'))
        self.assertNotIn('\u21a6', doc.xpath('//mo/text()'))
        self.assertEqual(doc.xpath('//annotation')[0].text, source[1:-1])

    def test_small_array_keeps_columns_blank_cells_blank_row_and_font_size(self):
        source = r'$\small\begin{array}{@{}c c c@{}}\mathbf1&\mathbf2&\mathbf3\\\\(0,0)&&(0,1)\\\end{array}$'
        doc, receipt = self.render(source, math_font_sizes={'small':'91.3242%'})
        self.assertEqual(doc.xpath('//mstyle/@mathsize'), ['91.3242%'])
        rows = doc.xpath('//mtable/mtr')
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 3)
        self.assertEqual(len(rows[2]), 3)
        self.assertEqual(''.join(rows[1].itertext()), '')
        self.assertEqual(''.join(rows[2][1].itertext()), '')
        self.assertEqual(doc.xpath('//annotation')[0].text, source[1:-1])


if __name__ == '__main__': unittest.main()
