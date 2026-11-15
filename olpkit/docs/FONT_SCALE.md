# Visible font-scale measurement

`olpkit check scale --pdf specimen.pdf --specimen specimen.json
--language-data data/languages/<locale>.toml --out <fresh-folder>` measures
the visible ink height of Latin lowercase `x` relative to a script reference
glyph in a specimen line. It writes the exact PDF hash, both cropped PNGs,
pixel heights, measured ratio and a conservative raster uncertainty interval.
Nominal point sizes are reported for diagnosis and do not determine the result.
Rendering uses 2400 dpi so small letter bodies have enough pixels for a useful
two-edge uncertainty bound.

The specimen manifest follows `schemas/scale-specimen.schema.json`: an exact
PDF hash, one-based page number, locale, and two disjoint cells. Each cell names
its glyph and actual PDF font and supplies a page-coordinate rectangle with
white margins around the glyph. Subset font prefixes are ignored. Ambiguous,
clipped, missing, rotated, transparent, stroked, or wrong glyphs, overlaid
drawings and different baselines do not pass.

For a joined script, a cell may identify a central glyph in a repeated run
through `context.text`, `context.index` and the actual PDF `context.glyph_id`.
The run must consist of the reference character, and the chosen glyph and both
neighbours must use the same glyph ID. The cell spans exactly that glyph's
horizontal advance and retains vertical white margins. This measures a medial
form without including a different initial/final form or pretending a connected
edge is clipping. The supplied Persian evidence uses the medial م in ممممم;
an isolated م would measure a different shape. Foreign text, drawings and images
in either cell remain failures.
Contextual measurement also resolves the actual embedded TrueType or CFF glyph
outline. It uses visible outline bounds to exclude neighbouring lines whose
nominal font boxes overlap, and requires raster height to agree with the
embedded outline. CID-keyed CFF identifiers are resolved as CIDs rather than
incorrectly used as subset-array indexes. Unresolved contextual outlines fail.

Keep nominal point-size ratios separate from ink ratios. In the supplied
Persian specimens, `12pt` with Persian `Scale=1.26` gives a nominal Latin/Persian
ratio near 0.79; that does not mean the Latin x-height is 0.79 of medial م.

The language data's optional `[scale]` table follows
`schemas/font-scale.schema.json`. It records the reference glyph, lower/upper
ratio bounds, decision date, rationale and actual evidence. The checker never
invents a language's range or human approval. A missing range or a raster
interval crossing a boundary is incomplete, not a pass.

This implements the specimen measurement portion of DESIGN 3.5. The four pilot
language decisions, actual guarded TeX specimens tied to each book's fonts and
integration into the release build record remain to be completed. Synthetic
test fixtures establish measurement behavior only. A specimen measurement
does not certify a reader, typography at every size, or source equivalence.
