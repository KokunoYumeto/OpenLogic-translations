# Open Logic translations

This is the catalogue and production standard for independent translations and accessibility work based on the [Open Logic Project](https://openlogicproject.org/). The editions listed here are adaptations; listing does not imply endorsement by the Open Logic Project.

The [frozen English source snapshot](https://github.com/OpenLogicProject/OpenLogic/tree/9620cc73f9c8e0ad003c514a5d3748f29611c4c0) contains 722 tracked content `.tex` files. Technical revision identities are recorded in the catalogue. Coverage of those files and coverage of a reading PDF are reported separately. In particular, “722 translated sources” does **not** mean that all 722 are present in one reader.

## Read or inspect an edition

| Edition | Public home | Evidence-based status |
|---|---|---|
| Arabic | [repository](https://github.com/KokunoYumeto/OpenLogic-ar) · [release](https://github.com/KokunoYumeto/OpenLogic-ar/releases/tag/ar-olp-0722-complete-dual-notation-r2-20260903) · [DOI](https://doi.org/10.5281/zenodo.21921850) | **Standalone 722/722 readers verified.** One Arabic text, with separate international-digit and Machrek Arabic-Indic mathematical-notation profiles. |
| Iranian Persian | [repository](https://github.com/KokunoYumeto/OpenLogic-fa-ir) · [release](https://github.com/KokunoYumeto/OpenLogic-fa-ir/releases/tag/fa-ir-olp-0722-readable-letter-r2-20260820) · [DOI](https://doi.org/10.5281/zenodo.21921852) | **722 translated sources; delivery repair required.** The current reader contains the ordinary 642-unit graph and the other 80 units are a separate supplement. A single 722-unit reader is not yet established. |
| Hindi | [repository](https://github.com/KokunoYumeto/open-logic-hi) · [release](https://github.com/KokunoYumeto/open-logic-hi/releases/tag/HI-OLP-PUB-0005) · [DOI](https://doi.org/10.5281/zenodo.21920511) | **722 translated sources; 642-source-file reader.** The accepted 842-page A4 build log loads 642 of the frozen content files, not all 722. The standalone-reader label has been corrected; the edition task has been notified. |
| Bahasa Indonesia | [repository](https://github.com/KokunoYumeto/OpenLogic-id) · [release](https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814) · [DOI](https://doi.org/10.5281/zenodo.21932786) | **722 translated sources; 642-unit reader.** The remaining 80 translated files are retained in editable sources and explicitly outside the build. |
| Mainland Simplified Chinese | [repository](https://github.com/KokunoYumeto/open-logic-zh-hans-cn) · [release](https://github.com/KokunoYumeto/open-logic-zh-hans-cn/releases/tag/ZH-OLP-PUB-0003) · [DOI](https://doi.org/10.5281/zenodo.21987817) | **722 translated sources; 642-unit reader.** Eighty translated alternative/draft units remain source-only. |
| Turkish | [repository](https://github.com/KokunoYumeto/OpenLogic-tr) · [release](https://github.com/KokunoYumeto/OpenLogic-tr/releases/tag/tr-olp-0722-20260814) · [DOI](https://doi.org/10.5281/zenodo.21921844) | **722 translated sources; 642-unit reader.** Eighty retained non-reader units are outside build/render applicability. |
| Spanish | [repository](https://github.com/KokunoYumeto/OpenLogic-es) · [latest public GitHub release](https://github.com/KokunoYumeto/OpenLogic-es/releases/tag/v2026-08-20-r4) · [concept DOI](https://doi.org/10.5281/zenodo.21997720) | **722/722 local r5 reader passes QA; public mirrors drift.** The README points to an unavailable r5 GitHub release and unavailable version DOI, while GitHub exposes r4 and the concept DOI resolves to an older record. |
| Brazilian Portuguese | [repository](https://github.com/KokunoYumeto/OpenLogic-pt-BR) · [latest inventoried GitHub release](https://github.com/KokunoYumeto/OpenLogic-pt-BR/releases/tag/v2026-08-20-r4) · [concept DOI](https://doi.org/10.5281/zenodo.21973104) | **722/722 local r5 reader passes recorded QA; public mirrors need reconciliation.** The GitHub inventory lacks the README-linked r5 release. Exact current Zenodo/r5 byte identity has not been established by this catalogue's manager. |
| Canon-first Inter-Turkic | [repository](https://github.com/KokunoYumeto/canon-first-turkic-interlanguage-openlogic) · [release](https://github.com/KokunoYumeto/canon-first-turkic-interlanguage-openlogic/releases/tag/v2.2.0) · [DOI](https://doi.org/10.5281/zenodo.22104592) | **722-record constructed interlanguage edition.** Latin, Cyrillic and Arabic-script PDFs are synchronized views of one explicit register, with structured provenance and uncertainty. |
| Interslavic | [live reader and evidence](https://kokunoyumeto.github.io/modern-latex-manuscripts/open-logic-interslavic/) · [method DOI](https://doi.org/10.5281/zenodo.22103007) | **Substantial partial: 182/722.** The Latin witness is editable authority and Cyrillic is a deterministic projection. The public HTML stops before untranslated OLP-0183; no complete PDF is claimed. |

The machine-readable record is [`catalogue/editions.json`](catalogue/editions.json). It records release and DOI versions, script profiles, reader/source coverage, hashes, limitations, and the evidence class behind each status.

## Accessibility infrastructure

The accessible Open Logic book is infrastructure, not another language edition. Its latest accepted checkpoint integrates 50 of 80 planned source tranches (62.5%). Later tranches have prepared or authored material but have not all passed cumulative acceptance. No public repository is claimed here yet.

## Active research editions

- **Inter-Farsi OpenLogic:** active corpus-wide scaffold/edition work. Its design separates a controlled pluricentric register from Iranian Persian and keeps Perso-Arabic and Tajik Cyrillic realization, regional adaptation, and notation profiles as typed layers. It is not yet listed as a public complete translation.
- **Romance interlanguage:** 722 provisional baseline files exist, but zero units were canon-admitted at the last exact checkpoint. It is research scaffolding, not a complete edition.

## What “done” means here

A new complete edition must translate all 722 tracked source files **and** provide one coherent standalone reader containing the complete declared closure. It must bind every segment to the language’s actual scholarly canon, preserve formulas and identifiers, pass script-aware structural and visual QA, publish editable sources and evidence, and verify released bytes anonymously. See [`TRANSLATION_STANDARD.md`](TRANSLATION_STANDARD.md).

The next-language shortlist and its limitations are in [`PRIORITIES.md`](PRIORITIES.md). The shortlist is a planning input, not a timeless or unquestionable ranking.

## Recovered mathematics translation work

The fuller laptop copy contains substantial work in nine language lanes. Those projects mainly translate **OpenStax Prealgebra, Elementary Algebra, Intermediate Algebra and Precalculus**, with further mathematics in some lanes. They are related translation resources, not nine completed OpenLogic editions. The [book-named recovery inventory](RELATED_MATHEMATICS.md) identifies the exact scope and distinguishes source drafts, readers and unfinished books; its [machine-readable catalogue](catalogue/related-mathematics.json) preserves the evidence boundaries. The [fuller recovered files are now public](https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/tree/ed6f2e2020118723c2a12fe3377d2273c3d8ec50/translations), with all 8,758 published files anonymously verified by size and SHA-256. The separate [OpenLogic candidate pipeline](catalogue/candidate-editions.json) records eight provisional shortlist targets and two additional motivated candidates, without crediting textbook work as translated OpenLogic.

## Licence

Catalogue and coordination text in this repository is licensed under [CC BY 4.0](LICENSE.md). Each translation repository states its own adaptation and source licensing.
