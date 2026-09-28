# Repository instructions

Before changing code, read every applicable file in `.claude/rules/`.

Order of precedence:
1. Safety, security, and explicit user instructions
2. Project profile (`90-project.md`)
3. Workflow and data rules
4. General quality rules

Default communication with the repository owner is Persian. Keep code, identifiers, commit messages, and machine-readable output in English unless the existing file requires another language.

Never trigger a paid API call, image rebuild, FTPS upload, WordPress publication, destructive SQL, or broad queue reset merely to validate a change. Use mocks, fixtures, dry-runs, or a dedicated manual workflow.
