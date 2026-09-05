# Repair and next-language priorities

## First: make the existing estate truthful and usable

1. **Iranian Persian:** turn the current 642-unit reader plus separate 80-unit supplement into one coherent 722-unit reader, then replay RTL/BiDi, formula, citation, build, visual, and public-byte QA.
2. **Spanish and Brazilian Portuguese:** integrate the retained source material into complete standalone readers from the verified existing translations. Fresh checks bind all722targets each, but current local r6 reader logs/recorders load642; current bytes differ from historical r5 QA. Public GitHub r4 packages are verified, while Zenodo serves Spanish r2 and Portuguese r5 PDF/r1 sources. Preserve those historical bytes while producing a coherent corrected edition; see [the mirror audit](evidence/ROMANCE_MIRROR_AUDIT.json).
3. **Accessibility:** finish cumulative semantic acceptance for tranches 50–79 and complete whole-book browser, keyboard, reflow, MathML, and deterministic-source gates.
4. **Interslavic:** continue from the exact accepted OLP-0182 boundary; do not relabel the QA PDF or 182-unit HTML prefix as a complete book.
5. **Hindi, Indonesian, Chinese, and Turkish:** retain their honest 722-source/642-reader status and integrate the retained 80 units into standalone readers without changing mathematical content. The Hindi correction is based on its actual accepted build log, not its source-translation completion label.

## Script and orthography routing

The [script and orthography policy](SCRIPT_AND_ORTHOGRAPHY.md) distinguishes reader profiles, deterministic projections, pronunciation accessibility, and separate editions. Arabic's international/Machrek pair and Punjabi's Naskh/Nastaliq pair share one translation in each language; Interslavic, Inter-Turkic, and Inter-Farsi use typed shared-semantic projections. Those outputs must not be counted as duplicate translations.

The strongest additional **separate-edition** routes are Eastern Punjabi in Gurmukhi (`pa-Guru-IN`), Urdu in Nastaliq (`ur-Arab-PK`), Dari (`prs-Arab-AF`), Tajik Cyrillic (`tg-Cyrl-TJ`), and Traditional Chinese with an explicit locale (`zh-Hant`). Each needs its own canon and semantic QA; none is accepted by transliterating or character-converting the existing edition. Kurmanji Latin and Arabic/Badini routes are conditional candidates once regional provenance is established. Hausa Ajami, Wolofal/Ajami and Garay, N’Ko, and Central Asian multi-script cohorts remain bounded research pilots rather than automatic 722-unit commitments. The machine-readable plan is [`catalogue/script-surfaces.json`](catalogue/script-surfaces.json).

## Historical commissioning shortlist; no current global rank

The compute project’s frozen 1 September 2026 v3 language-group shortlist was:

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

This was a model-conditional planning order, not an observed count of readers and not an eternal “top ten.” The live allocation study is still active and currently leaves exact-language audience, effect, physical compute, currency cost, and rank null. Its raw turns contain conflicting Top-10 formulations, so no current global order is accepted. The already commissioned lanes remain active as a continuity decision; they are not cancelled or re-ranked by missing evidence. See the [bounded actionable-findings audit](evidence/ADJACENT_COMPUTE_ACTIONABLE_FINDINGS_20260905.json). Existing translations were intentionally not predictors of need. The frozen shortlist artifacts are:

- `TOP10_NEEDS_ONLY_v3.csv`: 13,303 bytes; SHA-256 `c8886394fd96b0c292baf80028b888e41523a2eec713f36e03a21a8239461777`;
- `TOP10_LANGUAGE_GROUPS_v3.csv`: 3,106 bytes; SHA-256 `32413813c59a2960362385bb092e79a831bf78e11cb9d2dfb122a5996447fc55`;
- ranking QA: SHA-256 `c29f1a15bcfbae73e61a7022baf6a8b8595a61b5f91edf174b333952f80e13df`.

The laptop intake has now been indexed from actual source, translation and reader files. It contains serious mathematics work in Punjabi, Indian Bengali, Marathi, Telugu, Tamil, Javanese and Gujarati, plus Bangladesh Bengali and Vietnamese. See the [book-named recovery inventory](RELATED_MATHEMATICS.md). Reuse their applicable canon and infrastructure after exact-language checks; do not create duplicate mathematics producers. Their OpenStax work is not evidence of completed OpenLogic translations. No Pashto lane was present in this particular dump.

The [machine-readable candidate pipeline](catalogue/candidate-editions.json) keeps the eight not-yet-public shortlist targets and two additional motivated candidates distinct. A bounded inspection of 1,293 indexed target-source/reader files found no established OpenLogic translation start in the recovered outputs. Punjabi's apparent OpenLogic references belong to Levin source manifests; acquired OpenLogic snapshots are auxiliary sources, not translated OpenLogic sections.

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

## Additional motivated candidates outside this shortlist

**Bangladesh Bengali (`bn-Beng-BD`)** and **Vietnamese (`vi-Latn-VN`)** are also in the OpenLogic pipeline. They are not promoted into the frozen Top 10. Bangladesh's existing early-numeracy and worked-answer design and Vietnamese self-study/prerequisite design supply reusable pedagogical evidence, not a requirement to reshape the whole OpenLogic text into those textbooks. Keep faithful full-source translation distinct from optional local learning pathways.

For Bangladesh Bengali, begin with the recovered government-hosted teacher-material and dictionary passage index, preserve its regional distinction from India-standard Bengali, and add actual Bengali logic and university mathematical usage. The [bounded Bangladesh delivery checkpoint](evidence/COMPUTE_BANGLADESH_OPENLOGIC_ROUTE_20260905.json) supports phone-readable, downloadable, resumable, printable and self-contained offline endpoints; it does not supply a global rank or permission to substitute Sylheti, Chittagonian, Rohingya or other exact-language routes with standard Bangla. For Vietnamese, reuse the documented mathematical language witnesses and prerequisite crosswalks, then add logic-specific sources for proof systems, model theory, computability and metamathematics. Ordinary dictionary entries or introductory calculus examples do not by themselves attest those technical senses.

Recovered textbook production is routed through existing owners by book/work. That does not create an OpenLogic producer or silently transfer OpenLogic ownership. Each future OpenLogic owner must adopt explicit language/script scope, a source-aligned terminology ledger, per-segment canon-use records and the standard complete-reader gates.

## Production assignments — 4 September 2026

The post-intake ownership check is complete. All eight missing shortlist targets now have distinct OpenLogic owners and isolated production/state directories, recorded in [the ownership register](catalogue/ownership.json). Their initial live tasks are performing source/canon intake. The shared source handoff verifies the raw Git hashes of all 722 content files and preserves the historical checkout representation separately; none of this establishes translation or canon completion. Bangladesh Bengali and Vietnamese remain additional candidates, not newly commissioned full-edition tasks at this checkpoint.

Recovered textbook portions remain with the six existing book owners. No OpenLogic owner is commissioned to restart those textbook programmes. The first owner milestone must identify actual acquired scholarly sources, consulted passages and a real source-aligned translation boundary; acknowledgment alone is not delivery.

## Shared execution order

For every target: acquire and hash canon bytes; index passages and terms; translate against the frozen 722-file source; record canon use per segment; build one standalone reader; run language- and script-specific QA; publish editable sources, evidence, and checksums; and anonymously read the public bytes back. Adjacent-language reuse is limited to infrastructure, candidate discovery, and contrastive checking.

OpenLogic/forall x is principally a proof-and-research-access source. Treat ordinary use as U/R, or S only with explicit prerequisites. Any foundational or early-literacy package is separately authored, separately scoped, and receives no OpenLogic coverage credit. Optional prerequisite, navigation, diagnostic, or worked-answer companions supplement the faithful 722-unit edition; they never replace source units.
