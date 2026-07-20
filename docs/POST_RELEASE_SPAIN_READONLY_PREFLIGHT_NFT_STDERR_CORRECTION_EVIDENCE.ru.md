# POST-RELEASE Spain read-only preflight: fail-closed evidence и nft stderr correction

Дата: 2026-07-20

Фаза: post-release controlled operations

Phase 11: `completed-controlled-private-release`, без повторения rollout/acceptance

## Результат первого запуска

Оператор вернул точный checksum-bound approval для Spain read-only preflight.
Runner был запущен один раз и остановился до создания
`preflight-evidence.json`. Удалённая обязательная команда чтения firewall
`nft list ruleset` передала безопасное диагностическое предупреждение в stderr;
Windows PowerShell воспринял stderr native process как terminating
`NativeCommandError` при действующем `$ErrorActionPreference = "Stop"`.

Это fail-closed результат, а не частично успешный preflight:

- evidence-файл отсутствует;
- старый exact approval считается использованным и недействительным;
- автоматический повтор не выполнялся;
- установка, package update и config write не выполнялись;
- service start/stop/restart не выполнялись;
- Telegram и AWG не изменялись;
- посторонний Spain-сервис не изменялся;
- blind remediation не выполнялась.

## Узкое исправление

Remote probe изменён только в точке обязательного firewall inventory:

```bash
firewall_view="$(nft list ruleset 2>/dev/null)"
```

Подавляется только диагностический stderr `nft`. Ненулевой exit status команды
остаётся статусом assignment, поэтому `set -euo pipefail` по-прежнему завершает
probe с ошибкой. Значение по умолчанию, `|| true`, широкое подавление stderr
SSH-процесса, объединение stderr с JSON, ослабление schema validation или новый
mutation path не добавлялись.

## Новая byte binding

```text
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
remote_probe_sha256=4B73C2E892D9BF64F7A3F2840DB22C6124A990506DA8A8558E5D59E9510A4AF3
runner_sha256=E2A00A9FDF3C1176300CA2B75ED3BDB9EEF6A62A7E8CAB9609C3414C120B14A8
old_approval=rejected_for_reuse
new_approval=required_after_commit_push_and_origin_readback
```

Runner по-прежнему проверяет exact approval до private artifacts, хеширует
открытый remote-script stream, использует dedicated Ed25519 key, независимый
host pin, `-F none`, strict host-key checking и create-new/no-replace evidence.

## Проверки

```text
tdd_red=observed_before_fix
focused_tests=9_passed
root_full_tests=185_passed
bash_parse=pass
powershell_parse=pass
git_diff_check=pass
security_scan=8291665_3731823_20260720T074034Z
security_coverage=3_of_3_complete
security_findings=0
```

Новая живая попытка не входит в это исправление. После commit/push и точного
origin readback оператору должна быть выдана новая literal approval, связанная
с новыми SHA-256. До её отдельного возврата SSH retry запрещён.

Private target address, login, key material, host-key line, конфиги и секреты в
этот документ не включены. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не
изменялся.
