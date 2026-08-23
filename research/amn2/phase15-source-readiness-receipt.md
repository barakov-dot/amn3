# Phase 15 source readiness receipt

Date: 2026-08-23

Status: `SOURCE_VERIFIED_LOCAL`

This receipt records the exact committed Phase 15 application source selected
for a local checksum-bound package. It is not a package, remote preflight,
SSH, stage, issuance, deployment, push, or live-mutation authorization.

## Source identity

- Source worktree: `C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness`
- Source branch: `codex/phase15-local-package-bootstrap-readiness`
- Approved Phase 14 source base: `36981d7afc1fcd9eb17386c62f70adf175d76263`
- Verified Phase 15 source HEAD: `6b138784e9d0f02d852548de6414816b7224e145`
- Source status: clean before verification
- Range whitespace check: `git diff --check 36981d7afc1fcd9eb17386c62f70adf175d76263..HEAD` passed

## Source task commit ledger

- `ee66e108cf05b5b3af9df9dfb41ef6e971e42066` — `feat: add durable telegram callback state`
- `d827aff31f640b232992f3102e713ff76dd570b0` — `fix: add durable callback claim leases`
- `0b8d91ecd57ad5cf9159835ec1c388318bc26978` — `fix: keep phase15 ownership enforcement isolated`
- `e8cb47e677734b6d1cd583f3943bb3410e6313a0` — `fix: migrate d827 callback schema`
- `f457b2b7122136b3daa06b6647cbd32c118e4884` — `fix: verify d827 index-drop rollback`
- `e8eed52210c50940df47095984a9c0e816e53007` — `fix: make awg3 callbacks durable and bounded`
- `bf82512f61112fd1d46c14fb1c7be83af1f62be9` — `fix: harden awg3 callback finalization`
- `e99f3abfc33435c718aae50230f7adeae19da749` — `fix: preserve awg3 claims across expiry`
- `b9d635ce6d8236ba90b66678cc97cc2467018236` — `fix: prune consumed awg3 callback state`
- `d8c8e1b56ce9ad4795f23d160149b2a03187592b` — `build: lock phase15 python312 dependencies`
- `ab367e7d42d657ce650f37aafae77176b6d6082a` — `fix: harden phase15 dependency locking`
- `bf8e6161228bf0cbf8e06091ee63e26401a3a248` — `feat: wire fail closed awg3 production bootstrap`
- `6c59299e78b255040d096de96aebe4f2c0584cb7` — `fix: target AWG3 issuance runtime exactly`
- `2f7411b02a4cba36b9d03221d97a2b503bacad97` — `fix: harden AWG3 bootstrap boundaries`
- `6b138784e9d0f02d852548de6414816b7224e145` — `fix: redact host runtime dump errors`

## Local test and dependency evidence

- Focused package-controller safety check: `1 passed, 68 deselected in 0.05s` for the ACL-safe Git-root fix.
- Full source Python 3.12 suite: `1459 passed, 1 skipped, 1 warning in 249.18s`.
- The one warning was a permission-denied pytest-cache write under the ACL-protected source worktree; it did not affect test execution or source files.
- Runtime lock: `requirements/phase15-runtime-py312.lock`, SHA-256 `e87133ab00e86b542092d3b4d1976fdbfc7a6339ffda27d5c85be508fe236961`.
- Test lock: `requirements/phase15-test-py312.lock`, SHA-256 `323d855f3a3aa8fa75796f3f33f6a32debeb7bd43df4f7b8fe9266398c4b1118`.

## Control and execution state at source verification

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
PACKAGE_MATERIALIZED=false
PACKAGE_VERIFIED_LOCAL=false
REMOTE_PREFLIGHT_RUN=false
SSH_USED=false
APPLICATION_STAGED=false
AWG3_RUNTIME_STAGED=false
AWG3_PILOT_ISSUED=false
AWG3_GLOBAL_ACCEPTED=false
AWG3_ISSUANCE_ENABLED=false
LIVE_MUTATION=false
```

## Boundary

The next authorized action is one local materialization from the exact source
HEAD above. Remote preflight, SSH, stage, issuance, deployment, push, and any
live mutation remain forbidden.
