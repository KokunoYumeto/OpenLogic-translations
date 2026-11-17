# Localization patches and upstream settings

The builder reads the style files at the edition’s recorded upstream revision. For the settings below, it checks that upstream defines the setting and uses it at the package or font call. It writes the edition’s value into the textbook preamble before the class or style is loaded. The driver report records the setting, and the assembly report lists the patches actually applied. Editions pinned before the two merges use their original patches. Rebuild a textbook and compare it with its published reader when adopting a newer revision.

| Upstream setting | Edition patches | Adoption check |
| --- | --- | --- |
| [Reference language, Open Logic #447](https://github.com/OpenLogicProject/OpenLogic/pull/447) | [Javanese](jv-cleveref-local-captions.toml), [Gujarati](gu-cleveref-local-captions.toml), [Bengali](bn-sty-open-logic-sty-02.toml), [Marathi](mr-sty-open-logic-sty-03.toml) | Set `\olreferencelanguage` in the localization. Confirm that theorem, lemma and other cross-references retain the edition’s names and destinations. The Javanese pilot reproduced its PDF, EPUB and offline HTML archive byte for byte. |
| [Book fonts, Open Logic #448](https://github.com/OpenLogicProject/OpenLogic/pull/448) | [Gujarati main font](gu-unicode-main-font.toml), [Gujarati sans font](gu-unicode-sans-font.toml), [Bengali main font](bn-sty-open-logic-book-cls-02.toml) | Select the edition’s text fonts before the book class loads. Compare glyphs, page breaks and embedded fonts. |
| [Screen PDF profile, Open Logic #448](https://github.com/OpenLogicProject/OpenLogic/pull/448) | [Gujarati PDF/A profile](gu-pdfa-level.toml) | Set `\OLPscreenPDFStandard` to `a-2b`. The Gujarati font and PDF pilot matched the text and rendering of all 286 published pages. |

The [Bengali screen PDF patch](bn-sty-open-logic-book-cls-04.toml) skips loading `pdfx` altogether. Its patch recognizes the screen package call in both revisions and preserves the print profile. The [Marathi comment patch](mr-sty-open-logic-sty-02.toml) changes a source comment and can be reviewed separately from the package option.
