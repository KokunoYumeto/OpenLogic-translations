# Canon-first Open Logic translation standard

## 1. Freeze the semantic authority

Bind the edition to an exact upstream commit and enumerate the 722 tracked English content files. Assign a stable ID to every file or finer semantic segment. Preserve the source path, exact bytes, SHA-256, order, hierarchy, links, citations, labels, references, formulas, code, and intentional incompleteness.

No adjacent-language edition is semantic authority. An earlier translation can expose workflow lessons and candidate terminology, but discrepancies return to the frozen English source and its cited primary material.

## 2. Build and use a target-language canon

Before production, acquire lawful target-language mathematical-logic sources: official scientific terminology, current regional educational materials, university texts, research articles, dictionaries, grammars, and style authorities. Preserve original bytes and licensing metadata; create searchable normalized copies without replacing the originals.

Create machine-readable document, passage, term, citation, and hash indexes. Each translated segment must record the exact canon passage IDs and term IDs actually consulted. A bibliography that cannot be traced to decisions is not canon use.

When earlier source/canon work has been recovered, give the edition owner exact indexed original paths and hashes. Reconcile those references with new acquisitions and record what is reused, duplicated, irrelevant or superseded. The owner must actually read the relevant originals; an inherited consultation claim or old QA receipt is not fresh consultation or current acceptance. Date later re-review honestly rather than retrospectively claiming that newly read sources informed an earlier release. Preserve regional distinctions and separate local-needs learner adaptations from faithful source translation.

A minimum aligned record contains:

```json
{
  "segment_id": "OLP-0001:S0001",
  "source_path": "content/example.tex",
  "source_sha256": "…",
  "target_sha256": "…",
  "canon_passage_ids": ["CANON-DOC-001:P0042"],
  "term_ids": ["TERM-0001"],
  "decision_ids": ["DEC-0001"],
  "status": "accepted"
}
```

## 3. Keep language and presentation layers distinct

The production model has four typed layers:

1. **Semantic translation** — target-language wording and grammar.
2. **Regional adaptation** — a separately evidenced standard such as Iranian Persian, Dari, or Tajik; it requires its own canon and decision record.
3. **Script projection** — a documented mapping of the same linguistic register into another script. Every non-reversible or ambiguous mapping requires adjudication.
4. **Notation profile** — presentational choices such as international versus Machrek Arabic-Indic mathematical digits.

Transliteration is not translation. A script or digit profile must never be advertised as a second independently translated language. Conversely, a regional standard must not be reduced to a font or character substitution.

## 4. Preserve mathematics and TeX structure

- Preserve formula token order, variable identity, scope, quantifier force, proof direction, labels, citations, URLs, and code identifiers.
- Keep mathematical isolates left-to-right inside right-to-left prose. Use explicit BiDi isolation rather than relying on incidental engine behavior.
- Localize prose and permissible notation only. Do not transform source paths, labels, URLs, Latin/Greek variables, or machine identifiers.
- Maintain one source-to-target closure ledger. Report missing, duplicated, reordered, placeholder, untranslated, and structurally divergent segments as deterministic failures.

## 5. Deliver a genuinely complete reader

The ordinary upstream reader graph reaches 642 of the 722 tracked files. For this programme, “standalone 722/722 reader” means that the other 80 tracked units are incorporated in an explicit, navigable section of the same PDF. Keeping them only in editable sources or a separate supplement is source-complete but not standalone-reader-complete.

Those 80 paths are not necessarily 80 chapters. Distinguish omitted mathematical reading content, shared contextual imports, alternative drivers and formal-only controls. Document placement and legitimate repetition, isolate conflicting alternative namespaces, and verify the actual build closure. Do not satisfy a file count by blindly duplicating chapters or inserting empty headings.

Legacy editions may retain the 642+80 architecture, but the catalogue must say so. Future complete editions should ship:

- one primary standalone 722-unit reader;
- editable sources;
- source, canon-use, decision, build, and QA evidence;
- an external SHA-256 manifest.

## 6. Script-specific QA

Every edition runs UTF-8/NFC, replacement-character, raw-command, placeholder, citation, reference, link, formula, label, and structure checks. Additional gates include:

- **Arabic-derived scripts:** joining, combining marks, mirrored punctuation, digit policy, Nastaliq/Naskh behavior where relevant, and LTR math/code isolation;
- **Indic scripts:** grapheme clusters, conjuncts, vowel signs, line breaking, font fallback, search/extraction, and formula-boundary shaping;
- **CJK:** punctuation, line breaking, glyph coverage, vertical metrics, Latin/math spacing, and searchable text;
- **Latin/Cyrillic projections:** normalization, round-trip exceptions, language-specific diacritics, and cross-script alignment.

Build under the project’s machine-wide TeX mutex. Require zero fatal errors, unresolved citations/references, missing glyph diagnostics, broken internal targets, or out-of-page links. Perform all-page automated geometry/raster checks and representative original-detail visual inspection; record limitations such as untagged PDF or missing ToUnicode honestly.

## 7. Validate meaning and terminology

- Compare source and target semantic propositions, not just token counts.
- Back-translate stratified samples, including definitions, theorem statements, proofs, exercises, captions, and high-risk negation/quantifier passages.
- Run corpus-wide term consistency checks with documented allowed variants.
- Identify whether semantic review is same-agent or independent. Hash/reference integrity, successful compilation and sampled reverse-paraphrase do not certify every sentence or native-register choice. Keep explicit uncertainty and continue source-bound review without mislabelling the evidence.
- Log genuine upstream errors separately from translation choices. Do not silently inherit an obvious source typo when the intended reading is established; preserve evidence and report it upstream.
- Reuse stable cross-edition finding IDs from [shared source notes](SOURCE_NOTES.md). Verify the cited frozen bytes before applying a correction, keep the untouched source in provenance, and distinguish a false theorem, a wording defect, a terminology imprecision, and an explanatory inconsistency. A copied `upstream` directory without its own `.git` must be identified by its archive/manifest/file hashes, not by a parent repository HEAD discovered through directory ascent.

## 8. Publish and read back

Use the established GitHub repository and Zenodo concept lineage. Preserve historical assets. Publish only non-duplicative, privacy-safe packages with no credentials, private paths, or personal names. After publication, anonymously download each new artifact and verify filename, byte count, and SHA-256 against the sealed local manifest.

Statuses are evidence claims:

- `verified-standalone-722`: all tracked sources translated and present in one reader, with QA and public readback;
- `published-source-722-reader-642`: all sources translated, but 80 remain outside the reader;
- `partial-n/722`: exact accepted prefix or set only;
- `scaffold`: structural or provisional content not canon-admitted as a finished edition;
- `cross-mirror-repair`: GitHub, Zenodo, or README identities do not agree;
- `audit-needed`: a public claim exists without enough replayed evidence for a stronger label.
