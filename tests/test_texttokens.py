import unittest

from olpkit.texttokens import TextTokens


CORE = r'''
\def\tokenformat#1{#1}
\DeclareDocumentCommand\settexttoken{m s m m o o}{
 \definetoken{s}{#1}{#3}\definetoken{p}{#1}{#4}
 \IfBooleanTF{#2}{\definetoken{a}{#1}{an}\definetoken{A}{#1}{An}}
                 {\definetoken{a}{#1}{a}\definetoken{A}{#1}{A}}
 \IfNoValueTF{#5}{\definetokenuc{S}{#1}{#3}}{\definetoken{S}{#1}{#5}}
 \IfNoValueTF{#6}{\definetokenuc{P}{#1}{#4}}{\definetoken{P}{#1}{#6}}
}
\DeclareDocumentCommand\@printtoken{t^ ta m !ts}{
 \IfBooleanTF{#1}{
   \IfBooleanTF{#2}{\Article{#3}~\IfBooleanTF{#4}{\printtoken{p}{#3}}{\printtoken{s}{#3}}}
                   {\IfBooleanTF{#4}{\printtoken{P}{#3}}{\printtoken{S}{#3}}}}
                 {\IfBooleanTF{#2}{\article{#3}~}{}
                   \IfBooleanTF{#4}{\printtoken{p}{#3}}{\printtoken{s}{#3}}}
}
'''


class TextTokenTests(unittest.TestCase):
    def catalog(self):
        c=TextTokens();c.configure(CORE,'core-fixture')
        c.configure(r'\settexttoken{object}*{object}{objects}','base')
        return c

    def test_source_forms_articles_and_adjacent_suffixes(self):
        text,receipt=self.catalog().expand(
            r'!!{object}|!!{object}s|!!^{object}|!!^{object}s|!!a{object}|!!^a{object}s|!!{object} s|!!{object}d')
        self.assertEqual(text,'object|objects|Object|Objects|an~object|An~objects|object s|objectd')
        self.assertEqual(len(receipt['occurrences']),8)
        self.assertTrue(all(x['definition_ids'] for x in receipt['occurrences']))

    def test_source_order_helpers_and_book_override(self):
        c=self.catalog()
        c.configure(r'\definetoken{s}{object}{before}\settexttoken{object}{after}{afters}'
                    r'\newcommand{\NoArticle}[1]{\definetoken{a}{#1}{}\definetoken{A}{#1}{}}'
                    r'\forcsvlist{\NoArticle}{object}', 'book')
        text,receipt=c.expand(r'!!^a{object}')
        self.assertEqual(text,'~after')  # Native source retains the separator, even for an empty article.
        used=[receipt['definitions'][i] for i in receipt['occurrences'][0]['definition_ids']]
        self.assertEqual({r['provenance'][0]['source'] for r in used},{'book'})
        self.assertTrue(any(r['provenance'][0]['char_start']>0 for r in used))

    def test_local_scope_and_unused_helper_are_not_global_definitions(self):
        c=self.catalog()
        text,_=c.expand(r'!!{object}{\definetoken{s}{object}{local}!!{object}}!!{object}'
                       r'\begingroup\definetoken{s}{object}{group}!!{object}\endgroup!!{object}'
                       r'\newcommand{\Unused}{\definetoken{s}{object}{wrong}}!!{object}')
        self.assertTrue(text.startswith('object{local}object\\begingroupgroup\\endgroupobject'))
        self.assertTrue(text.endswith('!!{object}') is False)
        self.assertTrue(text.endswith('object'))

    def test_passive_suffix_is_source_defined(self):
        c=self.catalog()
        c.configure(r'\definetoken{d}{object}{passive}\definetoken{D}{object}{Passive}'
                    r'\RenewDocumentCommand\@printtoken{t^ ta m !ts !td}{'
                    r'\IfBooleanTF{#5}{\IfBooleanTF{#1}{\printtoken{D}{#3}}{\printtoken{d}{#3}}}'
                    r'{\printtoken{s}{#3}}}', 'passive-policy')
        text,_=c.expand(r'!!{object}d|!!^{object}d|!!{object} d')
        self.assertEqual(text,'passive|Passive|object d')

    def test_explicit_forms_unicode_and_math_are_preserved(self):
        c=self.catalog()
        c.configure(r'\settexttoken{object}{élan}{$\alpha$}[EXPLICIT][MATH]','override')
        text,_=c.expand(r'!!^{object}|!!{object}s|!!^{object}s')
        self.assertEqual(text,r'EXPLICIT|$\alpha$|MATH')
        c.configure(r'\settexttoken{macro}{\alpha value}{plain}','macro-form')
        self.assertEqual(c.expand(r'!!^{macro}','macro-body')[0],r'\alpha value')

    def test_comments_verbatim_and_definitions_are_not_occurrences(self):
        c=self.catalog()
        text,receipt=c.expand('% !!{unknown}\n'+r'\verb|!!{unknown}|'
            r'\begin{verbatim}!!{unknown}\end{verbatim}'
            r'\newcommand{\NotInvoked}{!!{unknown}} !!{object}')
        self.assertEqual(len(receipt['occurrences']),1)
        self.assertIn(r'\verb|!!{unknown}|',text)
        self.assertIn(r'\newcommand{\NotInvoked}{!!{unknown}}',text)

    def test_literal_url_and_path_are_preserved(self):
        text=r'\url{https://example.org/!!{x}}\path{folder/!!{x}}'
        output,receipt=self.catalog().expand(text)
        self.assertEqual(output,text)
        self.assertEqual(receipt['occurrences'],[])

    def test_adjacent_plural_and_passive_flags_follow_authored_spec(self):
        c=self.catalog()
        c.configure(r'\DeclareDocumentCommand\@printtoken{t^ ta m ts}{'
                    r'\IfBooleanTF{#4}{\printtoken{p}{#3}}{\printtoken{s}{#3}}}', 'old-xparse')
        self.assertEqual(c.expand('!!{object}\n s')[0],'objects')

    def test_definition_locator_is_exact_and_input_bound(self):
        c=self.catalog(); source='% not a definition\n'+r'\definetoken{s}{object}{replacement}'
        c.configure(source,'exact')
        _,receipt=c.expand(r'\usetoken{s}{object}')
        row=receipt['definitions'][receipt['occurrences'][0]['definition_ids'][0]]
        location=row['provenance'][0]
        self.assertEqual(location['source'],'exact')
        self.assertEqual(location['line'],2)
        self.assertEqual(source[location['char_start']:location['char_end']],
                         r'\definetoken{s}{object}{replacement}')

    def test_unknown_formatting_is_not_silently_mangled(self):
        c=self.catalog();c.configure(r'\def\tokenformat#1{prefix #1 suffix}','format')
        with self.assertRaisesRegex(ValueError,'explicit support'):c.expand(r'!!{object}')

    def test_native_article_existence_check_and_global_assignment_fail_closed(self):
        c=self.catalog();c.configure(r'\definetoken{A}{partial}{Upper}','partial')
        with self.assertRaisesRegex(ValueError,'existence-test'):c.expand(r'\Article{partial}')
        with self.assertRaisesRegex(ValueError,'global token helper'):
            c.configure(r'\gdef\GlobalHelper#1{\definetoken{s}{#1}{changed}}','global')

    def test_missing_forms_and_unresolved_execution_fail(self):
        for value in (r'!!{missing}',r'\usetoken{d}{object}',
                      r'\iftrue!!{object}\fi'):
            with self.subTest(value=value),self.assertRaises(ValueError):self.catalog().expand(value)
        with self.assertRaisesRegex(ValueError,'unhandled'):
            self.catalog().configure(r'\AtBeginDocument{\definetoken{s}{object}{later}}','pending')
        with self.assertRaisesRegex(ValueError,'primitive override'):
            self.catalog().configure(r'\def\article#1{different}','override')
        with self.assertRaisesRegex(ValueError,'unreviewed'):
            self.catalog().configure_native(CORE,'fake-native')

    def test_inputs_are_ordered_and_cycle_or_mutation_fails(self):
        c=self.catalog()
        c.resolver=lambda value,source:(value,r'\definetoken{s}{object}{included}')
        c.configure(r'\input{terms}\definetoken{s}{object}{last}','with-input')
        self.assertEqual(c.expand(r'!!{object}')[0],'last')
        with self.assertRaisesRegex(ValueError,'changed'):c.configure('different','terms')
        c.resolver=lambda value,source:(value,r'\input{cycle}')
        with self.assertRaisesRegex(ValueError,'recursive'):c.configure(r'\input{cycle}','cycle')


if __name__=='__main__':unittest.main()
