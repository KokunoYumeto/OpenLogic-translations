"""Source-bound biography photographs, native captions and complete credits."""
import re,hashlib
from .macrophases import COMMAND, group, mask_comments, skip_space, digest
from .selective import definition_end


def credit_rows(pcr):
    rows=[]
    for line in pcr.splitlines():
        if not line.strip():continue
        match=re.search(r',\s*\\cpageref\s*\{',line)
        if not match:raise ValueError('native photo-credit row has no page reference')
        key,pos=group(line,match.end()-1)
        rest=line[pos:]
        if not rest.startswith(':') or not re.search(r'\\par\s*$',rest):
            raise ValueError('unsupported native photo-credit row')
        body=re.sub(r'\\par\s*$','',rest[1:]).strip()
        rows.append({'key':key,'caption_tex':line[:match.start()].strip(),'credit_tex':body})
    if not rows or len({r['key'] for r in rows})!=len(rows):raise ValueError('missing/duplicate native photo credits')
    return rows


def prepare_photos(text, labels, pcr, *, read, localized_credit_directory,
                   figure_label, credits_title, page_label, width_percent, evidence):
    if not evidence or not all((figure_label,credits_title,page_label)):
        raise ValueError('native photo settings and localized labels required')
    if not 0<width_percent<=100:raise ValueError('invalid native photo width')
    credits=credit_rows(pcr);credit_map={r['key']:r for r in credits}
    code=mask_comments(text);pos=last=0;pieces=[];photos=[]
    while pos<len(code):
        if code[pos]!='\\':pos+=1;continue
        start=pos;m=COMMAND.match(code,pos);pos=m.end()
        stop=definition_end(code,start,pos,m[1])
        if stop is not None:pos=stop;continue
        if m[1]!='olphoto':continue
        pos=skip_space(code,pos)
        if code[pos:pos+1]=='[':raise ValueError('photo-specific width needs native setting support')
        name,pos=group(code,pos);caption,end=group(code,pos)
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*',name):raise ValueError('unsafe photo asset name')
        key='photo-'+name
        if key not in labels or key not in credit_map:raise ValueError('native photo label/credit missing')
        native=labels[key]
        if native.get('kind')!='figure':raise ValueError('native photo is not a figure')
        # The native .pcr serialization inserts spaces after control words.
        # Compare all non-whitespace source symbols; emit the original authored
        # caption and credit text without changing its words or punctuation.
        compact=lambda s:re.sub(r'\s+','',mask_comments(s))
        if compact(caption)!=compact(credit_map[key]['caption_tex']):raise ValueError('native photo caption differs')
        credit_path=localized_credit_directory+'/'+name+'-credit.tex'
        credit=read(credit_path).decode('utf-8-sig').strip()
        # The native .pcr expands the copyright glyph to a circled C. This
        # equivalence is only for comparison; the authored credit is emitted.
        native_credit=lambda s:compact(re.sub(r'\\copyright\b',lambda _:r'\textcircled{C}',s))
        if native_credit(credit)!=native_credit(credit_map[key]['credit_tex']):
            raise ValueError('native localized photo credit differs: '+key)
        base='assets/photos/'+name+'/'+name
        large=read(base+'-large.png');small=read(base+'-small.png')
        if not large or not small.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('native photograph is absent/not PNG')
        number=native['number_tex']
        if not re.fullmatch(r'[A-Za-z\d.]+',number):raise ValueError('unsupported native photo number')
        output='assets/photos/'+name+'.png'
        credit_id='olp-photo-credit-'+name
        replacement='\n\n'+r'\begin{olpbookphoto}'+ '\n'+r'\label{'+key+'}\n'+r'\includegraphics{'+output+'}\n'+r'\begin{olpbookphotocaption}'+figure_label+' '+number+': '+caption+'. '+r'\hyperlink{'+credit_id+'}{'+credits_title+'}'+r'\end{olpbookphotocaption}'+'\n'+r'\end{olpbookphoto}'+'\n\n'
        pieces.extend((text[last:start],replacement));pos=last=end
        photos.append({'key':key,'name':name,'caption_tex':caption,'number_tex':number,'asset':base+'-small.png',
                       'output_asset':output,'asset_sha256':hashlib.sha256(small).hexdigest(),
                       'asset_bytes':len(small),'credit_path':credit_path,'credit_sha256':digest(credit),
                       'credit_tex':credit,'credit_id':credit_id,'source_start':start,'source_end':end})
    pieces.append(text[last:]);result=''.join(pieces)
    if [r['key'] for r in photos]!=[r['key'] for r in credits]:raise ValueError('source/native photo coverage/order differs')
    if result.count(r'\photocredits')!=1:raise ValueError('native photo-credit insertion missing/ambiguous')
    block=[r'\chapter*{'+credits_title+'}',r'\begin{olpphotocredits}']
    for row in photos:
        block.extend((r'\hypertarget{'+row['credit_id']+'}{}',row['caption_tex']+', '+page_label+'~'+r'\pageref{'+row['key']+'}: '+row['credit_tex']+r'\par'))
    block.append(r'\end{olpphotocredits}')
    result=result.replace(r'\photocredits','\n\n'.join(block))
    return result,{'schema':'olpkit.book-photos.v1','input_sha256':digest(text),'output_sha256':digest(result),
                   'native_pcr_sha256':digest(pcr),'photos':photos,'width_percent':width_percent,
                   'native_credit_equivalences':{r'\copyright':r'\textcircled{C}'},
                   'credits_title':credits_title,'figure_label':figure_label,'native_evidence':evidence,'reader_complete':False}


def bind_photos(document, receipt):
    containers=document.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpbookphoto ")]')
    if len(containers)!=len(receipt['photos']):raise ValueError('rendered photo coverage differs')
    for node,row in zip(containers,receipt['photos']):
        if len(node.xpath('.//*[@id=$key]',key=row['key']))!=1:raise ValueError('photo native anchor missing')
        images=node.xpath('.//img');captions=node.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," olpbookphotocaption ")]')
        if len(images)!=len(captions) or len(images)!=1 or images[0].get('src')!=row['output_asset']:
            raise ValueError('photo asset/caption differs')
        if captions[0].xpath('.//a/@href')!=['#'+row['credit_id']]:raise ValueError('photo-credit link differs')
        if len(document.xpath('//*[@id=$key]',key=row['credit_id']))!=1:raise ValueError('photo credit is absent')
        node.tag='figure';node.set('class','olp-book-photo')
        node.set('style','float:right;width:'+str(receipt['width_percent'])+'%;max-width:100%;margin:0 0 1em 1em')
        captions[0].tag='figcaption';captions[0].set('class','olp-photo-caption')
        images[0].set('style','width:100%;height:auto')
        # Pandoc's image alt is empty here. Use the rendered native caption name,
        # not a guessed translation or a filename.
        caption=captions[0].text_content().strip()
        prefix=receipt['figure_label']+' '+row['number_tex']+': '
        if not caption.startswith(prefix):raise ValueError('rendered native photo caption prefix differs')
        title=caption[len(prefix):].rsplit('. '+receipt['credits_title'],1)[0]
        images[0].set('alt',title)
    credits=document.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," olpphotocredits ")]')
    if len(credits)!=1:raise ValueError('complete photo-credit block missing')
    return {'photographs':len(containers),'localized_credit_rows':len(receipt['photos']),
            'native_numbering':True,'reader_complete':False}
