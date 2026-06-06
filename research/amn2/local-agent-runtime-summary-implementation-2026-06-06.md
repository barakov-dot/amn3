# Local Agent Runtime Summary Implementation Evidence

Date: 2026-06-06.

Status: merged into AMN2 stable branch, local-only mapper slice.

## AMN2 Branch

```text
branch: codex/local-agent-runtime-summary
remote: amn2/codex/local-agent-runtime-summary
head: c8a6363 Add Local Agent runtime summary mapper
base: 32d01fd Update integration status for controlled prod
stable branch: codex-vps-test-prep
stable head after fast-forward: c8a6363 Add Local Agent runtime summary mapper
worktree: C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-local-agent-runtime-summary
```

## Scope

```text
pure mapper/service only
new file: app/agent/runtime_summary.py
new test file: tests/agent/test_runtime_summary.py
no API route
no web route
no CLI command
no package change
no VPS commands
no live write operation
```

## TDD Evidence

RED:

```text
python -m pytest tests/agent/test_runtime_summary.py -q
result: 1 collection error
expected error: ModuleNotFoundError: No module named 'app.agent.runtime_summary'
```

GREEN focused:

```text
python -m pytest tests/agent/test_runtime_summary.py -q
result: 3 passed in 0.03s
```

Adjacent regression before stable fast-forward:

```text
python -m pytest tests/agent/test_runtime_summary.py tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
result: 37 passed, 1 warning in 1.81s
warning: StarletteDeprecationWarning from fastapi/starlette testclient
```

Adjacent regression before stable push:

```text
python -m pytest tests/agent/test_runtime_summary.py tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
result: 37 passed, 1 warning in 1.79s
warning: StarletteDeprecationWarning from fastapi/starlette testclient
```

Full suite before stable push:

```text
python -m pytest -q
result: 619 passed, 1 warning in 63.89s
warning: StarletteDeprecationWarning from fastapi/starlette testclient
```

Baseline adjacent check before edits:

```text
python -m pytest tests/agent/test_runtime.py tests/agent/test_api.py tests/agent/test_policy.py tests/security/test_surface_policy_bindings.py -q
result: 34 passed, 1 warning in 2.86s
note: a pytest temp cleanup PermissionError appeared after exit 0; later runs used a worktree-local TMP/TEMP path.
```

## Hygiene

```text
git diff --check: exit 0
secret marker scan on changed AMN2 files: exit 1, no matches
AMN2 feature worktree status after push: clean, tracking amn2/codex/local-agent-runtime-summary
AMN2 stable checkout after fast-forward/push: clean, tracking amn2/codex-vps-test-prep
```

Secret marker scan pattern:

```text
ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|Authorization: Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|vpn://[A-Za-z0-9:/?&=._%-]{20,}
```

## Safety Boundary

This branch does not unlock:

```text
controlled-prod-ready
public web/API exposure
config:read
/api/clients write CRUD
Local Agent clients/configs/write routes
backup/import/reboot
VPS_APPLY_ENABLED=true
apply-peer --apply
revoke-peer --apply
config delivery
```

No `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR payloads, VPN URI payloads, or full logs were published.

## Decision

Result: `local-agent-runtime-summary-merged-stable-local-only`.

The branch was fast-forward merged into `codex-vps-test-prep` and pushed to `amn2`.

VPS status is unchanged: `32d01fd` remains the current VPS-smoked runtime/source baseline until a separate operator update/read-only smoke is performed for `c8a6363` or a later package. A VPS smoke is not required for the mapper-only code by itself unless it is combined with API route, web/admin runtime status, auth policy, packaging, smoke-script, or runtime behavior changes.
