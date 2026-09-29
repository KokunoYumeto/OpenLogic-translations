# Set-theory source review: seven supported findings and one retracted claim

This is a translation-manager review, not an upstream approval or a new issue submission. Eight Pashto reports were checked against their complete English source context, the actual notation macros, and earlier Tamil reports. All five current upstream files match the frozen source byte for byte. Six of the seven supported findings already had Tamil aliases; do not count those twice.

[Machine-readable findings](SET_THEORY_SOURCE_REVIEW_20260930.json) · [Three local fixes](SET_THEORY_SOURCE_REVIEW_20260930.patch)

## Dispositions

| Pashto report | Earlier Tamil record | Result |
|---|---|---|
| OLSTH-019 | TA-STH-035 | Exclude exponent zero from the finite-power law. |
| OLSTH-020 | TA-STH-037 | The recursion defines two sequences, not the parameter cardinal. |
| OLSTH-021 | — | State the infinite-cardinal induction domain and its base case. |
| OLSTH-022 | TA-STH-038 | The fixed-point iteration can be stationary, so the claimed injection fails. |
| OLSTH-023 | TA-STH-039 | The carrier is a subset of A, not of its relation R. |
| OLSTH-024 | TA-STH-041 | **Retract: the actual macro expands to a valid relation chain.** |
| OLSTH-025 | TA-STH-043; related TA-STH-044 | Correct the stop direction and distinguish the pre-stop restriction. |
| OLSTH-026 | TA-STH-042 | Handle the empty carrier before calling its choice function. |

These are seven supported findings, not seven newly discovered errors. Duplicate checking covered the central source collections and the relevant twelve earlier Tamil records; it does not establish uniqueness across every issue or pull request.

## OLSTH-019

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/card-arithmetic/expotough.tex#L77) · content/set-theory/card-arithmetic/expotough.tex

The definition counts functions from the exponent carrier to the base. The empty domain has exactly one function into any base, so an infinite cardinal to exponent zero is 1, not the base.

**Treatment:** Require a positive finite exponent. Included in the three-hunk patch.

## OLSTH-020

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/card-arithmetic/ch.tex#L35) · content/set-theory/card-arithmetic/ch.tex

The parameter a is not recursively defined here. The immediately preceding display recursively defines the aleph and beth sequences.

**Treatment:** Name the two sequences. Included in the three-hunk patch.

## OLSTH-021

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/card-arithmetic/ch.tex#L70) · content/set-theory/card-arithmetic/ch.tex

At a=omega the printed induction hypothesis refers to aleph indices for finite b; these do not exist. The union substitution uses these undefined indices. The infinite-cardinal theorem itself is true.

**Treatment:** State the omega base case and restrict induction and the limit union to infinite cardinals below a. At a limit cardinal above omega those are cofinal. Establish uniqueness from strict monotonicity. Not silently included in the mechanical patch.

## OLSTH-022

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/card-arithmetic/fix.tex#L152) · content/set-theory/card-arithmetic/fix.tex

For a beth fixed point kappa=card(A), substitution gives tau_n(A)=kappa for every n, so strict growth fails. After W1 reaches a fixed point, W2=W1. Thus the displayed recursion is not injective.

**Treatment:** A proof repair must start the beth iteration strictly above card(A). The earlier Tamil proposal uses beth at the ordinal successor of card(A). Also state how W0=0, which is not a beth fixed point, is excluded from the codomain claim or change that seed. These proof changes are not covered by the three-hunk patch.

## OLSTH-023

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/choice/hartogs.tex#L33) · content/set-theory/choice/hartogs.tex

Membership in C supplies a well-order on a carrier B contained in A, not a carrier contained in its order relation R.

**Treatment:** Replace B subseteq R with B subseteq A. Included in the three-hunk patch.

## OLSTH-024 — withdrawn claim

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/choice/hartogs.tex#L80) · content/set-theory/choice/hartogs.tex

In both pinned source revisions, cardeq expands to #1 approx #2 with no parentheses. Nesting therefore produces the ordinary chain A disjointsum B approx A times B approx M. TeX arguments are not typed mathematical-function arguments.

**Treatment:** Withdraw the malformed-formula allegation. Preserve the source formula. An equivalent two-claim Tamil presentation can remain as editorial clarification, not as a source-error correction. Existing Pashto warning needs removal/correction; owner application not yet verified.

## OLSTH-025

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/choice/wellorderingproblem.tex#L61) · content/set-theory/choice/wellorderingproblem.tex

The printed delta<=alpha stop rule overwrites all selected values up to the first exhaustion stage. With two selected elements it makes both earlier values equal to A. Merely reversing the inequality still leaves the full sentinel-extended function noninjective.

**Treatment:** Apply the sentinel only at/after first exhaustion, and restrict the injectivity/range/bijection conclusions to the initial segment before exhaustion. Not a one-symbol fully repaired proof; omitted from the three-hunk patch.

## OLSTH-026

[Exact source location](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/set-theory/choice/wellorderingproblem.tex#L52) · content/set-theory/choice/wellorderingproblem.tex

For empty A, the choice function on nonempty subsets has empty domain, so the displayed f(A) is undefined.

**Treatment:** Dispose of the empty-set case before introducing g(0)=f(A). This belongs with the stopping/scope proof repair, not the three-hunk patch.

## Why the retraction matters

The notation definition is identical in the [frozen source](https://github.com/OpenLogicProject/OpenLogic/blob/9620cc73f9c8e0ad003c514a5d3748f29611c4c0/open-logic-config.sty#L956) and the [current source](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/open-logic-config.sty#L956):

```tex
\DeclareDocumentCommand \cardeq { m m } {#1 \approx #2}
```

Expanding the nested command gives:

```tex
A \disjointsum B \approx A \times B \approx M
```

This is ordinary chained equinumerosity. A parser-level observation about nested macro arguments cannot establish a mathematical type error. The Pashto and Tamil owners have received a bounded correction; their completed repairs are not claimed here. Historical reports remain evidence of what was previously asserted, with this disposition superseding their error classification.

## What the patch does—and does not do

The linked patch changes only three local passages: the positive-exponent hypothesis, the sequence-definition referent, and the Hartogs carrier. It passed a non-mutating application check against the exact current file bytes. No upstream source was changed.

The induction, fixed-point and stop-rule findings need the proof-context changes described above. They are deliberately not represented as fixed by this small patch. For the stopping proof, reversing one inequality alone is insufficient: a constant sentinel extension is still noninjective; the bijection is its pre-stop restriction.

The finite examples checked the empty-domain-function convention and stopping behaviour on carriers of up to five elements. They are diagnostic illustrations, not computational proofs about infinite cardinals. The fixed-point counterexample follows directly by substituting a fixed point into every displayed iteration step.

## Provenance and limits

The frozen source is revision9620cc73f9c8e0ad003c514a5d3748f29611c4c0; current source checked at revision1e960beff9ed7835bf3e3f1335e21af3439cd107. Exact source hashes, locators, aliases, macro identities and bounded-check scope are in the linked JSON. The source and mathematical authority remain the Open Logic Project and its cited originals. No full-edition linguistic certification or human review is claimed.

Review and report: OpenAI Codex — GPT-6 Astra, Ultra effort. This report is retained in the existing translation hub. No additional upstream issue or comment was submitted.
