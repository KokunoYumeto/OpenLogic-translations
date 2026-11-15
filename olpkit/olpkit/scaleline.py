"""Set two widely separated glyphs using the exact font objects and CIDs from a reader line."""
from io import BytesIO
from pathlib import Path
import re

from .assembly import digest


def isolated_line(pdf, page_number, roles, output):
    """Return a one-line diagnostic PDF only for horizontal, unscaled Identity-H glyphs."""
    import fitz
    from pdfminer.converter import PDFPageAggregator
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdftypes import dict_value
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    manager=PDFResourceManager()
    with Path(pdf).open("rb") as stream:
        page=next(PDFPage.get_pages(stream,pagenos={page_number-1}))
        objects={}
        for ref in dict_value(page.resources["Font"]).values():
            if not hasattr(ref,"objid"):continue
            font=manager.get_font(ref.objid,dict_value(ref))
            objects[id(font)]=ref.objid
        choices=[[],[]]
        class Sampler(PDFPageAggregator):
            def render_char(self,matrix,font,fontsize,scaling,rise,cid,ncs,graphicstate):
                advance=super().render_char(matrix,font,fontsize,scaling,rise,cid,ncs,graphicstate)
                char=self.cur_item._objs[-1].get_text()
                name=re.sub(r"^[A-Z]{6}\+","",font.fontname).removesuffix("-Identity-H")
                for i,(face,glyph,size) in enumerate(roles):
                    if (char==glyph and name==face and abs(fontsize-size)<.02
                            and all(abs(a-b)<.0001 for a,b in zip(matrix[:4],(1,0,0,1)))
                            and abs(scaling-1)<.0001 and abs(rise)<.001 and id(font) in objects):
                        choices[i].append((objects[id(font)],cid,fontsize,matrix[4],matrix[5]))
                return advance
        PDFPageInterpreter(manager,Sampler(manager)).process_page(page)
    pairs=[(a,b) for a in choices[0] for b in choices[1] if abs(a[4]-b[4])<.4]
    if not pairs:return None
    reader=PdfReader(pdf)
    for pair in pairs:
        fonts=[reader.get_object(g[0]) for g in pair]
        if any(f.get("/Encoding")!="/Identity-H" for f in fonts):continue
        writer=PdfWriter();sheet=writer.add_blank_page(width=140,height=70)
        copied=DictionaryObject();ops=[];sources=[]
        for i,(glyph,font) in enumerate(zip(pair,fonts,strict=True)):
            xref,cid,size,x,y=glyph;key="/S"+str(i)
            copied[NameObject(key)]=font.clone(writer).indirect_reference
            ops.append(f"BT {key} {size:.8f} Tf 1 0 0 1 {30+65*i} 30 Tm <{cid:04X}> Tj ET")
            sources.append({"source_font_object":xref,"cid":cid,"size_pt":size,"origin_pdf":[x,y]})
        sheet[NameObject("/Resources")]=DictionaryObject({NameObject("/Font"):copied})
        content=DecodedStreamObject();content.set_data("\n".join(ops).encode("ascii"))
        sheet[NameObject("/Contents")]=writer._add_object(content)
        buf=BytesIO();writer.write(buf);body=buf.getvalue()
        record={}
        with fitz.open(stream=body,filetype="pdf") as sample, fitz.open(pdf) as original:
            traces=sample[0].get_texttrace()
            chars=[(s,c) for s in traces for c in s["chars"]]
            if len(chars)!=2:continue
            accepted=True
            for i,((span,char),(face,wanted,size)) in enumerate(zip(chars,roles,strict=True)):
                source=sources[i];x,y=source["origin_pdf"];p=original[page_number-1]
                if p.rotation or p.rect.x0 or p.rect.y0:accepted=False;break
                matches=[(s,c) for s in p.get_texttrace() if s["font"]==face
                         for c in s["chars"] if c[0]==ord(wanted) and c[1]==char[1]
                         and abs(c[2][0]-x)<.04 and abs(c[2][1]-(p.rect.height-y))<.04]
                if (len(matches)!=1 or span["font"]!=face or char[0]!=ord(wanted)
                        or abs(span["size"]-matches[0][0]["size"])>.01):
                    accepted=False;break
                actual=original.extract_font(source["source_font_object"])[3]
                new_obj=next((row[0] for row in sample[0].get_fonts() if row[4]=="S"+str(i)),None)
                if not actual or not new_obj or actual!=sample.extract_font(new_obj)[3]:accepted=False;break
                source.update(glyph_id=char[1],embedded_sha256=digest(actual))
                box=fitz.Rect(char[3])+(-3,-4,3,4)
                record[("latin","reference")[i]]={"glyph":wanted,"font":face,"box":list(box)}
            if not accepted:continue
        output=Path(output)
        if not output.is_file() or output.read_bytes()!=body:output.write_bytes(body)
        return {"cells":record,"sources":sources,"pdf_sha256":digest(body),"reader_page":page_number}
    return None

