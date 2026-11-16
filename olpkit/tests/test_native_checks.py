import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from olpkit.epubcheck import native_epub
from olpkit.tableprobe import mark_cells
from olpkit.unitbuild import unit_driver


class NativeCheckTests(TestCase):
    def test_unit_driver_keeps_native_preamble_and_reads_only_the_requested_entry(self):
        header = "% \\begin{document} in a comment\n\\usepackage{example}\n\\begin{document}"
        wrapper = unit_driver(header + "\n\\input{whole-book}", "content/a/b/c.tex").decode()
        self.assertTrue(wrapper.startswith(header))
        self.assertLess(wrapper.index(r"\ifcsname ps@OLPpage\endcsname\pagestyle{OLPpage}\fi"),
                        wrapper.index(r"\olimport*"))
        self.assertIn(r"\olimport*[a/b]{c}", wrapper)
        self.assertNotIn("whole-book", wrapper)
        with self.assertRaises(ValueError):
            unit_driver(header, "content/../other.tex")

    def test_math_tabular_and_prose_tabular_have_distinct_direction_requirements(self):
        tex = r"\begin{tabular}{cc}$x$ & $y$\\ A sentence & 1\end{tabular}"
        _,cells,issues=mark_cells(tex,"content/test.tex","pdflatex",1)
        self.assertFalse(issues)
        self.assertEqual([cell["required_math_direction"] for cell in cells], ["ltr","ltr",None,"ltr"])

    def test_epub_checks_reject_missing_profile_and_wrong_native_pdf(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            build={"pdf":{"sha256":"a"*64}}
            self.assertEqual(native_epub(root,build,{})["status"],"incomplete")
            (root/"web-profile.json").write_text(json.dumps({"witnesses":{"pdf":{"sha256":"b"*64}}}))
            self.assertEqual(native_epub(root,build,{})["status"],"fail")
