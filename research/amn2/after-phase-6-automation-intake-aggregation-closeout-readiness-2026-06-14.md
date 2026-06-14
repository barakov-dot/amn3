# After Phase 6 automation intake aggregation and closeout readiness review

Дата: 2026-06-14.

Статус: `completed-local-docs-only`.

Scope: normalize available weekly upstream-refresh automation inputs, mark
missing automation reports explicitly, refresh upstream facts through public
GitHub metadata when needed, update AMN2 candidates and decide whether Phase 6
can proceed to final closeout.

## Boundaries

This review did not perform live VPS commands, SSH commands, package
rebuild/apply on VPS, service restart/deploy, public exposure, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive cleanup/reinstall, Telegram token use, Telegram identity
mutation, secret-bearing evidence publication or upstream/GPL code copy.

## Inputs

| Automation | Result | Intake handling |
| --- | --- | --- |
| `prvtpro-weekly-upstream-refresh` | Available in current Phase 6 heartbeat context | Normalized into `research/upstreams/prvtpro-amnezia-web-panel-upstream-refresh-2026-06-14.md`. |
| `weekly-kyoresuas-upstream-refresh` | Final report not found in current thread or local AMN3 evidence | Marked `missing-input`; direct public GitHub metadata refresh used for `kyoresuas/amnezia-api`. |
| `amnezia-weekly-upstream-refresh` | Final aggregator report not found in current thread or local AMN3 evidence | Marked `missing-input`; direct public GitHub metadata refresh used for Amnezia ecosystem repos. |

Missing automation output was not invented. Every candidate below is based on
visible heartbeat text or direct public repository metadata.

## Normalized cards

### PRVTPRO

Источник: PRVTPRO/Amnezia-Web-Panel.

Automation ID: `prvtpro-weekly-upstream-refresh`.

Дата проверки: 2026-06-14.

Последний upstream commit/release: `fbe5a2b`, reported by the automation as
2026-06-08.

Что изменилось: Telemt path fix, multi-instance AmneziaWG discussion,
endpoint/DNS/subnet/IPv6 requests, per-user statistics and speed-limit
requests.

Что полезно для AMN2: package asset path preflight, multi-instance/IPAM conflict
model, dry-run config compatibility tests.

Что уже покрыто в AMN2: capability registry, aggregate-only analytics/privacy
boundary, client delivery/copy guidance, package markdown hygiene guard and
public/config/write gates.

Что добавить в план: `FI-M004` package asset path preflight and `P6-M005`
multi-instance/port/IPAM conflict model.

Что gated/deferred: per-user stats/speed limits, live multi-instance actions,
public/self-service surface and real config delivery.

Что нельзя переносить: GPL code, templates, UI, manager implementations,
scripts, workflows or admin-equivalent Bearer-token model.

### KYORESUAS

Источник: kyoresuas/amnezia-api.

Automation ID: `weekly-kyoresuas-upstream-refresh`.

Дата проверки: 2026-06-14.

Automation status: `missing-input/direct-refresh-used`.

Последний upstream commit/release:
`96a1f54c5942f7d8572e743ac90a018b60ce483a`, 2026-06-14T02:59:06Z,
`feat(swagger): порядок операций в ui по порядку регистрации маршрутов`;
latest release not observed.

Что изменилось: latest observed signal is Swagger UI operation ordering by
route registration order.

Что полезно для AMN2: deterministic API/docs taxonomy if public/operator docs
are generated later.

Что уже покрыто в AMN2: previous 2026-06-10 KYORESUAS signals for operation
lock, atomic config write, lifecycle vocabulary, QR/`vpn://` tests,
rate-limit/Helmet and setup resilience.

Что добавить в план: `P6-N005` OpenAPI/taxonomy route-order drift guard.

Что gated/deferred: public API docs publication, `/api/clients` write CRUD,
config read/delivery and backup/import/reboot.

Что нельзя переносить: upstream implementation code or service runtime.

### Amnezia ecosystem

Источник: amnezia-vpn client/defaultvpn/amneziawg repositories.

Automation ID: `amnezia-weekly-upstream-refresh`.

Дата проверки: 2026-06-14.

Automation status: `missing-input/direct-refresh-used`.

Последний upstream commit/release:

- `amnezia-vpn/amnezia-client`: release `4.8.18.0`, latest observed commit
  `594635e`.
- `amnezia-vpn/DefaultVPN`: latest observed commit `d139fb5`.
- `amnezia-vpn/amneziawg-android`: release `2.0.1`, latest observed commit
  `fb64e74`.
- `amnezia-vpn/amneziawg-apple`: latest observed commit `0c4d98d`.
- `amnezia-vpn/amneziawg-windows`: latest observed commit `4bab562`.

Что изменилось: Android AmneziaWG has a current `2.0.1` release; Apple and
Windows AmneziaWG version bumps remain watch-only; Amnezia client release state
is consistent with the already captured 2026-06-12 watch.

Что полезно для AMN2: continue treating DefaultVPN as practical iOS/RF path,
standalone AmneziaWG as installed/legacy iOS and Android paths, and client
compatibility as a watch-only matrix unless concrete import failures appear.

Что уже покрыто в AMN2: `P6-M004`/`P6-X001`/`P6-X002` client compatibility and
copy boundary, VPS-smoked in `b3102db` and superseded by later smoked `0de7a77`.

Что добавить в план: no new active Phase 6 item required from this refresh.

Что gated/deferred: real config delivery, public/self-service client flows and
Telegram live send/profile/media mutation.

Что нельзя переносить: GPL code/assets/templates/workflows from client repos.

## Deduplicated candidate list

| Candidate | Priority | Gate | Decision |
| --- | --- | --- | --- |
| `FI-M004` package asset path preflight | important | `package/preflight only` | New fresh-installer/package hygiene candidate. |
| `P6-M005` multi-instance/port/IPAM conflict model | important | `local-only/docs/tests` | New candidate, no live action. |
| `P6-N005` OpenAPI/taxonomy route-order drift guard | normal | `local-only/docs/tests` | New optional docs/test candidate. |
| AmneziaWG Android `2.0.1` watch | watch-only | `watch-only` | No active AMN2 work required now. |
| Per-user stats/speed limits | gated-deferred | `privacy gate`, `write API gate`, `config delivery gate` | Not default work. |

## Closeout readiness

Phase 6 can proceed to final closeout after this aggregation. There is no new
critical upstream signal that blocks closeout. The new items are either
fresh-installer/package hygiene (`FI-M004`), local docs/test modeling
(`P6-M005`, `P6-N005`) or watch-only.

Recommended next step:

```text
Phase 6 final closeout + clean-installer next-phase entry + current VPS known-good snapshot/runbook
```

Useful optional bundle before closeout:

```text
FI-M004 + P6-N005 as local-only docs/tests/package hygiene
```

Gated options remain separate named gates only:

- `P6-C001` public exposure;
- `P6-C002` real config delivery;
- `P6-C003` write API production;
- `P6-C004` backup/restore/import production;
- `P6-C007` destructive cleanup/reinstall;
- live VPS/package apply/smoke beyond current known-good `0de7a77`;
- Telegram identity/profile/media mutation.
