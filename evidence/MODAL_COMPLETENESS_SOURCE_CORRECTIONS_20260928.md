# K-tableau completeness and countermodels: consolidated source corrections

Twelve correction groups in two English source files are confirmed against the current upstream revision checked on 28 September 2026. These merge **nine Pashto reports with twelve existing Tamil findings**; they are not twelve new discoveries. A tenth Pashto report is a useful clarification, treated separately below.

- [Apply-ready two-file patch](MODAL_COMPLETENESS_SOURCE_CORRECTIONS_20260928.patch).
- [Machine-readable exact substitutions, evidence and aliases](MODAL_COMPLETENESS_SOURCE_CORRECTIONS_20260928.json).
- [Reproducible bounded checker](MODAL_COMPLETENESS_CHECK_20260928.mjs). Run it with Node.js. This public checker performs the finite semantic tests only; source/target byte checks are separately documented in the JSON.

This is a source-error report, not a new translation or an upstream-approved errata list. No new upstream issue or comment was sent. Audit and report: **OpenAI Codex — GPT-6 Astra, Ultra effort**. No independent human review is claimed.

## Exact changes

Links below pin the original lines, not a moving branch. The downloadable patch contains the complete copy-pasteable replacements.

| Existing finding aliases | Exact source | Correction |
| --- | --- | --- |
| TA-NML-047 / OLNML-042 | [completeness.tex:50](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L50) | Restore `[\sigma]` on the true-conjunction premise; both conclusions already use that prefix. |
| TA-NML-048 / OLNML-042 | [completeness.tex:52](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L52) | From T(B ∨ C), the left alternative is **T B**, not F B. |
| TA-NML-049 / OLNML-043 | [completeness.tex:54](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L54) | Supply B in four modal premises; the four successor conclusions contain **B**, not a bare modal operator. |
| TA-NML-050 / OLNML-044 | [completeness.tex:80](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L80) | Change “every branch is closed” to “every branch is complete”, restoring the proposition's stated conclusion. |
| TA-NML-051 / OLNML-045 | [completeness.tex:146](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L146) | False-conjunction induction: change the second semantic B to **C**. |
| TA-NML-052 / OLNML-045 | [completeness.tex:162](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L162) | False-disjunction induction: change the second semantic B to **C**. |
| TA-NML-053 / OLNML-045 | [completeness.tex:178](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L178) | False-conditional induction: retain true B, change the false B to **false C**. |
| TA-NML-054 / OLNML-046 | [countermodels.tex:16](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/countermodels.tex#L16) | Restore `!A` after `\Entails/`; this is a dropped formula-token marker. |
| TA-NML-058 / OLNML-047 | [countermodels.tex:76](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/countermodels.tex#L76) | In both examples (lines 76 and 206), use “complete tableau” instead of “closed tableau” for the systematic construction. |
| TA-NML-055 / OLNML-048 | [countermodels.tex:205](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/countermodels.tex#L205) | The described line 3 is **F◇(p ∧ q)**; use the **F◇ rule**, matching the displayed successors. |
| TA-NML-056 / OLNML-049 | [countermodels.tex:209](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/countermodels.tex#L209) | Restore the middle tree's root to **F((◇p ∧ ◇q) → ◇(p ∧ q))**, matching the first/final trees. |
| TA-NML-057 / OLNML-050 | [countermodels.tex:285](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/countermodels.tex#L285) | The explanation of V(q) must cite **T q at 1.2**, not at 1.1. |

## Why these changes are warranted

The chapter's own [propositional rules](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/rules-for-K.tex#L13) preserve the world prefix and give the true-disjunction alternatives T B and T C. Its [modal rules](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/rules-for-K.tex#L117) explicitly remove the outer modality and restrict conclusions to permitted successor prefixes. The eight malformed modal expressions therefore need operands in the premises and unmodalized operands in the conclusions.

The three corrected induction steps express the ordinary truth conditions:

- ¬(B ∧ C) iff ¬B or ¬C.
- ¬(B ∨ C) iff ¬B and ¬C.
- ¬(B → C) iff B and ¬C.

A branch consisting only of T p is open and already complete. Exhaustive expansion cannot guarantee that every finite input has a closed tableau; otherwise it would prove every input inconsistent. Replacing “closed” with “complete” restores the proposition's intended conclusion. **Scope caveat:** if an implementation stops expanding closed branches, its invariant should instead be “every open branch is complete.” The minimal patch does not silently rewrite the whole saturation/termination argument or certify it.

For the diamond example, use three worlds 1, 1.1, 1.2, with arrows only from 1 to each successor. Make p true only at 1.1 and q true only at 1.2. At world 1, ◇p and ◇q are both true, but ◇(p ∧ q) is false. This is exactly the final diagram and open branch. Conversely, any single witness to ◇(p ∧ q) is also a witness to each of ◇p and ◇q. Thus the accidentally reversed implication in the middle tree is valid in every K frame and cannot have the displayed countermodel.

The box example likewise checks: p is true only at 1.2 and q only at 1.1. Both successors satisfy p ∨ q, while neither p nor q holds at every successor.

## Clarification, not another definite typo

Pashto OLNML-041 concerns [item 4 of the complete-branch definition](https://github.com/OpenLogicProject/OpenLogic/blob/1e960beff9ed7835bf3e3f1335e21af3439cd107/content/normal-modal-logic/tableaux/completeness.tex#L42). “Every prefix occurring on the branch” is clearer as “every used successor prefix σ.n to which the rule applies.” The surrounding term “corresponding conclusion” can already carry this restriction, and the chapter explicitly states the restriction in its rules. Therefore this is a supported clarification, **excluded from the twelve-error count and from the minimal patch**.

## Verification and limits

- Both affected current-upstream files match the frozen source byte-for-byte. The untouched K-rule reference also matches.
- Applying the patch requires exactly the registered substitutions; the patch passes `git apply --check` against the two saved current-source files. It does not modify upstream or any translation.
- All four Boolean valuations and all 32,768 two-variable models on three labelled worlds were checked, covering 98,304 world cases. These are bounded tests, not a substitute for the general witness argument above.
- The six existing Pashto tableaux match their frozen witnesses, except for the one disclosed root correction. Both TikZ diagrams are unchanged. This is a structural check, not full Pashto fluency certification.
- Local Tamil records TA-NML-047–058 are merged by exact defect, not counted again. Four exact-filename issue/PR searches returned no matches. This is a bounded duplicate check, **not** a claim that no related report exists anywhere.
- Other source prose and the whole completeness proof have not been certified by this report. No TeX engine or reader rebuild was run.

## Technical provenance

Upstream revision: `1e960beff9ed7835bf3e3f1335e21af3439cd107`; frozen translation revision: `9620cc73f9c8e0ad003c514a5d3748f29611c4c0`.

| Source file | Bytes | SHA-256 |
| --- | ---: | --- |
| completeness.tex | 10148 | `ee4e86d1549731cdbe7088d4d682c304f04a9c007a93a525c99b25959a2c2d90` |
| countermodels.tex | 12874 | `c47ac240cc48f6e82093505895045e59de1a1f034b7e377086c5b53944d744bd` |
| rules-for-K.tex | 9559 | `781f917de40a4b8e0c38ade5e7cd1d9eab39a629563df7f6d07e0434ab5dffe3` |

Tamil intake snapshot SHA-256: `d8ba3ac78719fdcd445cc4c75a11541e482b922fd3c82fa06b9269c0334004e3`. Original report IDs remain in the JSON for traceability. The corrected Pashto countermodels target hash is `b4158e52e3572184c6ea77a6dc138fb7fede247999a5f7f5e087e5e7de6c640e`.

To check the patch in a checkout of the pinned upstream source:

```sh
git apply --check MODAL_COMPLETENESS_SOURCE_CORRECTIONS_20260928.patch
```

Applying it is a separate maintainer choice; this report makes no upstream changes.
