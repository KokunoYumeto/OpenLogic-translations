from copy import deepcopy
import csv
import io
import unittest

from olpkit.unitlint import unit_findings,kept_tokens,stored_marks,apply_exceptions,classify_exceptions,EXCEPTION_FIELDS
from olpkit.schemas import validate_schema


SOURCE = br'''\olfileid{part}{chapter}{section}
\begin{theorem}\label{thm:a} Text !!{enumerable}.\end{theorem}
\begin{proof}See \olref[a][b]{def:c} and \cite[p.~3]{A,B}.
\olimport*[x]{y}\iftag{tag}{one}{two}\end{proof}
'''
TARGET = SOURCE.replace(b'\\olfileid',b'\\olfileid[xx]').replace(b'Text',b'Translated')


class UnitLintTests(unittest.TestCase):
    def findings(self,target=TARGET,source=SOURCE,orthography=None):
        return unit_findings(source,target,'xx',orthography)[0]

    def test_preserved_structure_with_changed_prose_passes_literal_checks(self):
        self.assertEqual(self.findings(),[])

    def test_identifiers_and_stored_marks_are_distinct_checks(self):
        self.assertEqual([f['rule'] for f in self.findings(SOURCE)],['locale-mark'])
        self.assertIn('identifiers',[f['rule'] for f in self.findings(TARGET.replace(b'{section}',b'{wrong}'))])
        self.assertEqual(stored_marks('% \\olfileid[ignored]{a}\n\\olpartid \n [xx]{p}'),[['olpartid','xx']])

    def test_each_structure_mismatch_is_reported_without_rewriting(self):
        cases=[(b'{y}',b'{z}','imports'),(b'{thm:a}',b'{thm:b}','labels'),
               (b'{theorem}',b'{lemma}','environments'),(b'{A,B}',b'{A,C}','citations'),
               (b'{def:c}',b'{def:d}','references'),(b'{tag}',b'{other}','tags')]
        for before,after,rule in cases:
            with self.subTest(rule=rule):
                text=TARGET.replace(before,after)
                self.assertIn(rule,[f['rule'] for f in self.findings(text)])
                self.assertEqual(text,TARGET.replace(before,after))

    def test_kept_tokens_count_actual_uses_and_ignore_comments(self):
        text=r'!!^a{enumerable} !!{nonenumerable} \usetoken{P}{denumerable} % !!{enumerable}'
        self.assertEqual(kept_tokens(text),{'enumerable':1,'nonenumerable':1,'denumerable':1})
        self.assertIn('token:enumerable',[f['rule'] for f in self.findings(TARGET.replace(b'!!{enumerable}',b'spelled out'))])
        self.assertEqual(self.findings(TARGET.replace(b'!!{enumerable}',br'\usetoken{s}{enumerable}')),[])

    def test_added_and_missing_footnotes_are_reported(self):
        self.assertIn('footnotes',[f['rule'] for f in self.findings(TARGET+br'\footnote{New note}')])
        original=SOURCE+br'\footnote{Original note}'
        self.assertIn('footnotes',[f['rule'] for f in self.findings(source=original)])
        self.assertEqual(self.findings(TARGET+br'\footnote{Translated original}',original),[])

    def test_orthography_requires_evidence_and_detects_configured_defects(self):
        policy={'locale':'xx','rules':[{'id':'fixture','kind':'forbidden_literal','literal':'BAD',
                'reason':'Synthetic test only.','evidence':[{'source':'fixture','sha256':'a'*64,'locator':'1'}]}]}
        validate_schema('orthography',policy)
        self.assertEqual(self.findings(orthography=policy),[])
        self.assertIn('orthography:fixture',[f['rule'] for f in self.findings(TARGET+b'BAD',orthography=policy)])
        policy['rules'][0]['evidence']=[]
        with self.assertRaises(ValueError):validate_schema('orthography',policy)

    def test_nfc_is_checked_only_when_explicitly_configured(self):
        target=TARGET+' e\u0301'.encode()
        self.assertEqual(self.findings(target),[])
        p={'rules':[{'id':'unicode','kind':'nfc'}]}
        self.assertIn('orthography:unicode',[f['rule'] for f in self.findings(target,orthography=p)])

    def test_hash_bound_exception_remains_visible_and_cannot_cover_new_wording(self):
        f=self.findings(TARGET.replace(b'{def:c}',b'{def:d}'))[0]
        f.update(unit='OLP-0001',source_sha256='a'*64,target_sha256='b'*64)
        row={k:f[k] for k in EXCEPTION_FIELDS[:5]};row.update(reason='Correct source reference',evidence='Exact source comparison fixture')
        def body(rows):
            s=io.StringIO();w=csv.DictWriter(s,fieldnames=EXCEPTION_FIELDS,delimiter='\t');w.writeheader();w.writerows(rows);return s.getvalue().encode()
        result,accepted=apply_exceptions([deepcopy(f)],body([row]))
        self.assertEqual(len(result),1);self.assertEqual(result[0]['exception']['reason'],row['reason'])
        changed={**f,'target_sha256':'c'*64}
        with self.assertRaisesRegex(ValueError,'stale'):apply_exceptions([changed],body([row]))
        with self.assertRaisesRegex(ValueError,'duplicate'):apply_exceptions([deepcopy(f)],body([row,row]))

    def test_broken_literal_structure_is_not_silently_accepted(self):
        with self.assertRaises(ValueError):self.findings(TARGET+br'\label{open')

    def test_legacy_exception_is_retained_but_does_not_waive_a_difference(self):
        found=self.findings(TARGET.replace(b'{def:c}',b'{def:d}'))
        checked,accepted,legacy=classify_exceptions(found,b'unit\trule\treason\nOLP-0001\treferences\tHistorical correction\n')
        self.assertEqual(checked,found);self.assertEqual(accepted,[])
        self.assertNotIn('exception',checked[0])
        self.assertEqual(legacy['records'][0]['reason'],'Historical correction')


if __name__=='__main__':unittest.main()
