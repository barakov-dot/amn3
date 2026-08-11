# AMN2 Phase 15 Local Package, Bootstrap and Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Довести локальный контур AWG2/AWG3 до состояния, в котором production composition root, restart-safe Telegram callbacks, Python 3.12 dependencies, checksum-bound пакет и полностью read-only Spain preflight tooling готовы и локально проверены, но никакие SSH, stage, issuance, deploy или live mutation ещё не выполнялись.

**Architecture:** Phase 15 сохраняет AWG2 протоколом по умолчанию и добавляет AWG3 как fail-closed capability. Telegram wire callbacks используют короткие opaque handles, а полное состояние хранится в SQLite. Production composition root собирает уже существующие Phase 14 admission/control/issuance компоненты только из проверенных providers и реального issuer boundary. VPS-OPS-LAB материализует новый независимый checksum-bound пакет из точного source HEAD и проверяет его локально; remote collectors остаются неисполненными до отдельного `/GO`.

**Tech Stack:** Python 3.12, SQLite, aiogram, FastAPI/Starlette, httpx2, pytest, JSON Schema, SHA-256, PowerShell, Bash, Git archive.

## Global Constraints

- Source base: `36981d7afc1fcd9eb17386c62f70adf175d76263` on `codex/phase14-dual-protocol-application-local`.
- Phase 14 readiness receipt: `research/amn2/phase14-dual-protocol-application-readiness-receipt.md`, SHA-256 `D33E69B53C7397C567B16C4F1CAEA12AF97969D9436D3E95E6038148054AA982`, receipt commit `4e1052c079e1e25031a6c80f4dae1763e457ca48`.
- Phase 15 design: `docs/superpowers/specs/2026-08-11-amn2-phase15-local-package-bootstrap-readiness-design.ru.md`, commit `06f14bc9d7d4d98beca3852fe0ea674f7e65268d`.
- Create an isolated source worktree and branch `codex/phase15-local-package-bootstrap-readiness` from the exact source base. Do not modify the Phase 14 branch or remotes.
- Work locally only. No push, package transport, SSH, preflight execution against Spain, real issuance, peer/config/QR creation, deploy, service/firewall/runtime/client mutation, or live observation.
- Preserve AWG2 golden bytes, AWG2 runtime, existing Phase 14 admission/control/lifecycle contracts, callback ownership rules, and all unrelated untracked files.
- Do not activate admin monitoring notifications. Phase 15 may define only the future admin-only event taxonomy and bootstrap interface; active monitoring waits until the runtime/config contour exists.
- Use RED/GREEN TDD for every task. Any failure outside the declared RED, schema ambiguity, SQLite lock timeout, source/receipt mismatch, or new file-list expansion is a STOP condition. Do not blind retry.
- After each task: focused tests, `git diff --check`, secret-shaped added-line scan, exact file-scope review, one local task commit, spec-compliance review, code-quality review, then a Russian handoff with criticality, remaining tasks, estimate, current model/effort and recommended next model/effort.
- Use `GPT-5.6 SOL High` with effort `High` for implementation, migrations, bootstrap wiring, package identity and review. Medium is permitted only for purely mechanical documentation after all executable gates pass.
- Package ID for this plan is fixed: `phase15-dual-protocol-bootstrap-20260811-001`.
- Final local gates must record these booleans exactly:

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
PACKAGE_MATERIALIZED=true
PACKAGE_VERIFIED_LOCAL=true
REMOTE_PREFLIGHT_RUN=false
SSH_USED=false
APPLICATION_STAGED=false
AWG3_RUNTIME_STAGED=false
AWG3_PILOT_ISSUED=false
AWG3_GLOBAL_ACCEPTED=false
AWG3_ISSUANCE_ENABLED=false
LIVE_MUTATION=false
```

---

### Task 1: Establish the exact source gate and durable callback schema

**Criticality:** Critical — all restart-safe Telegram and bootstrap work depends on durable ownership and one-time state.

**Files:**

- Create: `app/db/phase15_bootstrap.py`
- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Create: `tests/db/test_phase15_bootstrap_schema.py`

- [ ] **Step 1: Verify exact immutable inputs and create the isolated worktree**

Run from a clean administrative shell:

```powershell
git -C C:\Users\SooL\Documents\amn2-phase14-dual-protocol-application rev-parse HEAD
git -C C:\Users\SooL\Documents\amn2-phase14-dual-protocol-application status --short
Get-FileHash -Algorithm SHA256 C:\Users\SooL\Documents\VPS-OPS-LAB\research\amn2\phase14-dual-protocol-application-readiness-receipt.md
git -C C:\Users\SooL\Documents\VPS-OPS-LAB rev-parse 4e1052c079e1e25031a6c80f4dae1763e457ca48
git -C C:\Users\SooL\Documents\amn2 worktree add C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness -b codex/phase15-local-package-bootstrap-readiness 36981d7afc1fcd9eb17386c62f70adf175d76263
```

Expected: exact source SHA and receipt hash match; source status is clean; new worktree HEAD is the same SHA. Otherwise STOP.

- [ ] **Step 2: Write failing schema and migration tests**

In `tests/db/test_phase15_bootstrap_schema.py`, require two additive tables:

1. `telegram_callback_handles`: `handle_digest` primary key, `purpose`, `owner_user_id`, `passport_device_id`, nullable `client_platform/application/version/build`, `request_fingerprint`, `created_at`, `expires_at`, nullable `consumed_at`, nullable `terminal_reason`.
2. `protocol_issuance_confirmations`: `token_digest` primary key, `selection_handle_digest`, `owner_user_id`, `passport_device_id`, exact structured client identity, `request_fingerprint`, `created_at`, `expires_at`, nullable `consumed_at`, nullable `terminal_reason`.

Test idempotent `initialize_schema()`, preservation of legacy Phase 14 rows, foreign-key/index presence, token/handle uniqueness, exact owner/passport lookup, TTL pruning, terminal consume, wrong-owner non-consume and restart visibility from a fresh SQLite connection.

- [ ] **Step 3: Run the RED**

```powershell
py -m pytest -q tests/db/test_phase15_bootstrap_schema.py
```

Expected: failures only because the Phase 15 tables/repository methods do not exist.

- [ ] **Step 4: Implement the additive migration and repository API**

`ensure_phase15_bootstrap_schema(conn)` must create/upgrade only the Phase 15 tables and indexes, preserve all Phase 14 data, be restart-idempotent, and run after `ensure_phase14_dual_protocol_schema(conn)` from `initialize_schema()`.

Add repository methods with typed row returns:

- `create_callback_handle(...)`
- `claim_callback_handle(handle_digest, owner_user_id, now)`
- `consume_callback_handle(..., terminal_reason)`
- `create_issuance_confirmation(...)`
- `claim_issuance_confirmation(token_digest, owner_user_id, now)`
- `consume_issuance_confirmation(..., terminal_reason)`
- `prune_expired_phase15_callback_state(now)`

All create/claim/consume paths must use `Repository.transaction()`; digest values only, never raw callback tokens.

- [ ] **Step 5: Run GREEN and migration compatibility**

```powershell
py -m pytest -q tests/db/test_phase15_bootstrap_schema.py tests/db/test_phase14_dual_protocol_schema.py tests/db/test_schema.py
git diff --check
```

Expected: all pass; no Phase 14 schema regression.

- [ ] **Step 6: Review and commit**

```powershell
git status --short
git diff -- app/db/phase15_bootstrap.py app/db/schema.py app/db/repositories.py tests/db/test_phase15_bootstrap_schema.py
git add app/db/phase15_bootstrap.py app/db/schema.py app/db/repositories.py tests/db/test_phase15_bootstrap_schema.py
git diff --cached --check
git commit -m "feat: add durable telegram callback state"
```

---

### Task 2: Replace oversized and process-only AWG3 callbacks

**Criticality:** Critical — self-service must survive restart and obey Telegram's 64-byte callback limit.

**Files:**

- Create: `app/services/telegram_callback_state.py`
- Modify: `app/services/self_service_issuance.py`
- Modify: `app/bot/workflows.py`
- Modify: `app/bot/handlers.py`
- Modify: `app/bot/main.py`
- Modify: `tests/services/test_self_service_issuance.py`
- Modify: `tests/bot/test_bot_workflows.py`
- Modify: `tests/bot/test_bot_handlers.py`
- Modify: `tests/bot/test_app_bootstrap.py`

- [ ] **Step 1: Write callback grammar and restart REDs**

Require exact wire grammar:

```text
a3s:<opaque-handle>
a3c:<opaque-token>
```

Every encoded callback must be at most 64 UTF-8 bytes. Handle/token entropy must be at least 128 bits. Selection TTL is 15 minutes; confirmation TTL is 5 minutes.

Test that selection state contains exact owner, passport, platform/application/version/build and request fingerprint; confirmation state links to the selection digest; fresh workflow/service instances can complete the same valid request; wrong owner neither reveals nor consumes; expired/invalid/blocked terminal states consume only the owner's state; transient failure preserves until TTL; success consumes exactly once; duplicate callback never calls issuer twice.

- [ ] **Step 2: Run the RED**

```powershell
py -m pytest -q tests/services/test_self_service_issuance.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_app_bootstrap.py -k "awg3 or callback or confirmation or restart"
```

Expected: failures expose `awg3:select`, `awg3:confirm`, `_pending`, and `_awg3_pending_requests` process-only behavior.

- [ ] **Step 3: Implement the durable callback service**

`TelegramCallbackStateService` must generate URL-safe opaque values using `secrets.token_urlsafe(16)` or stronger, persist only SHA-256 digests, validate exact purpose/owner/TTL, and return structured state from the repository. It must never serialize client identity into callback data.

Remove `SelfServiceIssuanceService._pending` and `BotWorkflow._awg3_pending_requests`. Inject the durable service into both layers. Keep issuance authority in `SelfServiceIssuanceService`; `BotWorkflow` remains only a presentation adapter.

Change handlers and dispatcher filters to the exact short prefixes. Keep private-chat checks, two-message config/QR delivery order, and AWG2 behavior unchanged.

- [ ] **Step 4: Run GREEN and callback mutation checks**

```powershell
py -m pytest -q tests/services/test_self_service_issuance.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_app_bootstrap.py
py -m pytest -q tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py
git diff --check
```

Temporarily mutation-check each critical regression by restoring an old long prefix or in-memory lookup; the relevant test must fail. Revert mutations before staging.

- [ ] **Step 5: Review and commit**

```powershell
git status --short
git add app/services/telegram_callback_state.py app/services/self_service_issuance.py app/bot/workflows.py app/bot/handlers.py app/bot/main.py tests/services/test_self_service_issuance.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_app_bootstrap.py
git diff --cached --check
git commit -m "fix: make awg3 callbacks durable and bounded"
```

---

### Task 3: Lock the Python 3.12 runtime and Starlette/httpx2 test toolchain

**Criticality:** Critical — package acceptance cannot rely on the current incidental Python 3.14/httpx fallback environment.

**Files:**

- Modify: `pyproject.toml`
- Create: `requirements/phase15-runtime-py312.lock`
- Create: `requirements/phase15-test-py312.lock`
- Create: `scripts/phase15_dependency_lock.py`
- Create: `tests/test_phase15_dependencies.py`

- [ ] **Step 1: Write dependency-contract REDs**

Test that:

- project Python range remains `>=3.12,<3.13`;
- dev dependencies use `httpx2==2.10.0` and no direct `httpx` fallback;
- runtime and test locks contain exact versions and hashes for every artifact;
- lock headers record Python 3.12, platform policy and generation command;
- the generator emits deterministic LF/UTF-8 output and rejects Python other than 3.12;
- no floating URL or un-hashed requirement is accepted.

- [ ] **Step 2: Run RED**

```powershell
py -m pytest -q tests/test_phase15_dependencies.py
```

- [ ] **Step 3: Implement the lock generator and generate under Python 3.12**

Use a discovered Python 3.12 executable and an isolated temporary virtual environment. Resolve only from the approved package index, pin `httpx2==2.10.0`, and write hashes into both lock files. Do not use Python 3.14 output as acceptance evidence.

```powershell
py -3.12 scripts/phase15_dependency_lock.py --runtime requirements/phase15-runtime-py312.lock --test requirements/phase15-test-py312.lock
py -3.12 -m venv .venv-phase15-verify
.venv-phase15-verify\Scripts\python.exe -m pip install --require-hashes -r requirements/phase15-test-py312.lock
```

If Python 3.12 or an exact hash is unavailable, STOP; do not relax versions/hashes.

- [ ] **Step 4: Verify Starlette TestClient uses httpx2 without warning**

```powershell
.venv-phase15-verify\Scripts\python.exe -m pytest -q tests/web/test_device_passports.py tests/web/test_users.py -W error
.venv-phase15-verify\Scripts\python.exe -m pytest -q tests/test_phase15_dependencies.py
git diff --check
```

Expected: no Starlette/httpx2 deprecation warning.

- [ ] **Step 5: Review and commit**

```powershell
git add pyproject.toml requirements/phase15-runtime-py312.lock requirements/phase15-test-py312.lock scripts/phase15_dependency_lock.py tests/test_phase15_dependencies.py
git diff --cached --check
git commit -m "build: lock phase15 python312 dependencies"
```

---

### Task 4: Add the fail-closed production AWG3 composition root

**Criticality:** Critical — Phase 14 adapters are intentionally dependency-injected and not yet production-wired.

**Files:**

- Create: `app/services/phase15_bootstrap.py`
- Modify: `app/config/settings.py`
- Modify: `app/main.py`
- Modify: `app/bot/main.py`
- Modify: `tests/config/test_settings.py`
- Modify: `tests/bot/test_app_bootstrap.py`
- Create: `tests/services/test_phase15_bootstrap.py`

- [ ] **Step 1: Write composition and fail-closed REDs**

Test explicit construction of:

- `Repository` plus durable `TelegramCallbackStateService`;
- fresh runtime/evidence/exact-build providers;
- `Awg3ControlService` and `ProtocolAdmissionService`;
- `SelfServiceIssuanceService` and `AdminConfigIssuanceService`;
- production `ConfigIssuer` boundary and delivery builder;
- AWG3 bot handlers registered in `create_dispatcher()`.

Settings must represent provider paths/identities and an explicit AWG3 bootstrap enable flag, default false. Missing/invalid provider, runtime, evidence, exact build, global acceptance or issuer configuration must block AWG3 while AWG2 workflow creation and issuance remain available. Startup must not call issuer, SSH, remote observation or peer mutation.

- [ ] **Step 2: Run RED**

```powershell
py -m pytest -q tests/services/test_phase15_bootstrap.py tests/bot/test_app_bootstrap.py tests/config/test_settings.py
```

- [ ] **Step 3: Implement one composition root**

Expose `build_phase15_awg3_components(settings, repo, access_service, peer_applier)` returning a typed immutable component bundle. Reuse existing Phase 14 services and repository state; do not create a second admission/control implementation.

The real issuer adapter must wrap the existing production `AccessService`/peer application boundary, use the preallocated passport and exact build lineage, and be callable only after fresh admission/control checks. No synthetic issuer is allowed in `app/`; synthetic implementations remain tests only.

Inject the bundle into `create_workflow()` and register handlers even when disabled so requests fail with a safe unavailable result rather than an exception. Record only secret-safe structured audit metadata.

Add an interface for future admin-only health events (`server_unreachable`, `awg2_degraded`, `awg3_degraded`) without scheduler, polling, messages or delivery activation.

- [ ] **Step 4: Run GREEN and bootstrap safety checks**

```powershell
py -m pytest -q tests/services/test_phase15_bootstrap.py tests/bot/test_app_bootstrap.py tests/config/test_settings.py tests/services/test_protocol_admission.py tests/services/test_self_service_issuance.py tests/services/test_admin_config_issuance.py
py -m pytest -q tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py
git diff --check
```

- [ ] **Step 5: Review and commit**

```powershell
git add app/services/phase15_bootstrap.py app/config/settings.py app/main.py app/bot/main.py tests/config/test_settings.py tests/bot/test_app_bootstrap.py tests/services/test_phase15_bootstrap.py
git diff --cached --check
git commit -m "feat: wire fail closed awg3 production bootstrap"
```

---

### Task 5: Define the independent Phase 15 package and preflight contracts

**Criticality:** Very important — package identity and read-only behavior must be fixed before materialization.

**Working directory:** `C:\Users\SooL\Documents\VPS-OPS-LAB`

**Files:**

- Create: `packaging/phase15-dual-protocol-bootstrap-contract/package-manifest.schema.json`
- Create: `packaging/phase15-dual-protocol-bootstrap-contract/preflight-evidence.schema.json`
- Create: `packaging/phase15-dual-protocol-bootstrap-contract/failure-outcome.schema.json`
- Create: `packaging/phase15-dual-protocol-bootstrap-contract/resource-plan.json`
- Create: `scripts/phase15_dual_protocol_package.py`
- Create: `tests/test_phase15_dual_protocol_contracts.py`
- Create: `tests/test_phase15_dual_protocol_package.py`
- Create: `tests/fixtures/phase15_dual_protocol_package/source-tree/`

- [ ] **Step 1: Write contract and deterministic-package REDs**

The manifest schema must require package ID, source branch/head, Phase 14 receipt path/hash/commit, Phase 15 source receipt path/hash, runtime/test lock hashes, canonical relative path, byte size, SHA-256, role, mode, secret classification, gate and rollback role for every entry.

Reject duplicate/case-colliding paths, backslashes, absolute paths, traversal, unsorted entries, missing hashes, BOM/non-UTF-8 JSON, forbidden secret roles and any stale Phase 13 manifest/outcome/evidence.

`resource-plan.json` must reserve only the future contour: `awg3`, bridge `amn2sp3br0`, UDP `30002`, approved fixed AWG3 CIDRs, container/service/state paths. It must explicitly state that AWG2 resources are unchanged.

- [ ] **Step 2: Run RED**

```powershell
py -m pytest -q tests/test_phase15_dual_protocol_contracts.py tests/test_phase15_dual_protocol_package.py
```

- [ ] **Step 3: Implement canonical materializer/verifier**

`phase15_dual_protocol_package.py` must support:

```text
materialize --source-root --source-head --package-id --output-root
verify --package-root
```

Materialization uses `git archive` from the exact clean source HEAD, never the working tree. Include application snapshot, additive migrations, callback/bootstrap code, both dependency locks, future guarded stage envelopes, read-only collector/runner, schemas, verifier, resource plan and operator docs. Exclude `.git`, databases, backups, `.env`, keys, tokens, configs, QR, peers and caches.

Write deterministic UTF-8/LF JSON with sorted normalized paths. Refuse existing non-empty output, dirty/mismatched source, wrong receipt hash or unclassified file.

- [ ] **Step 4: Run GREEN and cross-check Phase 13 isolation**

```powershell
py -m pytest -q tests/test_phase15_dual_protocol_contracts.py tests/test_phase15_dual_protocol_package.py tests/test_phase13_awg3_preflight_contract.py
git diff --check
```

- [ ] **Step 5: Review and commit**

```powershell
git add packaging/phase15-dual-protocol-bootstrap-contract scripts/phase15_dual_protocol_package.py tests/test_phase15_dual_protocol_contracts.py tests/test_phase15_dual_protocol_package.py tests/fixtures/phase15_dual_protocol_package/source-tree
git diff --cached --check
git commit -m "feat: define phase15 package contract"
```

---

### Task 6: Build guarded stage envelopes and the read-only Spain collector

**Criticality:** Very important — tooling must be verifiably inert before any remote authorization.

**Files:**

- Create: `scripts/vps/phase15_application_stage_remote.sh`
- Create: `scripts/vps/phase15_awg3_runtime_stage_remote.sh`
- Create: `scripts/vps/phase15_spain_readonly_preflight_remote.sh`
- Create: `scripts/vps/phase15_spain_readonly_preflight_ssh_runner.ps1`
- Create: `scripts/phase15_preflight_contract.py`
- Create: `tests/test_phase15_stage_envelopes.py`
- Create: `tests/test_phase15_spain_readonly_preflight.py`
- Create: `tests/test_phase15_preflight_contract.py`
- Create: `tests/fixtures/phase15_spain_preflight/`

- [ ] **Step 1: Write inert-stage and read-only REDs**

Stage envelopes must refuse execution without a one-time checksum-bound claim, exact package identity, explicit future gate and expected current-state hash. They are packaged but never run in Phase 15.

Collector fixture tests must prove read-only inspection of OS/architecture, Python 3.12, disk space, backup capability, application/DB/service/container state, AWG2 health, Telegram prerequisites, firewall/routes and conflicts for `awg3`, `amn2sp3br0`, UDP `30002`, CIDRs and paths. It must also report incomplete Phase 14/15 recovery markers without changing them.

Reject mutating tokens including `systemctl restart|stop|start|enable`, `docker run|rm`, `podman run|rm`, `iptables -A|-D`, `nft add|delete`, `ip link add|delete|set`, `sqlite3`, `cp`, `mv`, `rm`, `chmod`, `chown`, output redirection and package installation.

- [ ] **Step 2: Run RED**

```powershell
py -m pytest -q tests/test_phase15_stage_envelopes.py tests/test_phase15_spain_readonly_preflight.py tests/test_phase15_preflight_contract.py
```

- [ ] **Step 3: Implement collectors, runner and evidence binding**

The remote collector emits exactly one UTF-8 JSON document to stdout and diagnostics to stderr. It must not persist a file remotely. The PowerShell runner must remain unusable without an explicit future claim file and must validate package ID, collector checksum, host identity and output schema before accepting evidence.

`phase15_preflight_contract.py` validates one-time claim lifecycle and binds evidence/failure outcome to package ID, package manifest hash, collector hash, expected host, start/end timestamps and transport disposition. Do not include secrets or raw command output containing credentials.

- [ ] **Step 4: Run GREEN and mutation-token audit**

```powershell
py -m pytest -q tests/test_phase15_stage_envelopes.py tests/test_phase15_spain_readonly_preflight.py tests/test_phase15_preflight_contract.py tests/test_phase13_awg3_readonly_preflight.py
rg -n "systemctl (restart|stop|start|enable)|docker (run|rm)|podman (run|rm)|iptables -(A|D)|nft (add|delete)|ip link (add|delete|set)|sqlite3 |chmod |chown |rm " scripts/vps/phase15_* tests/test_phase15_*
git diff --check
```

Only explicit denylist assertions may match.

- [ ] **Step 5: Review and commit**

```powershell
git add scripts/vps/phase15_application_stage_remote.sh scripts/vps/phase15_awg3_runtime_stage_remote.sh scripts/vps/phase15_spain_readonly_preflight_remote.sh scripts/vps/phase15_spain_readonly_preflight_ssh_runner.ps1 scripts/phase15_preflight_contract.py tests/test_phase15_stage_envelopes.py tests/test_phase15_spain_readonly_preflight.py tests/test_phase15_preflight_contract.py tests/fixtures/phase15_spain_preflight
git diff --cached --check
git commit -m "feat: add guarded phase15 preflight tooling"
```

---

### Task 7: Materialize and locally verify the checksum-bound package

**Criticality:** Very important — this creates the exact artifact for the later separate remote gate, still without transport or execution.

**Files:**

- Create: `packaging/phase15-dual-protocol-bootstrap-20260811-001/`
- Create: `research/amn2/phase15-source-readiness-receipt.md`
- Create: `research/amn2/phase15-package-readonly-preflight-readiness-receipt.md`

- [ ] **Step 1: Run final source verification before materialization**

From the Phase 15 source worktree:

```powershell
git status --short
git diff --check 36981d7afc1fcd9eb17386c62f70adf175d76263..HEAD
py -3.12 -m pytest -q
```

Require clean source and complete Python 3.12 pass. Create `phase15-source-readiness-receipt.md` with source head, all source task commits, focused/full results, dependency lock hashes and unchanged live booleans; commit only that receipt locally in VPS-OPS-LAB before materialization.

- [ ] **Step 2: Materialize once from exact committed source**

```powershell
$phase15SourceRoot = 'C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness'
$phase15SourceHead = git -C $phase15SourceRoot rev-parse HEAD
if ((git -C $phase15SourceRoot status --porcelain) -or -not $phase15SourceHead) { throw 'Phase 15 source must be committed and clean' }
py scripts/phase15_dual_protocol_package.py materialize --source-root $phase15SourceRoot --source-head $phase15SourceHead --package-id phase15-dual-protocol-bootstrap-20260811-001 --output-root packaging/phase15-dual-protocol-bootstrap-20260811-001
```

The materializer must record the resolved 40-character `$phase15SourceHead`; a symbolic branch name is never accepted as package identity.

- [ ] **Step 3: Verify package twice without mutation**

```powershell
py scripts/phase15_dual_protocol_package.py verify --package-root packaging/phase15-dual-protocol-bootstrap-20260811-001
py -m pytest -q tests/test_phase15_dual_protocol_contracts.py tests/test_phase15_dual_protocol_package.py tests/test_phase15_stage_envelopes.py tests/test_phase15_spain_readonly_preflight.py tests/test_phase15_preflight_contract.py
Get-ChildItem packaging/phase15-dual-protocol-bootstrap-20260811-001 -Recurse -File | Get-FileHash -Algorithm SHA256
```

Then rerun verifier and confirm the manifest/package hashes are unchanged.

- [ ] **Step 4: Perform secret and scope review**

Scan added package bytes for PEM headers, WireGuard config syntax, `PrivateKey`, `PresharedKey`, `vpn://`, Telegram tokens, passwords, `.env`, SQLite database headers, QR/PNG signatures and unexpected binary files. Classify every remaining generic token literal as synthetic test data or STOP.

- [ ] **Step 5: Write receipts and commit materialized package**

`phase15-package-readonly-preflight-readiness-receipt.md` records exact source/package/manifest/lock/collector hashes, test evidence, resource plan and the approved booleans. It must say explicitly that remote preflight, SSH, stage, issuance and live mutation did not occur.

```powershell
git add packaging/phase15-dual-protocol-bootstrap-20260811-001 research/amn2/phase15-source-readiness-receipt.md research/amn2/phase15-package-readonly-preflight-readiness-receipt.md
git diff --cached --check
git commit -m "build: materialize phase15 readiness package"
```

---

### Task 8: Independent reviews, final verification and remote-gate handoff

**Criticality:** Important — proves readiness and stops before the first remote decision.

**Files:**

- Modify only if evidence changed: `research/amn2/phase15-source-readiness-receipt.md`
- Modify only if evidence changed: `research/amn2/phase15-package-readonly-preflight-readiness-receipt.md`

- [ ] **Step 1: Run independent source reviews**

Dispatch fresh read-only reviewers for:

1. spec compliance against the approved Phase 15 design;
2. code quality/concurrency/migration/restart safety;
3. security/secret handling of callback, bootstrap and issuer boundaries;
4. whole-branch review from `36981d7...` to exact Phase 15 HEAD.

Any Critical or Important finding is a STOP and requires a scoped fix round plus fresh review.

- [ ] **Step 2: Run final source verification after review PASS**

```powershell
py -3.12 -m pytest -q tests/db/test_phase15_bootstrap_schema.py tests/services/test_self_service_issuance.py tests/services/test_phase15_bootstrap.py tests/bot/test_bot_workflows.py tests/bot/test_bot_handlers.py tests/bot/test_app_bootstrap.py tests/config/test_settings.py tests/test_phase15_dependencies.py
py -3.12 -m pytest -q
git status --short
git diff --check 36981d7afc1fcd9eb17386c62f70adf175d76263..HEAD
```

- [ ] **Step 3: Run final VPS tooling verification**

```powershell
py -m pytest -q tests/test_phase15_dual_protocol_contracts.py tests/test_phase15_dual_protocol_package.py tests/test_phase15_stage_envelopes.py tests/test_phase15_spain_readonly_preflight.py tests/test_phase15_preflight_contract.py
py -m pytest -q
py scripts/phase15_dual_protocol_package.py verify --package-root packaging/phase15-dual-protocol-bootstrap-20260811-001
git status --short
git diff --check
```

- [ ] **Step 4: Read back receipt identity**

```powershell
git rev-parse HEAD
git log -1 --oneline
Get-FileHash -Algorithm SHA256 research/amn2/phase15-source-readiness-receipt.md
Get-FileHash -Algorithm SHA256 research/amn2/phase15-package-readonly-preflight-readiness-receipt.md
```

Confirm the two receipt files are the only receipt changes and their embedded hashes/SHAs match the current committed state.

- [ ] **Step 5: Stop and prepare one exact next `/GO`**

The next command may authorize only the Spain read-only preflight against the checksum-bound Phase 15 package. It must name exact source SHA, package commit SHA, manifest SHA-256, collector SHA-256 and receipt SHA-256. It must continue to forbid stage, deploy, issuance, service/firewall/runtime/client mutation and push.

Do not run that command as part of Phase 15.

## Boundary after this plan

At successful completion, the application can understand AWG2/AWG3, survive Telegram callback restarts, enforce exact AWG3 admission before every issuer call, and construct the production dependency graph without enabling live AWG3. A deterministic Phase 15 package and read-only Spain preflight tooling exist and pass local verification. No remote host has been contacted or changed. The next phase/gate begins with checksum-bound Spain read-only preflight and exact client acceptance evidence, not with rollout.
