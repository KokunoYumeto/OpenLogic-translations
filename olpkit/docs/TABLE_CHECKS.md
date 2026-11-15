# Table source and rendered checks

`olpkit.tableinventory.inventory(text, source, unit)` supplies the source side
of G-TABLE. It records every literal `tabular`, `tabular*`, `array` and
`longtable`, including nested tables, with exact source hashes, character and
line locators, rows, cells, column spans, vertical spans, implicit empty cells,
longtable header/footer boundaries, captions and rules. Proof cells retain
their `DisplayProof` locations and their required left-to-right direction.
Nothing is translated, reordered, removed or rendered by this module.

The inventory is always **incomplete** as a PDF gate. It cannot establish
rendered cell contents, direction, geometry or completeness. Unsupported
syntax stays in the report with its error; it is never dropped to obtain a
passing count. Conditional table openings and conditional row separators must
first be resolved by the existing native-tag projection, with that projection's
input hashes and selection receipt. A source-wide syntax count is not the
number of tables executed by a particular textbook.

The rendered check must bind the source inventory to the actual English and
translated builds, including their native import and tag selections. It must
compare every row and cell, mathematical/prose direction and the type-block
bounds, and retain paired images. The historical Persian cases in the design
remain mandatory: Tables 25.1–25.7 and 28.1 must reveal their actual layout
defects; Table 56.2 must retain its correct mixed prose/math layout. A few
correct axioms inside an otherwise reversed table do not make that table pass.

The tests cover nested proof tables, standard and decorated/repeated columns,
longtable bands, multirow coverage and collisions, explicit/implicit empty
cells, comments/verbatim, conditional projection and unsupported syntax.
