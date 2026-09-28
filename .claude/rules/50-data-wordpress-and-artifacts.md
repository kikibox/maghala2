# Data, WordPress, and artifact integrity

- Production create SQL must be idempotent; rollback must delete only records carrying the exact generation marker.
- Preserve WordPress table prefix and database name configuration; do not hardcode a different target.
- Use explicit `utf8mb4_unicode_520_ci` where this project compares legacy WordPress text values.
- Never label a translation complete unless JSON/HTML/create SQL/rollback and package membership all exist.
- A translated post must retain source relation, correct language/archive taxonomy, and inherited featured image when required.
- Write state and manifests atomically through a temporary file plus replace.
- Validate counts before publishing: source posts, translations, images, SQL entries, rollback entries, and checksum.
- Do not overwrite previously approved images until the complete candidate set passes quality gates.
- Release-ready ZIP files are immutable: a changed payload requires a new version/checksum, not silent replacement.
