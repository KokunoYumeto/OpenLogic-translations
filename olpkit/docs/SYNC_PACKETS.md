# Edition-specific synchronization packets

`sync edition --repo <repo> --ref <commit> --plan <plan-directory> --out <folder>`
reads the exact edition commit and the cached upstream revisions. It verifies the
full current unit ledger and target bytes before creating a packet for each
changed content unit. The upstream plan must include every actual changed file,
including style files, and its blob identities and SHA-256 values must match.

Each packet preserves the full English before and after, current translated text
and hash, current ledger record, and matched terminology rows with their source
locations. Matching uses literal English terms in added/deleted hunk lines;
headers and unchanged context are excluded. The complete termbase accompanies the
packets, so the filter is a navigation aid rather than a claim of complete canon
coverage. The exact orthography file also accompanies them.

Packet generation makes no edition change, chooses no disposition, runs no TeX
and asserts no canon consultation. Existing corrections remain visible for the
owner to retain, update or resolve explicitly. The owner must consult actual
target-language sources and record the resulting choices. Added, deleted and
renamed upstream paths require explicit migration handling; they are rejected
rather than treated as ordinary replacements by this first modified-file route.

Use `sync accept --help` for the command that checks the candidate's target
bytes, editorial decisions and build against its packet. Use `status` to
compare the edition's committed units and existing product receipts with a
specified upstream revision. Retain the acceptance receipt for verification
alongside the native reader, editable source and release artifacts.

For a change confined to styles, classes or other build inputs, inspect the technical file index in the packet. Keep the source revisions and reviewer fields in the review record and use an empty list for `units`. Acceptance checks the two upstream trees, records the exact changed paths and Git objects, and checks the compiled candidate. Verification still requires the full product checks, editable-source rebuilds and web exports. An identical pair of trees does not constitute a technical update.

## Carry a published textbook forward

Download the editable source ZIP for the previous textbook and verify its SHA-256 against its release manifest. Extract it to `previous-release`. Use the EPUBCheck JAR identified by that edition. From the hub checkout, recover the input files used to make the earlier HTML and EPUB:

```sh
python -m olpkit release-web-template --source previous-release --repo edition --epubcheck-jar epubcheck.jar --out previous-web
python -m olpkit rebind-credits --source build/source --previous-release previous-release --repo edition
```

The second command prints the path of the new credit policy. It checks changed notices against their previous Git versions and the assembled source. If a name, licence or other wording changed, review the actual change and update its evidence. Run the native build checks with the resulting policy.

For the new web profile, create `web-inputs.json`. Its `acceptance`, `edition` and `credits_policy` fields each contain the relative `path` and hexadecimal `sha256` of the sync acceptance receipt, the new edition's `olp-edition.toml` and the new credit policy. Set `book_inputs` to an array. For each changed textbook input in the projection, record its `path`, `old` and `new` SHA-256s and the editorial `reason`. Use an empty array when none changed. The builder verifies translated units against the sync decision and checks changed upstream styles against the localized bytes at both Git revisions.

```sh
python -m olpkit web-profile --build build/BUILD.json --template previous-web/web-profile.json --sync-inputs web-inputs.json --out current-web
python -m olpkit export --source build/source --product html --profile current-web/web-profile.json --out ordinary-html --check-numbers
```

Continue below to update the spoken mathematics and export the accessible formats.

## Verify a rebuilt textbook

Run the following from the builder checkout after generating both source
exports and cold-building each. Set `EDITION_COMMIT` to the commit used for
the final textbook. Use the same upstream cache as for `sync accept`.

```sh
python -m olpkit sync verify --repo edition --ref "$EDITION_COMMIT" \
  --packet packets/edition --review review.json --acceptance acceptance.json \
  --build build-final --source-export source-package/EXPORT.json \
  --package-check source-rebuild/PACKAGE-CHECK.json --out verified/textbook.json
```

If the final layout was built at a later commit, pass
`--accepted-build build-at-acceptance` as well. That directory contains the
original assembly and per-unit results for the reviewed source changes.
The verifier checks the full edition ledger, then matches each textbook unit
to the translated bytes used in the PDF, HTML and EPUB. It also checks the
direct TeX, every source ZIP member and both cold builds. The output names the
specific product checked and lists the changed units imported by each product.
Verify other affected products against their own builds before release.

## Update spoken mathematics after editing a textbook

For the Marathi textbook, download the [speech inputs for the edition you are updating](https://github.com/KokunoYumeto/OpenLogic-mr-Deva-IN/tree/main/publication/speech-inputs). Its archive includes the ordinary HTML, occurrence packet, reviewed Marathi readings and source map used by the commands below.

Build the revised textbook and generate its numbered HTML. Use the ordinary
HTML files immediately before speech binding for both versions. Keep the old
occurrence packet, speech store and source map together. The previous EPUB or
already-labelled HTML cannot substitute for the ordinary HTML.

```sh
python -m olpkit speech-sync --previous-reader old/reader.html --previous-packet old/speech-input.json --previous-store old/speech-store.json --reader new/reader.html --out update
```

`update/speech-delta.json` lists reusable occurrences and those needing an
editorial decision. For each changed occurrence, read the complete source
paragraph, revised target and relevant passages in the target-language canon.
In a review JSON, set `delta_sha256` to the SHA-256 of the delta file and
record `model`, `reasoning_effort`, `model_observed_at` and localized
`attribution`. Key `decisions` by current occurrence ID. Each entry needs its
`formula_sha256`, `source_locator`, `canon_passages` and `rationale`. To reuse
a reading of the identical formula, specify its old `from_occurrence`. For a
new reading supply `spoken_text` and `rule_ids`. New rules belong in
`additional_rules` and use the same canon and rationale fields as the old store.

Run the same command with `--review review.json --previous-source-map old/occurrence-sources.json`.
Keep the prior occurrence map and review with the new one. Add the new
`speech-input.json` and `speech-store.json` to the web profile as the
`formula_speech_input` and `formula_speech` witnesses with their exact SHA-256s.
Export the accessible product using that profile, then bundle its HTML with
the same images and fonts used in the checked EPUB.

```sh
python -m olpkit export --source build/source --product accessible --profile accessible-profile.json --out accessible --check-numbers --check-speech
python -m olpkit package-html --export accessible/EXPORT.json --out reader-html.zip
```

## Distribute the editable source for the web formats

Use the accepted accessible export, its web profile, the PDF source export,
and the PDF export profile that selected the public TeX files. Provide the
builder's licence and instructions in the edition's language. The command
includes the editable native book, the web builder, fonts and diagrams, and
the localized formula readings in a single source ZIP.

```sh
python -m olpkit package-web-source --build build-final \
  --profile accessible-profile.json --source-export source-package/EXPORT.json \
  --web-export accessible/EXPORT.json --pdf-profile pdf-export-profile.json \
  --builder-licence olpkit/LICENSE --instructions web-build.md --out textbook-source.zip
```

Extract the ZIP into a new directory and follow its README. The included
`rebuild_web.py` regenerates the HTML, offline HTML ZIP and EPUB from that
directory. It checks the output hashes and runs EPUBCheck before installing
the three readers and their assets in the chosen output directory. When the
text changes, use the editorial speech workflow above to prepare new readings.
