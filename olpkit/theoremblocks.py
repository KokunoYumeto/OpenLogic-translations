"""Preserve native textbook theorem headings, numbers and proof boundaries.

Pandoc treats custom theorem environments as anonymous divs and supplies its
own English proof heading. The native ntheorem contents stream is the numbering
witness here; every executed source environment must match it in exact order.
Localized names and the end-of-proof symbol are source configuration inputs.
"""
import re

from .macrophases import COMMAND, group, mask_comments, skip_space, digest
from .selective import definition_end, environment_end


KINDS = {'defn', 'thm', 'ex', 'prop', 'cor', 'lem', 'probd', 'proof'}
PREFIX = 'OLPTHEOREM'


def native_theorems(text):
    code = mask_comments(text)
    rows = []
    pos = 0
    while pos < len(code):
        pos = skip_space(code, pos)
        if pos == len(code):
            break
        m = COMMAND.match(code, pos)
        if not m or m[1] != 'contentsline':
            raise ValueError('unrecognized native theorem record')
        kind, pos = group(code, m.end())
        fields, pos = group(code, pos)
        page, pos = group(code, pos)
        anchor, pos = group(code, pos)
        name, inner = group(fields, 0)
        number, inner = group(fields, inner)
        title, inner = group(fields, inner)
        if fields[inner:].strip() or kind not in KINDS:
            raise ValueError('unsupported native theorem fields')
        # TeX may protect individual digits in braces; no macros are guessed.
        if not re.fullmatch(r'[0-9A-Z.{}]+', number):
            raise ValueError('unsupported native theorem number')
        rows.append({'kind':kind, 'name_tex':name, 'number':number.replace('{','').replace('}',''),
                     'title_tex':title, 'page':page, 'native_anchor':anchor})
    return rows


def source_theorems(text):
    code=mask_comments(text)
    pos=0
    stack=[]
    rows=[]
    while pos<len(code):
        if code[pos]!='\\':
            pos+=1
            continue
        start=pos
        m=COMMAND.match(code,pos);pos=m.end()
        end=definition_end(code,start,pos,m[1])
        if end is not None:
            pos=end
            continue
        if m[1] in ('verb','Verb'):
            if code[pos:pos+1]=='*':pos+=1
            delimiter=code[pos:pos+1];end=code.find(delimiter,pos+1) if delimiter else -1
            if end<0:raise ValueError('unclosed theorem-stage verbatim')
            pos=end+1
            continue
        if m[1] not in ('begin','end'):
            if m[1] in ('qed','qedhere'):
                raise ValueError('explicit proof-end placement requires native handling')
            continue
        kind,pos=group(code,pos)
        if m[1]=='begin' and kind in ('verbatim','Verbatim','minted','lstlisting','tikzpicture'):
            _,pos=environment_end(code,pos,kind)
            continue
        if kind not in KINDS:
            continue
        if m[1]=='begin':
            title=''
            at=skip_space(code,pos)
            if code[at:at+1]=='[':
                _,end=group(code,at,'[',']')
                title=text[at+1:end-1]
                pos=end
            row={'kind':kind,'title_tex':title,'start':start,'begin_end':pos}
            stack.append(row);rows.append(row)
        else:
            if not stack or stack[-1]['kind']!=kind:
                raise ValueError('unbalanced native theorem environments')
            row=stack.pop();row.update({'end_start':start,'end':pos,
                                      'source_sha256':digest(text[row['start']:pos])})
    if stack:raise ValueError('unclosed native theorem environment')
    return rows


def reconcile_theorem_source(text, native):
    """Check the actual native projected source against its emitted .thm file."""
    source=source_theorems(text)
    if len(source)!=len(native):raise ValueError('native theorem/source count differs')
    normal=lambda s:re.sub(r'\s+','',s)
    for row,witness in zip(source,native):
        if row['kind']!=witness['kind']:raise ValueError('native theorem/source order differs')
        expected=witness['name_tex'] if row['kind']=='proof' and row['title_tex'] else witness['title_tex']
        if normal(row['title_tex'])!=normal(expected):
            raise ValueError('native theorem/source title differs at '+str(len(source))+' '+witness['native_anchor'])
    return source


def prepare_theorems(text, native, names, *, evidence, proof_symbol):
    if not evidence or not proof_symbol:
        raise ValueError('native theorem evidence and proof symbol are required')
    if PREFIX in text or 'olpnativetheorem' in text:
        raise ValueError('reserved native theorem marker in source')
    source=source_theorems(text)
    if [r['kind'] for r in source]!=[r['kind'] for r in native]:
        raise ValueError('native theorem count/order differs from current source')
    edits=[];records=[]
    for index,(row,witness) in enumerate(zip(source,native),1):
        kind=row['kind']
        if kind not in names or not names[kind]:raise ValueError('missing localized theorem name: '+kind)
        key=PREFIX+str(index).zfill(6)
        number=witness['number'] if kind!='proof' else ''
        title=row['title_tex']
        if kind=='proof':
            heading=title or names[kind]
            header=r'\textit{'+heading+'.}'
        else:
            heading=names[kind]+' '+number
            if title:heading+=' ('+title+')'
            header=r'\textbf{'+heading+'.}'
        edits.append((row['start'],row['begin_end'],r'\begin{olpnativetheorem}'+'\n\n'+r'\mbox{'+key+'}'+header+'\n\n'))
        ending=''
        if kind=='proof':ending='\n\n'+r'\hfill\('+proof_symbol+r'\)'+'\n\n'
        edits.append((row['end_start'],row['end'],ending+r'\end{olpnativetheorem}'))
        records.append({**row,'marker':key,'visible_number':number,'native':witness,'heading_tex':heading})
    pos=0;parts=[]
    for start,end,replacement in sorted(edits):
        if start<pos:raise ValueError('overlapping theorem replacements')
        parts.extend((text[pos:start],replacement));pos=end
    parts.append(text[pos:]);output=''.join(parts)
    return output,{'schema':'olpkit.native-theorems.v1','input_sha256':digest(text),
                   'output_sha256':digest(output),'evidence':evidence,'records':records,
                   'proof_symbol_tex':proof_symbol,'reader_complete':False}


def bind_theorems(document,receipt):
    rows=receipt['records']
    blocks=document.xpath('.//div[@class="olpnativetheorem"]')
    if len(blocks)!=len(rows):raise ValueError('rendered native theorem count differs')
    for block,row in zip(blocks,rows):
        if not len(block) or block[0].tag!='p' or (block[0].text or '').strip()!=row['marker']:
            raise ValueError('rendered theorem marker/order differs')
        head=block[0];head.text=None
        head.set('class','olp-theorem-heading')
        block.set('class',row['kind']+' olp-theorem')
        block.set('id','olp-native-'+row['native']['native_anchor'])
        if row['visible_number']:block.set('data-native-number',row['visible_number'])
        if row['kind']=='proof':
            final=block[-1]
            formulas=final.xpath('.//math')
            if len(formulas)!=1 or final.xpath('.//annotation/text()')!=[receipt['proof_symbol_tex']]:
                raise ValueError('native proof-end symbol did not render')
            final.set('class','olp-proof-end')
    return {'blocks':len(rows),'numbered':sum(bool(r['visible_number']) for r in rows),
            'proofs':sum(r['kind']=='proof' for r in rows),'numbers_from_native_witness':True,
            'reader_complete':False}
