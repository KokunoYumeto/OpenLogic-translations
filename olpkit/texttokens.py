"""Expand OLP text tokens from authored configuration, not translated literals.

The retained Persian producer supplied the catalogue-expansion approach. Here
definitions execute in order, including source-defined helpers and book/local
overrides. This is a deliberately bounded interpreter for OLP's token language,
not a TeX engine. Unhandled token-bearing execution fails instead of guessing.
"""
from dataclasses import dataclass
import re

from .macrophases import COMMAND, digest, group, mask_comments, skip_space
from .selective import (definition_end, token, conditional_end, PRIMITIVE_IF,
                        environment_end, explicit_group_end)


OPERATIONS = re.compile(r'!!|\\(?:settexttoken|definetoken(?:uc)?|printtoken|usetoken|article|Article)\b')
INTRINSICS = {'definetoken', 'definetokenuc', 'printtoken', 'usetoken', 'article', 'Article'}
# Exact pinned upstream implementation whose six primitives are modeled below.
# A changed implementation needs inspection, not an optimistic compatibility pass.
NATIVE_SHA256 = 'e6b0287892308cff1effa7475894dbaef3a10dd0ed0769b7d2c768f9079387c2'


@dataclass(frozen=True)
class Definition:
    spec: str
    body: str
    origin: dict


def key(value):
    # TeX reduces consecutive ordinary whitespace to one space token. Retain
    # leading/trailing spaces: they must not silently alias a different key.
    return re.sub(r'[ \t\r\n]+', ' ', value)


def upper_first(value):
    """Native definetokenuc uppercases its first TeX token, not a control name."""
    if not value:
        raise ValueError('empty automatic uppercase form needs an explicit form')
    first, end, _ = token(value, 0)
    if first.startswith('\\'):
        return value
    if value.startswith('{'):
        # TeX's first argument can be a whole group. Control sequences are opaque.
        first = re.sub(r'\\[A-Za-z@]+|.', lambda m: m[0] if m[0].startswith('\\') else m[0].upper(), first)
        return '{' + first + '}' + value[end:]
    upper = first.upper()
    if len(upper) != len(first):
        raise ValueError('multi-character uppercase requires an explicit source form')
    return upper + value[end:]


def definition(text, start, command_end, name, origin):
    end = definition_end(text, start, command_end, name)
    if end is None:
        return None
    pos = skip_space(text, command_end)
    if text[pos:pos+1] == '*': pos = skip_space(text, pos+1)
    target, pos, _ = token(text, pos)
    if not re.fullmatch(r'\\[A-Za-z@]+', target): return end, None, None
    spec = ''
    if name in ('newcommand', 'renewcommand', 'providecommand', 'DeclareRobustCommand'):
        pos = skip_space(text, pos)
        if text[pos:pos+1] == '[':
            arity, pos = group(text, pos, '[', ']')
            if not re.fullmatch(r'[0-9]', arity): return end, None, None
            spec = 'm' * int(arity)
            pos = skip_space(text, pos)
            if text[pos:pos+1] == '[': return end, None, None
    elif name in ('DeclareDocumentCommand', 'NewDocumentCommand', 'RenewDocumentCommand', 'ProvideDocumentCommand'):
        spec, pos = group(text, pos)
    elif name in ('def', 'gdef', 'edef', 'xdef'):
        body_start = text.find('{', pos)
        params = text[pos:body_start].strip()
        if params != ''.join('#'+str(i+1) for i in range(params.count('#'))): return end, None, None
        spec = 'm' * params.count('#'); pos = body_start
    else:
        return end, None, None
    body, _, _ = token(text, pos)
    return end, target[1:], Definition(spec, body, origin)


def arguments(spec, text, pos):
    args = []; i = 0; immediate = False
    while i < len(spec):
        kind = spec[i]; i += 1
        if kind.isspace(): continue
        if kind == '!': immediate = True; continue
        if kind == 'm':
            value, pos, _ = token(text, pos); args.append(value)
        elif kind in ('s', 't'):
            marker = '*'
            if kind == 't':
                if i >= len(spec): raise ValueError('incomplete token argument specification')
                marker = spec[i]; i += 1
            p = pos if immediate else skip_space(text, pos)
            found = text[p:p+1] == marker
            args.append(found)
            if found: pos = p+1
        elif kind == 'o':
            p = skip_space(text, pos)
            if text[p:p+1] == '[':
                value, pos = group(text, p, '[', ']'); args.append(value)
            else: args.append(None)
        else:
            raise ValueError('unsupported token argument specification: ' + spec)
        immediate = False
    return args, pos


class TextTokens:
    def __init__(self, *, modern_xparse=True, resolver=None):
        self.modern_xparse = modern_xparse
        self.resolver = resolver
        self.forms = {}; self.macros = {}; self.definitions = []; self.occurrences = []
        self.inputs = {}; self.read_stack = []; self.intrinsic_origins = {}
        self.article_override_uses = []

    def location(self, source, text, start, end):
        return {'source':source, 'input_sha256':self.inputs[source]['sha256'], 'char_start':start,
                'char_end':end, 'line':text[:start].count('\n')+1,
                'expression_sha256':digest(text[start:end])}

    def _input(self, source, text):
        previous = self.inputs.setdefault(source, {'sha256':digest(text), 'characters':len(text)})
        if previous['sha256'] != digest(text): raise ValueError('token source identity changed: '+source)

    def _has_operation(self, text):
        return bool(OPERATIONS.search(text) or any(re.search(r'\\'+re.escape(name)+r'\b',text)
                                                  for name in self.macros))

    def configure_native(self, text, source):
        if digest(text) != NATIVE_SHA256:
            raise ValueError('unreviewed native token primitive implementation')
        self.configure(text,source,native=True)

    def _substitute(self, value, args):
        def replace(match):
            n = int(match[1])-1
            if n >= len(args) or not isinstance(args[n], str):
                raise ValueError('non-text or missing token macro argument')
            return args[n]
        return re.sub(r'#([1-9])', replace, value)

    def _lookup(self, switch, name, trace):
        pair = (key(switch), key(name))
        if pair not in self.forms: raise ValueError('undefined OLP text token: '+repr(pair))
        number = self.forms[pair]
        trace.append(number)
        return self.definitions[number]['text']

    def _invoke(self, name, args, chain, trace, depth=0):
        if depth > 40: raise ValueError('recursive token macro')
        if name in ('article', 'Article') and name in self.macros:
            # Some languages explicitly suppress the upstream English article.
            # Only the inspected, empty one-argument override is admitted here.
            macro = self.macros[name]
            self.article_override_uses.append({'name':name, 'argument':args[0],
                'definition':macro.origin, 'call_chain':chain})
            return ''
        if name in ('definetoken','definetokenuc'):
            switch, term, value = args
            if name == 'definetokenuc': value = upper_first(value)
            entry = {'switch':key(switch), 'key':key(term), 'text':value,
                     'provenance':chain, 'uppercase_first_token':name=='definetokenuc'}
            self.forms[(entry['switch'],entry['key'])] = len(self.definitions)
            self.definitions.append(entry)
            return ''
        if name in ('usetoken','printtoken','article','Article'):
            switch, term = args if len(args)==2 else ('a' if name=='article' else 'A', args[0])
            if name=='Article' and ('a',key(term)) not in self.forms:
                raise ValueError('capitalized article lacks its native existence-test form')
            value = self._lookup(switch,term,trace)
            if name == 'usetoken': return value
            return self._invoke('tokenformat',[value],chain,trace,depth+1)
        if name not in self.macros: raise ValueError('undefined token helper: '+name)
        macro = self.macros[name]
        return self._expression(macro.body, args, chain+[macro.origin], trace, depth+1)

    def _expression(self, text, args, chain, trace, depth):
        """Execute only the small expression language in token helper bodies."""
        out = []; pos = 0
        while pos < len(text):
            if text[pos].isspace(): pos += 1; continue  # formatting in macro programmes
            if text[pos] == '#':
                hit = re.match(r'#([1-9])',text[pos:])
                if not hit: raise ValueError('unsupported token parameter')
                out.append(self._substitute(hit[0],args)); pos += len(hit[0]); continue
            if text[pos] != '\\':
                if text[pos] not in '~{}':
                    raise ValueError('literal token-helper programme needs explicit support')
                out.append(text[pos]); pos += 1; continue
            hit = COMMAND.match(text,pos); name=hit[1]; pos=hit.end()
            if name in ('IfBooleanTF','IfNoValueTF'):
                parameter,pos = group(text,pos); yes,pos=group(text,pos); no,pos=group(text,pos)
                if not re.fullmatch(r'#[1-9]',parameter): raise ValueError('unsupported token condition')
                value = args[int(parameter[1])-1]
                if name=='IfBooleanTF' and not isinstance(value,bool): raise ValueError('nonboolean token condition')
                chosen = value if name=='IfBooleanTF' else value is None
                out.append(self._expression(yes if chosen else no,args,chain,trace,depth+1)); continue
            if name == 'PackageInfo':
                _,pos=group(text,pos); _,pos=group(text,pos); continue
            arity = {'definetoken':3,'definetokenuc':3,'usetoken':2,'printtoken':2,'article':1,'Article':1}.get(name)
            if arity is not None:
                actual=[]
                for _ in range(arity):
                    value,pos=group(text,pos); actual.append(self._substitute(value,args))
                out.append(self._invoke(name,actual,chain,trace,depth+1)); continue
            if name in self.macros:
                actual,pos=arguments(self.macros[name].spec,text,pos)
                actual=[self._substitute(a,args) if isinstance(a,str) else a for a in actual]
                out.append(self._invoke(name,actual,chain,trace,depth+1)); continue
            raise ValueError('unsupported operation in token helper: '+name)
        return ''.join(out)

    def configure(self, text, source='<config>', *, native=False):
        self._input(source,text)
        if source in self.read_stack: raise ValueError('recursive token configuration input')
        self.read_stack.append(source)
        try: self._walk(mask_comments(text),text,source,configuration=True,native=native)
        finally: self.read_stack.pop()

    def _walk(self, code, original, source, *, configuration=False, native=False, offset=0):
        out=[]; pos=0
        def origin(start,end): return self.location(source,original,offset+start,offset+end)
        def scoped(begin,end):
            forms=self.forms.copy(); macros=self.macros.copy()
            try: return self._walk(code[begin:end],original,source,configuration=configuration,native=native,offset=offset+begin)
            finally: self.forms=forms; self.macros=macros
        while pos < len(code):
            start=pos
            if code.startswith('!!',pos):
                if configuration: raise ValueError('executed text token in configuration')
                name='@printtoken'; pos+=2
            elif code[pos]=='\\':
                hit=COMMAND.match(code,pos); name=hit[1]; pos=hit.end()
            elif code[pos]=='{':
                _,end=group(code,pos); out.extend(('{',scoped(pos+1,end-1),'}'));pos=end;continue
            elif code[pos]=='}': raise ValueError('unmatched token group')
            else:
                out.append(code[pos]);pos+=1;continue
            if name == 'string':
                at=skip_space(code,pos)
                if at >= len(code): raise ValueError('string without a following token')
                end=COMMAND.match(code,at).end() if code[at]=='\\' else at+1
                out.append(code[start:end]);pos=end;continue
            try:
                parsed=definition(code,start,pos,name,origin(start,pos))
            except ValueError as error:
                raise ValueError(f'{source}:{origin(start,pos)["line"]}: {error}; {code[start:start+120]!r}') from error
            if parsed is not None:
                end,target,macro=parsed
                if macro is not None:
                    macro=Definition(macro.spec,macro.body,origin(start,end))
                    relevant=(target in ('settexttoken','@printtoken','tokenformat') or OPERATIONS.search(macro.body))
                    if target in INTRINSICS:
                        if native:
                            self.intrinsic_origins[target]=macro.origin
                        elif (target in ('article', 'Article') and macro.spec == 'm'
                              and not macro.body.strip() and name not in ('gdef','xdef')):
                            self.macros[target]=macro
                        else:
                            raise ValueError('token primitive override needs explicit support: '+target)
                    elif relevant:
                        if name in ('gdef','xdef'):
                            raise ValueError('global token helper definition needs explicit support')
                        if configuration or OPERATIONS.search(macro.body): self.macros[target]=macro
                    elif target in self.macros:
                        raise ValueError('token helper redefined with unsupported body: '+target)
                out.append(code[start:end]);pos=end;continue
            if name=='@ifpackagelater' and native:
                package,pos=group(code,pos); date,pos=group(code,pos)
                yes,yp,ys=token(code,pos); no,end,ns=token(code,yp)
                if package!='xparse' or date!='2018/04/17': raise ValueError('unrecognized token package condition')
                chosen,at=(yes,ys) if self.modern_xparse else (no,ns)
                self._walk(chosen,original,source,configuration=True,native=True,offset=offset+at)
                pos=end;continue
            if name in PRIMITIVE_IF:
                end=conditional_end(code,pos)
                if self._has_operation(code[start:end]): raise ValueError('unresolved conditional with token operations')
                out.append(code[start:end]);pos=end;continue
            if name in ('verb','Verb'):
                if code[pos:pos+1]=='*':pos+=1
                delimiter=code[pos:pos+1]; end=code.find(delimiter,pos+1) if delimiter else -1
                if end<0:raise ValueError('unclosed token verbatim')
                out.append(original[offset+start:offset+end+1]);pos=end+1;continue
            if (name in ('url','nolinkurl') or
                name=='path' and code[skip_space(code,pos):skip_space(code,pos)+1]=='{') and not configuration:
                _,end=group(code,pos)
                out.append(original[offset+start:offset+end]);pos=end;continue
            if name=='begingroup':
                stop,end=explicit_group_end(code,pos)
                out.extend((r'\begingroup',scoped(pos,stop),r'\endgroup'));pos=end;continue
            if name=='endgroup': raise ValueError('unmatched token endgroup')
            if name=='begin':
                env,p=group(code,pos)
                stop,end=environment_end(code,p,env)
                if env in ('verbatim','Verbatim','lstlisting','minted'):
                    out.append(original[offset+start:offset+end]);pos=end;continue
                out.extend((code[start:p],scoped(p,stop),code[stop:end]));pos=end;continue
            if name=='input' and configuration:
                path,end=group(code,pos)
                if not self.resolver: raise ValueError('token configuration input requires a source resolver')
                identity,contents=self.resolver(path,source)
                self.configure(contents,identity);pos=end;continue
            if name=='global' and self._has_operation(code[pos:]):
                raise ValueError('global token assignments need explicit support')
            if name=='forcsvlist' and configuration:
                helper,pos=group(code,pos); values,end=group(code,pos)
                if not re.fullmatch(r'\\[A-Za-z@]+',helper): raise ValueError('unsupported token CSV helper')
                if helper[1:] in self.macros:
                    for value in values.split(','):
                        if value.strip():self._invoke(helper[1:],[value.strip()],[origin(start,end)],[])
                elif OPERATIONS.search(values): raise ValueError('unsupported token CSV body')
                pos=end;continue
            arity={'definetoken':3,'definetokenuc':3,'usetoken':2,'printtoken':2,'article':1,'Article':1}.get(name)
            relevant = name in self.macros or arity is not None
            if name=='@printtoken' and not relevant:
                raise ValueError('OLP token shorthand has no source definition')
            if relevant:
                spec='m'*arity if arity is not None else self.macros[name].spec
                args,end=arguments(spec,code,pos); trace=[]
                result=self._invoke(name,args,[origin(start,end)],trace)
                if not configuration:
                    self.occurrences.append({'call':origin(start,end),'expression':code[start:end],
                        'text':result,'definition_ids':list(dict.fromkeys(trace)),
                        'renderer':self.macros.get(name,Definition('','',{})).origin})
                    out.append(result)
                pos=end;continue
            if configuration:
                # Unknown macros' arguments are opaque, not executable groups.
                p=skip_space(code,pos)
                while code[p:p+1] in ('{','['):
                    opening=code[p]; value,end=group(code,p,opening,'}' if opening=='{' else ']')
                    if self._has_operation(value) and not native:
                        raise ValueError('unhandled token-bearing configuration command: '+name)
                    p=skip_space(code,end)
                pos=p;continue
            out.append(code[start:pos])
        return ''.join(out)

    def expand(self, text, source='<body>'):
        self._input(source,text)
        output=self._walk(mask_comments(text),text,source)
        return output, {'schema':'olpkit.text-tokens.v1','inputs':dict(self.inputs),
            'modern_xparse':self.modern_xparse,'intrinsic_definitions':self.intrinsic_origins,
            'article_override_uses':self.article_override_uses,
            'definitions':self.definitions,'occurrences':self.occurrences,
            'output_sha256':digest(output),'arbitrary_tex_execution':False,
            'reader_complete':False}
