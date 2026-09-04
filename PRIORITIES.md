# Repair and next-language priorities

## First: make the existing estate truthful and usable

1. **Iranian Persian:** turn the current 642-unit reader plus separate 80-unit supplement into one coherent 722-unit reader, then replay RTL/BiDi, formula, citation, build, visual, and public-byte QA.
2. **Spanish and Brazilian Portuguese:** reconcile the exact local r5 artifacts with their public GitHub releases and Zenodo version metadata. Current README links and available public versions disagree.
3. **Accessibility:** finish cumulative semantic acceptance for tranches 50–79 and complete whole-book browser, keyboard, reflow, MathML, and deterministic-source gates.
4. **Interslavic:** continue from the exact accepted OLP-0182 boundary; do not relabel the QA PDF or 182-unit HTML prefix as a complete book.
5. **Hindi, Indonesian, Chinese, and Turkish:** retain their honest 722-source/642-reader status and integrate the retained 80 units into standalone readers without changing mathematical content. The Hindi correction is based on its actual accepted build log, not its source-translation completion label.

## Provisional new-language shortlist

The compute project’s current v3 language-group shortlist is:

1. Hindi (`hi-Deva-IN`) — public edition exists.
2. Bahasa Indonesia (`id-Latn-ID`) — public edition exists.
3. Punjabi, Pakistan standard (`pnb-Arab-PK`).
4. Bengali, India standard (`bn-Beng-IN`).
5. Marathi (`mr-Deva-IN`).
6. Telugu (`te-Telu-IN`).
7. Tamil, India standard (`ta-Taml-IN`).
8. Javanese (`jv-Latn-ID`).
9. Gujarati (`gu-Gujr-IN`).
10. Pashto, Pakistan curriculum target (`ps-Arab-PK`).

This is a model-conditional planning order, not an observed count of readers and not an eternal “top ten.” Existing translations were intentionally not predictors of need. The frozen shortlist artifacts are:

- `TOP10_NEEDS_ONLY_v3.csv`: 13,303 bytes; SHA-256 `c8886394fd96b0c292baf80028b888e41523a2eec713f36e03a21a8239461777`;
- `TOP10_LANGUAGE_GROUPS_v3.csv`: 3,106 bytes; SHA-256 `32413813c59a2960362385bb092e79a831bf78e11cb9d2dfb122a5996447fc55`;
- ranking QA: SHA-256 `c29f1a15bcfbae73e61a7022baf6a8b8595a61b5f91edf174b333952f80e13df`.

The laptop intake has now been indexed from actual source, translation and reader files. It contains serious mathematics work in Punjabi, Indian Bengali, Marathi, Telugu, Tamil, Javanese and Gujarati, plus Bangladesh Bengali and Vietnamese. See the [book-named recovery inventory](RELATED_MATHEMATICS.md). Reuse their applicable canon and infrastructure after exact-language checks; do not create duplicate mathematics producers. Their OpenStax work is not evidence of completed OpenLogic translations. No Pashto lane was present in this particular dump.

## Canon plans for the eight not-yet-public targets

### Punjabi (`pnb-Arab-PK`)

Use Pakistan-standard Punjabi in Shahmukhi as the target. Start with Punjab’s language institutions and Pakistan Punjab educational publications, then add actual Shahmukhi scholarly prose and university mathematical usage. The [Punjab Institute of Language, Art and Culture](https://pilac.punjab.gov.pk/) is a language witness; the [Punjab Curriculum and Textbook Board](https://pctb.punjab.gov.pk/) is an educational witness. Punjabi University’s [Gurmukhi–Shahmukhi dictionary](https://dic.learnpunjabi.org/) can test cross-script candidates, but Indian Gurmukhi wording must not become a silent pivot. Treat Shahmukhi spelling variation and Nastaliq shaping as explicit evidence and QA problems.

### Bengali (`bn-Beng-IN`)

Use India-standard Bengali and bind school terminology to current West Bengal usage, beginning with the government’s [Banglar Shiksha mathematics materials](https://banglarshiksha.gov.in/Frontend/online_guidelines_activities). Add Bengali university mathematics, philosophy, and logic publications before adjudicating formal terminology. Test Bengali conjuncts, vowel signs, line breaking, punctuation, and math-boundary spacing; do not import Bangladeshi register choices without labeling their witness role.

### Marathi (`mr-Deva-IN`)

Use Maharashtra’s [eBalbharati textbook library](https://books.ebalbharati.in/ebook.aspx), the Government of India’s [English–Hindi–Marathi Fundamental Glossary of Mathematics](https://cstt.education.gov.in/sites/default/files/fundamental-glossary-mathematics-eng-hin-marathi.pdf), and Marathi university-level mathematical writing. Record when the glossary offers Sanskritic, established vernacular, and borrowed alternatives; select by attested mathematical prose rather than automatic pan-Indian cognacy.

### Telugu (`te-Telu-IN`)

Use the [SCERT Telangana Telugu-medium mathematics and science corpus](https://www.scert.telangana.gov.in/Home.aspx/pdf/publication/ebooks/Pdf/DisplayContent.aspx?encry=ammkNW4%2Fgx+NeApstGPX+A%3D%3D) and add Andhra/Telangana university mathematical and philosophical sources. Record regional differences instead of collapsing them. Test Telugu grapheme clusters, vowel signs, ligatures, font fallback, and line breaking across prose/formula boundaries.

### Tamil (`ta-Taml-IN`)

Use [Tamil Nadu SCERT](https://scert.tnschools.gov.in/) educational usage and the [Tamil Virtual Academy technical glossary](https://www.tamilvu.org/en/technical-glossory), whose subject coverage includes mathematics, statistics, philosophy, science, and technology. Add contemporary university texts to decide between coined Tamil terms and established international loans. Test glyph coverage, pulli/combining behavior, line breaking, and copy/search text.

### Javanese (`jv-Latn-ID`)

Build a sparse but real Javanese canon from the Indonesian education ministry’s language repository, including its [Javanese–Indonesian dictionary](https://repositori.kemdikbud.go.id/2885/), authoritative grammars, provincial educational materials, and Javanese university writing. The Indonesian OpenLogic edition is a workflow witness only; Indonesian wording must not be mechanically relabeled as Javanese. Record speech-level/register choices and every unavoidable technical borrowing. Latin is the primary production script; Javanese-script output, if attempted, is a separately tested projection rather than the semantic authority.

### Gujarati (`gu-Gujr-IN`)

Use the [Government of India English–Hindi–Gujarati Fundamental Glossary of Mathematics](https://www.cstt.education.gov.in/sites/default/files/fundamental-glossary-mathematics-eng-hin-gujarati.pdf), [Gujarat State School Textbook Board](https://gsbstb.online/) materials, and Gujarati university mathematical prose. Prefer actual Gujarati usage over automatically copying Hindi/Sanskrit forms from trilingual lists. Test Gujarati conjuncts, vowel signs, fonts, line breaking, and text extraction.

### Pashto (`ps-Arab-PK`)

Use the [Pashto Academy, University of Peshawar](https://www.uop.edu.pk/departments/?q=Pashto-Academy) for dictionary, grammar, translation, and research witnesses, and the [Khyber Pakhtunkhwa Directorate of Curriculum and Teacher Education](https://dcte.kp.gov.pk/) for curriculum authority. Add Pashto-medium mathematics and university scientific prose. Urdu, Persian, and Arabic can explain loan histories but may not decide Pashto syntax or terminology. Test Pashto-specific letters, diacritics, joining, font coverage, RTL punctuation, and LTR math isolation.

## Shared execution order

For every target: acquire and hash canon bytes; index passages and terms; translate against the frozen 722-file source; record canon use per segment; build one standalone reader; run language- and script-specific QA; publish editable sources, evidence, and checksums; and anonymously read the public bytes back. Adjacent-language reuse is limited to infrastructure, candidate discovery, and contrastive checking.
