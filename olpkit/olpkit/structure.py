"""Inspect explicit TeX structure without expanding or changing its prose.

This is a source lint, not a TeX interpreter or semantic certification. Literal
macro arguments are compared; justified differences belong in an exception ledger.
"""
import re

COMMAND = re.compile(r"\\([A-Za-z@]+)(\*?)")


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
    text = without_comments(text)
    result = {key: [] for key in ['identifiers', 'imports', 'labels', 'environments', 'citations', 'references', 'tags']}
    result['footnotes'] = 0
    for match in COMMAND.finditer(text):
        name, star = match.groups()
        wanted = name in {'olfileid', 'olchapterid', 'olpartid', 'olimport', 'subfile', 'ollabel', 'label', 'begin', 'end', 'footnote', 'footnotetext', 'iftag', 'tagtrue', 'tagfalse'} or name.startswith('cite') or name in {'olref', 'ref', 'eqref', 'autoref', 'cref', 'Cref', 'pageref'}
        if not wanted:
            continue
        pos = match.end()
        opts, args = [], []
        while pos < len(text):
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos == len(text) or text[pos] not in '[{':
                break
            opening = text[pos]
            value, pos = argument(text, pos, opening, ']' if opening == '[' else '}')
            (opts if opening == '[' else args).append(value)
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
