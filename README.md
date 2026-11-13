# Open Logic edition tools

Local source-registry, synchronization, edition-metadata and pinned-source tools. Install from this checkout with `python -m pip install -e .` using Python 3.11 or later. The data and schema files remain in this checkout.

`olpkit units registry --check` verifies the shared path-to-unit map. `olpkit sync plan --from COMMIT --to COMMIT --out DIRECTORY` makes source-change packets. `olpkit sync plan --check DIRECTORY` replays their exact Git identities. `olpkit lint structure --en SOURCE --tr TARGET` compares explicit TeX structure; it does not certify mathematical or linguistic equivalence.

`olpkit edition import-manifest --repo REPOSITORY --adapter jv --out STAGING` converts an existing manifest into `olp-edition.toml` and `units.jsonl`. Other supplied adapters are `gu`, `bn` and `mr`. It checks actual English files against the pinned Git blobs and inherited source hashes, and reads every target file. Existing differing metadata is not overwritten. An owner can omit `--out` to create the two new files in that owner's repository.

`olpkit edition validate --repo REPOSITORY --metadata-dir STAGING` checks staged metadata against the repository. Omit `--metadata-dir` after the owner adds the files to the repository. Unknown keys, duplicate identities, missing units, incorrect pins and changed source/target bytes fail validation.

In this ledger, **current** means that the recorded source blob matches the edition pin. It is not a canon-use, translation-quality, completeness-of-proof or human-review certificate. `by.method = "inherited"` with null model/effort/date records a historical attribution gap; it does not credit the converter with translation work. Preserve established edition-level model attribution and consult the original production records before assigning per-unit models. A model and its effort must be recorded together. No fabricated dates or retrospective claims of earlier canon consultation are permitted.

`olpkit fetch --repo REPOSITORY` reads the edition's full source pins and fills the shared cache. `--metadata-dir STAGING` uses staged contracts. Each export contains exact Git blob bytes, including licences and files marked export-ignore. Checkout line-ending filters do not affect it. A warm fetch verifies the existing export without downloading again. A mismatched export is reported, not silently replaced. `OLPKIT_CACHE` can select another cache directory.

The Python assembly interface `SourceCache.require` is read-only and never fetches implicitly. Build patches in `data/shims` identify the precise before/after text, language/script/engine conditions, reason and pinned pilot evidence. `apply_shims` returns changed copies and records every match; missing or repeated matches fail. It does not rewrite translation units or alter the cache. These inherited patches preserve build behavior; they do not establish rendered quality by themselves.

Full assembly, TeX execution, PDF gates and reader export commands remain under implementation. Existing source files, publication history and substantive corrections must remain intact.

Builder code produced by OpenAI Codex — GPT-6 Astra, Ultra effort. This is a code attribution, not attribution of the inherited translations or original Open Logic Project texts.
