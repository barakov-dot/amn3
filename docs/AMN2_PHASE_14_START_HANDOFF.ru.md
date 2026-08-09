# AMN2 Phase 14 Start Handoff

## Зафиксированная граница

- `PHASE13_FORMALLY_SEALED=true`
- `USA_REINSTALL_READY=true`
- `SPAIN_BOT_WEB_MIGRATED=true`
- `SPAIN_CLIENT_ASSURANCE=PASS_WITH_PERFORMANCE_WARNING`
- `AWG3_PHASE=14`
- `PHASE14_STARTED=false`
- `FIRST_PHASE14_GATE_REQUIRES_SEPARATE_EXACT_APPROVAL=true`

Phase 13 перенесла private bot runtime, admin IDs и bot media/source на Spain,
подтвердила Spain web loopback-only и single-instance bot cutover. USA VPS не
выключалась, не очищалась и не переустанавливалась данным проектом; оператор
может использовать её отдельно. AMN2 migration head
`910539eaa8051cb1b59131d38b9fa27b9392744d` остаётся archival evidence.

## Spain client assurance

Operator smoke подтвердил Telegram и сайты через Spain. Existing-client
assurance имеет статус `PASS_WITH_PERFORMANCE_WARNING`: tunnel/route/DNS,
realistic-timeout HTTPS и sustained transfer прошли, Windows proxy был
выключен. Периодические connection latency и краткие Codex reconnect не
доказаны как tunnel drop.

Это non-blocking read-only diagnostic candidate Phase 14. Не менять MTU,
config, peer, server, AWG или firewall без нового воспроизводимого root cause.

## Phase 14 scope

AWG3 начинается только отдельным local-only baseline gate. Existing Spain
AWG2 D1–D7, device passports, configs, keys, firewall/forward rules и foreign
service остаются immutable baseline. AWG3 production package, preflight,
issuance, SSH и live action не разрешены этим handoff.

Первый Phase 14 gate обязан сначала сверить current status, AMN2 archival
head, accepted AWG2 baseline, official AWG3 runtime/client compatibility
evidence и non-blocking client latency evidence. Затем он может подготовить
отдельный implementation plan и новую exact approval phrase, но не выполнять
AWG3 mutation.

## Literal approval для следующего gate

```text
GPT-5.6 SOL HIGH
-> УТВЕРЖДАЮ ТОЛЬКО LOCAL-ONLY PHASE 14 START BASELINE ДЛЯ AWG3 READINESS И SPAIN CLIENT LATENCY EVIDENCE
-> СНАЧАЛА ПРОВЕРИТЬ CURRENT PROJECT STATUS AMN2 ARCHIVAL HEAD И ACCEPTED SPAIN AWG2 BASELINE
-> СОБРАТЬ ТОЛЬКО LOCAL/READ-ONLY EVIDENCE OFFICIAL AWG3 RUNTIME/CLIENT COMPATIBILITY И NON-BLOCKING CLIENT LATENCY
-> НЕ СОЗДАВАТЬ PACKAGE PREFLIGHT OUTCOME CONFIG PEER ИЛИ LIVE GATE
-> НЕ ВЫПОЛНЯТЬ SSH ISSUANCE DEPLOY AWG MUTATION FIREWALL MUTATION ИЛИ CLIENT SETTINGS MUTATION
-> ПОДГОТОВИТЬ ТОЛЬКО PHASE 14 BASELINE RECEIPT И EXACT TDD/APPROVAL PLAN
```
