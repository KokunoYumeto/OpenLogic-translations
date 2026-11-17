"""Resolve web export inputs at the profile location and bind a profile to a native build."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from .assembly import digest, json_bytes
from .cache import relative_path


def locations(profile):
    for group in ("witnesses", "packages"):
        for record in profile.get(group, {}).values():
            if "path" in record:
                yield record, "path"
    for record in profile.get("figure_exports", []):
        yield record, "directory"
    if profile.get("epubcheck"):
        yield profile["epubcheck"], "path"


def load_profile(path):
    path = Path(path).resolve()
    profile = json.loads(path.read_bytes())
    for record, key in locations(profile):
        record[key] = str((path.parent / record[key]).resolve())
    return profile


def released_template(source, repo, jar, out):
    """Recover the previous native projection using an editable public release and its pinned edition."""
    import shutil
    import tomllib
    from .assembly import GitSnapshot, locale_marks
    from .schemas import ROOT
    from .sourceexport import public_unit_bytes
    from .webreplay import project_source, released_inputs

    root, destination = Path(source).resolve(), Path(out).resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError("Choose a new template directory outside the released sources")
    release, profile = released_inputs(root, Path(jar))
    source_root = root / "source"
    if "source/ASSEMBLY.json" not in release["inputs"]:
        raise ValueError("Released native assembly is missing from the input manifest")
    assembly = json.loads((source_root / "ASSEMBLY.json").read_bytes())
    edition = GitSnapshot(repo, assembly["edition_commit"])
    contract = tomllib.loads(edition.read_many(["olp-edition.toml"])["olp-edition.toml"].decode("utf-8-sig"))
    if (contract["locale"] != assembly["locale"]
            or contract["pins"]["olp"]["commit"] != assembly["sources"]["olp"]["commit"]):
        raise ValueError("Edition and released source revisions differ")
    # Public source removes only approved private comments. Recover the native
    # unit bytes so the next sync compares the same two editorial records.
    origins = profile.pop("released_unit_sources", {})
    profile.pop("released_package_declarations", None)
    prefix = "locale/" + assembly["locale"] + "/content/"
    paths = {}
    for name in origins:
        if not name.startswith(prefix) or name not in assembly["files"]:
            raise ValueError("Unidentified native unit in the release: " + name)
        paths[name] = contract["paths"]["content"] + "/" + name.removeprefix(prefix)
    blobs = edition.read_many(paths.values())
    rules = ROOT / "data" / "exports" / (assembly["product"] + "-" + assembly["locale"] + ".json")
    comments = json.loads(rules.read_bytes()).get("private_comment_sha256") if origins else {}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as temporary:
        scratch = Path(temporary)
        tree, stage = scratch / "source", scratch / "template"
        stage.mkdir()
        for name, entry in assembly["files"].items():
            relative = relative_path(name)
            src, dest = source_root / relative, tree / relative
            if release["inputs"].get("source/" + name) != entry["sha256"]:
                raise ValueError("Source manifest differs from the release: " + name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if name not in origins:
                shutil.copyfile(src, dest)
                continue
            native = blobs[paths[name]]
            link = origins[name]
            if digest(native) != link["native_sha256"]:
                native, _ = locale_marks(native, assembly["locale"])
            if (digest(native) != link["native_sha256"] or link["editable_sha256"] != entry["sha256"]
                    or public_unit_bytes(name, native, comments) != src.read_bytes()):
                raise ValueError("Published and native units do not reconcile: " + name)
            dest.write_bytes(native)
            entry.update(bytes=len(native), sha256=digest(native))
        body = json_bytes(assembly)
        (tree / "ASSEMBLY.json").write_bytes(body)
        project_source(tree, profile, stage)
        (stage / "native-manifest.json").write_bytes(body)
        profile["witnesses"]["native_source_manifest"]["path"] = str(stage / "native-manifest.json")
        for record, key in locations(profile):
            path = Path(record[key])
            if path.is_relative_to(stage):
                path = destination / path.relative_to(stage)
            try:
                record[key] = Path(os.path.relpath(path, destination)).as_posix()
            except ValueError:
                record[key] = str(path)
        (stage / "web-profile.json").write_bytes(json_bytes(profile))
        stage.rename(destination)
    print(f"Recovered previous web inputs and {len(origins)} native unit witnesses")
    return 0


def projected_style_changes(cache, acceptance, previous_edition, current_edition, old, new):
    """Replay localized styles from both accepted upstream Git trees and the registered shims."""
    import tomllib
    from .assembly import GitSnapshot
    from .shims import edition_shims, localize_sources

    technical = {row["path"]: row for row in acceptance.get("technical_changes", [])}
    paths = {name for name in technical.keys() & new["inputs"].keys() & old["inputs"].keys()
             if name.startswith("sty/") and name.endswith((".sty", ".cls"))
             and new["inputs"][name]["sha256"] != old["inputs"][name]["sha256"]}
    if not paths:
        return {}
    for side, pin_key, edition_file, projection in (("before", "from", previous_edition, old),
                                                     ("after", "to", current_edition, new)):
        edition = tomllib.loads(edition_file.read_bytes().decode("utf-8-sig"))
        pin = acceptance[pin_key]
        if edition["pins"]["olp"]["commit"] != pin:
            raise ValueError("Projected style revision differs from the edition contract")
        tree = GitSnapshot(Path(cache) / "OpenLogic.git", pin)
        files = paths | {shim["path"] for shim, _ in edition_shims(edition)}
        localized, _, _ = localize_sources(tree.read_many(files), edition)
        for name in paths:
            if (list(tree.entries[name]) != technical[name][side]
                    or digest(localized[name]) != projection["inputs"][name]["sha256"]):
                raise ValueError("Localized style differs from the accepted upstream change: " + name)
    return {name: technical[name] for name in paths}


def reviewed_projection_changes(assembly, old, new, acceptance, book_changes, *, styles=None):
    """Account for each projected source file changed since the previous reader."""
    if (acceptance["schema"] != "olpkit.sync-accept.v1"
            or acceptance["to"] != assembly["sources"]["olp"]["commit"]):
        raise ValueError("sync acceptance belongs to a different upstream revision")
    if set(old["inputs"]) != set(new["inputs"]):
        raise ValueError("projection input inventory changed; new inputs require reconciliation")
    units = {r["path"]: r for r in acceptance["units"]}
    reviewed = {r["path"]: r for r in book_changes}
    if len(reviewed) != len(book_changes):
        raise ValueError("duplicate book layout decision")
    changed = []
    prefix = "locale/" + assembly["locale"] + "/"
    for name, record in sorted(new["inputs"].items()):
        before, after = old["inputs"][name]["sha256"], record["sha256"]
        if before == after:
            continue
        if name.startswith(prefix + "content/"):
            unit = units.get(name.removeprefix(prefix))
            if (not unit or unit["assembled_sha256"] != after or not unit["canon"]
                    or unit["hashes"]["target_before"] != before):
                raise ValueError("changed translation lacks matching sync evidence: " + name)
            decision = unit["unit"]
        elif styles and name in styles:
            decision = {"upstream_style": styles[name]}
        else:
            row = reviewed.pop(name, {})
            if (not name.startswith(assembly["book_directory"] + "/") or row.get("old") != before
                    or row.get("new") != after or not row.get("reason", "").strip()):
                raise ValueError("changed book input lacks its recorded decision: " + name)
            decision = row["reason"]
        changed.append({"path": name, "old": before, "new": after, "decision": decision})
    if reviewed:
        raise ValueError("book decision names unchanged or absent input")
    return changed


def source_equivalent_profile(build_path, template_path, destination, *, sync_inputs=None, cache=None):
    """Bind unchanged or explicitly reviewed source changes to the native build."""
    from .bookcontext import BookInputs
    from .bookprojection import BookProjection
    from .glossary import native_order
    from .references import read_aux
    from .sourceexport import export_import_lock
    from .texttokens import TextTokens

    template = Path(template_path).resolve()
    build_path = Path(build_path).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("use a new profile directory")
    profile = load_profile(template)
    refresh = {}
    if sync_inputs is not None:
        prior_edition = Path(profile["witnesses"]["edition"]["path"])
        if digest(prior_edition.read_bytes()) != profile["witnesses"]["edition"]["sha256"]:
            raise ValueError("Previous edition metadata differs from its release")
        settings_path = Path(sync_inputs).resolve()
        refresh = json.loads(settings_path.read_bytes())
        def checked_input(role):
            record = refresh[role]
            path = (settings_path.parent / record["path"]).resolve()
            if digest(path.read_bytes()) != record["sha256"]:
                raise ValueError("changed web input: " + role)
            return path
        acceptance = json.loads(checked_input("acceptance").read_bytes())
        for role in ("edition", "credits_policy"):
            path = checked_input(role)
            profile["witnesses"][role] = {"path": str(path), "sha256": refresh[role]["sha256"]}
    build = json.loads(build_path.read_bytes())
    source = build_path.parent/"source"
    assembly_path = source/"ASSEMBLY.json"
    assembly_hash = digest(assembly_path.read_bytes())
    if assembly_hash != build["assembly_sha256"] or build["gates"]["G-IMPORT"]["status"] != "pass":
        raise ValueError("native build and recorded imports must match the exact assembly")
    inputs = BookInputs(source, profile)
    assembly = inputs.assembly
    if assembly["book_directory"] != build["book_directory"]:
        raise ValueError("native and assembled book directories differ")
    pdf = build_path.parent/relative_path(build["pdf"]["path"])
    book = source/relative_path(build["book_directory"])
    if pdf.parent != book or digest(pdf.read_bytes()) != build["pdf"]["sha256"]:
        raise ValueError("native PDF differs from the build receipt")
    if digest(pdf.with_suffix(".fls").read_bytes()) != build["recorder_sha256"]:
        raise ValueError("native recorder differs from the build receipt")
    if profile["witnesses"]["edition"]["sha256"] != assembly["contract_hashes"]["olp-edition.toml"]:
        raise ValueError("web edition metadata differs from the compiled edition contract")
    credit_gate = build["gates"]["G-CREDIT"]
    credit_bytes = (build_path.parent/relative_path(credit_gate["report"])).read_bytes()
    credits = json.loads(credit_bytes)
    policy_path = Path(profile["witnesses"]["credits_policy"]["path"])
    if (credit_gate["status"] != "pass" or digest(credit_bytes) != credit_gate["sha256"]
            or credits["pdf"]["sha256"] != build["pdf"]["sha256"]
            or digest(json_bytes(json.loads(inputs.witness("credits_policy")))) != credits["policy_sha256"]):
        raise ValueError("web credit policy must match the verified native PDF credit report")

    prior_projection = inputs.witness_json("projection_receipt")
    _, imports, _ = export_import_lock(assembly, profile)
    projection, receipt = BookProjection(source,assembly,imports).project(
        profile["entry"],profile["projection_configuration"])
    previous_text = inputs.witness_text("projection_source", prior_projection["projected_sha256"])
    def import_order(record):
        if not refresh:
            return record["unit_order"]
        for row in record["unit_order"]:
            if row["sha256"] != record["inputs"][row["assembled_path"]]["sha256"]:
                raise ValueError("import digest differs from the projection input")
        return [{k:v for k,v in row.items() if k != "sha256"} for row in record["unit_order"]]
    if (not refresh and projection != previous_text
            or import_order(receipt) != import_order(prior_projection)
            or receipt["initial_selection"] != prior_projection["initial_selection"]):
        raise ValueError("source projection changed; regenerate the affected language resources")
    changes = []
    if refresh:
        styles = projected_style_changes(cache, acceptance, prior_edition, checked_input("edition"),
                                         prior_projection, receipt)
        changes = reviewed_projection_changes(assembly, prior_projection, receipt, acceptance,
                                              refresh["book_inputs"], styles=styles)
    if {p for _,p in imports} != set(build["content_inputs"]):
        raise ValueError("native recorder differs from the import lock")
    tokens = TextTokens(modern_xparse=profile["modern_xparse"],resolver=inputs.resolve)
    tokens.configure_native(inputs.text("sty/open-logic-tokenize.sty"),"sty/open-logic-tokenize.sty")
    for name in profile["notation_configuration"]:
        tokens.configure(inputs.text(name),name)
    expanded, _ = tokens.expand(projection,"book-projection.tex")
    if not refresh and expanded != inputs.witness_text("token_source",digest(expanded.encode())):
        raise ValueError("source tokens changed; compare the new target wording")
    aux = pdf.with_suffix(".aux").read_text(encoding="utf-8-sig")
    labels = read_aux(aux)
    if labels != read_aux(inputs.witness_text("aux")):
        raise ValueError("native reference labels changed; regenerate their reconciliation")
    if profile.get("glossary") and native_order(pdf.with_suffix(".gls").read_text(encoding="utf-8-sig")) != native_order(inputs.witness_text("gls")):
        raise ValueError("native glossary order changed")
    for suffix in ("toc","thm","pcr","bbl"):
        if suffix in profile["witnesses"] and pdf.with_suffix("."+suffix).read_text(encoding="utf-8-sig") != inputs.witness_text(suffix):
            if refresh and suffix == "thm":
                from .theoremblocks import native_theorems
                def identities(text):
                    return [{k:v for k,v in row.items() if k != "page"} for row in native_theorems(text)]
                if identities(pdf.with_suffix(".thm").read_text("utf-8-sig")) == identities(inputs.witness_text("thm")):
                    continue
            raise ValueError("native "+suffix+" changed; regenerate its bindings")

    destination.parent.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as scratch:
        stage = Path(scratch)/"profile"
        stage.mkdir()
        # References use this build's real PDF, auxiliary labels and import order.
        # Historical template evidence remains immutable and separately identified.
        reconciliation = {"schema":"olpkit.native-web-reconciliation.v1",
            "inputs":{"assembly_sha256":assembly_hash,"aux_sha256":digest(aux.encode()),
                      "native_pdf_sha256":build["pdf"]["sha256"],"recorder_sha256":build["recorder_sha256"],
                      "source_build_sha256":digest(build_path.read_bytes()),
                      "prior_profile_sha256":digest(template.read_bytes())},
            "labels":len(labels),"imports":len(imports),"projected_sha256":digest(projection.encode()),
            "expanded_sha256":digest(expanded.encode())}
        generated = {"projection_receipt":("projection.json",json_bytes(receipt)),
                     "reconciliation":("reconciliation.json",json_bytes(reconciliation))}
        if refresh:
            reconciliation["sync_acceptance_sha256"] = refresh["acceptance"]["sha256"]
            reconciliation["changed_inputs"] = changes
            generated.update(projection_source=("projection.tex", projection.encode("utf-8")),
                             token_source=("tokens.tex", expanded.encode("utf-8")),
                             reconciliation=("reconciliation.json", json_bytes(reconciliation)))
            # Speech belongs to the reviewed occurrence contexts. Generate the
            # new reader before mapping the prior speech evidence onto its math.
            profile["witnesses"].pop("formula_speech_input", None)
            profile["witnesses"].pop("formula_speech", None)
        new_inputs = {"native_source_manifest":assembly_path,"pdf":pdf,"credits_policy":policy_path}
        for role in ("aux","toc","thm","fls","gls","pcr","bbl"):
            if role in profile["witnesses"]:
                new_inputs[role] = pdf.with_suffix("."+role)
        for role,path in new_inputs.items():
            profile["witnesses"][role] = {"path":str(path),"sha256":digest(path.read_bytes())}
        for role,(name,data) in generated.items():
            (stage/name).write_bytes(data)
            profile["witnesses"][role] = {"path":str(destination/name),"sha256":digest(data)}
        for record,key in locations(profile):
            try:
                record[key] = Path(os.path.relpath(record[key],destination)).as_posix()
            except ValueError:
                # References on a different Windows volume retain an absolute path.
                pass
        (stage/"web-profile.json").write_bytes(json_bytes(profile))
        stage.rename(destination)
    print(f"{len(imports)} source units and {len(labels)} native labels bound to {pdf.name}")
    return 0
