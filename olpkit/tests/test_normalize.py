import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from olpkit.orthography import normalize_command, normalize_unit
from olpkit.unitlint import unit_findings


POLICY = {"locale":"jv","rules":[{"id":"nfc","kind":"nfc","reason":"Edition uses NFC.",
          "evidence":[{"source":"canonical edition", "sha256":"a"*64, "locator":"orthography"}]}]}


class NormalizationTests(unittest.TestCase):
    def test_composition_comments_and_distinct_output(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            unit=root/"unit.tex"
            raw="cafe\u0301 \\% cafe\u0301 % cafe\u0301\r\n".encode()
            unit.write_bytes(raw)
            policy=root/"policy.json"
            policy.write_text(json.dumps(POLICY))
            self.assertEqual(normalize_command(unit,policy),1)
            self.assertEqual(normalize_command(unit,policy,root/"new.tex"),0)
            self.assertEqual(unit.read_bytes(),raw)
            proposed=(root/"new.tex").read_bytes()
            self.assertEqual(proposed,"café \\% café % cafe\u0301\r\n".encode())
            self.assertEqual(normalize_unit(proposed,POLICY),proposed)
            with self.assertRaises(ValueError): normalize_command(unit,policy,unit)

    def test_reference_identity_is_preserved(self):
        raw="\\label{cafe\u0301}".encode()
        with self.assertRaisesRegex(ValueError,"structural"): normalize_unit(raw,POLICY)

    def test_genuine_source_note_and_added_translation_note(self):
        source=br"\sourcecorrection{a}{example}"
        matched,_=unit_findings(source,source,"jv",POLICY)
        self.assertFalse(any(r["rule"]=="note-commands" for r in matched))
        extra,_=unit_findings(b"text",b"text "+source,"jv",POLICY)
        self.assertEqual([r["rule"] for r in extra],["note-commands"])

