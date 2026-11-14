"""Project native OLP tag choices without translating or expanding mathematics.

Adapted from the Persian full_export.py:select_tags implementation recovered at
corpus/epub-production-full-20260912. Semantics follow open-logic-selective.sty:
imports execute in stream order, assignments respect scopes, and tagprob only
suppresses prob environments. This is not an arbitrary TeX interpreter.
"""
from dataclasses import dataclass, field
import hashlib
import re

from .macrophases import COMMAND, group, mask_comments, skip_space


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def token(text, pos):
    before = pos
    pos = skip_space(text, pos)
    # TeX turns an empty line into a paragraph token. It is a valid argument
    # to OLP's long macros, not whitespace to skip past into the next command.
    paragraph = re.search(r'\n[ \t\r]*\n', text[before:pos])
    if paragraph:
        return r'\par', before + paragraph.end(), before + paragraph.start()
    if pos >= len(text):
        raise ValueError('missing TeX argument')
    if text[pos] == '{':
        value, end = group(text, pos)
        return value, end, pos + 1
    found = COMMAND.match(text, pos)
    end = found.end() if found else pos + 1
    return text[pos:end], end, pos


def names(value):
    result = [s.strip() for s in value.split(',') if s.strip()]
    if not result or any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9@_-]*', s) for s in result):
        raise ValueError('unsupported or empty tag list: ' + value)
    return result


@dataclass
class SelectionState:
    tags: dict = field(default_factory=dict)
    excluded: set = field(default_factory=set)
    item_enabled: bool = True
    problem_enabled: bool = True
    context: dict = field(default_factory=dict)

    def copy(self):
        return SelectionState(dict(self.tags), set(self.excluded), self.item_enabled, self.problem_enabled,
                              dict(self.context))

    def values(self, value):
        keys = names(value)
        missing = [n for n in keys if n not in self.tags]
        if missing:
            raise ValueError('unknown OLP tags: ' + ', '.join(missing))
        return [self.tags[n] for n in keys]


def definition_end(text, start, command_end, name):
    """Keep macro bodies opaque: a definition is not an executed tag choice."""
    pos = skip_space(text, command_end)
    if text[pos:pos+1] == '*':
        pos = skip_space(text, pos + 1)
    if name in ('def', 'gdef', 'edef', 'xdef'):
        _, pos, _ = token(text, pos)
        while pos < len(text) and text[pos] != '{':
            pos += 1
        _, pos = group(text, pos)
        return pos
    if name in ('newcommand', 'renewcommand', 'providecommand', 'DeclareRobustCommand',
                'newenvironment', 'renewenvironment', 'provideenvironment'):
        _, pos, _ = token(text, pos)
        for _ in range(2):
            pos = skip_space(text, pos)
            if text[pos:pos+1] == '[':
                _, pos = group(text, pos, '[', ']')
        _, pos, _ = token(text, pos)
        if name.endswith('environment'):
            _, pos, _ = token(text, pos)
        return pos
    if name in ('DeclareDocumentCommand', 'NewDocumentCommand', 'RenewDocumentCommand',
                'ProvideDocumentCommand', 'DeclareDocumentMacro', 'DeclareDocumentEnvironment',
                'NewDocumentEnvironment', 'RenewDocumentEnvironment'):
        _, pos, _ = token(text, pos)
        count = 1 if name == 'DeclareDocumentMacro' else 3 if name.endswith('Environment') else 2
        for _ in range(count):
            _, pos, _ = token(text, pos)
        return pos
    return None


ENV = re.compile(r'\\(begin|end)\s*\{([^{}]+)\}')
PRIMITIVE_IF = {'if','ifcat','ifx','ifnum','ifdim','ifodd','ifvmode','ifhmode','ifmmode',
                'ifinner','ifvoid','ifhbox','ifvbox','ifeof','iftrue','iffalse','ifcase',
                'ifdefined','ifcsname','iffontchar','ifincsname'}


def conditional_end(text, pos):
    depth = 1
    while pos < len(text):
        match = COMMAND.search(text,pos)
        if not match: break
        name = match[1];pos = match.end()
        opaque = definition_end(text,match.start(),pos,name)
        if opaque is not None:
            pos = opaque;continue
        if name in PRIMITIVE_IF: depth += 1
        if name == 'fi':
            depth -= 1
            if depth == 0: return pos
    raise ValueError('unclosed primitive conditional')


def environment_end(text, pos, name):
    depth = 1
    for match in ENV.finditer(text, pos):
        if match[2] == name:
            depth += 1 if match[1] == 'begin' else -1
            if depth == 0:
                return match.start(), match.end()
    raise ValueError('unclosed environment: ' + name)


def explicit_group_end(text, pos):
    depth = 1
    for match in re.finditer(r'\\(begingroup|endgroup)\b', text[pos:]):
        depth += 1 if match[1] == 'begingroup' else -1
        if depth == 0:
            return pos + match.start(), pos + match.end()
    raise ValueError('unclosed explicit group')


class Selector:
    """Evaluate OLP selection; delegate structural commands to a book adapter.

    The optional handler(name, text, command_end, state, source) returns
    (replacement, end) or None. It is called at the point of execution, including
    inside chosen branches. It must not claim unrelated macro execution.
    """
    def __init__(self, handler=None, environment_handler=None):
        self.handler = handler
        self.environment_handler = environment_handler
        self.events = []
        self.inputs = {}

    def project(self, text, state, source='<input>'):
        original = self.inputs.setdefault(source, text)
        if original != text:
            raise ValueError('source identity reused for different text: ' + source)
        code = mask_comments(text)
        return self._walk(code, list(range(len(code))), state, source)

    def _walk(self, text, origins, state, source):
        out = []; pos = 0; problem_stack = []
        def event(kind, start, end, **extra):
            location = origins[start] if start < len(origins) else len(self.inputs[source])
            self.events.append({'source':source, 'selection_input_sha256':sha(self.inputs[source]),
                'char_start':location, 'line':self.inputs[source][:location].count('\n') + 1,
                'expression':text[start:end], 'kind':kind, **extra})
        def scoped(begin, end, child=None):
            return self._walk(text[begin:end], origins[begin:end], child or state.copy(), source)
        while pos < len(text):
            if text[pos] == '{':
                _, end = group(text, pos)
                out.extend(('{', scoped(pos + 1, end - 1), '}')); pos = end; continue
            if text[pos] == '}':
                raise ValueError('unmatched closing group: ' + source)
            if text[pos] != '\\':
                out.append(text[pos]); pos += 1; continue
            match = COMMAND.match(text, pos)
            if not match:
                out.append(text[pos]); pos += 1; continue
            start = pos; name = match[1]; pos = match.end()
            try:
                opaque = definition_end(text, start, pos, name)
            except ValueError as error:
                location = origins[start]
                raise ValueError(f'{source}:{self.inputs[source][:location].count(chr(10))+1}: '
                                 f'{error}; {text[start:start+100]!r}') from error
            if opaque is not None:
                out.append(text[start:opaque]); pos = opaque; continue
            if name == 'string':
                # TeX quotes exactly one following token. A printed command
                # such as \texttt{\string\iftag} must not execute selection.
                at = skip_space(text, pos)
                if at >= len(text): raise ValueError('string without a following token')
                quoted = COMMAND.match(text, at) if text[at] == '\\' else None
                end = quoted.end() if quoted else at + 1
                out.append(text[start:end]); pos = end; continue
            if name in PRIMITIVE_IF:
                end = conditional_end(text,pos)
                retained = text[start:end]
                if re.search(r'\\(?:tagtrue|tagfalse|toggletrue|togglefalse|iftag|iftoggle|tagitem|tagprob|olimport)\b',retained):
                    raise ValueError('selection inside an unevaluated primitive conditional: ' + source)
                event('retained_primitive_conditional',start,end)
                out.append(retained);pos=end;continue
            if name in ('verb', 'Verb'):
                if text[pos:pos+1] == '*': pos += 1
                delimiter = text[pos:pos+1]
                end = text.find(delimiter, pos + 1) if delimiter else -1
                if end < 0: raise ValueError('unclosed verbatim command')
                out.append(text[start:end+1]); pos = end + 1; continue
            if name == 'begingroup':
                stop, end = explicit_group_end(text, pos)
                out.extend((match[0], scoped(pos, stop), r'\endgroup')); pos = end; continue
            if name == 'endgroup':
                raise ValueError('unmatched endgroup: ' + source)
            if name in ('tagtrue','tagfalse','toggletrue','togglefalse','providetoggle','newtoggle'):
                value, end = group(text, pos); keys = names(value)
                if name in ('providetoggle', 'newtoggle'):
                    for key in keys:
                        if name == 'newtoggle' and key in state.tags:
                            raise ValueError('toggle already defined: ' + key)
                        state.tags.setdefault(key, False)
                else:
                    active = name.endswith('true')
                    if name.startswith('toggle'): state.values(value)
                    for key in keys:
                        state.tags[key] = active
                        if name.startswith('tag'): state.tags['not' + key] = not active
                event(name, start, end, tags=keys); pos = end; continue
            if name in ('iftag', 'iftoggle', 'tagitem'):
                value, p = group(text, pos)
                yes, p, yes_start = token(text, p); no, end, no_start = token(text, p)
                chosen = any(state.values(value))
                selected, at = (yes, yes_start) if chosen else (no, no_start)
                event(name, start, end, tags=names(value), chosen=chosen)
                if name == 'tagitem' and state.item_enabled and selected:
                    out.append(r'\item ')
                # Retain token-stream continuation: a chosen unbraced command
                # may take its arguments from the text following this conditional.
                text = text[:start] + selected + text[end:]
                origins = origins[:start] + origins[at:at+len(selected)] + origins[end:]
                pos = start; continue
            if name == 'tagrefs':
                value, end = group(text, pos); selected = []
                for pair in value.split(','):
                    key, label = pair.split('/', 1)
                    if any(state.values(key)): selected.append(label.strip().strip('{}'))
                event(name, start, end, labels=selected)
                out.append(r'\cref{' + ','.join(selected) + '}'); pos = end; continue
            if name in ('excludeenv','includeenv'):
                value, end = group(text, pos)
                if name == 'excludeenv': state.excluded.add(value)
                else: state.excluded.discard(value)
                event(name, start, end, environment=value); pos = end; continue
            if name == 'tagprob':
                outer = 'tagTrue'; p = skip_space(text, pos)
                if text[p:p+1] == '[': outer, p = group(text, p, '[', ']')
                inner, end = group(text, p)
                chosen = any(state.values(outer)) and any(state.values(inner))
                problem_stack.append(state.problem_enabled); state.problem_enabled = chosen
                event(name, start, end, chosen=chosen, tags=[outer,inner]); pos = end; continue
            if name == 'tagendprob':
                if not problem_stack: raise ValueError('unmatched tagendprob')
                state.problem_enabled = problem_stack.pop(); continue
            if name == 'item' and not state.item_enabled:
                continue
            if name == 'begin':
                env, body = group(text, pos)
                stop, end = environment_end(text, body, env)
                if env in ('verbatim','Verbatim','lstlisting','minted'):
                    out.append(text[start:end]); pos = end; continue
                if env in state.excluded or (env == 'prob' and not state.problem_enabled):
                    event('excluded_environment', start, end, environment=env); pos = end; continue
                child = state.copy()
                if env in ('tagblock','tagenumerate'):
                    value, begin = group(text, body); values = state.values(value)
                    event(env, start, begin, tags=names(value), chosen=any(values))
                    if env == 'tagblock':
                        if any(values): out.extend(('{', scoped(begin,stop,child), '}'))
                    else:
                        child.item_enabled = sum(values) > 1
                        inside = scoped(begin, stop, child)
                        out.append((r'\begin{enumerate}' + inside + r'\end{enumerate}')
                                   if child.item_enabled else '{' + inside + '}')
                else:
                    inside = scoped(body,stop,child)
                    handled = None if self.environment_handler is None else self.environment_handler(
                        env, text[start:body], inside, text[stop:end], child, source)
                    out.append(text[start:body] + inside + text[stop:end] if handled is None else handled)
                pos = end; continue
            if name == 'end':
                raise ValueError('unmatched environment ending: ' + source)
            if self.handler is not None:
                handled = self.handler(name, text, pos, state, source)
                if handled is not None:
                    replacement, end = handled
                    if end < pos: raise ValueError('book handler did not consume command')
                    out.append(replacement); pos = end; continue
            out.append(match[0])
        if problem_stack:
            raise ValueError('tagprob crosses an unsupported scope boundary: ' + source)
        return ''.join(out)
