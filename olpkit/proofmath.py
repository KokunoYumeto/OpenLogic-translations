"""Parse inference stacks for MathML, adapting the Gujarati proof template.

Every command is consumed in order; unknown rule or spacing operations fail
instead of being ignored by a regex search. Premises, conclusions and labels
remain editable mathematics. Unsupported line geometry is never relabelled as
an ordinary fraction.
"""
from dataclasses import dataclass, field
import re

from .macrophases import COMMAND, group, skip_space
from .selective import token


ARITIES = {'Deduce': 1, 'UnaryInf': 1, 'BinaryInf': 2, 'TrinaryInf': 3, 'QuaternaryInf': 4, 'QuinaryInf': 5}


@dataclass
class ProofNode:
    formula: str
    children: list = field(default_factory=list)
    labels: dict = field(default_factory=dict)
    line: str = 'single'
    gap: str = ''


def math_argument(text, pos):
    pos = skip_space(text, pos)
    if text[pos:pos+1] != '$': raise ValueError('expected proof math argument')
    start = pos+1
    pos = start
    while pos < len(text):
        if text[pos] == '{': _, pos = group(text, pos)
        elif text[pos] == '\\': pos = COMMAND.match(text, pos).end()
        elif text[pos] == '$': return text[start:pos], pos+1
        else: pos += 1
    raise ValueError('unclosed proof math argument')


def text_math(text, styles=None):
    """Represent a native text box without turning its words into math letters."""
    if not text.strip(): return '{}'
    text = text.strip()
    if text.startswith(r'\scriptsize'):
        if not styles or 'scriptsize' not in styles:
            raise ValueError('scriptsize proof label needs native font-size mapping')
        return '{'+styles['scriptsize']+' '+text_math(text[len(r'\scriptsize'):], styles)+'}'
    parts = []
    pos = 0
    prior = 0
    while pos < len(text):
        if text[pos] == '$':
            value, end = math_argument(text, pos)
        elif text.startswith(r'\ensuremath', pos) and not re.match('[A-Za-z@]', text[pos+11:pos+12]):
            value, end, _ = token(text, pos+11)
        else:
            pos = COMMAND.match(text, pos).end() if text[pos] == '\\' else pos+1
            continue
        if text[prior:pos]: parts.append(r'\text{'+text[prior:pos]+'}')
        parts.append('{'+value+'}')
        prior = end
        pos = end
    if text[prior:]: parts.append(r'\text{'+text[prior:]+'}')
    return ''.join(parts)


def render(node, decorate=None, styles=None):
    if not node.children: return node.formula or '{}'
    upper = (r'\qquad{}'+node.gap).join('{'+render(child, decorate, styles)+'}' for child in node.children)
    fraction = r'\dfrac{'+upper+'}{'+node.formula+'}'
    if node.line != 'single':
        if decorate is None: raise ValueError('proof line geometry needs MathML binding: '+node.line)
        fraction = decorate('proof-line-'+node.line, fraction)
    if node.labels.get('left'): fraction = text_math(node.labels['left'], styles)+r'\;'+fraction
    if node.labels.get('right'): fraction += r'\;'+text_math(node.labels['right'], styles)
    return fraction


def parse_proof(text, start=0, *, require_display=True, decorate=None, label_styles=None):
    stack = []
    pos = start
    labels = {}
    line = 'single'
    gap = ''
    bottom_align = False
    prefix = ''
    steps = []
    while True:
        pos = skip_space(text, pos)
        if pos == len(text):
            if require_display: raise ValueError('proof has no DisplayProof terminator')
            break
        match = COMMAND.match(text, pos)
        if not match: raise ValueError('unconsumed text in inference proof')
        name = match[1]
        begin = pos
        pos = match.end()
        base = name[:-1] if name.endswith('C') else name
        if name == 'DisplayProof': break
        if name in ('RightLabel', 'LeftLabel'):
            side = 'right' if name == 'RightLabel' else 'left'
            if side in labels: raise ValueError('unconsumed inference label')
            labels[side], pos, _ = token(text, pos)
            continue
        if name in ('doubleLine', 'noLine', 'singleLine'):
            line = {'doubleLine':'double', 'noLine':'none', 'singleLine':'single'}[name]
            continue
        if name == 'bottomAlignProof': bottom_align = True; continue
        if name in ('quad', 'qquad') and not stack:
            prefix += match[0]+'{}'
            continue
        if name == 'insertBetweenHyps':
            gap, pos, _ = token(text, pos)
            if not re.fullmatch(r'\\hspace\{[-+]?\d+(?:\.\d+)?em\}', gap):
                raise ValueError('unsupported insertion between proof premises')
            continue
        if base != 'Axiom' and base not in ARITIES:
            raise ValueError('unsupported inference command: '+name)
        if name.endswith('C'):
            formula, pos, _ = token(text, pos)
            formula = text_math(formula, label_styles)
        else:
            formula, pos = math_argument(text, pos)
        arity = 0 if base == 'Axiom' else ARITIES[base]
        if len(stack) < arity: raise ValueError('missing inference premises')
        children = stack[-arity:] if arity else []
        if arity: del stack[-arity:]
        node = ProofNode(formula, children, dict(labels) if arity else {},
                         'deduce' if base == 'Deduce' else line, gap if arity else '')
        stack.append(node)
        steps.append({'command': name, 'arity': arity, 'formula': formula,
                      'labels': node.labels, 'line': node.line, 'insert_between_hypotheses': node.gap,
                      'char_start': begin, 'char_end': pos})
        if arity: labels = {}; line = 'single'; gap = ''
    if len(stack) != 1: raise ValueError('inference proof does not yield one tree')
    if labels: raise ValueError('inference label has no rule')
    bound = (lambda kind, body: decorate(kind, body, start, pos)) if decorate else None
    return prefix+render(stack[0], bound, label_styles), pos, {'steps': steps, 'axioms': sum(not row['arity'] for row in steps),
                                                      'inferences': sum(bool(row['arity']) for row in steps),
                                                      'bottom_align': bottom_align}


def parse_proof_region(text, *, decorate=None, label_styles=None):
    """A prooftree environment may display several distinct adjacent trees."""
    pieces = []
    records = []
    pos = 0
    while (pos := skip_space(text, pos)) < len(text):
        match = COMMAND.match(text, pos)
        if match and match[1] in ('quad', 'qquad'):
            pieces.append(match[0]+'{}')
            pos = match.end()
            continue
        body, end, record = parse_proof(text, pos, require_display=False,
                                        decorate=decorate, label_styles=label_styles)
        if end <= pos: raise ValueError('proof region made no progress')
        pieces.append('{'+body+'}')
        records.append(record)
        pos = end
    if not records: raise ValueError('empty proof region')
    return ''.join(pieces), pos, {
        'trees': len(records), 'steps': [step for record in records for step in record['steps']],
        'axioms': sum(record['axioms'] for record in records),
        'inferences': sum(record['inferences'] for record in records),
        'bottom_align': any(record['bottom_align'] for record in records),
        'tree_records': records,
    }
