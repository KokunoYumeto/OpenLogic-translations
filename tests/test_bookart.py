import unittest,tempfile,hashlib,base64
from pathlib import Path
from lxml import html
from olpkit.bookart import bind_book_art


class BookArtTests(unittest.TestCase):
    def test_source_png_keeps_exact_bytes_and_decorative_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'original.png'
            data=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==')
            source.write_bytes(data);sha=hashlib.sha256(data).hexdigest()
            doc=html.fromstring('<p><img src="illustrations/Chapter" alt="image"></p>')
            r=bind_book_art(doc,resolve=lambda _: (source,sha),output=root/'out',cover_width_percent=24.5,evidence={'native':'checked'})
            self.assertEqual((root/'out'/r['assets'][0]['asset']).read_bytes(),data)
            self.assertEqual(doc.xpath('.//img/@alt'),[''])
            self.assertEqual(doc.xpath('.//img/@role'),['presentation'])
    def test_changed_source_art_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'original.png';source.write_bytes(b'changed')
            doc=html.fromstring('<p><img src="illustrations/Chapter"></p>')
            with self.assertRaisesRegex(ValueError,'source hash'):
                bind_book_art(doc,resolve=lambda _: (source,'wrong'),output=root/'out',cover_width_percent=24.5,evidence={'native':'checked'})
