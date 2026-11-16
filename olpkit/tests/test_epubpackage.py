from copy import deepcopy
import io
import unittest
from unittest.mock import patch
import zipfile
from lxml import etree

from olpkit.epubpackage import package_html
from olpkit.xhtml import clone_xhtml


class ReflowPackageTests(unittest.TestCase):
    def setUp(self):
        self.profile={'language':'xx','direction':'ltr','title':'Example','creator':'Source author',
                      'identifier':'urn:example:fixture','source':'https://example.org/source',
                      'description':'Test fixture','rights':'Source notice','modified':'2026-11-13T00:00:00Z',
                      'navigation_title':'Contents','opening_title':'Opening','notes_title':'Notes',
                      'unit_prefix':'unit:','css':'body { color: black; }','resource_map':{},
                      'image_descriptions':{},'required_supplements':['credits.xhtml']}
        self.html=b'''<!doctype html><html lang="xx" dir="ltr"><body>
<nav id="TOC"><ul><li><a href="#first">One</a></li><li><a href="#second">Two</a></li></ul></nav>
<h1 id="first">One</h1><span id="unit:OLP-0001"></span><p>Exact text <a href="#second">next</a>.</p>
<p><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi>x</mi><mn>2</mn></msup><annotation encoding="application/x-tex">x^2</annotation></semantics></math></p>
<h2 id="second">Two</h2><span id="unit:OLP-0002"></span><p>Retained proof.</p></body></html>'''
        self.supplement=b'<html xmlns="http://www.w3.org/1999/xhtml" lang="xx" dir="ltr"><head><title>Credits</title></head><body><p>Original credit retained.</p><a href="nav.xhtml">Contents</a></body></html>'

    def run_package(self,source=None,profile=None,assets=None,supplement=None,units=None):
        return package_html(source or self.html,profile or self.profile,units or ['OLP-0001','OLP-0002'],
                            assets or {},{'credits.xhtml':supplement or self.supplement})

    def test_content_math_cross_document_links_and_deterministic_bytes(self):
        first,receipt=self.run_package();second,_=self.run_package()
        self.assertEqual(first,second);self.assertEqual(receipt['mathml_formulas'],1)
        self.assertFalse(receipt['release_ready'])
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            self.assertEqual(archive.infolist()[0].filename,'mimetype')
            self.assertEqual(archive.infolist()[0].compress_type,zipfile.ZIP_STORED)
            first_doc=etree.fromstring(archive.read('OEBPS/chapter-001.xhtml'))
            self.assertEqual(first_doc.xpath('string(.//*[local-name()="annotation"])'),'x^2')
            self.assertIn('chapter-002.xhtml#second',first_doc.xpath('.//@href'))
            self.assertIn('nav.xhtml',first_doc.xpath('.//@href'))
            self.assertIn(b'Original credit retained.',archive.read('OEBPS/credits.xhtml'))

    def test_rtl_language_and_spine_come_only_from_data(self):
        profile=deepcopy(self.profile);profile.update(language='fa',direction='rtl',navigation_title='فهرست')
        source=self.html.replace(b'lang="xx" dir="ltr"',b'lang="fa" dir="rtl"')
        supplement=self.supplement.replace(b'lang="xx" dir="ltr"',b'lang="fa" dir="rtl"')
        output,_=self.run_package(source,profile,supplement=supplement)
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            for name in archive.namelist():
                if name.endswith('.xhtml'):
                    doc=etree.fromstring(archive.read(name));self.assertEqual(doc.get('dir'),'rtl');self.assertEqual(doc.get('lang'),'fa')
            opf=etree.fromstring(archive.read('OEBPS/package.opf'))
            self.assertEqual(opf.xpath('string(.//*[local-name()="spine"]/@page-progression-direction)'),'rtl')

    def test_missing_math_annotation_or_wrong_unit_order_fails(self):
        source=self.html.replace(b'<annotation encoding="application/x-tex">x^2</annotation>',b'')
        with self.assertRaisesRegex(ValueError,'annotation'):self.run_package(source)
        with self.assertRaisesRegex(ValueError,'unit order'):self.run_package(units=['OLP-0002','OLP-0001'])

    def test_broken_and_duplicate_anchors_fail(self):
        with self.assertRaisesRegex(ValueError,'unresolved fragment'):
            self.run_package(self.html.replace(b'href="#second"',b'href="#absent"'))
        with self.assertRaisesRegex(ValueError,'duplicate document identifier'):
            self.run_package(self.html.replace(b'Retained proof.',b'<span id="first">Duplicate</span>'))

    def test_images_require_registered_bytes_and_localized_descriptions(self):
        source=self.html.replace(b'Retained proof.',b'<img src="source/figure.svg"/>')
        with self.assertRaisesRegex(ValueError,'unregistered image'):self.run_package(source)
        profile=deepcopy(self.profile);profile['resource_map']={'source/figure.svg':'assets/figure.svg'}
        assets={'assets/figure.svg':b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0 L1 1"/></svg>'}
        with self.assertRaisesRegex(ValueError,'description absent'):self.run_package(source,profile,assets)
        profile['image_descriptions']={'source/figure.svg':'Given figure description.'}
        output,_=self.run_package(source,profile,assets)
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            self.assertEqual(archive.read('OEBPS/assets/figure.svg'),assets['assets/figure.svg'])

    def test_credit_and_css_resource_omissions_do_not_pass(self):
        with self.assertRaisesRegex(ValueError,'required localized'):
            package_html(self.html,self.profile,['OLP-0001','OLP-0002'],{}, {})
        with self.assertRaisesRegex(ValueError,'localized XHTML'):
            self.run_package(supplement=self.supplement.replace(b'dir="ltr"',b'dir="rtl"'))
        profile=deepcopy(self.profile);profile['css']="@font-face{src:url('../fonts/missing.ttf')}"
        with self.assertRaisesRegex(ValueError,'CSS resource'):self.run_package(profile=profile)

    def test_fonts_use_css_location_and_retain_exact_registered_bytes(self):
        profile=deepcopy(self.profile)
        profile['css']='@font-face{src:url("assets/font.ttf")}'
        profile['epub_css']='@font-face{src:url("../assets/font.ttf")}'
        data=b'font-fixture'
        output,_=self.run_package(profile=profile,assets={'assets/font.ttf':data})
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            self.assertEqual(archive.read('OEBPS/assets/font.ttf'),data)
            self.assertEqual(archive.read('OEBPS/styles/reader.css').decode(),profile['epub_css'])
            self.assertIn(b'media-type="font/ttf"',archive.read('OEBPS/package.opf'))

    def test_native_nested_contents_and_in_book_credits_remain_in_order(self):
        profile=deepcopy(self.profile);profile['required_supplements']=[]
        profile['required_credit_ids']=['source-credits']
        source=self.html.replace(b'<nav id="TOC">',b'<div class="front"><nav id="TOC">')
        source=source.replace(b'</nav>',b'</nav>Preserved after contents.</div><div id="source-credits">Exact native credit.</div>')
        data,receipt=package_html(source,profile,['OLP-0001','OLP-0002'],{}, {})
        self.assertTrue(receipt['visible_text_preserved'])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            opening=archive.read('OEBPS/chapter-001.xhtml')
            self.assertIn(b'Preserved after contents.',opening)
            self.assertIn(b'Exact native credit.',opening)
        with self.assertRaisesRegex(ValueError,'in-book credit'):
            package_html(source.replace(b'Exact native credit.',b''),profile,['OLP-0001','OLP-0002'],{}, {})

    def test_explicit_decorative_art_does_not_acquire_a_spoken_caption(self):
        source=self.html.replace(b'Retained proof.',b'<img src="assets/art.png" role="presentation" alt=""/>Retained proof.')
        output,_=self.run_package(source,assets={'assets/art.png':b'fixture-png'})
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            doc=etree.fromstring(archive.read('OEBPS/chapter-002.xhtml'))
            self.assertEqual(doc.xpath('.//*[local-name()="img"]/@alt'),[''])

    def test_details_remain_navigable_after_chapter_split(self):
        source=self.html.replace(b'Exact text',b'<img src="a.svg" alt="Graph" aria-details="notes"/>'
                                 b'<a href="#notes">Diagram description</a> Exact text')
        source=source.replace(b'Retained proof.',b'<span id="notes">Two vertices.</span>')
        data,_=self.run_package(source,assets={'a.svg':b'<svg/>'})
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            doc=etree.fromstring(archive.read('OEBPS/chapter-001.xhtml'))
            target=doc.xpath('string(//*[@aria-details]/@aria-details)')
            self.assertEqual(doc.xpath('string(//*[@id=$id]/@href)',id=target),'chapter-002.xhtml#notes')
        with self.assertRaisesRegex(ValueError,'adjacent description link'):
            self.run_package(source.replace(b'<a href="#notes">Diagram description</a>',b''),assets={'a.svg':b'<svg/>'})

    def test_source_scripts_and_unregistered_links_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'scripts or unbound'):
            self.run_package(self.html.replace(b'Retained proof.',b'<script>example()</script>'))
        with self.assertRaisesRegex(ValueError,'unsafe package member'):
            self.run_package(self.html.replace(b'href="#second"',b'href="../outside.xhtml"'))

    def test_document_cannot_bypass_localization_as_an_asset(self):
        with self.assertRaisesRegex(ValueError,'resource member'):
            self.run_package(assets={'unvalidated.xhtml':self.supplement})

    def test_math_link_relocation_preserves_target_identity(self):
        source=self.html.replace(b'<mi>x</mi>',b'<mi href="#second">x</mi>')
        output,_=self.run_package(source)
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            doc=etree.fromstring(archive.read('OEBPS/chapter-001.xhtml'))
            self.assertEqual(doc.xpath('string(.//*[local-name()="mi"]/@href)'),
                             'chapter-002.xhtml#second')

    def test_math_structure_mutation_fails_even_with_identical_visible_text(self):
        def wrong_clone(node):
            result=clone_xhtml(node)
            for child in result.iter():
                if child.tag.endswith('}msup'):child.tag=child.tag.replace('}msup','}msub')
            return result
        with patch('olpkit.epubpackage.clone_xhtml',side_effect=wrong_clone):
            with self.assertRaisesRegex(ValueError,'MathML structure'):
                self.run_package()


if __name__=='__main__':unittest.main()
