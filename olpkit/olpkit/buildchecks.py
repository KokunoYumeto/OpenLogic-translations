"""Checks that bind a settled textbook build to its source and independent replay."""
import json
from pathlib import Path
import tomllib

from .assembly import digest, json_bytes
from .cache import relative_path
from .importlock import pin_key, select_lock
from .schemas import ROOT


def native_pdf_checks(output, build, assembly, book):
    from . import pdfaudit, linkpaint
    from .build import record_pdf_credits, record_pdf_glyphs, record_pdf_links
    language=(ROOT/'data/languages'/(assembly['locale']+'.toml')).read_bytes()
    links=tomllib.loads(language.decode('utf-8'))['links']
    prior=output/'PDF-CHECK-INPUTS.json'
    previous=json.loads(prior.read_bytes()) if prior.is_file() else {}
    inputs={'pdf_sha256':build['pdf']['sha256'],'engine':build['engine'],'G-LOG':build['gates']['G-LOG'],
            'language_sha256':digest(language),'pdfaudit':digest(Path(pdfaudit.__file__).read_bytes()),
            'linkpaint':digest(Path(linkpaint.__file__).read_bytes())}
    def saved(name):
        report=output/(name+'.json')
        return (previous.get('inputs')==inputs and report.is_file()
                and digest(report.read_bytes())==build['gates'].get(name,{}).get('sha256'))
    if not saved('G-GLYPH'):
        record_pdf_glyphs(output,build)
    if not saved('G-LINK'):
        record_pdf_links(output,build,links['minimum_contrast'],links['color'],xdvipdfmx=build['engine']=='xelatex')
    prior.write_bytes(json_bytes({'inputs':inputs}))
    # Actual notice bytes and individual PDF credit spans are inexpensive to check.
    filename = book['source_id'] + '-' + assembly['locale'] + '.json'
    policies = ROOT / 'data' / 'credits'
    pins = {source: record['commit'] for source, record in assembly['sources'].items()}
    scoped = policies / 'pins' / pin_key(pins) / filename
    record_pdf_credits(output, build, scoped if scoped.is_file() else policies / filename)


def save_gate(output, build, name, result):
    payload = json_bytes(result)
    path = output / (name + ".json")
    path.write_bytes(payload)
    build["gates"][name] = {"status": result["status"], "report": path.name,
                            "sha256": digest(payload)}
    (output / "BUILD.json").write_bytes(json_bytes(build))


def unit_gates(output, build, assembly, repo, cache, lock, metadata_dir=None):
    from . import unitlint, orthography, structure
    scope = lock / "imports.lock"
    rules = digest(unitlint.CONTRACT_BYTES + b"".join(Path(m.__file__).read_bytes()
                   for m in (unitlint, orthography, structure)))
    lint_dir = output / "unit-checks" / rules
    unitlint.lint_units(repo, assembly["edition_commit"], cache, lint_dir, scope=scope,
                        metadata_dir=metadata_dir, contract_hashes=assembly["contract_hashes"])
    path = lint_dir / "LINT.json"
    raw = path.read_bytes()
    lint = json.loads(raw)
    unresolved = [row for row in lint["findings"] if row["in_scope"] and "exception" not in row]
    groups = {"G-STRUCT": [], "G-NOTE": [], "G-TOKEN": [], "G-ORTHO": []}
    for row in unresolved:
        rule = row["rule"]
        if rule in ("footnotes", "note-commands"):
            gate = "G-NOTE"
        elif rule.startswith("token:"):
            gate = "G-TOKEN"
        elif rule.startswith("orthography:"):
            gate = "G-ORTHO"
        else:
            gate = "G-STRUCT"
        finding = {"unit":row["unit"], "rule":rule, "finding_sha256":row["finding_sha256"]}
        groups[gate].append(finding)
        if rule == "environments":
            groups["G-NOTE"].append(finding)
    for gate, findings in groups.items():
        status = "fail" if findings else "pass"
        if not findings and (lint["unbound_exceptions"] or
                             (gate == "G-ORTHO" and lint["orthography_status"] != "configured")):
            status = "incomplete"
        if gate == "G-NOTE" and status == "pass":
            status = "pending_editorial_probe"
        save_gate(output, build, gate, {
            "status": status, "scope_units": lint["selected_units"], "findings": findings,
            "unit_lint": path.relative_to(output).as_posix(), "unit_lint_sha256": digest(raw),
            "policy_sha256": lint["orthography_sha256"] if gate == "G-ORTHO" else lint["unit_contract_sha256"]})


def reproducibility_gate(output, build, assembly, expected):
    from .build import compile_book, copy_build_input, verify_assembly
    from .pdfaudit import compare_pdfs
    source = output / "source"
    verify_assembly(source, assembly)
    first = output / "NATIVE-BUILD.json"
    if not first.exists():
        with first.open("xb") as stream:
            stream.write(json_bytes(build))
    replay = output / "reproducibility"
    tree = replay / "source"
    if not tree.exists():
        tree.mkdir(parents=True)
        for name in assembly["files"]:
            relative = relative_path(name)
            target = tree / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_build_input(source / relative, target)
        (tree / "ASSEMBLY.json").write_bytes(json_bytes(assembly))
    verify_assembly(tree, assembly)
    receipt = replay / "BUILD.json"
    second = json.loads(receipt.read_bytes()) if receipt.is_file() else {}
    if not second or second.get("status") == "slot_occupied":
        second = compile_book(tree, assembly, build["engine"], build["source_date_epoch"],
                              replay, expected, resume=bool(second))
    if second.get("status") == "slot_occupied":
        return {"status": "slot_occupied", "report": "reproducibility/BUILD.json"}
    if not second.get("pdf") or second["status"] == "failed":
        raise ValueError("independent compilation failed, see reproducibility/BUILD.json")
    comparison, _ = compare_pdfs(output / build["pdf"]["path"], replay / second["pdf"]["path"],
                                 first, receipt)
    return {**comparison, "status": comparison["G-SAME"]["status"]}


def verify_native_build(output, repo, cache, metadata_dir=None, web_profile=None, web_product="accessible"):
    from .build import load_build_product, verify_assembly
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT.parent / "out").resolve()):
        raise ValueError("expected a native olpkit build directory")
    receipt = output / "BUILD.json"
    build = json.loads(receipt.read_bytes())
    assembly = json.loads((output / "source/ASSEMBLY.json").read_bytes())
    if (build.get("assembly_sha256") != digest(json_bytes(assembly))
            or assembly["files"] != build["source_inputs"] or not build.get("pdf")):
        raise ValueError("build receipt does not bind a compiled assembly")
    verify_assembly(output / "source", assembly)
    relative = relative_path(build["pdf"]["path"])
    if digest((output / relative).read_bytes()) != build["pdf"]["sha256"]:
        raise ValueError("built PDF differs from recorded bytes")
    _, book = load_build_product(assembly["product"])
    native_pdf_checks(output, build, assembly, book)
    pins = {name: value["commit"] for name, value in assembly["sources"].items()}
    lock, expected, _ = select_lock(ROOT / "data/books" / book["id"], pins)
    unit_gates(output, build, assembly, repo, cache, lock, metadata_dir)
    from .readerscale import reader_scale
    save_gate(output,build,"G-SCALE",reader_scale(output,build,assembly["locale"],book["id"]))
    result = reproducibility_gate(output, build, assembly, expected)
    save_gate(output, build, "G-SAME", result)
    if result["status"] != "slot_occupied":
        from .tablecheck import reference_for_tables, table_gate
        reference = reference_for_tables(assembly, book, cache)
        tables = ({"status":"slot_occupied","reason":"English reference compilation pending"}
                  if reference is None else table_gate(output,assembly,build,reference))
        save_gate(output,build,"G-TABLE",tables)
        from .unitbuild import standalone_units
        if reference is not None and tables["status"] != "slot_occupied":
            from .editorial import editorial_setting
            notes = json.loads((output / "G-NOTE.json").read_bytes())
            english_setting = editorial_setting(reference)
            target_setting = (editorial_setting(output) if english_setting["status"] != "slot_occupied"
                              else {"status":"slot_occupied"})
            notes.update(english_setting=english_setting,target_setting=target_setting,
                         scope="Footnotes, environment order, note commands and effective native editorial setting. Unmarked prose is reviewed against the source separately.")
            if "slot_occupied" in (english_setting["status"],target_setting["status"]):
                if notes["status"] != "fail":
                    notes["status"] = "slot_occupied"
            elif (english_setting["status"]!="pass" or target_setting["status"]!="pass"
                  or english_setting["visible"] != target_setting["visible"]):
                notes["status"] = "fail"
            elif notes["status"] == "pending_editorial_probe":
                notes["status"] = "pass"
            save_gate(output,build,"G-NOTE",notes)
            save_gate(output, build, "G-ALONE", standalone_units(output, build, assembly))
    from .hubcheck import check_catalogue, hub_checkout
    save_gate(output, build, "G-HUB", check_catalogue(hub_checkout(ROOT)))
    from .epubcheck import native_epub
    save_gate(output, build, "G-EPUB", native_epub(output, build, assembly, web_profile, web_product))
    return build

