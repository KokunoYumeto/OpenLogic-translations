"""Verify a changed product against its accepted edition, build and editable sources."""
import json
from pathlib import Path
from zipfile import ZipFile

from .assembly import GitSnapshot, digest, json_bytes
from .build import GATES, verify_assembly
from .cache import relative_path
from .status import book_scope, compare_units, contract
from .syncaccept import reviewed_units, save_acceptance


def checked_file(root, name, checksum):
    root = Path(root).resolve()
    path = (root / relative_path(name)).resolve()
    if not path.is_relative_to(root):
        raise ValueError("file outside the recorded directory: " + name)
    data = path.read_bytes()
    if digest(data) != checksum:
        raise ValueError("recorded bytes changed: " + name)
    return data


def standalone_evidence(directory, report, scope):
    units = report["units"]
    if (report["status"] != "pass" or report["scope_units"] != len(scope)
            or {u["unit"] for u in units} != scope or len(units) != len(scope)):
        raise ValueError("standalone checks do not cover the requested units")
    for unit in units:
        record = json.loads(checked_file(directory, unit["file"], unit["sha256"]))
        if (record["unit"] != unit["unit"] or record["context_sha256"] != report["context_sha256"]
                or record["status"] != "pass" or record["fatal"] or record["wrong_language_inputs"]):
            raise ValueError("standalone build disagrees with its receipt: " + unit["unit"])


def native_gates(directory, build, scope):
    gates = build["gates"]
    if set(gates) != set(GATES) or any(row.get("status") != "pass" for row in gates.values()):
        raise ValueError("all native gates must pass on the same build")
    reports = {}
    for name, row in gates.items():
        if name in ("G-BOX", "G-LOG", "G-UNITS", "G-IMPORT"):
            continue
        report = json.loads(checked_file(directory, row["report"], row["sha256"]))
        if report.get("status") != "pass":
            raise ValueError("native report disagrees with gate: " + name)
        reports[name] = report
    if (set(build["content_inputs"]) != scope or gates["G-UNITS"]["checked_imported_units"] != len(scope)
            or not gates["G-IMPORT"]["pass"] or gates["G-IMPORT"]["observed"] != len(scope)
            or gates["G-IMPORT"]["expected"] != len(scope) or gates["G-IMPORT"]["wrong_language_inputs"]
            or gates["G-BOX"]["overfull_over_2pt"] or gates["G-LOG"]["issues"]):
        raise ValueError("native imports, log or layout differ from the confirmed scope")
    standalone_evidence(directory, reports["G-ALONE"], scope)
    return reports


def source_assets(export_path, check_path, build_dir, build):
    export_bytes = export_path.read_bytes()
    export = json.loads(export_bytes)
    check = json.loads(check_path.read_bytes())
    native_bytes = (build_dir / "NATIVE-BUILD.json").read_bytes()
    native = json.loads(native_bytes)
    if ({k:v for k,v in native.items() if k != "gates"} != {k:v for k,v in build.items() if k != "gates"}
            or export["assembly_sha256"] != build["assembly_sha256"]
            or export["package"]["build_sha256"] != digest(native_bytes)
            or export["package"]["pdf_sha256"] != build["pdf"]["sha256"]):
        raise ValueError("source export belongs to a different native build")
    if (check["status"] != "pass" or check["requested_mode"] != "both"
            or check["build_sha256"] != digest(native_bytes) or check["export_sha256"] != digest(export_bytes)
            or check["native_pdf_sha256"] != build["pdf"]["sha256"] or check["outputs"] != export["outputs"]
            or set(check["modes"]) != {"modular","cumulative"}):
        raise ValueError("both editable entry points need a matching cold build")
    for mode, result in check["modes"].items():
        compare = result["comparison"]
        if (result["status"] != "pass" or not compare["pass"] or not compare["text_equal"]
                or not compare["pages_equal"] or compare["different_rendered_pages"]
                or compare["render_dpi"] < 144 or result["recorded_units"] != len(build["content_inputs"])):
            raise ValueError("source round trip differs: " + mode)
    by_suffix = {}
    for name, item in export["outputs"].items():
        payload = checked_file(export_path.parent, name, item["sha256"])
        suffix = Path(name).suffix
        if relative_path(name).name != name or suffix in by_suffix or len(payload) != item["bytes"]:
            raise ValueError("unexpected source export asset")
        by_suffix[suffix] = name
    if set(by_suffix) != {".tex", ".zip"}:
        raise ValueError("expected direct cumulative LaTeX and an editable source ZIP")
    with ZipFile(export_path.parent / by_suffix[".zip"]) as archive:
        files = export["package"]["files"]
        if set(files) != set(archive.namelist()) or len(files) != len(archive.namelist()):
            raise ValueError("source ZIP member inventory differs")
        for info in archive.infolist():
            relative_path(info.filename)
            item = files[info.filename]
            if info.file_size != item["bytes"] or digest(archive.read(info)) != item["sha256"]:
                raise ValueError("source ZIP member differs: " + info.filename)
        cumulative = relative_path(export["driver"]).parent / by_suffix[".tex"]
        if files[cumulative.as_posix()]["sha256"] != export["outputs"][by_suffix[".tex"]]["sha256"]:
            raise ValueError("direct cumulative TeX differs from the archived source")
    return export["outputs"]


def verify_projected_units(rows, epub_order, build, scope):
    if len(rows) != len(scope) or {row["path"] for row in rows} != scope:
        raise ValueError("web reader differs from the native unit inventory")
    anchors = [row["html_id"] for row in rows]
    if (any(not anchor.startswith("olp-unit-") for anchor in anchors)
            or len(set(anchors)) != len(anchors)
            or [anchor.removeprefix("olp-unit-") for anchor in anchors] != epub_order):
        raise ValueError("HTML and EPUB unit anchors disagree")
    for row in rows:
        path = row["assembled_path"]
        native = build["source_inputs"].get(path)
        if (path not in build["content_inputs"][row["path"]] or native is None
                or native.get("unit") != row["unit"] or native["sha256"] != row["sha256"]):
            raise ValueError("web unit differs from the source used by the native reader: " + row["path"])


def web_assets(directory, build, gate, scope):
    if gate["pdf_sha256"] != build["pdf"]["sha256"] or gate["units"] != len(scope) or gate["issues"]:
        raise ValueError("web gate belongs to a different PDF or scope")
    raw = checked_file(directory, gate["export"], gate["export_sha256"])
    export = json.loads(raw)
    root = (directory / gate["export"]).parent
    rows = export["projection"]["unit_order"]
    if export["assembly_sha256"] != build["assembly_sha256"] or export["product"] != "accessible":
        raise ValueError("web reader does not match the native imports")
    verify_projected_units(rows, export["epub"]["unit_order"], build, scope)
    if (set(gate["files"]) != {"reader.html","reader.epub"}
            or export["native_numbers"]["total"] != export["native_numbers"]["matched"]
            or gate["numbers"] != export["native_numbers"]["total"] or not gate["numbers"]
            or export["speech"]["with_spoken_text"] != export["speech"]["formula_occurrences"]
            or gate["spoken_formulas"] != export["speech"]["with_spoken_text"]):
        raise ValueError("web formats, numbering or spoken mathematics incomplete")
    checks = export["epubcheck"]
    diagnostics = json.loads(checked_file(root, "EPUBCHECK.json", gate["epubcheck_sha256"]))
    if checks["report_sha256"] != gate["epubcheck_sha256"] or checks["exit_code"] or checks["diagnostics"] or diagnostics["messages"]:
        raise ValueError("EPUB validation did not pass")
    for name, checksum in gate["files"].items():
        data = checked_file(root, name, checksum)
        if export["products"][name] != {"bytes":len(data), "sha256":checksum}:
            raise ValueError("web export asset differs: " + name)
    return export["products"]


def verify_product(args, cache):
    snapshot = GitSnapshot(args.repo, args.ref)
    edition = contract(snapshot)
    folder = Path(args.packet).resolve()
    packets = [p for p in (folder/"edition.json", folder/"SYNC_EDITION.json") if p.is_file()]
    if len(packets) != 1:
        raise ValueError("expected one edition packet")
    packet_bytes = packets[0].read_bytes()
    review_bytes = Path(args.review).read_bytes()
    acceptance_bytes = Path(args.acceptance).read_bytes()
    accepted = json.loads(acceptance_bytes)
    if (accepted["schema"] != "olpkit.sync-accept.v1" or accepted["packet_sha256"] != digest(packet_bytes)
            or accepted["review_sha256"] != digest(review_bytes)):
        raise ValueError("acceptance belongs to different source or editorial decisions")
    snapshot.run("merge-base", "--is-ancestor", accepted["edition_commit"], snapshot.commit)
    review = json.loads(review_bytes)
    revised = reviewed_units(json.loads(packet_bytes), folder, review, snapshot, cache)
    if (revised != accepted["units"] or accepted["to"] != review["to"] or accepted["from"] != review["from"]
            or accepted["model"] != review["model"] or accepted["effort"] != review["effort"]):
        raise ValueError("accepted decisions do not reproduce at the candidate commit")
    accepted_dir = Path(args.accepted_build or args.build)
    accepted_assembly = checked_file(accepted_dir, "source/ASSEMBLY.json", accepted["assembly_sha256"])
    if json.loads(accepted_assembly)["edition_commit"] != accepted["edition_commit"]:
        raise ValueError("reviewed source assembly belongs to another edition commit")
    key = digest(packet_bytes + review_bytes + accepted_assembly)
    checks = checked_file(accepted_dir, f"sync-accept/{key}/standalone.json", accepted["standalone_sha256"])
    standalone_evidence(accepted_dir, json.loads(checks), {r["path"] for r in revised})
    upstream = GitSnapshot(cache/"OpenLogic.git", accepted["to"])
    ledger_bytes = snapshot.read_many(["units.jsonl"])["units.jsonl"]
    ledger = [json.loads(line) for line in ledger_bytes.splitlines() if line.strip()]
    rows = compare_units(edition,snapshot,ledger,upstream,upstream)
    if any(r["state"] != "current" or r["reasons"] for r in rows.values()):
        raise ValueError("the edition ledger does not reproduce the complete pinned source and target trees")
    directory = Path(args.build).resolve()
    build_bytes = (directory/"BUILD.json").read_bytes()
    build = json.loads(build_bytes)
    assembly_bytes = (directory/"source/ASSEMBLY.json").read_bytes()
    assembly = json.loads(assembly_bytes)
    product = assembly["product"]
    if (product not in edition["products"] or assembly["edition_commit"] != snapshot.commit
            or assembly["book_commit"] != snapshot.commit or assembly["english_fill_count"]
            or assembly["files"] != build["source_inputs"] or digest(assembly_bytes) != build["assembly_sha256"]
            or any(edition["pins"][k]["commit"] != v["commit"] for k,v in assembly["sources"].items())):
        raise ValueError("native build does not belong to the requested edition and pins")
    for path, raw in snapshot.read_many(assembly["contract_hashes"]).items():
        if digest(raw) != assembly["contract_hashes"][path]:
            raise ValueError("edition contract differs: " + path)
    verify_assembly(directory/"source", assembly)
    pdf = build["pdf"]
    if len(checked_file(directory, pdf["path"], pdf["sha256"])) != pdf["bytes"]:
        raise ValueError("native PDF size differs")
    scope = book_scope(product,snapshot,rows)
    if not scope:
        raise ValueError("the product needs a committed import scope")
    gates = native_gates(directory,build,scope)
    export_path, check_path = Path(args.source_export), Path(args.package_check)
    sources = source_assets(export_path,check_path,directory,build)
    web = web_assets(directory,build,gates["G-EPUB"],scope)
    changed = {r["path"] for r in revised}
    affected = {}
    for name in edition["products"]:
        selection = book_scope(name,snapshot,rows)
        affected[name] = sorted(changed & selection) if selection is not None else None
    report = {"schema":"olpkit.sync-product-verification.v1", "edition":edition["locale"],
              "edition_commit":snapshot.commit, "pins":edition["pins"], "product":product,
              "accepted_revision":accepted["to"], "acceptance_sha256":digest(acceptance_bytes),
              "source_units":len(rows), "reader_units":len(scope), "changed_units_by_product":affected,
              "native_build_sha256":digest(build_bytes), "assembly_sha256":digest(assembly_bytes),
              "package_check_sha256":digest(check_path.read_bytes()), "pdf":pdf, "source_assets":sources,
              "web_assets":web, "web_export_sha256":gates["G-EPUB"]["export_sha256"],
              "gates":{k:v["status"] for k,v in build["gates"].items()}, "status":"pass"}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_acceptance(out, json_bytes(report))
    print(f"{product}: {len(scope)} reader units, {len(gates)} external gate reports, {len(rows)} current edition units")
    return 0
