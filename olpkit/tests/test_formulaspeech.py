import unittest,hashlib
from olpkit.formulaspeech import index_formulas


class FormulaSpeechInputTests(unittest.TestCase):
    def test_same_tex_keeps_distinct_contexts_and_exact_hash(self):
        math='<math><semantics><mi>x</mi><annotation encoding="application/x-tex">x</annotation></semantics></math>'
        source=('<html lang="jv"><body><span data-unit-id="OLP-0001"></span><p>First '+math+'</p><p>Other '+math+'</p></body></html>').encode()
        r=index_formulas(source,'jv');self.assertEqual(r['formula_occurrences'],2);self.assertEqual(r['unique_formulas'],1)
        key=hashlib.sha256(b'x').hexdigest();self.assertEqual(r['formulas'][key]['tex'],'x')
        self.assertEqual([r['contexts'][x['context_id']] for x in r['occurrences']],['First x','Other x'])
        self.assertFalse(r['spoken_text_produced'])

    def test_missing_annotation_or_wrong_language_fails(self):
        with self.assertRaisesRegex(ValueError,'annotation'):
            index_formulas(b'<html lang="jv"><body><math><mi>x</mi></math></body></html>','jv')
        with self.assertRaisesRegex(ValueError,'language'):
            index_formulas(b'<html lang="en"><body/></html>','jv')
