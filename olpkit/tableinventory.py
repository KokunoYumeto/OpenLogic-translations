"""Lossless source table inventory for G-TABLE's rendered comparisons.

This is a syntax inventory, not a TeX interpreter or a passing PDF gate. It
retains nested tables, explicit/implicit cells, longtable bands and exact source
locators. Tags/macros and every rendered cell still need native-build binding.
Unsupported syntax is reported on its table, never silently omitted.
"""
import hashlib
import re

from .macrophases import COMMAND, group, mask_comments, skip_space
from .selective import environment_end


TABLES = {'tabular', 'tabular*', 'array', 'longtable'}
BANDS = {'endfirsthead', 'endhead', 'endfoot', 'endlastfoot'}
RULES = {'hline', 'cline', 'toprule', 'midrule', 'bottomrule', 'addlinespace'}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def columns(spec):
    """Count standard array columns without treating decorators as columns."""
    result = []; pos = 0
    while (pos := skip_space(spec, pos)) < len(spec):
        char = spec[pos]; pos += 1
        if char == '|': continue
        if char in '@!><':
            _, pos = group(spec, pos); continue
        if char == '*':
            count, pos = group(spec, pos); repeated, pos = group(spec, pos)
            if not count.strip().isdigit() or not 0 < int(count) <= 100:
                raise ValueError('nonliteral or excessive repeated columns')
            result.extend(columns(repeated) * int(count)); continue
        if char in 'lcr': result.append({'kind':char}); continue
        if char in 'pmb':
            width, pos = group(spec, pos)
            result.append({'kind':char, 'width':width}); continue
        raise ValueError('unsupported column type: ' + char)
    if not result: raise ValueError('table has no columns')
    return result


def _optional(text, pos):
    pos = skip_space(text, pos)
    return group(text, pos, '[', ']')[1] if text[pos:pos+1] == '[' else pos


def _cell(text, masked, start, end, column, env):
    while start < end and masked[start].isspace(): start += 1
    while end > start and masked[end-1].isspace(): end -= 1
    source = text[start:end]; code = masked[start:end]; span = 1; row_span = 1
    content = code
    hit = re.match(r'\\multicolumn\b', code)
    if hit:
        count, pos = group(code, hit.end()); spec, pos = group(code, pos)
        content, pos = group(code, pos)
        if code[pos:].strip() or not count.isdigit() or int(count) < 1:
            raise ValueError('unsupported multicolumn cell')
        if len(columns(spec)) != 1: raise ValueError('multicolumn alignment differs')
        span = int(count)
    multi = re.match(r'\\multirow\b', content)
    if multi:
        pos = _optional(content,multi.end())
        count,pos = group(content,pos)
        if not count.strip().isdigit() or not 1 <= int(count) <= 100:
            raise ValueError('unsupported multirow extent')
        row_span=int(count)
        pos=_optional(content,pos); _,pos=group(content,pos)
        pos=_optional(content,pos); _,pos=group(content,pos)
        if content[pos:].strip(): raise ValueError('content outside multirow')
    proofs = [start + m.start() for m in re.finditer(r'\\DisplayProof\b', code)]
    return {'char_start':start, 'char_end':end, 'source_tex':source,
            'sha256':sha(source), 'column':column, 'column_span':span, 'row_span':row_span,
            'proof_terminators':proofs,
            'required_math_direction':'ltr' if env == 'array' or proofs else None,
            'implicit':False}


def _shape(text, masked, start, stop, env, spec):
    cols = columns(spec); rows = []; events = []; cells = []
    row_start = cell_start = pos = start; band = 0

    def finish(end, delimiter_end):
        nonlocal cells, cell_start, row_start
        if not cells and not masked[cell_start:end].strip():
            cell_start = row_start = delimiter_end; return
        spans = cells + [(cell_start,end)]; row = []; column = 1
        for a,b in spans:
            item = _cell(text,masked,a,b,column,env); row.append(item)
            column += item['column_span']
        if column - 1 > len(cols): raise ValueError('too many cells for table columns')
        explicit = len(row)
        # TeX supplies the remaining empty cells when a short row ends.
        while column <= len(cols):
            row.append({'column':column, 'column_span':1, 'row_span':1, 'implicit':True,
                        'char_start':end, 'char_end':end, 'source_tex':'',
                        'sha256':sha(''), 'proof_terminators':[],
                        'required_math_direction':'ltr' if env=='array' else None})
            column += 1
        rows.append({'band':band, 'char_start':row_start, 'char_end':end,
                     'explicit_cells':explicit, 'cells':row})
        cells = []; cell_start = row_start = delimiter_end

    while pos < stop:
        char = masked[pos]
        if char == '{': _, pos = group(masked,pos); continue
        if char == '&': cells.append((cell_start,pos)); cell_start=pos+1; pos+=1; continue
        if char != '\\': pos+=1; continue
        hit = COMMAND.match(masked,pos)
        if hit is None: raise ValueError('trailing backslash')
        name = hit[1]; end = hit.end()
        if name in ('iftag','iftoggle','ifboolexpr'):
            raise ValueError('native tag/condition projection required before table shape')
        if name == 'begin':
            nested, body = group(masked,end)
            _,pos = environment_end(masked,body,nested); continue
        if name in ('\\', 'tabularnewline'):
            if masked[end:end+1]=='*': end+=1
            end = _optional(masked,end); finish(pos,end); pos=end; continue
        if name in RULES or name in BANDS or name in ('caption','label','ollabel'):
            if cells or masked[cell_start:pos].strip():
                raise ValueError('table control inside an unfinished row: '+name)
            if name == 'cline': _,end=group(masked,end)
            elif name == 'caption':
                end=_optional(masked,end); _,end=group(masked,end)
            elif name in ('label','ollabel'): _,end=group(masked,end)
            elif name in RULES: end=_optional(masked,end)
            events.append({'command':name,'char_start':pos,'char_end':end,
                           'after_row':len(rows),'band':band,'source_tex':text[pos:end]})
            if name in BANDS: band+=1
            cell_start=row_start=end; pos=end; continue
        pos=end
    finish(stop,stop)
    occupancy={}
    for row_index,row in enumerate(rows):
        for cell_index,cell in enumerate(row['cells']):
            slots=range(cell['column'],cell['column']+cell['column_span'])
            covered={occupancy[(row_index,c)] for c in slots if (row_index,c) in occupancy}
            if covered:
                if (len(covered)!=1 or cell['source_tex'].strip() or cell['row_span']!=1
                        or any((row_index,c) not in occupancy for c in slots)):
                    raise ValueError('overlapping or nonempty multirow-covered cell')
                cell['covered_by'] = list(next(iter(covered)))
            if cell['row_span']>1:
                end=row_index+cell['row_span']
                if end>len(rows) or any(r['band']!=row['band'] for r in rows[row_index:end]):
                    raise ValueError('multirow extends beyond its table band')
                for r in range(row_index+1,end):
                    for c in slots:
                        if (r,c) in occupancy: raise ValueError('overlapping multirow cells')
                        occupancy[r,c]=(row_index,cell_index)
    return {'columns':cols,'rows':rows,'events':events}


def inventory(text, source, unit=None):
    """Return every literal table, including nested and unsupported ones.

    Exact character offsets address the supplied decoded source. Commented
    examples and verbatim material are excluded; conditional/macro execution
    is deliberately not inferred. A projected input can narrow that scope.
    """
    masked=mask_comments(text); tables=[]; pos=0; ignored=[]
    while pos < len(masked):
        hit=COMMAND.search(masked,pos)
        if not hit: break
        pos=hit.end()
        if hit[1] in ('verb','Verb'):
            if masked[pos:pos+1]=='*': pos+=1
            delimiter=masked[pos:pos+1]
            end=masked.find(delimiter,pos+1) if delimiter else -1
            if end<0: raise ValueError('unclosed verbatim command')
            pos=end+1; continue
        if hit[1]!='begin': continue
        env,body=group(masked,pos)
        if env in ('verbatim','Verbatim','lstlisting','minted'):
            stop,end=environment_end(masked,body,env)
            ignored.append({'environment':env,'char_start':hit.start(),'char_end':end})
            pos=end; continue
        if env not in TABLES: continue
        start=hit.start()
        item={'id':source+'#'+str(start),'source':source,'unit':unit,
              'environment':env,'char_start':start,'line':text.count('\n',0,start)+1,
              'source_file_sha256':sha(text),'render_binding':'pending'}
        try:
            stop,end=environment_end(masked,body,env)
            item.update(char_end=end,source_tex=text[start:end],sha256=sha(text[start:end]))
            args=body
            if env=='tabular*': _,args=group(masked,args)
            args=_optional(masked,args)
            spec,args=group(masked,args)
            item['column_specification']=spec
            item.update(_shape(text,masked,args,stop,env,spec))
            item['syntax_status']='parsed'
        except ValueError as error:
            item.update(syntax_status='unsupported',error=str(error))
        tables.append(item)
        # Continue inside the table: nested tables have independent records.
        pos=body
    for item in tables:
        parents=[x for x in tables if x['char_start']<item['char_start']<x.get('char_end',-1)]
        item['parent']=max(parents,key=lambda x:x['char_start'])['id'] if parents else None
    return {'schema':'olpkit.table-source.v1','source':source,'unit':unit,
            'source_sha256':sha(text),'tables':tables,'ignored_verbatim':ignored,
            'scope':'literal source syntax; native execution and rendered cell comparison pending',
            'status':'incomplete','release_ready':False}
