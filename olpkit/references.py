"""Source-scoped OLP references using a separately verified native book aux.

The caller supplies evidence tying the auxiliary file to this edition and
localized reference names from the edition's actual configuration. No guessed
numbers, English fallback, or full-corpus aux substitution is permitted.
"""
import re
from .macrophases import COMMAND, group, mask_comments, skip_space, digest
from .selective import definition_end, environment_end, explicit_group_end, token

MARK = re.compile(r'OLPXREF\d{6}')
NAMESPACE = ('theolpart','theolchapter','theolsection')


def read_aux(text):
    labels={}; crefs={}
    for line_no,line in enumerate(text.splitlines(),1):
        if not line.startswith(r'\newlabel{'):continue
        key,pos=group(line,len(r'\newlabel'))
        payload,end=group(line,pos)
        fields=[];pos=0
        while skip_space(payload,pos)<len(payload):
            value,pos=group(payload,pos);fields.append(value)
        target=crefs if key.endswith('@cref') else labels
        key=key.removesuffix('@cref')
        if key in target:raise ValueError('duplicate native aux label: '+key)
        target[key]={'fields':fields,'line':line_no}
    for key,row in labels.items():
        fields=row.pop('fields')
        if len(fields)<4:raise ValueError('incomplete native aux label: '+key)
        row.update(number_tex=fields[0],page=fields[1],title_tex=fields[2],destination=fields[3])
        if key in crefs:
            value=crefs[key]['fields'][0];pos=0;parts=[]
            for _ in range(3):
                item,pos=group(value,pos,'[',']');parts.append(item)
            row.update(kind=parts[0],counter=parts[1],counter_prefix=parts[2],cref_line=crefs[key]['line'])
            if value[pos:]!=fields[0]:raise ValueError('native aux/cref number mismatch: '+key)
    return labels


def plain_number(value):
    value=value.replace('{','').replace('}','')
    # Decimal digits in the native script are reader text, not TeX commands.
    # Preserve them exactly; do not transliterate the edition's numbering.
    if not re.fullmatch(r'[A-Za-z\d.()\-]+',value):
        raise ValueError('reference number requires explicit TeX rendering: '+value)
    return value


class References:
    def __init__(self, labels, names, *, evidence, pair_conjunction, sort_pairs=True,
                 parenthesized_types=('enumi',)):
        if not evidence:raise ValueError('native auxiliary/source identity evidence required')
        self.labels=labels;self.names=names;self.evidence=evidence
        self.pair_conjunction=pair_conjunction;self.sort_pairs=sort_pairs
        self.parenthesized_types=tuple(parenthesized_types)
        self.markers={};self.anchors=[];self.calls=[];self.events=[];self.conditionals=[]

    def mark(self,row,original,start,end):
        marker='OLPXREF'+str(len(self.markers)).zfill(6)
        self.markers[marker]={**row,'original_tex':original,'char_start':start,'char_end':end}
        return r'\mbox{'+marker+'}'

    def anchor(self,key,original,start,end):
        if key not in self.labels:raise ValueError('source anchor absent from native aux: '+key)
        if key in self.anchors:raise ValueError('duplicate executed source anchor: '+key)
        self.anchors.append(key)
        return self.mark({'kind':'anchor','key':key},original,start,end)

    def reference(self,keys,name,original,start,end,linked=True):
        if not 1<=len(keys)<=2:raise ValueError('reference lists beyond pairs need native format support')
        rows=[]
        for key in keys:
            if key not in self.labels:raise ValueError('reference absent from native aux: '+key)
            rows.append((key,self.labels[key]))
        clever=name in ('olref','Olref','cref','Cref')
        if clever and any('kind' not in row for _,row in rows):raise ValueError('native cref type missing')
        same=clever and all(row['kind']==rows[0][1]['kind'] for _,row in rows)
        if same and len(rows)>1 and self.sort_pairs:
            def order(item):
                row=item[1]
                parts=row['counter_prefix'].split(',') if row['counter_prefix'] else []
                if not all(p.isdigit() for p in parts+[row['counter']]):
                    raise ValueError('unsupported native reference sorting fields')
                return tuple(map(int,parts+[row['counter']]))
            rows.sort(key=order)
        pieces=[]
        for index,(key,row) in enumerate(rows):
            if index:pieces.append({'text':self.pair_conjunction})
            number=plain_number(row['page'] if name=='pageref' else row['number_tex'])
            prefix=''
            if clever:
                kind=row['kind']
                if kind in self.parenthesized_types:number='('+number+')'
                elif index==0 or not same:
                    if kind not in self.names:raise ValueError('localized native reference name missing: '+kind)
                    prefix=self.names[kind][1 if same and len(rows)>1 else 0]+' '
            pieces.append({'text':prefix+number,'key':key,'linked':linked})
        self.calls.append({'command':name,'keys':keys,'rendered_keys':[key for key,_ in rows],
                           'pieces':pieces,'char_start':start,'char_end':end})
        return self.mark({'kind':'reference','pieces':pieces,'keys':keys},original,start,end)

    def walk(self,text,state,offset=0):
        out=[];pos=0;text_box=state.get('_text_box',False);inline_math=False
        while pos<len(text):
            if text[pos]=='$' and text_box:
                inline_math=not inline_math
                state['_text_box']=not inline_math
                out.append('$');pos+=1;continue
            if text[pos]=='{':
                body,end=group(text,pos)
                out.extend(('{',self.walk(body,state.copy(),offset+pos+1),'}'));pos=end;continue
            if text[pos]!='\\':out.append(text[pos]);pos+=1;continue
            start=pos;match=COMMAND.match(text,pos);name=match[1];pos=match.end()
            if name=='begingroup':
                stop,end=explicit_group_end(text,pos)
                out.extend((match[0],self.walk(text[pos:stop],state.copy(),offset+pos),r'\endgroup'));pos=end;continue
            end=definition_end(text,start,pos,name)
            if end is not None:
                p=skip_space(text,pos)
                if text[p:p+1]=='*':p+=1
                target,p,_=token(text,p)
                if target in tuple('\\'+x for x in NAMESPACE)+(r'\ol@sectioncs',):
                    value,p,_=token(text,p)
                    if p!=end or '\\' in value:raise ValueError('unsupported reference-context assignment')
                    state[target[1:]]=value
                out.append(text[start:end]);pos=end;continue
            if name=='let':
                target,p,_=token(text,pos);p=skip_space(text,p)
                if text[p:p+1]=='=':p+=1
                value,end,_=token(text,p)
                if target in tuple('\\'+x for x in NAMESPACE)+(r'\ol@sectioncs',):
                    raise ValueError('reference-context aliases require explicit support')
                out.append(text[start:end]);pos=end;continue
            if name in ('verb','Verb'):
                if text[pos:pos+1]=='*':pos+=1
                delimiter=text[pos:pos+1];end=text.find(delimiter,pos+1)
                if not delimiter or end<0:raise ValueError('unclosed reference verbatim')
                out.append(text[start:end+1]);pos=end+1;continue
            if name in ('text','mbox','textrm','textsf','texttt','textnormal','textbf','textit'):
                value,end,at=token(text,pos)
                inner=state.copy();inner['_text_box']=True
                out.append(match[0]+'{'+self.walk(value,inner,offset+at)+'}')
                pos=end;continue
            if name=='begin':
                env,at=group(text,pos);stop,end=environment_end(text,at,env)
                if env in ('verbatim','Verbatim','lstlisting','minted','tikzpicture'):
                    out.append(text[start:end])
                else:
                    self.events.append(['begin',env])
                    out.extend((text[start:at],self.walk(text[at:stop],state.copy(),offset+at),text[stop:end]))
                    self.events.append(['end',env])
                pos=end;continue
            if name in ('olfileid','olchapterid','olpartid'):
                p=skip_space(text,pos)
                if text[p:p+1]=='[':_,p=group(text,p,'[',']')
                for key in NAMESPACE[:{'olfileid':3,'olchapterid':2,'olpartid':1}[name]]:
                    state[key],p,_=token(text,p)
                out.append(text[start:p]);pos=p;continue
            if name=='oliflabeldef':
                key,p,_=token(text,pos);yes,p,yes_at=token(text,p);no,end,no_at=token(text,p)
                defined=key in self.labels
                self.conditionals.append({'key':key,'defined':defined,'char_start':offset+start,'char_end':offset+end,
                                          'selected_tex':yes if defined else no})
                out.append(self.walk(yes if defined else no,state,offset+(yes_at if defined else no_at)))
                pos=end;continue
            if name in ('olsection','olchapter','olpart'):
                p=skip_space(text,pos);option=''
                if text[p:p+1]=='[':
                    option_at=p+1
                    value,p=group(text,p,'[',']');option='['+self.walk(value,state.copy(),offset+option_at)+']'
                args=[]
                for _ in range({'olsection':1,'olchapter':3,'olpart':2}[name]):
                    value,p,at=token(text,p);args.append((value,at))
                if name=='olsection':key=':'.join(state[x] for x in NAMESPACE)+':sec';heading=state.get('ol@sectioncs','section')
                elif name=='olchapter':key=args[0][0]+':'+args[1][0]+'::chap';heading='chapter'
                else:key=args[0][0]+':::part';heading='part'
                title,at=args[-1]
                out.append('\\'+heading+option+'{'+self.walk(title,state.copy(),offset+at)+'}')
                # The source heading's native label is produced by the macro.
                out.append(self.anchor(key,'',offset+p,offset+p))
                self.events.append(['heading',heading,key]);pos=p;continue
            if name in ('ollabel','label'):
                value,end,_=token(text,pos)
                key=':'.join(state[x] for x in NAMESPACE)+':'+value if name=='ollabel' else value
                rendered=self.anchor(key,text[start:end],offset+start,offset+end)
                out.append(rendered[6:-1] if state.get('_text_box') else rendered);pos=end;continue
            if name in ('olref','Olref','cref','Cref','ref','pageref'):
                p=skip_space(text,pos);linked=True
                if text[p:p+1]=='*' and name not in ('olref','Olref'):linked=False;p+=1
                options=[]
                if name in ('olref','Olref'):
                    while text[skip_space(text,p):skip_space(text,p)+1]=='[':
                        p=skip_space(text,p);value,p=group(text,p,'[',']');options.append(value)
                    if len(options)>3:raise ValueError('too many relative reference components')
                value,end,_=token(text,p)
                if name in ('olref','Olref'):
                    keys=[':'.join([state[x] for x in NAMESPACE[:3-len(options)]]+options+[value])]
                else:keys=[key.strip() for key in value.split(',')]
                rendered=self.reference(keys,name,text[start:end],offset+start,offset+end,linked)
                out.append(rendered[6:-1] if state.get('_text_box') else rendered);pos=end;continue
            if name in ('chapter','section','subsection','part','appendix','mainmatter','frontmatter','backmatter','item','setcounter','addtocounter','refstepcounter'):
                self.events.append(['command',name])
            out.append(match[0])
        return ''.join(out)

    def prepare(self,text,source):
        if MARK.search(text) or self.markers:raise ValueError('reserved reference marker or reused adapter')
        result=self.walk(mask_comments(text),dict.fromkeys(NAMESPACE,'udf'))
        missing=sorted({key for call in self.calls for key in call['keys']}-set(self.anchors))
        return result,{'schema':'olpkit.references.v1','source':source,'input_sha256':digest(text),
                       'output_sha256':digest(result),'auxiliary_evidence':self.evidence,
                       'markers':self.markers,'calls':self.calls,'anchors':self.anchors,
                       'counter_events':self.events,'references_without_source_anchor':missing,
                       'native_label_conditionals':self.conditionals,
                       'parenthesized_types':self.parenthesized_types,
                       'reader_complete':False}


def bind_references(document,receipt):
    from lxml import etree
    markers=receipt['markers'];seen=[]
    def local(node):return node.tag.rsplit('}',1)[-1] if isinstance(node.tag,str) else ''
    def nodes(text,math):
        result=[];pos=0
        for hit in MARK.finditer(text):
            if hit.group() not in markers:raise ValueError('unknown reference marker')
            if hit.group() in seen:raise ValueError('duplicate rendered reference marker')
            if hit.start()>pos:result.append(text[pos:hit.start()])
            row=markers[hit.group()];seen.append(hit.group())
            if row['kind']=='anchor':
                node=etree.Element('mspace' if math else 'span',id=row['key'])
                if math:node.set('width','0em')
                result.append(node)
            else:
                for piece in row['pieces']:
                    if not piece.get('linked'):
                        result.append(piece['text']);continue
                    node=etree.Element('mtext' if math else 'a',href='#'+piece['key'])
                    node.text=piece['text'];result.append(node)
            pos=hit.end()
        result.append(text[pos:]);return result
    for node in list(document.iter()):
        if local(node)=='annotation':continue
        if local(node)=='mtext' and MARK.search(node.text or ''):
            namespace=node.tag.rsplit('}',1)[0]+'}' if '}' in node.tag else ''
            row=etree.Element(namespace+'mrow');row.tail=node.tail
            for item in nodes(node.text,True):
                if isinstance(item,str):
                    if not item:continue
                    child=etree.Element(namespace+'mtext');child.text=item
                else:
                    child=item
                    child.tag=namespace+child.tag
                row.append(child)
            node.getparent().replace(node,row)
            node=row
        for which in ('text','tail'):
            value=getattr(node,which)
            if not value or not MARK.search(value):continue
            if local(node) in ('mi','mo','mn') or (which=='tail' and any(local(p)=='math' for p in node.iterancestors())):
                raise ValueError('reference marker escaped its text box')
            parent=node if which=='text' else node.getparent()
            index=0 if which=='text' else parent.index(node)+1
            setattr(node,which,'');last=None
            for item in nodes(value,False):
                if isinstance(item,str):
                    if last is None:setattr(node,which,(getattr(node,which) or '')+item)
                    else:last.tail=(last.tail or '')+item
                else:parent.insert(index,item);index+=1;last=item
    for annotation in document.xpath('//*[local-name()="annotation"][@encoding="application/x-tex"]'):
        value=annotation.text or ''
        value=re.sub(r'\\(?:mbox|text)\{(OLPXREF\d{6})\}',lambda m:markers[m[1]]['original_tex'],value)
        value=MARK.sub(lambda m:markers[m[0]]['original_tex'],value)
        annotation.text=value
    missing=sorted(set(markers)-set(seen))
    if missing:raise ValueError('unconverted reference markers: '+', '.join(missing[:12]))
    return {'bound':len(seen),'anchors':len(receipt['anchors']),'references':len(receipt['calls']),
            'references_without_source_anchor':receipt['references_without_source_anchor'],'reader_complete':False}
