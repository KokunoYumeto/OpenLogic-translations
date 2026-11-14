import unittest
from olpkit.bookinsertions import glossary_insertion,insert_glossary,insert_bibliography,literal_definitions,bibliography_helpers,absent_glossary,bibliography_sources


class NativeBookInsertionTests(unittest.TestCase):
    def test_absent_native_glossary_cannot_hide_glossary_content(self):
        text='Full theorem and proof.\n% '+r'\printglossaries'+'\n'+r'\newcommand{\unused}{\gls{x}}'
        receipt=absent_glossary(text)
        self.assertEqual(receipt['status'],'absent')
        for command in [r'\printglossaries',r'\gls{x}',r'\Glspl{x}',r'\newglossaryentry{x}{name=X}',r'\glsentrytext{x}']:
            with self.subTest(command=command),self.assertRaisesRegex(ValueError,'source uses glossary commands'):
                absent_glossary(text+'\n'+command)

    def test_multiple_bibliographies_preserve_exact_native_order_and_paths(self):
        book='locale/mr/courses/intermediate-logic'
        sources=['bib/open-logic.bib',book+'/il.bib']
        text='before'+r'\bibliographystyle{natbib-oup}\bibliography{\olpath/bib/open-logic,il}'+'after'
        result,receipt=insert_bibliography(text,'BOTH DATABASES',source=sources,style='bib/natbib-oup.bst',book_directory=book)
        self.assertEqual(result,'beforeBOTH DATABASESafter')
        self.assertEqual(receipt[1]['source'],sources)
        for changed in [sources[::-1],sources[:1],['bib/open-logic.bib','other/il.bib']]:
            with self.subTest(sources=changed),self.assertRaisesRegex(ValueError,'bound native input'):
                insert_bibliography(text,'BODY',source=changed,style='bib/natbib-oup.bst',book_directory=book)
        for bad in [[],sources+sources[:1],['../private.bib'],['bib/open-logic']]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):bibliography_sources(bad)

    def test_glossary_uses_native_title_and_preserves_adjacent_content(self):
        text=r'first\glsaddall\printglossary[style=index,title={शब्दसूची},toctitle={शब्दसूची}]last'
        ins=glossary_insertion(text)
        self.assertEqual(ins['title'],'शब्दसूची')
        self.assertEqual(insert_glossary(text,ins,'BODY'),'firstBODYlast')
        with self.assertRaisesRegex(ValueError,'source changed'):insert_glossary(text+'x',ins,'BODY')

    def test_plural_glossary_uses_bound_default_not_definitions_or_comments(self):
        text=r'\newcommand{\unused}{\printglossaries}'+'\n% '+r'\printglossary'+'\n'+r'\glsaddall\printglossaries'
        ins=glossary_insertion(text,'Bound title')
        self.assertEqual(ins['title'],'Bound title')
        self.assertTrue(insert_glossary(text,ins,'BODY').endswith('BODY'))
        for tail in ('',r'\printglossaries',r'\printglossary[type=other]',r'\printglossary[style=long]',r'\printglossary[title=A,toctitle=B]'):
            bad=r'\glsaddall'+tail
            if tail==r'\printglossaries':bad+=tail
            with self.subTest(tail=tail),self.assertRaises(ValueError):glossary_insertion(bad,'Title')

    def test_bibliography_native_path_spellings_preserve_database_identity(self):
        for style in ('natbib-oup',r'\olpath/bib/natbib-oup',r'\olpath/bib/natbib-oup.bst'):
            for database in (r'\olpath/bib/open-logic',r'\olpath/bib/open-logic.bib'):
                text='before'+r'\bibliographystyle{'+style+'}'+r'\bibliography{'+database+'}after'
                result,receipt=insert_bibliography(text,'BODY',source='bib/open-logic.bib',style='bib/natbib-oup.bst')
                self.assertEqual(result,'beforeBODYafter');self.assertEqual(len(receipt),2)
        for database in ('open-logic',r'\olpath/other/open-logic',r'\olpath/bib/open-logic,other'):
            with self.assertRaisesRegex(ValueError,'bound native input'):
                insert_bibliography(r'\bibliographystyle{natbib-oup}\bibliography{'+database+'}',
                                    'BODY',source='bib/open-logic.bib',style='bib/natbib-oup.bst')

    def test_control_space_in_inherited_credit_is_preserved(self):
        prefix='Cod.\\ Ms.\\\nD. Hilbert. '
        text=prefix+r'\bibliographystyle{natbib-oup}\bibliography{\olpath/bib/open-logic}'
        result,_=insert_bibliography(text,'BODY',source='bib/open-logic.bib',style='bib/natbib-oup.bst')
        self.assertEqual(result,prefix+'BODY')

    def test_localized_bibliography_helpers_are_copied_from_source(self):
        text=r'\DeclareRobustCommand{\labeland}{आणि}\DeclareRobustCommand{\labelurl}{\mbox{दुवा}}'
        self.assertEqual(literal_definitions(text,{'labeland','labelurl'}),
                         r'\newcommand{\labeland}{आणि}'+'\n'+r'\newcommand{\labelurl}{\mbox{दुवा}}')
        bbl=r'\def\natexlab#1{#1}\def\urlprefix{\labelurl\space}'
        self.assertIn(r'\newcommand{\urlprefix}{\labelurl\space}',bibliography_helpers(bbl))
        for bad in (r'\def\labeland#1{#1}',text+text,''):
            with self.subTest(bad=bad),self.assertRaises(ValueError):literal_definitions(bad,{'labeland'})
