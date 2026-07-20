# POST-RELEASE Spain preflight stage-coded diagnostic implementation evidence

Дата: 2026-07-20

Статус: local implementation verified; live diagnostic not run

## Основание

- design approval:
  `APPROVE_POST_RELEASE_SPAIN_PREFLIGHT_STAGE_CODED_DIAGNOSTIC_GATE_DESIGN`;
- written design: commit `f5e22e4`;
- written-spec approval:
  `APPROVE_WRITTEN_POST_RELEASE_SPAIN_PREFLIGHT_STAGE_CODED_DIAGNOSTIC_SPEC_F5E22E4`;
- implementation plan: commit `ee02fcd`;
- inline execution approval:
  `APPROVE_SPAIN_DIAGNOSTIC_IMPLEMENTATION_PLAN_EE02FCD_INLINE_EXECUTION`.

Эти approvals разрешили локальную реализацию и проверки. Они не разрешают новый
SSH-запуск, install, remediation, Telegram или AWG action.

## Причина доработки

Две ранее разрешённые read-only попытки завершились до evidence. Первая
остановилась на обработке диагностического stderr `nft`. Вторая вернула
ненулевой SSH status, но прежний runner намеренно удалял raw stdout/stderr и не
мог безопасно определить failing collector.

## Реализованный контракт

Remote probe сохраняет `set -Eeuo pipefail`, назначает allowlisted stage каждому
обязательному collector и при ошибке выводит только:

```text
AMN2_SPAIN_PREFLIGHT_FAILURE_V1|stage=<allowlisted>|exit=<1..255>
```

`$BASH_COMMAND`, stderr, command output, unit/container names, target data и
пути не выводятся. Прямые validation exits `65..70` также маршрутизируются через
тот же emitter; это было найдено security review в первом snapshot и закрыто
отдельным RED -> GREEN тестом до финального snapshot.

Runner:

- требует exact approval и trust run id `spain-fresh-20260720-001` до private
  state;
- сохраняет locked-stream SHA binding remote bytes;
- повторно использует dedicated Ed25519 key и independently pinned host;
- перед SSH создаёт private current-user-only `preflight-outcome.claim` через
  `CreateNew`;
- принимает ровно одну exact envelope, allowlisted stage и совпадающий process
  exit code;
- отвергает unknown, malformed, duplicate и valid-plus-malformed envelope;
- не сохраняет raw SSH stdout/stderr;
- создаёт только success evidence или только sanitized failure evidence;
- не выполняет retry или remediation.

## Byte binding

```text
source_revision=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
runner_sha256=E754737965E994FE1C2E828785345E3078E2716514BA33EA84688176304B4CF1
remote_probe_sha256=16CE3F9E14A72DFB0DC957B2A1CA13F1ADBCA72F41C60FC2D4DD9904D3E74CD6
trust_run_id=spain-fresh-20260720-001
```

## TDD и проверки

```text
bash_failure_envelope_red=observed
bash_failure_envelope_green=pass
runner_parser_claim_run_id_red=observed
runner_parser_claim_run_id_green=pass
mixed_valid_malformed_envelope_red=observed
mixed_valid_malformed_envelope_green=pass
explicit_exit_diagnostic_red=observed
explicit_exit_diagnostic_green=pass
focused_tests=16_passed
root_full_tests=192_passed
bash_parse=pass
powershell_parse=pass
git_diff_check=pass
security_scan=ee02fcd_bf33180_20260720T090425Z
security_coverage=3_of_3_complete
security_deferred=0
security_findings=0
```

Security scan выполнялся по свежему snapshot после закрытия explicit-exit gap.
Все три code/test файла получили full-file receipts. Делегированные workers не
использовались из-за выбранного inline режима; узкий scope полностью прочитан
parent agent.

## Live boundary

Новый runner не запускался с непустым approval. Поэтому
`preflight-outcome.claim`, `preflight-evidence.json` и
`preflight-failure-evidence.json` новым кодом не создавались. Spain не
контактировалась после второй старой попытки.

Не выполнялись install/update, start/stop/restart, configuration write,
provider mutation, Telegram action, unrelated-service mutation или AWG action.
Новый запуск возможен только после commit/push, exact origin readback и возврата
оператором отдельной буквальной checksum-bound approval.

Private target, login, key material, host-key line, raw diagnostics и конфиги в
Git/evidence не включены. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не
изменялся.
