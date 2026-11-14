import unittest
from olpkit.schemas import validator


class HubMetadataSchemaTests(unittest.TestCase):
    def errors(self, public):
        schema=validator('olp-edition').schema['properties']['public']
        return list(type(validator('olp-edition'))(schema).iter_errors(public))

    def test_existing_public_tables_remain_valid(self):
        self.assertFalse(self.errors({'title':'Title','description':'Scope','limitations':[],
                                      'attribution':'Actual production attribution','license':'CC BY 4.0'}))

    def test_hash_bound_public_catalogue(self):
        self.assertFalse(self.errors({'catalogue':{'path':'publication/catalogue.json','sha256':'a'*64}}))

    def test_missing_hash_or_unknown_metadata_key_is_rejected(self):
        for data in [{'path':'publication/catalogue.json'},
                     {'path':'publication/catalogue.json','sha256':'not a digest'},
                     {'path':'publication/catalogue.json','sha256':'a'*64,'trust':True}]:
            with self.subTest(data=data):self.assertTrue(self.errors({'catalogue':data}))

    def test_catalogue_path_cannot_escape_or_point_to_executable_data(self):
        for path in ['../catalogue.json','/catalogue.json','C:/catalogue.json',
                     r'publication\catalogue.json','https://example.invalid/catalogue.json','catalogue.py']:
            with self.subTest(path=path):self.assertTrue(self.errors({'catalogue':{'path':path,'sha256':'a'*64}}))
