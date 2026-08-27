# Phase 16 package revision 016 readiness receipt

## Result and exact authorization

- Result: `local_package_ready_no_egress`.
- Metadata readback UTC: `2026-08-27T20:45:11.9613338Z`.
- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-016`.
- Package identity SHA256: `c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b`.
- Manifest SHA256: `e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc`.
- The latest user GO was interpreted after normalizing Markdown underscore escaping only.

```text
/GO PHASE16 LOCAL_PREPARE_PACKAGE_016 TDD FROM_COMMIT_392cc339f7f6afaed0a0dc2a0a80139ca030f560 LOCAL_FIX_RECEIPT_SHA256_549b515ea50e7668f56f433772633a63c674aaba973876f978f0a2ea15f823de NEW_PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-016 PACKAGE_015_IMMUTABLE TRANSACTION_006_CONSUMED ONE_TARGETED_REGRESSION ONE_MATERIALIZATION ONE_VERIFIER NO_SPAIN_EGRESS NO_REMOTE_WRITE NO_STAGE NO_INSTALL NO_CONFIG NO_ISSUANCE AWG2_UNTOUCHED
```

Package 015 remains immutable. Transaction `phase16-spain-stage-20260827-006` and its earlier live approvals remain consumed. This GO did not authorize any Spain egress, preflight/stage retry, install, config or issuance.

## Exact source, tooling and commit bindings

- Approved starting commit: `392cc339f7f6afaed0a0dc2a0a80139ca030f560`.
- Local-fix receipt: `research/amn2/phase16-local-controlled-stage-scalar-exit-and-stdin-eof-fix-receipt-015.md`.
- Local-fix receipt SHA256: `549b515ea50e7668f56f433772633a63c674aaba973876f978f0a2ea15f823de`.
- Retained scalar-exit/BOM-free-stdin implementation commit: `0e5b57a0a5b506bdea6f4b2672f6b67894f594df`.
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`.
- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`.
- Application worktree: `C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness`; no application changes.
- Packaged tooling SHA: `db7a4bde2ba8b5a23f6d9b6e580f1223259330ce`.
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-016`.
- Verified package commit: `bac20979b1715787a6b48fd67a4a4bb890f82c13`.
- Existing tooling worktree: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\phase16-004`.
- Local branch 016 was created from the exact approved starting commit in the existing worktree. Branch 015 was retained; no merge, reset, rebase, push or PR.
- This receipt is outside the immutable package; its commit does not alter package identity and does not require repeating the regression, materializer or verifier.

## Bounded delta and TDD

- Production change: 13 files, package-ID/tooling-branch substitutions only. Normalizing those substitutions reconstructs every original file SHA256.
- The fixed runner is preserved from the approved baseline, not copied from frozen package 015. Normalized fixed-source SHA256: `fbdeda5f061eda91e8ca835e5b7c95b1233c4e6698ef497b33374ab353711635`.
- Binding test was advanced from revision 015 to 016, with real manifest admission and rejection coverage. Historical tests remain recoverable through Git.
- Focused RED: 1 expected failure in 0.107s, `manifest package identity` on a revision-016 in-memory admission fixture against old revision-015 production bindings. No package was created by the test.
- Focused GREEN: 6 passed in 1.141s.
- Exactly one final targeted regression: 24 passed in 4.845s, no failures or errors.
- Covered modules: runner/host/scalar exit (5), local binary transport/EOF (4), coordinator failure-locus/milestones/rollback (9), revision-016 binding/preservation (6).
- These are real local runner/coordinator contracts with external boundaries replaced by local fixtures. Synthetic stage outcomes exist only in test temporary directories; they are not live acceptance evidence.
- Python: bundled standard-library unittest with `-I -B`; no pytest/dependency installation.
- Windows PowerShell test subprocesses: `-NoProfile -NonInteractive -ExecutionPolicy Bypass`; only child PSModulePath removed. No machine/user policy change.
- No full source/legacy suite, independent reviewer, subagent or additional final regression was run.
- Scoped pre-commit check: 20 logical files / 21 paths including the binding-test rename; `git diff --check` PASS, added-line secret matches 0.
- Package commit scope: exactly 172 new files, package-only staged inventory, staged diff check PASS, clean worktree after commit.

Reproducible final suite (with the child environment above):

```python
import unittest; loader=unittest.TestLoader(); suite=unittest.TestSuite(); patterns=('test_phase16_controlled_stage_runner_host_forwarding.py','test_phase16_controlled_stage_local_transport.py','test_phase16_controlled_stage_failure_locus.py','test_phase16_package_016_binding.py'); [suite.addTests(loader.discover('tests', pattern=p)) for p in patterns]; result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(0 if result.wasSuccessful() else 1)
```

## One materialization and one separate verifier

- Materialization invocation count: 1; result `materialized`, exit 0.
- Materialization UTC: `2026-08-27T20:43:55.2284017Z` to `2026-08-27T20:43:58.0103260Z`.
- Separate verifier invocation count: 1; result `verified`, exit 0.
- Separate verifier UTC: `2026-08-27T20:44:23.4134601Z` to `2026-08-27T20:44:23.5494738Z`.
- Materializer built-in integrity validation remained enabled. No automatic retry and no additional standalone verifier.
- Both returned the same package identity.
- Manifest entries: `171`; total inventory including manifest: `172`; payload bytes excluding manifest: `10585896`.
- Source and tooling were clean, named-branch and exact-HEAD bound before materialization.
- Local ignored attempt markers were reserved before dispatch and retained; they are not remote claims:
  - materialization marker SHA256: `63b0bc37a17ac447877d07d8412d91e4f9f08c1d59ead5f7bfc69e73d60f48ed`;
  - verifier marker SHA256: `c71668c21e5a9ddaebfd291902279c3ba7157f37c060dff6f05e95515147bfd7`.
- A sandbox ACL denial while reading packaged rollback metadata was resolved by repeating only that read with elevation; no ACL was changed and no test, materialization or verifier was repeated.

## Packaged artifact SHA256

- `manifest.json`: `e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc`.
- `source/requirements/phase15-runtime-py312.lock`: `a381be185b19777b9198526e11df8dcfa0afaf7f15acccd829809e698d679fab`.
- `source/requirements/phase15-test-py312.lock`: `52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235`.
- `tooling/packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json`: `dea2c165c4fe0e2959f34e78b722980ba810ea7c9546a2ad1aaaaf5917af82f3`.
- `tooling/research/amn2/phase16-source-readiness-receipt.md`: `ece7e57b411ef3f3600d0bfcdd51bd61e56a47f1200135b7a2549303d07b52cf`.
- `tooling/scripts/vps/phase16_application_stage_remote.sh`: `6454a6ff52f6f608f126aae7989e74666393d0da6f84c13533d99cb273b9e9f8`.
- `tooling/scripts/vps/phase16_awg31_runtime_stage_remote.sh`: `1aca96948c346286c0e1d5767e4de72778c70ff73faabd3a30b9a3f6e14626ea`.
- `tooling/scripts/vps/phase16_controlled_stage_coordinator.py`: `a016adbdcbf9acd57f6e96e9ffeb5f2289b5b9c1dbe2008e84b36984dbfae4ee`.
- `tooling/scripts/vps/phase16_controlled_stage_ssh_runner.ps1`: `6364d652181cd6f522dbecd25e2c4b36e8c1d06736cb67a2e6a3e4894da7dd77`.
- `tooling/scripts/vps/phase16_spain_readonly_preflight_remote.sh`: `fdda3146d2e98f544d10b56c2a0d27a2e2039f1b8738bee5d39a6fc14c74b75e`.
- `tooling/scripts/vps/phase16_spain_readonly_preflight_ssh_runner.ps1`: `9e99821cbd7eb7d223b257046cb178e99672d6c1b9cd0b08ed8be374345e5b26`.
- `tooling/scripts/vps/phase16_stage_support.py`: `67f991d909bbc398afee9e84063728645cb234b96a94a86ae5c61d77d20e4487`.
- Canonical rollback-scope SHA256: `9efad64c2a6bfa717d02da9967c49e049e31425722037d91c8d519c31d75fdb2` (Python and PowerShell scope equality was covered by the targeted tests).

## Preserved runtime, client and safety contracts

- Runtime artifact: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`.
- Runtime source commit: `1f50ad736ecca22a9bfc7b4606805ec9ca49fe48`.
- Required runtime capabilities: `disable_cookies`, `random_trailers`.
- Packaged client candidate: `amneziawg/android/v3.1.20260814/12`, release kind `stable`.
- Client artifact: `github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/AmneziaWG-3.1.202060814.apk@sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697`.
- These are retained pinned artifact bindings, not a new upstream or installed-client verification. ARM/Windows remains the requested first live pilot; its exact admission is a later separate gate. No Android/iPhone acceptance is claimed.
- AWG2 freshness remains 600 seconds; AWG2 config, peers, runtime, golden bytes and global issuance policy are unchanged.
- Preflight/application/runtime/support/coordinator/resource-plan bytes match package 015 after package-ID normalization.
- Mandatory rollback, allowlisted failure classes, ordered milestones, checksum/state/claim bindings, strict host checking, EOF/truncation/trailing-byte rejection and no-raw-output policy are retained.
- The local BOM reproduction does not conclusively establish every cause of historical transaction 006. New package readiness is not live transport or controlled-stage acceptance.
- Package-015 preservation: all 171 entries and 172-file inventory checked in the binding regression; manifest and identity anchors match the approved original.
- Package-015 manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Package-015 identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Existing consumed SIGTERM attempt marker remains `32094947f544e0e2cd6ea95fe1783eef514a9be03779a1547d652fa00b9cd77a`.
- Spain egress/SSH, remote write, live preflight, stage, install, rollback, config creation, peer/global issuance and AWG2 probes/mutations in this GO: 0.
- Public Git push was not attempted: separate informed approval to publish the accumulated history to the public origin remains pending.

## Next exact gate

Only a new checksum-bound Spain read-only preflight may be proposed next. The operator should generate fresh AWG2 traffic before the attempt; the unchanged health gate requires a successful handshake no older than 600 seconds. The VPN need not remain active for the assistant's transport after traffic has been generated.

The following is a proposed next approval, not an executed action or authority carried by the current local GO:

```text
/APPROVE PHASE16 SPAIN READONLY_PREFLIGHT_EGRESS TO_138.124.181.246 PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-016 IDENTITY_c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b MANIFEST_SHA256_e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc COLLECTOR_SHA256_fdda3146d2e98f544d10b56c2a0d27a2e2039f1b8738bee5d39a6fc14c74b75e RUNNER_SHA256_9e99821cbd7eb7d223b257046cb178e99672d6c1b9cd0b08ed8be374345e5b26 NO_REMOTE_WRITE NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

A successful new preflight must be followed by a separate package/state/rollback-scope/new-transaction-bound stage approval. No reuse of transaction 006. The first pilot config requires accepted controlled stage and its own exact client/pilot approval.

## Phase 16 status

- ✅ Task 0 — baseline confirmed.
- ✅ Task 1 — package 016 locally materialized and verified.
- ▶️ Task 2 — fresh checksum-bound Spain read-only preflight awaits exact approval.
- ⏳ Task 3 — controlled stage not yet accepted.
- ⏳ Task 4 — first AWG3.1 operator config for ARM/Windows.
- ⏳ Task 4.5 — mandatory AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — real client acceptance.
- ⏳ Task 6 — closeout.

Safety state: no new live actions; AWG2 untouched; package 015 immutable. Recommended next-step profile per the approved plan: GPT-5.6 SOL / High; actual active runtime model/effort metadata is not asserted.
