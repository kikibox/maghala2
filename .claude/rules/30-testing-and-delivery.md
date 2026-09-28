# Testing and delivery

Before declaring a code change complete:
1. Run Python syntax checks on changed Python files.
2. Validate changed YAML files with a parser.
3. Run the smallest relevant unit tests, then the full test suite when practical.
4. Verify no test made a real network, paid API, FTPS, WordPress, or production database call.
5. For packaging changes, inspect manifest counts, archive members, checksums, create SQL, and rollback SQL.

Never weaken or delete a failing test merely to make CI green. If a test cannot run because a dependency or fixture is missing, report that explicitly.

Required regression themes:
- queue recovery and saturated attempts;
- idempotent SQL/import and marker-scoped rollback;
- three-image article contract and safe staged replacement;
- 50 source + 150 translation package contract for article batches;
- language taxonomy, featured image inheritance, UTF-8 and collation safety;
- upload signal selects only newly approved packages.
