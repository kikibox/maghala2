# Contributing

## Change flow
1. Create an Issue for production bugs, costly operations, or multi-file changes.
2. Create a focused branch from current `main`.
3. Add or update regression tests.
4. Run the relevant local checks.
5. Open a Pull Request using the repository template.
6. Merge only after checks pass and production impact is understood.

## Prohibited in ordinary CI
Real paid API generation, FTPS upload, WordPress publishing, production SQL execution, queue reset, and secret rotation.

## Commit style
Use `fix:`, `feat:`, `test:`, `docs:`, `ci:`, or `chore:` with a concise English description.
