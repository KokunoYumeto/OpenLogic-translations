"""Preserve authored decorative book art as local, source-bound reader assets."""
from pathlib import Path
import hashlib,re,subprocess,shutil,xml.etree.ElementTree as ET


def bind_book_art(document, *, resolve, output, cover_width_percent, evidence, rasterize_pdf_hashes=()):
    if not evidence or not 0<cover_width_percent<=100:
        raise ValueError('verified native book-art configuration required')
    output=Path(output);directory=output/'assets/book-art';directory.mkdir(parents=True,exist_ok=True)
    sha=lambda b:hashlib.sha256(b).hexdigest();rows=[]
    for node in document.xpath('//img|//embed'):
        src=node.get('src','')
        if not (src.startswith(r'\olpath/') or src.startswith('illustrations/')):continue
        path,expected=resolve(src);path=Path(path);data=path.read_bytes()
        if sha(data)!=expected:raise ValueError('book-art source hash differs')
        name=re.sub('[^A-Za-z0-9_-]','-',path.stem)+'-'+expected[:12]
        method='exact_source_png'
        if path.suffix.lower()=='.pdf' and expected in rasterize_pdf_hashes:
            # Decorative authored art may use PDF clipping unsupported by an
            # SVG renderer. Preserve the actual PDF appearance and alpha; its
            # unchanged source PDF remains part of the editable book inputs.
            import fitz
            target=directory/(name+'.png')
            with fitz.open(path) as pdf:
                if len(pdf)!=1:raise ValueError('book art has more than one page')
                pix=pdf[0].get_pixmap(matrix=fitz.Matrix(240/72,240/72),alpha=True)
                pix.save(target)
            method='native_pdf_240dpi_alpha_preserving_raster_for_decorative_art'
        elif path.suffix.lower()=='.pdf':
            from pypdf import PdfReader
            if len(PdfReader(path).pages)!=1:raise ValueError('book art has more than one page')
            target=directory/(name+'.svg')
            converter=shutil.which('pdftocairo')
            if not converter:raise ValueError('native PDF-to-SVG converter unavailable')
            run=subprocess.run([converter,'-svg',str(path),str(target)],capture_output=True,timeout=30)
            if run.returncode:raise ValueError('book-art vector conversion failed')
            vector=target.read_bytes();root=ET.fromstring(vector)
            method='native_pdf_to_svg'
            for n in root.iter():
                tag=n.tag.rsplit('}',1)[-1]
                if tag in ('script','foreignObject'):raise ValueError('active content in book art')
                for key,value in n.attrib.items():
                    if key.rsplit('}',1)[-1].lower().startswith('on'):raise ValueError('event handler in book art')
                    if key.rsplit('}',1)[-1]=='href' and not value.startswith(('#','data:image/png;base64,','data:image/jpeg;base64,')):
                        raise ValueError('external reference in book art')
        elif path.suffix.lower()=='.png' and data.startswith(b'\x89PNG\r\n\x1a\n'):
            target=directory/(name+'.png')
            if not target.exists() or target.read_bytes()!=data:target.write_bytes(data)
        else:raise ValueError('unsupported source book-art format')
        node.tag='img';node.set('src',target.relative_to(output).as_posix())
        node.set('alt','');node.set('role','presentation')
        style=node.get('style','').rstrip(';')
        if '/portraits/' in src:style='width:'+str(cover_width_percent)+'%'
        elif src.startswith('illustrations/'):style='width:100%'
        node.set('style',style+';max-width:100%;object-fit:contain')
        node.set('data-source-sha256',expected)
        rows.append({'source_reference':src,'source_file':str(path),'source_sha256':expected,
                     'asset':target.relative_to(output).as_posix(),'asset_sha256':sha(target.read_bytes()),
                     'asset_bytes':target.stat().st_size,'conversion':method,
                     'role':'decorative authored art; complete attribution retained in the front matter'})
    return {'schema':'olpkit.book-art.v1','assets':rows,'native_evidence':evidence,'reader_complete':False}
