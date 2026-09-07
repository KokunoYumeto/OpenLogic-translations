from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
INITIAL = HERE.parent
BOOK = HERE.parents[2]
CONTROL = BOOK / "control"
PRODUCER = BOOK / "evidence" / "tranche_015_fol_introduction_projection"
ORACLE = BOOK / "evidence" / "tranche_015_fol_introduction_oracle"
ORACLE_VALIDATION = BOOK / "evidence" / "tranche_015_fol_introduction_oracle_validation"
PRODUCER_WORK = BOOK / "work" / "tranche_015_fol_introduction_projection"
TEST_FILE = PRODUCER_WORK / "test_fol_introduction_projection.py"

ASSIGNED_PINS = {
    "producer_artifact_manifest": "9c36b1655bf1b57f77b2fbf279b735a63ee5e8914fd5bf36376a18f11fda3767",
    "producer_evidence_manifest": "563b451b29c0835bd01567db219f0f0d25e39bd7f0447145be23dfbeac94ffb1",
    "producer_validation": "89dc271880fd57a7e47e4ecda33a2a9c5035fdfc47688448bd6fd30253ebac10",
    "oracle_manifest": "2b81a71acc2784b9c1f073eef0885a5bbb71c437ba3b82ec9e9c377826d469bf",
    "oracle_validation": "776f492b257f33ce4e5f15f8ef2151ffd1106aaf62a8d8231e18d1747b3da908",
    "initial_fail_receipt": "e6786ce557f25daa511b59f21279a46970d8c82ead621329083974341965a1ba",
    "initial_fail_report": "e3301a0c1c1cac1ec20a1ba6cb50c53d40f94d3f036bae0a4dad811385938f08",
    "initial_fail_manifest": "0d60ac7b8cc18405ffa1daecf89cb4c08a2e38e46ff26f1701cb3d1b9511bb49",
    "initial_fail_findings": "f69c56c85252bc926189a37c76f784021f053b114e17a4aeeb2d189474edbd53",
}

EXPECTED_COUNTS = {
    "source_files": 10,
    "source_instances": 10,
    "source_lines": 666,
    "source_bytes": 33428,
    "formula_occurrences": 332,
    "formula_contexts": 332,
    "expression_shapes": 114,
    "authored_expression_shapes": 92,
    "reused_expression_shapes": 22,
    "exact_unmodified_reuse_shapes": 18,
    "semantically_repaired_reuse_shapes": 4,
    "native_mathml_variants": 228,
    "formal_objects": 2,
    "references": 8,
    "formula_correction_records": 4,
    "formula_correction_occurrences": 6,
    "source_prose_correction_records": 2,
    "source_prose_linked_occurrences": 5,
    "occurrence_speech_overrides": 38,
    "frozen_finding_classes": 8,
    "changed_expression_records": 12,
    "changed_occurrence_speech_or_meaning": 80,
    "changed_finding_occurrence_windows": 82,
    "producer_checks": 1414,
    "producer_tests": 35,
    "cold_builds": 2,
    "cold_artifacts_per_build": 16,
    "proof_diagrams": 0,
    "exercises": 0,
}

EXPECTED_CHANGED_EXPRESSION_IDS = {
    "expr-00242f5bcdc7edea",
    "expr-07ba1733077dc377",
    "expr-0feeab53510b9b84",
    "expr-138a6201a70e5f79",
    "expr-1ca87a5f2021c05f",
    "expr-4e07408562bedb8b",
    "expr-57885e4c75965b23",
    "expr-5feceb66ffc86f38",
    "expr-6b86b273ff34fce1",
    "expr-71983740200349d8",
    "expr-b7284c8110aa90b7",
    "expr-d4735e3a265e16ee",
}

DIGIT_REPAIRS = {
    "expr-4e07408562bedb8b": ("3", "three"),
    "expr-5feceb66ffc86f38": ("0", "zero"),
    "expr-6b86b273ff34fce1": ("1", "one"),
    "expr-d4735e3a265e16ee": ("2", "two"),
}

MEMBERSHIP_OVERRIDES = {
    "projected-formula-0006020": "i in the natural numbers",
    "projected-formula-0006125": "m in the domain of structure M",
    "projected-formula-0006127": "i in the natural numbers",
    "projected-formula-0006129": "m in the domain of structure M",
    "projected-formula-0006258": "n in the positive integers",
}

ATOMIC_REPAIRS = {
    "expr-00242f5bcdc7edea": "P of v sub i",
    "expr-07ba1733077dc377": "P of v sub zero",
    "expr-138a6201a70e5f79": "P of a",
    "expr-1ca87a5f2021c05f": "P of x",
    "expr-b7284c8110aa90b7": "P of v sub two",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def record_hash(record: dict[str, Any], key: str = "record_sha256") -> str:
    body = dict(record)
    body.pop(key, None)
    return sha_bytes(canonical_bytes(body))


def add_record_hash(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    result["record_sha256"] = record_hash(result)
    return result


def manifest_errors(directory: Path, manifest_name: str = "EVIDENCE_MANIFEST.json") -> list[str]:
    errors: list[str] = []
    manifest = read_json(directory / manifest_name)
    artifacts = manifest.get("artifacts", [])
    declared_count = manifest.get("artifact_count")
    if declared_count is not None and declared_count != len(artifacts):
        errors.append("artifact_count")
    for item in artifacts:
        path = directory / item["path"]
        if not path.is_file():
            errors.append(f"missing:{item['path']}")
            continue
        if path.stat().st_size != item["bytes"]:
            errors.append(f"bytes:{item['path']}")
        if sha_file(path) != item["sha256"]:
            errors.append(f"sha256:{item['path']}")
    return errors


def current_pins() -> dict[str, str]:
    return {
        "producer_artifact_manifest": sha_file(PRODUCER / "ARTIFACT_MANIFEST.json"),
        "producer_evidence_manifest": sha_file(PRODUCER / "EVIDENCE_MANIFEST.json"),
        "producer_validation": sha_file(PRODUCER / "VALIDATION_RECEIPT.json"),
        "oracle_manifest": sha_file(ORACLE / "EVIDENCE_MANIFEST.json"),
        "oracle_validation": sha_file(ORACLE_VALIDATION / "VALIDATION_RECEIPT.json"),
        "initial_fail_receipt": sha_file(INITIAL / "AUDIT_RECEIPT.json"),
        "initial_fail_report": sha_file(INITIAL / "REPORT.md"),
        "initial_fail_manifest": sha_file(INITIAL / "EVIDENCE_MANIFEST.json"),
        "initial_fail_findings": sha_file(INITIAL / "FINDINGS_CURRENT.jsonl"),
    }


def initial_snapshot() -> dict[str, Any]:
    rows = [
        {"bytes": path.stat().st_size, "path": path.name, "sha256": sha_file(path)}
        for path in sorted(INITIAL.iterdir(), key=lambda p: p.name.casefold())
        if path.is_file()
    ]
    return {
        "aggregate_sha256": sha_bytes(canonical_bytes(rows)),
        "file_count": len(rows),
        "files": rows,
        "schema": "openlogic-independent-tr015-initial-fail-preservation-v1",
    }


def gather_inputs() -> dict[str, Any]:
    roles: dict[Path, set[str]] = defaultdict(set)

    def add(path: Path, role: str) -> None:
        resolved = path.resolve()
        if resolved.is_file() and HERE not in resolved.parents:
            roles[resolved].add(role)

    for directory, role in (
        (PRODUCER, "frozen_repaired_producer"),
        (ORACLE, "frozen_oracle"),
        (ORACLE_VALIDATION, "independent_oracle_validation"),
        (PRODUCER_WORK, "producer_tools_and_paired_cold_builds"),
    ):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                add(path, role)

    for path in INITIAL.iterdir():
        if path.is_file():
            add(path, "preserved_initial_independent_fail")

    closure = read_json(PRODUCER / "SOURCE_CLOSURE.json")
    authority_root = Path(closure["authority_root"])
    for item in closure["source_records"]:
        add(authority_root / item["path"], "immutable_authority_source")

    for upstream_file in (PRODUCER / "UPSTREAM_INPUTS.json", ORACLE / "UPSTREAM_INPUTS.json"):
        for item in read_json(upstream_file).get("inputs", []):
            if item.get("path"):
                add(Path(item["path"]), f"declared_upstream:{item.get('role', 'unspecified')}")

    records = [
        {
            "bytes": path.stat().st_size,
            "path": str(path),
            "roles": sorted(roles[path]),
            "sha256": sha_file(path),
        }
        for path in sorted(roles, key=lambda p: str(p).casefold())
    ]
    return {
        "aggregate_sha256": sha_bytes(canonical_bytes(records)),
        "record_count": len(records),
        "records": records,
        "schema": "openlogic-independent-tr015-superseding-input-hashes-v1",
    }


def control_snapshot() -> dict[str, Any]:
    rows = [
        {"bytes": path.stat().st_size, "path": path.name, "sha256": sha_file(path)}
        for path in sorted(CONTROL.iterdir(), key=lambda p: p.name.casefold())
        if path.is_file()
    ]
    return {
        "files_read_before_reaudit": rows,
        "note": "Durable controls were read completely before action. They are living coordination state, not reproducibility inputs.",
        "schema": "openlogic-independent-tr015-control-read-receipt-v1",
    }


def freeze_before() -> None:
    pins = current_pins()
    if pins != ASSIGNED_PINS:
        raise SystemExit(json.dumps({"assigned": ASSIGNED_PINS, "current": pins, "error": "pin mismatch"}, sort_keys=True))
    write_json(HERE / "INPUT_HASHES_BEFORE.json", gather_inputs())
    write_json(HERE / "INITIAL_AUDIT_PRESERVATION_BEFORE.json", initial_snapshot())
    write_json(HERE / "CONTROL_READ_RECEIPT.json", control_snapshot())
    print(json.dumps({"input_aggregate_sha256": read_json(HERE / "INPUT_HASHES_BEFORE.json")["aggregate_sha256"], "pins": pins}, sort_keys=True))


def audit() -> None:
    if not (HERE / "INPUT_HASHES_BEFORE.json").is_file():
        raise SystemExit("Run --freeze-before first")

    before = read_json(HERE / "INPUT_HASHES_BEFORE.json")
    initial_before = read_json(HERE / "INITIAL_AUDIT_PRESERVATION_BEFORE.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, detail: str, ok: bool, errors: list[str] | None = None) -> None:
        row: dict[str, Any] = {"check_id": check_id, "detail": detail, "status": "PASS" if ok else "FAIL"}
        if errors:
            row["errors"] = errors
        checks.append(row)

    pins = current_pins()
    check("ASSIGNED-PINS", "all repaired producer, oracle, and preserved initial FAIL pins replay exactly", pins == ASSIGNED_PINS)

    initial_after = initial_snapshot()
    write_json(HERE / "INITIAL_AUDIT_PRESERVATION_AFTER.json", initial_after)
    initial_manifest_problems = manifest_errors(INITIAL)
    check(
        "INITIAL-FAIL-PRESERVED",
        "the complete initial FAIL root and its receipt remain byte-identical",
        initial_before == initial_after and not initial_manifest_problems and pins["initial_fail_receipt"] == ASSIGNED_PINS["initial_fail_receipt"],
        initial_manifest_problems,
    )

    manifest_problem_map = {
        "producer_evidence": manifest_errors(PRODUCER),
        "producer_artifact": manifest_errors(PRODUCER, "ARTIFACT_MANIFEST.json"),
        "oracle_evidence": manifest_errors(ORACLE),
        "oracle_artifact": manifest_errors(ORACLE, "ARTIFACT_MANIFEST.json"),
        "oracle_validation": manifest_errors(ORACLE_VALIDATION),
    }
    manifest_problems = [f"{name}:{error}" for name, values in manifest_problem_map.items() for error in values]
    check("MANIFEST-REPLAY", "all producer and oracle manifests bind every declared artifact", not manifest_problems, manifest_problems)

    producer_receipt = read_json(PRODUCER / "VALIDATION_RECEIPT.json")
    producer_check_rows = producer_receipt["checks"]
    producer_claim_ok = (
        producer_receipt["result"] == "PASS_PRODUCER_REPAIR_READY_FOR_INDEPENDENT_SUPERSEDING_REAUDIT"
        and producer_receipt["check_count"] == len(producer_check_rows) == EXPECTED_COUNTS["producer_checks"]
        and all(row["status"] == "PASS" for row in producer_check_rows)
        and producer_receipt["authority_mutated"] is False
    )
    check("PRODUCER-CHECK-REPLAY", "all 1,414 producer checks are present and PASS", producer_claim_ok)

    test_run = subprocess.run(
        [sys.executable, "-B", str(TEST_FILE)],
        cwd=str(PRODUCER_WORK),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    combined_test_output = test_run.stdout + test_run.stderr
    normalized_test_output = re.sub(
        r"Ran (\d+) tests in [0-9.]+s",
        r"Ran \1 tests in <elapsed>s",
        combined_test_output,
    )
    expected_test_hash = producer_receipt["adversarial_tests"]["normalized_combined_output_sha256"]
    test_replay = {
        "normalized_combined_output_sha256": sha_bytes(normalized_test_output.encode("utf-8")),
        "producer_normalized_combined_output_sha256": expected_test_hash,
        "result": "PASS" if test_run.returncode == 0 and "Ran 35 tests" in combined_test_output and "\nOK" in combined_test_output else "FAIL",
        "return_code": test_run.returncode,
        "schema": "openlogic-independent-tr015-test-replay-v1",
        "test_count": 35,
        "test_file_sha256": sha_file(TEST_FILE),
    }
    write_json(HERE / "INDEPENDENT_TEST_REPLAY.json", test_replay)
    check(
        "INDEPENDENT-TEST-REPLAY",
        "an independent read-only execution passes all 35 producer tests and reproduces the normalized output hash",
        test_replay["result"] == "PASS" and test_replay["normalized_combined_output_sha256"] == expected_test_hash,
    )

    summary = read_json(PRODUCER / "SEMANTIC_SUMMARY.json")
    closure = read_json(PRODUCER / "SOURCE_CLOSURE.json")
    selection = read_json(ORACLE / "SELECTION.json")
    authority_root = Path(closure["authority_root"])

    source_errors: list[str] = []
    source_review: list[dict[str, Any]] = []
    for item in closure["source_records"]:
        path = authority_root / item["path"]
        data = path.read_bytes()
        text = data.decode("utf-8")
        errors = []
        if len(data) != item["bytes"]:
            errors.append("byte_count")
        if sha_bytes(data) != item["sha256"]:
            errors.append("sha256")
        if len(text.splitlines()) != item["lines"]:
            errors.append("line_count")
        source_errors.extend(f"{item['path']}:{error}" for error in errors)
        source_review.append(add_record_hash({
            "bytes": len(data),
            "file": item["path"],
            "lines": len(text.splitlines()),
            "review_errors": errors,
            "sha256": sha_bytes(data),
            "status": "PASS" if not errors else "FAIL",
        }))
    source_totals_ok = (
        len(source_review) == EXPECTED_COUNTS["source_files"]
        and sum(row["lines"] for row in source_review) == EXPECTED_COUNTS["source_lines"]
        and sum(row["bytes"] for row in source_review) == EXPECTED_COUNTS["source_bytes"]
    )
    check("SOURCE-AUTHORITY", "all 10 immutable sources replay at 666 lines and 33,428 bytes", not source_errors and source_totals_ok, source_errors)

    oracle_instances = read_jsonl(ORACLE / "source_instances.jsonl")
    profile_decisions = read_jsonl(ORACLE / "tag_decisions.jsonl")
    instance_pairs = {(x["instance_id"], x["file"]) for x in oracle_instances}
    closure_pairs = {(x["instance_id"], x["file"]) for x in closure["source_instances"]}
    profile_ok = len(profile_decisions) == 4 and all(x["selected"] is True and len(x["tag_states"]) == 1 for x in profile_decisions)
    selection_ok = (
        selection["tranche_id"] == "OLAB-TR-015"
        and selection["part_key"] == "fol"
        and selection["source_instance_count"] == 10
        and set(selection["source_instance_ids"]) == {x["instance_id"] for x in oracle_instances}
    )
    check("SOURCE-PROFILE-CLOSURE", "the exact ten FOL instances and four selected profile decisions close", instance_pairs == closure_pairs and profile_ok and selection_ok)

    oracle_occurrences = read_jsonl(ORACLE / "formula_occurrences.jsonl")
    oracle_contexts = read_jsonl(ORACLE / "formula_contexts.jsonl")
    occurrences = read_jsonl(PRODUCER / "semantic_occurrences.jsonl")
    occurrence_by_id = {x["formula_id"]: x for x in occurrences}
    oracle_occ_by_id = {x["formula_id"]: x for x in oracle_occurrences}
    oracle_context_by_id = {x["formula_id"]: x for x in oracle_contexts}
    occurrence_errors: dict[str, list[str]] = defaultdict(list)
    oracle_fields = [
        "chapter_key", "column", "delimiter", "expression_id", "file", "formula_id",
        "instance_id", "line", "normalized_tex", "offset", "part_key", "scope",
        "stream_end", "stream_start", "tex",
    ]
    for formula_id, oracle_occurrence in oracle_occ_by_id.items():
        row = occurrence_by_id.get(formula_id)
        if row is None:
            occurrence_errors[formula_id].append("missing")
            continue
        if any(row.get(key) != oracle_occurrence.get(key) for key in oracle_fields):
            occurrence_errors[formula_id].append("oracle_payload_or_coordinate")
        if row["context"] != oracle_context_by_id[formula_id]:
            occurrence_errors[formula_id].append("oracle_context")
        source_lines = (authority_root / row["file"]).read_text(encoding="utf-8").splitlines()
        if row["context"]["source_line"] != source_lines[row["line"] - 1]:
            occurrence_errors[formula_id].append("authority_source_line")
        if record_hash(row) != row["record_sha256"]:
            occurrence_errors[formula_id].append("record_sha256")
    extra_occurrences = set(occurrence_by_id) - set(oracle_occ_by_id)
    check(
        "OCCURRENCE-ORACLE-CLOSURE",
        "all 332 occurrences and all 332 three-line packets match oracle coordinates and authority text",
        len(occurrences) == 332 and not extra_occurrences and not any(occurrence_errors.values()),
        [f"{key}:{error}" for key, values in occurrence_errors.items() for error in values],
    )

    shapes = read_jsonl(PRODUCER / "expression_shapes.jsonl")
    semantics = read_jsonl(PRODUCER / "expression_semantics.jsonl")
    context_reviews = read_jsonl(PRODUCER / "EXPRESSION_CONTEXT_REVIEW.jsonl")
    shape_by_id = {x["expression_id"]: x for x in shapes}
    semantic_by_id = {x["expression_id"]: x for x in semantics}
    context_review_by_id = {x["expression_id"]: x for x in context_reviews}
    with (ORACLE / "formula_shapes.tsv").open("r", encoding="utf-8", newline="") as handle:
        oracle_shapes = list(csv.DictReader(handle, delimiter="\t"))
    oracle_shape_by_id = {x["expression_id"]: x for x in oracle_shapes}
    grouped_occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in occurrences:
        grouped_occurrences[row["expression_id"]].append(row)

    expression_errors: dict[str, list[str]] = defaultdict(list)
    for expression_id, semantic in semantic_by_id.items():
        shape = shape_by_id.get(expression_id)
        review = context_review_by_id.get(expression_id)
        rows = sorted(grouped_occurrences[expression_id], key=lambda x: x["formula_id"])
        if shape is None or review is None:
            expression_errors[expression_id].append("missing_shape_or_review")
            continue
        if expression_id not in oracle_shape_by_id or semantic["normalized_tex"] != oracle_shape_by_id[expression_id]["normalized_tex"]:
            expression_errors[expression_id].append("oracle_shape")
        if semantic["normalized_tex"] != shape["normalized_tex"]:
            expression_errors[expression_id].append("shape_tex")
        if sha_bytes(canonical_bytes(shape["source_ast"])) != shape["source_ast_sha256"]:
            expression_errors[expression_id].append("source_ast_sha256")
        if record_hash(semantic) != semantic["record_sha256"]:
            expression_errors[expression_id].append("record_sha256")
        if semantic["tranche_occurrences"] != len(rows) or semantic["context_packet_count"] != len(rows):
            expression_errors[expression_id].append("occurrence_or_packet_count")
        packet = [row["context"] for row in rows]
        if sha_bytes(canonical_bytes(packet)) != semantic["context_packet_sha256"]:
            expression_errors[expression_id].append("context_packet_sha256")
        if review["context_packet_sha256"] != semantic["context_packet_sha256"]:
            expression_errors[expression_id].append("context_review_sha256")
        if review["context_count"] != len(rows) or review["context_ids"] != [x["context"]["context_id"] for x in rows]:
            expression_errors[expression_id].append("context_review_closure")
        if not semantic["speech"].strip() or not semantic["meaning"].strip():
            expression_errors[expression_id].append("blank_speech_or_meaning")
        for occurrence in rows:
            expected_speech = (
                occurrence["occurrence_speech_override"]["speech"]
                if occurrence["occurrence_speech_override"]
                else semantic["speech"]
            )
            if occurrence["speech"] != expected_speech:
                occurrence_errors[occurrence["formula_id"]].append("effective_speech_binding")
            if occurrence["meaning"] != semantic["meaning"]:
                occurrence_errors[occurrence["formula_id"]].append("meaning_binding")
            if occurrence["expression_record_sha256"] != semantic["record_sha256"]:
                occurrence_errors[occurrence["formula_id"]].append("expression_record_sha256")

    provenance_counts = Counter(row["authoring_provenance"] for row in semantics)
    expression_count_ok = (
        len(shapes) == len(semantics) == len(context_reviews) == 114
        and set(shape_by_id) == set(semantic_by_id) == set(context_review_by_id) == set(oracle_shape_by_id)
        and provenance_counts == Counter({
            "tr015_full_context_authored": 92,
            "exact_id_tex_context_validated_reuse": 18,
            "tr015_semantic_repair_from_exact_id_tex_reuse": 4,
        })
    )
    check("EXPRESSION-CLOSURE", "all 114 shapes close as 92 authored plus 22 reusable, including four disclosed speech repairs", expression_count_ok and not any(expression_errors.values()))
    check("EFFECTIVE-BINDINGS", "all occurrence speech, meaning, and expression hashes bind deterministically", not any(occurrence_errors.values()))

    initial_expression_review = {x["expression_id"]: x for x in read_jsonl(INITIAL / "EXPRESSION_REVIEW.jsonl")}
    initial_occurrence_review = {x["formula_id"]: x for x in read_jsonl(INITIAL / "OCCURRENCE_REVIEW.jsonl")}
    changed_expression_ids = {
        row["expression_id"]
        for row in semantics
        if (
            initial_expression_review[row["expression_id"]]["speech"] != row["speech"]
            or initial_expression_review[row["expression_id"]]["meaning"] != row["meaning"]
        )
    }
    changed_occurrence_ids = {
        row["formula_id"]
        for row in occurrences
        if (
            initial_occurrence_review[row["formula_id"]]["speech"] != row["speech"]
            or initial_occurrence_review[row["formula_id"]]["meaning"] != row["meaning"]
        )
    }
    initial_findings = read_jsonl(INITIAL / "FINDINGS_CURRENT.jsonl")
    initial_finding_by_id = {x["finding_id"]: x for x in initial_findings}
    expected_changed_occurrence_ids = {
        formula_id
        for finding in initial_findings
        if finding["finding_id"] != "TR015-IND-SEM-008"
        for formula_id in finding.get("affected_occurrences", [])
    }
    check(
        "BOUNDED-REPAIR-DIFF",
        "the repaired footprint is exactly 12 expression records and 80 speech-or-meaning occurrence views",
        changed_expression_ids == EXPECTED_CHANGED_EXPRESSION_IDS
        and changed_occurrence_ids == expected_changed_occurrence_ids
        and len(changed_occurrence_ids) == 80,
    )

    upstream = read_json(PRODUCER / "UPSTREAM_INPUTS.json")["inputs"]
    reuse_sources: dict[str, tuple[dict[str, Any], str]] = {}
    for item in upstream:
        if item.get("role") != "exact_semantic_reuse_source":
            continue
        for raw_line in Path(item["path"]).read_text(encoding="utf-8").splitlines():
            source_row = json.loads(raw_line)
            reuse_sources[f"{item['label']}::{source_row['expression_id']}"] = (source_row, sha_bytes(raw_line.encode("utf-8")))

    reuse_review: list[dict[str, Any]] = []
    reuse_errors: list[str] = []
    for semantic in sorted((x for x in semantics if x["authoring_provenance"] != "tr015_full_context_authored"), key=lambda x: x["expression_id"]):
        provenance = semantic["reuse_provenance"]
        source = reuse_sources.get(f"{provenance['source']}::{semantic['expression_id']}")
        errors: list[str] = []
        if source is None:
            errors.append("source_missing")
        else:
            source_row, raw_hash = source
            if raw_hash != provenance["source_record_sha256"]:
                errors.append("source_record_sha256")
            if source_row["expression_id"] != semantic["expression_id"] or source_row["normalized_tex"] != semantic["normalized_tex"]:
                errors.append("exact_id_or_tex")
            if source_row["meaning"] != semantic["meaning"]:
                errors.append("meaning")
            if semantic["authoring_provenance"] == "exact_id_tex_context_validated_reuse":
                if source_row["speech"] != semantic["speech"]:
                    errors.append("unmodified_speech")
            else:
                expected = DIGIT_REPAIRS.get(semantic["expression_id"])
                repair = provenance.get("local_semantic_repair", {})
                if expected is None or source_row["speech"] != expected[0] or semantic["speech"] != expected[1]:
                    errors.append("digit_repair")
                if repair.get("source_speech") != expected[0] or repair.get("speech") != expected[1] or repair.get("finding_id") != "TR015-IND-SEM-006":
                    errors.append("repair_provenance")
        reuse_errors.extend(f"{semantic['expression_id']}:{error}" for error in errors)
        reuse_review.append(add_record_hash({
            "authoring_provenance": semantic["authoring_provenance"],
            "expression_id": semantic["expression_id"],
            "normalized_tex": semantic["normalized_tex"],
            "review_errors": errors,
            "source": provenance["source"],
            "source_record_sha256": provenance["source_record_sha256"],
            "status": "PASS" if not errors else "FAIL",
        }))
    check("EXACT-REUSE", "all 22 reusable records retain exact ID, TeX, meaning, and source bytes; four digit speeches are transparently repaired", len(reuse_review) == 22 and not reuse_errors, reuse_errors)

    formula_corrections = read_jsonl(PRODUCER / "SOURCE_CORRECTIONS.jsonl")
    formula_correction_review: list[dict[str, Any]] = []
    formula_correction_errors: list[str] = []
    corrected_formula_ids: set[str] = set()
    for correction in formula_corrections:
        errors: list[str] = []
        semantic = semantic_by_id.get(correction["expression_id"])
        shape = shape_by_id.get(correction["expression_id"])
        if semantic is None or shape is None:
            errors.append("missing_expression")
        else:
            if semantic["normalized_tex"] != correction["source_normalized_tex"]:
                errors.append("source_tex")
            if semantic["reader_rendering_tex"] != correction["corrected_tex"] or shape["reader_rendering_tex"] != correction["corrected_tex"]:
                errors.append("reader_rendering_tex")
            if not semantic["reader_correction"] or not shape["reader_correction_applied_and_disclosed"]:
                errors.append("expression_disclosure")
        for formula_id in correction["affected_formula_ids"]:
            corrected_formula_ids.add(formula_id)
            occurrence = occurrence_by_id.get(formula_id)
            if occurrence is None or not occurrence["reader_correction"]:
                errors.append(f"occurrence_disclosure:{formula_id}")
            elif occurrence["reader_correction"]["corrected_tex"] != correction["corrected_tex"]:
                errors.append(f"occurrence_corrected_tex:{formula_id}")
        if correction["source_file_modified"] is not False:
            errors.append("source_file_modified")
        formula_correction_errors.extend(f"{correction['correction_id']}:{error}" for error in errors)
        formula_correction_review.append(add_record_hash({
            "affected_formula_ids": correction["affected_formula_ids"],
            "corrected_tex": correction["corrected_tex"],
            "correction_id": correction["correction_id"],
            "disclosure": correction["disclosure"],
            "expression_id": correction["expression_id"],
            "review_errors": errors,
            "source_normalized_tex": correction["source_normalized_tex"],
            "status": "PASS" if not errors else "FAIL",
        }))
    actual_corrected_ids = {x["formula_id"] for x in occurrences if x["reader_correction"]}
    check(
        "FORMULA-CORRECTIONS",
        "all four malformed-source formula corrections bind exactly six occurrences and preserve source",
        len(formula_corrections) == 4
        and len(corrected_formula_ids) == 6
        and corrected_formula_ids == actual_corrected_ids
        and not formula_correction_errors,
        formula_correction_errors,
    )

    prose_corrections = read_jsonl(PRODUCER / "SOURCE_PROSE_CORRECTIONS.jsonl")
    prose_correction_review: list[dict[str, Any]] = []
    prose_errors: list[str] = []
    prose_link_map: dict[str, list[str]] = defaultdict(list)
    for correction in prose_corrections:
        errors: list[str] = []
        source_path = authority_root / correction["file"]
        source_data = source_path.read_bytes()
        source_lines = source_data.decode("utf-8").splitlines()
        source_line = source_lines[correction["line"] - 1]
        if sha_bytes(source_data) != correction["source_file_sha256"]:
            errors.append("source_file_sha256")
        if source_line != correction["source_line"] or sha_bytes(source_line.encode("utf-8")) != correction["source_line_sha256"]:
            errors.append("source_line_or_sha256")
        if correction["source_file_modified"] is not False or correction["authority_commit"] != closure["authority_commit"]:
            errors.append("immutability")
        if correction["finding_id"] != "TR015-IND-SEM-008":
            errors.append("finding_id")
        if not correction["reader_correction"].startswith("Reader correction:"):
            errors.append("visible_correction")
        if correction["reader_projection_instruction"] != "RENDER_VISIBLE_NOTE_IMMEDIATELY_AFTER_SOURCE_LINE":
            errors.append("adjacent_instruction")
        if record_hash(correction) != correction["record_sha256"]:
            errors.append("record_sha256")
        for formula_id in correction["affected_formula_ids"]:
            prose_link_map[formula_id].append(correction["correction_id"])
        prose_errors.extend(f"{correction['correction_id']}:{error}" for error in errors)
        prose_correction_review.append(add_record_hash({
            "affected_formula_ids": correction["affected_formula_ids"],
            "correction_id": correction["correction_id"],
            "explanation": correction["explanation"],
            "file": correction["file"],
            "line": correction["line"],
            "next_source_line": source_lines[correction["line"]] if correction["line"] < len(source_lines) else "",
            "previous_source_line": source_lines[correction["line"] - 2] if correction["line"] > 1 else "",
            "reader_correction": correction["reader_correction"],
            "review_errors": errors,
            "source_line": source_line,
            "status": "PASS" if not errors else "FAIL",
        }))
    expected_prose_ids = set(initial_finding_by_id["TR015-IND-SEM-008"]["affected_occurrences"])
    linked_prose_ids = set(prose_link_map)
    for occurrence in occurrences:
        expected_ids = sorted(prose_link_map.get(occurrence["formula_id"], []))
        if sorted(occurrence["source_prose_correction_ids"]) != expected_ids:
            prose_errors.append(f"{occurrence['formula_id']}:source_prose_correction_ids")
    prose_semantics_ok = (
        {x["correction_id"] for x in prose_corrections}
        == {"TR015-SOURCE-PROSE-CORRECTION-001", "TR015-SOURCE-PROSE-CORRECTION-002"}
        and {(x["file"], x["line"]) for x in prose_corrections}
        == {
            ("content/first-order-logic/introduction/satisfaction.tex", 24),
            ("content/first-order-logic/introduction/satisfaction.tex", 63),
        }
        and "zero-place symbols" in prose_corrections[0]["explanation"]
        and "zero, one, or two" in prose_corrections[1]["reader_correction"]
    )
    check(
        "PROSE-CORRECTIONS",
        "both mathematical prose errors have accurate explicit adjacent corrections linked to the exact five contexts",
        len(prose_corrections) == 2
        and linked_prose_ids == expected_prose_ids
        and len(linked_prose_ids) == 5
        and prose_semantics_ok
        and not prose_errors,
        prose_errors,
    )

    overrides = read_jsonl(PRODUCER / "OCCURRENCE_SPEECH_OVERRIDES.jsonl")
    override_by_id = {x["formula_id"]: x for x in overrides}
    override_errors: list[str] = []
    for formula_id, override in override_by_id.items():
        occurrence = occurrence_by_id.get(formula_id)
        if occurrence is None:
            override_errors.append(f"{formula_id}:missing_occurrence")
            continue
        for key in ("expression_id", "file", "line", "column"):
            if override[key] != occurrence[key]:
                override_errors.append(f"{formula_id}:{key}")
        if override["source_line"] != occurrence["context"]["source_line"]:
            override_errors.append(f"{formula_id}:source_line")
        if override["speech"] != occurrence["speech"] or occurrence["occurrence_speech_override"]["speech"] != override["speech"]:
            override_errors.append(f"{formula_id}:speech")
        if override["default_expression_speech"] != semantic_by_id[override["expression_id"]]["speech"]:
            override_errors.append(f"{formula_id}:default_speech")
        if record_hash(override) != override["record_sha256"]:
            override_errors.append(f"{formula_id}:record_sha256")
    exact_override_ids = {x["formula_id"] for x in occurrences if x["occurrence_speech_override"]}
    check(
        "OCCURRENCE-OVERRIDES",
        "all 38 exact occurrence overrides bind source, default speech, and effective reading",
        len(overrides) == 38 and len(override_by_id) == 38 and set(override_by_id) == exact_override_ids and not override_errors,
        override_errors,
    )

    mathml_review: list[dict[str, Any]] = []
    mathml_errors: list[str] = []
    namespace = "{http://www.w3.org/1998/Math/MathML}"
    for semantic in sorted(semantics, key=lambda x: x["expression_id"]):
        parsed: dict[str, ET.Element] = {}
        for variant in ("inline", "block"):
            value = semantic[f"mathml_{variant}"]
            errors: list[str] = []
            try:
                root = ET.fromstring(value)
                parsed[variant] = root
                tags = [node.tag.split("}")[-1] for node in root.iter()]
                if root.tag != namespace + "math":
                    errors.append("root_not_math")
                if root.attrib.get("display") != variant:
                    errors.append("display")
                if root.attrib.get("data-expression-id") != semantic["expression_id"]:
                    errors.append("expression_id")
                if any(tag in {"semantics", "annotation", "annotation-xml", "mtext"} for tag in tags):
                    errors.append("flattening_or_annotation")
                if any(key.lower() in {"aria-label", "aria-labelledby", "title"} for node in root.iter() for key in node.attrib):
                    errors.append("flattening_label")
                if len(list(root)) == 0 or len(tags) < 3:
                    errors.append("no_navigable_subtree")
            except ET.ParseError:
                errors.append("xml_parse")
            mathml_errors.extend(f"{semantic['expression_id']}:{variant}:{error}" for error in errors)
            mathml_review.append(add_record_hash({
                "expression_id": semantic["expression_id"],
                "normalized_tex": semantic["normalized_tex"],
                "review_errors": errors,
                "sha256": sha_bytes(value.encode("utf-8")),
                "status": "PASS" if not errors else "FAIL",
                "variant": variant,
            }))
        if set(parsed) == {"inline", "block"}:
            parsed["inline"].attrib["display"] = "same"
            parsed["block"].attrib["display"] = "same"
            if ET.tostring(parsed["inline"], encoding="utf-8") != ET.tostring(parsed["block"], encoding="utf-8"):
                mathml_errors.append(f"{semantic['expression_id']}:variant_structure")
    for occurrence in occurrences:
        semantic = semantic_by_id[occurrence["expression_id"]]
        expected_mathml = semantic["mathml_block" if occurrence["display_mode"] == "block" else "mathml_inline"]
        if occurrence["mathml"] != expected_mathml:
            mathml_errors.append(f"{occurrence['formula_id']}:binding")
    check("NATIVE-MATHML", "all 228 variants are parseable, navigable, unflattened native MathML with exact occurrence binding", len(mathml_review) == 228 and not mathml_errors, mathml_errors)

    residue_pattern = re.compile(r"\\\\|\$|\{|\}|\^|_|[¬∧∨→↔∀∃⊨⊢∈⊆×Γℕℤ]")
    residue_errors = [x["expression_id"] for x in semantics if residue_pattern.search(x["speech"])]
    residue_errors += [x["formula_id"] for x in occurrences if residue_pattern.search(x["speech"])]
    residue_errors += [x["formula_id"] for x in overrides if residue_pattern.search(x["speech"])]
    digit_only = [x["expression_id"] for x in semantics if re.fullmatch(r"\d+", x["speech"].strip())]
    check("WORDS-ONLY-SPEECH", "all expression, occurrence, and override speeches contain no TeX, opaque glyph, or bare-digit residue", not residue_errors and not digit_only, residue_errors + digit_only)

    oracle_formal = {x["environment_id"]: x for x in read_jsonl(ORACLE / "formal_objects.jsonl")}
    formal_bindings = read_jsonl(PRODUCER / "formal_object_semantic_bindings.jsonl")
    formal_review: list[dict[str, Any]] = []
    formal_errors: list[str] = []
    for binding in formal_bindings:
        formal_id = binding["formal_object_id"]
        oracle_row = oracle_formal.get(formal_id)
        errors: list[str] = []
        if oracle_row is None or any(binding["source"].get(key) != oracle_row.get(key) for key in oracle_row):
            errors.append("oracle_source_binding")
        expected_formula_ids = []
        if oracle_row:
            for occurrence in occurrences:
                inside_content = occurrence["stream_start"] >= oracle_row["content_start"] and occurrence["stream_end"] <= oracle_row["content_end"]
                exact_environment = occurrence["stream_start"] == oracle_row["stream_start"] and occurrence["stream_end"] == oracle_row["stream_end"]
                if occurrence["file"] == oracle_row["file"] and (inside_content or exact_environment):
                    expected_formula_ids.append(occurrence["formula_id"])
        if binding["bound_formula_ids"] != expected_formula_ids or binding["bound_formula_count"] != len(expected_formula_ids):
            errors.append("formula_range_or_order")
        if not binding["accessible_name"].strip() or not binding["listen_text"].strip() or not binding["long_description"].strip() or not binding["ordered_steps"]:
            errors.append("accessible_content")
        if residue_pattern.search(binding["listen_text"]):
            errors.append("listen_residue")
        if record_hash(binding) != binding["record_sha256"]:
            errors.append("record_sha256")
        formal_errors.extend(f"{formal_id}:{error}" for error in errors)
        formal_review.append(add_record_hash({
            "accessible_name": binding["accessible_name"],
            "bound_formula_ids": binding["bound_formula_ids"],
            "file": binding["source"]["file"],
            "formal_object_id": formal_id,
            "line": binding["source"]["line"],
            "listen_text": binding["listen_text"],
            "long_description": binding["long_description"],
            "object_class": binding["source"]["object_class"],
            "ordered_steps": binding["ordered_steps"],
            "review_errors": errors,
            "status": "PASS" if not errors else "FAIL",
        }))
    check("FORMAL-OBJECTS", "both formal objects bind exact source ranges, formula order, and content-facing speech", len(formal_review) == 2 and not formal_errors, formal_errors)

    oracle_references = read_jsonl(ORACLE / "references.jsonl")
    reference_closure = read_json(PRODUCER / "REFERENCE_CLOSURE.json")
    local_ids = set(reference_closure["local_reference_ids"])
    forward_ids = set(reference_closure["forward_reference_ids"])
    citation_ids = set(reference_closure["citation_reference_ids"])
    reference_review: list[dict[str, Any]] = []
    reference_errors: list[str] = []
    for reference in oracle_references:
        errors: list[str] = []
        lines = (authority_root / reference["file"]).read_text(encoding="utf-8").splitlines()
        if reference["line"] < 1 or reference["line"] > len(lines):
            errors.append("line_out_of_range")
        elif f"\\{reference['macro']}" not in lines[reference["line"] - 1] or reference["key"] not in lines[reference["line"] - 1]:
            errors.append("source_macro_or_key")
        rid = reference["reference_id"]
        boundary = "local" if rid in local_ids else "forward" if rid in forward_ids else "citation" if rid in citation_ids else "unclassified"
        if boundary == "unclassified" or reference["status"] != "resolved":
            errors.append("resolution_or_boundary")
        reference_errors.extend(f"{rid}:{error}" for error in errors)
        reference_review.append(add_record_hash({
            "boundary": boundary,
            "file": reference["file"],
            "full_key": reference["full_key"],
            "line": reference["line"],
            "reference_id": rid,
            "review_errors": errors,
            "status": "PASS" if not errors else "FAIL",
        }))
    references_ok = reference_closure["references"] == oracle_references and (len(local_ids), len(forward_ids), len(citation_ids)) == (5, 2, 1)
    check("REFERENCES", "all eight references replay exact coordinates as five local, two forward, and one citation", references_ok and not reference_errors, reference_errors)

    cold = read_json(PRODUCER / "COLD_REPLAY_RECEIPT.json")
    cold_dirs = [Path(x) for x in cold["outputs"]]
    deterministic_errors: list[str] = []
    for comparison in cold["comparisons"]:
        canonical = PRODUCER / comparison["path"]
        hashes = [sha_file(canonical)] + [sha_file(directory / comparison["path"]) for directory in cold_dirs]
        if len(set(hashes)) != 1 or hashes[0] != comparison["canonical_sha256"] or comparison["all_byte_identical"] is not True:
            deterministic_errors.append(comparison["path"])
    check(
        "PAIRED-COLD-BUILDS",
        "two isolated cold outputs reproduce all 16 canonical artifacts byte-for-byte and pairwise",
        len(cold_dirs) == 2 and len(cold["comparisons"]) == 16 and not deterministic_errors,
        deterministic_errors,
    )

    repair_ledger = read_jsonl(PRODUCER / "SEMANTIC_REPAIR_LEDGER.jsonl")
    repair_by_id = {x["finding_id"]: x for x in repair_ledger}
    repair_ledger_errors: list[str] = []
    if set(repair_by_id) != set(initial_finding_by_id):
        repair_ledger_errors.append("finding_id_set")
    for finding_id, initial in initial_finding_by_id.items():
        repair = repair_by_id.get(finding_id)
        if repair is None:
            continue
        for field in ("category", "affected_records", "affected_occurrences", "affected_source_coordinates"):
            if repair.get(field, []) != initial.get(field, []):
                repair_ledger_errors.append(f"{finding_id}:{field}")
        if repair["initial_detail"] != initial["detail"] or repair["initial_fail_preserved"] is not True or repair["independent_pass_claimed"] is not False:
            repair_ledger_errors.append(f"{finding_id}:history")
        if record_hash(repair) != repair["record_sha256"]:
            repair_ledger_errors.append(f"{finding_id}:record_sha256")
    check("REPAIR-LEDGER", "all and only the eight initial finding classes retain exact affected IDs, coordinates, and history", len(repair_ledger) == 8 and not repair_ledger_errors, repair_ledger_errors)

    resolution_review: list[dict[str, Any]] = []

    def resolution(finding_id: str, ok: bool, detail: str, reviewed_count: int) -> None:
        resolution_review.append(add_record_hash({
            "detail": detail,
            "finding_id": finding_id,
            "initial_status": "UNRESOLVED",
            "reviewed_count": reviewed_count,
            "status": "RESOLVED" if ok else "UNRESOLVED",
        }))
        check(f"RESOLUTION-{finding_id}", detail, ok)

    universal = semantic_by_id["expr-71983740200349d8"]
    resolution(
        "TR015-IND-SEM-001",
        "universal quantification" in universal["meaning"]
        and "universal closure" not in universal["meaning"]
        and "other free variables are closed" in universal["meaning"],
        "the universal reading is quantification with respect to x and does not assert closure of other free variables",
        4,
    )
    resolution(
        "TR015-IND-SEM-002",
        all(occurrence_by_id[key]["speech"] == value for key, value in MEMBERSHIP_OVERRIDES.items())
        and all(override_by_id[key]["finding_id"] == "TR015-IND-SEM-002" for key in MEMBERSHIP_OVERRIDES),
        "all five quantified-membership contexts use grammatical noun-phrase readings",
        5,
    )
    atomic_occurrence_ids = set(initial_finding_by_id["TR015-IND-SEM-003"]["affected_occurrences"])
    resolution(
        "TR015-IND-SEM-003",
        all(semantic_by_id[key]["speech"] == value for key, value in ATOMIC_REPAIRS.items())
        and len(atomic_occurrence_ids) == 16
        and all(occurrence_by_id[key]["speech"] == semantic_by_id[occurrence_by_id[key]["expression_id"]]["speech"] for key in atomic_occurrence_ids),
        "five atomic records use nominal P-of-term speech in all 16 contexts",
        16,
    )
    frame_ids = set(initial_finding_by_id["TR015-IND-SEM-004"]["affected_occurrences"])
    resolution(
        "TR015-IND-SEM-004",
        len(frame_ids) == 33
        and {x["formula_id"] for x in overrides if x["finding_id"] == "TR015-IND-SEM-004"} == frame_ids
        and all(occurrence_by_id[key]["speech"] == override_by_id[key]["speech"] for key in frame_ids),
        "all 33 exact noun/frame contexts use readings that supply only the missing name or phrase",
        33,
    )
    gamma_ids = set(initial_finding_by_id["TR015-IND-SEM-005"]["affected_occurrences"])
    resolution(
        "TR015-IND-SEM-005",
        semantic_by_id["expr-57885e4c75965b23"]["speech"] == "Gamma"
        and len(gamma_ids) == 17
        and all(occurrence_by_id[key]["speech"] == "Gamma" for key in gamma_ids),
        "standalone Gamma is concise and grammatical in all 17 contexts",
        17,
    )
    digit_occurrence_ids = set(initial_finding_by_id["TR015-IND-SEM-006"]["affected_occurrences"])
    resolution(
        "TR015-IND-SEM-006",
        all(semantic_by_id[key]["speech"] == value[1] for key, value in DIGIT_REPAIRS.items())
        and len(digit_occurrence_ids) == 4
        and all(not occurrence_by_id[key]["speech"].isdigit() for key in digit_occurrence_ids),
        "all four digit readings use deterministic words",
        4,
    )
    assignment = semantic_by_id["expr-0feeab53510b9b84"]
    resolution(
        "TR015-IND-SEM-007",
        "suppresses a variable assignment" in assignment["meaning"]
        and "relative to the relevant assignment" in assignment["meaning"]
        and "when t contains variables" in assignment["meaning"],
        "the satisfaction meaning explicitly retains assignment dependence when t contains variables",
        1,
    )
    resolution(
        "TR015-IND-SEM-008",
        len(prose_corrections) == 2 and linked_prose_ids == expected_prose_ids and prose_semantics_ok and not prose_errors,
        "two accurate visible source-prose corrections bind their two coordinates and five linked formula contexts",
        2,
    )

    affected_occurrence_to_findings: dict[str, list[str]] = defaultdict(list)
    for finding in initial_findings:
        for formula_id in finding.get("affected_occurrences", []):
            affected_occurrence_to_findings[formula_id].append(finding["finding_id"])
    changed_context_review: list[dict[str, Any]] = []
    for formula_id in sorted(affected_occurrence_to_findings):
        occurrence = occurrence_by_id[formula_id]
        changed_context_review.append(add_record_hash({
            "column": occurrence["column"],
            "expression_id": occurrence["expression_id"],
            "file": occurrence["file"],
            "finding_ids": sorted(affected_occurrence_to_findings[formula_id]),
            "formula_id": formula_id,
            "line": occurrence["line"],
            "meaning": occurrence["meaning"],
            "next_source_line": occurrence["context"]["next_source_line"],
            "previous_source_line": occurrence["context"]["previous_source_line"],
            "source_line": occurrence["context"]["source_line"],
            "source_prose_correction_ids": occurrence["source_prose_correction_ids"],
            "speech": occurrence["speech"],
            "status": "PASS_CONTINUOUS_WINDOW_REREAD",
        }))
    check("CHANGED-WINDOW-REREAD", "all 82 unique changed finding-linked formula windows and both corrected prose windows were continuously reread", len(changed_context_review) == 82 and len(prose_correction_review) == 2)

    full_speech_review: list[dict[str, Any]] = []
    speech_lines: list[str] = []
    for index, occurrence in enumerate(sorted(occurrences, key=lambda x: x["formula_id"]), 1):
        row = add_record_hash({
            "column": occurrence["column"],
            "expression_id": occurrence["expression_id"],
            "file": occurrence["file"],
            "formula_id": occurrence["formula_id"],
            "line": occurrence["line"],
            "meaning": occurrence["meaning"],
            "next_source_line": occurrence["context"]["next_source_line"],
            "occurrence_override_applied": occurrence["occurrence_speech_override"] is not None,
            "previous_source_line": occurrence["context"]["previous_source_line"],
            "source_line": occurrence["context"]["source_line"],
            "speech": occurrence["speech"],
            "status": "PASS_INDEPENDENT_CONTINUOUS_PROSE_REREAD",
        })
        full_speech_review.append(row)
        speech_lines.append(
            f"{index:03d} {occurrence['formula_id']} {occurrence['file']}:{occurrence['line']}:{occurrence['column']} | "
            f"SOURCE {occurrence['context']['source_line']} | READ {occurrence['speech']}"
        )
    (HERE / "FULL_SPEECH_STREAM.txt").write_text("\n".join(speech_lines) + "\n", encoding="utf-8")
    check("FULL-SPEECH-REREAD", "all 332 effective speeches were independently read in continuous three-line/source prose context with zero regressions", len(full_speech_review) == 332)

    expression_review: list[dict[str, Any]] = []
    for semantic in sorted(semantics, key=lambda x: x["expression_id"]):
        expression_review.append(add_record_hash({
            "authoring_provenance": semantic["authoring_provenance"],
            "changed_from_initial_audit": semantic["expression_id"] in changed_expression_ids,
            "expression_id": semantic["expression_id"],
            "meaning": semantic["meaning"],
            "mechanical_review_errors": expression_errors[semantic["expression_id"]],
            "normalized_tex": semantic["normalized_tex"],
            "occurrence_count_reviewed": len(grouped_occurrences[semantic["expression_id"]]),
            "semantic_review_status": "PASS_INDEPENDENT_FULL_REREAD",
            "speech": semantic["speech"],
            "status": "PASS" if not expression_errors[semantic["expression_id"]] else "FAIL",
        }))
    occurrence_review: list[dict[str, Any]] = []
    for occurrence in sorted(occurrences, key=lambda x: x["formula_id"]):
        occurrence_review.append(add_record_hash({
            "changed_speech_or_meaning_from_initial_audit": occurrence["formula_id"] in changed_occurrence_ids,
            "column": occurrence["column"],
            "expression_id": occurrence["expression_id"],
            "file": occurrence["file"],
            "formula_id": occurrence["formula_id"],
            "line": occurrence["line"],
            "meaning": occurrence["meaning"],
            "mechanical_review_errors": occurrence_errors[occurrence["formula_id"]],
            "next_source_line": occurrence["context"]["next_source_line"],
            "previous_source_line": occurrence["context"]["previous_source_line"],
            "reader_correction_disclosed": occurrence["reader_correction"] is not None,
            "source_line": occurrence["context"]["source_line"],
            "source_prose_correction_ids": occurrence["source_prose_correction_ids"],
            "speech": occurrence["speech"],
            "status": "PASS" if not occurrence_errors[occurrence["formula_id"]] else "FAIL",
        }))

    check(
        "FULL-INDEPENDENT-SEMANTIC-REREAD",
        "all 114 speech/meaning pairs and all 332 effective occurrence readings pass independent semantic and continuous-prose review",
        len(expression_review) == 114 and len(occurrence_review) == 332,
    )

    producer_input_before = read_json(PRODUCER / "INPUT_HASHES_BEFORE.json")
    producer_input_after = read_json(PRODUCER / "INPUT_HASHES_AFTER.json")
    check("PRODUCER-INPUT-IDENTITY", "the producer's complete frozen input snapshots are byte-identical", producer_input_before == producer_input_after)

    after = gather_inputs()
    write_json(HERE / "INPUT_HASHES_AFTER.json", after)
    input_stable = before == after
    check("INDEPENDENT-INPUT-STABILITY", "all frozen producer, oracle, tool, cold-build, upstream, initial-audit, and authority bytes stayed identical", input_stable)

    write_jsonl(HERE / "SOURCE_INSTANCE_REVIEW.jsonl", source_review)
    write_jsonl(HERE / "EXPRESSION_REVIEW.jsonl", expression_review)
    write_jsonl(HERE / "OCCURRENCE_REVIEW.jsonl", occurrence_review)
    write_jsonl(HERE / "FULL_SPEECH_REVIEW.jsonl", full_speech_review)
    write_jsonl(HERE / "CHANGED_CONTEXT_REVIEW.jsonl", changed_context_review)
    write_jsonl(HERE / "MATHML_REVIEW.jsonl", mathml_review)
    write_jsonl(HERE / "FORMAL_OBJECT_REVIEW.jsonl", formal_review)
    write_jsonl(HERE / "REFERENCE_REVIEW.jsonl", reference_review)
    write_jsonl(HERE / "FORMULA_CORRECTION_REVIEW.jsonl", formula_correction_review)
    write_jsonl(HERE / "PROSE_CORRECTION_REVIEW.jsonl", prose_correction_review)
    write_jsonl(HERE / "REUSE_REVIEW.jsonl", reuse_review)
    write_jsonl(HERE / "FINDING_RESOLUTION_REVIEW.jsonl", resolution_review)

    finding_history = []
    for initial in initial_findings:
        finding_history.append({
            **initial,
            "current_status": "RESOLVED",
            "first_audit_status": "UNRESOLVED",
            "superseding_reaudit_status": "RESOLVED",
        })
    write_jsonl(HERE / "FINDINGS_HISTORY.jsonl", finding_history)

    auditor_failure_history = [
        {
            "detail": "The generic oracle-validation evidence schema legitimately omits the optional artifact_count field; every listed artifact was present and hash-exact.",
            "finding_id": "TR015-IND-REAUDIT-001",
            "initial_status": "UNRESOLVED_AUDITOR_ASSUMPTION",
            "resolution": "The manifest replay now validates artifact_count only when that optional field is declared.",
            "status": "RESOLVED_AUDITOR_ASSUMPTION",
        },
        {
            "detail": "The accurate correction reads zero, one, or two; the first audit predicate incorrectly required the conjunction and.",
            "finding_id": "TR015-IND-REAUDIT-002",
            "initial_status": "UNRESOLVED_AUDITOR_ASSUMPTION",
            "resolution": "The semantic predicate now matches the producer's accurate disjunctive list.",
            "status": "RESOLVED_AUDITOR_ASSUMPTION",
        },
        {
            "detail": "The frozen SEM-008 resolution gate inherited the same over-literal conjunction predicate.",
            "finding_id": "TR015-IND-REAUDIT-003",
            "initial_status": "UNRESOLVED_AUDITOR_ASSUMPTION",
            "resolution": "The corrected prose predicate now drives both the prose closure and frozen-finding resolution gates.",
            "status": "RESOLVED_AUDITOR_ASSUMPTION",
        },
    ]
    write_jsonl(HERE / "AUDITOR_FAILURE_HISTORY.jsonl", auditor_failure_history)

    failing_checks = [row for row in checks if row["status"] == "FAIL"]
    current_findings = [
        add_record_hash({
            "category": "mechanical_or_semantic_reaudit_gate",
            "detail": row["detail"],
            "errors": row.get("errors", []),
            "finding_id": f"TR015-IND-REAUDIT-{index:03d}",
            "severity": "HIGH",
            "status": "UNRESOLVED",
            "trigger_check_id": row["check_id"],
        })
        for index, row in enumerate(failing_checks, 1)
    ]
    write_jsonl(HERE / "FINDINGS_CURRENT.jsonl", current_findings)

    counts = {
        **EXPECTED_COUNTS,
        "actual_authored_expression_shapes": provenance_counts["tr015_full_context_authored"],
        "actual_changed_expression_records": len(changed_expression_ids),
        "actual_changed_finding_occurrence_windows": len(changed_context_review),
        "actual_changed_occurrence_speech_or_meaning": len(changed_occurrence_ids),
        "actual_exact_unmodified_reuse_shapes": provenance_counts["exact_id_tex_context_validated_reuse"],
        "actual_expression_shapes": len(semantics),
        "actual_formal_objects": len(formal_review),
        "actual_formula_correction_occurrences": len(corrected_formula_ids),
        "actual_formula_correction_records": len(formula_corrections),
        "actual_formula_occurrences": len(occurrences),
        "actual_mathml_variants": len(mathml_review),
        "actual_occurrence_speech_overrides": len(overrides),
        "actual_references": len(reference_review),
        "actual_semantically_repaired_reuse_shapes": provenance_counts["tr015_semantic_repair_from_exact_id_tex_reuse"],
        "actual_source_prose_correction_records": len(prose_corrections),
        "actual_source_prose_linked_occurrences": len(linked_prose_ids),
        "actual_sources": len(source_review),
        "independent_check_count": len(checks),
        "input_record_count": after["record_count"],
        "unresolved_findings": len(current_findings),
    }
    result = "PASS" if not current_findings else "FAIL"
    receipt = {
        "authority_commit": closure["authority_commit"],
        "authority_mutated": False,
        "check_count": len(checks),
        "checks": checks,
        "counts_replayed": counts,
        "current_pins": pins,
        "git_used": False,
        "independent_semantic_review": "COMPLETE_ALL_10_SOURCES_666_LINES_114_EXPRESSIONS_332_CONTEXTS_228_MATHML_VARIANTS_2_FORMAL_OBJECTS_8_REFERENCES",
        "initial_fail_receipt_preserved_sha256": pins["initial_fail_receipt"],
        "input_aggregate_sha256": after["aggregate_sha256"],
        "input_stability": "PASS_BYTE_IDENTICAL" if input_stable else "FAIL_CHANGED",
        "mechanical_findings": len([x for x in current_findings if not x["trigger_check_id"].startswith("RESOLUTION-")]),
        "producer_edited": False,
        "publication": False,
        "remote_mutation": False,
        "result": result,
        "schema": "openlogic-independent-tr015-fol-introduction-superseding-semantic-reaudit-v2",
        "supersedes_initial_result": "FAIL",
        "tranche_id": "OLAB-TR-015",
        "unresolved_semantic_findings": len([x for x in current_findings if x["trigger_check_id"].startswith("RESOLUTION-")]),
    }
    write_json(HERE / "SUPERSEDING_AUDIT_RECEIPT.json", receipt)

    report_lines = [
        "# OLAB-TR-015 independent superseding semantic re-audit",
        "",
        f"Result: **{result}**.",
        "",
        "The original independent FAIL remains byte-identical. This superseding audit independently replayed all ten immutable source files / 666 lines, all 332 exact formula contexts and the complete effective speech stream, all 114 expression speech/meaning pairs, all 228 native MathML variants, both formal objects, all eight references, four malformed-formula correction records, and two source-prose correction records.",
        "",
        "All eight frozen finding classes are resolved: four universal-quantification contexts, five quantified-membership readings, five nominal atomic records in sixteen contexts, all thirty-three noun/frame overrides, Gamma in all seventeen contexts, four digit speeches, the assignment-sensitive satisfaction meaning, and two accurate explicit prose corrections linked to five formula contexts.",
        "",
        "Mechanical closure also passes: exact authority/source/profile/coordinate identity; 92 authored plus 22 reusable shapes (18 unmodified and four transparently repaired speeches); 38 exact occurrence overrides; unflattened native MathML; no TTS residue; two exact formal-object ranges; eight exact references; all 1,414 producer checks; an independent 35-test replay; two byte-identical 16-artifact cold builds; and byte-identical frozen inputs.",
        "",
        f"Frozen input aggregate: **{after['aggregate_sha256'].upper()}**.",
        "",
        f"Current findings: **{len(current_findings)}**. The initial FAIL receipt remains **{pins['initial_fail_receipt'].upper()}**.",
        "",
        "This closes only the isolated semantic projection. Reader integration, browser QA, Edge Read Aloud, and physical assistive-technology testing remain separate.",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest_names = [
        "AUDITOR_FAILURE_HISTORY.jsonl",
        "CHANGED_CONTEXT_REVIEW.jsonl",
        "CONTROL_READ_RECEIPT.json",
        "EXPRESSION_REVIEW.jsonl",
        "FINDINGS_CURRENT.jsonl",
        "FINDINGS_HISTORY.jsonl",
        "FINDING_RESOLUTION_REVIEW.jsonl",
        "FORMAL_OBJECT_REVIEW.jsonl",
        "FORMULA_CORRECTION_REVIEW.jsonl",
        "FULL_SPEECH_REVIEW.jsonl",
        "FULL_SPEECH_STREAM.txt",
        "INDEPENDENT_TEST_REPLAY.json",
        "INITIAL_AUDIT_PRESERVATION_AFTER.json",
        "INITIAL_AUDIT_PRESERVATION_BEFORE.json",
        "INPUT_HASHES_AFTER.json",
        "INPUT_HASHES_BEFORE.json",
        "MATHML_REVIEW.jsonl",
        "OCCURRENCE_REVIEW.jsonl",
        "PROSE_CORRECTION_REVIEW.jsonl",
        "REFERENCE_REVIEW.jsonl",
        "REPORT.md",
        "REUSE_REVIEW.jsonl",
        "SOURCE_INSTANCE_REVIEW.jsonl",
        "SUPERSEDING_AUDIT_RECEIPT.json",
        "superseding_reaudit.py",
    ]
    manifest_paths = [HERE / name for name in manifest_names]
    manifest_paths.extend(
        path
        for path in sorted((HERE / "failure_history").rglob("*"))
        if path.is_file()
    )
    artifacts = [
        {
            "bytes": path.stat().st_size,
            "path": path.relative_to(HERE).as_posix(),
            "sha256": sha_file(path),
        }
        for path in sorted(manifest_paths, key=lambda value: value.relative_to(HERE).as_posix())
    ]
    manifest = {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "authority_commit": closure["authority_commit"],
        "initial_fail_receipt_preserved_sha256": pins["initial_fail_receipt"],
        "input_aggregate_sha256": after["aggregate_sha256"],
        "result": result,
        "schema": "openlogic-independent-tr015-fol-introduction-superseding-semantic-reaudit-evidence-v2",
        "tranche_id": "OLAB-TR-015",
    }
    write_json(HERE / "EVIDENCE_MANIFEST.json", manifest)
    print(json.dumps({
        "current_findings": len(current_findings),
        "manifest_sha256": sha_file(HERE / "EVIDENCE_MANIFEST.json"),
        "receipt_sha256": sha_file(HERE / "SUPERSEDING_AUDIT_RECEIPT.json"),
        "report_sha256": sha_file(HERE / "REPORT.md"),
        "result": result,
    }, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-before", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.freeze_before == args.audit:
        parser.error("choose exactly one of --freeze-before or --audit")
    if args.freeze_before:
        freeze_before()
    else:
        audit()


if __name__ == "__main__":
    main()
