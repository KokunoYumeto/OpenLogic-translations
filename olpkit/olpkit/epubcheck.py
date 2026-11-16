"""Run the existing native-numbered web exporter against this build's actual PDF."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .assembly import digest, json_bytes
from .webexport import export_web
from .webprofile import load_profile


def verify_cached_dependencies(source, profile):
    from .bookcontext import BookInputs
    from .figurebinding import checked_asset

    inputs = BookInputs(source, profile)
    for name in profile.get("packages", {}):
        inputs.package(name)
    for batch in profile.get("figure_exports", []):
        directory = Path(batch["directory"])
        raw = (directory / "NATIVE_FIGURES.json").read_bytes()
        if digest(raw) != batch["receipt_sha256"]:
            raise ValueError("native figure export identity changed")
        for figure in json.loads(raw)["figures"]:
            checked_asset(directory, figure["source_file"], figure["source_sha256"])
            checked_asset(directory, figure["asset"], figure["svg_sha256"])


def native_epub(output, build, assembly, profile_path=None, web_product="accessible"):
    if web_product not in ("epub", "accessible"):
        raise ValueError("unknown web product: " + web_product)
    profile_path = Path(profile_path) if profile_path else output / "web-profile.json"
    if not profile_path.is_file():
        return {"status": "incomplete", "reason": "A web export profile bound to this PDF is required."}
    payload = profile_path.read_bytes()
    profile = load_profile(profile_path)
    witness = profile["witnesses"]["pdf"]
    if witness["sha256"] != build["pdf"]["sha256"] or digest(Path(witness["path"]).read_bytes()) != witness["sha256"]:
        return {"status": "fail", "reason": "Numbering witness belongs to a different PDF."}
    # The export recipe also depends on the upstream projection, math, speech,
    # numbering and packaging code. Reuse requires identical code and inputs.
    modules = Path(__file__).parent
    code = {p.name: digest(p.read_bytes()) for p in sorted(modules.glob("*.py"))}
    for name, item in profile["witnesses"].items():
        if digest(Path(item["path"]).read_bytes()) != item["sha256"]:
            return {"status": "fail", "reason": "Export witness changed", "witness": name}
    jar = profile["epubcheck"]
    if digest(Path(jar["path"]).read_bytes()) != jar["sha256"]:
        return {"status":"fail","reason":"EPUBCheck differs from the pinned validator."}
    key = digest(json_bytes([build["assembly_sha256"], build["pdf"]["sha256"], digest(payload), code, web_product]))
    target = output / "web" / key
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        verify_cached_dependencies(output / "source", profile)
    else:
        with TemporaryDirectory(dir=target.parent) as scratch:
            candidate = Path(scratch) / "edition"
            export_web(output / "source", web_product, candidate, profile_path,
                       check_numbers=True, check_speech=(web_product == "accessible"))
            candidate.rename(target)
    raw = (target / "EXPORT.json").read_bytes()
    report = json.loads(raw)
    diagnostics = (target / "EPUBCHECK.json").read_bytes()
    checks = report["epubcheck"]
    units = [r["html_id"].removeprefix("olp-unit-") for r in report["projection"]["unit_order"]]
    numbers = report["native_numbers"]
    speech = report.get("speech")
    issues = []
    files = {name: digest((target / name).read_bytes()) for name in ("reader.epub","reader.html")}
    if report["product"] != web_product:
        issues.append("Export product differs from the requested edition.")
    if any(files[name] != report["products"][name]["sha256"] for name in files):
        issues.append("Rendered file differs from export receipt.")
    if (report["assembly_sha256"] != digest((output / "source/ASSEMBLY.json").read_bytes())
            or report["profile_sha256"] != digest(payload) or report["locale"] != assembly["locale"]):
        issues.append("Edition, profile or assembly differs.")
    expected = {u["id"]:u["path"] for u in assembly["units"] if u["path"] in build["content_inputs"]}
    actual = {r["unit"]:r["path"] for r in report["projection"]["unit_order"]}
    if (report["epub"]["unit_order"] != units or len(set(units)) != len(units)
            or actual != expected):
        issues.append("EPUB unit order or coverage differs from native book.")
    if (checks["exit_code"] or checks["diagnostics"] or json.loads(diagnostics)["messages"]
            or checks["report_sha256"] != digest(diagnostics)):
        issues.append("EPUBCheck reports errors or its receipt differs.")
    if numbers["matched"] != numbers["total"] or numbers["total"] == 0:
        issues.append("Numbering comparison incomplete.")
    if web_product == "accessible" and (not speech or speech["formula_occurrences"] != speech["with_spoken_text"]):
        issues.append("Formula speech is incomplete.")
    return {"status":"fail" if issues else "pass", "issues":issues,
            "export":target.relative_to(output).as_posix()+"/EXPORT.json", "export_sha256":digest(raw),
            "files":files, "pdf_sha256":witness["sha256"], "epubcheck_sha256":digest(diagnostics),
            "units":len(units), "numbers":numbers["matched"], "web_product":web_product, "spoken_formulas":speech["with_spoken_text"] if speech else None}
