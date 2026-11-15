# Open Logic translations

[Choose a language](https://kokunoyumeto.github.io/OpenLogic-translations/) · [Open Logic Project](https://openlogicproject.org/) · [Original sources](https://github.com/OpenLogicProject/OpenLogic)

Translations of the Open Logic Project’s open-source mathematical logic texts, together with textbook editions that select and arrange those texts for a course. The original mathematics belongs to the Open Logic Project authors and contributors. Individual editions identify their human sources, AI translation authorship, licences and limits of review.

**English — accessible / compatibility edition:** [read, listen and explore equations](https://kokunoyumeto.github.io/OpenLogic-translations/accessible/en/). This edition preserves the mathematical content and provides alternative ways to read it. Accessibility is shared infrastructure, distinct from translation into another language or register.

{{editions}}

<!-- textbooks:begin -->
<!-- textbooks:end -->

## Using these editions

Translations preserve mathematical meaning, quantifier scope, formulas, citations and cross-references. Their terminology and register must be grounded in scholarship in the target language. The [translation-decision contract](catalogue/translation-decisions/README.md) describes the source and canon evidence needed to review choices. A published reader is not a claim of independent human review.

The [catalogue](catalogue/editions.json) retains script profiles, source versions, reader coverage, scholarly provenance, historical identifiers and known limitations. Current download links do not remove earlier releases. Rights and component credits remain attached to each edition; the licence of the main text need not cover every photograph, portrait or font.

[Script and register guide](catalogue/script-surfaces.json) · [Broader mathematics programme](https://openmaths.org/)

## Edition builder (olpkit)

The [`olpkit/`](olpkit/) folder holds olpkit, the shared tool that builds and checks the editions: it keeps the map from English source paths to translation units, plans updates when the English sources change, records each edition's source pins and unit metadata, compares the TeX structure of a translation with the English, and builds the readers from pinned sources. Its full history is kept in this repository. [`olpkit/README.md`](olpkit/README.md) describes each command.

To install it and run its tests (Python 3.11 or later):

```
cd olpkit
python -m pip install -e .
python -B -m unittest discover -s tests
```

The olpkit code is dedicated to the public domain under [CC0 1.0](olpkit/LICENSE). The Open Logic texts it builds keep their own licences.

<!-- releases:begin -->
<!-- releases:end -->

Catalogue tooling produced by OpenAI Codex — GPT-6 Astra, Ultra effort. Translation authorship is stated by each edition; no human translation or review is implied.
