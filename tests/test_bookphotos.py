import unittest,shutil,subprocess,hashlib
from lxml import html
from olpkit.bookphotos import prepare_photos,credit_rows,bind_photos


class BookPhotoTests(unittest.TestCase):
    def prepare(self,credit='Credit with '+r'\href{https://example.org}{original attribution}.',native_credit=None):
        text=r'Before \olphoto{example-person}{Example Person} after.\photocredits'
        labels={'photo-example-person':{'kind':'figure','number_tex':'C.1','page':'8'}}
        pcr='Example Person, '+r'\cpageref {photo-example-person}: '+(credit if native_credit is None else native_credit)+r'\par'
        read=lambda name:credit.encode() if name.endswith('.tex') else b'\x89PNG\r\n\x1a\nfixture'
        return prepare_photos(text,labels,pcr,read=read,localized_credit_directory='locale/xx/photocredits',figure_label='Figure',credits_title='Photo credits',page_label='page',width_percent=45,evidence={'native':'fixture'})

    def test_exact_credit_caption_asset_and_native_number_are_preserved(self):
        text,r=self.prepare()
        self.assertIn('Figure C.1: Example Person',text)
        self.assertIn(r'\href{https://example.org}{original attribution}',text)
        self.assertIn(r'page~\pageref{photo-example-person}',text)
        self.assertEqual(r['photos'][0]['asset_sha256'],hashlib.sha256(b'\x89PNG\r\n\x1a\nfixture').hexdigest())

    def test_duplicate_or_missing_native_credits_fail(self):
        row=r'Person, \cpageref{photo-x}: Credit.\par'
        with self.assertRaisesRegex(ValueError,'duplicate'):credit_rows(row+'\n'+row)
        with self.assertRaisesRegex(ValueError,'page reference'):credit_rows('Credit without photo identity.')

    def test_native_glyph_expansion_does_not_allow_credit_word_changes(self):
        text,r=self.prepare(r'\copyright{} Owner. Restricted use.',r'\textcircled {C}{} Owner. Restricted use.')
        self.assertIn(r'\copyright{} Owner. Restricted use.',text)
        with self.assertRaisesRegex(ValueError,'credit differs'):
            self.prepare('Owner. Restricted use.','Owner. Unrestricted use.')

    @unittest.skipUnless(shutil.which('pandoc'),'Pandoc required')
    def test_rendered_photo_and_complete_credit_remain_connected(self):
        text,r=self.prepare()
        text=text.replace(r'\label{photo-example-person}',r'\hypertarget{photo-example-person}{}').replace(r'\pageref{photo-example-person}',r'\hyperlink{photo-example-person}{8}')
        run=subprocess.run(['pandoc','-f','latex','-t','html5'],input=text,text=True,encoding='utf-8',capture_output=True,check=True)
        self.assertFalse(run.stderr)
        doc=html.fromstring(run.stdout);report=bind_photos(doc,r)
        self.assertEqual(report['photographs'],1)
        self.assertEqual(doc.xpath('//figure//img/@alt'),['Example Person'])
        self.assertEqual(len(doc.xpath('//figure/figcaption')),1)


if __name__=='__main__':unittest.main()
