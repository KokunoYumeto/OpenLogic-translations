import unittest
from olpkit.structure import differences, signature


class StructureTests(unittest.TestCase):
    def test_comment_does_not_invent_footnote(self):
        self.assertEqual(signature('% \\footnote{not text}\nText')['footnotes'],0)

    def test_escaped_percent_keeps_following_reference(self):
        self.assertEqual(len(signature(r'10\% \olref[a][b]{x}')['references']),1)

    def test_locale_mark_does_not_change_identity(self):
        self.assertEqual(differences(r'\olfileid{a}{b}{c}',r'\olfileid[jv]{a}{b}{c}'),[])

    def test_target_cannot_lose_import(self):
        self.assertEqual(differences(r'\olimport*[a]{b}','')[0]['rule'],'imports')

    def test_changed_reference_is_detected(self):
        self.assertEqual(differences(r'\olref[a]{x}',r'\olref[a]{y}')[0]['rule'],'references')

    def test_added_maxwidth_is_detected(self):
        d=differences(r'\begin{tableau}{}x\end{tableau}',r'\begin{maxwidth}\begin{tableau}{}x\end{tableau}\end{maxwidth}')
        self.assertEqual(d[0]['rule'],'environments')

    def test_nested_argument_is_not_truncated(self):
        self.assertEqual(signature(r'\label{a{b}c}')['labels'][0][1],['a{b}c'])

    def test_malformed_argument_fails(self):
        with self.assertRaises(ValueError):signature(r'\olref{broken')


if __name__=='__main__':unittest.main()
