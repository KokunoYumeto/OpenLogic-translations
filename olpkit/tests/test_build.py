from pathlib import Path
from copy import deepcopy
import json
import tempfile
import unittest

from olpkit.build import log_checks,bibliography_key,verify_assembly
from olpkit.recorder import read_inputs,content_inputs,compare_imports,load_imports
from olpkit.assembly import digest
from olpkit.schemas import ROOT,validate_schema


class BuildLogicTests(unittest.TestCase):
    def test_reference_contract_rejects_unknown_fields_moving_refs_and_escapes(self):
        original=json.loads((ROOT/'data/build-products/slc-screen-pdf.json').read_text())
        validate_schema('build-product',original)
        for where,key,value in [(None,'unexpected',True),('reference_pins','slc','main'),
                                ('reference_dependency','repository','../other'),
                                ('reference_dependency','files',['../secret']),
                                ('reference_mounts','slc','C:/outside')]:
            changed=deepcopy(original)
            (changed[where] if where else changed)[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):
                validate_schema('build-product',changed)

    def test_settled_log_has_no_errors_and_counts_both_box_types(self):
        result=log_checks('Overfull \\hbox (1.2pt too wide)\nOverfull \\vbox (2.01pt too high)')
        self.assertEqual(result['issues'],[]);self.assertEqual(result['overfull_count'],2)
        self.assertEqual(result['overfull_over_2pt'],[2.01])

    def test_wrapped_warnings_and_missing_glyphs_are_not_lost(self):
        text='Token x\n undefined. File requested but\n not marked xx. Missing character: X\nLaTeX Warning: Reference `a` undefined\nLabel(s) may have changed'
        self.assertEqual(set(log_checks(text)['issues']),{'undefined_token','unmarked_import','missing_character','undefined_reference','rerun'})

    def test_bibtex_is_not_repeated_for_only_page_label_changes(self):
        first='\\citation{A}\n\\bibdata{source}\n\\bibstyle{plain}\n\\newlabel{x}{{1}{2}}'
        self.assertEqual(bibliography_key(first),bibliography_key(first.replace('{2}','{3}')))
        self.assertNotEqual(bibliography_key(first),bibliography_key(first.replace('{A}','{B}')))

    def test_recorded_set_detects_wrong_language_and_missing_units(self):
        root=Path('C:/olp-build/out/fixture').resolve()
        files=[root/'locale/xx/content/a.tex',root/'content/b.tex',root/'sty/code.sty']
        found,wrong=content_inputs(files,root,'xx')
        result=compare_imports(found,wrong,[('OLP-0001','content/a.tex'),('OLP-0002','content/b.tex')])
        self.assertFalse(result['pass']);self.assertEqual(wrong,['content/b.tex'])
        good,wrong=content_inputs([files[0]],root,'xx')
        self.assertTrue(compare_imports(good,wrong,[('OLP-0001','content/a.tex')])['pass'])
        self.assertFalse(compare_imports(good,wrong,[('OLP-0002','content/b.tex')])['pass'])

    def test_recorder_resolves_duplicate_relative_inputs_once(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='recorder-',dir=boundary) as d:
            p=Path(d);(p/'x.fls').write_text('PWD '+p.as_posix()+'\nINPUT a.tex\nINPUT ./a.tex\nOUTPUT result.pdf\n')
            self.assertEqual(read_inputs(p/'x.fls',p),[(p/'a.tex').resolve()])
            (p/'a.tex').write_bytes(b'original');report={'files':{'a.tex':{'sha256':digest(b'original')}}}
            verify_assembly(p,report);(p/'a.tex').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'assembled input changed'):verify_assembly(p,report)
            (p/'imports.lock').write_text('OLP-0001\tcontent/a.tex\nOLP-0001\tcontent/b.tex\n')
            with self.assertRaisesRegex(ValueError,'duplicate'):load_imports(p/'imports.lock')


if __name__=='__main__':unittest.main()
