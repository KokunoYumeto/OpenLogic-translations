"""Reproduce the spoken labels of an exact released reader."""
from hashlib import sha256

from lxml import html


def original_source_locators(rows, origins):
    """Preserve the HTML's links to the native edition when a TeX comment was removed."""
    if set(origins) - {r["assembled_path"] for r in rows}:
        raise ValueError("unexpected source locator outside this book")
    result = []
    for row in rows:
        source = origins.get(row["assembled_path"])
        if source:
            if row["sha256"] != source["editable_sha256"]:
                raise ValueError("editable TeX differs from its release locator")
            row = {**row, "sha256": source["native_sha256"]}
        result.append(row)
    return result


def replay_labels(reader, packet):
    digest = lambda payload: sha256(payload).hexdigest()
    if packet.get("schema") != "olpkit.released-speech.v1" or digest(reader) != packet["reader_sha256"]:
        raise ValueError("released labels belong to a different reader")
    doc = html.document_fromstring(reader, parser=html.HTMLParser(encoding="utf-8", huge_tree=True))
    if doc.get("lang") != packet["language"]:
        raise ValueError("released speech language differs")
    nodes = doc.xpath("//math")
    for node, row in zip(nodes, packet["labels"], strict=True):
        annotations = [a for a in node.iter("annotation") if a.get("encoding", "").lower()
                       in {"application/x-tex", "text/x-tex", "application/x-latex"}]
        if len(annotations) != 1 or "alttext" in node.attrib or "aria-label" in node.attrib:
            raise ValueError("expected one unlabelled annotated formula")
        formula = "".join(annotations[0].itertext())
        if digest(formula.encode()) != row["tex_sha256"] or not row["text"].strip():
            raise ValueError("released formula or speech differs")
        node.set("alttext", row["text"])
        node.set("aria-label", row["text"])
    bound = html.tostring(doc, encoding="utf-8", doctype="<!DOCTYPE html>")
    if digest(bound) != packet["bound_reader_sha256"]:
        raise ValueError("released readings differ from the accepted speech binding")
    return bound, {"schema": "olpkit.released-speech-replay.v1", "reader_sha256": digest(reader),
                   "bound_reader_sha256": digest(bound), "formula_occurrences": len(nodes),
                   "with_spoken_text": len(nodes)}
