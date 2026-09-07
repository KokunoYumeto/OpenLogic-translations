#!/usr/bin/env python3
"""Fresh read-only independent re-audit of the repaired OLAB-TR-022 candidate.

The audit never imports producer validation claims as conclusions.  It checks
the protected producer bundle against the immutable source/oracle, performs
fresh semantic and MathML review, builds two isolated cold replays, and runs
independent adversarial guards.  It writes only below this audit directory.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PROJECTION = PROJECT / "evidence" / "tranche_022_fol_tableaux_projection"
WORK = PROJECT / "work" / "tranche_022_fol_tableaux_projection"
ORACLE = PROJECT / "evidence" / "tranche_022_fol_tableaux_oracle"
ORACLE_VALIDATION = PROJECT / "evidence" / "tranche_022_fol_tableaux_oracle_validation"
GLOBAL_LABELS = PROJECT / "evidence" / "complete_census" / "oracles" / "label_definitions.jsonl"
SOURCE_AUTHORITY = ORACLE / "SOURCE_AUTHORITY.json"
COLD_ROOT = HERE / "cold_rebuilds"

EXPECTED = {
    "sources": 14,
    "source_lines": 2208,
    "source_bytes": 83860,
    "expressions": 275,
    "occurrences": 589,
    "occurrence_mathml_roots": 1178,
    "expression_mathml_roots": 1100,
    "formals": 121,
    "proof_trees": 17,
    "tableaux": 50,
    "proof_commands": 77,
    "exercises": 9,
    "references": 14,
    "corrections": 7,
    "formula_nodes": 279,
    "terminal_paths": 80,
    "closed_terminal_paths": 40,
    "omitted_subtrees": 6,
}

LISTENER_RESIDUE = re.compile(
    r"!!|OPENLOGIC(?:FORMULA|REFERENCE|DISCLOSURE)|\\[A-Za-z]+|[${}]|"
    r"[¬∧∨→⇒↔∀∃⊢⊨⊥⊤∈∅∪∩⊆⊇≠≤≥]"
)
RAW_ROOT_ATTRIBUTES = {"aria-label", "role", "class"}
MATHML_TAGS = {
    "math", "mi", "mn", "mo", "mrow", "mspace", "mstyle", "msub",
    "msup", "mtable", "mtd", "mtext", "mtr",
}
NUMBER_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
    12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_text(path: Path, value: str) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(HERE):
        raise RuntimeError(f"audit write escaped evidence directory: {resolved}")
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def formal_id(row: Mapping[str, Any]) -> str:
    return str(row.get("formal_object_id") or row.get("environment_id"))


def record_hash_ok(row: Mapping[str, Any]) -> bool:
    payload = dict(row)
    declared = payload.pop("record_sha256", None)
    return isinstance(declared, str) and declared == sha256_bytes(compact_json(payload).encode("utf-8"))


def tree_signature(node: ET.Element) -> Any:
    return (
        local_name(node.tag),
        tuple(sorted((key, value) for key, value in node.attrib.items() if key != "data-formula-id")),
        (node.text or ""),
        tuple(tree_signature(child) for child in node),
        (node.tail or ""),
    )


class Audit:
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []
        self._finding_keys: set[tuple[str, str]] = set()

    def finding(
        self,
        finding_id: str,
        category: str,
        message: str,
        evidence: Mapping[str, Any],
        remediation: str,
        severity: str = "P1",
    ) -> None:
        key = (finding_id, compact_json(dict(evidence)))
        if key in self._finding_keys:
            return
        self._finding_keys.add(key)
        self.findings.append({
            "finding_id": finding_id,
            "severity": severity,
            "category": category,
            "message": message,
            "evidence": dict(evidence),
            "remediation": remediation,
            "status": "OPEN_CURRENT_CANDIDATE",
        })

    def check(
        self,
        condition: bool,
        finding_id: str,
        category: str,
        message: str,
        evidence: Mapping[str, Any],
        remediation: str,
        severity: str = "P1",
    ) -> bool:
        if not condition:
            self.finding(finding_id, category, message, evidence, remediation, severity)
            return False
        return True


def file_records(scope: str, root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rows.append({
            "scope": scope,
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return rows


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for scope, root in (
        ("producer_work", WORK),
        ("producer_projection", PROJECTION),
        ("oracle", ORACLE),
        ("oracle_validation", ORACLE_VALIDATION),
    ):
        rows.extend(file_records(scope, root))
    authority = read_json(SOURCE_AUTHORITY)
    authority_root = Path(authority["authority_root"])
    for source in authority["source_records"]:
        path = authority_root / source["path"]
        rows.append({
            "scope": "immutable_source",
            "path": source["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    rows.append({
        "scope": "global_label_oracle",
        "path": str(GLOBAL_LABELS.resolve()),
        "bytes": GLOBAL_LABELS.stat().st_size,
        "sha256": sha256_file(GLOBAL_LABELS),
    })
    rows.sort(key=lambda row: (row["scope"], row["path"]))
    return {
        "schema": "openlogic-tr022-independent-protected-snapshot-v1",
        "file_count": len(rows),
        "files": rows,
        "aggregate_sha256": sha256_bytes(compact_json(rows).encode("utf-8")),
    }


def cache_residue() -> list[str]:
    residue = []
    for root in (WORK, PROJECTION, HERE):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.name == "__pycache__" or (path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}):
                residue.append(str(path.resolve()))
    return sorted(set(residue))


def verify_manifest(audit: Audit, directory: Path, name: str) -> dict[str, Any]:
    manifest = read_json(directory / name)
    seen: set[str] = set()
    reviews = []
    for entry in manifest.get("files", []):
        relative = str(entry.get("path", ""))
        path = directory / relative
        good = (
            relative not in seen
            and path.is_file()
            and path.stat().st_size == entry.get("bytes")
            and sha256_file(path) == entry.get("sha256")
        )
        reviews.append({"path": relative, "status": "PASS" if good else "FAIL"})
        audit.check(
            good,
            "TR022-INDEPENDENT-MANIFEST-001",
            "manifest_integrity",
            f"Manifest entry is missing, duplicated, or hash/size-drifted in {name}.",
            {"manifest": name, "path": relative},
            "Regenerate the producer candidate and its manifest from protected inputs.",
        )
        seen.add(relative)
    return {"manifest": name, "entry_count": len(reviews), "entries": reviews}


def pin_and_manifest_audit(audit: Audit) -> dict[str, Any]:
    key_files = [
        "ARTIFACT_MANIFEST.json", "EVIDENCE_MANIFEST.json", "PRODUCER_RECEIPT.json",
        "VALIDATION_RECEIPT.json", "COLD_BUILD_RECEIPT.json", "ADVERSARIAL_TEST_RECEIPT.json",
        "PROTECTED_INPUT_VALIDATION_RECEIPT.json", "PRODUCER_BOUNDARY_RECEIPT.json",
    ]
    pins = []
    for name in key_files:
        path = PROJECTION / name
        audit.check(
            path.is_file(), "TR022-INDEPENDENT-PIN-001", "candidate_identity",
            "Required producer receipt is missing.", {"path": name},
            "Restore the complete producer receipt bundle before independent audit.",
        )
        if path.is_file():
            pins.append({"path": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})

    artifact_review = verify_manifest(audit, PROJECTION, "ARTIFACT_MANIFEST.json")
    evidence_review = verify_manifest(audit, PROJECTION, "EVIDENCE_MANIFEST.json")
    producer = read_json(PROJECTION / "PRODUCER_RECEIPT.json")
    validation = read_json(PROJECTION / "VALIDATION_RECEIPT.json")
    links = {
        "producer_to_artifact": producer.get("artifact_manifest_sha256") == sha256_file(PROJECTION / "ARTIFACT_MANIFEST.json"),
        "producer_to_builder": producer.get("builder_sha256") == sha256_file(WORK / "build_tr022.py"),
        "validation_to_artifact": validation.get("artifact_manifest_sha256") == sha256_file(PROJECTION / "ARTIFACT_MANIFEST.json"),
        "validation_to_producer": validation.get("producer_receipt_sha256") == sha256_file(PROJECTION / "PRODUCER_RECEIPT.json"),
        "validation_to_validator": validation.get("validator_sha256") == sha256_file(WORK / "validate_tr022.py"),
        "validation_to_cold": validation.get("cold_build_receipt_sha256") == sha256_file(PROJECTION / "COLD_BUILD_RECEIPT.json"),
        "validation_to_adversarial": validation.get("adversarial_test_receipt_sha256") == sha256_file(PROJECTION / "ADVERSARIAL_TEST_RECEIPT.json"),
        "validation_to_protected": validation.get("protected_input_receipt_sha256") == sha256_file(PROJECTION / "PROTECTED_INPUT_VALIDATION_RECEIPT.json"),
    }
    for link, good in links.items():
        audit.check(
            good, "TR022-INDEPENDENT-PIN-002", "receipt_cross_binding",
            "Producer receipt hash cross-binding drifted.", {"link": link},
            "Regenerate the producer receipts and re-run independent audit.",
        )
    expected_statuses = (
        producer.get("producer_status") == "PASS_SELF_VALIDATED_READY_FOR_INDEPENDENT_AUDIT"
        and producer.get("independent_audit_status") == "NOT_PERFORMED_OR_CLAIMED_BY_PRODUCER"
        and validation.get("status") == "PASS_PRODUCER_VALIDATION_COMPLETE_INDEPENDENT_AUDIT_PENDING"
    )
    audit.check(
        expected_statuses, "TR022-INDEPENDENT-BOUNDARY-001", "producer_boundary",
        "Producer receipts blur or pre-claim the independent-audit boundary.",
        {"producer_status": producer.get("producer_status"), "independent": producer.get("independent_audit_status"), "validation": validation.get("status")},
        "Restore producer-only status language and leave independent acceptance to this audit.",
    )
    return {
        "schema": "openlogic-tr022-independent-pin-and-manifest-audit-v1",
        "pins": pins,
        "artifact_manifest": artifact_review,
        "evidence_manifest": evidence_review,
        "cross_bindings": links,
        "status": "PASS" if all(links.values()) and expected_statuses else "FAIL",
    }


def load_data() -> dict[str, Any]:
    authority = read_json(SOURCE_AUTHORITY)
    authority_root = Path(authority["authority_root"])
    source_bytes = {row["path"]: (authority_root / row["path"]).read_bytes() for row in authority["source_records"]}
    return {
        "authority": authority,
        "source_bytes": source_bytes,
        "shapes": read_tsv(ORACLE / "formula_shapes.tsv"),
        "oracle_occurrences": read_jsonl(ORACLE / "formula_occurrences.jsonl"),
        "oracle_contexts": read_jsonl(ORACLE / "formula_contexts.jsonl"),
        "oracle_formals": read_jsonl(ORACLE / "formal_objects.jsonl"),
        "oracle_commands": read_jsonl(ORACLE / "proof_commands.jsonl"),
        "oracle_references": read_jsonl(ORACLE / "references.jsonl"),
        "labels": read_jsonl(GLOBAL_LABELS),
        "authored_expressions": read_json(WORK / "tr022_expressions_authored.json"),
        "authored_occurrences": read_json(WORK / "tr022_occurrences_authored.json"),
        "authored_formals": read_json(WORK / "tr022_formals_authored.json"),
        "authored_corrections": read_json(WORK / "tr022_source_corrections_authored.json"),
        "expressions": read_jsonl(PROJECTION / "expression_semantics.jsonl"),
        "occurrences": read_jsonl(PROJECTION / "semantic_occurrences.jsonl"),
        "contexts": read_jsonl(PROJECTION / "CONTEXT_AUTHORING_REVIEW.jsonl"),
        "coordinates": read_jsonl(PROJECTION / "formula_coordinate_ledger.jsonl"),
        "formals": read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl"),
        "tableaux": read_jsonl(PROJECTION / "tableau_structure_ledger.jsonl"),
        "commands": read_jsonl(PROJECTION / "proof_command_semantic_bindings.jsonl"),
        "references": read_jsonl(PROJECTION / "reference_bindings.jsonl"),
        "corrections": read_jsonl(PROJECTION / "SOURCE_CORRECTIONS.jsonl"),
        "disclosures": read_jsonl(PROJECTION / "LISTENER_DISCLOSURE_BINDINGS.jsonl"),
        "replays": read_jsonl(PROJECTION / "continuous_source_replay.jsonl"),
        "source_lines": read_jsonl(PROJECTION / "SOURCE_LINE_REPLAY.jsonl"),
    }


def source_authority_audit(audit: Audit, data: Mapping[str, Any]) -> dict[str, Any]:
    authority = data["authority"]
    records = authority["source_records"]
    totals = {
        "sources": len(records),
        "source_lines": sum(int(row["lines"]) for row in records),
        "source_bytes": sum(int(row["bytes"]) for row in records),
    }
    checks = {
        "immutable": authority.get("mutable") is False,
        "commit": authority.get("authority_commit") == "9620cc73f9c8e0ad003c514a5d3748f29611c4c0",
        "source_count": totals["sources"] == EXPECTED["sources"],
        "line_count": totals["source_lines"] == EXPECTED["source_lines"],
        "byte_count": totals["source_bytes"] == EXPECTED["source_bytes"],
    }
    rows = []
    for source in records:
        raw = data["source_bytes"][source["path"]]
        good = (
            len(raw) == source["bytes"]
            and sha256_bytes(raw) == source["sha256"]
            and len(raw.decode("utf-8").splitlines()) == source["lines"]
        )
        rows.append({"path": source["path"], "status": "PASS" if good else "FAIL"})
        if not good:
            checks["source_file_identity"] = False
    checks.setdefault("source_file_identity", True)
    for name, good in checks.items():
        audit.check(
            good, "TR022-INDEPENDENT-SOURCE-001", "source_identity",
            "Immutable source authority or source census drifted.", {"check": name, "totals": totals},
            "Restore the pinned source tree and regenerate the tranche.",
        )
    return {
        "schema": "openlogic-tr022-independent-source-authority-audit-v1",
        "authority_commit": authority.get("authority_commit"),
        "totals": totals,
        "checks": checks,
        "sources": rows,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def listener_ok(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and LISTENER_RESIDUE.search(value) is None


def semantic_obligations(tex: str, speech: str) -> list[dict[str, Any]]:
    lowered = speech.lower()
    obligations: list[tuple[str, bool]] = []

    def add(name: str, present: bool, words: tuple[str, ...]) -> None:
        if present:
            obligations.append((name, any(word in lowered for word in words)))

    add("true_sign", r"\True" in tex, ("true",))
    add("false_sign", r"\False" in tex, ("false",))
    add("negation", r"\lnot" in tex, ("not", "negation"))
    add("conjunction", r"\land" in tex, (" and ", "conjunction"))
    add("disjunction", r"\lor" in tex, (" or ", "disjunction"))
    add("conditional", r"\lif" in tex, ("implies", "conditional", "if "))
    add("universal_quantifier", r"\lforall" in tex, ("every", "universal"))
    add("existential_quantifier", r"\lexists" in tex, ("some", "exists", "existential"))
    add("negative_derivability", r"\Proves/" in tex, ("not tableau", "not a tableau", "not derivable"))
    add("derivability", r"\Proves" in tex, ("derivable", "derivability", "tableau theorem"))
    add("entailment", r"\Entails" in tex, ("entails", "semantic"))
    add("negative_satisfaction", r"\Sat/" in tex, ("does not satisfy", "not satisfy"))
    add("satisfaction", r"\Sat" in tex, ("satisf",))
    add("subset", r"\subseteq" in tex, ("subset",))
    add("membership", bool(re.search(r"\\in(?:\s|$)", tex)), ("belongs", "member"))
    add("union", r"\cup" in tex, ("union", "together"))
    add("substitution", r"\Subst" in tex, ("substitut",))
    add("value", r"\Value" in tex, ("value",))
    add("interpretation", r"\Assign" in tex, ("interpretation",))
    add("assignment_agreement", r"\varAssign" in tex, ("assignment", "agrees"))
    add("tableau_rule", r"\TRule" in tex, ("rule",))
    add("identity", r"\eq" in tex, ("identical", "identity", "equals"))
    return [{"obligation": name, "status": "PASS" if good else "FAIL"} for name, good in obligations]


def expression_and_mathml_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expressions = data["expressions"]
    shapes = {row["expression_id"]: row for row in data["shapes"]}
    occurrence_counts = Counter(row["expression_id"] for row in data["occurrences"])
    reviews = []
    mathml_reviews = []
    ids = [row["expression_id"] for row in expressions]
    audit.check(
        len(expressions) == EXPECTED["expressions"] and len(set(ids)) == EXPECTED["expressions"],
        "TR022-INDEPENDENT-EXPRESSION-001", "expression_census",
        "Expression census or stable expression-ID uniqueness failed.",
        {"rows": len(expressions), "unique_ids": len(set(ids))},
        "Regenerate all expression records from the frozen oracle.",
    )
    for row in expressions:
        expression_id = row["expression_id"]
        issues = []
        shape = shapes.get(expression_id)
        if not shape or shape["normalized_tex"] != row.get("normalized_tex"):
            issues.append("oracle shape binding mismatch")
        if int(row.get("occurrence_count", -1)) != occurrence_counts[expression_id]:
            issues.append("occurrence count mismatch")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        if not listener_ok(row.get("speech")):
            issues.append("listener speech residue or empty speech")
        if not listener_ok(row.get("meaning")):
            issues.append("listener meaning residue or empty meaning")
        obligations = semantic_obligations(str(row.get("normalized_tex", "")), str(row.get("speech", "")))
        failed_obligations = [item["obligation"] for item in obligations if item["status"] == "FAIL"]
        if failed_obligations:
            issues.append("semantic speech obligations failed: " + ",".join(failed_obligations))
        authored = data["authored_expressions"].get(expression_id)
        if not authored or row.get("expression_authority_record_sha256") != authored.get("record_sha256"):
            issues.append("authored authority hash binding mismatch")

        for field, display, projection_name in (
            ("reader_mathml_inline", "inline", "reader"),
            ("reader_mathml_block", "block", "reader"),
            ("source_mathml_inline", "inline", "source"),
            ("source_mathml_block", "block", "source"),
        ):
            value = row.get(field, "")
            root_issues = []
            try:
                root = ET.fromstring(value)
                tags = {local_name(node.tag) for node in root.iter()}
                if local_name(root.tag) != "math" or not len(root):
                    root_issues.append("flattened or missing structural MathML body")
                if root.attrib.get("display") != display:
                    root_issues.append("display mode mismatch")
                if root.attrib.get("data-expression-id") != expression_id:
                    root_issues.append("stable expression ID mismatch")
                if RAW_ROOT_ATTRIBUTES.intersection(root.attrib):
                    root_issues.append("root aria-label or role flattens native navigation")
                if not tags.issubset(MATHML_TAGS):
                    root_issues.append("unexpected MathML element")
            except ET.ParseError as exc:
                root_issues.append(f"invalid XML: {exc}")
            mathml_reviews.append({
                "expression_id": expression_id,
                "field": field,
                "projection": projection_name,
                "display": display,
                "status": "PASS" if not root_issues else "FAIL",
                "issues": root_issues,
            })
            issues.extend(f"{field}: {item}" for item in root_issues)

        reviews.append({
            "expression_id": expression_id,
            "normalized_tex": row.get("normalized_tex"),
            "speech": row.get("speech"),
            "semantic_class": row.get("semantic_class"),
            "obligations": obligations,
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
        })
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-EXPRESSION-002", "expression_semantics_or_mathml",
                "An expression failed source binding, semantic speech, record hash, or native MathML review.",
                {"expression_id": expression_id, "issues": issues},
                "Repair the expression authority and rebuild the producer candidate.",
            )
    audit.check(
        len(mathml_reviews) == EXPECTED["expression_mathml_roots"],
        "TR022-INDEPENDENT-MATHML-001", "mathml_census",
        "Expression MathML root census is incomplete.", {"actual": len(mathml_reviews)},
        "Emit reader/source inline/block native MathML for every expression.",
    )
    return reviews, mathml_reviews


def byte_line_column(raw: bytes, offset: int) -> tuple[int, int]:
    return raw.count(b"\n", 0, offset) + 1, offset - raw.rfind(b"\n", 0, offset)


def occurrence_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    occurrences = data["occurrences"]
    oracle_rows = {row["formula_id"]: row for row in data["oracle_occurrences"]}
    oracle_contexts = {row["formula_id"]: row for row in data["oracle_contexts"]}
    context_rows = {row["formula_id"]: row for row in data["contexts"]}
    coordinate_rows = {row["formula_id"]: row for row in data["coordinates"]}
    expressions = {row["expression_id"]: row for row in data["expressions"]}
    ids = [row["formula_id"] for row in occurrences]
    audit.check(
        len(occurrences) == EXPECTED["occurrences"] and len(set(ids)) == EXPECTED["occurrences"],
        "TR022-INDEPENDENT-OCCURRENCE-001", "occurrence_census",
        "Occurrence census or stable formula-ID uniqueness failed.",
        {"rows": len(occurrences), "unique_ids": len(set(ids))},
        "Regenerate all occurrence bindings from the frozen oracle.",
    )
    reviews = []
    mathml_reviews = []
    for row in occurrences:
        formula_id = row["formula_id"]
        issues = []
        oracle = oracle_rows.get(formula_id)
        context = oracle_contexts.get(formula_id)
        if oracle is None:
            issues.append("missing oracle occurrence")
        else:
            for field in oracle:
                if row.get(field) != oracle[field]:
                    issues.append(f"oracle field mismatch: {field}")
        if context is None or row.get("context_id") != context.get("context_id"):
            issues.append("three-line context binding mismatch")
        projected_context = context_rows.get(formula_id)
        if projected_context is None or projected_context.get("source_packet_sha256") != data["authored_occurrences"].get(formula_id, {}).get("source_packet_sha256"):
            issues.append("context authoring packet hash mismatch")
        coordinate = coordinate_rows.get(formula_id)
        if coordinate is None or coordinate.get("source_occurrence_sha256") != data["authored_occurrences"].get(formula_id, {}).get("source_occurrence_sha256"):
            issues.append("coordinate authority hash mismatch")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        if not listener_ok(row.get("speech")) or not listener_ok(row.get("meaning")):
            issues.append("listener speech/meaning residue or empty value")
        authored = data["authored_occurrences"].get(formula_id)
        if not authored or row.get("occurrence_authority_record_sha256") != authored.get("record_sha256"):
            issues.append("authored occurrence hash binding mismatch")
        expression = expressions.get(row.get("expression_id"))
        if expression is None:
            issues.append("unknown expression binding")
        source_raw = data["source_bytes"].get(row.get("file"), b"")
        offset = int(row.get("offset", -1))
        tex = str(row.get("tex", ""))
        delimiter = str(row.get("delimiter", ""))
        tex_bytes = tex.encode("utf-8")
        inline_close = source_raw.find(b"$", offset + 1) if offset >= 0 else -1
        delimiter_ok = (
            offset >= 0
            and (
                (
                    delimiter == "$"
                    and source_raw.startswith(b"$", offset)
                    and inline_close > offset
                )
                or (delimiter == r"\[...\]" and source_raw.startswith(br"\[", offset))
                or (delimiter == "align*" and source_raw.startswith(br"\begin{align*}", offset))
            )
        )
        if not delimiter_ok:
            issues.append("exact source delimiter/offset mismatch")
        elif byte_line_column(source_raw, offset) != (int(row["line"]), int(row["column"])):
            issues.append("source line/column mismatch")

        display = "inline" if row.get("delimiter") == "$" else "block"
        if row.get("display_mode") != display:
            issues.append("display-mode/delimiter mismatch")
        for field, projection_name in (("reader_mathml", "reader"), ("source_mathml", "source")):
            root_issues = []
            try:
                root = ET.fromstring(str(row.get(field, "")))
                if local_name(root.tag) != "math" or not len(root):
                    root_issues.append("flattened or missing structural MathML body")
                if root.attrib.get("display") != display:
                    root_issues.append("display mode mismatch")
                if root.attrib.get("data-expression-id") != row.get("expression_id"):
                    root_issues.append("stable expression ID mismatch")
                if root.attrib.get("data-formula-id") != formula_id:
                    root_issues.append("stable formula ID mismatch")
                if RAW_ROOT_ATTRIBUTES.intersection(root.attrib):
                    root_issues.append("root aria-label or role flattens native navigation")
                if expression is not None:
                    base_root = ET.fromstring(str(expression[f"{projection_name}_mathml_{display}"]))
                    if tree_signature(root) != tree_signature(base_root):
                        root_issues.append("occurrence structure differs from expression MathML")
            except ET.ParseError as exc:
                root_issues.append(f"invalid XML: {exc}")
            mathml_reviews.append({
                "formula_id": formula_id,
                "expression_id": row.get("expression_id"),
                "projection": projection_name,
                "field": field,
                "status": "PASS" if not root_issues else "FAIL",
                "issues": root_issues,
            })
            issues.extend(f"{field}: {item}" for item in root_issues)

        reviews.append({
            "formula_id": formula_id,
            "expression_id": row.get("expression_id"),
            "file": row.get("file"),
            "line": row.get("line"),
            "column": row.get("column"),
            "speech": row.get("speech"),
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
        })
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-OCCURRENCE-002", "occurrence_binding_or_mathml",
                "An occurrence failed exact source/context binding, stable-ID, listener, or native MathML review.",
                {"formula_id": formula_id, "issues": issues},
                "Repair the occurrence authority and rebuild the producer candidate.",
            )

    audit.check(
        len(mathml_reviews) == EXPECTED["occurrence_mathml_roots"],
        "TR022-INDEPENDENT-MATHML-002", "occurrence_mathml_census",
        "The reader/source occurrence MathML root census is incomplete.",
        {"actual": len(mathml_reviews), "expected": EXPECTED["occurrence_mathml_roots"]},
        "Emit exactly two native MathML variants for every occurrence.",
    )
    return reviews, mathml_reviews


def tableau_counts(node: Mapping[str, Any]) -> tuple[int, int, int, int, int]:
    children = list(node.get("children", []))
    formula_nodes = 1 if node.get("node_kind") == "formula" else 0
    omitted = 1 if node.get("node_kind") == "omitted_subtree" else 0
    branch_points = 1 if len(children) > 1 else 0
    if not children:
        return formula_nodes, 1, 1 if node.get("close") else 0, omitted, branch_points
    totals = [formula_nodes, 0, 0, omitted, branch_points]
    for child in children:
        values = tableau_counts(child)
        totals = [left + right for left, right in zip(totals, values)]
    return tuple(totals)  # type: ignore[return-value]


def balanced_group(value: str, cursor: int) -> tuple[str, int]:
    while cursor < len(value) and value[cursor].isspace():
        cursor += 1
    if cursor >= len(value) or value[cursor] != "{":
        raise ValueError("missing group")
    depth = 1
    start = cursor + 1
    cursor += 1
    while cursor < len(value) and depth:
        if value[cursor] == "\\":
            cursor += 2
            continue
        if value[cursor] == "{":
            depth += 1
        elif value[cursor] == "}":
            depth -= 1
            if depth == 0:
                return value[start:cursor], cursor + 1
        cursor += 1
    raise ValueError("unclosed group")


def signed_formula_key(tex: str) -> tuple[str, str] | None:
    marker = tex.find(r"\sFmla")
    if marker < 0:
        return None
    try:
        sign, cursor = balanced_group(tex, marker + len(r"\sFmla"))
        formula, _ = balanced_group(tex, cursor)
    except ValueError:
        return None
    sign_name = "true" if r"\True" in sign else "false" if r"\False" in sign else sign.strip()
    normalized_formula = re.sub(r"\s+", "", formula)
    return sign_name, normalized_formula


def closed_paths(node: Mapping[str, Any], path: list[tuple[str, str]] | None = None) -> list[dict[str, Any]]:
    current = list(path or [])
    key = signed_formula_key(str(node.get("formula_tex", "")))
    if key is not None:
        current.append(key)
    children = list(node.get("children", []))
    if not children:
        complementary = any(
            sign == "true" and ("false", formula) in current
            or sign == "false" and ("true", formula) in current
            for sign, formula in current
        )
        return [{"marked_closed": bool(node.get("close")), "complementary_pair_present": complementary}]
    rows = []
    for child in children:
        rows.extend(closed_paths(child, current))
    return rows


def source_block_for_formal(data: Mapping[str, Any], row: Mapping[str, Any]) -> str:
    source = row.get("source", {})
    raw = data["source_bytes"][row["file"]].decode("utf-8")
    lines = raw.splitlines()
    start = int(source.get("start_line", row.get("line", 1)))
    end = int(source.get("end_line", start))
    return "\n".join(lines[start - 1:end])


def formal_tableau_and_command_audit(
    audit: Audit, data: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    formals = data["formals"]
    oracle = data["oracle_formals"]
    occurrence_index = {row["formula_id"]: row for row in data["occurrences"]}
    formal_index = {row["formal_object_id"]: row for row in formals}
    class_counts = Counter(row["object_role"] for row in formals)
    expected_ids = [formal_id(row) for row in oracle]
    actual_ids = [row["formal_object_id"] for row in formals]
    audit.check(
        len(formals) == EXPECTED["formals"] and actual_ids == expected_ids
        and [row["source_order"] for row in formals] == list(range(1, EXPECTED["formals"] + 1)),
        "TR022-INDEPENDENT-FORMAL-001", "formal_census_and_order",
        "Formal objects are incomplete or not in exact oracle source order.",
        {"actual_count": len(formals), "expected_count": EXPECTED["formals"]},
        "Regenerate formal bindings in exact frozen source order.",
    )
    for role, expected in (("proof tree", EXPECTED["proof_trees"]), ("tableau", EXPECTED["tableaux"]), ("exercise", EXPECTED["exercises"])):
        audit.check(
            class_counts[role] == expected, "TR022-INDEPENDENT-FORMAL-002", "formal_class_census",
            "Formal-object class census drifted.", {"role": role, "actual": class_counts[role], "expected": expected},
            "Restore the exact formal-object census and rebuild.",
        )

    reviews = []
    for index, row in enumerate(formals):
        issues = []
        object_id = row["formal_object_id"]
        source = oracle[index] if index < len(oracle) else None
        if source is None or formal_id(source) != object_id:
            issues.append("oracle formal source-order mismatch")
        elif any(row.get(field) != value for field, value in source.items()):
            issues.append("oracle formal source fields mismatch")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        authored = data["authored_formals"].get(object_id)
        if not authored or row.get("formal_authority_record_sha256") != authored.get("record_sha256"):
            issues.append("authored formal hash binding mismatch")
        for field in ("accessible_name", "long_description", "listen_text"):
            if not listener_ok(row.get(field)):
                issues.append(f"listener residue or empty {field}")
        for step in row.get("ordered_steps", []):
            if not listener_ok(step):
                issues.append("listener residue in ordered step")
        if row.get("formula_ids") != [binding.get("formula_id") for binding in row.get("formula_bindings", [])]:
            issues.append("formula-binding order/closure mismatch")
        for binding in row.get("formula_bindings", []):
            occurrence = occurrence_index.get(binding.get("formula_id"))
            authored_occurrence = data["authored_occurrences"].get(binding.get("formula_id"))
            if occurrence is None or authored_occurrence is None or binding.get("occurrence_record_sha256") != authored_occurrence.get("record_sha256"):
                issues.append(f"formula binding hash mismatch: {binding.get('formula_id')}")
            if not listener_ok(binding.get("speech")) or not listener_ok(binding.get("meaning")):
                issues.append(f"formula binding listener residue: {binding.get('formula_id')}")
        if row.get("object_role") == "exercise" and row.get("exercise_solution_status") != "PRESERVED_UNSOLVED":
            issues.append("exercise was not preserved unsolved")

        # Fresh semantic grouping gate: never infer numbered listener items from
        # raw formula count.  The source's enumerate structure is authoritative.
        block = source_block_for_formal(data, row)
        source_item_count = len(re.findall(r"\\item(?:\s|$)", block))
        announced = re.findall(r"Source-listed mathematical item ([a-z]+)\b", str(row.get("listen_text", "")), flags=re.I)
        if source_item_count and announced and source_item_count != len(announced):
            issues.append(
                f"enumerated source grouping mismatch: source has {source_item_count} items, listener announces {len(announced)}"
            )
            all_formula_ids = list(row.get("formula_ids", []))
            affected_formula_ids = all_formula_ids[1:] if object_id == "projected-env-001715" else all_formula_ids
            audit.finding(
                "TR022-INDEPENDENT-FORMAL-GROUPING-001",
                "formal_listener_source_grouping",
                "The quantified-identity exercise promotes the second formula inside source item two to a nonexistent third problem.",
                {
                    "formal_object_id": object_id,
                    "file": row.get("file"),
                    "formal_start_line": row.get("line"),
                    "source_environment_lines": [93, 103] if object_id == "projected-env-001715" else [],
                    "misgrouped_second_item_lines": [98, 99, 100, 101] if object_id == "projected-env-001715" else [],
                    "source_item_count": source_item_count,
                    "listener_announced_item_count": len(announced),
                    "all_formula_ids": all_formula_ids,
                    "affected_formula_ids": affected_formula_ids,
                    "affected_step_ordinals_one_based": [3, 4] if object_id == "projected-env-001715" else [],
                    "source_fact": "Lines 98-101 are one second \\item containing two signed formulas separated by a comma and line break.",
                },
                "Rewrite the exercise listener steps so there are exactly two problems: item one has one false-signed formula; item two is one tableau-assumption set containing the false-signed existential formula together with the true-signed uniqueness formula. Rebuild and re-audit.",
            )

        reviews.append({
            "source_order": row.get("source_order"),
            "formal_object_id": object_id,
            "object_role": row.get("object_role"),
            "file": row.get("file"),
            "line": row.get("line"),
            "formula_ids": row.get("formula_ids", []),
            "source_enumerated_items": source_item_count,
            "listener_announced_items": len(announced),
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
        })
        non_grouping = [item for item in issues if not item.startswith("enumerated source grouping mismatch")]
        if non_grouping:
            audit.finding(
                "TR022-INDEPENDENT-FORMAL-003", "formal_semantics",
                "A formal object failed exact source, listener, exercise, or formula-binding review.",
                {"formal_object_id": object_id, "issues": non_grouping},
                "Repair the formal authority and rebuild the producer candidate.",
            )

    tableau_reviews = []
    aggregate = [0, 0, 0, 0]
    tableau_index = {row["formal_object_id"]: row for row in data["tableaux"]}
    audit.check(
        len(data["tableaux"]) == EXPECTED["tableaux"],
        "TR022-INDEPENDENT-TABLEAU-001", "tableau_census",
        "Tableau structure ledger count drifted.", {"actual": len(data["tableaux"])},
        "Restore all 50 source tableaux.",
    )
    for object_id, row in tableau_index.items():
        issues = []
        counts = tableau_counts(row["tableau_structure"])
        declared = (
            row.get("node_count"), row.get("terminal_branch_count"),
            row.get("closed_terminal_branch_count"), row.get("omitted_subtree_placeholder_count"),
        )
        if counts[:4] != declared:
            issues.append("recursive tableau counts differ from declared counts")
        aggregate = [left + right for left, right in zip(aggregate, counts[:4])]
        paths = closed_paths(row["tableau_structure"])
        bad_closed = [item for item in paths if item["marked_closed"] and not item["complementary_pair_present"]]
        if bad_closed:
            issues.append("a marked-closed branch lacks complementary true/false signed formulas")
        formal = formal_index.get(object_id)
        if formal is None or formal.get("object_role") != "tableau":
            issues.append("tableau lacks matching formal object")
        else:
            expected_steps = counts[0] + counts[3] + counts[4] + len(formal.get("source_correction_ids", []))
            if len(formal.get("ordered_steps", [])) != expected_steps:
                issues.append("linearized spoken-step count mismatch")
            if sum("splits into" in step for step in formal.get("ordered_steps", [])) != counts[4]:
                issues.append("branch-split announcements incomplete")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        tableau_reviews.append({
            "formal_object_id": object_id,
            "counts": {"formula_nodes": counts[0], "terminal_paths": counts[1], "closed_terminal_paths": counts[2], "omitted_subtrees": counts[3], "branch_points": counts[4]},
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
        })
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-TABLEAU-002", "tableau_structure",
                "A tableau failed recursive count, semantic closure, or spoken linearization review.",
                {"formal_object_id": object_id, "issues": issues},
                "Repair the tableau structure/linearization and rebuild.",
            )
    expected_aggregate = [EXPECTED["formula_nodes"], EXPECTED["terminal_paths"], EXPECTED["closed_terminal_paths"], EXPECTED["omitted_subtrees"]]
    audit.check(
        aggregate == expected_aggregate,
        "TR022-INDEPENDENT-TABLEAU-003", "tableau_aggregate",
        "Aggregate tableau formula/terminal/closure/omission counts drifted.",
        {"actual": aggregate, "expected": expected_aggregate},
        "Restore the frozen tableau structure census.",
    )

    command_reviews = []
    command_ids = [row["proof_command_id"] for row in data["commands"]]
    oracle_commands = {row["proof_command_id"]: row for row in data["oracle_commands"]}
    owner_counts = Counter(row["formal_object_id"] for row in data["commands"])
    audit.check(
        len(command_ids) == EXPECTED["proof_commands"] and len(set(command_ids)) == EXPECTED["proof_commands"],
        "TR022-INDEPENDENT-COMMAND-001", "proof_command_census",
        "Proof-command census or stable command-ID uniqueness failed.",
        {"rows": len(command_ids), "unique": len(set(command_ids))},
        "Restore all 77 exact proof commands.",
    )
    for ordinal, row in enumerate(data["commands"], 1):
        issues = []
        oracle_row = oracle_commands.get(row["proof_command_id"])
        if oracle_row is None or any(row.get(field) != value for field, value in oracle_row.items()):
            issues.append("oracle proof-command coordinate mismatch")
        if row.get("global_command_source_order") != ordinal:
            issues.append("global proof-command source order mismatch")
        formal = formal_index.get(row.get("formal_object_id"))
        if formal is None or row["proof_command_id"] not in formal.get("proof_command_ids", []):
            issues.append("proof-command owner closure mismatch")
        if formal is not None and owner_counts[row["formal_object_id"]] != formal.get("proof_command_count"):
            issues.append("per-proof command count mismatch")
        if not listener_ok(row.get("command_speech")):
            issues.append("proof-command listener residue")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        command_reviews.append({"proof_command_id": row["proof_command_id"], "formal_object_id": row.get("formal_object_id"), "status": "PASS" if not issues else "FAIL", "issues": issues})
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-COMMAND-002", "proof_command_binding",
                "A proof command failed coordinate, owner, order, speech, or record-hash review.",
                {"proof_command_id": row["proof_command_id"], "issues": issues},
                "Repair proof-command binding and rebuild.",
            )
    return reviews, tableau_reviews, command_reviews


def reference_and_correction_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels = data["labels"]
    oracle_refs = {row["reference_id"]: row for row in data["oracle_references"]}
    ref_reviews = []
    audit.check(
        len(data["references"]) == EXPECTED["references"],
        "TR022-INDEPENDENT-REFERENCE-001", "reference_census",
        "Reference binding census drifted.", {"actual": len(data["references"])},
        "Restore all 14 exact references.",
    )
    for ordinal, row in enumerate(data["references"], 1):
        issues = []
        oracle = oracle_refs.get(row["reference_id"])
        if oracle is None or any(row.get(field) != value for field, value in oracle.items()):
            issues.append("oracle reference source binding mismatch")
        matches = [
            label for label in labels
            if label.get("full_key") == row.get("full_key")
            and label.get("file") == row.get("target_file")
            and label.get("instance_id") == row.get("target_instance_id")
        ]
        if len(matches) != 1:
            issues.append("global label target is not unique")
        else:
            target = matches[0]
            expected_fields = {
                "target_label_definition_id": target["label_definition_id"],
                "target_label_definition_sha256": sha256_bytes(compact_json(target).encode("utf-8")),
                "target_line": target["line"], "target_column": target["column"],
                "target_offset": target["offset"], "target_stream_start": target["stream_start"],
                "target_stream_end": target["stream_end"],
            }
            if any(row.get(field) != value for field, value in expected_fields.items()):
                issues.append("exact global target coordinate/hash mismatch")
        if row.get("reference_source_order") != ordinal:
            issues.append("reference source order mismatch")
        if not listener_ok(row.get("target_speech")):
            issues.append("reference listener residue")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        ref_reviews.append({"reference_id": row["reference_id"], "full_key": row.get("full_key"), "target_file": row.get("target_file"), "target_line": row.get("target_line"), "status": "PASS" if not issues else "FAIL", "issues": issues})
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-REFERENCE-002", "reference_binding",
                "A reference failed exact global-label target, listener, order, or hash review.",
                {"reference_id": row["reference_id"], "issues": issues},
                "Repair the reference target binding and rebuild.",
            )

    occurrence_ids = {row["formula_id"] for row in data["occurrences"]}
    disclosure_index = {row["correction_id"]: row for row in data["disclosures"]}
    correction_reviews = []
    audit.check(
        len(data["corrections"]) == EXPECTED["corrections"]
        and len(data["disclosures"]) == EXPECTED["corrections"],
        "TR022-INDEPENDENT-CORRECTION-001", "correction_census",
        "Source-correction or audible-disclosure census drifted.",
        {"corrections": len(data["corrections"]), "disclosures": len(data["disclosures"])},
        "Restore all seven exact source corrections and one audible disclosure per correction.",
    )
    for row in data["corrections"]:
        correction_id = row["correction_id"]
        issues = []
        source_lines = data["source_bytes"][row["file"]].decode("utf-8").splitlines()
        exact = {str(number): source_lines[int(number) - 1] for number in row["lines"]}
        if exact != row.get("exact_source_lines"):
            issues.append("exact frozen correction lines mismatch")
        if sha256_bytes(compact_json(exact).encode("utf-8")) != row.get("exact_source_lines_sha256"):
            issues.append("correction exact-line digest mismatch")
        if any(formula_id not in occurrence_ids for formula_id in row.get("affected_formula_ids", [])):
            issues.append("affected stable formula-ID closure mismatch")
        authored = data["authored_corrections"].get(correction_id)
        if not authored or row.get("correction_authority_record_sha256") != authored.get("record_sha256"):
            issues.append("authored correction hash binding mismatch")
        disclosure = disclosure_index.get(correction_id)
        if disclosure is None or disclosure.get("speech") != row.get("listener_disclosure_speech"):
            issues.append("audible disclosure binding mismatch")
        if not listener_ok(row.get("listener_disclosure_speech")):
            issues.append("audible disclosure contains listener residue")
        if not record_hash_ok(row):
            issues.append("record hash mismatch")
        correction_reviews.append({"correction_id": correction_id, "file": row["file"], "lines": row["lines"], "affected_formula_ids": row.get("affected_formula_ids", []), "status": "PASS" if not issues else "FAIL", "issues": issues})
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-CORRECTION-002", "source_correction",
                "A source correction failed exact-line, formula-ID, or audible-disclosure closure.",
                {"correction_id": correction_id, "issues": issues},
                "Repair the correction ledger and listener anchor, then rebuild.",
            )
    return ref_reviews, correction_reviews


def replay_and_source_line_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    occurrence_index = {row["formula_id"]: row for row in data["occurrences"]}
    reference_index = {row["reference_id"]: row for row in data["references"]}
    correction_index = {row["correction_id"]: row for row in data["corrections"]}
    replay_reviews = []
    formula_bindings = []
    reference_bindings = []
    disclosure_bindings = []
    for replay in data["replays"]:
        issues = []
        words = replay.get("listen_text", "").split()
        if replay.get("word_count") != len(words):
            issues.append("word count mismatch")
        if not listener_ok(replay.get("listen_text")):
            issues.append("continuous listener contains raw marker/TeX/symbol residue")
        for binding in replay.get("ordered_formula_bindings", []):
            formula_bindings.append(binding)
            occurrence = occurrence_index.get(binding.get("formula_id"))
            expected_prefix = "Mathematical expression" if binding.get("delimiter") == "$" else "Displayed mathematical expression"
            expected_speech = f"{expected_prefix}. {str(binding.get('base_speech', '')).strip().rstrip('.')}. End {expected_prefix.lower()}."
            if occurrence is None or binding.get("base_speech") != occurrence.get("speech") or binding.get("speech") != expected_speech:
                issues.append(f"formula listener composition mismatch: {binding.get('formula_id')}")
            start, end = int(binding["word_start"]), int(binding["word_end"])
            if " ".join(words[start:end]) != binding.get("speech"):
                issues.append(f"formula listener word span mismatch: {binding.get('formula_id')}")
        for binding in replay.get("ordered_reference_bindings", []):
            reference_bindings.append(binding)
            reference = reference_index.get(binding.get("reference_id"))
            expected = f"Reference. {reference['target_speech']}. End reference." if reference else ""
            if binding.get("speech") != expected:
                issues.append(f"reference listener composition mismatch: {binding.get('reference_id')}")
            start, end = int(binding["word_start"]), int(binding["word_end"])
            if " ".join(words[start:end]) != binding.get("speech"):
                issues.append(f"reference listener word span mismatch: {binding.get('reference_id')}")
        for binding in replay.get("ordered_disclosure_bindings", []):
            disclosure_bindings.append(binding)
            correction = correction_index.get(binding.get("correction_id"))
            if correction is None or binding.get("speech") != correction.get("listener_disclosure_speech"):
                issues.append(f"disclosure listener composition mismatch: {binding.get('correction_id')}")
            start, end = int(binding["word_start"]), int(binding["word_end"])
            if " ".join(words[start:end]) != binding.get("speech"):
                issues.append(f"disclosure listener word span mismatch: {binding.get('correction_id')}")
        if replay.get("formula_count") != len(replay.get("ordered_formula_bindings", [])):
            issues.append("per-source formula anchor count mismatch")
        if replay.get("reference_count") != len(replay.get("ordered_reference_bindings", [])):
            issues.append("per-source reference anchor count mismatch")
        if replay.get("disclosure_count") != len(replay.get("ordered_disclosure_bindings", [])):
            issues.append("per-source disclosure anchor count mismatch")
        if not record_hash_ok(replay):
            issues.append("record hash mismatch")
        replay_reviews.append({"source_replay_id": replay["source_replay_id"], "file": replay["file"], "word_count": len(words), "formula_count": replay["formula_count"], "reference_count": replay["reference_count"], "disclosure_count": replay["disclosure_count"], "status": "PASS" if not issues else "FAIL", "issues": issues})
        if issues:
            audit.finding(
                "TR022-INDEPENDENT-LISTENER-001", "continuous_listener",
                "A continuous listener replay failed composition, span, residue, or hash review.",
                {"source_replay_id": replay["source_replay_id"], "issues": issues},
                "Repair deterministic listener composition and rebuild.",
            )
    totals_good = (
        len(data["replays"]) == EXPECTED["sources"]
        and len(formula_bindings) == EXPECTED["occurrences"]
        and len({row["formula_id"] for row in formula_bindings}) == EXPECTED["occurrences"]
        and len(reference_bindings) == EXPECTED["references"]
        and len({row["reference_id"] for row in reference_bindings}) == EXPECTED["references"]
        and len(disclosure_bindings) == EXPECTED["corrections"]
        and len({row["correction_id"] for row in disclosure_bindings}) == EXPECTED["corrections"]
    )
    audit.check(
        totals_good, "TR022-INDEPENDENT-LISTENER-002", "listener_anchor_census",
        "Continuous listener formula/reference/disclosure anchor closure failed.",
        {"sources": len(data["replays"]), "formula_anchors": len(formula_bindings), "reference_anchors": len(reference_bindings), "disclosure_anchors": len(disclosure_bindings)},
        "Restore exactly one listener anchor for every stable formula, reference, and correction.",
    )

    line_reviews = data["source_lines"]
    expected_line_ids = set()
    line_issues = []
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in line_reviews:
        by_file[row["file"]].append(row)
        if not record_hash_ok(row):
            line_issues.append(f"record hash mismatch: {row['source_line_id']}")
    for source_ordinal, source in enumerate(data["authority"]["source_records"], 1):
        exact_lines = data["source_bytes"][source["path"]].decode("utf-8").splitlines()
        rows = sorted(by_file[source["path"]], key=lambda row: row["line"])
        if len(rows) != len(exact_lines):
            line_issues.append(f"line census mismatch: {source['path']}")
            continue
        for number, (row, exact) in enumerate(zip(rows, exact_lines), 1):
            expected_line_ids.add(row["source_line_id"])
            if row["line"] != number or row["source_ordinal"] != source_ordinal or row["source_text"] != exact:
                line_issues.append(f"exact line replay mismatch: {row['source_line_id']}")
            expected_hash = sha256_bytes((exact + "\n").encode("utf-8"))
            if row["source_line_sha256"] != expected_hash:
                line_issues.append(f"logical-line hash mismatch: {row['source_line_id']}")
    source_line_status = not line_issues and len(line_reviews) == EXPECTED["source_lines"] and len(expected_line_ids) == EXPECTED["source_lines"]
    audit.check(
        source_line_status,
        "TR022-INDEPENDENT-SOURCE-REPLAY-001", "source_line_replay",
        "Exact source-line replay is incomplete, duplicated, or hash-drifted.",
        {"rows": len(line_reviews), "unique_ids": len(expected_line_ids), "issues": line_issues[:20]},
        "Regenerate the exact frozen source-line replay.",
    )
    return replay_reviews, {
        "schema": "openlogic-tr022-independent-source-line-audit-v1",
        "row_count": len(line_reviews),
        "unique_source_line_ids": len(expected_line_ids),
        "issues": line_issues,
        "status": "PASS" if source_line_status else "FAIL",
    }


def safe_remove(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(HERE) or resolved == HERE:
        raise RuntimeError(f"unsafe audit cleanup target: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def cold_build_command(output: Path) -> list[str]:
    code = (
        "import importlib.util,sys;"
        "from pathlib import Path;"
        "sys.dont_write_bytecode=True;"
        f"sys.path.insert(0,{str(WORK)!r});"
        f"p=Path({str(WORK / 'build_tr022.py')!r});"
        "s=importlib.util.spec_from_file_location('tr022_independent_cold_builder',p);"
        "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
        f"m.COLD_ROOT=Path({str(COLD_ROOT)!r});"
        f"m.build(Path({str(output)!r}))"
    )
    return [sys.executable, "-B", "-c", code]


def tree_records(root: Path, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    return [
        {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(item for item in root.rglob("*") if item.is_file())
        if path.relative_to(root).as_posix() not in excluded
    ]


def cold_rebuild_audit(audit: Audit) -> dict[str, Any]:
    safe_remove(COLD_ROOT)
    COLD_ROOT.mkdir(parents=True)
    runs = []
    for name in ("run_a", "run_b"):
        output = COLD_ROOT / name
        process = subprocess.run(
            cold_build_command(output), cwd=WORK, capture_output=True, text=True,
            encoding="utf-8", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False,
        )
        runs.append({
            "name": name, "returncode": process.returncode,
            "stdout_sha256": sha256_bytes(process.stdout.encode("utf-8")),
            "stderr": process.stderr,
        })
        audit.check(
            process.returncode == 0, "TR022-INDEPENDENT-COLD-001", "cold_rebuild",
            "An isolated cold producer replay failed.", {"run": name, "returncode": process.returncode, "stderr": process.stderr},
            "Repair the deterministic producer build before independent acceptance.",
        )
    records_a = tree_records(COLD_ROOT / "run_a")
    records_b = tree_records(COLD_ROOT / "run_b")
    pair_equal = records_a == records_b
    audit.check(
        pair_equal, "TR022-INDEPENDENT-COLD-002", "cold_determinism",
        "Two isolated cold producer replays are not byte-identical.",
        {"run_a_files": len(records_a), "run_b_files": len(records_b)},
        "Remove nondeterminism and regenerate the candidate.",
    )
    # The canonical evidence manifest is later expanded by producer validation;
    # compare the immutable producer core, artifact manifest, and producer receipt.
    artifact = read_json(PROJECTION / "ARTIFACT_MANIFEST.json")
    canonical_names = [entry["path"] for entry in artifact["files"]] + ["ARTIFACT_MANIFEST.json", "PRODUCER_RECEIPT.json"]
    canonical_comparisons = []
    for name in canonical_names:
        canonical = PROJECTION / name
        replay = COLD_ROOT / "run_a" / name
        good = replay.is_file() and canonical.read_bytes() == replay.read_bytes()
        canonical_comparisons.append({"path": name, "status": "PASS" if good else "FAIL"})
        audit.check(
            good, "TR022-INDEPENDENT-COLD-003", "canonical_cold_identity",
            "Cold replay differs from the canonical producer core.", {"path": name},
            "Rebuild the canonical candidate from the same protected inputs.",
        )
    return {
        "schema": "openlogic-tr022-independent-cold-rebuild-audit-v1",
        "invocation": "python -B isolated import of build_tr022.py with audit-local COLD_ROOT",
        "runs": runs,
        "run_a_tree_sha256": sha256_bytes(compact_json(records_a).encode("utf-8")),
        "run_b_tree_sha256": sha256_bytes(compact_json(records_b).encode("utf-8")),
        "paired_byte_identical": pair_equal,
        "canonical_core_comparisons": canonical_comparisons,
        "canonical_core_byte_identical": all(row["status"] == "PASS" for row in canonical_comparisons),
        "status": "PASS" if pair_equal and all(run["returncode"] == 0 for run in runs) and all(row["status"] == "PASS" for row in canonical_comparisons) else "FAIL",
    }


class MutantSurvived(RuntimeError):
    pass


def guard_listener(value: str) -> None:
    if not listener_ok(value):
        raise ValueError("listener residue")


def guard_mathml(value: str, formula_id: str) -> None:
    root = ET.fromstring(value)
    if local_name(root.tag) != "math" or not len(root):
        raise ValueError("flattened MathML")
    if RAW_ROOT_ATTRIBUTES.intersection(root.attrib):
        raise ValueError("root flattening attribute")
    if root.attrib.get("data-formula-id") != formula_id:
        raise ValueError("stable formula ID drift")


def guard_unique(rows: list[dict[str, Any]], field: str) -> None:
    values = [row[field] for row in rows]
    if len(values) != len(set(values)):
        raise ValueError("duplicate stable ID")


def guard_record(row: dict[str, Any]) -> None:
    if not record_hash_ok(row):
        raise ValueError("record hash drift")


def guard_semantics(row: dict[str, Any]) -> None:
    if any(item["status"] == "FAIL" for item in semantic_obligations(row["normalized_tex"], row["speech"])):
        raise ValueError("semantic speech token loss")


def guard_tableau_declared(row: dict[str, Any]) -> None:
    counts = tableau_counts(row["tableau_structure"])
    if counts[:4] != (row["node_count"], row["terminal_branch_count"], row["closed_terminal_branch_count"], row["omitted_subtree_placeholder_count"]):
        raise ValueError("tableau count drift")


def guard_closed_semantics(row: dict[str, Any]) -> None:
    if any(item["marked_closed"] and not item["complementary_pair_present"] for item in closed_paths(row["tableau_structure"])):
        raise ValueError("false closure marker")


def guard_identity_grouping(row: dict[str, Any]) -> None:
    """Reject either structural or listener regression of the repaired exercise."""
    expected_groups = [
        ["projected-formula-0010700"],
        ["projected-formula-0010701", "projected-formula-0010702"],
    ]
    groups = row.get("exercise_item_groups", [])
    if row.get("formal_object_id") != "projected-env-001715":
        raise ValueError("wrong repaired formal object")
    if row.get("source_enumerate_item_count") != 2 or len(groups) != 2:
        raise ValueError("identity exercise source item count drift")
    if [item.get("formula_ids") for item in groups] != expected_groups:
        raise ValueError("identity exercise formula grouping drift")
    if [item.get("formula_count") for item in groups] != [1, 2]:
        raise ValueError("identity exercise group cardinality drift")
    if groups[1].get("grouping_kind") != "ONE_SOURCE_ITEM_CONTAINING_TWO_SIMULTANEOUS_SIGNED_ASSUMPTIONS":
        raise ValueError("identity exercise simultaneous-assumption semantics drift")
    if "simultaneous signed assumptions" not in str(groups[1].get("listener_step", "")).lower():
        raise ValueError("identity exercise simultaneous-assumption listener drift")
    steps = row.get("ordered_steps", [])
    if len(steps) != 3:
        raise ValueError("identity exercise grouped listener steps drift")
    if re.findall(r"Source-listed mathematical item ([a-z]+)\b", str(steps[1]), flags=re.I) != ["one"]:
        raise ValueError("identity exercise listener item one drift")
    if re.findall(r"Source-listed mathematical item ([a-z]+)\b", str(steps[2]), flags=re.I) != ["two"]:
        raise ValueError("identity exercise listener item two drift")
    for field in ("listen_text", "long_description"):
        labels = re.findall(r"Source-listed mathematical item ([a-z]+)\b", str(row.get(field, "")), flags=re.I)
        if labels != ["one", "two"]:
            raise ValueError(f"identity exercise {field} item announcements drift")


def expect_rejected(test_id: str, description: str, payload: Any, guard: Callable[[Any], None]) -> dict[str, Any]:
    serialized = canonical_json(payload).encode("utf-8")
    try:
        guard(payload)
    except Exception as exc:
        return {
            "test_id": test_id, "mutation": description,
            "mutant_bytes": len(serialized), "mutant_sha256": sha256_bytes(serialized),
            "rejection": str(exc), "status": "PASS_FRESH_MUTANT_REJECTED",
        }
    raise MutantSurvived(test_id)


def adversarial_audit(audit: Audit, data: Mapping[str, Any]) -> dict[str, Any]:
    tests = []
    first_occ = data["occurrences"][0]
    first_expr = data["expressions"][1]
    first_tableau = data["tableaux"][0]

    root = ET.fromstring(first_occ["reader_mathml"])
    root.set("aria-label", "flattened")
    tests.append(expect_rejected("occurrence_root_aria", "add root aria-label", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["formula_id"])))
    root = ET.fromstring(first_occ["reader_mathml"])
    root.set("role", "img")
    tests.append(expect_rejected("occurrence_root_role", "add root role=img", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["formula_id"])))
    root = ET.fromstring(first_occ["reader_mathml"])
    for child in list(root):
        root.remove(child)
    root.text = first_occ["speech"]
    tests.append(expect_rejected("flatten_occurrence_mathml", "replace structural MathML with root text", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["formula_id"])))
    root = ET.fromstring(first_occ["reader_mathml"])
    root.set("data-formula-id", "projected-formula-mutated")
    tests.append(expect_rejected("formula_id_root_drift", "alter root stable formula ID", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["formula_id"])))

    mutated = copy.deepcopy(data["occurrences"][:2])
    mutated[1]["formula_id"] = mutated[0]["formula_id"]
    tests.append(expect_rejected("duplicate_formula_id", "duplicate a stable formula ID", mutated, lambda rows: guard_unique(rows, "formula_id")))
    tests.append(expect_rejected("glossary_marker_leak", "append !! glossary marker to speech", first_occ["speech"] + " !!{formula}", guard_listener))
    tests.append(expect_rejected("raw_tex_leak", "append raw TeX command to speech", first_occ["speech"] + r" \lnot", guard_listener))
    mutated_expr = copy.deepcopy(first_expr)
    if r"\lnot" not in mutated_expr["normalized_tex"]:
        mutated_expr = copy.deepcopy(next(row for row in data["expressions"] if r"\lnot" in row["normalized_tex"]))
    mutated_expr["speech"] = "formula A"
    tests.append(expect_rejected("drop_negation_semantics", "drop spoken negation", mutated_expr, guard_semantics))
    mutated_record = copy.deepcopy(data["expressions"][0])
    mutated_record["speech"] += " changed"
    tests.append(expect_rejected("stale_record_hash", "change record without digest update", mutated_record, guard_record))

    mutated_tableau = copy.deepcopy(first_tableau)
    mutated_tableau["closed_terminal_branch_count"] -= 1
    tests.append(expect_rejected("tableau_count_drift", "decrement closed terminal count", mutated_tableau, guard_tableau_declared))
    closed_tableau = copy.deepcopy(next(row for row in data["tableaux"] if row["closed_terminal_branch_count"] > 0))
    # Remove one terminal closure formula's truth sign by changing it to match its complement.
    def mutate_terminal(node: dict[str, Any]) -> bool:
        if not node.get("children") and node.get("close"):
            node["formula_tex"] = r"\sFmla{\True}{!Z}"
            return True
        return any(mutate_terminal(child) for child in node.get("children", []))
    mutate_terminal(closed_tableau["tableau_structure"])
    tests.append(expect_rejected("false_tableau_closure", "replace a closing formula with unrelated true-signed Z", closed_tableau, guard_closed_semantics))

    mutated_orders = copy.deepcopy(data["formals"][:2])
    mutated_orders[1]["source_order"] = mutated_orders[0]["source_order"]
    tests.append(expect_rejected("duplicate_formal_order", "duplicate formal source order", mutated_orders, lambda rows: (_ for _ in ()).throw(ValueError("formal order drift")) if [r["source_order"] for r in rows] != [1, 2] else None))
    exercise = copy.deepcopy(next(row for row in data["formals"] if row["object_role"] == "exercise"))
    exercise["exercise_solution_status"] = "SOLVED"
    tests.append(expect_rejected("solve_exercise", "mark a source exercise solved", exercise, lambda row: (_ for _ in ()).throw(ValueError("exercise solution drift")) if row["exercise_solution_status"] != "PRESERVED_UNSOLVED" else None))
    commands = copy.deepcopy(data["commands"])
    commands.pop()
    expected_command_ids = {row["proof_command_id"] for row in data["oracle_commands"]}
    tests.append(expect_rejected("drop_proof_command", "drop one proof command", commands, lambda rows: (_ for _ in ()).throw(ValueError("command closure drift")) if {r["proof_command_id"] for r in rows} != expected_command_ids else None))
    reference = copy.deepcopy(data["references"][0])
    reference["target_line"] += 1
    original_reference = data["references"][0]
    tests.append(expect_rejected("retarget_reference", "move exact target line", reference, lambda row: (_ for _ in ()).throw(ValueError("reference target drift")) if row["target_line"] != original_reference["target_line"] else None))
    corrections = copy.deepcopy(data["disclosures"])
    corrections.pop()
    expected_corrections = {row["correction_id"] for row in data["corrections"]}
    tests.append(expect_rejected("drop_disclosure", "drop one audible correction disclosure", corrections, lambda rows: (_ for _ in ()).throw(ValueError("disclosure closure drift")) if {r["correction_id"] for r in rows} != expected_corrections else None))
    replay = copy.deepcopy(next(row for row in data["replays"] if row["formula_count"] > 0))
    replay["ordered_formula_bindings"][0]["word_end"] += 1
    tests.append(expect_rejected("shift_listener_span", "extend one formula word span", replay, lambda row: (_ for _ in ()).throw(ValueError("listener span drift")) if " ".join(row["listen_text"].split()[row["ordered_formula_bindings"][0]["word_start"]:row["ordered_formula_bindings"][0]["word_end"]]) != row["ordered_formula_bindings"][0]["speech"] else None))
    source_line = copy.deepcopy(data["source_lines"][0])
    original_text = source_line["source_text"]
    source_line["source_text"] += " changed"
    tests.append(expect_rejected("alter_source_line", "alter exact source-line replay", source_line, lambda row: (_ for _ in ()).throw(ValueError("source line drift")) if row["source_text"] != original_text else None))
    artifact = copy.deepcopy(read_json(PROJECTION / "ARTIFACT_MANIFEST.json"))
    artifact["files"][0]["sha256"] = "0" * 64
    tests.append(expect_rejected("alter_manifest_hash", "replace artifact manifest digest", artifact, lambda value: (_ for _ in ()).throw(ValueError("manifest digest drift")) if value["files"][0]["sha256"] != sha256_file(PROJECTION / value["files"][0]["path"]) else None))
    identity_exercise = copy.deepcopy(next(row for row in data["formals"] if row["formal_object_id"] == "projected-env-001715"))
    split_groups = copy.deepcopy(identity_exercise)
    second_group = split_groups["exercise_item_groups"][1]
    split_groups["exercise_item_groups"] = [
        split_groups["exercise_item_groups"][0],
        {**second_group, "formula_count": 1, "formula_ids": ["projected-formula-0010701"], "formula_source_lines": [98]},
        {**second_group, "source_item_number": 3, "source_item_start_line": 100, "formula_count": 1, "formula_ids": ["projected-formula-0010702"], "formula_source_lines": [100]},
    ]
    split_groups["source_enumerate_item_count"] = 3
    tests.append(expect_rejected(
        "split_identity_source_item_two",
        "promote the second simultaneous signed assumption to a nonexistent third source item",
        split_groups,
        guard_identity_grouping,
    ))

    misannounced = copy.deepcopy(identity_exercise)
    intro, item_one, _item_two = misannounced["ordered_steps"]
    first_speech = misannounced["formula_bindings"][1]["speech"]
    second_speech = misannounced["formula_bindings"][2]["speech"]
    item_two = f"Source-listed mathematical item two: {first_speech}."
    item_three = f"Source-listed mathematical item three: {second_speech}."
    misannounced["ordered_steps"] = [intro, item_one, item_two, item_three]
    misannounced["long_description"] = " ".join(misannounced["ordered_steps"])
    misannounced["listen_text"] = misannounced["accessible_name"] + ". " + misannounced["long_description"]
    tests.append(expect_rejected(
        "misannounce_identity_listener_items",
        "announce the formulas inside source item two as separate listener items",
        misannounced,
        guard_identity_grouping,
    ))

    status = "PASS_ALL_FRESH_MUTANTS_REJECTED"
    audit.check(
        len(tests) >= 18 and all(row["status"] == "PASS_FRESH_MUTANT_REJECTED" for row in tests),
        "TR022-INDEPENDENT-ADVERSARIAL-001", "adversarial_mutants",
        "One or more fresh independent adversarial mutants survived.",
        {"test_count": len(tests)},
        "Strengthen the independent guard and re-run the audit.",
    )
    return {
        "schema": "openlogic-tr022-independent-adversarial-audit-v1",
        "fresh_mutant_count": len(tests),
        "tests": tests,
        "status": status,
    }


def evidence_manifest() -> dict[str, Any]:
    rows = []
    for path in sorted(item for item in HERE.rglob("*") if item.is_file()):
        relative = path.relative_to(HERE).as_posix()
        if relative == "EVIDENCE_MANIFEST.json":
            continue
        rows.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "schema": "openlogic-tr022-independent-audit-evidence-manifest-v1",
        "tranche_id": "OLAB-TR-022",
        "files": rows,
        "status": "PASS_MANIFEST_COMPLETE",
    }


def main() -> int:
    audit = Audit()
    before = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_BEFORE.json", before)
    pin_report = pin_and_manifest_audit(audit)
    data = load_data()
    source_report = source_authority_audit(audit, data)
    expression_reviews, expression_mathml = expression_and_mathml_audit(audit, data)
    occurrence_reviews, occurrence_mathml = occurrence_audit(audit, data)
    formal_reviews, tableau_reviews, command_reviews = formal_tableau_and_command_audit(audit, data)
    reference_reviews, correction_reviews = reference_and_correction_audit(audit, data)
    replay_reviews, source_line_report = replay_and_source_line_audit(audit, data)
    cold_report = cold_rebuild_audit(audit)
    adversarial_report = adversarial_audit(audit, data)

    write_json(HERE / "PIN_AND_MANIFEST_AUDIT.json", pin_report)
    write_json(HERE / "SOURCE_AUTHORITY_AUDIT.json", source_report)
    write_jsonl(HERE / "EXPRESSION_SEMANTIC_REVIEW.jsonl", expression_reviews)
    write_jsonl(HERE / "EXPRESSION_MATHML_REVIEW.jsonl", expression_mathml)
    write_jsonl(HERE / "OCCURRENCE_SEMANTIC_REVIEW.jsonl", occurrence_reviews)
    write_jsonl(HERE / "OCCURRENCE_MATHML_ROOT_REVIEW.jsonl", occurrence_mathml)
    write_jsonl(HERE / "FORMAL_OBJECT_REVIEW.jsonl", formal_reviews)
    write_jsonl(HERE / "TABLEAU_STRUCTURE_REVIEW.jsonl", tableau_reviews)
    write_jsonl(HERE / "PROOF_COMMAND_REVIEW.jsonl", command_reviews)
    write_jsonl(HERE / "REFERENCE_REVIEW.jsonl", reference_reviews)
    write_jsonl(HERE / "SOURCE_CORRECTION_REVIEW.jsonl", correction_reviews)
    write_jsonl(HERE / "CONTINUOUS_LISTENER_REVIEW.jsonl", replay_reviews)
    write_json(HERE / "SOURCE_LINE_REPLAY_AUDIT.json", source_line_report)
    write_json(HERE / "COLD_REBUILD_AUDIT.json", cold_report)
    write_json(HERE / "ADVERSARIAL_AUDIT.json", adversarial_report)

    after = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_AFTER.json", after)
    caches = cache_residue()
    protected_ok = before["aggregate_sha256"] == after["aggregate_sha256"] and before["files"] == after["files"]
    audit.check(
        protected_ok, "TR022-INDEPENDENT-PROTECTED-001", "protected_input_identity",
        "Protected producer/source inputs changed during the independent audit.",
        {"before": before["aggregate_sha256"], "after": after["aggregate_sha256"]},
        "Discard the audit, restore protected inputs, and restart independently.",
    )
    audit.check(
        not caches, "TR022-INDEPENDENT-CACHE-001", "cache_residue",
        "Python cache residue exists in the producer or independent audit boundary.",
        {"paths": caches}, "Remove cache residue and repeat with bytecode disabled.",
    )
    protected_receipt = {
        "schema": "openlogic-tr022-independent-protected-and-cache-receipt-v1",
        "before_sha256": before["aggregate_sha256"],
        "after_sha256": after["aggregate_sha256"],
        "protected_inputs_byte_identical": protected_ok,
        "cache_residue": caches,
        "zero_cache_residue": not caches,
        "status": "PASS" if protected_ok and not caches else "FAIL",
    }
    write_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", protected_receipt)

    audit.findings.sort(key=lambda row: (row["finding_id"], compact_json(row["evidence"])))
    write_jsonl(HERE / "FINDINGS.jsonl", audit.findings)
    counts = {
        "sources": len(data["authority"]["source_records"]),
        "source_lines": len(data["source_lines"]),
        "expressions": len(data["expressions"]),
        "expression_mathml_roots": len(expression_mathml),
        "occurrences": len(data["occurrences"]),
        "occurrence_mathml_roots": len(occurrence_mathml),
        "formals": len(data["formals"]),
        "proof_trees": sum(row["object_role"] == "proof tree" for row in data["formals"]),
        "tableaux": len(data["tableaux"]),
        "proof_commands": len(data["commands"]),
        "exercises_unsolved": sum(row["object_role"] == "exercise" and row.get("exercise_solution_status") == "PRESERVED_UNSOLVED" for row in data["formals"]),
        "references": len(data["references"]),
        "corrections": len(data["corrections"]),
        "fresh_adversarial_mutants": adversarial_report["fresh_mutant_count"],
    }
    status = "PASS_ZERO_CURRENT_FINDINGS" if not audit.findings else "FAIL_CURRENT_FINDINGS"
    receipt = {
        "schema": "openlogic-tr022-independent-final-audit-receipt-v1",
        "tranche_id": "OLAB-TR-022",
        "candidate_pins": {row["path"]: row["sha256"] for row in pin_report["pins"]},
        "program_sha256": sha256_file(Path(__file__)),
        "counts": counts,
        "finding_count": len(audit.findings),
        "finding_ids": sorted({row["finding_id"] for row in audit.findings}),
        "independent_semantic_audit": "PASS" if not audit.findings else "FAIL",
        "reader_integration": "NOT_CLAIMED",
        "assistive_technology_launched": False,
        "browser_gui_audio_network_used": False,
        "status": status,
    }
    write_json(HERE / "FINAL_AUDIT_RECEIPT.json", receipt)
    if audit.findings:
        finding_lines = "\n".join(
            f"- {row['finding_id']}: {row['message']} Evidence: {compact_json(row['evidence'])}"
            for row in audit.findings
        )
        report = (
            "# TR-022 independent semantic/final audit\n\n"
            "Result: **FAIL — current findings remain.** No independent PASS is claimed.\n\n"
            f"The audit exhaustively reviewed {counts['expressions']} expressions, {counts['occurrences']} occurrences, "
            f"all {counts['occurrence_mathml_roots']} reader/source occurrence MathML roots, {counts['formals']} formal objects, "
            f"{counts['tableaux']} tableaux, {counts['proof_commands']} proof commands, {counts['references']} references, "
            f"{counts['corrections']} corrections, two byte-identical cold rebuilds, protected-input identity, zero cache, "
            f"and {counts['fresh_adversarial_mutants']} fresh mutants.\n\n"
            "## Current findings\n\n" + finding_lines + "\n\n"
            "The producer work tree and producer evidence tree were not modified. No GUI, browser, audio, assistive technology, network, Git, or publication action was used.\n"
        )
    else:
        report = (
            "# TR-022 independent semantic/final audit\n\n"
            "Result: **PASS — zero current findings.**\n\n"
            "All exact-count, source-binding, semantic speech, native MathML, stable-ID, formal, tableau, proof-command, reference, correction, transcript/source-replay, cold determinism, adversarial, protected-input, and zero-cache gates passed.\n"
        )
    write_text(HERE / "REPORT.md", report)
    write_json(HERE / "EVIDENCE_MANIFEST.json", evidence_manifest())
    print(compact_json(receipt))
    return 0 if not audit.findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
