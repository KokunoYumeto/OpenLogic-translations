"""Preserve source table cells/rules before the Pandoc text-table reader.

Pandoc's LaTeX reader can print cline arguments as cell text and displace row
labels. Parse those rules explicitly; keep all cell mathematics for Pandoc's
MathML converter and restore borders from the source, not rendered guesses.
"""
import re
from .macrophases import COMMAND, group
from .selective import environment_end, token


def column_spec(value):
    value = re.sub(r'\s+', '', value)
    if not re.fullmatch(r'\|?[lcr](?:\|?[lcr])*\|?', value):
        raise ValueError('unsupported table column specification')
    columns = []
    for i, char in enumerate(value):
        if char in 'lcr':
            columns.append({'align': {'l':'left','c':'center','r':'right'}[char],
                            'left': i>0 and value[i-1]=='|',
                            'right': i+1<len(value) and value[i+1]=='|'})
    return columns


def parse_tabular(text):
    opening = re.match(r'\\begin\s*\{tabular\}', text)
    if not opening: raise ValueError('expected tabular')
    spec, start = group(text, opening.end())
    columns = column_spec(spec)
    stop, end = environment_end(text, start, 'tabular')
    if text[end:].strip(): raise ValueError('unconsumed table input')
    body = text[start:stop]
    rows, rules, cells, current = [], [], [], []
    pos = 0

    def cell(source, column):
        value = source.strip()
        original = value
        span = 1
        local_spec = None
        if value.startswith(r'\multicolumn'):
            count, at, _ = token(value, len(r'\multicolumn'))
            local_spec, at, _ = token(value, at)
            value, end, _ = token(value, at)
            if original[end:].strip(): raise ValueError('content outside multicolumn')
            if not count.isdigit() or int(count)<1: raise ValueError('invalid column span')
            span = int(count)
            styles = column_spec(local_spec)
            if len(styles)!=1: raise ValueError('multicolumn must have one alignment')
            style = styles[0]
        else:
            if column>=len(columns): raise ValueError('too many table cells')
            style = columns[column]
        # A text-mode phantom is invisible but contributes width. Move its
        # contained ensuremath inside math mode, retaining mphantom in MathML.
        if value.startswith(r'\phantom'):
            phantom, pend, _ = token(value, len(r'\phantom'))
            if value[pend:].strip() or not phantom.startswith(r'\ensuremath'):
                raise ValueError('unsupported table phantom')
            math, mend, _ = token(phantom, len(r'\ensuremath'))
            if phantom[mend:].strip(): raise ValueError('unsupported phantom content')
            value = r'$\phantom{'+math+'}$'
        render = value if span==1 else r'\multicolumn{'+str(span)+'}{'+local_spec.replace('|','')+'}{'+value+'}'
        return {'source_tex': original, 'render_tex': render, 'column': column+1,
                'span':span, **style}

    def finish():
        cells.append(''.join(current))
        row=[]; col=0
        for source in cells:
            item=cell(source,col); row.append(item); col+=item['span']
        if col != len(columns): raise ValueError('table row width differs from source columns')
        rows.append(row); cells.clear(); current.clear()

    while pos < len(body):
        if body[pos]=='{':
            _, end=group(body,pos); current.append(body[pos:end]);pos=end;continue
        if body[pos]=='&':
            cells.append(''.join(current));current.clear();pos+=1;continue
        if body[pos]!='\\':
            current.append(body[pos]);pos+=1;continue
        command=COMMAND.match(body,pos)
        name=command[1]
        if name in ('cline','hline'):
            if cells or ''.join(current).strip(): raise ValueError('table rule inside a row')
            current.clear()
            if name=='cline':
                value,end,_=token(body,command.end())
                hit=re.fullmatch(r'(\d+)-(\d+)',value)
                if not hit: raise ValueError('invalid cline')
                a,b=map(int,hit.groups())
            else: a,b,end=1,len(columns),command.end()
            if not 1<=a<=b<=len(columns): raise ValueError('cline outside columns')
            rules.append({'boundary':len(rows),'first_column':a,'last_column':b})
            pos=end;continue
        if name=='\\':
            finish();pos=command.end();continue
        if name=='begin':
            env,at=group(body,command.end());_,end=environment_end(body,at,env)
            current.append(body[pos:end]);pos=end;continue
        current.append(command[0]);pos=command.end()
    if cells or ''.join(current).strip(): finish()
    if not rows: raise ValueError('empty table')
    normalized = (r'\begin{tabular}{'+''.join({'left':'l','center':'c','right':'r'}[x['align']] for x in columns)+'}\n'+
                  '\\\\\n'.join(' & '.join(c['render_tex'] for c in row) for row in rows)+'\n'+r'\end{tabular}')
    return normalized, {'columns':len(columns),'rows':rows,'rules':rules,'source_tex':text}


def bind_tables(document, tables):
    """Apply source rules to exactly one table between each marker pair."""
    bound=[]
    for item in tables:
        marker=item['marker']
        matches=[p for p in document.xpath('//p') if p.text_content().strip()==marker+'START']
        if len(matches)!=1: raise ValueError('table start marker missing/duplicated')
        start=matches[0]; table=start.getnext(); end=table.getnext() if table is not None else None
        if table is None or table.tag!='table' or end is None or end.tag!='p' or end.text_content().strip()!=marker+'END':
            raise ValueError('table marker boundary mismatch')
        rows=table.xpath('./thead/tr|./tbody/tr|./tr')
        if len(rows)!=len(item['rows']): raise ValueError('rendered table row count differs')
        for index,(rendered,expected) in enumerate(zip(rows,item['rows'])):
            if len(rendered)!=len(expected): raise ValueError('rendered table cell count differs')
            for cell,source in zip(rendered,expected):
                if int(cell.get('colspan','1'))!=source['span']: raise ValueError('rendered column span differs')
                styles=['text-align: '+source['align'],'padding: 0.15em 0.55em']
                for side in ('left','right'):
                    if source[side]: styles.append('border-'+side+': 0.4pt solid currentColor')
                for edge,boundary in (('top',index),('bottom',index+1)):
                    for rule in item['rules']:
                        if rule['boundary']!=boundary: continue
                        first,last=source['column'],source['column']+source['span']-1
                        if first<=rule['last_column'] and last>=rule['first_column']:
                            if not (rule['first_column']<=first<=last<=rule['last_column']):
                                raise ValueError('partial rule across a spanned cell needs explicit layout')
                            styles.append('border-'+edge+': 0.4pt solid currentColor')
                cell.set('style','; '.join(styles))
                cell.set('data-source-tex',source['source_tex'])
        table.set('style','border-collapse: collapse; margin-inline: auto')
        table.set('data-source-tex',item['source_tex'])
        start.getparent().remove(start);end.getparent().remove(end)
        bound.append(marker)
    return {'bound':len(bound),'accessibility_header_review':'pending'}
