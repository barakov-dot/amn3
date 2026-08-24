# Phase 15 source readiness receipt

Date: 2026-08-24

Status: `SOURCE_VERIFIED_LOCAL`

This receipt records the exact committed Phase 15 application source selected
for a local checksum-bound package. It is not a package, remote preflight,
SSH, stage, issuance, deployment, push, or live-mutation authorization.

## Source identity

- Source worktree: `C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness`
- Source branch: `codex/phase15-local-package-bootstrap-readiness`
- Approved Phase 14 source base: `36981d7afc1fcd9eb17386c62f70adf175d76263`
- Verified Phase 15 source HEAD: `c01c2e34ca506102e485ee3fa50b9420de6e591a`
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
- `b8d0d4babbd2e59f184a2f8e98f699555d4b3b6a` — `fix: preserve retryable phase15 bootstrap failures`
- `02a5cb7987e30b3dfb86b26de7044f6702175faf` — `fix: recover safe phase15 retries`
- `c6b0919f5d6729772857085920f89647db93c29e` — `fix: bind phase15 locks and identity`
- `2aad47622bc5d3b93f7859dca10c7e424e4d7b19` — `fix: expand phase15 manylinux target tags`
- `f598f65e00649e75d04571d3f4f9ec0cca381793` — `fix: harden phase15 bootstrap boundaries`
- `36a39eda6fd07d3588d27632aa2c14b39c25bd73` — `fix: bind phase15 confirmations to attempts`
- `2863b7ea84de89d74ef36b6b72ffad26909ab5ff` — `fix: decouple phase15 confirmation schema`
- `48590dae726a03dc145978d51ce5931e8abc25b6` — `fix: reject malformed phase15 attempt foreign keys`
- `700a0fd641ecd4652f219859065fd8395cb88c0c` — `fix: normalize phase15 foreign key identifiers`
- `a072ea22a6da394ea553dd52f32c87ecb14ab669` — `fix: validate phase15 trigger semantics`
- `15413780c6a805a3791990d54c012c03adeca26b` — `fix: use ascii phase15 identifier folding`
- `518814cdccafb1b30f77ecda3da66131a61bfdae` — `fix: validate exact phase15 schema shapes`
- `8c66b5a79e2524423da99cd23e969112c1c3e924` — `fix: preserve phase15 sql token boundaries`
- `293eb538c699845b62ccfeb92935671125e56961` — `fix: bound awg3 runtime networks`
- `5823578e90c8494670329900e0d4776372bd996d` — `fix: preserve awg2 allocation ordering`
- `3b0412d43219740e78705edeb12a5fb528753b92` — `fix: separate awg2 and awg3 access inputs`
- `e8870cf3c833bf809cad511053c401f90f82fc26` — `fix: validate awg2 operator context`
- `8ef2020262db82ddb7774a1a5a5e2aab3e28abdb` — `fix: validate awg3 operator context`
- `8beb35f39f9f33b764a110236dfcf92a9da3b0b1` — `fix: protect bound confirmation claims`
- `c01c2e34ca506102e485ee3fa50b9420de6e591a` — `fix: normalize confirmation binding columns`

## Local test and dependency evidence

- Final Task 8 targeted Python 3.12 suite: `404 passed, 1 warning in 80.30s`.
- Full source Python 3.12 suite: `1627 passed, 1 skipped, 1 warning in 272.48s`.
- The one warning was a permission-denied pytest-cache write under the ACL-protected source worktree; it did not affect test execution or source files.
- Runtime lock: `requirements/phase15-runtime-py312.lock`, SHA-256 `a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab`.
- Test lock: `requirements/phase15-test-py312.lock`, SHA-256 `52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235`.

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
