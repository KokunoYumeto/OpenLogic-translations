"""Project native OLP book front matter without retyping its scholarly credits."""
import re
from .macrophases import COMMAND,group,skip_space,mask_comments,digest


def native_frontmatter(class_source, metadata, locale, cover_text, driver, *, language, evidence):
    if not evidence:raise ValueError('native front-matter provenance required')
    pattern=r'\\newcommand\s*\{\\OLPfrontmatter\}'
    matches=list(re.finditer(pattern,mask_comments(class_source)))
    if len(matches)!=1:raise ValueError('native front-matter definition missing/ambiguous')
    at=matches[0].end();_,end=group(mask_comments(class_source),at)
    start=skip_space(class_source,at)+1;body=class_source[start:end-1]
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
    definitions+='\n'+cover_text
    return cover+'\n'+front,definitions,{
        'schema':'olpkit.book-front.v1','class_sha256':digest(class_source),
        'metadata_sha256':digest(metadata),'locale_sha256':digest(locale),
        'cover_text_sha256':digest(cover_text),'driver_sha256':digest(driver),
        'native_frontmatter_body_sha256':digest(body),'native_frontmatter_pages':len(pages),
        'metadata':values,'captions':captions,'native_evidence':evidence,
        'projection_sha256':digest(cover+'\n'+front),'definitions_sha256':digest(definitions),
        'reader_complete':False}
