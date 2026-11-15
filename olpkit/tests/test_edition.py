import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from olpkit.edition import ROOT, git_blob, render_edition, safe_path, sha256, validate_edition
from olpkit.schemas import validate_schema


class EditionTests(unittest.TestCase):
    def setUp(self):
        test_root = (ROOT.parent/'out/tests').resolve()
        test_root.mkdir(parents=True,exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='olpkit-edition-',dir=test_root)
        def cleanup():
            target=Path(self.temporary.name).resolve()
            if target==test_root or not target.is_relative_to(test_root):
                raise ValueError('test cleanup target is outside the named test directory')
            self.temporary.cleanup()
        self.addCleanup(cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base/'source';self.source.mkdir()
        self.repo = self.base/'edition';self.repo.mkdir()
        subprocess.run(['git','init','-q',str(self.source)],check=True,capture_output=True)
        self.rows=[]
        for line in (ROOT/'data/units/olp-units.tsv').read_text(encoding='utf-8').splitlines()[1:3]:
            uid,path=line.split('\t');body=(uid+' synthetic English fixture\n').encode()
            target=(uid+' synthetic target fixture\n').encode()
            for root,payload in [(self.source,body),(self.repo/'upstream',body),(self.repo/'target',target)]:
                file=root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(payload)
            self.rows.append({'id':uid,'src':'olp','path':path,'src_blob':git_blob(body),'src_sha256':sha256(body),'tr_sha256':sha256(target),'state':'current','by':{'model':None,'effort':None,'date':None,'method':'inherited','evidence':'historical-manifest.json'}})
        subprocess.run(['git','-C',str(self.source),'add','.'],check=True,capture_output=True)
        subprocess.run(['git','-C',str(self.source),'-c','user.name=Test fixture','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True,capture_output=True)
        self.pin=subprocess.run(['git','-C',str(self.source),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
        self.data={'schema_version':1,'locale':'test','language_tag':'en','script':'Latn','babel':'english','engine':'lualatex','repository':'https://github.com/example/fixture','products':['fixture'],'paths':{'content':'target/content','source_content':'upstream/content'},'pins':{'olp':{'repository':'https://github.com/OpenLogicProject/OpenLogic','commit':self.pin}},'conversion':{'source_manifest':'historical-manifest.json','source_manifest_sha256':'a'*64,'attribution_policy':'preserve-recorded-else-unresolved'}}

    def write(self):
        (self.repo/'olp-edition.toml').write_bytes(render_edition(self.data).encode())
        (self.repo/'units.jsonl').write_bytes((''.join(json.dumps(x)+'\n' for x in self.rows)).encode())

    def validate(self):
        self.write()
        with contextlib.redirect_stdout(io.StringIO()):
            return validate_edition(self.repo,None,self.source/'.git')

    def test_matching_sources_and_targets(self):
        result=self.validate();self.assertEqual(result['matched'],2)
        self.assertEqual(result['unresolved_attribution'],2)

    def test_unknown_key_names_the_typo(self):
        self.data['paths']['contnet']='elsewhere'
        with self.assertRaisesRegex(ValueError,'contnet'):self.validate()

    def test_target_tampering_rejected(self):
        path=self.repo/'target'/self.rows[0]['path'];path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'translated file differs'):self.validate()

    def test_missing_unit_rejected(self):
        self.rows.pop()
        with self.assertRaisesRegex(ValueError,'omits or adds'):self.validate()

    def test_source_tampering_rejected(self):
        path=self.repo/'upstream'/self.rows[0]['path'];path.write_bytes(b'not the pinned source')
        with self.assertRaisesRegex(ValueError,'source differs'):self.validate()

    def test_model_and_effort_are_a_pair(self):
        row=copy.deepcopy(self.rows[0]);row['by']['effort']='ultra'
        with self.assertRaises(ValueError):validate_schema('unit',row)

    def test_paths_cannot_escape(self):
        for path in ['../secrets','/absolute','C:/outside',r'..\outside']:
            with self.subTest(path=path), self.assertRaises(ValueError):safe_path(self.repo,path)

    def test_nonstandard_engine_needs_reason(self):
        self.data['engine']='xelatex'
        with self.assertRaisesRegex(ValueError,'engine_reason'):self.validate()

    def test_declared_current_cannot_hide_stale_blob(self):
        self.rows[0]['src_blob']='a'*40
        with self.assertRaisesRegex(ValueError,'declared state'):self.validate()


if __name__=='__main__':unittest.main()
