# Modal-tableau source corrections

Three correction groups remain in current Open Logic source. They were reported independently in the Tamil and Pashto translation records; those six reports describe **three defects, not six**. This page supplies precise source links and one minimal, applicable patch. It does not claim that any theorem needs replacement or that these suggestions have been accepted upstream.

AI source comparison and mathematical audit: **OpenAI Codex — GPT-6 Astra, Ultra effort**. No independent human review is claimed.

[Download the complete two-file patch](MODAL_TABLEAUX_SOURCE_CORRECTIONS_20260928.patch) · [Machine-readable evidence](MODAL_TABLEAUX_SOURCE_CORRECTIONS_20260928.json)

## 1. False-diamond rule: wrong conclusion in the proof description

ID: **OLI-NML-4R-DIAMOND-CONCLUSION**. Aliases: Tamil TA-NML-046; Pashto OLNML-038.

[more-soundness.tex, line 204](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/more-soundness.tex#L204) describes the conclusion as `\sFmla{\True}{\Box!B}[\sigma]`. Replace it with `\sFmla{\False}{\Diamond!B}[\sigma]`.

The rule is transferring falsity of ◇B from the successor prefix back to its predecessor. Both the rule table and the final sentence already say this. Let x = f(σ) and y = f(σ.n). Since xRy and R is Euclidean, every z with xRz also has yRz. If ◇B is false at y, B is false at every such z; therefore ◇B is false at x. This proves the corrected conclusion for every Euclidean model.

The printed T□B conclusion is genuinely wrong, not just an alternative notation: take one reflexive world where B is false. F◇B holds, but T□B fails.

## 2. Interpret the whole successor prefix

ID: **OLI-NML-4R-PREFIX-INTERPRETATION**. Aliases: Tamil TA-NML-045; Pashto OLNML-039.

At [more-soundness.tex, line 198](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/more-soundness.tex#L198) and [line 210](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/more-soundness.tex#L210), replace both `[f(\sigma).n]` occurrences with `[f(\sigma.n)]`.

The [definition at soundness.tex:46–51](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/soundness.tex#L46) makes f a function from prefixes to worlds. Dot-n extends the prefix σ before applying f. It is not an operation defined on the resulting world f(σ). The surrounding premises already use f(σ.n).

## 3. Keep the valid tableau; correct its name

ID: **OLI-NML-S5-EXAMPLE-AXIOM-LABEL**. Aliases: Tamil TA-NML-044; Pashto OLNML-040.

The [example at more-rules.tex:161–162](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/more-rules.tex#L161) calls □A → □◇A “axiom 5.” But [schemas.tex:126–127](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/syntax-and-semantics/schemas.tex#L126) defines axiom 5 as **◇A → □◇A**.

The existing tableau really starts from the negation of □A → □◇A and closes correctly. Preserve that formula and the entire proof tree. Replace only its introductory claim with:

```tex
  We give a closed tableau that shows
  $\Log{S5} \Proves \Box!A \lif \Box\Diamond!A$.
```

Changing just the displayed formula to axiom 5 would leave it inconsistent with the unchanged tableau.

## Verification, provenance and reporting

Checked on 28 September 2026 against upstream commit `1e960beff9ed7835bf3e3f1335e21af3439cd107`. Both affected files are byte-identical to their frozen translation witnesses. The patch passes `git apply --check` against those exact current files. No upstream files were changed.

A bounded exhaustive regression checked 48 Euclidean frames on one through three worlds, 344 valuations and 2,260 rule instances. All corrected rule instances passed. The general argument above—not the finite test—is the universal justification.

Tamil records TA-NML-044/045/046 in two preserved intake snapshots corroborate the exact aliases. The earlier consolidated [upstream issue #436](https://github.com/OpenLogicProject/OpenLogic/issues/436), reports #432/#433/#435, their relevant comments, the Indonesian list linked from #432, and targeted issue/PR filename searches did not identify a matching submitted correction. That bounded search is **not** a claim of exhaustive global deduplication.

These three groups have **not** been sent in another issue or comment. They remain collected here for a later consolidated upstream batch, with a fresh duplicate check before sending. This audit does not certify a complete target-language edition or require a reader rebuild.

