# AMN2 Phase 10: canonical hybrid recovery replacement

Дата: 2026-07-14.

## Цель и граница

Закрыт остаточный DR-дефект первой full-recovery copy: metadata writer теперь
формирует отдельные canonical строки `source_overlay` и `container_name`, а
новая immutable copy выпущена и проверена без остановки production VPN.

Одновременно устранён небезопасный live CLI с передачей symmetric recovery key
через stdin. Новый writer принимает только RSA public key. Одноразовый Fernet
data key создаётся в памяти процесса, bundle шифруется authenticated Fernet,
а data key оборачивается RSA-OAEP с SHA-256. RSA private key никогда не
передавался на VPS и хранится отдельно от ciphertext с ACL текущего
пользователя.

## Код и тесты

Добавлены или усилены:

- `scripts/phase10_recovery_crypto.py`;
- `scripts/phase10_full_recovery_bundle.py`;
- `scripts/phase10_restore_rehearsal_verify.py`;
- focused tests для hybrid round-trip, tamper rejection, malformed envelope,
  minimum RSA size, writer/verifier integration и legacy Fernet compatibility.

Логические commits:

```text
dd87ea7 Add canonical full recovery writer
117b72c Use public-key recovery envelope
```

Проверки перед live-выпуском:

```text
focused_dr_tests=20_passed
root_tests=43_passed
python_compile=passed
diff_check=passed
diff_review=passed
legacy_fernet_verification=retained
live_symmetric_key_stdin=false
```

## Production bundle

Run ID: `20260714T045754Z`.

```text
source_overlay=1c7fb78
format=amn2-full-recovery-v1
encryption=rsa-oaep-sha256+fernet
artifact=amn2-recovery-20260714T045754Z.hybrid.enc
artifact_bytes=19220
artifact_sha256=2c618fa52aed038eb494a892480970795c554bddd6649156e1fe5a9c00e52280
member_files=13
manifest_entries=12
production_plaintext_written=false
recipient_private_key_transferred=false
service_restart_performed=false
```

Перед writer и после cleanup `amnezia-awg2` был `running=true` с
`restart_count=0`; `amneziya-web` остался active/enabled. Bot остался в
исходном intentional состоянии inactive/disabled. Ни один production service
не останавливался и не перезапускался. Temporary production tree удалён после
скачивания ciphertext и совпадения SHA-256.

## Локальная проверка и независимая копия

Ciphertext расшифрован только локально и в памяти verifier. Production
plaintext bundle на диск не записывался.

```text
decrypt=passed
metadata_contract=passed
metadata_warnings=[]
critical_contracts=passed
sqlite_integrity=ok
sqlite_foreign_keys=ok
sqlite_tables=12
awg_peers=12
awg_peer_psks=12
systemd_contract=passed
```

Secret-free sanitized fixture:

```text
sha256=d7845bdbd8623476bcfb81d6a602cfe8604aebd571a0ae38cc1c49bb36eab1d9
bytes=6281
archive_files=14
manifest_entries=13
sqlite_tables=12
sqlite_total_rows=0
production_secrets=false
service_start_allowed=false
```

Вторая encrypted copy записана в
`F:\AMN2-Recovery\20260714T045754Z`; её SHA-256 совпал. На носителе находятся
только ciphertext, `SHA256SUMS.txt` и `RECOVERY_INFO.txt`; private key туда не
копировался. Предыдущие copy и key от 2026-07-13 сохранены как fallback до
отдельного operator retirement decision.

## Изолированный staging rehearsal

На staging `45.95.232.7` передавался только sanitized tar, verifier и его
несекретный crypto module. Production ciphertext и оба recovery key туда не
передавались.

```text
sanitized_verify_extract=passed
systemd_analyze_verify=passed
start_guard_exit=64
runtime_installed=false
services_started=false
production_secrets=false
remote_tree_removed=true
post_cleanup_opt_amn2_absent=true
post_cleanup_amneziya_units_absent=true
post_cleanup_external_listener=ssh_22_only
```

Staging остаётся у того же provider и не считается независимым provider
failure domain; независимость ciphertext обеспечивает removable media `F:`.

## Решение

Metadata newline defect закрыт новой проверенной replacement copy. Старый
bundle остаётся читаемым legacy verifier и пока не удаляется. Этот DR-срез не
выполнял restore apply, не создавал peer/config, не отправлял Telegram delivery
и не расширяет Phase 10 launch gate. Полный restore с production secrets и
запуском runtime остаётся отдельным exact gate в доверенной disposable среде.
