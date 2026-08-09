# Phase 13 Bot/Web Migration Final Acceptance Closeout — 2026-08-09

Статус: `PASSED`, `USA_REINSTALL_READY=true`.

## Принятый итоговый scope

По позднему operator override Phase 13 завершает перенос private Telegram bot
runtime, admin Telegram IDs и bot media/source на Spain. Spain database остаётся
authoritative; USA legacy database не восстанавливается поверх неё. Spain web
сохраняется только на loopback. USA VPS не выключалась, не очищалась и не
переиспользовалась в рамках этого gate.

AWG3 полностью перенесена в Phase 14. Phase 13 не выполняла AWG3 analysis,
package, preflight или live action.

## Live evidence

- Runtime-only disabled stage:
  `spain-bot-runtime-stage-20260809-113453`, sanitized receipt SHA-256
  `9142b5b42366adc0d2d7fd6b01da140a411f05ca614f51da199ca0f17ecc0523`.
- Single-instance cutover:
  `bot-cutover-20260809-103106`, `6` SSH processes, status `success`,
  `single_owner=true`, `spain_active=true`, `usa_active=false`,
  `rolled_back=false`, `usa_server_mutated=false`. Sanitized receipt SHA-256:
  `d4f66f2d8262a929c162806cc6bf76fbdbc1fcd41fd561f75dd73d646fce1a07`.
- Final read-only acceptance:
  `bot-web-final-acceptance-20260809-110018`, ровно `2` SSH processes,
  status `success`, `service_action_performed=false`,
  `raw_output_persisted=false`. Sanitized receipt SHA-256:
  `305a24a69dc668b6c42819815d7f5f3caf784eb399ff577c7afeaf7930b434d0`.

Final acceptance подтвердил:

- `single_owner=true`;
- Spain bot active, USA bot inactive;
- Spain web loopback healthy;
- database/runtime/source equality;
- Spain AWG2 equality;
- foreign service equality;
- `USA_REINSTALL_READY=true`.

## Local verification

Финальный focused regression scope: `106 passed`. Python syntax,
`git diff --check`, scoped secret review и manual scoped security review passed.
Broad security scan не запускался. Reportable findings: `0`.

VPS-OPS-LAB tooling head перед closeout docs:
`7e44a5f8dbcba2ab91a371dd64a35b9326a444db`.
AMN2 migration head сохранён без изменений:
`910539eaa8051cb1b59131d38b9fa27b9392744d`.

## Negative controls

- USA server shutdown/cleanup/reuse/provider mutation: не выполнялись;
- USA web/database mutation: не выполнялась;
- live Spain database apply в финальном runtime-only scope: не выполнялся;
- AWG restart/update/recreate/config/peer action: не выполнялись;
- Spain D1–D7, keys, firewall, forward rules и foreign service: не изменялись;
- raw database/config/token/key/SSH target/stdout/stderr: не сохранялись и не
  выводились.

Phase 13 exit condition выполнено. Следующее product изменение требует
отдельного Phase 14 start gate; предыдущие Phase 13 approvals его не открывают.
