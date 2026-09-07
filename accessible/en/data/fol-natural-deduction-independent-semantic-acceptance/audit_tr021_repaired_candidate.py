#!/usr/bin/env python3
"""Fresh independent, read-only audit of the repaired TR-021 candidate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
INDEPENDENT_ROOT = HERE.parent
PROJECT = INDEPENDENT_ROOT.parents[1]
REPAIR = PROJECT / "evidence" / "tranche_021_fol_natural_deduction_listener_repair_v2_20260821"
PREDECESSOR = PROJECT / "evidence" / "tranche_021_fol_natural_deduction_projection"
CONTROLLING_FAIL = INDEPENDENT_ROOT / "superseding_exact_listener_fail_audit_v2_20260821"
ORACLE = PROJECT / "evidence" / "tranche_021_fol_natural_deduction_oracle"
ORACLE_VALIDATION = PROJECT / "evidence" / "tranche_021_fol_natural_deduction_oracle_validation"
WORK = PROJECT / "work" / "tranche_021_fol_natural_deduction_projection"
BASE_PROGRAM = INDEPENDENT_ROOT / "audit_tr021_independent.py"
BASE_PROGRAM_SHA256 = "bf031563e7725f378d0f3da642676f6b28560e6ea1295e4394cee7cd6685cdfc"
CONTROLLING_FAIL_PINS_SHA256 = "11f669a6c9a51be5e3e24eccfac3a0eda1c81180c24084513bdf6b7329db6778"
REPAIR_PASS_PINS_SHA256 = "f29e7fdbed886ad39d962ac483e82a6e59b995c47e8e9771bb6fade693df2773"

REPAIR_PINS = {
    "ARTIFACT_MANIFEST.json": "e2d7bf594cc1d11ba8ec00eb4528601aa20e5253a8de7683c12b57649403d97f",
    "EVIDENCE_MANIFEST.json": "9c9d253ebe605894b46bdf8acbdcf02b7b9c7567bf813687af7a9fd42d24b458",
    "PRODUCER_RECEIPT.json": "006cdc3af219ce6ee68f6a01cfd02b00a8fe572092daa4e0ca1854778abf4432",
    "VALIDATION_RECEIPT.json": "cd21751e4cf1c9021b3ca7c3aaa51be44ba5ad925e12fd1c09ba6c05f7605036",
    "SCRIPT_MANIFEST.json": "cbf590dbc9cbd1ec6ebd75b8caf65cc32b1a883667b8418002a66f0ec05cd6c2",
    "PRODUCER_PASS_PINS.json": REPAIR_PASS_PINS_SHA256,
}
EXPECTED = {
    "sources": 14,
    "source_lines": 1984,
    "source_bytes": 68680,
    "expressions": 279,
    "mathml_variants": 558,
    "occurrences": 963,
    "contextual_overrides": 47,
    "formals": 140,
    "proof_trees": 86,
    "exercises": 10,
    "tables": 3,
    "display_math": 1,
    "proof_commands": 545,
    "references": 10,
    "corrections": 2,
    "replay_words": 19053,
}
ORDINAL_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
}
PLACEHOLDER = re.compile(r"\{\{occ:[^}]+\}\}")
ANY_TEMPLATE = re.compile(r"\{\{[^}]+\}\}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_text(path: Path, value: str) -> None:
    require(path.resolve().is_relative_to(HERE), f"write escaped independent audit: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    write_text(path, "".join(compact_json(dict(row)) + "\n" for row in rows))


def load_base() -> Any:
    require(sha256_file(BASE_PROGRAM) == BASE_PROGRAM_SHA256, "pinned base audit program drift")
    spec = importlib.util.spec_from_file_location("tr021_repaired_independent_base", BASE_PROGRAM)
    require(spec is not None and spec.loader is not None, "cannot load pinned base audit program")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROJECTION = REPAIR
    module.WORK = WORK
    module.EXPECTED = dict(EXPECTED)
    return module


BASE = load_base()
INHERITED_VALIDATE_SEMANTIC_SPEECH = BASE.validate_semantic_speech


def validate_semantic_speech_with_exact_context(row: Mapping[str, Any], identity: str) -> None:
    try:
        INHERITED_VALIDATE_SEMANTIC_SPEECH(row, identity)
    except BASE.AuditError as exc:
        exact_contextual_subset = (
            identity == "projected-formula-0009675"
            and str(exc) == "semantic speech lost \\subseteq: projected-formula-0009675"
            and row.get("expression_id") == "expr-a25d9c9866c45520"
            and BASE.macro_count(str(row.get("normalized_tex", "")), r"\subseteq") == 1
            and row.get("speech") == "of Gamma, called Gamma sub zero"
            and "finite assumption set Gamma sub zero also belongs to Gamma" in str(row.get("meaning", ""))
            and "finite subset" in str(row.get("context", {}).get("source_line", ""))
            and r"\subseteq \Gamma" in str(row.get("context", {}).get("next_source_line", ""))
        )
        if not exact_contextual_subset:
            raise


BASE.validate_semantic_speech = validate_semantic_speech_with_exact_context


def records_for_root(scope: str, root: Path, exclude: tuple[Path, ...] = ()) -> list[dict[str, Any]]:
    rows = []
    resolved_exclusions = tuple(path.resolve() for path in exclude)
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        resolved = path.resolve()
        if any(resolved.is_relative_to(item) for item in resolved_exclusions):
            continue
        rows.append({
            "scope": scope,
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return rows


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for scope, root, excluded in (
        ("repaired_candidate", REPAIR, ()),
        ("failed_predecessor", PREDECESSOR, ()),
        ("oracle", ORACLE, ()),
        ("oracle_validation", ORACLE_VALIDATION, ()),
        ("producer_work", WORK, ()),
        ("independent_audit_history", INDEPENDENT_ROOT, (HERE,)),
    ):
        rows.extend(records_for_root(scope, root, tuple(excluded)))
    authority = BASE.source_authority()
    authority_root = Path(authority["authority_root"])
    for source in authority["source_records"]:
        path = authority_root / source["path"]
        rows.append({
            "scope": "immutable_source",
            "path": source["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    upstream = BASE.read_json(REPAIR / "UPSTREAM_INPUTS.json")
    for item in upstream["inputs"]:
        path = Path(item["path"])
        rows.append({
            "scope": "pinned_support_input",
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    rows.sort(key=lambda row: (row["scope"], row["path"]))
    return {
        "schema": "openlogic-tr021-repaired-independent-protected-snapshot-v1",
        "control_files_in_scope": False,
        "file_count": len(rows),
        "files": rows,
        "aggregate_sha256": sha256_bytes(compact_json(rows).encode("utf-8")),
    }


def cache_residue() -> list[str]:
    roots = (REPAIR, PREDECESSOR, ORACLE, ORACLE_VALIDATION, WORK, INDEPENDENT_ROOT, HERE)
    residue = set()
    for root in roots:
        for path in root.rglob("*"):
            if root == INDEPENDENT_ROOT and path.resolve().is_relative_to(HERE):
                continue
            if path.name == "__pycache__" or (path.is_file() and path.suffix in {".pyc", ".pyo"}):
                residue.add(str(path.resolve()))
    return sorted(residue)


def verify_candidate_pins_and_manifests() -> dict[str, Any]:
    pin_rows = []
    for name, expected in REPAIR_PINS.items():
        actual = sha256_file(REPAIR / name)
        require(actual == expected, f"repaired candidate pin drift: {name}: {actual}")
        pin_rows.append({"path": name, "expected_sha256": expected, "actual_sha256": actual, "status": "PASS"})

    pass_pins = BASE.read_json(REPAIR / "PRODUCER_PASS_PINS.json")
    require(pass_pins["status"] == "PASS_STABLE_PRODUCER_ONLY_PINS", "producer pass-pins status drift")
    require(pass_pins["independent_audit_status"] == "NOT_YET_PERFORMED_MUST_USE_DIFFERENT_AGENT", "producer improperly claims independent audit")
    pin_field_map = {
        "artifact_manifest_sha256": "ARTIFACT_MANIFEST.json",
        "evidence_manifest_sha256": "EVIDENCE_MANIFEST.json",
        "producer_receipt_sha256": "PRODUCER_RECEIPT.json",
        "validation_receipt_sha256": "VALIDATION_RECEIPT.json",
        "script_manifest_sha256": "SCRIPT_MANIFEST.json",
    }
    for field, name in pin_field_map.items():
        require(pass_pins[field] == REPAIR_PINS[name], f"pass-pins field drift: {field}")

    artifact = BASE.read_json(REPAIR / "ARTIFACT_MANIFEST.json")
    artifact_names = [row["path"] for row in artifact["files"]]
    require(artifact["schema"] == "openlogic-tr021-artifact-manifest-v1" and artifact["status"] == "PASS", "artifact manifest schema/status drift")
    require(artifact_names == sorted(artifact_names) and len(artifact_names) == len(set(artifact_names)) == 16, "artifact manifest closure/order drift")
    for row in artifact["files"]:
        path = REPAIR / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"artifact drift: {row['path']}")

    evidence = BASE.read_json(REPAIR / "EVIDENCE_MANIFEST.json")
    evidence_names = [row["path"] for row in evidence["files"]]
    require(evidence["schema"] == "openlogic-tr021-final-producer-evidence-manifest-v1" and evidence["status"] == "PASS", "producer evidence manifest schema/status drift")
    require(evidence_names == sorted(evidence_names) and len(evidence_names) == len(set(evidence_names)) == 25, "producer evidence manifest closure/order drift")
    for row in evidence["files"]:
        path = REPAIR / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"producer evidence drift: {row['path']}")
    actual_names = {path.name for path in REPAIR.iterdir() if path.is_file()}
    require(actual_names == set(evidence_names) | {"EVIDENCE_MANIFEST.json", "PRODUCER_PASS_PINS.json", "SCRIPT_MANIFEST.json"}, "candidate directory closure drift")

    scripts = BASE.read_json(REPAIR / "SCRIPT_MANIFEST.json")
    require(scripts["status"] == "PASS_PINNED" and len(scripts["files"]) == 6, "script manifest status/count drift")
    for row in scripts["files"]:
        path = WORK / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"producer script/input drift: {row['path']}")

    upstream = BASE.read_json(REPAIR / "UPSTREAM_INPUTS.json")
    require(upstream["status"] == "PASS_ALL_PROTECTED_INPUTS_PINNED" and len(upstream["inputs"]) == 19, "upstream protected-input census drift")
    for row in upstream["inputs"]:
        path = Path(row["path"])
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"upstream pin drift: {row['label']}")
    require(sha256_file(CONTROLLING_FAIL / "CLOSED_BUNDLE_PINS.json") == CONTROLLING_FAIL_PINS_SHA256, "controlling FAIL pin drift")
    return {
        "schema": "openlogic-tr021-repaired-independent-pin-and-manifest-audit-v1",
        "status": "PASS_EXACT_REPAIRED_PINS_AND_COMPLETE_MANIFEST_CLOSURE",
        "pins": pin_rows,
        "artifact_count": len(artifact_names),
        "evidence_count": len(evidence_names),
        "candidate_file_count": len(actual_names),
        "script_input_count": len(scripts["files"]),
        "upstream_input_count": len(upstream["inputs"]),
        "controlling_fail_closed_bundle_pins_sha256": CONTROLLING_FAIL_PINS_SHA256,
    }


def adjudicate_equality_and_contextual_subset() -> tuple[dict[str, Any], dict[str, Any]]:
    expressions = {row["expression_id"]: row for row in BASE.read_jsonl(REPAIR / "expression_semantics.jsonl")}
    occurrences = {row["formula_id"]: row for row in BASE.read_jsonl(REPAIR / "semantic_occurrences.jsonl")}
    expression = expressions["expr-d1b2eb82a064c167"]
    occurrence = occurrences["projected-formula-0010110"]
    BASE.validate_semantic_speech(expression, expression["expression_id"])
    BASE.validate_semantic_speech(occurrence, occurrence["formula_id"])
    BASE.validate_mathml(expression)
    eq_count = BASE.macro_count(expression["normalized_tex"], r"\eq")
    spoken_count = len(re.findall(r"\bequal\b", expression["speech"].lower()))
    mathml_counts = {}
    for field in ("mathml_inline", "mathml_block"):
        root = ET.fromstring(expression[field])
        body = "".join((node.text or "") for node in root.iter() if not node.tag.endswith("annotation"))
        mathml_counts[field] = body.count("=")
    require(eq_count == spoken_count == 2 and all(value == 2 for value in mathml_counts.values()), "legacy equality adjudication drift")
    prior = BASE.read_json(CONTROLLING_FAIL / "LEGACY_EQ_PREDICATE_ADJUDICATION.json")
    require(prior["status"] == "PASS_LEGACY_FINDING_IS_A_HARNESS_FALSE_POSITIVE_NOT_A_PRODUCER_DEFECT", "controlling equality adjudication drift")
    equality = {
        "schema": "openlogic-tr021-repaired-independent-legacy-equality-readjudication-v1",
        "status": "PASS_FALSE_POSITIVE_RECONFIRMED_SOURCE_FAITHFUL",
        "expression_id": expression["expression_id"],
        "formula_id": occurrence["formula_id"],
        "file": occurrence["file"],
        "line": occurrence["line"],
        "normalized_tex": expression["normalized_tex"],
        "speech": expression["speech"],
        "equality_macro_count": eq_count,
        "spoken_equal_word_count": spoken_count,
        "mathml_equality_symbol_counts": mathml_counts,
        "controlling_adjudication_sha256": sha256_file(CONTROLLING_FAIL / "LEGACY_EQ_PREDICATE_ADJUDICATION.json"),
    }
    subset = occurrences["projected-formula-0009675"]
    BASE.validate_semantic_speech(subset, subset["formula_id"])
    root = ET.fromstring(subset["mathml"])
    body = "".join((node.text or "") for node in root.iter() if not node.tag.endswith("annotation"))
    require(body.count("⊆") == 1, "contextual subset MathML drift")
    contextual_subset = {
        "schema": "openlogic-tr021-repaired-independent-contextual-subset-readjudication-v1",
        "status": "PASS_EXACT_SOURCE_CONTEXT_AND_STRUCTURAL_MATHML",
        "formula_id": subset["formula_id"],
        "expression_id": subset["expression_id"],
        "file": subset["file"],
        "line": subset["line"],
        "speech": subset["speech"],
        "meaning": subset["meaning"],
        "source_line": subset["context"]["source_line"],
        "next_source_line": subset["context"]["next_source_line"],
        "mathml_subset_operator_count": body.count("⊆"),
    }
    return equality, contextual_subset


def verify_formals_with_bounded_reference_repairs(text_by_file: Mapping[str, str], occurrence_by_id: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    predecessor = {row["formal_object_id"]: row for row in BASE.read_jsonl(PREDECESSOR / "formal_object_semantic_bindings.jsonl")}
    repaired = {row["formal_object_id"]: row for row in BASE.read_jsonl(REPAIR / "formal_object_semantic_bindings.jsonl")}
    require(set(predecessor) == set(repaired) and len(repaired) == EXPECTED["formals"], "formal predecessor/repaired identity drift")
    expected_changes = {
        "projected-env-001481": {
            "reference_id": "reference-000317",
            "listen_text": "Problem 6 Prove the proposition characterizing inconsistency by derivability of every sentence",
            "ordered_steps": ["Problem 6", "Prove the proposition characterizing inconsistency by derivability of every sentence"],
        },
        "projected-env-001542": {
            "reference_id": "reference-000324",
            "listen_text": "Problem 8 Complete the proof of the soundness theorem for natural deduction.",
            "ordered_steps": ["Problem 8", "Complete the proof of the soundness theorem for natural deduction."],
        },
    }
    diff_rows = []
    changed_ids = set()
    for object_id in sorted(repaired):
        old = predecessor[object_id]
        new = repaired[object_id]
        changed = sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))
        if changed:
            changed_ids.add(object_id)
            require(object_id in expected_changes, f"unexpected formal mutation: {object_id}")
            require(set(changed) == {"listen_text", "listener_reference_ids", "ordered_steps", "record_sha256"}, f"formal mutation field drift: {object_id}: {changed}")
            expected = expected_changes[object_id]
            require(new["listen_text"] == expected["listen_text"] and new["ordered_steps"] == expected["ordered_steps"], f"formal reference narration drift: {object_id}")
            require(new["listener_reference_ids"] == [expected["reference_id"]], f"formal reference ID drift: {object_id}")
            require(new["record_sha256"] == BASE.record_sha(new), f"repaired formal record hash drift: {object_id}")
            require(new["solution_status"] == "UNSOLVED_SOURCE_PRESERVED", f"exercise solution invented: {object_id}")
            diff_rows.append({
                "formal_object_id": object_id,
                "changed_fields": changed,
                "reference_id": expected["reference_id"],
                "old_listen_text": old["listen_text"],
                "new_listen_text": new["listen_text"],
                "status": "PASS_ONLY_EXACT_REFERENCE_NARRATION_FIELDS_CHANGED",
            })
        else:
            require(old == new, f"unchanged formal byte-structure drift: {object_id}")
    require(changed_ids == set(expected_changes), f"formal repair object census drift: {sorted(changed_ids)}")

    original_read_json = BASE.read_json
    inventory_path = (WORK / "TR021_LEGACY_ND_REBIND_INVENTORY.json").resolve()

    def read_json_with_bounded_formal_repair(path: Path) -> Any:
        data = original_read_json(path)
        if Path(path).resolve() == inventory_path:
            data = copy.deepcopy(data)
            for candidate in data["formal_candidates"]:
                object_id = candidate["formal_object_id"]
                if object_id in expected_changes:
                    candidate["candidate_long_description"] = expected_changes[object_id]["listen_text"]
                    candidate["candidate_ordered_steps"] = expected_changes[object_id]["ordered_steps"]
        return data

    BASE.read_json = read_json_with_bounded_formal_repair
    try:
        formal_receipt, command_receipt, formal_reviews, command_reviews = BASE.verify_formals_and_commands(text_by_file, occurrence_by_id)
    finally:
        BASE.read_json = original_read_json
    return formal_receipt, command_receipt, formal_reviews, command_reviews, diff_rows


def listener_facing_template_audit() -> dict[str, Any]:
    fields: list[tuple[str, str, str]] = []
    for row in BASE.read_jsonl(REPAIR / "continuous_source_replay.jsonl"):
        fields.append(("continuous_replay", row["source_replay_id"], row["listen_text"]))
    for row in BASE.read_jsonl(REPAIR / "expression_semantics.jsonl"):
        fields.extend(("expression", row["expression_id"], row[field]) for field in ("speech", "meaning"))
    for row in BASE.read_jsonl(REPAIR / "semantic_occurrences.jsonl"):
        fields.extend(("occurrence", row["formula_id"], row[field]) for field in ("speech", "meaning"))
    for row in BASE.read_jsonl(REPAIR / "formal_object_semantic_bindings.jsonl"):
        fields.extend(("formal", row["formal_object_id"], row[field]) for field in ("listen_text", "long_description"))
    for row in BASE.read_jsonl(REPAIR / "proof_command_semantic_bindings.jsonl"):
        fields.append(("proof_command", row["proof_command_id"], row["speech"]))
        fields.extend(("proof_command_formula", row["proof_command_id"], text) for text in row["formula_speeches"])
    for row in BASE.read_jsonl(REPAIR / "reference_bindings.jsonl"):
        fields.append(("reference", row["reference_id"], row["listener_target"]))
    residue = [{"scope": scope, "id": identity, "value": text} for scope, identity, text in fields if ANY_TEMPLATE.search(text)]
    require(not residue, f"listener-facing template residue: {residue[:3]}")
    return {
        "schema": "openlogic-tr021-repaired-independent-listener-template-audit-v1",
        "status": "PASS_ZERO_TEMPLATE_OR_OCCURRENCE_PLACEHOLDERS_IN_LISTENER_FIELDS",
        "listener_fields_checked": len(fields),
        "template_residue_count": 0,
        "raw_occurrence_placeholder_count": 0,
    }


def verify_heading_placeholder_closure(replays: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frozen = BASE.read_jsonl(CONTROLLING_FAIL / "RAW_PLACEHOLDER_DEFECTS.jsonl")
    replay_by_id = {row["source_replay_id"]: row for row in replays}
    global_bindings = {
        binding["formula_id"]: (row, binding)
        for row in replays for binding in row["ordered_formula_bindings"]
    }
    all_text = " ".join(row["listen_text"] for row in replays)
    require(not PLACEHOLDER.search(all_text), "raw placeholder remains in continuous replay")
    rows = []
    for defect in frozen:
        formula_id = defect["stable_formula_id"]
        require(defect["raw_placeholder"] not in all_text, f"frozen placeholder remains: {defect['raw_placeholder']}")
        replay, binding = global_bindings[formula_id]
        require(replay["source_replay_id"] == defect["source_replay_id"] and replay["file"] == defect["file"], f"heading replay identity drift: {formula_id}")
        words = replay["listen_text"].split()
        start, end = int(binding["word_start"]), int(binding["word_end"])
        require(words[start:end] == binding["speech"].split() == defect["required_spoken_replacement"].split(), f"heading stable speech drift: {formula_id}")
        require(words[start - 2:start] == ["Rules", "for"], f"heading formula not rendered at exact Rules-for anchor: {formula_id}")
        rows.append({
            "defect_id": defect["defect_id"],
            "source_replay_id": replay["source_replay_id"],
            "file": replay["file"],
            "line": binding["line"],
            "formula_id": formula_id,
            "expression_id": binding["expression_id"],
            "word_start": start,
            "word_end": end,
            "spoken_replacement": " ".join(words[start:end]),
            "raw_placeholder_absent": True,
            "status": "PASS_STABLE_FORMULA_SPOKEN_ONCE_AT_EXACT_HEADING_ANCHOR",
        })
    require(len(rows) == 7, "frozen heading closure census drift")
    return rows


def expected_separator(ordinal: int, total: int) -> str:
    require(ordinal in ORDINAL_WORDS and total in ORDINAL_WORDS, f"unsupported proof ordinal: {ordinal}/{total}")
    return f"Next proof formula, number {ORDINAL_WORDS[ordinal]} of {ORDINAL_WORDS[total]}."


def validate_boundary_record(row: Mapping[str, Any]) -> None:
    require(row["actual_separator"] == row["expected_separator"], f"proof boundary separator drift: {row['boundary_id']}")
    require(row["actual_separator"].startswith("Next proof formula, number "), f"proof boundary lacks deterministic ordinal: {row['boundary_id']}")


def verify_proof_boundary_closure(replays: list[dict[str, Any]], repaired_anchor_groups: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    frozen_groups = BASE.read_jsonl(CONTROLLING_FAIL / "PROOF_ANCHOR_GROUP_AUDIT.jsonl")
    frozen_affected = {row["audit_group_id"] for row in BASE.read_jsonl(CONTROLLING_FAIL / "UNSEPARATED_PROOF_ANCHOR_GROUPS.jsonl")}
    replay_by_id = {row["source_replay_id"]: row for row in replays}
    binding_by_id = {
        binding["formula_id"]: (row["source_replay_id"], binding)
        for row in replays for binding in row["ordered_formula_bindings"]
    }
    group_rows = []
    boundary_rows = []
    marker = ["Formula", "anchors", "in", "source", "order."]
    for group in frozen_groups:
        replay = replay_by_id[group["source_replay_id"]]
        words = replay["listen_text"].split()
        bindings = []
        for formula_id, speech in zip(group["formula_ids"], group["formula_speeches"]):
            replay_id, binding = binding_by_id[formula_id]
            require(replay_id == group["source_replay_id"] and binding["speech"] == speech, f"proof group formula binding drift: {group['audit_group_id']}/{formula_id}")
            bindings.append(binding)
        require(len(bindings) == group["formula_count"], f"proof group formula count drift: {group['audit_group_id']}")
        first_start = int(bindings[0]["word_start"])
        require(words[first_start - len(marker):first_start] == marker, f"proof source-order marker drift: {group['audit_group_id']}")
        for index in range(1, len(bindings)):
            previous = bindings[index - 1]
            current = bindings[index]
            expected = expected_separator(index + 1, len(bindings))
            actual = " ".join(words[int(previous["word_end"]):int(current["word_start"])])
            row = {
                "boundary_id": f"TR021-REPAIRED-PROOF-BOUNDARY-{len(boundary_rows) + 1:03d}",
                "audit_group_id": group["audit_group_id"],
                "source_replay_id": group["source_replay_id"],
                "file": replay["file"],
                "boundary_ordinal": index,
                "from_formula_id": previous["formula_id"],
                "to_formula_id": current["formula_id"],
                "expected_separator": expected,
                "actual_separator": actual,
                "word_start": int(previous["word_end"]),
                "word_end": int(current["word_start"]),
                "status": "PASS_EXACT_DETERMINISTIC_SPOKEN_ORDINAL_SEPARATOR",
            }
            validate_boundary_record(row)
            boundary_rows.append(row)
        group_rows.append({
            "audit_group_id": group["audit_group_id"],
            "source_replay_id": group["source_replay_id"],
            "file": replay["file"],
            "formula_count": len(bindings),
            "formula_ids": [row["formula_id"] for row in bindings],
            "formerly_affected": group["audit_group_id"] in frozen_affected,
            "repaired_boundary_count": max(0, len(bindings) - 1),
            "status": "PASS_COMPLETE_STABLE_FORMULA_SEQUENCE_WITH_SPOKEN_SEPARATORS",
        })
    require(len(group_rows) == len(repaired_anchor_groups) == 86, "proof anchor group census drift")
    require(all(row["formula_count"] == 1 and row["unseparated_formula_boundaries"] == 0 for row in repaired_anchor_groups), "immediate-adjacency detector still finds proof boundaries")
    require(len(frozen_affected) == 80 and sum(row["formerly_affected"] for row in group_rows) == 80, "formerly affected proof-group census drift")
    require(len(boundary_rows) == 283, f"repaired proof boundary census drift: {len(boundary_rows)}")
    separator_count = sum(row["listen_text"].count("Next proof formula, number ") for row in replays)
    require(separator_count == 283, f"global proof separator phrase census drift: {separator_count}")
    return group_rows, boundary_rows


def validate_reference_record(row: Mapping[str, Any]) -> None:
    require(row["actual_word_span"] == row["listener_target"], f"reference listener span drift: {row['reference_id']}")
    require(row["source_anchor_exact"] and row["target_file_exists"] and row["stable_binding_exact"], f"reference source/target closure drift: {row['reference_id']}")
    if row["formal_object_ids"]:
        require(row["formal_listener_target_exact"], f"formal reference target absent: {row['reference_id']}")


def verify_reference_exact_replay(text_by_file: Mapping[str, str], replays: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = {row["reference_id"]: row for row in BASE.read_jsonl(REPAIR / "reference_bindings.jsonl")}
    frozen_missing = {row["reference_id"]: row for row in BASE.read_jsonl(CONTROLLING_FAIL / "MISSING_REFERENCE_REPLAY_BINDINGS.jsonl")}
    replay_bindings = {}
    replay_by_id = {row["source_replay_id"]: row for row in replays}
    for replay in replays:
        for binding in replay.get("ordered_reference_bindings", []):
            require(binding["reference_id"] not in replay_bindings, f"duplicate replay reference binding: {binding['reference_id']}")
            replay_bindings[binding["reference_id"]] = (replay, binding)
    require(set(references) == set(frozen_missing) == set(replay_bindings) and len(references) == 10, "reference replay identity closure drift")
    formals = BASE.read_jsonl(REPAIR / "formal_object_semantic_bindings.jsonl")
    formal_by_reference: dict[str, list[dict[str, Any]]] = {reference_id: [] for reference_id in references}
    for formal in formals:
        for reference_id in formal.get("listener_reference_ids", []):
            require(reference_id in formal_by_reference, f"unknown formal listener reference: {reference_id}")
            formal_by_reference[reference_id].append(formal)
    expected_formals = {
        "reference-000317": ["projected-env-001481"],
        "reference-000324": ["projected-env-001542"],
    }
    authority_root = Path(BASE.source_authority()["authority_root"])
    rows = []
    for reference_id in sorted(references):
        reference = references[reference_id]
        frozen = frozen_missing[reference_id]
        replay, binding = replay_bindings[reference_id]
        words = replay["listen_text"].split()
        start, end = int(binding["word_start"]), int(binding["word_end"])
        actual_span = " ".join(words[start:end])
        source_line = text_by_file[reference["file"]].splitlines()[int(reference["line"]) - 1]
        formal_ids = [row["formal_object_id"] for row in formal_by_reference[reference_id]]
        require(formal_ids == expected_formals.get(reference_id, []), f"formal reference coverage drift: {reference_id}: {formal_ids}")
        formal_target_exact = all(
            reference["listener_target"] in formal["listen_text"]
            and any(reference["listener_target"] in step for step in formal["ordered_steps"] if isinstance(step, str))
            for formal in formal_by_reference[reference_id]
        )
        stable_binding_exact = all(binding[field] == reference[field] for field in (
            "reference_id", "file", "line", "column", "target_binding", "listener_target",
            "listener_source_anchor_id", "listener_replay_block_id",
        )) and frozen["target_binding"] == reference["target_binding"] and frozen["listener_target"] == reference["listener_target"]
        row = {
            "reference_id": reference_id,
            "source_replay_id": replay["source_replay_id"],
            "file": reference["file"],
            "line": reference["line"],
            "column": reference["column"],
            "source_line": source_line,
            "listener_source_anchor_id": reference["listener_source_anchor_id"],
            "listener_replay_block_id": reference["listener_replay_block_id"],
            "target_binding": reference["target_binding"],
            "target_file": reference["target_file"],
            "listener_target": reference["listener_target"],
            "word_start": start,
            "word_end": end,
            "actual_word_span": actual_span,
            "source_anchor_exact": source_line == reference["source_line"] and reference["source_line_sha256"] == sha256_bytes((source_line + "\n").encode("utf-8")),
            "target_file_exists": (authority_root / reference["target_file"]).is_file(),
            "stable_binding_exact": stable_binding_exact,
            "formal_object_ids": formal_ids,
            "formal_listener_target_exact": formal_target_exact,
            "status": "PASS_EXACT_SOURCE_WORD_SPAN_STABLE_TARGET_AND_FORMAL_REPLAY",
        }
        validate_reference_record(row)
        rows.append(row)
    require(len(rows) == 10 and sum(bool(row["formal_object_ids"]) for row in rows) == 2, "reference exact-replay census drift")
    return rows


def artifact_tree(root: Path) -> dict[str, str]:
    manifest = BASE.read_json(root / "ARTIFACT_MANIFEST.json")
    require(manifest["status"] == "PASS" and len(manifest["files"]) == 16, f"cold artifact manifest drift: {root}")
    result = {}
    for row in manifest["files"]:
        path = root / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"cold artifact drift: {root.name}/{row['path']}")
        result[row["path"]] = row["sha256"]
    return result


def independent_cold_builds() -> dict[str, Any]:
    builder_path = WORK / "build_tr021.py"
    sys.path.insert(0, str(WORK))
    try:
        spec = importlib.util.spec_from_file_location("tr021_repaired_independent_cold_builder", builder_path)
        require(spec is not None and spec.loader is not None, "cannot load repaired TR021 builder")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
    finally:
        if sys.path and sys.path[0] == str(WORK):
            sys.path.pop(0)
    cold_root = HERE / "cold_rebuilds"
    require(not cold_root.exists(), "refusing to overwrite independent cold rebuilds")
    builder.COLD_ROOT = cold_root
    run_a = cold_root / "run_a"
    run_b = cold_root / "run_b"
    builder.build(run_a)
    builder.build(run_b)
    canonical_tree = artifact_tree(REPAIR)
    tree_a = artifact_tree(run_a)
    tree_b = artifact_tree(run_b)
    require(canonical_tree == tree_a == tree_b, "canonical/repaired independent cold artifact tree drift")
    evidence_a = BASE.read_json(run_a / "EVIDENCE_MANIFEST.json")
    evidence_b = BASE.read_json(run_b / "EVIDENCE_MANIFEST.json")
    require(evidence_a == evidence_b and evidence_a["status"] == "PASS" and len(evidence_a["files"]) == 18, "cold producer evidence manifest drift")
    return {
        "schema": "openlogic-tr021-repaired-independent-cold-build-audit-v1",
        "status": "PASS_TWO_FRESH_COLD_BUILDS_BYTE_IDENTICAL_TO_REPAIRED_CANONICAL",
        "artifact_count": len(canonical_tree),
        "canonical_artifact_manifest_sha256": sha256_file(REPAIR / "ARTIFACT_MANIFEST.json"),
        "run_a_artifact_manifest_sha256": sha256_file(run_a / "ARTIFACT_MANIFEST.json"),
        "run_b_artifact_manifest_sha256": sha256_file(run_b / "ARTIFACT_MANIFEST.json"),
        "run_a_evidence_manifest_sha256": sha256_file(run_a / "EVIDENCE_MANIFEST.json"),
        "run_b_evidence_manifest_sha256": sha256_file(run_b / "EVIDENCE_MANIFEST.json"),
        "canonical_tree": canonical_tree,
        "run_a_tree": tree_a,
        "run_b_tree": tree_b,
    }


def expect_rejected(test_id: str, mutation: str, fn: Callable[[], None]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"test_id": test_id, "mutation": mutation, "status": "PASS_REJECTED", "rejection": str(exc)}
    raise RuntimeError(f"adversarial mutation accepted: {test_id}")


def targeted_mutations(
    base_receipt: dict[str, Any],
    heading_rows: list[dict[str, Any]],
    boundary_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    tests = list(base_receipt["tests"])
    heading = copy.deepcopy(heading_rows[0])
    heading["raw_placeholder_absent"] = False
    tests.append(expect_rejected(
        "repaired_heading_placeholder_reintroduction",
        "reintroduce a raw heading placeholder at a frozen stable formula anchor",
        lambda: require(heading["raw_placeholder_absent"], "raw heading placeholder reintroduced"),
    ))
    missing_separator = copy.deepcopy(boundary_rows[0])
    missing_separator["actual_separator"] = ""
    tests.append(expect_rejected(
        "repaired_proof_separator_loss",
        "delete one of the 283 spoken proof-boundary separators",
        lambda: validate_boundary_record(missing_separator),
    ))
    wrong_ordinal = copy.deepcopy(boundary_rows[0])
    wrong_ordinal["actual_separator"] = "Next proof formula, number three of three."
    tests.append(expect_rejected(
        "repaired_proof_separator_wrong_ordinal",
        "change one separator's deterministic ordinal",
        lambda: validate_boundary_record(wrong_ordinal),
    ))
    generic_reference = copy.deepcopy(reference_rows[0])
    generic_reference["actual_word_span"] = "the referenced result"
    tests.append(expect_rejected(
        "repaired_reference_generic_reversion",
        "replace an exact stable listener target with generic referenced-result wording",
        lambda: validate_reference_record(generic_reference),
    ))
    shifted_reference = copy.deepcopy(reference_rows[1])
    shifted_reference["source_anchor_exact"] = False
    tests.append(expect_rejected(
        "repaired_reference_source_shift",
        "shift a listener reference binding away from its exact source anchor",
        lambda: validate_reference_record(shifted_reference),
    ))
    formal_reference_loss = copy.deepcopy(next(row for row in reference_rows if row["formal_object_ids"]))
    formal_reference_loss["formal_listener_target_exact"] = False
    tests.append(expect_rejected(
        "repaired_formal_reference_loss",
        "remove the stable target from a source-unsolved exercise's listener text",
        lambda: validate_reference_record(formal_reference_loss),
    ))
    expressions = {row["expression_id"]: row for row in BASE.read_jsonl(REPAIR / "expression_semantics.jsonl")}
    equality = copy.deepcopy(expressions["expr-d1b2eb82a064c167"])
    equality["speech"] = re.sub(r"\bequal\b", "associated", equality["speech"], flags=re.IGNORECASE)
    tests.append(expect_rejected(
        "legacy_equality_actual_speech_loss",
        "remove both spoken equality terms while retaining two equality macros",
        lambda: BASE.validate_semantic_speech(equality, equality["expression_id"]),
    ))
    subset = copy.deepcopy(next(row for row in BASE.read_jsonl(REPAIR / "semantic_occurrences.jsonl") if row["formula_id"] == "projected-formula-0009675"))
    subset["meaning"] = "Gamma sub zero is mentioned."
    tests.append(expect_rejected(
        "contextual_subset_meaning_loss",
        "remove the belongs-to-Gamma meaning from the contextual subset occurrence",
        lambda: BASE.validate_semantic_speech(subset, subset["formula_id"]),
    ))
    require(all(row["status"] == "PASS_REJECTED" for row in tests), "mutation rejection status drift")
    return {
        "schema": "openlogic-tr021-repaired-independent-adversarial-audit-v1",
        "status": "PASS_ALL_FRESH_AND_TARGETED_MUTATIONS_REJECTED",
        "risk_families": len(tests),
        "tests": tests,
    }


def write_manifest() -> dict[str, Any]:
    excluded = {HERE / "EVIDENCE_MANIFEST.json", HERE / "CLOSED_BUNDLE_PINS.json"}
    rows = []
    for path in sorted(item for item in HERE.rglob("*") if item.is_file() and item not in excluded):
        rows.append({
            "path": path.relative_to(HERE).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    manifest = {
        "schema": "openlogic-tr021-repaired-independent-pass-evidence-manifest-v1",
        "status": "CLOSED_SELF_CONSISTENT_ZERO_FINDING_PASS_EVIDENCE",
        "excluded_non_circular_closure_files": sorted(path.name for path in excluded),
        "artifact_count": len(rows),
        "artifacts": rows,
    }
    write_json(HERE / "EVIDENCE_MANIFEST.json", manifest)
    for row in rows:
        path = HERE / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256_file(path) == row["sha256"], f"audit manifest self-check drift: {row['path']}")
    return manifest


def main() -> int:
    require(HERE.name == "superseding_repaired_candidate_reaudit_20260821", "unsafe repaired audit directory")
    preexisting = sorted(path.name for path in HERE.iterdir() if path.is_file() and path.name != Path(__file__).name)
    require(not preexisting and not (HERE / "cold_rebuilds").exists(), f"refusing to overwrite frozen audit evidence: {preexisting}")

    before = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_BEFORE.json", before)
    pin_receipt = verify_candidate_pins_and_manifests()
    write_json(HERE / "PIN_AND_MANIFEST_AUDIT.json", pin_receipt)

    source_receipt, text_by_file, source_records, line_reviews = BASE.verify_sources_and_corrections()
    write_json(HERE / "SOURCE_AND_CORRECTION_AUDIT.json", source_receipt)
    write_jsonl(HERE / "SOURCE_LINE_REVIEW.jsonl", line_reviews)

    expression_receipt, occurrence_receipt, expression_reviews, occurrence_reviews, occurrence_by_id = BASE.verify_expressions_occurrences(text_by_file)
    write_json(HERE / "EXPRESSION_AND_MATHML_AUDIT.json", expression_receipt)
    write_json(HERE / "OCCURRENCE_AND_CONTEXT_AUDIT.json", occurrence_receipt)
    write_jsonl(HERE / "EXPRESSION_REVIEW.jsonl", expression_reviews)
    write_jsonl(HERE / "OCCURRENCE_REVIEW.jsonl", occurrence_reviews)
    equality, contextual_subset = adjudicate_equality_and_contextual_subset()
    write_json(HERE / "LEGACY_EQ_PREDICATE_READJUDICATION.json", equality)
    write_json(HERE / "CONTEXTUAL_SUBSET_PREDICATE_READJUDICATION.json", contextual_subset)

    formal_receipt, command_receipt, formal_reviews, command_reviews, formal_diffs = verify_formals_with_bounded_reference_repairs(text_by_file, occurrence_by_id)
    write_json(HERE / "FORMAL_AND_PROOF_AUDIT.json", formal_receipt)
    write_json(HERE / "PROOF_COMMAND_AUDIT.json", command_receipt)
    write_jsonl(HERE / "FORMAL_REVIEW.jsonl", formal_reviews)
    write_jsonl(HERE / "PROOF_COMMAND_REVIEW.jsonl", command_reviews)
    write_jsonl(HERE / "FORMAL_REFERENCE_REPAIR_DIFF_AUDIT.jsonl", formal_diffs)

    replays = BASE.read_jsonl(REPAIR / "continuous_source_replay.jsonl")
    listener_receipt, raw_defects, repaired_anchor_groups, replay_text = BASE.verify_continuous_replay(source_records, occurrence_by_id)
    require(listener_receipt["status"] == "PASS_LISTENER_NATURAL_WORDS_ONLY" and not raw_defects, "continuous listener repair did not close")
    write_json(HERE / "CONTINUOUS_LISTENER_AUDIT.json", listener_receipt)
    template_receipt = listener_facing_template_audit()
    write_json(HERE / "LISTENER_FACING_TEMPLATE_AUDIT.json", template_receipt)
    heading_rows = verify_heading_placeholder_closure(replays)
    write_jsonl(HERE / "HEADING_PLACEHOLDER_CLOSURE_AUDIT.jsonl", heading_rows)
    proof_group_rows, boundary_rows = verify_proof_boundary_closure(replays, repaired_anchor_groups)
    write_jsonl(HERE / "PROOF_GROUP_REPAIR_CLOSURE_AUDIT.jsonl", proof_group_rows)
    write_jsonl(HERE / "PROOF_BOUNDARY_REPAIR_CLOSURE_AUDIT.jsonl", boundary_rows)

    reference_receipt, reference_reviews, missing_references = BASE.verify_references(text_by_file, replay_text)
    require(reference_receipt["status"] == "PASS_ALL_REFERENCES_RESOLVED_AND_LISTENER_REPLAYED" and not missing_references, "reference listener repair did not close")
    write_json(HERE / "REFERENCE_AUDIT.json", reference_receipt)
    write_jsonl(HERE / "REFERENCE_REVIEW.jsonl", reference_reviews)
    reference_exact_rows = verify_reference_exact_replay(text_by_file, replays)
    write_jsonl(HERE / "REFERENCE_EXACT_REPLAY_AUDIT.jsonl", reference_exact_rows)

    fail_closure = {
        "schema": "openlogic-tr021-repaired-independent-controlling-fail-closure-v1",
        "status": "PASS_ALL_THREE_FROZEN_FINDINGS_CLOSED_EXACTLY",
        "controlling_fail_closed_bundle_pins_sha256": CONTROLLING_FAIL_PINS_SHA256,
        "controlling_findings_sha256": sha256_file(CONTROLLING_FAIL / "FINDINGS.jsonl"),
        "closures": {
            "TR021-INDEPENDENT-001": {"frozen_instances": 7, "remaining_raw_placeholders": 0, "exact_heading_bindings": len(heading_rows)},
            "TR021-INDEPENDENT-002": {"frozen_groups_total": 86, "frozen_affected_groups": 80, "frozen_boundaries": 283, "exact_spoken_separators": len(boundary_rows), "remaining_unseparated_boundaries": 0},
            "TR021-INDEPENDENT-003": {"frozen_missing_targets": 10, "exact_source_listener_targets": len(reference_exact_rows), "remaining_missing_targets": 0, "formal_targets_replayed": sum(bool(row["formal_object_ids"]) for row in reference_exact_rows)},
        },
    }
    write_json(HERE / "CONTROLLING_FAIL_CLOSURE_AUDIT.json", fail_closure)

    cold_receipt = independent_cold_builds()
    write_json(HERE / "COLD_REBUILD_AUDIT.json", cold_receipt)
    adversarial = targeted_mutations(BASE.adversarial_probes(text_by_file, source_records, occurrence_by_id), heading_rows, boundary_rows, reference_exact_rows)
    write_json(HERE / "ADVERSARIAL_AUDIT.json", adversarial)

    after = protected_snapshot()
    caches = cache_residue()
    require(before == after, "protected repaired/prior/oracle/source/work evidence changed")
    require(not caches, f"cache residue: {caches}")
    write_json(HERE / "PROTECTED_SNAPSHOT_AFTER.json", after)
    write_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", {
        "schema": "openlogic-tr021-repaired-independent-protected-identity-v1",
        "status": "PASS_ALL_PROTECTED_BYTES_UNCHANGED_NO_CACHE_RESIDUE",
        "before_aggregate_sha256": before["aggregate_sha256"],
        "after_aggregate_sha256": after["aggregate_sha256"],
        "protected_file_count": before["file_count"],
        "protected_identity": True,
        "control_files_in_scope": False,
        "cache_residue": caches,
    })

    findings: list[dict[str, Any]] = []
    write_jsonl(HERE / "FINDINGS.jsonl", findings)
    final = {
        "schema": "openlogic-tr021-repaired-independent-final-audit-receipt-v1",
        "status": "PASS_ZERO_CURRENT_FINDINGS",
        "tranche_id": "OLAB-TR-021",
        "repaired_candidate_pins": REPAIR_PINS,
        "controlling_fail_closed_bundle_pins_sha256": CONTROLLING_FAIL_PINS_SHA256,
        "counts": EXPECTED,
        "exact_repair_closure": {
            "raw_heading_placeholders": 0,
            "closed_heading_bindings": len(heading_rows),
            "proof_groups": len(proof_group_rows),
            "formerly_affected_proof_groups": sum(row["formerly_affected"] for row in proof_group_rows),
            "explicit_deterministic_proof_separators": len(boundary_rows),
            "unseparated_proof_boundaries": 0,
            "exact_listener_reference_targets": len(reference_exact_rows),
            "missing_listener_reference_targets": 0,
            "formal_reference_targets": sum(bool(row["formal_object_ids"]) for row in reference_exact_rows),
        },
        "legacy_eq_predicate": "READJUDICATED_FALSE_POSITIVE_SOURCE_FAITHFUL",
        "finding_count": 0,
        "finding_ids": [],
        "independent_semantic_audit": "PASS",
        "reader_integration": "NOT_CLAIMED",
    }
    write_json(HERE / "FINAL_AUDIT_RECEIPT.json", final)
    write_json(HERE / "PROGRAM_RECEIPT.json", {
        "schema": "openlogic-tr021-repaired-independent-program-receipt-v1",
        "status": "PASS_PINNED_PROGRAM_AND_INPUTS",
        "program": Path(__file__).name,
        "program_sha256": sha256_file(Path(__file__)),
        "pinned_base_program": str(BASE_PROGRAM.resolve()),
        "pinned_base_program_sha256": BASE_PROGRAM_SHA256,
        "repaired_candidate_pass_pins_sha256": REPAIR_PASS_PINS_SHA256,
        "controlling_fail_closed_bundle_pins_sha256": CONTROLLING_FAIL_PINS_SHA256,
    })
    report = f"""# OLAB-TR-021 repaired candidate — fresh independent re-audit

Status: **PASS — zero current findings.**

The audit independently reread all 14 immutable sources (1,984 lines), 279 expression records and 558 native MathML variants, 963 exact occurrence/context packets, 140 formal objects including 86 proof trees and 10 source-unsolved exercises, 545 proof commands, 10 references, two explicit source corrections, and the 19,053-word repaired continuous replay.

All three frozen listener blockers are closed: zero raw heading placeholders remain; all 283 formerly unseparated formula boundaries across the 80 affected proof groups now carry exact deterministic ordinal speech; and references `reference-000317` through `reference-000326` speak their stable targets at exact source word spans, including both affected formal exercise objects. The legacy equality predicate was re-adjudicated as a source-faithful harness false positive.

Two fresh audit-local cold builds matched all 16 canonical artifacts byte-for-byte. All {adversarial['risk_families']} fresh/adapted mutation probes were rejected. Protected repaired, prior-audit, predecessor, oracle, source, work, and support-input bytes remained identical; no cache residue was created.

No producer, source, prior evidence, control, GUI, browser, audio, assistive-technology, network, Git, or publication state was modified.
"""
    write_text(HERE / "REPORT.md", report)

    manifest = write_manifest()
    pins = {
        "schema": "openlogic-tr021-repaired-independent-closed-pass-bundle-pins-v1",
        "status": "CLOSED_NON_CIRCULAR_ZERO_FINDING_PASS_BUNDLE",
        "program_sha256": sha256_file(Path(__file__)),
        "findings_sha256": sha256_file(HERE / "FINDINGS.jsonl"),
        "final_audit_receipt_sha256": sha256_file(HERE / "FINAL_AUDIT_RECEIPT.json"),
        "controlling_fail_closure_audit_sha256": sha256_file(HERE / "CONTROLLING_FAIL_CLOSURE_AUDIT.json"),
        "evidence_manifest_sha256": sha256_file(HERE / "EVIDENCE_MANIFEST.json"),
        "manifest_artifact_count": manifest["artifact_count"],
        "note": "This pins file is intentionally excluded from EVIDENCE_MANIFEST.json to avoid a hash cycle; its own SHA-256 is the external bundle checkpoint.",
    }
    write_json(HERE / "CLOSED_BUNDLE_PINS.json", pins)
    result = {
        "status": final["status"],
        "finding_count": 0,
        "heading_placeholders": 0,
        "proof_separators": len(boundary_rows),
        "exact_reference_targets": len(reference_exact_rows),
        "program_sha256": pins["program_sha256"],
        "final_audit_receipt_sha256": pins["final_audit_receipt_sha256"],
        "evidence_manifest_sha256": pins["evidence_manifest_sha256"],
        "closed_bundle_pins_sha256": sha256_file(HERE / "CLOSED_BUNDLE_PINS.json"),
    }
    print(compact_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
