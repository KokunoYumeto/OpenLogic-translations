"""Include source-bound external TikZ assets in the ordered figure projection."""
import re,json,collections
from pathlib import PurePosixPath,Path
from .macrophases import COMMAND,group,mask_comments,skip_space
from .selective import definition_end
from .nativefigures import extract_tikz,extract_native_figures,sha
from .bookinsertions import calls


def initial_asset_width(class_source, style_source):
    """Apply the book's begin-document width, not the earlier style default."""
    code=mask_comments(class_source);assignments=[]
    for _,_,at in calls(class_source,{'AtBeginDocument'}):
        hook,_=group(code,at)
        for _,start,end in calls(hook,{'setlength'}):
            name,end=group(hook,end);value,stop=group(hook,end)
            if name==r'\olphotowidth':assignments.append((hook[start:stop],value))
    if len(assignments)!=1:raise ValueError('native begin-document asset width missing/ambiguous')
    command,value=assignments[0]
    m=re.fullmatch(r'\s*(\d*(?:\.\d+)?)\s*\\textwidth\s*',value)
    if not m or not m[1]:raise ValueError('unsupported native initial asset width')
    width=float(m[1])*100
    if not 0<width<=100:raise ValueError('native initial asset width outside text area')
    return width,{'book_class_sha256':sha(class_source.encode()),
                  'style_sha256':sha(style_source.encode()),'begin_document_width_command':command}


def expand_external_figures(text, *, read, default_width_percent, evidence):
    if not evidence or not 0<default_width_percent<=100:
        raise ValueError('verified native asset width/configuration required')
    width=default_width_percent;code=mask_comments(text);pos=last=delta=0;pieces=[];rows=[]
    def width_value(value):
        m=re.fullmatch(r'\s*(\d*(?:\.\d+)?)\s*\\(olphotowidth|textwidth)\s*',value)
        if not m:raise ValueError('unsupported native asset width: '+value)
        v=float(m[1] or 1)*(width if m[2]=='olphotowidth' else 100)
        if not 0<v<=100:raise ValueError('native asset width outside text area')
        return v
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);pos=m.end()
        stop=definition_end(code,start,pos,m[1])
        if stop is not None:pos=stop;continue
        if m[1]=='setlength':
            name,after=group(code,pos);value,end=group(code,after)
            if name==r'\olphotowidth':width=width_value(value)
            pos=end;continue
        if m[1]!='olasset':continue
        pos=skip_space(code,pos);value=r'\olphotowidth'
        if code[pos:pos+1]=='[':value,pos=group(code,pos,'[',']')
        name,end=group(code,pos);name=name.removeprefix(r'\olpath/')
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or path.suffix!='.tikz':
            raise ValueError('unsafe or unsupported external figure asset')
        data=read(name);source=data.decode('utf-8-sig');figures=extract_tikz(source)
        if len(figures)!=1:raise ValueError('external asset must contain one native TikZ picture')
        figure=figures[0]
        if mask_comments(source[:figure['char_start']]+source[figure['char_end']:]).strip():
            raise ValueError('external figure has additional executable content')
        rows.append({'asset':name,'asset_sha256':sha(data),'source_sha256':figure['source_sha256'],
                     'source_command':text[start:end],'width_percent':width_value(value),
                     'original_start':start,'original_end':end,'expanded_start':start+delta})
        pieces.extend((text[last:start],figure['source_tex']));last=pos=end
        delta+=len(figure['source_tex'])-(end-start)
    pieces.append(text[last:]);result=''.join(pieces)
    # Bind locations after expansion, including intervening inline figures.
    expanded={f['char_start']:f for f in extract_native_figures(result)}
    for row in rows:
        actual=expanded.get(row['expanded_start'])
        if not actual or actual['source_sha256']!=row['source_sha256']:
            raise ValueError('expanded external asset is absent')
        row['index']=actual['index']
    return result,{'schema':'olpkit.external-figures.v1','input_sha256':sha(text.encode()),
                   'output_sha256':sha(result.encode()),'figures':rows,'native_evidence':evidence}


def combine_exports(text, exports, output, *, external):
    """Reuse verified vector bytes from native batches without rerunning TeX."""
    from .figurebinding import checked_asset,inspect_svg
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    available=collections.defaultdict(list);evidence=[];identity=None
    for folder,record in exports:
        if record.get('status')!='vectors_exported_pending_visual_and_semantic_checks':
            raise ValueError('all native figure batches must be exported')
        current=tuple(record[k] for k in ['driver_sha256','preamble_sha256','assembly_sha256'])
        if identity is not None and current!=identity:raise ValueError('native batches have different book configurations')
        identity=current
        evidence.append({'receipt_sha256':sha(json.dumps(record,sort_keys=True).encode()),
                         'source_sha256':record['source_sha256'],'configuration':record['configuration_evidence']})
        for row in record['figures']:
            original=checked_asset(folder,row['source_file'],row['source_sha256'])
            # TeX treats CRLF and LF as the same line boundary. Preserve the
            # engine's exact witness, but match the converter's LF source.
            normalized=original.replace(b'\r\n',b'\n')
            if b'\r' in normalized:raise ValueError('unsupported native source line ending')
            available[sha(normalized)].append((Path(folder),row,original,normalized))
    widths={r['index']:r['width_percent'] for r in external['figures']}
    rows=[]
    for actual in extract_native_figures(text):
        queue=available[actual['source_sha256']]
        if not queue:raise ValueError('no exported vector for source figure: '+actual['environment']+' occurrence '+str(actual['index'])+' sha256 '+actual['source_sha256'])
        folder,native,rendered_source,original=queue.pop(0);index=actual['index']
        if original.decode('utf-8')!=actual['source_tex']:raise ValueError('native source differs')
        vector=checked_asset(folder,native['asset'],native['svg_sha256']);inspect_svg(vector)
        row={k:v for k,v in native.items() if k not in ('index','source_file','asset','source_tex')}
        row.update({'index':index,'asset':f'figure-{index:03d}.svg','source_file':f'figure-{index:03d}.tex',
                    'origin_index':native['index'],'origin_directory':str(folder)})
        if rendered_source!=original:
            row['source_sha256']=sha(original)
            row['source_normalization']={'kind':'CRLF-to-LF only','native_source_sha256':sha(rendered_source),
                                         'matched_source_sha256':sha(original),'native_source_file':native['source_file']}
        if index in widths:row['width_percent']=widths[index]
        for key,data in [('asset',vector),('source_file',original)]:
            target=output/row[key]
            if target.exists() and target.read_bytes()!=data:raise ValueError('different existing combined figure bytes')
            if not target.exists():target.write_bytes(data)
        rows.append(row)
    if any(available.values()):raise ValueError('exported figures absent from combined source')
    result={'schema':'olpkit.native-figures.v1','status':'vectors_exported_pending_visual_and_semantic_checks',
            'source_sha256':sha(text.encode()),'configuration_evidence':evidence,'figures':rows,
            'tex_runs':0,'method':'Exact vector/source byte reuse in document occurrence order; no new rendering.',
            'publishable':False}
    (output/'NATIVE_FIGURES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
