import unittest

from olpkit.tablecheck import verify_proof_label_sources


class ProofLabelSources(unittest.TestCase):
    path = "book/slc-config.sty"
    label = {"path": path, "sha256": "a" * 64, "other_source_sha256": ["b" * 64]}

    def check(self, assembled, recorded, *, path=None, kind="assembled-tree"):
        verify_proof_label_sources(
            [self.label],
            {self.path: {"sha256": assembled}},
            [{"kind": kind, "path": path or self.path, "sha256": recorded}],
        )

    def test_original_and_reviewed_layout(self):
        for sha in ("a" * 64, "b" * 64):
            self.check(sha, sha)

    def test_recorder_must_match_exact_assembled_version(self):
        with self.assertRaises(ValueError):
            self.check("a" * 64, "b" * 64)

    def test_reject_unreviewed_version_and_unrelated_files(self):
        with self.assertRaises(ValueError):
            self.check("c" * 64, "c" * 64)
        with self.assertRaises(ValueError):
            self.check("b" * 64, "b" * 64, path="different.sty")
        with self.assertRaises(ValueError):
            self.check("b" * 64, "b" * 64, kind="toolchain")
