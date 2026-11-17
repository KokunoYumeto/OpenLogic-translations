"""Replay historical canon citations against exact source and translation bytes."""
import hashlib
import json
import re


def _records(body):
    return [json.loads(line) for line in body.decode("utf-8-sig").splitlines() if line.strip()]


def segment_index(segments, passages, sources):
    source_rows = _records(sources)
    source_ids = {row["source_id"] for row in source_rows}
    passage_rows = _records(passages)
    passage_ids = {row["passage_id"] for row in passage_rows}
    if len(source_ids) != len(source_rows) or len(passage_ids) != len(passage_rows):
        raise ValueError("Duplicate bibliographic source or passage ID")
    if any(row["source_id"] not in source_ids for row in passage_rows):
        raise ValueError("Canon passage cites an unknown source")
    by_unit = {}
    for number, row in enumerate(_records(segments), 1):
        unit = row["unit"]
        if (not row["segment"].startswith(unit + "-") or row["scope"] not in ("unit", "passage")
                or not row["passages"] or not set(row["passages"]) <= passage_ids):
            raise ValueError(f"Invalid segment or canon reference at record {number}")
        for side in ("source", "target"):
            start, end = row[side]["bytes"]
            if (type(start) is not int or type(end) is not int or not 0 <= start < end
                    or not re.fullmatch(r"[a-f0-9]{64}", row[side]["sha256"])):
                raise ValueError(f"Invalid {side} byte span at record {number}")
        by_unit.setdefault(unit, []).append((number, row))
    return by_unit


def compare_canon_spans(records, source, target):
    results = []
    for number, row in records:
        result = {"record": number, "segment": row["segment"], "scope": row["scope"],
                  "passages": row["passages"]}
        entire = True
        for side, body in (("source", source), ("target", target)):
            span = row[side]
            start, end = span["bytes"]
            matches = (body is not None and end <= len(body)
                       and hashlib.sha256(body[start:end]).hexdigest() == span["sha256"])
            result[side + "_matches"] = matches
            entire = entire and matches and start == 0 and end == len(body)
        if row["scope"] == "unit":
            result["covers_current_unit"] = entire
        results.append(result)
    return results
