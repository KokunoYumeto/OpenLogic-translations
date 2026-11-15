"""Apply the edition's explicit, source-backed orthography policy to a proposed unit."""
import json
from pathlib import Path
import re
import unicodedata

from .assembly import digest
from .schemas import validate_schema
from .structure import signature, without_comments


def inspect_orthography(text, policy):
    code = without_comments(text)
    findings = []
    for rule in (policy or {}).get("rules", []):
        name = "orthography:" + rule["id"]
        if rule["kind"] == "nfc":
            if not unicodedata.is_normalized("NFC", code):
                findings.append((name, "NFC", "non-NFC text"))
        elif rule["kind"] == "forbidden_literal":
            hits = [{"line": code.count("\n", 0, m.start()) + 1, "text": m.group()}
                    for m in re.finditer(re.escape(rule["literal"]), code)]
            if hits:
                findings.append((name, [], hits))
    return findings


def normalize_unit(raw, policy):
    """Canonical composition is allowed only when explicitly required by this edition."""
    validate_schema("orthography", policy)
    text = raw.decode("utf-8")
    if not policy["rules"]:
        raise ValueError("edition has no orthography rules")
    if len({rule["id"] for rule in policy["rules"]}) != len(policy["rules"]):
        raise ValueError("duplicate orthography rule identifier")
    if any(rule["kind"] == "nfc" for rule in policy["rules"]):
        result = []
        for line in text.splitlines(keepends=True):
            # Leave comments and their line endings byte-for-byte intact.
            cut = len(line)
            for match in re.finditer("%", line):
                prefix = line[:match.start()]
                if (len(prefix) - len(prefix.rstrip("\\"))) % 2 == 0:
                    cut = match.start()
                    break
            result.append(unicodedata.normalize("NFC", line[:cut]) + line[cut:])
        normalized = "".join(result)
    else:
        normalized = text
    if text != normalized and signature(text) != signature(normalized):
        raise ValueError("normalization changes a structural identifier or reference")
    remaining = inspect_orthography(normalized, policy)
    if remaining:
        raise ValueError("edition forbids this form and supplies no automatic correction: "
                         + ", ".join(rule for rule, _, _ in remaining))
    return normalized.encode("utf-8")


def normalize_command(source, policy_path, out=None):
    raw = Path(source).read_bytes()
    policy_bytes = Path(policy_path).read_bytes()
    normalized = normalize_unit(raw, json.loads(policy_bytes.decode("utf-8-sig")))
    if out is not None:
        output = Path(out)
        if output.resolve() == Path(source).resolve():
            raise ValueError("write the proposal to a separate output file")
        if output.exists():
            if output.read_bytes() != normalized:
                raise ValueError("output already contains a different proposal")
        else:
            with output.open("xb") as stream:
                stream.write(normalized)
    print(json.dumps({"source_sha256": digest(raw), "normalized_sha256": digest(normalized),
                      "policy_sha256": digest(policy_bytes), "changed": raw != normalized}))
    return int(out is None and raw != normalized)

