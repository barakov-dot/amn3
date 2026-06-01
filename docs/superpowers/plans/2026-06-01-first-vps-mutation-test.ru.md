# First VPS Mutation Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Safely execute and document the first real `agent:clients:write` apply/revoke test on a VPS after `GO-1`.

**Architecture:** This is a VPS execution packet, not a local mutation. The test uses the already implemented Phase 1-4 stack: dedicated write settings, guarded endpoints, Local Agent peer adapter, controller client, and web admin preflight. The only accepted product flow is `dry-run -> confirmation -> apply/revoke -> audit -> rollback`, with `LOCAL_AGENT_WRITE_ENABLED=false -> true -> false` around a narrow test window.

**Tech Stack:** AMN3 on VPS, systemd, curl, bundled Python/pytest, FastAPI Local Agent, SQLite audit storage, web admin, existing redaction tooling.

---

## Scope And Gates

This is the code-ready packet for `Phase 5 - first VPS mutation test` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Run this only when all of these are true:

- `GO-1` is recorded from `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`;
- Phase 1 write settings are implemented and tested;
- Phase 2 Local Agent write endpoints are implemented and tested;
- Phase 3 controller client is implemented and tested;
- Phase 4 web admin preflight UX is implemented and tested;
- Local Agent is bound to `127.0.0.1:3031` only;
- public port `3031` is closed;
- rollback command was already checked in read-only smoke;
- the operator understands: do not paste secrets.

This packet introduces a stricter gate:

```text
GO-2 - first controlled VPS mutation test may start
```

`GO-2` requires:

- exact branch `codex/local-agent-production-wiring` deployed on the VPS;
- clean or explained `git status --short --branch`;
- `LOCAL_AGENT_WRITE_ENABLED=false -> true -> false` is possible without manual code edits;
- `LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH` exists and is readable only by the controller/web process owner;
- `LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write`;
- read-only token still has no `agent:clients:write`;
- test-only user/device/peer binding is available;
- rollback owner is present during the window.

`NO-GO` is mandatory if any of these is true:

- Local Agent is offline or public;
- write token is missing or shared in chat;
- read-only token can access write routes;
- web admin preview shows private key, PSK, QR, `vpn://`, or full client config;
- dry-run has no `rollback_reference`;
- audit event is not recorded;
- runtime state cannot be checked;
- revoke or rollback cannot be executed immediately.

## Secret Rules

Never paste into chat, issues, docs, screenshots, commit messages, or copied logs:

- raw token
- bearer token
- Authorization header value
- private key
- PSK
- QR
- `vpn://`
- full client config
- complete `.env`

Allowed evidence:

- commit hash;
- redacted command output;
- `peer_public_key_fingerprint`;
- `rollback_reference`;
- operation ids;
- status codes;
- redacted audit event metadata;
- final `Decision: go | no-go`.

## Required Documents

- `docs/AMN3_VPS_TEST_PACKET.ru.md`
- `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`
- `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md`
- `docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md`

## Route Contract Under Test

```text
POST /agent/clients/dry-run
POST /agent/clients
DELETE /agent/clients/{id}
```

The web admin labels for the same flow are `Preview peer apply`, `Confirm apply`, and `Revoke peer`.

## Task 1: VPS Evidence Intake

**Files:**
- Verify: `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md`
- Verify: `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`

- [ ] **Step 1: Confirm deployed branch and commit**

Run on VPS:

```bash
cd /opt/amn2
git fetch origin codex/local-agent-production-wiring
git status --short --branch
git log -1 --oneline --decorate
git remote -v
```

Expected:

```text
branch contains origin/codex/local-agent-production-wiring
working tree clean or every local change explained
commit matches the pushed AMN3 branch
```

- [ ] **Step 2: Confirm Local Agent read-only status**

Run on VPS:

```bash
cd /opt/amn2
sudo systemctl status amneziya-agent --no-pager
ss -lntp | grep ':3031'
python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Expected:

```text
Local Agent status: online | degraded with explained non-mutation reason
Bind check: 127.0.0.1:3031 only
raw token absent from output
private key / PSK / QR / vpn:// absent from output
```

- [ ] **Step 3: Confirm Phase 1-4 tests are green on VPS**

Run on VPS:

```bash
cd /opt/amn2
./venv/bin/python -m pytest tests/agent/test_policy.py tests/agent/test_api.py tests/agent/test_client.py tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py -v
```

Expected:

```text
all selected tests pass
no warnings reveal raw token, private key, PSK, QR, vpn://, or full client config
```

- [ ] **Step 4: Record GO-2 or stop**

Fill this local decision block in the working notes before continuing:

```text
GO-2 decision before mutation:
Decision: go | no-go
Reason:
Commit:
Operator:
Rollback owner:
```

If decision is `no-go`, stop. Do not run mutation commands.

## Task 2: Narrow Write Window

**Files:**
- Verify: `.env` on VPS
- Verify: systemd service override on VPS
- Verify: `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md`

- [ ] **Step 1: Confirm write token boundary**

Run on VPS without printing token values:

```bash
cd /opt/amn2
grep -n 'LOCAL_AGENT_WRITE_ENABLED\|LOCAL_AGENT_WRITE_TOKEN_SCOPES\|LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH' .env
test -s "$(grep '^LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH=' .env | cut -d= -f2-)"
```

Expected:

```text
LOCAL_AGENT_WRITE_ENABLED=false before the window
LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write
LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH exists
no raw token is printed
```

- [ ] **Step 2: Enable write mode only for the test window**

Run on VPS:

```bash
cd /opt/amn2
cp .env ".env.before-first-vps-mutation.$(date +%Y%m%d%H%M%S)"
perl -0pi -e 's/^LOCAL_AGENT_WRITE_ENABLED=.*/LOCAL_AGENT_WRITE_ENABLED=true/m' .env
grep -n '^LOCAL_AGENT_WRITE_ENABLED=' .env
sudo systemctl restart amneziya-agent
sudo systemctl restart amneziya-web
```

Expected:

```text
LOCAL_AGENT_WRITE_ENABLED=true
Local Agent restarted
web admin restarted
```

- [ ] **Step 3: Confirm read-only token cannot write**

Run on VPS with a read-only token held only in memory:

```bash
read -rsp "Local Agent read-only token: " LOCAL_AGENT_READ_TOKEN; echo
curl -fsS -o /tmp/amn3-readonly-write-check.json -w "%{http_code}\n" \
  -H "Authorization: Bearer $LOCAL_AGENT_READ_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  --data '{"client_id":"amn3-vps-mutation-test","peer_public_key":"test-peer-public","preshared_key":"test-psk","vpn_ip":"10.8.255.2","protocol":"amneziawg"}' \
  http://127.0.0.1:3031/agent/clients/dry-run
unset LOCAL_AGENT_READ_TOKEN
cat /tmp/amn3-readonly-write-check.json
```

Expected:

```text
HTTP 403
missing_scope
no raw token in output
```

If read-only token is accepted for write, stop and set `Decision: no-go`.

## Task 3: Create Test-Only Identity

**Files:**
- Verify: application SQLite database on VPS
- Verify: web admin server detail page

- [ ] **Step 1: Create or select a test-only user/device/peer binding**

Use web admin or a dedicated local admin script to create a record that is clearly disposable:

```text
user label: amn3-vps-mutation-test
device label: amn3-vps-mutation-test-device
server alias: current VPS alias
client_id: amn3-vps-mutation-test-client
protocol: amneziawg
vpn_ip: a free test address in the configured VPN network
```

Expected:

```text
test-only user/device/peer binding exists
no production user is selected
no full client config is copied into the test notes
```

- [ ] **Step 2: Record safe identity evidence**

Record only:

```text
server_alias:
user_id:
device_id:
device_label:
client_id:
peer_public_key_fingerprint:
vpn_ip:
```

Do not record raw private key, PSK, QR, `vpn://`, or full client config.

## Task 4: Dry-Run And Confirmation

**Files:**
- Verify: `app/agent/write_confirmation.py`
- Verify: `app/web/local_agent_actions.py`
- Verify: `app/web/templates/server_detail.html`

- [ ] **Step 1: Probe before dry-run**

Run:

```bash
cd /opt/amn2
python -m app.cli agent probe --base-url http://127.0.0.1:3031
```

Expected:

```text
status online or explained degraded
raw token absent
private key / PSK / QR / vpn:// absent
```

- [ ] **Step 2: Run API dry-run with write token**

Run on VPS:

```bash
read -rsp "Local Agent write token: " LOCAL_AGENT_WRITE_TOKEN; echo
curl -fsS -H "Authorization: Bearer $LOCAL_AGENT_WRITE_TOKEN" http://127.0.0.1:3031/agent/clients/dry-run \
  -H "Content-Type: application/json" \
  -X POST \
  --data '{"client_id":"amn3-vps-mutation-test-client","peer_public_key":"test-peer-public","preshared_key":"test-psk","vpn_ip":"10.8.255.2","protocol":"amneziawg","actor_surface":"manual_vps","actor_id":"operator","server_alias":"test-vps"}' \
  | tee /tmp/amn3-first-mutation-dry-run.redacted.json
unset LOCAL_AGENT_WRITE_TOKEN
```

Expected:

```text
operation_id: local_agent.clients.apply.dry_run
status: planned
dry_run: true
risk_class: state-write
preflight_id present
rollback_reference present if runtime adapter can provide it
peer_public_key_fingerprint present
raw token absent
private key / PSK / QR / vpn:// / full client config absent
```

- [ ] **Step 3: Run web admin preview**

In web admin server detail, click:

```text
Preview peer apply
```

Expected:

```text
planned_commands visible
risk_class visible
peer_public_key_fingerprint visible
confirmation nonce field visible
Confirm apply visible
raw token absent
private key / PSK / QR / vpn:// / full client config absent
```

If web preview differs from API dry-run in a safety-relevant way, stop and set `Decision: no-go`.

## Task 5: Apply And Runtime State Check

**Files:**
- Verify: Local Agent write endpoint
- Verify: web admin action log
- Verify: runtime peer state on VPS

- [ ] **Step 1: Confirm apply through web admin**

In web admin server detail, enter the confirmation nonce and click:

```text
Confirm apply
```

Expected:

```text
operation_id: local_agent.clients.apply
status: applied
audit event recorded
rollback_reference recorded
peer_public_key_fingerprint recorded
raw token absent from UI
private key / PSK / QR / vpn:// absent from UI
```

- [ ] **Step 2: Confirm runtime state**

Run on VPS:

```bash
cd /opt/amn2
sudo awg show || true
sudo wg show || true
bash deploy/runtime/collect_debug_snapshot.sh
```

Expected:

```text
runtime state contains the test peer fingerprint or expected redacted equivalent
production peers unchanged
snapshot collected
no private key / PSK / QR / vpn:// / full client config in copied evidence
```

- [ ] **Step 3: Confirm audit event**

Run a safe audit query that returns only redacted metadata:

```bash
cd /opt/amn2
./venv/bin/python -m app.cli audit recent --operation local_agent.clients.apply --limit 5
```

Expected:

```text
audit event exists
operation_id local_agent.clients.apply
result_state success | applied
peer_public_key_fingerprint present
rollback_reference present
raw token absent
private key / PSK / QR / vpn:// absent
```

If CLI audit command is not yet available, query through the repository helper created by the audit storage plan and include only redacted fields.

## Task 6: Revoke Or Rollback

**Files:**
- Verify: Local Agent revoke endpoint
- Verify: rollback command path
- Verify: runtime state after cleanup

- [ ] **Step 1: Preview revoke**

In web admin server detail, click:

```text
Revoke peer
```

Expected:

```text
operation_id: local_agent.clients.revoke.dry_run
planned_commands visible
rollback_reference visible
peer_public_key_fingerprint visible
raw token absent
private key / PSK / QR / vpn:// absent
```

- [ ] **Step 2: Confirm revoke**

Enter confirmation nonce and confirm revoke.

Expected:

```text
operation_id: local_agent.clients.revoke
status: revoked
audit event recorded
runtime peer removed or disabled
```

- [ ] **Step 3: Use rollback if revoke fails**

If revoke fails, run the recorded rollback command or disable write mode and restore the previous config:

```bash
cd /opt/amn2
perl -0pi -e 's/^LOCAL_AGENT_WRITE_ENABLED=.*/LOCAL_AGENT_WRITE_ENABLED=false/m' .env
sudo systemctl restart amneziya-agent
sudo systemctl restart amneziya-web
```

Expected:

```text
revoke or rollback completed
LOCAL_AGENT_WRITE_ENABLED=false
test peer no longer active
```

## Task 7: Secret Scan And Result Summary

**Files:**
- Modify: `docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md` only through safe copied summary
- Verify: `tests/security/test_redaction.py`

- [ ] **Step 1: Collect logs**

Run:

```bash
journalctl -u amneziya-agent -n 200 --no-pager
journalctl -u amneziya-web -n 200 --no-pager
tail -n 300 /opt/amn2/logs/app.log
bash deploy/runtime/collect_debug_snapshot.sh
```

Expected:

```text
logs collected
raw token absent
private key absent
PSK absent
QR absent
vpn:// absent
full client config absent
```

- [ ] **Step 2: Fill final safe summary**

Use this block:

```text
First VPS mutation test summary:
Commit observed:
GO-2 before mutation: go | no-go
LOCAL_AGENT_WRITE_ENABLED window: false -> true -> false
Test-only user/device/peer binding: yes | no
Dry-run status:
Apply status:
Runtime state check:
Audit event:
Revoke status:
Rollback used: yes | no
Secret leakage observed: no | yes
raw token leakage observed: no | yes
private key / PSK / QR / vpn:// leakage observed: no | yes
full client config leakage observed: no | yes
Decision: go | no-go
Required follow-ups:
```

- [ ] **Step 3: Final local verification after copying the safe summary**

Run locally before committing any filled summary:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/security/test_redaction.py tests/deploy/test_runtime_registry.py -v
git diff --check
```

Expected:

```text
tests pass
git diff --check has no output
summary contains no raw token, private key, PSK, QR, vpn://, or full client config
```
