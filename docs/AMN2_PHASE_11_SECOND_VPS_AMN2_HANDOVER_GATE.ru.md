# AMN2 Phase 11: safe handover второго VPS

Актуально: 2026-07-15.

## Решение

Второй VPS больше не нужен AMN2: `PHASE11-RESTORE-001A` завершён успешно,
mandatory cleanup прошёл, повторный read-only аудит подтвердил clean SSH-only
host. По решению оператора VPS сохраняется до выходных и затем передаётся под
другой функционал. Удаление сервера, отмена тарифа, отключение автопродления и
любая другая provider mutation не входят в этот gate.

## Read-only billing visibility

```text
provider=4VPS
location=Switzerland_Zurich
plan=SW-cx01
paid_until=2026-08-12_23:18:25|provider_displayed_time
current_month_price_rub=590.00
autorenew=enabled_observed_read_only
provider_mutation_performed=false
```

Эти данные получены из авторизованного кабинета только чтением. Они не
разрешают менять автопродление, оплачивать, продлевать, отменять или удалять
сервер.

## Текущий clean-host contract

Повторный аудит 2026-07-15 подтвердил:

```text
ssh=active_key_only
ufw=active_default_incoming_deny
external_tcp_ports=22
external_udp_ports=none
amn2_tree=absent
amn2_units=0
containers=0
recovery_or_amn2_artifacts=0
failed_units=0
docker=absent
production_contact=false
secret_transfer=false
provider_mutation=false
```

## Exact AMN2 handover procedure

После выходных и перед фактической передачи:

1. Повторить `tmp/phase11_second_vps_retention_audit.ps1` только read-only.
2. Остановиться, если найден AMN2 tree/unit/container, recovery artifact,
   дополнительный listener или failed unit; ничего автоматически не удалять.
3. Подтвердить, что production не зависит от этого адреса, DNS/endpoint и
   provider instance не привязаны к AMN2 production.
4. Зафиксировать sanitized handover receipt без IP, password, SSH key,
   provider instance ID или raw logs.
5. Только после подтверждения передачи отдельным exact cleanup approval удалить
   локально dedicated staging SSH private key и только его known-host binding.
6. Не трогать production operator key, production known-host binding, старый
   recovery fallback, canonical recovery artifacts или production AWG.

## Prepared exact cleanup phrase

Не выполнять автоматически. После финального clean audit оператор может
отдельно разрешить только локальную очистку AMN2 staging-доступа фразой:

```text
APPROVE PHASE11_SECOND_VPS_AMN2_CLEAN_HANDOVER_AFTER_FINAL_READ_ONLY_AUDIT_AND_REMOVE_ONLY_DEDICATED_STAGING_SSH_KEY_AND_KNOWN_HOST_BINDING_WITH_PROVIDER_PRODUCTION_AND_AWG_UNTOUCHED
```

Эта фраза не разрешает provider deletion/cancellation, VPS wipe/reinstall,
remote file deletion или изменение нового функционала после передачи.
