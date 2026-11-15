from copy import deepcopy
import unittest
from olpkit.vendored import compare_files
from olpkit.schemas import validate_schema


class VendoredTests(unittest.TestCase):
    def setUp(self):
        self.base={'content/unit.tex':b'original','unused.tex':b'not vendored'}
        self.component={'source':'photos','mount':'assets/photos','commit':'a'*40,
                        'files':{'photo.png':b'IMAGE','README.md':b'Credit'}}
        self.actual={'content/unit.tex':b'original','assets/photos/photo.png':b'IMAGE','assets/photos/README.md':b'Credit'}

    def test_explicit_complete_component_and_base_subset_pass(self):
        result=compare_files(self.actual,self.base,[self.component])
        self.assertTrue(result['pass']);self.assertEqual(result['counts'],{'olp':1,'photos':2})

    def test_undeclared_extra_is_not_ignored(self):
        self.assertFalse(compare_files(self.actual,self.base,[])['pass'])
        self.actual['assets/photos/unknown.txt']=b'extra'
        self.assertFalse(compare_files(self.actual,self.base,[self.component])['pass'])

    def test_missing_credit_and_changed_bytes_fail(self):
        del self.actual['assets/photos/README.md']
        self.assertFalse(compare_files(self.actual,self.base,[self.component])['pass'])
        self.actual['assets/photos/README.md']=b'Altered credit'
        self.assertFalse(compare_files(self.actual,self.base,[self.component])['pass'])

    def test_overlapping_components_and_unsafe_paths_fail(self):
        other={**self.component,'mount':'assets/photos/nested'}
        with self.assertRaisesRegex(ValueError,'overlapping'):compare_files(self.actual,self.base,[self.component,other])
        other['mount']='../outside'
        with self.assertRaises(ValueError):compare_files(self.actual,self.base,[other])

    def test_empty_tree_is_not_a_success(self):
        self.assertFalse(compare_files({},self.base,[])['pass'])

    def test_subset_selection_requires_explicit_evidence_and_unique_members(self):
        declaration={k:self.component[k] for k in ['source','mount','commit']}
        declaration['members']=['photo.png','README.md']
        with self.assertRaises(ValueError):validate_schema('vendored-components',[declaration])
        declaration['selection_evidence']={'repository':'https://example.invalid/source','commit':'b'*40,'path':'assets/photos'}
        validate_schema('vendored-components',[declaration])
        declaration['members'].append('photo.png')
        with self.assertRaises(ValueError):validate_schema('vendored-components',[declaration])


if __name__=='__main__':unittest.main()
