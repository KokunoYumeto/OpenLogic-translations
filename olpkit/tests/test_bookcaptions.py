import unittest
from lxml import html
from olpkit.bookcaptions import bind_captions


class NativeCaptionTests(unittest.TestCase):
    def test_numbers_and_detached_table_anchor_preserve_caption_text(self):
        doc=html.fromstring('<div><figure><p><span id="f"/></p><figcaption>Exact <em>meaning</em>.</figcaption></figure><table><caption>Table title.</caption><tr><td>Cell</td></tr></table><p><span id="t"/></p></div>')
        labels={'f':{'kind':'figure','number_tex':'1.2'},'t':{'kind':'table','number_tex':'3.1'}}
        titles={'f':html.fromstring('<p>Exact <em>meaning</em></p>'),'t':html.fromstring('<p>Table title</p>')}
        report=bind_captions(doc,labels,titles,names={'figure':'Figure','table':'Table'},evidence={'native':'fixture'},native_aux_drops_terminal_period=True)
        self.assertEqual(len(report['captions']),2)
        self.assertEqual(doc.xpath('//figcaption/span/text()'),['Figure 1.2: '])
        self.assertEqual(doc.xpath('//table/@id'),['t'])
        self.assertEqual(doc.xpath('//figcaption/em/text()'),['meaning'])
        self.assertEqual(doc.xpath('//td/text()'),['Cell'])
    def test_changed_meaning_is_rejected_even_with_period_elision(self):
        doc=html.fromstring('<figure><span id="f"/><figcaption>Different meaning.</figcaption></figure>')
        with self.assertRaisesRegex(ValueError,'caption text differs'):
            bind_captions(doc,{'f':{'kind':'figure','number_tex':'1'}},{'f':html.fromstring('<p>Exact meaning</p>')},names={'figure':'Figure'},evidence={'native':'fixture'},native_aux_drops_terminal_period=True)
