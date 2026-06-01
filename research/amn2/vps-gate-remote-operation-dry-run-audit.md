# `amn2` Remote Operation VPS Gate: dry-run/audit candidate

Дата: 2026-06-01.

Назначение: подготовить controlled real VPS verification gate для remote-operation dry-run/audit stack после verified amn2 live baseline.

Этот документ не является разрешением на live mutation. Он фиксирует, что уже подготовлено локально, какие команды запускать на реальном VPS, где остановиться перед `--apply`, какие результаты считать успешными и какую evidence вернуть в AMN3.

## Candidate branch

Production repo:

```text
C:\Users\SooL\Documents\Amneziya
https://github.com/barakov-dot/amn2.git
```

Candidate branch:

```text
codex/remote-operation-vps-gate-prep
```

Base branch/head:

```text
codex-vps-test-prep
1fdcde5 Add scoped API token storage contract
```

Candidate head after local preparation:

```text
aca6663 Add VPS gate handoff for remote ops
```

Included remote-operation commits:

```text
c249bd0 Add state-changing operation metadata
8af6b5e Add remote partial failure model
b7a12ca Add remote operation dry-run metadata
50be810 Document remote operation local gate
aca6663 Add VPS gate handoff for remote ops
```

Why this candidate exists: the older `codex/remote-operation-dry-run-audit` branch diverged from `codex-vps-test-prep` at `91aeb3e`. The VPS test must use a fresh branch on top of the current verified transfer head `1fdcde5`, not the stale branch.

## Local verification

Worktree used:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-vps-gate-prep
```

Focused gate:

```text
tests\server\test_operation_runner.py
tests\server\test_peer_apply.py
tests\security\test_redaction.py
tests\web\test_servers.py
tests\web\test_users.py
result: 79 passed, 1 StarletteDeprecationWarning
```

Runtime registry docs:

```text
tests\deploy\test_runtime_registry.py
result: 7 passed
```

Full local suite:

```text
551 passed, 1 StarletteDeprecationWarning
```

Note: the first Windows worktree run failed because `tmp\...` did not exist for `--basetemp`; after creating local `tmp` and disabling pytest cache, the same candidate passed. This was an execution-environment issue, not a code regression.

## Scope

Allowed in the real VPS gate:

- fetch/switch the candidate branch on the VPS;
- run local tests only if the VPS has the expected Python environment;
- run read-only `check-network`, `preflight`, `check`, `collect-traffic --dry-run`;
- run `apply-peer --dry-run` and `revoke-peer --dry-run` for one dedicated test peer;
- stop and record evidence before any live `--apply`.

Allowed only after separate operator confirmation:

- one dedicated test peer `apply-peer --apply`;
- one matching `revoke-peer --apply`;
- `sync-peers` after apply/revoke to confirm live state.

Not allowed in this gate:

- using a production user's real device as the test object;
- broad API integration;
- copying KYORESUAS/PRVTPRO code;
- public/self-service config links;
- backup/import/reboot flows;
- raw config editing;
- live VPS changes from the lab chat without the operator intentionally entering the VPS gate.

## Companion documents

Use these AMN3 notes together with this runbook:

- `research/amn2/vps-gate-evidence-checklist.md` - short pass/fail checklist for the actual VPS evidence.
- `research/amn2/post-vps-gate-merge-decision.md` - merge/PR decision rules after the gate.
- `research/amn2/docker-manager-design-note.md` - safety contract for future Docker manager implementation.
- `research/amn2/neighbor-chat-vps-gate-handoff.md` - what KYORESUAS/PRVTPRO chats may do after evidence.

## Preconditions

Before entering the real VPS gate:

- operator has a VPS maintenance window and recovery access;
- current production app state is known and recoverable;
- `servers.yml` server alias is known; examples below use `debian-vps-1`;
- database path is known; examples below use `data/amneziya.sqlite3`;
- runtime config path points to the persistent AmneziaWG config used by Docker;
- `VPS_APPLY_ENABLED=false` for read-only/dry-run phases;
- a dedicated test peer is prepared, with public key, PSK and VPN IP kept in operator notes outside AMN3;
- no secrets are pasted into AMN3 notes or GitHub comments.

## VPS setup commands

Run on the real VPS only after the operator explicitly starts the VPS gate:

```powershell
cd /opt/amn2
git fetch amn2
git switch codex/remote-operation-vps-gate-prep
git log -1 --oneline
```

Expected head:

```text
aca6663 Add VPS gate handoff for remote ops
```

If the VPS uses a virtual environment:

```powershell
source venv/bin/activate
python -m pip install -e .
```

Generate the existing retest bundle:

```powershell
python -m app.cli server retest-plan --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

## Phase 1: read-only and dry-run

These commands must not change the VPS state:

```powershell
python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run
python -m app.cli server check --config servers.yml --server debian-vps-1
python -m app.cli server collect-traffic --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3 --dry-run
```

Dry-run mutation previews:

```powershell
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --preshared-key TEST_PEER_PSK --vpn-ip TEST_VPN_IP --dry-run
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --dry-run
```

Expected dry-run evidence:

- output includes operation metadata: `operation_id`, `risk_class`, `consistency_status=dry-run`;
- output lists safe side effects and rollback/recovery note;
- output does not include raw PSK, private key, full config, raw command string or secret-bearing diagnostics;
- no peer is added or removed on the VPS.

Stop here and record evidence before any live mutation.

## Phase 2: optional single test peer apply/revoke

This phase requires separate operator confirmation after Phase 1 evidence is reviewed.

Use only a dedicated test peer/device:

```powershell
python -m app.cli server apply-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --preshared-key TEST_PEER_PSK --vpn-ip TEST_VPN_IP --apply
python -m app.cli server sync-peers --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
python -m app.cli server revoke-peer --config servers.yml --server debian-vps-1 --public-key TEST_PEER_PUBLIC_KEY --apply
python -m app.cli server sync-peers --config servers.yml --server debian-vps-1 --db data/amneziya.sqlite3
```

Expected live evidence:

- apply adds exactly one dedicated test peer;
- existing peers remain unchanged;
- sync sees the expected remote state after apply;
- revoke removes exactly that test peer;
- final sync no longer shows the test peer as active;
- all failures are redacted and include a recovery note.

If apply succeeds but revoke fails, do not continue with API/web/agent integration tests. Keep the test peer public key in operator notes, attempt the same `revoke-peer --apply` once after checking connectivity, then use the existing manual Amnezia/Docker recovery path for this test peer only.

## Evidence template

Fill this back into AMN3 after the real VPS gate:

```text
date/time:
operator:
VPS alias:
candidate branch:
candidate head:
server alias:
database path:
runtime:
Phase 1 commands run:
Phase 1 result:
dry-run apply output redacted:
dry-run revoke output redacted:
Phase 2 live apply/revoke run: yes/no
if yes, test peer public key suffix:
sync result after apply:
sync result after revoke:
final state:
secrets leaked in output: yes/no
rollback/recovery needed: yes/no
residual risks:
decision: verified-live / needs-fix / dry-run-only-pass
```

## Next decision after gate

If Phase 1 and optional Phase 2 pass, record VPS evidence in AMN3 and then decide whether to merge the candidate branch into `codex-vps-test-prep`.

Only after that should KYORESUAS/PRVTPRO-derived integration work move from reference material into the main project. The next likely safe integration slice is aggregate-only read-only metrics/API route shell based on `research/amn2/read-only-metrics-privacy-classification.md`, not write lifecycle API.
