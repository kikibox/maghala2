# Cost and external side-effect safety

Treat these as high-impact operations requiring explicit authorization or an already-approved manual workflow input:
- paid text/image API calls or concurrency benchmarks;
- full or family-wide image regeneration;
- FTPS upload, WordPress publication, production SQL import, or rollback;
- queue reset, retry of exhausted items, mass status changes, or artifact deletion;
- rotation, creation, or exposure of secrets.

Rules:
- Tests must mock network and paid providers.
- A code push must not accidentally select an expensive workflow; use path filters and `workflow_dispatch` inputs.
- Manual workflows must default destructive/expensive booleans to `false` and print a plan before execution.
- Re-running an old failed job is forbidden when the fix exists only on a newer SHA; run the corrected workflow revision instead.
- Prefer targeted regeneration by item/family/range over global rebuild.
- Record estimated item count, image count, language count, and expected API calls before expensive runs.
