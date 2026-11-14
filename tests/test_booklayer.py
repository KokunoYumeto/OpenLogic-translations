from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from olpkit.booklayer import bind_book_units, check_assembled_book_layer, validate_book_contract
from olpkit.edition import git_blob
from olpkit.schemas import ROOT, validate_schema


def sha(b):return hashlib.sha256(b).hexdigest()


class BookLayerTests(unittest.TestCase):
    def setUp(self):
        boundary=ROOT.parent/'out/tests';boundary.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='booklayer-',dir=boundary)
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.source={'include/preface.tex':b'Original prose.', 'include/summary-1.tex':b'Original summary.',
                     'book.bib':b'Unchanged citation', 'reader.tex':b'Native driver'}
        self.target={'courses/example/'+p:b.replace(b'Original',b'Translated')
                     for p,b in self.source.items() if p!='reader.tex'}
        self.contract={'schema_version':1,'id':'example','source_id':'ex',
                       'repository':'https://example.invalid/book','commit':'a'*40,
                       'drivers':['reader.tex'],'book_units':['include/*.tex','book.bib'],
                       'imports_lock':'imports.lock','credits':[]}
        self.edition={'pins':{'ex':{'repository':self.contract['repository'],'commit':'a'*40}}}
        self.profile={'book':'example','source_id':'ex'}
        (self.root/'review.json').write_bytes(b'Private canon and choices')
        self.rows=[{'id':'EX:'+p,'source_revision':'a'*40,'source_git_blob':git_blob(b),
                    'source_sha256':sha(b),'target_path':'courses/example/'+p,
                    'target_sha256':sha(self.target['courses/example/'+p]),
                    'disposition':'retained-verbatim' if p=='book.bib' else 'translated',
                    'model':'test-model','reasoning_effort':'ultra',
                    'private_review_record':'review.json','private_review_sha256':sha(b'Private canon and choices')}
                   for p,b in self.source.items() if p!='reader.tex']

    def bind(self):
        return bind_book_units(self.contract,self.source,self.target,
                               '\n'.join(json.dumps(r) for r in self.rows).encode(),
                               self.root,'courses/example')

    def test_exact_coverage_keeps_attribution_and_excludes_private_text(self):
        report=self.bind();self.assertEqual(report['coverage'],3)
        self.assertEqual(report['private_review_files_checked'],1)
        self.assertNotIn('Private canon',json.dumps(report))
        self.assertEqual(report['units'][0]['effort'],'ultra')
        self.assertIn('not established',report['linguistic_acceptance'])

    def test_missing_duplicate_or_foreign_units_cannot_pass(self):
        rows=deepcopy(self.rows)
        for replacement in (rows[:-1],rows+[rows[0]],[{**r,'id':r['id'].replace('EX:','SLC:')} for r in rows]):
            self.rows=replacement
            with self.subTest(rows=len(replacement)),self.assertRaises(ValueError):self.bind()

    def test_source_target_and_review_changes_fail_independently(self):
        for field,value in [('source_revision','b'*40),('source_git_blob','b'*40),
                            ('source_sha256','b'*64),('target_sha256','b'*64),
                            ('private_review_sha256','b'*64),('target_path','courses/other/include/preface.tex'),
                            ('model',None),('reasoning_effort',None)]:
            original=self.rows[0][field];self.rows[0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.bind()
            self.rows[0][field]=original

    def test_retained_label_cannot_excuse_changed_bytes(self):
        self.rows[0]['disposition']='retained-verbatim'
        with self.assertRaisesRegex(ValueError,'retained book unit changed'):self.bind()

    def test_wrong_book_pin_and_reduced_unit_patterns_fail(self):
        registered=deepcopy(self.contract)
        validate_book_contract(self.contract,registered,self.edition,self.profile)
        self.contract['book_units']=['book.bib']
        with self.assertRaisesRegex(ValueError,'registered book_units'):
            validate_book_contract(self.contract,registered,self.edition,self.profile)
        self.contract=registered;self.edition['pins']['ex']['commit']='b'*40
        with self.assertRaisesRegex(ValueError,'pins differ'):
            validate_book_contract(self.contract,registered,self.edition,self.profile)

    def test_final_tree_must_contain_every_unchanged_target(self):
        report=self.bind();files={p.replace('courses/','locale/xx/courses/',1):b for p,b in self.target.items()}
        check_assembled_book_layer(report,files,'locale/xx/courses/example')
        files['locale/xx/courses/example/include/preface.tex']+=b' changed'
        with self.assertRaisesRegex(ValueError,'not preserved'):
            check_assembled_book_layer(report,files,'locale/xx/courses/example')

    def test_no_match_pattern_and_private_path_escape_fail(self):
        self.contract['book_units'].append('missing.tex')
        with self.assertRaisesRegex(ValueError,'matches no source'):self.bind()
        self.contract['book_units'].pop();self.rows[0]['private_review_record']='../outside.json'
        with self.assertRaises(ValueError):self.bind()

    def test_profile_requires_one_provenance_contract(self):
        p=json.loads((ROOT/'data/assembly/mr.json').read_bytes())
        validate_schema('assembly-profile',p)
        p['book_contract']='courses/example/book.toml'
        with self.assertRaises(ValueError):validate_schema('assembly-profile',p)
        del p['manifest'];del p['manifest_pins'];validate_schema('assembly-profile',p)
        del p['book_contract']
        with self.assertRaises(ValueError):validate_schema('assembly-profile',p)


if __name__=='__main__':unittest.main()
