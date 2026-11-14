import shutil,subprocess,unittest
from olpkit.mathsource import SourceMath


FORMULAS=r'''
\def\ollatinformulas{\let\formula\relax}
\def\olgreekformulas{\gdef\formula{\lookup{A/\varphi,B/\psi}}}
\def\olalphagreekformulas{\gdef\formula{\lookup{A/\alpha,B/\beta}}}
'''
QUANTIFIERS=r'''
\olgreekformulas
\DeclareDocumentCommand\lexists{t{!} o o}{\exists\IfBooleanTF{#1}\mathexclaim\relax
 \IfNoValueTF{#2}\relax{#2}\IfNoValueTF{#3}\relax{\,#3}}
\DeclareDocumentCommand\lforall{o o}{\forall\IfNoValueTF{#1}\relax{#1}\IfNoValueTF{#2}\relax{\,#2}}
\DeclareDocumentMacro\Nat{\mathbb{N}}
'''


class SourceMathTests(unittest.TestCase):
    def converter(self):
        c=SourceMath();c.formula_library(FORMULAS,'formulas-fixture');c.configure(QUANTIFIERS,'base');return c

    def test_book_notation_wins_and_only_math_shorthand_expands(self):
        c=self.converter();c.configure(r'\ollatinformulas\DeclareDocumentMacro\Nat{\mathbf{N}}','book')
        text,receipt=c.expand(r'Text !A; $!A+\Nat$; \ensuremath{!B}','body')
        self.assertEqual(text,r'Text !A; $A+\mathbf{N}$; \ensuremath{B}')
        self.assertEqual(receipt['configured_formula_mode']['source'],'formulas-fixture')
        self.assertEqual(len(receipt['formula_shorthands']),2)
        self.assertEqual(receipt['declarations'][receipt['calls'][0]['definition']]['origin']['source'],'book')

    def test_defined_branch_requires_native_declaration_and_keeps_scope(self):
        c=self.converter();c.configure(r'\newcommand{\Known}{K}','book')
        text,receipt=c.expand(r'$\ifdefined\Known\Known+!A\else lost\fi$','body')
        self.assertEqual(text,r'$K+\varphi $')
        self.assertEqual(receipt['source_conditionals'][0]['target'],'Known')
        with self.assertRaisesRegex(ValueError,'source declaration'):
            self.converter().expand(r'\ifdefined\Unknown yes\else no\fi','unknown')
        with self.assertRaisesRegex(ValueError,'source declaration'):
            self.converter().expand(r'{\newcommand{\Local}{L}}\ifdefined\Local yes\fi','scoped')

    def test_optional_quantifiers_uniqueness_and_nested_matrix(self):
        text,_=self.converter().expand(r'$\lexists![x][\lforall[y][!A(x,y)]]$','body')
        compact=''.join(text.split())
        self.assertEqual(compact,r'$\exists\mathexclaimx\,\forally\,\varphi(x,y)$')
        self.assertNotIn('IfNoValue',text)

    def test_native_one_branch_optional_and_boolean_programs(self):
        c=self.converter()
        c.configure(r'\RenewDocumentCommand\Intro{m o}{\ensuremath{{#1}\mathrm{I}\IfValueT{#2}{_{#2}}}}'
                    r'\NewDocumentCommand\choice{s o}{\IfBooleanT{#1}{+}\IfBooleanF{#1}{-}'
                    r'\IfNoValueT{#2}{N}\IfNoValueF{#2}{V}\IfValueF{#2}{0}}','book')
        text,_=c.expand(r'$\Intro{\land}+\Intro{\lor}[2]+\choice+\choice*[x]$','body')
        self.assertEqual(text,r'$\ensuremath{{\land}\mathrm{I}}+\ensuremath{{\lor}\mathrm{I}_{2}}+-N0++V$')

    def test_intertext_returns_to_text_mode_and_restores_alignment_math(self):
        c=self.converter()
        source=r'\begin{align*}!A&=!B\\\intertext{Prose! $!A$ and \ensuremath{!B}.}!B&=!A\end{align*}'
        text,receipt=c.expand(source,'intertext')
        self.assertEqual(text,r'\begin{align*}\varphi &=\psi \\\intertext{Prose! $\varphi $ and \ensuremath{\psi }.}\psi &=\varphi \end{align*}')
        self.assertEqual(len(receipt['formula_shorthands']),6)

    def test_text_box_nested_math_does_not_invert_outer_math_mode(self):
        c=self.converter()
        text,_=c.expand(r'$!A+\textrm{Keep prose! $!B$}+!B$','nested-text')
        self.assertEqual(text,r'$\varphi +\textrm{Keep prose! $\psi $}+\psi $')

    def test_proof_formula_and_label_contexts_inside_a_display(self):
        c=self.converter()
        source=r'\[\Axiom$!A$\AxiomC{Text! $!B$}\RightLabel{Rule! $!A$}\BinaryInf$!B$\DisplayProof\]'
        text,receipt=c.expand(source,'proof')
        self.assertEqual(text,r'\[\Axiom$\varphi $\AxiomC{Text! $\psi $}\RightLabel{Rule! $\varphi $}\BinaryInf$\psi $\DisplayProof\]')
        self.assertEqual(len(receipt['formula_shorthands']),4)

    def test_proof_math_argument_nested_text_does_not_end_at_its_inline_math(self):
        c=self.converter()
        text,_=c.expand(r'\[\Axiom$!A\text{where $!B$}$\DisplayProof\]','proof-nested')
        self.assertEqual(text,r'\[\Axiom$\varphi \text{where $\psi $}$\DisplayProof\]')

    def test_negation_and_optional_assignment_from_source(self):
        c=self.converter();c.configure(r'\DeclareDocumentCommand\Sat{t{/} m m o}{'
            r'\IfNoValueTF{#4}{#2}{#2,#4}\IfBooleanTF{#1}{\nvDash}{\vDash}#3}','sat')
        text,_=c.expand(r'$\Sat/{M}{!A}[s]$','body')
        self.assertEqual(''.join(text.split()),r'$M,s\nvDash\varphi$')

    def test_comment_lines_are_not_paragraph_arguments(self):
        c=self.converter();c.configure('\\DeclareDocumentCommand\\Eq{o o}{\\IfNoValueTF{#2}\n'
            '% only a symbol\n { = }\n% two terms\n{#1=#2}}','commented')
        text,_=c.expand(r'$\Eq+\Eq[x][y]$','body')
        self.assertEqual(''.join(text.split()),'$=+x=y$')

    def test_expansion_preserves_control_sequence_token_boundaries(self):
        c=self.converter();c.configure(r'\ollatinformulas\DeclareDocumentCommand\Neg{m}{\lnot#1}'
            '\\DeclareDocumentMacro\\Commented{\\lnot%comment\n A}','boundaries')
        text,_=c.expand(r'$\lnot!A+\Neg{B}+\Commented$','body')
        self.assertEqual(text,r'$\lnot A+\lnot B+\lnot A$')
        self.assertNotIn(r'\lnotA',text);self.assertNotIn(r'\lnotB',text)

    def test_source_alphabet_style_is_explicit_and_unknown_shapes_fail(self):
        c=self.converter();c.configure(r'\DeclareMathAlphabet{\mathbi}{OT1}{pplx}{b}{it}','font')
        preamble,rows=c.font_preamble()
        self.assertEqual(preamble,r'\newcommand{\mathbi}[1]{\boldsymbol{\mathit{#1}}}')
        self.assertEqual(rows[0]['origin']['source'],'font')
        self.assertFalse(rows[0]['exact_font_face_acceptance'])
        c.configure(r'\DeclareMathAlphabet{\odd}{OT1}{pplx}{m}{sc}','unknown-font')
        with self.assertRaisesRegex(ValueError,'weight/shape'):c.font_preamble()

    def test_formula_mapping_obeys_captured_symbol_aliases(self):
        c=self.converter();c.configure(r'\let\varphi\psi','symbol-alias')
        text,_=c.expand('$!A$','body')
        self.assertEqual(''.join(text.split()),r'$\psi$')

    def test_unsupported_global_and_eager_definitions_fail(self):
        for command in ('gdef','edef','xdef'):
            with self.subTest(command=command),self.assertRaisesRegex(ValueError,'explicit support'):
                self.converter().configure('\\'+command+r'\Name{x}','global')

    def test_aliases_capture_definitions_instead_of_rebinding(self):
        c=self.converter();c.configure(r'\let\oldphi\phi\let\phi\varphi','aliases')
        text,_=c.expand(r'$\oldphi+\phi$','body')
        self.assertEqual(''.join(text.split()),r'$\phi+\varphi$')

    def test_local_scope_and_opaque_definition(self):
        c=self.converter()
        text,receipt=c.expand(r'$\Nat{\DeclareDocumentMacro\Nat{Z}\Nat}\Nat$'
            r'\newcommand{\Unused}{\Nat}','body')
        self.assertEqual(''.join(text.split()),r'$\mathbb{N}{\DeclareDocumentMacro\Nat{Z}Z}\mathbb{N}$\newcommand{\Unused}{\Nat}')
        self.assertEqual(len(receipt['calls']),3)

    def test_unbraced_branch_and_local_induction_bindings(self):
        c=self.converter();c.configure(r'\DeclareDocumentCommand\Case{s m +m}{'
            r'\DeclareDocumentMacro\caseformula{#2}\IfBooleanTF{#1}{atomic: }{general: }#3}','case')
        text,_=c.expand(r'\Case*{!A}{Inside $\caseformula$.}','body')
        self.assertIn('atomic: Inside $\\varphi ',text)
        self.assertNotIn('#',text)

    def test_first_token_style_does_not_swallow_subscripts(self):
        c=self.converter();c.configure(r'\def\applytofirst#1#2{{\expandafter#1#2}}'
            r'\DeclareDocumentCommand\Struct{m}{\applytofirst{\mathbi}{#1}}','style')
        text,_=c.expand(r'$\Struct{M_k}$','body')
        self.assertEqual(text,r'${\mathbi{M}_k}$')

    def test_default_argument_and_literal_contexts(self):
        c=self.converter();c.configure(r'\newcommand{\Pair}[2][x]{(#1,#2)}','optional')
        text,_=c.expand(r'$\Pair{y}+\Pair[z]{t}$ \verb|!A\Nat| \url{https://example/!A}','body')
        self.assertEqual(text,r'$(x,y)+(z,t)$ \verb|!A\Nat| \url{https://example/!A}')

    def test_unknown_conditional_and_recursive_definitions_fail(self):
        c=self.converter();c.configure(r'\DeclareDocumentMacro\Bad{\iftrue x\fi}','bad')
        with self.assertRaisesRegex(ValueError,'unsupported conditional'):c.expand(r'$\Bad$','body')
        c=self.converter();c.configure(r'\DeclareDocumentMacro\Loop{\Loop}','loop')
        with self.assertRaisesRegex(ValueError,'recursive'):c.expand(r'$\Loop$','body')

    @unittest.skipUnless(shutil.which('pandoc'),'Pandoc required for actual MathML check')
    def test_real_mathml_distinguishes_authored_formula_alphabets(self):
        c=self.converter();greek,_=c.expand('$!A$','greek-body')
        c.configure(r'\ollatinformulas','book');latin,_=c.expand('$!A$','latin-body')
        def render(text):return subprocess.run([shutil.which('pandoc'),'-f','latex','-t','html5','--mathml'],
            input=text,text=True,encoding='utf-8',capture_output=True,check=True,timeout=20).stdout
        self.assertIn('<mi>A</mi>',render(latin));self.assertNotIn('<mi>A</mi>',render(greek))
        self.assertIn('application/x-tex',render(latin))


if __name__=='__main__':unittest.main()
