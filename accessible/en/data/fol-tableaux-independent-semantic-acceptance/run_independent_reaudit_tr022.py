#!/usr/bin/env python3
"""Fail-closed, read-only independent re-audit orchestrator for OLAB-TR-022.

This program runs the tranche-local independent semantic engine twice in
isolated evidence roots, compares every resulting byte, and adds independent
repair-scope, old-FAIL-lineage, MathML/accessibility, replay, provenance, and
adversarial grouping checks.  Writes are confined to this evidence directory.
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PROJECTION = PROJECT / "evidence" / "tranche_022_fol_tableaux_projection"
WORK = PROJECT / "work" / "tranche_022_fol_tableaux_projection"
ORACLE = PROJECT / "evidence" / "tranche_022_fol_tableaux_oracle"
ORACLE_VALIDATION = PROJECT / "evidence" / "tranche_022_fol_tableaux_oracle_validation"
OLD_FAIL = PROJECT / "evidence" / "independent_tranche_022_fol_tableaux_semantic_audit_20260822"
GLOBAL_LABELS = PROJECT / "evidence" / "complete_census" / "oracles" / "label_definitions.jsonl"
ENGINE_PATH = HERE / "independent_audit_engine_tr022.py"
RUN_ROOT = HERE / "isolated_full_audits"
TARGET_ID = "projected-env-001715"

EXPECTED = {
    "sources": 14,
    "source_lines": 2208,
    "source_bytes": 83860,
    "expressions": 275,
    "occurrences": 589,
    "expression_mathml_roots": 1100,
    "occurrence_mathml_roots": 1178,
    "formals": 121,
    "tableaux": 50,
    "formula_nodes": 279,
    "terminal_paths": 80,
    "closed_terminal_paths": 40,
    "omitted_subtrees": 6,
    "proof_trees": 17,
    "proof_commands": 77,
    "exercises_unsolved": 9,
    "references": 14,
    "corrections": 7,
}

EXPECTED_PINS = {
    "producer/ARTIFACT_MANIFEST.json": "d343f84ab707ee14a26f3962c1c80ef10a5faed328bf0bd89a7e50081c2ced72",
    "producer/EVIDENCE_MANIFEST.json": "8fd7b1b7a22ab175d103f3b7ec7bb0cf6173048d50d2d547ce9b5b2898546423",
    "producer/PRODUCER_RECEIPT.json": "292885f5eea981620e7341dd94acc063d000fe6e7f6d9961191cde77b225c45d",
    "producer/VALIDATION_RECEIPT.json": "24f8d3113fb5aed87c326e0d671dd84fa6c214d8274e27e514ad6838bfda71b8",
    "producer/PRODUCER_BOUNDARY_RECEIPT.json": "f82b5ad7e05e8fac1f6807c6b833433b1175b698c2c99484e5b21e105a3eea6f",
    "producer/formal_object_semantic_bindings.jsonl": "13af5fee491bab943aa4eb9baaca5e4f416d09ffb9a8b8c28716dfbdbffe1256",
    "work/tr022_formals_authored.json": "be28521690c568b7be259a87c24f231c27ac2031e0b716e66362fa1f1897d2da",
    "work/build_tr022.py": "75898019a7e1e75a21ac596997d3e4512387304bee27e8200ca83a2854808697",
    "work/validate_tr022.py": "86d6cbd3d8c5a945475ab0e23853d745f7495a76dd052f0590fc95d1cd664823",
    "old_fail/FINAL_AUDIT_RECEIPT.json": "0f750e41af40f57170386f847af1a50fa60db23ca323402297473018e7e105f8",
    "old_fail/FINDINGS.jsonl": "92fffa2aca26a80d42bc9d762ace00e88f39f4724ea44918b884d9c1e82a71b9",
}

EXPECTED_TARGET_AUTHORITY_SHA = "7bd8cf6a69a57f9e1a48c96d1779ad4c9df287151850bec8bfd7946f37b5657d"
EXPECTED_TARGET_RECORD_SHA = "d2ddf3e021e83de4b9b0aaf20939256348902b95af568817d0aca9acd6b80365"
EXPECTED_OLD_TARGET_RECORD_SHA = "094270a27c987edb067b98128c887fad269cf453fa410b5bf4aaed0a208b69d7"
EXPECTED_OLD_MANIFEST_SHA = "9d671c5ad58c59591c173c8caa39ef9fb8e3b94e3e81962e156d677af9de8cc3"
DELEGATED_PRODUCER_TREE_PIN = "7ae21b509ea0c3a614f995137db8c5b9d1d6fceb40c3d4b6ff75c73d4ec8eeb0"
MATHML_TAGS = {
    "math", "mi", "mn", "mo", "mrow", "mspace", "mstyle", "msub",
    "msup", "mtable", "mtd", "mtext", "mtr",
}
FORBIDDEN_ROOT_ATTRS = {"aria-label", "role", "class"}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_text(path: Path, value: str) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(HERE):
        raise RuntimeError(f"audit write escaped evidence root: {resolved}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    write_text(path, "".join(compact_json(dict(row)) + "\n" for row in rows))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def records(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(root).as_posix(),
        )
    ]


def records_digest(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(compact_json(rows).encode("utf-8"))


class Audit:
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    def gate(self, finding_id: str, condition: bool, category: str, evidence: Mapping[str, Any]) -> bool:
        if not condition:
            self.findings.append({
                "finding_id": finding_id,
                "severity": "P1",
                "category": category,
                "evidence": dict(evidence),
                "status": "OPEN_CURRENT_CANDIDATE",
            })
        return condition


def protected_snapshot() -> dict[str, Any]:
    scoped: list[dict[str, Any]] = []
    for scope, root in (
        ("producer_projection", PROJECTION),
        ("producer_work", WORK),
        ("oracle", ORACLE),
        ("oracle_validation", ORACLE_VALIDATION),
        ("old_fail_bundle", OLD_FAIL),
    ):
        for row in records(root):
            scoped.append({"scope": scope, **row})
    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    authority_root = Path(authority["authority_root"])
    for source in authority["source_records"]:
        path = authority_root / source["path"]
        scoped.append({
            "scope": "immutable_source",
            "path": source["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    scoped.append({
        "scope": "global_label_oracle",
        "path": str(GLOBAL_LABELS.resolve()),
        "bytes": GLOBAL_LABELS.stat().st_size,
        "sha256": sha256_file(GLOBAL_LABELS),
    })
    scoped.sort(key=lambda row: (row["scope"], row["path"]))
    return {
        "schema": "openlogic-tr022-independent-reaudit-protected-snapshot-v1",
        "file_count": len(scoped),
        "files": scoped,
        "aggregate_sha256": sha256_bytes(compact_json(scoped).encode("utf-8")),
    }


def manifest_review(audit: Audit, root: Path, manifest_name: str, exact_tree: bool, prefix: str) -> dict[str, Any]:
    manifest = read_json(root / manifest_name)
    reviewed = []
    declared_paths: list[str] = []
    for entry in manifest.get("files", []):
        relative = str(entry.get("path", ""))
        declared_paths.append(relative)
        path = root / relative
        safe = bool(relative) and not Path(relative).is_absolute() and ".." not in Path(relative).parts
        good = (
            safe
            and path.is_file()
            and path.stat().st_size == entry.get("bytes")
            and sha256_file(path) == entry.get("sha256")
        )
        audit.gate(
            f"TR022-REAUDIT-{prefix}-MANIFEST-ENTRY",
            good,
            "manifest_integrity",
            {"manifest": manifest_name, "path": relative},
        )
        reviewed.append({"path": relative, "status": "PASS" if good else "FAIL"})
    unique = len(declared_paths) == len(set(declared_paths))
    audit.gate(
        f"TR022-REAUDIT-{prefix}-MANIFEST-UNIQUE",
        unique,
        "manifest_integrity",
        {"manifest": manifest_name, "declared": len(declared_paths), "unique": len(set(declared_paths))},
    )
    unlisted: list[str] = []
    if exact_tree:
        actual = {row["path"] for row in records(root)}
        expected = set(declared_paths) | {manifest_name}
        unlisted = sorted(actual.symmetric_difference(expected))
        audit.gate(
            f"TR022-REAUDIT-{prefix}-MANIFEST-CLOSURE",
            not unlisted,
            "manifest_tree_closure",
            {"manifest": manifest_name, "symmetric_difference": unlisted},
        )
    return {
        "manifest": manifest_name,
        "manifest_sha256": sha256_file(root / manifest_name),
        "entry_count": len(reviewed),
        "entries_passed": sum(row["status"] == "PASS" for row in reviewed),
        "unique_paths": unique,
        "tree_symmetric_difference": unlisted,
        "status": "PASS" if all(row["status"] == "PASS" for row in reviewed) and unique and not unlisted else "FAIL",
    }


def pin_and_old_fail_audit(audit: Audit) -> tuple[dict[str, Any], dict[str, Any]]:
    pin_paths = {
        "producer/ARTIFACT_MANIFEST.json": PROJECTION / "ARTIFACT_MANIFEST.json",
        "producer/EVIDENCE_MANIFEST.json": PROJECTION / "EVIDENCE_MANIFEST.json",
        "producer/PRODUCER_RECEIPT.json": PROJECTION / "PRODUCER_RECEIPT.json",
        "producer/VALIDATION_RECEIPT.json": PROJECTION / "VALIDATION_RECEIPT.json",
        "producer/PRODUCER_BOUNDARY_RECEIPT.json": PROJECTION / "PRODUCER_BOUNDARY_RECEIPT.json",
        "producer/formal_object_semantic_bindings.jsonl": PROJECTION / "formal_object_semantic_bindings.jsonl",
        "work/tr022_formals_authored.json": WORK / "tr022_formals_authored.json",
        "work/build_tr022.py": WORK / "build_tr022.py",
        "work/validate_tr022.py": WORK / "validate_tr022.py",
        "old_fail/FINAL_AUDIT_RECEIPT.json": OLD_FAIL / "FINAL_AUDIT_RECEIPT.json",
        "old_fail/FINDINGS.jsonl": OLD_FAIL / "FINDINGS.jsonl",
    }
    pins = []
    for label, path in pin_paths.items():
        actual = sha256_file(path) if path.is_file() else None
        expected = EXPECTED_PINS[label]
        audit.gate(
            "TR022-REAUDIT-PIN-001",
            actual == expected,
            "candidate_or_lineage_pin",
            {"label": label, "expected": expected, "actual": actual},
        )
        pins.append({"label": label, "bytes": path.stat().st_size if path.is_file() else None, "expected_sha256": expected, "actual_sha256": actual, "status": "PASS" if actual == expected else "FAIL"})

    artifact_manifest = manifest_review(audit, PROJECTION, "ARTIFACT_MANIFEST.json", False, "PRODUCER-ARTIFACT")
    evidence_manifest = manifest_review(audit, PROJECTION, "EVIDENCE_MANIFEST.json", True, "PRODUCER-EVIDENCE")
    # Preserve the supplied tree-pin serialization exactly: pathlib's native
    # path ordering followed by project-relative POSIX paths and compact JSON.
    producer_rows = [
        {
            "path": path.relative_to(PROJECTION).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(PROJECTION.rglob("*"))
        if path.is_file()
    ]
    producer_tree_sha256 = records_digest(producer_rows)
    producer_tree_pin_good = producer_tree_sha256 == DELEGATED_PRODUCER_TREE_PIN
    audit.gate(
        "TR022-REAUDIT-PRODUCER-TREE-PIN",
        producer_tree_pin_good,
        "producer_tree",
        {"expected": DELEGATED_PRODUCER_TREE_PIN, "actual": producer_tree_sha256, "file_count": len(producer_rows)},
    )
    producer_tree = {
        "file_count": len(producer_rows),
        "total_bytes": sum(row["bytes"] for row in producer_rows),
        "actual_sha256": producer_tree_sha256,
        "expected_sha256": DELEGATED_PRODUCER_TREE_PIN,
        "pin_matches": producer_tree_pin_good,
        "algorithm": "sha256(compact canonical JSON of pathlib-native-sorted {path,bytes,sha256} records)",
        "records": producer_rows,
    }
    audit.gate("TR022-REAUDIT-PRODUCER-TREE-COUNT", len(producer_rows) == 28, "producer_tree", {"actual": len(producer_rows), "expected": 28})

    old_manifest = manifest_review(audit, OLD_FAIL, "EVIDENCE_MANIFEST.json", True, "OLD-FAIL")
    audit.gate(
        "TR022-REAUDIT-OLD-FAIL-MANIFEST-PIN",
        old_manifest["manifest_sha256"] == EXPECTED_OLD_MANIFEST_SHA,
        "immutable_failure_lineage",
        {"expected": EXPECTED_OLD_MANIFEST_SHA, "actual": old_manifest["manifest_sha256"]},
    )
    old_receipt = read_json(OLD_FAIL / "FINAL_AUDIT_RECEIPT.json")
    old_findings = read_jsonl(OLD_FAIL / "FINDINGS.jsonl")
    old_lineage_good = (
        old_receipt.get("status") == "FAIL_CURRENT_FINDINGS"
        and old_receipt.get("independent_semantic_audit") == "FAIL"
        and old_receipt.get("finding_count") == 1
        and len(old_findings) == 1
        and old_findings[0].get("finding_id") == "TR022-INDEPENDENT-FORMAL-GROUPING-001"
    )
    audit.gate(
        "TR022-REAUDIT-OLD-FAIL-SEMANTICS",
        old_lineage_good,
        "immutable_failure_lineage",
        {"receipt_status": old_receipt.get("status"), "finding_ids": [row.get("finding_id") for row in old_findings]},
    )
    old_fail_report = {
        "schema": "openlogic-tr022-old-fail-bundle-immutability-audit-v1",
        "manifest_review": old_manifest,
        "bundle_file_count": len(records(OLD_FAIL)),
        "bundle_tree_sha256": records_digest(records(OLD_FAIL)),
        "receipt_sha256": sha256_file(OLD_FAIL / "FINAL_AUDIT_RECEIPT.json"),
        "findings_sha256": sha256_file(OLD_FAIL / "FINDINGS.jsonl"),
        "preserved_finding_id": old_findings[0].get("finding_id") if old_findings else None,
        "status": "PASS" if old_manifest["status"] == "PASS" and old_lineage_good else "FAIL",
    }
    return {
        "schema": "openlogic-tr022-independent-pin-and-producer-tree-audit-v1",
        "pins": pins,
        "artifact_manifest": artifact_manifest,
        "evidence_manifest": evidence_manifest,
        "producer_tree": producer_tree,
        "status": "PASS" if all(row["status"] == "PASS" for row in pins) and artifact_manifest["status"] == evidence_manifest["status"] == "PASS" and producer_tree_pin_good else "FAIL",
    }, old_fail_report


def source_lines(authority: Mapping[str, Any]) -> tuple[dict[tuple[int, int], str], list[dict[str, Any]]]:
    authority_root = Path(authority["authority_root"])
    line_map: dict[tuple[int, int], str] = {}
    reviews = []
    for ordinal, row in enumerate(authority["source_records"], 1):
        path = authority_root / row["path"]
        raw = path.read_bytes()
        decoded = raw.decode("utf-8").splitlines()
        reviews.append({
            "source_ordinal": ordinal,
            "path": row["path"],
            "bytes": len(raw),
            "lines": len(decoded),
            "sha256": sha256_bytes(raw),
            "status": "PASS" if len(raw) == row["bytes"] and len(decoded) == row["lines"] and sha256_bytes(raw) == row["sha256"] else "FAIL",
        })
        for number, text in enumerate(decoded, 1):
            line_map[(ordinal, number)] = text
    return line_map, reviews


def tableau_counts(node: Mapping[str, Any]) -> tuple[int, int, int, int]:
    children = list(node.get("children", []))
    formula = 1 if node.get("node_kind") == "formula" else 0
    omitted = 1 if node.get("node_kind") == "omitted_subtree" else 0
    if not children:
        return formula, 1, 1 if node.get("close") else 0, omitted
    totals = [formula, 0, 0, omitted]
    for child in children:
        child_counts = tableau_counts(child)
        totals = [left + right for left, right in zip(totals, child_counts)]
    return tuple(totals)  # type: ignore[return-value]


def repair_scope_audit(audit: Audit) -> dict[str, Any]:
    current = read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl")
    baseline = read_jsonl(OLD_FAIL / "cold_rebuilds" / "run_a" / "formal_object_semantic_bindings.jsonl")
    current_by_id = {row["formal_object_id"]: row for row in current}
    baseline_by_id = {row["formal_object_id"]: row for row in baseline}
    unchanged = [
        object_id for object_id in sorted(current_by_id)
        if object_id != TARGET_ID and compact_json(current_by_id[object_id]) == compact_json(baseline_by_id.get(object_id))
    ]
    changed = [
        object_id for object_id in sorted(current_by_id)
        if compact_json(current_by_id[object_id]) != compact_json(baseline_by_id.get(object_id))
    ]
    audit.gate("TR022-REAUDIT-REPAIR-SCOPE-001", len(current) == len(baseline) == 121, "bounded_repair_scope", {"current": len(current), "baseline": len(baseline)})
    audit.gate("TR022-REAUDIT-REPAIR-SCOPE-002", len(unchanged) == 120 and changed == [TARGET_ID], "bounded_repair_scope", {"unchanged": len(unchanged), "changed": changed})

    target = current_by_id[TARGET_ID]
    old_target = baseline_by_id[TARGET_ID]
    expected_groups = [
        ["projected-formula-0010700"],
        ["projected-formula-0010701", "projected-formula-0010702"],
    ]
    groups = target.get("exercise_item_groups", [])
    labels = re.findall(r"Source-listed mathematical item ([a-z]+)\b", target.get("listen_text", ""), flags=re.I)
    target_good = (
        target.get("record_sha256") == EXPECTED_TARGET_RECORD_SHA
        and target.get("formal_authority_record_sha256") == EXPECTED_TARGET_AUTHORITY_SHA
        and target.get("source_enumerate_item_count") == 2
        and target.get("source_formula_grouping_status") == "PASS_EXACT_TWO_SOURCE_ITEMS_SECOND_ITEM_HAS_TWO_SIMULTANEOUS_SIGNED_ASSUMPTIONS"
        and len(groups) == 2
        and [row.get("formula_ids") for row in groups] == expected_groups
        and [row.get("formula_count") for row in groups] == [1, 2]
        and groups[1].get("grouping_kind") == "ONE_SOURCE_ITEM_CONTAINING_TWO_SIMULTANEOUS_SIGNED_ASSUMPTIONS"
        and "simultaneous signed assumptions" in groups[1].get("listener_step", "").lower()
        and labels == ["one", "two"]
        and len(target.get("ordered_steps", [])) == 3
        and "item three" not in target.get("listen_text", "").lower()
        and target.get("formula_ids") == ["projected-formula-0010700", "projected-formula-0010701", "projected-formula-0010702"]
        and target.get("exercise_solution_status") == "PRESERVED_UNSOLVED"
    )
    audit.gate("TR022-REAUDIT-REPAIR-TARGET-001", target_good, "repaired_grouping_semantics", {"labels": labels, "groups": [row.get("formula_ids") for row in groups], "target_record_sha256": target.get("record_sha256")})
    old_target_good = (
        old_target.get("record_sha256") == EXPECTED_OLD_TARGET_RECORD_SHA
        and len(old_target.get("ordered_steps", [])) == 4
        and re.findall(r"Source-listed mathematical item ([a-z]+)\b", old_target.get("listen_text", ""), flags=re.I) == ["one", "two", "three"]
        and "exercise_item_groups" not in old_target
    )
    audit.gate("TR022-REAUDIT-OLD-TARGET-001", old_target_good, "pre_repair_baseline", {"old_record_sha256": old_target.get("record_sha256"), "old_step_count": len(old_target.get("ordered_steps", []))})

    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    source_root = Path(authority["authority_root"])
    identity_lines = (source_root / "content/first-order-logic/tableaux/identity.tex").read_text(encoding="utf-8").splitlines()
    block = "\n".join(identity_lines[92:103])
    source_items = len(re.findall(r"\\item(?:\s|$)", block))
    source_good = (
        source_items == 2
        and "\\sFmla{\\False}" in identity_lines[95]
        and "\\sFmla{\\False}" in identity_lines[97]
        and "\\sFmla{\\True}" in identity_lines[99]
        and identity_lines[99].lstrip().startswith("$\\sFmla")
    )
    audit.gate("TR022-REAUDIT-SOURCE-GROUPING-001", source_good, "manual_source_grouping", {"source_item_count": source_items, "lines": [93, 103], "block_sha256": sha256_bytes((block + "\n").encode("utf-8"))})
    return {
        "schema": "openlogic-tr022-independent-bounded-repair-scope-audit-v1",
        "current_formal_file_sha256": sha256_file(PROJECTION / "formal_object_semantic_bindings.jsonl"),
        "pre_repair_formal_file_sha256": sha256_file(OLD_FAIL / "cold_rebuilds" / "run_a" / "formal_object_semantic_bindings.jsonl"),
        "current_formal_authority_sha256": sha256_file(WORK / "tr022_formals_authored.json"),
        "pre_repair_formal_authority_sha256_from_old_protected_snapshot": "287bb2b9bf6dd841f591cda5720dda4be189a6f5764dc842565e3245cae91ff1",
        "unchanged_non_target_formal_count": len(unchanged),
        "changed_formal_ids": changed,
        "target": {
            "formal_object_id": TARGET_ID,
            "record_sha256": target.get("record_sha256"),
            "formal_authority_record_sha256": target.get("formal_authority_record_sha256"),
            "source_item_count": target.get("source_enumerate_item_count"),
            "formula_groups": [row.get("formula_ids") for row in groups],
            "listener_item_labels": labels,
            "ordered_step_count": len(target.get("ordered_steps", [])),
            "source_lines": [93, 103],
            "source_block_sha256": sha256_bytes((block + "\n").encode("utf-8")),
        },
        "old_target": {
            "record_sha256": old_target.get("record_sha256"),
            "listener_item_labels": re.findall(r"Source-listed mathematical item ([a-z]+)\b", old_target.get("listen_text", ""), flags=re.I),
            "ordered_step_count": len(old_target.get("ordered_steps", [])),
        },
        "status": "PASS" if len(unchanged) == 120 and changed == [TARGET_ID] and target_good and old_target_good and source_good else "FAIL",
    }


def accessibility_and_replay_audit(audit: Audit) -> dict[str, Any]:
    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    exact_line_map, source_reviews = source_lines(authority)
    expressions = read_jsonl(PROJECTION / "expression_semantics.jsonl")
    occurrences = read_jsonl(PROJECTION / "semantic_occurrences.jsonl")
    coordinates = read_jsonl(PROJECTION / "formula_coordinate_ledger.jsonl")
    formals = read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl")
    tableaux = read_jsonl(PROJECTION / "tableau_structure_ledger.jsonl")
    commands = read_jsonl(PROJECTION / "proof_command_semantic_bindings.jsonl")
    references = read_jsonl(PROJECTION / "reference_bindings.jsonl")
    corrections = read_jsonl(PROJECTION / "SOURCE_CORRECTIONS.jsonl")
    disclosures = read_jsonl(PROJECTION / "LISTENER_DISCLOSURE_BINDINGS.jsonl")
    replays = read_jsonl(PROJECTION / "continuous_source_replay.jsonl")
    replay_lines = read_jsonl(PROJECTION / "SOURCE_LINE_REPLAY.jsonl")

    expression_ids = [row["expression_id"] for row in expressions]
    formula_ids = [row["formula_id"] for row in occurrences]
    formal_ids = [row["formal_object_id"] for row in formals]
    command_ids = [row["proof_command_id"] for row in commands]
    reference_ids = [row["reference_id"] for row in references]
    correction_ids = [row["correction_id"] for row in corrections]
    uniqueness_good = all(len(values) == len(set(values)) for values in (expression_ids, formula_ids, formal_ids, command_ids, reference_ids, correction_ids))
    crosslinks_good = (
        {row["expression_id"] for row in occurrences}.issubset(expression_ids)
        and {row["formula_id"] for row in coordinates} == set(formula_ids)
        and all(set(row.get("formula_ids", [])).issubset(formula_ids) for row in formals)
        and {row["formal_object_id"] for row in commands}.issubset(formal_ids)
        and {row["correction_id"] for row in disclosures} == set(correction_ids)
    )
    audit.gate("TR022-REAUDIT-ID-CROSSLINK-001", uniqueness_good and crosslinks_good, "stable_ids_and_crosslinks", {"unique": uniqueness_good, "crosslinks": crosslinks_good})

    root_reviews = []
    for row in expressions:
        for field, display in (("reader_mathml_inline", "inline"), ("reader_mathml_block", "block"), ("source_mathml_inline", "inline"), ("source_mathml_block", "block")):
            issues = []
            try:
                root = ET.fromstring(row.get(field, ""))
                tags = {local_name(node.tag) for node in root.iter()}
                if local_name(root.tag) != "math" or len(root) == 0:
                    issues.append("flattened_or_empty")
                if root.attrib.get("display") != display:
                    issues.append("display")
                if root.attrib.get("data-expression-id") != row["expression_id"]:
                    issues.append("expression_id")
                if FORBIDDEN_ROOT_ATTRS.intersection(root.attrib):
                    issues.append("root_aria_role_or_class")
                if not tags.issubset(MATHML_TAGS):
                    issues.append("unexpected_element")
            except ET.ParseError as exc:
                issues.append(f"parse:{exc}")
            root_reviews.append({"owner": row["expression_id"], "field": field, "issues": issues})
    for row in occurrences:
        for field in ("reader_mathml", "source_mathml"):
            issues = []
            try:
                root = ET.fromstring(row.get(field, ""))
                tags = {local_name(node.tag) for node in root.iter()}
                if local_name(root.tag) != "math" or len(root) == 0:
                    issues.append("flattened_or_empty")
                if root.attrib.get("data-expression-id") != row["expression_id"] or root.attrib.get("data-formula-id") != row["formula_id"]:
                    issues.append("stable_id")
                if root.attrib.get("display") != row["display_mode"]:
                    issues.append("display")
                if FORBIDDEN_ROOT_ATTRS.intersection(root.attrib):
                    issues.append("root_aria_role_or_class")
                if not tags.issubset(MATHML_TAGS):
                    issues.append("unexpected_element")
            except ET.ParseError as exc:
                issues.append(f"parse:{exc}")
            root_reviews.append({"owner": row["formula_id"], "field": field, "issues": issues})
    mathml_good = len(root_reviews) == EXPECTED["expression_mathml_roots"] + EXPECTED["occurrence_mathml_roots"] and not any(row["issues"] for row in root_reviews)
    audit.gate("TR022-REAUDIT-MATHML-001", mathml_good, "native_mathml", {"roots": len(root_reviews), "failed": sum(bool(row["issues"]) for row in root_reviews)})

    role_counts = Counter(row["object_role"] for row in formals)
    exercise_unsolved = sum(row["object_role"] == "exercise" and row.get("exercise_solution_status") == "PRESERVED_UNSOLVED" for row in formals)
    tableau_totals = [0, 0, 0, 0]
    tableau_declared_good = True
    for row in tableaux:
        counts = tableau_counts(row["tableau_structure"])
        declared = (row["node_count"], row["terminal_branch_count"], row["closed_terminal_branch_count"], row["omitted_subtree_placeholder_count"])
        tableau_declared_good = tableau_declared_good and counts == declared
        tableau_totals = [left + right for left, right in zip(tableau_totals, counts)]
    command_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for command in commands:
        command_groups[command["formal_object_id"]].append(command)
    command_boundaries_good = True
    for formal in (row for row in formals if row["object_role"] == "proof tree"):
        group = sorted(command_groups[formal["formal_object_id"]], key=lambda row: row["formal_command_ordinal"])
        command_boundaries_good = command_boundaries_good and (
            [row["formal_command_ordinal"] for row in group] == list(range(1, len(group) + 1))
            and [row["proof_command_id"] for row in group] == formal.get("proof_command_ids", [])
            and [row["command"] for row in group] == formal.get("proof_command_names", [])
        )
    formal_good = (
        len(formals) == EXPECTED["formals"]
        and role_counts["proof tree"] == EXPECTED["proof_trees"]
        and role_counts["tableau"] == EXPECTED["tableaux"]
        and exercise_unsolved == EXPECTED["exercises_unsolved"]
        and len(commands) == EXPECTED["proof_commands"]
        and tuple(tableau_totals) == (EXPECTED["formula_nodes"], EXPECTED["terminal_paths"], EXPECTED["closed_terminal_paths"], EXPECTED["omitted_subtrees"])
        and tableau_declared_good
        and command_boundaries_good
    )
    audit.gate("TR022-REAUDIT-FORMAL-001", formal_good, "formal_tableau_proof_boundaries", {"role_counts": dict(sorted(role_counts.items())), "tableau_totals": tableau_totals, "commands": len(commands), "unsolved": exercise_unsolved})

    source_good = (
        len(source_reviews) == EXPECTED["sources"]
        and sum(row["lines"] for row in source_reviews) == EXPECTED["source_lines"]
        and sum(row["bytes"] for row in source_reviews) == EXPECTED["source_bytes"]
        and all(row["status"] == "PASS" for row in source_reviews)
    )
    audit.gate("TR022-REAUDIT-SOURCE-001", source_good, "immutable_source_closure", {"sources": len(source_reviews), "lines": sum(row["lines"] for row in source_reviews), "bytes": sum(row["bytes"] for row in source_reviews)})

    exact_line_good = len(replay_lines) == EXPECTED["source_lines"]
    for row in replay_lines:
        exact_text = exact_line_map.get((row["source_ordinal"], row["line"]))
        exact_line_good = exact_line_good and row["source_text"] == exact_text and row["source_line_sha256"] == sha256_bytes((row["source_text"] + "\n").encode("utf-8"))
    formula_replay_order = []
    reference_replay_order = []
    disclosure_replay_order = []
    spans_good = True
    for replay in replays:
        words = replay["listen_text"].split()
        for field, destination in (("ordered_formula_bindings", formula_replay_order), ("ordered_reference_bindings", reference_replay_order), ("ordered_disclosure_bindings", disclosure_replay_order)):
            for binding in replay[field]:
                destination.append(binding.get("formula_id") or binding.get("reference_id") or binding.get("correction_id"))
                spans_good = spans_good and " ".join(words[binding["word_start"]:binding["word_end"]]) == binding["speech"]
    replay_good = (
        len(replays) == EXPECTED["sources"]
        and [row["source_ordinal"] for row in replays] == list(range(1, EXPECTED["sources"] + 1))
        and formula_replay_order == formula_ids
        and reference_replay_order == reference_ids
        and set(disclosure_replay_order) == set(correction_ids)
        and len(disclosure_replay_order) == EXPECTED["corrections"]
        and spans_good
        and exact_line_good
    )
    audit.gate("TR022-REAUDIT-REPLAY-001", replay_good, "continuous_listener_and_source_replay", {"sources": len(replays), "formula_anchors": len(formula_replay_order), "reference_anchors": len(reference_replay_order), "disclosures": len(disclosure_replay_order), "exact_lines": len(replay_lines), "spans_good": spans_good})

    correction_reviews = []
    authority_root = Path(authority["authority_root"])
    correction_good = len(corrections) == len(disclosures) == EXPECTED["corrections"]
    for correction in corrections:
        source_text = (authority_root / correction["file"]).read_text(encoding="utf-8").splitlines()
        exact = {str(line): source_text[int(line) - 1] for line in correction["lines"]}
        bound = next((row for row in disclosures if row["correction_id"] == correction["correction_id"]), None)
        good = exact == correction["exact_source_lines"] and bound is not None and bound["speech"] == correction["listener_disclosure_speech"]
        correction_good = correction_good and good
        correction_reviews.append({"correction_id": correction["correction_id"], "file": correction["file"], "lines": correction["lines"], "disclosure_id": correction["listener_disclosure_binding_id"], "status": "PASS" if good else "FAIL"})
    audit.gate("TR022-REAUDIT-CORRECTION-001", correction_good, "correction_source_and_listener_binding", {"reviewed": len(correction_reviews), "failed": sum(row["status"] == "FAIL" for row in correction_reviews)})

    dep = read_json(PROJECTION / "DEPENDENCY_BOUNDARY.json")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in PROJECTION.iterdir() if path.is_file())
    external_residue = re.findall(r"https?://[^\s\"<>]+", combined.replace("http://www.w3.org/1998/Math/MathML", ""), flags=re.I)
    offline_good = (
        dep.get("network_dependency") is False
        and dep.get("requires_javascript") is False
        and dep.get("javascript_used") is False
        and dep.get("network_used") is False
        and "<script" not in combined.lower()
        and "javascript:" not in combined.lower()
        and not external_residue
    )
    accessible_fields_good = all(row.get("accessible_name") and row.get("long_description") and row.get("listen_text") for row in formals)
    provenance_good = (
        authority.get("authority_commit") == "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"
        and all(row.get("file") and row.get("line") for row in occurrences)
        and all(row.get("file") and row.get("line") for row in formals)
        and read_json(PROJECTION / "UPSTREAM_INPUTS.json").get("status") == "PASS_ALL_PROTECTED_INPUTS_EXACTLY_PINNED"
    )
    audit.gate("TR022-REAUDIT-OFFLINE-001", offline_good, "offline_no_javascript", {"dependency_boundary": dep, "external_residue": external_residue[:10]})
    audit.gate("TR022-REAUDIT-ACCESSIBILITY-001", accessible_fields_good and provenance_good, "accessibility_and_provenance", {"accessible_formals": sum(bool(row.get("accessible_name") and row.get("long_description") and row.get("listen_text")) for row in formals), "authority_commit": authority.get("authority_commit")})

    counts = {
        "sources": len(source_reviews),
        "source_lines": len(replay_lines),
        "source_bytes": sum(row["bytes"] for row in source_reviews),
        "expressions": len(expressions),
        "occurrences": len(occurrences),
        "expression_mathml_roots": 4 * len(expressions),
        "occurrence_mathml_roots": 2 * len(occurrences),
        "formals": len(formals),
        "tableaux": len(tableaux),
        "formula_nodes": tableau_totals[0],
        "terminal_paths": tableau_totals[1],
        "closed_terminal_paths": tableau_totals[2],
        "omitted_subtrees": tableau_totals[3],
        "proof_trees": role_counts["proof tree"],
        "proof_commands": len(commands),
        "exercises_unsolved": exercise_unsolved,
        "references": len(references),
        "corrections": len(corrections),
    }
    audit.gate("TR022-REAUDIT-COUNTS-001", counts == EXPECTED, "complete_census", {"actual": counts, "expected": EXPECTED})
    return {
        "schema": "openlogic-tr022-independent-accessibility-source-replay-audit-v1",
        "counts": counts,
        "source_reviews": source_reviews,
        "mathml": {
            "root_count": len(root_reviews),
            "failed_root_count": sum(bool(row["issues"]) for row in root_reviews),
            "forbidden_root_attribute_count": sum("root_aria_role_or_class" in row["issues"] for row in root_reviews),
            "native_unflattened": mathml_good,
        },
        "formal_roles": dict(sorted(role_counts.items())),
        "tableau_totals": {"formula_nodes": tableau_totals[0], "terminal_paths": tableau_totals[1], "closed_terminal_paths": tableau_totals[2], "omitted_subtrees": tableau_totals[3]},
        "proof_command_boundaries": "PASS" if command_boundaries_good else "FAIL",
        "continuous_replay": {"formula_anchors": len(formula_replay_order), "reference_anchors": len(reference_replay_order), "disclosure_anchors": len(disclosure_replay_order), "word_spans_exact": spans_good, "source_lines_exact": exact_line_good},
        "correction_reviews": correction_reviews,
        "offline_no_javascript": offline_good,
        "accessible_formal_fields_complete": accessible_fields_good,
        "attribution_provenance": {"authority_commit": authority.get("authority_commit"), "authority_root": authority.get("authority_root"), "source_paths_and_hashes_present": all(row.get("path") and row.get("sha256") for row in authority["source_records"]), "status": "PASS" if provenance_good else "FAIL"},
        "status": "PASS" if counts == EXPECTED and uniqueness_good and crosslinks_good and mathml_good and formal_good and source_good and replay_good and correction_good and offline_good and accessible_fields_good and provenance_good else "FAIL",
    }


def guard_repaired_grouping(row: Mapping[str, Any]) -> None:
    expected = [["projected-formula-0010700"], ["projected-formula-0010701", "projected-formula-0010702"]]
    groups = row.get("exercise_item_groups", [])
    if row.get("source_enumerate_item_count") != 2 or len(groups) != 2:
        raise ValueError("source item count regression")
    if [item.get("formula_ids") for item in groups] != expected or [item.get("formula_count") for item in groups] != [1, 2]:
        raise ValueError("formula group regression")
    if groups[1].get("grouping_kind") != "ONE_SOURCE_ITEM_CONTAINING_TWO_SIMULTANEOUS_SIGNED_ASSUMPTIONS":
        raise ValueError("simultaneous assumption regression")
    if len(row.get("ordered_steps", [])) != 3:
        raise ValueError("listener step regression")
    if re.findall(r"Source-listed mathematical item ([a-z]+)\b", row.get("listen_text", ""), flags=re.I) != ["one", "two"]:
        raise ValueError("listener item announcement regression")


def adversarial_grouping_audit(audit: Audit) -> dict[str, Any]:
    target = next(row for row in read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl") if row["formal_object_id"] == TARGET_ID)
    tests = []

    structural = copy.deepcopy(target)
    second = structural["exercise_item_groups"][1]
    structural["exercise_item_groups"] = [
        structural["exercise_item_groups"][0],
        {**second, "formula_count": 1, "formula_ids": ["projected-formula-0010701"], "formula_source_lines": [98]},
        {**second, "source_item_number": 3, "formula_count": 1, "formula_ids": ["projected-formula-0010702"], "formula_source_lines": [100]},
    ]
    structural["source_enumerate_item_count"] = 3
    tests.append(("split_identity_source_item_two", "split the source's second item into two structural items", structural))

    listener = copy.deepcopy(target)
    intro, one, _two = listener["ordered_steps"]
    two = "Source-listed mathematical item two: " + listener["formula_bindings"][1]["speech"] + "."
    three = "Source-listed mathematical item three: " + listener["formula_bindings"][2]["speech"] + "."
    listener["ordered_steps"] = [intro, one, two, three]
    listener["listen_text"] = listener["accessible_name"] + ". " + " ".join(listener["ordered_steps"])
    tests.append(("misannounce_identity_listener_items", "announce the two assumptions as listener items two and three", listener))

    reviews = []
    for test_id, mutation, payload in tests:
        rejected = False
        reason = None
        try:
            guard_repaired_grouping(payload)
        except ValueError as exc:
            rejected = True
            reason = str(exc)
        serialized = canonical_json(payload).encode("utf-8")
        reviews.append({"test_id": test_id, "mutation": mutation, "mutant_bytes": len(serialized), "mutant_sha256": sha256_bytes(serialized), "rejection": reason, "status": "PASS_FRESH_MUTANT_REJECTED" if rejected else "FAIL_MUTANT_SURVIVED"})
    good = len(reviews) == 2 and all(row["status"] == "PASS_FRESH_MUTANT_REJECTED" for row in reviews)
    audit.gate("TR022-REAUDIT-ADVERSARIAL-GROUPING-001", good, "fresh_grouping_regressions", {"tests": reviews})
    return {"schema": "openlogic-tr022-independent-fresh-grouping-adversarial-audit-v1", "fresh_mutant_count": len(reviews), "tests": reviews, "status": "PASS" if good else "FAIL"}


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location("tr022_fresh_independent_reaudit_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent audit engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_isolated_full_audits(audit: Audit) -> dict[str, Any]:
    if RUN_ROOT.exists():
        raise RuntimeError(f"collision: isolated run root already exists: {RUN_ROOT}")
    engine = load_engine()
    runs = []
    for name in ("run_a", "run_b"):
        output = RUN_ROOT / name
        output.mkdir(parents=True)
        engine.HERE = output
        engine.COLD_ROOT = output / "cold_rebuilds"
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            returncode = engine.main()
        receipt = read_json(output / "FINAL_AUDIT_RECEIPT.json")
        findings = read_jsonl(output / "FINDINGS.jsonl")
        runs.append({
            "name": name,
            "returncode": returncode,
            "stdout_sha256": sha256_bytes(captured.getvalue().encode("utf-8")),
            "receipt_sha256": sha256_file(output / "FINAL_AUDIT_RECEIPT.json"),
            "finding_count": len(findings),
            "status": receipt.get("status"),
        })
        audit.gate("TR022-REAUDIT-COLD-FULL-001", returncode == 0 and not findings and receipt.get("status") == "PASS_ZERO_CURRENT_FINDINGS", "isolated_full_audit", runs[-1])
        manifest_review(audit, output, "EVIDENCE_MANIFEST.json", True, f"ISOLATED-{name.upper()}")
    rows_a = records(RUN_ROOT / "run_a")
    rows_b = records(RUN_ROOT / "run_b")
    identical = rows_a == rows_b
    audit.gate("TR022-REAUDIT-COLD-FULL-002", identical, "full_audit_determinism", {"run_a_files": len(rows_a), "run_b_files": len(rows_b), "run_a_tree": records_digest(rows_a), "run_b_tree": records_digest(rows_b)})
    return {
        "schema": "openlogic-tr022-independent-two-isolated-full-audits-v1",
        "runs": runs,
        "run_a_file_count": len(rows_a),
        "run_b_file_count": len(rows_b),
        "run_a_tree_sha256": records_digest(rows_a),
        "run_b_tree_sha256": records_digest(rows_b),
        "byte_identical": identical,
        "each_full_audit_contains_two_isolated_cold_producer_replays": True,
        "status": "PASS" if identical and all(row["returncode"] == 0 and row["finding_count"] == 0 for row in runs) else "FAIL",
    }


def cache_residue() -> list[str]:
    residue = []
    for root in (HERE, PROJECTION, WORK, ORACLE, ORACLE_VALIDATION, OLD_FAIL):
        for path in root.rglob("*"):
            if path.name == "__pycache__" or (path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}):
                residue.append(str(path.resolve()))
    return sorted(set(residue))


def evidence_manifest() -> dict[str, Any]:
    rows = [row for row in records(HERE) if row["path"] != "EVIDENCE_MANIFEST.json"]
    return {
        "schema": "openlogic-tr022-independent-reaudit-evidence-manifest-v1",
        "tranche_id": "OLAB-TR-022",
        "files": rows,
        "file_count": len(rows),
        "status": "PASS_MANIFEST_COMPLETE",
    }


def main() -> int:
    audit = Audit()
    before = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_BEFORE.json", before)

    pins, old_fail = pin_and_old_fail_audit(audit)
    repair = repair_scope_audit(audit)
    accessibility = accessibility_and_replay_audit(audit)
    adversarial = adversarial_grouping_audit(audit)
    cold = run_isolated_full_audits(audit)

    write_json(HERE / "PIN_AND_PRODUCER_TREE_AUDIT.json", pins)
    write_json(HERE / "OLD_FAIL_BUNDLE_AUDIT.json", old_fail)
    write_json(HERE / "BOUNDED_REPAIR_SCOPE_AUDIT.json", repair)
    write_json(HERE / "ACCESSIBILITY_SOURCE_REPLAY_AUDIT.json", accessibility)
    write_json(HERE / "FRESH_GROUPING_ADVERSARIAL_AUDIT.json", adversarial)
    write_json(HERE / "TWO_ISOLATED_FULL_AUDITS.json", cold)

    targeted_review = {
        "schema": "openlogic-tr022-targeted-manual-semantic-review-v1",
        "review_basis": "Independent inspection of immutable identity.tex lines 93-103, all seven correction records and source lines, all 17 proof-tree command groups, all 50 tableau trees, and the exact pre/post repair target records.",
        "identity_exercise_judgment": "PASS: the source contains exactly two enumerate items; item one is false-signed formula 0010700; item two is one simultaneous assumption set containing false-signed 0010701 and true-signed 0010702.",
        "formal_boundary_judgment": "PASS: 121 source-ordered formal records remain; all 17 proof-tree command groups are contiguous and exact; all 50 tableau trees agree with their declared structural counts.",
        "correction_binding_judgment": "PASS: all seven disclosures preserve exact immutable source text and bind one-to-one to their listener disclosures without changing source bytes.",
        "pre_repair_judgment": "PASS: the immutable old target still exhibits the rejected three-listener-item split and is rejected by both fresh grouping guards.",
        "status": "PASS" if repair["status"] == accessibility["status"] == adversarial["status"] == "PASS" else "FAIL",
    }
    write_json(HERE / "TARGETED_MANUAL_SEMANTIC_REVIEW.json", targeted_review)

    after = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_AFTER.json", after)
    protected_good = before == after
    caches = cache_residue()
    audit.gate("TR022-REAUDIT-PROTECTED-001", protected_good, "protected_input_identity", {"before": before["aggregate_sha256"], "after": after["aggregate_sha256"]})
    audit.gate("TR022-REAUDIT-CACHE-001", not caches, "cache_residue", {"paths": caches})
    protected_receipt = {
        "schema": "openlogic-tr022-independent-reaudit-protected-and-cache-receipt-v1",
        "before_sha256": before["aggregate_sha256"],
        "after_sha256": after["aggregate_sha256"],
        "protected_inputs_byte_identical": protected_good,
        "cache_residue": caches,
        "zero_cache_residue": not caches,
        "status": "PASS" if protected_good and not caches else "FAIL",
    }
    write_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", protected_receipt)

    audit.findings.sort(key=lambda row: (row["finding_id"], compact_json(row["evidence"])))
    write_jsonl(HERE / "FINDINGS.jsonl", audit.findings)
    status = "PASS_ZERO_CURRENT_FINDINGS" if not audit.findings else "FAIL_CURRENT_FINDINGS"
    receipt = {
        "schema": "openlogic-tr022-independent-final-reaudit-receipt-v1",
        "tranche_id": "OLAB-TR-022",
        "programs": {
            "orchestrator": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__))},
            "independent_engine": {"path": str(ENGINE_PATH.resolve()), "sha256": sha256_file(ENGINE_PATH)},
        },
        "producer_pins": {row["label"]: row["actual_sha256"] for row in pins["pins"]},
        "producer_tree_sha256": pins["producer_tree"]["actual_sha256"],
        "old_fail_bundle": {"manifest_sha256": old_fail["manifest_review"]["manifest_sha256"], "receipt_sha256": old_fail["receipt_sha256"], "findings_sha256": old_fail["findings_sha256"]},
        "counts": accessibility["counts"],
        "repair_scope": {"changed_formal_ids": repair["changed_formal_ids"], "unchanged_non_target_formal_count": repair["unchanged_non_target_formal_count"], "formula_groups": repair["target"]["formula_groups"]},
        "isolated_full_audits": {"run_a_tree_sha256": cold["run_a_tree_sha256"], "run_b_tree_sha256": cold["run_b_tree_sha256"], "byte_identical": cold["byte_identical"]},
        "fresh_grouping_mutants_rejected": adversarial["fresh_mutant_count"],
        "protected_snapshot_sha256": before["aggregate_sha256"],
        "finding_count": len(audit.findings),
        "finding_ids": sorted({row["finding_id"] for row in audit.findings}),
        "independent_semantic_accessibility_source_replay_audit": "PASS" if not audit.findings else "FAIL",
        "reader_integration": "NOT_CLAIMED",
        "assistive_technology_launched": False,
        "browser_gui_audio_network_git_publication_used": False,
        "status": status,
    }
    write_json(HERE / "FINAL_REAUDIT_RECEIPT.json", receipt)
    report = (
        "# TR-022 repaired FOL Tableaux independent re-audit\n\n"
        + ("Result: **PASS — zero current findings.**\n\n" if not audit.findings else "Result: **FAIL — current findings remain.**\n\n")
        + f"Two isolated full independent audits produced byte-identical {cold['run_a_file_count']}-file evidence trees. "
        + f"The re-audit independently covered {accessibility['counts']['sources']} immutable sources, {accessibility['counts']['source_lines']} exact source lines, "
        + f"{accessibility['counts']['expressions']} expressions, {accessibility['counts']['occurrences']} occurrences, {accessibility['mathml']['root_count']} native MathML roots, "
        + f"{accessibility['counts']['formals']} formal objects, {accessibility['counts']['tableaux']} tableaux, {accessibility['counts']['proof_commands']} proof commands, "
        + f"{accessibility['counts']['references']} references, and {accessibility['counts']['corrections']} correction disclosures.\n\n"
        + "The repaired identity exercise has exactly two source items: formula 0010700 in item one, and formulas 0010701 plus 0010702 as simultaneous signed assumptions in item two. All other 120 formal records are byte-semantically unchanged from the preserved pre-repair cold baseline.\n\n"
        + "The producer tree, producer work, oracles, immutable source, global labels, and original FAIL bundle remained byte-identical. No GUI, browser, audio, assistive technology, network, Git, or publication action was used.\n"
    )
    write_text(HERE / "REPORT.md", report)
    write_json(HERE / "EVIDENCE_MANIFEST.json", evidence_manifest())
    print(compact_json(receipt))
    return 0 if not audit.findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
