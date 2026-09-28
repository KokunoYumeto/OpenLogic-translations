# Shared English source notes

These corrections are shared across Open Logic translations. They are not silent changes to the upstream source: each finding is bound to frozen revision `9620cc73f9c8e0ad003c514a5d3748f29611c4c0`, the raw source manifest, exact file hashes and line locators. Translation editions should cite the stable finding ID, retain the untouched English bytes in provenance, and distinguish source correction from translation choice.

The machine-readable audit is [SHARED_FUNCTIONS_SOURCE_AUDIT_20260904.json](evidence/SHARED_FUNCTIONS_SOURCE_AUDIT_20260904.json).

## Functions audit — 4 September 2026

### OLFUN-001 — left inverse requires an empty-domain qualification

`content/sets-functions-relations/functions/inverses.tex`, lines 62–84, claims that every injection `f: A -> B` has a left inverse. This is false when `A` is empty and `B` is nonempty: the empty map `emptyset -> {0}` is injective, but no map `{0} -> emptyset` exists. The proof itself chooses an element of `A`.

Use the simple corrected theorem “if `A` is nonempty and `f` is injective, then `f` has a left inverse.” The exact condition is that an injective `f: A -> B` has a left inverse iff `A` is nonempty or `B` is empty. State the correction in an adjacent editorial note.

### OLFUN-002 — principal square root is nonnegative

`function-basics.tex`, lines 64–71, calls the selected square root “positive” while defining it on all natural numbers. Open Logic defines the naturals to include zero; the principal square root of zero is zero. Translate this as the “nonnegative (principal) square root.” The preceding statement that each positive integer has two real square roots is correct.

### OLFUN-003 — n/x input typo

`function-basics.tex`, lines 103–107, introduces a natural number `n` and immediately describes the successors of `x`. Use one input variable consistently without changing the alpha-equivalent formula, and record the source typo.

### OLFUN-004 — graph is a relation between A and B

`functions-relations.tex`, lines 24–30 and 61–64, correctly defines the graph as a subset of `A x B` but then calls it a relation “on `A x B`.” Under the project's own definition, a binary relation on `U` is a subset of `U^2`. Use “a relation between `A` and `B`” or “a relation contained in `A x B`.”

### OLFUN-005 — two different restriction operations

The explicit function restriction in `functions-relations.tex`, lines 78–90, is correct: it keeps graph pairs whose input lies in `C`, equivalently `R_f intersect (C x B)`. The earlier relation restriction in `relations/operations.tex`, lines 20–32, is `R intersect C^2` and restricts both coordinates. The later claim that these are exact counterparts is therefore too strong.

For `A={0}`, `B={1}`, `f(0)=1`, and `C={0}`, the function-restriction graph is `{(0,1)}`, whereas `R_f intersect C^2` is empty. Preserve the correct function definition and qualify the analogy in prose or an adjacent note.

## Modal tableaux — 28 September 2026

The [three modal-tableau correction groups](evidence/MODAL_TABLEAUX_SOURCE_CORRECTIONS_20260928.md) merge the matching Tamil and Pashto reports. They repair a wrong signed modal conclusion, two misplaced prefix parentheses and a worked example incorrectly called axiom 5. The report includes permanent source links, a semantic justification and an apply-checked patch against current upstream. These groups have not been sent in a new upstream issue or comment. Audit: OpenAI Codex — GPT-6 Astra, Ultra effort; no independent human review is claimed.

## K-tableau completeness and countermodels — 28 September 2026

The [consolidated completeness/countermodel report](evidence/MODAL_COMPLETENESS_SOURCE_CORRECTIONS_20260928.md) records twelve correction groups already shared by the Tamil and Pashto editions: missing formula operands and prefixes, wrong truth signs and induction variables, a reversed tableau root, and a mislocated witness. One additional successor-prefix clarification is kept separate, not counted as a definite error. Permanent source links, exact replacements, a two-file patch and a reproducible finite semantic checker are included. No new upstream issue/comment was sent. Audit: OpenAI Codex — GPT-6 Astra, Ultra effort; no independent human review is claimed.

## Scope of the earlier Functions audit

This was a bounded source audit, not whole-corpus source certification. It does not independently certify any complete target-language edition. The source archive and all seven named files matched the frozen manifest byte-for-byte; details are in the linked JSON evidence.
