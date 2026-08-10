# AMN2 Phase 14 Start Handoff

## Зафиксированная граница

- `PHASE13_FORMALLY_SEALED=true`
- `USA_REINSTALL_READY=true`
- `SPAIN_BOT_WEB_MIGRATED=true`
- `SPAIN_CLIENT_ASSURANCE=PASS_WITH_PERFORMANCE_WARNING`
- `AWG3_PHASE=14`
- `PHASE14_STARTED=true`
- `PHASE14_LOCAL_READINESS_GATE_COMPLETED=true`
- `PHASE14_SOURCE_HEAD=4547af1b23e4774822119f98004568c6eb039303`
- `PHASE14_SOURCE_RECEIPT_SHA256=3DF5A62B23C5BE565E08383288269AA7F486EE23F9E1A60D4D767D53A240316B`
- `PHASE14_DUAL_PROTOCOL_DESIGN_APPROVED=true`
- `PACKAGE_AND_READONLY_PREFLIGHT_DESIGN_APPROVED=true`
- `PACKAGE_MATERIALIZED=false`
- `PREFLIGHT_RUN=false`
- `SSH_USED=false`
- `LIVE_MUTATION=false`

Phase 13 перенесла private bot runtime, admin IDs и bot media/source на Spain,
подтвердила Spain web loopback-only и single-instance bot cutover. USA VPS не
выключалась, не очищалась и не переустанавливалась данным проектом; оператор
может использовать её отдельно. AMN2 migration head
`910539eaa8051cb1b59131d38b9fa27b9392744d` остаётся archival evidence.

Phase 14 local source-integration/readiness gate завершён в изолированном
worktree `codex/phase14-awg3-readiness-local`. Exact HEAD
`4547af1b23e4774822119f98004568c6eb039303` имеет clean status; локальная
verification receipt подтверждена точным SHA-256
`3DF5A62B23C5BE565E08383288269AA7F486EE23F9E1A60D4D767D53A240316B`.

Утверждён новый standalone Phase 14 contract: AWG2 продолжает выпускаться и
остаётся default; AWG3 добавляется параллельно, требует exact
platform/application/version/build, global acceptance и отдельного issuance
enable. Per-user admin approval после глобального enable не требуется.

## Spain client assurance

Operator smoke подтвердил Telegram и сайты через Spain. Existing-client
assurance имеет статус `PASS_WITH_PERFORMANCE_WARNING`: tunnel/route/DNS,
realistic-timeout HTTPS и sustained transfer прошли, Windows proxy был
выключен. Периодические connection latency и краткие Codex reconnect не
доказаны как tunnel drop.

Это non-blocking read-only diagnostic candidate Phase 14. Не менять MTU,
config, peer, server, AWG или firewall без нового воспроизводимого root cause.

## Phase 14 current scope

Design/status gate разделил продолжение на две независимые реализации:

1. dual-protocol application/self-service issuance;
2. checksum-bound package/read-only preflight tooling.

Утверждённая spec:
`docs/superpowers/specs/2026-08-10-amn2-phase14-dual-protocol-package-readonly-preflight-design.ru.md`.

Implementation plans:

- `docs/superpowers/plans/2026-08-10-amn2-phase14-dual-protocol-self-service-issuance.md`;
- `docs/superpowers/plans/2026-08-10-amn2-phase14-package-readonly-preflight-tooling.md`.

Application plan выполняется первым и заканчивается новым local readiness
receipt. Package tooling plan может начаться только от принятого application
HEAD/receipt. Production package materialization, оба preflight, application
stage, runtime stage, admin pilot, acceptance и issuance enable остаются
отдельными gates без автоматического chaining.

Existing Spain AWG2 D1–D7, configs, keys, runtime, firewall/forward rules и
foreign service остаются immutable baseline. Monitoring уведомлений в bot
отложен до появления runtime/configs и не входит в текущий scope.

## Следующее разрешение

Текущий handoff не содержит разрешения на выполнение implementation plan.
Следующая команда может разрешить только local-only TDD application plan от
exact HEAD `4547af1b23e4774822119f98004568c6eb039303`. Она не должна разрешать
package materialization, preflight, SSH, config/QR/peer, deploy, push или live
mutation. Exact executable text формируется отдельно вместе с планом по
критичности и рекомендацией model/effort.
