"""Carry reviewed math speech across a source update using complete reader contexts."""
from collections import defaultdict
import json
from pathlib import Path

from lxml import html
from .assembly import digest, json_bytes
from .formulaspeech import bind_speech, index_formulas
from .xhtml import text_without_annotations


def full_context_keys(data, packet):
    doc = html.document_fromstring(data, parser=html.HTMLParser(encoding="utf-8", huge_tree=True))
    contexts = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "figcaption", "caption"}
    blocks = {}
    keys = []
    for node, row in zip(doc.xpath("//math"), packet["occurrences"], strict=True):
        block = next((p for p in node.iterancestors() if p.tag in contexts), node.getparent())
        if block not in blocks:
            # Include every formula in the block and the entire surrounding prose.
            # The older speech packets retained only the first 800 prose characters.
            formulas = [a.text or "" for a in block.iter("annotation")
                        if a.get("encoding", "").lower() in ("application/x-tex", "text/x-tex", "application/x-latex")]
            ids = [(p.tag, p.get("id")) for p in [block, *block.iterancestors()] if p.get("id")]
            blocks[block] = digest(json_bytes([ids, text_without_annotations(block), formulas]))
        keys.append((row["formula_sha256"], row["preceding_import_locator"], blocks[block],
                     row["context_id"], row["in_navigation"], row["display"]))
    return keys


def speech_delta(old_html, old_packet_bytes, old_store_bytes, new_html):
    old = json.loads(old_packet_bytes)
    store = json.loads(old_store_bytes)
    if (old["reader_sha256"] != digest(old_html) or store["input_sha256"] != digest(old_packet_bytes)
            or store["language"] != old["language"] or store["reader_sha256"] != old["reader_sha256"]):
        raise ValueError("speech store, input packet and previous reader differ")
    old_replay = index_formulas(old_html, old["language"])
    for key in ("formulas", "occurrences", "contexts"):
        if old_replay[key] != old[key]:
            raise ValueError("previous speech packet does not reproduce: " + key)
    new = index_formulas(new_html, old["language"])
    old_keys = full_context_keys(old_html, old)
    new_keys = full_context_keys(new_html, new)
    groups = defaultdict(list)
    targets = defaultdict(list)
    for key, row in zip(old_keys, old["occurrences"], strict=True):
        groups[key].append(row["occurrence_id"])
    for key, row in zip(new_keys, new["occurrences"], strict=True):
        targets[key].append(row["occurrence_id"])
    reused = {}
    pending = []
    for key, current in targets.items():
        previous = groups.get(key, [])
        if len(current) == len(previous):
            for old_id, new_id in zip(previous, current, strict=True):
                reused[new_id] = old_id
        else:
            pending.extend(current)
    removed = sorted(set(r["occurrence_id"] for r in old["occurrences"]) - set(reused.values()))
    return new, {"schema":"olpkit.speech-delta.v1", "previous_reader":digest(old_html),
                 "current_reader":digest(new_html), "previous_packet":digest(old_packet_bytes),
                 "previous_store":digest(old_store_bytes), "current_packet":digest(json_bytes(new)),
                 "reused":reused, "review_required":sorted(pending), "unpaired_previous":removed}


def reviewed_store(packet, delta, previous_bytes, review, previous_map_bytes):
    previous = json.loads(previous_bytes)
    if digest(previous_bytes) != delta["previous_store"] or digest(json_bytes(packet)) != delta["current_packet"]:
        raise ValueError("speech plan differs from the supplied records")
    previous_map = digest(previous_map_bytes)
    if previous_map != previous["occurrence_source_map_sha256"]:
        raise ValueError("previous occurrence source map differs")
    if review.get("delta_sha256") != digest(json_bytes(delta)):
        raise ValueError("editorial review belongs to a different speech update")
    decisions = review["decisions"]
    if set(decisions) != set(delta["review_required"]):
        raise ValueError("changed contexts lack an exact occurrence review")
    for field in ("model", "reasoning_effort", "model_observed_at", "attribution"):
        if not review.get(field):
            raise ValueError("missing speech update attribution: " + field)
    rules = dict(previous["rules"])
    for rule_id, rule in review.get("additional_rules", {}).items():
        if rule_id in rules:
            raise ValueError("new speech rules need distinct identities")
        rules[rule_id] = rule
    passage_ids = {p["passage_id"] for rule in rules.values() for p in rule["canon_passages"]}
    source_map = {"previous_map_sha256": previous_map, "previous_store_sha256": digest(previous_bytes),
                  "review_sha256": digest(json_bytes(review)), "current_packet_sha256": delta["current_packet"],
                  "retained_occurrences": delta["reused"], "reviewed_occurrences": {}}
    old_rows = previous["formulas"]
    formulas = {}
    for key, group in packet["formulas"].items():
        prior = old_rows.get(key, {})
        readings = {}
        rule_ids = set()
        for oid in group["occurrence_ids"]:
            if oid in decisions:
                decision = decisions[oid]
                if (decision.get("formula_sha256") != key or not decision.get("source_locator")
                        or not decision.get("rationale") or not decision.get("canon_passages")):
                    raise ValueError("speech review lacks evidence at " + oid)
                if not set(decision["canon_passages"]) <= passage_ids:
                    raise ValueError("speech review cites an unknown canon passage at " + oid)
                source_map["reviewed_occurrences"][oid] = decision["source_locator"]
                previous_id = decision.get("from_occurrence")
                if previous_id is None:
                    readings[oid] = decision["spoken_text"]
                    rule_ids.update(decision["rule_ids"])
                    continue
            else:
                previous_id = delta["reused"][oid]
            if previous_id not in prior.get("occurrence_ids", ()):
                raise ValueError("previous reading uses different TeX at " + oid)
            readings[oid] = prior.get("contextual_variants", {}).get(previous_id, prior["spoken_text"])
            rule_ids.update(prior["rule_ids"])
        default = prior.get("spoken_text", next(iter(readings.values())))
        formulas[key] = {"tex": group["tex"], "occurrence_ids": group["occurrence_ids"],
                         "spoken_text": default, "rule_ids": sorted(rule_ids),
                         "contextual_variants": {k:v for k,v in readings.items() if v != default}}
    store = {"schema": previous["schema"], "language": packet["language"], "formulas": formulas, "rules": rules,
             "input_sha256": delta["current_packet"], "reader_sha256": packet["reader_sha256"],
             "occurrence_source_map_sha256": digest(json_bytes(source_map)),
             "interface": {"attribution": review["attribution"]},
             "inheritance": {k: previous[k] for k in ("model", "reasoning_effort", "model_observed_at")}}
    store["inheritance"]["store_sha256"] = digest(previous_bytes)
    for k in ("model", "reasoning_effort", "model_observed_at"):
        store[k] = review[k]
    return store, source_map


def sync_speech(args):
    previous_html, previous_packet, previous_store, reader = (
        Path(value).read_bytes() for value in (args.previous_reader, args.previous_packet, args.previous_store, args.reader))
    bind_speech(previous_html, previous_packet, previous_store)
    packet, delta = speech_delta(previous_html, previous_packet, previous_store, reader)
    output = Path(args.out)
    records = {"speech-input": packet, "speech-delta": delta}
    if args.review:
        if not args.previous_source_map:
            raise ValueError("applying reviews requires the previous occurrence source map")
        review = json.loads(Path(args.review).read_bytes())
        store, source_map = reviewed_store(packet, delta, previous_store, review, Path(args.previous_source_map).read_bytes())
        _, receipt = bind_speech(reader, json_bytes(packet), json_bytes(store))
        records.update({"speech-store": store, "occurrence-sources": source_map, "speech-binding": receipt})
    payloads = {output / (name + ".json"): json_bytes(value) for name, value in records.items()}
    if any(path.exists() and path.read_bytes() != data for path, data in payloads.items()):
        raise ValueError("the output directory already contains a different speech update")
    output.mkdir(parents=True, exist_ok=True)
    for path, data in payloads.items():
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(data)
    print(f"{len(delta['reused'])} unchanged formula contexts; {len(delta['review_required'])} occurrences require editorial review")
    return 0
