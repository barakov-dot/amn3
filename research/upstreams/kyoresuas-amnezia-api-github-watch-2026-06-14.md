# kyoresuas/amnezia-api GitHub watch 2026-06-14

Дата: 2026-06-14.

Источник: `kyoresuas/amnezia-api`.

Automation source: `weekly-kyoresuas-upstream-refresh` output was not available
in the AMN2 working thread or local AMN3 evidence during intake. This note uses
direct public GitHub metadata refresh and marks the automation report as
`missing-input`.

License boundary: MIT, but AMN2 transfer remains independent-design only. Do
not copy upstream code or implementation.

## Observed upstream state

- Default branch: `main`.
- Latest public commit observed: `96a1f54c5942f7d8572e743ac90a018b60ce483a`.
- Commit date: 2026-06-14T02:59:06Z.
- Commit message: `feat(swagger): порядок операций в ui по порядку регистрации маршрутов`.
- Latest release: none observed.
- Repository URL: `https://github.com/kyoresuas/amnezia-api`.

## AMN2 interpretation

The new signal is documentation/API-surface ordering, not a production runtime
requirement. It reinforces the existing `P6-N001` public docs/API taxonomy
boundary and suggests a small future drift guard if AMN2 later publishes or
generates public API docs.

## AMN2 candidates

- `P6-N005`: OpenAPI/taxonomy route-order drift guard. Priority: normal. Gate:
  `local-only/docs/tests`. If AMN2 generates public or operator API docs, keep
  route grouping/order deterministic and aligned with the surface policy,
  without opening public API publication.

## Already covered

- Operation locking/serialization, atomic config write, lifecycle vocabulary,
  QR/`vpn://` tests, rate-limit/Helmet-style hardening and setup resilience were
  already captured from the 2026-06-10 refresh and mapped to local policy/gate
  work.

## Gated or deferred

- `/api/clients` CRUD remains behind `P6-C003`.
- Public API/docs publication remains behind `P6-C001`.
- Config read/delivery remains behind `P6-C002`.
- Backup/import/reboot remains behind `P6-C004`.

## Для цепочки

- Add `P6-N005` only if Phase 6 continues with public docs/API polish before
  closeout.
- Do not infer a need to install or run the upstream API service.
- Do not copy implementation code.
