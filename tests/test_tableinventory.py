import unittest

from olpkit.tableinventory import columns, inventory


class TableInventoryTests(unittest.TestCase):
    def test_decorated_repeated_and_paragraph_columns(self):
        result=columns(r'@{}>{\bfseries}l*{2}{c|}p{.3\linewidth}!{\quad}')
        self.assertEqual([r['kind'] for r in result],['l','c','c','p'])
        with self.assertRaisesRegex(ValueError,'unsupported column'): columns('Q')

    def test_nested_proofs_spans_and_row_spacing_keep_exact_locators(self):
        text=(r'\begin{tabular}{@{}c@{}c@{}}'
              r'\multicolumn{2}{c}{Rules}\\[2ex]'
              r'\begin{tabular}[t]{l}\Axiom$A$\UnaryInf$B$\DisplayProof\\[3ex]x\end{tabular}'
              r'&\Axiom$C$\UnaryInf$D$\DisplayProof\\\end{tabular}')
        report=inventory(text,'content/rules.tex','OLP-0704')
        outer,inner=report['tables']; self.assertEqual(outer['syntax_status'],'parsed')
        self.assertEqual(len(outer['rows']),2); self.assertEqual(len(inner['rows']),2)
        self.assertEqual(inner['parent'],outer['id'])
        self.assertEqual(outer['rows'][0]['cells'][0]['column_span'],2)
        for table in report['tables']:
            self.assertEqual(text[table['char_start']:table['char_end']],table['source_tex'])
            for row in table['rows']:
                for cell in row['cells']:
                    self.assertEqual(text[cell['char_start']:cell['char_end']],cell['source_tex'])
        self.assertEqual(outer['rows'][1]['cells'][1]['required_math_direction'],'ltr')
        self.assertFalse(report['release_ready']); self.assertEqual(report['status'],'incomplete')

    def test_longtable_bands_caption_and_implicit_cells(self):
        text=(r'\begin{longtable}{lc}\caption{A table}\label{t}\\'
              r'a&b\\\endfirsthead c&d\\\endhead e\\\hline\end{longtable}')
        table=inventory(text,'table')['tables'][0]
        self.assertEqual(table['syntax_status'],'parsed')
        self.assertEqual([r['band'] for r in table['rows']],[0,1,2])
        self.assertEqual(table['rows'][2]['explicit_cells'],1)
        self.assertTrue(table['rows'][2]['cells'][1]['implicit'])
        self.assertEqual([r['command'] for r in table['events']],
                         ['caption','label','endfirsthead','endhead','hline'])

    def test_comments_escaped_separators_groups_and_verbatim(self):
        text=('% \\begin{tabular}{c}ignored\\end{tabular}\n'
              r'\verb|\begin{tabular}{c}ignored\end{tabular}|'
              r'\begin{verbatim}\begin{array}{c}ignored\end{array}\end{verbatim}'
              r'\begin{tabular}{cc}{a&b}&c\&d\end{tabular}')
        report=inventory(text,'sample'); self.assertEqual(len(report['tables']),1)
        self.assertEqual([r['source_tex'] for r in report['tables'][0]['rows'][0]['cells']],
                         ['{a&b}',r'c\&d'])
        self.assertEqual(len(report['ignored_verbatim']),1)

    def test_array_nested_matrix_and_starred_table(self):
        text=(r'\begin{tabular*}{\textwidth}[b]{cc}'
              r'$\begin{array}{cc}a&b\\c&d\end{array}$&text\end{tabular*}')
        report=inventory(text,'sample'); a,b=report['tables']
        self.assertEqual(len(a['rows']),1); self.assertEqual(len(b['rows']),2)
        self.assertTrue(all(c['required_math_direction']=='ltr' for r in b['rows'] for c in r['cells']))

    def test_unsupported_and_unclosed_tables_are_retained(self):
        report=inventory(r'\begin{tabular}{Q}x\end{tabular}\begin{array}{c}x','bad')
        self.assertEqual(len(report['tables']),2)
        self.assertEqual([r['syntax_status'] for r in report['tables']],['unsupported','unsupported'])
        for text in [r'\begin{array}{c}a&b\end{array}',
                     r'\begin{tabular}{c}\multirow{2}{*}{x}\end{tabular}']:
            self.assertEqual(inventory(text,'bad')['tables'][0]['syntax_status'],'unsupported')

    def test_multirow_retains_covered_cells_and_rejects_collisions(self):
        text=r'\begin{tabular}{cc}a&\multirow[t]{2}{*}{$p$}\\b&\end{tabular}'
        table=inventory(text,'spans')['tables'][0]
        self.assertEqual(table['syntax_status'],'parsed')
        self.assertEqual(table['rows'][0]['cells'][1]['row_span'],2)
        self.assertEqual(table['rows'][1]['cells'][1]['covered_by'],[0,1])
        for broken in [text.replace(r'b&\end',r'b&collision\end'),
                       text.replace(r'b&',r'\endhead b&'),
                       text.replace('{2}','{-2}')]:
            self.assertEqual(inventory(broken,'bad')['tables'][0]['syntax_status'],'unsupported')

    def test_conditional_cells_require_native_projection(self):
        from olpkit.selective import SelectionState, Selector
        source=r'\begin{tabular}{cc}a\iftag{p}{&b\\}{}\hline\end{tabular}'
        raw=inventory(source,'conditional')['tables'][0]
        self.assertEqual(raw['syntax_status'],'unsupported')
        self.assertIn('native tag',raw['error'])
        projected=Selector().project(source,SelectionState({'p':True}))
        table=inventory(projected,'selected')['tables'][0]
        self.assertEqual(table['syntax_status'],'parsed')
        self.assertEqual([c['source_tex'] for c in table['rows'][0]['cells']],['a','b'])


if __name__=='__main__': unittest.main()
