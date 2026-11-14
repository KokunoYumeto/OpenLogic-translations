import json,tempfile,unittest,hashlib
from pathlib import Path
from olpkit.bookcontext import BookInputs


class BookContextIntegrityTests(unittest.TestCase):
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
