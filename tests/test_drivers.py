from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import tomllib
import unittest

from olpkit.drivers import generate_drivers,write_drivers
from olpkit.edition import ROOT,render_edition


class DriverTests(unittest.TestCase):
    def setUp(self):
        boundary=(ROOT.parent/'out/tests').resolve();boundary.mkdir(parents=True,exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(prefix='drivers-',dir=boundary)
        self.root=Path(self.temporary.name)
        def cleanup():
            if self.root.resolve().parent!=boundary:raise ValueError('test directory escaped its boundary')
            self.temporary.cleanup()
        self.addCleanup(cleanup)
        self.data=self.root/'data'
        for part in ['books','languages','preambles']:
            shutil.copytree(ROOT/'data'/part,self.data/part)
        self.sources={name:(ROOT/'tests/fixtures/slc'/name).read_bytes() for name in ['slc.tex','slc-screen.tex']}

    def edition(self,locale):
        adapter=tomllib.loads((ROOT/'data/imports'/(locale+'.toml')).read_text(encoding='utf-8'))
        fields={k:adapter[k] for k in ['locale','language_tag','script','babel','engine','repository']}
        fields.update(schema_version=1,products=['slc-screen-pdf'],paths={'content':'content','source_content':'upstream/content'},
                      pins={'olp':{'repository':'https://github.com/OpenLogicProject/OpenLogic','commit':'a'*40},**adapter['pins']},
                      conversion={'source_manifest':'manifest.json','source_manifest_sha256':'a'*64,'attribution_policy':'preserve-recorded-else-unresolved'})
        if 'engine_reason' in adapter:fields['engine_reason']=adapter['engine_reason']
        return fields

    def generate(self,locale='gu',edition=None,sources=None):
        return generate_drivers(edition or self.edition(locale),sources or self.sources,data_root=self.data)

    def test_driver_code_is_shared_and_locale_values_are_in_preambles(self):
        jv,jv_report=self.generate('jv');gu,gu_report=self.generate('gu')
        for name in ['slc.tex','slc-screen.tex']:
            self.assertEqual(jv[name],gu[name])
            for locale,outputs in [('jv',jv),('gu',gu)]:
                profile=tomllib.loads((self.data/'languages'/(locale+'.toml')).read_text(encoding='utf-8'))
                for value in profile['strings'].values():self.assertNotIn(value.encode(),outputs[name])
                for font in profile['fonts'].values():
                    for field in ['file','name']:
                        if field in font:self.assertNotIn(font[field].encode(),outputs[name])
        self.assertNotEqual(jv['olpkit-after-olp.tex'],gu['olpkit-after-olp.tex'])
        self.assertEqual(jv_report['untranslated_driver_labels'],0)
        self.assertEqual(gu_report['untranslated_driver_labels'],0)
        self.assertEqual(len(gu_report['transformations']),10)
        self.assertIn(b'{0.245}',jv['olpkit-after-olp.tex'])
        self.assertIn(b'{0.26}',gu['olpkit-after-olp.tex'])
        self.assertIn(b'{0.29}',gu['olpkit-after-olp.tex'])

    def test_source_imports_are_preserved_except_explicit_about_route(self):
        outputs,_=self.generate()
        source=self.sources['slc.tex'].decode().replace(r'\olpath/content/open-logic-about',r'\olpath/locale/\ollangid/content/open-logic-about')
        pattern=r'\\olimport[^\n]+'
        self.assertEqual(re.findall(pattern,source),re.findall(pattern,outputs['slc.tex'].decode()))

    def test_bengali_native_policy_does_not_replace_other_locales(self):
        bn,bn_report=self.generate('bn');jv,jv_report=self.generate('jv');gu,gu_report=self.generate('gu')
        self.assertEqual(bn_report['policy'],'books/sets-logic-computation-bn-drivers.toml')
        self.assertEqual(jv_report['policy'],gu_report['policy'])
        self.assertEqual(jv_report['policy'],'books/sets-logic-computation-drivers.toml')
        self.assertIn(b'../../../../sty/open-logic-book',bn['slc-screen.tex'])
        self.assertIn(b'\\quad',bn['slc-screen.tex'])
        self.assertIn(b'\\AddToHook{begindocument/end}',bn['olpkit-after-olp.tex'])
        self.assertIn(b'{684106}',bn['olpkit-after-olp.tex'])
        self.assertEqual(bn_report['untranslated_driver_labels'],0)
        self.assertEqual(jv['slc-screen.tex'],gu['slc-screen.tex'])

    def test_locale_policy_path_cannot_escape_book_data(self):
        p=self.data/'books/sets-logic-computation.toml'
        p.write_text(p.read_text().replace('sets-logic-computation-bn-drivers.toml','../../private.toml'))
        with self.assertRaisesRegex(ValueError,'book:'):self.generate('bn')

    def test_upstream_change_requires_explicit_policy_review(self):
        sources={**self.sources,'slc.tex':self.sources['slc.tex']+b'\\chapter{New reader text}\n'}
        with self.assertRaisesRegex(ValueError,'upstream driver changed'):
            self.generate(sources=sources)

    def test_missing_translation_is_not_replaced_with_english(self):
        p=self.data/'languages/gu.toml'
        text=p.read_text(encoding='utf-8')
        p.write_text(re.sub(r'^summary = .*\n','',text,flags=re.M),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'summary'):
            self.generate()

    def test_unknown_profile_key_is_rejected(self):
        p=self.data/'languages/gu.toml'
        p.write_text('engien = "lualatex"\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'engien'):
            self.generate()

    def test_low_contrast_profile_is_rejected_before_build(self):
        p=self.data/'languages/gu.toml'
        p.write_text(p.read_text(encoding='utf-8').replace('color = "0B3C6F"','color = "FFFFFF"'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'contrast'):
            self.generate()

    def test_font_override_requires_reason_and_is_used(self):
        edition=self.edition('gu')
        edition['fonts']={'main':{'file':'ChangedFixtureFont.ttf'}}
        with self.assertRaisesRegex(ValueError,'explicit reason'):
            self.generate(edition=edition)
        edition['overrides']=[{'field':'fonts.main.file','reason':'Synthetic override test only.'}]
        outputs,_=self.generate(edition=edition)
        self.assertIn(b'ChangedFixtureFont.ttf',outputs['olpkit-before-olp.tex'])

    def test_check_detects_one_character_edit(self):
        outputs,report=self.generate();folder=self.root/'generated'
        with contextlib.redirect_stdout(io.StringIO()):
            write_drivers(outputs,report,folder)
            write_drivers(outputs,report,folder,check=True)
        path=folder/'slc.tex';path.write_bytes(path.read_bytes()+b'x')
        with self.assertRaisesRegex(ValueError,'generated driver differs: slc.tex'):
            write_drivers(outputs,report,folder,check=True)

    def test_missing_transform_anchor_names_the_rule(self):
        p=self.data/'books/sets-logic-computation-drivers.toml'
        text=p.read_text(encoding='utf-8').replace('Summary','ChangedAnchor')
        p.write_text(text,encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'slc.tex/summary: expected'):
            self.generate()

    def test_output_cannot_overwrite_source_checkout(self):
        outputs,report=self.generate()
        with self.assertRaisesRegex(ValueError,'named child'):
            write_drivers(outputs,report,ROOT)

    def test_book_preamble_override_changes_only_that_book_policy(self):
        original,_=self.generate('mr')
        path=self.data/'books/sets-logic-computation-mr-drivers.toml'
        path.write_text(path.read_text(encoding='utf-8')+'\n[preamble]\nafter_olp = ["fixture-book.tex"]\n',encoding='utf-8')
        (self.data/'preambles/fixture-book.tex').write_bytes(b'% Different book; same language.\n')
        changed,report=self.generate('mr')
        self.assertEqual(changed['olpkit-after-olp.tex'],b'% Different book; same language.\n')
        self.assertEqual(original['olpkit-before-olp.tex'],changed['olpkit-before-olp.tex'])
        self.assertEqual(original['slc.tex'],changed['slc.tex'])
        self.assertTrue(any(r['path']=='preambles/fixture-book.tex' for r in report['templates']))
        path.write_text(path.read_text(encoding='utf-8').replace('fixture-book.tex','../private.tex'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'driver-policy'):self.generate('mr')


if __name__=='__main__':unittest.main()
