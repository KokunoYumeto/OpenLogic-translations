"""Inspect explicit TeX structure without expanding or changing its prose.

This is a source lint, not a TeX interpreter or semantic certification. Literal
macro arguments are compared; justified differences belong in an exception ledger.
"""
import re

COMMAND = re.compile(r"\\([A-Za-z@]+)(\*?)")


TEX_TOKEN = re.compile(r"%[^\r\n]*|\\(?:[A-Za-z@]+|[^\r\n])")
IDENTIFIER_ARITY = {"olfileid": 3, "olchapterid": 2, "olpartid": 1}
TRIVIA = re.compile(r"(?:\s+|%[^\r\n]*)*")


def active_tex(text):
    """Mask comments and quoted TeX tokens, keeping offsets and line endings."""
    parts = []
    kept = pos = 0
    while match := TEX_TOKEN.search(text, pos):
        token = match[0]
        pos = match.end()
        if token == r"\string":
            pos = TRIVIA.match(text, pos).end()
            operand = TEX_TOKEN.match(text, pos)
            pos = operand.end() if operand else min(pos + 1, len(text))
        elif token == r"\verb" and pos < len(text):
            if text[pos] == "*":
                pos += 1
            if pos >= len(text) or text[pos].isspace():
                continue
            close = text.find(text[pos], pos + 1)
            if close < 0 or "\n" in text[pos:close] or "\r" in text[pos:close]:
                continue
            pos = close + 1
        elif not token.startswith("%") and token != r"\\":
            continue
        parts.append(text[kept:match.start()])
        parts.append(re.sub(r"[^\r\n]", " ", text[match.start():pos]))
        kept = pos
    parts.append(text[kept:])
    return "".join(parts)


def without_comments(text):
    out = []
    for line in text.splitlines(keepends=True):
        cut = len(line)
        for match in re.finditer('%', line):
            before = line[:match.start()]
            backslashes = len(before) - len(before.rstrip('\\'))
            if backslashes % 2 == 0:
                cut = match.start()
                break
        out.append(line[:cut] + ('\n' if cut < len(line) else ''))
    return ''.join(out)


def argument(text, pos, opening, closing):
    depth = 1
    start = pos + 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
            if depth == 0:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError(f'unclosed {opening} argument at offset {start - 1}')


def signature(text):
    code = active_tex(text)
    result = {key: [] for key in ['identifiers', 'imports', 'labels', 'environments', 'citations', 'references', 'tags']}
    result['footnotes'] = 0
    for match in COMMAND.finditer(code):
        name, star = match.groups()
        wanted = name in {'olfileid', 'olchapterid', 'olpartid', 'olimport', 'subfile', 'ollabel', 'label', 'begin', 'end', 'footnote', 'footnotetext', 'iftag', 'tagtrue', 'tagfalse'} or name.startswith('cite') or name in {'olref', 'ref', 'eqref', 'autoref', 'cref', 'Cref', 'pageref'}
        if not wanted:
            continue
        pos = match.end()
        opts, args = [], []
        while pos < len(text):
            while pos < len(code) and code[pos].isspace():
                pos += 1
            if pos == len(text) or text[pos] not in '[{':
                break
            opening = text[pos]
            start = pos + 1
            _, pos = argument(code, pos, opening, ']' if opening == '[' else '}')
            value = without_comments(text[start:pos-1])
            (opts if opening == '[' else args).append(value)
            if name in IDENTIFIER_ARITY and len(args) == IDENTIFIER_ARITY[name]:
                break
        if name in {'olfileid', 'olchapterid', 'olpartid'}:
            result['identifiers'].append([name, args])
        elif name in {'olimport', 'subfile'}:
            result['imports'].append([name + star, opts, args[:1]])
        elif name in {'ollabel', 'label'}:
            result['labels'].append([name, args[:1]])
        elif name in {'begin', 'end'}:
            result['environments'].append([name, args[:1]])
        elif name.startswith('cite'):
            result['citations'].extend(k.strip() for a in args[:1] for k in a.split(','))
        elif name in {'olref', 'ref', 'eqref', 'autoref', 'cref', 'Cref', 'pageref'}:
            result['references'].append([name + star, opts, args[:1]])
        elif name in {'iftag', 'tagtrue', 'tagfalse'}:
            result['tags'].append([name, args[:1]])
        else:
            result['footnotes'] += 1
    return result


def differences(english, translation):
    first, second = signature(english), signature(translation)
    return [{'rule': key, 'english': first[key], 'translation': second[key]} for key in first if first[key] != second[key]]
