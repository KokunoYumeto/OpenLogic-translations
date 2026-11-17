import unittest,json,hashlib,copy
from pathlib import Path
from tempfile import TemporaryDirectory
from lxml import html
from olpkit.formulaspeech import index_formulas,bind_speech


class SpeechBindingTests(unittest.TestCase):
    def setUp(self):
        math='<math><semantics><mi>x</mi><annotation encoding="application/x-tex">x</annotation></semantics></math>'
        self.reader=('<html lang="xx"><body><p>First '+math+'</p><p>Other '+math+'</p></body></html>').encode()
        self.packet=json.dumps(index_formulas(self.reader,'xx')).encode()
        self.key=hashlib.sha256(b'x').hexdigest()
        self.store={'language':'xx','input_sha256':hashlib.sha256(self.packet).hexdigest(),
            'model':'test-model','reasoning_effort':'ultra','rules':{'r':{'explanation':'rule',
            'canon_passages':[{'passage_id':'p','source_id':'s','source_sha256':'a'*64,
                'locator':'page 1','excerpt':'example','use':'register'}],
            'rationale':'reason','rejected_alternatives':[],'uncertainty':'provisional',
            'editorial_confidence':{'level':'provisional','reason':'test fixture'}}},
            'formulas':{self.key:{'tex':'x','spoken_text':'letter x','rule_ids':['r'],
                'occurrence_ids':['formula-000001','formula-000002'],
                'contextual_variants':{'formula-000002':'the variable x'}}}}

    def bind(self,store=None,reader=None):
        return bind_speech(reader or self.reader,self.packet,json.dumps(store or self.store).encode())

    def test_maintenance_archive_reproduces_attributed_reader_and_checks_source_map(self):
        from olpkit.assembly import digest, json_bytes
        from olpkit.formulaspeech import add_speech_attribution
        from olpkit.speecharchive import maintenance_inputs
        reader = self.reader.replace(b"<body>", b'<body><div id="olp-native-credit-3"></div>')
        packet = json_bytes(index_formulas(reader, "xx"))
        store = copy.deepcopy(self.store)
        store.update(input_sha256=digest(packet), occurrence_source_map_sha256=digest(b"map"),
                     interface={"attribution": "Spoken text by Fixture"})
        passage = store["rules"]["r"]["canon_passages"][0]
        passage["consultation"] = "private administrative note"
        bound, _ = bind_speech(reader, packet, json_bytes(store))
        readings = store["formulas"][self.key]
        labels = {"schema": "olpkit.released-speech.v1", "language": "xx",
                  "reader_sha256": digest(reader), "bound_reader_sha256": digest(bound),
                  "attribution": store["interface"]["attribution"],
                  "labels": [{"tex_sha256": self.key, "text": readings.get("contextual_variants", {}).get(i, readings["spoken_text"])}
                             for i in readings["occurrence_ids"]]}
        final = digest(add_speech_attribution(bound, labels["attribution"]))
        with TemporaryDirectory() as tmp:
            update = Path(tmp)
            (update / "speech-input.json").write_bytes(packet)
            (update / "speech-store.json").write_bytes(json_bytes(store))
            (update / "occurrence-sources.json").write_bytes(b"map")
            files = maintenance_inputs(reader, update, labels, final)
            public = json.loads(files["speech-store.json"])["rules"]["r"]["canon_passages"][0]
            self.assertEqual(public, {k:v for k,v in passage.items() if k != "consultation"})
            with self.assertRaisesRegex(ValueError, "released reader"):
                maintenance_inputs(reader, update, labels, digest(bound))
            with self.assertRaisesRegex(ValueError, "released reader"):
                maintenance_inputs(reader, update, {**labels, "attribution":"Changed"}, final)
            (update / "occurrence-sources.json").write_bytes(b"different")
            with self.assertRaisesRegex(ValueError, "source map"):
                maintenance_inputs(reader, update, labels, final)

    def test_exact_occurrences_receive_distinct_readings_without_math_changes(self):
        data,report=self.bind();doc=html.document_fromstring(data)
        self.assertEqual(doc.xpath('//math/@alttext'),['letter x','the variable x'])
        self.assertEqual(doc.xpath('//math/@aria-label'),['letter x','the variable x'])
        self.assertEqual(doc.xpath('//annotation/text()'),['x','x'])
        self.assertEqual(report['with_spoken_text'],2);self.assertEqual(report['contextual_variants'],1)
        self.assertFalse(report['release_ready'])

    def test_unchanged_formula_in_changed_context_requires_review(self):
        with self.assertRaisesRegex(ValueError,'changed; review'):
            self.bind(reader=self.reader.replace(b'First',b'Changed meaning'))

    def test_missing_or_unbound_reading_is_rejected(self):
        for change in ('missing_formula','missing_occurrence','wrong_tex','missing_rule','empty_variant','unknown_variant','missing_canon'):
            store=copy.deepcopy(self.store);row=store['formulas'][self.key]
            if change=='missing_formula':store['formulas'].clear()
            elif change=='missing_occurrence':row['occurrence_ids'].pop()
            elif change=='wrong_tex':row['tex']='y'
            elif change=='missing_rule':row['rule_ids']=['absent']
            elif change=='empty_variant':row['contextual_variants']['formula-000002']=''
            elif change=='unknown_variant':row['contextual_variants']['formula-000003']='other'
            else:store['rules']['r']['canon_passages']=[]
            with self.subTest(change=change),self.assertRaises(ValueError):self.bind(store)

    def test_changed_packet_or_language_and_rebinding_are_rejected(self):
        store=copy.deepcopy(self.store);store['input_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'identity'):self.bind(store)
        store=copy.deepcopy(self.store);store['language']='other'
        with self.assertRaisesRegex(ValueError,'language'):self.bind(store)
        data,_=self.bind()
        with self.assertRaisesRegex(ValueError,'already attached'):self.bind(reader=data)
