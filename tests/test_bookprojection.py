import tempfile
from pathlib import Path
import unittest

from olpkit.assembly import digest
from olpkit.bookprojection import BookProjection


DEFER = r'\renewenvironment{probdeferredtag}[2]{\begin{probd}}{\end{probd}}'


class BookProjectionTests(unittest.TestCase):
    def fixture(self, folder, entry, contents, extra=None):
        files = {'sty/open-logic-defer.sty':DEFER, 'sty/open-logic-selective.sty':'',
                 'sty/open-logic-referencing.sty':'', 'config.tex':r'\tagtrue{p,tagTrue}\excludeenv{editorial}',
                 'locale/xx/book/book.tex':entry}
        files.update({'locale/xx/'+k:v for k,v in contents.items()})
        files.update(extra or {})
        for name,text in files.items():
            path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.encode())
        units=[{'path':p,'id':f'OLP-{n:04d}','state':'current','english_fill':False}
               for n,p in enumerate(contents,1)]
        assembly={'book_directory':'locale/xx/book','locale':'xx','units':units,
                  'files':{p:{'sha256':digest(t.encode())} for p,t in files.items()}}
        imports=[(u['id'],u['path']) for u in units]
        return assembly,imports

    def test_native_order_summaries_and_deferred_exercises(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            entry=(r'\preto\OLEndChapterHook{\IfFileExists{include/summary-\thechapter}'
                r'{\input{include/summary-\thechapter}}{}}\problemsperchapter\mainmatter'
                r'\olimport*[one]{chapter}')
            units={'content/one/chapter.tex':r'\olchapter{x}{y}{Title}\olimport{body}\OLEndChapterHook',
                'content/one/body.tex':r'\olfileid[xx]{x}{y}{z}Before\begin{prob}Exercise\end{prob}After'
                 r'\begin{editorial}hidden\end{editorial}\tagprob{notp}Keep'
                 r'\begin{prob}omitted\end{prob}Also keep\tagendprob'}
            a,imports=self.fixture(root,entry,units,{'locale/xx/book/include/summary-1.tex':'Summary'})
            text,receipt=BookProjection(root,a,imports).project('book.tex',['config.tex'])
            self.assertEqual(receipt['unique_units'],2)
            self.assertLess(text.index('Before'),text.index('After'))
            self.assertLess(text.index('After'),text.index('Summary'))
            self.assertLess(text.index('Summary'),text.index('Exercise'))
            self.assertNotIn('hidden',text); self.assertNotIn('omitted',text)
            self.assertIn('Keep',text);self.assertIn('Also keep',text)
            self.assertEqual(receipt['deferred_exercises'][0]['context'],
                             {'theolpart':'x','theolchapter':'y','theolsection':'z'})
            self.assertFalse(receipt['reader_complete'])

    def test_import_assignments_are_local_and_in_execution_order(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a,imports=self.fixture(root,r'\olimport*[one]{a}\iftag{p}{\olimport*[one]{b}}{}',{
                'content/one/a.tex':r'\tagfalse{p}\iftag{p}{wrong}{first}',
                'content/one/b.tex':r'\iftag{p}{second}{wrong}'})
            text,receipt=BookProjection(root,a,imports).project('book.tex',['config.tex'])
            self.assertNotIn('wrong',text)
            self.assertLess(text.index('first'),text.index('second'))
            self.assertEqual([r['path'] for r in receipt['unit_order']],list(a['units'][n]['path'] for n in range(2)))

    def test_unit_anchors_follow_nested_execution_without_changing_source(self):
        import re
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a,imports=self.fixture(root,r'\olimport*[one]{a}',{
                'content/one/a.tex':r'Before\olimport{b}After',
                'content/one/b.tex':r'Nested $x^2$.'})
            plain,_=BookProjection(root,a,imports).project('book.tex',['config.tex'])
            marked,receipt=BookProjection(root,a,imports,mark_units=True).project('book.tex',['config.tex'])
            ids=re.findall(r'\\hypertarget\{(olp-unit-\d+)\}\{\}',marked)
            self.assertEqual(ids,[r['html_id'] for r in receipt['unit_order']])
            self.assertEqual(ids,['olp-unit-000001','olp-unit-000002'])
            self.assertEqual(re.sub(r'\\hypertarget\{olp-unit-\d+\}\{\}','',marked),plain)

    def test_probtag_matches_native_discarded_argument(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a,imports=self.fixture(root,r'\problemsperchapter\mainmatter\olimport*[one]{a}',{
                'content/one/a.tex':r'\olchapter{x}{y}{Title}\begin{probtag}{notp}Kept by native style'
                                    r'\end{probtag}\OLEndChapterHook'})
            text,receipt=BookProjection(root,a,imports).project('book.tex',['config.tex'])
            self.assertIn('Kept by native style',text)
            self.assertEqual(receipt['deferred_exercises'][0]['native_ignored_probtag_argument'],'notp')

    def test_changed_missing_out_of_scope_and_english_inputs_fail(self):
        for case in ('changed','missing','outside_lock','english','missing_lock_member'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                root=Path(td)
                a,imports=self.fixture(root,r'\olimport*[one]{a}',{'content/one/a.tex':'Text'})
                path=root/'locale/xx/content/one/a.tex'
                if case=='changed': path.write_text('Changed',encoding='utf-8')
                if case=='missing': path.unlink()
                if case=='outside_lock': imports=[]
                if case=='english': a['units'][0]['english_fill']=True
                if case=='missing_lock_member': imports.append(('OLP-0002','content/one/b.tex'))
                with self.assertRaises(ValueError): BookProjection(root,a,imports).project('book.tex',['config.tex'])

    def test_unflushed_exercise_is_a_failure_not_an_omission(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a,imports=self.fixture(root,r'\problemsperchapter\mainmatter\olimport*[one]{a}',{
                'content/one/a.tex':r'\olchapter{x}{y}{Title}\begin{prob}Exercise\end{prob}'})
            with self.assertRaisesRegex(ValueError,'unflushed'):
                BookProjection(root,a,imports).project('book.tex',['config.tex'])

    def test_import_expansion_preserves_control_word_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            entry=r'\let\emph\textbf\input{summary}\input{last}x'
            a,imports=self.fixture(root,entry,{},
                {'locale/xx/book/summary.tex':'Gedhene', 'locale/xx/book/last.tex':r'\alpha'})
            text,_=BookProjection(root,a,imports).project('book.tex',['config.tex'])
            self.assertEqual(text,r'\let\emph\textbf Gedhene\alpha x')


if __name__ == '__main__': unittest.main()
