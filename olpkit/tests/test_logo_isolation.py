import unittest

import fitz

from olpkit.linkpaint import isolation_comparison


def form_fixture(backdrop):
    doc = fitz.open()
    page = doc.new_page(width=60, height=60)
    ref = doc.get_new_xref()
    doc.update_object(ref, (
        '<< /Type /XObject /Subtype /Form /BBox [0 0 60 60] '
        '/Group << /S /Transparency /I false >> '
        '/Resources << /ExtGState << /Paint << /BM /Multiply >> >> >> >>'
    ))
    doc.update_stream(ref, b'/Paint gs 1 0 0 rg 10 10 40 40 re f')
    resources = int(doc.xref_get_key(page.xref, 'Resources')[1].split()[0])
    doc.xref_set_key(resources, 'XObject', f'<< /Mark {ref} 0 R >>')
    stream = doc.get_new_xref()
    doc.update_object(stream, '<<>>')
    doc.update_stream(stream, backdrop + b' q /Mark Do Q')
    page.set_contents(stream)
    return doc, page, ref


class LogoIsolationTests(unittest.TestCase):
    def test_same_render_on_paper(self):
        doc, page, ref = form_fixture(b'')
        with doc:
            self.assertEqual(len(isolation_comparison(doc, page, page.rect, ref)), 64)
            self.assertEqual(doc.xref_get_key(ref, 'Group/I'), ('bool', 'false'))

    def test_reject_changed_render_on_coloured_backdrop(self):
        doc, page, ref = form_fixture(b'0 0 1 rg 0 0 60 60 re f')
        with doc, self.assertRaisesRegex(ValueError, 'differs from isolated form'):
            isolation_comparison(doc, page, page.rect, ref)
