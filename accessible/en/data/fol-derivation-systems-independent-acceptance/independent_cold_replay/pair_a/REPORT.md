# OLAB-TR-019 First-Order Derivation Systems semantic projection

Producer status: **PASS — ready for independent semantic audit**

This projection uses the independently audited TR-009 semantic layer only after
proving exact source equality of all 64 expression IDs and shapes, all 137
normalized-TeX/file/line/column/source-coordinate tuples, and all three-line
source context packets. The only profile differences are the expected projected
IDs, global stream coordinates, and six FOL entry-tag states.

The initial independent TR-019 audit showed that source equality did not make
two propositional meanings valid in the first-order profile. Those two meanings,
covering three occurrences, now explicitly quantify over first-order structures
and relevant variable assignments. The other 62 expression meanings remain
exact to the independently audited TR-009 payload.

The package contains 128 native, parseable, unflattened MathML variants, 15
preserved contextual overrides, and complete words-only narratives for two
proof trees, one tableau, and one derivation. The tableau's printed source-label
issue remains explicitly disclosed. Reader integration and independent TR-019
semantic approval are downstream and are not claimed here.

The deterministic semantic input boundary now contains only immutable source,
oracle, audited-reuse, audit-finding, and tool inputs. Mutable durable controls
are documented as nonbinding operational context without embedding live hashes,
so their normal advancement cannot perturb canonical semantic bytes.
