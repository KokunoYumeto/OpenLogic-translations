"""Bundle the numbered offline HTML reader with its verified local resources."""
import json
from pathlib import Path
from zipfile import ZipFile

from .assembly import digest
from .cache import relative_path
from .sourceexport import deterministic_zip


def package_html_reader(export_file, destination):
    export_file = Path(export_file).resolve()
    root = export_file.parent
    export = json.loads(export_file.read_bytes())
    if export.get("product") not in ("accessible", "epub"):
        raise ValueError("the offline reader needs the paired HTML and validated EPUB export")
    checks = export["epubcheck"]
    diagnostics = (root / "EPUBCHECK.json").read_bytes()
    if (checks["exit_code"] or checks["diagnostics"] or digest(diagnostics) != checks["report_sha256"]
            or json.loads(diagnostics)["messages"]):
        raise ValueError("the EPUB has outstanding diagnostics")
    files = {"reader.html": (root / "reader.html").read_bytes()}
    epub = root / "reader.epub"
    if (digest(files["reader.html"]) != export["products"]["reader.html"]["sha256"]
            or digest(files["reader.html"]) != export["epub"]["source_html_sha256"]
            or digest(epub.read_bytes()) != export["products"]["reader.epub"]["sha256"]):
        raise ValueError("reader differs from its export receipt")
    with ZipFile(epub) as witness:
        for name, checksum in export["epub"]["assets"].items():
            path = relative_path(name)
            if not name.startswith("assets/") or not (root / path).resolve().is_relative_to(root):
                raise ValueError("offline resource escapes the reader directory")
            data = (root / path).read_bytes()
            if digest(data) != checksum or data != witness.read("OEBPS/" + name):
                raise ValueError("offline resource differs from the validated EPUB: " + name)
            files[name] = data
        epub_assets = {n.removeprefix("OEBPS/") for n in witness.namelist() if n.startswith("OEBPS/assets/") and not n.endswith("/")}
        if epub_assets != set(export["epub"]["assets"]):
            raise ValueError("offline resource inventory differs from the validated EPUB")
    archive = deterministic_zip(files)
    target = Path(destination)
    if target.exists():
        if target.read_bytes() != archive:
            raise ValueError("a different offline HTML archive already exists")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(archive)
    print(f"{len(files)-1} local HTML resources; ZIP SHA-256 {digest(archive)}")
    return 0
