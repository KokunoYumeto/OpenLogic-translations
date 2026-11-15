"""Compile each imported unit as the entry point in its native textbook preamble."""
import json
import os
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory

from .assembly import digest, json_bytes
from .build import build_job, log_checks
from .cache import relative_path
from .macrophases import mask_comments
from .process import run_job, TeXSlot
from .recorder import content_inputs, read_inputs


def unit_driver(driver, unit):
    path = relative_path(unit)
    if not re.fullmatch(r"content/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.tex", unit):
        raise ValueError("unsupported unit filename for native import")
    markers = list(re.finditer(r"\\begin\s*\{document\}", mask_comments(driver)))
    if len(markers) != 1:
        raise ValueError("expected one native document boundary")
    directory = "/".join(path.parts[1:-1])
    return (driver[:markers[0].end()] + "\n" + r"\olimport*[" + directory + "]{"
            + path.stem + "}\n" + r"\end{document}" + "\n").encode("utf-8")


def compile_unit(book, tree, output, assembly, build, unit, uid, executable, preamble):
    driver = unit_driver(preamble, unit)
    job = "alone-" + uid.lower()
    with TemporaryDirectory(dir=book, prefix="olpkit-unit-") as name:
        scratch = Path(name)
        (scratch / "driver.tex").write_bytes(driver)
        options = ["--disable-installer"] if "MiKTeX" in build["engine_version"] else []
        args = [executable, *options, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                "-file-line-error", "-recorder", "-output-directory=" + scratch.name, "-jobname=" + job,
                r"\tracinglostchars=3\input{" + scratch.name + "/driver.tex}"]
        env = {**os.environ, "SOURCE_DATE_EPOCH": str(build["source_date_epoch"]),
               "FORCE_SOURCE_DATE": "1", "openin_any": "a", "openout_any": "p"}
        run = run_job(args, book, scratch / "stdout.txt", env=env, timeout=180)
        recorder = scratch / (job + ".fls")
        log = scratch / (job + ".log")
        pdf = scratch / (job + ".pdf")
        inputs = read_inputs(recorder, book) if recorder.is_file() else []
        found, wrong = content_inputs(inputs, tree, assembly["locale"])
        logbytes = log.read_bytes() if log.is_file() else (scratch / "stdout.txt").read_bytes()
        checks = log_checks(logbytes.decode("utf-8", errors="replace"))
        fatal = sorted(set(checks["issues"]) & {"missing_character", "tex_error", "undefined_token"})
        dependencies = {p.relative_to(tree).as_posix(): digest(p.read_bytes()) for p in inputs
                        if p.is_relative_to(tree) and p.relative_to(tree).as_posix() in assembly["files"]}
        expected_inputs = build["content_inputs"].get(unit, ["locale/" + assembly["locale"] + "/" + unit])
        ok = (run["exit_code"] == 0 and not run["timed_out"] and not fatal and not wrong
              and found.get(unit) == expected_inputs and pdf.is_file() and pdf.stat().st_size)
        result = {"unit": unit, "id": uid, "driver_sha256": digest(driver), "log_sha256": digest(logbytes),
                  "run": run, "observed_units": sorted(found), "wrong_language_inputs": wrong,
                  "source_inputs": dependencies, "fatal": fatal, "status": "pass" if ok else "fail"}
        if not ok:
            (output / (uid + ".log")).write_bytes(logbytes)
        return result


def standalone_units(output, build, assembly, selected=None):
    output = Path(output)
    tree = output / "source"
    book = tree / relative_path(assembly["book_directory"])
    preamble = (book / (build_job(assembly) + ".tex")).read_text("utf-8-sig")
    available = {u["path"]: u["id"] for u in assembly["units"] if u["state"] == "current" and not u["english_fill"]}
    imported = set(build["content_inputs"])
    if not imported <= available.keys():
        raise ValueError("standalone scope differs from the actual native imports")
    scope = set(selected) if selected is not None else imported
    if not scope or not scope <= available.keys():
        raise ValueError("standalone scope includes an absent or untranslated unit")
    units = {path: available[path] for path in scope}
    exe = shutil.which(build["engine"])
    if not exe:
        raise ValueError("standalone TeX executable unavailable")
    context = digest(json_bytes({
        "engine_sha256": digest(Path(exe).read_bytes()), "engine_version": build["engine_version"],
        "source_date_epoch": build["source_date_epoch"], "preamble": digest(preamble.encode("utf-8")),
        "code": digest(Path(__file__).read_bytes()), "assembly_sha256": build["assembly_sha256"],
        "toolchain": [r for r in build["recorder_inputs"] if r["kind"] == "toolchain"]}))
    target = output / "standalone-units" / context
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    with TeXSlot() as slot:
        if not slot.acquired:
            return {"status": "slot_occupied", "scope_units": len(units)}
        for unit, uid in sorted(units.items()):
            path = target / (uid + ".json")
            row = json.loads(path.read_bytes()) if path.is_file() else None
            if (row is None or row.get("context_sha256") != context or row.get("unit") != unit
                    or row.get("status") != "pass"):
                row = compile_unit(book, tree, target, assembly, build, unit, uid, exe, preamble)
                row["context_sha256"] = context
                temp = path.with_suffix(".tmp")
                temp.write_bytes(json_bytes(row))
                temp.replace(path)
            rows.append({"unit": unit, "status": row["status"], "file": path.relative_to(output).as_posix(),
                         "sha256": digest(path.read_bytes())})
    return {"status": "pass" if rows and all(r["status"] == "pass" for r in rows) else "fail",
            "scope_units": len(units), "context_sha256": context, "units": rows}
