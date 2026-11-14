import io
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject, ArrayObject, FloatObject, DecodedStreamObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

from olpkit.pdfaudit import compare_pdfs, contrast, digest, inspect_links, inspect_glyphs, rgb, split_citations


BLUE=(11/255,60/255,111/255)


def fixture(path,text='Example',colour=BLUE,split=False,extra_page=False,background=None):
    output=io.BytesIO();c=canvas.Canvas(output,pagesize=(612,792))
    if background is not None:
        c.setFillColorRGB(*background)
        c.rect(15,690,150,35,stroke=0,fill=1)
    c.setFont('Helvetica',12);c.setFillColorRGB(*colour)
    c.drawString(20,700,text)
    width=stringWidth(text,'Helvetica',12)
    rects=[(20,697,20+width,714)]
    if split:
        c.setFillColorRGB(0,0,0);c.drawString(22+width,700,',')
        c.setFillColorRGB(*colour);c.drawString(32+width,700,'2020')
        rects.append((32+width,697,32+width+stringWidth('2020','Helvetica',12),714))
    c.showPage()
    if extra_page:c.drawString(20,700,'Second page');c.showPage()
    c.save()
    writer=PdfWriter();writer.append(PdfReader(io.BytesIO(output.getvalue())))
    for rect in rects:
        annotation=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),
            NameObject('/Rect'):ArrayObject([FloatObject(x) for x in rect]),
            NameObject('/Border'):ArrayObject([FloatObject(0)]*3),
            NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/GoTo'),NameObject('/D'):TextStringObject('cite.Example')})})
        writer.add_annotation(0,annotation)
    with path.open('wb') as stream:writer.write(stream)


def receipt(folder,pdf,pid):
    source=folder/'source';source.mkdir(exist_ok=True);(source/'text.tex').write_bytes(b'fixed source')
    result={'pdf':{'path':pdf.name,'sha256':digest(pdf.read_bytes())},'passes':2,
            'commands':[{'exit_code':0,'timed_out':False,'process_id':pid}],
            'source_inputs':{'text.tex':{'sha256':digest(b'fixed source')}},
            'source_date_epoch':1,'engine_version':'test-engine'}
    path=folder/'BUILD.json';path.write_text(json.dumps(result));return path


def mapped_glyph_fixture(path,codepoint):
    """A real PDF whose ordinary extractor may mask the malformed font map."""
    fixture(path,text='A')
    writer=PdfWriter();writer.append(PdfReader(path))
    mapping=DecodedStreamObject()
    mapping.set_data(('/CIDInit /ProcSet findresource begin 12 dict begin begincmap '
        '/CIDSystemInfo << /Registry (Test) /Ordering (Test) /Supplement 0 >> def '
        '/CMapName /GlyphRegression def /CMapType 2 def '
        '1 begincodespacerange <00> <FF> endcodespacerange '
        f'1 beginbfchar <41> <{codepoint:04X}> endbfchar '
        'endcmap CMapName currentdict /CMap defineresource pop end end').encode())
    writer.pages[0]['/Resources']['/Font']['/F1'].get_object()[NameObject('/ToUnicode')]=writer._add_object(mapping)
    with path.open('wb') as stream:writer.write(stream)


def actualtext_fixture(path,*,unmarked=False,notdef=False,nested_form=False,replacement='A'):
    """Real embedded Type0 font; the same missing map can be marked or unmarked."""
    import fitz
    import reportlab
    fontpath=Path(reportlab.__file__).parent/'fonts/Vera.ttf'
    font=fitz.Font(fontfile=str(fontpath));gid=0 if notdef else font.has_glyph(ord('A'))
    with fitz.open() as doc:
        page=doc.new_page();page.insert_font(fontname='TestFont',fontfile=str(fontpath))
        page.insert_text((72,72),'A',fontname='TestFont')
        writer=PdfWriter();writer.append(PdfReader(io.BytesIO(doc.tobytes())))
    page=writer.pages[0]
    mapping=DecodedStreamObject()
    mapping.set_data(('/CIDInit /ProcSet findresource begin 12 dict begin begincmap '
        '/CIDSystemInfo << /Registry (Test) /Ordering (Test) /Supplement 0 >> def '
        '/CMapName /ActualTextRegression def /CMapType 2 def '
        '1 begincodespacerange <0000> <FFFF> endcodespacerange '
        f'1 beginbfchar <{gid:04X}> <FFFD> endbfchar '
        'endcmap CMapName currentdict /CMap defineresource pop end end').encode())
    page['/Resources']['/Font']['/TestFont'].get_object()[NameObject('/ToUnicode')]=writer._add_object(mapping)
    actual=(b'\xfe\xff'+replacement.encode('utf-16-be')).hex()
    text=f'BT /TestFont 12 Tf 72 720 Td <{gid:04X}> Tj ET'
    raw=f'/Span << /ActualText <{actual}> >> BDC {text} EMC'
    if unmarked:raw+=f' BT /TestFont 12 Tf 72 680 Td <{gid:04X}> Tj ET'
    content=DecodedStreamObject();content.set_data(raw.encode())
    if nested_form:
        content[NameObject('/Type')]=NameObject('/XObject')
        content[NameObject('/Subtype')]=NameObject('/Form')
        content[NameObject('/BBox')]=ArrayObject([FloatObject(x) for x in (0,0,600,800)])
        content[NameObject('/Resources')]=page['/Resources']
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject('/Fm'):writer._add_object(content)})})
        wrapper=DecodedStreamObject();wrapper.set_data(b'q /Fm Do Q')
        page[NameObject('/Contents')]=writer._add_object(wrapper)
    else:page[NameObject('/Contents')]=writer._add_object(content)
    with path.open('wb') as stream:writer.write(stream)


class PDFAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_actual_glyph_trace_rejects_replacement_hidden_by_text_fallback(self):
        import fitz
        p=self.root/'fallback.pdf';mapped_glyph_fixture(p,0xfffd)
        with fitz.open(p) as doc:self.assertEqual(doc[0].get_text().strip(),'A')
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'fail')
        self.assertEqual(report['unmapped_trace_glyphs'],1)
        self.assertEqual(report['issues'][0]['font'],'Helvetica')
        self.assertTrue(report['issues'][0]['examples'][0]['bbox'])

    def test_poppler_exposes_control_hidden_by_mupdf_fallback(self):
        p=self.root/'control.pdf';mapped_glyph_fixture(p,6)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'fail')
        self.assertEqual(report['poppler_invalid_characters'],1)

    def test_private_use_is_not_silently_accepted(self):
        p=self.root/'private.pdf';mapped_glyph_fixture(p,0xe123)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'incomplete')
        self.assertEqual(report['private_use_glyphs'],1)

    def test_square_is_not_automatically_a_missing_glyph(self):
        p=self.root/'square.pdf';mapped_glyph_fixture(p,0x25a1)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'pass')
        self.assertEqual(report['square_codepoints'],{'U+25A1':1})

    def test_ordinary_pdf_encoding_passes_without_visual_quality_claim(self):
        p=self.root/'plain.pdf';fixture(p)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'pass')
        self.assertEqual(report['pages'],1)
        self.assertTrue(report['limits'])

    def test_exact_actualtext_covers_a_marked_glyph(self):
        p=self.root/'actual.pdf';actualtext_fixture(p)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'pass',report)
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],1)

    def test_actualtext_does_not_whitelist_same_font_outside_span(self):
        p=self.root/'unmarked.pdf';actualtext_fixture(p,unmarked=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'fail')
        self.assertEqual(report['unmapped_trace_glyphs'],1)
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],1)

    def test_actualtext_cannot_excuse_painted_notdef(self):
        p=self.root/'notdef.pdf';actualtext_fixture(p,notdef=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'fail')
        self.assertTrue(any(x['rule']=='notdef-glyph' for x in report['issues']))

    def test_actualtext_inside_form_is_matched(self):
        p=self.root/'form.pdf';actualtext_fixture(p,nested_form=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'pass',report)
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],1)

    def test_actualtext_invalid_character_is_not_a_waiver(self):
        p=self.root/'invalid.pdf';actualtext_fixture(p,replacement='\ufffd')
        with self.assertRaisesRegex(ValueError,'ActualText contains an invalid character'):inspect_glyphs(p)

    def test_actualtext_private_use_remains_unresolved(self):
        p=self.root/'actual-private.pdf';actualtext_fixture(p,replacement='\ue123')
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'incomplete')
        self.assertEqual(report['private_use_glyphs'],1)

    def test_build_binds_actual_glyph_failure_and_refuses_changed_bytes(self):
        from olpkit.build import record_pdf_glyphs
        p=self.root/'book.pdf';mapped_glyph_fixture(p,0xfffd)
        result={'pdf':{'path':p.name,'sha256':digest(p.read_bytes())},'gates':{'G-LOG':{'status':'pass'}},'release_ready':False}
        self.assertFalse(record_pdf_glyphs(self.root,result))
        stored=json.loads((self.root/'BUILD.json').read_text())
        self.assertEqual(stored['gates']['G-GLYPH']['unmapped_trace_glyphs'],1)
        self.assertEqual(stored['gates']['G-GLYPH']['status'],'fail')
        p.write_bytes(p.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'PDF bytes changed'):record_pdf_glyphs(self.root,result)

    def test_contrast_black_white_and_blue(self):
        self.assertEqual(contrast((0,0,0)),21)
        self.assertEqual(contrast((1,1,1)),1)
        self.assertGreater(contrast(BLUE),7)
        self.assertLess(contrast((0,.6,0)),7)

    def test_colour_space_not_guessed(self):
        self.assertEqual(rgb(.5),(.5,.5,.5))
        for value in ((0,0,0,1),None,(2,0,0)):
            with self.assertRaises(ValueError):rgb(value)

    def test_literal_equal_is_not_reproducibility(self):
        a=self.root/'a.pdf';b=self.root/'b.pdf';fixture(a);fixture(b)
        report,_=compare_pdfs(a,b)
        self.assertEqual(report['status'],'equal')
        self.assertEqual(report['G-SAME']['status'],'not_established')

    def test_one_changed_word_fails_exact_comparison(self):
        a=self.root/'a.pdf';b=self.root/'b.pdf';fixture(a);fixture(b,text='Different')
        report,_=compare_pdfs(a,b)
        self.assertFalse(report['text_equal']);self.assertTrue(report['pages_equal'])
        self.assertTrue(report['difference_preview'])

    def test_page_count_difference(self):
        a=self.root/'a.pdf';b=self.root/'b.pdf';fixture(a);fixture(b,extra_page=True)
        report,_=compare_pdfs(a,b);self.assertFalse(report['pages_equal'])

    def test_two_receipts_bind_artifacts_inputs_and_runs(self):
        a=self.root/'first';b=self.root/'second';a.mkdir();b.mkdir()
        pa=a/'book.pdf';pb=b/'book.pdf';fixture(pa);fixture(pb)
        ra=receipt(a,pa,100);rb=receipt(b,pb,200)
        report,_=compare_pdfs(pa,pb,ra,rb)
        self.assertEqual(report['G-SAME']['status'],'pass')
        (b/'source/text.tex').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'input bytes'):compare_pdfs(pa,pb,ra,rb)

    def test_receipt_rejects_different_pdf(self):
        a=self.root/'a';b=self.root/'b';a.mkdir();b.mkdir()
        pa=a/'book.pdf';pb=b/'book.pdf';fixture(pa);fixture(pb)
        ra=receipt(a,pa,100);rb=receipt(b,pb,200)
        fixture(pb,text='Changed')
        with self.assertRaisesRegex(ValueError,'PDF bytes'):compare_pdfs(pa,pb,ra,rb)

    def test_single_dark_citation_link_passes(self):
        p=self.root/'single.pdf';fixture(p,text='Example, 2020')
        report=inspect_links(p)
        self.assertEqual(report['status'],'pass',report)
        self.assertEqual(report['citation_areas'],1)

    def test_split_author_and_year_detected_in_pdf(self):
        p=self.root/'split.pdf';fixture(p,split=True)
        report=inspect_links(p)
        splits=[i for i in report['issues'] if i['rule']=='split-citation']
        self.assertEqual(len(splits),1);self.assertEqual(splits[0]['unlinked_text'],',')

    def test_pale_actual_text_fails_despite_annotation_border(self):
        p=self.root/'pale.pdf';fixture(p,colour=(.75,.75,.75))
        report=inspect_links(p)
        self.assertEqual(report['status'],'fail')
        self.assertTrue(any(i['rule']=='contrast' for i in report['issues']))

    def test_image_under_link_is_unmeasured(self):
        from PIL import Image
        p=self.root/'image.pdf';fixture(p)
        out=io.BytesIO();c=canvas.Canvas(out,pagesize=(612,792))
        c.drawInlineImage(Image.new('RGB',(30,20),'yellow'),0,680,100,60)
        c.setFont('Helvetica',12);c.setFillColorRGB(*BLUE);c.drawString(20,700,'Example');c.save()
        writer=PdfWriter();writer.append(PdfReader(io.BytesIO(out.getvalue())))
        annotation=PdfReader(p).pages[0]['/Annots'][0].get_object()
        writer.add_annotation(0,annotation)
        with p.open('wb') as f:writer.write(f)
        report=inspect_links(p)
        self.assertEqual(report['status'],'incomplete')

    def test_line_wrap_not_mistaken_for_split_same_line(self):
        links=[{'index':0,'destination':'cite.x','rect':[0,0,20,10]},
               {'index':1,'destination':'cite.x','rect':[30,20,60,30]}]
        chars=[{'text':',','x0':22,'x1':24,'top':0,'bottom':10}]
        self.assertEqual(split_citations(links,chars),[])

    def test_build_receipt_contains_actual_pdf_link_result(self):
        from olpkit.build import record_pdf_links
        pdf=self.root/'book.pdf';fixture(pdf,split=True)
        result={'pdf':{'path':pdf.name,'sha256':digest(pdf.read_bytes())},'gates':{},'release_ready':False}
        self.assertFalse(record_pdf_links(self.root,result))
        stored=json.loads((self.root/'BUILD.json').read_text())
        self.assertEqual(stored['gates']['G-LINK']['status'],'fail')
        self.assertEqual(stored['gates']['G-LINK']['issues'],1)
        self.assertFalse(stored['release_ready'])
        pdf.write_bytes(pdf.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'PDF bytes changed'):record_pdf_links(self.root,result)

    def test_dark_colour_override_is_detected_even_when_contrast_passes(self):
        pdf=self.root/'override.pdf';fixture(pdf,colour=(0,0,0))
        report=inspect_links(pdf,expected_color='0B3C6F')
        self.assertTrue(all(c['contrast_white']>=7 for c in report['text_colours']))
        self.assertEqual(report['status'],'fail')
        self.assertIn('declared-link-colour-overridden',[i['rule'] for i in report['issues']])
        fixture(pdf)
        self.assertEqual(inspect_links(pdf,expected_color='0B3C6F')['status'],'pass')


    def test_xelatex_rgb_accepts_exact_serialization(self):
        path=self.root/'serial.pdf'
        fixture(path,colour=(.408,.255,.024))
        self.assertEqual(inspect_links(path,expected_color='684106')['status'],'fail')
        self.assertEqual(inspect_links(path,expected_color='684106',xdvipdfmx=True)['status'],'pass')
        fixture(path,colour=(.409,.255,.024))
        report=inspect_links(path,expected_color='684106',xdvipdfmx=True)
        self.assertEqual(report['status'],'fail')
        self.assertIn('declared-link-colour-overridden',[i['rule'] for i in report['issues']])

    def test_xelatex_flat_fill_uses_actual_background(self):
        path=self.root/'boxed.pdf'
        fill=(.973,.796,.537)
        fixture(path,colour=(.408,.255,.024),background=fill)
        report=inspect_links(path,expected_color='684106',xdvipdfmx=True)
        self.assertEqual(report['status'],'fail',report)
        self.assertEqual(len(report['background_measurements']),1)
        self.assertEqual(report['unmeasured'],[])
        self.assertAlmostEqual(report['issues'][0]['minimum'],5.9174,delta=.08)
        fixture(path,colour=(.325,.2,0),background=fill)
        report=inspect_links(path,expected_color='533300',xdvipdfmx=True)
        self.assertEqual(report['status'],'pass',report)
        self.assertGreater(report['background_measurements'][0]['minimum_contrast'],7)

    def test_xelatex_keeps_image_backing_unmeasured(self):
        from PIL import Image
        path=self.root/'image.pdf';fixture(path)
        out=io.BytesIO();c=canvas.Canvas(out,pagesize=(612,792))
        c.drawInlineImage(Image.new('RGB',(30,20),'yellow'),0,680,100,60)
        c.setFont('Helvetica',12);c.setFillColorRGB(*BLUE);c.drawString(20,700,'Example');c.save()
        writer=PdfWriter();writer.append(PdfReader(io.BytesIO(out.getvalue())))
        writer.add_annotation(0,PdfReader(path).pages[0]['/Annots'][0].get_object())
        with path.open('wb') as f:writer.write(f)
        report=inspect_links(path,xdvipdfmx=True)
        self.assertEqual(report['status'],'incomplete')
        self.assertEqual(report['background_measurements'],[])


if __name__=='__main__':unittest.main()
