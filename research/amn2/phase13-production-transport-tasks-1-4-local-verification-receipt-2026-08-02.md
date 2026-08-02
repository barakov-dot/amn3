# AMN2 Phase 13 — квитанция локальной интеграционной проверки Production Transport Tasks 1–4

Дата проверки: 2026-08-02

Статус: `local_transport_chain_verified_not_manifest_or_live_authorized`

## Основание и границы

Проверена локальная fail-closed цепочка Phase 13 Production Transport поверх
root head `8221e5b0cdaf78ec08cd01b6e21de8d2a2941618`. Она охватывает private
outcome claim, Phase 12 trust-bundle adapter, один bounded SSH transport и
self-observing read-only Spain collector. AMN2 AWG3 worktree сохранён без
изменений на `82290c06942176c36d2e09a9d968900560a49048`.

В scope вошли только следующие root commits:

- `9cd5db9c26a6831c05c02144383fec486a7cf935` — private outcome claim;
- `d3e14edbe60b4583b5ce3d7320f7110a28d9bbb1` — Phase 12 trust-bundle adapter;
- `5826debb7975e33399a041237da2af7ed720ef12` — one-SSH bounded transport;
- `8221e5b0cdaf78ec08cd01b6e21de8d2a2941618` — self-observing collector.

Не создавались и не разрешены: новый outcome или manifest, package build,
SSH/preflight run, deploy, config/peer issuance, AWG stop/restart/recreate/
upgrade, reboot, rollback rehearsal, Spain/USA mutation, foreign Spain service
change, USA shutdown, cleanup или reuse.

## Локальные результаты

- Phase 13 focused suite:
  `tests/test_phase13_awg3_preflight_contract.py` и
  `tests/test_phase13_awg3_readonly_preflight.py` — `91 passed`;
- утверждённый Phase 12 Spain regression scope:
  `tests/test_post_release_spain_readonly_preflight.py` и
  `tests/test_phase12_spain_package_tooling.py` — `233 passed, 1 skipped`;
- Bash collector syntax — passed;
- PowerShell runner syntax — passed;
- `git diff --check` для полного диапазона Tasks 1–4 — passed.

Подтверждён порядок: exact approval, create-new claim, fixed private
trust-bundle и host pin, один bounded SSH process, строгий UTF-8/LF envelope,
checksum/schema validation и secret-safe evidence. Все проверки использовали
только local fake harness; collector и SSH на Spain не запускались.

## Контроли и security review

Collector не принимает пользовательские или ENV-подменяемые
`AMN2_PHASE13_AWG2_*` и `AMN2_PHASE13_FOREIGN_*` observed values. Неизменяемая
Phase 12 equality foundation используется только как expected projection.

Подтверждена taxonomy: foreign equality mismatch — exit `69`, AWG2 equality
mismatch — exit `70`, candidate conflict — exit `71`, ambiguous observation —
exit `72`. Static mutation review не обнаружил в новых collector/runner bytes
команд управления Docker, AWG, firewall, IP или systemd. Secret review не
обнаружил secret payload: единственное совпадение было собственным регулярным
выражением runner, которое блокирует PrivateKey, PSK, token и другие секретные
поля в evidence.

Manual scoped security review не выявил reportable findings. Новый broad
security scan, durable security report и любые scan artifacts не создавались.

## Stale manifest/outcome boundary

Historical receipt локального tooling на `0e768930247148ab7edfecdb0fd89e9eeee1d3ca`
остаётся историческим evidence. Однако прежние materialized manifest/outcome
нельзя использовать: collector bytes теперь относятся к root head `8221e5b`.
Новый checksum-bound manifest/outcome допускается подготовить только отдельным
exact gate после status/receipt и последующего commit/push решения.

Spain AWG2 d1–d7 остаётся принятым baseline. USA остаётся rollback contour;
отключение, cleanup или reuse не разрешены без отдельного USA retirement
readiness gate и exact live approval.
