"""Measure body glyphs in the actual reader against the published edition specimen."""
from collections import Counter
import json
from pathlib import Path
import tomllib

import fitz

from .assembly import digest
from .pdfscale import inspect_scale
from .schemas import ROOT


def reader_scale(output, build, locale, book):
    language_path = ROOT / "data/languages" / (locale + ".toml")
    language = tomllib.loads(language_path.read_text("utf-8"))
    receipt = ROOT / "data/books" / book / "scale-samples" / (locale + ".json")
    if not receipt.is_file() or "scale" not in language:
        return {"status":"incomplete","reason":"No edition-bound specimen and language threshold pair."}
    pdf = output / build["pdf"]["path"]
    pdf_hash = digest(pdf.read_bytes())
    if pdf_hash != build["pdf"]["sha256"]:
        raise ValueError("reader bytes differ from build receipt")
    raw = receipt.read_bytes()
    reference = json.loads(raw)
    specimen = reference["published_specimen"]
    if specimen["locale"] != locale or specimen["reference"]["glyph"] != language["scale"]["reference_glyph"]:
        raise ValueError("published specimen and language policy differ")
    binding = {"body_pdf_sha256":pdf_hash,"language_sha256":digest(language_path.read_bytes()),
               "published_pdf_sha256":reference.get("published_pdf_sha256",specimen["pdf_sha256"]),
               "published_specimen_sha256":digest(raw)}
    roles = [(specimen[k]["font"], ord(specimen[k]["glyph"])) for k in ("latin","reference")]
    with fitz.open(pdf) as doc:
        # Keep the specimen representative of normal body type even if a new
        # edition moves it or changes the nominal size used by the main text.
        frequencies = [Counter(), Counter()]
        candidate_pages = []
        for page in doc:
            present=set()
            for span in page.get_texttrace():
                face=span["font"].split("+")[-1]
                for i,(font,char) in enumerate(roles):
                    if face != font: continue
                    count=sum(c[0]==char for c in span["chars"])
                    if count:
                        frequencies[i][round(span["size"],2)]+=count
                        present.add(i)
            if len(present)==2:candidate_pages.append(page.number)
        if any(not counts for counts in frequencies):
            return {**binding,"status":"fail","reason":"Required reader specimen font or glyph is absent."}
        sizes = [counts.most_common(1)[0][0] for counts in frequencies]
        candidate_pages.sort(key=lambda n:(n+1!=reference.get("reader_page",specimen["page"]),n))
        attempts=0
        for page_number in candidate_pages:
            page=doc[page_number]
            chars=[(s,c,fitz.Rect(c[3])) for s in page.get_texttrace() for c in s["chars"]]
            if reference.get("measurement")=="isolated-line":
                from .scaleline import isolated_line
                roles_with_size=[(font,chr(ch),size) for (font,ch),size in zip(roles,sizes,strict=True)]
                artifact=output/"G-SCALE-SPECIMEN.pdf"
                line=isolated_line(pdf,page_number+1,roles_with_size,artifact)
                if line is None:continue
                current={"schema_version":1,"locale":locale,"page":1,"pdf_sha256":line["pdf_sha256"],**line["cells"]}
                measurement=inspect_scale(artifact,current,language)
                return {**measurement,**binding,"specimen":current,"reader_binding":line,
                        "specimen_file":artifact.name}
            choices=[]
            for (font,glyph),size in zip(roles,sizes,strict=True):
                choices.append([(c,rect) for s,c,rect in chars if c[0]==glyph
                                and s["font"].split("+")[-1]==font and round(s["size"],2)==size
                                and sum(rect.intersects(other) for _,_,other in chars)==1])
            for left,lbox in choices[0]:
                for right,rbox in choices[1]:
                    if abs(left[2][1]-right[2][1])>.4 or lbox.intersects(rbox):continue
                    current={"schema_version":1,"locale":locale,"pdf_sha256":pdf_hash,"page":page_number+1,
                             "latin":{**specimen["latin"],"box":list(lbox)},
                             "reference":{**specimen["reference"],"box":list(rbox)}}
                    result=inspect_scale(pdf,current,language)
                    attempts+=1
                    # The first measurable pair decides the check, including a
                    # failed ratio. Only isolation errors select another pair.
                    if result.get("ratio") is not None:
                        return {**result,**binding,"specimen":current,"candidate_pairs_inspected":attempts}
                    if attempts>=64:
                        return {**binding,"status":"incomplete","reason":"No isolated measurable body pair in 64 candidates.",
                                "last_issues":result["issues"]}
    return {**binding,"status":"incomplete","reason":"No isolated body specimen on a shared baseline."}

