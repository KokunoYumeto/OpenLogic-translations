"""Find glossary leads in changed English prose while retaining the full decision row."""
import re


GROUPED = "grouped-english-v1"


def prose_for_matching(changed):
    # The source itself stays in the packet. Only the search copy expands OLP's term tokens.
    return re.sub(r"!!\^?a?\{([\w -]+)\}", r"\1", changed).replace("~", " ")


def grouped_labels(label):
    """Split top-level catalogue separators, leaving examples and mathematical notation intact."""
    closing = {"(": ")", "[": "]", "{": "}", '"': '"', "$": "$"}
    stack = []
    start = 0
    parts = []
    for token in re.finditer(r'\\.|[()\[\]{}"$]|;\s+|\s+/\s+', label):
        value = token.group()
        if stack and value == stack[-1]:
            stack.pop()
        elif stack and stack[-1] in ('"', '$'):
            continue
        elif value in closing:
            stack.append(closing[value])
        elif not stack and (value.startswith(";") or value.strip() == "/"):
            parts.append(label[start:token.start()].strip())
            start = token.end()
    if stack or not parts:
        return []
    return [*parts, label[start:].strip()]


def matched_labels(label, changed, prose=None):
    if not isinstance(label, str) or not label.strip():
        return []
    label = label.strip()
    def occurs(term, text):
        return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I) is not None
    if occurs(label, changed) or (prose is not None and occurs(label, prose)):
        return [label]
    if prose is None:
        return []
    return list(dict.fromkeys(part for part in grouped_labels(label) if part and occurs(part, prose)))
