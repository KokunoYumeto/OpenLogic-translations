import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from olpkit.assembly import digest
from olpkit.packagecheck import unpack
from olpkit.tablecheck import localized_proof_labels


class PackageCheckTests(unittest.TestCase):
    def test_zip_requires_the_export_and_internal_manifest_to_agree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = {'unit.tex': b'A', 'SOURCE-SHA256SUMS.txt': (digest(b'A') + '  unit.tex\n').encode()}
            members = {n: {'sha256': digest(s), 'bytes': len(s)} for n, s in data.items()}
            archive = root / 'source.zip'
            with ZipFile(archive, 'w') as z:
                for n, s in data.items():
                    z.writestr(n, s)
            unpack(archive, members, root / 'clean')
            self.assertEqual((root / 'clean/unit.tex').read_bytes(), b'A')
            data['unit.tex'] = b'B'
            members['unit.tex']['sha256'] = digest(b'B')
            with ZipFile(archive, 'w') as z:
                for n, s in data.items():
                    z.writestr(n, s)
            with self.assertRaisesRegex(ValueError, 'internal source manifest'):
                unpack(archive, members, root / 'bad')

    def test_matching_label_does_not_rename_a_proposition(self):
        label = [{'command': 'LeftR', 'english': 'L', 'target': 'डा.'}]
        before = {'source_tex': r'\LeftR{\land}'}
        after = {'source_tex': r'\LeftR{\lor}'}
        self.assertEqual(localized_proof_labels('L⇒M∧LL', before, before, label), 'L⇒M∧डा.L')
        self.assertEqual(localized_proof_labels('L⇒M∧LL', before, after, label), 'L⇒M∧LL')
