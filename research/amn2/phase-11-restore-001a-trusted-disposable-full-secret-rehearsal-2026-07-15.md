# Phase 11 RESTORE-001A trusted disposable full-secret rehearsal

Дата: 2026-07-15.

## Решение

`PHASE11-RESTORE-001A=PASS` для production source pin `801f8c3`.

Полученный ранее exact approval был исполнен только на trusted disposable VPS.
Production source, web, database, regular bot и AWG не изменялись. Production
AWG не останавливался, не перезапускался и не пересоздавался.

## Canonical recovery input

```text
format=amn2-full-recovery-v2
source_overlay=801f8c3
encrypted_bundle_sha256=22fc6fcdf94405187db448d3ffd97a170829aaf3a64794cae416e05a8ac490ff
source_archive_sha256=6c58c33fc5b152114f651cece46cd99955758198e25e67e3c422ed5ca1f8166e
image_layers=6
image_compressed_layers=6
runtime_image_identity=legacy_runtime_id_bound_to_config_and_rootfs
repo_tags=null
```

Encrypted bundle прошёл external, local и in-memory validation. Local plaintext
не создавался. Recovery private key на disposable VPS не передавался.

## Scoped diagnostic progression

Все промежуточные failures завершались fail closed и обязательным cleanup.
Перед новым шагом disposable VPS повторно подтверждался как clean SSH-only host;
после secret-bearing attempts дополнительно повторялись production runtime и OPS
audits.

Подтверждённые compatibility/verification fixes:

1. package inventory сравнивается с одинаковым `LC_ALL=C`;
2. listener inventory нормализован до protocol и local endpoint; transient
   listener допускается только как единственный TCP loopback high-port владельца
   `containerd`;
3. canonical wheelhouse tar root `.` разрешён только как нулевая directory entry;
4. runtime image inspect/create использует аттестованный legacy runtime image ID,
   а archive config digest остаётся отдельной self-hash проверкой;
5. configured AWG addresses обязательны, а дополнительные адреса допускаются
   только как валидные IPv6 link-local;
6. systemd `IPAddressDeny=any` и `IPAddressAllow=localhost` проверяются по точным
   canonical CIDR sets, которые возвращает `systemctl show`.

Safe failure output ограничен allowlisted stage/reason codes. Raw Docker,
systemd, AWG config, secret, key, database и address values не выводились.

## Scoped tests and review

```text
safe_stage_observability=passed
listener_endpoint_normalization=passed
containerd_loopback_admission=passed
canonical_dot_root_wheelhouse_exact_parser=passed
dependency_offline_install=passed
runtime_tests=29_passed
legacy_runtime_image_id_binding=passed
awg_failure_reason_allowlist=passed
awg_ipv6_link_local_policy=passed
systemd_canonical_ip_policy_exact_set=passed
success_output_noise_redaction=passed
helper_syntax_and_hash_pins=passed
security_review=ready|new_reportable_findings_0
```

Offline dependency slice проверил 40 pinned wheels, exact hash lock,
`--no-index --require-hashes`, install/import под `amneziya` с network deny и
отсутствие residual process до secret stream.

## Successful full-secret evidence

```text
staging_static_verify=passed
staging_runtime_contract=passed
staging_critical_contracts=passed
plaintext_stream=passed|bytes_20118420
local_plaintext_written=false
private_key_transferred=false
staging_awg=passed|running_true|restart_0|peers_12
staging_awg_peer_key_psk_allowed_ips_match=true
staging_awg_interface_and_config_hash_match=true
staging_awg_internal_network=true
staging_awg_default_route=false
staging_awg_host_port_publication=false
staging_awg_link_local_only_extra=true
staging_web=passed|loopback_only|login_200|outbound_denied
staging_database=integrity_ok|counts_schema_values_file_hash_unchanged
staging_bot_started=false
telegram_api_called=false
production_contact_performed=false
staging_runtime=passed
```

## Mandatory cleanup and re-audit

```text
staging_cleanup=passed
staging_plaintext_source_database_awg_runtime_removed=true
staging_packages_versions_apt_marks_listeners_docker_state_restored=true
second_vps_audit=pass|amn2_absent|docker_absent|containers_0|artifacts_0|failed_units_0
second_vps_external_tcp=22
second_vps_external_udp=none
production_runtime_contract=pass
production_overlay=801f8c3
production_web=active_enabled_restart_0
production_bot=inactive_disabled_process_0
production_database=integrity_ok|foreign_keys_0
production_awg=running|restart_0|peers_12|peer_set_unchanged
telegram_api_called=false
```

## Разблокированные, но не исполненные решения

- Старый recovery fallback/key теперь можно рассматривать для отдельного exact
  destructive retirement gate. В этом rehearsal ничего не удалялось.
- Второй VPS больше не требуется для `RESTORE-001A`. Рекомендация — отдельный
  provider retirement gate после финального retention/billing read-only review;
  provider deletion и локальное удаление staging SSH binding не выполнялись.
- Canonical logo commit `6abc620` остаётся local/source-only: production overlay
  всё ещё `801f8c3`, Telegram profile photo не менялась.
- `TELEGRAM-002A` остаётся local engineering hardening; production bot остаётся
  inactive и disabled.
