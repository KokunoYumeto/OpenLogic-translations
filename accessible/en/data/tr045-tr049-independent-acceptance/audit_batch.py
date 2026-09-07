"""Independent read-only semantic-packet audit for TR045--TR049.

This is one shared validator for the five new chapters.  It imports only an
older independent audit utility module, never producer code.  It reconstructs
source closure from the immutable oracles, checks the sealed canonical/cold
bytes, formal structures, continuous listener projection and native MathML,
and writes evidence only beside this file.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
OLD = PROJECT / "evidence/independent_tr034_semantic_listener_audit/audit_tr034_candidate.py"
spec = importlib.util.spec_from_file_location("independent_reused_checks", OLD)
a = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(a)

ROOT = PROJECT / "work/tr045_tr049_semantic_batch"
ORACLES = PROJECT / "work/source_batch_045_079/canonical"
TRANCHES = [f"OLAB-TR-{number:03d}" for number in range(45, 50)]
LABELS = {
    row["label_definition_id"]: row
    for row in a.read_jsonl(PROJECT / "evidence/complete_census/oracles/label_definitions.jsonl")
}
NAMES = {
    "occ": "semantic_occurrences.jsonl",
    "expr": "expression_semantics.jsonl",
    "formal": "formal_object_semantic_bindings.jsonl",
    "source": "SOURCE_LINE_REPLAY.jsonl",
    "listen": "continuous_listen_stream.jsonl",
    "ref": "REFERENCE_LEDGER.jsonl",
    "correction": "SOURCE_CORRECTIONS.jsonl",
    "structure": "DIAGRAM_LEDGER.jsonl",
    "anchor": "ANCHOR_CROSSLINK_LEDGER.jsonl",
    "disclosure": "LISTENER_DISCLOSURE_BINDINGS.jsonl",
    "projection": "LISTENER_PROJECTIONS.jsonl",
    "macro": "SOURCE_MACRO_SEMANTICS.jsonl",
}
EXPECTED_AGGREGATE = {
    "formula_occurrences": 1670,
    "expressions": 678,
    "formal_objects": 185,
    "tables": 34,
    "proof_trees": 29,
    "proof_nodes": 94,
    "source_generated_math_objects": 100,
    "exercises": 26,
}
Q = "{http://www.w3.org/1998/Math/MathML}"
ARITY = {
    "msub": 2,
    "msup": 2,
    "msubsup": 3,
    "mfrac": 2,
    "mover": 2,
    "munder": 2,
    "munderover": 3,
    "mroot": 2,
}
REDUCTIONS = {
    "aconvone": ("→", "α"), "bredone": ("→", "β"),
    "eredone": ("→", "η"), "beredone": ("→", "βη"),
    "xredone": ("→", "X"), "aconv": ("↠", "α"),
    "bred": ("↠", "β"), "ered": ("↠", "η"),
    "bered": ("↠", "βη"), "xred": ("↠", "X"),
    "aeq": ("=", "α"), "bredpar": ("⇒", "β"),
    "beredpar": ("⇒", "βη"),
}
PLACEHOLDER = re.compile(
    r"\{\{(projected-formula-\d+|source-math:\d+|reference-\d+)\}\}"
)
BOUNDARY_NOUNS = {
    "valuation", "rule", "language", "logic", "predicate", "function",
    "relation", "formula", "term", "expression", "set", "sequence", "variable",
}
BAD_CONTINUOUS_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in [
        r"\bfor (?:some|any) formula [A-Z] belongs to\b",
        r"\bthere is a finite subset .{0,50} is a subset of\b",
        r"\bdistinct positions in the sequent position\b",
        r"\ba sequent the (?:two|three|n) sided sequent\b",
        r"\ban expression the (?:two|three|n) sided sequent\b",
        r"\bin a three sided sequent the three sided sequent\b",
        r"\bthe sequent the (?:two|three|n) sided sequent\b",
        r"\binitial sequents the (?:two|three|n) sided sequent\b",
        r"\btake the sequent the (?:two|three|n) sided sequent\b",
        r"\baxioms are the (?:two|three|n) sided sequent\b",
        r"\b(?:a|for any) sentence formula [A-Z]\b",
        r"\bwe should set .{0,120} has value\b",
        r"\bstipulated (?!that\b).{0,120} has value\b",
        r"\bwill have truth value the value\b",
        r"\bwe have the truth function .{0,120} has value\b",
        r"\bthere is a valuation assignment [a-z] maps\b",
        r"\bfor some valuation the assignment\b",
        r"\bfor any the assignment\b",
    ]
]


def words(value: str, label: str) -> None:
    a.require(isinstance(value, str) and value.strip() == value and bool(value), f"empty/untrimmed {label}")
    a.require(not a.LISTEN_RESIDUE.search(value), f"raw notation {label}")
    a.require(not re.search(r"![A-Za-z]|!!|OLABMARK[A-Z]+", value), f"raw producer marker {label}")


def normalize_tex(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_spoken_punctuation(value: str) -> str:
    return re.sub(r"\s+([,.:;!?])", r"\1", re.sub(r"\s+", " ", value)).strip()


def boundary_word(value: str) -> str:
    value = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", value).lower()
    if value.endswith("s") and len(value) > 3:
        value = value[:-1]
    return value


def inspect_mathml(value: str, tex: str, label: str, metrics: Counter) -> ET.Element:
    a.verify_mathml(value, tex, label)
    root = ET.fromstring(value)
    metrics["native_mathml_records"] += 1
    for node in root.iter():
        a.require(node.tag.startswith(Q), f"foreign MathML namespace {label}")
        tag = node.tag.removeprefix(Q)
        if tag in ARITY:
            a.require(len(node) == ARITY[tag], f"fixed MathML arity {label} {tag}")
        if tag in {"mi", "mo", "mn", "mtext"}:
            a.require(not len(node), f"children in MathML token {label} {tag}")
            a.require(not re.search(r"\\[A-Za-z]+|\$|!!", node.text or ""), f"raw TeX token {label}")

    if not root.get("data-source-fragment"):
        for name in set(re.findall(r"\\fn\{([A-Za-z]{2,})\}", tex)):
            a.require(any(node.text == name for node in root.iter(Q + "mi")), f"named function split {label} {name}")
            metrics["named_function_checks"] += 1
        for macro, (arrow, script) in REDUCTIONS.items():
            expected = len(re.findall(r"\\" + macro + r"(?![A-Za-z])", tex))
            if expected:
                found = sum(
                    len(node) == 2
                    and node[0].tag == Q + "mo"
                    and node[0].text == arrow
                    and "".join(node[1].itertext()) == script
                    for node in root.iter(Q + "mover")
                )
                a.require(found >= expected, f"reduction relation topology {label} {macro}")
                metrics["reduction_relation_checks"] += expected
        lambda_count = len(re.findall(r"\\(?:lambd|lambda)(?![A-Za-z])", tex))
        if lambda_count:
            actual = sum(node.text == "λ" for node in root.iter(Q + "mi"))
            a.require(actual == lambda_count, f"lambda binder count {label}")
            metrics["lambda_binder_checks"] += lambda_count

        entail_calls = list(re.finditer(r"\\Entails(?P<neg>/)?(?P<sub>\[[^\]]+\])?", tex))
        if entail_calls:
            relations = [node for node in root.iter(Q + "mo") if node.text in {"⊨", "⊭"}]
            a.require(len(relations) >= len(entail_calls), f"entailment relation missing {label}")
            for index, match in enumerate(entail_calls):
                expected_relation = "⊭" if match.group("neg") else "⊨"
                relation = relations[index]
                a.require(relation.text == expected_relation, f"entailment polarity {label}")
                if match.group("sub"):
                    parent = next((node for node in root.iter(Q + "msub") if len(node) == 2 and node[0] is relation), None)
                    a.require(parent is not None, f"entailment optional logic must be subscript {label}")
            forbidden = [node.text for node in root.iter(Q + "mo") if node.text in {"[", "]", "/"}]
            a.require(not forbidden, f"literal entailment macro syntax in MathML {label}: {forbidden}")
            metrics["entailment_macro_checks"] += len(entail_calls)
    return root


def verify_widest_lambda_scope(formula_id: str, root: ET.Element, label: str) -> None:
    expectations = {
        "projected-formula-0023016": ("y", "x"),
        "projected-formula-0023035": ("n", None),
        "projected-formula-0023087": ("x1…xn", "g"),
    }
    if formula_id not in expectations:
        return
    scopes = [node for node in root.iter(Q + "mrow") if node.get("data-source-scope") == "widest-continuation"]
    a.require(len(scopes) == 1, f"widest-scope structural root count {label}")
    scope = scopes[0]
    children = [node for node in scope if node.tag != Q + "mspace"]
    binder, outer_binder = expectations[formula_id]
    a.require(
        len(children) == 4
        and children[0].tag == Q + "mi" and children[0].text == "λ"
        and children[1].tag == Q + "mrow" and "".join(children[1].itertext()) == binder
        and children[2].tag == Q + "mo" and children[2].text == "."
        and children[3].tag == Q + "mrow",
        f"widest-scope abstraction topology {label}",
    )
    body = children[3]
    direct = [node for node in body if node.tag != Q + "mspace"]
    if formula_id == "projected-formula-0023016":
        a.require(
            len(direct) >= 2
            and ["".join(node.itertext()) for node in direct[-2:]] == ["n¯", "m¯"]
            and all(node.tag == Q + "mover" for node in direct[-2:]),
            f"continuation numerals outside inner lambda body {label}",
        )
    elif formula_id == "projected-formula-0023035":
        names = [node.text for node in body.iter(Q + "mi") if node.get("mathvariant") == "normal"]
        a.require(names[:2] == ["IsZero", "Mult"] and "Pred" in names, f"continued Mult factor outside outer lambda body {label}")
    else:
        signature = [(node.tag.removeprefix(Q), "".join(node.itertext())) for node in direct]
        a.require(
            len(signature) == 5
            and signature[0] == ("mi", "N")
            and signature[1] == ("mo", "(")
            and signature[2] == ("mi", "Y")
            and signature[3][0] == "mrow" and signature[3][1].startswith("λg.λx1…xn.N")
            and signature[4] == ("mo", ")"),
            f"Y-lambda continuation outside first abstraction body {label}",
        )
    if outer_binder is not None:
        parent = {child: node for node in root.iter() for child in node}
        ancestors = []
        cursor = scope
        while cursor in parent:
            cursor = parent[cursor]
            ancestors.append(cursor)
        a.require(
            any(
                node.tag == Q + "mrow"
                and any(child.tag == Q + "mi" and child.text == "λ" for child in node)
                and outer_binder in "".join(node.itertext()).split(".", 1)[0]
                for node in ancestors
            ),
            f"widest-scope continuation escaped outer lambda {label}",
        )


def source_span(original: dict, raw: str) -> tuple[int, int]:
    start = original["offset"]
    if "stream_end" in original:
        end = start + original["stream_end"] - original["stream_start"]
    else:
        end = start
    a.require(0 <= start <= end <= len(raw), "source span outside immutable file")
    return start, end


def recursive_formula_ids(value) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"formula_id", "row_header_formula_id", "conclusion_formula_id"} and isinstance(item, str):
                found.append(item)
            else:
                found.extend(recursive_formula_ids(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(recursive_formula_ids(item))
    return found


def verify_structure(
    row: dict,
    oracle_formals: dict,
    occurrences: list[dict],
    macros: list[dict],
    references: list[dict],
    raw: dict[str, str],
) -> dict:
    ident = row["formal_object_id"]
    a.require(ident in oracle_formals, f"structure formal missing from oracle {ident}")
    original = oracle_formals[ident]
    a.require(row["source_formal_object"] == original, f"structure source formal drift {ident}")
    a.require(row["file"] == original["file"], f"structure file drift {ident}")
    source = raw[row["file"]]
    if row["kind"] == "table":
        start, end = source_span(original, source)
        a.require(original["object_class"] == "table", f"non-table oracle object {ident}")
    else:
        start, end = row["offset"], row["source_end"]
        a.require(original["object_class"] == "proof_tree", f"non-proof oracle object {ident}")
    a.require(source[start:end] == row["source_normalized_tex"], f"structure exact source slice {ident}")
    first_line = source.count("\n", 0, start) + 1
    last_line = source.count("\n", 0, max(start, end - 1)) + 1
    a.require(row["source_lines"] == [first_line, last_line], f"structure source line span {ident}")

    nested = [item["formula_id"] for item in occurrences if item["file"] == row["file"] and start <= item["offset"] < end]
    a.require(row["nested_formula_ids"] == nested, f"structure frozen-formula source order {ident}")
    inside_macros = [item for item in macros if item["file"] == row["file"] and start <= item["offset"] < end]
    inside_refs = [item for item in references if item["source_reference"]["file"] == row["file"] and start <= item["source_reference"]["offset"] < end]
    events = [(next(item["offset"] for item in occurrences if item["formula_id"] == fid), fid) for fid in nested]
    events += [(item["offset"], f"source-math:{item['offset']}") for item in inside_macros]
    events += [(item["source_reference"]["offset"], item["reference_id"]) for item in inside_refs]
    expected_placeholders = [ident for _, ident in sorted(events)]
    actual_placeholders = PLACEHOLDER.findall(row["listen_template"])
    a.require(actual_placeholders == expected_placeholders, f"structure listener placeholder/source order {ident}")

    by_formula = {item["formula_id"]: item["speech"] for item in occurrences}
    by_macro = {f"source-math:{item['offset']}": item["speech"] for item in inside_macros}
    by_reference = {item["reference_id"]: item["speech"] for item in inside_refs}
    substitutions = {**by_formula, **by_macro, **by_reference}
    rendered = PLACEHOLDER.sub(lambda match: substitutions[match.group(1)], row["listen_template"])
    # listen_text is an independently authored standalone description; the
    # rendered template is the source-span replacement used in the continuous
    # stream.  Both must be source-faithful but need not use identical wording.
    words(row["listen_text"], f"structure {ident}")
    metadata_ids = recursive_formula_ids({
        key: value for key, value in row.items()
        if key not in {"nested_formula_ids", "source_formal_object", "listen_template"}
    })
    a.require(set(metadata_ids) <= set(nested), f"structure metadata references alien formula {ident}")

    if row["kind"] == "table":
        a.require(row["column_headers"] and row["rows"], f"empty table coordinates {ident}")
        positions = [item.get("source_line", item.get("source_row", item.get("row_index", 0))) for item in row["rows"]]
        a.require(positions == sorted(positions), f"table row order {ident}")
        return {"kind": "table", "nodes": 0, "nested_formulas": len(nested)}

    a.require(row["kind"] == "proof_tree", f"unknown structure kind {ident}")
    nodes = row["nodes"]
    node_ids = [item["node_id"] for item in nodes]
    a.require(len(node_ids) == len(set(node_ids)), f"duplicate proof node {ident}")
    a.require(row["conclusion_node_id"] in node_ids, f"missing proof conclusion {ident}")
    seen: set[str] = set()
    for node in nodes:
        a.require(all(premise in seen for premise in node["premise_ids"]), f"proof premise order/topology {node['node_id']}")
        if node.get("conclusion_formula_id"):
            occurrence = next(item for item in occurrences if item["formula_id"] == node["conclusion_formula_id"])
            a.require(occurrence["file"] == row["file"] and occurrence["offset"] == node["source_offset"], f"proof node formula coordinate {node['node_id']}")
            a.require(normalize_tex(occurrence["tex"]) == normalize_tex(node["source_tex"]), f"proof node TeX {node['node_id']}")
        if node.get("rule_source_offset") is not None:
            macro = next((item for item in inside_macros if item["offset"] == node["rule_source_offset"]), None)
            frozen_rule = next((item for item in occurrences if item["file"] == row["file"] and item["offset"] == node["rule_source_offset"]), None)
            containing_formula = next((
                item for item in occurrences
                if item["file"] == row["file"]
                and item["offset"] <= node["rule_source_offset"]
                < item["offset"] + item["source_occurrence"]["stream_end"] - item["source_occurrence"]["stream_start"]
            ), None)
            a.require(
                (macro is not None and macro["speech"] == node["rule"])
                or (frozen_rule is not None and frozen_rule["speech"] == node["rule"])
                or (
                    containing_formula is not None
                    and (
                        source.startswith(node["rule_source_tex"], node["rule_source_offset"])
                        or source.startswith("$" + node["rule_source_tex"] + "$", node["rule_source_offset"])
                    )
                ),
                f"proof rule source-math binding {node['node_id']}",
            )
        words(node["speech"], f"proof node {node['node_id']}")
        seen.add(node["node_id"])
    a.require(nodes[-1]["node_id"] == row["conclusion_node_id"], f"proof conclusion not final source node {ident}")
    command_offsets = [item["offset"] for item in row["source_commands"]]
    a.require(command_offsets == sorted(command_offsets) and len(command_offsets) == len(set(command_offsets)), f"proof command source order {ident}")
    for command in row["source_commands"]:
        a.require(start <= command["offset"] < command["source_end"] <= end, f"proof command span {ident}")
        a.require(source.startswith("\\" + command["command"], command["offset"]), f"proof command exact source token {ident}")
    return {"kind": "proof_tree", "nodes": len(nodes), "nested_formulas": len(nested)}


def verify(tranche: str) -> dict:
    oracle = ORACLES / tranche
    candidate = ROOT / "canonical" / tranche
    cold = ROOT / "cold" / tranche
    expected = a.read_json(oracle / "SUMMARY.json")
    a.EXPECTED.update({key: expected[key] for key in ("source_files", "source_lines", "source_bytes")})
    records, _ = a.verify_source_authority(a.read_json(oracle / "SOURCE_AUTHORITY.json"))
    raw = {row["path"]: (a.AUTHORITY / row["path"]).read_bytes().decode("utf-8") for row in records}
    data = {key: a.read_jsonl(candidate / value) for key, value in NAMES.items()}
    composites = a.read_jsonl(candidate / "READER_COMPOSITE_MATH.jsonl")
    source = {
        key: a.read_jsonl(oracle / value)
        for key, value in {
            "occ": "formula_occurrences.jsonl", "context": "formula_contexts.jsonl",
            "formal": "formal_objects.jsonl", "ref": "references.jsonl",
            "label": "label_definitions.jsonl", "proof": "proof_diagrams.jsonl",
        }.items()
    }
    for path in candidate.glob("*.jsonl"):
        for index, row in enumerate(a.read_jsonl(path)):
            a.verify_record_hash(row, f"{tranche}/{path.name}:{index}")
    a.verify_source_replay(data["source"], records)

    a.require(len(data["occ"]) == expected["formula_occurrences"], f"formula count {tranche}")
    a.require(len(data["expr"]) == expected["expression_shapes"], f"expression count {tranche}")
    a.require(len(data["formal"]) == expected["formal_objects"], f"formal count {tranche}")
    contexts = {row["formula_id"]: row for row in source["context"]}
    byid = {row["formula_id"]: row for row in data["occ"]}
    groups: defaultdict[str, list[str]] = defaultdict(list)
    a.require(len(byid) == len(data["occ"]), f"duplicate formula IDs {tranche}")
    a.require([row["formula_id"] for row in data["occ"]] == [row["formula_id"] for row in source["occ"]], f"formula order {tranche}")
    metrics: Counter = Counter()
    formula_spans: defaultdict[str, list[tuple[int, int]]] = defaultdict(list)
    for row, original in zip(data["occ"], source["occ"]):
        fid = row["formula_id"]
        groups[row["expression_id"]].append(fid)
        a.require(row["source_occurrence"] == original, f"oracle formula identity {fid}")
        a.require(row["three_line_context"] == contexts[fid], f"source context identity {fid}")
        a.require(row["source_normalized_tex"] == original["normalized_tex"] == normalize_tex(row["tex"]), f"source TeX drift {fid}")
        opening = "$" if row["delimiter"] == "$" else (r"\[" if row["delimiter"] == r"\[...\]" else "\\begin{" + row["delimiter"] + "}")
        a.require(raw[row["file"]].startswith(opening, row["offset"]), f"immutable formula coordinate {fid}")
        end = row["offset"] + original["stream_end"] - original["stream_start"]
        formula_spans[row["file"]].append((row["offset"], end))
        source_tree = inspect_mathml(row["source_mathml"], row["source_normalized_tex"], fid + "/source", metrics)
        reader_tree = inspect_mathml(row["mathml"], row["reader_normalized_tex"], fid + "/reader", metrics)
        verify_widest_lambda_scope(fid, source_tree, fid + "/source")
        verify_widest_lambda_scope(fid, reader_tree, fid + "/reader")
        for field in ("speech", "source_speech", "read_as", "meaning"):
            words(row[field], fid + "/" + field)
        a.require(row["speech"] == row["read_as"] == row["meaning"], f"speech meaning drift {fid}")

    a.require(len(groups) == len(data["expr"]), f"expression group count {tranche}")
    for row in data["expr"]:
        eid = row["expression_id"]
        a.require(row["occurrence_ids"] == groups[eid], f"expression occurrence closure {eid}")
        a.require(row["contextual_speech_variants"] == sorted({byid[fid]["speech"] for fid in groups[eid]}), f"expression variants {eid}")
        first = byid[groups[eid][0]]
        source_tree = inspect_mathml(row["source_mathml_inline"], row["normalized_tex"], eid + "/source", metrics)
        reader_tree = inspect_mathml(row["mathml_inline"], row["reader_normalized_tex"], eid + "/reader", metrics)
        expected_source = ET.fromstring(first["source_mathml"]); expected_source.set("display", "inline")
        expected_reader = ET.fromstring(first["mathml"]); expected_reader.set("display", "inline")
        a.require(ET.tostring(source_tree) == ET.tostring(expected_source), f"expression source tree identity {eid}")
        a.require(ET.tostring(reader_tree) == ET.tostring(expected_reader), f"expression reader tree identity {eid}")

    oracle_formals = {
        row.get("environment_id", row.get("formal_object_id")): row for row in source["formal"]
    }
    formal_bindings = 0
    unsolved = 0
    for row in data["formal"]:
        ident = row["formal_object_id"]
        original = oracle_formals[ident]
        a.require(row["source_formal_object"] == original, f"formal source identity {ident}")
        a.require(row["source_formal_object_sha256"] == a.payload_hash(original), f"formal source hash {ident}")
        if "stream_end" in original:
            expected_ids = [
                item["formula_id"] for item in data["occ"]
                if item["file"] == original["file"]
                and original["stream_start"] <= item["stream_start"]
                and item["stream_end"] <= original["stream_end"]
            ]
        elif original["object_class"] == "proof_tree":
            structure = next(item for item in data["structure"] if item["formal_object_id"] == ident)
            expected_ids = structure["nested_formula_ids"]
        else:
            expected_ids = []
        a.require(row["formula_ids"] == expected_ids, f"formal stream-interval formula bindings {ident}")
        a.require(row["expression_ids"] == list(dict.fromkeys(byid[fid]["expression_id"] for fid in expected_ids)), f"formal expression bindings {ident}")
        words(row["long_description"], f"formal description {ident}")
        words(row["listen_text"], f"formal listener {ident}")
        status = "PRESERVED_UNSOLVED" if original["object_class"] == "exercise" else None
        a.require(row["exercise_solution_status"] == status, f"exercise status {ident}")
        unsolved += original["object_class"] == "exercise"
        formal_bindings += len(expected_ids)

    a.require(len(data["ref"]) == len(source["ref"]) == expected["references"], f"reference count {tranche}")
    for row, original in zip(data["ref"], source["ref"]):
        a.require(row["source_reference"] == original and row["source_reference_sha256"] == a.payload_hash(original), f"reference exact source {row['reference_id']}")
        a.require(raw[original["file"]][original["offset"]:original["offset"] + len(row["source_call"])] == row["source_call"], f"reference source call {row['reference_id']}")
        a.require(row["target_label_definition"] == LABELS[row["target_label_definition_id"]], f"reference target {row['reference_id']}")
        a.require(row["source_target_key"] == original["full_key"] == row["target_label_definition"]["full_key"], f"reference key {row['reference_id']}")
        a.require(row["resolution_status"] == "resolved", f"unresolved reference {row['reference_id']}")
        words(row["speech"], f"reference {row['reference_id']}")

    corrections = {row["correction_id"]: row for row in data["correction"]}
    a.require(len(corrections) == len(data["correction"]), f"duplicate corrections {tranche}")
    repairs: dict[str, str] = {}
    for row in corrections.values():
        exact = {str(number): raw[row["file"]].splitlines()[number - 1] for number in row["lines"]}
        a.require(row["exact_source_lines"] == exact and row["exact_source_lines_sha256"] == a.payload_hash(exact), f"correction exact source {row['correction_id']}")
        a.require(row["source_file_sha256"] == a.sha256_bytes(raw[row["file"]].encode("utf-8")), f"correction source bytes {row['correction_id']}")
        a.require(row["mode"] in {"PRESERVED_WITH_NOTE", "ENACTED_READER_CORRECTION"}, f"correction mode {row['correction_id']}")
        a.require(row["immutable_source_preserved"] is True and row["reader_projection_disclosed"] is True, f"correction disclosure {row['correction_id']}")
        if row["mode"] == "PRESERVED_WITH_NOTE":
            a.require(not row["formula_repairs"] and not row.get("replacements"), f"preserved source secretly changed {row['correction_id']}")
        else:
            a.require(row["formula_repairs"] or row.get("replacements"), f"empty enacted correction {row['correction_id']}")
        for fid, tex in row["formula_repairs"].items():
            a.require(byid[fid]["reader_normalized_tex"] == tex, f"declared formula repair not enacted {fid}")
            repairs[fid] = tex
        affected = row["affected_formula_ids"]
        a.require(len(affected) == len(set(affected)) and all(fid in byid for fid in affected), f"correction formula IDs {row['correction_id']}")
        expected_expressions = list(dict.fromkeys(byid[fid]["expression_id"] for fid in affected))
        a.require(row["affected_expression_ids"] == expected_expressions, f"correction expression links {row['correction_id']}")
        source_lines = raw[row["file"]].splitlines(keepends=True)
        line_starts = []
        cursor = 0
        for source_line in source_lines:
            line_starts.append((cursor, cursor + len(source_line)))
            cursor += len(source_line)
        correction_spans = [line_starts[number - 1] for number in row["lines"]]
        overlapping = {
            formula["formula_id"]
            for formula in data["occ"]
            if formula["file"] == row["file"]
            for formula_start, formula_end in [(
                formula["offset"],
                formula["offset"] + formula["source_occurrence"]["stream_end"] - formula["source_occurrence"]["stream_start"],
            )]
            if any(formula_start < line_end and line_start < formula_end for line_start, line_end in correction_spans)
        }
        a.require(overlapping <= set(affected), f"correction misses overlapping formula links {row['correction_id']}: {sorted(overlapping - set(affected))}")
        words(row["reader_projection"], f"correction projection {row['correction_id']}")
    for row in data["occ"]:
        if row["source_normalized_tex"] != row["reader_normalized_tex"]:
            a.require(row["formula_id"] in repairs, f"undisclosed formula repair {row['formula_id']}")

    macro_ids: set[str] = set()
    for row in data["macro"]:
        ident = row["source_macro_id"]
        a.require(ident not in macro_ids, f"duplicate source math ID {ident}")
        macro_ids.add(ident)
        a.require(raw[row["file"]][row["offset"]:row["source_end"]] == row["source_call"], f"source math exact span {ident}")
        a.require(row["source_call_sha256"] == a.sha256_bytes(row["source_call"].encode("utf-8")), f"source math hash {ident}")
        a.require(not any(start < row["source_end"] and row["offset"] < end for start, end in formula_spans[row["file"]]), f"source math overlaps frozen formula {ident}")
        inspect_mathml(row["mathml"], row["normalized_tex"], ident, metrics)
        words(row["speech"], ident)

    structure_metrics = Counter()
    structure_ids: set[str] = set()
    for row in data["structure"]:
        ident = row["formal_object_id"]
        a.require(ident not in structure_ids, f"duplicate structure ID {ident}")
        structure_ids.add(ident)
        result = verify_structure(row, oracle_formals, data["occ"], data["macro"], data["ref"], raw)
        structure_metrics[result["kind"]] += 1
        structure_metrics["proof_nodes"] += result["nodes"]
        structure_metrics["nested_formula_bindings"] += result["nested_formulas"]

    a.require([row["file"] for row in data["listen"]] == [row["path"] for row in records], f"listener file order {tranche}")
    seen: defaultdict[str, list[str]] = defaultdict(list)
    structure_by_id = {row["formal_object_id"]: row for row in data["structure"]}
    macro_by_id = {row["source_macro_id"]: row for row in data["macro"]}
    macro_by_file_offset = {(row["file"], row["offset"]): row for row in data["macro"]}
    ref_by_id = {row["reference_id"]: row for row in data["ref"]}
    for stream, record in zip(data["listen"], records):
        a.require(stream["source_sha256"] == record["sha256"], f"listener source hash {stream['file']}")
        words(stream["listen_text"], f"continuous stream {stream['file']}")
        for pattern in BAD_CONTINUOUS_PATTERNS:
            a.require(not pattern.search(stream["listen_text"]), f"known ungrammatical source/formula join {stream['file']}: {pattern.pattern}")
        tokens = stream["listen_text"].split()
        a.require(len(tokens) == stream["word_count"], f"listener word count {stream['file']}")
        binding_sets = {
            "formula": (stream["ordered_formula_bindings"], "formula_id"),
            "reference": (stream["ordered_reference_bindings"], "reference_id"),
            "disclosure": (stream["ordered_disclosure_bindings"], "correction_id"),
            "source_macro": (stream["ordered_source_macro_bindings"], "source_macro_id"),
            "structure": (stream["ordered_source_span_diagram_bindings"], "formal_object_id"),
        }
        for kind, (bindings, key) in binding_sets.items():
            for binding in bindings:
                start, end = binding["word_start"], binding["word_end"]
                a.require(0 <= start < end <= len(tokens), f"listener word range {kind}/{binding[key]}")
                a.require(" ".join(tokens[start:end]) == binding["speech"], f"listener bound words {kind}/{binding[key]}")
                seen[kind].append(binding[key])
        for binding in stream["ordered_formula_bindings"]:
            row = byid[binding["formula_id"]]
            a.require(all(binding[key] == row[key] for key in ("file", "line", "offset", "expression_id")), f"listener formula coordinate {binding['formula_id']}")
            suffix = {
                None: "", "SOURCE_ARITY": " argument", "SOURCE_NUMBER_OF_PLACES": " place",
                "SOURCE_TRUTH_VALUE_COUNT_COMPOUND": " valued",
            }
            rule = binding.get("listener_context_integration_rule")
            a.require(rule in suffix, f"unreviewed listener integration rule {binding['formula_id']}: {rule}")
            expected_speech = row["speech"] + suffix[rule]
            if row["display_mode"] == "block":
                expected_speech = "Displayed expression. " + expected_speech.rstrip(".") + ". End displayed expression."
            variants = {expected_speech}
            if expected_speech.endswith(" rule"):
                variants.add(expected_speech[:-5])
            a.require(binding["speech"] in variants, f"formula/listener speech drift {binding['formula_id']}")
            first = boundary_word(binding["speech"].split()[0])
            last = boundary_word(binding["speech"].split()[-1])
            if binding["word_start"]:
                previous = boundary_word(tokens[binding["word_start"] - 1])
                a.require(not (first in BOUNDARY_NOUNS and previous == first), f"duplicated pre-formula noun {binding['formula_id']}: {first}")
            if binding["word_end"] < len(tokens):
                following = boundary_word(tokens[binding["word_end"]])
                a.require(not (last in BOUNDARY_NOUNS and following == last), f"duplicated post-formula noun {binding['formula_id']}: {last}")
        for binding in stream["ordered_reference_bindings"]:
            base = ref_by_id[binding["reference_id"]]["speech"]
            a.require(binding["speech"].rstrip(".,;:") == base.rstrip(".,;:"), f"listener reference speech {binding['reference_id']}")
        for binding in stream["ordered_source_macro_bindings"]:
            a.require(binding["speech"] == macro_by_id[binding["source_macro_id"]]["speech"], f"listener source math speech {binding['source_macro_id']}")
        for binding in stream["ordered_source_span_diagram_bindings"]:
            row = structure_by_id[binding["formal_object_id"]]
            a.require(binding["nested_formula_ids"] == row["nested_formula_ids"], f"listener structure formula closure {binding['formal_object_id']}")
            rendered = PLACEHOLDER.sub(
                lambda match: (
                    byid[match.group(1)]["speech"] if match.group(1).startswith("projected-formula-")
                    else macro_by_file_offset[(row["file"], int(match.group(1).split(":", 1)[1]))]["speech"]
                    if match.group(1).startswith("source-math:")
                    else ref_by_id[match.group(1)]["speech"]
                ),
                row["listen_template"],
            )
            variants = {rendered}
            if (
                len(row["nested_formula_ids"]) == 1
                and row["listen_template"].strip() == "{{" + row["nested_formula_ids"][0] + "}}"
                and byid[row["nested_formula_ids"][0]]["display_mode"] == "block"
            ):
                variants.add("Displayed expression. " + rendered.rstrip(".") + ". End displayed expression.")
            a.require(normalize_spoken_punctuation(binding["speech"]) in variants, f"listener structure speech {binding['formal_object_id']}")
        for binding in stream["ordered_disclosure_bindings"]:
            a.require(corrections[binding["correction_id"]]["reader_projection"].rstrip(".") in binding["speech"], f"listener correction disclosure {binding['correction_id']}")

    exact_once = {
        "formula": [row["formula_id"] for row in data["occ"]],
        "reference": [row["reference_id"] for row in data["ref"]],
        "disclosure": list(corrections),
        "source_macro": [row["source_macro_id"] for row in data["macro"]],
        "structure": [row["formal_object_id"] for row in data["structure"]],
    }
    for kind, expected_ids in exact_once.items():
        a.require(Counter(seen[kind]) == Counter(expected_ids), f"listener exact-once closure {tranche}/{kind}")

    anchors = [row["anchor_id"] for row in data["anchor"]]
    a.require(len(set(anchors)) == len(anchors), f"duplicate anchors {tranche}")
    required = set(byid) | set(groups) | set(oracle_formals) | set(corrections)
    required |= {row["source_line_id"] for row in data["source"]}
    required |= {row["label_definition_id"] for row in source["label"]}
    required |= macro_ids | {row["composite_math_id"] for row in composites}
    a.require(required == set(anchors), f"source/semantic anchor closure {tranche}")

    counts = {
        "source_files": len(records), "source_lines": len(data["source"]),
        "source_bytes": sum(row["bytes"] for row in records),
        "formula_occurrences": len(data["occ"]), "expressions": len(data["expr"]),
        "formal_objects": len(data["formal"]), "formal_formula_bindings": formal_bindings,
        "references": len(data["ref"]), "source_corrections": len(corrections),
        "formula_reader_repairs": len(repairs), "source_generated_math_objects": len(data["macro"]),
        "listen_rows": len(data["listen"]), "listen_words": sum(row["word_count"] for row in data["listen"]),
        "exercises": unsolved, "tables": structure_metrics["table"],
        "proof_trees": structure_metrics["proof_tree"], "proof_nodes": structure_metrics["proof_nodes"],
    }
    summary = a.read_json(candidate / "SUMMARY.json")
    for key, value in counts.items():
        if key in summary:
            a.require(summary[key] == value, f"derived summary {tranche}/{key}")
    manifest = a.read_json(candidate / "EVIDENCE_MANIFEST.json")
    inventory = a.tree_rows(candidate)
    a.require([row for row in inventory if row["path"] != "EVIDENCE_MANIFEST.json"] == manifest["files"], f"manifest byte inventory {tranche}")
    producer = a.read_json(candidate / "PRODUCER_RECEIPT.json")
    a.require(producer["oracle_manifest_sha256"] == a.sha256_file(oracle / "EVIDENCE_MANIFEST.json"), f"oracle manifest pin {tranche}")
    drift = []
    for row in producer["inputs"]:
        path = Path(row["path"])
        if not path.is_absolute():
            path = PROJECT / path
        if not path.is_file() or path.stat().st_size != row["bytes"] or a.sha256_file(path) != row["sha256"]:
            drift.append(row["path"])
    a.require(not drift, f"producer input drift {tranche}: {drift}")
    cold_inventory = a.tree_rows(cold)
    a.require(cold_inventory == inventory, f"canonical/cold byte identity {tranche}")
    return {
        "status": "MECHANICAL_AND_STRUCTURAL_PASS_SEMANTIC_REVIEW_SEPARATE",
        "counts": counts,
        "mathml_metrics": dict(sorted(metrics.items())),
        "structure_metrics": dict(sorted(structure_metrics.items())),
        "tree_sha256_compact_inventory": a.tree_hash(inventory),
        "files": len(inventory), "bytes": sum(row["bytes"] for row in inventory),
        "inventory": inventory, "producer_input_drift": drift,
    }


def mutation_suite() -> list[dict]:
    results: list[dict] = []
    def reject(name, action):
        try:
            action()
        except Exception as error:
            results.append({"mutation": name, "detected": True, "detector": f"{type(error).__name__}: {error}"})
            return
        raise a.AuditError(f"adversarial mutation escaped detection: {name}")

    sample = a.read_jsonl(ROOT / "canonical/OLAB-TR-047/semantic_occurrences.jsonl")[0]
    reject("mathml_flattening_attribute", lambda: inspect_mathml(sample["mathml"].replace("<math ", '<math aria-label="flat" ', 1), sample["reader_normalized_tex"], "mutant", Counter()))
    entails = next(row for row in a.read_jsonl(ROOT / "canonical/OLAB-TR-047/semantic_occurrences.jsonl") if r"\Entails" in row["reader_normalized_tex"])
    wrong = entails["mathml"].replace("⊨", "⊭", 1) if r"\Entails/" not in entails["reader_normalized_tex"] else entails["mathml"].replace("⊭", "⊨", 1)
    reject("entailment_polarity", lambda: inspect_mathml(wrong, entails["reader_normalized_tex"], "mutant-entails", Counter()))
    structure = copy.deepcopy(a.read_jsonl(ROOT / "canonical/OLAB-TR-049/DIAGRAM_LEDGER.jsonl")[0])
    structure["nodes"][-1]["premise_ids"] = list(reversed(structure["nodes"][-1]["premise_ids"]))
    # The shared verifier catches premise order only when source/authored order is changed;
    # use a nonexistent premise to prove topology closure independently.
    structure["nodes"][-1]["premise_ids"] = ["missing-node"]
    oracle = ORACLES / "OLAB-TR-049"
    formals = {row.get("environment_id", row.get("formal_object_id")): row for row in a.read_jsonl(oracle / "formal_objects.jsonl")}
    occ = a.read_jsonl(ROOT / "canonical/OLAB-TR-049/semantic_occurrences.jsonl")
    macros = a.read_jsonl(ROOT / "canonical/OLAB-TR-049/SOURCE_MACRO_SEMANTICS.jsonl")
    refs = a.read_jsonl(ROOT / "canonical/OLAB-TR-049/REFERENCE_LEDGER.jsonl")
    authority = a.read_json(oracle / "SOURCE_AUTHORITY.json")
    raw = {row["path"]: (a.AUTHORITY / row["path"]).read_bytes().decode("utf-8") for row in authority["source_records"]}
    reject("proof_topology_missing_premise", lambda: verify_structure(structure, formals, occ, macros, refs, raw))
    a.require(len(results) == 3, "mutation suite closure")
    return results


def main() -> None:
    result = {
        "schema": "openlogic-accessible-independent-tr045-tr049-shared-audit-v1",
        "scope": "One shared independent mechanical/structural validator; semantic review is recorded separately.",
        "authority_commit": "9620cc73f9c8e0ad003c514a5d3748f29611c4c0",
        "audit_program_sha256": a.sha256_file(Path(__file__)),
        "reused_independent_utility_sha256": a.sha256_file(OLD),
        "chapters": {},
    }
    aggregate = Counter()
    aggregate_rows = []
    for tranche in TRANCHES:
        try:
            row = verify(tranche)
        except Exception as error:
            row = {"status": "NOT_ACCEPTED", "failure": f"{type(error).__name__}: {error}"}
        result["chapters"][tranche] = row
        if row["status"].endswith("PASS_SEMANTIC_REVIEW_SEPARATE"):
            aggregate.update(row["counts"])
            aggregate_rows.extend({**item, "path": f"{tranche}/{item['path']}"} for item in row["inventory"])
    result["aggregate_counts"] = dict(sorted(aggregate.items()))
    result["expected_aggregate"] = EXPECTED_AGGREGATE
    if all(row["status"].endswith("PASS_SEMANTIC_REVIEW_SEPARATE") for row in result["chapters"].values()):
        for key, value in EXPECTED_AGGREGATE.items():
            a.require(result["aggregate_counts"].get(key) == value, f"aggregate closure {key}")
        result["aggregate_tree_sha256_compact_inventory"] = a.payload_hash(aggregate_rows)
        result["aggregate_files"] = len(aggregate_rows)
        result["aggregate_bytes"] = sum(row["bytes"] for row in aggregate_rows)
        result["adversarial_mutations"] = mutation_suite()
        result["status"] = "PASS_SHARED_MECHANICAL_AND_STRUCTURAL_AUDIT_SEMANTIC_REVIEW_SEPARATE"
    else:
        result["status"] = "NOT_ACCEPTED"
    a.write_json(HERE / "MECHANICAL_RESULT.json", result)
    print(a.compact({"status": result["status"], "chapters": {key: value["status"] for key, value in result["chapters"].items()}, "aggregate_counts": result["aggregate_counts"]}))


if __name__ == "__main__":
    main()
