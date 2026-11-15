import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from olpkit.assembly import digest
from olpkit.syncverify import checked_file, standalone_evidence, verify_projected_units


class SyncVerificationTests(unittest.TestCase):
    def test_web_readers_must_reference_each_compiled_source(self):
        source = "content/chapter.tex"
        target = "locale/mr/" + source
        unit = {"path": source, "unit": "OLP-0001", "sha256": digest(b"translated"),
                "assembled_path": target, "html_id": "olp-unit-000001"}
        build = {"content_inputs": {source: [target]},
                 "source_inputs": {target: {"unit": unit["unit"], "sha256": unit["sha256"]}}}
        def verify(rows, order):
            verify_projected_units(rows, order, build, {source})
        verify([unit], ["000001"])
        for field, value in (("unit", "OLP-0099"), ("sha256", digest(b"older translation")),
                             ("assembled_path", "locale/en/" + source)):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "source used"):
                verify([{**unit, field: value}], ["000001"])
        with self.assertRaisesRegex(ValueError, "inventory"):
            verify([unit, unit], ["000001", "000001"])
        with self.assertRaisesRegex(ValueError, "anchors"):
            verify([unit], ["000002"])

    def test_receipt_must_bind_the_run_context_and_checked_bytes(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            record = {"status": "pass", "unit": "content/a.tex", "context_sha256": digest(b"run A"),
                      "fatal": [], "wrong_language_inputs": []}
            payload = json.dumps(record).encode()
            (root / "unit.json").write_bytes(payload)
            entry = {"unit": record["unit"], "file": "unit.json", "sha256": digest(payload)}
            report = {"status": "pass", "scope_units": 1, "context_sha256": record["context_sha256"],
                      "units": [entry]}
            scope = {record["unit"]}
            standalone_evidence(root, report, scope)
            with self.assertRaisesRegex(ValueError, "disagrees"):
                standalone_evidence(root, {**report, "context_sha256": digest(b"run B")}, scope)
            with self.assertRaisesRegex(ValueError, "cover"):
                standalone_evidence(root, {**report, "units": [entry, entry]}, scope)
            (root / "unit.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "bytes changed"):
                standalone_evidence(root, report, scope)
            with self.assertRaises(ValueError):
                checked_file(root, "../unit.json", digest(payload))
