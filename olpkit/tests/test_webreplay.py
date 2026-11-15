import unittest
from unittest.mock import patch

from lxml import html

from olpkit.assembly import digest
from olpkit.bookcontext import BookInputs, PACKAGE_DECLARATIONS
from olpkit.speechreplay import original_source_locators, replay_labels


class ReleasedWebTests(unittest.TestCase):
    def test_speech_replay_checks_context_formula_and_final_bound_bytes(self):
        reader = b'<html lang="mr"><body><p>A <math><annotation encoding="text/x-tex">x</annotation></math></p></body></html>'
        doc = html.document_fromstring(reader)
        node = doc.xpath("//math")[0]
        node.set("alttext", "reading")
        node.set("aria-label", "reading")
        expected = html.tostring(doc, encoding="utf-8", doctype="<!DOCTYPE html>")
        packet = {"schema": "olpkit.released-speech.v1", "language": "mr", "reader_sha256": digest(reader),
                  "bound_reader_sha256": digest(expected), "labels": [{"tex_sha256": digest(b"x"), "text": "reading"}]}
        result, report = replay_labels(reader, packet)
        self.assertEqual(result, expected)
        self.assertEqual(report["with_spoken_text"], 1)
        cases = [(reader.replace(b"A ", b"B "), packet), (reader, {**packet, "language": "en"}),
                 (reader, {**packet, "labels": []}),
                 (reader, {**packet, "labels": [{"tex_sha256": digest(b"y"), "text": "reading"}]}),
                 (reader, {**packet, "labels": [{"tex_sha256": digest(b"x"), "text": "other"}]})]
        for source, record in cases:
            with self.assertRaises(ValueError):
                replay_labels(source, record)

    def test_reader_retains_original_locator_for_a_released_unit(self):
        row = {"assembled_path": "a.tex", "sha256": digest(b"public")}
        origins = {"a.tex": {"native_sha256": digest(b"native"), "editable_sha256": row["sha256"]}}
        self.assertEqual(original_source_locators([row], origins)[0]["sha256"], digest(b"native"))
        self.assertEqual(row["sha256"], digest(b"public"))
        self.assertEqual(original_source_locators([row], {}), [row])
        with self.assertRaisesRegex(ValueError, "editable"):
            original_source_locators([{**row, "sha256": digest(b"changed")}], origins)
        with self.assertRaisesRegex(ValueError, "outside"):
            original_source_locators([], origins)

    def test_native_package_is_read_in_production_and_exactly_attested_in_replay(self):
        name = "natbib.sty"
        body = b"\n".join(PACKAGE_DECLARATIONS[name])
        inputs = BookInputs.__new__(BookInputs)
        inputs.profile = {"packages": {name: {"sha256": digest(body)}}}
        inputs.released_declarations = None
        with patch.object(inputs, "package", return_value=body) as package:
            record = inputs.package_declarations(name)
            package.assert_called_once_with(name)
        with patch.object(inputs, "package", return_value=b""):
            with self.assertRaisesRegex(ValueError, "native package declaration"):
                inputs.package_declarations(name)
        inputs.released_declarations = {name: record}
        with patch.object(inputs, "package", side_effect=AssertionError("unexpected local TeX dependency")):
            self.assertEqual(inputs.package_declarations(name), record)
            inputs.profile["packages"][name]["sha256"] = digest(b"another version")
            with self.assertRaisesRegex(ValueError, "released package declarations"):
                inputs.package_declarations(name)
