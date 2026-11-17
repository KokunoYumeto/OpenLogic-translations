"""Accept reviewed changes against the published hub packet and the actual TeX inputs."""
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile

from .assembly import GitSnapshot, digest, json_bytes, locale_marks
from .build import verify_assembly
from .cache import relative_path
from .orthography import normalize_unit
from .status import contract, is_content
from .unitbuild import standalone_units
from .unitlint import lint_units


def by_id(rows, key):
    indexed = {}
    for row in rows:
        uid = row[key]
        if not re.fullmatch(r"OLP-\d{4}", uid) or uid in indexed:
            raise ValueError("Invalid or duplicate reviewed unit: " + str(uid))
        indexed[uid] = row
    return indexed


def change_set(before, after):
    old = {p: item[2] for p, item in before.entries.items() if is_content(p)}
    new = {p: item[2] for p, item in after.entries.items() if is_content(p)}
    if old.keys() != new.keys():
        raise ValueError("Added, removed or renamed source paths need a unit-registry migration")
    return {p for p in old if old[p] != new[p]}


def technical_changes(cache, packet):
    """Reconstruct a technical-only interval directly from both upstream Git trees."""
    left, right = [GitSnapshot(Path(cache) / "OpenLogic.git", packet[key]) for key in ("from", "to")]
    paths = sorted(path for path in left.entries.keys() | right.entries.keys()
                   if left.entries.get(path) != right.entries.get(path))
    if not paths or any(is_content(path) for path in paths):
        raise ValueError("Expected changed upstream files outside the translated content tree")
    if "files" in packet:
        listed = {path for change in packet["files"] for path in (change["before"], change["after"]) if path}
        if listed != set(paths):
            raise ValueError("Technical packet file list differs from upstream")
    return [{"path": path, "before": list(left.entries[path]) if path in left.entries else None,
             "after": list(right.entries[path]) if path in right.entries else None} for path in paths]


def validate_decision(row, bodies, witnesses):
    for name, body in bodies.items():
        if row["hashes"].get(name) != digest(body):
            raise ValueError(row["unit"] + ": editorial decision belongs to different " + name)
    changed = bodies["target_before"] != bodies["target_after"]
    if row["disposition"] not in ({"patched", "conflict-resolved"} if changed else {"carried"}):
        raise ValueError(row["unit"] + ": decision differs from observed target change")
    if not isinstance(row["rationale"], str) or not row["rationale"].strip():
        raise ValueError(row["unit"] + ": editorial rationale missing")
    target = bodies["target_after"].decode("utf-8-sig").splitlines()
    lines = row.get("target_lines", [])
    if (not lines or any(type(n) is not int or not 1 <= n <= len(target) for n in lines)
            or not row.get("anchor") or not any(row["anchor"] in target[n - 1] for n in lines)):
        raise ValueError(row["unit"] + ": target passage does not match the reviewed translation")
    if not row.get("confidence") or not row.get("confidence_basis"):
        raise ValueError(row["unit"] + ": editorial confidence and reason are required")
    if not row["canon"] or any(key not in witnesses for key in row["canon"]):
        raise ValueError(row["unit"] + ": no identified canon passage for this decision")
    for key in row["canon"]:
        if not all(isinstance(witnesses[key].get(k), str) and witnesses[key][k].strip()
                   for k in ("source", "locator")):
            raise ValueError(row["unit"] + ": canon passage has no source or locator")


def packet_summary(packet):
    if packet.get("schema") == "olpkit.sync-edition.v1":
        return by_id(packet["packets"], "id"), packet["metadata_hashes"]
    return by_id(packet["units"], "unit"), {
        "olp-edition.toml": packet["contract_sha256"], "units.jsonl": packet["ledger_sha256"]}


def verify_packet_unit(folder, uid, summary, bodies):
    if "packet_sha256" in summary:
        raw = (folder / "packets" / (uid + ".json")).read_bytes()
        if digest(raw) != summary["packet_sha256"]:
            raise ValueError(uid + ": packet metadata changed")
        detail = json.loads(raw)
        if detail["unit"] != uid or detail["path"] != summary["path"]:
            raise ValueError(uid + ": packet identifies another unit")
        for key, field, expected in (
                ("source_before", "source_before", detail["upstream_change"]["old_sha256"]),
                ("source_after", "source_after", detail["upstream_change"]["new_sha256"]),
                ("target_before", "target_text", detail["target_sha256"])):
            if detail[field] != bodies[key].decode("utf-8-sig") or digest(bodies[key]) != expected:
                raise ValueError(uid + ": packet differs from source control for " + field)
        patch = detail["upstream_change"]["hunks"]
    else:
        unit = folder / "units" / uid
        raw = (unit / "unit.json").read_bytes()
        detail = json.loads(raw)
        if digest(raw) != summary["record_sha256"] or detail["unit"] != uid:
            raise ValueError(uid + ": packet metadata changed")
        for key, filename in (("source_before", "before.tex"), ("source_after", "after.tex"),
                              ("target_before", "current-target.tex")):
            if (unit / filename).read_bytes() != bodies[key]:
                raise ValueError(uid + ": packet contains different bytes for " + filename)
        diff_bytes = (unit / "source.diff").read_bytes()
        if digest(diff_bytes) != detail["diff_sha256"]:
            raise ValueError(uid + ": source diff changed")
        patch = diff_bytes.decode("utf-8")
    return [line for line in patch.splitlines() if line.startswith("@@ ")]


def reviewed_units(packet, folder, review, candidate, cache):
    base = GitSnapshot(candidate.repo, packet["edition_commit"])
    candidate.run("merge-base", "--is-ancestor", base.commit, candidate.commit)
    edition = contract(candidate)
    old_contract = contract(base)
    revisions = (packet["from"], packet["to"])
    if (old_contract["pins"]["olp"]["commit"], edition["pins"]["olp"]["commit"]) != revisions:
        raise ValueError("Source pins differ between packet and edition contracts")
    if ((review["from"], review["to"]) != revisions or old_contract["repository"] != edition["repository"]
            or packet.get("repository", old_contract["repository"]) != edition["repository"]):
        raise ValueError("Wrong source interval or edition repository")
    if review["schema"] != "olpkit.sync-review.v1" or not review["model"].strip() or not review["effort"].strip():
        raise ValueError("Review requires a schema and actual model and effort")
    english = [GitSnapshot(Path(cache) / "OpenLogic.git", revision) for revision in revisions]
    changed = change_set(*english)
    packets, contract_hashes = packet_summary(packet)
    decisions = by_id(review["units"], "unit")
    if (decisions.keys() != packets.keys() or len(packets) != len(changed)
            or {row["path"] for row in packets.values()} != changed):
        raise ValueError("Packet and reviewed units must cover the exact upstream content change set")
    raw = base.read_many(["olp-edition.toml", "units.jsonl"])
    if any(digest(raw[name]) != contract_hashes[name] for name in raw):
        raise ValueError("Packet does not identify the original edition ledger")
    def olp_ledger(payload):
        rows = (json.loads(line) for line in payload.splitlines() if line.strip())
        return by_id((row for row in rows if row["src"] == "olp"), "id")

    before = olp_ledger(raw["units.jsonl"])
    candidate_ledger = candidate.read_many(["units.jsonl"])["units.jsonl"]
    after = olp_ledger(candidate_ledger)
    if before.keys() != after.keys() or any(before[k] != after[k] for k in before.keys() - decisions.keys()):
        raise ValueError("Candidate changed unrelated unit ledger entries")
    after_root = edition["paths"]["content"]
    old_root = old_contract["paths"]["content"]
    old_paths = {p: old_root + "/" + p.removeprefix("content/") for p in changed}
    new_paths = {p: after_root + "/" + p.removeprefix("content/") for p in changed}
    old_targets = base.read_many(old_paths.values())
    new_targets = candidate.read_many(new_paths.values())
    left, right = [s.read_many(changed) for s in english]
    policy_path = edition["paths"].get("orthography", "lang/orthography.json")
    policy = json.loads(candidate.read_many([policy_path])[policy_path])
    results = []
    for uid, summary in sorted(packets.items()):
        path = summary["path"]
        if (before[uid]["path"] != path or after[uid]["path"] != path
                or after[uid]["state"] != "current"):
            raise ValueError(uid + ": packet, candidate and ledger path disagree")
        bodies = {"source_before": left[path], "source_after": right[path],
                  "target_before": old_targets[old_paths[path]], "target_after": new_targets[new_paths[path]]}
        hunks = verify_packet_unit(folder, uid, summary, bodies)
        if normalize_unit(bodies["target_after"], policy) != bodies["target_after"]:
            raise ValueError(uid + ": candidate still needs orthographic normalization")
        row = decisions[uid]
        if not hunks or row.get("source_hunks") != hunks:
            raise ValueError(uid + ": editorial review does not cover the packet's source hunks")
        validate_decision(row, bodies, review["canon"])
        assembled, _ = locale_marks(bodies["target_after"], edition["locale"])
        results.append({"unit": uid, "path": path, "assembled_sha256": digest(assembled),
                        "disposition": row["disposition"],
                        "hashes": row["hashes"], "canon": row["canon"]})
    return results


def save_acceptance(path, body):
    if path.exists():
        if path.read_bytes() != body:
            raise ValueError("Acceptance receipt already exists for different evidence")
        return
    with NamedTemporaryFile(dir=path.parent, delete=False) as staged:
        staged.write(body)
        temp = Path(staged.name)
    try:
        try:
            os.link(temp, path)
        except FileExistsError:
            if path.read_bytes() != body:
                raise ValueError("A different acceptance receipt already exists")
    finally:
        temp.unlink()


def accept(repo, ref, packet_dir, review_file, build_dir, out, cache):
    folder = Path(packet_dir)
    inputs = [p for p in (folder / "edition.json", folder / "SYNC_EDITION.json") if p.is_file()]
    if len(inputs) != 1:
        raise ValueError("Point --packet at one edition directory from the hub or olpkit")
    packet_bytes = inputs[0].read_bytes()
    review_bytes = Path(review_file).read_bytes()
    review = json.loads(review_bytes)
    candidate = GitSnapshot(repo, ref)
    build_dir = Path(build_dir)
    assembly_bytes = (build_dir / "source/ASSEMBLY.json").read_bytes()
    assembly = json.loads(assembly_bytes)
    native = json.loads((build_dir / "BUILD.json").read_bytes())
    if (assembly["edition_commit"] != candidate.commit or native["assembly_sha256"] != digest(assembly_bytes)
            or native["gates"]["G-IMPORT"]["status"] != "pass" or not native.get("pdf")):
        raise ValueError("Acceptance needs a compiled native build at the exact candidate with verified imports")
    verify_assembly(build_dir / "source", assembly)
    if digest((build_dir / relative_path(native["pdf"]["path"])).read_bytes()) != native["pdf"]["sha256"]:
        raise ValueError("Native PDF differs from its build receipt")
    packet = json.loads(packet_bytes)
    rows = reviewed_units(packet, folder, review, candidate, cache)
    assembled = by_id(assembly["units"], "id")
    for row in rows:
        unit = assembled[row["unit"]]
        path = "locale/" + assembly["locale"] + "/" + row["path"]
        if (unit["english_fill"] or unit["state"] != "current" or unit["path"] != row["path"]
                or unit["source_sha256"] != row["hashes"]["source_after"]
                or unit["target_sha256"] != row["hashes"]["target_after"]
                or assembly["files"][path]["sha256"] != row["assembled_sha256"]):
            raise ValueError(row["unit"] + ": compiled source differs from reviewed translation")
    if rows:
        paths = [row["path"] for row in rows]
        # Store diagnostics even on failure. Only a passing run writes the acceptance.
        evidence = build_dir / "sync-accept" / digest(packet_bytes + review_bytes + assembly_bytes)
        evidence.mkdir(parents=True, exist_ok=True)
        scope = evidence / "scope.txt"
        scope.write_bytes(("\n".join(paths) + "\n").encode())
        if lint_units(repo, candidate.commit, cache, evidence / "lint", scope=scope):
            raise ValueError("Source contract or orthography failed; see " + str(evidence / "lint"))
        units = standalone_units(build_dir, native, assembly, paths)
        if units["status"] == "slot_occupied":
            print("Standalone compilation pending; TeX slot occupied")
            return 75
        (evidence / "standalone.json").write_bytes(json_bytes(units))
        if units["status"] != "pass" or units["scope_units"] != len(rows):
            raise ValueError("Standalone compilation failed; see " + str(evidence / "standalone.json"))
        delta_checks = {"standalone_sha256": digest(json_bytes(units))}
    else:
        delta_checks = {"technical_changes": technical_changes(cache, packet)}
    report = {"schema": "olpkit.sync-accept.v1", "edition_commit": candidate.commit,
              "from": review["from"], "to": review["to"], "model": review["model"], "effort": review["effort"],
              "packet_sha256": digest(packet_bytes), "review_sha256": digest(review_bytes),
              "assembly_sha256": digest(assembly_bytes), "native_pdf_sha256": native["pdf"]["sha256"],
              "units": rows, **delta_checks}
    destination = Path(out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save_acceptance(destination, json_bytes(report))
    if rows:
        print(f"Accepted {len(rows)} reviewed units at {candidate.commit[:12]}")
    else:
        print(f"Accepted {len(delta_checks['technical_changes'])} changed upstream files "
              f"and zero changed content units at {candidate.commit[:12]}")
    return 0
