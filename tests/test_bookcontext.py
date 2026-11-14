import json,tempfile,unittest,hashlib
from pathlib import Path
from olpkit.bookcontext import BookInputs,source_caption,display_inventory


class BookContextIntegrityTests(unittest.TestCase):
    def test_native_tableau_is_deferred_in_context_but_not_dropped_from_conversion(self):
        from olpkit.mathdisplay import DisplayAdapter
        tableau=r'\begin{oltableau}[A,just={Given}[B,close][C]]\end{oltableau}'
        text='Before\n'+tableau+'\nAfter $x=y$'
        result=display_inventory(text,{'proof_label_styles':{},'math_font_sizes':{}})
        row,=result['deferred_native_figures']
        self.assertEqual(row['source_sha256'],hashlib.sha256(tableau.encode()).hexdigest())
        self.assertEqual(text[row['char_start']:row['char_end']],tableau)
        self.assertEqual(row['line'],2)
        self.assertEqual(result['source_before_native_deferral_sha256'],hashlib.sha256(text.encode()).hexdigest())
        with self.assertRaisesRegex(ValueError,'complete tree renderer'):
            DisplayAdapter().prepare(text,'unbound-render-input')

    def test_text_witness_newlines_are_bound_to_the_projection_hash(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);data=b'first\r\nsecond\n';(p/'projection.tex').write_bytes(data)
            (p/'ASSEMBLY.json').write_text(json.dumps({'locale':'xx','book_directory':'book','files':{}}))
            profile={'locale':'xx','witnesses':{'projection':{'path':str(p/'projection.tex'),'sha256':hashlib.sha256(data).hexdigest()}}}
            obj=BookInputs(p,profile)
            self.assertEqual(obj.witness_text('projection',hashlib.sha256(data).hexdigest()),data.decode())
            normalized=data.replace(b'\r\n',b'\n')
            self.assertEqual(obj.witness_text('projection',hashlib.sha256(normalized).hexdigest()),normalized.decode())
            with self.assertRaisesRegex(ValueError,'recorded projection'):
                obj.witness_text('projection','0'*64)

    def test_native_caption_spellings_and_ambiguity(self):
        self.assertEqual(source_caption(r'\setlocalecaption{gujarati}{proof}{સાબિતી}','gujarati','proof'),'સાબિતી')
        self.assertEqual(source_caption(r'\addto\captionsjavanese{\renewcommand{\proofname}{Bukti}}','javanese','proof'),'Bukti')
        text='% '+r'\renewcommand{\proofname}{wrong}'+'\n'+r'\setlocalecaption{gujarati}{proof}{સાબિતી}'
        self.assertEqual(source_caption(text,'gujarati','proof'),'સાબિતી')
        for value in (r'\setlocalecaption{other}{proof}{wrong}',
                      r'\renewcommand{\proofname}{one}\setlocalecaption{gujarati}{proof}{two}'):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'missing or ambiguous'):
                source_caption(value,'gujarati','proof')

    def test_changed_source_or_witness_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);data=b'exact source';(p/'unit.tex').write_bytes(data)
            (p/'ASSEMBLY.json').write_text(json.dumps({'locale':'xx','book_directory':'book','files':{'unit.tex':{'sha256':hashlib.sha256(data).hexdigest()}}}))
            profile={'locale':'xx','witnesses':{'aux':{'path':str(p/'unit.tex'),'sha256':hashlib.sha256(data).hexdigest()}}}
            obj=BookInputs(p,profile);self.assertEqual(obj.bytes('unit.tex'),data);self.assertEqual(obj.witness('aux'),data)
            (p/'unit.tex').write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError,'input changed'):obj.bytes('unit.tex')
            with self.assertRaisesRegex(ValueError,'witness changed'):obj.witness('aux')
            with self.assertRaisesRegex(ValueError,'unrecorded'):obj.bytes('../unit.tex')
            with self.assertRaisesRegex(ValueError,'locale differs'):BookInputs(p,{'locale':'other'})
