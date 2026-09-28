# Operations runbook

## Before a manual production run
- Confirm the workflow SHA contains the intended fix.
- Record target item/range/family, expected posts/translations/images, and estimated API calls.
- Confirm no overlapping generation, translation, rebuild, package, or upload run can conflict.
- Confirm secrets and target environment without printing values.
- Prefer dry-run or one-item canary.

## Failure handling
1. Classify: failed, cancelled, skipped, stalled, or covered by a newer run.
2. Preserve logs and item IDs; redact secrets.
3. Do not repeatedly rerun the same SHA.
4. Fix the root cause and add a regression test.
5. Resume only the missing scope; do not reset successful output.

## Release checklist
- Tests pass.
- Manifest counts and archive members match.
- Create SQL is idempotent and rollback is marker-scoped.
- Checksums are recorded.
- Production package is published as a versioned Release when stable.
