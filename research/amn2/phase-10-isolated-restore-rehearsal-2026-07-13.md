# AMN2 Phase 10: isolated restore rehearsal

Дата: 2026-07-13.

## Цель и граница

Проверить восстановимость encrypted full-recovery bundle без остановки или
изменения production VPS и без передачи production recovery key либо plaintext
третьей стороне.

Реализован безопасный split:

1. Production bundle расшифровывается и проверяется только локально, в памяти.
2. Для staging создаётся новый schema-only fixture с нулём DB rows, redacted
   AWG material, пустым `servers.yml`, inventory только имён env keys,
   synthetic systemd units с `/bin/false` и блокирующим `start.sh`.
3. На staging разрешены только verify/extract и read-only проверки. Установка
   runtime, service start, peer/config mutation и network listener запрещены.

Production VPS `89.185.80.166` в rehearsal не использовался и не изменялся.

## Verifier

Добавлены:

- `scripts/phase10_restore_rehearsal_verify.py`;
- `tests/test_phase10_restore_rehearsal_verify.py`;
- commit `f1ec6ca` (`Add safe restore rehearsal verifier`).

Fail-closed contracts включают authenticated bundle hash/decrypt, archive size
limits, traversal/duplicate/non-regular rejection, exact manifest coverage,
SQLite integrity и foreign keys, AWG server-private-key binding, валидные
32-byte base64 public/PSK keys для каждого peer и exact sanitized file/content
allowlist. Hash и decrypt используют один immutable read; sanitized fixture
валидируется до записи и повторно после tar serialization.

AMN2 source `3c91601` подтвердил, что PSK создаётся отдельно для каждого
устройства. Поэтому standalone `wireguard_psk.key` проверяется как валидный
key material, но не обязан совпадать с одним из per-peer PSK.

## Local production verification

Источник независимой encrypted copy:

```text
source=F:\AMN2-Recovery\20260713T153359Z\amn2-recovery-20260713T153359Z.tar.gz.enc
source_sha256=3e2339fdbe7e78bcdd1ab90510e204acdffba0b09df5c4ae05dae64293136cb8
run_id=20260713T215439Z
decrypt=passed
production_plaintext_written=false
archive_files=13
manifest_entries=12
sqlite_integrity=ok
sqlite_foreign_keys=ok
sqlite_tables=12
awg_peers=12
awg_peer_psks=12
systemd_contract=passed
critical_contracts=passed
```

Recovery key остался только на operator workstation и на staging не
передавался. Production DB rows, env values, AWG keys и configs в evidence не
выводились.

## Sanitized staging rehearsal

Изолированная Ubuntu 24.04 VM: `45.95.232.7`, 4VPS Zurich. Перед rehearsal на
ней были включены key-only SSH и UFW default-deny; наружу разрешён только
`22/tcp`. Это тот же provider, что и production, поэтому VM пригодна для
изолированной технической репетиции, но не считается независимым provider
failure domain.

```text
sanitized_sha256=ff10c841946c8fa5725ef974360bb987dad942e8353ac5fae09ab80e0dd1ae59
sanitized_bytes=6265
archive_files=14
manifest_entries=13
exact_safe_contract=passed
sqlite_integrity=ok
sqlite_foreign_keys=ok
sqlite_tables=12
sqlite_total_rows=0
systemd_analyze_verify=passed
start_guard_exit=64
service_start_allowed=false
production_secrets=false
```

После скачивания secret-free report удалено всё remote rehearsal tree.
`/opt/amn2` отсутствует, AMN2 unit files не установлены, внешние listeners
после cleanup: только SSH; systemd-resolved слушает только loopback DNS.

Локальные ignored artifacts финального run:

```text
backups/amn2-recovery/restore-rehearsal-20260713T215439Z/local-production-verification.json
backups/amn2-recovery/restore-rehearsal-20260713T215439Z/staging-verification-report.json
backups/amn2-recovery/restore-rehearsal-20260713T215439Z/amn2-sanitized-rehearsal.tar.gz
```

## Обнаруженный дефект bundle metadata

Критические recovery contracts прошли, но `metadata.txt` исходного bundle
содержит склеенные без newline поля `source_overlay` и `container_name`.
Verifier корректно выдал:

```text
metadata_missing_container_name
metadata_source_overlay_mismatch
```

Отдельный `host/source_overlay_commit=1c7fb78` валиден, поэтому rehearsal
завершён как `passed_with_warning`. Следующий DR product slice: исправить
metadata writer и выпустить новую immutable encrypted recovery copy; старую
копию не удалять до полной проверки новой.

## Проверки и решение о запуске

```text
focused_restore_tests=11_passed
root_tests=34_passed
python_compile=passed
diff_review=passed
production_vps_touched=false
config_or_peer_action=false
launch_plan_change=false
live_restore_apply=false
```

Bare `pytest` без explicit scope не является корректной root-командой этого
orchestration repo: он рекурсивно собирает несколько вложенных package snapshots
и worktrees с одинаковыми module names. Канонический root scope `pytest tests`
прошёл полностью.

Полный restore с production secrets, запуском services и client acceptance
остаётся отдельным exact gate в доверенной disposable environment. Текущий
результат доказывает структуру, целостность, sanitization и операционную
процедуру, но не открывает live remediation или launch gate.
