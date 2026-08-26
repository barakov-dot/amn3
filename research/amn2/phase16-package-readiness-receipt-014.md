# Phase 16 package revision 014 readiness receipt

- Recorded: `2026-08-26T20:37:00Z`
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-014`
- Package identity SHA-256: `d741006c3b0d788700020a93ac02a3bb5f35a1ec89d9497902ef7c8ac5726f19`
- Manifest SHA-256: `844499afb51ca4cd5eacc8a395c003aabba39ffd02723ae4e95e4d28105b6cb1`
- Collector SHA-256: `59f2849561cfc6bd52a76c2ca809c69a8e4aee2eba98f0d2e6f0921bdb8ba169`
- Preflight runner SHA-256: `10994e09ffa000dbd5bb482d36e8939d6e5fbe524995d5905b8b796bf0231be8`
- Resource-plan SHA-256: `4e13be95ba38faf1985f1e2912045302ecd604a8bcf236be0ef8e06d0ff2267f`
- Application stage SHA-256: `0babd8b5f34a0f232afb44f839304d31b762f998f9813a1ac42f20bf79ee8e06`
- AWG3.1 runtime stage SHA-256: `c31e922b9830658fdc3630e697afd2d1e53cb79db1852a4c72983879f2802b55`
- Stage support SHA-256: `6a5162188b3d199a6636fc75e3b7754d59b0031dd798b333f1e8b88ceb4735fe`
- Controlled-stage coordinator SHA-256: `39e96e6dc70cf048c2e501d7cd5010b8c87aa6086eb9dcb9479d0552ff96bffb`
- Controlled-stage SSH runner SHA-256: `62aa74ffe9dbc3038391d2ebf59aed8a2a0a47a6deb072d8be0f904577a8e620`
- Source-readiness receipt SHA-256: `8d4fbc305fbdb359172c12e4d2ab8e09cd691aec43426b135bf0b2b142c05627`
- Canonical rollback-scope SHA-256: `1c520a5033b8b391d57fdf477b0cc20b2f51f6e748345120b5ed0d2606d60a26`

## Source and commit binding

- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-014`
- Approved local starting commit: `ccdf44cc75331e2254a87590a4fdb84a347af9b6`
- Runner observability correction commit: `a66532ccbdf7a62d143cd23b3862093b256166ae`
- Package revision binding and packaged tooling source SHA: `7a1fea9c18af377abe3b6a67656a1a11468f661a`
- Package materialization commit: `f8ea21e5eeefcc3628cbd10ad8b194d6c7eed364`

## Materialization and verification

- Actual materialization count: `1`
- Separate verifier count: `1`
- Materializer result: `materialized`
- Verifier result: `verified`
- Package identity returned by materializer and verifier: equal
- Manifest entry count: `171`
- Total package file count including manifest: `172`
- Materializer and verifier reported file count: `171`
- Dependency installation: none

## Local validation evidence

- Runner observability RED: `3 failed`, `1 passed`; all failures were the three missing observability functions
- Runner observability focused GREEN: `4 passed in 1.379s`
- Package binding RED: active package script returned revision 013 instead of revision 014
- Package binding GREEN: revision 014 active bindings passed and package 013 immutable hashes matched
- Final targeted regression: runner `unittest` `4 passed in 1.654s`; binding/immutability `1 passed`; Python AST `6 passed`; Bash syntax `3 passed`; PowerShell parser `2 passed`
- Full changed-file scope from the approved starting commit: `18` exact files
- Pre-materialization `git diff --check`: pass
- Added-line secret matches: `0`
- Package staged inventory: exact `172` files under the package-014 root

## Controlled-stage observability and safety boundary

- The external stderr contract remains the single fixed token `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP`
- A failed runner may create only the sibling local artifact `<outcome>.runner-failure.json` with create-new semantics
- Failure class and last completed milestone are selected from fixed finite allowlists
- Transport output evidence is limited to UTF-8 byte length and SHA-256 for stdout and stderr plus a bounded process exit code
- Raw exception text, raw stdout, raw stderr, credentials, host-key material, package payload and configuration material are not written to the failure artifact
- Automatic retry was not added
- Transaction `phase16-spain-stage-20260826-003` remains consumed and must not be reused
- Package 013 remains checksum-immutable
- Spain egress, SSH, remote write, rollback, stage retry, stage, install, peer/config issuance and global issuance during package 014 local work: none
- AWG2 mutations or service operations: none

This receipt records one materialized and one separately verified local package.
It does not authorize Spain preflight, controlled stage, install, pilot issuance,
config creation, global AWG3 issuance or any AWG2 operation. A new Spain
read-only preflight requires a separate exact package-, identity-, manifest-,
collector- and runner-bound approval.
