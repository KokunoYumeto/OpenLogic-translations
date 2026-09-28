# Intuitionistic tableaux: source corrections and a scope gap

This bounded review confirms eleven Pashto-owner reports and identifies one additional two-occurrence rule-label inconsistency. It is not a proof that all OpenLogic content or all Pashto translation choices are correct. No new upstream issue or comment was posted. Existing report #436 is not amended by this catalogue.

Audit and new catalogue text: OpenAI Codex — GPT-6 Astra, Ultra effort. The inspected B155 translation and owner notes disclose OpenAI Codex — GPT-6 Sol, Ultra effort. No independent human review is claimed.

## Source identities

Frozen revision: `9620cc73f9c8e0ad003c514a5d3748f29611c4c0`. Current upstream inspected: `1e960beff9ed7835bf3e3f1335e21af3439cd107`. The four affected current files match their frozen bytes. See [machine-readable evidence](INTUITIONISTIC_TABLEAUX_SOURCE_FINDINGS_20260929.json) for exact file hashes, replacements and public locators.

## Mechanical corrections

| Owner identifier | Location | Correction |
|---|---|---|
| OLINT-012 | [introduction.tex:40](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/introduction.tex#L40) | Replace the stray modal-tableau description with intuitionistic. |
| OLINT-013 | [rules.tex:92](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/rules.tex#L92) | For true implication, the branches are false antecedent or true consequent; fix all four prose occurrences to agree with the table. |
| OLINT-014 | [proofs.tex:32](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/proofs.tex#L32) | Both false-conjunction references point to line 7, not line 4. |
| OLINT-015 | [soundness.tex:22](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L22) | A countermodel makes the conclusion not satisfied. |
| OLINT-016 | [soundness.tex:31](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L31) | The discussion is the intuitionistic case. |
| OLINT-018 | [soundness.tex:78](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L78) | Repair the broken sentence, interpret the second accessibility endpoint, and conclude truth at the extended world. |
| OLINT-019 | [soundness.tex:141](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L141) | Restore the omitted prefix on the false-disjunction premise. |
| OLINT-020 | [soundness.tex:151](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L151) | Both extended sets must list the true antecedent and false consequent at the fresh prefix. |
| OLINT-021 | [soundness.tex:166](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L166) | The next cases have two branches, not two premises. |
| OLINT-022 | [soundness.tex:205](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/soundness.tex#L205) | The contradiction concludes semantic entailment, not the derivability assumed at the outset. |
| Manager addition | [rules.tex:90](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/intuitionistic-logic/tableaux/rules.tex#L90) | Two rule-name macros reverse Sign and Op; use the order documented in open-logic-config.sty lines 293–298 and already used in the formal tables. |

The [four-file mechanical patch](intuitionistic-tableaux-mechanical-fixes-20260929.patch) passes an applicability check against those exact current files. It deliberately does **not** repair the scope gap below. Eleven dollar-math substitutions in the existing translation match their disclosures; two proof-tree references are separately checked. The manager parser covers 259 dollar-delimited spans, not all possible TeX mathematics.

## OLINT-017: missing intermediate prefixes

The source definition permits arbitrary prefix sets and constrains only immediate extensions whose endpoints both belong to that set. Let P = {1, 1.1.1}; use two worlds a and b with identity accessibility, make p true only at a, and map 1 to a and 1.1.1 to b. This is a nonempty reflexive, antisymmetric, transitive frame with persistent valuation. There is no immediate-extension pair in P, so the stated interpretation condition holds vacuously. Both T p at 1 and F p at 1.1.1 are satisfied, although the stated syntactic closure criterion closes the branch. Consequently the unrestricted closed-set proposition needs an additional domain/interpretation condition.

This does not refute the ordinary common-root entailment corollary: branches generated from the common initial prefix by the stated rules retain the intermediate prefixes. An unrestricted fresh-prefix extension argument also needs care if a previously present prefix extends the supposedly fresh one. No complete repaired general theorem is claimed here, and simply changing the definition without checking extension of interpretations is not offered as a finished repair.

The counterexample was recomputed from its worlds, relation, valuation and map, not accepted from stored PASS flags. Its scope warning is explicitly retained in the Pashto draft.

## Provenance limits

The scholarly canon images support native prose/word order and regional entailment/relation usage, not direct Pakistani attestation of every intuitionistic-tableau expression. Such terms remain provisional. This report records confirmed source findings, not human linguistic certification. Before any later authorized upstream batch, recheck current source and all relevant public issues/PRs; external duplicate checking is not complete.

[Pashto edition audit](PASHTO515_REVIEW.ps.html) · [Programme source notes](../SOURCE_NOTES.md)
