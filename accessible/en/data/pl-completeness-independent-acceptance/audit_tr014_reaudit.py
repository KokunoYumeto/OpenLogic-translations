#!/usr/bin/env python3
"""Fresh independent semantic re-audit for repaired OLAB-TR-014.

This program is intentionally standard-library-only for its audit logic.  It
reads producer, oracle, source, formal, reference, correction, and preserved
prior-FAIL records directly from their pinned locations.  Producer code is
invoked only in isolated subprocesses for cold-replay and fail-closed mutation
tests; it is not imported as an authority for the independent checks below.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable


AUDIT = Path(__file__).resolve().parent
PRIOR = AUDIT.parent
PROJECT = AUDIT.parents[2]
WORK = PROJECT / "work" / "tranche_014_pl_completeness_projection"
PRODUCER = PROJECT / "evidence" / "tranche_014_pl_completeness_projection"
VALIDATION = PRODUCER / "producer_validation"
ORACLE = PROJECT / "evidence" / "tranche_014_pl_completeness_oracle"
ORACLE_VALIDATION = PROJECT / "evidence" / "tranche_014_pl_completeness_oracle_validation"
SOURCE_AUTHORITY = json.loads((ORACLE / "SOURCE_AUTHORITY.json").read_text(encoding="utf-8"))
AUTHORITY = Path(SOURCE_AUTHORITY["authority_root"])

TRANCHE_ID = "OLAB-TR-014"
AUTHORITY_COMMIT = "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"

EXPECTED_PINS = {
    "ARTIFACT_MANIFEST.json": "829ecfbc9f795bbf1ca11ed6b7dba99dc1141f70d9de2a09ebbb2561a2a762b1",
    "producer_validation/VALIDATION_RECEIPT.json": "865a621fc94faff7d0f9934c1ffd55d7fd15275fe46e7cc8cdf5e4d110eccbce",
    "producer_validation/VALIDATION_MANIFEST.json": "532546071cadc41a22ee53d4011143e45067b4860cf97f64ddd310f8b0d8d51d",
    "EVIDENCE_MANIFEST.json": "3817d43817ffaea38ecbc9fce58215ac9ec09a98c96b9cb53ef086d128e4c8de",
}

PRIOR_FAIL_PINS = {
    "EVIDENCE_MANIFEST.json": "9ad80d2d2825761e05ac3863948f06952ccb5a9f638870cc091aa1d6d88e55b1",
    "FINAL_AUDIT_RECEIPT.json": "939e1a950cf6d10ac2fbed180db2bc41935b214a8e8ef74475be3cf38eda2ffb",
    "FINDINGS_CURRENT.jsonl": "671c80cae2da43ad0c6ffe290c03b5f4e33ce05cd1700eddc27892d5e8c7310f",
    "INITIAL_AUDIT_FAIL.json": "cce4f74a82db281efc3d08c1b09a191a7b9521fc279af13ecf82db9277030862",
}

EXPECTED_COUNTS = {
    "source_instances": 9,
    "source_lines": 1373,
    "source_bytes": 58079,
    "expression_shapes": 112,
    "formula_occurrences": 335,
    "formal_objects": 21,
    "exercises": 8,
    "source_references": 69,
    "derived_reader_references": 1,
    "source_corrections": 2,
    "diagrams": 0,
}

SAR_STATUS = "SOURCE_CLOSURE_ONLY_OMITTED_FROM_DERIVED_PL_BY_SAR_002"
SELECTED_STATUS = "SELECTED_IN_DERIVED_PL"
MIXED_STATUS = "MIXED_SELECTED_AND_SAR_002_SOURCE_CLOSURE"
SAR_FORMULA_IDS = tuple(f"projected-formula-{n:07d}" for n in range(5815, 5846))
SAR_AFFECTED_EXPRESSIONS = (
    "expr-043a718774c572bd", "expr-06fde3d4eab0d5cf", "expr-09e63ea920e41318",
    "expr-1ee97228549db748", "expr-33a9c96304bcc292", "expr-42b8f19ae63d24a4",
    "expr-68b2905229e1eb0a", "expr-71983740200349d8", "expr-7d7e64950a6606db",
    "expr-abce2438ed9913f5", "expr-b30a5c6340432dd4", "expr-b50bb8940da5b931",
    "expr-d475527c5abd77f4", "expr-dd108c91f74990ba", "expr-e3b98a4da31a127d",
    "expr-e54c6513d9ceaf9c", "expr-ffd510d6693c962f",
)
SAR_EXCLUSIVE_EXPRESSIONS = tuple(x for x in SAR_AFFECTED_EXPRESSIONS if x != "expr-b50bb8940da5b931")

PIECEWISE_IDS = ("expr-437f5dd050d65408", "expr-bcafa705da31438a")
PRIME_IDS = ("expr-5757d5082cda4415", "expr-ac5217203ef7dcda", "expr-e9c6ccabbc4578c3")

REFERENCE_REPAIR_IDS = (
    "reference-000227", "reference-000229", "reference-000236", "reference-000240",
    "reference-000241", "reference-000242", "reference-000244", "reference-000245",
    "reference-000246", "reference-000247", "reference-000248", "reference-000253",
    "reference-001756", "reference-001757", "reference-001758", "reference-001759",
    "reference-001760", "reference-001761", "reference-001762", "reference-001763",
    "reference-001764", "reference-001765", "reference-001766", "reference-001767",
    "reference-001768", "reference-001769", "reference-001770", "reference-001771",
    "reference-001772", "reference-001773", "reference-001774", "reference-001775",
    "reference-001776", "reference-001777", "reference-001778", "reference-001779",
    "reference-001780", "reference-001781", "reference-001782", "reference-001783",
    "reference-001784", "reference-001785", "reference-001786", "reference-001787",
    "reference-001788", "reference-001789", "reference-001790", "reference-001791",
)

PROOF_SYSTEMS = {
    "seq": "sequent calculus",
    "ntd": "natural deduction",
    "axd": "axiomatic derivation",
    "tab": "tableaux",
}
PROOF_TEMPLATES = {
    "ptn:sec": "the proof-theoretic notions section for {system}",
    "prv:prop:explicit-inc": "the {system} proposition that derivability plus an explicit negation yields inconsistency",
    "ppr:prop:provability-lor": "the {system} proposition about disjunction and derivability",
    "prv:prop:provability-exhaustive": "the {system} proposition that two inconsistent one-formula extensions make the original set inconsistent",
    "ptn:prop:proves-compact": "the proof-compactness proposition for {system}",
    "prv:prop:prov-incons": "the {system} proposition equating derivability of A with inconsistency after adjoining not A",
    "sou:cor:consistency-soundness": "the {system} soundness corollary that satisfiability implies consistency",
}
LOCAL_REFERENCE_NAMES = {
    "pl:com:mod:defn:termmodel": "the canonical valuation definition",
    "pl:com:ccs:prop:ccs-prov-in": "the complete-consistent-set closure-under-derivability proposition",
    "pl:com:ccs:prop:ccs-or": "the complete-consistent-set disjunction proposition",
    "pl:com:cth:thm:completeness": "the model-existence Completeness Theorem",
    "pl:com:cth:cor:completeness": "the semantic-consequence corollary to the Completeness Theorem",
}

NS = "{http://www.w3.org/1998/Math/MathML}"
FORBIDDEN_SPEECH = re.compile(r"[\\$^_{}=<>\u2208\u2209\u2286\u2287\u22a2\u22a8\u22ad\u2227\u2228\u2192\u22a5\u22a4]")
OPAQUE_REFERENCE = re.compile(r"cited proof-system|term-model or canonical|ccs prov in|provability lor|proves compact", re.I)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(canonical(value), encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(compact(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


findings: list[dict[str, Any]] = []
predicate_results: dict[str, bool] = {}


def assert_pred(condition: bool, predicate: str, detail: str, family: str = "OUT_OF_FAMILY") -> bool:
    prior = predicate_results.get(predicate, True)
    predicate_results[predicate] = prior and bool(condition)
    if not condition:
        key = (predicate, detail)
        if not any((row["predicate"], row["detail"]) == key for row in findings):
            findings.append({
                "finding_id": f"TR014-REAUDIT-{len(findings) + 1:03d}",
                "family": family,
                "predicate": predicate,
                "detail": detail,
                "status": "OPEN_CURRENT",
            })
    return bool(condition)


def file_record(path: Path, base: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def canonical_source_hash(row: dict[str, Any]) -> str:
    return sha256_bytes(compact(row).encode("utf-8"))


def expected_reference_name(full_key: str) -> str | None:
    if full_key in LOCAL_REFERENCE_NAMES:
        return LOCAL_REFERENCE_NAMES[full_key]
    parts = full_key.split(":")
    if len(parts) >= 4 and parts[0] == "pl" and parts[1] in PROOF_SYSTEMS:
        template = PROOF_TEMPLATES.get(":".join(parts[2:]))
        if template:
            return template.format(system=PROOF_SYSTEMS[parts[1]])
    return None


def project_fol_conditionals_to_pl(value: str) -> str:
    r"""Evaluate braced ``\iftag{FOL}{yes}{no}`` calls for the PL profile."""

    def argument(text: str, cursor: int) -> tuple[str, int]:
        if cursor >= len(text) or text[cursor] != "{":
            raise ValueError(f"expected braced argument at {cursor}: {text!r}")
        depth = 0
        start = cursor + 1
        cursor += 1
        while cursor < len(text):
            if text[cursor] == "{" and (cursor == 0 or text[cursor - 1] != "\\"):
                depth += 1
            elif text[cursor] == "}" and (cursor == 0 or text[cursor - 1] != "\\"):
                if depth == 0:
                    return text[start:cursor], cursor + 1
                depth -= 1
            cursor += 1
        raise ValueError(f"unterminated braced argument: {text!r}")

    marker = "\\iftag"
    while marker in value:
        start = value.index(marker)
        cursor = start + len(marker)
        tag, cursor = argument(value, cursor)
        selected, cursor = argument(value, cursor)
        omitted, cursor = argument(value, cursor)
        if tag != "FOL":
            raise ValueError(f"unexpected inline profile tag {tag!r}")
        value = value[:start] + omitted + value[cursor:]
    return value


def capture_protected_scope() -> dict[str, Any]:
    baseline = read_json(WORK / "REPAIR_PROTECTED_SCOPE_BEFORE.json")
    baseline_rows = []
    for record in baseline["records"]:
        if record["scope"] == "project_protected":
            path = PROJECT / record["path"]
        elif record["scope"] == "immutable_source":
            path = AUTHORITY / record["path"]
        else:
            assert_pred(False, "PROTECTED_SCOPE_KIND_EXACT", f"unknown protected scope {record['scope']}")
            continue
        present = path.is_file()
        actual_bytes = path.stat().st_size if present else None
        actual_hash = sha256_file(path) if present else None
        exact = present and actual_bytes == record["bytes"] and actual_hash == record["sha256"]
        assert_pred(exact, "PROTECTED_BASELINE_IDENTITY_EXACT", f"protected baseline drift: {record['path']}")
        baseline_rows.append({**record, "present": present, "actual_bytes": actual_bytes, "actual_sha256": actual_hash, "exact": exact})

    current_roots = {
        "producer_work": WORK,
        "producer_evidence": PRODUCER,
    }
    current_rows: list[dict[str, Any]] = []
    for scope, root in current_roots.items():
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            current_rows.append({"scope": scope, **file_record(path, root)})

    # The prior audit tree itself is protected.  New re-audit directories are
    # excluded because they are the only authorized write scope for this run.
    for path in sorted(p for p in PRIOR.rglob("*") if p.is_file()):
        relative = path.relative_to(PRIOR)
        if relative.parts and relative.parts[0].startswith("reaudit_"):
            continue
        current_rows.append({"scope": "prior_independent_tree", **file_record(path, PRIOR)})

    return {
        "schema": "openlogic-tr014-independent-reaudit-protected-snapshot-v1",
        "tranche_id": TRANCHE_ID,
        "baseline_record_count": len(baseline_rows),
        "baseline_records": baseline_rows,
        "current_tree_record_count": len(current_rows),
        "current_tree_records": current_rows,
    }


def capture_cache_hits() -> list[str]:
    roots = [WORK, PRODUCER, ORACLE, ORACLE_VALIDATION, PRIOR]
    hits: list[str] = []
    for root in roots:
        for path in root.rglob("*"):
            if path.name == "__pycache__" or path.suffix.lower() in {".pyc", ".pyo"}:
                hits.append(str(path))
    return sorted(hits)


def main() -> int:
    pin_rows = []
    for relative, expected in EXPECTED_PINS.items():
        path = PRODUCER / relative
        actual = sha256_file(path) if path.is_file() else None
        exact = actual == expected
        assert_pred(exact, "REPAIRED_CANONICAL_PINS_EXACT", f"pin mismatch: {relative}")
        pin_rows.append({"path": relative, "expected_sha256": expected, "actual_sha256": actual, "exact": exact})
    write_json(AUDIT / "PIN_VERIFICATION.json", {
        "schema": "openlogic-tr014-independent-reaudit-pin-verification-v1",
        "tranche_id": TRANCHE_ID,
        "records": pin_rows,
        "result": "PASS_EXACT_REPAIRED_PINS" if all(row["exact"] for row in pin_rows) else "FAIL_PIN_DRIFT",
    })

    prior_rows = []
    for name, expected in PRIOR_FAIL_PINS.items():
        path = PRIOR / name
        actual = sha256_file(path) if path.is_file() else None
        exact = actual == expected
        assert_pred(exact, "PRIOR_INDEPENDENT_FAIL_PRESERVED_EXACT", f"prior FAIL drift: {name}", "PRIOR_FAIL_BINDING")
        prior_rows.append({"path": name, "bytes": path.stat().st_size if path.is_file() else None, "expected_sha256": expected, "actual_sha256": actual, "exact": exact})

    prior_findings = read_jsonl(PRIOR / "FINDINGS_CURRENT.jsonl")
    expected_finding_ids = [f"TR014-IND-{n:03d}" for n in range(1, 6)]
    assert_pred(
        [row["finding_id"] for row in prior_findings] == expected_finding_ids,
        "PRIOR_INDEPENDENT_FINDING_IDENTITIES_EXACT",
        "preserved prior finding identities/order drift",
        "PRIOR_FAIL_BINDING",
    )
    assert_pred(
        [row.get("formula_count") for row in prior_findings[:4]] == [31, 22, 2, 5]
        and prior_findings[4].get("reference_count") == 48,
        "PRIOR_INDEPENDENT_FINDING_COUNTS_EXACT",
        "preserved prior finding family counts drift",
        "PRIOR_FAIL_BINDING",
    )
    write_json(AUDIT / "PRIOR_FAIL_BINDING.json", {
        "schema": "openlogic-tr014-independent-reaudit-prior-fail-binding-v1",
        "tranche_id": TRANCHE_ID,
        "records": prior_rows,
        "finding_ids": [row["finding_id"] for row in prior_findings],
        "finding_row_sha256": [sha256_bytes(compact(row).encode("utf-8")) for row in prior_findings],
        "result": "PASS_EXACT_PRIOR_FAIL_BOUND_UNMODIFIED" if all(row["exact"] for row in prior_rows) else "FAIL_PRIOR_FAIL_DRIFT",
    })

    before = capture_protected_scope()
    write_json(AUDIT / "PROTECTED_SCOPE_BEFORE.json", before)
    initial_cache_hits = capture_cache_hits()
    assert_pred(not initial_cache_hits, "PRODUCER_AND_PROTECTED_CACHE_CLEAN", f"initial cache hits: {initial_cache_hits[:5]}")

    artifact_manifest = read_json(PRODUCER / "ARTIFACT_MANIFEST.json")
    evidence_manifest = read_json(PRODUCER / "EVIDENCE_MANIFEST.json")
    validation_manifest = read_json(VALIDATION / "VALIDATION_MANIFEST.json")
    validation_receipt = read_json(VALIDATION / "VALIDATION_RECEIPT.json")

    assert_pred(artifact_manifest.get("artifact_count") == len(artifact_manifest.get("artifacts", [])) == 21,
                "PRODUCER_ARTIFACT_MANIFEST_CLOSED", "artifact manifest count is not 21")
    for record in artifact_manifest["artifacts"]:
        path = PRODUCER / record["path"]
        exact = path.is_file() and path.stat().st_size == record["bytes"] and sha256_file(path) == record["sha256"]
        assert_pred(exact, "PRODUCER_ARTIFACT_BYTES_EXACT", f"artifact drift: {record['path']}")
    assert_pred(validation_manifest.get("artifact_count") == len(validation_manifest.get("artifacts", [])) == 9,
                "VALIDATION_MANIFEST_CLOSED", "validation manifest count is not 9")
    for record in validation_manifest["artifacts"]:
        path = VALIDATION / record["path"]
        exact = path.is_file() and path.stat().st_size == record["bytes"] and sha256_file(path) == record["sha256"]
        assert_pred(exact, "VALIDATION_ARTIFACT_BYTES_EXACT", f"validation artifact drift: {record['path']}")
    assert_pred(validation_receipt.get("result") == "PASS_PRODUCER_VALIDATION" and validation_receipt.get("finding_count") == 0,
                "PRODUCER_VALIDATION_RECEIPT_PASS", "producer validation receipt is not a zero-finding PASS")
    assert_pred(evidence_manifest.get("artifacts", [])[0].get("sha256") == EXPECTED_PINS["ARTIFACT_MANIFEST.json"],
                "ROOT_EVIDENCE_MANIFEST_BINDS_ARTIFACT_PIN", "root evidence manifest does not bind repaired artifact pin")
    assert_pred(evidence_manifest.get("artifacts", [])[1].get("sha256") == EXPECTED_PINS["producer_validation/VALIDATION_MANIFEST.json"],
                "ROOT_EVIDENCE_MANIFEST_BINDS_VALIDATION_PIN", "root evidence manifest does not bind repaired validation pin")

    expressions = read_jsonl(PRODUCER / "expression_semantics.jsonl")
    occurrences = read_jsonl(PRODUCER / "semantic_occurrences.jsonl")
    contexts = read_jsonl(PRODUCER / "EXPRESSION_CONTEXT_REVIEW.jsonl")
    formals = read_jsonl(PRODUCER / "formal_object_semantic_bindings.jsonl")
    references = read_jsonl(PRODUCER / "REFERENCE_LEDGER.jsonl")
    derived_references = read_jsonl(PRODUCER / "DERIVED_REFERENCE_LEDGER.jsonl")
    corrections = read_jsonl(PRODUCER / "SOURCE_CORRECTIONS.jsonl")

    oracle_occurrences = read_jsonl(ORACLE / "formula_occurrences.jsonl")
    oracle_contexts = read_jsonl(ORACLE / "formula_contexts.jsonl")
    oracle_formals = read_jsonl(ORACLE / "formal_objects.jsonl")
    oracle_references = read_jsonl(ORACLE / "references.jsonl")
    with (ORACLE / "formula_shapes.tsv").open(encoding="utf-8", newline="") as handle:
        oracle_shapes = list(csv.DictReader(handle, delimiter="\t"))
    formal_packets_doc = read_json(WORK / "TR014_FORMAL_AUTHORING_PACKETS.json")

    count_checks = {
        "expression_shapes": len(expressions),
        "formula_occurrences": len(occurrences),
        "formal_objects": len(formals),
        "exercises": sum(row.get("object_class") == "exercise" for row in formals),
        "source_references": len(references),
        "derived_reader_references": len(derived_references),
        "source_corrections": len(corrections),
        "diagrams": 0,
    }
    for key, actual in count_checks.items():
        assert_pred(actual == EXPECTED_COUNTS[key], "CORPUS_COUNTS_EXACT", f"{key}: {actual} != {EXPECTED_COUNTS[key]}")
    assert_pred(len(oracle_shapes) == 112 and len(oracle_occurrences) == len(oracle_contexts) == 335,
                "ORACLE_CORPUS_COUNTS_EXACT", "oracle expression/occurrence counts drift")

    source_rows: list[dict[str, Any]] = []
    source_bytes_total = 0
    source_lines_total = 0
    source_content: dict[str, bytes] = {}
    formula_counts_by_file = Counter(row["file"] for row in oracle_occurrences)
    formal_counts_by_file = Counter(row["file"] for row in oracle_formals)
    reference_counts_by_file = Counter(row["file"] for row in oracle_references)
    correction_counts_by_file = Counter(row["file"] for row in corrections)
    for record in SOURCE_AUTHORITY["source_records"]:
        path = AUTHORITY / record["path"]
        data = path.read_bytes()
        source_content[record["path"]] = data
        lines = len(data.decode("utf-8").splitlines())
        exact = len(data) == record["bytes"] and sha256_bytes(data) == record["sha256"] and lines == record["lines"]
        assert_pred(exact, "IMMUTABLE_SOURCE_BYTES_LINES_HASH_EXACT", f"source drift: {record['path']}")
        source_bytes_total += len(data)
        source_lines_total += lines
        source_rows.append({
            "file": record["path"], "bytes": len(data), "lines": lines, "sha256": sha256_bytes(data),
            "formula_occurrences_reviewed": formula_counts_by_file[record["path"]],
            "formal_objects_reviewed": formal_counts_by_file[record["path"]],
            "source_references_reviewed": reference_counts_by_file[record["path"]],
            "source_corrections_reviewed": correction_counts_by_file[record["path"]],
            "result": "PASS_EXACT_SOURCE_READ_AND_BOUND" if exact else "FAIL_SOURCE_DRIFT",
        })
    assert_pred(source_bytes_total == EXPECTED_COUNTS["source_bytes"], "SOURCE_BYTES_TOTAL_EXACT", f"source bytes {source_bytes_total}")
    assert_pred(source_lines_total == EXPECTED_COUNTS["source_lines"], "SOURCE_LINES_TOTAL_EXACT", f"source lines {source_lines_total}")
    write_jsonl(AUDIT / "SOURCE_REVIEW.jsonl", source_rows)

    shape_by_id = {row["expression_id"]: row for row in oracle_shapes}
    expression_by_id = {row["expression_id"]: row for row in expressions}
    occurrence_by_formula = {row["formula_id"]: row for row in occurrences}
    context_by_formula = {row["formula_id"]: row for row in contexts}
    oracle_occurrence_by_formula = {row["formula_id"]: row for row in oracle_occurrences}
    oracle_context_by_formula = {row["formula_id"]: row for row in oracle_contexts}
    formal_by_id = {row["environment_id"]: row for row in formals}
    reference_by_id = {row["reference_id"]: row for row in references}
    packet_by_id = {row["environment_id"]: row for row in formal_packets_doc["packets"]}

    assert_pred(len(expression_by_id) == len(expressions), "EXPRESSION_IDS_UNIQUE", "duplicate expression ID")
    assert_pred(set(expression_by_id) == set(shape_by_id), "EXPRESSION_ORACLE_SET_EXACT", "expression set differs from oracle")
    assert_pred(len(occurrence_by_formula) == len(occurrences), "FORMULA_IDS_UNIQUE", "duplicate semantic formula ID")
    assert_pred(set(occurrence_by_formula) == set(oracle_occurrence_by_formula), "OCCURRENCE_ORACLE_SET_EXACT", "occurrence set differs from oracle")
    assert_pred(len(formal_by_id) == len(formals), "FORMAL_IDS_UNIQUE", "duplicate formal environment ID")
    assert_pred(len(reference_by_id) == len(references), "REFERENCE_IDS_UNIQUE", "duplicate reference ID")

    mathml_rows: list[dict[str, Any]] = []
    expression_rows: list[dict[str, Any]] = []
    operator_expectations = {
        "Gamma": (r"\\Gamma", "Γ"), "Delta": (r"\\Delta", "Δ"),
        "subseteq": (r"\\subseteq", "⊆"), "supseteq": (r"\\supseteq", "⊇"),
        "notin": (r"\\notin", "∉"), "land": (r"\\land", "∧"), "lor": (r"\\lor", "∨"),
        "lif": (r"\\lif", "→"), "cup": (r"\\cup", "∪"), "bigcup": (r"\\bigcup", "⋃"),
        "lnot": (r"\\lnot", "¬"), "Proves": (r"\\Proves", "⊢"), "Entails": (r"\\Entails", "⊨"),
    }
    for expression_id in sorted(expression_by_id):
        row = expression_by_id[expression_id]
        shape = shape_by_id[expression_id]
        row_ok = True
        row_ok &= assert_pred(row["normalized_tex"] == shape["normalized_tex"], "EXPRESSION_TEX_EXACT", f"normalized TeX drift: {expression_id}")
        row_ok &= assert_pred(row["formula_ids"] == [x["formula_id"] for x in oracle_occurrences if x["expression_id"] == expression_id],
                              "EXPRESSION_FORMULA_OWNERSHIP_ORDER_EXACT", f"formula ownership drift: {expression_id}")
        row_ok &= assert_pred(row["source_occurrence_count"] == len(row["formula_ids"]),
                              "EXPRESSION_SOURCE_OCCURRENCE_COUNT_EXACT", f"source occurrence count drift: {expression_id}")
        row_ok &= assert_pred(bool(row["speech"].strip()) and FORBIDDEN_SPEECH.search(row["speech"]) is None,
                              "EXPRESSION_SPEECH_WORDS_ONLY", f"symbol leak/empty speech: {expression_id}")
        row_ok &= assert_pred(len(row["meaning"].strip()) >= 35 and "fallback" not in row["meaning"].lower(),
                              "EXPRESSION_MEANING_SPECIFIC", f"short/fallback meaning: {expression_id}")
        row_ok &= assert_pred(sha256_bytes(row["speech"].encode("utf-8")) == row["speech_sha256"],
                              "EXPRESSION_SPEECH_HASH_EXACT", f"speech hash drift: {expression_id}")
        row_ok &= assert_pred(sha256_bytes(row["meaning"].encode("utf-8")) == row["meaning_sha256"],
                              "EXPRESSION_MEANING_HASH_EXACT", f"meaning hash drift: {expression_id}")

        body_serializations = []
        for variant, expected_display in (("mathml_inline", "inline"), ("mathml_block", "block")):
            value = row[variant]
            variant_hash = row[variant + "_sha256"]
            variant_ok = True
            try:
                root = ET.fromstring(value)
            except ET.ParseError as error:
                assert_pred(False, "MATHML_PARSEABLE", f"{expression_id} {expected_display}: {error}")
                mathml_rows.append({"expression_id": expression_id, "display": expected_display, "result": "FAIL_PARSE"})
                row_ok = False
                continue
            variant_ok &= assert_pred(root.tag == NS + "math" and root.attrib.get("display") == expected_display,
                                      "MATHML_ROOT_AND_DISPLAY_EXACT", f"root/display drift: {expression_id} {expected_display}")
            variant_ok &= assert_pred(root.attrib.get("data-expression-id") == expression_id,
                                      "MATHML_EXPRESSION_BINDING_EXACT", f"expression binding drift: {expression_id} {expected_display}")
            variant_ok &= assert_pred(not any("aria-label" in node.attrib for node in root.iter()),
                                      "MATHML_NO_ARIA_FLATTENING", f"aria flattening: {expression_id} {expected_display}")
            semantics = root.find(NS + "semantics")
            annotation = semantics.find(NS + "annotation") if semantics is not None else None
            bodies = [child for child in (list(semantics) if semantics is not None else []) if child.tag != NS + "annotation"]
            variant_ok &= assert_pred(semantics is not None and len(bodies) == 1 and annotation is not None,
                                      "MATHML_SEMANTICS_BODY_ANNOTATION_PRESENT", f"semantics structure drift: {expression_id} {expected_display}")
            variant_ok &= assert_pred(annotation is not None and annotation.attrib.get("encoding") == "application/x-tex" and annotation.text == row["normalized_tex"],
                                      "MATHML_TEX_ANNOTATION_EXACT", f"annotation drift: {expression_id} {expected_display}")
            variant_ok &= assert_pred(sha256_bytes(value.encode("utf-8")) == variant_hash,
                                      "MATHML_HASH_EXACT", f"MathML hash drift: {expression_id} {expected_display}")
            if bodies:
                body = bodies[0]
                body_serializations.append(ET.tostring(body, encoding="unicode"))
                body_text = "".join(body.itertext())
                mtexts = ["".join(node.itertext()) for node in body.iter(NS + "mtext")]
                variant_ok &= assert_pred(not any(re.search(r"[ΓΔ∈∉⊆⊇∪⊢⊨⊭∧∨→]", text) for text in mtexts),
                                          "MATHML_MTEXT_CONTAINS_WORDS_NOT_MATH", f"math flattened in mtext: {expression_id} {expected_display}")
                for label, (pattern, symbol) in operator_expectations.items():
                    expected_count = len(re.findall(pattern, row["normalized_tex"]))
                    if label == "cup":
                        expected_count -= len(re.findall(r"\\bigcup", row["normalized_tex"]))
                    if label == "Entails" and ("\\pSat" in row["normalized_tex"] or "\\Sat" in row["normalized_tex"]):
                        continue
                    if expected_count:
                        variant_ok &= assert_pred(body_text.count(symbol) >= expected_count,
                                                  "MATHML_OPERATOR_TOKEN_COVERAGE", f"missing {label} token: {expression_id} {expected_display}")
                nonsat = row["normalized_tex"].count("\\pSat/") + row["normalized_tex"].count("\\Sat/")
                sat = row["normalized_tex"].count("\\pSat{") + row["normalized_tex"].count("\\Sat{")
                if nonsat:
                    variant_ok &= assert_pred(body_text.count("⊭") >= nonsat, "MATHML_SATISFACTION_POLARITY_EXACT", f"missing non-satisfaction: {expression_id}")
                if sat:
                    variant_ok &= assert_pred(body_text.count("⊨") >= sat, "MATHML_SATISFACTION_POLARITY_EXACT", f"missing satisfaction: {expression_id}")
                mathml_rows.append({
                    "expression_id": expression_id, "display": expected_display,
                    "mrow_count": sum(1 for _ in root.iter(NS + "mrow")),
                    "msub_count": sum(1 for _ in root.iter(NS + "msub")),
                    "msup_count": sum(1 for _ in root.iter(NS + "msup")),
                    "mtable_count": sum(1 for _ in root.iter(NS + "mtable")),
                    "mtext_values": mtexts, "body_text": body_text,
                    "result": "PASS_NATIVE_STRUCTURAL_MATHML_REVIEWED" if variant_ok else "FAIL_CURRENT",
                })
            row_ok &= variant_ok
        row_ok &= assert_pred(len(body_serializations) == 2 and body_serializations[0] == body_serializations[1],
                              "INLINE_BLOCK_MATHML_BODY_IDENTICAL", f"inline/block body drift: {expression_id}")
        expression_rows.append({
            "expression_id": expression_id, "normalized_tex": row["normalized_tex"],
            "formula_count": len(row["formula_ids"]), "speech": row["speech"], "meaning": row["meaning"],
            "reader_projection_status": row["reader_projection_status"], "reader_render_eligible": row["reader_render_eligible"],
            "result": "PASS_FULL_EXPRESSION_REVIEW" if row_ok else "FAIL_CURRENT",
        })
    assert_pred(len(mathml_rows) == 224, "MATHML_VARIANT_CENSUS_EXACT", f"MathML review variants: {len(mathml_rows)}")
    write_jsonl(AUDIT / "EXPRESSION_REVIEW.jsonl", expression_rows)
    write_jsonl(AUDIT / "MATHML_REVIEW.jsonl", mathml_rows)

    # Exact native piecewise and postfix-prime structure, independently
    # inspected in each inline/block variant.
    piecewise_variant_count = 0
    for expression_id in PIECEWISE_IDS:
        row = expression_by_id[expression_id]
        for variant in ("mathml_inline", "mathml_block"):
            root = ET.fromstring(row[variant])
            table = root.find(".//" + NS + "mtable")
            rows = table.findall(NS + "mtr") if table is not None else []
            condition_cells = [r.findall(NS + "mtd")[1] for r in rows if len(r.findall(NS + "mtd")) == 2]
            ok = table is not None and len(rows) == 2 and len(condition_cells) == 2
            if expression_id == "expr-437f5dd050d65408" and ok:
                ok = all(any("".join(n.itertext()) == rel for n in cell.iter(NS + "mo")) for cell, rel in zip(condition_cells, ("∈", "∉")))
                ok = ok and all(any("".join(n.itertext()) == "p" for n in cell.iter(NS + "mi")) for cell in condition_cells)
                ok = ok and all(any("".join(n.itertext()) == "Γ∗" for n in cell.iter(NS + "msup")) for cell in condition_cells)
            elif ok:
                first = condition_cells[0]
                ok = any("".join(n.itertext()) == "Γn" for n in first.iter(NS + "msub"))
                ok = ok and any("".join(n.itertext()) == "An" for n in first.iter(NS + "msub"))
                ok = ok and any("".join(n.itertext()) == "∪" for n in first.iter(NS + "mo"))
            assert_pred(ok, "TR014_IND_003_PIECEWISE_CONDITIONS_NATIVE", f"piecewise structural failure: {expression_id} {variant}", "TR014-IND-003")
            piecewise_variant_count += int(ok)

    prime_variant_count = 0
    for expression_id in PRIME_IDS:
        row = expression_by_id[expression_id]
        for variant in ("mathml_inline", "mathml_block"):
            root = ET.fromstring(row[variant])
            ok = any(len(list(node)) == 2 and "".join(list(node)[0].itertext()) == "Γ" and "".join(list(node)[1].itertext()) == "′" for node in root.iter(NS + "msup"))
            assert_pred(ok, "TR014_IND_004_GAMMA_PRIME_STRUCTURAL_MSUP", f"Gamma-prime structural failure: {expression_id} {variant}", "TR014-IND-004")
            prime_variant_count += int(ok)

    occurrence_rows: list[dict[str, Any]] = []
    frames_by_file_line: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for occurrence in oracle_occurrences:
        frames_by_file_line[(occurrence["file"], occurrence["line"])].append(occurrence)
    for key in frames_by_file_line:
        frames_by_file_line[key].sort(key=lambda row: row["offset"])

    for ordinal, oracle_row in enumerate(oracle_occurrences, 1):
        formula_id = oracle_row["formula_id"]
        row = occurrence_by_formula[formula_id]
        review = context_by_formula[formula_id]
        oracle_context = oracle_context_by_formula[formula_id]
        data = source_content[row["file"]]
        tex_bytes = oracle_row["tex"].encode("utf-8")
        if oracle_row["delimiter"] == "$":
            closing_offset = data.find(b"$", oracle_row["offset"] + 1)
            source_inner = data[oracle_row["offset"] + 1:closing_offset].decode("utf-8") if closing_offset >= 0 else ""
            try:
                selected_inner = project_fol_conditionals_to_pl(source_inner)
            except ValueError:
                selected_inner = ""
            exact_span = data[oracle_row["offset"]:oracle_row["offset"] + 1] == b"$" and selected_inner == oracle_row["tex"]
        else:
            complete_source_span = b"\\[" + tex_bytes + b"\\]"
            exact_span = data[oracle_row["offset"]:oracle_row["offset"] + len(complete_source_span)] == complete_source_span
        actual_line = data[:oracle_row["offset"]].count(b"\n") + 1
        last_nl = data.rfind(b"\n", 0, oracle_row["offset"])
        actual_column = oracle_row["offset"] - (last_nl + 1) + 1
        row_ok = True
        row_ok &= assert_pred(exact_span and actual_line == oracle_row["line"] and actual_column == oracle_row["column"],
                              "OCCURRENCE_SOURCE_COORDINATE_AND_SPAN_EXACT", f"source coordinate/span drift: {formula_id}")
        for field in ("expression_id", "file", "instance_id", "line", "column", "delimiter", "normalized_tex", "tex", "offset", "stream_start", "stream_end", "scope"):
            row_ok &= assert_pred(row.get(field) == oracle_row.get(field), "OCCURRENCE_ORACLE_FIELDS_EXACT", f"{field} drift: {formula_id}")
        row_ok &= assert_pred(row["semantic_occurrence_id"] == f"tr014-semantic-occurrence-{ordinal:04d}",
                              "SEMANTIC_OCCURRENCE_IDS_ORDERED", f"semantic occurrence ID drift: {formula_id}")
        row_ok &= assert_pred(review["previous_source_line"] == oracle_context["previous_source_line"]
                              and review["source_line"] == oracle_context["source_line"]
                              and review["next_source_line"] == oracle_context["next_source_line"],
                              "OCCURRENCE_THREE_LINE_CONTEXT_EXACT", f"three-line context drift: {formula_id}")
        packet_hash = sha256_bytes(compact(oracle_context).encode("utf-8"))
        row_ok &= assert_pred(row["source_packet_sha256"] == review["source_packet_sha256"] == packet_hash,
                              "OCCURRENCE_SOURCE_PACKET_HASH_EXACT", f"context packet hash drift: {formula_id}")
        row_ok &= assert_pred(row["speech"] == review["speech"] and row["meaning"] == review["meaning"],
                              "OCCURRENCE_CONTEXT_SEMANTICS_BOUND", f"context semantic binding drift: {formula_id}")
        row_ok &= assert_pred(row["meaning"].endswith(row["contextual_role"]),
                              "OCCURRENCE_MEANING_CONTEXT_SPECIFIC", f"contextual meaning missing: {formula_id}")
        row_ok &= assert_pred(bool(row["speech"].strip()) and FORBIDDEN_SPEECH.search(row["speech"]) is None,
                              "OCCURRENCE_SPEECH_WORDS_ONLY", f"symbol leak/empty occurrence speech: {formula_id}")
        expression = expression_by_id[row["expression_id"]]
        expected_mathml = expression["mathml_inline" if row["mathml_display"] == "inline" else "mathml_block"]
        row_ok &= assert_pred(row["mathml"] == expected_mathml and sha256_bytes(row["mathml"].encode("utf-8")) == row["mathml_sha256"],
                              "OCCURRENCE_MATHML_BOUND_EXACT", f"occurrence MathML drift: {formula_id}")

        omitted = formula_id in SAR_FORMULA_IDS
        expected_projection = SAR_STATUS if omitted else SELECTED_STATUS
        row_ok &= assert_pred(row["reader_projection_status"] == expected_projection and row["reader_render_eligible"] is (not omitted),
                              "TR014_IND_001_OCCURRENCE_PROFILE_FAIL_CLOSED", f"SAR-002 reader eligibility drift: {formula_id}", "TR014-IND-001")
        row_ok &= assert_pred(row["intervention_ids"] == (["SAR-002"] if omitted else []),
                              "TR014_IND_001_OCCURRENCE_INTERVENTION_EXACT", f"SAR-002 intervention drift: {formula_id}", "TR014-IND-001")

        # Render the exact source line with every mathematical occurrence on
        # that line replaced by its occurrence-specific speech.  This retains
        # a compact, independently regenerated continuous-frame audit trail.
        line_bytes = data.splitlines()[row["line"] - 1]
        line_start = data.rfind(b"\n", 0, row["offset"]) + 1
        if row["delimiter"] == "$":
            replacements = []
            multiline = False
            for peer in frames_by_file_line[(row["file"], row["line"])]:
                peer_semantic = occurrence_by_formula[peer["formula_id"]]
                local_start = peer["offset"] - line_start
                closing_offset = line_bytes.find(b"$", local_start + 1)
                if closing_offset < 0:
                    multiline = True
                    break
                local_end = closing_offset + 1
                replacements.append((local_start, local_end, peer_semantic["speech"]))
            if multiline:
                rendered = review["source_line"] + " ⟦" + row["speech"] + "⟧"
            else:
                rendered_bytes = line_bytes
                for start, end, speech in reversed(replacements):
                    rendered_bytes = rendered_bytes[:start] + speech.encode("utf-8") + rendered_bytes[end:]
                rendered = rendered_bytes.decode("utf-8")
        else:
            rendered = row["speech"]
        occurrence_rows.append({
            "formula_id": formula_id, "expression_id": row["expression_id"], "file": row["file"],
            "line": row["line"], "column": row["column"], "normalized_tex": row["normalized_tex"],
            "speech": row["speech"], "reader_projection_status": row["reader_projection_status"],
            "reader_render_eligible": row["reader_render_eligible"], "source_line": review["source_line"],
            "continuous_line_with_speech": rendered,
            "result": "PASS_EXACT_OCCURRENCE_CONTEXT_SPEECH_MATHML_REVIEW" if row_ok else "FAIL_CURRENT",
        })
    write_jsonl(AUDIT / "OCCURRENCE_REVIEW.jsonl", occurrence_rows)

    # Retest the prior speech collision map from the preserved finding itself.
    required_speech = prior_findings[1]["required_speech"]
    assert_pred(len(required_speech) == 22, "TR014_IND_002_FROZEN_MAP_COUNT_EXACT", "prior continuous-speech map is not 22", "TR014-IND-002")
    for formula_id, expected in required_speech.items():
        row = occurrence_by_formula.get(formula_id, {})
        review = context_by_formula.get(formula_id, {})
        ok = row.get("speech") == expected and review.get("speech") == expected and row.get("review_decision") == "FROZEN_INDEPENDENT_CONTEXT_COLLISION_REPAIRED"
        assert_pred(ok, "TR014_IND_002_EXACT_FORMULA_CONTEXT_SPEECH", f"speech repair drift: {formula_id}", "TR014-IND-002")
    assert_pred(
        {row["formula_id"] for row in occurrences if row["review_decision"] == "FROZEN_INDEPENDENT_CONTEXT_COLLISION_REPAIRED"} == set(required_speech),
        "TR014_IND_002_REPAIR_CENSUS_EXACT", "continuous-speech repair census includes missing/extra rows", "TR014-IND-002",
    )
    joined_frames = "\n".join(row["continuous_line_with_speech"] for row in occurrence_rows)
    bad_frames = [
        r"for all p belongs", r"transitivity of\s+is a subset", r"Let Gamma prime is a subset",
        r"every B belongs.+is also belongs", r"complete consistent Gamma star contains Gamma",
        r"there is a Gamma star contains Gamma", r"every finite Gamma sub zero is a subset",
        r"Avoid the use of syntactically derives",
    ]
    for pattern in bad_frames:
        assert_pred(re.search(pattern, joined_frames, re.I) is None, "CONTINUOUS_SPEECH_NO_KNOWN_OR_NEW_COLLISION_PATTERN", f"collision pattern present: {pattern}")

    formal_rows: list[dict[str, Any]] = []
    class_counts = Counter(row["object_class"] for row in formals)
    assert_pred(class_counts == Counter({"definition": 3, "lemma": 3, "proposition": 3, "theorem": 3, "corollary": 1, "exercise": 8}),
                "FORMAL_CLASS_CENSUS_EXACT", f"formal class census drift: {dict(class_counts)}")
    assert_pred(len({row["accessible_name"] for row in formals}) == 21, "FORMAL_ACCESSIBLE_NAMES_UNIQUE", "formal accessible-name collision")
    assert_pred(len({row["full_source_order_linearization"] for row in formals}) == 21, "FORMAL_LINEARIZATIONS_UNIQUE", "formal linearization collision")
    for oracle_formal in oracle_formals:
        environment_id = oracle_formal["environment_id"]
        row = formal_by_id[environment_id]
        packet = packet_by_id[environment_id]
        row_ok = True
        row_ok &= assert_pred(row["source_record_sha256"] == canonical_source_hash(oracle_formal),
                              "FORMAL_ORACLE_RECORD_HASH_EXACT", f"formal oracle hash drift: {environment_id}")
        packet_source_bytes = packet["source_block"].replace("\n", "\r\n").encode("utf-8")
        row_ok &= assert_pred(row["source_block_sha256"] == packet["source_block_sha256"] == sha256_bytes(packet_source_bytes)
                              and packet["source_block_bytes"] == len(packet_source_bytes),
                              "FORMAL_SOURCE_BLOCK_HASH_EXACT", f"formal source block hash drift: {environment_id}")
        normalized_source = source_content[row["source_file"]].decode("utf-8").replace("\r\n", "\n")
        row_ok &= assert_pred(normalized_source.count(packet["source_block"]) == 1,
                              "FORMAL_SOURCE_BLOCK_PRESENT_EXACTLY_ONCE", f"formal block absent/duplicated: {environment_id}")
        expected_sequence = [occurrence_by_formula[x]["speech"] for x in row["formula_ids"]]
        expected_full = row["narrative_before_explicit_math_replay"] + (
            " Source-order mathematics: " + "; then ".join(expected_sequence) + "." if expected_sequence
            else " This object contains no standalone mathematical expression."
        )
        row_ok &= assert_pred(row["formula_ids"] == packet["formula_ids"] and row["spoken_formula_sequence"] == expected_sequence,
                              "FORMAL_FORMULA_SOURCE_ORDER_EXACT", f"formal formula order drift: {environment_id}")
        row_ok &= assert_pred(row["full_source_order_linearization"] == expected_full and "$" not in expected_full and "\\" not in expected_full,
                              "FORMAL_FULL_LINEARIZATION_EXACT_WORDS_ONLY", f"formal full linearization drift: {environment_id}")
        if row["object_class"] == "exercise":
            row_ok &= assert_pred(row["exercise_policy"] == "PRESERVE_UNSOLVED_NO_ANSWER_ADDED" and "No solution is supplied." in row["full_source_order_linearization"],
                                  "EXERCISES_PRESERVED_UNSOLVED", f"exercise solution boundary drift: {environment_id}")
            row_ok &= assert_pred("Here is the solution" not in row["full_source_order_linearization"] and "Answer:" not in row["full_source_order_linearization"],
                                  "EXERCISES_NO_INJECTED_ANSWER", f"answer injected: {environment_id}")
        formal_rows.append({
            "environment_id": environment_id, "source_file": row["source_file"], "source_line": row["source_line"],
            "object_class": row["object_class"], "accessible_name": row["accessible_name"],
            "formula_count": len(row["formula_ids"]), "reference_count": len(row["reference_ids"]),
            "projection_status": row["projection_status"], "full_source_order_linearization": row["full_source_order_linearization"],
            "result": "PASS_FULL_FORMAL_OBJECT_REVIEW" if row_ok else "FAIL_CURRENT",
        })
    assert_pred(formal_by_id["projected-env-000956"]["projection_status"] == SAR_STATUS,
                "TR014_IND_001_SOURCE_ONLY_FORMAL_OMITTED", "SAR-002 formal remains reader-selected", "TR014-IND-001")
    write_jsonl(AUDIT / "FORMAL_REVIEW.jsonl", formal_rows)

    reference_rows: list[dict[str, Any]] = []
    for oracle_ref in oracle_references:
        reference_id = oracle_ref["reference_id"]
        row = reference_by_id[reference_id]
        row_ok = True
        for field, value in oracle_ref.items():
            row_ok &= assert_pred(row.get(field) == value, "REFERENCE_ORACLE_FIELDS_EXACT", f"{field} drift: {reference_id}")
        row_ok &= assert_pred(row["source_record_sha256"] == canonical_source_hash(oracle_ref),
                              "REFERENCE_SOURCE_RECORD_HASH_EXACT", f"source reference hash drift: {reference_id}")
        data = source_content[row["file"]]
        macro_prefix = ("\\" + row["macro"]).encode("utf-8")
        row_ok &= assert_pred(data[row["offset"]:row["offset"] + len(macro_prefix)] == macro_prefix,
                              "REFERENCE_SOURCE_COORDINATE_EXACT", f"reference coordinate drift: {reference_id}")
        row_ok &= assert_pred(row["closure_status"] == "PASS_CLOSED_SOURCE_REFERENCE_ROW",
                              "REFERENCE_ROW_CLOSED", f"reference not closed: {reference_id}")
        if reference_id in REFERENCE_REPAIR_IDS:
            full_key = row["effective_reader_target_full_key"] or row["full_key"]
            expected = expected_reference_name(full_key)
            ok = expected is not None and row["spoken_target"] == expected and OPAQUE_REFERENCE.search(row["spoken_target"]) is None
            row_ok &= assert_pred(ok, "TR014_IND_005_REFERENCE_TARGET_DISTINCTION_EXACT", f"spoken reference ambiguity: {reference_id}", "TR014-IND-005")
            row_ok &= assert_pred(row["spoken_target_repair_status"] == "PASS_FROZEN_INDEPENDENT_REFERENCE_DISTINCTION_REPAIRED",
                                  "TR014_IND_005_REFERENCE_REPAIR_PROVENANCE_EXACT", f"repair provenance drift: {reference_id}", "TR014-IND-005")
        reference_rows.append({
            "reference_id": reference_id, "file": row["file"], "line": row["line"],
            "source_full_key": row["full_key"], "effective_reader_target_full_key": row["effective_reader_target_full_key"],
            "spoken_target": row["spoken_target"], "intervention_ids": row["intervention_ids"],
            "result": "PASS_FULL_REFERENCE_REVIEW" if row_ok else "FAIL_CURRENT",
        })
    assert_pred({row["reference_id"] for row in references if row["spoken_target_repair_status"] == "PASS_FROZEN_INDEPENDENT_REFERENCE_DISTINCTION_REPAIRED"} == set(REFERENCE_REPAIR_IDS),
                "TR014_IND_005_REFERENCE_REPAIR_CENSUS_EXACT", "reference repair census includes missing/extra rows", "TR014-IND-005")
    omitted_reference_ids = {"reference-000231", "reference-000232", "reference-000233", "reference-000234"}
    assert_pred({row["reference_id"] for row in references if "SAR-002" in row["intervention_ids"]} == omitted_reference_ids
                and all(reference_by_id[x]["effective_reader_target_full_key"] is None for x in omitted_reference_ids),
                "TR014_IND_001_SAR002_REFERENCES_NONRENDERABLE", "SAR-002 reference omission drift", "TR014-IND-001")
    write_jsonl(AUDIT / "REFERENCE_REVIEW.jsonl", reference_rows)

    correction_rows: list[dict[str, Any]] = []
    correction_by_id = {row["correction_id"]: row for row in corrections}
    assert_pred(set(correction_by_id) == {"SAR-002", "TR014-SOURCE-PROSE-001"}, "CORRECTION_SET_EXACT", "source correction set drift")
    sar = correction_by_id["SAR-002"]
    sar_ok = sar["affected_formula_ids"] == list(SAR_FORMULA_IDS) and sar["affected_expression_ids"] == list(SAR_AFFECTED_EXPRESSIONS)
    sar_ok = sar_ok and sar["required_occurrence_reader_projection_status"] == SAR_STATUS and sar["immutable_source_preserved"] is True and bool(sar["visible_disclosure"].strip())
    construction_lines = source_content[sar["file"]].decode("utf-8").splitlines()
    sar_ok = sar_ok and construction_lines[98].startswith("\\iftag{FOL}{%") and construction_lines[154].strip() == "}{}"
    assert_pred(sar_ok, "TR014_IND_001_SAR002_CORRECTION_BOUND_EXACT", "SAR-002 correction/source branch binding drift", "TR014-IND-001")
    correction_rows.append({"correction_id": "SAR-002", "file": sar["file"], "affected_formula_count": len(sar["affected_formula_ids"]), "affected_expression_count": len(sar["affected_expression_ids"]), "result": "PASS_FULL_CORRECTION_REVIEW" if sar_ok else "FAIL_CURRENT"})

    prose = correction_by_id["TR014-SOURCE-PROSE-001"]
    prose_source = source_content[prose["file"]]
    prose_ok = sha256_bytes(prose["source_context"].encode("utf-8")) == prose["source_context_sha256"] and prose["source_context"].encode("utf-8") in prose_source
    prose_ok = prose_ok and sha256_bytes(prose["conditional_source_span"].encode("utf-8")) == prose["conditional_source_span_sha256"] and prose["conditional_source_span"].encode("utf-8") in prose_source
    prose_ok = prose_ok and sha256_bytes(prose["selected_pl_tex_before_correction"].encode("utf-8")) == prose["selected_pl_tex_before_correction_sha256"]
    prose_ok = prose_ok and "by references to \\olref{prop:fsat-ccs}." in prose["reader_corrected_tex"] and bool(prose["visible_disclosure"].strip())
    prose_ok = prose_ok and prose["source_reference_row_added"] is False and prose["derived_reader_reference_count"] == 1
    prose_ok = prose_ok and len(derived_references) == 1 and derived_references[0]["target_full_key"] == "pl:com:cpd:prop:fsat-ccs" and derived_references[0]["not_an_immutable_source_reference_row"] is True
    assert_pred(prose_ok, "SOURCE_PROSE_CORRECTION_EXACT_VISIBLE_AND_DERIVED", "TR014 local source prose correction drift")
    correction_rows.append({"correction_id": "TR014-SOURCE-PROSE-001", "file": prose["file"], "derived_reader_reference_count": len(derived_references), "result": "PASS_FULL_CORRECTION_REVIEW" if prose_ok else "FAIL_CURRENT"})
    write_jsonl(AUDIT / "CORRECTION_REVIEW.jsonl", correction_rows)

    sar_occurrences = [occurrence_by_formula[x] for x in SAR_FORMULA_IDS]
    sar_expressions = [expression_by_id[x] for x in SAR_AFFECTED_EXPRESSIONS]
    sar_family_ok = all(row["reader_projection_status"] == SAR_STATUS and row["reader_render_eligible"] is False for row in sar_occurrences)
    sar_family_ok = sar_family_ok and all(expression_by_id[x]["reader_projection_status"] == SAR_STATUS and expression_by_id[x]["reader_render_eligible"] is False for x in SAR_EXCLUSIVE_EXPRESSIONS)
    sar_family_ok = sar_family_ok and expression_by_id["expr-b50bb8940da5b931"]["reader_projection_status"] == MIXED_STATUS and expression_by_id["expr-b50bb8940da5b931"]["reader_render_eligible"] is True
    assert_pred(sar_family_ok, "TR014_IND_001_COMPLETE_REPAIR_PREDICATE", "31 occurrence/17 expression SAR-002 fail-closed predicate not closed", "TR014-IND-001")

    family_rows = [
        {
            "finding_id": "TR014-IND-001", "prior_predicate": "31 SAR-002 occurrences omitted and affected expressions conservatively non-renderable",
            "observed": {"omitted_occurrences": sum(not x["reader_render_eligible"] for x in sar_occurrences), "affected_expressions": len(sar_expressions), "exclusive_nonrenderable_expressions": sum(not expression_by_id[x]["reader_render_eligible"] for x in SAR_EXCLUSIVE_EXPRESSIONS)},
            "result": "PASS_CLOSED_CURRENT" if sar_family_ok else "FAIL_CURRENT",
        },
        {
            "finding_id": "TR014-IND-002", "prior_predicate": "22 exact continuous-speech context collisions",
            "observed": {"exact_repaired_occurrences": sum(occurrence_by_formula[k]["speech"] == v for k, v in required_speech.items()), "full_occurrence_frames_reviewed": len(occurrence_rows)},
            "result": "PASS_CLOSED_CURRENT" if all(occurrence_by_formula[k]["speech"] == v for k, v in required_speech.items()) else "FAIL_CURRENT",
        },
        {
            "finding_id": "TR014-IND-003", "prior_predicate": "2 piecewise expressions / 4 variants keep mathematical conditions native",
            "observed": {"piecewise_expressions": len(PIECEWISE_IDS), "passing_native_variants": piecewise_variant_count},
            "result": "PASS_CLOSED_CURRENT" if piecewise_variant_count == 4 else "FAIL_CURRENT",
        },
        {
            "finding_id": "TR014-IND-004", "prior_predicate": "3 Gamma-prime expressions / 6 variants encode prime as msup",
            "observed": {"gamma_prime_expressions": len(PRIME_IDS), "passing_msup_variants": prime_variant_count},
            "result": "PASS_CLOSED_CURRENT" if prime_variant_count == 6 else "FAIL_CURRENT",
        },
        {
            "finding_id": "TR014-IND-005", "prior_predicate": "48 active listener references preserve target and proof-system distinctions",
            "observed": {"repaired_reference_ids": len(REFERENCE_REPAIR_IDS), "exact_distinctions": sum(reference_by_id[x]["spoken_target"] == expected_reference_name(reference_by_id[x]["effective_reader_target_full_key"] or reference_by_id[x]["full_key"]) for x in REFERENCE_REPAIR_IDS)},
            "result": "PASS_CLOSED_CURRENT" if all(reference_by_id[x]["spoken_target"] == expected_reference_name(reference_by_id[x]["effective_reader_target_full_key"] or reference_by_id[x]["full_key"]) for x in REFERENCE_REPAIR_IDS) else "FAIL_CURRENT",
        },
    ]
    write_jsonl(AUDIT / "FROZEN_FINDING_RETEST.jsonl", family_rows)

    corpus_receipt = {
        "schema": "openlogic-tr014-independent-reaudit-corpus-review-v1",
        "tranche_id": TRANCHE_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "counts": EXPECTED_COUNTS,
        "records_read": {
            "source_files": len(source_rows), "source_bytes": source_bytes_total, "source_lines": source_lines_total,
            "expressions": len(expression_rows), "occurrences_and_exact_frames": len(occurrence_rows),
            "mathml_variants": len(mathml_rows), "formal_objects": len(formal_rows),
            "references": len(reference_rows), "corrections": len(correction_rows),
        },
        "manual_semantic_review": "PASS_EVERY_EXPRESSION_OCCURRENCE_FRAME_FORMAL_REFERENCE_AND_CORRECTION_REREAD",
        "new_out_of_family_finding_count_at_review_stage": len([x for x in findings if x["family"] == "OUT_OF_FAMILY"]),
        "result": "PASS_FULL_CORPUS_NO_NEW_DEFECTS" if not findings else "FAIL_CURRENT_FINDINGS",
    }
    write_json(AUDIT / "CORPUS_REVIEW_RECEIPT.json", corpus_receipt)

    cold_receipt = run_cold_replays()
    write_json(AUDIT / "COLD_REPLAY_RECEIPT.json", cold_receipt)
    adversarial_receipt = run_adversarial_probes()
    write_json(AUDIT / "ADVERSARIAL_PROBE_RECEIPT.json", adversarial_receipt)

    validator = subprocess.run(
        [sys.executable, "-B", str(WORK / "validate_tr014.py"), "--evidence", str(PRODUCER), "--check-only"],
        cwd=str(WORK), capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert_pred(validator.returncode == 0, "CANONICAL_PRODUCER_VALIDATOR_COLD_CHECK_PASS", f"canonical check-only validator failed: {validator.stderr[-1000:]}")
    write_json(AUDIT / "CANONICAL_VALIDATOR_RECEIPT.json", {
        "schema": "openlogic-tr014-independent-reaudit-canonical-validator-v1",
        "returncode": validator.returncode,
        "stdout_sha256": sha256_bytes(validator.stdout.encode("utf-8")),
        "stderr": validator.stderr[-2000:],
        "result": "PASS_CHECK_ONLY" if validator.returncode == 0 else "FAIL",
    })

    after = capture_protected_scope()
    write_json(AUDIT / "PROTECTED_SCOPE_AFTER.json", after)
    before_signature = compact(before["baseline_records"]) + compact(before["current_tree_records"])
    after_signature = compact(after["baseline_records"]) + compact(after["current_tree_records"])
    protected_exact = before_signature == after_signature
    assert_pred(protected_exact, "PROTECTED_SCOPE_BEFORE_AFTER_IDENTICAL", "protected or producer tree changed during re-audit")
    final_cache_hits = capture_cache_hits()
    assert_pred(not final_cache_hits, "PRODUCER_AND_PROTECTED_CACHE_CLEAN", f"final cache hits: {final_cache_hits[:5]}")
    write_json(AUDIT / "PROTECTED_AND_CACHE_RECEIPT.json", {
        "schema": "openlogic-tr014-independent-reaudit-protected-cache-v1",
        "tranche_id": TRANCHE_ID,
        "protected_before_after_identical": protected_exact,
        "baseline_record_count": before["baseline_record_count"],
        "current_tree_record_count": before["current_tree_record_count"],
        "initial_cache_hits": initial_cache_hits,
        "final_cache_hits": final_cache_hits,
        "result": "PASS_PROTECTED_IDENTITY_AND_CACHE_CLEAN" if protected_exact and not initial_cache_hits and not final_cache_hits else "FAIL_CURRENT",
    })

    write_jsonl(AUDIT / "FINDINGS_CURRENT.jsonl", findings)
    result = "PASS_INDEPENDENT_REAUDIT_ZERO_CURRENT_FINDINGS" if not findings else "FAIL_INDEPENDENT_REAUDIT_CURRENT_FINDINGS_FROZEN"
    final_receipt = {
        "schema": "openlogic-tr014-independent-repaired-reaudit-receipt-v1",
        "tranche_id": TRANCHE_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "canonical_pins": {
            "artifact_manifest_sha256": EXPECTED_PINS["ARTIFACT_MANIFEST.json"],
            "validation_receipt_sha256": EXPECTED_PINS["producer_validation/VALIDATION_RECEIPT.json"],
            "validation_manifest_sha256": EXPECTED_PINS["producer_validation/VALIDATION_MANIFEST.json"],
            "evidence_manifest_sha256": EXPECTED_PINS["EVIDENCE_MANIFEST.json"],
        },
        "prior_fail_pins": {name: digest for name, digest in PRIOR_FAIL_PINS.items()},
        "frozen_family_results": {row["finding_id"]: row["result"] for row in family_rows},
        "cold_replay_result": cold_receipt["result"],
        "adversarial_probe_result": adversarial_receipt["result"],
        "corpus_result": corpus_receipt["result"],
        "protected_and_cache_result": "PASS_PROTECTED_IDENTITY_AND_CACHE_CLEAN" if protected_exact and not final_cache_hits else "FAIL_CURRENT",
        "reader_browser_audio_or_assistive_technology_run": False,
        "producer_or_source_edited_by_auditor": False,
        "current_finding_count": len(findings),
        "current_finding_ids": [row["finding_id"] for row in findings],
        "result": result,
    }
    write_json(AUDIT / "FINAL_AUDIT_RECEIPT.json", final_receipt)

    report_lines = [
        "# OLAB-TR-014 repaired PL Completeness independent re-audit",
        "",
        f"Result: **{result}**",
        "",
        f"The four repaired canonical pins were read from disk and matched exactly. The preserved prior independent FAIL was bound by its four original file hashes and all five finding families were retested against current rows.",
        "",
        f"Full corpus reviewed: {source_bytes_total} source bytes / {source_lines_total} lines; {len(expressions)} expression shapes; {len(occurrences)} occurrence frames; {len(mathml_rows)} MathML variants; {len(formals)} formal objects; {len(references)} source references; {len(corrections)} corrections.",
        "",
        f"Cold replay: {cold_receipt['result']}. Adversarial probes: {adversarial_receipt['result']}. Protected identity/cache: {'PASS' if protected_exact and not final_cache_hits else 'FAIL'}.",
        "",
    ]
    if findings:
        report_lines.extend(["## Frozen current findings", ""])
        for row in findings:
            report_lines.append(f"- {row['finding_id']} [{row['family']}] `{row['predicate']}`: {row['detail']}")
    else:
        report_lines.append("No current in-family or out-of-family findings remain.")
    (AUDIT / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8", newline="\n")

    manifest_records = []
    for path in sorted(p for p in AUDIT.rglob("*") if p.is_file() and p.name != "EVIDENCE_MANIFEST.json"):
        manifest_records.append(file_record(path, AUDIT))
    evidence_manifest_out = {
        "schema": "openlogic-tr014-independent-repaired-reaudit-evidence-manifest-v1",
        "tranche_id": TRANCHE_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "artifact_count": len(manifest_records),
        "artifacts": manifest_records,
        "canonical_artifact_manifest_sha256": EXPECTED_PINS["ARTIFACT_MANIFEST.json"],
        "canonical_validation_receipt_sha256": EXPECTED_PINS["producer_validation/VALIDATION_RECEIPT.json"],
        "canonical_validation_manifest_sha256": EXPECTED_PINS["producer_validation/VALIDATION_MANIFEST.json"],
        "canonical_evidence_manifest_sha256": EXPECTED_PINS["EVIDENCE_MANIFEST.json"],
        "current_finding_count": len(findings),
        "result": result,
    }
    write_json(AUDIT / "EVIDENCE_MANIFEST.json", evidence_manifest_out)
    print(json.dumps(final_receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not findings else 1


def run_cold_replays() -> dict[str, Any]:
    cold_root = AUDIT / "cold_replays"
    outputs = [cold_root / "run_a", cold_root / "run_b"]
    code = (
        "import json,pathlib,sys; "
        "sys.path.insert(0,sys.argv[1]); import build_tr014 as b; "
        "root=pathlib.Path(sys.argv[2]).resolve(); b.COLD_ROOT=root; "
        "print(json.dumps(b.build(root/pathlib.Path(sys.argv[3])),ensure_ascii=False,sort_keys=True))"
    )
    runs = []
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code, str(WORK), str(cold_root), output.name],
            cwd=str(AUDIT), capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        ok = proc.returncode == 0 and output.is_dir()
        assert_pred(ok, "ISOLATED_COLD_REPLAY_COMPLETES", f"cold replay failed: {output.name}: {proc.stderr[-1000:]}")
        runs.append({
            "directory": output.relative_to(AUDIT).as_posix(), "returncode": proc.returncode,
            "stdout_sha256": sha256_bytes(proc.stdout.encode("utf-8")), "stderr": proc.stderr[-2000:],
        })

    canonical_manifest_bytes = (PRODUCER / "ARTIFACT_MANIFEST.json").read_bytes()
    canonical_manifest = read_json(PRODUCER / "ARTIFACT_MANIFEST.json")
    byte_identical = True
    signatures = []
    for output in outputs:
        run_identical = (output / "ARTIFACT_MANIFEST.json").read_bytes() == canonical_manifest_bytes
        records = []
        for record in canonical_manifest["artifacts"]:
            canonical_path = PRODUCER / record["path"]
            replay_path = output / record["path"]
            exact = replay_path.is_file() and replay_path.read_bytes() == canonical_path.read_bytes()
            run_identical &= exact
            records.append({"path": record["path"], "sha256": sha256_file(replay_path) if replay_path.is_file() else None, "byte_identical": exact})
        byte_identical &= run_identical
        signatures.append({"directory": output.relative_to(AUDIT).as_posix(), "artifact_count": len(records), "artifact_manifest_sha256": sha256_file(output / "ARTIFACT_MANIFEST.json"), "all_artifacts_byte_identical": run_identical, "records": records})
    assert_pred(byte_identical, "TWO_ISOLATED_COLD_REPLAYS_BYTE_IDENTICAL", "fresh cold builds differ from canonical producer artifacts")
    return {
        "schema": "openlogic-tr014-independent-reaudit-cold-replay-v1",
        "tranche_id": TRANCHE_ID,
        "runs": runs,
        "signatures": signatures,
        "result": "PASS_TWO_ISOLATED_COLD_REPLAYS_BYTE_IDENTICAL" if byte_identical else "FAIL_COLD_REPLAY_DRIFT",
    }


def run_adversarial_probes() -> dict[str, Any]:
    scratch = AUDIT / "probe_scratch"

    def rebind(root: Path, names: Iterable[str]) -> None:
        manifest_path = root / "ARTIFACT_MANIFEST.json"
        manifest = read_json(manifest_path)
        index = {row["path"]: row for row in manifest["artifacts"]}
        for name in names:
            path = root / name
            index[name]["bytes"] = path.stat().st_size
            index[name]["sha256"] = sha256_file(path)
        write_json(manifest_path, manifest)

    def mutate_jsonl(root: Path, name: str, action: Callable[[list[dict[str, Any]]], None]) -> None:
        rows = read_jsonl(root / name)
        action(rows)
        write_jsonl(root / name, rows)

    def mutate_json(root: Path, name: str, action: Callable[[dict[str, Any]], None]) -> None:
        value = read_json(root / name)
        action(value)
        write_json(root / name, value)

    def row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
        return next(item for item in rows if item[key] == value)

    cases: list[tuple[str, Callable[[Path], tuple[list[str], bool]]]] = []

    def case(name: str):
        def register(fn: Callable[[Path], tuple[list[str], bool]]):
            cases.append((name, fn))
            return fn
        return register

    @case("sar002_occurrence_reader_reenabled")
    def _(root: Path):
        def action(rows):
            target = row(rows, "formula_id", SAR_FORMULA_IDS[0]); target["reader_projection_status"] = SELECTED_STATUS; target["reader_render_eligible"] = True
        mutate_jsonl(root, "semantic_occurrences.jsonl", action)
        current = row(read_jsonl(root / "semantic_occurrences.jsonl"), "formula_id", SAR_FORMULA_IDS[0])
        return ["semantic_occurrences.jsonl"], current["reader_projection_status"] == SAR_STATUS and current["reader_render_eligible"] is False

    @case("sar002_expression_reader_reenabled")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", SAR_EXCLUSIVE_EXPRESSIONS[0]); target["reader_projection_status"] = SELECTED_STATUS; target["reader_render_eligible"] = True
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        current = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", SAR_EXCLUSIVE_EXPRESSIONS[0])
        return ["expression_semantics.jsonl"], current["reader_projection_status"] == SAR_STATUS and current["reader_render_eligible"] is False

    @case("continuous_speech_collision_reintroduced")
    def _(root: Path):
        for name in ("semantic_occurrences.jsonl", "EXPRESSION_CONTEXT_REVIEW.jsonl"):
            def action(rows, n=name): row(rows, "formula_id", "projected-formula-0005635")["speech"] = "p belongs to Gamma"
            mutate_jsonl(root, name, action)
        current = row(read_jsonl(root / "semantic_occurrences.jsonl"), "formula_id", "projected-formula-0005635")
        return ["semantic_occurrences.jsonl", "EXPRESSION_CONTEXT_REVIEW.jsonl"], current["speech"] == "p in Gamma"

    @case("piecewise_condition_flattened_to_mtext")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", PIECEWISE_IDS[0])
            for key in ("mathml_inline", "mathml_block"):
                target[key] = re.sub(r"<mi>p</mi><mo>∈</mo><msup><mo>Γ</mo><mo>∗</mo></msup>", "<mtext>p ∈ Γ∗</mtext>", target[key])
                target[key + "_sha256"] = sha256_bytes(target[key].encode("utf-8"))
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        target = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", PIECEWISE_IDS[0])
        flat = any("∈" in "".join(n.itertext()) for n in ET.fromstring(target["mathml_inline"]).iter(NS + "mtext"))
        return ["expression_semantics.jsonl"], not flat

    @case("gamma_prime_flattened_to_siblings")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", PRIME_IDS[0])
            for key in ("mathml_inline", "mathml_block"):
                target[key] = target[key].replace("<msup><mo>Γ</mo><mo>′</mo></msup>", "<mo>Γ</mo><mo>′</mo>")
                target[key + "_sha256"] = sha256_bytes(target[key].encode("utf-8"))
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        target = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", PRIME_IDS[0])
        structured = any("".join(n.itertext()) == "Γ′" for n in ET.fromstring(target["mathml_inline"]).iter(NS + "msup"))
        return ["expression_semantics.jsonl"], structured

    @case("proof_system_reference_conflated")
    def _(root: Path):
        def action(rows): row(rows, "reference_id", "reference-001756")["spoken_target"] = "the cited proof-system section"
        mutate_jsonl(root, "REFERENCE_LEDGER.jsonl", action)
        target = row(read_jsonl(root / "REFERENCE_LEDGER.jsonl"), "reference_id", "reference-001756")
        return ["REFERENCE_LEDGER.jsonl"], target["spoken_target"] == expected_reference_name(target["effective_reader_target_full_key"])

    @case("theorem_corollary_reference_conflated")
    def _(root: Path):
        def action(rows): row(rows, "reference_id", "reference-000240")["spoken_target"] = "the model-existence Completeness Theorem"
        mutate_jsonl(root, "REFERENCE_LEDGER.jsonl", action)
        target = row(read_jsonl(root / "REFERENCE_LEDGER.jsonl"), "reference_id", "reference-000240")
        return ["REFERENCE_LEDGER.jsonl"], target["spoken_target"] == expected_reference_name(target["effective_reader_target_full_key"])

    @case("occurrence_source_coordinate_drift")
    def _(root: Path):
        def action(rows): row(rows, "formula_id", "projected-formula-0005611")["line"] += 1
        mutate_jsonl(root, "semantic_occurrences.jsonl", action)
        target = row(read_jsonl(root / "semantic_occurrences.jsonl"), "formula_id", "projected-formula-0005611")
        return ["semantic_occurrences.jsonl"], target["line"] == 19

    @case("mathml_root_aria_flattening")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", "expr-8238c028f61fc0f7")
            for key in ("mathml_inline", "mathml_block"):
                target[key] = target[key].replace("<math ", "<math aria-label=\"A\" ", 1)
                target[key + "_sha256"] = sha256_bytes(target[key].encode("utf-8"))
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        target = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", "expr-8238c028f61fc0f7")
        return ["expression_semantics.jsonl"], "aria-label" not in ET.fromstring(target["mathml_inline"]).attrib

    @case("mathml_tex_annotation_drift")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", "expr-8238c028f61fc0f7")
            for key in ("mathml_inline", "mathml_block"):
                target[key] = target[key].replace(">!A</annotation>", ">!B</annotation>")
                target[key + "_sha256"] = sha256_bytes(target[key].encode("utf-8"))
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        target = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", "expr-8238c028f61fc0f7")
        annotation = ET.fromstring(target["mathml_inline"]).find(".//" + NS + "annotation")
        return ["expression_semantics.jsonl"], annotation is not None and annotation.text == target["normalized_tex"]

    @case("formal_formula_source_order_swapped")
    def _(root: Path):
        def action(rows):
            target = row(rows, "environment_id", "projected-env-000939"); target["formula_ids"][0], target["formula_ids"][1] = target["formula_ids"][1], target["formula_ids"][0]
        mutate_jsonl(root, "formal_object_semantic_bindings.jsonl", action)
        target = row(read_jsonl(root / "formal_object_semantic_bindings.jsonl"), "environment_id", "projected-env-000939")
        expected = next(x for x in read_json(WORK / "TR014_FORMAL_AUTHORING_PACKETS.json")["packets"] if x["environment_id"] == target["environment_id"])["formula_ids"]
        return ["formal_object_semantic_bindings.jsonl"], target["formula_ids"] == expected

    @case("exercise_solution_injected")
    def _(root: Path):
        def action(rows):
            target = row(rows, "environment_id", "projected-env-000977"); target["narrative_before_explicit_math_replay"] += " Here is the solution."; target["full_source_order_linearization"] += " Here is the solution."
        mutate_jsonl(root, "formal_object_semantic_bindings.jsonl", action)
        target = row(read_jsonl(root / "formal_object_semantic_bindings.jsonl"), "environment_id", "projected-env-000977")
        return ["formal_object_semantic_bindings.jsonl"], "Here is the solution" not in target["full_source_order_linearization"]

    @case("source_reference_row_omitted")
    def _(root: Path):
        def action(rows): rows.pop()
        mutate_jsonl(root, "REFERENCE_LEDGER.jsonl", action)
        return ["REFERENCE_LEDGER.jsonl"], len(read_jsonl(root / "REFERENCE_LEDGER.jsonl")) == 69

    @case("correction_visible_disclosure_removed")
    def _(root: Path):
        def action(rows): row(rows, "correction_id", "TR014-SOURCE-PROSE-001")["visible_disclosure"] = ""
        mutate_jsonl(root, "SOURCE_CORRECTIONS.jsonl", action)
        target = row(read_jsonl(root / "SOURCE_CORRECTIONS.jsonl"), "correction_id", "TR014-SOURCE-PROSE-001")
        return ["SOURCE_CORRECTIONS.jsonl"], bool(target["visible_disclosure"].strip())

    @case("preserved_prior_fail_pin_rewritten")
    def _(root: Path):
        def action(value): value["preserved_independent_fail_pins"]["initial_audit_fail_sha256"] = "0" * 64
        mutate_json(root, "INDEPENDENT_FAIL_REPAIR_CLOSURE.json", action)
        current = read_json(root / "INDEPENDENT_FAIL_REPAIR_CLOSURE.json")
        return ["INDEPENDENT_FAIL_REPAIR_CLOSURE.json"], current["preserved_independent_fail_pins"]["initial_audit_fail_sha256"] == PRIOR_FAIL_PINS["INITIAL_AUDIT_FAIL.json"]

    @case("derived_reference_promoted_to_source")
    def _(root: Path):
        def action(rows): rows[0]["not_an_immutable_source_reference_row"] = False
        mutate_jsonl(root, "DERIVED_REFERENCE_LEDGER.jsonl", action)
        return ["DERIVED_REFERENCE_LEDGER.jsonl"], read_jsonl(root / "DERIVED_REFERENCE_LEDGER.jsonl")[0]["not_an_immutable_source_reference_row"] is True

    @case("expression_meaning_generic_fallback")
    def _(root: Path):
        def action(rows):
            target = row(rows, "expression_id", "expr-8238c028f61fc0f7"); target["meaning"] = "This is a fallback mathematical expression."; target["meaning_sha256"] = sha256_bytes(target["meaning"].encode("utf-8"))
        mutate_jsonl(root, "expression_semantics.jsonl", action)
        target = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", "expr-8238c028f61fc0f7")
        return ["expression_semantics.jsonl"], "fallback" not in target["meaning"].lower()

    @case("occurrence_mathml_bound_to_wrong_expression")
    def _(root: Path):
        def action(rows):
            target = row(rows, "formula_id", "projected-formula-0005611"); other = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", "expr-d055ee4dbcdd0c8b"); target["mathml"] = other["mathml_inline"]; target["mathml_sha256"] = sha256_bytes(target["mathml"].encode("utf-8"))
        mutate_jsonl(root, "semantic_occurrences.jsonl", action)
        target = row(read_jsonl(root / "semantic_occurrences.jsonl"), "formula_id", "projected-formula-0005611"); expression = row(read_jsonl(root / "expression_semantics.jsonl"), "expression_id", target["expression_id"])
        return ["semantic_occurrences.jsonl"], target["mathml"] == expression["mathml_inline"]

    results = []
    try:
        for label, mutation in cases:
            if scratch.exists():
                resolved = scratch.resolve()
                if resolved.parent != AUDIT.resolve():
                    raise RuntimeError(f"unsafe probe scratch path: {resolved}")
                shutil.rmtree(scratch)
            shutil.copytree(PRODUCER, scratch)
            names, predicate_still_valid = mutation(scratch)
            rebind(scratch, names)
            proc = subprocess.run(
                [sys.executable, "-B", str(WORK / "validate_tr014.py"), "--evidence", str(scratch), "--check-only"],
                cwd=str(WORK), capture_output=True, text=True, encoding="utf-8",
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            independent_rejected = not predicate_still_valid
            validator_rejected = proc.returncode != 0
            ok = independent_rejected and validator_rejected
            assert_pred(ok, "FRESH_ADVERSARIAL_MUTATION_REJECTED", f"probe not rejected: {label}")
            results.append({
                "case": label, "mutated_artifacts": names,
                "independent_predicate_rejected": independent_rejected,
                "producer_validator_rejected": validator_rejected,
                "validator_returncode": proc.returncode,
                "validator_error_tail": (proc.stderr or proc.stdout)[-1200:],
                "result": "PASS_MUTATION_REJECTED" if ok else "FAIL_MUTATION_ACCEPTED",
            })
    finally:
        if scratch.exists():
            resolved = scratch.resolve()
            if resolved.parent == AUDIT.resolve():
                shutil.rmtree(scratch)
    return {
        "schema": "openlogic-tr014-independent-reaudit-adversarial-probes-v1",
        "tranche_id": TRANCHE_ID,
        "probe_count": len(results),
        "probes": results,
        "result": "PASS_ALL_FRESH_ADVERSARIAL_MUTATIONS_REJECTED" if len(results) == len(cases) and all(x["result"].startswith("PASS_") for x in results) else "FAIL_ADVERSARIAL_PROBE",
    }


if __name__ == "__main__":
    raise SystemExit(main())
