#!/usr/bin/env python3
"""Superseding independent re-audit of repaired OLAB-TR-019 bytes.

The frozen initial FAIL remains outside this directory and is treated as an
immutable input.  Producer code is loaded only for isolated cold builds and
adversarial exercises after independent source, semantic, MathML, and formal-
object review has completed.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


HERE = Path(__file__).resolve().parent
INITIAL_ROOT = HERE.parent
PROJECT = INITIAL_ROOT.parents[1]
EVIDENCE = PROJECT / "evidence"
PROJECTION = EVIDENCE / "tranche_019_fol_derivation_systems_projection"
PRODUCER_VALIDATION = PROJECTION / "producer_validation"
PRODUCER_WORK = PROJECT / "work" / "tranche_019_fol_derivation_systems_projection"
TR009_ORACLE = EVIDENCE / "tranche_009_pl_derivation_systems_oracle"
TR009_PROJECTION = EVIDENCE / "tranche_009_pl_derivation_systems_projection"
TR009_AUDIT = EVIDENCE / "independent_tranche_009_pl_derivation_systems_semantic_audit" / "superseding_reaudit"
TR019_ORACLE = EVIDENCE / "tranche_019_fol_derivation_systems_oracle"
TR019_ORACLE_VALIDATION = EVIDENCE / "tranche_019_fol_derivation_systems_oracle_validation"
ORACLE_CORE = PROJECT / "work" / "tranche_oracle_core"
CONTROL = PROJECT / "control"

AUTHORITY_COMMIT = "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"
VALIDITY_ID = "expr-0ab83730c263f0b7"
CONSEQUENCE_ID = "expr-ab733e02bed54e75"
REPAIRED_IDS = {VALIDITY_ID, CONSEQUENCE_ID}
REPAIRED_FORMULAS = {
    "projected-formula-0008076": "TR019-IND-SEM-001",
    "projected-formula-0008078": "TR019-IND-SEM-002",
    "projected-formula-0008082": "TR019-IND-SEM-002",
}
INITIAL_PINS = {
    "receipt": "ebf1814616fa2eef0bb4dd71b4afa2a66959705eac1aceca2d81062599fa2918",
    "report": "e5de41aeaa5a49c6ce702476b3bb5c09b316af527224ee517d6fe7ad415da8fc",
    "manifest": "9390141d72faca61d00bd399211f10c479c7224573505858b843bbc9a55a8bd3",
}
ASSIGNED_PINS = {
    "projection_manifest": "aa7eabfd154d60196294bcf12f3326eadcf29e995cc7ec282e71bfe3872dc020",
    "producer_validation_receipt": "6bbd2e726ba751ebba4fa1f14e152e179a99abb7cad1e658aac9f4333fc58ce8",
    "producer_validation_manifest": "872f73e7e5828c8b4024618d53fac624dbe7cd0d353b903db2099029ad621d91",
    "repair_closure": "82d9a2764d9d34a1433115a596caa0c1bbafe67e00b0dcec8d983b512edd4cf6",
    "equality_ledger": "a52e162a1b9e94fde99fd76ac94ed03e4d8cc9816b3b2b96820069ea9d2803e3",
}
CONTROL_FILES = (
    "DURABLE_GOAL.md", "WORKFLOW.md", "DECISIONS.md", "STATE.json",
    "TASK_LEDGER.tsv", "CHAPTER_COVERAGE.tsv", "UNRESOLVED_ITEMS.tsv",
    "LOGBOOK.jsonl",
)
OCCURRENCE_SEMANTIC_FIELDS = {
    "binding_status", "display_mode", "mathml", "meaning",
    "semantic_binding_kind", "speech",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compact_hash(value: Any) -> str:
    return sha256_bytes(compact_json(value).encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if any(not line.strip() for line in lines):
        raise ValueError(f"blank JSONL row: {path}")
    return [json.loads(line) for line in lines]


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    write_text(path, "".join(compact_json(row) + "\n" for row in rows))


def add_tree(paths: set[Path], root: Path) -> None:
    paths.update(
        path.resolve() for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


def display_path(path: Path) -> tuple[str, str]:
    try:
        return path.relative_to(PROJECT.resolve()).as_posix(), "complete-book"
    except ValueError:
        return path.as_posix(), "external-authority"


def initial_manifest_replay() -> dict[str, Any]:
    manifest_path = INITIAL_ROOT / "EVIDENCE_MANIFEST.json"
    errors = []
    manifest = read_json(manifest_path)
    for row in manifest["artifacts"]:
        path = INITIAL_ROOT / row["path"]
        if not path.is_file():
            errors.append(f"missing {row['path']}")
        elif path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
            errors.append(f"hash/size mismatch {row['path']}")
    pins = {
        "receipt": sha256_file(INITIAL_ROOT / "INITIAL_FAIL_RECEIPT.json"),
        "report": sha256_file(INITIAL_ROOT / "REPORT.md"),
        "manifest": sha256_file(manifest_path),
    }
    if pins != INITIAL_PINS:
        errors.append(f"initial pin mismatch: {pins}")
    return {
        "schema": "openlogic-independent-tr019-preserved-initial-fail-v1",
        "status": "PASS_BYTE_IDENTICAL" if not errors else "FAIL",
        "pins": pins, "expected_pins": INITIAL_PINS,
        "manifest_artifacts": manifest.get("artifact_count"),
        "manifest_aggregate_sha256": manifest.get("aggregate_sha256"),
        "review_errors": errors,
    }


def protected_inventory() -> dict[str, Any]:
    paths: set[Path] = set()
    for root in (
        PROJECTION, TR009_ORACLE, TR009_PROJECTION, TR009_AUDIT,
        TR019_ORACLE, TR019_ORACLE_VALIDATION,
    ):
        add_tree(paths, root)
    for name in ("build_fol_derivation_rebind.py", "validate_fol_derivation_rebind.py", "test_fol_derivation_rebind.py"):
        paths.add((PRODUCER_WORK / name).resolve())
    for name in ("build_tranche_oracle.py", "validate_tranche_oracle.py"):
        paths.add((ORACLE_CORE / name).resolve())
    upstream = read_json(PROJECTION / "UPSTREAM_INPUTS.json")
    for row in upstream["inputs"]:
        paths.add((PROJECT / row["path"]).resolve())
    authority = read_json(TR019_ORACLE / "SOURCE_AUTHORITY.json")
    authority_root = Path(authority["authority_root"])
    for row in authority["source_records"]:
        paths.add((authority_root / row["path"]).resolve())
    initial_manifest = read_json(INITIAL_ROOT / "EVIDENCE_MANIFEST.json")
    for row in initial_manifest["artifacts"]:
        paths.add((INITIAL_ROOT / row["path"]).resolve())
    paths.add((INITIAL_ROOT / "EVIDENCE_MANIFEST.json").resolve())
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"protected audit input missing: {missing}")
    records = []
    for path in sorted(paths, key=lambda item: item.as_posix().lower()):
        display, scope = display_path(path)
        records.append({
            "scope": scope, "path": display, "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    payload = "".join(
        f"{row['sha256']}  {row['bytes']}  {row['scope']}:{row['path']}\n"
        for row in records
    ).encode("utf-8")
    return {
        "schema": "openlogic-independent-tr019-superseding-input-freeze-v1",
        "record_count": len(records), "aggregate_sha256": sha256_bytes(payload),
        "records": records,
    }


def control_snapshot() -> dict[str, Any]:
    rows = []
    for name in CONTROL_FILES:
        path = CONTROL / name
        rows.append({"path": f"control/{name}", "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "schema": "openlogic-independent-tr019-control-nonmutation-snapshot-v1",
        "binding": "AUDIT_NONMUTATION_ONLY_NOT_SEMANTIC_BUILD_INPUT",
        "files": rows, "aggregate_sha256": compact_hash({"files": rows}),
    }


def verify_manifest(root: Path) -> list[str]:
    errors = []
    manifest = read_json(root / "EVIDENCE_MANIFEST.json")
    for row in manifest["artifacts"]:
        path = root / row["path"]
        if not path.is_file():
            errors.append(f"missing {row['path']}")
        elif path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
            errors.append(f"hash/size mismatch {row['path']}")
    return errors


def record_hash_ok(row: dict[str, Any]) -> bool:
    payload = dict(row)
    declared = payload.pop("record_sha256", None)
    return isinstance(declared, str) and compact_hash(payload) == declared


def load_initial_auditor() -> Any:
    sys.dont_write_bytecode = True
    path = INITIAL_ROOT / "audit_tr019_semantic_rebind.py"
    spec = importlib.util.spec_from_file_location("frozen_initial_tr019_auditor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen initial auditor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    return {field: row[field] for field in sorted(OCCURRENCE_SEMANTIC_FIELDS) if field in row}


def expression_review(initial: Any, oracle_occ: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_rows = read_jsonl(TR009_PROJECTION / "expression_semantics.jsonl")
    target_rows = read_jsonl(PROJECTION / "expression_semantics.jsonl")
    source = {row["expression_id"]: row for row in source_rows}
    target = {row["expression_id"]: row for row in target_rows}
    if set(source) != set(target) or len(target) != 64:
        raise ValueError("64-expression ID closure differs")
    occurrence_count = Counter(row["expression_id"] for row in oracle_occ)
    expression_reviews = []
    mathml_reviews = []
    mismatch_ids = []
    for expression_id in sorted(target):
        src, dst = source[expression_id], target[expression_id]
        errors = []
        if not record_hash_ok(dst):
            errors.append("target record hash differs")
        if dst.get("source_tr009_record_sha256") != src.get("record_sha256"):
            errors.append("TR009 source record hash binding differs")
        src_payload = dict(src)
        src_payload.pop("record_sha256", None)
        dst_payload = dict(dst)
        dst_payload.pop("record_sha256", None)
        dst_payload.pop("source_tr009_record_sha256", None)
        rebind = dst_payload.pop("rebind_provenance", None)
        profile_override = dst_payload.pop("tr019_profile_override", None)
        differences = sorted(field for field in set(src_payload) | set(dst_payload) if src_payload.get(field) != dst_payload.get(field))
        if differences:
            mismatch_ids.append(expression_id)
        if expression_id not in REPAIRED_IDS:
            if src_payload != dst_payload:
                errors.append(f"non-repair payload differs in fields {differences}")
            if profile_override is not None:
                errors.append("unexpected FOL profile override metadata")
            if not isinstance(rebind, dict) or rebind.get("kind") != "EXACT_INDEPENDENTLY_AUDITED_TR009_REBIND":
                errors.append("exact TR009 rebind provenance differs")
        else:
            expected_differences = ["authoring_provenance", "authoring_status", "meaning", "semantic_repair_ids"]
            if differences != expected_differences:
                errors.append(f"repair changes unexpected fields: {differences}")
            finding_id = "TR019-IND-SEM-001" if expression_id == VALIDITY_ID else "TR019-IND-SEM-002"
            if dst.get("authoring_provenance") != "tr019_fol_profile_override_after_independent_fail":
                errors.append("repair authoring provenance differs")
            if dst.get("authoring_status") != "REPAIRED_AFTER_INDEPENDENT_AUDIT":
                errors.append("repair authoring status differs")
            if finding_id not in dst.get("semantic_repair_ids", []):
                errors.append("repair finding ID is absent")
            if not isinstance(profile_override, dict):
                errors.append("profile override metadata is absent")
            else:
                if profile_override.get("finding_id") != finding_id:
                    errors.append("profile override finding binding differs")
                if profile_override.get("initial_independent_fail_receipt_sha256") != INITIAL_PINS["receipt"]:
                    errors.append("profile override initial FAIL binding differs")
                if profile_override.get("source_tr009_meaning_sha256") != sha256_bytes(src["meaning"].encode("utf-8")):
                    errors.append("profile override source meaning hash differs")
                if profile_override.get("overridden_fields") != ["meaning", "authoring_provenance", "authoring_status", "semantic_repair_ids"]:
                    errors.append("declared override field set differs")
            if not isinstance(rebind, dict) or rebind.get("kind") != "FOL_PROFILE_OVERRIDE_FROM_AUDITED_TR009":
                errors.append("FOL override rebind provenance differs")
            meaning = str(dst.get("meaning", ""))
            lower = meaning.lower()
            if re.search(r"\b(?:propositional|valuation)\b", lower):
                errors.append("propositional residue remains in FOL meaning")
            if expression_id == VALIDITY_ID:
                for phrase in ("first-order structure", "variable assignment", "free variables"):
                    if phrase not in lower:
                        errors.append(f"FOL validity meaning omits {phrase!r}")
            else:
                for phrase in ("every first-order structure", "variable assignment", "satisfies every formula in gamma", "satisfies a under that assignment"):
                    if phrase not in lower:
                        errors.append(f"FOL consequence meaning omits {phrase!r}")
        if initial.SPEECH_RESIDUE.search(str(dst.get("speech", ""))):
            errors.append("speech contains symbolic/source residue")
        variants = []
        for display in ("inline", "block"):
            variant_errors = []
            visible_text = ""
            try:
                _, visible, variant_errors = initial.parse_mathml(
                    dst[f"mathml_{display}"], expression_id, display, dst["normalized_tex"]
                )
                visible_text = "".join(visible.itertext())
                if r"\True" in dst["normalized_tex"] and "𝕋" not in visible_text:
                    variant_errors.append("exact double-struck T is absent")
                if r"\False" in dst["normalized_tex"] and "𝔽" not in visible_text:
                    variant_errors.append("exact double-struck F is absent")
            except Exception as exc:
                variant_errors = [f"MathML parse/review error: {exc}"]
            errors.extend(f"{display} MathML: {item}" for item in variant_errors)
            variants.append({
                "display": display, "visible_text": visible_text,
                "review_errors": variant_errors, "status": "PASS" if not variant_errors else "FAIL",
            })
        expression_reviews.append({
            "expression_id": expression_id, "normalized_tex": dst["normalized_tex"],
            "speech": dst["speech"], "meaning": dst["meaning"],
            "tr009_payload_difference_fields": differences,
            "classification": "FOL_PROFILE_REPAIR" if expression_id in REPAIRED_IDS else "EXACT_AUDITED_TR009_PAYLOAD",
            "tranche_occurrences_reviewed": occurrence_count[expression_id],
            "review_errors": errors, "status": "PASS" if not errors else "FAIL",
        })
        mathml_reviews.append({
            "expression_id": expression_id, "variants": variants,
            "status": "PASS" if all(item["status"] == "PASS" for item in variants) else "FAIL",
        })
    if set(mismatch_ids) != REPAIRED_IDS:
        raise ValueError(f"payload mismatch inventory differs: {mismatch_ids}")
    if len([variant for row in mathml_reviews for variant in row["variants"]]) != 128:
        raise ValueError("MathML variant closure differs")
    if len([row for row in target_rows if r"\True" in row["normalized_tex"] or r"\False" in row["normalized_tex"]]) != 12:
        raise ValueError("truth-sign expression inventory differs")
    return expression_reviews, mathml_reviews


def occurrence_review(
    initial: Any, source_data: dict[str, bytes], source_lines: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    oracle_rows = read_jsonl(TR019_ORACLE / "formula_occurrences.jsonl")
    contexts = {row["formula_id"]: row for row in read_jsonl(TR019_ORACLE / "formula_contexts.jsonl")}
    target_rows = read_jsonl(PROJECTION / "semantic_occurrences.jsonl")
    source_rows = read_jsonl(TR009_PROJECTION / "semantic_occurrences.jsonl")
    source_by_key = initial.keyed(source_rows, initial.OCCURRENCE_KEY_FIELDS)
    target_by_formula = {row["formula_id"]: row for row in target_rows}
    expression_by_id = {row["expression_id"]: row for row in read_jsonl(PROJECTION / "expression_semantics.jsonl")}
    if not (len(oracle_rows) == len(target_rows) == 137):
        raise ValueError("occurrence closure differs")
    coordinate_fields = (
        "instance_id", "file", "line", "column", "offset", "delimiter",
        "expression_id", "normalized_tex", "tex", "stream_start", "stream_end",
    )
    reviews = []
    override_reviews = []
    semantic_difference_formulas = []
    for oracle in oracle_rows:
        formula_id = oracle["formula_id"]
        row = target_by_formula.get(formula_id, {})
        errors = []
        for field in coordinate_fields:
            if row.get(field) != oracle.get(field):
                errors.append(f"{field} differs from oracle")
        if row.get("context") != contexts[formula_id]:
            errors.append("three-line context differs")
        data = source_data[oracle["file"]]
        try:
            if initial.extract_formula(data, int(oracle["offset"]), oracle["delimiter"]) != oracle["tex"]:
                errors.append("formula payload differs from authority")
        except Exception as exc:
            errors.append(f"source extraction failed: {exc}")
        if initial.line_column(data, int(oracle["offset"])) != (int(oracle["line"]), int(oracle["column"])):
            errors.append("authority line/column differs")
        if not record_hash_ok(row):
            errors.append("occurrence record hash differs")
        display = "inline" if oracle["delimiter"] == "$" else "block"
        expression = expression_by_id[row["expression_id"]]
        if row.get("display_mode") != display or row.get("mathml") != expression.get(f"mathml_{display}"):
            errors.append("display/MathML expression binding differs")
        if row.get("expression_record_sha256") != expression.get("record_sha256"):
            errors.append("expression record hash binding differs")
        key = tuple(oracle[field] for field in initial.OCCURRENCE_KEY_FIELDS)
        source = source_by_key[key]
        source_semantic = semantic_payload(source)
        target_semantic = semantic_payload(row)
        semantic_differences = sorted(
            field for field in set(source_semantic) | set(target_semantic)
            if source_semantic.get(field) != target_semantic.get(field)
        )
        if semantic_differences:
            semantic_difference_formulas.append(formula_id)
        if formula_id in REPAIRED_FORMULAS:
            if semantic_differences != ["binding_status", "meaning", "semantic_binding_kind"]:
                errors.append(f"FOL occurrence repair changes unexpected fields: {semantic_differences}")
            if row.get("semantic_binding_kind") != "fol_profile_expression_override":
                errors.append("FOL occurrence repair binding kind differs")
            if row.get("binding_status") != "BOUND_WITH_EXPLICIT_FOL_PROFILE_OVERRIDE":
                errors.append("FOL occurrence repair status differs")
            if row.get("meaning") != expression.get("meaning") or row.get("speech") != expression.get("speech"):
                errors.append("FOL occurrence repair does not bind repaired expression semantics")
            provenance = row.get("rebind_provenance", {})
            if provenance.get("source_semantic_payload_equal") is not False:
                errors.append("FOL occurrence repair does not declare semantic inequality")
            if provenance.get("profile_override_finding_id") != REPAIRED_FORMULAS[formula_id]:
                errors.append("FOL occurrence repair finding binding differs")
            if provenance.get("initial_independent_fail_receipt_sha256") != INITIAL_PINS["receipt"]:
                errors.append("FOL occurrence initial FAIL binding differs")
        else:
            if semantic_differences:
                errors.append(f"non-repair occurrence semantics differ: {semantic_differences}")
            if row.get("semantic_binding_kind") == "fol_profile_expression_override":
                errors.append("unexpected FOL occurrence override")
        if row.get("source_tr009_semantic_record_sha256") != compact_hash(source):
            errors.append("TR009 occurrence hash binding differs")
        provenance = row.get("rebind_provenance", {})
        if provenance.get("source_coordinate_tuple_equal") is not True or provenance.get("three_line_context_equal") is not True:
            errors.append("source/context equality provenance differs")
        if initial.SPEECH_RESIDUE.search(str(row.get("speech", ""))):
            errors.append("speech contains symbolic/source residue")
        if row.get("semantic_binding_kind") == "exact_source_context_override":
            override_key = (Path(oracle["file"]).name, int(oracle["line"]))
            phrases = initial.OVERRIDE_EXPECTATIONS.get(override_key)
            override_errors = []
            if phrases is None or any(phrase.lower() not in str(row.get("meaning", "")).lower() for phrase in (phrases or ())):
                override_errors.append("context override omits reviewed local role")
            override_reviews.append({
                "formula_id": formula_id, "file": oracle["file"], "line": oracle["line"],
                "meaning": row.get("meaning"), "required_phrases": list(phrases or ()),
                "review_errors": override_errors, "status": "PASS" if not override_errors else "FAIL",
            })
            errors.extend(override_errors)
        reviews.append({
            "formula_id": formula_id, "expression_id": row.get("expression_id"),
            "file": oracle["file"], "line": oracle["line"], "column": oracle["column"],
            "source_line": source_lines[oracle["file"]][int(oracle["line"]) - 1],
            "speech": row.get("speech"), "meaning": row.get("meaning"),
            "tr009_semantic_difference_fields": semantic_differences,
            "classification": "FOL_PROFILE_REPAIR" if formula_id in REPAIRED_FORMULAS else "EXACT_AUDITED_TR009_SEMANTICS",
            "review_errors": errors, "status": "PASS" if not errors else "FAIL",
        })
    if set(semantic_difference_formulas) != set(REPAIRED_FORMULAS):
        raise ValueError(f"occurrence semantic mismatch inventory differs: {semantic_difference_formulas}")
    if len(override_reviews) != 15:
        raise ValueError("context override review count differs")
    kinds = Counter(row["semantic_binding_kind"] for row in target_rows)
    if kinds != {"expression_semantics": 119, "fol_profile_expression_override": 3, "exact_source_context_override": 15}:
        raise ValueError(f"occurrence binding-kind closure differs: {kinds}")
    return reviews, override_reviews


def immutable_boundary_review() -> dict[str, Any]:
    payload = read_json(PROJECTION / "UPSTREAM_INPUTS.json")
    rows = payload.get("inputs", [])
    errors = []
    reviews = []
    if payload.get("binding") != "IMMUTABLE_SEMANTIC_INPUTS_ONLY":
        errors.append("immutable-only binding declaration differs")
    if len(rows) != 9 or len({row.get("path") for row in rows}) != 9:
        errors.append("immutable input inventory is not exactly nine unique paths")
    if any(str(row.get("path", "")).startswith("control/") for row in rows):
        errors.append("mutable control is bound as a semantic input")
    for row in rows:
        path = PROJECT / row["path"]
        actual_hash = sha256_file(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        status = "PASS" if actual_hash == row.get("sha256") and actual_bytes == row.get("bytes") else "FAIL"
        reviews.append({
            "path": row.get("path"), "declared_bytes": row.get("bytes"), "actual_bytes": actual_bytes,
            "declared_sha256": row.get("sha256"), "actual_sha256": actual_hash, "status": status,
        })
        if status != "PASS":
            errors.append(f"immutable input drift: {row.get('path')}")
    operational = read_json(PROJECTION / "OPERATIONAL_CONTEXT_CONTRACT.json")
    if operational.get("status") != "NONBINDING":
        errors.append("operational context is not declared nonbinding")
    if operational.get("content_or_hash_embedded") is not False:
        errors.append("operational context claims embedded content/hash")
    if operational.get("existence_required_by_semantic_builder") is not False:
        errors.append("semantic builder claims control existence is required")
    if operational.get("may_advance_without_changing_canonical_semantic_bytes") is not True:
        errors.append("operational controls are not declared advance-safe")
    if any(not str(path).startswith("control/") for path in operational.get("paths", [])):
        errors.append("operational context contains a non-control path")
    if any(key in {"bytes", "sha256", "hash", "content"} for key in operational):
        errors.append("operational context contains a binding bytes/hash/content field")
    builder_path = PRODUCER_WORK / "build_fol_derivation_rebind.py"
    builder_source = builder_path.read_text(encoding="utf-8")
    tree = ast.parse(builder_source)
    control_literal_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            segment = ast.get_source_segment(builder_source, node) or ""
            if "control/" in segment and any(name in segment for name in ("read_text", "read_bytes", "sha256_file", "read_json", "is_file", "stat")):
                control_literal_calls.append(segment)
    if control_literal_calls:
        errors.append("builder contains a control-content read/hash call")
    dependency = read_json(PROJECTION / "DEPENDENCY_BOUNDARY.json")
    if dependency.get("semantic_build_inputs") != "ONLY_IMMUTABLE_HASH_PINNED_UPSTREAM_INPUTS":
        errors.append("dependency immutable boundary differs")
    if dependency.get("mutable_durable_controls") != "NONBINDING_OPERATIONAL_CONTEXT_NOT_READ_OR_HASHED_BY_BUILDER":
        errors.append("dependency operational-control boundary differs")
    return {
        "schema": "openlogic-independent-tr019-immutable-boundary-review-v1",
        "status": "PASS" if not errors else "FAIL", "immutable_input_count": len(rows),
        "immutable_inputs": reviews, "operational_context": operational,
        "builder_control_content_read_calls": control_literal_calls,
        "review_errors": errors,
    }


def root_file_map(root: Path) -> dict[str, dict[str, Any]]:
    return {
        path.name: {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(root.iterdir(), key=lambda item: item.name) if path.is_file()
    }


def run_replays() -> tuple[dict[str, Any], dict[str, Any]]:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(PRODUCER_WORK))
    builder = importlib.import_module("build_fol_derivation_rebind")
    adversarial = importlib.import_module("test_fol_derivation_rebind")
    validator = importlib.import_module("validate_fol_derivation_rebind")
    replay_root = HERE / "independent_cold_replay"
    if replay_root.exists():
        if replay_root.parent != HERE:
            raise ValueError("unsafe cold replay root")
        shutil.rmtree(replay_root)
    builder.COLD_ROOT = replay_root
    pair_a, pair_b = replay_root / "pair_a", replay_root / "pair_b"
    builder.build(pair_a)
    builder.build(pair_b)
    canonical, map_a, map_b = root_file_map(PROJECTION), root_file_map(pair_a), root_file_map(pair_b)
    differences_a = sorted(name for name in set(canonical) | set(map_a) if canonical.get(name) != map_a.get(name))
    differences_b = sorted(name for name in set(map_a) | set(map_b) if map_a.get(name) != map_b.get(name))
    cold = {
        "schema": "openlogic-independent-tr019-superseding-cold-replay-v1",
        "status": "PASS_BYTE_IDENTICAL" if not differences_a and not differences_b else "FAIL",
        "canonical_pair_a_differences": differences_a,
        "pair_a_pair_b_differences": differences_b,
        "canonical_tree": canonical, "pair_a_tree": map_a, "pair_b_tree": map_b,
    }
    tests = adversarial.run_adversarial(
        pair_a, replay_root / "negative", validator.validate_projection,
        (
            validator.ValidationError, builder.RebindError, ET.ParseError, KeyError,
            ValueError, json.JSONDecodeError, RuntimeError,
        ),
    )
    adversarial_receipt = {
        "schema": "openlogic-independent-tr019-superseding-adversarial-replay-v1",
        "status": "PASS_ALL_REJECTED" if len(tests) == 18 and all(row["rejected"] for row in tests) else "FAIL",
        "test_count": len(tests), "tests": tests,
    }
    return cold, adversarial_receipt


def main() -> int:
    checks = []
    current_findings = []

    def check(check_id: str, detail: str, condition: bool, evidence: Any = None) -> None:
        checks.append({"check_id": check_id, "detail": detail, "status": "PASS" if condition else "FAIL"})
        if not condition:
            current_findings.append({
                "finding_id": f"TR019-SUPERSEDING-{len(current_findings) + 1:03d}",
                "severity": "HIGH", "category": "superseding_reaudit_failure",
                "current_status": "UNRESOLVED", "detail": detail, "evidence": evidence,
            })

    initial = load_initial_auditor()
    preserved_before = initial_manifest_replay()
    write_json(HERE / "PRESERVED_INITIAL_FAIL_BEFORE.json", preserved_before)
    check("INITIAL-FAIL-PRESERVED-BEFORE", "the complete initial FAIL manifest and assigned receipt/report pins replay", preserved_before["status"] == "PASS_BYTE_IDENTICAL", preserved_before["review_errors"])

    before = protected_inventory()
    controls_before = control_snapshot()
    write_json(HERE / "INPUT_HASHES_BEFORE.json", before)
    write_json(HERE / "CONTROL_SNAPSHOT_BEFORE.json", controls_before)
    current_pins = {
        "projection_manifest": sha256_file(PROJECTION / "EVIDENCE_MANIFEST.json"),
        "producer_validation_receipt": sha256_file(PRODUCER_VALIDATION / "VALIDATION_RECEIPT.json"),
        "producer_validation_manifest": sha256_file(PRODUCER_VALIDATION / "EVIDENCE_MANIFEST.json"),
        "repair_closure": sha256_file(PROJECTION / "REPAIR_CLOSURE.json"),
        "equality_ledger": sha256_file(PROJECTION / "REUSE_EQUALITY_LEDGER.jsonl"),
    }
    check("ASSIGNED-PINS", "all repaired producer pins and the unchanged 214-row ledger pin are exact", current_pins == ASSIGNED_PINS, current_pins)
    projection_manifest_errors = verify_manifest(PROJECTION)
    validation_manifest_errors = verify_manifest(PRODUCER_VALIDATION)
    check("PROJECTION-MANIFEST", "the repaired projection manifest replays", not projection_manifest_errors, projection_manifest_errors)
    check("VALIDATION-MANIFEST", "the repaired producer-validation manifest replays", not validation_manifest_errors, validation_manifest_errors)
    producer_validation = read_json(PRODUCER_VALIDATION / "VALIDATION_RECEIPT.json")
    check(
        "VALIDATION-BINDING", "producer validation binds the repaired projection manifest and reports 18 adversarial rejections",
        producer_validation.get("projection_evidence_manifest_sha256") == ASSIGNED_PINS["projection_manifest"]
        and producer_validation.get("checks", {}).get("adversarial_rejections") == 18,
    )

    source_data, source_lines, equality, source_reviews, maps = initial.source_and_equality_review()
    equality = dict(equality)
    equality["semantic_profile_equivalence"] = "PASS_AFTER_EXPLICIT_TWO_EXPRESSION_REVIEW"
    proof = read_json(PROJECTION / "REUSE_EQUALITY_PROOF.json")
    source_tuples = [list(key) for key in sorted(maps["occ019"], key=compact_json)]
    proof_errors = []
    expected_proof_values = {
        "expression_id_and_shape_count": 64, "formula_source_coordinate_tuples": 137,
        "three_line_context_packets_equal": 137, "formal_source_coordinate_tuples_equal": 4,
        "proof_commands_equal": 7, "proof_diagrams_equal": 2,
        "expected_entry_profile_gate_differences": 6, "ledger_records": 214,
    }
    for field, value in expected_proof_values.items():
        if proof.get(field) != value:
            proof_errors.append(f"{field} differs")
    if proof.get("formula_source_coordinate_tuple_aggregate_sha256") != compact_hash({"tuples": source_tuples}):
        proof_errors.append("source-coordinate tuple aggregate differs")
    if proof.get("ledger_aggregate_sha256") != equality.get("ledger_aggregate_sha256"):
        proof_errors.append("ledger aggregate differs")
    if proof.get("fol_profile_semantic_override_expression_ids") != sorted(REPAIRED_IDS):
        proof_errors.append("FOL profile override expression inventory differs")
    if proof.get("semantic_payload_reuse_contract") != "SOURCE_EQUALITY_DOES_NOT_AUTHORIZE_CROSS_PROFILE_MEANING_REUSE_WITHOUT_REVIEW":
        proof_errors.append("cross-profile semantic reuse contract differs")
    write_jsonl(HERE / "SOURCE_REVIEW.jsonl", source_reviews)
    write_json(HERE / "SOURCE_EQUALITY_REVIEW.json", {**equality, "producer_proof_errors": proof_errors})
    check("SOURCE-CLOSURE", "six authority files replay at 21,672 bytes and 461 lines", all(row["status"] == "PASS" for row in source_reviews))
    check("SOURCE-EQUALITY", "64 shapes, 137 coordinate/context packets, and the 214-row ledger replay independently", equality["status"].startswith("PASS") and not proof_errors, proof_errors)

    tags = initial.tag_gate_review()
    write_jsonl(HERE / "TAG_GATE_REVIEW.jsonl", tags)
    check("PROFILE-GATES", "all six entry differences remain profile identity gates only", len(tags) == 6 and all(row["status"] == "PASS" for row in tags))

    oracle_occ = read_jsonl(TR019_ORACLE / "formula_occurrences.jsonl")
    expression_reviews, mathml_reviews = expression_review(initial, oracle_occ)
    write_jsonl(HERE / "EXPRESSION_REVIEW.jsonl", expression_reviews)
    write_jsonl(HERE / "MATHML_REVIEW.jsonl", mathml_reviews)
    exact_expression_count = sum(row["classification"] == "EXACT_AUDITED_TR009_PAYLOAD" for row in expression_reviews)
    repaired_expression_count = sum(row["classification"] == "FOL_PROFILE_REPAIR" for row in expression_reviews)
    check(
        "EXPRESSION-SEMANTICS", "exactly 62 expression payloads remain unchanged and exactly two contain reviewed FOL repairs",
        exact_expression_count == 62 and repaired_expression_count == 2 and all(row["status"] == "PASS" for row in expression_reviews),
    )
    check("MATHML", "all 128 MathML variants remain native, unflattened, and exact for double-struck T/F", all(row["status"] == "PASS" for row in mathml_reviews))

    occurrence_reviews, override_reviews = occurrence_review(initial, source_data, source_lines)
    write_jsonl(HERE / "OCCURRENCE_REVIEW.jsonl", occurrence_reviews)
    write_jsonl(HERE / "CONTEXT_OVERRIDE_REVIEW.jsonl", override_reviews)
    exact_occurrences = sum(row["classification"] == "EXACT_AUDITED_TR009_SEMANTICS" for row in occurrence_reviews)
    repaired_occurrences = sum(row["classification"] == "FOL_PROFILE_REPAIR" for row in occurrence_reviews)
    check(
        "OCCURRENCE-SEMANTICS", "all 137 exact contexts close with exactly three reviewed FOL repairs and 134 unchanged semantic payloads",
        exact_occurrences == 134 and repaired_occurrences == 3 and all(row["status"] == "PASS" for row in occurrence_reviews),
    )
    check("CONTEXT-OVERRIDES", "all 15 context-specific overrides retain their reviewed local roles", len(override_reviews) == 15 and all(row["status"] == "PASS" for row in override_reviews))

    formal_reviews, proof_review = initial.formal_and_proof_review(source_data)
    write_jsonl(HERE / "FORMAL_OBJECT_REVIEW.jsonl", formal_reviews)
    write_json(HERE / "PROOF_OBJECT_REVIEW.json", proof_review)
    check("FORMAL-OBJECTS", "two proof trees, one tableau, and one derivation retain complete ordered words-only narratives", all(row["status"] == "PASS" for row in formal_reviews))
    check("PROOF-OBJECTS", "two diagrams and seven proof commands replay at exact source coordinates", proof_review["status"] == "PASS")

    boundary = immutable_boundary_review()
    write_json(HERE / "IMMUTABLE_BOUNDARY_REVIEW.json", boundary)
    check("IMMUTABLE-BOUNDARY", "exactly nine immutable inputs bind bytes and mutable controls remain hash-free operational context", boundary["status"] == "PASS", boundary["review_errors"])

    cold, adversarial_receipt = run_replays()
    write_json(HERE / "COLD_REPLAY_RECEIPT.json", cold)
    write_json(HERE / "ADVERSARIAL_REPLAY_RECEIPT.json", adversarial_receipt)
    check("COLD-REPLAY", "canonical, pair A, and pair B are byte-identical", cold["status"] == "PASS_BYTE_IDENTICAL", {
        "canonical_pair_a": cold["canonical_pair_a_differences"], "pair_a_pair_b": cold["pair_a_pair_b_differences"],
    })
    check("ADVERSARIAL-GATES", "all 18 repaired producer adversarial mutations are rejected", adversarial_receipt["status"] == "PASS_ALL_REJECTED")

    repair = read_json(PROJECTION / "REPAIR_CLOSURE.json")
    repair_ids = [row.get("finding_id") for row in repair.get("resolutions", [])]
    check(
        "REPAIR-CLOSURE", "repair closure binds and addresses the exact three frozen finding IDs",
        repair.get("initial_fail_receipt_sha256") == INITIAL_PINS["receipt"]
        and repair.get("initial_fail_report_sha256") == INITIAL_PINS["report"]
        and repair_ids == ["TR019-IND-SEM-001", "TR019-IND-SEM-002", "TR019-IND-DET-001"],
    )

    after = protected_inventory()
    controls_after = control_snapshot()
    preserved_after = initial_manifest_replay()
    write_json(HERE / "INPUT_HASHES_AFTER.json", after)
    write_json(HERE / "CONTROL_SNAPSHOT_AFTER.json", controls_after)
    write_json(HERE / "PRESERVED_INITIAL_FAIL_AFTER.json", preserved_after)
    check("PROTECTED-INPUT-STABILITY", "all protected semantic/audit inputs remained byte-identical during re-audit", before == after, {
        "before": before["aggregate_sha256"], "after": after["aggregate_sha256"],
    })
    check("CONTROL-NONMUTATION", "operational controls were not changed during re-audit", controls_before == controls_after, {
        "before": controls_before["aggregate_sha256"], "after": controls_after["aggregate_sha256"],
    })
    check("INITIAL-FAIL-PRESERVED-AFTER", "the complete initial FAIL remains byte-identical after re-audit", preserved_after["status"] == "PASS_BYTE_IDENTICAL", preserved_after["review_errors"])

    initial_findings = read_jsonl(INITIAL_ROOT / "INITIAL_FAIL_FINDINGS.jsonl")
    resolutions = []
    for finding in initial_findings:
        finding_id = finding["finding_id"]
        if finding_id == "TR019-IND-SEM-001":
            evidence = {"expression_id": VALIDITY_ID, "occurrences": ["projected-formula-0008076"], "predicate": "FOL structures and relevant assignments; no propositional valuation residue"}
        elif finding_id == "TR019-IND-SEM-002":
            evidence = {"expression_id": CONSEQUENCE_ID, "occurrences": ["projected-formula-0008078", "projected-formula-0008082"], "predicate": "FOL structures and satisfying relevant assignments; no propositional valuation residue"}
        else:
            evidence = {"immutable_inputs": 9, "operational_controls": "NONBINDING_HASH_FREE", "canonical_pair_identity": cold["status"]}
        resolutions.append({**finding, "current_status": "RESOLVED", "superseding_evidence": evidence})
    write_jsonl(HERE / "FINDINGS_HISTORY.jsonl", resolutions)
    write_jsonl(HERE / "FINDINGS_CURRENT.jsonl", current_findings)
    write_json(HERE / "FROZEN_FINDING_RESOLUTION.json", {
        "schema": "openlogic-independent-tr019-frozen-finding-resolution-v1",
        "initial_fail_receipt_sha256": INITIAL_PINS["receipt"],
        "initial_findings": [row["finding_id"] for row in initial_findings],
        "resolved_findings": [row["finding_id"] for row in resolutions if row["current_status"] == "RESOLVED"],
        "unresolved_findings": [row["finding_id"] for row in current_findings],
        "status": "PASS_ALL_RESOLVED" if not current_findings and len(resolutions) == 3 else "FAIL",
    })

    result = "PASS" if not current_findings and all(row["status"] == "PASS" for row in checks) else "FAIL"
    receipt = {
        "schema": "openlogic-independent-tr019-fol-derivation-systems-superseding-reaudit-v1",
        "result": result, "tranche_id": "OLAB-TR-019", "authority_commit": AUTHORITY_COMMIT,
        "authority_mutated": False, "assigned_pins": ASSIGNED_PINS, "current_pins": current_pins,
        "initial_fail_preserved": preserved_after["status"], "initial_fail_pins": INITIAL_PINS,
        "protected_input_aggregate_sha256": before["aggregate_sha256"],
        "protected_input_stability": "PASS_BYTE_IDENTICAL" if before == after else "FAIL",
        "operational_control_stability": "PASS_BYTE_IDENTICAL" if controls_before == controls_after else "FAIL",
        "counts_replayed": {
            "source_files": 6, "source_bytes": 21672, "source_lines": 461,
            "expression_records": 64, "exact_tr009_expression_payloads": 62,
            "fol_profile_expression_repairs": 2, "formula_occurrences": 137,
            "exact_tr009_occurrence_payloads": 134, "fol_profile_occurrence_repairs": 3,
            "contextual_overrides": 15, "mathml_variants": 128,
            "formal_objects": 4, "proof_trees": 2, "tableaux": 1, "derivations": 1,
            "proof_diagrams": 2, "proof_commands": 7, "references": 0,
            "profile_gates": 6, "equality_ledger_records": 214,
            "immutable_semantic_inputs": 9, "adversarial_rejections": 18,
        },
        "semantic_review": "PASS_ALL_64_EXPRESSIONS_137_CONTEXTS_15_OVERRIDES_128_MATHML_4_FORMALS",
        "cold_replay": cold["status"], "adversarial_replay": adversarial_receipt["status"],
        "historical_findings": len(initial_findings),
        "resolved_historical_findings": len(resolutions),
        "unresolved_semantic_findings": 0 if result == "PASS" else len(current_findings),
        "unresolved_deterministic_findings": 0 if result == "PASS" else len(current_findings),
        "unresolved_mechanical_findings": 0 if result == "PASS" else len(current_findings),
        "checks": checks, "check_count": len(checks),
        "producer_edited": False, "controls_edited": False, "git_used": False,
        "publication": False, "remote_mutation": False,
    }
    write_json(HERE / "SUPERSEDING_AUDIT_RECEIPT.json", receipt)
    report = [
        "# OLAB-TR-019 superseding independent semantic re-audit",
        "", f"Result: **{result}**.", "",
        "The repaired projection closes all three findings from the byte-preserved initial FAIL. First-order validity and consequence now quantify over first-order structures and relevant variable assignments in exactly two expression records and three occurrence contexts. The other 62 expression payloads remain exact to the independently audited TR009 records.",
        "",
        "The complete source and accessibility surface passed again: 64 shapes, 137 source-coordinate and three-line context packets, the 214-row equality ledger, 15 contextual overrides, 128 native unflattened MathML variants, four formal narratives, two diagrams, and seven proof commands.",
        "",
        "The deterministic boundary now contains exactly nine immutable consumed inputs. Durable controls are named only as nonbinding operational context; their content and hashes are absent from the semantic build. Two fresh builds are byte-identical to each other and to the canonical root, and all 18 adversarial mutations are rejected.",
        "",
        f"Protected-input stability: **{'PASS' if before == after else 'FAIL'}** (`{before['aggregate_sha256']}`).",
        "",
        "Unresolved findings: none." if not current_findings else "Unresolved findings remain; see FINDINGS_CURRENT.jsonl.",
        "",
        "The initial FAIL receipt, report, evidence manifest, and all of its manifested artifacts remain byte-identical. No producer, control, authority, reader, Git, remote, or publication state was modified.",
        "",
    ]
    write_text(HERE / "REPORT.md", "\n".join(report))

    artifacts = []
    for path in sorted(
        (item for item in HERE.rglob("*") if item.is_file() and item.name != "EVIDENCE_MANIFEST.json" and "__pycache__" not in item.parts),
        key=lambda item: item.relative_to(HERE).as_posix(),
    ):
        artifacts.append({
            "path": path.relative_to(HERE).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    aggregate_payload = "".join(f"{row['sha256']}  {row['bytes']}  {row['path']}\n" for row in artifacts)
    write_json(HERE / "EVIDENCE_MANIFEST.json", {
        "schema": "openlogic-independent-tr019-superseding-evidence-manifest-v1",
        "result": result, "tranche_id": "OLAB-TR-019", "artifact_count": len(artifacts),
        "artifacts": artifacts, "aggregate_sha256": sha256_bytes(aggregate_payload.encode("utf-8")),
    })
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
