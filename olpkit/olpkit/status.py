"""Compare committed edition inputs and released product scopes with a pinned English tree."""
from collections import Counter
import json
from pathlib import Path
import re
import tomllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

from .assembly import GitSnapshot, digest
from .cache import relative_path
from .recorder import parse_imports
from .schemas import ROOT, validate_schema


def is_content(path):
    return path.startswith("content/") and path.endswith(".tex")


def contract(snapshot):
    raw = snapshot.read_many(["olp-edition.toml"])["olp-edition.toml"]
    data = tomllib.loads(raw.decode("utf-8-sig"))
    validate_schema("olp-edition", data)
    return data


def compare_units(edition, snapshot, units, original, comparison):
    rows = {}
    ids = set()
    root = edition["paths"]["content"]
    mirror = edition["paths"].get("source_content")
    relative_path(root)
    for unit in units:
        validate_schema("unit", unit)
        if unit["id"] in ids or (unit["src"], unit["path"]) in rows:
            raise ValueError("duplicate unit identity or source path in edition ledger")
        ids.add(unit["id"])
        rows[unit["src"], unit["path"]] = unit

    active = {path:u for (src,path),u in rows.items() if src == "olp" and u["state"] != "retired"}
    old_paths = {path for path in original.entries if is_content(path)}
    new_paths = {path for path in comparison.entries if is_content(path)}
    target_only = {"content/"+p[len(root)+1:] for p in snapshot.entries
                   if p.startswith(root+"/") and p.endswith(".tex")} - (old_paths | new_paths | active.keys())
    # Read vendored English only where its Git blob is the authoritative one.
    # This keeps the operation usable with the public planner's filtered clone.
    mirror_paths = {}
    target_paths = {}
    for path in old_paths | new_paths | active.keys():
        if not is_content(path):
            raise ValueError("OLP content unit outside its content tree: "+path)
        suffix = path[len("content/"):]
        target_paths[path] = root+"/"+suffix
        if mirror and path in old_paths:
            alias = mirror+"/"+suffix
            entry = snapshot.entries.get(alias)
            if entry and entry[0] in {"100644","100755"} and entry[1:] == original.entries[path][1:]:
                mirror_paths[path] = alias
    originals = original.read_many(old_paths - mirror_paths.keys())
    names = set(mirror_paths.values()) | {p for p in target_paths.values() if p in snapshot.entries}
    edition_bytes = snapshot.read_many(names)
    originals.update({p:edition_bytes[alias] for p,alias in mirror_paths.items()})
    shared = {p:u for u,p in (line.split("\t") for line in
              (ROOT/"data/units/olp-units.tsv").read_text(encoding="utf-8").splitlines()[1:])}
    result = {}
    for path in sorted(old_paths | new_paths | active.keys()):
        u = active.get(path)
        target = target_paths[path]
        current_target = digest(edition_bytes[target]) if target in edition_bytes else None
        before = original.entries.get(path)
        after = comparison.entries.get(path)
        reasons = []
        if u is None:
            state = "new"
            if before:
                reasons.append("missing at the edition pin")
            if current_target is not None:
                reasons.append("target exists without an active ledger entry")
        else:
            if path in shared and u["id"] != shared[path]:
                reasons.append("unit identity differs from the shared registry")
            if before and u["state"] == "current" and (u["src_blob"] != before[2] or
                    u["src_sha256"] != digest(originals[path])):
                reasons.append("source hashes differ at the edition pin")
            if not before:
                reasons.append("active ledger path absent at the edition pin")
            if u["tr_sha256"] != current_target:
                reasons.append("target bytes differ from the ledger")
            if after is None:
                state = "removed"
            elif u["state"] == "new" and current_target is None:
                state = "new"
            elif u["state"] != "current" or not before or before[2] != after[2] or reasons:
                state = "stale"
            else:
                state = "current"
        result[path] = {"id": u["id"] if u else shared.get(path), "state": state,
                        "target":target,"target_sha256":current_target,"reasons":reasons}
    for path in sorted(target_only):
        result[path] = {"id":None,"state":"unmapped","target":root+"/"+path[len("content/"):],
                        "reasons":["translated file outside the source tree and active ledger"]}
    return result


def book_scope(book, snapshot, rows):
    if book == "olp-complete":
        return set(rows)
    profile = ROOT/"data/build-products"/(str(relative_path(book))+".json")
    if not profile.is_file():
        return None
    name = json.loads(profile.read_bytes())["book"]
    book_dir = "courses/"+str(relative_path(name))+"/"
    config = book_dir+"book.toml"
    if config not in snapshot.entries:
        return None
    data = tomllib.loads(snapshot.read_many([config])[config].decode("utf-8-sig"))
    path = book_dir+str(relative_path(data["imports_lock"]))
    text = snapshot.read_many([path])[path].decode("utf-8-sig")
    if "\t" not in text:
        # Earlier course manifests list paths alone. Bind them to the same edition ledger.
        lines = []
        for name in text.splitlines():
            if name not in rows or not rows[name]["id"]:
                raise ValueError("book imports an unrecognized unit: "+name)
            lines.append(rows[name]["id"]+"\t"+name)
        text = "\n".join(lines)
    members = parse_imports(text)
    scope = set()
    for uid,path in members:
        if path not in rows or rows[path]["id"] != uid:
            raise ValueError("book imports an unrecognized unit: "+path)
        scope.add(path)
    if not scope:
        raise ValueError("empty book import scope: "+book)
    return scope


def tag_selection(edition, snapshot):
    selection = edition.get("public", {}).get("catalogue")
    if not selection:
        return {}
    path = selection["path"]
    body = snapshot.read_many([path])[path]
    if digest(body) != selection["sha256"]:
        raise ValueError("edition catalogue hash differs from the contract")
    catalogue = json.loads(body)
    tags = {}
    if catalogue.get("release_selection", {}).get("tag"):
        tags["olp-complete"] = catalogue["release_selection"]["tag"]
    if catalogue.get("textbook", {}).get("selection", {}).get("release_tag"):
        # The legacy catalogue's singular textbook field is the SLC selection.
        tags["slc-screen-pdf"] = catalogue["textbook"]["selection"]["release_tag"]
    return tags


def release_receipt(edition, product, tag, explicit, snapshot):
    if product in explicit:
        body = explicit[product]
    elif tag:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", tag):
            raise ValueError("invalid publication tag")
        path = f"releases/{tag}/release.json"
        if path in snapshot.entries:
            body = snapshot.read_many([path])[path]
        else:
            repo = edition["repository"].removesuffix(".git")
            if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", repo):
                raise ValueError("unsupported edition release URL")
            try:
                with urlopen(f"{repo}/releases/download/{quote(tag)}/release.json", timeout=30) as resp:
                    body = resp.read(4_000_001)
            except HTTPError as error:
                if error.code == 404:
                    return None
                raise
            if len(body)>4_000_000:
                raise ValueError("release receipt exceeds size limit")
    else:
        return None
    receipt = json.loads(body)
    validate_schema("release",receipt)
    if (receipt["edition"] not in (edition["locale"],edition["language_tag"]) or
            receipt["product_group"] != product or (tag and receipt["tag"] != tag)):
        raise ValueError("receipt does not identify the selected edition, product and tag")
    tag_ref = "refs/tags/"+receipt["tag"]
    snapshot.run("check-ref-format",tag_ref)
    if snapshot.run("rev-parse","--verify",tag_ref+"^{commit}").decode().strip() != receipt["commit"]:
        raise ValueError("release commit differs from its local public tag: "+receipt["tag"])
    return receipt, digest(body)


def changed_paths(old, new):
    return {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}


def product_status(snapshot, edition, product, scope, rows, comparison, receipt_info):
    changed = sorted(p for p in (scope or ()) if rows[p]["state"] != "current" or rows[p]["reasons"])
    result = {"product":product,"scope_units":len(scope) if scope is not None else None,
              "changed_units":changed, "state":"stale" if changed else "unverified"}
    if not receipt_info:
        result["missing_evidence"] = "release.json unavailable"
        return result
    receipt, receipt_hash = receipt_info
    released = GitSnapshot(snapshot.repo,receipt["commit"])
    ledger = receipt["unit_ledger"]
    if digest(released.read_many([ledger["path"]])[ledger["path"]]) != ledger["sha256"]:
        raise ValueError("release ledger does not match the tagged bytes")
    result.update(tag=receipt["tag"], release_sha256=receipt_hash, release_commit=released.commit,
                  gate_states={g["id"]:g["status"] for g in receipt["gates"]})
    if scope is None:
        result["missing_evidence"] = "product import scope unavailable"
        return result
    release_contract = contract(released)
    if any(release_contract["pins"].get(source) != pin for source,pin in receipt["pins"].items()):
        raise ValueError("release source pins differ from the tagged edition contract")
    # Compare the raw translated blobs imported by this product, even if a
    # maintainer already updated its unit ledger and all units are current.
    new_content = edition["paths"]["content"]+"/"
    old_content = release_contract["paths"]["content"]+"/"
    for p in scope:
        suffix = p[len("content/"):]
        if released.entries.get(old_content+suffix) != snapshot.entries.get(new_content+suffix):
            changed.append(p)
    previous = GitSnapshot(comparison.repo,receipt["pins"]["olp"]["commit"])
    upstream = changed_paths(previous.entries, comparison.entries)
    changed.extend(upstream & scope)
    result["changed_units"] = sorted(set(changed))
    result["changed_upstream_support"] = sorted(p for p in upstream if not is_content(p))
    other_pins = {src for src in receipt["pins"]
                  if src != "olp" and receipt["pins"].get(src) != edition["pins"].get(src)}
    result["changed_component_pins"] = sorted(other_pins)
    if result["changed_units"] or other_pins or "sty/open-logic.sty" in result["changed_upstream_support"]:
        result["state"] = "stale"
        return result
    if receipt["reader_units"] != len(scope):
        result.update(state="stale", reason="published and current reader scopes differ")
        return result
    # Legacy releases sometimes record only a unit ledger or an import list.
    # An unrelated translated unit can be excluded from a book with a known
    # scope. Other changed inputs require evidence from the actual product.
    exempt = {"units.jsonl"}
    differences = sorted(p for p in changed_paths(released.entries,snapshot.entries)
                         if p not in exempt and not p.startswith((old_content,new_content)))
    if differences or result["changed_upstream_support"]:
        result["unresolved_edition_files"] = differences
    else:
        result["state"] = "current"
    return result


def status_command(repo, ref, upstream_repo, compare_to=None, receipts=(), json_output=False):
    edition_tree = GitSnapshot(repo,ref)
    edition = contract(edition_tree)
    pin = edition["pins"]["olp"]["commit"]
    original = GitSnapshot(upstream_repo,pin)
    comparison = GitSnapshot(upstream_repo,compare_to) if compare_to else original
    unit_data = edition_tree.read_many(["units.jsonl"])["units.jsonl"].decode("utf-8-sig")
    units = [json.loads(line) for line in unit_data.splitlines() if line.strip()]
    rows = compare_units(edition,edition_tree,units,original,comparison)
    explicit = {}
    for path in receipts:
        data = Path(path).read_bytes()
        name = json.loads(data)["product_group"]
        if name in explicit or name not in edition["products"]:
            raise ValueError("duplicate or undeclared release product: "+name)
        explicit[name] = data
    tags = tag_selection(edition,edition_tree)
    products = []
    for product in edition["products"]:
        scope = book_scope(product,edition_tree,rows)
        receipt = release_receipt(edition,product,tags.get(product),explicit,edition_tree)
        products.append(product_status(edition_tree,edition,product,scope,rows,comparison,receipt))
    counts = Counter(row["state"] for row in rows.values())
    report = {"schema":"olpkit.status.v1","edition_commit":edition_tree.commit,"pin":pin,
              "compared_to":comparison.commit,"counts":dict(counts),"products":products,
              "unit_changes":{p:r for p,r in rows.items() if r["state"] != "current" or r["reasons"]}}
    if json_output:
        print(json.dumps(report,ensure_ascii=False,indent=2))
    else:
        print(f"Committed edition {edition_tree.commit[:12]} compared with source {comparison.commit[:12]}")
        print(f"pin {pin[:8]}; {counts['current']} current; {counts['stale']} stale; "
              f"{sum(p['state']=='stale' for p in products)} stale products")
        print(f"{counts['new']} new; {counts['removed']} removed; {counts['unmapped']} unmapped; "
              f"{sum(p['state']=='unverified' for p in products)} unverified products")
        for p in products:
            print(f"{p['product']}: {p['state']} ({len(p['changed_units'])} changed units)")
    return 0
