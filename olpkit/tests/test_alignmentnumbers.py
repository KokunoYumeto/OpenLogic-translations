import copy
import shutil
import subprocess
import unittest

from olpkit.alignmentnumbers import numbered_rows
from olpkit.references import References, bind_references
from olpkit.mathdisplay import DisplayAdapter, bind_mathml
from olpkit.bookcontext import display_inventory


def referenced(source):
    labels = {
        'one': {'number_tex':'११.३', 'kind':'equation', 'destination':'equation.11.3', 'page':'41'},
        'two': {'number_tex':'११.७', 'kind':'equation', 'destination':'equation.11.7', 'page':'42'},
        'tagged': {'number_tex':r'{\textit {Tr}}','kind':'equation','destination':'AMS.1','page':'43'}}
    return References(labels, {}, pair_conjunction=' and ', evidence={
        'inputs': {'native_pdf_sha256':'a'*64, 'aux_sha256':'b'*64, 'assembly_sha256':'c'*64}}
    ).prepare(source,'numbered-alignment-fixture')


class NumberedAlignmentTests(unittest.TestCase):
    def test_native_anchor_retains_number_type_and_destination(self):
        _, ref = referenced(r'\label{one}')
        native = ref['markers']['OLPXREF000000']['native_label']
        self.assertEqual(native['number_tex'],'११.३')
        self.assertEqual(native['kind'],'equation')
        self.assertEqual(native['destination'],'equation.11.3')

    def test_row_controls_do_not_split_nested_matrix(self):
        source = r'a&=\begin{matrix}b\\c\end{matrix}\notag\\[1ex]d&=e\label{two}\\'
        text, refs = referenced(source)
        rendered, record = numbered_rows(text, refs)
        self.assertEqual([r['number'] for r in record['rows']],[None,'११.७'])
        self.assertIn(r'\begin{matrix}b\\c\end{matrix}',rendered)
        self.assertIn(r'\\[1ex]',rendered)
        self.assertNotIn(r'\notag',rendered)
        self.assertFalse(rendered.endswith(r'\\'))
        for row in record['rows']:
            self.assertEqual(text[row['char_start']:row['char_end']],row['source_tex'])

    def test_missing_stale_or_wrong_kind_number_evidence_is_rejected(self):
        text, refs = referenced(r'a&=b\label{one}')
        for mutation, message in [
            (lambda r: r['auxiliary_evidence']['inputs'].pop('native_pdf_sha256'),'bound PDF'),
            (lambda r: r['markers']['OLPXREF000000']['native_label'].update(kind='thm'),'equation label'),
            (lambda r: r['markers']['OLPXREF000000']['native_label'].pop('destination'),'equation label')]:
            bad = copy.deepcopy(refs); mutation(bad)
            with self.assertRaisesRegex(ValueError,message): numbered_rows(text,bad)
        with self.assertRaisesRegex(ValueError,'exactly one'): numbered_rows('a&=b',refs)
        with self.assertRaisesRegex(ValueError,'PDF-derived'): numbered_rows(text,None)

    def test_conflicting_row_controls_are_not_silently_resolved(self):
        for source, message in [
            (r'a&=b\notag\label{one}','suppressed'),
            (r'a&=b\label{one}\label{two}','exactly one'),
            (r'a&=b\notag\nonumber','repeated'),
            (r'a&={b\notag}\label{one}','grouped'),
            (r'a&=b\tag{3}\label{one}','differs from native'),
            (r'a&=b\tag{3}\tag{4}\label{one}','conflicting')]:
            text, refs = referenced(source)
            with self.subTest(source=source),self.assertRaisesRegex(ValueError,message):
                numbered_rows(text,refs)

    def test_context_uses_same_bound_numbers_as_body(self):
        text, refs = referenced(r'\begin{align}a&=b\notag\intertext{Reason.}b&=c\label{two}\end{align}')
        record=display_inventory(text,{'proof_label_styles':{},'math_font_sizes':{}},native_references=refs)
        rows=[r for m in record['markers'].values() if m['kind']=='numbered-alignment' for r in m['alignment']['rows']]
        self.assertEqual([r['number'] for r in rows],[None,'११.७'])
        self.assertFalse(record['reader_complete'])

    def test_unbound_numbered_or_explicitly_tagged_math_cannot_pass_through(self):
        for source in [r'\begin{equation}a=b\end{equation}',
                       r'\begin{align}a&=b\end{align}',
                       r'\begin{align*}a&=b\tag{X}\end{align*}',
                       r'\[a=b\tag{X}\]',
                       r'\begin{multline}a+b\\c+d\end{multline}']:
            with self.subTest(source=source),self.assertRaisesRegex(ValueError,'native|PDF-derived'):
                DisplayAdapter().prepare(source,'fixture')


@unittest.skipUnless(shutil.which('pandoc'),'Pandoc required')
class NumberedAlignmentRenderTests(unittest.TestCase):
    def render(self, source):
        from lxml import html
        text, refs = referenced(source)
        prepared, receipt = DisplayAdapter(native_references=refs).prepare(text,'fixture')
        run = subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],input=prepared,
                             capture_output=True,encoding='utf-8',check=True)
        self.assertEqual(run.stderr,'')
        doc=html.fromstring(run.stdout)
        result=bind_mathml(doc,receipt)
        bind_references(doc,refs)
        self.assertNotIn('OLPDISPLAY',html.tostring(doc,encoding='unicode'))
        self.assertNotIn('OLPXREF',html.tostring(doc,encoding='unicode'))
        return doc,receipt,result,text

    def test_four_step_derivation_retains_prose_suppression_and_final_number(self):
        source=(r'\begin{align}Q&\vdash A\notag\intertext{First reason.}'
                r'Q&\vdash B\nonumber\intertext{Second reason with $x<y$.}'
                r'Q&\vdash C\notag\intertext{Conclusion.}Q&\vdash D\label{one}\end{align}')
        doc,receipt,result,text=self.render(source)
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['(११.३)'])
        self.assertEqual(len(doc.xpath('//mtable[@data-native-numbering]/mtr')),4)
        self.assertEqual(len(doc.xpath('//*[@id="one"]')),1)
        self.assertEqual(result['native_equation_numbers'],[{'label':'one','number':'११.३'}])
        words=' '.join(doc.itertext())
        self.assertLess(words.index('First reason.'),words.index('Second reason'))
        self.assertLess(words.index('Second reason'),words.index('Conclusion.'))
        event=next(e for e in receipt['events'] if e['kind']=='intertext')
        self.assertEqual(event['original_tex'],text)
        for row in event['prose_segments']:
            self.assertEqual(text[row['char_start']:row['char_end']],row['prose'])

    def test_numbered_rows_do_not_restart_and_nested_math_annotations_stay_exact(self):
        source=(r'\begin{align}a&=\nicefrac12\label{one}\\b&=c\notag'
                r'\intertext{Next step.}d&=\nicefrac34\label{two}\end{align}')
        doc,receipt,result,text=self.render(source)
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['(११.३)','(११.७)'])
        self.assertEqual(len(doc.xpath('//mfrac[@bevelled="true"]')),2)
        for row in receipt['markers'].values():
            self.assertEqual(text[row['char_start']:row['char_end']],row['original_tex'])
        self.assertEqual(len(doc.xpath('//mtable[@data-native-numbering]/mtr')),3)

    def test_ordinary_equation_and_alignment_keep_numbers_and_equation_references(self):
        source=(r'\begin{equation}a=b\label{one}\end{equation}'
                r'By \eqref{one}, we get \begin{align}b&=c\label{two}\\'
                r'&\text{from \eqref{one}}\notag\end{align}')
        doc,receipt,result,text=self.render(source)
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['(११.३)','(११.७)'])
        self.assertEqual(doc.xpath('//a[@href="#one"]/text()'),['(११.३)'])
        self.assertEqual(doc.xpath('//mtext[@href="#one"]/text()'),['(११.३)'])
        self.assertEqual([e['environment'] for e in receipt['events'] if e['kind']=='native-numbered-display'],['equation','align'])
        self.assertEqual(len(result['native_equation_numbers']),2)

    def test_literal_italic_tag_and_both_reference_modes_preserve_style(self):
        source=(r'\begin{equation}T\vdash A\label{tagged}\tag{\textit{Tr}}\end{equation}'
                r'See \eqref{tagged} and $\text{by \eqref{tagged}}$.')
        doc,receipt,result,text=self.render(source)
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['(Tr)'])
        self.assertEqual(doc.xpath('//mtd[@data-equation-label]//mtext[@mathvariant="italic"]/text()'),['Tr'])
        self.assertEqual(doc.xpath('//a[@href="#tagged"]/span[@style="font-style:italic"]/text()'),['Tr'])
        self.assertEqual(doc.xpath('//mrow[@href="#tagged"]/mtext[@mathvariant="italic"]/text()'),['Tr'])
        self.assertEqual(result['native_equation_numbers'],[{'label':'tagged','number':'Tr'}])

    def test_starred_explicit_tag_keeps_its_unparenthesized_display(self):
        doc,_,_,_=self.render(r'\begin{equation}a=b\label{tagged}\tag*{\textit{Tr}}\end{equation}')
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['Tr'])

    def test_gather_rows_keep_each_native_number(self):
        doc,_,_,_=self.render(r'\begin{gather}a=b\label{one}\\c=d\label{two}\end{gather}')
        self.assertEqual([''.join(n.itertext()) for n in doc.xpath('//mtd[@data-equation-label]')],['(११.३)','(११.७)'])

    def test_converted_row_loss_fails_binding(self):
        from lxml import html
        text, refs=referenced(r'\begin{align}a&=b\label{one}\intertext{Reason.}c&=d\label{two}\end{align}')
        prepared,receipt=DisplayAdapter(native_references=refs).prepare(text,'fixture')
        run=subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],input=prepared,
                           capture_output=True,encoding='utf-8',check=True)
        doc=html.fromstring(run.stdout)
        row=doc.xpath('//mtable/mtr')[0];row.getparent().remove(row)
        with self.assertRaisesRegex(ValueError,'rows differ'):bind_mathml(doc,receipt)
