import shutil
import subprocess
import unittest

from olpkit.proofmath import parse_proof, parse_proof_region
from olpkit.mathdisplay import DisplayAdapter, bind_mathml


class ProofTests(unittest.TestCase):
    def test_nested_stack_preserves_premise_order_labels_and_conclusions(self):
        source = (r'\Axiom$A$\Axiom$B$\RightLabel{$r$}\BinaryInf$C$'
                  r'\Axiom$D$\LeftLabel{rule $s$}\BinaryInf$E$\DisplayProof')
        math, end, record = parse_proof(source)
        self.assertEqual(end, len(source))
        self.assertEqual(record['axioms'], 3)
        self.assertEqual(record['inferences'], 2)
        self.assertEqual([row['formula'] for row in record['steps']], list('ABCDE'))
        self.assertEqual(math.count(r'\dfrac'), 2)
        self.assertIn(r'\text{rule }{s}', math)

    def test_unknown_styles_and_stray_text_are_never_discarded(self):
        for extra in (r'\doubleLine', r'\noLine', 'lost premise'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                parse_proof(r'\Axiom$A$'+extra+r'\UnaryInf$B$\DisplayProof')

    def test_missing_premise_and_unused_label_fail(self):
        for source in (r'\Axiom$A$\BinaryInf$B$\DisplayProof', r'\Axiom$A$\RightLabel{unused}\DisplayProof'):
            with self.assertRaises(ValueError): parse_proof(source)

    def test_text_arguments_keep_text_and_embedded_math_distinct(self):
        math, _, _ = parse_proof(r'\AxiomC{Prose $A$}\RightLabel{\ensuremath{\mathrm{Cut}}}\UnaryInfC{$B$}\DisplayProof')
        self.assertIn(r'\text{Prose }{A}', math)
        self.assertIn(r'{\mathrm{Cut}}', math)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc required')
    def test_native_cut_renders_two_premises_one_rule_and_exact_annotation(self):
        from lxml import html
        source = (r'\[\Axiom$\Gamma\Rightarrow\Delta,A$'
                  r'\Axiom$A,\Pi\Rightarrow\Lambda$'
                  r'\RightLabel{\ensuremath{\mathrm{Cut}}}'
                  r'\BinaryInf$\Gamma,\Pi\Rightarrow\Delta,\Lambda$\DisplayProof\]')
        prepared, receipt = DisplayAdapter().prepare(source, 'proof')
        result = subprocess.run(['pandoc', '-f', 'latex', '-t', 'html5', '--mathml'],
                                input=prepared, encoding='utf-8', capture_output=True, check=True)
        self.assertNotIn('[WARNING]', result.stderr)
        doc = html.fromstring(result.stdout)
        bind_mathml(doc, receipt)
        self.assertEqual(len(doc.xpath('//mfrac')), 1)
        self.assertEqual(len(doc.xpath('//mfrac/*')), 2)
        self.assertEqual(doc.xpath('//annotation')[0].text, source[2:-2])
        self.assertEqual(doc.xpath('//mo[text()="⇒"]').__len__(), 3)
        self.assertIn('Cut', ''.join(doc.xpath('//mi/text()')))

    def test_prooftree_environment_has_a_balanced_display(self):
        source = r'\begin{prooftree}\Axiom$A$\UnaryInf$B$\end{prooftree}'
        text, receipt = DisplayAdapter().prepare(source, 'proof-env')
        self.assertTrue(text.startswith(r'\[') and text.endswith(r'\]'))
        self.assertEqual(next(iter(receipt['markers'].values()))['original_tex'], source)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc required')
    def test_dotted_double_and_absent_rules_preserve_distinctions(self):
        from lxml import html
        source = (r'\begin{prooftree}\AxiomC{}\RightLabel{$\pi$}\DeduceC{$A$}'
                  r'\doubleLine\UnaryInfC{$B$}\noLine\UnaryInfC{$C$}'
                  r'\LeftLabel{\scriptsize $1$}\RightLabel{rule}\UnaryInfC{$D$}\end{prooftree}')
        prepared, receipt = DisplayAdapter(proof_label_styles={'scriptsize':r'\scriptstyle'}).prepare(source, 'rules')
        result = subprocess.run(['pandoc', '-f', 'latex', '-t', 'html5', '--mathml'],
                                input=prepared, encoding='utf-8', capture_output=True, check=True)
        self.assertNotIn('[WARNING]', result.stderr)
        doc = html.fromstring(result.stdout)
        bind_mathml(doc, receipt)
        self.assertEqual(len(doc.xpath('//mtable[@rowlines="solid solid"]')), 1)
        self.assertEqual(len(doc.xpath('//mo[text()="⋮"]')), 1)
        self.assertEqual(len(doc.xpath('//mfrac[@linethickness="0"]')), 1)
        self.assertEqual(doc.xpath('//annotation')[0].text, source)
        self.assertIn('1', ''.join(doc.xpath('//mn/text()')))
        self.assertIn('rule', ''.join(doc.xpath('//mtext/text()')))

    def test_discharge_label_size_requires_source_configuration(self):
        source = r'\Axiom$A$\LeftLabel{\scriptsize $1$}\UnaryInf$B$\DisplayProof'
        with self.assertRaisesRegex(ValueError, 'native font-size mapping'):
            parse_proof(source)

    def test_sequential_displays_preserve_every_tree_not_only_the_first(self):
        source = r'\Axiom$A$\UnaryInf$B$\DisplayProof\bottomAlignProof\qquad\Axiom$C$\UnaryInf$D$'
        body, end, record = parse_proof_region(source)
        self.assertEqual(end, len(source))
        self.assertEqual(record['trees'], 2)
        self.assertEqual(record['axioms'], 2)
        self.assertEqual(record['inferences'], 2)
        self.assertEqual([r['formula'] for r in record['steps']], list('ABCD'))
        self.assertIn(r'\qquad{}', body)


if __name__ == '__main__': unittest.main()
