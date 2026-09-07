# Current theory-name MathML normalization

OLAB-NATIVE-MATHML-TH-001 repairs the inherited native-MathML rendering of the source macro `\Th` in Models of Arithmetic. Source `open-logic-config.sty` line 1145 defines a bold theory name, not a Th(argument) operator. The distinct `\Theory` macro at line 480 remains unchanged.

The 83 formula occurrences / 34 expressions retain their IDs, source TeX, speech and annotations. Only the two Models of Arithmetic Read/Explore routes change. Original semantic evidence is preserved unchanged; `expression_overrides.jsonl` and `occurrence_overrides.jsonl` provide current normalized MathML by predecessor row/ID, and `NORMALIZATION_LEDGER.json` provides source anchors and byte-minimal route deltas.

This overlay is produced for independent cumulative-reader audit and does not self-claim acceptance or assistive-technology certification.
