# Edition-specific synchronization packets

`sync edition --repo <repo> --ref <commit> --plan <plan-directory> --out <folder>`
reads the exact edition commit and the cached upstream revisions. It verifies the
full current unit ledger and target bytes before creating a packet for each
changed content unit. The upstream plan must include every actual changed file,
including style files, and its blob identities and SHA-256 values must match.

Each packet preserves the full English before and after, current translated text
and hash, current ledger record, and matched terminology rows with their source
locations. Matching uses literal English terms in added/deleted hunk lines;
headers and unchanged context are excluded. The complete termbase accompanies the
packets, so the filter is a navigation aid rather than a claim of complete canon
coverage. The exact orthography file also accompanies them.

Packet generation makes no edition change, chooses no disposition, runs no TeX
and asserts no canon consultation. Existing corrections remain visible for the
owner to retain, update or resolve explicitly. The owner must consult actual
target-language sources and record the resulting choices. Added, deleted and
renamed upstream paths require explicit migration handling; they are rejected
rather than treated as ordinary replacements by this first modified-file route.

The remaining T15 accept, product verification, status and release integration
must bind actual source/canon decisions and build receipts before declaring the
sync complete. Preparing these packets does not establish a new edition pin or
publication readiness.
