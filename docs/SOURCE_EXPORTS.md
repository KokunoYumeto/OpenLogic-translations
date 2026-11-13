# Source exports

`export --product cumulative-tex` reads an immutable assembled tree and the import
lock for its four exact source pins. It embeds all imported translated units and
the book's screen text, metadata and preambles without TeX expansion. Imports
dispatch to embedded subfiles. A conditional import outside the lock remains an
explicit runtime error if that branch becomes active; it is never silently deleted.
Book selection is data in `data/exports`, not language-specific code.

The method follows `textbooks/slc/assemble.py` and `pack.py` from
`KokunoYumeto/OpenLogic-jv-Latn-ID` at
`a56163e19864f50f2da5197b56ba4c561b5e9b15`, which adapted the Bengali pilot's
unexpanded module embedding. The shared implementation also embeds book preambles
and glossary adapters and preserves comments during import retargeting.

`export --product source-zip` additionally requires a successful recorded build,
matching PDF and recorder hashes, a component-notice policy, and localized build
instructions. Its command-line inputs are `--build`, `--credits` and
`--instructions`. It packages recorded assembled inputs, their exact required
notices, the BibTeX inputs named in the auxiliary file, and the cumulative source.
Generated build intermediates and private assembly/QA records are excluded. ZIP
membership and checksums are deterministic. A failed or unbound build is rejected.

Both products are written to a fresh private output directory with `EXPORT.json`.
That report is not part of a publication. Export success does not mean release
acceptance: clean extracted-tree and cumulative builds must reproduce the modular
reader's pages and text; credit, visual and other applicable gates remain mandatory.
The source ZIP's localized instructions must describe those exact build inputs.

HTML, EPUB and accessible exports still depend on the T13 converter choice. This
source-only implementation does not introduce a competing HTML converter.
