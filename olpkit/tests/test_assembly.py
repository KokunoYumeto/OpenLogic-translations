from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from olpkit.assembly import (AssemblyTree, GitSnapshot, assemble_units, digest,
                             locale_marks, write_assembly)
from olpkit.edition import git_blob
from olpkit.schemas import ROOT


class UnitAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.edition = {'locale':'xx','paths':{'content':'translation/content'}}
        self.english = {f'content/chapter/u{i}.tex':(r'\olfileid{ch}{sub}{u'+str(i)+'}\nSource '+str(i)).encode() for i in range(12)}
        self.targets = {p.replace('content/','translation/content/',1):b.replace(b'Source',b'Target') for p,b in self.english.items()}
        self.registry = {p:f'OLP-{i:04d}' for i,p in enumerate(self.english,1)}
        self.units = [{'id':self.registry[p],'src':'olp','path':p,'src_blob':git_blob(b),
                       'src_sha256':digest(b),'tr_sha256':digest(self.targets['translation/'+p]),
                       'state':'current','by':{'model':None,'effort':None,'date':None,
                       'method':'inherited','evidence':'test fixture'}} for p,b in self.english.items()]

    def run_assembly(self):
        return assemble_units(self.edition,self.units,self.english,self.targets,self.registry)

    def test_ten_explicit_new_units_are_english_and_unmarked(self):
        for u in self.units[:10]:
            u.update(state='new',tr_sha256=None)
            del self.targets['translation/'+u['path']]
        files,report = self.run_assembly()
        self.assertEqual(sum(r['english_fill'] for r in report),10)
        for u in self.units[:10]:
            self.assertEqual(files[u['path']],self.english[u['path']])
            self.assertNotIn(b'[xx]',files[u['path']])
        for u in self.units[10:]:
            self.assertIn(b'\\olfileid[xx]',files[u['path']])

    def test_missing_recorded_translation_fails_instead_of_filling(self):
        del self.targets['translation/'+self.units[0]['path']]
        with self.assertRaisesRegex(ValueError,'translated bytes differ'):
            self.run_assembly()

    def test_changed_translation_and_source_each_fail(self):
        path='translation/'+self.units[0]['path'];self.targets[path]+=b'x'
        with self.assertRaisesRegex(ValueError,'translated bytes differ'):self.run_assembly()
        self.targets[path]=self.targets[path][:-1]
        self.units[0]['src_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'source SHA-256'):self.run_assembly()

    def test_stale_unit_is_retained_and_reported_never_called_current(self):
        self.units[0].update(src_blob='1'*40,src_sha256='2'*64,state='stale')
        _,report=self.run_assembly()
        self.assertEqual(report[0]['state'],'stale')
        self.assertFalse(report[0]['english_fill'])

    def test_duplicate_and_unrecorded_targets_fail(self):
        self.units.append(deepcopy(self.units[0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):self.run_assembly()
        self.units.pop();self.targets['translation/content/unrecorded.tex']=b'Hidden'
        with self.assertRaisesRegex(ValueError,'outside the pinned source ledger'):self.run_assembly()

    def test_existing_target_cannot_hide_behind_new_state(self):
        self.units[0].update(state='new',tr_sha256=None)
        with self.assertRaisesRegex(ValueError,'unrecorded target'):self.run_assembly()

    def test_marks_preserve_prose_math_bytes_comments_and_existing_flags(self):
        original=(b'\xef\xbb\xbf% \\olfileid{comment}\r\n'+
                  b'\\olfileid{a}{b}{c}\r\n\\olchapterid[xx]{d}\n'+
                  b'Target $x=y$ \\% \\olpartid{z}% comment\n')
        expected=original.replace(b'\\olfileid{a}',b'\\olfileid[xx]{a}').replace(b'\\olpartid{z}',b'\\olpartid[xx]{z}')
        result,count=locale_marks(original,'xx')
        self.assertEqual(result,expected);self.assertEqual(count,2)
        self.assertEqual(locale_marks(result,'xx'),(result,0))
        with self.assertRaisesRegex(ValueError,'different locale'):
            locale_marks(b'\\olfileid[yy]{a}','xx')


class AssemblyIOTests(unittest.TestCase):
    def setUp(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='assembly-',dir=boundary)
        self.root=Path(self.temp.name)
        self.addCleanup(self.cleanup)

    def cleanup(self):
        if self.root.resolve().parent!=(ROOT.parent/'out/tests').resolve():
            raise ValueError('test folder escaped its boundary')
        self.temp.cleanup()

    def test_tree_rejects_collisions_escapes_and_windows_device_names(self):
        tree=AssemblyTree();tree.add('content/a.tex',b'one',{'source':'fixture'})
        for name in ['content/a.tex','content/A.tex','../outside','NUL.tex','content\\bad']:
            with self.subTest(name=name),self.assertRaises(ValueError):
                tree.add(name,b'two',{'source':'fixture'})

    def test_same_tree_and_report_have_identical_bytes_and_preserve_changed_output(self):
        tree=AssemblyTree();tree.add('unit.tex',b'Exact\r\n',{'source':'fixture'})
        report={'files':tree.origins}
        for name in ['one','two']:write_assembly(tree,report,self.root/name)
        self.assertEqual((self.root/'one/ASSEMBLY.json').read_bytes(),(self.root/'two/ASSEMBLY.json').read_bytes())
        write_assembly(tree,report,self.root/'one',check=True)
        (self.root/'one/unit.tex').write_bytes(b'Owner edit')
        with self.assertRaisesRegex(ValueError,'preserve it'):
            write_assembly(tree,report,self.root/'one')
        self.assertEqual((self.root/'one/unit.tex').read_bytes(),b'Owner edit')
        with self.assertRaisesRegex(ValueError,'named child'):
            write_assembly(tree,report,ROOT)

    def test_snapshot_uses_committed_raw_bytes_without_checkout_filters(self):
        repo=self.root/'repo';repo.mkdir()
        def git(*args,input=None):
            return subprocess.run(['git','-C',str(repo),*args],input=input,capture_output=True,check=True).stdout
        git('init','-q');git('config','core.autocrlf','false')
        (repo/'unit.tex').write_bytes(b'Original\n');git('add','unit.tex')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Fixture')
        snap=GitSnapshot(repo,'HEAD')
        (repo/'unit.tex').write_bytes(b'Uncommitted owner work\r\n')
        self.assertEqual(snap.read_many(['unit.tex']),{'unit.tex':b'Original\n'})
        with self.assertRaisesRegex(ValueError,'absent'):snap.read_many(['missing.tex'])
        with self.assertRaisesRegex(ValueError,'unsafe'):snap.read_many(['../unit.tex'])
        self.assertEqual((repo/'unit.tex').read_bytes(),b'Uncommitted owner work\r\n')


if __name__=='__main__':unittest.main()
