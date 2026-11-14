"""Number align/intertext rows from the book's bound native reference labels.

No counter simulation or invented numbers: an unsuppressed row needs exactly
one equation label from the same PDF/aux reconciliation used for references.
"""
import re

from .macrophases import COMMAND, group, digest
from .selective import environment_end, token
from .references import plain_number


def numbered_rows(text, references):
    if not references:
        raise ValueError('numbered intertext needs PDF-derived row numbers before splitting')
    evidence = references.get('auxiliary_evidence', {}).get('inputs', {})
    for key in ('native_pdf_sha256', 'aux_sha256', 'assembly_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', evidence.get(key, '')):
            raise ValueError('numbered intertext needs bound PDF, auxiliary and assembly hashes')
    markers = references['markers']
    rows = []
    start = pos = 0
    suppressed = []
    anchors = []

    def finish(end, separator=''):
        nonlocal start, suppressed, anchors
        original = text[start:end]
        if not original.strip():
            raise ValueError('empty numbered alignment row')
        if len(suppressed) > 1:
            raise ValueError('repeated number suppression in alignment row')
        number = key = None
        if suppressed:
            if anchors:
                raise ValueError('suppressed alignment row has a native equation anchor')
        else:
            if len(anchors) != 1:
                raise ValueError('numbered alignment row needs exactly one native equation anchor')
            anchor = anchors[0]
            native = anchor.get('native_label', {})
            if native.get('kind') != 'equation' or not native.get('destination'):
                raise ValueError('alignment anchor is not a bound native equation label')
            number, key = plain_number(native['number_tex']), anchor['key']
        rendered = original
        for a, b in reversed(suppressed):
            rendered = rendered[:a-start] + rendered[b-start:]
        rows.append({'source_tex': original, 'source_sha256': digest(original),
                     'render_tex': rendered, 'separator': separator,
                     'char_start': start, 'char_end': end,
                     'suppression_spans': [(a-start,b-start) for a,b in suppressed],
                     'number': number, 'label': key, 'suppressed': bool(suppressed)})
        suppressed, anchors = [], []

    while pos < len(text):
        if text[pos] == '{':
            value, pos = group(text, pos)
            if re.search(r'\\(?:notag|nonumber|tag)(?![A-Za-z@])|OLPXREF\d{6}', value):
                raise ValueError('grouped alignment numbering controls need explicit reconciliation')
            continue
        if text[pos] != '\\':
            pos += 1
            continue
        match = COMMAND.match(text, pos)
        at, pos, name = pos, match.end(), match[1]
        if name == 'begin':
            env, body = group(text, pos)
            _, pos = environment_end(text, body, env)
        elif name in ('notag', 'nonumber'):
            suppressed.append((at, pos))
        elif name == 'tag':
            raise ValueError('explicit alignment tags require native tag-style reconciliation')
        elif name == 'mbox':
            value, pos, _ = token(text, pos)
            if re.search(r'\\(?:notag|nonumber|tag)(?![A-Za-z@])',value):
                raise ValueError('grouped alignment numbering controls need explicit reconciliation')
            if value in markers and markers[value]['kind'] == 'anchor':
                anchors.append(markers[value])
        elif name == '\\':
            # Keep authored spacing and star flags between real rows. A final
            # separator is omitted from the converter input only, because it
            # otherwise creates a spurious empty MathML row.
            spacing = re.match(r'\*?(?:\s*\[[^\]\n]*\])?', text[pos:])
            pos += spacing.end()
            finish(at, text[at:pos])
            start = pos
    if text[start:].strip():
        finish(len(text))
    if not rows:
        raise ValueError('empty numbered alignment segment')
    rendered = ''.join(row['render_tex'] + (row['separator'] if i+1 < len(rows) else '')
                       for i, row in enumerate(rows))
    return rendered, {'rows': rows, 'native_evidence': evidence,
                      'source_sha256': digest(text), 'source_tex': text}
