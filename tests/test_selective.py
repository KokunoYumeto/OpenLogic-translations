import unittest

from olpkit.selective import SelectionState, Selector


class SelectionTests(unittest.TestCase):
    def run_source(self, text, **tags):
        state = SelectionState(tags)
        selector = Selector()
        return selector.project(text, state), state, selector

    def test_book_overrides_and_complement_not_plain_toggle(self):
        text, state, _ = self.run_source(r'\tagtrue{p}\tagfalse{p}\toggletrue{p}'
                                        r'\iftag{p}{yes}{no}\iftag{notp}{still}{changed}')
        self.assertEqual(text, 'yesstill')
        self.assertEqual(state.tags, {'p':True, 'notp':True})

    def test_braced_environment_and_explicit_scopes(self):
        text, _, _ = self.run_source(r'\tagtrue{p}{\tagfalse{p}\iftag{p}{x}{a}}'
            r'\begin{proof}\tagfalse{p}\iftag{p}{x}{b}\end{proof}'
            r'\begingroup\tagfalse{p}\iftag{p}{x}{c}\endgroup\iftag{p}{d}{x}')
        self.assertEqual(text, r'{a}\begin{proof}b\end{proof}\begingroup c\endgroup d'.replace(' ',''))

    def test_unbraced_branch_consumes_following_arguments(self):
        text, _, selector = self.run_source(r'\iftag{p}\iftag\relax{q}{selected}{wrong}', p=True, q=True)
        self.assertEqual(text, 'selected')
        self.assertEqual(len(selector.events), 2)
        self.assertEqual(selector.events[0]['char_start'], 0)

    def test_native_empty_line_is_the_third_argument(self):
        # Actual main-operator.tex leaves a blank line after the true branch.
        source = r'\iftag{p}{chosen}' + '\n\n' + r'\begin{table}kept\end{table}'
        text, _, _ = self.run_source(source, p=True)
        self.assertEqual(text, r'chosen\begin{table}kept\end{table}')
        text, _, _ = self.run_source(source, p=False)
        self.assertEqual(text, r'\par\begin{table}kept\end{table}')

    def test_definitions_comments_and_verbatim_are_not_execution(self):
        source = ('% '+r'\tagfalse{p}'+'\n'+r'\newcommand{\Future}{\tagfalse{p}}'
                  r'\def\FutureB#1{\tagfalse{p}}\verb|\tagfalse{p}|\iftag{p}{yes}{no}')
        text, state, _ = self.run_source(source, p=True)
        self.assertTrue(text.endswith('yes'))
        self.assertTrue(state.tags['p'])
        self.assertIn(r'\newcommand{\Future}{\tagfalse{p}}', text)

    def test_tagprob_keeps_prose_and_other_environments(self):
        text, _, _ = self.run_source(r'\tagprob{p}before\begin{prob}hidden\end{prob}'
            r'\begin{proof}visible\end{proof}after\tagendprob\begin{prob}kept\end{prob}',
            p=False, tagTrue=True)
        self.assertEqual(text, r'before\begin{proof}visible\end{proof}after\begin{prob}kept\end{prob}')

    def test_tagblock_and_nested_enumerations(self):
        text, _, _ = self.run_source(r'\begin{tagblock}{p}hidden\end{tagblock}'
            r'\begin{tagenumerate}{p,q}\tagitem{q}{outer}{}'
            r'\begin{tagenumerate}{q,r}\tagitem{q}{a}{}\tagitem{r}{b}{}'
            r'\end{tagenumerate}\end{tagenumerate}', p=False,q=True,r=True)
        self.assertNotIn('hidden',text)
        self.assertEqual(text, r'{outer\begin{enumerate}\item a\item b\end{enumerate}}')

    def test_excluded_editorial_is_not_reader_content(self):
        text, _, _ = self.run_source(r'\excludeenv{editorial}\begin{editorial}private\end{editorial}'
                                    r'\includeenv{editorial}\begin{editorial}permitted\end{editorial}')
        self.assertEqual(text, r'\begin{editorial}permitted\end{editorial}')

    def test_unknown_tags_and_truncated_scopes_fail(self):
        for source in (r'\iftag{missing}{x}{y}',r'\begin{tagblock}{missing}x\end{tagblock}',
                       r'\tagprob{missing}x\tagendprob',r'\tagendprob',r'\begin{proof}x',
                       r'\begingroup x',r'{x',r'\toggletrue{missing}'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.run_source(source, tagTrue=True)

    def test_primitive_conditions_are_retained_not_guessed(self):
        source=r'\ifodd\value{page}\stepcounter{page}\fi'
        text,_,_=self.run_source(source)
        self.assertEqual(text,source)
        with self.assertRaisesRegex(ValueError,'unevaluated primitive'):
            self.run_source(r'\ifdefined\unknown\tagtrue{p}\fi')

    def test_import_callback_observes_position_not_final_assignments(self):
        observed=[]
        def handler(name,text,pos,state,source):
            if name=='load':
                observed.append(state.tags['p']); return ('loaded',pos)
        selector=Selector(handler)
        text=selector.project(r'\tagtrue{p}\load\tagfalse{p}\load',SelectionState())
        self.assertEqual(observed,[True,False]); self.assertEqual(text,'loadedloaded')


if __name__ == '__main__': unittest.main()
