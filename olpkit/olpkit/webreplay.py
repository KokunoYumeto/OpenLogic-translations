"""Build the HTML and EPUB from a released textbook source tree."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .assembly import digest, json_bytes
from .bookcontext import BookInputs
from .bookprojection import BookProjection
from .cache import relative_path
from .htmlarchive import package_html_reader
from .sourceexport import export_import_lock
from .texttokens import TextTokens
from .webexport import export_web
from .webprofile import load_profile


def project_source(source, profile, scratch):
    inputs = BookInputs(source, profile)
    _, imports, _ = export_import_lock(inputs.assembly, profile)
    projected, record = BookProjection(source, inputs.assembly, imports).project(
        profile["entry"], profile["projection_configuration"])
    tokens = TextTokens(modern_xparse=profile["modern_xparse"], resolver=inputs.resolve)
    tokens.configure_native(inputs.text("sty/open-logic-tokenize.sty"), "sty/open-logic-tokenize.sty")
    for name in profile["notation_configuration"]:
        tokens.configure(inputs.text(name), name)
    expanded, _ = tokens.expand(projected, "book-projection.tex")
    assembly = source / "ASSEMBLY.json"
    profile["witnesses"]["native_source_manifest"] = {"path": str(assembly), "sha256": digest(assembly.read_bytes())}
    reconciliation = {"inputs": {"assembly_sha256": digest(assembly.read_bytes()),
                                 "native_pdf_sha256": digest(inputs.witness("pdf")),
                                 "aux_sha256": digest(inputs.witness_text("aux").encode())}}
    for role, payload in (("projection_source", projected.encode()), ("token_source", expanded.encode()),
                          ("projection_receipt", json_bytes(record)), ("reconciliation", json_bytes(reconciliation))):
        path = scratch / role
        path.write_bytes(payload)
        profile["witnesses"][role] = {"path": str(path), "sha256": digest(payload)}


def rebuild(root, destination, jar):
    root = root.resolve()
    release = json.loads((root / "WEB-EDITION.json").read_bytes())
    for name, checksum in release["inputs"].items():
        path = (root / relative_path(name)).resolve()
        if not path.is_relative_to(root) or digest(path.read_bytes()) != checksum:
            raise ValueError("release input differs: " + name)
    profile = load_profile(root / "web/profile.json")
    if not jar.is_file() or digest(jar.read_bytes()) != profile["epubcheck"]["sha256"]:
        raise ValueError("EPUBCheck JAR differs from this edition's version")
    profile["epubcheck"]["path"] = str(jar.resolve())
    source = root / "source"
    labels = json.loads((root / "web/speech.json").read_bytes())
    destination = destination.resolve()
    if destination.is_relative_to(root) or destination.exists():
        raise ValueError("choose a new output directory outside the source package")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as temporary:
        scratch = Path(temporary)
        project_source(source, profile, scratch)
        config = scratch / "profile.json"
        config.write_bytes(json_bytes(profile))
        stage = scratch / "output"
        export_web(source, "accessible", stage, config, released_speech=labels)
        public = scratch / "readers"
        public.mkdir()
        package_html_reader(stage / "EXPORT.json", public / "reader-html.zip")
        assets = json.loads((stage / "EXPORT.json").read_bytes())["epub"]["assets"]
        for name in ("reader.html", "reader.epub", *assets):
            path = relative_path(name)
            target = public / path
            target.parent.mkdir(parents=True, exist_ok=True)
            (stage / path).rename(target)
        for name, checksum in release["outputs"].items():
            if digest((public / relative_path(name)).read_bytes()) != checksum:
                raise ValueError("rebuilt output differs: " + name)
        public.rename(destination)


def main(default_root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=default_root, required=default_root is None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--epubcheck-jar", type=Path, required=True)
    args = parser.parse_args()
    rebuild(args.source, args.out, args.epubcheck_jar)


if __name__ == "__main__":
    main()
