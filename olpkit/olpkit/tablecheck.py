"""Compare rendered cells from matched English and localized native textbook builds."""
from collections import defaultdict
import json
from pathlib import Path
import re
import tomllib

from .assembly import digest, json_bytes
from .cache import relative_path
from .schemas import ROOT
from .tableprobe import probe_build
from .texttokens import TextTokens


def cells_by_location(report):
    placed = {str(k): v for k,v in report["shipped"].items()}
    paint = {r["cell"]:r["glyphs"] for r in report["paint"]}
    rows = {}
    for c in report["records"]:
        key = c["unit"], c["table"], c["row"], c["col"]
        if key in rows:
            raise ValueError("two cells at one logical position")
        rows[key] = {**c, "glyphs":paint.get(c["id"], []), "pages":placed.get(str(c["id"]), [])}
    return rows


def printed(cell):
    return "".join(c["text"] for c in cell["glyphs"])


def bounds(chars):
    return [min(g["box"][0] for g in chars), min(g["box"][1] for g in chars),
            max(g["box"][2] for g in chars), max(g["box"][3] for g in chars)]


def type_block(directory, build):
    log = (directory / build["pdf"]["path"]).with_suffix(".log").read_bytes()
    if digest(log) != build["log_sha256"]:
        raise ValueError("native log no longer matches its receipt")
    log = log.decode("utf-8",errors="replace")
    def pair(label, sep):
        matches=set(re.findall(re.escape(label)+r": ([\d.]+)pt "+sep+r" ([\d.]+)pt",log))
        if len(matches) != 1: raise ValueError("need one recorded memoir layout for "+label)
        return [float(x)*72/72.27 for x in next(iter(matches))]
    height, width=pair("Text height and width","by")
    spine, edge=pair("Spine and edge margins","and")
    upper, _=pair("Upper and lower margins","and")
    if abs(spine-edge)>0.1 or pair("Top and edge trims","and") != [0,0]:
        raise ValueError("asymmetric or trimmed pages require separate recto/verso type blocks")
    return [min(spine,edge),upper,max(spine,edge)+width,upper+height]


def expected_literal(cell, expander):
    tex=cell["source_tex"]
    if "!!" in tex or re.search(r"\\(?:printtoken|usetoken)\b", tex):
        tex,_=expander.expand(tex,"table-cell-"+str(cell["id"]))
    # Resolve only text cells and simple inline symbols. Complex mathematics
    # must match the English rendering or have an explicit editorial witness.
    tex=tex.replace(r"\text{","{").replace(r"\sigma","σ")
    if "\\" in tex: return None
    return re.sub(r"[\s{}$~]","",tex)


def localized_proof_labels(printed_source, old, new, labels):
    """Match suffixes of sequent rule names without replacing proposition letters."""
    connectives = {"land": "∧", "lor": "∨", "lnot": "¬", "lif": "→", "liff": "↔"}
    result = printed_source
    for label in labels:
        command = r"\\" + re.escape(label["command"]) + r"\b"
        if not all(re.search(command, cell["source_tex"]) for cell in (old, new)):
            continue
        if label["command"] in ("LeftR", "RightR"):
            pattern = command + r"\s*\{\s*\\(\w+)\s*\}"
            source_args = re.findall(pattern, old["source_tex"])
            if source_args != re.findall(pattern, new["source_tex"]):
                continue
            for arg in source_args:
                if arg in connectives:
                    op = connectives[arg]
                    result = result.replace(op + label["english"], op + label["target"], 1)
        else:
            result = result.replace(label["english"], label["target"])
    return result


def math_direction_changed(source, target):
    """Compare horizontally separated glyphs on the same line in both books."""
    for i, (left, other) in enumerate(zip(source,target,strict=True)):
        for right, following in zip(source[i+1:],target[i+1:],strict=True):
            def side(a,b):
                if a["page"]!=b["page"]: return 0
                ax,ay,bx,by=a["box"]; cx,cy,dx,dy=b["box"]
                overlap=min(by,dy)-max(ay,cy)
                if overlap <= .65*min(by-ay,dy-cy): return 0
                if cx >= bx-.05: return 1
                if ax >= dx-.05: return -1
                return 0
            if side(left,right)*side(other,following)<0: return True
    return False


def glyph_ink_outside(page, glyphs, block):
    """PDF font metrics include blank space around the glyph. Inspect the protruding area."""
    import fitz
    x,y,r,b=block
    outside=[(0,0,x,page.rect.height),(r,0,page.rect.width,page.rect.height),
             (0,0,page.rect.width,y),(0,b,page.rect.width,page.rect.height)]
    for glyph in glyphs:
        for side in outside:
            rect=fitz.Rect(glyph["box"]) & fitz.Rect(side)
            if rect.width<=.1 or rect.height<=.1: continue
            # Ignore the one boundary pixel that straddles the type-block edge.
            rect=fitz.Rect(rect.x0+.08,rect.y0+.08,rect.x1-.08,rect.y1-.08)
            if rect.is_empty: continue
            pix=page.get_pixmap(matrix=fitz.Matrix(12,12),clip=rect,colorspace=fitz.csGRAY,alpha=False)
            if pix.samples and min(pix.samples)<180: return True
    return False


def confirmed_corrections(en, tr, decisions):
    def table_hash(cells, unit, number):
        rows=[(c["row"],c["col"],c["source_tex"],c["implicit"],c["span"],c["rows"])
              for key,c in sorted(cells.items()) if key[:2]==(unit,number)]
        return digest(json_bytes(rows))
    confirmed={}
    for decision in decisions:
        unit,number=decision["unit"],decision["table"]
        if table_hash(en,unit,number)!=decision["english_table_sha256"]:continue
        if table_hash(tr,unit,number)!=decision["target_table_sha256"]:continue
        matches={}
        for cell in decision["cells"]:
            key=unit,number,cell["row"],cell["col"]
            if printed(en[key])!=cell["english"] or printed(tr[key])!=cell["target"]:break
            matches[key]=decision["id"]
        else:
            confirmed.update(matches)
    return confirmed


def witnessed_glyph(pdf, glyph, witness):
    """Identify the visible glyph at this position in the inspected font program."""
    import fitz
    page = pdf[glyph["page"]-1]
    box = fitz.Rect(glyph["box"])
    matches = []
    for span in page.get_texttrace():
        if span["font"] != witness["font"] or span["type"] != 0 or span["dir"] != (1.0, 0.0):
            continue
        for char, gid, _, area in span["chars"]:
            center = (fitz.Point(area[:2]) + fitz.Point(area[2:])) / 2
            if chr(char) == witness["text"] and box.contains(center):
                matches.append(gid)
    if matches != [witness["gid"]]:
        return False
    programs = {digest(pdf.extract_font(f[0])[3]) for f in page.get_fonts()
                if f[3].split("+")[-1] == witness["font"]}
    return programs == {witness["program_sha256"]}


def symbol_mapping(old, new, rules, english_pdf, target_pdf):
    if english_pdf is None or old["source_tex"] != new["source_tex"]:
        return None
    for rule in rules:
        before, after = rule["english"], rule["target"]
        occurrences = len(re.findall(r"\\" + re.escape(rule["command"]) + r"\b", old["source_tex"]))
        source, target = printed(old), printed(new)
        if (not occurrences or source.count(before["text"]) != occurrences
                or source.replace(before["text"], after["text"]) != target):
            continue
        for cell, pdf, witness in ((old, english_pdf, before), (new, target_pdf, after)):
            glyphs = [g for g in cell["glyphs"] if g["text"] == witness["text"]]
            if len(glyphs) != occurrences or not all(witnessed_glyph(pdf, g, witness) for g in glyphs):
                break
        else:
            if (len(old["glyphs"]) == len(new["glyphs"])
                    and not math_direction_changed(old["glyphs"], new["glyphs"])):
                return rule["command"]
    return None


def compare_tables(english, translation, policy, expander, block, native_pdf, decisions=(), english_pdf=None):
    en=cells_by_location(english); tr=cells_by_location(translation)
    corrections=confirmed_corrections(en,tr,decisions)
    differences=[]; unresolved=[]; checked=[]; geometries=defaultdict(list)
    confirmed_symbols = []
    table_modes=defaultdict(set)
    for key,cell in en.items():
        if cell["source_tex"].strip() and cell["glyphs"]:
            table_modes[key[:2]].add(cell["required_math_direction"])
    for data in (english,translation):
        unresolved.extend(data["binding_issues"]+data["unsupported"])
        if not data["same_rendered_text"]:
            unresolved.append({"reason":"diagnostic text or pagination differs"})
    for key in sorted(en.keys() | tr.keys()):
        if key not in en or key not in tr:
            differences.append({"location":key,"reason":"missing source or target cell"})
            continue
        old,new=en[key],tr[key]
        source,target=printed(old),printed(new)
        issue={"location":key,"source":source,"target":target}
        if (old["span"],old["rows"]) != (new["span"],new["rows"]):
            differences.append({**issue,"reason":"cell span differs"})
        if bool(old["pages"]) != bool(new["pages"]) and key not in corrections:
            differences.append({**issue,"reason":"cell shipped on only one side"})
        localized=localized_proof_labels(source,old,new,policy.get("proof_labels",[]))
        if localized != target and key not in corrections:
            symbol = symbol_mapping(old, new, policy.get("symbol_mappings", []), english_pdf, native_pdf)
            expected=expected_literal(new,expander)
            if symbol:
                confirmed_symbols.append({**issue, "command": symbol})
            elif expected != target.replace("𝜎","σ") or new["environment"]=="array" and r"\text{" not in new["source_tex"]:
                unresolved.append({**issue,"reason":"rendering differs; check target text or a pinned correction"})
        elif (old["required_math_direction"]=="ltr" and source==target and source
              and len(old["glyphs"])==len(new["glyphs"])):
            if math_direction_changed(old["glyphs"],new["glyphs"]):
                differences.append({**issue,"reason":"glyphs reverse horizontal order"})
        if not new["glyphs"]: continue
        for page in sorted({g["page"] for g in new["glyphs"]}):
            glyphs=[g for g in new["glyphs"] if g["page"]==page]
            area=bounds(glyphs)
            if area[0]<block[0]-.1 or area[1]<block[1]-.1 or area[2]>block[2]+.1 or area[3]>block[3]+.1:
                if glyph_ink_outside(native_pdf[page-1],glyphs,block):
                    differences.append({**issue,"page":page,"box":area,"reason":"cell ink outside type block"})
            geometries[(key[:3],page)].append((key[3],area))
        checked.append(key)
    for (row,page), cells in geometries.items():
        direction = "math" if table_modes[row[:2]] == {"ltr"} else "text"
        descending=policy[direction]=="rtl"
        cells.sort()
        for (_,left),(column,right) in zip(cells,cells[1:]):
            if (right[0]+right[2] < left[0]+left[2]) != descending:
                differences.append({"location":(*row,column),"page":page,"reason":"columns reverse declared order"})
    return {"status":"fail" if differences else ("incomplete" if unresolved else "pass"),
            "english_pdf_sha256":english["native"],"target_pdf_sha256":translation["native"],
            "source_cells":len(en),"target_cells":len(tr),"target_painted_cells":len(checked),
            "differences":differences,"unresolved":unresolved,"type_block_bp":block,
            "confirmed_symbol_mappings":confirmed_symbols,
            "confirmed_corrections":[{"location":k,"id":v} for k,v in sorted(corrections.items())]}


def verify_proof_label_sources(labels, files, recorder_inputs):
    recorded = {(row["path"], row["sha256"]) for row in recorder_inputs
                if row["kind"] == "assembled-tree"}
    for label in labels:
        path = label["path"]
        source_hash = files.get(path, {}).get("sha256")
        allowed = (label["sha256"], *label.get("other_source_sha256", ()))
        if source_hash not in allowed or (path, source_hash) not in recorded:
            raise ValueError("proof-label policy differs from the TeX input actually read")


def table_gate(output, assembly, build, english_dir):
    english_dir=Path(english_dir).resolve()
    en_build=json.loads((english_dir/"BUILD.json").read_bytes())
    en_assembly=json.loads((english_dir/"source/ASSEMBLY.json").read_bytes())
    if (en_build["status"]!="reference_compiled" or en_assembly.get("pins")!={k:r["commit"] for k,r in assembly["sources"].items()}
            or set(en_build["content_inputs"])!=set(build["content_inputs"])):
        raise ValueError("English comparison must use the same book pins and import set")
    profile=tomllib.loads((ROOT/"data/languages"/(assembly["locale"]+".toml")).read_text("utf-8"))
    if "tables" not in profile:
        return {"status":"incomplete","reason":"language table policy not configured"}
    verify_proof_label_sources(profile["tables"].get("proof_labels", ()), assembly["files"], build["recorder_inputs"])
    en=probe_build(english_dir)
    if en.get("status")=="slot_occupied":return en
    tr=probe_build(output)
    if tr.get("status")=="slot_occupied":return tr
    tokens=TextTokens()
    root=output/"source"
    native="sty/open-logic-tokenize.sty"
    tokens.configure_native((root/native).read_text("utf-8-sig"),native)
    for name in profile["tables"]["token_files"]:
        relative=relative_path(name)
        if name not in assembly["files"]:
            raise ValueError("locale token file missing from assembly: "+name)
        tokens.configure((root/relative).read_text("utf-8-sig"),name)
    import fitz
    with (fitz.open(output / relative_path(build["pdf"]["path"])) as pdf,
          fitz.open(english_dir / relative_path(en_build["pdf"]["path"])) as english_pdf):
        decisions=json.loads((ROOT/"data/table-corrections.json").read_bytes())
        result=compare_tables(en,tr,profile["tables"],tokens,type_block(output,build),pdf,decisions,english_pdf)
    for label,directory in (("english",english_dir),("target",output)):
        path=directory/"table-probe/CELLS.json"
        result[label+"_evidence"]={"file":str(path),"sha256":digest(path.read_bytes())}
    return result


def reference_for_tables(assembly, book, cache):
    from .build import build_command
    from .importlock import pin_key
    pins={k:v["commit"] for k,v in assembly["sources"].items()}
    out=ROOT.parent/"out"
    historical=out/(book["source_id"]+"-reference-"+pins["olp"][:8])
    reference=out/"english-references"/pin_key(pins)/assembly["product"]
    for directory in (historical,reference):
        manifest=directory/"source/ASSEMBLY.json"
        receipt=directory/"BUILD.json"
        if manifest.is_file() and receipt.is_file():
            a=json.loads(manifest.read_bytes()); b=json.loads(receipt.read_bytes())
            if (a.get("pins")==pins and a.get("book_directory")=="courses/"+book["id"]
                    and b["status"]=="reference_compiled"):
                return directory
    resume=(reference/"BUILD.json").is_file()
    code=build_command(None,None,None,None,cache,reference,assembly["product"],True,pins["olp"],resume)
    return None if code==75 else reference

