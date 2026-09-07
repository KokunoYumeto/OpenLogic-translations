# Expert-review index: native mathematical notation

Edition: English accessible source-faithful transformation.
Final printed/PDF pages are pending final pagination; exact source and rendered locations are in `DECISION_OCCURRENCES.csv`.

## OLAB-EN-A11Y-NOTATION-001 — HIGH

Source: `\DeclareDocumentCommand \Lang { m }{\applytofirst{\mathcal}{#1}}` at `open-logic-config.sty:1101`.

Chosen rendering: Apply script styling to the first language-name token only; leave primes and subscripts outside that style scope.

Why: The frozen macro explicitly applies mathcal only to the first token. Styling the entire subscripted or primed expression changes the source typographic scope and can alter braille/screen-reader navigation semantics.

Alternatives: Script the full language expression; Use a precomposed script-L glyph where structurally equivalent.

Review value: A mathematical accessibility reviewer can confirm that the chosen structural MathML best communicates the source convention across speech and braille systems.

Question: Please double-check: should primes and subscripts remain outside the script-styled base in every repaired language-name expression?

Confidence: HIGH; provisional and openly revisable. Final page: PENDING_FINAL_PAGINATION.

## OLAB-EN-A11Y-NOTATION-002 — MEDIUM

Source: `\DeclareDocumentCommand \Setabs { m m }{\{ #1 : #2 \}}` at `open-logic-config.sty:911`.

Chosen rendering: Use a colon between the bound expression and condition in every source \Setabs rendering.

Why: The frozen edition explicitly selects a colon. A vertical bar is mathematically equivalent but is not faithful to this source configuration and may be confused with divisibility or cardinality in linearized navigation.

Alternatives: Vertical bar separator.

Review value: An accessibility reviewer can assess whether the colon offers the intended disambiguation in braille and navigable MathML.

Question: Please double-check: is the source-selected colon preferable to a vertical bar for these set-builder expressions in braille and screen-reader navigation?

Confidence: HIGH; provisional and openly revisable. Final page: PENDING_FINAL_PAGINATION.

## OLAB-EN-A11Y-NOTATION-003 — HIGH

Source: `\Sat{M}{!A}[s] renders as structure M, assignment s, satisfaction relation, formula A` at `open-logic-config.sty:343-360`.

Chosen rendering: Place the optional assignment beside the structure, before the satisfaction relation; never as a subscript on the relation or trailing after the formula.

Why: The frozen macro and its own documentation specify M, s models A. The repair preserves the existing assignment and formula nodes but restores their source-defined structural ownership.

Alternatives: Assignment as a subscript on the satisfaction sign; Assignment in trailing brackets.

Review value: A logic and braille specialist can confirm that the comma-separated structure-assignment pair gives the clearest navigable relation.

Question: Please double-check: does placing the assignment immediately after the structure and before the satisfaction relation preserve the intended scope in all repaired cases?

Confidence: HIGH; provisional and openly revisable. Final page: PENDING_FINAL_PAGINATION.
