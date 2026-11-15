import unittest
from olpkit.htmlpackage import reader_html


class ReaderHTMLTests(unittest.TestCase):
    def fixture(self):
        data=b'<div><div id="credits">Exact inherited credit.</div><nav class="olp-book-contents"><ol><li><a href="#title">Contents entry</a></li></ol></nav><span id="olp-unit-000001"></span><h2 id="title">Title</h2><p>Exact meaning.</p></div>'
        profile={'language':'xx','direction':'ltr','title':'Title','css':'body{color:black}','required_credit_ids':['credits']}
        units=[{'html_id':'olp-unit-000001','unit':'OLP-0010','sha256':'a'*64}]
        return data,profile,units

    def test_preserves_source_and_sets_language_without_visible_admin_text(self):
        data,profile,units=self.fixture();out,r=reader_html(data,profile,units,{})
        self.assertIn(b'<html lang="xx" dir="ltr">',out)
        self.assertIn(b'Exact inherited credit.',out)
        self.assertIn(b'data-unit-id="OLP-0010"',out)
        self.assertTrue(r['text_preserved']);self.assertFalse(r['release_ready'])

    def test_missing_import_or_credit_cannot_pass(self):
        data,profile,units=self.fixture()
        with self.assertRaisesRegex(ValueError,'import order'):
            reader_html(data.replace(b'olp-unit-000001',b'wrong'),profile,units,{})
        with self.assertRaisesRegex(ValueError,'credit block'):
            reader_html(data.replace(b'Exact inherited credit.',b''),profile,units,{})

    def test_percent_encoded_non_ascii_heading_links_resolve(self):
        data,profile,units=self.fixture()
        data=data.replace(b'id="title"','id="dosèn"'.encode()).replace(b'href="#title"',b'href="#dos%C3%A8n"')
        out,_=reader_html(data,profile,units,{})
        self.assertIn(b'#dos%C3%A8n',out)
