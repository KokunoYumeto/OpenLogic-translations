"""Merge authored macro phases without Pandoc keeping an obsolete definition.

Adapted from tools/prepare_full_epub_html.py:unique_macro_preamble in
KokunoYumeto/OpenLogic-gu-Gujr-IN at 085336b59ab402c2daae25216371b9ecae08ceb7.
Language text, notation and phase priority are inputs, never inferred here.
This handles top-level newcommand/renewcommand, not arbitrary TeX execution.
"""
import hashlib
import re


# A backslash followed by an end-of-line is a TeX control-space token.
# Authored credits use it (for example after "Ms."); keep its exact source.
COMMAND = re.compile(r'\\([A-Za-z@]+|[\s\S])')
NAME = re.compile(r'\\[A-Za-z@]+')


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def mask_comments(text):
    """Keep offsets while masking comments; escaped percent signs remain live."""
    chars = list(text)
    for match in re.finditer('%', text):
        pos = match.start(); preceding = pos - 1
        while preceding >= 0 and text[preceding] == '\\': preceding -= 1
        if (pos - preceding - 1) % 2: continue
        end = text.find('\n', pos)
        if end < 0: end = len(text)
        chars[pos:end] = ' ' * (end - pos)
    return ''.join(chars)


def skip_space(text, pos):
    while pos < len(text) and text[pos].isspace(): pos += 1
    return pos


def group(text, pos, opening='{', closing='}'):
    pos = skip_space(text, pos)
    if text[pos:pos+1] != opening: raise ValueError('expected macro argument')
    start = pos + 1; depth = 1; braces = 0; pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            hit = COMMAND.match(text, pos)
            pos = hit.end() if hit else pos + 1
            continue
        char = text[pos]
        # Braces protect literal brackets inside a default argument.
        if opening == '[':
            if char == '{': braces += 1
            if char == '}':
                braces -= 1
                if braces < 0: raise ValueError('unbalanced default argument')
        if braces == 0:
            if char == opening: depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0: return text[start:pos], pos + 1
        pos += 1
    raise ValueError('unclosed macro argument')


def declarations(text):
    masked = mask_comments(text); pos = 0
    while pos < len(masked):
        if masked[pos] == '{':
            _, pos = group(masked, pos)
            continue
        if masked[pos] == '}': raise ValueError('unbalanced macro phase')
        if masked[pos] != '\\':
            pos += 1; continue
        hit = COMMAND.match(masked, pos)
        if not hit:
            pos += 1; continue
        start = pos; pos = hit.end()
        if hit[1] not in ('newcommand', 'renewcommand'): continue
        if masked[pos:pos+1] == '*': pos += 1
        pos = skip_space(masked, pos)
        if masked[pos:pos+1] == '{':
            name, pos = group(masked, pos)
            name = name.strip()
        else:
            found = NAME.match(masked, pos)
            if not found: raise ValueError('missing macro name')
            name = found[0]; pos = found.end()
        if not NAME.fullmatch(name): raise ValueError('unsupported macro name')
        pos = skip_space(masked, pos)
        if masked[pos:pos+1] == '[':
            arity, pos = group(masked, pos, '[', ']')
            if not re.fullmatch(r'[0-9]', arity.strip()): raise ValueError('invalid macro arity')
            pos = skip_space(masked, pos)
            if masked[pos:pos+1] == '[':
                if arity.strip() == '0': raise ValueError('default argument with zero arity')
                _, pos = group(masked, pos, '[', ']')
        _, pos = group(masked, pos)
        original = text[start:pos]
        emitted = re.sub(r'^\\renewcommand', lambda _: r'\newcommand', original)
        yield {'name':name, 'start':start, 'end':pos, 'source':original, 'emitted':emitted}


def merge_macro_phases(phases):
    """Return the merged preamble and exact declaration/phase provenance.

    The caller supplies ordered (phase name, source text) pairs. Later top-level
    declarations replace earlier ones. Scoped declarations and comments are
    retained but do not override a top-level definition. No files are written.
    """
    phases = list(phases)
    names = [name for name, _ in phases]
    if not names or len(names) != len(set(names)) or any(not n for n in names):
        raise ValueError('macro phases require unique nonempty names')
    pieces = []; latest = {}; history = {}; inputs = []
    for phase, text in phases:
        inputs.append({'phase':phase, 'sha256':digest(text)})
        cursor = 0
        for declaration in declarations(text):
            pieces.append((None, text[cursor:declaration['start']]))
            name = declaration['name']; latest[name] = len(pieces)
            pieces.append((name, declaration['emitted']))
            history.setdefault(name, []).append({
                'phase':phase, 'start':declaration['start'], 'end':declaration['end'],
                'source_sha256':digest(declaration['source']),
                'emitted_sha256':digest(declaration['emitted'])})
            cursor = declaration['end']
        pieces.append((None, text[cursor:]))
    merged = '\n'.join(text for i, (name, text) in enumerate(pieces)
                       if name is None or latest[name] == i)
    return merged, {'schema':'olpkit.macro-phases.v1', 'phases':inputs,
        'definitions':history, 'duplicate_names_resolved':sorted(n for n, rows in history.items() if len(rows)>1),
        'merged_sha256':digest(merged), 'arbitrary_tex_execution':False}
