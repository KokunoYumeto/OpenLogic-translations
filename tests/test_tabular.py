import shutil,subprocess,unittest
from olpkit.tabular import parse_tabular
from olpkit.mathdisplay import DisplayAdapter,bind_mathml

TABLE = (r'\begin{tabular}{lllll}\cline{2-4}'
         r'\multicolumn{1}{l|}{}&\multicolumn{1}{c|}{$\sqcup$}&\multicolumn{1}{c|}{$I$}&\multicolumn{1}{c|}{$\triangleright$}&\\\cline{1-4}'
         r'\multicolumn{1}{|l|}{$q_0$}&\multicolumn{1}{l|}{}&\multicolumn{1}{l|}{\ensuremath{I,q_1,R}}&\multicolumn{1}{l|}{\phantom{\ensuremath{I,q_1,R}}}&\\\cline{1-4}'
         r'\multicolumn{1}{|l|}{$q_1$}&\multicolumn{1}{l|}{\ensuremath{\sqcup,q_1,R}}&\multicolumn{1}{l|}{\ensuremath{I,q_0,R}}&\multicolumn{1}{l|}{\phantom{\ensuremath{I,q_1,R}}}&\\\cline{1-4}\end{tabular}')

class TableTests(unittest.TestCase):
    def test_table_rules_cells_and_phantoms_survive_normalization(self):
        rendered,record=parse_tabular(TABLE)
        self.assertEqual(len(record['rows']),3)
        self.assertEqual(len(record['rules']),4)
        self.assertEqual(record['rows'][1][0]['source_tex'],r'\multicolumn{1}{|l|}{$q_0$}')
        self.assertNotIn(r'\cline',rendered)
        self.assertIn(r'$\phantom{I,q_1,R}$',rendered)
        self.assertEqual(record['rules'][0],{'boundary':0,'first_column':2,'last_column':4})

    def test_rules_or_widths_cannot_be_guessed(self):
        for source in (r'\begin{tabular}{cc}a&b&c\end{tabular}',r'\begin{tabular}{cc}\cline{1-3}a&b\end{tabular}',
                       r'\begin{tabular}{cc}a\cline{1-2}&b\end{tabular}'):
            with self.assertRaises(ValueError):parse_tabular(source)

    @unittest.skipUnless(shutil.which('pandoc'),'Pandoc required')
    def test_rendered_table_preserves_row_labels_instead_of_printing_cline_ranges(self):
        from lxml import html
        source=r'Before\[\centering'+TABLE+r'\]After'
        prepared,receipt=DisplayAdapter().prepare(source,'fixture')
        run=subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],input=prepared,encoding='utf-8',capture_output=True,check=True)
        self.assertFalse(run.stderr)
        document=html.fromstring(run.stdout)
        binding=bind_mathml(document,receipt)
        self.assertEqual(binding['tables']['bound'],1)
        rows=document.xpath('//table//tr')
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[1][0].xpath('.//annotation/text()'),['q_0'])
        self.assertEqual(rows[2][0].xpath('.//annotation/text()'),['q_1'])
        self.assertEqual(len(document.xpath('//mphantom')),2)
        self.assertNotIn('2-4',document.text_content())
        self.assertNotIn('1-4',document.text_content())
        self.assertEqual(document.xpath('//table/@data-source-tex'),[TABLE])
        self.assertNotIn('border-top',rows[0][0].get('style'))
        self.assertIn('border-top',rows[0][1].get('style'))
        self.assertIn('border-bottom',rows[2][0].get('style'))

if __name__=='__main__':unittest.main()
