"""Observe whether the native book preamble actually executes editorial text."""
import json
import os
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from .assembly import digest, json_bytes
from .build import build_job
from .macrophases import mask_comments
from .process import TeXSlot, run_job


def editorial_setting(directory):
    tree = directory / "source"
    assembly = json.loads((tree / "ASSEMBLY.json").read_bytes())
    build = json.loads((directory / "BUILD.json").read_bytes())
    book = tree / assembly["book_directory"]
    driver = (book / (build_job(assembly) + ".tex")).read_text("utf-8-sig")
    markers = list(re.finditer(r"\\begin\s*\{document\}", mask_comments(driver)))
    if len(markers) != 1:
        raise ValueError("native driver must contain one document boundary")
    probe = driver[:markers[0].end()] + r"""
\typeout{OLPKIT-EDITORIAL-START}
\begin{editorial}
\typeout{OLPKIT-EDITORIAL-VISIBLE}
\end{editorial}
\typeout{OLPKIT-EDITORIAL-END}
\end{document}
"""
    key = digest(json_bytes([build["assembly_sha256"],build["engine_version"],
                             build["recorder_inputs"],digest(probe.encode())]))
    evidence = directory / ("editorial-" + key + ".json")
    if evidence.is_file():
        result = json.loads(evidence.read_bytes())
        if result.get("input_sha256") == key and result.get("status") == "pass":
            return result
    exe = shutil.which(build["engine"])
    with TeXSlot() as slot:
        if not slot.acquired:
            return {"status": "slot_occupied"}
        with TemporaryDirectory(dir=book, prefix="olpkit-editorial-") as name:
            scratch = Path(name)
            (scratch / "driver.tex").write_text(probe,encoding="utf-8")
            options = ["--disable-installer"] if "MiKTeX" in build["engine_version"] else []
            args = [exe,*options,"-no-shell-escape","-halt-on-error","-interaction=nonstopmode",
                    "-output-directory="+scratch.name,"-jobname=editorial-setting",
                    r"\input{"+scratch.name+"/driver.tex}"]
            env = {**os.environ,"openin_any":"a","openout_any":"p",
                   "SOURCE_DATE_EPOCH":str(build["source_date_epoch"]),"FORCE_SOURCE_DATE":"1"}
            run = run_job(args,book,scratch/"console.log",env=env,timeout=120)
            raw = (scratch / "console.log").read_bytes()
            tokens = re.findall(rb"(?m)^OLPKIT-EDITORIAL-(START|VISIBLE|END)\r?$",raw)
            ok = run["exit_code"]==0 and tokens in ([b"START",b"END"],[b"START",b"VISIBLE",b"END"])
            result = {"status":"pass" if ok else "fail", "input_sha256":key,
                      "visible":b"VISIBLE" in tokens, "log_sha256":digest(raw), "run":run}
            if not ok:
                (directory / "editorial-setting-failure.log").write_bytes(raw)
            evidence.write_bytes(json_bytes(result))
            return result
