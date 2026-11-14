import io
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject, ArrayObject, FloatObject, DecodedStreamObject, NumberObject
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


def mixed_actualtext_fixture(path,*,unmarked_bad=False,encoding_mismatch=False,pdf_differences=False):
    """Two embedded font types share a trace name, with different glyph IDs.

    The Type0 occurrence has ActualText; the later Type1 occurrence does not.
    The font is generated in memory so the regression needs no TeX or fixture
    copied from a published book.
    """
    import fitz
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.t2CharStringPen import T2CharStringPen
    actualtext_fixture(path)
    with fitz.open(path) as doc:name=doc[0].get_texttrace()[0]['font']
    builder=FontBuilder(1000,isTTF=False);builder.setupGlyphOrder(['.notdef','A','B'])
    strings={}
    for glyph in ['.notdef','A','B']:
        pen=T2CharStringPen(600,None)
        if glyph!='.notdef':
            pen.moveTo((50,0));pen.lineTo((300,700));pen.lineTo((550,0));pen.closePath()
        strings[glyph]=pen.getCharString()
    builder.setupCFF(name,{'FullName':name,'FamilyName':name,'Weight':'Regular'},strings,{})
    encoding=['.notdef']*256
    encoding[65],encoding[66]=('B','A') if encoding_mismatch else ('A','B')
    builder.font['CFF '].cff.topDictIndex[0].Encoding=encoding
    fontdata=builder.font['CFF '].compile(builder.font)
    writer=PdfWriter();writer.append(PdfReader(path));page=writer.pages[0]
    program=DecodedStreamObject();program.set_data(fontdata)
    program[NameObject('/Subtype')]=NameObject('/Type1C')
    descriptor=DictionaryObject({NameObject('/Type'):NameObject('/FontDescriptor'),
        NameObject('/FontName'):NameObject('/'+name),NameObject('/Flags'):NumberObject(32),
        NameObject('/FontBBox'):ArrayObject([NumberObject(x) for x in (0,0,600,700)]),
        NameObject('/ItalicAngle'):NumberObject(0),NameObject('/Ascent'):NumberObject(700),
        NameObject('/Descent'):NumberObject(0),NameObject('/CapHeight'):NumberObject(700),
        NameObject('/StemV'):NumberObject(80),NameObject('/FontFile3'):writer._add_object(program)})
    pdf_encoding=NameObject('/WinAnsiEncoding')
    if pdf_differences:
        pdf_encoding=DictionaryObject({NameObject('/BaseEncoding'):pdf_encoding,
            NameObject('/Differences'):ArrayObject([NumberObject(65),NameObject('/B')])})
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),
        NameObject('/BaseFont'):NameObject('/'+name),NameObject('/FirstChar'):NumberObject(65),
        NameObject('/LastChar'):NumberObject(66),NameObject('/Widths'):ArrayObject([NumberObject(600)]*2),
        NameObject('/Encoding'):pdf_encoding,NameObject('/FontDescriptor'):writer._add_object(descriptor)})
    mapping=DecodedStreamObject()
    mapping.set_data(('/CIDInit /ProcSet findresource begin 12 dict begin begincmap '
        '/CIDSystemInfo << /Registry (Test) /Ordering (Test) /Supplement 0 >> def '
        '/CMapName /MixedRegression def /CMapType 2 def '
        '1 begincodespacerange <00> <FF> endcodespacerange '
        f'1 beginbfchar <41> <{"FFFD" if unmarked_bad else "0041"}> endbfchar '
        'endcmap CMapName currentdict /CMap defineresource pop end end').encode())
    font[NameObject('/ToUnicode')]=writer._add_object(mapping)
    page['/Resources']['/Font'][NameObject('/Simple')]=writer._add_object(font)
    raw=page.get_contents().get_data()+b' BT /Simple 12 Tf 72 680 Td <41> Tj ET'
    content=DecodedStreamObject();content.set_data(raw);page[NameObject('/Contents')]=writer._add_object(content)
    with path.open('wb') as stream:writer.write(stream)


def neighbouring_superscript_fixture(path,*,inside=False):
    output=io.BytesIO();c=canvas.Canvas(output,pagesize=(612,792))
    c.setFont('Helvetica',12);c.setFillColorRGB(*BLUE);c.drawString(72,700,'Target')
    c.setFont('Helvetica',6);c.setFillColorRGB(0,0,0)
    c.drawString(80,692 if inside else 690,"'")
    c.save();writer=PdfWriter();writer.append(PdfReader(io.BytesIO(output.getvalue())))
    # A real metric discrepancy: PDFMiner puts the lower prime's centre at
    # y=100.242, while the rendered glyph trace puts it at y=100.306.
    annotation=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),
        NameObject('/Rect'):ArrayObject([FloatObject(x) for x in (72,691.73,110,710)]),
        NameObject('/Border'):ArrayObject([FloatObject(0)]*3),
        NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/URI'),NameObject('/URI'):TextStringObject('https://example.org/')})})
    writer.add_annotation(0,annotation)
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

    def test_same_name_type1_and_type0_keep_exact_painted_sequence(self):
        import fitz
        p=self.root/'mixed.pdf';mixed_actualtext_fixture(p)
        with fitz.open(p) as doc:
            spans=doc[0].get_texttrace()
            self.assertEqual(len({s['font'] for s in spans}),1)
            self.assertEqual(sum(len(s['chars']) for s in spans),2)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'pass',report)
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],1)
        self.assertEqual(report['actualtext']['unmeasured'],[])

    def test_same_name_simple_unmarked_bad_glyph_is_not_excused(self):
        p=self.root/'mixed-bad.pdf';mixed_actualtext_fixture(p,unmarked_bad=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'fail',report)
        self.assertEqual(report['unmapped_trace_glyphs'],1)
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],1)

    def test_type1_pdf_encoding_differences_are_not_guessed(self):
        p=self.root/'mixed-differences.pdf';mixed_actualtext_fixture(p,pdf_differences=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'incomplete',report)
        self.assertTrue(report['actualtext']['unmeasured'])
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],0)

    def test_type1_embedded_encoding_disagreement_is_not_guessed(self):
        p=self.root/'mixed-encoding.pdf';mixed_actualtext_fixture(p,encoding_mismatch=True)
        report=inspect_glyphs(p)
        self.assertEqual(report['status'],'incomplete',report)
        self.assertTrue(report['actualtext']['unmeasured'])
        self.assertEqual(report['actualtext']['covered_glyph_occurrences'],0)

    def test_xelatex_link_uses_painted_geometry_for_neighbouring_superscript(self):
        p=self.root/'neighbour.pdf';neighbouring_superscript_fixture(p)
        coarse=inspect_links(p,expected_color='0B3C6F')
        self.assertEqual(coarse['status'],'fail')
        precise=inspect_links(p,expected_color='0B3C6F',xdvipdfmx=True)
        self.assertEqual(precise['status'],'pass',precise)
        self.assertEqual(len(precise['text_colours']),1)

    def test_xelatex_link_keeps_a_real_wrong_colour_inside_the_area(self):
        p=self.root/'inside.pdf';neighbouring_superscript_fixture(p,inside=True)
        report=inspect_links(p,expected_color='0B3C6F',xdvipdfmx=True)
        self.assertEqual(report['status'],'fail')
        self.assertTrue(any(x['rule']=='declared-link-colour-overridden' for x in report['issues']))

    def test_bengali_link_colour_passes_on_the_observed_theorem_background(self):
        import tomllib
        from olpkit.schemas import ROOT
        profile=tomllib.loads((ROOT/'data/languages/bn.toml').read_text(encoding='utf-8'))
        value=profile['links']['color'];colour=tuple(int(value[i:i+2],16)/255 for i in (0,2,4))
        self.assertGreaterEqual(contrast(colour,(.973,.796,.537)),7)

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
