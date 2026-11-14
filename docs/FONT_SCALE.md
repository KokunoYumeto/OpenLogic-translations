# Visible font-scale measurement

`olpkit check scale --pdf specimen.pdf --specimen specimen.json
--language-data data/languages/<locale>.toml --out <fresh-folder>` measures
the visible ink height of Latin lowercase `x` relative to a script reference
glyph in a specimen line. It writes the exact PDF hash, both cropped PNGs,
pixel heights, measured ratio and a conservative raster uncertainty interval.
Nominal point sizes are reported for diagnosis and do not determine the result.

The specimen manifest follows `schemas/scale-specimen.schema.json`: an exact
PDF hash, one-based page number, locale, and two disjoint cells. Each cell names
its glyph and actual PDF font and supplies a page-coordinate rectangle with
white margins around the glyph. Subset font prefixes are ignored. Ambiguous,
clipped, missing, rotated, transparent, stroked, or wrong glyphs, overlaid
drawings and different baselines do not pass.

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
