"""Source-defined glossary entries in the native book's emitted order.

No definitions, plurals, symbols or sort order are translated or guessed here.
SLC's slcterm declaration must first be checked against its native definition;
standard newglossaryentry input is also supported for other edition sources.
"""
import re
from .macrophases import COMMAND, group, mask_comments, skip_space, digest


def entry_fields(text):
    fields={};pos=0
    while pos<len(text):
        pos=skip_space(text,pos)
        if pos==len(text):break
        m=re.match(r'([A-Za-z]+)\s*=\s*',text[pos:])
        if not m:raise ValueError('unsupported glossary field')
        key=m[1];pos+=m.end()
        if key in fields:raise ValueError('duplicate glossary field')
        if text[pos:pos+1]=='{':value,pos=group(text,pos)
        else:
            end=text.find(',',pos)
            if end<0:end=len(text)
            value=text[pos:end].strip();pos=end
        fields[key]=value;pos=skip_space(text,pos)
        if pos<len(text):
            if text[pos]!=',':raise ValueError('missing glossary field separator')
            pos+=1
    return fields


def read_entries(text, *, slcterm_definition=None):
    if slcterm_definition is not None:
        expected=r'\newglossaryentry{#2}{sort={#3},name={#4},plural={#4},symbol={#1},description={#5}}'
        if re.sub(r'\s+','',mask_comments(slcterm_definition))!=expected:
            raise ValueError('slcterm definition does not match the native mapping')
    code=mask_comments(text);pos=0;entries={}
    while pos<len(code):
        pos=skip_space(code,pos)
        if pos==len(code):break
        start=pos;m=COMMAND.match(code,pos)
        if not m or m[1] not in ('slcterm','newglossaryentry'):
            raise ValueError('unsupported glossary source statement')
        pos=m.end()
        if m[1]=='slcterm':
            if slcterm_definition is None:raise ValueError('native slcterm definition is required')
            symbol='';pos=skip_space(code,pos)
            if code[pos:pos+1]=='[':symbol,pos=group(code,pos,'[',']')
            args=[]
            for _ in range(4):value,pos=group(code,pos);args.append(value)
            key,sort,name,description=args
            fields={'sort':sort,'name':name,'plural':name,'symbol':symbol,'description':description}
        else:
            key,pos=group(code,pos);value,pos=group(code,pos);fields=entry_fields(value)
        if not key or key in entries:raise ValueError('missing or duplicate glossary key')
        if not fields.get('name') or not fields.get('description'):
            raise ValueError('glossary name/definition missing')
        unsupported=set(fields)-{'name','sort','plural','symbol','description'}
        if unsupported:raise ValueError('unsupported glossary fields: '+', '.join(sorted(unsupported)))
        entries[key]={'key':key,**fields,'source_start':start,'source_end':pos,
                      'source_sha256':digest(text[start:pos]),
                      'anchor':'olp-glossary-'+digest(key)[:20]}
    return entries


def native_order(text):
    code=mask_comments(text);rows=[]
    for m in re.finditer(r'\\glossentry\b',code):
        key,pos=group(code,m.end());_,end=group(code,pos)
        if key in rows:raise ValueError('duplicate native glossary entry')
        rows.append(key)
    if not rows:raise ValueError('native glossary has no entries')
    return rows


def expand_links(text, entries, *, sentence_case=None):
    code=mask_comments(text);pieces=[];pos=0;last=0;calls=[]
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        m=COMMAND.match(code,pos);start=pos;pos=m.end()
        if m[1] not in ('gls','glspl','Gls','Glspl'):
            if m[1].startswith(('gls','Gls','GLS')):
                raise ValueError('unsupported glossary access command: '+m[1])
            continue
        key,end=group(code,pos)
        if key not in entries:raise ValueError('unknown glossary reference: '+key)
        field='plural' if m[1].lower()=='glspl' else 'name'
        if field not in entries[key]:raise ValueError('native plural is not explicitly established: '+key)
        label=entries[key][field]
        if m[1].startswith('G'):
            if sentence_case is None:raise ValueError('native sentence-case rule is required')
            label=sentence_case(label)
        # Labels here must not recursively invoke glossary references.
        if re.search(r'\\(?:gls|Gls|GLS)',label):raise ValueError('recursive glossary name')
        pieces.extend((text[last:start],r'\hyperlink{'+entries[key]['anchor']+'}{'+label+'}'))
        calls.append({'key':key,'form':m[1],'label_tex':label,'source_start':start,'source_end':end})
        last=end;pos=end
    pieces.append(text[last:])
    return ''.join(pieces),calls


def glossary_tex(entries, order, title, *, heading='chapter*', evidence, sentence_case=None):
    if set(order)!=set(entries) or len(order)!=len(entries):
        raise ValueError('source/native glossary coverage differs')
    if not evidence or not title or heading not in ('chapter*','section*'):
        raise ValueError('native glossary title, hierarchy and evidence required')
    pieces=['\\'+heading+'{'+title+'}',r'\begin{description}'];calls=[]
    for key in order:
        row=entries[key]
        label=row['name']
        if row.get('symbol'):label+=' ('+row['symbol']+')'
        label,lc=expand_links(label,entries,sentence_case=sentence_case)
        body,bc=expand_links(row['description'],entries,sentence_case=sentence_case)
        calls.extend({'entry':key,**c} for c in lc+bc)
        # A braced item label protects literal square brackets in mathematical
        # symbols. Keep the native name, symbol and full definition verbatim.
        pieces.extend((r'\item[{'+label+'}]'+r'\hypertarget{'+row['anchor']+'}{}',body))
    pieces.append(r'\end{description}');output='\n\n'.join(pieces)+'\n'
    return output,{'schema':'olpkit.glossary.v1','order':order,'entries':entries,'links':calls,
                   'title_tex':title,'heading':heading,'native_evidence':evidence,
                   'output_sha256':digest(output),'reader_complete':False}


def bind_glossary(document, receipt):
    """Check the complete emitted list and make each term the link target."""
    expected=[receipt['entries'][key]['anchor'] for key in receipt['order']]
    nodes=document.xpath('//*[@id[starts-with(.,"olp-glossary-")]]')
    if [n.get('id') for n in nodes]!=expected:
        raise ValueError('glossary anchor order/coverage differs from the native book')
    pairs=[];lists=[]
    for node in nodes:
        body=node.getparent();term=body.getprevious() if body is not None else None
        if body is None or body.tag!='dd' or term is None or term.tag!='dt':
            raise ValueError('glossary entry is not a term/definition pair')
        if node.tag not in ('span','div') or len(node) or (node.text or '').strip() or (node.tail or '').strip():
            raise ValueError('glossary anchor unexpectedly contains reader text')
        if term.get('id') or not ''.join(term.itertext()).strip() or not ''.join(body.itertext()).strip():
            raise ValueError('glossary term/definition missing or already bound')
        parent=body.getparent()
        if parent is None or parent.tag!='dl':raise ValueError('glossary list structure differs')
        pairs.append((node,term,body));lists.append(parent)
    if not lists or any(parent is not lists[0] for parent in lists):
        raise ValueError('glossary entries are not in one complete list')
    if len(lists[0])!=2*len(expected):raise ValueError('unexpected extra glossary entries')
    links=document.xpath('//a[starts-with(@href,"#olp-glossary-")]')
    expected_links=['#'+receipt['entries'][call['key']]['anchor'] for call in receipt['links']]
    if [node.get('href') for node in links]!=expected_links:
        raise ValueError('glossary cross-reference coverage/order differs')
    for node,term,body in pairs:
        term.set('id',node.get('id'))
        whitespace=(node.text or '')+(node.tail or '')
        previous=node.getprevious()
        if previous is None:body.text=(body.text or '')+whitespace
        else:previous.tail=(previous.tail or '')+whitespace
        body.remove(node)
    classes=lists[0].get('class','').split()
    if 'olp-glossary' not in classes:classes.append('olp-glossary')
    lists[0].set('class',' '.join(classes))
    return {'entries':len(pairs),'links':len(links),'native_order_complete':True,
            'targets_on_terms':True,'reader_complete':False}
