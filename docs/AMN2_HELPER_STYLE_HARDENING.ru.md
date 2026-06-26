# AMN2 hardening стиля helper-ов

Дата: 2026-06-22.

Статус:

```text
helper_style_hardening_status=completed-local-only
source_evidence=PRIVATE_RC_OPERATOR_RUN_GATE_and_session_0_closeout
live_vps_ssh_performed=false
package_apply_performed=false
service_restart_performed=false
public_exposure_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
bot_polling_started=false
secret_values_printed=false
```

Этот hardening использует существующие Phase 8 evidence и результат
`PRIVATE_RC_OPERATOR_RUN_GATE`. Он не открывает live/VPS/config/Telegram/public
gates и не выполняет новых операций.

## 1. Причина

В первой private/operator RC session 0 были зафиксированы две проблемы
helper-а:

```text
helper_encoding_issue=windows_powershell_5_1_mojibake_for_utf8_without_bom
helper_external_probe_url_issue=powershell_interpreted_$TargetIp:3030_as_scoped_variable
```

Влияние:

- русские подсказки в Windows PowerShell 5.1 отобразились mojibake;
- initial external probes сформировали malformed URLs вида `http:///...`;
- probes были вручную повторены с `${TargetIp}` и прошли как `000/000/000/000`.

## 2. Обязательные правила для будущих helper-ов

Правила:

- PowerShell helper prompts должны быть ASCII-only, либо сам `.ps1` должен быть
  сохранен как UTF-8 with BOM;
- если файл сохраняется без BOM, русские operator prompts нельзя помещать в
  исполняемый `.ps1`;
- русские инструкции и copy/paste команды держать в Markdown/evidence;
- в PowerShell interpolated URLs всегда использовать `${TargetIp}:PORT` или
  `$($TargetIp):PORT`;
- запрещено использовать `$TargetIp:PORT` внутри строк;
- перед выдачей helper-а оператору обязателен parse check;
- перед выдачей helper-а оператору обязательна сухая инспекция probe URLs;
- external probes должны печатать полный target URL до выполнения;
- helper должен выводить safe markers, а не secret-bearing payload.
- если PowerShell helper передает bash через `ssh ... bash -s`, текст remote
  script должен быть нормализован в LF до передачи;
- CRLF в stdin bash может сломать даже успешный remote run на финальном
  `exit 0` с ошибкой `numeric argument required`.

Canonical URL pattern:

```powershell
"http://${TargetIp}:3030/login"
"http://${TargetIp}:3040/api/servers"
"http://${TargetIp}:80/"
"https://${TargetIp}:443/"
```

Запрещенный pattern:

```powershell
"http://$TargetIp:3030/login"
```

## 3. Preflight parse check

Перед использованием нового PowerShell helper-а:

```powershell
$ScriptPath = "C:\Users\SooL\Documents\VPS-OPS-LAB\docs\templates\amn2_safe_gate_helper_template.ps1"
$Source = Get-Content -Raw -LiteralPath $ScriptPath
[scriptblock]::Create($Source) | Out-Null
"parse_check_status=passed"
```

Для будущего gate-specific helper-а менять только `$ScriptPath`.

## 4. Dry inspection для probe URLs

Перед любым helper-ом, который содержит public closed probes, выполнить сухую
проверку URL-формы:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\SooL\Documents\VPS-OPS-LAB\docs\templates\amn2_safe_gate_helper_template.ps1" -DryRun
```

Ожидаемая форма:

```text
probe_url=http://89.185.80.166:3030/login
probe_url=http://89.185.80.166:3040/api/servers
probe_url=http://89.185.80.166:80/
probe_url=https://89.185.80.166:443/
probe_url_shape_status=passed
network_probe_performed=false
```

Если в output есть `http:///`, helper нельзя выдавать оператору.

## 5. Шаблон безопасного helper-а

Tracked template:

```text
docs/templates/amn2_safe_gate_helper_template.ps1
```

Шаблон делает только local dry inspection по умолчанию. Он намеренно:

- использует ASCII prompts/output;
- содержит `${TargetIp}:PORT` URL interpolation;
- проверяет malformed `http:///` и missing port;
- не выполняет network probes;
- не выполняет SSH/VPS действий;
- не содержит live body;
- требует, чтобы gate-specific helper явно добавил свой narrow allowed scope.

## 6. Минимальный checklist для будущего helper-а

Перед тем как helper попадает оператору:

```text
helper_encoding_rule=ascii_prompts_or_utf8_with_bom
url_interpolation_rule=${TargetIp}:PORT
remote_stdin_bash_lf_normalization_required=true
parse_check_required=true
probe_url_dry_inspection_required=true
secret_payload_guard_required=true
stop_at_first_failed_gate_required=true
```

LF normalization pattern для bash через stdin:

```powershell
$RemoteScriptLf = $RemoteScript.Replace("`r`n", "`n").Replace("`r", "`n")
$remoteOutput = $RemoteScriptLf | & ssh @sshArgs 2>&1
```

Команды проверки:

```powershell
$ScriptPath = "C:\Users\SooL\Documents\VPS-OPS-LAB\tmp\future_gate_helper.ps1"
$Source = Get-Content -Raw -LiteralPath $ScriptPath
[scriptblock]::Create($Source) | Out-Null
"parse_check_status=passed"
```

```powershell
Select-String -LiteralPath $ScriptPath -Pattern '\$TargetIp:\d+'
```

Если последняя команда что-то нашла, helper требует исправления на
`${TargetIp}:PORT`.

## 7. Stop-lines

Этот hardening не разрешает:

- live VPS/SSH command;
- package upload/apply;
- service restart;
- public exposure;
- firewall/listener/TLS/reverse proxy/Cloudflare/ngrok changes;
- config generation/delivery;
- `.conf`, QR, `vpn://`, private key, PSK, token или password output;
- Telegram live send;
- bot polling;
- Telegram profile/media mutation;
- restore/import/reboot;
- provider rebuild;
- production peer/user mutation;
- broader rollout.

Для любого такого действия нужен новый exact named gate.

## 8. Следующее рекомендованное состояние

Остается активным:

```text
recommended_next_state=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
recommended_practical_next_state=FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
```

Если Android phone появится, следующий практический шаг - review gate для
fresh Android phone post-RC recheck. Если телефона нет, оставаться в ожидании
точного именованного gate.
