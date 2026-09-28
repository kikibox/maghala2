# Project profile: maghala2

Purpose: generate Persian articles, three linked translations, images, SQL packages, and optional WordPress delivery.

Invariants:
- Final integrated batch contract is 50 Persian sources + 150 translations (Arabic, Tajik, English) = 200 posts.
- Every source uses the three-image article contract; translation featured images inherit the source thumbnail.
- Translation archive taxonomies are `maqalat-al-ray`, `maqolahoi-obyor`, and `en` as defined by current tests.
- Translation completion requires JSON, HTML, create SQL, rollback, relation metadata, taxonomy, and package membership.
- Legacy comparisons use explicit `utf8mb4_unicode_520_ci`; do not reintroduce bare `SET NAMES utf8mb4;`.
- Image rebuild, translation, article generation, packaging, and upload use independent concurrency groups.
- Priority when serialization is required: image repair, then translations/packages, then new Persian generation.
- Text-tail cleanup must be deterministic and must not call an AI model.

Relevant tests: all files under `tests/`, especially translation/package/idempotency regressions.
