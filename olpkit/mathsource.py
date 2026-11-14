"""Source-defined OLP notation expansion for the Gujarati/Pandoc export route.

This replaces the recovered converter's fixed formula alphabet and hand-written
symbol substitutions with ordered source declarations. Standard LaTeX commands
remain for Pandoc; fonts, diagrams, references and document structure are separate
stages. It is a bounded macro adapter, not arbitrary TeX execution.
"""
from dataclasses import dataclass,field
import re

from .macrophases import COMMAND,digest,group,mask_comments,skip_space
from .selective import token,definition_end,environment_end,explicit_group_end,PRIMITIVE_IF,conditional_end
from .texttokens import Definition,definition


def tex_join(parts):
    """Expansion joins tokens, not control-sequence name strings."""
    result=[];previous=''
    for part in parts:
        if not part:continue
        if previous and re.search(r'\\[A-Za-z@]+$',previous) and re.match(r'[A-Za-z@]',part):
            result.append(' ')
        result.append(part);previous=part
    return ''.join(result)


def uncomment(text):
    """Remove TeX comments before reading programme arguments (not blank lines)."""
    out=[];cursor=0
    for m in re.finditer('%',text):
        pos=m.start()
        if pos<cursor:continue
        prior=pos-1
        while prior>=0 and text[prior]=='\\':prior-=1
        if (pos-prior-1)%2:continue
        out.append(text[cursor:pos]);end=text.find('\n',pos)
        cursor=len(text) if end<0 else end+1
        while cursor<len(text) and text[cursor] in ' \t':cursor+=1
    out.append(text[cursor:]);return tex_join(out)


def parse_definition(text,start,end,name,origin):
    if name=='DeclareDocumentMacro':
        target,pos,_=token(text,end);body,pos,_=token(text,pos)
        if not re.fullmatch(r'\\[A-Za-z@]+',target):raise ValueError('invalid document macro name')
        return pos,target[1:],Definition('',body,origin)
    parsed=definition(text,start,end,name,origin)
    if parsed and parsed[1] is None and name in ('newcommand','renewcommand','providecommand'):
        pos=skip_space(text,end)
        if text[pos:pos+1]=='*':pos+=1
        target,pos,_=token(text,pos);count,pos=group(text,pos,'[',']')
        default,pos=group(text,pos,'[',']');body,pos,_=token(text,pos)
        if not re.fullmatch(r'[1-9]',count):raise ValueError('invalid optional macro arity')
        return pos,target[1:],Definition('O{'+default+'}'+'m'*(int(count)-1),body,origin)
    return parsed


def arguments(spec,text,pos):
    args=[];i=0;immediate=False
    while i<len(spec):
        c=spec[i];i+=1
        if c.isspace() or c=='+':continue
        if c=='!':immediate=True;continue
        if c=='m':value,pos,_=token(text,pos);args.append(value)
        elif c in ('s','t'):
            marker='*'
            if c=='t':marker,i,_=token(spec,i)
            p=pos if immediate else skip_space(text,pos)
            yes=text.startswith(marker,p);args.append(yes)
            if yes:pos=p+len(marker)
        elif c in ('o','O'):
            default=None
            if c=='O':default,i=group(spec,i)
            p=pos if immediate else skip_space(text,pos)
            if text[p:p+1]=='[':value,pos=group(text,p,'[',']');args.append(value)
            else:args.append(default)
        else:raise ValueError('unsupported source macro signature: '+spec)
        immediate=False
    return args,pos


def program(body,args):
    """Evaluate source xparse branches before substituting text arguments."""
    out=[];pos=0
    while pos<len(body):
        if body.startswith('##',pos):out.append('#');pos+=2;continue
        if body[pos]=='#':
            m=re.match(r'#([1-9])',body[pos:])
            if not m:raise ValueError('unsupported macro parameter')
            value=args[int(m[1])-1]
            if not isinstance(value,str):raise ValueError('non-text optional parameter reached output')
            out.append(value);pos+=2;continue
        if body[pos]=='\\':
            m=COMMAND.match(body,pos);name=m[1];pos=m.end()
            if name in ('IfBooleanTF','IfNoValueTF','IfValueTF'):
                parameter,pos,_=token(body,pos)
                yes,pos,_=token(body,pos);no,pos,_=token(body,pos)
                if not re.fullmatch(r'#[1-9]',parameter.strip()):raise ValueError('unsupported xparse condition')
                value=args[int(parameter.strip()[1])-1]
                if name=='IfBooleanTF':
                    if not isinstance(value,bool):raise ValueError('nonboolean source condition')
                    chosen=value
                else:chosen=(value is None) if name=='IfNoValueTF' else (value is not None)
                out.append(program(yes if chosen else no,args));continue
            if name.startswith('If') or name in PRIMITIVE_IF:
                raise ValueError('unsupported conditional in source notation: '+name)
            out.append(m[0]);continue
        out.append(body[pos]);pos+=1
    return tex_join(out)


@dataclass
class MathState:
    macros:dict=field(default_factory=dict)
    unsupported:set=field(default_factory=set)
    alphabet:dict|None=None
    alphabet_origin:dict|None=None
    math:bool=False

    def copy(self):
        return MathState(dict(self.macros),set(self.unsupported),self.alphabet,self.alphabet_origin,self.math)


class SourceMath:
    def __init__(self,*,resolver=None):
        self.resolver=resolver;self.state=MathState();self.inputs={};self.declarations=[]
        self.calls=[];self.shorthands=[];self.modes={};self.read_stack=[];self.fonts=[]

    def record_input(self,source,text):
        row={'sha256':digest(text),'characters':len(text)}
        if self.inputs.setdefault(source,row)!=row:raise ValueError('notation source identity changed')

    def origin(self,source,text,start,end,chain):
        return {'source':source,'input_sha256':self.inputs[source]['sha256'],
                'char_start':start,'char_end':end,'line':text[:start].count('\n')+1,'expansion_chain':chain}

    def formula_library(self,text,source):
        self.record_input(source,text)
        code=mask_comments(text)
        for m in re.finditer(r'\\def\\(ol(?:latin|greek|alphagreek)formulas)\b',code):
            body,end=group(code,m.end());compact=re.sub(r'\s+','',body)
            if compact==r'\let\formula\relax':mapping={}
            else:
                match=re.fullmatch(r'\\gdef\\formula\{\\lookup\{([^{}]+)\}\}',compact)
                if not match:raise ValueError('unrecognized formula alphabet implementation')
                mapping=dict(item.split('/',1) for item in match[1].split(','))
            self.modes[m[1]]=(mapping,self.origin(source,text,m.start(),end,[]))
        if len(self.modes)!=3:raise ValueError('incomplete native formula alphabet')

    def configure(self,text,source):
        self.record_input(source,text)
        if source in self.read_stack:raise ValueError('recursive notation configuration')
        self.read_stack.append(source)
        try:self._walk(mask_comments(text),self.state,source,text,configuration=True)
        finally:self.read_stack.pop()

    def _walk(self,text,state,source,original,*,configuration=False,offset=0,chain=(),depth=0):
        if depth>60:raise ValueError('recursive source notation')
        out=[];pos=0
        def loc(a,b):return self.origin(source,original,offset+a,offset+b,list(chain))
        def child(a,b,childstate=None):
            return self._walk(text[a:b],childstate or state.copy(),source,original,
                configuration=configuration,offset=offset+a,chain=chain,depth=depth+1)
        while pos<len(text):
            start=pos
            if text[pos]=='{':
                _,end=group(text,pos);out.extend(('{',child(pos+1,end-1),'}'));pos=end;continue
            if text[pos]=='}':raise ValueError('unbalanced source notation group')
            if text[pos]=='$' and not configuration:
                delimiter='$$' if text[pos:pos+2]=='$$' else '$'
                state.math=not state.math;out.append(delimiter);pos+=len(delimiter);continue
            if text[pos]=='!' and state.math and not configuration:
                if text[pos:pos+2]=='!!':raise ValueError('unexpanded text token before notation conversion')
                if state.alphabet is None:raise ValueError('formula shorthand has no configured alphabet')
                if not state.alphabet:replacement='';end=pos+1
                else:
                    value,end,_=token(text,pos+1);replacement=state.alphabet.get(value,value)
                index=len(self.shorthands)
                self.shorthands.append({'call':loc(start,end),'expression':text[start:end],
                    'text':replacement,'mode':state.alphabet_origin})
                if replacement:
                    identity=source+'#formula-'+str(index)
                    self.record_input(identity,replacement)
                    replacement=self._walk(replacement,state,identity,replacement,chain=chain,depth=depth+1)
                    self.shorthands[index]['expanded_text']=replacement
                if re.search(r'\\[A-Za-z@]+$',replacement):replacement+=' '
                out.append(replacement);pos=end;continue
            if text[pos]!='\\':out.append(text[pos]);pos+=1;continue
            m=COMMAND.match(text,pos);name=m[1];pos=m.end()
            parsed=parse_definition(text,start,pos,name,loc(start,pos))
            if parsed:
                end,target,macro=parsed
                if macro:
                    if name in ('gdef','edef','xdef'):
                        raise ValueError('global or eager notation definition needs explicit support: '+name)
                    clean=uncomment(original[offset+start:offset+end])
                    head=COMMAND.match(clean)
                    _,_,macro=parse_definition(clean,0,head.end(),head[1],macro.origin)
                    origin=loc(start,end);idx=len(self.declarations)
                    self.declarations.append({'name':target,'signature':macro.spec,'body':macro.body,'origin':origin})
                    if name=='providecommand' and target in state.macros:pass
                    else:state.macros[target]=(Definition(macro.spec,macro.body,origin),idx,False)
                else:
                    target,_,_=token(text,pos)
                    if re.fullmatch(r'\\[A-Za-z@]+',target):state.unsupported.add(target[1:])
                if not configuration:out.append(text[start:end])
                pos=end;continue
            if name in self.modes:
                state.alphabet,definition_origin=self.modes[name]
                if state.alphabet and depth:
                    raise ValueError('global formula alphabet change in a local scope needs explicit support')
                state.alphabet_origin={**definition_origin,'selected_at':loc(start,pos)};continue
            if name=='let':
                target,p,_=token(text,pos);p=skip_space(text,p)
                if text[p:p+1]=='=':p+=1
                value,end,_=token(text,p)
                if not re.fullmatch(r'\\[A-Za-z@]+',target):raise ValueError('unsupported notation alias')
                origin=loc(start,end);idx=len(self.declarations)
                self.declarations.append({'name':target[1:],'alias_of':value,'origin':origin})
                if value.startswith('\\') and value[1:] in state.macros:
                    macro,_,literal=state.macros[value[1:]]
                    state.macros[target[1:]]=(macro,idx,literal)
                else:state.macros[target[1:]]=(Definition('',value,origin),idx,True)
                if not configuration:out.append(text[start:end])
                pos=end;continue
            if name=='input' and configuration:
                path,end=group(text,pos)
                if not self.resolver:raise ValueError('notation input requires source resolver')
                identity,contents=self.resolver(path,source)
                self.configure(contents,identity);pos=end;continue
            if name=='DeclareMathAlphabet' and configuration:
                fields=[]
                for _ in range(5):value,pos,_=token(text,pos);fields.append(value)
                self.fonts.append({'declaration':fields,'origin':loc(start,pos)});continue
            if configuration:
                p=skip_space(text,pos)
                while text[p:p+1] in ('[','{'):
                    opening=text[p];_,p=group(text,p,opening,']' if opening=='[' else '}');p=skip_space(text,p)
                pos=p;continue
            if name in ('verb','Verb'):
                if text[pos:pos+1]=='*':pos+=1
                delimiter=text[pos:pos+1];end=text.find(delimiter,pos+1) if delimiter else -1
                if end<0:raise ValueError('unclosed notation verbatim')
                out.append(text[start:end+1]);pos=end+1;continue
            if name in ('url','nolinkurl','label','ref','pageref','cref','Cref','cite'):
                p=skip_space(text,pos)
                if text[p:p+1]=='*':p+=1
                while text[p:p+1]=='[':_,p=group(text,p,'[',']');p=skip_space(text,p)
                if text[p:p+1]=='{':_,p=group(text,p)
                out.append(text[start:p]);pos=p;continue
            if name=='string':
                _,end,_=token(text,pos);out.append(text[start:end]);pos=end;continue
            if name=='begingroup':
                stop,end=explicit_group_end(text,pos)
                out.extend((m[0],child(pos,stop),r'\endgroup'));pos=end;continue
            if name=='endgroup':raise ValueError('unmatched notation endgroup')
            if name=='begin':
                env,p=group(text,pos);stop,end=environment_end(text,p,env)
                if env in ('verbatim','Verbatim','lstlisting','minted','tikzpicture'):
                    out.append(text[start:end]);pos=end;continue
                nested=state.copy()
                if re.fullmatch(r'(?:equation|align|alignat|gather|multline|displaymath|math)\*?',env):nested.math=True
                out.extend((text[start:p],child(p,stop,nested),text[stop:end]));pos=end;continue
            if name in ('[','('):state.math=True;out.append(m[0]);continue
            if name in (']',')'):state.math=False;out.append(m[0]);continue
            if name in ('ensuremath','text','mbox'):
                value,end,at=token(text,pos);nested=state.copy();nested.math=name=='ensuremath'
                out.extend((m[0]+'{',child(at,at+len(value),nested),'}'));pos=end;continue
            if name in PRIMITIVE_IF:
                end=conditional_end(text,pos)
                if depth and chain:raise ValueError('unevaluated conditional in notation expansion: '+name)
                out.append(text[start:end]);pos=end;continue
            if name=='relax':continue
            if name=='applytofirst':
                helper=state.macros.get(name)
                if not helper or re.sub(r'\s+','',helper[0].body)!=r'{\expandafter#1#2}':
                    raise ValueError('unrecognized first-token formatter')
                values,end=arguments('mm',text,pos);style,value=values
                first,after,_=token(value,0)
                if first.startswith('\\') and first[1:] in state.macros:
                    macro,index,literal=state.macros[first[1:]]
                    actual,after=arguments(macro.spec,value,after)
                    expanded=program(macro.body,actual)+value[after:]
                    first,after,_=token(expanded,0);value=expanded
                expansion='{'+style+'{'+first+'}'+value[after:]+'}'
                idx=helper[1]
            elif name in state.macros:
                macro,idx,literal=state.macros[name]
                try:actual,end=arguments(macro.spec,text,pos);expansion=program(macro.body,actual)
                except (ValueError,IndexError) as e:raise ValueError(f'{source}:{loc(start,pos)["line"]}: {name}: {e}') from e
                if literal:
                    self.calls.append({'call':loc(start,end),'name':name,'definition':idx,'text':expansion,'captured_alias':True})
                    out.append(expansion+(' ' if re.search(r'\\[A-Za-z@]+$',expansion) else ''));pos=end;continue
            elif name in state.unsupported:raise ValueError('called unsupported source declaration: '+name)
            else:out.append(m[0]);continue
            call_id=len(self.calls)
            self.calls.append({'call':loc(start,end),'name':name,'definition':idx,'arguments':values if name=='applytofirst' else actual})
            identity=source+'#call-'+str(call_id)
            self.record_input(identity,expansion)
            rendered=self._walk(expansion,state,identity,expansion,chain=(*chain,call_id),depth=depth+1)
            self.calls[call_id]['output_sha256']=digest(rendered)
            out.append(rendered+(' ' if re.search(r'\\[A-Za-z@]+$',rendered) else ''));pos=end
        return tex_join(out)

    def font_preamble(self):
        """Carry declared weight/shape into Pandoc; retain exact font provenance.

        These are MathML style equivalents, not claims of identical font files,
        glyph geometry or PDF appearance. Unrecognized shapes are rejected.
        """
        parts=[];rows=[]
        for row in self.fonts:
            name,encoding,family,series,shape=row['declaration']
            if series not in ('m','b','bx') or shape not in ('n','it'):
                raise ValueError('unsupported source math alphabet weight/shape')
            body=(r'\mathit{#1}' if shape=='it' else r'\mathrm{#1}')
            if series in ('b','bx'):body=r'\boldsymbol{'+body+'}'
            parts.append(r'\newcommand{'+name+r'}[1]{'+body+'}')
            rows.append({**row,'mathml_style_body':body,'exact_font_face_acceptance':False})
        return '\n'.join(parts),rows

    def expand(self,text,source):
        self.record_input(source,text)
        result=self._walk(mask_comments(text),self.state.copy(),source,text)
        return result,{'schema':'olpkit.source-notation.v1','inputs':self.inputs,'declarations':self.declarations,
            'calls':self.calls,'formula_shorthands':self.shorthands,'font_declarations':self.fonts,
            'configured_formula_mode':self.state.alphabet_origin,'output_sha256':digest(result),
            'arbitrary_tex_execution':False,'reader_complete':False}
