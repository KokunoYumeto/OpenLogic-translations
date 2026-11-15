import unittest,shutil,subprocess
from olpkit.bibliography import read_citation_labels,read_bibliography,bibliography_tex,expand_citations,citation_parts,bind_bibliography


STYLE={'open':'(','close':')','separator':';','author_year':',','year_separator':',','note_separator':', '}
AUX=r'\bibcite{a}{{1}{1936{a}}{{Church}}{{}}}\bibcite{b}{{2}{1936{b}}{{Church}}{{}}}\bibcite{c}{{3}{1986}{{Feferman et~al.}}{{Feferman, Dawson, lan Kleene}}}\bibcite{d}{{4}{1990}{{Feferman et~al.}}{{Feferman, Dawson, lan Kleene}}}'


class BibliographyTests(unittest.TestCase):
    def setUp(self):self.labels=read_citation_labels(AUX)

    def labels_for(self,source):
        _,r=expand_citations(source,self.labels,style=STYLE,evidence={'native':'checked'})
        return ''.join(p['label_tex'] for p in r['calls'][0]['parts'])

    def test_same_author_year_suffixes_and_distinct_years(self):
        self.assertEqual(self.labels_for(r'\citet{a,b}'),'Church (1936{a},b)')
        self.assertEqual(self.labels_for(r'\citep{c,d}'),'(Feferman et~al., 1986, 1990)')

    def test_notes_bare_cite_and_stars(self):
        self.assertEqual(self.labels_for(r'\cite{a}'),'Church (1936{a})')
        self.assertEqual(self.labels_for(r'\cite[pp.~2--3]{a}'),'(Church, 1936{a}, pp.~2--3)')
        self.assertEqual(self.labels_for(r'\citet[see][p.~2]{a}'),'Church (see 1936{a}, p.~2)')
        self.assertEqual(self.labels_for(r'\citealt*{c}'),'Feferman, Dawson, lan Kleene 1986')

    def test_distinct_authors_preserve_separate_links_and_punctuation(self):
        text,receipt=expand_citations(r'\citet{a,c}',self.labels,style=STYLE,evidence={'n':1})
        self.assertEqual(''.join(p['label_tex'] for p in receipt['calls'][0]['parts']),
                         'Church (1936{a}); Feferman et~al. (1986)')
        self.assertEqual(text.count(r'\hyperlink'),2)

    def test_unknown_or_ambiguous_citations_are_not_guessed(self):
        with self.assertRaisesRegex(ValueError,'unknown'):self.labels_for(r'\citep{z}')
        with self.assertRaisesRegex(ValueError,'unsupported'):self.labels_for(r'\citetalias{a}')
        with self.assertRaisesRegex(ValueError,'duplicate'):self.labels_for(r'\citep{a,a}')
        with self.assertRaisesRegex(ValueError,'punctuation'):
            expand_citations(r'\cite{a}',self.labels,style={},evidence={'n':1})

    def test_definitions_and_opaque_figures_do_not_execute_citations(self):
        source=r'\newcommand{\unused}{\cite{z}}\begin{tikzpicture}\node{\cite{z}};\end{tikzpicture}\cite{a}'
        output,r=expand_citations(source,self.labels,style=STYLE,evidence={'n':1})
        self.assertEqual(len(r['calls']),1);self.assertIn(r'\cite{z}',output)

    def test_complete_native_bibliography_preserves_authored_bodies(self):
        body=r'\begin{thebibliography}{4}'+''.join(r'\bibitem[{Name(2000)}]{'+k+r'}Name. \emph{Title {X}}. \url{https://example.org/'+k+'}.' for k in self.labels)+r'\end{thebibliography}'
        record=read_bibliography(body,self.labels,evidence={'n':1})
        out=bibliography_tex(record,'Kapustakan')
        self.assertEqual(len(record['entries']),4)
        self.assertIn(r'\emph{Title {X}}',out)
        self.assertIn('https://example.org/d',out)
        with self.assertRaisesRegex(ValueError,'coverage'):read_bibliography(body,self.labels|{'extra':{}},evidence={'n':1})

    @unittest.skipUnless(shutil.which('pandoc'),'Pandoc required')
    def test_footnote_citations_remain_bound_when_moved_to_the_end(self):
        from lxml import html
        bbl=r'\begin{thebibliography}{4}'+''.join(r'\bibitem[{Name(2000)}]{'+k+r'}Name. Title.' for k in self.labels)+r'\end{thebibliography}'
        record=read_bibliography(bbl,self.labels,evidence={'n':1})
        source=r'First\footnote{Note \citep{a}.} Then \citet{c}.'+bibliography_tex(record,'References')
        source,calls=expand_citations(source,self.labels,style=STYLE,evidence={'n':1})
        run=subprocess.run(['pandoc','-f','latex','-t','html5'],input=source,encoding='utf-8',capture_output=True,check=True)
        self.assertFalse(run.stderr)
        doc=html.fromstring(run.stdout)
        report=bind_bibliography(doc,record,calls)
        self.assertEqual(report['rendered_call_order'],['olp-citation-000002','olp-citation-000001'])
        self.assertEqual(report['citation_links'],2)
        self.assertEqual(len(doc.xpath('//ol[@class="olp-bibliography-list"]/li')),4)
        self.assertFalse(doc.xpath('//*[@role="doc-biblioentry"]'))
        doc.xpath('//span[@id="olp-citation-000001"]/a')[0].set('href','#'+self.labels['b']['anchor'])
        with self.assertRaisesRegex(ValueError,'destination'):bind_bibliography(doc,record,calls)


if __name__=='__main__':unittest.main()
