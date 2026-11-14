import unittest,tempfile
from pathlib import Path
from olpkit.figureassets import expand_external_figures,combine_exports,initial_asset_width
from olpkit.nativefigures import sha


class ExternalFigureTests(unittest.TestCase):
    def test_book_begin_document_width_supersedes_style_default(self):
        width,evidence=initial_asset_width(
            r'\AtBeginDocument{\setlength{\olphotowidth}{.45\textwidth}}',
            r'\setlength{\olphotowidth}{.4\textwidth}')
        self.assertEqual(width,45)
        self.assertEqual(evidence['begin_document_width_command'],r'\setlength{\olphotowidth}{.45\textwidth}')

    def test_absent_or_ambiguous_initial_width_is_not_guessed(self):
        hook=r'\AtBeginDocument{\setlength{\olphotowidth}{.45\textwidth}}'
        for source in ('',hook+hook,r'\newcommand{\unused}{'+hook+'}'):
            with self.assertRaisesRegex(ValueError,'missing/ambiguous'):
                initial_asset_width(source,r'\setlength{\olphotowidth}{.4\textwidth}')

    def run_source(self,text):
        assets={'assets/a.tikz':b'\\begin{tikzpicture}A\\end{tikzpicture}',
                'assets/b.tikz':b'\\begin{tikzpicture}B\\end{tikzpicture}'}
        return expand_external_figures(text,read=assets.__getitem__,default_width_percent=40,evidence={'config':'checked'})

    def test_external_and_inline_order_with_actual_relative_widths(self):
        text=r'Before \olasset{assets/a.tikz} \begin{tikzpicture}inline\end{tikzpicture} \olasset[2\olphotowidth]{\olpath/assets/b.tikz} After'
        result,r=self.run_source(text)
        self.assertEqual([x['index'] for x in r['figures']],[1,3])
        self.assertEqual([x['width_percent'] for x in r['figures']],[40,80])
        self.assertTrue(result.startswith('Before '));self.assertTrue(result.endswith(' After'))
        self.assertNotIn(r'\olasset',result)

    def test_definition_is_opaque_and_runtime_width_is_retained(self):
        result,r=self.run_source(r'\newcommand{\unused}{\olasset{missing.tikz}} \setlength{\olphotowidth}{.45\textwidth}\olasset{assets/a.tikz}')
        self.assertEqual(len(r['figures']),1);self.assertEqual(r['figures'][0]['width_percent'],45)
        self.assertIn('missing.tikz',result)

    def test_unsafe_asset_and_unknown_width_fail(self):
        for text in [r'\olasset{../x.tikz}',r'\olasset[\unknownwidth]{assets/a.tikz}']:
            with self.assertRaises(ValueError):self.run_source(text)

    def test_identical_inline_source_cannot_steal_external_width(self):
        result,r=self.run_source(r'\begin{tikzpicture}A\end{tikzpicture}\olasset{assets/a.tikz}')
        self.assertEqual(r['figures'][0]['index'],2)

    def test_tableau_shifts_global_occurrence_without_stealing_external_width(self):
        result,r=self.run_source(r'\begin{oltableau}[A,close]\end{oltableau}\olasset{assets/a.tikz}')
        self.assertEqual(r['figures'][0]['index'],2)
        self.assertEqual(r['figures'][0]['width_percent'],40)

    def test_native_crlf_witness_is_retained_when_converter_uses_lf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'native';folder.mkdir()
            source=b'\\begin{oltableau}\r\n[A[B,close][C]]\r\n\\end{oltableau}'
            vector=b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10" viewBox="0 0 20 10"><path d="M0 0L1 1"/></svg>'
            (folder/'figure-001.tex').write_bytes(source);(folder/'figure-001.svg').write_bytes(vector)
            record={'status':'vectors_exported_pending_visual_and_semantic_checks',
                'driver_sha256':'same','preamble_sha256':'same','assembly_sha256':'same',
                'source_sha256':'whole','configuration_evidence':{'source':'native'},'figures':[
                    {'index':1,'source_sha256':sha(source),'source_file':'figure-001.tex',
                     'asset':'figure-001.svg','svg_sha256':sha(vector)}]}
            expected=source.replace(b'\r\n',b'\n')
            result=combine_exports(expected.decode(),[(folder,record)],root/'combined',external={'figures':[]})
            row,=result['figures']
            self.assertEqual(row['source_sha256'],sha(expected))
            self.assertEqual(row['source_normalization']['native_source_sha256'],sha(source))
            self.assertEqual((folder/'figure-001.tex').read_bytes(),source)
            self.assertEqual((root/'combined/figure-001.svg').read_bytes(),vector)
            self.assertEqual((root/'combined/figure-001.tex').read_bytes(),expected)

    def test_combining_native_exports_reuses_exact_bytes_and_rejects_changed_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);exports=[];sources=[]
            svg=b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10" viewBox="0 0 20 10"><path d="M0 0L1 1"/></svg>'
            for label in ['A','B']:
                folder=root/label;folder.mkdir()
                source=(r'\begin{tikzpicture}A\end{tikzpicture}' if label=='A' else
                        r'\begin{oltableau}[B,just={Given}[C,close][D]]\end{oltableau}')
                sources.append(source)
                (folder/'figure-001.tex').write_text(source,encoding='utf-8');(folder/'figure-001.svg').write_bytes(svg)
                record={'status':'vectors_exported_pending_visual_and_semantic_checks',
                        'driver_sha256':'same','preamble_sha256':'same','assembly_sha256':'same',
                        'source_sha256':sha(source.encode()),'configuration_evidence':{'source':label},
                        'figures':[{'index':1,'source_sha256':sha(source.encode()),'source_file':'figure-001.tex',
                                    'asset':'figure-001.svg','svg_sha256':sha(svg),'width':'20','height':'10','viewBox':'0 0 20 10'}]}
                exports.append((folder,record))
            result=combine_exports(sources[1]+sources[0],exports,root/'combined',external={'figures':[{'index':1,'width_percent':80}]})
            self.assertEqual(result['tex_runs'],0)
            self.assertEqual((root/'combined/figure-001.tex').read_text(),sources[1])
            self.assertEqual((root/'combined/figure-002.svg').read_bytes(),svg)
            self.assertEqual(result['figures'][0]['width_percent'],80)
            exports[1][1]['preamble_sha256']='different'
            with self.assertRaisesRegex(ValueError,'different book configurations'):
                combine_exports(sources[1]+sources[0],exports,root/'different',external={'figures':[]})
