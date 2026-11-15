"""Rebuild both editable forms from the exact release ZIP."""
from pathlib import Path, PurePosixPath
import json
import stat
from zipfile import ZipFile

from .assembly import digest, json_bytes
from .build import settle_tex
from .cache import relative_path
from .pdfaudit import compare_pdfs
from .process import TeXSlot
from .recorder import content_inputs, read_inputs
from .schemas import ROOT


def unpack(archive, members, dest):
    dest.mkdir(parents=True, exist_ok=False)
    with ZipFile(archive) as package:
        names = package.namelist()
        if set(names) != set(members) or len({n.casefold() for n in names}) != len(names):
            raise ValueError('archive and declared member lists differ')
        for info in package.infolist():
            relative = relative_path(info.filename)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if info.is_dir() or mode not in (0, stat.S_IFREG):
                raise ValueError('unexpected non-file archive member')
            record = members[info.filename]
            if info.file_size != record['bytes']:
                raise ValueError('incorrect archive member size: ' + info.filename)
            data = package.read(info)
            if digest(data) != record['sha256']:
                raise ValueError('incorrect archive member digest: ' + info.filename)
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
    checksums = ''.join(r['sha256'] + '  ' + k + '\n' for k, r in sorted(members.items())
                        if k != 'SOURCE-SHA256SUMS.txt')
    if (dest / 'SOURCE-SHA256SUMS.txt').read_bytes() != checksums.encode('utf-8'):
        raise ValueError('internal source manifest differs from the export receipt')


def compare_pages(original, rebuilt):
    import fitz
    text, _ = compare_pdfs(original, rebuilt)
    changed = []
    with fitz.open(original) as first, fitz.open(rebuilt) as second:
        for left, right in zip(first, second):
            options = dict(matrix=fitz.Matrix(2, 2), colorspace=fitz.csRGB, alpha=False)
            a, b = left.get_pixmap(**options), right.get_pixmap(**options)
            if left.rect != right.rect or (a.width, a.height, a.digest) != (b.width, b.height, b.digest):
                changed.append(left.number + 1)
    return {'page_counts': text['pages'], 'text_sha256': text['text_sha256'],
            'pages_equal': text['pages_equal'], 'text_equal': text['text_equal'],
            'render_dpi': 144, 'different_rendered_pages': changed,
            'pass': text['status'] == 'equal' and not changed}


def inspect_compiled(mode, tree, job, build, export, native, result):
    book = relative_path(build['book_directory'])
    cwd = tree / book
    inputs = read_inputs(cwd / (job + '.fls'), cwd)
    external = {(r['path'], r['sha256']) for r in build['recorder_inputs'] if r['kind'] == 'toolchain'}
    for path in inputs:
        if path.is_file() and not path.is_relative_to(tree) and (path.name, digest(path.read_bytes())) not in external:
            raise ValueError('unaccounted external TeX input: ' + path.name)
    found, wrong = content_inputs(inputs, tree, export['locale'])
    embedded = {p.name for p in inputs if p.parent == cwd and p.name.startswith('olpkit-olp-')}
    expected = {r['embedded'] for r in export['embedded'] if r['embedded'].startswith('olpkit-olp-')}
    if (not expected or len(expected) != export['units'] or wrong
            or (mode == 'modular' and (found != build['content_inputs'] or embedded))
            or (mode == 'cumulative' and (found or embedded != expected))):
        raise ValueError(mode + ' reader did not read the exact exported units')
    result['recorded_units'] = len(found) + len(embedded)
    declared_book = {r['path']: r['embedded'] for r in export['embedded']
                     if r['embedded'].startswith('olpkit-book-')}
    native_inputs = {r['path'] for r in build['recorder_inputs'] if r['kind'] == 'assembled-tree'}
    used_book = set(declared_book) & native_inputs
    read_paths = {p.relative_to(tree).as_posix() for p in inputs if p.is_relative_to(tree)}
    original_book = set(declared_book) & read_paths
    embedded_book = {p.name for p in inputs if p.parent == cwd and p.name.startswith('olpkit-book-')}
    expected_book = {declared_book[path] for path in used_book}
    result['book_inputs'] = {'native': sorted(used_book), 'modular': sorted(original_book),
                             'embedded': sorted(embedded_book)}
    # TeX opens the original filename to test its existence when a
    # kernel file substitution is active. Check which files executed.
    indirect = set(export.get('package_book_input_lookups', ()))
    log_bytes = (cwd / (job + '.log')).read_bytes()
    executed_originals = [path for path in original_book & indirect
                          if ('(' + PurePosixPath(path).relative_to(book).as_posix()).encode() in log_bytes]
    if (mode == 'modular' and (original_book != used_book or embedded_book)
            or mode == 'cumulative' and (original_book - indirect or executed_originals
                                          or embedded_book != expected_book)):
        raise ValueError(mode + ' reader bypassed editable book inputs')
    pdf = cwd / (job + '.pdf')
    result['pdf_sha256'] = digest(pdf.read_bytes())
    result['comparison'] = compare_pages(native, pdf)
    if not result['comparison']['pass']:
        raise ValueError(mode + ' reader differs from the native PDF')
    result['status'] = 'pass'


def verify_package(export_file, build_file, out, *, mode_choice="both"):
    export_file = Path(export_file).resolve()
    build_file = Path(build_file).resolve()
    out = Path(out).resolve()
    boundary = (ROOT.parent / 'out').resolve()
    if out == boundary or not out.is_relative_to(boundary) or out.exists():
        raise ValueError('package verification requires a fresh named output folder')
    export = json.loads(export_file.read_bytes())
    build = json.loads(build_file.read_bytes())
    package = export['package']
    if (export['product'] != 'source-zip' or package['build_sha256'] != digest(build_file.read_bytes())
            or export['assembly_sha256'] != build['assembly_sha256']):
        raise ValueError('export and native build receipts do not match')
    native = build_file.parent / relative_path(build['pdf']['path'])
    native_hash = digest(native.read_bytes())
    if native_hash != package['pdf_sha256'] or native_hash != build['pdf']['sha256']:
        raise ValueError('native PDF differs from the source package witness')
    assets = {}
    for name, record in export['outputs'].items():
        path = export_file.parent / relative_path(name)
        if (path.parent != export_file.parent or path.suffix in assets or path.stat().st_size != record['bytes']
                or digest(path.read_bytes()) != record['sha256']):
            raise ValueError('source artifact differs: ' + name)
        assets[path.suffix] = path
    if set(assets) != {'.zip', '.tex'}:
        raise ValueError('expected ZIP and directly downloadable cumulative TeX')
    book = relative_path(build['book_directory'])
    driver = relative_path(export['driver'])
    if driver.parent != book or driver.name != native.with_suffix('.tex').name:
        raise ValueError('native driver differs')
    report = {'schema': 'olpkit.package-check.v1', 'status': 'running', 'modes': {},
              'export_sha256': digest(export_file.read_bytes()), 'native_pdf_sha256': native_hash,
              'build_sha256': package['build_sha256'], 'outputs': export['outputs']}
    if mode_choice not in ('both', 'modular', 'cumulative'):
        raise ValueError('unknown source entry point')
    report['requested_mode'] = mode_choice
    out.mkdir(parents=True)
    def save():
        (out / 'PACKAGE-CHECK.json').write_bytes(json_bytes(report))
    try:
        for mode, entry in [('modular', driver.name), ('cumulative', assets['.tex'].name)]:
            if mode_choice not in ('both', mode):
                continue
            stage = out / mode
            tree = stage / 'source'
            unpack(assets['.zip'], package['files'], tree)
            cwd = tree / book
            if (cwd / assets['.tex'].name).read_bytes() != assets['.tex'].read_bytes():
                raise ValueError('direct cumulative source differs from ZIP')
            result = {'commands': [], 'passes': 0, 'status': 'running'}
            report['modes'][mode] = result
            save()
            job = Path(entry).stem
            with TeXSlot() as slot:
                if not slot.acquired:
                    report['status'] = result['status'] = 'slot_occupied'
                    return 75
                checks = settle_tex(tree, cwd, job, build['engine'], build['source_date_epoch'],
                                    stage, result, save)
            result['log_checks'] = checks
            if checks['issues'] or checks['overfull_over_2pt']:
                raise ValueError(mode + ' reader failed the native typesetting checks')
            inspect_compiled(mode, tree, job, build, export, native, result)
        report['status'] = 'pass'
        return 0
    except Exception as error:
        report['status'] = 'fail'
        report['error'] = str(error)
        raise
    finally:
        save()
