import shutil,subprocess,unittest
from olpkit.bookbody import pandoc_import_scopes


class ImportScopeTests(unittest.TestCase):
    def test_only_synthetic_document_wrapper_changes(self):
        prefix=r'\hypertarget{olp-unit-000176}{}'
        body=r'\def\ol@sectioncs{section}\chapter*{About} A {bold} $\begingroup x+y\endgroup$.'
        source='{\n'+prefix+r'\begingroup'+body+r'\endgroup\par}'
        converted,report=pandoc_import_scopes(source)
        self.assertEqual(converted,'{\n'+prefix+'{'+body+r'}\par}')
        self.assertEqual(len(report['imports']),1)
        self.assertEqual(report['imports'][0]['unit'],'olp-unit-000176')

    def test_authored_and_unidentified_scopes_are_untouched(self):
        source=r'{\textbf{Text}} $\begingroup x+y\endgroup$ \begingroup\chapter{Title}\endgroup'
        converted,report=pandoc_import_scopes(source)
        self.assertEqual(converted,source);self.assertEqual(report['imports'],[])

    def test_ordinary_import_and_literal_escaped_braces_are_not_rewritten(self):
        source=r'\verb|{| \{ \hypertarget{olp-unit-000001}{}\begingroup\def\ol@sectioncs{section} Text\endgroup'
        converted,report=pandoc_import_scopes(source)
        self.assertEqual(converted,source);self.assertEqual(report['imports'],[])

    def test_missing_scope_end_is_a_failure(self):
        with self.assertRaisesRegex(ValueError,'group'):
            pandoc_import_scopes(r'\hypertarget{olp-unit-000001}{}\begingroup\def\ol@sectioncs{section} Text')

    @unittest.skipUnless(shutil.which('pandoc'),'Pandoc required for the mixed-group regression')
    def test_mixed_native_layout_group_exports_all_prose_math_and_links(self):
        source='{\n'+r'\addtolength{\beforechapskip}{-\baselineskip}'+'\n'+(
            r'\hypertarget{olp-unit-000176}{}\begingroup\def\ol@sectioncs{section}'+'\n'+
            r'\chapter*{About}'+'\n\n'+r'Exact $x+y$ text. \href{https://example.org/}{Source}.'+'\n\n'+r'\endgroup\par}')
        converted,report=pandoc_import_scopes(source)
        result=subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],input=converted,
                              capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stderr,'')
        for value in ['About','Exact','text.','https://example.org/','Source','<math','<mi>x</mi>','<mi>y</mi>']:
            self.assertIn(value,result.stdout)
        self.assertEqual(len(report['imports']),1)


if __name__=='__main__':unittest.main()
