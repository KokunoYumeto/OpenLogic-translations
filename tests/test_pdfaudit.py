import io
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject, ArrayObject, FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

from olpkit.pdfaudit import compare_pdfs, contrast, digest, inspect_links, rgb, split_citations


BLUE=(11/255,60/255,111/255)


def fixture(path,text='Example',colour=BLUE,split=False,extra_page=False):
    output=io.BytesIO();c=canvas.Canvas(output,pagesize=(612,792))
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


class PDFAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

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


if __name__=='__main__':unittest.main()
