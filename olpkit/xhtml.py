# Adapted from OpenLogic-gu-Gujr-IN, commit 085336b59ab402c2daae25216371b9ecae08ceb7, tools/epub_utils.py.
"""XHTML/MathML namespace and EPUB container helpers."""
from lxml import etree
XHTML = 'http://www.w3.org/1999/xhtml'
MATHML = 'http://www.w3.org/1998/Math/MathML'
EPUB = 'http://www.idpf.org/2007/ops'
XML = 'http://www.w3.org/XML/1998/namespace'
CONTAINER = 'urn:oasis:names:tc:opendocument:xmlns:container'

def local_name(value: str) -> str:
    if value.startswith("{"):
        return etree.QName(value).localname
    return value.split(":", 1)[-1]

def clone_xhtml(
    source: etree._Element,
    *,
    in_math: bool = False,
    root: bool = False,
) -> etree._Element:
    name = local_name(str(source.tag))
    math = in_math or name == "math"
    namespace = MATHML if math else XHTML
    nsmap = ({None: XHTML, "epub": EPUB} if root else ({None: MATHML} if name == "math" else None))
    target = etree.Element(f"{{{namespace}}}{name}", nsmap=nsmap)
    for raw_name, value in source.attrib.items():
        name_key = str(raw_name)
        if name_key == "xmlns" or name_key.startswith("xmlns:"):
            continue
        if name_key == "xml:lang" or name_key == f"{{{XML}}}lang":
            target.set(f"{{{XML}}}lang", value)
        elif name_key == "epub:type" or name_key == f"{{{EPUB}}}type":
            target.set(f"{{{EPUB}}}type", value)
        else:
            target.set(name_key, value)
    target.text = source.text
    target.tail = source.tail
    for child in source:
        if isinstance(child.tag, str):
            target.append(clone_xhtml(child, in_math=math))
    return target

def text_without_annotations(element: etree._Element) -> str:
    parts: list[str] = []

    def visit(node: etree._Element) -> None:
        if local_name(str(node.tag)) == "annotation":
            if node.tail:
                parts.append(node.tail)
            return
        if node.text:
            parts.append(node.text)
        for child in node:
            if isinstance(child.tag, str):
                visit(child)
            elif child.tail:
                parts.append(child.tail)
        if node.tail:
            parts.append(node.tail)

    visit(element)
    return " ".join("".join(parts).split())

def make_container() -> bytes:
    container = etree.Element(f"{{{CONTAINER}}}container", nsmap={None: CONTAINER})
    container.set("version", "1.0")
    rootfiles = etree.SubElement(container, f"{{{CONTAINER}}}rootfiles")
    rootfile = etree.SubElement(rootfiles, f"{{{CONTAINER}}}rootfile")
    rootfile.set("full-path", "OEBPS/package.opf")
    rootfile.set("media-type", "application/oebps-package+xml")
    return etree.tostring(container, encoding="utf-8", xml_declaration=True, pretty_print=True)
