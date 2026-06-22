# Phase 8 helper style hardening

Дата: 2026-06-22.

Статус:

```text
helper_style_hardening_status=completed-local-only
source_evidence=PRIVATE_RC_OPERATOR_RUN_GATE_and_session_0_closeout
template=docs/templates/amn2_safe_gate_helper_template.ps1
live_vps_ssh_performed=false
package_apply_performed=false
service_restart_performed=false
public_exposure_performed=false
config_delivery_performed=false
telegram_live_send_performed=false
bot_polling_started=false
secret_values_printed=false
```

Это evidence использует только существующие Phase 8 evidence и результат
session 0. Оно не открывает live/VPS/config/Telegram/public gates.

## Session 0 findings

```text
helper_encoding_issue=windows_powershell_5_1_mojibake_for_utf8_without_bom
helper_external_probe_url_issue=powershell_interpreted_$TargetIp:3030_as_scoped_variable
```

Влияние:

- Windows PowerShell 5.1 показал русские helper prompts как mojibake.
- Initial local external probes напечатали malformed URLs вида `http:///...`.
- Corrected manual probes с `${TargetIp}` вернули `000/000/000/000`.

## Новые правила helper-ов

```text
helper_encoding_rule=ascii_prompts_or_utf8_with_bom
url_interpolation_rule=${TargetIp}:PORT_or_$($TargetIp):PORT
forbidden_url_pattern=$TargetIp:PORT
parse_check_required=true
probe_url_dry_inspection_required=true
secret_payload_guard_required=true
```

Будущие PowerShell helper prompts должны быть ASCII-only, если скрипт не
сохранен как UTF-8 with BOM. Русские operator-facing инструкции держим в
Markdown handoff/evidence, если BOM не гарантирован.

## Safe template

Tracked template:

```text
docs/templates/amn2_safe_gate_helper_template.ps1
```

Шаблон:

- использует ASCII output;
- использует `${TargetIp}:PORT` URL interpolation;
- проверяет форму probe URL до любой network operation;
- по умолчанию делает только dry inspection;
- не содержит live gate body;
- печатает только safe markers.

## Verification commands

Parse check:

```powershell
$Source = Get-Content -Raw -LiteralPath "docs\templates\amn2_safe_gate_helper_template.ps1"
[scriptblock]::Create($Source) | Out-Null
"template_parse_status=passed"
```

Dry inspection:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "docs\templates\amn2_safe_gate_helper_template.ps1" -DryRun
```

Ожидаемая форма probe URL:

```text
probe_url=http://89.185.80.166:3030/login
probe_url=http://89.185.80.166:3040/api/servers
probe_url=http://89.185.80.166:80/
probe_url=https://89.185.80.166:443/
probe_url_shape_status=passed
network_probe_performed=false
```

## Текущий статус после hardening

```text
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
phase8_private_operator_rc_session_0_status=passed-read-only
recommended_next_state=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
recommended_practical_next_state=FRESH_ANDROID_PHONE_POST_RC_RECHECK_GATE_REVIEW
```

Известных helper-style blockers для local-only helper preparation не осталось.
Любое live/VPS/config/Telegram/public/destructive action по-прежнему требует
новый exact named gate.
