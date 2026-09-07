#!/usr/bin/env python3
"""Fresh, read-only independent audit of OLAB-TR-023.

This program does not import or call the producer builder, validator, tests, or
certifier.  It independently reconciles the frozen source, the source oracle,
and the producer projection; writes only below this audit directory; runs its
own adversarial guards; and produces two isolated deterministic audit runs.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PROJECTION = PROJECT / "evidence" / "tranche_023_fol_axiomatic_deduction_projection"
ORACLE = PROJECT / "evidence" / "tranche_023_fol_axiomatic_deduction_oracle"
WORK = PROJECT / "work" / "tranche_023_fol_axiomatic_deduction_projection"

EXPECTED = {
    "source_files": 14,
    "source_lines": 1152,
    "source_bytes": 40484,
    "expressions": 209,
    "occurrences": 475,
    "primary_expression_mathml_roots": 418,
    "source_fidelity_mathml_roots": 6,
    "occurrence_mathml_roots": 475,
    "formals": 61,
    "derivations": 5,
    "derivation_printed_lines": 23,
    "references": 84,
    "exercises": 8,
    "corrections": 5,
    "listen_streams": 14,
}

PINS = {
    "ARTIFACT_MANIFEST.json": "41b9325a1b6ee4170ed59707aac405929e9d485fc95f8ef312049e37f38b1a35",
    "EVIDENCE_MANIFEST.json": "8ad4b3496225c2534cada32a8de71c8558772aaf2295c728f6c6ee309adc8532",
    "PRODUCER_RECEIPT.json": "b652706fd64b440a88f504312eed4bd1b726754a8b9fe1a58b66899aaca55f8e",
    "producer_validation/PRODUCER_CERTIFICATION.json": "2626fd9438fe2b83f38b87bc035e0c05fece67c38e023ad5b095249d38c53cd3",
}
EXPECTED_PRODUCER_TREE = "f7d6f9513b798cfdef131442da01c044e45989d20c78b01b3f678acd42586a02"
AUTHORITY_COMMIT = "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"

FORBIDDEN_ROOT_ATTRIBUTES = {
    "alttext", "aria-label", "aria-labelledby", "class", "role", "title",
}
LISTENER_RESIDUE = re.compile(
    r"!!|OPENLOGIC(?:FORMULA|REFERENCE|DISCLOSURE)|\\[A-Za-z]+|[$^{}_]|"
    r"[¬∧∨→⇒↔∀∃⊢⊨⊥⊤∈∅∪∩⊆⊇≠≤≥]"
)
EXTERNAL_OR_SCRIPT = re.compile(r"(?i)<script\b|javascript:|https://|http://(?!www\.w3\.org/1998/Math/MathML)")

DERIVATION_GROUPS = {
    "projected-env-001735": [
        ["projected-formula-0010818"],
        ["projected-formula-0010819", "projected-formula-0010820"],
        ["projected-formula-0010821"],
        ["projected-formula-0010822"],
        ["projected-formula-0010823"],
    ],
    "projected-env-001737": [
        ["projected-formula-0010850"],
        ["projected-formula-0010851", "projected-formula-0010852"],
        ["projected-formula-0010853"],
        ["projected-formula-0010854"],
        ["projected-formula-0010855"],
    ],
    "projected-env-001739": [
        ["projected-formula-0010859"],
        ["projected-formula-0010860"],
        ["projected-formula-0010861"],
        ["projected-formula-0010862"],
        ["projected-formula-0010863", "projected-formula-0010864"],
        ["projected-formula-0010865"],
        ["projected-formula-0010866"],
    ],
    "projected-env-001765": [
        ["projected-formula-0010967"],
        ["projected-formula-0010968"],
        ["projected-formula-0010969"],
    ],
    "projected-env-001798": [
        ["projected-formula-0011086"],
        ["projected-formula-0011087"],
        ["projected-formula-0011088"],
    ],
}

EXERCISE_IDS = {
    "projected-env-001744", "projected-env-001759", "projected-env-001772",
    "projected-env-001776", "projected-env-001781", "projected-env-001786",
    "projected-env-001814", "projected-env-001822",
}

CORRECTION_EXPECTATIONS = {
    "TR023-SOURCE-FORMULA-001": {
        "file": "content/first-order-logic/axiomatic-deduction/deduction-theorem.tex",
        "lines": [67], "formulas": ["projected-formula-0010985"],
        "kind": "missing_membership_subject",
    },
    "TR023-SOURCE-FORMULA-002": {
        "file": "content/first-order-logic/axiomatic-deduction/deduction-theorem.tex",
        "lines": [106, 107], "formulas": ["projected-formula-0011008"],
        "kind": "missing_closing_parenthesis",
    },
    "TR023-SOURCE-FORMULA-005": {
        "file": "content/first-order-logic/axiomatic-deduction/deduction-theorem-quantifiers.tex",
        "lines": [44], "formulas": ["projected-formula-0011028"],
        "kind": "missing_closing_parenthesis_in_quantified_conditional",
    },
    "TR023-SOURCE-PROSE-004": {
        "file": "content/first-order-logic/axiomatic-deduction/provability-propositional.tex",
        "lines": [58], "formulas": [], "kind": "misspelled_rule_name",
    },
    "TR023-SOURCE-REFERENCE-003": {
        "file": "content/first-order-logic/axiomatic-deduction/provability-propositional.tex",
        "lines": [33], "formulas": [], "kind": "duplicated_axiom_reference",
    },
}

SENSITIVE_FORMAL_EXPECTATIONS = {
    "projected-env-001721": ["finite sequence", "premise", "axiom", "inference rule"],
    "projected-env-001729": ["fourteen", "three for conjunction", "double-negation elimination"],
    "projected-env-001730": ["substitution instances", "fourteen schemes"],
    "projected-env-001732": ["two quantifier schemes", "universal instantiation", "existential introduction"],
    "projected-env-001733": ["closed term", "universal instantiation", "existential introduction"],
    "projected-env-001734": ["universal", "existential", "eigenvariable condition"],
    "projected-env-001745": ["complete source-order argument", "every intermediate conditional"],
    "projected-env-001768": ["two consequences", "printed order"],
    "projected-env-001774": ["universal-quantifier rule case", "induction", "nested conditional"],
    "projected-env-001818": ["identity reflexivity", "substitution-of-identicals"],
    "projected-env-001819": ["reflexivity of identity", "substitution of identical closed terms"],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def value_sha256(value: Any) -> str:
    return sha256_bytes(compact_json(value).encode("utf-8"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def record_hash_ok(row: Mapping[str, Any]) -> bool:
    payload = dict(row)
    claimed = payload.pop("record_sha256", None)
    return claimed == value_sha256(payload)


def listener_ok(value: str) -> bool:
    return bool(value.strip()) and not LISTENER_RESIDUE.search(value)


def write_text(root: Path, relative: str, value: str) -> None:
    target = (root / relative).resolve()
    if not target.is_relative_to(HERE):
        raise RuntimeError(f"audit write escaped isolated evidence tree: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding="utf-8", newline="\n")


def write_json(root: Path, relative: str, value: Any) -> None:
    write_text(root, relative, canonical_json(value))


def write_jsonl(root: Path, relative: str, rows: Iterable[Mapping[str, Any]]) -> None:
    write_text(root, relative, "".join(compact_json(dict(row)) + "\n" for row in rows))


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(HERE) or resolved in {HERE, HERE.parent}:
        raise RuntimeError(f"unsafe audit-local reset target: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def tree_snapshot(root: Path, *, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


class Audit:
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    def check(
        self,
        condition: bool,
        finding_id: str,
        category: str,
        message: str,
        evidence: Mapping[str, Any],
        remediation: str,
    ) -> None:
        if condition:
            return
        self.findings.append({
            "finding_id": finding_id,
            "severity": "P1",
            "category": category,
            "message": message,
            "evidence": dict(evidence),
            "remediation": remediation,
            "status": "OPEN",
        })


def protected_snapshot() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[Path] = set()

    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    source_root = Path(authority["authority_root"])
    for record in authority["source_records"]:
        path = source_root / record["path"]
        seen.add(path.resolve())
        rows.append({
            "boundary": "immutable_source",
            "path": record["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    for boundary, root in (("oracle", ORACLE), ("producer_projection", PROJECTION)):
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.resolve() in seen:
                continue
            seen.add(path.resolve())
            rows.append({
                "boundary": boundary,
                "path": path.relative_to(PROJECT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })

    upstream = read_json(PROJECTION / "UPSTREAM_INPUTS.json")
    for record in upstream["inputs"]:
        path = PROJECT / record["path"]
        if path.resolve() in seen:
            continue
        seen.add(path.resolve())
        rows.append({
            "boundary": "producer_input",
            "path": record["path"],
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    rows.sort(key=lambda row: (row["boundary"], row["path"]))
    return {
        "schema": "openlogic-tr023-independent-protected-snapshot-v1",
        "files": rows,
        "file_count": len(rows),
        "aggregate_sha256": value_sha256(rows),
    }


def cache_residue() -> list[str]:
    found: list[str] = []
    for root in (HERE, WORK, ORACLE, PROJECTION):
        for path in root.rglob("*"):
            if path.is_dir() and path.name == "__pycache__":
                found.append(path.relative_to(PROJECT).as_posix() if path.is_relative_to(PROJECT) else str(path))
            elif path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}:
                found.append(path.relative_to(PROJECT).as_posix() if path.is_relative_to(PROJECT) else str(path))
    return sorted(set(found))


def producer_tree() -> list[dict[str, Any]]:
    return [
        {
            "path": path.relative_to(PROJECTION).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(PROJECTION.rglob("*"))
        if path.is_file() and not path.relative_to(PROJECTION).as_posix().startswith("producer_validation/")
    ]


def pin_manifest_audit(audit: Audit) -> dict[str, Any]:
    pin_rows = []
    for relative, expected in PINS.items():
        actual = sha256_file(PROJECTION / relative)
        pin_rows.append({"path": relative, "expected_sha256": expected, "actual_sha256": actual,
                         "status": "PASS" if actual == expected else "FAIL"})
        audit.check(
            actual == expected, "TR023-INDEPENDENT-PIN-001", "input_pin",
            "A supplied producer pin does not match the audited file.",
            {"path": relative, "expected": expected, "actual": actual},
            "Freeze the intended producer candidate and restart a new independent audit.",
        )

    artifact = read_json(PROJECTION / "ARTIFACT_MANIFEST.json")
    artifact_rows = artifact["artifacts"]
    expected_artifact_paths = sorted(
        path.name for path in PROJECTION.iterdir()
        if path.is_file() and path.name not in {"ARTIFACT_MANIFEST.json", "EVIDENCE_MANIFEST.json"}
    )
    actual_artifact_paths = sorted(row["path"] for row in artifact_rows)
    audit.check(
        expected_artifact_paths == actual_artifact_paths,
        "TR023-INDEPENDENT-MANIFEST-001", "artifact_manifest",
        "Producer artifact manifest path closure is not exact.",
        {"expected": expected_artifact_paths, "actual": actual_artifact_paths},
        "Regenerate the artifact manifest from the complete producer core.",
    )
    bad_artifacts = []
    for row in artifact_rows:
        path = PROJECTION / row["path"]
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            bad_artifacts.append({"path": row["path"], "declared": row, "actual": actual})
    audit.check(
        not bad_artifacts, "TR023-INDEPENDENT-MANIFEST-002", "artifact_manifest",
        "One or more producer artifact-manifest records are stale.",
        {"mismatches": bad_artifacts}, "Regenerate the manifest and certification.",
    )

    validation_manifest = read_json(PROJECTION / "producer_validation" / "EVIDENCE_MANIFEST.json")
    validation_rows = validation_manifest["artifacts"]
    validation_root = PROJECTION / "producer_validation"
    expected_validation_paths = sorted(
        path.name for path in validation_root.iterdir()
        if path.is_file() and path.name != "EVIDENCE_MANIFEST.json"
    )
    actual_validation_paths = sorted(row["path"] for row in validation_rows)
    validation_bad = []
    for row in validation_rows:
        path = validation_root / row["path"]
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            validation_bad.append({"path": row["path"], "declared": row, "actual": actual})
    audit.check(
        expected_validation_paths == actual_validation_paths and not validation_bad,
        "TR023-INDEPENDENT-MANIFEST-003", "validation_manifest",
        "Producer-certification evidence closure is not exact.",
        {"expected": expected_validation_paths, "actual": actual_validation_paths, "mismatches": validation_bad},
        "Regenerate producer certification evidence before acceptance.",
    )

    root_manifest = read_json(PROJECTION / "EVIDENCE_MANIFEST.json")
    root_pointer_ok = (
        root_manifest.get("artifact_manifest", {}).get("sha256") == PINS["ARTIFACT_MANIFEST.json"]
        and root_manifest.get("oracle_manifest_sha256") == sha256_file(ORACLE / "EVIDENCE_MANIFEST.json")
    )
    audit.check(
        root_pointer_ok, "TR023-INDEPENDENT-MANIFEST-004", "root_manifest",
        "Producer root manifest does not pin its artifact/oracle authorities.",
        {"root_manifest": root_manifest}, "Repair the root evidence pointer manifest.",
    )

    tree = producer_tree()
    tree_digest = value_sha256(tree)
    audit.check(
        tree_digest == EXPECTED_PRODUCER_TREE,
        "TR023-INDEPENDENT-PIN-002", "producer_tree",
        "The complete non-validation producer tree does not match the supplied pin.",
        {"expected": EXPECTED_PRODUCER_TREE, "actual": tree_digest, "file_count": len(tree)},
        "Freeze the exact certified producer tree and repeat the independent audit.",
    )

    upstream = read_json(PROJECTION / "UPSTREAM_INPUTS.json")
    upstream_bad = []
    for row in upstream["inputs"]:
        path = PROJECT / row["path"]
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            upstream_bad.append({"path": row["path"], "declared": row, "actual": actual})
    audit.check(
        not upstream_bad, "TR023-INDEPENDENT-UPSTREAM-001", "upstream_inputs",
        "A hash-pinned producer input has drifted.", {"mismatches": upstream_bad},
        "Restore the pinned authority chain and rebuild the producer candidate.",
    )

    return {
        "schema": "openlogic-tr023-independent-pin-manifest-audit-v1",
        "pins": pin_rows,
        "artifact_manifest_entries": len(artifact_rows),
        "producer_validation_manifest_entries": len(validation_rows),
        "producer_tree_file_count": len(tree),
        "producer_tree_bytes": sum(row["bytes"] for row in tree),
        "producer_tree_sha256": tree_digest,
        "upstream_input_count": len(upstream["inputs"]),
        "status": "PASS" if all(row["status"] == "PASS" for row in pin_rows) and not bad_artifacts and not validation_bad and root_pointer_ok and tree_digest == EXPECTED_PRODUCER_TREE and not upstream_bad else "FAIL",
    }


def load_data() -> dict[str, Any]:
    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    return {
        "authority": authority,
        "source_root": Path(authority["authority_root"]),
        "shapes": read_tsv(ORACLE / "formula_shapes.tsv"),
        "oracle_contexts": read_jsonl(ORACLE / "formula_contexts.jsonl"),
        "oracle_occurrences": read_jsonl(ORACLE / "formula_occurrences.jsonl"),
        "oracle_formals": read_jsonl(ORACLE / "formal_objects.jsonl"),
        "oracle_refs": read_jsonl(ORACLE / "references.jsonl"),
        "expressions": read_jsonl(PROJECTION / "expression_semantics.jsonl"),
        "context_reviews": read_jsonl(PROJECTION / "EXPRESSION_CONTEXT_REVIEW.jsonl"),
        "occurrences": read_jsonl(PROJECTION / "semantic_occurrences.jsonl"),
        "formals": read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl"),
        "references": read_jsonl(PROJECTION / "REFERENCE_LEDGER.jsonl"),
        "corrections": read_jsonl(PROJECTION / "SOURCE_CORRECTIONS.jsonl"),
        "source_lines": read_jsonl(PROJECTION / "SOURCE_LINE_REPLAY.jsonl"),
        "streams": read_jsonl(PROJECTION / "continuous_listen_stream.jsonl"),
        "disclosures": read_jsonl(PROJECTION / "LISTENER_DISCLOSURE_BINDINGS.jsonl"),
    }


def source_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    authority = data["authority"]
    source_root: Path = data["source_root"]
    records = authority["source_records"]
    audit.check(
        authority.get("authority_commit") == AUTHORITY_COMMIT and authority.get("mutable") is False,
        "TR023-INDEPENDENT-SOURCE-001", "source_authority",
        "Source authority is not the required immutable commit.",
        {"commit": authority.get("authority_commit"), "mutable": authority.get("mutable")},
        "Restore the frozen detached source authority.",
    )
    reviews = []
    total_lines = total_bytes = 0
    for ordinal, record in enumerate(records, 1):
        path = source_root / record["path"]
        raw = path.read_bytes()
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        status = (
            len(raw) == record["bytes"]
            and len(lines) == record["lines"]
            and sha256_bytes(raw) == record["sha256"]
        )
        reviews.append({
            "source_ordinal": ordinal,
            "path": record["path"],
            "declared_bytes": record["bytes"],
            "actual_bytes": len(raw),
            "declared_lines": record["lines"],
            "actual_lines": len(lines),
            "declared_sha256": record["sha256"],
            "actual_sha256": sha256_bytes(raw),
            "status": "PASS_EXACT_IMMUTABLE_SOURCE" if status else "FAIL",
        })
        audit.check(
            status, "TR023-INDEPENDENT-SOURCE-002", "source_file",
            "A frozen source record does not replay exactly.", reviews[-1],
            "Restore the exact source file at the pinned commit.",
        )
        total_lines += len(lines)
        total_bytes += len(raw)

    source_closure = read_json(PROJECTION / "SOURCE_CLOSURE.json")
    exact_counts = (
        len(records) == EXPECTED["source_files"]
        and total_lines == EXPECTED["source_lines"]
        and total_bytes == EXPECTED["source_bytes"]
        and source_closure["source_records"] == records
    )
    audit.check(
        exact_counts, "TR023-INDEPENDENT-SOURCE-003", "source_closure",
        "Source closure counts or record sequence are not exact.",
        {"files": len(records), "lines": total_lines, "bytes": total_bytes},
        "Rebuild from the complete 14-file source authority.",
    )
    return ({
        "schema": "openlogic-tr023-independent-source-audit-v1",
        "authority_commit": authority.get("authority_commit"),
        "source_files": len(records), "source_lines": total_lines, "source_bytes": total_bytes,
        "status": "PASS_EXACT_SOURCE_CLOSURE" if exact_counts and all(row["status"].startswith("PASS") for row in reviews) else "FAIL",
    }, reviews)


def semantic_obligations(tex: str, speech: str) -> list[dict[str, Any]]:
    lower = speech.lower()
    macro = lambda name: re.search(r"\\" + re.escape(name) + r"(?![A-Za-z])", tex) is not None
    rules: list[tuple[bool, str, tuple[str, ...]]] = [
        (macro("lnot"), "negation", ("not", "negation")),
        (macro("land"), "conjunction", (" and ", "conjunction")),
        (macro("lor"), "disjunction", (" or ", "disjunction")),
        (macro("lif"), "conditional", ("implies", "conditional", "antecedent")),
        (macro("liff"), "biconditional", ("biconditional",)),
        (macro("lforall"), "universal_quantifier", ("for every", "universal")),
        (macro("lexists"), "existential_quantifier", ("for some", "existential")),
        (macro("cup"), "union", ("union",)),
        (macro("subseteq"), "subset", ("subset",)),
        (macro("in"), "membership", ("belongs", "member")),
        (macro("Entails"), "semantic_entailment", ("entail",)),
        (macro("Sat"), "satisfaction", ("satisf",)),
        (macro("Proves"), "derivability", ("deriv", "axiomatic")),
        (macro("lfalse"), "falsum", ("falsum",)),
        (macro("ltrue") or macro("top"), "truth_constant", ("verum", "truth constant", "top")),
        (macro("eq") or macro("ident"), "identity", ("identical", "identity")),
        (macro("Subst"), "substitution", ("substitut",)),
        (macro("Value"), "term_value", ("value",)),
        (macro("Assign"), "interpretation", ("interpretation",)),
        (macro("varAssign"), "assignment_agreement", ("agrees",)),
        (macro("dots"), "ellipsis", ("through", "omitted", "dots")),
        (macro("QR"), "quantifier_rule", ("quantifier rule",)),
        (macro("MP"), "modus_ponens", ("modus ponens",)),
        (macro("le"), "less_or_equal", ("less than or equal",)),
        (" < " in tex, "strict_order", ("less than",)),
        (" = " in tex, "equality", ("equals", "last formula is")),
    ]
    rows = []
    for applies, name, alternatives in rules:
        if not applies:
            continue
        good = any(token in lower for token in alternatives)
        rows.append({"obligation": name, "alternatives": list(alternatives), "status": "PASS" if good else "FAIL"})
    if r"\Proves/" in tex or r"\Sat/" in tex:
        good = " not " in f" {lower} " or "does not" in lower
        rows.append({"obligation": "negated_relation", "alternatives": ["not", "does not"], "status": "PASS" if good else "FAIL"})
    return rows


def inspect_mathml(
    value: str,
    expression_id: str,
    formula_id: str | None,
    display: str,
    tex: str,
) -> tuple[bool, dict[str, Any]]:
    problems: list[str] = []
    try:
        root = ET.fromstring(value)
    except ET.ParseError as exc:
        return False, {"problems": [f"parse:{exc}"]}
    if local_name(root.tag) != "math" or not root.tag.startswith("{http://www.w3.org/1998/Math/MathML}"):
        problems.append("root_is_not_namespaced_math")
    forbidden = sorted(FORBIDDEN_ROOT_ATTRIBUTES.intersection(root.attrib))
    if forbidden:
        problems.append("forbidden_root_attributes:" + ",".join(forbidden))
    if root.attrib.get("display") != display:
        problems.append("display_mismatch")
    if root.attrib.get("data-expression-id") != expression_id:
        problems.append("expression_id_mismatch")
    if formula_id is None:
        if "data-formula-id" in root.attrib:
            problems.append("unexpected_formula_id")
    elif root.attrib.get("data-formula-id") != formula_id:
        problems.append("formula_id_mismatch")
    descendants = list(root.iter())
    if len(descendants) < 4:
        problems.append("flattened_or_empty_tree")
    semantic_nodes = [node for node in descendants if local_name(node.tag) == "semantics"]
    annotations = [node for node in descendants if local_name(node.tag) == "annotation"]
    presentation = [
        node for node in descendants
        if local_name(node.tag) in {"mi", "mn", "mo", "mrow", "msub", "msup", "mtable", "mtr", "mtd", "mstyle", "mtext"}
    ]
    if len(semantic_nodes) != 1 or len(annotations) != 1 or not presentation:
        problems.append("missing_native_semantics_or_presentation")
    elif annotations[0].attrib.get("encoding") != "application/x-tex" or (annotations[0].text or "") != tex:
        problems.append("tex_annotation_mismatch")
    return not problems, {
        "sha256": sha256_bytes(value.encode("utf-8")),
        "element_count": len(descendants),
        "presentation_element_count": len(presentation),
        "root_attributes": dict(sorted(root.attrib.items())),
        "problems": problems,
    }


def expression_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    shapes = {row["expression_id"]: row for row in data["shapes"]}
    expressions = data["expressions"]
    contexts_by_expr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data["oracle_contexts"]:
        contexts_by_expr[row["expression_id"]].append(row)
    ids = [row["expression_id"] for row in expressions]
    audit.check(
        len(expressions) == EXPECTED["expressions"] and len(ids) == len(set(ids)) and set(ids) == set(shapes),
        "TR023-INDEPENDENT-EXPRESSION-001", "expression_closure",
        "Expression IDs do not exactly close over the oracle shapes.",
        {"candidate_count": len(expressions), "unique_count": len(set(ids)), "oracle_count": len(shapes)},
        "Regenerate the exhaustive expression authority.",
    )
    reviews = []
    primary_roots = source_roots = 0
    for row in expressions:
        expression_id = row["expression_id"]
        shape = shapes.get(expression_id, {})
        expected_context_ids = [item["formula_id"] for item in contexts_by_expr.get(expression_id, [])]
        obligations = semantic_obligations(row["normalized_tex"], row["speech"])
        inline_ok, inline = inspect_mathml(row["mathml_inline"], expression_id, None, "inline", row["normalized_tex"])
        block_ok, block = inspect_mathml(row["mathml_block"], expression_id, None, "block", row["normalized_tex"])
        primary_roots += 2
        source_variant_reviews = []
        for key, display in (("source_mathml_inline", "inline"), ("source_mathml_block", "block")):
            if key in row:
                ok, review = inspect_mathml(row[key], expression_id, None, display, row["normalized_tex"])
                review.update({"variant": key, "status": "PASS" if ok else "FAIL"})
                source_variant_reviews.append(review)
                source_roots += 1
        row_ok = (
            expression_id in shapes
            and row["normalized_tex"] == shape.get("normalized_tex")
            and row.get("physical_unique_source_occurrences") == int(shape.get("physical_unique_source_occurrences", -1))
            and row.get("canonical_projected_occurrences") == int(shape.get("canonical_projected_occurrences", -1))
            and row.get("occurrence_count") == len(expected_context_ids)
            and row.get("reviewed_occurrence_ids") == expected_context_ids
            and record_hash_ok(row)
            and listener_ok(row.get("speech", ""))
            and listener_ok(row.get("meaning", ""))
            and all(item["status"] == "PASS" for item in obligations)
            and inline_ok and block_ok
            and all(item["status"] == "PASS" for item in source_variant_reviews)
        )
        reviews.append({
            "expression_id": expression_id,
            "normalized_tex_sha256": sha256_bytes(row["normalized_tex"].encode("utf-8")),
            "speech_sha256": sha256_bytes(row["speech"].encode("utf-8")),
            "meaning_sha256": sha256_bytes(row["meaning"].encode("utf-8")),
            "reviewed_occurrence_count": len(expected_context_ids),
            "semantic_obligations": obligations,
            "inline_mathml": inline,
            "block_mathml": block,
            "source_fidelity_variants": source_variant_reviews,
            "status": "PASS_INDEPENDENT_EXPRESSION_SEMANTIC_AND_MATHML_REVIEW" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-EXPRESSION-002", "expression_semantics_mathml",
            "An expression failed independent semantic, closure, record, or MathML review.",
            {"expression_id": expression_id, "review": reviews[-1]},
            "Correct the expression at its exact source contexts and regenerate dependent evidence.",
        )
    root_counts_ok = (
        primary_roots == EXPECTED["primary_expression_mathml_roots"]
        and source_roots == EXPECTED["source_fidelity_mathml_roots"]
    )
    audit.check(
        root_counts_ok, "TR023-INDEPENDENT-MATHML-001", "expression_mathml_closure",
        "Expression MathML root counts are not exact.",
        {"primary": primary_roots, "source_fidelity": source_roots},
        "Restore all inline/block native MathML variants.",
    )
    receipt = {
        "schema": "openlogic-tr023-independent-expression-mathml-audit-v1",
        "expressions": len(expressions),
        "primary_mathml_roots": primary_roots,
        "source_fidelity_mathml_roots": source_roots,
        "root_forbidden_attributes": sorted(FORBIDDEN_ROOT_ATTRIBUTES),
        "status": "PASS" if root_counts_ok and all(row["status"].startswith("PASS") for row in reviews) else "FAIL",
    }
    return reviews, receipt


def occurrence_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    oracle = data["oracle_contexts"]
    occurrences = data["occurrences"]
    context_reviews = data["context_reviews"]
    expression_by_id = {row["expression_id"]: row for row in data["expressions"]}
    oracle_by_id = {row["formula_id"]: row for row in oracle}
    review_by_id = {row["formula_id"]: row for row in context_reviews}
    ids = [row["formula_id"] for row in occurrences]
    exact_ids = ids == [row["formula_id"] for row in oracle] and len(ids) == len(set(ids))
    audit.check(
        len(occurrences) == EXPECTED["occurrences"] and exact_ids and len(context_reviews) == len(oracle),
        "TR023-INDEPENDENT-OCCURRENCE-001", "occurrence_closure",
        "Occurrence/context IDs do not exactly replay the oracle in source order.",
        {"occurrences": len(occurrences), "context_reviews": len(context_reviews), "oracle": len(oracle)},
        "Regenerate the complete contextual occurrence ledger.",
    )
    source_cache = {
        record["path"]: (data["source_root"] / record["path"]).read_text(encoding="utf-8").splitlines()
        for record in data["authority"]["source_records"]
    }
    comparable = ("context_id", "formula_id", "expression_id", "file", "line", "column", "delimiter", "instance_id", "normalized_tex")
    reviews = []
    roots = 0
    for row in occurrences:
        formula_id = row["formula_id"]
        source = oracle_by_id.get(formula_id, {})
        packet = review_by_id.get(formula_id, {})
        expr = expression_by_id.get(row["expression_id"], {})
        source_lines = source_cache.get(row["file"], [])
        line_index = row["line"] - 1
        actual_packet = {
            "previous_source_line": source_lines[line_index - 1] if line_index > 0 else "",
            "source_line": source_lines[line_index] if 0 <= line_index < len(source_lines) else None,
            "next_source_line": source_lines[line_index + 1] if line_index + 1 < len(source_lines) else "",
        }
        packet_exact = all(packet.get(key) == value for key, value in actual_packet.items())
        display = "block" if row["display_mode"] == "block" else "inline"
        mathml_ok, mathml_review = inspect_mathml(
            row["mathml"], row["expression_id"], formula_id, display, row["normalized_tex"]
        )
        roots += 1
        obligations = semantic_obligations(row["normalized_tex"], row["speech"])
        exact_coordinate = all(row.get(key) == source.get(key) for key in comparable)
        context_exact = all(packet.get(key) == source.get(key) for key in comparable)
        binding_exact = (
            packet.get("speech") == row.get("speech")
            and packet.get("meaning") == row.get("meaning")
            and packet.get("source_packet_sha256") == row.get("source_packet_sha256")
            and packet.get("reader_correction") == row.get("reader_correction")
            and packet.get("source_correction_ids") == row.get("source_correction_ids")
        )
        expression_bound = expr and row["normalized_tex"] == expr["normalized_tex"]
        row_ok = (
            exact_coordinate and context_exact and packet_exact and binding_exact and expression_bound
            and record_hash_ok(row) and record_hash_ok(packet)
            and listener_ok(row.get("speech", "")) and listener_ok(row.get("meaning", ""))
            and all(item["status"] == "PASS" for item in obligations) and mathml_ok
        )
        reviews.append({
            "formula_id": formula_id,
            "expression_id": row.get("expression_id"),
            "file": row.get("file"), "line": row.get("line"), "column": row.get("column"),
            "source_packet_exact": packet_exact,
            "context_and_occurrence_binding_exact": binding_exact,
            "semantic_obligations": obligations,
            "mathml": mathml_review,
            "source_correction_ids": row.get("source_correction_ids"),
            "status": "PASS_INDEPENDENT_CONTEXT_OCCURRENCE_REVIEW" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-OCCURRENCE-002", "contextual_occurrence",
            "A contextual occurrence failed source, semantic, stable-ID, or MathML replay.",
            {"formula_id": formula_id, "review": reviews[-1]},
            "Repair the exact contextual binding and regenerate all dependent artifacts.",
        )
    audit.check(
        roots == EXPECTED["occurrence_mathml_roots"],
        "TR023-INDEPENDENT-MATHML-002", "occurrence_mathml_closure",
        "Occurrence MathML root count is not exact.", {"actual": roots},
        "Restore one native MathML root for every stable occurrence.",
    )
    receipt = {
        "schema": "openlogic-tr023-independent-occurrence-audit-v1",
        "occurrences": len(occurrences), "mathml_roots": roots,
        "zero_root_aria_role_class": all(not row["mathml"]["problems"] for row in reviews),
        "status": "PASS" if roots == EXPECTED["occurrence_mathml_roots"] and all(row["status"].startswith("PASS") for row in reviews) else "FAIL",
    }
    return reviews, receipt


def source_line_replay_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lines = data["source_lines"]
    formulas_by_line: dict[tuple[str, int], list[str]] = defaultdict(list)
    refs_by_line: dict[tuple[str, int], list[str]] = defaultdict(list)
    formals_by_line: dict[tuple[str, int], list[str]] = defaultdict(list)
    corrections_by_line: dict[tuple[str, int], list[str]] = defaultdict(list)
    for row in data["oracle_contexts"]:
        formulas_by_line[(row["file"], row["line"])].append(row["formula_id"])
    for row in data["oracle_refs"]:
        refs_by_line[(row["file"], row["line"])].append(row["reference_id"])
    for row in data["oracle_formals"]:
        formals_by_line[(row["file"], row["line"])].append(row["environment_id"])
    for row in data["corrections"]:
        for line in row["lines"]:
            corrections_by_line[(row["file"], line)].append(row["correction_id"])
    source_records = data["authority"]["source_records"]
    expected_rows: list[tuple[int, str, int, str]] = []
    for ordinal, record in enumerate(source_records, 1):
        source = (data["source_root"] / record["path"]).read_text(encoding="utf-8").splitlines()
        expected_rows.extend((ordinal, record["path"], index, text) for index, text in enumerate(source, 1))
    audit.check(
        len(lines) == EXPECTED["source_lines"] and len(lines) == len(expected_rows),
        "TR023-INDEPENDENT-LINE-001", "source_line_closure",
        "Source-line replay count is not exact.",
        {"candidate": len(lines), "expected": len(expected_rows)},
        "Regenerate the full source-line replay ledger.",
    )
    reviews = []
    for index, expected in enumerate(expected_rows):
        row = lines[index] if index < len(lines) else {}
        ordinal, file, line_number, source_text = expected
        key = (file, line_number)
        expected_id = f"tr023-source-line-{ordinal:02d}-{line_number:04d}"
        row_ok = (
            row.get("source_ordinal") == ordinal and row.get("file") == file
            and row.get("line") == line_number and row.get("source_text") == source_text
            and row.get("source_line_id") == expected_id
            and row.get("source_line_sha256") == sha256_bytes((source_text + "\n").encode("utf-8"))
            and row.get("formula_ids") == formulas_by_line[key]
            and row.get("reference_ids") == refs_by_line[key]
            and row.get("formal_object_ids_starting_here") == formals_by_line[key]
            and row.get("correction_ids") == corrections_by_line[key]
            and record_hash_ok(row)
        )
        reviews.append({
            "source_line_id": expected_id,
            "file": file, "line": line_number,
            "source_text_sha256": sha256_bytes(source_text.encode("utf-8")),
            "formula_ids": formulas_by_line[key], "reference_ids": refs_by_line[key],
            "formal_object_ids_starting_here": formals_by_line[key],
            "correction_ids": corrections_by_line[key],
            "status": "PASS_EXACT_SOURCE_LINE_AND_ANCHOR_REPLAY" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-LINE-002", "source_line_replay",
            "A source-line replay or its stable anchors differ from source/oracle truth.",
            {"index": index, "expected": reviews[-1], "candidate": row},
            "Regenerate the exact source-line and anchor crosswalk.",
        )
    receipt = {
        "schema": "openlogic-tr023-independent-source-line-replay-audit-v1",
        "source_line_rows": len(lines),
        "formula_anchors": sum(len(row["formula_ids"]) for row in reviews),
        "reference_anchors": sum(len(row["reference_ids"]) for row in reviews),
        "formal_start_anchors": sum(len(row["formal_object_ids_starting_here"]) for row in reviews),
        "correction_line_anchors": sum(len(row["correction_ids"]) for row in reviews),
        "status": "PASS" if len(reviews) == EXPECTED["source_lines"] and all(row["status"].startswith("PASS") for row in reviews) else "FAIL",
    }
    return reviews, receipt


def formal_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    formals = data["formals"]
    oracle_by_id = {row["environment_id"]: row for row in data["oracle_formals"]}
    occurrence_by_id = {row["formula_id"]: row for row in data["occurrences"]}
    reference_by_id = {row["reference_id"]: row for row in data["references"]}
    ids = [row["formal_object_id"] for row in formals]
    audit.check(
        len(formals) == EXPECTED["formals"] and len(ids) == len(set(ids)) and set(ids) == set(oracle_by_id),
        "TR023-INDEPENDENT-FORMAL-001", "formal_closure",
        "Formal-object IDs do not exactly close over the oracle.",
        {"candidate": len(formals), "unique": len(set(ids)), "oracle": len(oracle_by_id)},
        "Regenerate the complete formal-object authority.",
    )
    formals_reviews = []
    derivation_reviews = []
    for row in formals:
        fid = row["formal_object_id"]
        oracle = oracle_by_id.get(fid, {})
        exact_oracle = all(row.get(key) == oracle.get(key) for key in (
            "environment_id", "file", "line", "column", "offset", "content_start",
            "content_end", "stream_start", "stream_end", "instance_id", "name", "object_class",
            "chapter_key", "part_key", "scope",
        ))
        source_path = data["source_root"] / row["file"]
        source_text = source_path.read_text(encoding="utf-8")
        source_raw_text = source_path.read_bytes().decode("utf-8-sig")
        source_binding = row["source_binding"]
        source_block = source_binding["source_block"]
        source_block_raw = source_block.replace("\n", "\r\n") if "\r\n" in source_raw_text else source_block
        leading_source_spaces = len(source_block) - len(source_block.lstrip(" "))
        block_start = row["offset"] - leading_source_spaces
        block_end = block_start + len(source_block_raw)
        source_exact = (
            source_raw_text[block_start:block_end].replace("\r\n", "\n") == source_block
            and source_binding["source_block_sha256"] == sha256_bytes(source_block.encode("utf-8"))
            and source_binding["source_block_utf8_bytes"] == len(source_block.encode("utf-8"))
            and source_binding["source_file_sha256"] == sha256_file(source_path)
        )
        expected_formula_ids = [
            item["formula_id"] for item in data["oracle_occurrences"]
            if item["stream_start"] < row["content_end"] and item["stream_end"] > row["content_start"]
        ]
        expected_ref_ids = [
            item["reference_id"] for item in data["oracle_refs"]
            if item["file"] == row["file"]
            and item["offset"] >= block_start
            and item["offset"] < block_end
        ]
        expected_expression_ids = list(dict.fromkeys(occurrence_by_id[item]["expression_id"] for item in expected_formula_ids))
        bindings_exact = (
            row["formula_ids"] == expected_formula_ids
            and row["reference_ids"] == expected_ref_ids
            and row["expression_ids"] == expected_expression_ids
        )
        listener_fields_ok = all(listener_ok(row.get(key, "")) for key in ("accessible_name", "long_description", "listen_text"))
        all_bound_spoken = all(occurrence_by_id[item]["speech"] in row["listen_text"] for item in row["formula_ids"])
        all_refs_spoken = all(reference_by_id[item]["accessible_name"] in row["listen_text"] for item in row["reference_ids"])
        sensitive = SENSITIVE_FORMAL_EXPECTATIONS.get(fid, [])
        sensitive_ok = all(token.lower() in (row["long_description"] + " " + row["listen_text"]).lower() for token in sensitive)
        exercise_ok = (
            (fid in EXERCISE_IDS and row["object_role"] == "exercise" and row["exercise_solution_status"] == "PRESERVED_UNSOLVED")
            or (fid not in EXERCISE_IDS and row["object_role"] != "exercise" and row["exercise_solution_status"] is None)
        )
        row_ok = (
            exact_oracle and source_exact and bindings_exact and record_hash_ok(row)
            and listener_fields_ok and all_bound_spoken and all_refs_spoken and sensitive_ok and exercise_ok
        )
        formals_reviews.append({
            "formal_object_id": fid, "object_role": row["object_role"],
            "file": row["file"], "line": row["line"],
            "formula_count": len(row["formula_ids"]), "reference_count": len(row["reference_ids"]),
            "source_block_sha256": source_binding["source_block_sha256"],
            "oracle_boundary_exact": exact_oracle, "source_block_exact": source_exact,
            "formula_reference_boundaries_exact": bindings_exact,
            "sensitive_manual_expectations": sensitive,
            "status": "PASS_INDEPENDENT_FORMAL_BOUNDARY_AND_LISTENER_REVIEW" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-FORMAL-002", "formal_semantics_grouping",
            "A formal object failed independent source-boundary, grouping, or listener review.",
            {"formal_object_id": fid, "review": formals_reviews[-1]},
            "Correct the formal at its exact source boundary and regenerate dependent artifacts.",
        )

        if row["object_role"] == "derivation":
            expected_groups = DERIVATION_GROUPS.get(fid, [])
            actual_groups = [item["formula_ids"] for item in row.get("derivation_lines") or []]
            line_numbers = [item["printed_line_number"] for item in row.get("derivation_lines") or []]
            derivation_ok = actual_groups == expected_groups and line_numbers == list(range(1, len(expected_groups) + 1))
            exact_rows_ok = True
            justification_ok = True
            for line in row.get("derivation_lines") or []:
                actual_source_lines = source_text.splitlines()
                exact_rows_ok = exact_rows_ok and all(
                    actual_source_lines[item["line"] - 1] == item["text"] for item in line["exact_source_rows"]
                )
                justification_ok = justification_ok and listener_ok(line["justification"]) and listener_ok(line["listen_text"])
                for formula_id, speech in zip(line["formula_ids"], line["formula_speeches"]):
                    justification_ok = justification_ok and occurrence_by_id[formula_id]["speech"] == speech
            derivation_ok = derivation_ok and exact_rows_ok and justification_ok
            derivation_reviews.append({
                "formal_object_id": fid,
                "expected_formula_groups_by_printed_line": expected_groups,
                "actual_formula_groups_by_printed_line": actual_groups,
                "printed_lines": len(actual_groups),
                "source_rows_exact": exact_rows_ok,
                "justifications_and_formula_speeches_exact": justification_ok,
                "status": "PASS_INDEPENDENT_DERIVATION_LINE_AND_GROUPING_REVIEW" if derivation_ok else "FAIL",
            })
            audit.check(
                derivation_ok, "TR023-INDEPENDENT-DERIVATION-001", "derivation_grouping",
                "A derivation's printed-line grouping, source rows, formula speech, or justification is wrong.",
                {"formal_object_id": fid, "review": derivation_reviews[-1]},
                "Repair the exact derivation line grouping and re-audit all formal boundaries.",
            )

    class_counts = Counter(row["object_role"] for row in formals)
    printed_lines = sum(len(row.get("derivation_lines") or []) for row in formals)
    totals_ok = (
        len(derivation_reviews) == EXPECTED["derivations"]
        and printed_lines == EXPECTED["derivation_printed_lines"]
        and {row["formal_object_id"] for row in formals if row["object_role"] == "exercise"} == EXERCISE_IDS
        and sum(row["exercise_solution_status"] == "PRESERVED_UNSOLVED" for row in formals) == EXPECTED["exercises"]
    )
    audit.check(
        totals_ok, "TR023-INDEPENDENT-FORMAL-003", "formal_totals",
        "Derivation/exercise closure is not exact.",
        {"derivations": len(derivation_reviews), "printed_lines": printed_lines, "class_counts": dict(class_counts)},
        "Restore all formal objects, printed derivation lines, and unsolved exercises.",
    )
    receipt = {
        "schema": "openlogic-tr023-independent-formal-audit-v1",
        "formal_objects": len(formals), "formal_classes": dict(sorted(class_counts.items())),
        "derivations": len(derivation_reviews), "derivation_printed_lines": printed_lines,
        "unsolved_exercises": sum(row["exercise_solution_status"] == "PRESERVED_UNSOLVED" for row in formals),
        "status": "PASS" if totals_ok and all(row["status"].startswith("PASS") for row in formals_reviews + derivation_reviews) else "FAIL",
    }
    return formals_reviews, derivation_reviews, receipt


def reference_correction_audit(
    audit: Audit, data: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    references = data["references"]
    oracle_by_id = {row["reference_id"]: row for row in data["oracle_refs"]}
    source_records = {row["path"]: row for row in data["authority"]["source_records"]}
    ids = [row["reference_id"] for row in references]
    audit.check(
        len(references) == EXPECTED["references"] and len(ids) == len(set(ids)) and set(ids) == set(oracle_by_id),
        "TR023-INDEPENDENT-REFERENCE-001", "reference_closure",
        "Reference IDs do not exactly close over the oracle.",
        {"candidate": len(references), "unique": len(set(ids)), "oracle": len(oracle_by_id)},
        "Regenerate the exact reference ledger.",
    )
    ref_reviews = []
    for index, row in enumerate(references, 1):
        reference_id = row["reference_id"]
        oracle = oracle_by_id.get(reference_id, {})
        source_path = data["source_root"] / row["source"]["file"]
        source_text = source_path.read_text(encoding="utf-8")
        source_raw_text = source_path.read_bytes().decode("utf-8-sig")
        source_lines = source_text.splitlines()
        call = row["source_call"]
        source_exact = (
            row["source"] == oracle
            and source_raw_text[oracle.get("offset", 0):oracle.get("offset", 0) + len(call)] == call
            and row["source_call_sha256"] == sha256_bytes(call.encode("utf-8"))
            and row["source_line_text"] == source_lines[oracle.get("line", 1) - 1]
            and row["source_line_sha256"] == sha256_bytes(row["source_line_text"].encode("utf-8"))
            and row["source_file_sha256"] == source_records[row["source"]["file"]]["sha256"]
            and row["source_order_index"] == index
        )
        target = row["source_resolved_target"]["label_definition"]
        target_exact = (
            row["source_resolved_target"]["full_key"] == oracle.get("full_key")
            and target["file"] == oracle.get("target_file")
            and target["instance_id"] == oracle.get("target_instance_id")
            and row["target_replay_status"].startswith("PASS")
        )
        correction_ids = row["source_correction_ids"]
        correction_ok = (
            (reference_id == "reference-000398" and correction_ids == ["TR023-SOURCE-REFERENCE-003"]
             and row["listener_target_full_key"] == "fol:axd:prp:ax:land2"
             and row["reader_corrected_target"]["full_key"] == "fol:axd:prp:ax:land2")
            or (reference_id != "reference-000398" and correction_ids == [] and row["reader_corrected_target"] is None)
        )
        row_ok = (
            source_exact and target_exact and correction_ok and record_hash_ok(row)
            and listener_ok(row["accessible_name"]) and listener_ok(row["listen_text"])
        )
        ref_reviews.append({
            "reference_id": reference_id, "file": oracle.get("file"), "line": oracle.get("line"),
            "source_call_sha256": row.get("source_call_sha256"),
            "source_target_full_key": row.get("source_resolved_target", {}).get("full_key"),
            "listener_target_full_key": row.get("listener_target_full_key"),
            "source_correction_ids": correction_ids,
            "status": "PASS_INDEPENDENT_REFERENCE_SOURCE_AND_TARGET_REPLAY" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-REFERENCE-002", "reference_replay",
            "A reference failed exact source-call, target, correction, or listener replay.",
            {"reference_id": reference_id, "review": ref_reviews[-1]},
            "Repair the exact reference binding and regenerate dependent artifacts.",
        )

    corrections = data["corrections"]
    correction_by_id = {row["correction_id"]: row for row in corrections}
    exact_correction_ids = set(correction_by_id) == set(CORRECTION_EXPECTATIONS) and len(corrections) == EXPECTED["corrections"]
    audit.check(
        exact_correction_ids, "TR023-INDEPENDENT-CORRECTION-001", "correction_closure",
        "Source-correction IDs are not the exact independently reviewed set.",
        {"actual": sorted(correction_by_id), "expected": sorted(CORRECTION_EXPECTATIONS)},
        "Restore the five disclosed corrections without editing frozen source.",
    )
    occurrence_by_id = {row["formula_id"]: row for row in data["occurrences"]}
    correction_reviews = []
    for correction_id, expected in CORRECTION_EXPECTATIONS.items():
        row = correction_by_id.get(correction_id, {})
        source_path = data["source_root"] / expected["file"]
        source_lines = source_path.read_text(encoding="utf-8").splitlines()
        exact_lines = {str(line): source_lines[line - 1] for line in expected["lines"]}
        actual_lines = {str(key): value for key, value in row.get("exact_source_lines", {}).items()}
        formula_bindings_ok = all(
            occurrence_by_id[formula_id]["source_correction_ids"] == [correction_id]
            and occurrence_by_id[formula_id]["reader_correction"] == row.get("reader_disclosure")
            for formula_id in expected["formulas"]
        )
        row_ok = (
            row.get("file") == expected["file"] and row.get("lines") == expected["lines"]
            and row.get("affected_formula_ids") == expected["formulas"] and row.get("kind") == expected["kind"]
            and actual_lines == exact_lines and row.get("source_file_sha256") == sha256_file(source_path)
            and row.get("source_bytes_status") == "IMMUTABLE_AND_UNCHANGED"
            and row.get("authority_status") == "IMMUTABLE_SOURCE_PRESERVED_DERIVED_READER_CORRECTION_DISCLOSED"
            and listener_ok(row.get("reader_disclosure", "")) and listener_ok(row.get("reader_reading", ""))
            and listener_ok(row.get("source_reading", "")) and formula_bindings_ok and record_hash_ok(row)
        )
        correction_reviews.append({
            "correction_id": correction_id, "file": expected["file"], "lines": expected["lines"],
            "kind": expected["kind"], "affected_formula_ids": expected["formulas"],
            "exact_source_lines_replayed": actual_lines == exact_lines,
            "formula_bindings_exact": formula_bindings_ok,
            "status": "PASS_INDEPENDENT_CORRECTION_AND_DISCLOSURE_REVIEW" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-CORRECTION-002", "source_correction",
            "A disclosed source correction failed exact coordinate, binding, or immutable-source review.",
            {"correction_id": correction_id, "review": correction_reviews[-1]},
            "Repair the derived reader correction while preserving source bytes.",
        )
    receipt = {
        "schema": "openlogic-tr023-independent-reference-correction-audit-v1",
        "references": len(references), "resolved_references": sum(row["source"]["status"] == "resolved" for row in references),
        "source_corrections": len(corrections),
        "corrected_reference_id": "reference-000398",
        "status": "PASS" if exact_correction_ids and all(row["status"].startswith("PASS") for row in ref_reviews + correction_reviews) else "FAIL",
    }
    return ref_reviews, correction_reviews, receipt


def listen_audit(audit: Audit, data: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    streams = data["streams"]
    source_records = data["authority"]["source_records"]
    occurrence_by_id = {row["formula_id"]: row for row in data["occurrences"]}
    reference_by_id = {row["reference_id"]: row for row in data["references"]}
    disclosure_by_id = {row["correction_id"]: row for row in data["disclosures"]}
    all_formula_ids: list[str] = []
    all_reference_ids: list[str] = []
    all_disclosure_ids: list[str] = []
    reviews = []
    for ordinal, record in enumerate(source_records, 1):
        row = streams[ordinal - 1] if ordinal - 1 < len(streams) else {}
        words = row.get("listen_text", "").split()
        bindings = (
            [(item["word_start"], item["word_end"], "formula", item) for item in row.get("ordered_formula_bindings", [])]
            + [(item["word_start"], item["word_end"], "reference", item) for item in row.get("ordered_reference_bindings", [])]
            + [(item["word_start"], item["word_end"], "disclosure", item) for item in row.get("ordered_disclosure_bindings", [])]
        )
        span_exact = all(" ".join(words[start:end]) == item["speech"] for start, end, _, item in bindings)
        ordered = [item[0] for item in sorted(bindings)] == sorted(item[0] for item in bindings)
        in_bounds = all(0 <= start < end <= len(words) for start, end, _, _ in bindings)
        formula_exact = all(
            item["formula_id"] in occurrence_by_id
            and item["expression_id"] == occurrence_by_id[item["formula_id"]]["expression_id"]
            and item["file"] == occurrence_by_id[item["formula_id"]]["file"]
            and item["line"] == occurrence_by_id[item["formula_id"]]["line"]
            and occurrence_by_id[item["formula_id"]]["speech"] in item["speech"]
            for item in row.get("ordered_formula_bindings", [])
        )
        reference_exact = all(
            item["reference_id"] in reference_by_id
            and item["target_full_key"] == reference_by_id[item["reference_id"]]["listener_target_full_key"]
            and reference_by_id[item["reference_id"]]["accessible_name"] in item["speech"]
            for item in row.get("ordered_reference_bindings", [])
        )
        disclosure_exact = all(
            item["correction_id"] in disclosure_by_id
            and disclosure_by_id[item["correction_id"]].get("source_replay_id") == row.get("source_replay_id")
            and all(disclosure_by_id[item["correction_id"]].get(key) == value for key, value in item.items())
            for item in row.get("ordered_disclosure_bindings", [])
        )
        row_ok = (
            row.get("source_ordinal") == ordinal and row.get("file") == record["path"]
            and row.get("source_sha256") == record["sha256"] and row.get("source_lines") == record["lines"]
            and row.get("word_count") == len(words) and listener_ok(row.get("listen_text", ""))
            and not EXTERNAL_OR_SCRIPT.search(row.get("listen_text", ""))
            and row.get("formula_count") == len(row.get("ordered_formula_bindings", []))
            and row.get("reference_count") == len(row.get("ordered_reference_bindings", []))
            and row.get("disclosure_count") == len(row.get("ordered_disclosure_bindings", []))
            and span_exact and ordered and in_bounds and formula_exact and reference_exact and disclosure_exact
            and record_hash_ok(row)
        )
        all_formula_ids.extend(item["formula_id"] for item in row.get("ordered_formula_bindings", []))
        all_reference_ids.extend(item["reference_id"] for item in row.get("ordered_reference_bindings", []))
        all_disclosure_ids.extend(item["correction_id"] for item in row.get("ordered_disclosure_bindings", []))
        reviews.append({
            "source_replay_id": row.get("source_replay_id"), "source_ordinal": ordinal,
            "file": record["path"], "word_count": len(words),
            "formula_bindings": len(row.get("ordered_formula_bindings", [])),
            "reference_bindings": len(row.get("ordered_reference_bindings", [])),
            "correction_disclosures": len(row.get("ordered_disclosure_bindings", [])),
            "all_word_spans_exact": span_exact, "listener_residue_absent": listener_ok(row.get("listen_text", "")),
            "status": "PASS_INDEPENDENT_SOURCE_ORDER_WORDS_ONLY_REVIEW" if row_ok else "FAIL",
        })
        audit.check(
            row_ok, "TR023-INDEPENDENT-LISTEN-001", "continuous_listen",
            "A continuous Listen stream failed source order, binding, residue, or record review.",
            {"source_ordinal": ordinal, "review": reviews[-1]},
            "Repair the source-order words-only stream and regenerate all binding spans.",
        )
    closure_ok = (
        len(streams) == EXPECTED["listen_streams"]
        and all_formula_ids == [row["formula_id"] for row in data["occurrences"]]
        and all_reference_ids == [row["reference_id"] for row in data["references"]]
        and set(all_disclosure_ids) == set(CORRECTION_EXPECTATIONS) and len(all_disclosure_ids) == EXPECTED["corrections"]
    )
    audit.check(
        closure_ok, "TR023-INDEPENDENT-LISTEN-002", "continuous_listen_closure",
        "Continuous Listen formula/reference/correction closure is not exact.",
        {"streams": len(streams), "formulas": len(all_formula_ids), "references": len(all_reference_ids), "disclosures": len(all_disclosure_ids)},
        "Restore every stable anchor exactly once in source order.",
    )
    receipt = {
        "schema": "openlogic-tr023-independent-continuous-listen-audit-v1",
        "streams": len(streams), "formula_bindings": len(all_formula_ids),
        "reference_bindings": len(all_reference_ids), "correction_disclosures": len(all_disclosure_ids),
        "raw_tex_opaque_symbol_script_and_external_url_residue": 0 if all(row["listener_residue_absent"] for row in reviews) else None,
        "status": "PASS" if closure_ok and all(row["status"].startswith("PASS") for row in reviews) else "FAIL",
    }
    return reviews, receipt


def manual_sensitive_audit(audit: Audit, data: Mapping[str, Any]) -> dict[str, Any]:
    expressions = {row["expression_id"]: row for row in data["expressions"]}
    occurrences = {row["formula_id"]: row for row in data["occurrences"]}
    formals = {row["formal_object_id"]: row for row in data["formals"]}
    checks = [
        ("current_step_range", "positions one through n" in expressions["expr-d826a37801d792cd"]["meaning"].lower()),
        ("fourteen_schemes_complete", all(token in expressions["expr-767e19047750a558"]["speech"].lower() for token in (
            "conjunction elimination left", "conjunction elimination right", "conjunction introduction",
            "disjunction introduction left", "disjunction introduction right", "disjunction elimination",
            "conditional scheme one", "conditional scheme two", "negation scheme one", "negation scheme two",
            "truth scheme", "falsity scheme one", "falsity scheme two", "double negation elimination"))),
        ("quantifier_schemes_complete", all(token in expressions["expr-f2a1e865d57e76b4"]["speech"].lower() for token in (
            "quantifier axiom one", "quantifier axiom two", "for every variable x", "for some variable x"))),
        ("identity_schemes_complete", all(token in expressions["expr-abc48be8a2aa47e8"]["speech"].lower() for token in (
            "identity axiom one", "identity axiom two", "identical"))),
        ("eight_row_quantified_display", all(f"formula row {word}" in expressions["expr-819d3dedca8759b5"]["speech"].lower() for word in (
            "one", "two", "three", "four", "five", "six", "seven", "eight"))),
        ("seven_row_deduction_display", all(f"formula row {word}" in expressions["expr-64b2bf09dbc7530b"]["speech"].lower() for word in (
            "one", "two", "three", "four", "five", "six", "seven"))),
        ("missing_subject_supplied", occurrences["projected-formula-0010985"]["speech"] == "B belongs to Gamma union the set containing A"),
        ("missing_parenthesis_disclosed", occurrences["projected-formula-0011008"]["source_correction_ids"] == ["TR023-SOURCE-FORMULA-002"]),
        ("quantified_parenthesis_disclosed", occurrences["projected-formula-0011028"]["source_correction_ids"] == ["TR023-SOURCE-FORMULA-005"]),
        ("derivation_definition_three_cases", all(token in formals["projected-env-001721"]["long_description"].lower() for token in ("premise", "axiom", "inference rule"))),
        ("quantifier_rule_eigenvariable_scope", all(token in formals["projected-env-001734"]["long_description"].lower() for token in ("gamma", "unaffected side formula", "eigenvariable"))),
        ("all_derivation_manual_groups", all(
            [item["formula_ids"] for item in formals[fid]["derivation_lines"]] == groups
            for fid, groups in DERIVATION_GROUPS.items()
        )),
    ]
    repair = read_json(PROJECTION / "producer_validation" / "PRODUCER_REPAIR_HISTORY.json")
    repair_ok = (
        repair.get("finding", {}).get("id") == "TR023-PRODUCER-MATHML-NONFLATTENING-001"
        and repair.get("finding", {}).get("affected_occurrence_count") == EXPECTED["occurrences"]
        and repair.get("finding", {}).get("source_content_changed") is False
        and repair.get("finding", {}).get("semantic_expression_content_changed") is False
        and repair.get("finding", {}).get("formal_or_reference_content_changed") is False
        and repair.get("changed_pins", [])[0].get("after") == "8db9f69715b59e82a8439977f472533407eac808e7c89e9cce3023f2b53546c2"
    )
    checks.append(("documented_root_aria_repair_chain", repair_ok))
    rows = [{"check": name, "status": "PASS" if good else "FAIL"} for name, good in checks]
    audit.check(
        all(good for _, good in checks), "TR023-INDEPENDENT-MANUAL-001", "manual_semantic_review",
        "A hand-selected high-risk semantic, scope, grouping, correction, or repair-history check failed.",
        {"checks": rows}, "Repair the exact high-risk binding before independent acceptance.",
    )
    return {
        "schema": "openlogic-tr023-independent-manual-sensitive-review-v1",
        "review_basis": "Independent source reading of the derivation definition, 14 propositional schemes, two quantifier schemes/rules, quantified displays, identity schemes, five derivations, and five correction coordinates.",
        "checks": rows,
        "status": "PASS" if all(good for _, good in checks) else "FAIL",
    }


class MutantSurvived(RuntimeError):
    pass


def reject_if(condition: bool, message: str) -> None:
    if condition:
        raise ValueError(message)


def guard_unique(rows: list[dict[str, Any]], field: str) -> None:
    reject_if(len({row[field] for row in rows}) != len(rows), f"duplicate {field}")


def guard_listener(value: str) -> None:
    reject_if(not listener_ok(value), "listener residue")


def guard_mathml(value: str, expr: str, formula: str | None, display: str, tex: str) -> None:
    ok, review = inspect_mathml(value, expr, formula, display, tex)
    reject_if(not ok, ";".join(review["problems"]))


def guard_semantics(row: dict[str, Any]) -> None:
    reject_if(any(item["status"] == "FAIL" for item in semantic_obligations(row["normalized_tex"], row["speech"])), "semantic operator omitted")


def guard_record(row: dict[str, Any]) -> None:
    reject_if(not record_hash_ok(row), "record hash drift")


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
    tests: list[dict[str, Any]] = []
    first_expr = copy.deepcopy(data["expressions"][0])
    neg_expr = copy.deepcopy(next(row for row in data["expressions"] if r"\lnot" in row["normalized_tex"]))
    first_occ = copy.deepcopy(data["occurrences"][0])
    derivation = copy.deepcopy(next(row for row in data["formals"] if row["formal_object_id"] == "projected-env-001735"))
    exercise = copy.deepcopy(next(row for row in data["formals"] if row["formal_object_id"] in EXERCISE_IDS))
    corrected_ref = copy.deepcopy(next(row for row in data["references"] if row["reference_id"] == "reference-000398"))

    exprs = copy.deepcopy(data["expressions"][:2]); exprs[1]["expression_id"] = exprs[0]["expression_id"]
    tests.append(expect_rejected("duplicate_expression_id", "duplicate an expression ID", exprs, lambda rows: guard_unique(rows, "expression_id")))
    first_expr["speech"] += r" \lnot"
    tests.append(expect_rejected("raw_tex_speech", "append raw TeX to expression speech", first_expr["speech"], guard_listener))
    neg_expr["speech"] = "formula A"
    tests.append(expect_rejected("drop_negation", "drop spoken negation", neg_expr, guard_semantics))
    stale = copy.deepcopy(data["expressions"][0]); stale["meaning"] += " changed"
    tests.append(expect_rejected("stale_expression_hash", "change expression without rehashing", stale, guard_record))

    root = ET.fromstring(first_occ["mathml"]); root.set("aria-label", "flattened")
    tests.append(expect_rejected("root_aria_label", "add occurrence root aria-label", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["expression_id"], first_occ["formula_id"], "inline", first_occ["normalized_tex"])))
    root = ET.fromstring(first_occ["mathml"]); root.set("role", "img")
    tests.append(expect_rejected("root_role", "add occurrence root role", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["expression_id"], first_occ["formula_id"], "inline", first_occ["normalized_tex"])))
    root = ET.fromstring(first_occ["mathml"]); root.set("class", "flattened")
    tests.append(expect_rejected("root_class", "add occurrence root class", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["expression_id"], first_occ["formula_id"], "inline", first_occ["normalized_tex"])))
    root = ET.fromstring(first_occ["mathml"]); [root.remove(child) for child in list(root)]; root.text = first_occ["speech"]
    tests.append(expect_rejected("flatten_mathml", "replace native MathML with root text", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["expression_id"], first_occ["formula_id"], "inline", first_occ["normalized_tex"])))
    root = ET.fromstring(first_occ["mathml"]); root.set("data-formula-id", "projected-formula-mutated")
    tests.append(expect_rejected("formula_id_drift", "alter MathML formula ID", ET.tostring(root, encoding="unicode"), lambda value: guard_mathml(value, first_occ["expression_id"], first_occ["formula_id"], "inline", first_occ["normalized_tex"])))
    occs = copy.deepcopy(data["occurrences"][:2]); occs[1]["formula_id"] = occs[0]["formula_id"]
    tests.append(expect_rejected("duplicate_formula_id", "duplicate stable formula ID", occs, lambda rows: guard_unique(rows, "formula_id")))

    mutated_derivation = copy.deepcopy(derivation); mutated_derivation["derivation_lines"][1]["formula_ids"] = mutated_derivation["derivation_lines"][1]["formula_ids"][:1]
    tests.append(expect_rejected("split_derivation_line", "drop second segment from printed derivation line two", mutated_derivation, lambda row: reject_if([item["formula_ids"] for item in row["derivation_lines"]] != DERIVATION_GROUPS[row["formal_object_id"]], "derivation grouping drift")))
    mutated_derivation = copy.deepcopy(derivation); mutated_derivation["derivation_lines"].pop()
    tests.append(expect_rejected("drop_derivation_line", "drop a printed derivation line", mutated_derivation, lambda row: reject_if(len(row["derivation_lines"]) != len(DERIVATION_GROUPS[row["formal_object_id"]]), "derivation line closure")))
    exercise["exercise_solution_status"] = "SOLVED"
    tests.append(expect_rejected("solve_exercise", "mark source exercise solved", exercise, lambda row: reject_if(row["exercise_solution_status"] != "PRESERVED_UNSOLVED", "exercise solution drift")))
    formals = copy.deepcopy(data["formals"][:2]); formals[1]["formal_object_id"] = formals[0]["formal_object_id"]
    tests.append(expect_rejected("duplicate_formal_id", "duplicate formal object ID", formals, lambda rows: guard_unique(rows, "formal_object_id")))
    formal = copy.deepcopy(data["formals"][0]); formal["formula_ids"].pop()
    original_formal_ids = data["formals"][0]["formula_ids"]
    tests.append(expect_rejected("drop_formal_formula", "drop formula from formal boundary", formal, lambda row: reject_if(row["formula_ids"] != original_formal_ids, "formal formula boundary drift")))

    refs = copy.deepcopy(data["references"][:2]); refs[1]["reference_id"] = refs[0]["reference_id"]
    tests.append(expect_rejected("duplicate_reference_id", "duplicate reference ID", refs, lambda rows: guard_unique(rows, "reference_id")))
    corrected_ref["listener_target_full_key"] = corrected_ref["source_resolved_target"]["full_key"]
    tests.append(expect_rejected("lose_reference_correction", "retarget corrected reference back to duplicated source target", corrected_ref, lambda row: reject_if(row["listener_target_full_key"] != "fol:axd:prp:ax:land2", "corrected reference target drift")))
    stale_ref = copy.deepcopy(data["references"][0]); stale_ref["accessible_name"] += " changed"
    tests.append(expect_rejected("stale_reference_hash", "change reference without rehashing", stale_ref, guard_record))

    corrections = copy.deepcopy(data["corrections"]); corrections.pop()
    tests.append(expect_rejected("drop_correction", "drop one disclosed source correction", corrections, lambda rows: reject_if({row["correction_id"] for row in rows} != set(CORRECTION_EXPECTATIONS), "correction closure drift")))
    correction = copy.deepcopy(next(row for row in data["corrections"] if row["correction_id"] == "TR023-SOURCE-FORMULA-001")); correction["affected_formula_ids"] = []
    tests.append(expect_rejected("unbind_formula_correction", "remove affected formula from correction", correction, lambda row: reject_if(row["affected_formula_ids"] != ["projected-formula-0010985"], "correction binding drift")))

    source_line = copy.deepcopy(data["source_lines"][0]); original_line = source_line["source_text"]; source_line["source_text"] += " changed"
    tests.append(expect_rejected("alter_source_line", "alter exact source-line replay", source_line, lambda row: reject_if(row["source_text"] != original_line, "source line drift")))
    stream = copy.deepcopy(next(row for row in data["streams"] if row["formula_count"])); stream["listen_text"] += " →"
    tests.append(expect_rejected("listener_symbol_residue", "append opaque arrow to continuous listener", stream["listen_text"], guard_listener))
    stream = copy.deepcopy(next(row for row in data["streams"] if row["formula_count"])); stream["ordered_formula_bindings"][0]["word_end"] += 1
    tests.append(expect_rejected("shift_listener_span", "shift formula word span", stream, lambda row: reject_if(" ".join(row["listen_text"].split()[row["ordered_formula_bindings"][0]["word_start"]:row["ordered_formula_bindings"][0]["word_end"]]) != row["ordered_formula_bindings"][0]["speech"], "listener span drift")))
    disclosures = copy.deepcopy(data["disclosures"]); disclosures.pop()
    tests.append(expect_rejected("drop_disclosure", "drop one listener correction disclosure", disclosures, lambda rows: reject_if({row["correction_id"] for row in rows} != set(CORRECTION_EXPECTATIONS), "listener disclosure closure")))
    artifact = copy.deepcopy(read_json(PROJECTION / "ARTIFACT_MANIFEST.json")); artifact["artifacts"][0]["sha256"] = "0" * 64
    tests.append(expect_rejected("artifact_digest", "replace producer artifact digest", artifact, lambda value: reject_if(value["artifacts"][0]["sha256"] != sha256_file(PROJECTION / value["artifacts"][0]["path"]), "artifact manifest drift")))
    repair = copy.deepcopy(read_json(PROJECTION / "producer_validation" / "PRODUCER_REPAIR_HISTORY.json")); repair["finding"]["affected_occurrence_count"] -= 1
    tests.append(expect_rejected("repair_history_count", "alter documented root-ARIA repair coverage", repair, lambda value: reject_if(value["finding"]["affected_occurrence_count"] != EXPECTED["occurrences"], "repair coverage drift")))

    audit.check(
        len(tests) >= 24 and all(row["status"] == "PASS_FRESH_MUTANT_REJECTED" for row in tests),
        "TR023-INDEPENDENT-ADVERSARIAL-001", "adversarial_guards",
        "One or more fresh independent adversarial mutants survived.",
        {"test_count": len(tests)}, "Strengthen the independent guard and repeat the audit.",
    )
    return {
        "schema": "openlogic-tr023-independent-adversarial-audit-v1",
        "fresh_mutant_count": len(tests), "tests": tests,
        "status": "PASS_ALL_FRESH_MUTANTS_REJECTED",
    }


def accessibility_offline_audit(audit: Audit, data: Mapping[str, Any]) -> dict[str, Any]:
    evidence_files = [path for path in PROJECTION.rglob("*") if path.is_file()]
    executable_assets = [path.relative_to(PROJECTION).as_posix() for path in evidence_files if path.suffix.lower() in {".js", ".mjs", ".exe", ".dll"}]
    script_or_external = []
    for path in evidence_files:
        if path.suffix.lower() not in {".json", ".jsonl", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        if EXTERNAL_OR_SCRIPT.search(text):
            script_or_external.append(path.relative_to(PROJECTION).as_posix())
    native_structure = all(row.get("accessible_name") and row.get("long_description") and row.get("listen_text") for row in data["formals"])
    stable_crosslinks = (
        len({row["formula_id"] for row in data["occurrences"]}) == EXPECTED["occurrences"]
        and len({row["formal_object_id"] for row in data["formals"]}) == EXPECTED["formals"]
        and len({row["reference_id"] for row in data["references"]}) == EXPECTED["references"]
    )
    summary = read_json(PROJECTION / "SUMMARY.json")
    provenance = (
        summary.get("authority_commit") == AUTHORITY_COMMIT
        and summary.get("chapter_title") == "First-Order Axiomatic Deduction"
        and read_json(PROJECTION / "UPSTREAM_INPUTS.json").get("source_authority_root") == str(data["source_root"]).replace("\\", "/")
    )
    good = not executable_assets and not script_or_external and native_structure and stable_crosslinks and provenance
    audit.check(
        good, "TR023-INDEPENDENT-ACCESS-001", "offline_accessibility_provenance",
        "Offline/no-script, accessibility-structure, stable-crosslink, or provenance gate failed.",
        {"executable_assets": executable_assets, "script_or_external": script_or_external,
         "native_structure": native_structure, "stable_crosslinks": stable_crosslinks, "provenance": provenance},
        "Remove runtime dependencies and restore explicit native/listener/provenance structure.",
    )
    return {
        "schema": "openlogic-tr023-independent-accessibility-offline-audit-v1",
        "executable_or_javascript_assets": executable_assets,
        "external_url_or_script_markup_files": script_or_external,
        "native_formal_accessible_names_descriptions_and_listeners": native_structure,
        "stable_formula_formal_reference_crosslinks": stable_crosslinks,
        "frozen_commit_chapter_and_source_provenance": provenance,
        "browser_gui_audio_or_assistive_technology_tested": False,
        "status": "PASS_STATIC_OFFLINE_ACCESSIBILITY_AND_PROVENANCE" if good else "FAIL",
    }


def core_manifest(output: Path) -> dict[str, Any]:
    files = tree_snapshot(output, exclude={"EVIDENCE_MANIFEST.json"})
    return {
        "schema": "openlogic-tr023-independent-core-evidence-manifest-v1",
        "tranche_id": "OLAB-TR-023", "files": files,
        "status": "PASS_MANIFEST_COMPLETE",
    }


def run_core(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    audit = Audit()
    before = protected_snapshot()
    write_json(output, "PROTECTED_SNAPSHOT_BEFORE.json", before)
    pin_receipt = pin_manifest_audit(audit)
    data = load_data()
    source_receipt, source_reviews = source_audit(audit, data)
    expression_reviews, expression_receipt = expression_audit(audit, data)
    occurrence_reviews, occurrence_receipt = occurrence_audit(audit, data)
    line_reviews, line_receipt = source_line_replay_audit(audit, data)
    formal_reviews, derivation_reviews, formal_receipt = formal_audit(audit, data)
    reference_reviews, correction_reviews, reference_receipt = reference_correction_audit(audit, data)
    listen_reviews, listen_receipt = listen_audit(audit, data)
    manual_receipt = manual_sensitive_audit(audit, data)
    adversarial_receipt = adversarial_audit(audit, data)
    accessibility_receipt = accessibility_offline_audit(audit, data)

    after = protected_snapshot()
    protected_ok = before == after
    audit.check(
        protected_ok, "TR023-INDEPENDENT-PROTECTED-001", "protected_inputs",
        "Protected source/oracle/producer inputs changed during the independent audit.",
        {"before": before["aggregate_sha256"], "after": after["aggregate_sha256"]},
        "Discard this run, restore protected inputs, and restart independently.",
    )
    caches = cache_residue()
    audit.check(
        not caches, "TR023-INDEPENDENT-CACHE-001", "cache_residue",
        "Python cache residue exists in the bounded audit/producer area.",
        {"paths": caches}, "Remove cache residue and repeat with bytecode disabled.",
    )

    write_json(output, "PIN_AND_MANIFEST_AUDIT.json", pin_receipt)
    write_json(output, "SOURCE_AUDIT_RECEIPT.json", source_receipt)
    write_jsonl(output, "SOURCE_FILE_REVIEW.jsonl", source_reviews)
    write_json(output, "EXPRESSION_MATHML_AUDIT_RECEIPT.json", expression_receipt)
    write_jsonl(output, "EXPRESSION_SEMANTIC_MATHML_REVIEW.jsonl", expression_reviews)
    write_json(output, "OCCURRENCE_AUDIT_RECEIPT.json", occurrence_receipt)
    write_jsonl(output, "OCCURRENCE_SEMANTIC_MATHML_REVIEW.jsonl", occurrence_reviews)
    write_json(output, "SOURCE_LINE_REPLAY_AUDIT_RECEIPT.json", line_receipt)
    write_jsonl(output, "SOURCE_LINE_REVIEW.jsonl", line_reviews)
    write_json(output, "FORMAL_AUDIT_RECEIPT.json", formal_receipt)
    write_jsonl(output, "FORMAL_OBJECT_REVIEW.jsonl", formal_reviews)
    write_jsonl(output, "DERIVATION_REVIEW.jsonl", derivation_reviews)
    write_json(output, "REFERENCE_CORRECTION_AUDIT_RECEIPT.json", reference_receipt)
    write_jsonl(output, "REFERENCE_REVIEW.jsonl", reference_reviews)
    write_jsonl(output, "SOURCE_CORRECTION_REVIEW.jsonl", correction_reviews)
    write_json(output, "CONTINUOUS_LISTEN_AUDIT_RECEIPT.json", listen_receipt)
    write_jsonl(output, "CONTINUOUS_LISTEN_REVIEW.jsonl", listen_reviews)
    write_json(output, "MANUAL_SENSITIVE_REVIEW.json", manual_receipt)
    write_json(output, "ADVERSARIAL_AUDIT.json", adversarial_receipt)
    write_json(output, "ACCESSIBILITY_OFFLINE_AUDIT.json", accessibility_receipt)
    write_json(output, "PROTECTED_SNAPSHOT_AFTER.json", after)
    write_json(output, "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", {
        "schema": "openlogic-tr023-independent-protected-cache-receipt-v1",
        "before_sha256": before["aggregate_sha256"], "after_sha256": after["aggregate_sha256"],
        "protected_inputs_byte_identical": protected_ok,
        "cache_residue": caches, "zero_cache_residue": not caches,
        "authorized_write_root": HERE.as_posix(),
        "durable_controls_written": False,
        "status": "PASS" if protected_ok and not caches else "FAIL",
    })

    audit.findings.sort(key=lambda row: (row["finding_id"], compact_json(row["evidence"])))
    write_jsonl(output, "FINDINGS.jsonl", audit.findings)
    counts = {
        "source_files": len(data["authority"]["source_records"]),
        "source_lines": len(data["source_lines"]),
        "source_bytes": sum(row["bytes"] for row in data["authority"]["source_records"]),
        "expressions": len(data["expressions"]),
        "primary_expression_mathml_roots": EXPECTED["primary_expression_mathml_roots"],
        "source_fidelity_mathml_roots": EXPECTED["source_fidelity_mathml_roots"],
        "occurrences": len(data["occurrences"]),
        "occurrence_mathml_roots": len(data["occurrences"]),
        "formals": len(data["formals"]),
        "derivations": len(derivation_reviews),
        "derivation_printed_lines": sum(row["printed_lines"] for row in derivation_reviews),
        "references": len(data["references"]),
        "exercises_unsolved": sum(row["exercise_solution_status"] == "PRESERVED_UNSOLVED" for row in data["formals"]),
        "corrections": len(data["corrections"]),
        "continuous_listen_streams": len(data["streams"]),
        "fresh_adversarial_mutants": adversarial_receipt["fresh_mutant_count"],
    }
    receipt = {
        "schema": "openlogic-tr023-independent-core-audit-receipt-v1",
        "tranche_id": "OLAB-TR-023", "program_sha256": sha256_file(Path(__file__)),
        "candidate_pins": {row["path"]: row["actual_sha256"] for row in pin_receipt["pins"]},
        "producer_tree_sha256": pin_receipt["producer_tree_sha256"],
        "counts": counts, "finding_count": len(audit.findings),
        "finding_ids": sorted({row["finding_id"] for row in audit.findings}),
        "independent_semantic_accessibility_source_replay_audit": "PASS" if not audit.findings else "FAIL",
        "browser_gui_audio_network_assistive_technology_nvda_git_publication_used": False,
        "reader_integration": "NOT_CLAIMED_PRODUCER_PROJECTION_ONLY",
        "status": "PASS_ZERO_CURRENT_FINDINGS" if not audit.findings else "FAIL_CURRENT_FINDINGS",
    }
    write_json(output, "CORE_AUDIT_RECEIPT.json", receipt)
    write_json(output, "EVIDENCE_MANIFEST.json", core_manifest(output))
    return receipt


def root_manifest() -> dict[str, Any]:
    files = tree_snapshot(HERE, exclude={"EVIDENCE_MANIFEST.json"})
    return {
        "schema": "openlogic-tr023-independent-final-evidence-manifest-v1",
        "tranche_id": "OLAB-TR-023", "files": files,
        "status": "PASS_MANIFEST_COMPLETE",
    }


def main() -> int:
    cold_root = HERE / "cold_independent_runs"
    run_a = cold_root / "run_a"
    run_b = cold_root / "run_b"
    safe_reset(cold_root)
    run_a_receipt = run_core(run_a)
    run_b_receipt = run_core(run_b)
    tree_a = tree_snapshot(run_a)
    tree_b = tree_snapshot(run_b)
    deterministic = tree_a == tree_b

    for name in (
        "PIN_AND_MANIFEST_AUDIT.json", "SOURCE_AUDIT_RECEIPT.json", "EXPRESSION_MATHML_AUDIT_RECEIPT.json",
        "OCCURRENCE_AUDIT_RECEIPT.json", "SOURCE_LINE_REPLAY_AUDIT_RECEIPT.json", "FORMAL_AUDIT_RECEIPT.json",
        "REFERENCE_CORRECTION_AUDIT_RECEIPT.json", "CONTINUOUS_LISTEN_AUDIT_RECEIPT.json",
        "MANUAL_SENSITIVE_REVIEW.json", "ADVERSARIAL_AUDIT.json", "ACCESSIBILITY_OFFLINE_AUDIT.json",
        "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", "FINDINGS.jsonl",
    ):
        shutil.copy2(run_a / name, HERE / name)

    determinism_receipt = {
        "schema": "openlogic-tr023-independent-cold-determinism-receipt-v1",
        "run_a_file_count": len(tree_a), "run_b_file_count": len(tree_b),
        "run_a_tree_sha256": value_sha256(tree_a), "run_b_tree_sha256": value_sha256(tree_b),
        "byte_identity_ledger": tree_a,
        "two_isolated_independent_audit_runs_byte_identical": deterministic,
        "run_a_status": run_a_receipt["status"], "run_b_status": run_b_receipt["status"],
        "status": "PASS_TWO_ISOLATED_AUDIT_RUNS_BYTE_IDENTICAL" if deterministic else "FAIL",
    }
    write_json(HERE, "COLD_INDEPENDENT_RUN_RECEIPT.json", determinism_receipt)
    final_findings = read_jsonl(HERE / "FINDINGS.jsonl")
    if not deterministic:
        final_findings.append({
            "finding_id": "TR023-INDEPENDENT-COLD-001", "severity": "P1", "category": "determinism",
            "message": "Two isolated independent audit runs were not byte-identical.",
            "evidence": {"run_a_tree": value_sha256(tree_a), "run_b_tree": value_sha256(tree_b)},
            "remediation": "Remove nondeterminism and repeat the independent audit.", "status": "OPEN",
        })
        write_jsonl(HERE, "FINDINGS.jsonl", final_findings)
    final = {
        "schema": "openlogic-tr023-independent-final-audit-receipt-v1",
        "tranche_id": "OLAB-TR-023", "program_sha256": sha256_file(Path(__file__)),
        "candidate_pins": run_a_receipt["candidate_pins"],
        "producer_tree_sha256": run_a_receipt["producer_tree_sha256"],
        "counts": run_a_receipt["counts"],
        "two_isolated_cold_independent_runs_byte_identical": deterministic,
        "finding_count": len(final_findings),
        "finding_ids": sorted({row["finding_id"] for row in final_findings}),
        "independent_semantic_accessibility_source_replay_audit": "PASS" if not final_findings else "FAIL",
        "root_aria_repair_independently_verified": not final_findings,
        "zero_mathml_root_aria_label_role_or_class": not final_findings,
        "native_parseable_unflattened_mathml_verified": not final_findings,
        "formal_and_derivation_boundaries_manually_reconciled": not final_findings,
        "source_order_continuous_listen_and_exact_line_replay_verified": not final_findings,
        "offline_no_javascript_and_stable_crosslinks_verified": not final_findings,
        "frozen_commit_source_and_chapter_provenance_verified": not final_findings,
        "protected_inputs_byte_identical": read_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json")["protected_inputs_byte_identical"],
        "zero_cache_residue": read_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json")["zero_cache_residue"],
        "assistive_technology_launched": False,
        "browser_gui_audio_network_nvda_git_publication_used": False,
        "reader_integration": "NOT_CLAIMED_PRODUCER_PROJECTION_ONLY",
        "status": "PASS_ZERO_CURRENT_FINDINGS" if not final_findings else "FAIL_CURRENT_FINDINGS",
    }
    write_json(HERE, "FINAL_AUDIT_RECEIPT.json", final)
    if final_findings:
        details = "\n".join(f"- {row['finding_id']}: {row['message']}" for row in final_findings)
        report = (
            "# TR-023 independent semantic/accessibility/source-replay audit\n\n"
            "Result: **FAIL — current findings remain.** No independent PASS is claimed.\n\n"
            f"{details}\n\nNo GUI, browser, audio, assistive technology, network, Git, or publication action was used.\n"
        )
    else:
        report = (
            "# TR-023 independent semantic/accessibility/source-replay audit\n\n"
            "Result: **PASS — zero current findings.**\n\n"
            "The fresh audit independently closed all 14 frozen sources and 1,152 lines; 209 expression shapes; "
            "475 contextual occurrences; 418 primary expression and 475 occurrence native MathML roots, plus six "
            "source-fidelity MathML counterparts; 61 formal objects; five derivations and 23 printed lines; 84 "
            "references; eight unsolved exercises; five explicit corrections; and 14 source-order words-only streams. "
            "The documented 475-occurrence root-ARIA repair is present with zero root aria-label, role, or class. "
            "Fresh adversarial guards rejected every mutant, and two isolated independent runs were byte-identical.\n\n"
            "This is a static producer-projection audit. It does not claim cumulative-reader integration or a live "
            "browser, audio, or assistive-technology observation. No GUI, browser, audio, assistive technology, "
            "network, Git, or publication action was used.\n"
        )
    write_text(HERE, "REPORT.md", report)
    write_json(HERE, "EVIDENCE_MANIFEST.json", root_manifest())
    print(compact_json(final))
    return 0 if not final_findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
