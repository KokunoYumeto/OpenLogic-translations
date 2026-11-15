from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from reportlab.pdfgen import canvas
from olpkit.tableprobe import diagnostic_text_check, mark_cells, measure_pdf
from olpkit.tablecheck import confirmed_corrections, math_direction_changed


class TableProbeTests(unittest.TestCase):
    def test_diagnostic_reading_order_requires_identical_glyphs_and_vectors(self):
        import fitz
        with TemporaryDirectory() as folder:
            def page_file(name, shift, line_y):
                path = Path(folder)/name
                with fitz.open() as doc:
                    page = doc.new_page()
                    page.insert_font(fontname="ProbeFont", fontbuffer=fitz.Font("helv").buffer)
                    page.insert_text((40+shift, 40), "5", fontname="ProbeFont")
                    page.insert_text((40, 55), "2", fontname="ProbeFont")
                    page.draw_line((38, line_y), (49, line_y))
                    doc.save(path)
                return path
            native = page_file("native.pdf", 0, 44)
            texts = (b"52\f", b"25\f")
            self.assertTrue(diagnostic_text_check(native, native, texts, [1,1])["pass"])
            self.assertFalse(diagnostic_text_check(native, page_file("moved.pdf", 1, 44), texts, [1,1])["pass"])
            self.assertFalse(diagnostic_text_check(native, page_file("line.pdf", 0, 48), texts, [1,1])["pass"])
            self.assertFalse(diagnostic_text_check(native, native, (b"52\f", b"23\f"), [1,1])["pass"])

    def test_multicolumn_keeps_omit_first_and_empty_cells_receive_markers(self):
        tex=r"\begin{tabular}{cc}\multicolumn{2}{c}{AB}\\ & C\end{tabular}"
        marked,cells,issues=mark_cells(tex,"unit","pdflatex",100)
        self.assertFalse(issues)
        self.assertIn(r"\multicolumn{2}{c}{\pdfliteral direct",marked)
        self.assertEqual([(x["row"],x["col"],x["span"]) for x in cells],[(1,1,2),(2,1,1),(2,2,1)])
        self.assertEqual(marked.count("BDC"),3)
        self.assertEqual(marked.count("EMC"),3)

    def test_nested_actualtext_binds_native_coordinates_and_rejects_different_glyphs(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            def make(name, mark, x, word):
                c=canvas.Canvas(str(root/name),pagesize=(150,100))
                if mark:c.addLiteral("/OLPCell << /MCID 101 >> BDC")
                c.addLiteral("/Span << /ActualText <FEFF0AA80ABF> >> BDC")
                c.drawString(x,50,word)
                c.addLiteral("EMC")
                if mark:c.addLiteral("EMC")
                c.save()
            make("native.pdf",False,20,"AB")
            make("marked.pdf",True,30,"AB")
            cells=[{"id":101}]
            paint,shipped,issues=measure_pdf(root/"native.pdf",root/"marked.pdf",cells)
            self.assertFalse(issues)
            self.assertEqual(shipped,{101:[1]})
            self.assertEqual([v["text"] for v in paint[0]["glyphs"]],["નિ",""])
            self.assertEqual(paint[0]["glyphs"][0]["box"][0],20)
            make("different.pdf",True,30,"AC")
            paint,_,issues=measure_pdf(root/"native.pdf",root/"different.pdf",cells)
            self.assertFalse(paint)
            self.assertTrue(issues)

    def test_reverse_glyph_order_is_visible_even_when_extracted_sequence_agrees(self):
        def glyph(x):
            return {"page":1,"box":[x,10,x+5,20]}
        self.assertTrue(math_direction_changed([glyph(10),glyph(30)],[glyph(30),glyph(10)]))
        self.assertFalse(math_direction_changed([glyph(10),glyph(30)],[glyph(15),glyph(40)]))

