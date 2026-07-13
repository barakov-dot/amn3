# AMN2 Phase 10: external full recovery backup

Дата: 2026-07-13.

## Причина

Provider incident показал, что DB-only backup недостаточен для сохранения
совместимости уже выданных конфигов. Для восстановления старых клиентов нужны
также AWG server private key и persistent peer configuration.

## Preflight

```text
vps_reachable=true
sqlite_integrity=ok
remote_cryptography=available
docker_copy=available
app_secret_presence=present_without_value_output
disk_space_sufficient=true
amnezia_awg2_running=true
```

## Состав

Bundle формата `amn2-full-recovery-v1` содержит:

- консистентную SQLite copy через `sqlite3.Connection.backup`;
- AMN2 `.env`, `servers.yml` и source overlay marker;
- AWG `awg0.conf`, server private/public keys и PSK material;
- container start file;
- web/bot systemd units;
- безопасную metadata и SHA-256 manifest.

Содержимое, ключи, конфиги, DB rows и env values в evidence не выводились.

## Шифрование и проверка

```text
encryption=Fernet_authenticated_encryption
artifact=backups/amn2-recovery/amn2-recovery-20260713T153359Z.tar.gz.enc
artifact_bytes=19000
artifact_sha256=3e2339fdbe7e78bcdd1ab90510e204acdffba0b09df5c4ae05dae64293136cb8
member_files=13
manifest_sha256_checks=12
local_decrypt_status=passed
sqlite_integrity_after_decrypt=ok
awg_recovery_contract=passed
host_runtime_contract=passed
```

Recovery key перемещён из workspace в отдельный каталог профиля пользователя,
имеет ACL только текущего пользователя и не отслеживается Git. Encrypted bundle
находится в `backups/`, который добавлен в root `.gitignore`.

## Cleanup и runtime

Remote plaintext stage, transient key и скачанная encrypted remote copy удалены.
Restore/import не выполнялись. VPN не останавливался и не перезапускался:

```text
container=running
restart_count=0
post_backup_rx_delta=5536
post_backup_tx_delta=167
service_restart=false
peer_mutation=false
config_delivery=false
telegram_action=false
```

## Остаток

Это первая внешняя копия вне VPS, но пока на одном operator workstation.
Следующий DR hardening: вторая encrypted copy на независимом носителе и
restore rehearsal в изолированной временной среде. Ни одно из этих действий не
расширяет launch gate и не разрешает production restore apply.
