# AMN2 Phase 13 — квитанция локальной интеграционной проверки Transport Subreason Tasks 1–4

Дата проверки: 2026-08-02

Статус: `local_transport_subreason_chain_verified_not_manifest_or_live_authorized`

## Основание и границы

Проверена локальная fail-closed цепочка Phase 13 Transport Subreason на root
head `fcea09f9f2e2bf89770e5c8bd6e3cfecc2fabb07`. В scope вошли только commits:

- `2c980ae0646aa417fc0b04dec67471aa5aa441e7` — failure evidence V2 contract;
- `78e1cdfaf4564825173ce59645ef8fe2592b6b1c` — pure transport subreason mapping;
- `97a9654946e69ca80c3c01d38199ebb7662e49b4` — local process failure classification;
- `fcea09f9f2e2bf89770e5c8bd6e3cfecc2fabb07` — strict sanitized V2 writer и call sites.

Проверка использовала только local fake harness. Не создавались новый outcome или
manifest; не выполнялись package build, SSH/preflight, deploy, config/peer
issuance, AWG stop/restart/recreate/upgrade, reboot, rollback rehearsal,
Spain/USA mutation, изменение постороннего Spain-сервиса, USA shutdown,
cleanup или reuse.

## Результаты

- Phase 13 focused suite:
  `tests/test_phase13_awg3_preflight_contract.py` и
  `tests/test_phase13_awg3_readonly_preflight.py` — `102 passed`;
- утверждённый Phase 12 Spain regression scope:
  `tests/test_post_release_spain_readonly_preflight.py` и
  `tests/test_phase12_spain_package_tooling.py` — `233 passed, 1 skipped`;
- `verify-local` — `7` contract artifacts; network, package build и live
  authorization — `false`;
- Bash, PowerShell и Python syntax — passed;
- `git diff --check` полного диапазона Tasks 1–4 — passed.

V2 требует обязательный `transport_subreason`: transport принимает только
allowlist, а все не-transport stages — только `not_applicable`. Маппинг
сохраняет `timeout`, `output_oversized`, `ssh_exit_unclassified`,
`local_process_failure` и `transport_internal_failure`; внешний transport exit
остаётся `67` с `observation_ambiguous`.

## Исторические границы и security review

Исторический V1 failure contract не изменён. Consumed
`spain-awg3-20260802-002` сохранён как failure-only: claim и sanitized failure
receipt присутствуют, success evidence отсутствует. Повторное использование
этого outcome запрещено.

Manual scoped review полного production diff Tasks 1–4 не выявил reportable
findings: added production lines не содержат secret payload, raw output sink
или mutation command. Единственный `Process.Start()` остаётся bounded local
transport process; пустые stdout/stderr buffers не сохраняют output. Новый
broad security scan, durable security report и scan artifacts не создавались.

## Stale/live boundary

Текущие materialized manifest/outcome stale относительно проверенных bytes и
не могут применяться. Новый checksum-bound manifest/outcome, package build,
SSH approval, Spain preflight и любые live actions требуют отдельных exact
gates. AWG3 остаётся candidate; Spain AWG2 d1–d7 — принятый baseline. USA
остаётся rollback contour: shutdown, cleanup или reuse требуют отдельного USA
retirement readiness gate и exact live approval.
