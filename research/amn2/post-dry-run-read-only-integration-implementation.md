# Post Dry-Run Read-Only Integration Implementation

Date: 2026-06-04.

Production repo: `C:\Users\SooL\Documents\Amneziya`

Implementation worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-post-dry-run-read-only
```

Branch:

```text
codex/post-dry-run-read-only-integration
```

Base:

```text
amn2/codex-vps-test-prep -> 708c98e Merge pull request #7 from barakov-dot/codex/remote-operation-vps-gate-prep
```

Commit:

```text
55a7ed6 Add post dry-run integration status
```

## Decision

Real VPS Phase 1 is fixed as `dry-run-only-pass`. Phase 2 live single test peer apply/revoke was not run and remains blocked until a separate operator confirmation in a new chat/gate.

This implementation adds only read-only integration status visibility:

- `GET /api/integration/status` under `server:read`;
- web-admin `/integration-status`;
- shared local `app.services.integration_status` service;
- route policy and route binding coverage;
- API token policy documentation.

## Safety Boundary

No live VPS write behavior was added. The slice does not add `/api/clients`, `config:read`, public/self-service config delivery, Local Agent mutations, SSH writes, Docker writes, peer apply/revoke, backup/import/reboot routes, detailed per-peer metrics, config artifacts, QR payloads or `vpn://` output.

The status payload reports:

- stable head `708c98e`;
- historical API/web baseline `294803e`;
- remote-operation candidate `7281254`;
- Phase 1 `dry_run_only_pass`;
- Phase 2 `not_run`;
- write routes and remote writes disabled.

## Verification

Focused baseline before changes:

```text
python -m pytest tests/api/test_app.py tests/web/test_api_readiness.py tests/web/test_api_tokens.py tests/security/test_surface_policy_bindings.py -q
result: 19 passed, 1 StarletteDeprecationWarning
```

Focused slice verification:

```text
python -m pytest tests/services/test_integration_status_service.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py -q
result: 31 passed, 1 StarletteDeprecationWarning
```

Full local verification:

```text
python -m pytest -q -p no:cacheprovider --basetemp tmp/pytest-post-dry-run-read-only
result: 610 passed, 1 StarletteDeprecationWarning
```

Note: the first full-suite attempt used `--basetemp tmp/pytest-post-dry-run-read-only` before creating parent `tmp/`, so pytest produced setup `FileNotFoundError` noise. After creating ignored `tmp/`, the full suite passed.

## Secret Review

No `.env`, raw tokens, bearer headers, token hashes, private keys, PSK, config bodies, QR payloads, `vpn://`, SSH command output, server hostnames, peer public keys, peer IPs or per-peer traffic were published in this evidence.

## Next Gate

Recommended next step: keep Phase 2 in a new chat. That chat should start from this state, require a separate operator confirmation, and prepare a dedicated disposable test peer plus rollback checklist before any live `apply-peer --apply` or `revoke-peer --apply`.
