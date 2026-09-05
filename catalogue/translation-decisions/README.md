# OpenLogic translation-decision contract

This directory publishes the shared evidence contract used by OpenLogic language, locale, script-projection, notation-profile, accessibility, and constructed-register lanes. See [`translation-decision.schema.json`](translation-decision.schema.json) for the normative machine schema. [`example.valid.json`](example.valid.json) is a synthetic adapter fixture and explicitly not canon or translation evidence. [`TRANSLATION_DECISION_SCHEMA_QA.json`](TRANSLATION_DECISION_SCHEMA_QA.json) records its deterministic validation.

Each edition release should expose these generated views:

- `START_HERE.md`
- `TRANSLATION_DECISIONS_FULL.md`
- `PRIORITY_REVIEW.md`
- `DECISION_OCCURRENCES.csv`
- `DECISIONS.json`
- `translation-decision.schema.json`
- `TRANSLATION_DECISION_QA.json`

The contract distinguishes a stable semantic `decision_id` from each concrete `occurrence_id`; records whether evidence was contemporaneous, retrospective, or derived; binds exact source and target spans; records actual canon passages and their hashes; never guesses missing reader pages; and keeps language, script, territory, register, and notation profile separate.

Review fields expose uncertainty without creating a human-dependent release gate. If an established headword is absent, the edition records a reversible best-evidence rendering and alternatives instead of omitting the source.

The complete human-readable operating rules and release semantics are retained in the manager state copy and summarized in the repository's [`TRANSLATION_STANDARD.md`](../../TRANSLATION_STANDARD.md).
