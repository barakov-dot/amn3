# AMN2 Phase 13 — receipt локального AWG3 preflight tooling

Дата проверки: 2026-08-02
Статус: `local_tooling_verified_not_package_or_live_authorized`

## Основание и границы

Локальный комплект подготовлен поверх неизменяемой Phase 12 equality
foundation. Проверенный root head:
`0e768930247148ab7edfecdb0fd89e9eeee1d3ca`.

В scope вошли schemas, manifest/evidence validator, read-only remote collector
и checksum/outcome PowerShell runner. Не выполнялись и не разрешены: package
build, production manifest/outcome, SSH, Spain preflight, выдача config/peer,
restart/recreate/upgrade AWG, reboot, rollback rehearsal и любые Spain/USA
live mutations.

Spain AWG2 d1–d7, USA rollback contour и посторонний Spain-сервис не
изменялись. USA не готов к отключению, очистке или иному использованию:
`live_action_authorized=false`.

## Связанные локальные commits

- `656b8be` — schemas Phase 13 AWG3 preflight;
- `a996354` — contract Phase 13 AWG3 preflight;
- `b2fb763` — read-only collector Phase 13 AWG3;
- `96da6c6` — checksum-bound runner Phase 13 AWG3;
- `09023c1` — Phase 12 PowerShell exact stdin encoding regression fix;
- `0e76893` — local AWG3 manifest/collector/runner binding.

## Проверка Task 7

- Phase 13 AWG3 tooling: `60 passed`;
- Spain regression scope: `233 passed, 1 skipped`;
- Python, Bash и PowerShell syntax: passed;
- `git diff --check`: passed;
- secret-pattern scan: `0` matches;
- `verify-local`: passed, `artifact_count=6`,
  `candidate_sha256=f78ab80caceb1dc894bd6910cdbe93f9f9c9d6c4afe7502995698ce74a1f60ab`,
  `network_attempted=false`, `package_build_performed=false`,
  `live_action_authorized=false`;
- неизвестный production mode: fail-closed, exit `64`.

Один Spain test запускался отдельным локальным harness из-за особенности
Windows/Git Bash temporary-path boundary; итоговый scope остаётся `233 passed,
1 skipped`. Harness удалён до финальной проверки Git scope.

## Контрольные суммы артефактов

| Артефакт | SHA-256 |
| --- | --- |
| `evidence.schema.json` | `4FC09289AE3BD89DAFB64F68C079918F980444CD8666D9B127C44789EBB1090D` |
| `failure-evidence.schema.json` | `17C5A71D7DFD25462907FF433761798929E36D73734124818A0C04B265A778F9` |
| `manifest.schema.json` | `FB2F245421ADC533169E38239EF2C5A8B8C09D3C291E87EB06A9167357E04B6A` |
| `phase12-equality-foundation.json` | `0E5A5926821D88AE4A2515F9E95CD7C3F69DB52100C1A1EC74E99FB794222281` |

Файлы collector и runner закреплены manifest contract; проверка `verify-local`
подтвердила их общий candidate SHA-256 выше. В receipt не помещены target
host/user/IP/key paths, raw outputs, private keys, PSK, tokens или usable
configs.

## Security review

Новый broad security scan и durable report не создавались: Task 7 прямо
разрешал только manual scoped security review. Вручную проверены collector,
runner и validator: remote collector ограничен read-only наблюдениями `ss`,
`ip … show`, `docker ps/network inspect` и `systemctl list-unit-files`; команд
управления AWG, Docker, firewall, IP-конфигурацией или сервисами нет. Runner
содержит bounded local transport для будущего отдельного gate, но в этой
проверке не запускался.

Sealed security diff report исходной local-only реализации остаётся отдельным
evidence: SHA-256
`150E7DADEB1C6156777C9E8203B1FE6EB09E09667C48187FAE633FB31774D52B`;
он не подменяет отсутствующий новый scan tooling diff.

## Следующий gate

Следующее действие требует нового exact approval. Оно может рассматривать
только checksum-bound package design и read-only Spain conflict/equality
preflight; без build/deploy, SSH mutation, issuance, reboot, AWG alteration
или USA retirement. До отдельного USA readiness decision старый USA server
остаётся rollback contour.
