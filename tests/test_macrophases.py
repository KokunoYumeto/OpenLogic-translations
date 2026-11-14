import shutil
import subprocess
import unittest
from olpkit.macrophases import declarations, digest, merge_macro_phases


class MacroPhasesTests(unittest.TestCase):
    def test_final_definition_and_provenance(self):
        phases = [('base', r'\newcommand{\Choice}{x}'),
                  ('book', r'\renewcommand*{\Choice}{y}')]
        text, receipt = merge_macro_phases(phases)
        self.assertEqual(list(d['emitted'] for d in declarations(text)), [r'\newcommand*{\Choice}{y}'])
        self.assertEqual(receipt['duplicate_names_resolved'], [r'\Choice'])
        self.assertEqual(receipt['definitions'][r'\Choice'][0]['source_sha256'], digest(phases[0][1]))
        self.assertEqual(receipt['merged_sha256'], digest(text))

    def test_comments_and_scoped_declarations_cannot_override(self):
        original = r'\newcommand{\Choice}{x}'
        ignored = '\n% '+r'\renewcommand{\Choice}{wrong}'+'\n'+r'{\renewcommand{\Choice}{local}}'
        text, receipt = merge_macro_phases([('one', original+ignored)])
        self.assertIn(original, text)
        self.assertIn(ignored, text)
        self.assertEqual(len(receipt['definitions'][r'\Choice']), 1)

    def test_escaped_percent_and_braces_default_argument(self):
        source = r'\newcommand\Choice[2][{[x]}]{\{#1\}\%+#2}'
        text, _ = merge_macro_phases([('one', source)])
        self.assertIn(source, text)

    def test_nested_declaration_stays_in_outer_body(self):
        source = r'\newcommand{\Outer}{\newcommand{\Inner}{x}}'
        text, receipt = merge_macro_phases([('one', source)])
        self.assertEqual(set(receipt['definitions']), {r'\Outer'})
        self.assertIn(source, text)

    def test_invalid_phase_and_truncated_declaration(self):
        for phases in [[], [('x',''),('x','')], [('x',r'\newcommand{\Foo}{x')],
                       [('x',r'\newcommand{\Foo}[0][x]{x}')]]:
            with self.subTest(phases=phases), self.assertRaises(ValueError): merge_macro_phases(phases)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc is needed for actual macro precedence regression')
    def test_actual_pandoc_uses_final_book_notation(self):
        phases = [('base',r'\newcommand{\Choice}{x}'),('book',r'\newcommand{\Choice}{y}')]
        merged, _ = merge_macro_phases(phases)
        def render(text):
            return subprocess.run([shutil.which('pandoc'),'-f','latex','-t','html5','--mathml'],
                input=text+'\n$\\Choice$',text=True,encoding='utf-8',capture_output=True,check=True,timeout=20).stdout
        self.assertIn('<mi>x</mi>',render('\n'.join(t for _,t in phases)))
        self.assertIn('<mi>y</mi>',render(merged))
        self.assertNotIn('<mi>x</mi>',render(merged))


if __name__ == '__main__': unittest.main()
