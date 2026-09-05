# Script and orthography policy

OpenLogic editions are not multiplied merely because text can be converted into another character set. Every proposed surface is assigned one of five production types before work begins:

1. **Notation or typography profile:** the same linguistic translation with different digits, formula conventions, or fonts. It shares one semantic record and may have several readers.
2. **Deterministic script projection:** one constructed-language semantic record rendered in another script. It requires a reversible mapping and exception ledger, but is not credited as a second translation.
3. **Pronunciation accessibility companion:** an ID-aligned, pronunciation-resolved surface for readers who understand the language but may not read its usual script. It is distinct from graphemic transliteration and never replaces the native surface.
4. **Separate language or locale edition:** terminology, syntax, register, or educational convention differs. It requires its own scholarly canon, segment decisions, semantic QA, build, and publication evidence.
5. **Research candidate:** reader need, mapping quality, or specialist terminology evidence is not yet sufficient for a 722-unit production lane.

The machine-readable decisions are in [`catalogue/script-surfaces.json`](catalogue/script-surfaces.json). Mixed right-to-left prose and left-to-right mathematics must follow the [Unicode Bidirectional Algorithm](https://www.unicode.org/reports/tr9/); script-specific digits and numeric direction are tested rather than assumed from an Arabic profile.

## Surfaces already in use

| Edition | Current surfaces | Type and decision |
|---|---|---|
| Arabic `ar-Arab` | international mathematical digits; Machrek Arabic-Indic mathematical notation | Two notation profiles over the same Arabic translation. Both standalone 722-unit readers are retained; no third linguistic edition is implied. |
| Iranian Persian `fa-IR` | Perso-Arabic | Separate Iranian Persian edition. Dari and Tajik are not automatic variants. |
| Conceptual Inter-Farsi | Perso-Arabic; Tajik Cyrillic; mechanical Latin mappings; pronunciation-resolved Latin | The first two are constructed surfaces over a shared semantic layer. Mechanical transliteration and pronunciation accessibility remain separately labelled outputs. |
| Interslavic | editable Latin authority; deterministic Cyrillic projection | Keep one semantic record, an exception ledger, and two rendered surfaces. |
| Inter-Turkic | Latin; Cyrillic; Arabic | Keep the synchronized constructed-language architecture; audit mapping exceptions and rendered usability. |
| Pakistan Punjabi `pnb-Arab-PK` | Shahmukhi in Naskh and Nastaliq | Two typography profiles over one Punjabi translation. Gurmukhi needs a separate Indian Punjabi edition. |
| Javanese `jv-Latn-ID` | Latin | Latin remains primary. Aksara Jawa is research-only until reader need and rendering support are evidenced. |
| Mainland Chinese `zh-Hans-CN` | Simplified Han | A Traditional Chinese edition is worthwhile, but needs an explicit locale and independent terminology QA—not blind character replacement. |
| Hindi, Bengali, Marathi, Telugu, Tamil, Gujarati | their current native production scripts | No generic Latin duplicate. Marathi Modi is historical/research-only for this scientific reader. |
| Pakistan Pashto `ps-Arab-PK` | Pakistan Pashto orthography in Arabic-derived script | Afghan Pashto is a regional language/register edition, not a character variant. |

Unicode’s script chapters support these boundaries: [Gurmukhi is associated with East Punjab while West Punjabi uses Arabic script](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-12/); [Modi ceased to be the standard Marathi script in the mid-twentieth century](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-15/); and [Javanese has substantial implementation and shaping requirements](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-17/). These facts identify script constraints; they do not substitute for language-specific canon evidence.

## Recommended separate editions

The strongest next script-related routes are:

- `pa-Guru-IN`: Eastern/Indian Punjabi in Gurmukhi, paired by segment with Pakistan Punjabi where useful but independently canonized and translated.
- `ur-Arab-PK`: Urdu in Nastaliq, aligned with Hindi for comparison but governed by Urdu scholarly usage.
- `prs-Arab-AF`: Dari with Afghan canon, terminology, orthography, and locale QA.
- `tg-Cyrl-TJ`: Tajik in Cyrillic with Tajik canon; Inter-Farsi may supply hypotheses, never automatic acceptance.
- `zh-Hant` with an explicit target locale: Traditional Chinese terminology and educational register checked independently of the Mainland Simplified edition.
- `kmr-Latn` and `kmr-Arab`/Badini only when each route has explicit regional provenance; neither is a free rendering of the other.

These are edition candidates, not a claim that all should outrank every other missing language. The allocation research currently supplies package-design constraints, not a validated global language ranking.

## Research pilots, not automatic full readers

- Hausa Boko/Latin and Hausa Ajami.
- Wolof Latin, Wolofal/Ajami, and Garay.
- Named Manding language editions and a possible N’Ko shared layer. N’Ko is right-to-left and its numeric behavior is script-specific; see the [Unicode N’Ko chapter](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-19/) and [Unicode numeric notation guidance](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-22/).
- Central Asian multi-script cohorts only as separately evidenced language/script packages, not as one regional converter.

Do not currently commission generic Latin transliterations of Indic editions, full Marathi Modi or Javanese-script duplicates, Gurmukhi generated from Shahmukhi, Urdu generated from Hindi, Tajik or Dari generated from Iranian Persian, or Traditional Chinese produced by character substitution and presented as a complete educational edition.

## Required QA for every additional surface

A profile or projection must preserve source and segment IDs, formulas, citations, links, and semantic record hashes; publish its mapping and exception ledger; pass Unicode normalization, BiDi isolation, glyph coverage, copy/search extraction, line-breaking, and representative rendered-page checks; and report coverage separately from the authoritative translation. A separate edition additionally needs its own machine-readable canon-use records and semantic review. The public evidence basis for these decisions includes the [adjacent allocation findings audit](evidence/ADJACENT_COMPUTE_ACTIONABLE_FINDINGS_20260905.json) and the edition-specific records in [`catalogue/editions.json`](catalogue/editions.json).
