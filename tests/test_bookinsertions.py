import unittest
from olpkit.bookinsertions import glossary_insertion,insert_glossary,insert_bibliography,literal_definitions,bibliography_helpers


class NativeBookInsertionTests(unittest.TestCase):
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
