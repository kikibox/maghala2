# GitHub collaboration

- Use Issues for reproducible failures, operational debt, and manual production actions.
- Use a branch and Pull Request for workflow, queue, SQL generator, image policy, upload, and security changes.
- PRs must explain cost impact, side effects, rollback, tests, workflow/concurrency impact, and generated artifacts.
- Prefer Conventional Commit prefixes: `fix:`, `feat:`, `test:`, `docs:`, `ci:`, `chore:`.
- Close or update stale PRs before merging overlapping changes.
- Do not merge with unresolved failing checks or unknown production impact.
- Record durable architecture decisions in `docs/ARCHITECTURE_DECISIONS.md`; record actionable failures as Issues rather than a local AI memory database.
- Tag immutable user-facing deployment packages as GitHub Releases; do not rely only on expiring Actions artifacts.
