from pathlib import Path
import tempfile
import unittest

from olpkit.assembly import digest,json_bytes
from olpkit.importlock import pin_key,select_lock,write_lock
from olpkit.schemas import ROOT


class ImportLockTests(unittest.TestCase):
    def setUp(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='pin-lock-',dir=boundary)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.pins={'olp':'a'*40,'slc':'b'*40,'photos':'c'*40,'portraits':'d'*40}
        self.body=b'OLP-0001\tcontent/open-logic-about.tex\n'

    def meta(self,pins=None,body=None):
        return {'schema':'olpkit.imports.v1','pins':pins or self.pins,
                'units':1,'lock_sha256':digest(body or self.body),
                'recorder_sha256':'1'*64,'reference_pdf_sha256':'2'*64}

    def legacy(self):
        (self.root/'imports.lock').write_bytes(self.body)
        (self.root/'imports.json').write_bytes(json_bytes(self.meta()))

    def test_old_and_new_pins_coexist_without_replacing_original(self):
        self.legacy();before=(self.root/'imports.json').read_bytes()
        second={**self.pins,'olp':'e'*40}
        folder=write_lock(self.root,self.body,self.meta(second))
        self.assertEqual(select_lock(self.root,self.pins)[0],self.root)
        self.assertEqual(select_lock(self.root,second)[0],folder)
        self.assertEqual((self.root/'imports.json').read_bytes(),before)

    def test_unknown_pin_set_is_not_inferred_from_equal_paths(self):
        self.legacy()
        with self.assertRaisesRegex(ValueError,'no import lock'):
            select_lock(self.root,{**self.pins,'olp':'e'*40})

    def test_tampered_scoped_lock_is_not_hidden_by_legacy_fallback(self):
        folder=write_lock(self.root,self.body,self.meta());self.legacy()
        (folder/'imports.lock').write_bytes(self.body+b'changed')
        with self.assertRaisesRegex(ValueError,'hash differs'):select_lock(self.root,self.pins)

    def test_changed_import_set_at_same_pins_requires_review(self):
        self.legacy();changed=b'OLP-0002\tcontent/other.tex\n'
        with self.assertRaisesRegex(ValueError,'existing import lock differs'):
            write_lock(self.root,changed,self.meta(body=changed))

    def test_repeated_reference_preserves_first_witness(self):
        folder=write_lock(self.root,self.body,self.meta())
        before=(folder/'imports.json').read_bytes()
        new={**self.meta(),'recorder_sha256':'3'*64}
        self.assertEqual(write_lock(self.root,self.body,new),folder)
        self.assertEqual((folder/'imports.json').read_bytes(),before)

    def test_all_source_pins_are_part_of_identity(self):
        for key in self.pins:
            self.assertNotEqual(pin_key(self.pins),pin_key({**self.pins,key:'e'*40}))
        for bad in [{**self.pins,'olp':'main'}, {'olp':'a'*40}, {**self.pins,'olp':'../private'}]:
            with self.assertRaises(ValueError):pin_key(bad)

    def test_reference_witness_and_unit_count_are_required(self):
        self.legacy()
        for mutation in [{'units':2},{'reference_pdf_sha256':None}]:
            (self.root/'imports.json').write_bytes(json_bytes({**self.meta(),**mutation}))
            with self.assertRaises(ValueError):select_lock(self.root,self.pins)


if __name__=='__main__':unittest.main()
