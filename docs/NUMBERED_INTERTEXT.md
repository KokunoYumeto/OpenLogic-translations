# Native equation numbers and derivations with prose between rows

The shared HTML/EPUB converter preserves `align` derivations containing
`intertext` without restarting their equation counters. Each numbered row
uses the equation label from the exact native book auxiliary file already
bound to its PDF and assembled sources by the reference reconciliation.
Rows marked `notag` or `nonumber` remain unnumbered. The target script's
digits are preserved. Ordinary `equation`, `align` and `gather` displays use
the same binding. A literal explicit tag must agree with the native label,
including its supported text style. `tag*` retains its unparenthesized form;
`eqref` preserves parentheses, the target link and any styled label text.

The display receipt records the original environment, intervening prose,
each row, suppression controls, native label and number, and PDF/auxiliary/
assembly identities. MathML receives a number cell for the corresponding
row. The binding rejects missing or extra converted rows. Reference anchors
remain in the formula, and nested math annotations retain their source
positions. Export reports include these bound equation numbers separately.

An unsuppressed row without a native equation label is not assigned a
guessed counter. Unsupported tag expressions, conflicting labels or
suppression controls, grouped numbering controls, and numbered `multline`,
`alignat` or `eqnarray` require additional source/native reconciliation.
An unbound explicit tag cannot silently pass through the converter.
A source-only inventory is not proof of native numbering or
reader completeness. The Intermediate Logic candidate still requires its
actual native PDF/auxiliary build and rendered comparison before release.

Regression checks exercise the four-row derivation pattern with three
unnumbered rows and a final numbered row, multiple nonconsecutive numbers,
target-script digits, nested arrays, mathematical annotations, intervening
prose, reference anchors, literal italic tags, equation references in prose
and in math, and deliberate loss of a rendered row. These
checks execute Pandoc/MathML conversion; they do not run TeX or claim visual
acceptance of a full reader.
