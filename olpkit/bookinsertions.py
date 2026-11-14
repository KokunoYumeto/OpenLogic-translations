"""Locate native book back matter without imposing one edition's spelling."""
import re
from .macrophases import COMMAND, group, mask_comments, skip_space, digest
from .selective import definition_end, environment_end, token
from .glossary import entry_fields
from .cache import relative_path


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


def absent_glossary(text):
    """An explicit absent profile may not suppress executed glossary content."""
    names={m[1] for m in COMMAND.finditer(mask_comments(text))
           if m[1].startswith(('gls','Gls','GLS','printgloss','loadgls','newgloss','makegloss','setgloss'))}
    if calls(text,names):
        raise ValueError('glossary declared absent but native source uses glossary commands')
    return {'schema':'olpkit.glossary.v1','status':'absent','order':[],'entries':{},'links':[],
            'native_evidence':{'explicit_profile':None,'projected_source_sha256':digest(text)},
            'reader_complete':False}


def bibliography_sources(source):
    rows=[source] if isinstance(source,str) else source
    if not isinstance(rows,list) or not rows or any(not isinstance(n,str) for n in rows):
        raise ValueError('bibliography requires an ordered source list')
    if len(rows)!=len(set(rows)):
        raise ValueError('duplicate bibliography source')
    for name in rows:
        relative_path(name)
        if not name.endswith('.bib'):raise ValueError('bibliography input must name an exact bib file')
    return rows


def insert_bibliography(text, rendered, *, source, style, book_directory=None):
    databases=bibliography_sources(source)
    if book_directory is not None:relative_path(book_directory)
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
        configured=databases if name=='bibliography' else [style]
        actual=[v.strip() for v in value.split(',')]
        if len(actual)!=len(configured):raise ValueError('bibliography command does not name the bound native input')
        for literal,path in zip(actual,configured):
            allowed={r'\olpath/'+path,r'\olpath/'+path.removesuffix(suffix)}
            if name=='bibliographystyle':
                allowed.update({path.rsplit('/',1)[-1],path.rsplit('/',1)[-1].removesuffix(suffix)})
            elif book_directory and path.startswith(book_directory+'/'):
                local=path[len(book_directory)+1:]
                allowed.update({local,local.removesuffix(suffix)})
            if literal not in allowed:raise ValueError('bibliography command does not name the bound native input')
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
