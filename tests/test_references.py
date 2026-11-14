import shutil
import subprocess
import unittest

from olpkit.references import read_aux, References, bind_references


def label(number='2.3',kind='thm',counter='3',prefix='2'):
    return dict(number_tex=number,page='23',kind=kind,counter=counter,counter_prefix=prefix)


def adapter(labels,**kwargs):
    return References(labels,{'thm':('Teorema','Teorema'),'section':('Perangan','Perangan'),
                             'chapter':('Bab','Bab')},
                      evidence={'fixture':'explicit native witness'},pair_conjunction=' lan ',**kwargs)


class ReferenceTests(unittest.TestCase):
    def test_aux_balanced_fields_and_native_number_consistency(self):
        rows=read_aux(r'\newlabel{x}{{7.{13}}{99}{A {nested} title}{thm.1}{}}'+'\n'+
                      r'\newlabel{x@cref}{{[thm][13][7]7.{13}}{[1][98][]99}{}{}{}}')
        self.assertEqual(rows['x']['number_tex'],'7.{13}')
        self.assertEqual(rows['x']['kind'],'thm')
        self.assertEqual(rows['x']['counter_prefix'],'7')
        with self.assertRaisesRegex(ValueError,'mismatch'):
            read_aux(r'\newlabel{x}{{2}{3}{}{dest}{}}'+'\n'+r'\newlabel{x@cref}{{[thm][3][]3}{}{}{}{}}')

    def test_context_respects_import_groups_and_locale_and_deferred_restore(self):
        keys=['a:b:c:x','a:b:d:x','z:y:w:x']
        source=(r'\olfileid[jv]{a}{b}{c}\newcommand{\unused}{\olfileid{x}{y}{z}\ollabel{hidden}}'
                r'\begingroup\olfileid{a}{b}{d}\olref{x}\ollabel{x}\endgroup'
                r'\olref{x}\ollabel{x}'
                r'\begingroup\renewcommand*{\theolpart}{z}\renewcommand*{\theolchapter}{y}'
                r'\renewcommand*{\theolsection}{w}\olref{x}\ollabel{x}\endgroup')
        _,receipt=adapter(dict.fromkeys(keys,label())).prepare(source,'fixture')
        self.assertEqual([r['keys'][0] for r in receipt['calls']],[keys[1],keys[0],keys[2]])
        self.assertFalse(receipt['references_without_source_anchor'])
        for row in receipt['markers'].values():
            self.assertEqual(source[row['char_start']:row['char_end']],row['original_tex'])

    def test_chapter_heading_does_not_change_olfileid_context(self):
        labels={'a:b:c:x':label(),'z:y::chap':label('3',kind='chapter')}
        result,receipt=adapter(labels).prepare(r'\olfileid{a}{b}{c}\olchapter{z}{y}{Title}\olref{x}\ollabel{x}','fixture')
        self.assertIn(r'\chapter{Title}',result)
        self.assertEqual(receipt['calls'][0]['keys'],['a:b:c:x'])

    def test_native_pair_order_and_enum_no_type_name(self):
        labels={'later':label('2.10',counter='10'),'earlier':label('2.2',counter='2'),
                'item':label('a',kind='enumi')}
        _,receipt=adapter(labels).prepare(r'\cref{later,earlier}, \cref{item}.','fixture')
        self.assertEqual(receipt['calls'][0]['rendered_keys'],['earlier','later'])
        self.assertEqual(''.join(x['text'] for x in receipt['calls'][0]['pieces']),'Teorema 2.2 lan 2.10')
        self.assertEqual(receipt['calls'][1]['pieces'][0]['text'],'(a)')

    def test_missing_source_label_and_missing_name_are_failures(self):
        with self.assertRaisesRegex(ValueError,'absent'):
            adapter({}).prepare(r'\ref{missing}','fixture')
        with self.assertRaisesRegex(ValueError,'name missing'):
            adapter({'x':label(kind='unknown')}).prepare(r'\cref{x}','fixture')
        with self.assertRaisesRegex(ValueError,'duplicate executed'):
            adapter({'x':label()}).prepare(r'\label{x}\label{x}','fixture')

    def test_short_heading_reference_span_is_exact(self):
        source=r'\olfileid{a}{b}{c}\olsection[See \ref{x}]{Title}'
        _,receipt=adapter({'a:b:c:sec':label(kind='section'),'x':label()}).prepare(source,'fixture')
        ref=next(x for x in receipt['markers'].values() if x['kind']=='reference')
        self.assertEqual(source[ref['char_start']:ref['char_end']],r'\ref{x}')

    def test_native_label_conditionals_exclude_missing_reference_branches(self):
        source=r'\oliflabeldef{missing}{\cref{missing}}{Kept \cref{x}}\oliflabeldef{x}{ present}{}'
        _,receipt=adapter({'x':label()}).prepare(source,'fixture')
        self.assertEqual(len(receipt['calls']),1)
        self.assertEqual([x['defined'] for x in receipt['native_label_conditionals']],[False,True])

    def test_let_targets_are_not_executed_as_text_commands(self):
        source=r'\let\emph\textbf\emph{Summary}\let\emph=\textit\section*{Exercises}'
        result,receipt=adapter({}).prepare(source,'fixture')
        self.assertEqual(result,source)
        self.assertEqual(receipt['markers'],{})


@unittest.skipUnless(shutil.which('pandoc'),'Pandoc required')
class PandocReferenceTests(unittest.TestCase):
    def test_links_in_prose_and_math_restore_exact_annotations(self):
        from lxml import html
        source=r'\label{x}See \cref{x}. $a\text{ by \cref{x}}=b$. \pageref*{x}.'
        prepared,receipt=adapter({'x':label()}).prepare(source,'fixture')
        result=subprocess.run(['pandoc','-f','latex','-t','html5','--mathml'],
                              input=prepared,capture_output=True,encoding='utf-8',check=True)
        self.assertNotIn('[WARNING]',result.stderr)
        doc=html.fromstring(result.stdout)
        binding=bind_references(doc,receipt)
        self.assertEqual(binding['bound'],4)
        self.assertEqual(len(doc.xpath('//*[@id="x"]')),1)
        self.assertEqual(doc.xpath('//a[@href="#x"]/text()'),['Teorema 2.3'])
        self.assertEqual(doc.xpath('//mtext[@href="#x"]/text()'),['Teorema 2.3'])
        self.assertEqual(doc.xpath('//annotation/text()'),[r'a\text{ by \cref{x}}=b'])
        self.assertNotIn('OLPXREF',html.tostring(doc,encoding='unicode'))

    def test_bound_namespace_mathml_remains_namespaced(self):
        from lxml import etree
        _,receipt=adapter({'x':label()}).prepare(r'$\cref{x}$','fixture')
        doc=etree.fromstring(b'<math xmlns="http://www.w3.org/1998/Math/MathML"><mtext>OLPXREF000000</mtext><annotation encoding="application/x-tex">\\mbox{OLPXREF000000}</annotation></math>')
        bind_references(doc,receipt)
        self.assertEqual(doc[0].tag,'{http://www.w3.org/1998/Math/MathML}mrow')
        self.assertEqual(doc[0][0].tag,'{http://www.w3.org/1998/Math/MathML}mtext')
        self.assertEqual(doc[1].text,r'\cref{x}')
