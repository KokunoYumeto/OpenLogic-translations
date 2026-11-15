import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from olpkit.assembly import digest
from olpkit.syncaccept import by_id, save_acceptance, validate_decision


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.bodies = {"source_before": b"old source", "source_after": b"new source",
                       "target_before": b"same target", "target_after": b"same target"}
        self.witnesses = {"term": {"source": "A cited textbook", "locator": "section 2, definition 3"}}
        self.row = {"unit": "OLP-0001", "disposition": "carried", "rationale": "Already corrected",
                    "anchor": "same target", "target_lines": [1], "confidence": "high",
                    "confidence_basis": "The target already contains the corrected wording.",
                    "canon": ["term"], "hashes": {k: digest(v) for k,v in self.bodies.items()}}

    def test_carried_requires_the_actual_unchanged_target(self):
        validate_decision(self.row, self.bodies, self.witnesses)
        self.bodies["target_after"] = b"changed later"
        with self.assertRaisesRegex(ValueError, "target_after"):
            validate_decision(self.row, self.bodies, self.witnesses)
        self.row["hashes"]["target_after"] = digest(self.bodies["target_after"])
        with self.assertRaisesRegex(ValueError, "observed target"):
            validate_decision(self.row, self.bodies, self.witnesses)

    def test_review_cannot_use_a_bibliography_without_a_passage(self):
        with self.assertRaisesRegex(ValueError, "no source or locator"):
            validate_decision(self.row, self.bodies, {"term": {"source": "Book"}})

    def test_duplicate_units_and_conflicting_receipts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            by_id([self.row, self.row], "unit")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "accepted.json"
            save_acceptance(path, b"one")
            save_acceptance(path, b"one")
            with self.assertRaisesRegex(ValueError, "different"):
                save_acceptance(path, b"two")
            self.assertEqual(path.read_bytes(), b"one")
