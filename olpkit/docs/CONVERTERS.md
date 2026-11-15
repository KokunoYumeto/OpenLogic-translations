# HTML and EPUB converter selection

The shared implementation uses the inspected Gujarati packaging and macro-precedence code, together with source-bound import/tag/token handling. The `export` command accepts `html`, `epub` and `accessible` products from an immutable assembled source tree and an explicit hashed native-witness profile. The Javanese SLC run preserves all 176 imports, 28 native diagrams, 242 native headings, 27 caption numbers, credits and 10,645 annotated MathML expressions. Its ordinary and formula-speech EPUBs pass EPUBCheck 5.3.0. This remains a private integration candidate: assistive-technology and full rendered-reader inspection, source-package integration and the other three languages remain before T14 acceptance. Historical converter observations below describe the exact inspected versions, not current release certification.

## Shared command and native evidence

`python -I -B -m olpkit export --source <assembled-tree> --product accessible --profile <native-witness-profile.json> --out <fresh-output> --check-numbers --check-speech`

The profile selects recorded source/configuration paths and hashes the native PDF, auxiliary files, glossary, bibliography, contents, theorem list, source manifest, terminology/name resolutions, diagram batches, language-owner descriptions, edition/script metadata and component-credit policy. A changed input is rejected. The command reuses native vector exports; it does not start TeX. Native diagram export remains a separate guarded batch. The original unit files are never edited by conversion.

The accessible product retains MathML and its exact TeX annotations. It adds language-owned `alttext` and `aria-label` values to each occurrence, retaining context-specific readings. The store must match the exact indexed formula/occurrence/context packet; changed context requires a new comparison even when the formula hash is unchanged. Every reading links to a canon-backed decision rule with rationale, alternatives, uncertainty and editorial confidence. These structural checks do not themselves establish linguistic correctness or screen-reader interoperability. The language-owner review record and actual source/canon replay remain evidence for those distinct checks. The MathML `alttext` attribute is specified in [MathML 3, section 2.2.1](https://www.w3.org/TR/MathML3/chapter2.html#interf.toplevel.atts).

Output includes the reader files, local assets, the exact reader packaging profile and a private `EXPORT.json` receipt. The receipt is not publication content. It records the remaining gates rather than treating an EPUBCheck pass as release authorization. Number checking covers native heading, caption and theorem/exercise block numbers; reference destinations are checked independently.

The 13 November read-only inventory covers every repository or explicit subtree named in the hub catalogue, at exact observed Git commits. The private inventory records the full tree response, truncation status, selected source blobs, Git blob identities, SHA-256 values and source locations. Twenty-seven selected source files have been retrieved and byte-verified. These source inspections neither execute the converters nor certify their output.

## Findings that affect selection

1. **The named Persian program is an updater, not a LaTeX converter.** `build/orthography-20261029/fa_epub.py`, lines 1–7 and 19–35, opens an existing EPUB, changes XHTML/OPF text, and packages the existing web runtime. The underlying full producer is now located in the retained editable-source tree: `corpus/epub-production-full-20260912/full_export.py`, its document/math/diagram adapters, and `full_package.py`. It uses the standalone occurrence ledger and source-correction composition, not a language-neutral assembled-tree interface.
2. **The named Javanese program is the old 24-unit converter.** `tools/build-epub.py`, lines 49–79, fixes the unit list and chapter grouping. Lines 515–516 discard `olimport`; lines 930–941 load the fixed per-unit source list. Its presence beside a full-edition release does not prove that it generated that release. The anonymously downloaded v0.3.0 source ZIP matches its recorded SHA-256 and contains no Python, JavaScript or PowerShell converter files. The actual producer is now recovered: TeX4ht plus a private Python XHTML packager, whose retained bytes and release receipts were replayed independently. It was outside Git and outside the source ZIP.
3. **The first Bengali filename is also not the complete route.** `tools/build_reader_html.py` is superseded for this comparison by the combination of `build_full_semantic_reader.py` and `build_cumulative_semantic_reader.py`. The latter contains the Bengali token inflection and selector logic; comparing only the small wrapper would undercount both code and language-specific behavior.
4. **The public Arabic rebuild script packages expanded XHTML.** The 30 September source archive's `REBUILD_EPUBS.py` reconstructs ZIP bytes; it does not convert LaTeX. The actual retained producer is `build/epub/full_book/produce_current_complete_body.py`, which calls the source-scope/context renderer and `assemble_full_epub.py`. The three notation/register products remain distinct. The inspected static dependency closure is much larger than the compact Pandoc candidates.
5. **The Marathi v1.4 successor is now public.** Its eight assets were anonymously read back. A bounded replay confirms the previously failing proof has matching prose and MathML reference numbers, the EPUB link resolves, and the base/induction cases survive. This is concrete repair evidence, not an audit of every sentence. Compare the corrected producer rather than the superseded v1.3 numbering logic.
6. **A stale template is not necessarily a current reader defect.** The French `french-epub.cfg` contains old partial-edition metadata; `prepare_full_epub.py`, lines 105–162, replaces the title, author, identifier and OPF metadata for the full build. Inspect generated inputs before reporting the old template as a public metadata failure.

## Inspected implementation families

The sizes below describe individual source files, not complete dependency closures. “Language literals present” is an observed failure of the data-only criterion, not an estimate of how much extraction is required. The machine-readable inspection index includes non-ASCII string locations, but these are not an exact language-literal count: ASCII labels also need review.

| Edition / route | Actual input and expansion | Mathematics / figures | Numbering and direction | Current selection assessment |
|---|---|---|---|---|
| Gujarati | `prepare_full_epub_html.py` (1,225 lines) reads the cumulative TeX; uses source/base macro modules, final-definition precedence and balanced replacements. | Pandoc MathML with TeX annotations; separate graph, proof, operator-font and native-figure modules. | `latex_labels()` reads the current PDF auxiliary labels (lines 367–379); equation annotations acquire anchors. Current configuration is Gujarati/LTR. | Serious full-reader candidate. Requires complete dependency inventory, parameterized source/configuration, removal of language literals, RTL proof and exact current EPUBCheck receipt. |
| Javanese, named old tool | `build-epub.py` (1,066 lines) uses a fixed 24-unit manifest, token replacement and pylatexenc AST parsing. | latex2mathml and vector diagrams; unsupported macros are collected, and unknown-macro arguments may be rendered without their command. | Builds its own scoped label records; hardcoded language and labels. | Do not select this historical tool as the current 722-unit producer. The recovered full producer is listed separately below. |
| Javanese, current full route | Prepared cumulative TeX, native configuration and bibliography feed guarded TeX4ht; a private Python packager consumes 104 XHTML documents. The retained packager is about 24 KB. | MathML and TeX4ht SVG; annotation coverage and the source-specific MathML correction still need review against the selection criteria. | TeX provides counters. Code retains fixed chapter counts, language literals and a source-located mathematical repair. | Both v0.3.0 and v0.3.1 have 989 ZIP members matching their EPUBCheck 5.3.0 receipt values and full-file hashes. Both receipts report zero diagnostics. Not yet eligible as a shared base: data extraction, annotation proof and the DOM-filter recovery remain unresolved. |
| Bengali, complete route | `build_full_semantic_reader.py` (444 lines) uses `build_cumulative_semantic_reader.py` (2,269 lines); source macro expansion, tag/label selectors and Bengali token inflection. | Pandoc MathML and a separate diagram pipeline. | Source anchors and reader metadata are processed explicitly; Bengali/LTR constants are embedded in code. | Candidate family to compare with Gujarati after following all dependencies and checking actual numbering/figure output. |
| Marathi | `prepare_complete_html.py` (877 lines), `core_html_proofs.py` and packaging modules read the complete reader and expand mathematical/proof macros before Pandoc. | MathML with TeX annotations; separate diagram and operator-glyph modules. | v1.4 uses PDF-derived numbers and restores six table captions; the formerly failing prose/math reference has been independently replayed. | Reuse only the corrected, evidenced implementation. The bounded repair is verified, but shared-converter acceptance remains pending. |
| Persian, named updater / recovered full producer | `fa_epub.py` is an updater. The full producer uses a standalone ledger, effective source overlays and document adapters before Pandoc. Eleven recovered modules plus explicit dynamic entry points total 6,649 Python lines. | Native MathML and SVG through separate adapters; full-source package keeps the converter inputs. | RTL is explicit; occurrence and reference crosswalks carry numbering. Target-language metadata and source-specific repair dependencies remain embedded. | Full producer recovered and hashed, not executed here. Its exact private inputs are not a general assembled-tree interface. |
| French | `build_full_reader.py` orchestrates prepared TeX through a guarded TeX4ebook/TeX4ht route; `prepare_full_epub.py` handles the full source graph and configuration. | Configuration requests MathML; proof environments use TeX4ht picture handling. The complete annotation and figure pipeline still needs inspection. | TeX supplies counters; recorder checks compare loaded source units. Language metadata is generated for the full build. | Candidate engine-based route. Requires exact math-annotation, direction and dependency comparison; do not compare only its small wrapper. |
| Punjabi | `build_sets_epub.py` is a sets-scoped Pandoc pipeline; `web/package_cumulative_epub.py` is a separate cumulative packaging path. | MathML annotation coverage is explicitly checked; accessible SVG figures. | RTL body is explicit. Full producer/numbering route remains to be followed. | Useful RTL evidence; bounded producer does not prove cumulative generality. |
| Pashto | `build_cumulative_epub.py` contains the cumulative Pandoc conversion and macro handling. | MathML and a separate figure-rendering pipeline. | Includes LTR equation-number spans within the RTL edition. | Candidate RTL implementation; language/configuration extraction and PDF-number comparison remain. |
| Tamil | `build/build-epub-html.ps1` drives make4ht under a Windows process guard; `epub/package_epub.py` packages the result. | Native MathML is requested; source-derived alternative text and figure handling require complete review. | TeX auxiliary files are carried into conversion. | Candidate engine-based route. No converter was executed during this inventory. |
| Telugu | `scripts/build-html.mjs` imports `tex-reader.mjs`, `tag-projector.mjs` and `bibtex-reader.mjs`; manifest identifies source units. | Actual renderer and mathematics implementation are in dependencies still to inspect. | Source-unit anchors and Telugu navigation are emitted; labels are code literals. | Dependency closure and exact output evidence required before selection. |
| Dutch, both registers | Each register contains copies of `build_partial_epub3.py` and `epub3/direct_latex.py`. | Direct LaTeX parsing and EPUB assembly; full mathematics/diagram behavior remains to inspect. | Paired register copies are not two independent converter families. | Current published scope is partial; test generality against the assembled textbook before selection. |
| Arabic, recovered full producer | Source-scope and contextual-driver graphs feed a direct complete-body producer. Thirty-eight static dependency modules total 32,573 Python lines. | Custom MathML adapters, proof trees and figures. Every MathML formula in all three inspected expanded public EPUBs has a TeX annotation. | Explicit modern/Classical profiles and international/Machrek notation; fixed occurrence counts and source-bound rules. | Source witnesses recovered. Larger and substantially more tied to a particular edition than the Gujarati family; no generalization or full semantic audit claimed. |
| English accessibility | `whole_book_epub33/build_epub33.py` packages a sealed multi-profile HTML tree; the synchronized adapter adds occurrence-specific speech. The final HTML integration also consumes earlier generated trees. | Existing MathML, source/formula crosswalks and spoken alternatives are preserved. | English profile names and exact historical input-tree hashes are embedded. | Useful speech/accessibility evidence, not a standalone source-to-HTML converter. The three recovered packaging/integration entry points total 2,728 lines, excluding earlier producers. |

## Catalogue coverage and unresolved producer locations

The accompanying generated repository table records all catalogue rows, including English source preservation and accessibility infrastructure. A repository with no matching public source path is labelled **not located**, never “no converter exists.” Historical release bundles and bounded local producer paths remain possible sources. Latin-script variants and multiple registers sharing a repository are retained as distinct edition IDs.

The following still prevent completion of T13:

- Trace the remaining release-only producer locations where public source paths are absent. The named Arabic, Persian and English accessibility production stages have now been recovered; English packaging still relies on earlier generated HTML rather than accepting an assembled source tree.
- Follow each candidate's imports and helpers; count the whole implementation and actual language-specific literals, not wrappers or generic dependency code.
- Bind the latest relevant EPUBCheck report to the exact EPUB bytes; a repository status, catalogue claim or historical pass is insufficient.
- Demonstrate assembled-tree input, configuration-derived tags/tokens, MathML with source annotations, data-only language strings and an error-free EPUBCheck result on the same candidate.
- Choose the smallest implementation only among candidates meeting those five criteria. No current candidate is being represented as having passed all five.

Source witnesses and their exact locators are in `CONVERTER_REPOSITORIES.md`; the private source manifest retains every inspected blob identity. Existing converters and published editions remain unchanged.

The Javanese manager replay checked 28 exact producer/input/receipt files and both 989-item EPUB inventories. EPUBCheck serializes checksum bytes without hexadecimal zero-padding; replay uses that observed representation, while separate full-EPUB SHA-256 values provide canonical hashes. The initial replay that assumed ordinary hexadecimal is retained privately as a corrected verification error, not a publication defect.

Direct XML inspection now settles the Javanese annotation criterion: v0.3.0 contains 38,301 MathML formulas and v0.3.1 contains 38,303; neither contains a MathML annotation element. All 105 XHTML documents in each archive have the correct `jv-Latn-ID` root language, but none has an explicit root direction. The 105 documents include navigation in addition to the 104 spine documents. These exact producers therefore do not meet T13's MathML-with-LaTeX-annotation criterion as they stand, despite their clean EPUBCheck receipts. This does not establish incorrect formula meaning or withdraw the existing editions. A shared successor would need source-bound annotations and data-driven direction, with direct output checks.

The same direct inspection of Gujarati `full-edition-v1.2.0`, SHA-256 `ac83f2d010a3a752434e1d7ac00bfbe694d4f5e94502eb2c270698b5f39ff320`, finds 40,993 MathML formulas and 40,993 nonempty `application/x-tex` annotations. All 109 XHTML documents explicitly set `lang="gu-Gujr-IN"` and `dir="ltr"`. This establishes annotation and direction coverage in that exact output, not semantic equivalence of every formula or general RTL support. Gujarati remains the stronger inspected candidate for these format requirements; source/configuration generalization and language-literal extraction still require evidence before selection as the shared base.

## Gujarati dependency closure and reusable packaging

At commit `085336b59ab402c2daae25216371b9ecae08ceb7`, the two Gujarati entry points have a static local Python dependency closure of eleven modules, 2,404 lines and 133,328 bytes. AST inspection finds 52 Gujarati string-literal nodes. This does not count every reader-facing literal, external package, font, TeX input or generated vector. The current native-figure helper binds editable figure sources and preamble/include hashes; its retained `PDF_SHA = None` is a compatibility value, not a dependency on an old PDF.

The source-to-HTML stage remains under comparison. Separately, `olpkit.epubpackage` adapts the released `build_full_epub.py` packaging stage, with its namespace helpers from `epub_utils.py`. All edition text and resources are supplied as data. This is reusable infrastructure, not selection of the complete Gujarati converter under T13.

A full-size regression reconstructs a packaging input from the exact published Gujarati EPUB, then repackages it without changing its translation. All 722 unit anchors, all 106 chapter text streams, 40,993 MathML trees with annotations, and all resource bytes are preserved. Internal mathematical links are compared by their resolved target identity when chapters are split. Two runs produce identical bytes. The result passes EPUBCheck 5.3.0 with zero errors and warnings. This proves the measured packaging properties only; it does not prove source-to-HTML conversion, PDF-number parity, visual equivalence or spoken mathematics. Small tests also exercise RTL metadata and reject a superscript-to-subscript mutation despite unchanged visible text.

## Implementation basis and remaining acceptance

Use the Gujarati Pandoc family as the basis for the shared adaptation, retaining its source-defined notation and PDF-derived numbering. This is an implementation choice, not a claim that T13's five acceptance criteria already pass. No existing inspected producer has demonstrated all five unchanged; in particular their reader-facing strings are embedded in code. T14 explicitly requires extracting those strings into data. The integrated adaptation must pass the original five criteria before T13/T14 acceptance. The final least-code comparison among qualifying implementations remains open; raw line counts alone do not establish it.

The retained Arabic source archive is 35,148,175 bytes, SHA-256 `81f8a0865b19a9bcd7f0ddfa40f03a000a0febbac339ea2deaeedcb85b05f937`. Its expanded international and Machrek EPUB sources each contain 49,509 MathML expressions, and Classical contains 49,541. All have nonempty TeX annotations; all 812 XHTML documents per product explicitly use `lang="ar"` and `dir="rtl"`. These are format observations on exact archive members, not a translation-quality or current-release certification. The recovered local producer bytes are separately hashed and are not assumed to be identical to that public release's complete production inputs.

`olpkit.macrophases` reuses the Gujarati macro-precedence method as a pure function. It preserves authored phase order, records exact source/emitted declaration hashes, and keeps the final top-level definition because Pandoc otherwise keeps the first duplicate `newcommand`. Comments and scoped definitions cannot accidentally replace a top-level declaration. A real Pandoc regression proves the difference. Three literal phases from the recovered Gujarati producer, comprising 213 definitions, produce byte-identical merged text. Dynamic font/source phases, arbitrary TeX execution, import expansion and book conversion are outside that component check.

`olpkit.selective` adapts the recovered Persian selector, with native OLP scope, configuration order, paragraph arguments, environment exclusions and tagged-problem behavior. `olpkit.bookprojection` applies it to immutable assembled inputs, expands only recorded localized imports, executes the book's chapter-summary hooks, and defers exercises to chapter ends. It retains mathematical macros, tokens and reference commands for the Gujarati-based conversion stage. Its output is intermediate source, not a reader or a completed HTML export.

The assembled Javanese SLC replay covers all 176 recorded imports, its preface, all 12 summary files and 144 deferred exercises. The ordered exercise numbers agree with the existing English reference auxiliary file at the same four source pins. This does not substitute for the final translated-PDF number check. Native `probtag` currently discards its tag argument; the projection preserves that behavior instead of silently dropping exercises. A native blank-line argument in `main-operator.tex` is treated as a paragraph token, so the following table is retained. No translation files are edited.

`olpkit.texttokens` now expands the projected text from the actual native token
package and ordered edition/book configuration. The native package is bound to
its inspected SHA-256; the xparse branch is selected from an existing native
build's package-version evidence. Token forms, articles, uppercase alternatives,
plural/passive suffix behavior and helper bodies come from source, rather than
language literals in Python. Definitions remain opaque until invoked; groups
restore local assignments. Unsupported token-bearing execution fails explicitly.
This bounded token interpreter does not execute arbitrary TeX or replace the
mathematical-macro conversion stage.

The Javanese SLC replay expands 2,347 occurrences from 117 used definitions, all
in its Javanese configuration or book override files. Each occurrence records
its exact projected-source range and the defining source locations/hashes.
An independent splice of only those ranges reproduces the output exactly:
surrounding source and mathematics remain byte-for-byte unchanged. This is a
conversion check, not a new translation or a claim of expert linguistic review.

`olpkit.mathsource` adapts the source-declaration and balanced-argument approach
of the Gujarati producer. It evaluates the authored xparse choices, mandatory
and optional arguments, captured aliases and first-token formatting. Formula
alphabets are read from the native style and selected by the actual configuration
calls. In SLC, the book's Latin formula letters therefore supersede the default
Greek letters. The older converter's hardcoded Greek mapping cannot be reused
unchanged for this book. Macro definitions and calls have source locators and
hashes. Unsupported eager/global definitions and conditional execution fail.

The complete Javanese projection expands 10,674 source macro calls and 4,090
formula shorthands. A private Pandoc probe renders 10,200 MathML expressions with
TeX annotations. It still emits 69 warnings: native figures/proofs, compound
operators and display constructs need their conversion stages. It is not a
publishable reader. Source-declared font weight and shape have MathML equivalents;
this does not certify identical font faces or glyph geometry. The probe also
exposed and fixed two control-sequence joins caused by removing active formula
shorthand characters; focused regressions retain TeX token boundaries.

The next acceptance work is the remaining display/proof/figure conversion,
PDF-derived references, front matter, glossary, bibliography, credits, full
HTML/EPUB assembly and accessible formula speech. The original five acceptance
criteria and all book-unit requirements remain open. Repeating closed archive or
packaging checks does not advance that boundary.

`olpkit.mathdisplay` now adapts the Gujarati producer's balanced `intertext`
splitting and nested text/math conversion. It preserves the actual prose and
source formulas, with no language literals. Numbered alignments cannot be split
without PDF-derived numbering. Source-mode handling was also repaired: an
`intertext` argument is text containing its own inline math, not continuation
of the enclosing display's math mode.

Marked expressions retain their input TeX in MathML annotations. The binding
stage restores bevelled fractions and explicit multline row alignment. The
source's double-bar turnstile remains two vertical bars joined to an equals
sign with the native `joinrel` spacing. The recovered producer's substitution
with `Vdash` loses a horizontal bar and is not reused. Unresolved markers fail
strict binding; a diagnostic mode reports them without allowing publication.

The full Javanese replay now expands 4,097 formula shorthands and renders 10,298
MathML expressions, each with a nonempty TeX annotation. Fourteen intertext
blocks and 45 text/math spans are recorded. Unconverted expressions fall from
69 to 33; three markers are inside displays still awaiting actual reference
binding. Partial-function overlays, three small arrays, native diagrams, a
proof tree and a transition table also remain. This is not a completed reader
or visual-equivalence claim. The original replay and its failure evidence are
retained; no translation source or published edition was changed.

`olpkit.proofmath` replaces the recovered proof template's permissive command
search with an inference-stack parser that consumes every command. The source
has multiple trees inside some `prooftree` environments; stopping at the first
`DisplayProof` would lose the later trees. Both discharge and rule labels are
retained. Dotted deductions, double rules and absent rules remain distinct in
MathML. Source-mode handling also distinguishes native dollar-delimited proof
arguments from surrounding display math. Label-size mappings are supplied from
the actual memoir/newtxmath configuration, rather than assumed for every book.

The new full Javanese replay covers 165 proof regions containing 176 trees,
264 axioms/premises and 408 inference steps. An independent source command scan
maps every live proof command to exactly one rendered region, and the original
proof text remains in annotations. These are structural and source-binding
checks: native baseline alignment, tight premise spacing and actual rendered
proof appearance still need visual comparison. There are 32 remaining math
fallbacks; warning counts alone did not reveal the earlier loss of proof
structure and are not a completeness gate.

`olpkit.nativefigures` adapts the Gujarati native-vector manifest route to the
assembled book. It extracts active TikZ outside definitions/verbatim, prepares
one batch using the actual book preamble, and binds vector exports to source
and recorder hashes. It uses the shared TeX mutex and capped process runner;
an occupied slot returns without starting an engine or copying the source tree.
For SLC, 19 diagrams are prepared. The first attempt found the slot occupied;
no native PDF/SVG or visual acceptance is claimed yet.

Reusing the recovered Turing renderer unchanged would be wrong here: its
fixed blank/stroke symbols are `0`/`1`, whereas the SLC book configuration uses
`\sqcup`/`I`, and the native edition sets its own initial-state text. The native
route retains these definitions, placement options and every editable diagram.
The figure inventory includes diagrams outside the math-warning list. Native
figure assets, source-matched references, remaining operators/tables, book
matter and all four languages' complete export acceptance remain open.

Native-figure attempts can resume the existing prepared batch only when the
previous receipt proves that no engine ran. Source, preamble, configuration,
individual figure bytes and batch bytes must match; a per-directory lock
serializes invocation. The original receipt is retained. This avoids another
assembly copy and does not authorize mutex polling or restarting a live build.

Partial-function overlays are represented by U+21F8, whose vertical stroke
crosses the arrow shaft, preserving the mathematical distinction from mapsto.
Original TeX remains in the annotation. Small arrays use the edition's native
font-size ratio, retain intentional blank rows/cells and suppress only the
spurious final row Pandoc otherwise adds for a terminal row delimiter. The
native Javanese reader has 10pt table type against 10.95pt body type; its
observed PDF sizes corroborate the source font settings. Other configurations
must supply their own size data.

`olpkit.tabular` parses supported source table columns, spans, rows and rules
before Pandoc. Unhandled specifications fail. This is necessary because the
unmodified reader prints cline ranges in cells and displaces state labels in
the transition table. The adapter retains every cell's TeX, renders invisible
width material as MathML mphantom, checks the rendered row/cell/span counts and
applies borders from the original rules. Header semantics, visual layout and
complete product acceptance remain separate requirements.
# Native textbook references

`olpkit.references` resolves executed OLP labels and relative references using
the auxiliary file from the corresponding translated textbook. The caller
must reconcile that witness with the actual assembly; an English or full-corpus
auxiliary file is not an acceptable substitute. The adapter records the aux
identity, source spans, scoped namespaces, selected `oliflabeldef` branches,
reference names and ordered targets. Missing native labels, unsupported list
formats and unknown localized type names fail explicitly.

Imports, explicit groups, environments and deferred exercise context assignments
retain their native reference scope. Definitions and `let` assignments are not
executed as displayed text. The DOM binding supplies links in prose and MathML,
keeps stable destination IDs, and restores original reference commands in the
TeX annotations. It runs after display binding. A source anchor is not a claim
that the theorem's complete visual presentation has been accepted.

The Javanese SLC replay reconciles all 176 imported units and 144 exercises with
the existing translated native source. Its 250 reference calls, 370 body
anchors and 3,391 counter events agree. Explicit source-defined text and font
shims, bibliography path normalization and whitespace account for the source
differences. Nine native photo-credit labels belong to front/back matter still
outside this body binding. The probe has 266 links with unique, existing targets;
the two reference-bearing equation fallbacks now render. Native TikZ conversion,
full front/back matter, visual and accessibility checks and complete EPUB
acceptance remain required.

The projection also protects control-word boundaries when expanding `input`:
an imported word immediately after `let` must not become part of the preceding
command name. Use the textbook's actual environment configuration, including
its exclusions, rather than the default corpus environment file.

## Native diagrams and theorem blocks

`figurebinding` verifies the complete ordered diagram inventory against the
native batch, including repeated source bodies. It checks every editable TikZ
file and SVG by hash before substitution. Figure-only math displays become
vector images; a display with additional mathematics fails rather than losing
that mathematics. Prose between diagrams and occurrence order are preserved.
The library has no localized labels: the caller supplies the source's figure
name and substantive descriptions. A generic label is permitted in a private
diagnostic preview only; missing descriptions remain an accessibility gate.

The Javanese batch now has 19 native vector assets, produced in one successful
guarded pdfLaTeX invocation. All were inspected after independent SVG rendering
as well as in the native PDF batch. The actual source configuration retains
the blank and stroke symbols, transition labels, initial-state text, isolated
vertices, loops and all tree branches. These assets total 390,881 bytes. The
complete SLC body replay now has no unconverted math nodes or Pandoc warnings;
this alone does not establish complete book or accessibility acceptance.

`theoremblocks` reads the native ntheorem contents stream and reconciles its
ordered types and titles against the actual native projected source. It then
uses those numbers with the current source's full titles and localized names.
It prevents Pandoc from dropping custom theorem headings or supplying its
English proof label. Each block's source span and native witness are recorded.
The end-of-proof symbol is supplied from the actual class configuration.

For Javanese SLC, all 663 blocks reconcile: 524 numbered theorem-like blocks
and exercises, and 139 unnumbered proof headings. The proof counter stored in
the native auxiliary stream is deliberately not printed. A custom proof title
and its cross-reference are retained. Full book headings, front/back matter,
credits, descriptions, speech and complete HTML/EPUB visual acceptance remain
open; the intermediate body is not a release artifact.
