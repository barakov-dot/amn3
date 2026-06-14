# AMN2 Fresh Installer Backlog

Дата: 2026-06-13.

Назначение: зафиксировать будущий путь к чистому установщику AMN2 через
вопрос-ответ, safe defaults, preflight, dry-run and named gates. Этот документ
не разрешает зачистку текущего VPS, установку на новый VPS, live SSH, package
apply, public exposure, config delivery, write API или production mutations.

## Current Baseline

```text
AMN2 branch: codex-vps-test-prep
AMN2 current head: 0de7a77 Polish fresh installer preflight planning
AMN2 latest VPS-smoked/package head: c46f664 Add public taxonomy cleanup checklist
AMN2 local-only after-smoke head: 0de7a77, not package-rebuilt/VPS-smoked
AMN3 latest evidence slice: P6-S004 Phase 6 closeout / next-chat / installer backlog grooming
current working VPS: 89.185.80.166, disposable test VPS, no destructive action authorized here
```

Relevant completed inputs:

- `P6-I007` local-only fresh-install wizard/bootstrap automation.
- `P6-C007` destructive cleanup/reinstall checklist-only boundary.
- `P6-C009` live update/smoke for `c46f664`, read-only smoke passed.
- `P6-X003` package runbook escaping hygiene guardrail.
- `P5-C004` secret handoff protocol.
- `P5-C005` source-overlay permission preservation.
- `FI-I001 + FI-I002 + FI-I003` fresh installer question schema, rendered plan
  and secret handoff binding in AMN2 `de635a0`.
- `FI-M001 + FI-M002 + FI-M003` fresh installer target preflight matrix,
  runtime decision and package hygiene planning in AMN2 `7416fb0`.
- `FI-N001 + FI-N002 + FI-S001` fresh installer smoke/evidence template,
  existing-server reconciliation input and operator docs index in AMN2 `525a9cd`.
- `P6-C001 + P6-C002` docs-only public/config gate checklist refresh in AMN2
  `ff77d4c`.
- `FI-X001 + current-head package preflight planning` Russian-first installer
  prompts and `fresh-install-package-preflight.v1` planning in AMN2 `0de7a77`.

## Backlog Status

All items below are candidates. None are active by default.

### Critical gated/deferred

- `FI-C001` Destructive clean install execution gate.
  Maps to `P6-C007`. Requires exact named destructive phrase, target decision,
  retention/data-loss acceptance, stop criteria, package choice, rollback story
  and second confirmation.

- `FI-C002` Public exposure cutover gate.
  Maps to `P6-C001`. Required before domain, HTTPS, reverse proxy, public web,
  public API or firewall/listener changes.

- `FI-C003` Config delivery enablement gate.
  Maps to `P6-C002`. Required before `.conf`, QR, `vpn://`, public token redeem,
  Telegram real config delivery or self-service download.

- `FI-C004` Write API/install mutation gate.
  Maps to `P6-C003`, Local Agent write/config routes and production peer/user
  mutation. Required before `/api/clients` CRUD, peer sync/apply/revoke,
  server config rewrite or automated live install changes.

- `FI-C005` Backup/restore/import gate.
  Maps to `P6-C004`. Required before archive import, restore apply, reboot,
  destructive migration or disaster recovery drill on a live target.

### Very important local-only

Completed:

- `FI-I001` Installer question model hardening.
  Extend the existing `P6-I007` wizard with explicit answer schema versions,
  validation groups and stop-line explanations. Completed in AMN2 `de635a0`.

- `FI-I002` Install plan renderer.
  Generate a redacted, operator-readable install plan from answers, including
  package choice, secrets needed through operator-local channel, expected
  listeners and smoke steps. Completed in AMN2 `de635a0`.

- `FI-I003` Secret handoff checklist binding.
  Bind the installer plan to `docs/AMN2_SECRET_HANDOFF_PROTOCOL.ru.md` so raw
  tokens, `.env`, `servers.yml`, client configs, QR and `vpn://` never enter
  AMN3 evidence. Completed in AMN2 `de635a0`.

### Important local-only

Completed:

- `FI-M001` Target OS/runtime preflight matrix.
  Define read-only checks for Ubuntu version, Python runtime, Docker, ports,
  disk, time sync and package prerequisites. Live execution requires a named
  read-only diagnostic gate. Completed in AMN2 `7416fb0`.

- `FI-M002` Runtime mode decision.
  Keep manual runtime vs systemd vs reverse proxy as an explicit answer. No
  service enable/restart by default. Completed in AMN2 `7416fb0`.

- `FI-M003` Package hygiene integration.
  Include `scripts/check_markdown_hygiene.py`, source zip checksum, forbidden
  source entries, shell LF/no-BOM and operator runbook checks in future package
  builds. Do not rewrite already-smoked evidence packages. Completed in AMN2
  `7416fb0`.

### Normal local-only

Completed:

- `FI-N001` Smoke/evidence template.
  Reuse read-only loopback smoke, auth/listener/audit summary, external closed
  probes and no-secret evidence review. Completed in AMN2 `525a9cd`.

- `FI-N002` Existing-server reconciliation input.
  Reuse report-only reconciliation before any clean install. No auto-fix,
  import, peer creation/removal or config overwrite. Completed in AMN2 `525a9cd`.

### Simple/cosmetic

Completed:

- `FI-S001` Installer docs index.
  Create a short operator index linking wizard, destructive checklist, secret
  handoff, package hygiene and smoke evidence rules. Completed in AMN2 `525a9cd`.

- `FI-X001` Russian-first prompt copy polish.
  Keep prompts short, direct and safe, while preserving stable technical IDs.
  Completed in AMN2 `0de7a77`.

## Recommended Order

1. Local package build/preflight for `0de7a77` if the operator wants a package
   candidate, without live apply/smoke.
2. A separate named live apply/smoke gate only if the operator wants to update
   the disposable VPS.
3. Only then consider `FI-C001` or other live/destructive named gates.

## Hard Stop Lines

Stop and require a separate named gate if any step would:

- run SSH or live VPS commands;
- upload/apply a package to a VPS;
- stop/restart/deploy services;
- open public `3030`, `3040`, `80`, `443`, domain, HTTPS or reverse proxy;
- emit `.conf`, QR, `vpn://`, config body or client secret;
- enable write API, Local Agent mutation, backup/import/reboot or peer/user
  mutation;
- delete, wipe, rebuild or reinstall a VPS;
- use Telegram tokens, live bot send or Telegram identity/profile mutation;
- publish secret-bearing evidence;
- copy upstream/GPL implementation code.
