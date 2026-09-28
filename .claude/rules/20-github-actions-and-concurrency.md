# GitHub Actions and concurrency

- Give generation, translation, image rebuild, packaging, upload, and watchdog workflows separate concurrency groups.
- Use `cancel-in-progress: false` for production pipelines whose partial output must survive; use `true` only for read-only CI.
- Prevent recursive push loops with precise `paths`/`paths-ignore`, commit markers, and event guards.
- A watchdog may observe and dispatch but must not race with the worker it monitors.
- Bound every poll loop, API retry, and queue wait with timeout, backoff, and a terminal state.
- Pin action major versions, minimize `GITHUB_TOKEN` permissions, and never print secrets.
- Generated state commits must be atomic, scoped, and conflict-aware. Pull/rebase before push and never force-push `main`.
- Upload only diagnostic artifacts needed for recovery; set short retention for logs and candidates, longer retention for release-ready packages.
- A skipped/cancelled run is not automatically a failure. Confirm whether a newer successful run covers its intended output.
