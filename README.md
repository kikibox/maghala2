# Navar Abyari multilingual content project

Workspace for auditing and completing Persian → Iraqi Arabic and Tajik translations for navar-abyari.ir.

## Baseline

- Database dump: `navaraby_wp569.sql` (kept local; never committed)
- Dump generated: 2026-09-13
- WordPress table prefix: `ha_`
- Output target: validated full SQL import file

## Workflow

1. Inventory published WordPress content
2. Match existing Iraqi Arabic and Tajik translations to Persian sources
3. Translate missing articles in controlled batches
4. Preserve HTML, SEO metadata, taxonomies, and WordPress relationships
5. Validate IDs, SQL syntax, encodings, and content counts
6. Package the complete SQL output
