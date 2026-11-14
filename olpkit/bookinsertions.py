"""Locate native book back matter without imposing one edition's spelling."""
import re
from .macrophases import COMMAND, group, mask_comments, skip_space, digest
from .selective import definition_end, environment_end, token
from .glossary import entry_fields


def calls(text, names):
    code=mask_comments(text);pos=0;rows=[]
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);name=m[1];pos=m.end()
        end=definition_end(code,start,pos,name)
        if end is not None:pos=end;continue
        if name=='string':_,pos,_=token(code,pos);continue
        if name=='begin':
            env,at=group(code,pos)
            if env in ('verbatim','Verbatim','lstlisting','minted','tikzpicture'):
                _,pos=environment_end(code,at,env)
            continue
        if name in names:rows.append((name,start,pos))
    return rows


def glossary_insertion(text, default_title=None):
    rows=calls(text,{'printglossary','printglossaries','glsaddall'})
    prints=[r for r in rows if r[0]!='glsaddall'];adds=[r for r in rows if r[0]=='glsaddall']
    if len(prints)!=1 or len(adds)!=1:raise ValueError('native glossary insertion differs')
    name,start,end=prints[0];code=mask_comments(text);at=skip_space(code,end);options={}
    if code[at:at+1]=='[':
        if name!='printglossary':raise ValueError('unsupported plural glossary options')
        value,end=group(code,at,'[',']');options=entry_fields(value)
    if set(options)-{'style','title','toctitle'}:raise ValueError('unsupported native glossary option')
    if options.get('style','index')!='index':raise ValueError('unsupported native glossary style')
    title=options.get('title',default_title)
    if not title:raise ValueError('native glossary title missing')
    if options.get('toctitle',title)!=title:raise ValueError('distinct glossary navigation title needs support')
    add=adds[0]
    return {'title':title,'start':start,'end':end,'add_start':add[1],'add_end':add[2],
            'command':text[start:end],'options':options,'input_sha256':digest(text)}


def insert_glossary(text, insertion, rendered):
    if digest(text)!=insertion['input_sha256']:raise ValueError('glossary insertion source changed')
    edits=[(insertion['start'],insertion['end'],rendered),
           (insertion['add_start'],insertion['add_end'],'')]
    for start,end,value in sorted(edits,reverse=True):text=text[:start]+value+text[end:]
    return text


def insert_bibliography(text, rendered, *, source, style):
    rows=calls(text,{'bibliography','bibliographystyle'})
    if len(rows)!=2 or {r[0] for r in rows}!={'bibliography','bibliographystyle'}:
        raise ValueError('bibliography source insertion differs')
    edits=[];evidence=[];code=mask_comments(text)
    for name,start,at in rows:
        value,end=group(code,at)
        expected,suffix=(source,'.bib') if name=='bibliography' else (style,'.bst')
        # The profile binds the actual native BibTeX inputs. Accept their
        # explicit OLP path (with/without suffix), and the native style search
        # spelling; never infer a different database from its basename.
        allowed={r'\olpath/'+expected,r'\olpath/'+expected.removesuffix(suffix)}
        if name=='bibliographystyle':
            allowed.update({expected.rsplit('/',1)[-1],expected.rsplit('/',1)[-1].removesuffix(suffix)})
        if value not in allowed:raise ValueError('bibliography command does not name the bound native input')
        edits.append((start,end,rendered if name=='bibliography' else ''))
        evidence.append({'command':text[start:end],'source':expected,'source_start':start,'source_end':end})
    for start,end,value in sorted(edits,reverse=True):text=text[:start]+value+text[end:]
    return text,evidence


def literal_definitions(text, names):
    """Copy only explicitly requested, argument-free native text declarations."""
    names=set(names);found={};code=mask_comments(text);pos=0
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);pos=m.end()
        end=definition_end(code,start,pos,m[1])
        if end is None:continue
        at=skip_space(code,pos)
        if code[at:at+1]=='*':at+=1
        target,at,_=token(code,at)
        key=target.removeprefix('\\')
        if key in names:
            if key in found:raise ValueError('ambiguous native prose definition: '+key)
            if m[1] not in ('def','newcommand','renewcommand','providecommand','DeclareRobustCommand'):
                raise ValueError('unsupported native prose declaration: '+key)
            body,stop=group(code,at)
            if stop!=end or '#' in body:raise ValueError('native prose declaration has parameters: '+key)
            found[key]=body
        pos=end
    if set(found)!=names:raise ValueError('native prose definitions missing: '+', '.join(sorted(names-set(found))))
    return '\n'.join('\\newcommand{\\'+key+'}{'+value+'}' for key,value in found.items())


def bibliography_helpers(bbl):
    if r'\def\natexlab#1{#1}' not in mask_comments(bbl):
        raise ValueError('native bibliography year-label helper differs')
    return (literal_definitions(bbl,{'urlprefix'})+'\n'+
            r'\newcommand{\natexlab}[1]{#1}\newcommand{\newblock}{ }')
