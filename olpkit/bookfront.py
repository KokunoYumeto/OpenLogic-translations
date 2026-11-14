"""Project native OLP book front matter without retyping its scholarly credits."""
import re
from decimal import Decimal
from .macrophases import COMMAND,group,skip_space,mask_comments,digest
from .bookinsertions import calls,literal_definitions
from .glossary import entry_fields
from .selective import definition_end,token


def native_definitions(text, names):
    """Copy actual command declarations, including parameters, without executing TeX."""
    wanted=set(names);found={};code=mask_comments(text);pos=0
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);pos=m.end()
        end=definition_end(code,start,pos,m[1])
        if end is None:continue
        at=skip_space(code,pos)
        if code[at:at+1]=='*':at+=1
        target,_,_=token(code,at);name=target.removeprefix('\\')
        if name in wanted:
            if name in found:raise ValueError('ambiguous native front definition: '+name)
            found[name]=text[start:end]
        pos=end
    if set(found)!=wanted:raise ValueError('native front definition missing: '+', '.join(sorted(wanted-set(found))))
    return '\n'.join(found.values())


def apply_front_patches(body,metadata):
    rows=[];code=mask_comments(metadata)
    for _,start,at in calls(metadata,{'patchcmd'}):
        args=[]
        for _ in range(5):value,at=group(code,at);args.append(value)
        target,search,replacement,success,failure=args
        if target==r'\OLPfrontmatter':
            if success.strip():raise ValueError('unsupported native front-patch success action')
            if not search or search not in body:raise ValueError('native front patch target absent')
            body=body.replace(search,replacement,1)
            disposition='applied first literal match, as in native patchcmd'
        elif target==r'\OLPscreencover':
            # Reflowable covers retain content; fixed-page vertical spacing has
            # no corresponding dimension. Record the exact native command.
            if not re.fullmatch(r'\\vspace\*?\{[.\d]+cm\}',search) or not re.fullmatch(r'\\vspace\*?\{[.\d]+cm\}',replacement):
                raise ValueError('unsupported native cover patch')
            disposition='fixed-page cover vertical spacing; reflowed cover retains all content'
        else:raise ValueError('unsupported native metadata patch target: '+target)
        rows.append({'command':metadata[start:at],'target':target,'disposition':disposition})
    return body,rows


def native_cover_width(driver, definition_sources):
    """Read the width actually applied to each native cover portrait."""
    covers=calls(driver,{'OLPscreencover'})
    if len(covers)!=1:raise ValueError('native screen-cover call missing/ambiguous')
    code=mask_comments(driver)
    artwork,_=group(code,covers[0][2]);rows=[];definitions={}
    number=r'(?:\d+(?:\.\d*)?|\.\d+)'
    for _,start,at in calls(artwork,{'includegraphics'}):
        at=skip_space(artwork,at);options={}
        if artwork[at:at+1]=='[':
            value,at=group(artwork,at,'[',']');options=entry_fields(value)
        path,end=group(artwork,at)
        if '/portraits/' not in path:continue
        value=options.get('width','')
        m=re.fullmatch(r'\s*('+number+r'|\\[A-Za-z@]+)\s*\\textwidth\s*',value)
        if not m:raise ValueError('unsupported native cover portrait width')
        factor=m[1]
        if factor.startswith('\\'):
            name=factor[1:]
            declaration=literal_definitions('\n'.join(definition_sources.values()),{name})
            body,_=group(declaration,len(r'\newcommand{')+len(factor)+1)
            if not re.fullmatch(number,body.strip()):
                raise ValueError('native cover width is not a literal decimal')
            definitions[name]=declaration;factor=body.strip()
        width=Decimal(factor)*100
        if not 0<width<=100:raise ValueError('native cover width outside text area')
        rows.append({'source_reference':path,'source_command':artwork[start:end],
                     'width_tex':value,'width_percent':float(width)})
    if not rows or len({r['width_percent'] for r in rows})!=1:
        raise ValueError('missing or differing native cover portrait widths')
    return rows[0]['width_percent'],{'driver_sha256':digest(driver),'portraits':rows,
        'definitions':definitions,'definition_sources':{n:digest(t) for n,t in definition_sources.items()}}


def native_frontmatter(class_source, metadata, locale, cover_text, driver, *, language, evidence, style_source=''):
    if not evidence:raise ValueError('native front-matter provenance required')
    pattern=r'\\newcommand\s*\{\\OLPfrontmatter\}'
    matches=list(re.finditer(pattern,mask_comments(class_source)))
    if len(matches)!=1:raise ValueError('native front-matter definition missing/ambiguous')
    at=matches[0].end();_,end=group(mask_comments(class_source),at)
    start=skip_space(class_source,at)+1;body=class_source[start:end-1]
    body,patches=apply_front_patches(body,metadata)
    metadata_names={'setOLPbooktitle':('OLPbooktitle','optional'),
                    'setOLPbooksubtitle':('OLPbooksubtitle','optional'),
                    'setOLPauthor':('OLPauthor','optional'),
                    'setOLPbookversion':('OLPbookversion','second'),
                    'setOLPsourcelink':('OLPsourcelink','single'),
                    'setOLPauthorlink':('OLPauthorlink','single')}
    values={};observed=[];code=mask_comments(metadata);pos=0
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        m=COMMAND.match(code,pos);pos=m.end()
        if m[1] not in metadata_names:continue
        name,kind=metadata_names[m[1]];pos=skip_space(code,pos);optional=None
        if kind=='optional' and code[pos:pos+1]=='[':optional,pos=group(code,pos,'[',']')
        value,pos=group(code,pos)
        if name in values:raise ValueError('duplicate native book metadata')
        values[name]=value
        if kind=='optional':values[name+'cover']=value if optional is None else optional
        if kind=='second':values['OLPshortbookversion'],pos=group(code,pos)
        observed.append(m[1])
    if set(observed)!=set(metadata_names):raise ValueError('incomplete native book metadata')
    captions={}
    for m in re.finditer(r'\\setlocalecaption\b',mask_comments(locale)):
        lang,pos=group(locale,m.end());name,pos=group(locale,pos);value,pos=group(locale,pos)
        if lang==language:captions[name+'name']=value
    required={'OLPname','instigatorname','editorialboardname','contributorsname','contentsname','OLTname','OLTlinkname','licensename'}
    if not required<=set(captions):raise ValueError('localized front-matter labels incomplete')
    cover_call=list(re.finditer(r'\\OLPscreencover\s*\{',mask_comments(driver)))
    if len(cover_call)!=1:raise ValueError('native screen-cover call missing/ambiguous')
    _,stop=group(mask_comments(driver),cover_call[0].end()-1)
    artwork=driver[cover_call[0].end():stop-1]
    pages=body.split(r'\newpage')
    if len(pages)!=5 or body.count(r'\tableofcontents*')!=1:
        raise ValueError('native front-matter page structure changed')
    pages[-1]=pages[-1].replace(r'\tableofcontents*',r'\begin{olpbooktoc}OLPBOOKTOC\end{olpbooktoc}')
    front='\n\n'.join(r'\begin{olpfrontpage}'+page+r'\end{olpfrontpage}' for page in pages)
    cover=(r'\begin{olpbookcover}'+ '\n'+r'\begin{olpcovertitle}\OLPbooktitlecover\end{olpcovertitle}'+'\n'+
           r'\begin{olpcoversubtitle}\OLPbooksubtitlecover\end{olpcoversubtitle}'+'\n'+artwork+'\n'+
           r'\begin{olpcoverversion}\OLPshortbookversion\end{olpcoverversion}'+ '\n'+r'\end{olpbookcover}')
    definitions='\n'.join('\\newcommand{\\'+name+'}{'+value+'}' for name,value in {**captions,**values}.items())
    # Pagination/positioning has no text equivalent in reflowable output.
    # Consume native bookmark arguments explicitly instead of leaking them.
    definitions+='\n'+r'\newcommand{\currentpdfbookmark}[2]{}'
    if calls(body,{'oluselicense'}):
        definitions+='\n'+native_definitions(style_source,{'ollicensefont','oluselicense'})
    definitions+='\n'+cover_text
    return cover+'\n'+front,definitions,{
        'schema':'olpkit.book-front.v1','class_sha256':digest(class_source),
        'metadata_sha256':digest(metadata),'locale_sha256':digest(locale),
        'cover_text_sha256':digest(cover_text),'driver_sha256':digest(driver),
        'style_sha256':digest(style_source),'native_metadata_patches':patches,
        'native_frontmatter_body_sha256':digest(body),'native_frontmatter_pages':len(pages),
        'metadata':values,'captions':captions,'native_evidence':evidence,
        'projection_sha256':digest(cover+'\n'+front),'definitions_sha256':digest(definitions),
        'reader_complete':False}
