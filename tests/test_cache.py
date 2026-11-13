import json
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from olpkit.cache import SourceCache, cache_manifest, relative_path


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.boundary = Path('C:/olp-build/out/tests').resolve()
        self.boundary.mkdir(parents=True,exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='cache-',dir=self.boundary))
        self.repo = self.root/'upstream'
        self.repo.mkdir()
        self.git('init')
        self.git('config','user.name','Builder test')
        self.git('config','user.email','builder-test@example.invalid')
        self.git('config','core.autocrlf','false')
        (self.repo/'content').mkdir()
        (self.repo/'content/unit.tex').write_bytes(b'\\section{A}\nAn exact source.\n')
        (self.repo/'LICENSE').write_bytes(b'Test fixture only.\n')
        self.pin = self.commit()
        self.cache = SourceCache(self.root/'cache',{'sample':{'repository':self.repo.as_posix(),'cache':'sample.git'}})

    def git(self,*args):
        return subprocess.run(['git','-C',str(self.repo),*args],check=True,capture_output=True).stdout

    def commit(self):
        self.git('add','.')
        self.git('commit','-m','fixture')
        return self.git('rev-parse','HEAD').decode().strip()

    def tearDown(self):
        self.assertEqual(self.root.resolve().parent,self.boundary)
        self.assertTrue(self.root.name.startswith('cache-'))
        for file in self.root.rglob('*'):
            if file.is_file() and not file.is_symlink():
                file.chmod(stat.S_IWRITE|stat.S_IREAD)
        shutil.rmtree(self.root)

    def test_cold_and_warm_fetch_preserve_exact_bytes(self):
        first = self.cache.fetch('sample',self.pin)
        self.assertEqual(first['network_fetches'],1)
        self.assertTrue(first['export_created'])
        folder,record = self.cache.require('sample',self.pin)
        self.assertEqual((folder/'content/unit.tex').read_bytes(),(self.repo/'content/unit.tex').read_bytes())
        before = cache_manifest(self.cache.root)
        second = self.cache.fetch('sample',self.pin)
        self.assertEqual(second['network_fetches'],0)
        self.assertFalse(second['export_created'])
        self.assertEqual(before,cache_manifest(self.cache.root))
        self.assertEqual(len(record['files']),2)

    def test_require_uses_no_git_or_network(self):
        self.cache.fetch('sample',self.pin)
        with patch('olpkit.cache.run_git',side_effect=AssertionError('offline read called Git')):
            self.cache.require('sample',self.pin)

    def test_no_implicit_fetch(self):
        with self.assertRaisesRegex(ValueError,'run fetch'):
            self.cache.require('sample',self.pin)

    def test_tampered_export_is_rejected_without_repairing_it(self):
        self.cache.fetch('sample',self.pin)
        _,folder,_ = self.cache.locations('sample',self.pin)
        file = folder/'content/unit.tex'
        file.chmod(stat.S_IWRITE|stat.S_IREAD)
        file.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'bytes differ'):
            self.cache.fetch('sample',self.pin)
        self.assertEqual(file.read_bytes(),b'changed')

    def test_added_export_file_is_rejected(self):
        self.cache.fetch('sample',self.pin)
        _,folder,_ = self.cache.locations('sample',self.pin)
        (folder/'unexpected.tex').write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError,'file set'):
            self.cache.require('sample',self.pin)

    def test_unpinned_and_unknown_sources_are_rejected(self):
        for source,pin in [('sample','main'),('missing',self.pin),('../sample',self.pin)]:
            with self.subTest(source=source,pin=pin),self.assertRaises(ValueError):
                self.cache.fetch(source,pin)

    def test_checkout_and_export_attributes_cannot_change_source(self):
        (self.repo/'.gitattributes').write_bytes(b'LICENSE export-ignore\n*.tex text eol=crlf\n')
        pin = self.commit()
        self.cache.fetch('sample',pin)
        _,folder,receipt=self.cache.locations('sample',pin)
        self.assertTrue((folder/'LICENSE').is_file())
        self.assertEqual((folder/'content/unit.tex').read_bytes(),b'\\section{A}\nAn exact source.\n')
        self.assertTrue(receipt.exists())
        self.assertEqual(list((self.cache.root/'incoming').iterdir()),[])

    def test_windows_and_traversal_paths_rejected(self):
        for name in ['../x','/x','a/../x','a\\x','C:/x','.git/config','a/CON.txt','a./x','a//x']:
            with self.subTest(name=name),self.assertRaises(ValueError):
                relative_path(name)

    def test_tampered_manifest_identity_rejected(self):
        self.cache.fetch('sample',self.pin)
        _,_,receipt=self.cache.locations('sample',self.pin)
        record=json.loads(receipt.read_text())
        record['commit']='0'*40
        receipt.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'different source'):
            self.cache.require('sample',self.pin)


if __name__ == '__main__':
    unittest.main()
