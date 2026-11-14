import unittest
from olpkit.glossary import read_entries,native_order,glossary_tex,expand_links,bind_glossary


DEFINITION=r'\newglossaryentry{#2}{sort={#3},name={#4},plural={#4},symbol={#1},description={#5}}'


class GlossaryTests(unittest.TestCase):
    def test_native_mapping_order_and_all_definition_text(self):
        source=r'\slcterm[\ensuremath{A\subseteq B}]{set}{himpunan}{himpunan}{Definition, with $A$.}\slcterm{rel}{relasi}{relasi}{See \glspl{set}.}'
        entries=read_entries(source,slcterm_definition=DEFINITION)
        order=native_order(r'\glossentry{rel}{}\glossentry{set}{}')
        text,receipt=glossary_tex(entries,order,'Glosarium',evidence={'native':'checked'})
        self.assertLess(text.index('relasi'),text.index('himpunan'))
        self.assertIn(r'\ensuremath{A\subseteq B}',text)
        self.assertIn('Definition, with $A$.',text)
        self.assertEqual(len(receipt['links']),1)
        self.assertIn(r'\hyperlink{'+entries['set']['anchor']+'}{himpunan}',text)

    def test_standard_entry_balanced_fields(self):
        entries=read_entries(r'\newglossaryentry{x}{name={X},plural={Xes},description={Nested {a,b}, plus $x$.},symbol={\ensuremath{x}}}')
        self.assertEqual(entries['x']['description'],r'Nested {a,b}, plus $x$.')
        self.assertIn('{Xes}',expand_links(r'\glspl{x}',entries)[0])

    def test_native_link_text_can_differ_from_glossary_heading(self):
        entries=read_entries(r'\newglossaryentry{x}{name={प्रांत (फलनाचा)},text={प्रांत},description={Definition.}}')
        value,links=expand_links(r'\gls{x}',entries)
        self.assertEqual(links[0]['label_tex'],'प्रांत')
        text,receipt=glossary_tex(entries,['x'],'Title',evidence={'native':'fixture'})
        self.assertIn('प्रांत (फलनाचा)',text)
        self.assertEqual(receipt['entries']['x']['text'],'प्रांत')

    def test_missing_plural_is_not_an_english_guess(self):
        entries=read_entries(r'\newglossaryentry{x}{name={X},description={Definition.}}')
        with self.assertRaisesRegex(ValueError,'plural'):expand_links(r'\glspl{x}',entries)

    def test_native_coverage_and_definition_changes_fail(self):
        with self.assertRaisesRegex(ValueError,'mapping'):
            read_entries(r'\slcterm{x}{x}{X}{Def}',slcterm_definition=DEFINITION.replace('plural={#4}','plural={#3}'))
        entries=read_entries(r'\slcterm{x}{x}{X}{Def}',slcterm_definition=DEFINITION)
        with self.assertRaisesRegex(ValueError,'coverage'):glossary_tex(entries,['y'],'Title',evidence={'a':1})
        with self.assertRaisesRegex(ValueError,'duplicate'):native_order(r'\glossentry{x}{}\glossentry{x}{}')

    def test_unknown_commands_references_and_fields_fail(self):
        with self.assertRaisesRegex(ValueError,'statement'):read_entries(r'\input{external}')
        entries=read_entries(r'\newglossaryentry{x}{name={X},description={Definition.}}')
        with self.assertRaisesRegex(ValueError,'unknown'):expand_links(r'\gls{missing}',entries)
        with self.assertRaisesRegex(ValueError,'sentence-case'):expand_links(r'\Gls{x}',entries)
        with self.assertRaisesRegex(ValueError,'unsupported glossary access'):expand_links(r'\glssymbol{x}',entries)
        with self.assertRaisesRegex(ValueError,'fields'):read_entries(r'\newglossaryentry{x}{name={X},description={D},parent={z}}')

    def test_sentence_case_preserves_the_rest_of_the_authored_name(self):
        entries=read_entries(r'\newglossaryentry{x}{name={fungsi M},description={D}}')
        value,rows=expand_links(r'\Gls{x}',entries,sentence_case=lambda s:s[0].upper()+s[1:])
        self.assertIn('{Fungsi M}',value)
        self.assertEqual(rows[0]['label_tex'],'Fungsi M')

    def rendered_fixture(self):
        from lxml import html
        entries=read_entries(r'\slcterm{x}{x}{X}{Def.}\slcterm{y}{y}{Y}{See \gls{x}.}',slcterm_definition=DEFINITION)
        _,receipt=glossary_tex(entries,['x','y'],'Glossary',evidence={'fixture':True})
        x,y=[entries[k]['anchor'] for k in ['x','y']]
        doc=html.fromstring(f'<dl><dt>X</dt><dd><div id="{x}"></div>\n<p>Def.</p></dd><dt>Y</dt><dd><div id="{y}"></div>\n<p>See <a href="#{x}">X</a>.</p></dd></dl>')
        return doc,receipt

    def test_complete_dom_binding_keeps_text_and_moves_targets_to_terms(self):
        doc,receipt=self.rendered_fixture()
        before=''.join(doc.itertext()).split()
        report=bind_glossary(doc,receipt)
        self.assertEqual(report['entries'],2)
        self.assertEqual(report['links'],1)
        self.assertEqual(len(doc.xpath('./dt[@id]')),2)
        self.assertEqual(''.join(doc.itertext()).split(),before)

    def test_missing_definition_or_cross_reference_fails_before_binding(self):
        doc,receipt=self.rendered_fixture()
        doc.xpath('.//a')[0].set('href','#other')
        with self.assertRaisesRegex(ValueError,'cross-reference'):bind_glossary(doc,receipt)
        self.assertFalse(doc.xpath('./dt[@id]'))
        doc,receipt=self.rendered_fixture()
        doc.remove(doc[-1])
        with self.assertRaisesRegex(ValueError,'coverage'):bind_glossary(doc,receipt)


if __name__=='__main__':unittest.main()
