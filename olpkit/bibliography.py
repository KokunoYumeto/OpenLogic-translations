"""Preserve the native bibliography and evidenced natbib author–date labels.

The caller binds the native .bbl/.aux to the actual edition inputs and supplies
its citation punctuation. No bibliographic data is fetched or reformatted.
"""
import re
from .macrophases import COMMAND, digest, group, mask_comments, skip_space
from .selective import definition_end, environment_end


def unbrace(value):
    if value.startswith('{'):
        inner,end=group(value,0)
        if end==len(value):return inner
    return value


def read_citation_labels(aux):
    code=mask_comments(aux);labels={}
    for m in re.finditer(r'\\bibcite\b',code):
        key,pos=group(code,m.end());record,pos=group(code,pos)
        fields=[];i=0
        for _ in range(4):v,i=group(record,i);fields.append(v)
        if record[i:].strip() or key in labels:raise ValueError('invalid/duplicate native citation label')
        number,year,short,full=fields
        labels[key]={'number':number,'year':year,'author':unbrace(short),'full_author':unbrace(full),
                     'anchor':'olp-bib-'+digest(key)[:20]}
    if not labels:raise ValueError('native citation labels missing')
    return labels


def read_bibliography(bbl, labels, *, evidence):
    code=mask_comments(bbl)
    opening=re.match(r'\s*\\begin\{thebibliography\}',code)
    if not opening or not evidence:raise ValueError('native bibliography/evidence required')
    _,pos=group(code,opening.end())
    stop,end=environment_end(code,pos,'thebibliography')
    if code[end:].strip():raise ValueError('content follows native bibliography')
    hits=list(re.finditer(r'\\bibitem\b',code[pos:stop]));entries=[]
    for i,m in enumerate(hits):
        start=pos+m.start();at=skip_space(code,pos+m.end())
        if code[at:at+1]!='[':raise ValueError('native author-date bibliography label missing')
        label,at=group(code,at,'[',']');key,at=group(code,at)
        finish=pos+hits[i+1].start() if i+1<len(hits) else stop
        body=bbl[at:finish].strip()
        if key not in labels or not body:raise ValueError('bibliography entry/auxiliary label missing')
        entries.append({'key':key,'label_tex':label,'body_tex':body,'anchor':labels[key]['anchor'],
                        'source_start':at,'source_end':finish,'source_sha256':digest(bbl[at:finish])})
    if len(entries)!=len(labels) or {r['key'] for r in entries}!=set(labels):
        raise ValueError('native bibliography/auxiliary coverage differs')
    if len({r['key'] for r in entries})!=len(entries):raise ValueError('duplicate bibliography entry')
    return {'schema':'olpkit.bibliography.v1','entries':entries,'labels':labels,
            'source_sha256':digest(bbl),'native_evidence':evidence}


def bibliography_tex(record, title):
    if not title:raise ValueError('localized bibliography title required')
    parts=[r'\chapter*{'+title+'}',r'\begin{olpbibliography}']
    for entry in record['entries']:
        parts.extend((r'\begin{olpbibentry}',r'\hypertarget{'+entry['anchor']+'}{}',entry['body_tex'],r'\end{olpbibentry}'))
    parts.append(r'\end{olpbibliography}')
    return '\n\n'.join(parts)+'\n'


def date_parts(year):
    match=re.fullmatch(r'(\d{4})(?:\{([a-z])\}|([a-z]))?',year)
    return (match[1],match[2] or match[3] or '') if match else (year,'')


def citation_parts(keys, labels, form, prenote, postnote, style, *, full=False):
    required={'open','close','separator','author_year','year_separator','note_separator'}
    if set(style)!=required:raise ValueError('complete native citation punctuation required')
    if form not in ('citep','citet','citealt','citealp'):raise ValueError('unsupported citation form')
    if not keys or len(set(keys))!=len(keys):raise ValueError('empty/duplicate citation keys')
    for key in keys:
        if key not in labels:raise ValueError('unknown native citation key: '+key)
    parenthetical=form in ('citep','citealp');parens=form in ('citep','citet')
    opening=style['open'] if parens else '';closing=style['close'] if parens else ''
    pieces=[];last_author=None;last_year=None
    for index,key in enumerate(keys):
        row=labels[key];author=row['full_author'] if full and row['full_author'] else row['author']
        year=row['year'];base,suffix=date_parts(year)
        if not author:raise ValueError('empty native citation author')
        if author==last_author and year:
            if base==last_year:
                if not suffix:raise ValueError('ambiguous repeated native citation year')
                value=style['year_separator']+suffix
            else:value=style['year_separator']+' '+year
        else:
            if index and not parenthetical and labels[keys[index-1]]['year']:
                pieces[-1]['label_tex']+=closing
            prefix=style['separator']+' ' if index else ''
            if parenthetical:
                value=prefix+author+(style['author_year']+' '+year if year else '')
            else:
                value=prefix+author
                if year:value+=' '+opening+(prenote+' ' if prenote else '')+year
        pieces.append({'key':key,'anchor':row['anchor'],'label_tex':value})
        last_author=author;last_year=base
    if parenthetical:pieces[0]['label_tex']=opening+(prenote+' ' if prenote else '')+pieces[0]['label_tex']
    if postnote:pieces[-1]['label_tex']+=style['note_separator']+postnote
    if parenthetical or labels[keys[-1]]['year']:pieces[-1]['label_tex']+=closing
    return pieces


def expand_citations(text, labels, *, style, evidence):
    if not evidence:raise ValueError('native citation style evidence required')
    code=mask_comments(text);pos=last=0;pieces=[];calls=[]
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);name=m[1];pos=m.end()
        end=definition_end(code,start,pos,name)
        if end is not None:pos=end;continue
        if name=='begin':
            env,at=group(code,pos)
            if env in ('verbatim','Verbatim','lstlisting','minted','tikzpicture'):
                _,pos=environment_end(code,at,env)
            continue
        if name not in ('cite','citep','citet','citealt','citealp'):
            if name.startswith(('cite','Cite')):raise ValueError('unsupported citation command: '+name)
            continue
        full=code[pos:pos+1]=='*'
        if full:pos+=1
        options=[];pos=skip_space(code,pos)
        while code[pos:pos+1]=='[':
            value,pos=group(code,pos,'[',']');options.append(value);pos=skip_space(code,pos)
        if len(options)>2:raise ValueError('too many citation notes')
        value,end=group(code,pos);keys=[key.strip() for key in value.split(',')]
        prenote=options[0] if len(options)==2 else '';postnote=options[-1] if options else ''
        form=('citep' if options else 'citet') if name=='cite' else name
        parts=citation_parts(keys,labels,form,prenote,postnote,style,full=full)
        output=''.join(r'\hyperlink{'+p['anchor']+'}{'+p['label_tex']+'}' for p in parts)
        marker='olp-citation-'+str(len(calls)+1).zfill(6)
        output=r'\hypertarget{'+marker+'}{'+output+'}'
        pieces.extend((text[last:start],output));last=end;pos=end
        calls.append({'marker':marker,'command':name,'form':form,'keys':keys,'prenote':prenote,'postnote':postnote,
                      'parts':parts,'source_start':start,'source_end':end,'source_tex':text[start:end]})
    pieces.append(text[last:]);result=''.join(pieces)
    return result,{'schema':'olpkit.citations.v1','input_sha256':digest(text),'output_sha256':digest(result),
                   'calls':calls,'native_evidence':evidence,'reader_complete':False}


def bind_bibliography(document, record, citations):
    expected=[r['anchor'] for r in record['entries']]
    nodes=document.xpath('//*[@id[starts-with(.,"olp-bib-")]]')
    if [n.get('id') for n in nodes]!=expected:raise ValueError('bibliography anchor coverage/order differs')
    lists=document.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpbibliography ")]')
    if len(lists)!=1:raise ValueError('complete bibliography container missing')
    entries=lists[0].xpath('./*[contains(concat(" ",normalize-space(@class)," ")," olpbibentry ")]|./ol[@class="olp-bibliography-list"]/*')
    if len(entries)!=len(expected):raise ValueError('bibliography entry count differs')
    for container,node in zip(entries,nodes):
        if node not in container.iterdescendants() or not ''.join(container.itertext()).strip():
            raise ValueError('bibliography entry text/target missing')
    links=document.xpath('//a[starts-with(@href,"#olp-bib-")]')
    rendered_calls=document.xpath('//*[@id[starts-with(.,"olp-citation-")]]')
    expected_calls={c['marker']:c for c in citations['calls']}
    if len(rendered_calls)!=len(expected_calls) or {n.get('id') for n in rendered_calls}!=set(expected_calls):
        raise ValueError('citation occurrence coverage differs')
    # Pandoc moves footnotes to the end. Check each occurrence and its ordered
    # destinations, rather than falsely requiring lexical source order in DOM.
    consumed=[]
    for node in rendered_calls:
        call=expected_calls[node.get('id')]
        targets=node.xpath('.//a[starts-with(@href,"#olp-bib-")]')
        if [a.get('href') for a in targets]!=['#'+p['anchor'] for p in call['parts']]:
            raise ValueError('citation occurrence destination/order differs')
        consumed.extend(targets)
    if len(consumed)!=len(links) or set(consumed)!=set(links):
        raise ValueError('citation link outside its source occurrence')
    lists[0].set('role','doc-bibliography')
    if not lists[0].findall('ol'):
        from lxml import etree
        ordered=etree.SubElement(lists[0],'ol',attrib={'class':'olp-bibliography-list','role':'list'})
        for container in entries:ordered.append(container)
    for container in entries:
        container.tag='li';container.attrib.pop('role',None)
    for link in links:link.set('role','doc-biblioref')
    return {'entries':len(entries),'citation_calls':len(citations['calls']),'citation_links':len(links),
            'rendered_call_order':[n.get('id') for n in rendered_calls],'reader_complete':False}
