"""Balanced display adaptation for the recovered Gujarati/Pandoc route.

The intertext and nested text/math operations derive from that producer's
math_preprocess. No language literals or guessed reference numbers are used.
Unsupported diagrams, references and table layout remain explicit failures.
Markers preserve exact input TeX when a MathML layout repair is necessary.
"""
import re
from decimal import Decimal

from .macrophases import COMMAND, digest, group, mask_comments
from .selective import definition_end, environment_end, token
from .proofmath import parse_proof, parse_proof_region
from .tabular import parse_tabular, bind_tables
from .alignmentnumbers import numbered_rows


PREFIX = 'OLPDISPLAY'
MARKER = re.compile(r'\\overset\{\\text\{(OLPDISPLAY\d{6})\}\}')
DOUBLE_BAR = re.compile(r'\\mathrel\s*\{\|\|\}\s*\\joinrel\s*\\Relbar(?![A-Za-z@])')
PARTIAL_ARROW = r'\ooalign{\hfil$\mapstochar\mkern5mu$\hfil\cr$\to$}'
MATH_ENVS = re.compile(r'(?:equation|align|alignat|gather|multline|displaymath|math)\*?')
OPAQUE = {'verbatim', 'Verbatim', 'lstlisting', 'minted', 'tikzpicture'}


class DisplayAdapter:
    def __init__(self, *, proof_label_styles=None, math_font_sizes=None, native_references=None):
        self.markers = {}
        self.events = []
        self.tables = []
        self.proof_label_styles = proof_label_styles or {}
        self.math_font_sizes = math_font_sizes or {}
        self.native_references = native_references

    def alignment_part(self, text, *, numbered, offset):
        if not numbered:
            return r'\begin{align*}'+self.walk(text,math=True,offset=offset)+r'\end{align*}'
        _, record = numbered_rows(text, self.native_references)
        # Adapt each original row separately so nested annotation offsets still
        # refer to the unmodified source, even after removing number controls.
        pieces=[]
        for i,row in enumerate(record['rows']):
            original=row['source_tex']
            # Whitespace masking preserves offsets for all nested decorations.
            masked=original
            for a,b in reversed(row['suppression_spans']):
                masked=masked[:a]+''.join('\n' if c=='\n' else ' ' for c in masked[a:b])+masked[b:]
            pieces.append(self.walk(masked,math=True,offset=offset+row['char_start']))
            if i+1<len(record['rows']):pieces.append(row['separator'])
        rendered=r'\begin{aligned}'+''.join(pieces)+r'\end{aligned}'
        marked=self.mark('numbered-alignment',rendered,text,offset,offset+len(text))
        self.markers[PREFIX+str(len(self.markers)-1).zfill(6)]['alignment']=record
        return r'\['+marked+r'\]'

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
                if env == 'oltableau':
                    raise ValueError('native OLP tableau requires a complete tree renderer; Pandoc would silently omit it')
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
                        cursor = 0
                        records = []
                        for a, b, at, prose, command in chunks:
                            if command != 'intertext':
                                raise ValueError('shortintertext spacing needs explicit support')
                            before = body[cursor:a]
                            if before.strip():
                                out.append(self.alignment_part(before,numbered=env=='align',offset=offset+body_start+cursor))
                            out.extend(('\n\n', self.walk(prose, math=False, offset=offset+body_start+at), '\n\n'))
                            records.append({'prose': prose, 'char_start': offset+body_start+at,
                                            'char_end': offset+body_start+at+len(prose)})
                            cursor = b
                        after = body[cursor:]
                        if after.strip():
                            out.append(self.alignment_part(after,numbered=env=='align',offset=offset+body_start+cursor))
                        self.events.append({'kind': 'intertext', 'char_start': offset+start,
                                            'char_end': offset+end, 'original_sha256': digest(text[start:end]),
                                            'original_tex': text[start:end], 'numbered':env=='align',
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
            if name == '[':
                table_start = re.match(r'\s*\\centering\s*(?=\\begin\{tabular\})',text[pos:])
                if table_start:
                    at=pos+table_start.end()
                    _, table_body=group(text,at+len(r'\begin'))
                    _,end=environment_end(text,table_body,'tabular')
                    closing=re.match(r'\s*\\\]',text[end:])
                    if not closing: raise ValueError('other content in display table')
                    normalized,record=parse_tabular(text[at:end])
                    marker='OLPSOURCETABLE'+str(len(self.tables)).zfill(6)
                    record.update({'marker':marker,'char_start':offset+start,'char_end':offset+end+closing.end()})
                    self.tables.append(record)
                    out.extend(('\n\n',marker+'START\n\n',normalized,'\n\n'+marker+'END\n\n'))
                    pos=end+closing.end();continue
            if name in ('[', '('): math = True; out.append(match[0]); continue
            if name in (']', ')'): math = False; out.append(match[0]); continue
            if name == 'ensuremath':
                value, end, at = token(text, pos)
                # The argument enters math mode even in a prose/list label.
                # Keep that mode local, just as TeX does, and retain its wrapper.
                out.extend((r'\ensuremath{', self.walk(value, math=True, offset=offset+at), '}'))
                pos = end
                continue
            if math and name == 'setlength':
                register,p=group(text,pos);length,p=group(text,p)
                opening=re.match(r'\s*\\begin\s*\{array\}',text[p:])
                if register==r'\arraycolsep' and opening:
                    dimension=re.fullmatch(r'\s*(\d+(?:\.\d+)?)pt\s*',length)
                    if not dimension:raise ValueError('array spacing requires an explicit point length')
                    columns,body_start=group(text,p+opening.end())
                    trimmed=re.fullmatch(r'@\{\}([clr\s]+)@\{\}',columns)
                    if not trimmed:raise ValueError('unsupported spaced-array column specification')
                    stop,end=environment_end(text,body_start,'array')
                    if not re.match(r'\s*(?:\\\]|\$|\})',text[end:]):
                        raise ValueError('array spacing continues beyond the supported array scope')
                    body=self.walk(text[body_start:stop],math=True,offset=offset+body_start)
                    body=re.sub(r'\\\\\s*$','',body,count=1)
                    rendered=r'\begin{array}{'+trimmed[1]+'}'+body+r'\end{array}'
                    out.append(self.mark('spaced-array',rendered,text[start:end],offset+start,offset+end))
                    # CSS/MathML pt is 1/72 inch; TeX pt is 1/72.27 inch.
                    width=Decimal(dimension[1])*2*Decimal(72)/Decimal('72.27')
                    self.markers[PREFIX+str(len(self.markers)-1).zfill(6)]['columnspacing']=format(width.quantize(Decimal('.000001')),'f')+'pt'
                    pos=end;continue
            if math and name == 'hbox':
                width=re.match(r'\s*to\s*((?:\d+(?:\.\d*)?|\.\d+)(?:em|ex|pt))\s*',text[pos:])
                if width:
                    body,end,at=token(text,pos+width.end())
                    content=re.fullmatch(r'(\s*\\ensuremath[\s\S]+?)\\hfil\s*',body)
                    if not content:raise ValueError('fixed-width math box needs known left-aligned mathematical content')
                    rendered=self.walk(content[1],math=True,offset=offset+at)
                    out.append(self.mark('fixed-width-math',rendered,text[start:end],offset+start,offset+end))
                    self.markers[PREFIX+str(len(self.markers)-1).zfill(6)]['width']=width[1]
                    pos=end;continue
            if math and name == 'small':
                opening = re.match(r'\s*\\begin\s*\{array\}', text[pos:])
                if opening:
                    if 'small' not in self.math_font_sizes:
                        raise ValueError('small-array font size requires native edition data')
                    columns, body_start = group(text, pos+opening.end())
                    trimmed = re.fullmatch(r'@\{\}([clr\s]+)@\{\}', columns)
                    if not trimmed: raise ValueError('unsupported small-array column specification')
                    stop, end = environment_end(text, body_start, 'array')
                    if not re.match(r'\s*(?:\\\]|\$|\})',text[end:]):
                        raise ValueError('small size continues beyond the supported array scope')
                    body = self.walk(text[body_start:stop], math=True, offset=offset+body_start)
                    # Pandoc treats a terminal row delimiter as another empty
                    # row, unlike TeX. Remove that delimiter only; intentional
                    # empty rows between delimiters remain in their positions.
                    body = re.sub(r'\\\\\s*$', '', body, count=1)
                    rendered = r'\begin{array}{'+trimmed[1]+'}'+body+r'\end{array}'
                    out.append(self.mark('small-array', rendered, text[start:end], offset+start, offset+end))
                    self.markers[PREFIX+str(len(self.markers)-1).zfill(6)]['mathsize'] = self.math_font_sizes['small']
                    pos = end
                    continue
            if math and name == 'mathrel':
                value, end, _ = token(text, pos)
                if re.sub(r'\s+', '', value) == PARTIAL_ARROW:
                    # U+21F8 has the source's vertical stroke in the arrow shaft,
                    # unlike mapsto (a bar at the tail). Keep the original TeX.
                    out.append(self.mark('partial-function-arrow', r'\to', text[start:end], offset+start, offset+end))
                    pos = end
                    continue
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
                    if value[prior:opening]:
                        prose=value[prior:opening]
                        # TeX's italic-correction command is a font-engine
                        # operation at this text/math boundary, not prose.
                        # Keep it in the original annotation, and let the web
                        # font engine space the text and following math glyph.
                        prose=re.sub(r'\\/\s*$',lambda m:m[0][2:],prose)
                        pieces.append('\\'+name+'{'+prose+'}')
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
        if PREFIX in text or 'OLPSOURCETABLE' in text: raise ValueError('reserved display marker in source')
        if self.markers or self.events or self.tables: raise ValueError('use a fresh adapter per document')
        output = self.walk(mask_comments(text))
        return output, {'schema': 'olpkit.math-display.v1', 'source': source,
                        'input_sha256': digest(text), 'output_sha256': digest(output),
                        'proof_label_styles': self.proof_label_styles,
                        'math_font_sizes': self.math_font_sizes,
                        'tables': self.tables,
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
        elif kind == 'partial-function-arrow':
            base = element(node, 'mo', '\u21f8', stretchy='false', lspace='0.277778em', rspace='0.277778em')
        elif kind == 'small-array':
            if local(base) != 'mtable': raise ValueError('small array did not render as a table')
            styled = element(node, 'mstyle', mathsize=markers[key]['mathsize'])
            styled.append(base)
            base = styled
        elif kind == 'spaced-array':
            if local(base)!='mtable':raise ValueError('spaced array did not render as a table')
            base.set('columnspacing',markers[key]['columnspacing'])
        elif kind == 'fixed-width-math':
            padded=element(node,'mpadded',width=markers[key]['width'],lspace='0em')
            padded.append(base);base=padded
        elif kind == 'numbered-alignment':
            rows=markers[key]['alignment']['rows']
            if local(base)!='mtable' or len(base)!=len(rows) or any(local(r)!='mtr' for r in base):
                raise ValueError('native numbered alignment rows differ after MathML conversion')
            base.set('data-native-numbering','true')
            for node_row,source_row in zip(base,rows):
                cell=element(node_row,'mtd',columnalign='right')
                if source_row['number'] is not None:
                    cell.set('data-equation-label',source_row['label'])
                    cell.append(element(cell,'mtext','('+source_row['number']+')'))
                node_row.append(cell)
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
    tables=bind_tables(document,receipt.get('tables',[]))
    numbers=[{'label':r['label'],'number':r['number']}
             for m in markers.values() if m['kind']=='numbered-alignment'
             for r in m['alignment']['rows'] if r['number'] is not None]
    return {'bound': len(bound), 'unbound': unbound, 'tables':tables,
            'native_equation_numbers':numbers,'reader_complete': False}
