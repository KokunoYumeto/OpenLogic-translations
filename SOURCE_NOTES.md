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

## Evidence limits

This was a bounded source audit, not whole-corpus source certification. It does not independently certify any complete target-language edition. The source archive and all seven named files matched the frozen manifest byte-for-byte; details are in the linked JSON evidence.
