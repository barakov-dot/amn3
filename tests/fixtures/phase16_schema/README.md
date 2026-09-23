# Exact-source synthetic schema fixtures

The four `.txt` files are schema-only Python Git blobs from AMN2 commits
55dc243b8e6c6bdb57f8301b56326e4cd4072d19 and
6e682356ed14a62d636ee58039fd3a389e794809. `provenance.json` binds each path,
commit and SHA256 of Git bytes (LF). They contain no production database rows.

The v3 readback tests verify these hashes and imports before loading only the
schema modules with isolated, temporary module bindings. Application package
initializers, main, Repository and third-party dependencies are never loaded.
Initializers create disposable in-memory SQLite fixtures for old, candidate and
old-to-candidate cases. No retained fixture is silently migrated and reused as
an old-schema baseline. Product code must not import these fixtures.

After collection, tests release the retained authorizer only on disposable
memory connections to compare serialized bytes. This does not modify the
production guard. Trigger bodies and index expressions exist in fixture source
for realism; the collector must not return them in receipts.


Repository slices (2026-09-23): `old_repository_slice.txt` and
`candidate_repository_slice.txt` are Python AST-unparsed selections of seven
methods plus DEFAULT_PLAN_DAYS/_first_host_address, with only stdlib imports.
`repository_provenance.json` binds full original Git blob hashes, revisions,
selected method names and normalized slice hashes. No method body changes;
no app.main, networking, token, env or production data. The maintenance helper
pins these hashes separately from the frozen readback tools/provenance.
