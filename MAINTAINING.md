# Maintaining an Open Logic edition

Start here when the English sources change. The [Open Logic Project](https://github.com/OpenLogicProject/OpenLogic) supplies the mathematics. This hub lists language editions in `registry.toml`. Each edition repository owns its translations, scholarly terminology, reader formats and releases. A textbook such as *Sets, Logic, Computation* selects units from that content and adds its own preface, summaries, glossary, driver and credits. A change in one unit can affect the full reader and several textbooks.

## Maintaining these editions yourself

The editions are maintained here, and requests are welcome through [the hub’s issues](https://github.com/KokunoYumeto/OpenLogic-translations/issues). You can also maintain an edition from your own checkout. For the translation work, a coding agent signed in through an ordinary Codex or Claude Code subscription can read and edit the packet. Packet preparation, compilation, checks and release use command-line tools. They require no model-provider API key, paid API calls, access to another maintainer’s computer or Zenodo account. The share of a subscription needed to update all editions over a monthly release cycle has yet to be measured.

Install Git and Python 3.11 or later for the planner. To build and publish, use a GitHub account, the GitHub CLI and the TeX engine, fonts and format tools listed under [Build and check](#build-and-check). The native textbook build currently uses Windows. The packet tools also run on Linux.

If you work from forks, fork the hub and the editions you want to publish. Clone your hub fork as `origin`. Enable Issues and GitHub Actions there, including the **Upstream source changes** workflow. It reads the original Open Logic sources and posts advisories to the hub checkout’s own repository. To publish an edition from your fork, set its repository URL in its edition contract and catalogue record, and set the corresponding URL in your hub’s `registry.toml`. For a legacy catalogue entry, update the matching file in `catalogue/legacy/`. A GitHub transfer likewise requires checking these URLs. Read back your release links and regenerate the hub. Earlier releases, original source credits and immutable source citations keep their original identities.

For each new upstream release:

1. [Plan the update](#find-the-changes) for the edition with `--to YY.MM` and verify the resulting packet.
2. [Translate the delta](#translate-the-delta) against the existing edition and its cited canon. Record which passages already incorporate the correction.
3. [Build and check](#build-and-check) the complete reader and each textbook that imports the changed units.
4. [Stage and publish](#publish-and-regenerate-the-hub) to the edition repository you control. Verify the downloadable readers and editable sources.
5. Regenerate the hub catalogue and check that its reading and download links lead to your edition.

## Find the changes

Install Git and Python 3.11 or newer. In the commands below, use the Python interpreter that reports that version. The planner uses the standard library. A public clone suffices for preparing and verifying packets.

```sh
git clone --filter=blob:none https://github.com/KokunoYumeto/OpenLogic-translations.git
cd OpenLogic-translations
python maintain.py plan --out ../olp-packets
```

Use a new output directory for each run. Use `--edition mr` for Marathi or pass an edition ID from the registry. Omit `--to` to use current upstream master. For an inventory without the target files, add `--summary-only`. The optional `--cache` names a reusable directory for upstream Git objects.

The Marathi acceptance case has fixed English and Marathi starting points. This lets the exercise be repeated after either project advances.

```sh
python maintain.py plan --edition mr --edition-commit c5bd5d8e74a89bd4efda2f495551ee85520c296a --to a216aa641a823b861974b5612579aacbf59fd015 --out ../marathi-packets
python maintain.py verify-packet --packet ../marathi-packets/openlogic-mr-deva-in
```

Open `summary.json` first. Each edition directory contains `edition.json`. Read its `pin_evidence`, `issues`, and the issues on individual units. A shared catalogue freeze is a lead to investigate. Establish the edition's actual starting commit from its published sources before editing. The frozen English reference deliberately retains its original pin. Several registers or scripts can share a repository. Use the content tree and spelling rules belonging to the product you are updating.

Each unit directory contains the English `before.tex` and `after.tex` where present, the Git diff, and the current target where located. `unit.json` records the file identities and term matches. The edition directory includes the available terminology, spelling rules, canon passage index and canon source index. The shared `upstream/<old-commit>/files.json` describes changes to styles, images, drivers and other non-unit files. Its blob files retain the original bytes. `verify-packet` replays the original pins, detects changed or missing files, and works even after the edition advances. Keep translations and new notes outside that original packet.

For French, Pakistan Punjabi, Pakistan Pashto, Tamil and Telugu, the planner can recover the starting revision from the source manifest in the edition repository. It compares every recorded English file with the corresponding upstream Git blob and checks the stable unit identifiers. The full packet includes the exact manifest. Review each changed unit against its current translation to see which upstream corrections have already been incorporated.

French packets also list the earlier translation choices that the edition links to segments in each changed unit. `prior_segment_choices` points to numbered records in the accompanying terminology file, starting at one. Read the recorded rationale and cited passages before deciding whether a choice still fits the changed English. An empty list means the indexed file supplies no such choice for that unit.

The [French comparison of nine corrections](maintenance/reviews/openlogic-fr/9cf6715a.json) links the English before and after each correction to the corresponding French lines. Two entries distinguish a correct French formula from a footnote that describes the older English source. To recover the passages at their recorded revisions:

```sh
python maintain.py plan --edition fr --edition-commit 0ef12147a948c09d02319e1d075b713db44e7778 --to 9cf6715abaf33c45911c2380562fcd3d8e7636ba --out ../fr-review-packet
python maintain.py verify-packet --packet ../fr-review-packet/openlogic-fr
python maintain.py verify-review --packet ../fr-review-packet/openlogic-fr --record maintenance/reviews/openlogic-fr/9cf6715a.json
```

The last command checks each cited file and excerpt against the record. Read the linked passages to assess the mathematical judgment or apply it to a later edition.

## Translate the delta

For a monthly Open Logic release, pass its published `YY.MM` tag to `plan --to`. The packet uses the exact commit behind the tag, including when Git stores it as an annotated tag. To inspect the source tags currently associated with each edition, run `python maintain.py plan --summary-only --out ../olp-tag-inventory` and read each edition’s `from_upstream_tag` beside its commit and pin evidence.

Once you set `pins.olp.commit` to the reviewed source revision in the edition checkout, record its upstream tag before committing the edition metadata and verifying the build:

```sh
python maintain.py upstream-tag --edition-dir ../edition
```

The command writes the top-level `upstream_tag` in `olp-edition.toml`. It records `none yet` until the first monthly upstream release. Afterward, it records `untagged` for commits between monthly releases. The edition’s `release.json` carries this same value alongside the source commit. Its separate `tag` field identifies the translated edition’s own release. Historical manifests can predate the `upstream_tag` field.

1. Clone the repository in `edition.json` and check out its recorded edition commit on a work branch. If its default branch has moved, generate a new packet against that head before merging. A `/tree/<branch>/<path>` URL identifies the edition's subdirectory in that branch.
2. Read the entire source passage on both sides and the current target. Identify what changed mathematically. A language edition may already contain the correction. Keep that reading if it still agrees with the new source. Record additions, moves, retirements and changes to build inputs separately. Assign a stable identity to a new unit and check dependent imports and cross-references.
3. For each changed passage consult the cited scholarship in the target language. Follow passage IDs to their source, edition and page. The automatically matched terms are suggestions based on changed English lines. For example, the Marathi entry for *set* points to MR-P001 and MR-P007. Read the relevant passages before choosing a rendering. When the packet lacks a resource, locate it in the edition's source release or obtain an appropriate scholarly source and record the exact passage. Keep the original term record and any conflicting evidence.
4. Edit the canonical translated unit. Preserve the proof, quantifier scope, OLP feature switches, symbols, citations, identifiers and labels. Check each conditional branch, including alternatives absent from one printed textbook. Record segment ID, source and target hashes, actual consulted passages, reason, difficult alternatives and editorial confidence in the edition's choice ledger. Record a mathematical correction, a wording change and an already-correct target distinctly. Keep suggested expansions outside the translated text.
5. Update the edition's source files, unit ledger and source pin together. Retain historical authorship and passage evidence. Preserve per-file human credits such as Pedro Lima's in Brazilian Portuguese. Identify each model that translated, corrected or typeset the work and its actual effort. Use the edition's language for its reader-facing metadata.

## Build and check

For an edition with local changes to Open Logic’s style files, consult the [patches and their corresponding upstream settings](olpkit/data/shims/README.md) before updating the source pin.

### English reference for *What If?*

Audrey Yap and Richard Zach’s textbook uses `wi-screen.tex` for the screen edition. Its imports include nine Open Logic files for epistemic logic and six for temporal logic under `content/applied-modal-logic`. The textbook repository supplies the preface, introduction and short chapter on paraconsistent logics. [Textbook sources](https://github.com/rzach/what-if/tree/1ab49ac49b8038f0b007870f7289aae976f5685f)

From the hub root, use a Python 3.11+ environment with the builder installed in editable mode and a Windows TeX installation providing pdfLaTeX, BibTeX and the Open Logic packages. The commands fetch all four pinned source repositories and build the English reader.

```sh
python -m pip install -e "./olpkit[pdf]"
olpkit fetch --product wi-screen-pdf --olp-pin 9cf6715abaf33c45911c2380562fcd3d8e7636ba
olpkit build --english --product wi-screen-pdf --olp-pin 9cf6715abaf33c45911c2380562fcd3d8e7636ba --out out/wi-english
```

Open `out/wi-english/source/courses/what-if/wi-screen.pdf`. At these revisions the reader has 350 pages and imports 172 Open Logic content files. The English reference edition corrects the link in Problem 3.4 to Proposition 3.15. The assembly records the original and corrected file hashes in `source/ASSEMBLY.json`. The source cache retains the exact upstream text. [Editorial correction](olpkit/data/books/what-if/reference-corrections/wi-screen-pdf/exercise-3-4.toml)

### Translated editions

Use the published edition's product profile and fonts. For modular editions install the editable builder from this same checkout. The PDF tools require Poppler (`pdftotext`, `pdfinfo`, `pdftoppm`). Install the edition's TeX distribution with its specified packages and engine. EPUB validation also uses EPUBCheck. The hub generator uses Node.js 22 and the GitHub CLI. The builder manual documents product names, font notices, pinned source inputs and the available commands. [Builder manual](olpkit/README.md)

| SLC edition | TeX engine | Fonts to reproduce its typesetting |
| --- | --- | --- |
| Javanese, Latin script | pdfLaTeX | Baskervaldx, Helvetica via helvet, newtxmath and the native book's Type 1 packages |
| Gujarati | LuaLaTeX | The edition's regular and bold Noto Sans Gujarati, with newtxmath |
| Marathi, Devanagari | XeLaTeX | OLMarathiSerif regular and bold from the edition, with newtxmath |
| Bengali | XeLaTeX | Check the selected product's driver. The registered profile specifies Noto Serif Bengali, Latin Modern and newtxmath. A STIX edition must carry its own font files and notices. |

For other scripts inspect the edition's release source ZIP, actual TeX driver and embedded PDF fonts. In Arabic-script editions check RTL prose, LTR formulas and proof cells, glyph shaping, punctuation and the source square at the end of a proof. A script name alone does not determine the engine, typeface or notation. Carry the exact font files, redistribution notices and version in the source package.

For example, with the Marathi repository checked out beside the hub, the modular commands for fetching and checking its sources are:

```sh
python -m pip install -e "./olpkit[pdf,epub]"
olpkit fetch --repo ../OpenLogic-mr-Deva-IN
olpkit edition validate --repo ../OpenLogic-mr-Deva-IN
```

For a migrated textbook, select the immutable commit carrying the book layer with `--ref` and the immutable commit carrying shared units with `--edition-ref`. Use the same commit for both when both layers are present there. The CLI syntax is `olpkit build --repo EDITION --ref BOOK_COMMIT --edition-ref EDITION_COMMIT --product slc-screen-pdf --out out/slc`. A complete corpus release also needs its own full-reader build. The Marathi source tree provides `tools/prepare_complete.py` and its guarded build script. Consult the release's editable source and build instructions for the exact product. The published native builder currently provides a Windows capped TeX runner. Cross-platform packet planning and verification require no TeX installation.

Compare the new English and translated structure, formulas, citations, references, coverage, Unicode and target-language spelling. Build serially with a bounded process tree. Check the actual PDF: extract the text page by page, inspect glyphs, proof trees, table alignment, scale and links, and compare a second clean build. Count overfull boxes and repair protrusions above about 2 pt through layout. Render and inspect every page that showed an overflow above 10 pt and a spread of pages across the book. Check the final HTML/EPUB numbering and destinations against the PDF, math alternatives and local navigation. Run EPUBCheck on the final EPUB. Preserve the mathematical wording during layout repairs.

## Publish and regenerate the hub

Use the existing edition repository and a new release tag at the verified edition commit. The release includes the cumulative PDF, its directly downloadable complete editable TeX, and a ZIP containing its modular sources, fonts, notices and build instructions. Include the checked HTML and EPUB for each product that offers them. Inspect the archive file list and its reproducibility. Use a reader-facing description in the edition language, including the original human credits, actual AI models and efforts, format and scope. Keep working packets and private choice records out of reader downloads. Preserve previous public tags and files. Publish to GitHub with Zenodo deposition disabled; leave upstream issues, branches and pull requests alone.

For a migrated textbook, complete `olpkit sync accept`, build the native and accessible readers, cold-build both editable PDF entry points, and run `olpkit sync verify`. Package the editable web source with `olpkit package-web-source`. Extract that ZIP and follow its localized README to reproduce the HTML, offline HTML ZIP and EPUB. The exact commands and source inputs are in the [synchronization guide](olpkit/docs/SYNC_PACKETS.md).

For an ordinary HTML and EPUB edition, use the `epub` product for web export and packaging. Pass `--web-product epub` to `olpkit build`, `olpkit check build` and `olpkit sync verify`. These checks bind the EPUB to the native book’s imports and numbering and require a clean EPUBCheck report. For the accessible edition, use `accessible` throughout. Verification defaults to this edition and requires a spoken reading for every formula. Each source ZIP must reproduce its own edition.

To publish a textbook at an already recorded upstream revision, run the following after rebuilding both editable PDF entry points and verifying the web edition. Use the full upstream commit from the edition’s `olp-edition.toml`. This checks the source and translation ledger, the book’s imports, every native build check, the editable sources and the actual web files.

```sh
olpkit check product --repo EDITION --ref EDITION_COMMIT --olp-pin UPSTREAM_COMMIT --build BUILD_DIR --source-export SOURCE_EXPORT_JSON --package-check PACKAGE_CHECK_JSON --web-product epub --out verified.json
```

Use this receipt as the `verified` field of the release job. For an upstream update, use `sync accept` and `sync verify` so the release also records the reviewed changes between the two pins.

Use the [Marathi release job](olpkit/data/releases/slc-mr-job.json) as a schema example. Paths resolve from the job file. Supply the actual edition checkout, native build receipt, product verification, direct TeX, native PDF source ZIP, combined web/PDF source ZIP and cold-built readers. Set the release tag, localized title, description file, scholarly credits, component licences, gate scopes and tool versions for the new edition.

```sh
python maintain.py release --job release-job.json --out release-assets
python maintain.py release --job release-job.json --out release-assets --publish
```

The first command stages the PDF, LaTeX, complete editable source ZIP, offline HTML ZIP, EPUB and machine-readable manifest. The second uses the authenticated GitHub CLI for the selected edition, checks its webhooks, creates or resumes its release, then downloads each published asset anonymously. Keep `PUBLIC-READBACK.json` with the edition's maintenance evidence. Update the edition's catalogue and its digest in `olp-edition.toml`, then push the edition's default branch. Regenerate and test the hub:

```sh
node scripts/generate-catalogue.mjs all
node scripts/generate-catalogue.mjs all --check
npm run check
```

Inspect the generated reader links and commit the corresponding hub files. Verify the public hub and direct downloads after the push.

The Marathi textbook uses 176 imported units. The complete Marathi collection at the same upstream revision covers 722 units. To reproduce the collection, unpack its editable source ZIP, regenerate the cumulative TeX with `python -X utf8 tools/prepare_complete.py`, then follow the Marathi build guide for the guarded PDF build, HTML, EPUB and their checks. The release manifest lists the output hashes, including those of the 79 editable chapter extracts. [Textbook](https://github.com/KokunoYumeto/OpenLogic-mr-Deva-IN/releases/tag/slc-2026-11-15) · [Complete collection](https://github.com/KokunoYumeto/OpenLogic-mr-Deva-IN/releases/tag/complete-2026-11-15) · [Collection build guide](https://github.com/KokunoYumeto/OpenLogic-mr-Deva-IN/blob/complete-2026-11-15/publication/complete-source-mr.md).

Legacy editions with missing pins, resource indexes or product profiles need those inputs before they can complete an unattended release.

## Daily notification

The hub checks upstream master at 05:41 UTC daily. A new commit range produces an issue here with the changed files and the editions' individual source comparisons. Closing the issue retains its marker and prevents a repeat for the same revision. On a workstation with the GitHub CLI, preview the next notice with `python maintain.py watch --out ../olp-advisory`. The scheduled workflow supplies its own hub-scoped token.

Maintenance tooling produced by OpenAI Codex — GPT-6 Astra, Ultra effort. Translation and source authorship belong to the contributors identified in each edition.
