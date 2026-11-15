import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from olpkit.assembly import digest
from olpkit.syncrelease import verify_web_bundle


class WebReleaseTests(unittest.TestCase):
    def test_bundle_preserves_native_source_and_cold_web_products(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            files = {"reader.html": b"html", "reader.epub": b"epub", "reader-html.zip": b"offline"}
            for name, data in files.items():
                (root / name).write_bytes(data)
            outputs = {k: digest(v) for k, v in files.items()}
            verified = {"web_assets": {k: {"sha256": outputs[k]} for k in ("reader.html", "reader.epub")}}
            native, combined = root / "native.zip", root / "book.zip"
            with ZipFile(native, "w") as z:
                z.writestr("book.tex", b"source")
            def stage(source):
                record = {"inputs": {"source/book.tex": digest(source)}, "outputs": outputs}
                with ZipFile(combined, "w") as z:
                    z.writestr("source/book.tex", source)
                    z.writestr("WEB-EDITION.json", json.dumps(record))
            stage(b"source")
            verify_web_bundle(combined, native, root, verified)
            stage(b"different source")
            with self.assertRaisesRegex(ValueError, "preserve"):
                verify_web_bundle(combined, native, root, verified)
            stage(b"source")
            (root / "reader-html.zip").write_bytes(b"stale")
            with self.assertRaisesRegex(ValueError, "cold web build"):
                verify_web_bundle(combined, native, root, verified)
