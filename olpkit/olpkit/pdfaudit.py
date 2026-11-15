"""Read actual PDF artifacts. No TeX, source rewriting or publication.

Text equality is deliberately exact Poppler output, not a normalized similarity
score. Link checks use text paint colours and annotation geometry; annotation
border colours are not evidence of readable text contrast.
"""
from collections import Counter
import difflib
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from .cache import relative_path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_record(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path':str(path), 'bytes':len(data), 'sha256':digest(data)}


def extracted_text(path):
    tool = shutil.which('pdftotext')
    if not tool:
        raise ValueError('pdftotext is required; no substitute extraction for equality')
    run = subprocess.run([tool, '-enc', 'UTF-8', str(Path(path).resolve()), '-'],
                         capture_output=True, timeout=120, check=True)
    return run.stdout, run.stderr.decode('utf-8', errors='replace')


def _winansi_type1_gid_mapper(font):
    """Resolve only independently confirmed ASCII slots of embedded Type1C.

    The PDF encoding can override the font program's encoding. Require both
    to agree with the Adobe ASCII glyph name; do not infer a mapping from a
    font name or accept an Encoding dictionary with unexamined Differences.
    Unknown bytes deliberately break the exact painted-sequence comparison.
    """
    import io
    from fontTools.agl import UV2AGL
    from fontTools.cffLib import CFFFontSet
    if font.get('/Subtype')!='/Type1' or font.get('/Encoding')!='/WinAnsiEncoding':
        return None
    descriptor=font.get('/FontDescriptor')
    descriptor=descriptor.get_object() if descriptor is not None else {}
    stream=descriptor.get('/FontFile3')
    stream=stream.get_object() if stream is not None else None
    if stream is None or stream.get('/Subtype')!='/Type1C':return None
    cff=CFFFontSet();cff.decompile(io.BytesIO(stream.get_data()),None)
    if len(cff.topDictIndex)!=1:return None
    embedded=cff.topDictIndex[0];encoding=embedded.Encoding
    if not isinstance(encoding,list) or len(encoding)!=256:return None
    glyph_ids={name:index for index,name in enumerate(embedded.charset)}
    positions={code:glyph_ids[name] for code,name in enumerate(encoding)
        if 0x20<=code<=0x7e and UV2AGL.get(code)==name and glyph_ids.get(name,0)>0}
    if not positions:return None
    return lambda code:positions.get(code,-1)


def _actualtext_glyph_coverage(page, trace, font_cache=None):
    """Match marked-content replacements to exact painted glyph occurrences.

    A font-level whitelist would hide an unmarked bad occurrence elsewhere.
    Match the complete per-font glyph sequence before accepting any coverage.
    Unsupported fonts or a sequence mismatch remain explicitly unresolved.
    """
    from pypdf.generic import ByteStringObject, TextStringObject
    import io
    font_cache={} if font_cache is None else font_cache
    def resolved(value):
        return value.get_object() if hasattr(value,'get_object') else value
    resources=page.get('/Resources',{})
    if hasattr(resources,'get_object'):resources=resources.get_object()
    content=page.get_contents()
    if content is None:return {},[],0
    raw=content.get_data()
    if b'ActualText' not in raw and not resources.get('/Properties') and not resources.get('/XObject'):
        return {},[],0
    records={};marked_fonts=set();unsupported=set();replacements=0
    def text_bytes(value):
        if isinstance(value,ByteStringObject):return bytes(value)
        if isinstance(value,TextStringObject):return value.original_bytes
        raise ValueError('unsupported PDF text operand in ActualText audit')
    def font_info(res,key):
        obj=resolved(res.get('/Font',{})).get(key)
        if obj is None:return None
        obj=resolved(obj)
        identity=id(obj)
        if identity in font_cache:return font_cache[identity]
        def font_name(value):return re.sub(r'^/[A-Z]{6}\+','',str(value)).lstrip('/')
        name=font_name(obj.get('/BaseFont',''))
        type1_mapper=_winansi_type1_gid_mapper(obj)
        if type1_mapper is not None:
            result=name,type1_mapper,1
            font_cache[identity]=result
            return result
        if obj.get('/Subtype')!='/Type0' or obj.get('/Encoding') not in ('/Identity-H','/Identity-V'):
            return name,None,0
        child=obj['/DescendantFonts'][0].get_object()
        if child.get('/Subtype')=='/CIDFontType0':
            from fontTools.cffLib import CFFFontSet
            descriptor=resolved(child.get('/FontDescriptor',{}))
            stream=resolved(descriptor.get('/FontFile3'))
            if stream is None or stream.get('/Subtype')!='/CIDFontType0C':return name,None,0
            cff=CFFFontSet();cff.decompile(io.BytesIO(stream.get_data()),None)
            if len(cff.topDictIndex)!=1:return name,None,0
            charset=cff.topDictIndex[0].charset
            cid_to_gid={0:0}
            for gid,charname in enumerate(charset[1:],1):
                if not re.fullmatch(r'cid\d+',charname):return name,None,0
                cid_to_gid[int(charname[3:])]=gid
            name=font_name('/'+cff.fontNames[0])
            # MuPDF traces CID-keyed CFF fonts with their CID, not the charset
            # array offset. Still require that the actual font contains the CID.
            result=name,(lambda code:code if code in cid_to_gid else 0),2
            font_cache[identity]=result
            return result
        if child.get('/Subtype')!='/CIDFontType2':return name,None,0
        descriptor=resolved(child.get('/FontDescriptor',{}))
        if '/FontFile2' in descriptor:
            from fontTools.ttLib import TTFont
            with TTFont(io.BytesIO(resolved(descriptor['/FontFile2']).get_data()),lazy=True) as ttf:
                postscript=ttf['name'].getDebugName(6) if 'name' in ttf else None
                if postscript:name=font_name('/'+postscript)
        mapping=child.get('/CIDToGIDMap','/Identity')
        if hasattr(mapping,'get_object'):mapping=mapping.get_object()
        if mapping=='/Identity':result=name,(lambda code:code),2
        else:
            data=mapping.get_data()
            result=name,(lambda code:int.from_bytes(data[2*code:2*code+2],'big') if 2*code+2<=len(data) else 0),2
        font_cache[identity]=result
        return result
    def walk(stream,res,marks,font=None,depth=0):
        nonlocal replacements
        if depth>16:raise ValueError('nested PDF form depth exceeds glyph-audit bound')
        stack=[];local_marks=list(marks)
        for args,op in stream.operations:
            if op==b'q':stack.append(font)
            elif op==b'Q':font=stack.pop() if stack else None
            elif op==b'Tf':font=font_info(res,args[0])
            elif op in (b'BMC',b'BDC'):
                replacement=None
                if op==b'BDC':
                    prop=args[1]
                    if not hasattr(prop,'get'):
                        prop=resolved(res.get('/Properties',{})).get(prop,{})
                    if hasattr(prop,'get_object'):prop=prop.get_object()
                    if '/ActualText' in prop:
                        value=prop['/ActualText']
                        replacement=str(value) if isinstance(value,TextStringObject) else None
                        if isinstance(value,ByteStringObject):
                            b=bytes(value)
                            if b.startswith(b'\xfe\xff'):replacement=b[2:].decode('utf-16-be')
                        if replacement is None:raise ValueError('ActualText is not a decoded PDF string')
                        if any((ord(c)<32 and c not in '\t\r\n') or 0x7f<=ord(c)<=0x9f or
                               c=='\ufffd' or (ord(c)&0xffff) in (0xfffe,0xffff) or
                               0xfdd0<=ord(c)<=0xfdef for c in replacement):
                            raise ValueError('ActualText contains an invalid character')
                        replacements+=1
                local_marks.append(replacement)
            elif op==b'EMC':
                if len(local_marks)<=len(marks):raise ValueError('unbalanced PDF marked content')
                local_marks.pop()
            elif op in (b'Tj',b'TJ',b"'",b'"') and font:
                name,mapper,width=font
                replacement=next((m for m in local_marks if m is not None),None)
                if replacement is not None:marked_fonts.add(name)
                if mapper is None:
                    if replacement is not None:unsupported.add(name)
                    continue
                strings=args[0] if op==b'TJ' else [args[-1]]
                for item in strings:
                    if not isinstance(item,(ByteStringObject,TextStringObject)):continue
                    b=text_bytes(item)
                    if len(b)%width:raise ValueError('misaligned PDF glyph string')
                    for i in range(0,len(b),width):
                        gid=mapper(int.from_bytes(b[i:i+width],'big'))
                        records.setdefault(name,[]).append((gid,replacement))
            elif op==b'Do':
                obj=resolved(res.get('/XObject',{})).get(args[0])
                if obj is None:continue
                obj=obj.get_object()
                if obj.get('/Subtype')=='/Form':
                    from pypdf.generic import ContentStream
                    child_res=obj.get('/Resources',res)
                    if hasattr(child_res,'get_object'):child_res=child_res.get_object()
                    walk(ContentStream(obj,page.pdf),child_res,local_marks,font,depth+1)
        if len(local_marks)!=len(marks):raise ValueError('unclosed PDF marked content')
    walk(content,resources,[])
    observed={}
    for span in trace:
        for code,gid,origin,bbox in span['chars']:
            if gid>=0:observed.setdefault(span['font'],[]).append(gid)
    matched={};unknown=[]
    for name in marked_fonts:
        expected=records.get(name,[])
        if name in unsupported or [r[0] for r in expected]!=observed.get(name,[]):
            unknown.append({'font':name,'reason':'ActualText glyph sequence is unsupported or differs',
                'encoded_glyphs':len(expected),'observed_glyphs':len(observed.get(name,[]))})
        else:matched[name]=expected
    return matched,unknown,replacements


def inspect_glyphs(path):
    """Inspect encoded glyphs, including failures hidden by word-extractor fallback.

    MuPDF's text trace can expose an unmapped glyph as U+FFFD even when its
    ordinary text extractor guesses a plausible ASCII character. Poppler is
    checked separately because the two extractors expose different controls.
    Private-use values are unresolved evidence, never automatically a pass.
    """
    import fitz
    from pypdf import PdfReader
    artifact=file_record(path)
    groups={};private={};squares=Counter();fonts=Counter();painted=0
    reader=PdfReader(path);actualtext_unknown=[];covered=0;replacement_spans=0;font_cache={}
    def add(store,rule,page,font,code,glyph_id,position=None,context=None):
        key=(rule,font,code,glyph_id)
        row=store.setdefault(key,{'rule':rule,'font':font,'unicode':f'U+{code:04X}',
            'glyph_id':glyph_id,'occurrences':0,'pages':{},'examples':[]})
        row['occurrences']+=1
        row['pages'][page]=row['pages'].get(page,0)+1
        # Counts cover all occurrences. Positions are bounded diagnostic examples.
        if len(row['examples'])<6:
            row['examples'].append({'page':page,**({'bbox':list(position)} if position else {}),
                                    **({'context':context} if context is not None else {})})
    def control(code):
        return (code<32 and code not in (9,10,13)) or 0x7f<=code<=0x9f
    def private_use(code):
        return 0xe000<=code<=0xf8ff or 0xf0000<=code<=0xffffd or 0x100000<=code<=0x10fffd
    with fitz.open(path) as doc:
        pages=len(doc)
        for number,page in enumerate(doc,1):
            trace=page.get_texttrace()
            coverage,unknown,spans=_actualtext_glyph_coverage(reader.pages[number-1],trace,font_cache)
            actualtext_unknown.extend({'page':number,**x} for x in unknown)
            replacement_spans+=spans
            unresolved_fonts={x['font'] for x in unknown};positions=Counter()
            for span in trace:
                font=span['font']
                for code,gid,origin,bbox in span['chars']:
                    painted+=1;fonts[font]+=1
                    replacement=None
                    if gid>=0:
                        if font in coverage:replacement=coverage[font][positions[font]][1]
                        positions[font]+=1
                    if gid==0:
                        add(groups,'notdef-glyph',number,font,code,gid,bbox)
                        continue
                    if replacement is not None:
                        covered+=1
                        for char in replacement:
                            if private_use(ord(char)):
                                add(private,'actualtext-private-use-needs-source-review',number,font,ord(char),gid,bbox)
                        continue
                    if font in unresolved_fonts:
                        continue
                    if code==0xfffd or (code&0xffff) in (0xfffe,0xffff) or 0xfdd0<=code<=0xfdef:
                        add(groups,'unmapped-or-invalid-glyph',number,font,code,gid,bbox)
                    elif control(code):
                        add(groups,'control-glyph',number,font,code,gid,bbox)
                    elif private_use(code):
                        add(private,'private-use-needs-source-review',number,font,code,gid,bbox)
                    if code in (0x25a0,0x25a1):squares[f'U+{code:04X}']+=1
    raw,warnings=extracted_text(path)
    for number,page in enumerate(raw.decode('utf-8').split('\f'),1):
        for i,char in enumerate(page):
            code=ord(char)
            if control(code) or code==0xfffd:
                add(groups,'poppler-invalid-character',number,None,code,None,
                    context=page[max(0,i-40):i+41])
    if file_record(path)!=artifact:raise ValueError('PDF bytes changed during glyph inspection')
    issues=list(groups.values());unmeasured=list(private.values())
    return {'schema':'olpkit.pdf-glyphs.v1','artifact':artifact,'pages':pages,
        'status':'fail' if issues else ('incomplete' if unmeasured or warnings or actualtext_unknown else 'pass'),
        'painted_glyphs_inspected':painted,'font_glyph_counts':dict(fonts),
        'unmapped_trace_glyphs':sum(x['occurrences'] for x in issues if x['rule']=='unmapped-or-invalid-glyph'),
        'notdef_glyphs':sum(x['occurrences'] for x in issues if x['rule']=='notdef-glyph'),
        'trace_control_glyphs':sum(x['occurrences'] for x in issues if x['rule']=='control-glyph'),
        'poppler_invalid_characters':sum(x['occurrences'] for x in issues if x['rule']=='poppler-invalid-character'),
        'private_use_glyphs':sum(x['occurrences'] for x in unmeasured),
        'issues':issues,'unmeasured':unmeasured,'extraction_warnings':warnings,
        'actualtext':{'spans':replacement_spans,'covered_glyph_occurrences':covered,'unmeasured':actualtext_unknown},
        'poppler_text_sha256':digest(raw),'square_codepoints':dict(squares),
        'limits':['Complete glyph counts and per-page counts; at most six position/context examples per group.',
                  'Legitimate square codepoints are not missing glyphs; proof-end classification requires source context.',
                  'This checks extractable encoding, not the intended mathematical meaning or every rendered glyph shape.',
                  'ActualText coverage is accepted only after exact marked-content/per-font glyph-sequence matching; its semantic accuracy still requires source comparison.',
                  'Private-use mappings and unsupported ActualText sequences remain unresolved, not automatically waived.']}


def compare_pdfs(first, second, first_build=None, second_build=None):
    from pypdf import PdfReader
    paths = [Path(first).resolve(), Path(second).resolve()]
    texts, warnings = zip(*(extracted_text(p) for p in paths))
    records = [file_record(p) for p in paths]
    pages = [len(PdfReader(p).pages) for p in paths]
    equal = pages[0] == pages[1] and texts[0] == texts[1]
    reproducibility = {'status':'not_established', 'reason':'Two verified independent build receipts required.'}
    if bool(first_build) != bool(second_build):
        raise ValueError('provide both build receipts or neither')
    if first_build and second_build:
        receipts = [Path(first_build).resolve(), Path(second_build).resolve()]
        checks = []
        builds = []
        for receipt, pdf, record in zip(receipts, paths, records):
            build = json.loads(receipt.read_text(encoding='utf-8-sig'))
            if not build.get('pdf') or not build.get('commands') or not build.get('passes'):
                raise ValueError('receipt does not record a completed PDF build')
            declared = (receipt.parent / build['pdf']['path']).resolve()
            if declared != pdf or build['pdf']['sha256'] != record['sha256']:
                raise ValueError('build receipt does not bind the compared PDF bytes')
            if any(c.get('exit_code') != 0 or c.get('timed_out') for c in build['commands']):
                raise ValueError('build receipt contains a failed command')
            source_root=(receipt.parent/'source').resolve()
            for name,item in build.get('source_inputs',{}).items():
                relative_path(name)
                source=(source_root/name).resolve()
                if not source.is_relative_to(source_root) or not source.is_file() or digest(source.read_bytes())!=item['sha256']:
                    raise ValueError('build input bytes no longer match receipt: '+name)
            builds.append(build)
            checks.append(file_record(receipt))
        if receipts[0] == receipts[1] or paths[0] == paths[1]:
            raise ValueError('independent builds require distinct receipts and PDF paths')
        for key in ('source_inputs','source_date_epoch','engine_version'):
            if not builds[0].get(key) or builds[0][key] != builds[1].get(key):
                raise ValueError('builds do not have identical '+key)
        pids = [{c.get('process_id') for c in b['commands']} for b in builds]
        if None in pids[0] or None in pids[1] or pids[0] == pids[1]:
            raise ValueError('build process evidence is absent or duplicated')
        reproducibility = {'status':'pass' if equal else 'fail', 'receipts':checks,
                           'same_source_inputs':True, 'same_engine_version':True,
                           'same_source_date_epoch':True}
    return {'schema':'olpkit.pdf-compare.v1', 'artifacts':records, 'pages':pages,
            'text_sha256':[digest(t) for t in texts], 'extraction_warnings':list(warnings),
            'text_equal':texts[0] == texts[1], 'pages_equal':pages[0] == pages[1],
            'status':'equal' if equal else 'different', 'G-SAME':reproducibility,
            'difference_preview':list(difflib.unified_diff(texts[0].decode('utf-8').splitlines(),
                texts[1].decode('utf-8').splitlines(),fromfile='first',tofile='second'))[:100]}, texts


def rgb(value):
    if isinstance(value,(int,float)):
        result = (float(value),)*3
    elif isinstance(value,(tuple,list)) and len(value) in (1,3):
        result = tuple(float(v) for v in value)
        if len(result)==1: result *= 3
    else:
        raise ValueError('unsupported colour space; do not guess CMYK/ICC conversion')
    if any(v < 0 or v > 1 for v in result):
        raise ValueError('colour component outside [0,1]')
    return result


def contrast(foreground,background=(1,1,1)):
    def luminance(c):
        values = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in rgb(c)]
        return sum(a*b for a,b in zip(values,(.2126,.7152,.0722)))
    lo,hi = sorted((luminance(foreground),luminance(background)))
    return (hi+.05)/(lo+.05)


def contains(rect,char):
    x=(char['x0']+char['x1'])/2; y=(char['top']+char['bottom'])/2
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def intersects(a,b):
    return min(a[2],b[2]) > max(a[0],b[0]) and min(a[3],b[3]) > max(a[1],b[1])


def split_citations(links,chars):
    """Find same-line, same-bibliography destinations with intervening unlinked ink.

    Two separate mentions of the same work can also trigger this condition; keep
    the exact spans for source-context review instead of silently suppressing it.
    """
    found=[]
    for i,left in enumerate(links):
        if not left['destination'].startswith('cite.'):
            continue
        for right in links[i+1:]:
            if left['destination'] != right['destination']: continue
            a,b=sorted((left,right),key=lambda item:item['rect'][0])
            ra,rb=a['rect'],b['rect']
            top,bottom=max(ra[1],rb[1]),min(ra[3],rb[3])
            if rb[0] <= ra[2] or bottom-top < .5*min(ra[3]-ra[1],rb[3]-rb[1]): continue
            gap=[c for c in chars if c['text'].strip() and contains((ra[2],top,rb[0],bottom),c)
                 and not any(contains(l['rect'],c) for l in links)]
            if gap:
                found.append({'destination':a['destination'],'first':a['index'],'second':b['index'],
                              'unlinked_text':''.join(c['text'] for c in sorted(gap,key=lambda c:c['x0'])),
                              'rectangles':[ra,rb]})
    return found


def serialized_link_rgb(color):
    # The xcolor HTML conversion used by this XeLaTeX profile emits RGB
    # components rounded to three decimal places in the PDF content stream.
    return tuple(float((Decimal(int(color[i:i+2],16))/255).quantize(
        Decimal('0.001'),rounding=ROUND_HALF_UP)) for i in (0,2,4))


def inspect_links(path,minimum_contrast=7,progress=None,expected_color=None,*,xdvipdfmx=False):
    from pypdf import PdfReader
    import pdfplumber
    import fitz
    if minimum_contrast < 7:
        raise ValueError('link contrast acceptance cannot be below 7:1')
    expected_rgb=None
    if expected_color is not None:
        if not isinstance(expected_color,str) or not re.fullmatch(r'[0-9a-fA-F]{6}',expected_color):
            raise ValueError('expected link colour must be six hexadecimal digits')
        expected_rgb=tuple(int(expected_color[i:i+2],16)/255 for i in (0,2,4))
    pdf = PdfReader(path)
    observations=[]; issues=[]; unknown=[]; colours=Counter(); citation_count=0
    with pdfplumber.open(path) as parsed, fitz.open(path) as painted:
        if len(parsed.pages)!=len(pdf.pages):
            raise ValueError('PDF parsers disagree on page coverage')
        if len(painted)!=len(pdf.pages):raise ValueError('paint trace page coverage differs')
        for number,(page,geometry) in enumerate(zip(pdf.pages,parsed.pages),1):
            links=[]
            if int(page.get('/Rotate',0)) % 360 or list(page.mediabox)[:2] != [0,0] or page.cropbox != page.mediabox:
                unknown.append({'page':number,'reason':'rotated, shifted or cropped coordinate space'})
                geometry.close();continue
            height=float(page.mediabox.height)
            for index,ref in enumerate(page.get('/Annots',[])):
                obj=ref.get_object()
                if obj.get('/Subtype')!='/Link': continue
                action=obj.get('/A',{})
                if hasattr(action,'get_object'): action=action.get_object()
                destination=obj.get('/Dest', action.get('/D',action.get('/URI')))
                kind='uri' if action.get('/S')=='/URI' else 'internal'
                if not isinstance(destination,str) or '/QuadPoints' in obj or '/Rect' not in obj:
                    unknown.append({'page':number,'index':index,'reason':'unsupported link destination or geometry'});continue
                x0,y0,x1,y1=map(float,obj['/Rect'])
                links.append({'index':index,'destination':destination,'kind':kind,
                              'rect':[min(x0,x1),height-max(y0,y1),max(x0,x1),height-min(y0,y1)]})
            if not links:
                geometry.close();continue
            chars=geometry.chars
            paint_chars=[]
            if xdvipdfmx:
                # PDFMiner's font-descriptor boxes can include a superscript
                # from the next line in this link. Use actual painted glyph
                # trace geometry, also used by the background/raster check.
                for span in painted[number-1].get_texttrace():
                    for code,gid,origin,box in span['chars']:
                        if gid<0 or not chr(code).strip():continue
                        paint_chars.append({'text':chr(code),'x0':box[0],'top':box[1],
                            'x1':box[2],'bottom':box[3],'non_stroking_color':span['color'],
                            'opaque_fill':span.get('type')==0 and span.get('opacity')==1})
            for link in links:
                ink=[c for c in chars if c['text'].strip() and contains(link['rect'],c)]
                colour_ink=([c for c in paint_chars if contains(link['rect'],c)] if xdvipdfmx else ink)
                if not colour_ink:
                    unknown.append({'page':number,'index':link['index'],'reason':'link has no extractable painted text'})
                measured=[]; paints=set()
                for c in colour_ink:
                    if xdvipdfmx and not c['opaque_fill']:
                        unknown.append({'page':number,'index':link['index'],'reason':'linked text paint is not an opaque fill'});continue
                    try: paint=rgb(c.get('non_stroking_color'))
                    except (ValueError,TypeError):
                        unknown.append({'page':number,'index':link['index'],'reason':'unsupported text colour'});continue
                    serialized=tuple(round(x,6) for x in paint)
                    colours[serialized]+=1
                    paints.add(serialized)
                    measured.append(contrast(paint))
                # Unpainted PDF paper is white. A coloured filled object/image
                # behind a link requires a rendered measurement, not this gate.
                for image in geometry.images:
                    if intersects(link['rect'],[image['x0'],image['top'],image['x1'],image['bottom']]):
                        unknown.append({'page':number,'index':link['index'],'reason':'image overlaps link background'})
                for shape in geometry.rects+geometry.curves:
                    if shape.get('fill') and intersects(link['rect'],[shape['x0'],shape['top'],shape['x1'],shape['bottom']]):
                        try: white=rgb(shape.get('non_stroking_color'))==(1,1,1)
                        except (ValueError,TypeError):white=False
                        if not white:unknown.append({'page':number,'index':link['index'],'reason':'non-white vector fill overlaps link background'})
                if measured and min(measured)<minimum_contrast:
                    issues.append({'page':number,'index':link['index'],'rule':'contrast','minimum':min(measured)})
                observations.append({'page':number,**link,'text':''.join(c['text'] for c in ink),
                                     'minimum_contrast':min(measured) if measured else None,
                                     'text_rgb':sorted(paints)})
                citation_count += int(link['destination'].startswith('cite.'))
            issues.extend({'page':number,'rule':'split-citation',**x} for x in split_citations(links,chars))
            geometry.close()
            if progress and number%50==0:progress(number)
    if len(colours)>1:issues.append({'rule':'multiple-link-text-colours','count':len(colours)})
    if expected_rgb is not None:
        serialized=serialized_link_rgb(expected_color) if xdvipdfmx else None
        for actual in colours:
            if actual==serialized:
                continue
            if xdvipdfmx:
                matches = actual==tuple(round(value,6) for value in expected_rgb)
            else:
                matches = all(abs(a-b)<=0.0001 for a,b in zip(actual,expected_rgb))
            if not matches:
                issues.append({'rule':'declared-link-colour-overridden','expected_rgb':list(expected_rgb),'actual_rgb':list(actual)})
    measurements=[]
    if unknown:
        try:
            from .linkpaint import measure_unresolved
        except ModuleNotFoundError as error:
            if error.name!='fitz':
                raise
        else:
            unknown, paint_issues, measurements = measure_unresolved(path,observations,unknown,minimum_contrast)
            issues.extend(paint_issues)
    return {'schema':'olpkit.pdf-links.v1','artifact':file_record(path),'pages':len(pdf.pages),
            'status':'fail' if issues else ('incomplete' if unknown else ('pass' if observations else 'not_applicable')),
            'minimum_required_contrast':minimum_contrast,'link_areas':len(observations),
            'expected_colour':expected_color,
            'citation_areas':citation_count,'text_colours':[{'rgb':list(k),'characters':v,'contrast_white':contrast(k)} for k,v in colours.items()],
            'issues':issues,'unmeasured':unknown,'observations':observations,
            'background_measurements':measurements,
            'limits':['Non-white fills and non-text links require supported paint-order and raster evidence.',
                      'XeLaTeX link colours use painted-glyph trace geometry; nearby extracted text is diagnostic, not an exact link-content transcription.',
                      'Citation split candidates require source-context adjudication when distinct mentions share a destination.',
                      'This gate does not certify link destinations exist, reading order, semantic fidelity, table layout or font scale.']}


def pdf_command(action,first,second,out,first_build=None,second_build=None):
    folder=Path(out)
    if folder.exists():raise ValueError('preserve prior PDF audit; choose a new output folder')
    folder.mkdir(parents=True)
    if action=='compare':
        if not second:raise ValueError('PDF comparison requires --second')
        report,texts=compare_pdfs(first,second,first_build,second_build)
        for n,text in enumerate(texts,1):(folder/f'text-{n}.txt').write_bytes(text)
        ok=report['status']=='equal'
    elif action=='glyphs':
        report=inspect_glyphs(first)
        ok=report['status']=='pass'
    else:
        report=inspect_links(first,progress=lambda page:print(f'PDF links: inspected page {page}',flush=True))
        ok=report['status']=='pass'
    (folder/'REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','pages','link_areas','citation_areas','text_equal','pages_equal',
        'unmapped_trace_glyphs','poppler_invalid_characters','private_use_glyphs') if k in report}))
    return int(not ok)
