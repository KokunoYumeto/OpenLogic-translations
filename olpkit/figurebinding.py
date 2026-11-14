"""Bind native vector exports to every executed diagram occurrence.

The assets are rendered by nativefigures under the book's own configuration.
This stage does not draw a replacement graph or infer a language description.
It verifies ordered source/asset identities before introducing placeholders,
and refuses to discard any surrounding mathematics during DOM replacement.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .nativefigures import extract_tikz, sha


PREFIX = 'OLPNATIVEFIG'
MARKER = re.compile(PREFIX + r'\d{6}')
SVG = 'http://www.w3.org/2000/svg'


def checked_asset(folder, name, digest):
    root = Path(folder).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError('native figure asset outside its directory')
    data = path.read_bytes()
    if sha(data) != digest:
        raise ValueError('native figure asset hash mismatch: '+name)
    return data


def inspect_svg(data):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('external declarations in native SVG')
    root = ET.fromstring(data)
    if root.tag != '{'+SVG+'}svg':
        raise ValueError('native figure is not an SVG')
    for node in root.iter():
        tag = node.tag.rsplit('}', 1)[-1]
        if tag in ('image', 'script', 'foreignObject', 'style'):
            raise ValueError('non-vector or active content in native SVG')
        for name, value in node.attrib.items():
            local = name.rsplit('}', 1)[-1]
            if local.lower().startswith('on'):
                raise ValueError('event handler in native SVG')
            if local == 'href' and not value.startswith('#'):
                raise ValueError('external reference in native SVG')
            if '@import' in value or any(not x.strip(' \"\'').startswith('#')
                                         for x in re.findall(r'url\((.*?)\)', value)):
                raise ValueError('external style reference in native SVG')
    for key in ('width', 'height'):
        if not re.fullmatch(r'\d+(?:\.\d+)?', root.get(key, '')) or float(root.get(key)) <= 0:
            raise ValueError('unsupported native SVG dimension')
    return root


def prepare_figures(text, source, exported, assets):
    """Validate ordered occurrences even when the surrounding projection changed.

    The caller reconciles the native book configuration with its assembly. The
    full source hash is recorded here, while each unchanged exact diagram must
    match the native batch in occurrence order, including repeated diagrams.
    """
    if PREFIX in text:
        raise ValueError('reserved native figure marker in source')
    if (exported.get('schema') != 'olpkit.native-figures.v1' or
            exported.get('status') != 'vectors_exported_pending_visual_and_semantic_checks'):
        raise ValueError('native figures have no successful vector export')
    actual = extract_tikz(text)
    expected = exported['figures']
    if len(actual) != len(expected):
        raise ValueError('native figure occurrence count differs')
    markers = {}
    pieces = []
    pos = 0
    for row, native in zip(actual, expected):
        if row['index'] != native['index'] or row['source_sha256'] != native['source_sha256']:
            raise ValueError('native figure source/order mismatch')
        original = checked_asset(assets, native['source_file'], native['source_sha256'])
        if original.decode('utf-8') != row['source_tex']:
            raise ValueError('native figure source bytes mismatch')
        vector = checked_asset(assets, native['asset'], native['svg_sha256'])
        svg = inspect_svg(vector)
        if any(svg.get(k) != native[k] for k in ('width', 'height', 'viewBox')):
            raise ValueError('native figure dimensions differ')
        key = PREFIX + str(row['index']).zfill(6)
        markers[key] = {**row, 'asset': native['asset'], 'source_file': native['source_file'],
                        'svg_sha256': native['svg_sha256'], 'svg_bytes': len(vector),
                        'width_pt': native['width'], 'height_pt': native['height']}
        pieces.extend((text[pos:row['char_start']], r'\mbox{'+key+'}'))
        pos = row['char_end']
    pieces.append(text[pos:])
    result = ''.join(pieces)
    return result, {'schema': 'olpkit.figure-binding.v1', 'source': source,
                    'input_sha256': sha(text.encode('utf-8')),
                    'output_sha256': sha(result.encode('utf-8')),
                    'native_source_sha256': exported['source_sha256'],
                    'configuration_evidence': exported['configuration_evidence'],
                    'markers': markers, 'reader_complete': False}


def bind_figures(document, receipt, *, asset_prefix, fallback_alt, descriptions=None):
    """Replace figure-only displays and inline placeholders without dropping text.

    Missing localized descriptions remain an explicit accessibility failure in
    the receipt. The caller supplies its own source-defined generic figure name
    for a diagnostic preview; it is never accepted as a substantive description.
    """
    from lxml import etree

    if not fallback_alt.strip():
        raise ValueError('source-defined figure label is required')
    if (not re.fullmatch(r'[A-Za-z0-9_/-]+', asset_prefix) or
            asset_prefix.startswith('/') or '..' in asset_prefix.split('/')):
        raise ValueError('unsafe local figure asset prefix')
    descriptions = descriptions or {}
    markers = receipt['markers']
    bound = []
    pending = []

    def local(node):
        return node.tag.rsplit('}', 1)[-1] if isinstance(node.tag, str) else ''

    def graphic(key):
        if key not in markers or key in bound:
            raise ValueError('unknown or duplicate native figure marker: '+key)
        row = markers[key]
        alt = descriptions.get(row['source_sha256'])
        if alt is not None and (not isinstance(alt, str) or not alt.strip()):
            raise ValueError('empty native figure description')
        if alt is None:
            pending.append(key)
        span = etree.Element('span', {'class': 'olp-native-figure',
                                    'id': 'olp-native-figure-'+str(row['index']),
                                    'data-source-sha256': row['source_sha256']})
        etree.SubElement(span, 'img', src=asset_prefix.rstrip('/')+'/'+row['asset'],
                         alt=alt or fallback_alt,
                         style='width:'+row['width_pt']+'pt;max-width:100%;height:auto;vertical-align:middle')
        bound.append(key)
        return span

    # Only a display consisting entirely of one diagram can leave MathML.
    # Losing a neighbouring equation/sign during replacement is a hard error.
    for node in list(document.iter()):
        if local(node) != 'math':
            continue
        leaves = []
        for item in node.iter():
            if local(item) == 'annotation' or any(local(p) == 'annotation' for p in item.iterancestors()):
                continue
            if item.text:
                leaves.append(item.text)
        text = ''.join(leaves).strip()
        keys = MARKER.findall(text)
        if not keys:
            continue
        allowed = {'math', 'semantics', 'mrow', 'mtable', 'mtr', 'mtd', 'mtext',
                   'mspace', 'mstyle', 'annotation'}
        if len(keys) != 1 or text != keys[0] or any(local(n) not in allowed for n in node.iter()):
            raise ValueError('native diagram shares a display with other mathematics')
        replacement = graphic(keys[0])
        replacement.tail = node.tail
        node.getparent().replace(node, replacement)

    # Pandoc emits a prose mbox as plain text, possibly beside other prose.
    for node in list(document.iter()):
        if local(node) == 'annotation':
            continue
        for attribute in ('text', 'tail'):
            value = getattr(node, attribute)
            if not value or not MARKER.search(value):
                continue
            matches = list(MARKER.finditer(value))
            setattr(node, attribute, value[:matches[0].start()])
            parent = node if attribute == 'text' else node.getparent()
            index = 0 if attribute == 'text' else parent.index(node)+1
            for i, match in enumerate(matches):
                graphic_node = graphic(match[0])
                stop = matches[i+1].start() if i+1 < len(matches) else len(value)
                graphic_node.tail = value[match.end():stop]
                parent.insert(index, graphic_node)
                index += 1
    missing = sorted(set(markers)-set(bound))
    if missing:
        raise ValueError('unbound native figures: '+', '.join(missing))
    if MARKER.search(etree.tostring(document, encoding='unicode')):
        raise ValueError('native figure marker remains in output')
    order = [PREFIX+str(node.get('id').rsplit('-',1)[1]).zfill(6)
             for node in document.xpath('.//span[@class="olp-native-figure"]')]
    if order != list(markers):
        raise ValueError('rendered native figure occurrence order differs')
    return {'bound': len(bound), 'order': order, 'missing': missing,
            'descriptions_pending': pending, 'reader_complete': False}
