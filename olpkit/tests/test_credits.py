import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from reportlab.pdfgen import canvas
from olpkit.assembly import digest,json_bytes
from olpkit.credits import inspect_credits,CATEGORIES,rebind_source_links,previous_credit_policy


class CreditTests(unittest.TestCase):
    def test_rebinds_only_exact_source_urls_and_their_matching_printed_labels(self):
        upstream = "https://github.com/example/source"
        old, new = "ab" * 20, "cd" * 20
        for n in (7, 8, 12, 40):
            with self.subTest(length=n):
                before = rf"\href{{{upstream}/tree/{old}}}{{{old[:n]}}}"
                after = rf"\href{{{upstream}/tree/{new}}}{{{new[:n]}}}"
                notice = f"Translator {old[:n]}: {before}.\n{upstream}/blob/{old}/COPYING"
                expected = f"Translator {old[:n]}: {after}.\n{upstream}/blob/{new}/COPYING"
                self.assertEqual(rebind_source_links(notice.encode(), upstream, old, new),
                                 (expected.encode(), {old[:n]}))
        notice = rf"\href{{{upstream}/tree/{old}}}{{editions}}; {upstream}/tree/{old}x"
        self.assertEqual(rebind_source_links(notice.encode(), upstream, old, new),
                         (notice.replace(old+"}", new+"}").encode(), set()))

    def test_released_credit_checks_identify_the_full_pinned_policy(self):
        (self.root / "web").mkdir()
        prior = self.root / "full-policy.json"
        prior.write_bytes(json_bytes(self.policy))
        checks = {"components": [{"id": c["id"], "reader_checks": c["reader_checks"]}
                                 for c in self.policy["components"]]}
        subset = self.root / "web/credits.json"
        def save_subset(value):
            subset.write_bytes(json_bytes(value))
            names = ("web/credits.json", "source/ASSEMBLY.json")
            (self.root / "WEB-EDITION.json").write_bytes(json_bytes({
                "inputs": {k: digest((self.root / k).read_bytes()) for k in names}}))
        save_subset(checks)
        with patch("olpkit.credits.edition_credit_paths", return_value=(prior, self.root / "unused")):
            self.assertEqual(previous_credit_policy(self.root), self.policy)
            save_subset({"components": []})
            with self.assertRaisesRegex(ValueError, "registered policy"):
                previous_credit_policy(self.root)
            subset.write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "release manifest"):
                previous_credit_policy(self.root)

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir()
        self.policy={'schema_version':1,'locale':'test','product':'slc-screen-pdf','pins':{'olp':'a'*40},'components':[]}
        files={}
        for cat in sorted(CATEGORIES):
            name=cat+'.txt';data=('Full notice for '+cat).encode();(self.source/name).write_bytes(data)
            files[name]={'sha256':digest(data),'bytes':len(data)}
            self.policy['components'].append({'id':cat,'category':cat,'state':'specified','reason':'Fixture witness',
                'files':[{'path':name,'sha256':digest(data),'witness':'https://example.org/'+name}],
                'reader_checks':[{'id':cat,'all_of':['Full notice for '+cat]}]})
        self.assembly={'locale':'test','product':'slc-screen-pdf','sources':{'olp':{'commit':'a'*40}},'files':files}
        (self.source/'ASSEMBLY.json').write_bytes(json_bytes(self.assembly))
        self.pdf=self.root/'book.pdf';c=canvas.Canvas(str(self.pdf))
        for i,cat in enumerate(sorted(CATEGORIES)):c.drawString(40,750-i*20,'Full notice for '+cat)
        c.save()
        self.build=self.root/'BUILD.json';self.receipt={'pdf':{'path':'book.pdf','sha256':digest(self.pdf.read_bytes())},'commands':[{'exit_code':0,'timed_out':False}],
            'assembly_sha256':digest(json_bytes(self.assembly)),'source_inputs':files}
        self.build.write_bytes(json_bytes(self.receipt))

    def run_check(self,policy=None,pdf=True,build=True):
        return inspect_credits(self.source,policy or self.policy,self.pdf if pdf else None,self.build if build else None)

    def test_actual_notices_and_bound_reader_pass(self):
        self.assertEqual(self.run_check()['status'],'pass')

    def test_removed_notice_fails_even_with_unchanged_manifest(self):
        (self.source/'portraits.txt').unlink();r=self.run_check()
        self.assertEqual(r['status'],'fail')
        self.assertTrue(any(x['kind']=='notice_missing_or_changed' for x in r['issues']))

    def test_changed_notice_fails(self):
        (self.source/'original-text.txt').write_text('Credit removed')
        self.assertEqual(self.run_check()['status'],'fail')

    def test_credit_source_does_not_substitute_for_reader(self):
        p=copy.deepcopy(self.policy);p['components'][0]['reader_checks'][0]['all_of']=['Missing author']
        r=self.run_check(p);self.assertEqual(r['status'],'fail')
        self.assertTrue(any(x['kind']=='reader_credit_absent' for x in r['issues']))

    def test_omitted_component_cannot_pass(self):
        p=copy.deepcopy(self.policy);p['components'].pop()
        with self.assertRaises(ValueError):self.run_check(p)

    def test_unresolved_font_notice_is_not_a_pass(self):
        p=copy.deepcopy(self.policy);p['components'][0]['state']='unresolved'
        self.assertEqual(self.run_check(p)['status'],'incomplete')

    def test_source_only_is_not_reader_acceptance(self):
        self.assertEqual(self.run_check(pdf=False,build=False)['status'],'incomplete')

    def test_unbound_or_tampered_pdf_cannot_pass(self):
        self.assertEqual(self.run_check(build=False)['status'],'incomplete')
        self.pdf.write_bytes(self.pdf.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'PDF differs'):self.run_check()

    def test_path_escape_rejected(self):
        p=copy.deepcopy(self.policy);p['components'][0]['files'][0]['path']='../private.txt'
        with self.assertRaises(ValueError):self.run_check(p)

    def test_different_pin_or_locale_rejected(self):
        p=copy.deepcopy(self.policy);p['pins']['olp']='b'*40
        with self.assertRaisesRegex(ValueError,'source pins'):self.run_check(p)
        p=copy.deepcopy(self.policy);p['locale']='other'
        with self.assertRaisesRegex(ValueError,'different edition'):self.run_check(p)

    def test_actual_build_receipt_records_gate_without_claiming_release(self):
        from olpkit.build import record_pdf_credits
        policy=self.root/'policy.json';policy.write_bytes(json_bytes(self.policy))
        result={**self.receipt,'gates':{},'release_ready':False}
        self.build.write_bytes(json_bytes(result))
        self.assertTrue(record_pdf_credits(self.root,result,policy))
        stored=json.loads(self.build.read_text())
        self.assertEqual(stored['gates']['G-CREDIT']['status'],'pass')
        self.assertFalse(stored['release_ready'])
        self.assertFalse(record_pdf_credits(self.root,result,self.root/'missing.json'))
        self.assertEqual(result['gates']['G-CREDIT']['status'],'incomplete')
        self.assertIn('policy',result['gates']['G-CREDIT']['reason'])


if __name__=='__main__':unittest.main()
