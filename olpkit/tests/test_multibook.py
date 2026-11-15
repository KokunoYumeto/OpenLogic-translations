from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from olpkit.assembly import digest,json_bytes
from olpkit.build import build_job,load_build_product,reference_tree,_compile_book
from olpkit.importlock import pin_key,select_lock,write_lock
from olpkit.schemas import ROOT


class MultiBookTests(unittest.TestCase):
    def setUp(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='multibook-',dir=boundary)
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def test_each_product_resolves_its_own_source_driver_and_pin(self):
        slc,slc_book=load_build_product('slc-screen-pdf')
        il,il_book=load_build_product('il-screen-pdf')
        self.assertEqual(slc_book['source_id'],'slc')
        self.assertEqual(il_book['source_id'],'il')
        self.assertEqual(build_job({}),'slc-screen')
        self.assertEqual(build_job(il),'il-screen')
        self.assertNotEqual(slc_book['commit'],il_book['commit'])
        self.assertEqual(il['reference_pins']['il'],il_book['commit'])

    def fixture_data(self):
        data=self.root/'data';(data/'build-products').mkdir(parents=True)
        (data/'books').mkdir()
        for name in ['sources.toml','books/intermediate-logic.toml','build-products/il-screen-pdf.json']:
            shutil.copyfile(ROOT/'data'/name,data/name)
        return data

    def test_cross_book_pin_driver_and_mount_cannot_be_silently_substituted(self):
        data=self.fixture_data();path=data/'build-products/il-screen-pdf.json'
        original=json.loads(path.read_bytes())
        for where,key,value in [('reference_pins','il','1'*40),
                                ('reference_mounts','il','courses/sets-logic-computation'),
                                (None,'driver','slc-screen.tex')]:
            changed=deepcopy(original);(changed[where] if where else changed)[key]=value
            path.write_bytes(json_bytes(changed))
            with self.subTest(field=key),self.assertRaises(ValueError):load_build_product('il-screen-pdf',data)
        changed=deepcopy(original);changed['reference_pins']['unknown']=changed['reference_pins'].pop('il')
        path.write_bytes(json_bytes(changed))
        with self.assertRaisesRegex(ValueError,'registered book'):load_build_product('il-screen-pdf',data)

    def test_unsafe_product_and_driver_paths_are_rejected(self):
        for product in ['../outside','C:/other','il-screen-pdf.json']:
            with self.subTest(product=product),self.assertRaises(ValueError):load_build_product(product)
        for driver in ['../reader.tex','sub/il.tex','il.tex -shell-escape',None]:
            with self.subTest(driver=driver),self.assertRaises(ValueError):build_job({'driver':driver})

    def test_lock_identity_includes_book_source_even_when_all_hashes_are_equal(self):
        common={k:'a'*40 for k in ('olp','photos','portraits')}
        slc={**common,'slc':'b'*40};il={**common,'il':'b'*40}
        self.assertNotEqual(pin_key(slc),pin_key(il))
        # The historical four-pin key remains exactly unchanged.
        self.assertEqual(pin_key(slc),digest(json_bytes(slc)))
        for bad in [common,{**common,'unknown':'b'*40},{**slc,'il':'b'*40},
                    {**il,'photos':'main'},{**il,'photos':None}]:
            with self.subTest(pins=bad),self.assertRaises(ValueError):pin_key(bad)

    def test_identical_unit_lists_do_not_make_an_slc_witness_an_il_witness(self):
        common={k:'a'*40 for k in ('olp','photos','portraits')}
        body=b'OLP-0001\tcontent/open-logic-about.tex\n'
        pins={**common,'slc':'b'*40}
        meta={'schema':'olpkit.imports.v1','pins':pins,'lock_sha256':digest(body),
              'units':1,'recorder_sha256':'1'*64,'reference_pdf_sha256':'2'*64}
        original=write_lock(self.root/'locks',body,meta)
        with self.assertRaisesRegex(ValueError,'no import lock'):
            select_lock(self.root/'locks',{**common,'il':'b'*40})
        self.assertEqual(select_lock(self.root/'locks',pins)[0],original)

    def test_reference_assembly_routes_to_il_and_preserves_book_bytes(self):
        data,book=load_build_product('il-screen-pdf')
        il_bytes=b'\\input{il}\n'
        def require(source,pin):
            folder=self.root/'cache'/source;folder.mkdir(parents=True)
            content={data['driver']:il_bytes,'includeonly.tex':b''} if source=='il' else {'witness.txt':source.encode()}
            for name,body in content.items():(folder/name).write_bytes(body)
            return folder,{'files':content}
        with patch('olpkit.build.SourceCache') as cache, patch('olpkit.build.GitSnapshot', side_effect=AssertionError('unexpected edition checkout')):
            cache.return_value.require.side_effect=require
            output=self.root/'assembled'
            report=reference_tree(self.root/'cache','a'*40,output,product='il-screen-pdf')
        self.assertEqual(report['driver'],'il-screen.tex')
        self.assertEqual(report['book_directory'],'courses/intermediate-logic')
        self.assertEqual((output/report['book_directory']/report['driver']).read_bytes(),il_bytes)
        for path in data['reference_dependency']['files']:
            name = report['book_directory'] + '/' + Path(path).name
            body = (output / name).read_bytes()
            self.assertIn(b'LaTeX Project Public License', body)
            self.assertEqual(report['files'][name]['sha256'], digest(body))
        self.assertEqual(set(report['pins']),{'olp','il','photos','portraits'})
        self.assertFalse((output/'courses/sets-logic-computation').exists())

    def test_occupied_slot_creates_no_tex_command_for_the_new_driver(self):
        source=self.root/'source';book=source/'courses/intermediate-logic';book.mkdir(parents=True)
        body=b'\\input{il}\n';(book/'il-screen.tex').write_bytes(body)
        report={'book_directory':'courses/intermediate-logic','driver':'il-screen.tex',
                'files':{'courses/intermediate-logic/il-screen.tex':{'sha256':digest(body)}}}
        with patch('olpkit.build.TeXSlot') as slot,patch('olpkit.build.run_job') as job:
            slot.return_value.__enter__.return_value.acquired=False
            slot.return_value.__enter__.return_value.abandoned=False
            result=_compile_book(source,report,'pdflatex',42,self.root,reference=True)
        job.assert_not_called();self.assertEqual(result['status'],'slot_occupied')
        self.assertEqual(result['commands'],[])
        self.assertFalse((book/'slc-screen.tex').exists())


if __name__=='__main__':unittest.main()
