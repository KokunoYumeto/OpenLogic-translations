"""Compare a committed hub snapshot with its own generator in read-only check mode."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from .assembly import GitSnapshot


CATALOGUES = ("README.md", "index.html", "index.ps.html", "catalogue/editions.json",
              "catalogue/releases.json", "catalogue/textbooks.json", "catalogue/ownership.json",
              "catalogue/release-selection.json", "catalogue/textbook-selection.json")
GENERATOR = "scripts/generate-catalogue.mjs"


def hub_checkout(builder_root):
    if override := os.environ.get("OLPKIT_HUB"):
        return Path(override).resolve()
    parent = Path(builder_root).resolve().parent
    if (parent/"registry.toml").is_file() and (parent/GENERATOR).is_file():
        return parent
    return parent/"repos"/"OpenLogic-translations"


def check_catalogue(repo, ref="HEAD"):
    snap = GitSnapshot(repo, ref)
    paths = [name for name in snap.entries if name in (*CATALOGUES, "registry.toml")
             or name.startswith(("templates/", "catalogue/", "scripts/"))]
    files = snap.read_many(paths)
    required = {*CATALOGUES, "registry.toml", GENERATOR}
    if required - files.keys():
        return {"status": "fail", "hub_commit": snap.commit,
                "missing": sorted(required - files.keys())}
    evidence = {name: hashlib.sha256(body).hexdigest() for name, body in files.items()}
    result = {"hub_commit": snap.commit, "input_sha256": evidence}
    node = shutil.which("node")
    if node is None:
        return {**result, "status": "incomplete", "reason": "Node executable unavailable"}
    with TemporaryDirectory(prefix="olpkit-catalogue-") as directory:
        root = Path(directory)
        for name, body in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        try:
            run = subprocess.run([node, GENERATOR, "all", "--check"], cwd=root,
                                 env={**os.environ, "OLPKIT_PYTHON": sys.executable},
                                 capture_output=True, timeout=600, check=False)
        except subprocess.TimeoutExpired:
            return {**result, "status": "incomplete", "reason": "catalogue generation timed out"}
        if any((root / name).read_bytes() != files[name] for name in CATALOGUES):
            return {**result, "status": "fail", "reason": "check mode modified a committed output"}
        if run.returncode:
            # Record only output names the generator reported, never raw service errors.
            error = run.stderr.decode("utf-8", errors="replace")
            message = "Generated files differ: "
            names = error.partition(message)[2].strip().split(", ")
            if names and all(name in CATALOGUES for name in names):
                return {**result, "status": "fail", "different_files": names}
            return {**result, "status": "incomplete", "reason": "generation could not finish",
                    "exit_code": run.returncode, "diagnostic_sha256": hashlib.sha256(run.stderr).hexdigest()}
    return {**result, "status": "pass", "checked_outputs": list(CATALOGUES)}
