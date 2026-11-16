"""Mark individual TeX table cells in a private diagnostic build for PDF inspection."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from .assembly import digest, json_bytes
from .build import compile_book, copy_build_input, verify_assembly
from .cache import relative_path
from .macrophases import group, skip_space
from .pdfaudit import compare_pdfs
from .schemas import ROOT
from .tableinventory import inventory


def paint_sequence(page):
    """Return ordered paint operations for a text/vector page with embedded fonts."""
    allowed = {"fill-text", "stroke-text", "fill-path", "stroke-path"}
    if any(kind not in allowed for kind, _ in page.get_bboxlog()):
        raise ValueError("unsupported page paint operation")
    fonts = []
    for xref, _, kind, name, *_ in page.get_fonts():
        program = page.parent.extract_font(xref)[3]
        if not program:
            raise ValueError("font program is unavailable")
        fonts.append((kind, name.split("+")[-1], digest(program)))
    events = []
    for span in page.get_texttrace():
        style = tuple(span.get(k) for k in ("font", "size", "type", "wmode", "dir", "color",
                                            "opacity", "linewidth", "layer"))
        for code, gid, position, rectangle in span["chars"]:
            events.append((span["seqno"], ("glyph", style, code, gid), (*position, *rectangle)))
    for path in page.get_drawings(extended=True):
        if path["type"] not in ("s", "f", "fs"):
            raise ValueError("unsupported vector operation")
        order = path.pop("seqno")
        events.append((order, ("path", path), ()))
    events.sort(key=lambda e: e[0])
    return sorted(fonts), events


def diagnostic_text_check(native, marked, texts, page_counts):
    """Resolve extraction-order differences only for the tagged measurement PDF."""
    import fitz
    if texts[0] == texts[1] and page_counts[0] == page_counts[1]:
        return {"pass": True, "poppler_equal": True, "pages_replayed": []}
    evidence = {"pass": False, "poppler_equal": False, "pages_replayed": []}
    if page_counts[0] != page_counts[1]:
        return evidence
    native_text, marked_text = (t.decode("utf-8").split("\f") for t in texts)
    if len(native_text) != page_counts[0]+1 or len(marked_text) != len(native_text) or native_text[-1] or marked_text[-1]:
        return evidence
    with fitz.open(native) as first, fitz.open(marked) as second:
        for i, (a, b) in enumerate(zip(native_text[:-1], marked_text[:-1], strict=True)):
            if a == b:
                continue
            left, right = first[i], second[i]
            if (Counter(a) != Counter(b) or left.rect != right.rect or left.rotation != right.rotation
                    or left.get_text() != right.get_text()):
                return evidence
            try:
                fonts, ops = paint_sequence(left)
                other_fonts, other_ops = paint_sequence(right)
            except ValueError:
                return evidence
            if fonts != other_fonts or len(ops) != len(other_ops):
                return evidence
            displacement = 0
            for (_, shape, points), (_, other_shape, other_points) in zip(ops, other_ops, strict=True):
                if shape != other_shape or len(points) != len(other_points):
                    return evidence
                for x, y in zip(points, other_points, strict=True):
                    displacement = max(displacement, abs(x-y))
            # Tagged XeTeX runs split text objects at cell boundaries. Allow only
            # sub-hundredth-point text positioning; vector paths must be identical.
            if displacement > 0.01:
                return evidence
            evidence["pages_replayed"].append({"page": i+1, "paint_events": len(ops),
                                               "embedded_fonts": len(fonts),
                                               "max_glyph_displacement_bp": displacement})
    evidence["pass"] = bool(evidence["pages_replayed"])
    return evidence


def mark_cells(text, unit, engine, first_id):
    literal = {"pdflatex": r"\pdfliteral direct", "lualatex": r"\pdfextension literal direct",
               "xelatex": r"\special"}[engine]
    prefix = "pdf:literal direct " if engine == "xelatex" else ""
    records, unsupported, insertions = [], [], defaultdict(list)
    for number, table in enumerate(inventory(text, unit)["tables"], 1):
        if table["syntax_status"] != "parsed":
            unsupported.append({"unit": unit, "table": number, "reason": table["error"]})
            continue
        for row_no, row in enumerate(table["rows"], 1):
            for cell in row["cells"]:
                mcid = first_id + len(records)
                record = {"id": mcid, "unit": unit, "table": number, "row": row_no,
                          "col": cell["column"], "span": cell["column_span"], "rows": cell["row_span"],
                          "source_tex": cell["source_tex"], "implicit": cell["implicit"],
                          "environment": table["environment"],
                          "required_math_direction": cell["required_math_direction"]}
                records.append(record)
                if cell["implicit"]:
                    continue
                start, end = cell["char_start"], cell["char_end"]
                multi = re.match(r"\\multicolumn\b", text[start:end])
                if multi:
                    # TeX requires \omit to be the first item in this cell.
                    pos = start + multi.end()
                    _, pos = group(text, pos)
                    _, pos = group(text, pos)
                    start = skip_space(text, pos) + 1
                    _, end = group(text, start - 1)
                    end -= 1
                begin = literal + "{" + prefix + "/OLPCell << /MCID " + str(mcid) + " >> BDC}"
                close = literal + "{" + prefix + "EMC}"
                if start == end:
                    insertions[start].append(begin + close)
                else:
                    insertions[start].append(begin)
                    insertions[end].insert(0, close)
    for pos in sorted(insertions, reverse=True):
        text = text[:pos] + "".join(insertions[pos]) + text[pos:]
    return text, records, unsupported


def measure_pdf(native, marked, records):
    """Transfer cell IDs to actual reader glyphs after replaying the full page's character stream."""
    import fitz
    import pdfplumber
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.layout import LTChar, LTContainer
    from pdfminer.utils import decode_text
    from pdfplumber.page import PDFPageAggregatorWithMarkedContent
    class CellAggregator(PDFPageAggregatorWithMarkedContent):
        # HarfBuzz uses nested ActualText spans for Indic clusters. Keep the
        # enclosing cell through those spans and through nested tables.
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.stack=[]
            self.actual=None
            self.replacements={}

        def begin_tag(self,tag,props=None):
            self.stack.append((self.cur_tag,self.cur_mcid,self.actual))
            if tag.name=="OLPCell":
                super().begin_tag(tag,props)
            if isinstance(props,dict) and isinstance(props.get("ActualText"),bytes):
                self.actual=[decode_text(props["ActualText"]),False]

        def end_tag(self):
            if not self.stack: raise ValueError("unbalanced marked-content end tag")
            self.cur_tag,self.cur_mcid,self.actual=self.stack.pop()

        def render_char(self,*args,**kwargs):
            advance=super().render_char(*args,**kwargs)
            if self.actual is not None:
                char=self.cur_item._objs[-1]
                self.replacements[id(char)]="" if self.actual[1] else self.actual[0]
                self.actual[1]=True
            return advance

    def page_glyphs(page):
        device=CellAggregator(page.pdf.rsrcmgr,pageno=page.page_number,laparams=page.pdf.laparams)
        PDFPageInterpreter(page.pdf.rsrcmgr,device).process_page(page.page_obj)
        if device.stack: raise ValueError("unclosed marked-content sequence")
        def walk(item):
            if isinstance(item,LTChar):
                obj=page.process_object(item)
                obj["actual"]=device.replacements.get(id(item),obj["text"])
                yield obj
            elif isinstance(item,LTContainer):
                for child in item: yield from walk(child)
        return list(walk(device.get_result()))

    wanted = {r["id"] for r in records}
    paint = defaultdict(list)
    shipped = defaultdict(set)
    issues = []
    pages = []
    marker = re.compile(rb"/OLPCell\s*<<\s*/MCID\s+(\d+)\s*>>\s*BDC")
    with fitz.open(marked) as doc:
        for n, page in enumerate(doc, 1):
            ids = {int(key) for obj in page.get_contents() for key in marker.findall(doc.xref_stream(obj))}
            for obj, *_ in page.get_xobjects():
                if marker.search(doc.xref_stream(obj)):
                    issues.append({"page": n, "reason": "cell in form XObject needs invocation binding"})
            if ids:
                pages.append(n)
            for key in ids:
                shipped[key].add(n)
    if pages:
        with pdfplumber.open(native, pages=pages) as reader, pdfplumber.open(marked, pages=pages) as diagnostic:
            for page, probe in zip(reader.pages, diagnostic.pages, strict=True):
                native_chars=page_glyphs(page)
                tagged_chars=page_glyphs(probe)
                def identity(char):
                    return (char["text"],char["actual"], re.sub(r"^[A-Z]{6}\+", "", char["fontname"]))
                if ([identity(c) for c in native_chars] != [identity(c) for c in tagged_chars]
                        or page.bbox != probe.bbox):
                    issues.append({"page": page.page_number, "reason": "native/diagnostic glyph stream differs"})
                else:
                    for obj, tagged in zip(native_chars, tagged_chars, strict=True):
                        key = tagged.get("mcid")
                        if tagged.get("tag") == "OLPCell" and key in wanted:
                            paint[key].append({"page":page.page_number,"text":obj["actual"],
                                               "glyph_text":obj["text"],
                                               "box":[round(obj[s],3) for s in ("x0","top","x1","bottom")]})
                page.close()
                probe.close()
    return ([{"cell": key, "glyphs": glyphs} for key, glyphs in sorted(paint.items())],
            {key:sorted(values) for key,values in shipped.items()}, issues)


def probe_build(build_dir):
    """Run one guarded diagnostic book, with all cells instrumented in one pass sequence."""
    build_dir = Path(build_dir).resolve()
    if not build_dir.is_relative_to((ROOT.parent / "out").resolve()):
        raise ValueError("expected a native build in the builder output directory")
    build = json.loads((build_dir / "BUILD.json").read_bytes())
    source = build_dir / "source"
    original = json.loads((source / "ASSEMBLY.json").read_bytes())
    if build["assembly_sha256"] != digest(json_bytes(original)) or not build.get("pdf"):
        raise ValueError("table probe needs an intact, compiled native build")
    verify_assembly(source, original)
    pdf = build_dir / relative_path(build["pdf"]["path"])
    if digest(pdf.read_bytes()) != build["pdf"]["sha256"]:
        raise ValueError("native PDF changed since compilation")
    probe = build_dir / "table-probe"
    tree = probe / "source"
    receipt = probe / "BUILD.json"
    assembly = json.loads(json_bytes(original))
    native_units = {relative: path for path, names in build["content_inputs"].items() for relative in names}
    records, unsupported = [], []
    for name, member in assembly["files"].items():
        relative = relative_path(name)
        path = tree / relative
        if name in native_units:
            body = (source / relative).read_bytes()
            text, cells, issues = mark_cells(body.decode("utf-8"), native_units[name],
                                              build["engine"], 10000 + len(records))
            records.extend(cells)
            unsupported.extend(issues)
            data = text.encode("utf-8")
            if data != body:
                member["uninstrumented_sha256"] = member["sha256"]
                member["sha256"] = digest(data)
                member["bytes"] = len(data)
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_bytes(data)
                continue
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            copy_build_input(source / relative, path)
    assembly["purpose"] = "private rendered-cell measurement"
    verify_assembly(tree, assembly)
    assembly_path = tree / "ASSEMBLY.json"
    if assembly_path.exists() and assembly_path.read_bytes() != json_bytes(assembly):
        raise ValueError("table probe inputs differ from their earlier recipe")
    assembly_path.write_bytes(json_bytes(assembly))
    earlier = json.loads(receipt.read_bytes()) if receipt.exists() else {}
    if not earlier or earlier["status"] == "slot_occupied":
        expected = [(None, name) for name in build["content_inputs"]]
        earlier = compile_book(tree, assembly, build["engine"], build["source_date_epoch"],
                               probe, expected, "locale" not in assembly, bool(earlier))
    if earlier["status"] == "slot_occupied":
        return {"status": "slot_occupied"}
    if earlier["status"] == "failed" or not earlier.get("pdf"):
        raise ValueError("table probe did not compile: "+str(earlier.get("error", "see BUILD.json")))
    instrumented = probe / relative_path(earlier["pdf"]["path"])
    diagnostic_hash=digest(instrumented.read_bytes())
    if diagnostic_hash!=earlier["pdf"]["sha256"]:
        raise ValueError("diagnostic PDF differs from its build receipt")
    keys={"native_sha256":build["pdf"]["sha256"],"diagnostic_sha256":diagnostic_hash,
          "probe_code_sha256":digest(Path(__file__).read_bytes()),
          "inventory_code_sha256":digest(Path(__file__).with_name("tableinventory.py").read_bytes()),
          "assembly_sha256":earlier["assembly_sha256"]}
    cells_path=probe/"CELLS.json"
    witness=probe/"CELL-RECEIPT.json"
    if witness.is_file() and cells_path.is_file():
        saved=json.loads(witness.read_bytes())
        data=cells_path.read_bytes()
        if saved.get("inputs")==keys and saved.get("sha256")==digest(data):
            return json.loads(data)
    cmp, texts = compare_pdfs(pdf, instrumented)
    diagnostic = diagnostic_text_check(pdf, instrumented, texts, cmp["pages"])
    paint, shipped, issues = measure_pdf(pdf, instrumented, records)
    evidence = {"pages": cmp["pages"], "text_sha256": cmp["text_sha256"], "native": build["pdf"]["sha256"],
                "diagnostic": earlier["pdf"]["sha256"], "same_rendered_text": diagnostic["pass"],
                "diagnostic_text_check": diagnostic,
                "records": records, "unsupported": unsupported, "paint": paint, "shipped": shipped,
                "binding_issues": issues}
    raw=json_bytes(evidence)
    cells_path.write_bytes(raw)
    witness.write_bytes(json_bytes({"inputs":keys,"sha256":digest(raw)}))
    return evidence

