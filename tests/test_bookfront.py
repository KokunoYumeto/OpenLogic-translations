import unittest
from olpkit.bookfront import native_frontmatter


class BookFrontTests(unittest.TestCase):
    def prepare(self,metadata_extra=''):
        cls=r'\newcommand{\OLPfrontmatter}{Title\newpage Editor, \emph{University}.\newpage Author\newpage Full licence and credits.\newpage\tableofcontents*}'
        metadata=r'\setOLPbooktitle[Cover\\Title]{Full title}\setOLPbooksubtitle{Subtitle}\setOLPauthor{Author}\setOLPbookversion{Version}{xx}\setOLPsourcelink{https://example.org/source}\setOLPauthorlink{https://example.org/author}'+metadata_extra
        locale=''.join(r'\setlocalecaption{xx}{'+key+'}{'+key+'}' for key in ['OLP','instigator','editorialboard','contributors','contents','OLT','OLTlink','license'])
        return native_frontmatter(cls,metadata,locale,r'\newcommand{\credit}{Human source credit.}',r'\OLPscreencover{\includegraphics{portrait.pdf}}',language='xx',evidence={'source':'fixture'})
    def test_native_credit_body_and_cover_variant_are_retained(self):
        text,defs,r=self.prepare()
        self.assertIn(r'Editor, \emph{University}.',text)
        self.assertIn('Full licence and credits.',text)
        self.assertIn(r'\newcommand{\OLPbooktitlecover}{Cover\\Title}',defs)
        self.assertIn('Human source credit.',defs)
        self.assertEqual(r['native_frontmatter_pages'],5)
        self.assertEqual(text.count('OLPBOOKTOC'),1)
    def test_conflicting_book_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):self.prepare(r'\setOLPauthor{Different author}')
