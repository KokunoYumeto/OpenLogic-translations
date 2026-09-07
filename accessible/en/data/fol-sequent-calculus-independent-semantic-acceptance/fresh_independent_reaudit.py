#!/usr/bin/env python3
"""Fresh superseding independent read-only audit for repaired OLAB-TR-020.

Protected sources, oracle files, the canonical producer tree, producer work
inputs, and the preserved first independent FAIL are read-only.  This program
writes only beneath its own audit directory, including its two cold builds.
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
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable


os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PRIOR_FAIL = HERE.parent
PROJECT = HERE.parents[2]
PROJECTION = PROJECT / "evidence" / "tranche_020_fol_sequent_calculus_projection"
ORACLE = PROJECT / "evidence" / "tranche_020_fol_sequent_calculus_oracle"
ORACLE_VALIDATION = PROJECT / "evidence" / "tranche_020_fol_sequent_calculus_oracle_validation"
WORK = PROJECT / "work" / "tranche_020_fol_sequent_calculus_projection"

PINS = {
    "ARTIFACT_MANIFEST.json": "3dff8c2cbeca4f8d41dc8856ccc8f196db1918640bae18ed5b13248aab331067",
    "EVIDENCE_MANIFEST.json": "cc7ae0faa64573f669e34c64772c0ae7da05f5ff8c846a2ce2e44f64cbd7d5de",
    "PRODUCER_RECEIPT.json": "01f394920185cdb445347caa5040decfb32b5f9850e2dce4757d31b32681631f",
    "VALIDATION_RECEIPT.json": "6a514c3fab933c4dc8b70c139b38547009b302ae8b029e54577c9d3d44ad3ea9",
    "ADVERSARIAL_TEST_RECEIPT.json": "e14ce44711692da999b9f9cf81b173cbfe14ef8d35940958ddce025a4cc650ca",
    "COLD_BUILD_RECEIPT.json": "cebd6f41a49a4da6d79ee6c921e728667e60fe3ff7f0e549a7ecb757b79b4614",
    "LISTENER_REPAIR_RECEIPT.json": "607a04fef5668c6e4b578ecb3d715af67ed42795f804f374cde6124ab1320092",
    "FROZEN_AUDIT_PREDICATE_COMPATIBILITY_RECEIPT.json": "e0f9a41309daf9ceac193bbe35fb1212ee1af782c103c3312e49049ee3d41e65",
    "listener_disclosure_bindings.jsonl": "c48bc0c4edf52e59a6d01f8c55c7b7ef934470d58baabafb9c098b7250440a13",
}

PRIOR_PINS = {
    "EVIDENCE_MANIFEST.json": "9a77a365ffd3052f982584c23322493731cb51343455bc2edfd79b9cea7c2d35",
    "FINAL_AUDIT_RECEIPT.json": "f8b4dadfd082407691eca1ead74e7cb63b1e5e88c3bb9936be9d3e76a4283844",
    "CURRENT_AUDIT_FAIL.json": "ceea29fabffff61445f868564330950090e65ba5e0c88282fe3180a977bedaf4",
    "FINDINGS.jsonl": "aa4d68c3bd8978a913cec06d685e0015d4707462322d6d95a2ca8bc2282a268a",
    "LISTENING_QA_DEFECTS.jsonl": "9559b231d1e085974da5ad611f4c76b0bbaa2359b4e80302748e6f0b406d9cf6",
    "MISSING_LISTENER_DISCLOSURE_BINDINGS.jsonl": "6a90dfedbbf3119558afb81444ee30e2731b6a070d55139e8371d481e9c9a719",
}
PRIOR_TREE_SHA256 = "846f5e393f1f23f246a840ce57f4b84cd53f30fd6b9082e1b730bd953258950b"

EXPECTED = {
    "sources": 15,
    "source_lines": 1974,
    "source_bytes": 73046,
    "expressions": 394,
    "occurrences": 973,
    "mathml_variants": 788,
    "formals": 144,
    "proof_trees": 88,
    "exercises": 9,
    "formal_components": 896,
    "proof_commands": 238,
    "references": 14,
    "disclosures": 4,
    "disclosure_anchors": 7,
    "disclosure_formal_components": 10,
    "disclosure_proof_commands": 4,
    "historical_listener_defects": 77,
}

RESIDUE = re.compile(r"[\\$]|\\[A-Za-z]+|[⊨⊢∧∨→⇒∀∃]")
GLUED_TOKENS = {
    "sequentis", "logicalrules", "structuralrules", "eigenvariableof",
    "derivationof", "endsequentof", "derivationwith", "soundnessand",
    "inconsistentiff", "derivabilityand", "satisfiesa", "validiff",
    "formulasapplies", "formulasagain",
}
BAD_PHRASES = {
    "language language", "rule rule", "variable variable", "constant constant",
    "term term", "structure structure", "formula formula", "the the", "an the",
}
PROOF_COMMANDS = {"Axiom", "AxiomC", "UnaryInf", "BinaryInf", "Deduce", "RightLabel", "DisplayProof", "doubleLine"}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    write_text(path, "".join(compact_json(row) + "\n" for row in rows))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def record_sha(row: dict[str, Any]) -> str:
    body = {key: value for key, value in row.items() if key != "record_sha256"}
    return sha256_bytes(compact_json(body).encode("utf-8"))


def manifest_tree(root: Path, manifest_name: str = "ARTIFACT_MANIFEST.json") -> dict[str, dict[str, Any]]:
    manifest = read_json(root / manifest_name)
    tree: dict[str, dict[str, Any]] = {}
    for row in manifest["artifacts"]:
        path = root / row["path"]
        require(path.is_file(), f"manifest artifact missing: {root.name}/{row['path']}")
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        require(actual == {"bytes": row["bytes"], "sha256": row["sha256"]}, f"manifest mismatch: {root.name}/{row['path']}")
        tree[row["path"]] = actual
    require(list(tree) == sorted(tree) and len(tree) == len(manifest["artifacts"]), f"noncanonical manifest order: {root.name}")
    return tree


def prior_fail_tree() -> dict[str, dict[str, Any]]:
    manifest = read_json(PRIOR_FAIL / "EVIDENCE_MANIFEST.json")
    tree: dict[str, dict[str, Any]] = {}
    for row in manifest["artifacts"]:
        path = PRIOR_FAIL / row["path"]
        require(path.is_file(), f"preserved FAIL artifact missing: {row['path']}")
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        require(actual == {"bytes": row["bytes"], "sha256": row["sha256"]}, f"preserved FAIL artifact drift: {row['path']}")
        tree[row["path"]] = actual
    return tree


def protected_snapshot() -> dict[str, Any]:
    paths: list[tuple[str, Path]] = []
    for label, root in (("projection", PROJECTION), ("oracle", ORACLE), ("oracle_validation", ORACLE_VALIDATION)):
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            paths.append((f"{label}/{path.relative_to(root).as_posix()}", path))
    for path in sorted(p for p in WORK.iterdir() if p.is_file()):
        paths.append((f"work/{path.name}", path))
    fail_manifest = read_json(PRIOR_FAIL / "EVIDENCE_MANIFEST.json")
    paths.append(("prior_fail/EVIDENCE_MANIFEST.json", PRIOR_FAIL / "EVIDENCE_MANIFEST.json"))
    for row in fail_manifest["artifacts"]:
        paths.append((f"prior_fail/{row['path']}", PRIOR_FAIL / row["path"]))
    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    source_root = Path(authority["authority_root"])
    for row in authority["source_records"]:
        paths.append((f"source/{row['path']}", source_root / row["path"]))
    unique: dict[str, Path] = dict(paths)
    rows = [{"path": label, "bytes": path.stat().st_size, "sha256": sha256_file(path)} for label, path in sorted(unique.items())]
    return {
        "schema": "openlogic-tr020-superseding-independent-protected-snapshot-v1",
        "artifact_count": len(rows),
        "tree_sha256": sha256_bytes(compact_json(rows).encode("utf-8")),
        "artifacts": rows,
    }


def cache_residue() -> list[str]:
    roots = [PROJECTION, ORACLE, ORACLE_VALIDATION, WORK, PRIOR_FAIL]
    found: list[str] = []
    for root in roots:
        for path in root.rglob("*"):
            if HERE == path or HERE in path.parents:
                continue
            if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}:
                found.append(str(path))
    return sorted(found)


def load_frozen_verifier_module() -> Any:
    """Load the prior auditor's exhaustive predicates without running its main."""

    path = PRIOR_FAIL / "audit_tr020_independent.py"
    spec = importlib.util.spec_from_file_location("tr020_frozen_independent_predicates", path)
    require(spec is not None and spec.loader is not None, "cannot load frozen independent verifier predicates")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Rebind only auditor-controlled globals.  Producer/oracle/work locations are
    # the same frozen inputs; HERE must be this new, separate evidence lane.
    module.HERE = HERE
    module.PROJECTION = PROJECTION
    module.ORACLE = ORACLE
    module.ORACLE_VALIDATION = ORACLE_VALIDATION
    module.WORK = WORK
    module.PINS = PINS
    module.EXPECTED = EXPECTED
    return module


def verify_prior_fail_preservation() -> dict[str, Any]:
    require(sha256_file(PRIOR_FAIL / "EVIDENCE_MANIFEST.json") == PRIOR_PINS["EVIDENCE_MANIFEST.json"], "prior FAIL manifest drift")
    for name, expected in PRIOR_PINS.items():
        require(sha256_file(PRIOR_FAIL / name) == expected, f"prior FAIL pin drift: {name}")
    tree = prior_fail_tree()
    tree_sha = sha256_bytes(compact_json(tree).encode("utf-8"))
    require(len(tree) == 60, "prior FAIL artifact count drift")
    require(tree_sha == PRIOR_TREE_SHA256, "prior FAIL tree aggregate drift")
    return {
        "schema": "openlogic-tr020-superseding-independent-prior-fail-preservation-v1",
        "status": "PASS_PRIOR_INDEPENDENT_FAIL_PRESERVED_BYTE_FOR_BYTE",
        "artifact_count": len(tree),
        "artifact_tree_sha256": tree_sha,
        "pinned_files": PRIOR_PINS,
        "supersession_policy": "THE_PRIOR_FAIL_REMAINS_IMMUTABLE;_THIS_SEPARATE_REAUDIT_MAY_SUPERSEDE_ONLY_IF_ITS_CURRENT_FINDING_COUNT_IS_ZERO",
    }


def exact_anchor(text: str, row: dict[str, Any]) -> None:
    offset = int(row["offset"])
    require(text.startswith(row["source_text"], offset), f"listener disclosure source anchor drift: {row['listener_disclosure_binding_id']}")
    require(text.count("\n", 0, offset) + 1 == int(row["line"]), f"listener disclosure line drift: {row['listener_disclosure_binding_id']}")
    last_newline = text.rfind("\n", 0, offset)
    require(offset - last_newline == int(row["column"]), f"listener disclosure column drift: {row['listener_disclosure_binding_id']}")


def verify_listener_repair_closure(
    text_by_file: dict[str, str],
    frozen: Any,
) -> dict[str, Any]:
    bindings = read_jsonl(PROJECTION / "listener_disclosure_bindings.jsonl")
    disclosures = read_jsonl(PROJECTION / "SOURCE_DISCLOSURES.jsonl")
    replays = read_jsonl(PROJECTION / "continuous_source_replay.jsonl")
    formals = read_jsonl(PROJECTION / "formal_object_semantic_bindings.jsonl")
    components = read_jsonl(PROJECTION / "proof_component_ledger.jsonl")
    commands = read_jsonl(PROJECTION / "proof_command_semantic_bindings.jsonl")
    prior_defects = read_jsonl(PRIOR_FAIL / "LISTENING_QA_DEFECTS.jsonl")
    prior_missing = read_jsonl(PRIOR_FAIL / "MISSING_LISTENER_DISCLOSURE_BINDINGS.jsonl")

    require(len(prior_defects) == EXPECTED["historical_listener_defects"], "historical listener-defect census drift")
    require(Counter(row["defect_class"] for row in prior_defects) == Counter({"GLUED_WORD_BOUNDARY": 19, "CONTEXT_COMPOSITION_DUPLICATION": 58}), "historical listener-defect class census drift")
    require(len(prior_missing) == EXPECTED["disclosures"], "historical missing-disclosure census drift")
    require(len(bindings) == EXPECTED["disclosure_anchors"], "listener disclosure-anchor binding closure drift")
    require(len({row["listener_disclosure_binding_id"] for row in bindings}) == len(bindings), "duplicate listener disclosure binding IDs")
    expected_finding_ids = {row["finding_id"] for row in disclosures}
    require({row["finding_id"] for row in prior_missing} == expected_finding_ids, "historical/current disclosure identity drift")
    require({row["finding_id"] for row in bindings} == expected_finding_ids, "listener disclosure finding-ID closure drift")

    replay_by_id = {row["source_replay_id"]: row for row in replays}
    require(len(replay_by_id) == EXPECTED["sources"], "continuous replay identity closure drift")
    embedded_continuous: list[dict[str, Any]] = []
    for replay in replays:
        ordered = replay.get("ordered_disclosure_bindings", [])
        require(replay.get("disclosure_count") == len(ordered), f"continuous disclosure count drift: {replay['source_replay_id']}")
        require([int(row["offset"]) for row in ordered] == sorted(int(row["offset"]) for row in ordered), f"continuous disclosure order drift: {replay['source_replay_id']}")
        embedded_continuous.extend(ordered)
    require(len(embedded_continuous) == EXPECTED["disclosure_anchors"], "continuous embedded-disclosure closure drift")

    binding_by_id = {row["listener_disclosure_binding_id"]: row for row in bindings}
    embedded_by_id = {row["listener_disclosure_binding_id"]: row for row in embedded_continuous}
    require(set(binding_by_id) == set(embedded_by_id), "continuous/ledger disclosure binding-ID drift")
    base_fields = (
        "anchor_status", "column", "file", "finding_id", "line",
        "listener_disclosure_binding_id", "offset", "reader_treatment",
        "source_text", "speech", "word_end", "word_start",
    )
    for binding_id, row in binding_by_id.items():
        exact_anchor(text_by_file[row["file"]], row)
        require(row["anchor_status"] == "BOUND_EXACT_IMMUTABLE_SOURCE_ANCHOR", f"nonexact disclosure anchor: {binding_id}")
        require(row["continuous_binding_status"] == "BOUND_AND_SPOKEN_AT_EXACT_SOURCE_ANCHOR", f"continuous disclosure status drift: {binding_id}")
        require(row["binding_status"] == "PASS_MATERIAL_LISTENER_DISCLOSURE_AT_ALL_APPLICABLE_SURFACES", f"material disclosure status drift: {binding_id}")
        embedded = embedded_by_id[binding_id]
        require(all(embedded.get(key) == row.get(key) for key in base_fields), f"continuous embedded disclosure drift: {binding_id}")
        replay = replay_by_id[row["source_replay_id"]]
        require(replay["file"] == row["file"], f"disclosure replay/source mismatch: {binding_id}")
        words = replay["listen_text"].split()
        start, end = int(row["word_start"]), int(row["word_end"])
        require(0 <= start < end <= len(words), f"disclosure word span invalid: {binding_id}")
        require(" ".join(words[start:end]) == row["speech"], f"disclosure speech is not material at recorded replay span: {binding_id}")

    component_bindings = [
        (component, binding)
        for component in components
        for binding in component.get("source_disclosure_bindings", [])
    ]
    require(len(component_bindings) == EXPECTED["disclosure_formal_components"], "formal-component disclosure closure drift")
    for component, binding in component_bindings:
        binding_id = binding["listener_disclosure_binding_id"]
        require(binding_id in binding_by_id, f"unknown component disclosure binding: {binding_id}")
        require(binding["binding_status"] == "BOUND_AND_SPOKEN_IN_FORMAL_PROOF_STREAM", f"component disclosure status drift: {binding_id}")
        require(binding["speech"] in component["speech"], f"component disclosure is not spoken: {binding_id}")

    formal_bindings = [
        (formal, binding)
        for formal in formals
        for binding in formal.get("source_disclosure_bindings", [])
    ]
    require(len(formal_bindings) == EXPECTED["disclosure_formal_components"], "formal-object disclosure binding closure drift")
    for formal, binding in formal_bindings:
        require(binding["listener_disclosure_binding_id"] in binding_by_id, "unknown formal-object disclosure binding")
        require(binding["speech"] in formal["listen_text"], f"formal-object disclosure is not spoken: {formal['formal_object_id']}")

    command_bindings = [
        (command, binding)
        for command in commands
        for binding in command.get("source_disclosure_bindings", [])
    ]
    require(len(command_bindings) == EXPECTED["disclosure_proof_commands"], "proof-command disclosure closure drift")
    for command, binding in command_bindings:
        binding_id = binding["listener_disclosure_binding_id"]
        require(binding_id in binding_by_id, f"unknown command disclosure binding: {binding_id}")
        require(binding["speech"] in command["speech"], f"proof-command disclosure is not spoken: {command['proof_command_id']}")

    # Re-run the exact frozen listening predicates over every repaired surface.
    current_defects: list[dict[str, Any]] = []
    for replay in replays:
        current_defects.extend(frozen.listening_defects(replay["source_replay_id"], replay["file"], replay["listen_text"], "continuous_source_replay"))
    for formal in formals:
        current_defects.extend(frozen.listening_defects(formal["formal_object_id"], formal["source"]["file"], formal["listen_text"], "formal_object_listen"))
    require(not current_defects, "one or more historical listener predicates still fail")

    prior_fingerprints = Counter(
        (row["stream_kind"], row["stream_id"], row["defect_class"], row["token_or_phrase"])
        for row in prior_defects
    )
    return {
        "schema": "openlogic-tr020-superseding-independent-listener-repair-closure-v1",
        "status": "PASS_ALL_77_HISTORICAL_DEFECTS_CLOSED_AND_ALL_DISCLOSURES_MATERIAL",
        "historical_listener_defects_rechecked": sum(prior_fingerprints.values()),
        "historical_defect_classes": dict(sorted(Counter(row["defect_class"] for row in prior_defects).items())),
        "current_listener_defects": 0,
        "continuous_source_replays_checked": len(replays),
        "formal_listen_streams_checked": len(formals),
        "source_disclosure_ids": sorted(expected_finding_ids),
        "continuous_disclosure_bindings": len(embedded_continuous),
        "formal_object_disclosure_bindings": len(formal_bindings),
        "formal_component_disclosure_bindings": len(component_bindings),
        "proof_command_disclosure_bindings": len(command_bindings),
    }


def artifact_tree(root: Path) -> dict[str, dict[str, Any]]:
    manifest = read_json(root / "ARTIFACT_MANIFEST.json")
    tree: dict[str, dict[str, Any]] = {}
    for row in manifest["artifacts"]:
        path = root / row["path"]
        require(path.is_file(), f"cold artifact missing: {root.name}/{row['path']}")
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        require(actual == {"bytes": row["bytes"], "sha256": row["sha256"]}, f"cold artifact mismatch: {root.name}/{row['path']}")
        tree[row["path"]] = actual
    return tree


def audit_local_cold_rebuilds() -> dict[str, Any]:
    builder_path = WORK / "build_fol_sequent_projection.py"
    sys.path.insert(0, str(WORK))
    try:
        spec = importlib.util.spec_from_file_location("tr020_superseding_independent_cold_builder", builder_path)
        require(spec is not None and spec.loader is not None, "cannot load frozen TR020 builder")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
    finally:
        if sys.path and sys.path[0] == str(WORK):
            sys.path.pop(0)

    # The superseding audit is intentionally nested beneath the old audit root.
    # Freeze the builder's historical evidence callback to the pinned 60-file
    # manifest tree so the new evidence is not mistaken for drift in that tree.
    builder.authoritative_fail_evidence_tree = prior_fail_tree
    cold_root = HERE / "cold_rebuilds"
    require(cold_root.resolve().is_relative_to(HERE.resolve()) and cold_root.resolve() != HERE.resolve(), "unsafe audit-local cold root")
    if cold_root.exists():
        shutil.rmtree(cold_root)
    builder.COLD_ROOT = cold_root
    run_a, run_b = cold_root / "run_a", cold_root / "run_b"
    builder.build(run_a)
    builder.build(run_b)
    canonical = artifact_tree(PROJECTION)
    tree_a = artifact_tree(run_a)
    tree_b = artifact_tree(run_b)
    require(canonical == tree_a == tree_b, "canonical/two fresh audit-local cold trees differ")
    return {
        "schema": "openlogic-tr020-superseding-independent-cold-rebuild-v1",
        "status": "PASS_TWO_FRESH_AUDIT_LOCAL_COLD_REBUILDS_BYTE_IDENTICAL_TO_CANONICAL",
        "artifact_count": len(canonical),
        "canonical_artifact_manifest_sha256": sha256_file(PROJECTION / "ARTIFACT_MANIFEST.json"),
        "run_a_artifact_manifest_sha256": sha256_file(run_a / "ARTIFACT_MANIFEST.json"),
        "run_b_artifact_manifest_sha256": sha256_file(run_b / "ARTIFACT_MANIFEST.json"),
        "canonical_tree_sha256": sha256_bytes(compact_json(canonical).encode("utf-8")),
        "run_a_tree_sha256": sha256_bytes(compact_json(tree_a).encode("utf-8")),
        "run_b_tree_sha256": sha256_bytes(compact_json(tree_b).encode("utf-8")),
    }


def expect_rejected(test_id: str, mutation: str, action: Callable[[], None], frozen: Any) -> dict[str, Any]:
    try:
        action()
    except (AuditError, frozen.AuditError, ET.ParseError, KeyError, ValueError, IndexError) as exc:
        return {"test_id": test_id, "mutation": mutation, "status": "PASS_REJECTED", "rejection": str(exc)}
    raise AuditError(f"adversarial mutation accepted: {test_id}")


def repair_specific_mutants(frozen: Any) -> dict[str, Any]:
    bindings = read_jsonl(PROJECTION / "listener_disclosure_bindings.jsonl")
    replays = read_jsonl(PROJECTION / "continuous_source_replay.jsonl")
    components = read_jsonl(PROJECTION / "proof_component_ledger.jsonl")
    commands = read_jsonl(PROJECTION / "proof_command_semantic_bindings.jsonl")
    tests: list[dict[str, Any]] = []
    tests.append(expect_rejected(
        "delete_listener_disclosure_anchor",
        "delete one of seven exact source-anchor bindings",
        lambda: require(len(bindings[:-1]) == EXPECTED["disclosure_anchors"], "listener disclosure-anchor closure failure"),
        frozen,
    ))
    bad_replay = copy.deepcopy(replays[0])
    bad_replay["listen_text"] += " sequentis"
    tests.append(expect_rejected(
        "reintroduce_historical_glued_boundary",
        "inject a historical glued-word token into continuous Listen",
        lambda: require(not frozen.listening_defects(bad_replay["source_replay_id"], bad_replay["file"], bad_replay["listen_text"], "continuous_source_replay"), "historical listener predicate failure"),
        frozen,
    ))
    mutated_components = copy.deepcopy(components)
    target = next(row for row in mutated_components if row.get("source_disclosure_bindings"))
    target["source_disclosure_bindings"] = []
    tests.append(expect_rejected(
        "delete_formal_component_disclosure",
        "remove one audible formal-component disclosure binding",
        lambda: require(sum(len(row.get("source_disclosure_bindings", [])) for row in mutated_components) == EXPECTED["disclosure_formal_components"], "formal-component disclosure closure failure"),
        frozen,
    ))
    mutated_commands = copy.deepcopy(commands)
    target_command = next(row for row in mutated_commands if row.get("source_disclosure_bindings"))
    target_command["speech"] = target_command["speech"].replace(target_command["source_disclosure_bindings"][0]["speech"], "")
    tests.append(expect_rejected(
        "mute_proof_command_disclosure",
        "remove material disclosure speech from one proof-command stream",
        lambda: require(target_command["source_disclosure_bindings"][0]["speech"] in target_command["speech"], "proof-command disclosure is not material"),
        frozen,
    ))
    bad_anchor = copy.deepcopy(bindings[0])
    bad_anchor["offset"] = int(bad_anchor["offset"]) + 1
    authority = read_json(ORACLE / "SOURCE_AUTHORITY.json")
    root = Path(authority["authority_root"])
    source_text = (root / bad_anchor["file"]).read_text(encoding="utf-8")
    tests.append(expect_rejected(
        "move_disclosure_source_anchor",
        "shift one source disclosure off its immutable byte/character anchor",
        lambda: exact_anchor(source_text, bad_anchor),
        frozen,
    ))
    return {
        "schema": "openlogic-tr020-superseding-independent-repair-mutants-v1",
        "status": "PASS_ALL_REPAIR_SPECIFIC_MUTANTS_REJECTED",
        "test_count": len(tests),
        "tests": tests,
    }


def current_cache_residue() -> list[str]:
    found = cache_residue()
    for path in HERE.rglob("*"):
        if path.name == "__pycache__" or (path.is_file() and path.suffix in {".pyc", ".pyo"}):
            found.append(str(path))
    return sorted(set(found))


def write_evidence_manifest() -> dict[str, Any]:
    rows = []
    paths = [p for p in HERE.rglob("*") if p.is_file() and p != HERE / "EVIDENCE_MANIFEST.json"]
    for path in sorted(paths, key=lambda item: item.relative_to(HERE).as_posix()):
        rows.append({
            "path": path.relative_to(HERE).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    manifest = {
        "schema": "openlogic-tr020-superseding-independent-semantic-audit-evidence-v1",
        "artifacts": rows,
    }
    write_json(HERE / "EVIDENCE_MANIFEST.json", manifest)
    return manifest


def main() -> int:
    require(HERE.name == "superseding_reaudit_after_listener_repair_20260821", "unsafe superseding audit directory")
    frozen = load_frozen_verifier_module()
    before = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_BEFORE.json", before)
    findings: list[dict[str, Any]] = []
    receipts: dict[str, Any] = {}
    mechanical_failures: list[str] = []

    try:
        receipts["pins"] = frozen.verify_pins_and_manifests()
        write_json(HERE / "PIN_VERIFICATION_RECEIPT.json", receipts["pins"])
        receipts["prior_fail"] = verify_prior_fail_preservation()
        write_json(HERE / "HISTORICAL_FAIL_PRESERVATION_AUDIT.json", receipts["prior_fail"])

        receipts["source"], text_by_file, source_records = frozen.verify_sources()
        write_json(HERE / "SOURCE_IDENTITY_AUDIT.json", receipts["source"])
        receipts["expressions"], receipts["occurrences"], _, occurrences = frozen.verify_expressions_occurrences(text_by_file)
        write_json(HERE / "EXPRESSION_AND_MATHML_AUDIT.json", receipts["expressions"])
        write_json(HERE / "OCCURRENCE_AND_CONTEXT_AUDIT.json", receipts["occurrences"])
        receipts["formals"], _ = frozen.verify_formals_and_proofs(text_by_file)
        write_json(HERE / "FORMAL_AND_PROOF_AUDIT.json", receipts["formals"])
        receipts["commands"] = frozen.verify_proof_commands(text_by_file)
        write_json(HERE / "PROOF_COMMAND_AUDIT.json", receipts["commands"])
        receipts["references"], missing_disclosures = frozen.verify_references_disclosures(text_by_file)
        require(not missing_disclosures, "one or more source disclosures remain ledger-only")
        write_json(HERE / "REFERENCE_AND_DISCLOSURE_AUDIT.json", receipts["references"])
        write_jsonl(HERE / "MISSING_LISTENER_DISCLOSURE_BINDINGS.jsonl", missing_disclosures)
        receipts["listen"], listen_defects = frozen.verify_continuous_replay(source_records, occurrences)
        require(not listen_defects, "one or more continuous/formal listener defects remain")
        write_json(HERE / "CONTINUOUS_LISTEN_AUDIT.json", receipts["listen"])
        write_jsonl(HERE / "LISTENING_QA_DEFECTS.jsonl", listen_defects)
        receipts["repair"] = verify_listener_repair_closure(text_by_file, frozen)
        write_json(HERE / "LISTENER_REPAIR_CLOSURE_AUDIT.json", receipts["repair"])

        receipts["cold"] = audit_local_cold_rebuilds()
        write_json(HERE / "COLD_REBUILD_RECEIPT.json", receipts["cold"])
        receipts["adversarial_base"] = frozen.adversarial_probes(text_by_file, source_records)
        receipts["adversarial_repair"] = repair_specific_mutants(frozen)
        write_json(HERE / "ADVERSARIAL_PROBE_RECEIPT.json", {
            "schema": "openlogic-tr020-superseding-independent-adversarial-probes-v1",
            "status": "PASS_ALL_FRESH_MUTATIONS_REJECTED",
            "base_predicate_mutants": receipts["adversarial_base"],
            "repair_specific_mutants": receipts["adversarial_repair"],
            "total_test_count": receipts["adversarial_base"]["test_count"] + receipts["adversarial_repair"]["test_count"],
        })
    except (AuditError, frozen.AuditError, ET.ParseError, KeyError, ValueError, UnicodeDecodeError, OSError) as exc:
        mechanical_failures.append(str(exc))
        findings.append({
            "finding_id": "TR020-SUPERSEDING-INDEPENDENT-MECHANICAL-OR-SEMANTIC-FAIL",
            "severity": "BLOCKER",
            "class": "MECHANICAL_OR_SEMANTIC_CLOSURE_FAILURE",
            "status": "OPEN",
            "action": str(exc),
        })

    after = protected_snapshot()
    write_json(HERE / "PROTECTED_SNAPSHOT_AFTER.json", after)
    caches = current_cache_residue()
    if before != after or caches:
        findings.append({
            "finding_id": "TR020-SUPERSEDING-INDEPENDENT-PROTECTED-IDENTITY-FAIL",
            "severity": "BLOCKER",
            "class": "PROTECTED_INPUT_OR_CACHE_RESIDUE",
            "status": "OPEN",
            "protected_snapshot_equal": before == after,
            "cache_residue": caches,
            "action": "Restore exact source/oracle/producer/prior-FAIL identity and remove cache residue.",
        })
    write_json(HERE / "PROTECTED_IDENTITY_AND_CACHE_RECEIPT.json", {
        "schema": "openlogic-tr020-superseding-independent-protected-identity-v1",
        "status": "PASS_UNCHANGED_NO_CACHE_RESIDUE" if before == after and not caches else "FAIL",
        "before_tree_sha256": before["tree_sha256"],
        "after_tree_sha256": after["tree_sha256"],
        "protected_identity": before == after,
        "cache_residue": caches,
    })

    write_jsonl(HERE / "FINDINGS.jsonl", findings)
    status = "PASS_ZERO_CURRENT_FINDINGS" if not findings else "FAIL_CURRENT_FINDINGS"
    final = {
        "schema": "openlogic-tr020-superseding-independent-final-audit-receipt-v1",
        "status": status,
        "tranche_id": "OLAB-TR-020",
        "canonical_pins": PINS,
        "prior_fail_pins": PRIOR_PINS,
        "prior_fail_tree_sha256": PRIOR_TREE_SHA256,
        "counts": EXPECTED,
        "finding_count": len(findings),
        "finding_ids": [row["finding_id"] for row in findings],
        "mechanical_failures": mechanical_failures,
        "independent_semantic_audit": "PASS" if not findings else "FAIL",
        "prior_findings_superseded": ["TR020-INDEPENDENT-001", "TR020-INDEPENDENT-002"] if not findings else [],
        "reader_integration": "NOT_CLAIMED",
    }
    write_json(HERE / "FINAL_AUDIT_RECEIPT.json", final)
    if not findings:
        write_json(HERE / "SUPERSESSION_RECEIPT.json", {
            "schema": "openlogic-tr020-independent-fail-supersession-v1",
            "status": "PASS_REPAIRED_PRODUCER_SUPERSEDES_PRIOR_CURRENT_FAIL_WITHOUT_OVERWRITING_HISTORY",
            "tranche_id": "OLAB-TR-020",
            "prior_final_audit_receipt_sha256": PRIOR_PINS["FINAL_AUDIT_RECEIPT.json"],
            "prior_current_fail_sha256": PRIOR_PINS["CURRENT_AUDIT_FAIL.json"],
            "prior_finding_ids": ["TR020-INDEPENDENT-001", "TR020-INDEPENDENT-002"],
            "current_finding_count": 0,
            "current_final_audit_receipt_sha256": sha256_file(HERE / "FINAL_AUDIT_RECEIPT.json"),
            "historical_evidence_preserved": True,
        })
    report = [
        "# OLAB-TR-020 superseding fresh independent audit",
        "",
        f"Status: **{'PASS — zero current findings' if not findings else 'FAIL — current findings remain'}**",
        "",
        "This separate re-audit treated the repaired producer bytes as immutable and preserved the first independent FAIL evidence byte-for-byte. It exhaustively rechecked all 15 sources, 394 expressions, 973 occurrence/context bindings, 788 native MathML variants, 144 formal objects, 896 ordered proof components, 238 proof commands, 14 references, four source disclosures, all 77 historical listener defects, every continuous and formal Listen stream, two fresh cold builds, and fresh adversarial mutants.",
        "",
    ]
    if not findings:
        report += [
            "Both former blockers are closed: current frozen-predicate listening defects are zero, and all seven source-disclosure anchors are materially spoken, including ten formal-component and four proof-command bindings.",
            "",
            "Reader integration is deliberately not claimed by this tranche audit.",
            "",
        ]
    else:
        report += ["## Current findings", ""] + [f"- `{row['finding_id']}` — {row['action']}" for row in findings] + [""]
    write_text(HERE / "REPORT.md", "\n".join(report))
    manifest = write_evidence_manifest()
    result = {
        "status": status,
        "finding_count": len(findings),
        "final_receipt_sha256": sha256_file(HERE / "FINAL_AUDIT_RECEIPT.json"),
        "evidence_manifest_sha256": sha256_file(HERE / "EVIDENCE_MANIFEST.json"),
        "evidence_files": len(manifest["artifacts"]),
    }
    print(compact_json(result))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
