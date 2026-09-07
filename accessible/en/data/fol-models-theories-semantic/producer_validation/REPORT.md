# OLAB-TR-018 producer validation

Status: **PASS — producer validation complete; ready for separate independent audit**.

The fail-closed validator accepted the exact 163-shape, 326-MathML-variant, 310-context, 310-occurrence, 28-formal-object, four-unsolved-exercise, and four-source-correction projection. It replayed all 310 occurrence readings across all seven source files and retained the sixteen prior continuous-Listen repairs plus the exact operand-order repair for projected-formula-0007820. Against the byte-preserved latest independent FAIL cold build, exactly one expression speech row and its one occurrence/review speech row changed, with dependent record hashes only; meanings, native MathML, source, coordinates, formals, exercises, corrections, and closures remain unchanged. All 56 adversarial mutations were rejected, including in-memory replay and fully rehashed artifact regressions of operand order. The canonical build and two clean cold replays produced three byte-identical 16-file trees. Authority inputs remained stable during certification; controls and every historical independent audit artifact remained byte-identical; and no producer Python cache or adversarial-case residue remains.

This evidence is producer-authored and producer-run. It does not claim an independent semantic PASS.
