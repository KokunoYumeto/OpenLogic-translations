import copy
import json
import unittest

from olpkit.assembly import digest
from olpkit.edition import git_blob
from olpkit.syncedition import checked_delta, make_packets, term_rows


class SyncEditionTests(unittest.TestCase):
    def setUp(self):
        self.path='content/a.tex'
        self.old={self.path:b'An injective map.', 'sty/style.sty':b'old style'}
        self.new={self.path:b'An injective function.', 'sty/style.sty':b'new style'}
        self.plan={'schema':'olpkit.upstream-delta.v1','from':'a'*40,'to':'b'*40,'files':[]}
        for path in self.old:
            self.plan['files'].append({'path':path,'old_path':path,'status':'M',
                'kind':'content_unit' if path.startswith('content/') else 'build_file',
                'unit_id':'OLP-0001' if path.startswith('content/') else None,
                'old_sha256':digest(self.old[path]),'new_sha256':digest(self.new[path]),
                'old_blob':git_blob(self.old[path]),'new_blob':git_blob(self.new[path]),
                'hunks':'--- old\n+++ new\n@@ -1 +1 @@\n-An injective map.\n+An injective function.\n'})
        self.edition={'pins':{'olp':{'commit':'a'*40}},'paths':{'content':'xx/content','orthography':'lang/orthography.json'}}
        self.target=b'Existing justified translation.'
        self.units=[{'src':'olp','state':'current','path':self.path,'id':'OLP-0001',
                    'tr_sha256':digest(self.target),'src_blob':git_blob(self.old[self.path])}]
        self.terms=b'english\ttarget\tsource\ninjective\tlocal term\tcanon passage\nmap\tsecond term\tanother passage\n'

    def test_packets_preserve_exact_target_and_do_not_choose_disposition(self):
        packets,summary=make_packets(self.plan,self.edition,self.units,{'xx/content/a.tex':self.target},
                                    self.old,self.new,self.terms,b'{"rules":[]}')
        p=json.loads(packets['packets/OLP-0001.json'])
        self.assertEqual(p['target_text'],self.target.decode())
        self.assertEqual(p['target_sha256'],digest(self.target));self.assertIsNone(p['disposition'])
        self.assertEqual(p['source_before'],self.old[self.path].decode())
        self.assertEqual(p['source_after'],self.new[self.path].decode())
        self.assertEqual(len(p['relevant_terms']),2);self.assertEqual(len(summary),1)
        self.assertNotIn('canon_used',p)

    def test_term_matching_ignores_diff_headers_context_and_substrings(self):
        t=b'english\ttarget\nmap\tx\ninjective\ty\n'
        h='--- map\n+++ map\n injective context\n-mapping\n+injection\n'
        self.assertEqual(term_rows(t,h),[])
        self.assertEqual(len(term_rows(t,'-A MAP\n')),1)

    def test_malformed_termbase_cannot_silently_drop_context(self):
        for body in [b'en\ttarget\nmap\tx\n',b'english\ttarget\nmap\n',b'english\ttarget\n\tx\n']:
            with self.assertRaises(ValueError):term_rows(body,'+map')

    def test_plan_must_include_the_build_change_and_exact_source_bytes(self):
        plan=copy.deepcopy(self.plan);plan['files'].pop()
        with self.assertRaisesRegex(ValueError,'exact upstream change set'):
            checked_delta(plan,self.old,self.new)
        plan=copy.deepcopy(self.plan);plan['files'][0]['new_blob']='0'*40
        with self.assertRaisesRegex(ValueError,'bytes differ'):
            checked_delta(plan,self.old,self.new)

    def test_wrong_starting_pin_or_modified_target_is_rejected(self):
        edition=copy.deepcopy(self.edition);edition['pins']['olp']['commit']='c'*40
        with self.assertRaisesRegex(ValueError,'starting pin'):
            make_packets(self.plan,edition,self.units,{'xx/content/a.tex':self.target},self.old,self.new,self.terms,b'{}')
        with self.assertRaisesRegex(ValueError,'differs from current ledger'):
            make_packets(self.plan,self.edition,self.units,{'xx/content/a.tex':b'changed'},self.old,self.new,self.terms,b'{}')

    def test_duplicates_and_unsupported_renames_fail_before_writing(self):
        plan=copy.deepcopy(self.plan);plan['files'].append(plan['files'][0])
        with self.assertRaisesRegex(ValueError,'duplicate'):
            checked_delta(plan,self.old,self.new)
        plan=copy.deepcopy(self.plan);plan['files'][0]['status']='R100'
        with self.assertRaisesRegex(ValueError,'migration handling'):
            checked_delta(plan,self.old,self.new)


if __name__=='__main__':unittest.main()
