import unittest
from lxml import html
from olpkit.bookheadings import read_contents,bind_headings


class NativeHeadingTests(unittest.TestCase):
    def test_native_decimal_numbering_is_preserved_in_contents(self):
        rows=read_contents(r'\contentsline{chapter}{\chapternumberline{१}प्रकरण}{१}{ch}',language_wrapper='bbl@ensure@marathi')
        self.assertEqual(rows[0]['number'],'१')

    def rows(self):
        text='\n'.join([r'\contentsline{chapter}{Preface}{i}{pre}',
                        r'\contentsline{part}{\partnumberline{I}Part}{1}{part}',
                        r'\contentsline{chapter}{\chapternumberline{1}Chapter}{2}{ch}',
                        r'\contentsline{section}{\bbl@ensure@xx{Exercises}}{3}{ex}',
                        r'\contentsline{paragraph}{Reading}{4}{read}'])
        return read_contents(text,language_wrapper='bbl@ensure@xx')
    def bind(self,doc):
        rows=self.rows();titles=[html.fromstring('<p>'+r['title_tex']+'</p>') for r in rows]
        return bind_headings(doc,rows,titles,reading_title='Reading',problems_title='Exercises',contents_title='Contents',evidence={'native':'fixture'})
    def test_complete_order_numbers_and_native_generated_headings(self):
        doc=html.fromstring('<div><div class="olpbooktoc">OLPBOOKTOC</div><h2 id="pre">Preface</h2><h1 id="part">Part</h1><h2 id="ch">Chapter</h2><h3 id="ex"></h3><div class="reading"><p>Original bibliography.</p></div></div>')
        report=self.bind(doc)
        self.assertEqual(len(report['headings']),5)
        self.assertEqual(doc.xpath('//h2[@id="ch"]/span/text()'),['1 '])
        self.assertEqual(doc.xpath('//h3/text()'),['Exercises'])
        self.assertEqual(doc.xpath('//nav/ol/li/a/@href'),['#pre','#part'])
        self.assertEqual(doc.xpath('//nav/ol/li[2]/ol/li/a/@href'),['#ch'])
        self.assertEqual(doc.xpath('//nav//a/@href'),['#pre','#part','#ch','#ex','#olp-reading-1'])
        self.assertIn('Original bibliography.',doc.text_content())
    def test_changed_title_is_not_silently_replaced(self):
        doc=html.fromstring('<div><div class="olpbooktoc"/><h2 id="pre">Changed meaning</h2><h1 id="part">Part</h1><h2 id="ch">Chapter</h2><h3 id="ex"/><div class="reading"/></div>')
        with self.assertRaisesRegex(ValueError,'title differs'):self.bind(doc)
    def test_incomplete_native_contents_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'missing/duplicated'):read_contents('')
