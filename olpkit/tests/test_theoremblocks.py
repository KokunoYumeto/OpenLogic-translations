import unittest
from lxml import html
from olpkit.theoremblocks import native_theorems, source_theorems, reconcile_theorem_source, prepare_theorems, bind_theorems


class TheoremBlockTests(unittest.TestCase):
    def native(self, kind='defn', title='Title', name=r'\definitionname ', number='1.{1}'):
        return native_theorems(r'\contentsline {'+kind+'}{{'+name+'}{'+number+'}{'+title+'}}{2}{'+kind+'*.10}%\n')

    def test_native_number_title_and_exact_executed_source(self):
        source=r'\newcommand{\unused}{\begin{defn}unused\end{defn}}\begin{defn}[Title]content\end{defn}'
        n=self.native()
        rows=reconcile_theorem_source(source,n)
        self.assertEqual(len(rows),1)
        self.assertEqual(n[0]['number'],'1.1')
        prepared,receipt=prepare_theorems(source,n,{'defn':'Definisi'},evidence={'native':'reconciled'},proof_symbol=r'\Box')
        self.assertIn(r'\textbf{Definisi 1.1 (Title).}',prepared)
        self.assertIn('content',prepared)
        self.assertEqual(receipt['records'][0]['source_sha256'],rows[0]['source_sha256'])

    def test_native_script_number_is_preserved_in_theorem_heading(self):
        n=self.native(number='१.{१२}')
        prepared,receipt=prepare_theorems(r'\begin{defn}[Title]content\end{defn}',n,{'defn':'व्याख्या'},evidence={'native':'fixture'},proof_symbol=r'\Box')
        self.assertIn('व्याख्या १.१२',prepared)
        self.assertEqual(n[0]['number'],'१.१२')

    def test_mismatched_native_title_and_kind_fail(self):
        source=r'\begin{defn}[Different]content\end{defn}'
        with self.assertRaisesRegex(ValueError,'title differs'):reconcile_theorem_source(source,self.native())
        with self.assertRaisesRegex(ValueError,'count/order'):
            prepare_theorems(source,self.native(kind='ex'),{'ex':'Example'},evidence={'x':1},proof_symbol=r'\Box')

    def test_custom_proof_heading_replaces_default_and_has_no_counter(self):
        source=r'\begin{proof}[Bukti \olref{thm}]body\end{proof}'
        native=self.native(kind='proof',title='',name=r'Bukti \olref {thm}',number='12')
        self.assertEqual(len(reconcile_theorem_source(source,native)),1)
        text,receipt=prepare_theorems(source,native,{'proof':'Bukti'},evidence={'x':1},proof_symbol=r'\Box')
        self.assertIn(r'\textit{Bukti \olref{thm}.}',text)
        self.assertNotIn('12',receipt['records'][0]['heading_tex'])
        self.assertIn(r'\hfill\(\Box\)',text)

    def test_unsupported_end_placement_and_unbalanced_environment_fail(self):
        with self.assertRaisesRegex(ValueError,'proof-end'):source_theorems(r'\begin{proof}x\qedhere\end{proof}')
        with self.assertRaisesRegex(ValueError,'unclosed'):source_theorems(r'\begin{defn}x')
        with self.assertRaisesRegex(ValueError,'unbalanced'):source_theorems(r'\begin{defn}x\end{thm}')

    def test_dom_binding_never_overwrites_body_or_native_number(self):
        _,receipt=prepare_theorems(r'\begin{defn}[Title]body\end{defn}',self.native(),{'defn':'Definisi'},evidence={'x':1},proof_symbol=r'\Box')
        doc=html.fromstring('<article><div class="olpnativetheorem"><p>OLPTHEOREM000001<strong>Definisi 1.1 (Title).</strong></p><p>body</p></div></article>')
        result=bind_theorems(doc,receipt)
        self.assertEqual(result['numbered'],1)
        self.assertEqual(doc.xpath('.//div/@data-native-number'),['1.1'])
        self.assertEqual(doc.xpath('.//div/@id'),['olp-native-theorem-000001'])
        self.assertEqual(doc.xpath('.//div/p[2]/text()'),['body'])
        with self.assertRaisesRegex(ValueError,'count'):bind_theorems(html.fromstring('<article/>'),receipt)

    def test_nested_theorems_keep_native_opening_order(self):
        text=r'\begin{thm}outer\begin{proof}inner\end{proof}\end{thm}'
        native=self.native(kind='thm',title='',name=r'\theoremname')+self.native(kind='proof',title='',name=r'\proofname',number='1')
        prepared,receipt=prepare_theorems(text,native,{'thm':'Teorema','proof':'Bukti'},evidence={'x':1},proof_symbol=r'\Box')
        self.assertEqual([r['kind'] for r in receipt['records']],['thm','proof'])
        self.assertEqual(prepared.count(r'\begin{olpnativetheorem}'),2)


if __name__=='__main__':unittest.main()
