# Core operating principles

- Inspect the relevant code, workflow, state, tests, and recent failure before editing.
- Make the smallest reversible change that fixes the verified root cause.
- Do not silently broaden scope or rewrite unrelated files.
- Preserve existing idempotency markers, artifact formats, queue schemas, and rollback behavior.
- Prefer deterministic local logic over new AI/API calls.
- State assumptions. If an ambiguity affects cost, data integrity, publication, or security, stop and ask.
- At completion report: changed files, tests run, remaining risk, operational action required, and whether any external side effect occurred.
- Stop after two failed attempts with the same strategy. Re-inspect evidence and change the hypothesis; never loop retries indefinitely.
