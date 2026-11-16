import unittest
from io import BytesIO
from copy import deepcopy
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from lxml import html,etree
from olpkit.webfonts import bind_web_fonts


class NativeWebFontTests(unittest.TestCase):
    def setUp(self):
        self.title='मुद्राक्षरांचे श्रेय आणि परवाने'
        points={32,0x915}|{ord(c) for c in self.title}
        cmap={c:'uni'+format(c,'04X') for c in points}
        font=FontBuilder(1000,isTTF=True);glyphs=['.notdef',*cmap.values()]
        font.setupGlyphOrder(glyphs)
        font.setupCharacterMap(cmap)
        font.setupGlyf({name:TTGlyphPen(None).glyph() for name in glyphs})
        font.setupHorizontalMetrics({name:(500,0) for name in glyphs})
        font.setupHorizontalHeader(ascent=800,descent=-200)
        font.setupNameTable({'familyName':'Fixture Serif','styleName':'Regular',
                            'uniqueFontIdentifier':'FixtureSerif','fullName':'Fixture Serif','psName':'FixtureSerif'})
        font.setupOS2();font.setupPost();font.setupMaxp()
        data=BytesIO();font.save(data)
        self.data={'font.ttf':data.getvalue(),'OFL.txt':b'Original source licence\nExact notice.\n',
                   'credits.md':('# '+self.title+'\n').encode()}
        self.config={'family':'Fixture Serif','script':'Deva','faces':[{'source':'font.ttf','weight':400}],
                     'licence_source':'OFL.txt','title_source':'credits.md'}

    def test_original_bytes_licence_and_existing_prose_are_preserved(self):
        doc=html.fromstring('<div><p>क</p></div>');before=etree.tostring(doc[0])
        assets,css,epub_css,record=bind_web_fonts(doc,self.config,self.data.__getitem__)
        self.assertEqual(etree.tostring(doc[0]),before)
        self.assertEqual(list(assets.values()),[self.data['font.ttf']])
        self.assertEqual(doc.xpath('.//pre')[0].text.encode(),self.data['OFL.txt'])
        self.assertIn('url("assets/fonts/',css)
        self.assertIn('url("../assets/fonts/',epub_css)
        self.assertEqual(record['faces'][0]['missing_script_characters'],0)

    def test_missing_used_glyph_and_wrong_family_fail(self):
        with self.assertRaisesRegex(ValueError,'lacks used'):
            bind_web_fonts(html.fromstring('<div><p>ख</p></div>'),self.config,self.data.__getitem__)
        config=deepcopy(self.config);config['family']='Another Family'
        with self.assertRaisesRegex(ValueError,'family differs'):
            bind_web_fonts(html.fromstring('<div><p>क</p></div>'),config,self.data.__getitem__)

    def test_native_family_names_the_licence_when_no_notice_heading_exists(self):
        config=deepcopy(self.config)
        del config['title_source']
        doc=html.fromstring('<div><p>क</p></div>')
        _,_,_,record=bind_web_fonts(doc,config,self.data.__getitem__)
        self.assertEqual(doc.xpath('.//h1')[0].text,config['family'])
        self.assertEqual(record['title_source'],'font.ttf')
        self.assertEqual(doc.xpath('.//pre')[0].text.encode(),self.data['OFL.txt'])

    def test_other_scripts_and_shared_script_punctuation_are_checked(self):
        config=deepcopy(self.config);config['script']='Beng'
        with self.assertRaisesRegex(ValueError,'lacks used Beng'):
            bind_web_fonts(html.fromstring('<div><p>ক</p></div>'),config,self.data.__getitem__)
        with self.assertRaisesRegex(ValueError,'0x965'):
            bind_web_fonts(html.fromstring('<div><p>क॥</p></div>'),self.config,self.data.__getitem__)

    def test_licence_cannot_be_omitted_or_duplicated(self):
        doc=html.fromstring('<div><p>क</p></div>')
        bind_web_fonts(doc,self.config,self.data.__getitem__)
        with self.assertRaisesRegex(ValueError,'already exists'):
            bind_web_fonts(doc,self.config,self.data.__getitem__)
        self.data['OFL.txt']=b''
        with self.assertRaisesRegex(ValueError,'licence absent'):
            bind_web_fonts(html.fromstring('<div><p>क</p></div>'),self.config,self.data.__getitem__)
