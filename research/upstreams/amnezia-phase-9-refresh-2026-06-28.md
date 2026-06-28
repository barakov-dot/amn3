# Amnezia Phase 9 upstream refresh 2026-06-28

Дата: 2026-06-28.

Источник: Phase 9 automation aggregation input from `amnezia-weekly-upstream-refresh`
fallback/manual continuation.

Scope: docs-only / review-only upstream delta note. This note does not open
live VPS, SSH, config generation/delivery, peer creation, public exposure,
Telegram action, package apply, write API, backup/import/reboot or
secret-bearing output.

## Inputs

Fresh reports for these chain steps were not found locally:

- `prvtpro-weekly-upstream-refresh`;
- `weekly-kyoresuas-upstream-refresh`.

Amnezia refresh was continued manually from available upstream signals.

## Observed delta

`amnezia-client` received fresh commits after 2026-06-21:

- `9b8bfaa`: regression fixes vs `4.8.15.4`, including revoke/admin restore,
  client update and `nextAvailableServerName`;
- `d8b8590`: XRay validation audit for host/SNI/path validation, numeric
  limits and save validation;
- `203a092`: macOS network extension / codesigning packaging fixes;
- `0f68472`: unreleased version bump to `4.9.0.3`.

Latest published release remains `amnezia-client 4.8.19.0`.

`amneziawg-android` latest published release remains `2.0.1`.

No new commits after 2026-06-21 were found for:

- `DefaultVPN`;
- `amneziawg-android`;
- `amneziawg-apple`;
- `amneziawg-windows`.

## AMN2 interpretation

`SERVER1` / `Сервер 1` is reinforced as upstream/client display-name behavior,
not as a proven AMN2 generator defect. Phase 9 keeps canonical production
naming as `Neobyatnaya-AMNZ-N`; Android `Сервер 1` remains a documented
limitation with `manual rename` fallback until
`ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`.

The XRay validation audit is useful as a hardening pattern: validate
host/SNI/path/ranges before save/apply. For AMN2 this is a docs-only/local-test
checklist candidate, not upstream code transfer.

Revoke/admin restore/client update fixes reinforce that live peer/write/restore
operations have async and failure-edge risk. Phase 9 stop-lines remain:
do not open write/config/restore without exact named gate.

The `4.9.0.3` version bump is unreleased and remains watch-only. Phase 9
compatibility matrix should update only after a published release or exact
client-compatibility review.

## Candidate classification

- `SERVER1` / `Сервер 1` display-name signal: `already-covered` plus
  `candidate-now-docs-only` reference for naming review.
- Android profile-name acceptance: `candidate-later-exact-gate`; existing gate
  is `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`.
- XRay validation audit: `candidate-now-docs-only` for hardening checklist;
  `candidate-later-exact-gate` only if live config/manager behavior appears.
- Revoke/restore/admin async behavior: `candidate-later-exact-gate`; no action
  now.
- macOS/codesigning packaging: `candidate-now-docs-only` for package-preflight
  notes; iOS claims remain `failed-no-tested-import-path`.
- Public/self-service/config/write transfer: `rejected-by-negative-control`.

## License boundary

Do not copy upstream/GPL code, templates, manager implementations,
scripts/workflows or generated clients. Use only links, behavioral signals,
compatibility risks and local docs/tests/checklists.

## Recommendation

```text
recommendation=P9-N007
title=Amnezia Phase 9 upstream delta note
importance=normal
gate=docs-only/review-only
live_vps_ssh_config_telegram_public=false
```
