import json
import unittest

from olpkit.assembly import digest, json_bytes
from olpkit.formulaspeech import index_formulas
from olpkit.speechsync import reviewed_store, speech_delta


class SpeechSyncTests(unittest.TestCase):
    def setUp(self):
        math = '<math><mi>x</mi><annotation encoding="application/x-tex">x</annotation></math>'
        reader = '<html lang="xx"><body><p>One {0}</p><p>Two {0}</p></body></html>'
        self.old = reader.format(math).encode()
        self.new = reader.replace('<body>', '<body><p>New {0}</p>').format(math).encode()
        packet = index_formulas(self.old, 'xx')
        self.packet = json_bytes(packet)
        key = digest(b'x')
        self.store = json_bytes({
            'schema': 'test', 'language': 'xx', 'input_sha256': digest(self.packet),
            'reader_sha256': digest(self.old), 'occurrence_source_map_sha256': digest(b'map'),
            'model': 'previous', 'reasoning_effort': 'test', 'model_observed_at': 'then',
            'rules': {'literal': {'canon_passages': [{'passage_id': 'p1'}]}},
            'formulas': {key: {**packet['formulas'][key], 'spoken_text': 'letter', 'rule_ids': ['literal'],
                               'contextual_variants': {'formula-000002': 'second reading'}}}
        })

    def test_changed_letter_name_in_adjacent_cell_requires_review_for_old_packets(self):
        math = '<math><mi>I</mi><annotation encoding="application/x-tex">I</annotation></math>'
        reader = ('<html lang="xx"><body><table><tr><td>Iota</td><td><p>' + math +
                  '</p></td></tr></table><p>Input ' + math + '</p></body></html>').encode()
        packet = index_formulas(reader, 'xx')
        chart = packet.pop('table_context')
        where = chart['occurrences']['formula-000001']
        self.assertEqual(where['cell'], 1)
        self.assertEqual(chart['rows'][where['row']][0]['text'], 'Iota')
        self.assertNotIn('formula-000002', chart['occurrences'])
        previous_bytes = json_bytes(packet)
        store = json.loads(self.store)
        store.update(input_sha256=digest(previous_bytes), reader_sha256=digest(reader))
        _, delta = speech_delta(reader, previous_bytes, json_bytes(store), reader.replace(b'Iota', b'Latin I'))
        self.assertEqual(delta['review_required'], ['formula-000001'])
        self.assertEqual(delta['reused'], {'formula-000002': 'formula-000002'})
        packet['table_context'] = chart
        where['cell'] = 0
        previous_bytes = json_bytes(packet)
        store['input_sha256'] = digest(previous_bytes)
        with self.assertRaisesRegex(ValueError, 'table_context'):
            speech_delta(reader, previous_bytes, json_bytes(store), reader)

    def test_readings_follow_the_exercise_definition_and_glossary_headword(self):
        math = '<math><mi>x</mi><annotation encoding="application/x-tex">x</annotation></math>'
        reader = ('<html lang="xx"><body><div class="probd" data-native-number="2.4">'
                  '<p>Let x denote a cell.</p><p>' + math + '</p></div>'
                  '<dl class="olp-glossary"><dt id="a">Stroke</dt><dd><p>' + math + '</p></dd>'
                  '<dt id="b">Word</dt><dd>' + math + '</dd></dl><p>' + math + '</p></body></html>').encode()
        packet = index_formulas(reader, 'xx')
        regions = packet.pop('reading_regions')
        self.assertEqual(len(regions['regions']), 3)
        for i, locator in enumerate(('2.4','a','b'), 1):
            key, = regions['occurrences'][f'formula-{i:06d}']
            self.assertEqual(regions['regions'][key]['locator'], locator)
        previous_bytes = json_bytes(packet)
        store = json.loads(self.store)
        store.update(input_sha256=digest(previous_bytes), reader_sha256=digest(reader))
        after = reader.replace(b'a cell', b'an input').replace(b'>Stroke<', b'>Alphabet<')
        _, delta = speech_delta(reader, previous_bytes, json_bytes(store), after)
        self.assertEqual(delta['review_required'], ['formula-000001', 'formula-000002'])
        self.assertEqual(set(delta['reused']), {'formula-000003','formula-000004'})

    def test_variant_follows_context_when_number_changes(self):
        packet, delta = speech_delta(self.old, self.packet, self.store, self.new)
        self.assertEqual(delta['review_required'], ['formula-000001'])
        review = {'delta_sha256': digest(json_bytes(delta)), 'model': 'current', 'reasoning_effort': 'test',
                  'model_observed_at': 'now', 'attribution': 'previous and current',
                  'decisions': {'formula-000001': {
                      'formula_sha256': digest(b'x'), 'from_occurrence': 'formula-000001',
                      'source_locator': 'unit 1', 'rationale': 'same role', 'canon_passages': ['p1']}}}
        store, sources = reviewed_store(packet, delta, self.store, review, b'map')
        self.assertEqual(store['formulas'][digest(b'x')]['contextual_variants'], {'formula-000003': 'second reading'})
        self.assertEqual(sources['retained_occurrences']['formula-000003'], 'formula-000002')
        with self.assertRaisesRegex(ValueError, 'source map differs'):
            reviewed_store(packet, delta, self.store, review, b'other')
        review['decisions'] = {}
        with self.assertRaisesRegex(ValueError, 'exact occurrence review'):
            reviewed_store(packet, delta, self.store, review, b'map')

    def test_change_beyond_truncated_prose_requires_review(self):
        start = self.old.replace(b'One ', b'a' * 900 + b'b')
        packet = json_bytes(index_formulas(start, 'xx'))
        store = json.loads(self.store)
        store.update(reader_sha256=digest(start), input_sha256=digest(packet))
        _, delta = speech_delta(start, packet, json_bytes(store), start.replace(b'ab<math>', b'ac<math>'))
        self.assertEqual(delta['review_required'], ['formula-000001'])
