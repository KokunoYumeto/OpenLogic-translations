import json
from pathlib import Path
import shutil
import tempfile
import unittest

from olpkit.shims import apply_shims,load_shims


class ShimTests(unittest.TestCase):
    def setUp(self):
        self.boundary=Path('C:/olp-build/out/tests').resolve()
        self.boundary.mkdir(parents=True,exist_ok=True)
        self.folder=Path(tempfile.mkdtemp(prefix='shims-',dir=self.boundary))
        self.context={'locale':'zz','script':'Latn','engine':'lualatex'}
        self.record={'id':'sample-shim','path':'sty/source.sty','before':'OLD','after':'NEW',
                     'conditions':[self.context],'reason':'Fixture for exact source patching.',
                     'evidence':['https://github.com/example/repo/blob/'+'a'*40+'/file']}
        self.write()

    def write(self):
        lines=[]
        for key,value in self.record.items():
            if key=='conditions':continue
            lines.append(key+' = '+json.dumps(value,ensure_ascii=False))
        for condition in self.record['conditions']:
            lines.append('\n[[conditions]]')
            lines.extend(k+' = '+json.dumps(v) for k,v in condition.items())
        (self.folder/'sample.toml').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    def tearDown(self):
        self.assertEqual(self.folder.resolve().parent,self.boundary)
        self.assertTrue(self.folder.name.startswith('shims-'))
        shutil.rmtree(self.folder)

    def test_exactly_once_with_input_immutable(self):
        original={'sty/source.sty':b'prefix OLD suffix','content/example.tex':b'untouched'}
        result,receipts=apply_shims(original,self.context,self.folder)
        self.assertEqual(result['sty/source.sty'],b'prefix NEW suffix')
        self.assertEqual(original['sty/source.sty'],b'prefix OLD suffix')
        self.assertEqual(result['content/example.tex'],b'untouched')
        self.assertEqual(receipts[0]['matches'],1)

    def test_missing_or_repeated_text_names_shim(self):
        for data in [b'absent',b'OLD OLD',b'NEW']:
            with self.subTest(data=data),self.assertRaisesRegex(ValueError,'sample-shim: expected exactly one'):
                apply_shims({'sty/source.sty':data},self.context,self.folder)

    def test_other_engine_or_script_not_patched(self):
        for field,value in [('engine','xelatex'),('script','Arab'),('locale','xx')]:
            original={'sty/source.sty':b'OLD'}
            output,receipts=apply_shims(original,{**self.context,field:value},self.folder)
            self.assertEqual(original,output)
            self.assertEqual(receipts,[])

    def test_unknown_key_is_rejected(self):
        self.record['reasom']='typo'
        self.write()
        with self.assertRaisesRegex(ValueError,'reasom'):
            load_shims(self.folder)

    def test_path_escape_rejected(self):
        self.record['path']='../source.sty'
        self.write()
        with self.assertRaisesRegex(ValueError,'unsafe'):
            load_shims(self.folder)

    def test_missing_file_is_not_silently_skipped(self):
        with self.assertRaisesRegex(ValueError,'sample-shim: upstream file absent'):
            apply_shims({},self.context,self.folder)


if __name__=='__main__':unittest.main()
