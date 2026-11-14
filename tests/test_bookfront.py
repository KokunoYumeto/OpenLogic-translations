import unittest
from olpkit.bookfront import native_frontmatter,native_cover_width


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

    def test_literal_native_cover_does_not_require_another_languages_helper(self):
        picture=r'\includegraphics[width=.29\textwidth]{\olpath/assets/portraits/a.pdf}'
        driver=r'\newcommand{\unused}{\OLPscreencover{ignored}}\OLPscreencover{'+picture*5+'}'
        width,record=native_cover_width(driver,{'config.tex':r'\newcommand{\other}{x}'})
        self.assertEqual(width,29)
        self.assertEqual(len(record['portraits']),5)
        self.assertEqual(record['definitions'],{})

    def test_native_helper_width_is_bound_to_its_exact_declaration(self):
        driver=r'\OLPscreencover{\includegraphics[width=\nativeWidth\textwidth]{assets/portraits/a.pdf}}'
        config=r'\newcommand*{\nativeWidth}{0.245}'
        width,record=native_cover_width(driver,{'config.tex':config})
        self.assertEqual(width,24.5)
        self.assertEqual(record['definitions']['nativeWidth'],r'\newcommand{\nativeWidth}{0.245}')
        with self.assertRaisesRegex(ValueError,'missing'):
            native_cover_width(driver,{'config.tex':''})
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            native_cover_width(driver,{'config.tex':config+config})

    def test_different_portrait_widths_are_not_silently_equalized(self):
        driver=r'\OLPscreencover{\includegraphics[width=.29\textwidth]{assets/portraits/a.pdf}\includegraphics[width=.2\textwidth]{assets/portraits/b.pdf}}'
        with self.assertRaisesRegex(ValueError,'differing'):
            native_cover_width(driver,{})

    def test_unsupported_dimension_is_not_guessed(self):
        for dim in ('2cm',r'\dimexpr.3\textwidth-1pt',r'1.5\textwidth'):
            with self.subTest(dim=dim), self.assertRaisesRegex(ValueError,'width'):
                native_cover_width(r'\OLPscreencover{\includegraphics[width='+dim+r']{assets/portraits/a.pdf}}',{})
