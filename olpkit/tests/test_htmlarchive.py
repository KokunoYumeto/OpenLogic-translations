import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from olpkit.assembly import digest
from olpkit.htmlarchive import package_html_reader


class HtmlArchiveTests(unittest.TestCase):
    def test_offline_reader_contains_exact_epub_resources_and_omits_private_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            resource = root / "assets" / "figure.svg"
            resource.parent.mkdir()
            resource.write_bytes(b"<svg/>")
            reader = b'<img src="assets/figure.svg">'
            (root / "reader.html").write_bytes(reader)
            (root / "private.txt").write_text("editorial note")
            diagnostics = b'{"messages":[]}'
            (root / "EPUBCHECK.json").write_bytes(diagnostics)
            epub = root / "reader.epub"
            with ZipFile(epub, "w") as archive:
                archive.write(resource, "OEBPS/assets/figure.svg")
            receipt = {"product":"accessible", "epubcheck":{"exit_code":0, "diagnostics":0,
                       "report_sha256":digest(diagnostics)}, "products":{"reader.html":{"sha256":digest(reader)},
                       "reader.epub":{"sha256":digest(epub.read_bytes())}}, "epub":{"source_html_sha256":digest(reader),
                       "assets":{"assets/figure.svg":digest(resource.read_bytes())}}}
            export = root / "EXPORT.json"
            export.write_text(json.dumps(receipt))
            destination = root / "reader.zip"
            package_html_reader(export, destination)
            with ZipFile(destination) as archive:
                self.assertEqual(set(archive.namelist()), {"assets/figure.svg","reader.html"})
                self.assertEqual(archive.read("reader.html"), reader)
            resource.write_bytes(b"other")
            with self.assertRaisesRegex(ValueError, "resource differs"):
                package_html_reader(export, destination)
