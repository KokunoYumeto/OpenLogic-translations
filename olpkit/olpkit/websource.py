"""Assemble release inputs for replaying a native textbook's accessible web export."""
import ast
import json
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

from lxml import html

from .assembly import digest, json_bytes
from .bookcontext import BookInputs
from .cache import relative_path
from .htmlarchive import package_html_reader
from .packagecheck import unpack
from .schemas import ROOT
from .sourceexport import deterministic_zip, export_import_lock, public_unit_bytes
from .syncaccept import save_acceptance
from .webprofile import load_profile


def fields(record, keys):
    return {k: record[k] for k in keys}


def checked(path, checksum):
    data = Path(path).read_bytes()
    if digest(data) != checksum:
        raise ValueError("source differs: " + Path(path).name)
    return data


def reader_speech(folder, report):
    reader = checked(folder / "reader.html", report["products"]["reader.html"]["sha256"])
    doc = html.document_fromstring(reader, parser=html.HTMLParser(encoding="utf-8", huge_tree=True))
    speech = report["speech"]
    if speech.get("schema") != "olpkit.formula-speech-binding.v1" or not speech["canon_rule_links_complete"]:
        raise ValueError("the accepted language-owned speech binding is required")
    if digest(reader) != speech["attributed_reader_sha256"]:
        raise ValueError("released speech belongs to a different HTML edition")
    labels = []
    for node in doc.xpath("//math"):
        tex = [a for a in node.iter("annotation") if a.get("encoding", "").lower()
               in {"application/x-tex", "text/x-tex", "application/x-latex"}]
        spoken = node.get("alttext")
        if len(tex) != 1 or not spoken or spoken != node.get("aria-label"):
            raise ValueError("reader has incomplete formula labels")
        labels.append({"tex_sha256": digest("".join(tex[0].itertext()).encode()), "text": spoken})
    if len(labels) != speech["with_spoken_text"] or len(labels) != speech["formula_occurrences"]:
        raise ValueError("reader formula coverage differs from the binding")
    return {"schema": "olpkit.released-speech.v1", "language": doc.get("lang"), "labels": labels,
            **fields(speech, ["reader_sha256", "bound_reader_sha256", "model", "reasoning_effort"]),
            "attribution": speech["attribution_text"]}


def copy_replay_tool(destination, assembly, profile, licence):
    modules = {"webreplay"}
    copied = set()
    (destination / "olpkit").mkdir(parents=True)
    while modules:
        module = modules.pop()
        if module in copied:
            continue
        copied.add(module)
        source = ROOT / "olpkit" / (module + ".py")
        payload = source.read_bytes()
        (destination / "olpkit" / source.name).write_bytes(payload)
        for node in ast.walk(ast.parse(payload)):
            if isinstance(node, ast.ImportFrom) and node.level and node.module:
                modules.add(node.module)
    (destination / "olpkit/__init__.py").write_bytes((ROOT / "olpkit/__init__.py").read_bytes())
    (destination / "LICENSE").write_bytes(Path(licence).read_bytes())
    locked, _, _ = export_import_lock(assembly, profile)
    names = ["data/sources.toml", "data/build-products/" + assembly["product"] + ".json",
             "data/books/" + profile["book"] + ".toml", "schemas/book.schema.json",
             "schemas/build-product.schema.json"]
    names += [(locked / n).relative_to(ROOT).as_posix() for n in ("imports.lock", "imports.json")]
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())


def copy_figure_batches(profile, web):
    batches = []
    for number, source in enumerate(profile["figure_exports"], 1):
        original = Path(source["directory"])
        raw = checked(original / "NATIVE_FIGURES.json", source["receipt_sha256"])
        record = json.loads(raw)
        folder = web / ("figures-" + str(number))
        folder.mkdir()
        separate = fields(record, ["schema", "status", "driver_sha256", "preamble_sha256",
                                  "assembly_sha256", "source_sha256", "figures"])
        separate["configuration_evidence"] = {"native_receipt_sha256": digest(raw)}
        for row in record["figures"]:
            for key, checksum in (("source_file", "source_sha256"), ("asset", "svg_sha256")):
                name = relative_path(row[key])
                target = folder / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(checked(original / name, row[checksum]))
        output = json_bytes(separate)
        (folder / "NATIVE_FIGURES.json").write_bytes(output)
        batches.append({"directory": folder.name, "receipt_sha256": digest(output)})
    return batches


def assemble(project, build_dir, profile_path, source_export, web_export, licence, pdf_profile, instructions):
    project, build_dir, source_export, web_export = map(Path, (project, build_dir, source_export, web_export))
    build = json.loads((build_dir / "BUILD.json").read_bytes())
    assembly = json.loads(checked(build_dir / "source/ASSEMBLY.json", build["assembly_sha256"]))
    pdf_export = json.loads(source_export.read_bytes())
    report = json.loads(web_export.read_bytes())
    if (pdf_export["assembly_sha256"] != build["assembly_sha256"] or report["assembly_sha256"] != build["assembly_sha256"]
            or pdf_export["package"]["pdf_sha256"] != build["pdf"]["sha256"]
            or digest(Path(profile_path).read_bytes()) != report["profile_sha256"]):
        raise ValueError("PDF, web export and profile must belong to the same accepted build")
    profile = load_profile(profile_path)
    native_inputs = BookInputs(build_dir / "source", profile)
    profile["released_package_declarations"] = {k: native_inputs.package_declarations(k) for k in profile["packages"]}
    project.mkdir(parents=True, exist_ok=False)
    source = project / "source"
    web = project / "web"
    web.mkdir()
    archives = [k for k in pdf_export["outputs"] if k.endswith(".zip")]
    if len(archives) != 1:
        raise ValueError("expected one native editable source package")
    archive = source_export.parent / relative_path(archives[0])
    checked(archive, pdf_export["outputs"][archives[0]]["sha256"])
    members = pdf_export["package"]["files"]
    unpack(archive, members, source)
    files = {name: fields(row, ["sha256", "bytes"]) for name, row in members.items() if name in assembly["files"]}
    if not set(report["source_inputs"]) <= files.keys():
        raise ValueError("web source files absent from the PDF source archive")
    pdf_settings = json.loads(checked(pdf_profile, pdf_export["profile_sha256"]))
    origins = {}
    for row in report["projection"]["unit_order"]:
        name = row["assembled_path"]
        origin = checked(build_dir / "source" / relative_path(name), row["sha256"])
        released = (source / name).read_bytes()
        if origin != released:
            if public_unit_bytes(name, origin, pdf_settings.get("private_comment_sha256")) != released:
                raise ValueError("packaged unit has unaccounted differences: " + name)
            origins[name] = {"native_sha256": digest(origin), "editable_sha256": digest(released)}
    profile["released_unit_sources"] = origins
    rows = {r["path"] for r in report["projection"]["unit_order"]}
    scoped = {**fields(assembly, ["locale", "product", "book_directory", "sources", "edition_commit", "book_commit"]),
              "files": files, "units": [fields(r, ["id", "path", "state", "english_fill"]) for r in assembly["units"]
                                        if r["path"] in rows]}
    (source / "ASSEMBLY.json").write_bytes(json_bytes(scoped))
    witnesses = {}
    def write(role, filename, data):
        (web / filename).write_bytes(data)
        witnesses[role] = {"path": filename, "sha256": digest(data)}

    for role in ("aux", "bbl", "gls", "pcr", "thm", "toc", "css", "edition", "script", "pdf"):
        row = profile["witnesses"][role]
        write(role, "native-" + role + Path(row["path"]).suffix, checked(row["path"], row["sha256"]))
    for role, keys in (("display_settings", ["proof_label_styles", "math_font_sizes"]),
                       ("names", ["names", "pair_conjunction"])):
        row = profile["witnesses"][role]
        write(role, role + ".json", json_bytes(fields(json.loads(checked(row["path"], row["sha256"])), keys)))
    row = profile["witnesses"]["credits_policy"]
    credits = json.loads(checked(row["path"], row["sha256"]))
    write("credits_policy", "credits.json", json_bytes({"components": [
        {"id": c["id"], "reader_checks": c.get("reader_checks", [])} for c in credits["components"]]}))
    row = profile["witnesses"]["fls"]
    observed = checked(row["path"], row["sha256"]).decode("utf-8-sig").replace(chr(92), "/").splitlines()
    photos = sorted(p for p in files if p.endswith("-small.png") and any(
        line.startswith("INPUT ") and (line[6:] == p or line.endswith("/" + p)) for line in observed))
    write("fls", "photo-inputs.fls", "".join("INPUT " + p + "\n" for p in photos).encode())
    for role in profile["diagram_description_witnesses"]:
        row = profile["witnesses"][role]
        original = json.loads(checked(row["path"], row["sha256"]))
        descriptions = {key: fields(desc, ["source_sha256", "occurrence_indices", "alt_text", "long_description"])
                        for key, desc in original["descriptions"].items()}
        write(role, role + ".json", json_bytes({**fields(original, ["language", "provenance", "labels"]),
                                                "descriptions": descriptions}))
    profile["witnesses"] = witnesses
    profile["figure_exports"] = copy_figure_batches(profile, web)
    profile["packages"] = {name: {"sha256": row["sha256"]} for name, row in profile["packages"].items()}
    profile["epubcheck"]["path"] = "epubcheck.jar"
    (web / "profile.json").write_bytes(json_bytes(profile))
    (web / "speech.json").write_bytes(json_bytes(reader_speech(web_export.parent, report)))
    copy_replay_tool(project / "builder", assembly, profile, licence)
    (project / "README.md").write_bytes(Path(instructions).read_bytes())
    (project / "rebuild_web.py").write_text(
        "from pathlib import Path\nimport sys\n\n"
        "root = Path(__file__).resolve().parent\n"
        "sys.path.insert(0, str(root / 'builder'))\n"
        "from olpkit.webreplay import main\n\n"
        "if __name__ == '__main__':\n    main(default_root=root)\n", encoding="utf-8", newline="\n")
    (project / "requirements.txt").write_text("".join(
        name + "==" + version(name) + "\n" for name in ("fonttools", "jsonschema", "lxml", "PyMuPDF", "pypdf")
    ), encoding="utf-8", newline="\n")
    outputs = {name: row["sha256"] for name, row in report["products"].items()}
    for name, checksum in outputs.items():
        checked(web_export.parent / relative_path(name), checksum)
    with TemporaryDirectory(dir=project.parent) as temp:
        offline = Path(temp) / "reader-html.zip"
        package_html_reader(web_export, offline)
        outputs["reader-html.zip"] = digest(offline.read_bytes())
    document = {"schema": "olpkit.released-web-source.v1", "outputs": outputs, "inputs": {
        p.relative_to(project).as_posix(): digest(p.read_bytes()) for p in sorted(project.rglob("*")) if p.is_file()}}
    (project / "WEB-EDITION.json").write_bytes(json_bytes(document))


def package(args):
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out.parent) as temp:
        project = Path(temp) / "book"
        assemble(project, args.build, args.profile, args.source_export, args.web_export, args.builder_licence,
                 args.pdf_profile, args.instructions)
        files = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        archive = deterministic_zip(files)
        save_acceptance(out, archive)
        print(f"{len(files)} source files; ZIP SHA-256 {digest(archive)}")
    return 0
