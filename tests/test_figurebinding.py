import json
import tempfile
import unittest
from pathlib import Path

from lxml import html, etree

from olpkit.figurebinding import prepare_figures, bind_figures, inspect_svg, attach_long_descriptions
from olpkit.nativefigures import sha


class FigureBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.picture = r'\begin{tikzpicture}\node{$q_0$};\end{tikzpicture}'
        self.svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10" viewBox="0 0 20 10"><path d="M0 0 L1 1"/></svg>'
        (self.root/'figure-001.tex').write_text(self.picture, encoding='utf-8')
        (self.root/'figure-001.svg').write_bytes(self.svg)
        self.exported = {'schema':'olpkit.native-figures.v1',
                         'status':'vectors_exported_pending_visual_and_semantic_checks',
                         'source_sha256':'prior-projection-hash', 'configuration_evidence':{'actual':'native'},
                         'figures':[{'index':1, 'source_sha256':sha(self.picture.encode()),
                                     'source_file':'figure-001.tex', 'asset':'figure-001.svg',
                                     'svg_sha256':sha(self.svg), 'width':'20', 'height':'10', 'viewBox':'0 0 20 10'}]}

    def prepared(self, text=None):
        return prepare_figures(text or self.picture, 'book.tex', self.exported, self.root)

    def bind(self, doc, receipt, **kwargs):
        return bind_figures(doc, receipt, asset_prefix='assets/native', fallback_alt='Gambar', **kwargs)

    def test_repeated_diagrams_keep_separate_occurrences(self):
        self.exported['figures'].append({**self.exported['figures'][0], 'index':2})
        result, receipt = self.prepared('before '+self.picture+' between '+self.picture+' after')
        self.assertEqual(len(receipt['markers']),2)
        doc=html.fromstring('<p>before OLPNATIVEFIG000001 between OLPNATIVEFIG000002 after</p>')
        report=self.bind(doc,receipt)
        self.assertEqual(doc.text_content(),'before  between  after')
        self.assertEqual(len(doc.xpath('.//img')),2)
        self.assertEqual(report['descriptions_pending'],['OLPNATIVEFIG000001','OLPNATIVEFIG000002'])

    def test_source_asset_or_order_changes_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'source/order'):
            self.prepared(self.picture.replace('q_0','q_1'))
        (self.root/'figure-001.svg').write_bytes(self.svg+b' ')
        with self.assertRaisesRegex(ValueError,'asset hash'):
            self.prepared()

    def test_tableau_must_have_its_own_exact_vector_and_localized_description(self):
        tableau=r'\begin{oltableau}[A,just={Given}[B,close][C]]\end{oltableau}'
        with self.assertRaisesRegex(ValueError,'source/order'):
            self.prepared(tableau)
        (self.root/'figure-001.tex').write_text(tableau,encoding='utf-8')
        self.exported['figures'][0]['source_sha256']=sha(tableau.encode())
        prepared,receipt=self.prepared('Before '+tableau+' After')
        self.assertIn('Before ',prepared);self.assertIn(' After',prepared)
        self.assertEqual(receipt['markers']['OLPNATIVEFIG000001']['environment'],'oltableau')
        doc=html.fromstring('<p>Before OLPNATIVEFIG000001 After</p>')
        report=self.bind(doc,receipt,descriptions={sha(tableau.encode()):'Tableau with two branches'})
        self.assertEqual(report['descriptions_pending'],[])
        self.assertEqual(doc.text_content(),'Before  After')
        self.assertEqual(doc.xpath('.//img/@alt'),['Tableau with two branches'])

    def test_external_relative_width_and_centering_are_preserved(self):
        self.exported['figures'][0]['width_percent']=80
        _,r=self.prepared()
        doc=html.fromstring('<p>OLPNATIVEFIG000001</p>')
        self.bind(doc,r)
        self.assertIn('width:80%;',doc.xpath('.//img/@style')[0])
        self.assertIn('text-align:center',doc.xpath('.//span/@style')[0])

    def test_source_count_and_path_escape_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'occurrence count'):
            self.prepared('no diagram')
        self.exported['figures'][0]['asset']='../external.svg'
        with self.assertRaisesRegex(ValueError,'outside'):
            self.prepared()

    def test_display_wrapper_is_replaced_but_intertext_stays(self):
        _,r=self.prepared()
        doc=html.fromstring('<div><p>îki</p><math display="block"><semantics><mtable><mtr><mtd/><mtd><mtext>OLPNATIVEFIG000001</mtext></mtd></mtr></mtable><annotation encoding="application/x-tex">\\mbox{OLPNATIVEFIG000001}</annotation></semantics></math><p>sabanjuré</p></div>')
        report=self.bind(doc,r,descriptions={sha(self.picture.encode()):'Kahanan q₀.'})
        self.assertEqual(report['bound'],1)
        self.assertFalse(report['descriptions_pending'])
        self.assertEqual(doc.xpath('.//img/@alt'),['Kahanan q₀.'])
        self.assertEqual(doc.xpath('.//p/text()'),['îki','sabanjuré'])
        self.assertFalse(doc.xpath('.//math'))

    def test_mixed_math_is_never_discarded(self):
        _,r=self.prepared()
        for extra in ['<mo>+</mo><mn>1</mn>','<mfrac><mrow/><mrow/></mfrac>']:
            doc=html.fromstring('<div><math><mrow><mtext>OLPNATIVEFIG000001</mtext>'+extra+'</mrow></math></div>')
            with self.assertRaisesRegex(ValueError,'other mathematics'):
                self.bind(doc,r)

    def test_inline_tail_preserves_order_and_surrounding_words(self):
        _,r=self.prepared()
        doc=html.fromstring('<p>before <em>term</em> OLPNATIVEFIG000001 after</p>')
        self.bind(doc,r)
        self.assertEqual(doc.text_content(),'before term  after')
        self.assertEqual([x.tag for x in doc],['em','span'])

    def test_missing_duplicate_and_empty_description_fail(self):
        _,r=self.prepared()
        for text, msg in [('absent','unbound'),('OLPNATIVEFIG000001 OLPNATIVEFIG000001','duplicate')]:
            with self.assertRaisesRegex(ValueError,msg):self.bind(html.fromstring('<p>'+text+'</p>'),r)
        with self.assertRaisesRegex(ValueError,'empty'):
            self.bind(html.fromstring('<p>OLPNATIVEFIG000001</p>'),r,descriptions={sha(self.picture.encode()):''})

    def test_namespaced_math_and_svg_active_content(self):
        _,r=self.prepared()
        doc=etree.fromstring(b'<div><math xmlns="http://www.w3.org/1998/Math/MathML"><mtext>OLPNATIVEFIG000001</mtext></math></div>')
        self.assertEqual(self.bind(doc,r)['bound'],1)
        for body in [b'<image/>',b'<script/>',b'<use href="https://example.org/x"/>',b'<path onclick="x"/>']:
            with self.assertRaises(ValueError):inspect_svg(self.svg.replace(b'<path d="M0 0 L1 1"/>',body))

    def test_visible_long_description_keeps_prose_and_never_interprets_html(self):
        _,r=self.prepared();h=sha(self.picture.encode())
        doc=html.fromstring('<div><p>Before OLPNATIVEFIG000001 after.</p></div>')
        self.bind(doc,r,descriptions={h:'State q₀.'})
        data={h:{'source_sha256':h,'occurrence_indices':[1],'alt_text':'State q₀.',
                 'long_description':'A < B & C.\n\nFrom 0 to 1.\nFrom 1 to 0.'}}
        result=attach_long_descriptions(doc,r,data,labels={'description_link':'Read description','descriptions_heading':'Descriptions'},figure_label='Figure')
        self.assertEqual(result['occurrences'],1)
        self.assertEqual(doc.xpath('./p')[0].text_content(),'Before  Read description after.')
        self.assertEqual(doc.xpath('.//section/section/p/text()'),['A < B & C.'])
        self.assertEqual(doc.xpath('.//section/section/ul/li/text()'),['From 0 to 1.','From 1 to 0.'])
        self.assertEqual(doc.xpath('.//img/@aria-details'),['olp-diagram-description-1'])
        self.assertEqual(doc.xpath('.//h3/a/@href'),['#olp-native-figure-1'])
        with self.assertRaisesRegex(ValueError,'already attached'):
            attach_long_descriptions(doc,r,data,labels={'description_link':'Read','descriptions_heading':'Descriptions'},figure_label='Figure')

    def test_incomplete_long_description_never_silently_passes(self):
        _,r=self.prepared();h=sha(self.picture.encode())
        doc=html.fromstring('<div>OLPNATIVEFIG000001</div>');self.bind(doc,r,descriptions={h:'State.'})
        with self.assertRaisesRegex(ValueError,'coverage'):
            attach_long_descriptions(doc,r,{},labels={'description_link':'Read','descriptions_heading':'Descriptions'},figure_label='Figure')


if __name__ == '__main__': unittest.main()
