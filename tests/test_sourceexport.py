import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from olpkit.assembly import digest, json_bytes
from olpkit.recorder import input_hashes, read_inputs
from olpkit.sourceexport import (book_name, code_lines, cumulative, deterministic_zip,
                                embed, retarget_book_inputs, retarget_imports, source_package)
from olpkit.schemas import ROOT


class SourceExportTests(unittest.TestCase):
    def test_conditional_missing_import_is_preserved_as_error_not_omitted(self):
        excluded=set();modules={'content/a/one.tex':'one.tex'}
        text=r'\iftag{x}{\olimport{one}[chapter]}{\olimport{other}}'
        changed=retarget_imports(text,'content/a/a.tex',modules,excluded)
        self.assertEqual(changed,r'\iftag{x}{\olpkitEmbeddedImport{one.tex}[chapter]}{\olpkitMissingImport{content/a/other.tex}}')
        self.assertEqual(excluded,{('content/a/a.tex','content/a/other.tex')})

    def test_comments_and_escaped_percent_remain_exact(self):
        text='\\% \\olimport{one}% \\olimport{wrong}\n\\\\% \\olimport{wrong}\n'
        result=retarget_imports(text,'content/a.tex',{'content/one.tex':'one.tex'},set())
        self.assertEqual(result,'\\% \\olpkitEmbeddedImport{one.tex}% \\olimport{wrong}\n\\\\% \\olimport{wrong}\n')

    def test_starred_and_about_imports_keep_source_identity(self):
        names={'content/a/one.tex':'one.tex','content/open-logic-about.tex':'about.tex'}
        text=r'\olimport*[a]{one}\olimport*{\olpath/locale/\ollangid/content/open-logic-about}'
        self.assertEqual(retarget_imports(text,'',names,set()),r'\olpkitEmbeddedImport{one.tex}\olpkitEmbeddedImport{about.tex}')
        with self.assertRaisesRegex(ValueError,'escapes|unsafe'):
            retarget_imports(r'\olimport*[../../]{secret}','',names,set())

    def test_dynamic_summaries_and_glossary_are_both_embedded(self):
        names={p:book_name(p) for p in ['include/summary-1.tex','include/summary-2.tex','include/glossary.tex']}
        text=r'\IfFileExists{include/summary-\thechapter}{\input{include/summary-\thechapter}}{}\loadglsentries{include/glossary}'
        out=retarget_book_inputs(text,names)
        self.assertEqual(out.count(r'olpkit-book-include-summary-\thechapter.tex'),2)
        self.assertIn('{olpkit-book-include-glossary.tex}',out)
        with self.assertRaisesRegex(ValueError,'not embedded'):
            retarget_book_inputs(r'\input{include/forgotten}',names)

    def test_embed_does_not_expand_formula_or_rewrite_whitespace(self):
        original='  $\\forall x\\,P(x)$\n\n'
        result=embed('unit.tex',original)
        self.assertIn(original,result)
        with self.assertRaises(ValueError):embed('unit.tex',r'\end{filecontents*}')

    def test_zip_is_deterministic_and_rejects_unsafe_paths(self):
        one={'b.txt':b'b','a.tex':b'formula'};two=dict(reversed(list(one.items())))
        self.assertEqual(deterministic_zip(one),deterministic_zip(two))
        with ZipFile(io.BytesIO(deterministic_zip(one))) as z:
            self.assertEqual(z.read('a.tex'),b'formula');self.assertIsNone(z.testzip())
        for unsafe in [{'../secret':b'x'},{'a.tex':b'x','A.tex':b'y'}]:
            with self.assertRaises(ValueError):deterministic_zip(unsafe)

    def test_cumulative_includes_all_book_prose_but_not_print_driver(self):
        base=ROOT.parent/'out/tests';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='export-',dir=base) as tmp:
            root=Path(tmp);book='locale/xx/courses/book'
            files={
                'locale/xx/content/a.tex':r'\olfileid{a} $P(x)$',
                book+'/slc-screen.tex':'\\input{slc-metadata}\n\\begin{document}\n\\input{slc}\n\\end{document}\n',
                book+'/slc-metadata.tex':r'\title{Book}',
                book+'/slc.tex':r'\input{include/preface}\olimport*[.]{a}',
                book+'/include/preface.tex':'The full preface.',
                book+'/printtest/cover.tex':'NOT SCREEN CONTENT',
            }
            for p,text in files.items():
                dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(text.encode())
            assembly={'book_directory':book,'locale':'xx','files':{p:{'sha256':digest(t.encode())} for p,t in files.items()},
                      'units':[{'id':'OLP-0001','path':'content/a.tex','state':'current','english_fill':False}]}
            profile={'driver':'slc-screen.tex','text_patterns':['*.tex','include/*.tex']}
            body,report=cumulative(root,assembly,[('OLP-0001','content/a.tex')],profile)
            self.assertIn(b'The full preface.',body);self.assertIn(b'$P(x)$',body)
            self.assertNotIn(b'NOT SCREEN CONTENT',body)
            self.assertEqual(report['units'],1);self.assertEqual(report['book_files'],3)
            self.assertNotIn(b'\\olimport',body)
            (root/'locale/xx/content/a.tex').write_text('changed')
            with self.assertRaisesRegex(ValueError,'assembled input changed'):
                cumulative(root,assembly,[('OLP-0001','content/a.tex')],profile)

    def test_source_zip_keeps_notices_and_bibliography_and_excludes_private_files(self):
        base=ROOT.parent/'out/tests';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='source-zip-',dir=base) as tmp:
            output=Path(tmp);source=output/'source';book='locale/xx/courses/book'
            texts={'locale/xx/content/a.tex':b'Full mathematics',book+'/slc-screen.tex':b'driver',
                   'LICENSE.md':b'Original author notice','bib/refs.bib':b'Bibliography',
                   'bib/style.bst':b'Bibliography style','PRIVATE.txt':b'PRIVATE WORKFLOW',
                   book+'/fonts/symbol.cmap':b'Unicode font map'}
            for name,body in texts.items():
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
            assembly={'locale':'xx','product':'slc-screen-pdf','book_directory':book,
                      'sources':{'olp':{'commit':'a'*40}},'files':{p:{'sha256':digest(b)} for p,b in texts.items()}}
            (source/'ASSEMBLY.json').write_bytes(json_bytes(assembly))
            folder=source/book
            (folder/'slc-screen.aux').write_text('\\bibdata{../../../../bib/refs}\n\\bibstyle{style}\n')
            generated = ['slc-screen.aux', 'slc-screen.pcr', 'slc-screen.prb']
            for name in generated[1:]:
                (folder/name).write_text('Generated by Open Logic.')
            fls=folder/'slc-screen.fls'
            inputs = ['locale/xx/content/a.tex', book+'/slc-screen.tex']
            inputs.extend(book+'/'+name for name in generated)
            fls.write_text(''.join('INPUT '+str(source/n)+'\n' for n in inputs))
            (output/'reader.pdf').write_bytes(b'PDF fixture')
            build={'status':'compiled_pending_remaining_gates','commands':[{'exit_code':0,'timed_out':False}],
                   'assembly_sha256':digest(json_bytes(assembly)),'build_tree':'source',
                   'gates':{g:{'status':'pass'} for g in ['G-IMPORT','G-UNITS','G-LOG','G-BOX']},
                   'pdf':{'path':'reader.pdf','sha256':digest(b'PDF fixture')},'recorder_sha256':digest(fls.read_bytes()),
                   'recorder_inputs':input_hashes(read_inputs(fls,folder),source),
                   'content_inputs':{'content/a.tex':['locale/xx/content/a.tex']}}
            receipt=output/'BUILD.json';receipt.write_bytes(json_bytes(build))
            categories=['original-text','book','translation','portraits','photographs','fonts','bundled-packages']
            policy={'schema_version':1,'locale':'xx','product':'slc-screen-pdf','pins':{'olp':'a'*40},
                    'components':[{'id':c,'category':c,'state':'specified','reason':'Fixture notice',
                        'files':[{'path':'LICENSE.md','sha256':digest(texts['LICENSE.md']),'witness':'https://example.org/notice'}],
                        'reader_checks':[]} for c in categories]}
            data,report=source_package(
                source,assembly,receipt,policy,b'Build instructions',b'All text','cumulative.tex',
                driver_inputs=['fonts/symbol.cmap']
            )
            with self.assertRaisesRegex(ValueError,'unrecorded PDF driver input'):
                source_package(source,assembly,receipt,policy,b'Build instructions',b'All text','cumulative.tex',
                               driver_inputs=['fonts/missing.cmap'])
            with ZipFile(io.BytesIO(data)) as z:
                self.assertIn('bib/refs.bib',z.namelist());self.assertIn('bib/style.bst',z.namelist())
                self.assertEqual(z.read('LICENSE.md'),texts['LICENSE.md'])
                self.assertNotIn('PRIVATE.txt',z.namelist())
                for name in generated:
                    self.assertNotIn(book+'/'+name,z.namelist())
                self.assertEqual(z.read(book+'/cumulative.tex'),b'All text')
                self.assertEqual(z.read(book+'/fonts/symbol.cmap'),b'Unicode font map')
            (folder/'slc-screen.aux').write_text('\\bibdata{../../../../../refs}\n')
            build['recorder_inputs']=input_hashes(read_inputs(fls,folder),source)
            receipt.write_bytes(json_bytes(build))
            with self.assertRaisesRegex(ValueError,'unsafe cache member'):
                source_package(source,assembly,receipt,policy,b'Build instructions',b'All text','cumulative.tex')
            build['status']='failed';receipt.write_bytes(json_bytes(build))
            with self.assertRaisesRegex(ValueError,'successful recorded'):
                source_package(source,assembly,receipt,policy,b'Build instructions',b'All text','cumulative.tex')
            build['status']='compiled_pending_remaining_gates';build['recorder_inputs']=[];receipt.write_bytes(json_bytes(build))
            with self.assertRaisesRegex(ValueError,'recorded input hashes'):
                source_package(source,assembly,receipt,policy,b'Build instructions',b'All text','cumulative.tex')


if __name__=='__main__':unittest.main()
