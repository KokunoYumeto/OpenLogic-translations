"""Balanced display adaptation for the recovered Gujarati/Pandoc route.

The intertext and nested text/math operations derive from that producer's
math_preprocess. No language literals or guessed reference numbers are used.
Unsupported diagrams, references and table layout remain explicit failures.
Markers preserve exact input TeX when a MathML layout repair is necessary.
"""
import re

from .macrophases import COMMAND, digest, group, mask_comments
from .selective import definition_end, environment_end, token
from .proofmath import parse_proof, parse_proof_region


PREFIX = 'OLPDISPLAY'
MARKER = re.compile(r'\\overset\{\\text\{(OLPDISPLAY\d{6})\}\}')
DOUBLE_BAR = re.compile(r'\\mathrel\s*\{\|\|\}\s*\\joinrel\s*\\Relbar(?![A-Za-z@])')
MATH_ENVS = re.compile(r'(?:equation|align|alignat|gather|multline|displaymath|math)\*?')
OPAQUE = {'verbatim', 'Verbatim', 'lstlisting', 'minted', 'tikzpicture'}


class DisplayAdapter:
    def __init__(self, *, proof_label_styles=None):
        self.markers = {}
        self.events = []
        self.proof_label_styles = proof_label_styles or {}

    def mark(self, kind, body, original, start, end):
        key = PREFIX + str(len(self.markers)).zfill(6)
        self.markers[key] = {'kind': kind, 'original_tex': original,
                             'char_start': start, 'char_end': end}
        return r'\overset{\text{' + key + '}}{' + body + '}'

    @staticmethod
    def intertexts(text):
        """Locate executed top-level intertext, never a nested macro body."""
        pos = 0
        while pos < len(text):
            if text[pos] == '{':
                _, pos = group(text, pos)
                continue
            if text[pos] != '\\':
                pos += 1
                continue
            match = COMMAND.match(text, pos)
            start = pos
            pos = match.end()
            end = definition_end(text, start, pos, match[1])
            if end is not None:
                pos = end
            elif match[1] == 'begin':
                env, pos = group(text, pos)
                _, pos = environment_end(text, pos, env)
            elif match[1] in ('intertext', 'shortintertext'):
                value, end, at = token(text, pos)
                yield start, end, at, value, match[1]
                pos = end

    def walk(self, text, *, math=False, offset=0):
        out = []
        pos = 0
        while pos < len(text):
            start = pos
            if text[pos] == '{':
                value, end = group(text, pos)
                out.extend(('{', self.walk(value, math=math, offset=offset+pos+1), '}'))
                pos = end
                continue
            if text[pos] == '$':
                delimiter = '$$' if text[pos:pos+2] == '$$' else '$'
                math = not math
                out.append(delimiter)
                pos += len(delimiter)
                continue
            if text[pos] != '\\':
                out.append(text[pos])
                pos += 1
                continue
            match = COMMAND.match(text, pos)
            name = match[1]
            pos = match.end()
            end = definition_end(text, start, pos, name)
            if end is not None:
                out.append(text[start:end])
                pos = end
                continue
            if name in ('verb', 'Verb'):
                if text[pos:pos+1] == '*': pos += 1
                delimiter = text[pos:pos+1]
                end = text.find(delimiter, pos+1) if delimiter else -1
                if end < 0: raise ValueError('unclosed display-stage verbatim')
                out.append(text[start:end+1])
                pos = end+1
                continue
            if name == 'begin':
                env, body_start = group(text, pos)
                stop, end = environment_end(text, body_start, env)
                if env == 'prooftree':
                    inner = text[body_start:stop]
                    body, used, proof = parse_proof_region(inner,
                        label_styles=self.proof_label_styles,
                        decorate=lambda kind, body, a, b: self.mark(kind, body, inner[a:b], offset+body_start+a, offset+body_start+b))
                    if text[body_start+used:stop].strip(): raise ValueError('unconsumed prooftree body')
                    marked = self.mark('inference-proof', body, text[start:end], offset+start, offset+end)
                    out.append(marked if math else r'\['+marked+r'\]')
                    self.events.append({'kind': 'inference-proof', 'char_start': offset+start,
                                        'char_end': offset+end, **proof})
                elif env in OPAQUE:
                    out.append(text[start:end])
                else:
                    body = text[body_start:stop]
                    chunks = list(self.intertexts(body)) if env in ('align', 'align*') else []
                    if chunks:
                        if env != 'align*':
                            raise ValueError('numbered intertext needs PDF-derived row numbers before splitting')
                        cursor = 0
                        records = []
                        for a, b, at, prose, command in chunks:
                            if command != 'intertext':
                                raise ValueError('shortintertext spacing needs explicit support')
                            before = body[cursor:a]
                            if before.strip():
                                out.extend((r'\begin{align*}', self.walk(before, math=True, offset=offset+body_start+cursor), r'\end{align*}'))
                            out.extend(('\n\n', self.walk(prose, math=False, offset=offset+body_start+at), '\n\n'))
                            records.append({'prose': prose, 'char_start': offset+body_start+at,
                                            'char_end': offset+body_start+at+len(prose)})
                            cursor = b
                        after = body[cursor:]
                        if after.strip():
                            out.extend((r'\begin{align*}', self.walk(after, math=True, offset=offset+body_start+cursor), r'\end{align*}'))
                        self.events.append({'kind': 'intertext', 'char_start': offset+start,
                                            'char_end': offset+end, 'original_sha256': digest(text[start:end]),
                                            'prose_segments': records})
                    else:
                        out.extend((text[start:body_start], self.walk(body, math=math or bool(MATH_ENVS.fullmatch(env)), offset=offset+body_start), text[stop:end]))
                pos = end
                continue
            if name in ('Axiom', 'AxiomC'):
                body, end, proof = parse_proof(text, start, label_styles=self.proof_label_styles,
                    decorate=lambda kind, body, a, b: self.mark(kind, body, text[a:b], offset+a, offset+b))
                # The proof renderer emits only standard math and text commands.
                # Its exact source is retained by the outer annotation marker.
                marked = self.mark('inference-proof', body, text[start:end], offset+start, offset+end)
                out.append(marked if math else r'\['+marked+r'\]')
                self.events.append({'kind': 'inference-proof', 'char_start': offset+start,
                                    'char_end': offset+end, **proof})
                pos = end
                continue
            if name in ('[', '('): math = True; out.append(match[0]); continue
            if name in (']', ')'): math = False; out.append(match[0]); continue
            if name in ('text', 'mbox', 'textrm') and math:
                value, end, at = token(text, pos)
                pieces = []
                prior = 0
                i = 0
                while i < len(value):
                    if value[i] == '\\':
                        i = COMMAND.match(value, i).end()
                        continue
                    if value[i] != '$':
                        i += 1
                        continue
                    opening = i
                    i += 1
                    while i < len(value) and value[i] != '$':
                        i = COMMAND.match(value, i).end() if value[i] == '\\' else i+1
                    if i == len(value): raise ValueError('unclosed nested inline math')
                    if value[prior:opening]: pieces.append('\\'+name+'{'+value[prior:opening]+'}')
                    # Braces keep scripts on the nested math from binding to preceding text.
                    pieces.append('{'+self.walk(value[opening+1:i], math=True, offset=offset+at+opening+1)+'}')
                    prior = i+1
                    i += 1
                if pieces:
                    if value[prior:]: pieces.append('\\'+name+'{'+value[prior:]+'}')
                    out.append(self.mark('nested-text-math', ''.join(pieces), text[start:end], offset+start, offset+end))
                    self.events.append({'kind': 'nested-text-math', 'char_start': offset+start,
                                        'char_end': offset+end, 'original_tex': text[start:end]})
                else:
                    out.append(text[start:end])
                pos = end
                continue
            if math and name == 'mathrel' and (compound := DOUBLE_BAR.match(text, start)):
                end = compound.end()
                out.append(self.mark('double-bar-turnstile', r'\mathrel{||=}', text[start:end], offset+start, offset+end))
                pos = end
                continue
            if math and name == 'mathexclaim':
                out.append(self.mark('ordinary-exclamation', r'\mathord{!}', match[0], offset+start, offset+pos))
                continue
            if math and name in ('nicefrac', 'shoveleft', 'shoveright'):
                first, end, at = token(text, pos)
                body = self.walk(first, math=True, offset=offset+at)
                if name == 'nicefrac':
                    second, end, at = token(text, end)
                    body = r'\frac{'+body+'}{'+self.walk(second, math=True, offset=offset+at)+'}'
                out.append(self.mark(name, body, text[start:end], offset+start, offset+end))
                pos = end
                continue
            out.append(match[0])
        return ''.join(out)

    def prepare(self, text, source):
        if PREFIX in text: raise ValueError('reserved display marker in source')
        if self.markers or self.events: raise ValueError('use a fresh adapter per document')
        output = self.walk(mask_comments(text))
        return output, {'schema': 'olpkit.math-display.v1', 'source': source,
                        'input_sha256': digest(text), 'output_sha256': digest(output),
                        'proof_label_styles': self.proof_label_styles,
                        'markers': self.markers, 'events': self.events,
                        'reader_complete': False}


def restore_annotations(text, markers):
    parts = []
    pos = 0
    while match := MARKER.search(text, pos):
        _, end = group(text, match.end())
        parts.extend((text[pos:match.start()], markers[match[1]]['original_tex']))
        pos = end
    parts.append(text[pos:])
    return ''.join(parts)


def bind_mathml(document, receipt, *, strict=True):
    """Bind only recognized rendered markers; missing markers fail acceptance.

    Non-strict mode is exclusively for diagnostic probes with other unresolved
    math. It reports every unbound marker and never marks the reader complete.
    """
    from lxml import etree

    markers = receipt['markers']
    bound = []
    def local(node): return node.tag.rsplit('}', 1)[-1] if isinstance(node.tag, str) else ''
    def element(parent, name, text=None, **attrs):
        namespace = parent.tag.rsplit('}', 1)[0]+'}' if '}' in parent.tag else ''
        child = etree.Element(namespace+name, attrs)
        child.text = text
        return child

    for node in reversed(list(document.iter())):
        if local(node) != 'mover' or len(node) != 2: continue
        key = ''.join(node[1].itertext()).strip()
        if key not in markers: continue
        if key in bound: raise ValueError('duplicate rendered display marker: '+key)
        kind = markers[key]['kind']
        base = node[0]
        if kind == 'nicefrac':
            candidates = [item for item in base.iter() if local(item) == 'mfrac']
            if local(base) != 'mfrac' or not candidates:
                raise ValueError('fraction marker did not render as a fraction')
            base.set('bevelled', 'true')
        elif kind in ('shoveleft', 'shoveright'):
            cell = node.getparent()
            while cell is not None and local(cell) != 'mtd': cell = cell.getparent()
            if cell is None: raise ValueError('shove marker has no alignment cell')
            if len(cell.getparent()) != 1: raise ValueError('shove marker is not in a single-column multline row')
            cell.set('columnalign', 'left' if kind == 'shoveleft' else 'right')
        elif kind == 'double-bar-turnstile':
            base = element(node, 'mrow')
            base.append(element(node, 'mo', '||', stretchy='false', lspace='0.277778em', rspace='0em'))
            base.append(element(node, 'mspace', width='-0.166667em'))
            base.append(element(node, 'mo', '=', stretchy='false', lspace='0em', rspace='0.277778em'))
        elif kind.startswith('proof-line-'):
            fraction = next((item for item in base.iter() if local(item) == 'mfrac'), None)
            if fraction is None or len(fraction) != 2: raise ValueError('proof rule has no fraction structure')
            style = kind.removeprefix('proof-line-')
            if style == 'none':
                fraction.set('linethickness', '0')
            elif style in ('double', 'deduce'):
                table = element(node, 'mtable', columnspacing='0em', rowspacing='0.1em', columnalign='center')
                if style == 'double': table.set('rowlines', 'solid solid')
                middle = element(node, 'mo', '⋮') if style == 'deduce' else element(node, 'mspace', height='0.1em', width='0em')
                for cell_content in (fraction[0], middle, fraction[1]):
                    row = element(node, 'mtr'); cell = element(node, 'mtd')
                    cell.append(cell_content); row.append(cell); table.append(row)
                parent = fraction.getparent()
                if fraction is base: base = table
                else: parent.replace(fraction, table)
            else: raise ValueError('unsupported proof line: '+style)
        elif kind not in ('ordinary-exclamation', 'nested-text-math', 'inference-proof'):
            raise ValueError('unknown display marker kind: '+kind)
        base.tail = node.tail
        node.getparent().replace(node, base)
        bound.append(key)
    for node in document.iter():
        if local(node) == 'annotation' and node.get('encoding') == 'application/x-tex':
            node.text = restore_annotations(node.text or '', markers)
    unbound = sorted(set(markers)-set(bound))
    if strict and unbound: raise ValueError('unconverted display markers: '+', '.join(unbound))
    return {'bound': len(bound), 'unbound': unbound, 'reader_complete': False}
