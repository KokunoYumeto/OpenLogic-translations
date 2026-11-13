"""Read actual PDF artifacts. No TeX, source rewriting or publication.

Text equality is deliberately exact Poppler output, not a normalized similarity
score. Link checks use text paint colours and annotation geometry; annotation
border colours are not evidence of readable text contrast.
"""
from collections import Counter
import difflib
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


def inspect_links(path,minimum_contrast=7,progress=None):
    from pypdf import PdfReader
    import pdfplumber
    if minimum_contrast < 7:
        raise ValueError('link contrast acceptance cannot be below 7:1')
    pdf = PdfReader(path)
    observations=[]; issues=[]; unknown=[]; colours=Counter(); citation_count=0
    with pdfplumber.open(path) as parsed:
        if len(parsed.pages)!=len(pdf.pages):
            raise ValueError('PDF parsers disagree on page coverage')
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
            for link in links:
                ink=[c for c in chars if c['text'].strip() and contains(link['rect'],c)]
                if not ink:
                    unknown.append({'page':number,'index':link['index'],'reason':'link has no extractable painted text'})
                measured=[]
                for c in ink:
                    try: paint=rgb(c.get('non_stroking_color'))
                    except (ValueError,TypeError):
                        unknown.append({'page':number,'index':link['index'],'reason':'unsupported text colour'});continue
                    colours[tuple(round(x,6) for x in paint)]+=1
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
                                     'minimum_contrast':min(measured) if measured else None})
                citation_count += int(link['destination'].startswith('cite.'))
            issues.extend({'page':number,'rule':'split-citation',**x} for x in split_citations(links,chars))
            geometry.close()
            if progress and number%50==0:progress(number)
    if len(colours)>1:issues.append({'rule':'multiple-link-text-colours','count':len(colours)})
    return {'schema':'olpkit.pdf-links.v1','artifact':file_record(path),'pages':len(pdf.pages),
            'status':'fail' if issues else ('incomplete' if unknown else ('pass' if observations else 'not_applicable')),
            'minimum_required_contrast':minimum_contrast,'link_areas':len(observations),
            'citation_areas':citation_count,'text_colours':[{'rgb':list(k),'characters':v,'contrast_white':contrast(k)} for k,v in colours.items()],
            'issues':issues,'unmeasured':unknown,'observations':observations,
            'limits':['Background accepted only for unpainted white paper or white vector fill; other overlaps require rendering.',
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
    else:
        report=inspect_links(first,progress=lambda page:print(f'PDF links: inspected page {page}',flush=True))
        ok=report['status']=='pass'
    (folder/'REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','pages','link_areas','citation_areas','text_equal','pages_equal') if k in report}))
    return int(not ok)
