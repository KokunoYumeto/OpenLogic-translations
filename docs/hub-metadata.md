# Edition metadata for the translation catalogue

An edition owns its catalogue facts. The shared hub keeps a repository and locale registry; it reads an edition's default-branch `olp-edition.toml` at one exact commit and the public release manifests. A build contract without public metadata is not a completed hub migration.

The `[public]` table supplies localized `title`, `description`, `limitations`, `attribution` and `license`. Preserve the exact AI model and effort for the work actually performed, inherited human authorship and component rights. Coverage and review are separate facts.

For existing editions, preserving historical DOIs, multiple scripts, download labels and review links requires more than five strings. The optional `[public.catalogue]` table binds an edition-owned JSON presentation record:

```toml
[public.catalogue]
path = "publication/catalogue.json"
sha256 = "<SHA-256 of the exact UTF-8 JSON bytes>"
```

This extends the original public metadata contract without creating a second hand-maintained list in the hub. The file must be in the same repository commit as the contract. The hub verifies the hash before reading it. It may not contain local paths, chat identifiers, private administrative records or credentials.

The JSON wrapper uses schema `openlogic.edition-catalogue.v1` and contains `edition`, `release_discovery`, `release_selection` and `textbook`. Its `edition` carries the preserved public catalogue entry; the other fields carry existing release selections and textbook identity. `link_base` explicitly identifies the published hub root to which inherited relative evidence links refer. Do not reinterpret those links as paths in the language repository. Preserve all historical DOI identities and scholarly credits. The locale, language tag and repository must agree with the contract and registry.

The modern adapter checks published `release.json` records against the Releases API: tag, product group, pins, coverage, exact asset names, sizes and digests. A newer release or structurally valid record is not evidence of wider translation coverage or human review. Failed or unperformed gates must remain explicit. Product groups remain distinct: a textbook cannot replace the complete collection.

Only remove the corresponding hub legacy input after the edition-owned record is public, its exact bytes are verified, its inherited facts are reconciled, and the modern adapter reproduces the accepted scope and links. Until then, retain the existing public edition and report migration as incomplete. Do not create a release or rebuild a reader merely to move metadata; use an authorized existing or naturally due publication checkpoint.
