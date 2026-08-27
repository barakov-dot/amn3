# Phase 16 — package 015: read-only preflight PASS после операторского AWG2-трафика

Дата: 2026-08-27. Это локальная квитанция одного завершённого прогона, не разрешение на stage или выпуск конфига.

## Результат и границы

- Decision: `pass`; runner exit: `0`; SSH: `1/1`.
- Claim: `phase16-spain-preflight-20260827-027`; terminal status: `completed`, reason: `not_applicable`.
- Окно наблюдения: `2026-08-27T16:58:05Z`–`2026-08-27T16:58:21Z` (19:58:05–19:58:21 Europe/Moscow).
- Все 23 наблюдения приняты package-bound валидатором; `stop`/`unknown` отсутствуют.
- `awg2_health=pass`; политика `MAX_HANDSHAKE_AGE_600S` не менялась.
- Пользователь подтвердил, что трафик был и VPN уже отключён. Повторно включать VPN для этого завершённого preflight не требовалось.
- Результат описывает указанное окно наблюдения, а не непрерывный мониторинг или гарантию качества AWG2.
- Remote write: `false`; live mutation: `false`; raw output persisted: `false`; SSH used: `true`.
- Stage/install/config/issuance: `0/0/0/0`; AWG2 untouched.
- Package 015 не изменялся; materialization, полный package verifier и регрессии повторно не запускались.

## Основание и неизменяемые bindings

Пользователь дал точный `READONLY_PREFLIGHT_EGRESS_AFTER_OPERATOR_AWG2_TRAFFIC` approval для одного нового preflight; общее продолжение /GO не использовалось как замена approval.

- Target: `138.124.181.246`.
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`.
- Manifest SHA256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`.
- Collector SHA256: `244601519bdb7fa003af4dcb0eb8140d946cf8239e83b1098b2242d7d22db992`.
- Runner SHA256: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`.
- Preflight contract SHA256: `8d37a4f02e7a5bc7d82a19545a11f4138836e660838653506b7a94c570120d6b`.
- Previous preflight outcome SHA256: `752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80`.
- Previous diagnostic normalized stdout SHA256: `559fbab5aec0afda366f4232b81bdefc4cf7c71b32e0a32f98820dd9a630667b`.
- Previous diagnostic receipt SHA256: `8644f4c0296b627533d82f71a843d917da4698a3550a4de34f618475a1b936d1`.
- Accepted local scope receipt SHA256: `24ff7d25ad55666da25dacf4ffd52d81f1d70ab7af5fa87ce0dbf43dcb89af11`.
- Pre-run HEAD: `01edf3ffd1555b9ca3941f45d02d7ec621d325fd`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-015`.

Исторический STOP claim 026, диагностическая квитанция и подготовительный scope не переписывались. Новый PASS опубликован только как отдельный outcome claim 027.

## Локальные evidence

- Issued claim: `2026-08-27T16:57:08Z`; expiry: `2026-08-27T17:02:08Z`.
- Canonical future-claim SHA256: `d074bd883e7baa22f44169f2030923297f025322dc14fc280b2637ebca70896c`.
- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260827-027.json`.
- Outcome bytes: `3616`.
- Outcome SHA256 / observed current-state SHA256: `e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92`.
- Terminal claim: `C:\ProgramData\AMN2\phase16\readonly-preflight\claims\phase16-spain-preflight-20260827-027.json`.
- Terminal claim SHA256: `badd633649f4264b761a8e4b193401e71e7c1128271bc8291f86535c6246c622`.
- Transport disposition: `read_only_completed`.

Canonical JSON и точное восстановление evidence через packaged `bind_evidence` проверены локально. Это проверка результата, не новый collector/preflight.

Временная локальная копия issued claim `tmp/phase16-spain-preflight-20260827-027.future.json` удалена после сверки SHA256. Terminal claim и outcome сохранены; использованный claim не подлежит повторному запуску.

## Нормализованные наблюдения

- Present: `application_state`, `database_state`.
- Pass: `architecture`, `awg2_health`, `backup_capability`, `container_capability`, `disk_space`, `firewall`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, `telegram_prerequisites`.
- Free: `bridge_amn2sp3br0`, `config_path`, `container_cidr_172_29_252_0_28`, `container_name`, `interface_awg3`, `service_name`, `state_root`, `udp_30002`, `vpn_cidr_10_212_13_0_24`.
- Absent: `recovery_markers_phase14_phase15_phase16`.

Сырые выводы, конфиги, ключи, packet capture и иной raw traffic не сохранялись.

## Локальная проверка после завершения

- Незавершённые preflight transactions: `0`.
- Recovery outcomes / outcome-lock residues для claim 027: `0/0`.
- Оставшиеся Spain SSH / preflight runner процессы: `0/0`.
- Штатный claim lock: zero-byte, retained, released.
- Освобождение lock проверено read-only открытием существующего файла с `FileShare.None`, затем handle закрыт. Файл не удалялся и не переписывался: runner по контракту сохраняет файл и освобождает handle.
- Outcome, terminal claim, исходный future claim и предыдущие evidence повторно совпали по SHA256.
- Локальные outcome и runner-failure для предложенной stage transaction 005 отсутствуют.
- Дополнительные SSH, collector, diagnostic и preflight retries не выполнялись.

Проверки после прогона были локальными. Они не являются новым удалённым наблюдением.

## Следующий gate: controlled server-only stage

Stage не запускался и не разрешён текущим preflight approval. Следующая предлагаемая транзакция: `phase16-spain-stage-20260827-005`. Transaction 004 consumed, не переиспользовать.

Метаданные следующих assets сверены с package manifest; их entrypoints не запускались:

- `resource-plan.json`: `6268b67ced3b397fd9991453f0f3bca73fe43bc14d3c5c687adde0cbbcb57da4`.
- `phase16_application_stage_remote.sh`: `b52dec1f9e9de262bd7c3ddb3ae9fb9c9d58b5e0f526d839c168878fe41afec3`.
- `phase16_awg31_runtime_stage_remote.sh`: `ad48758ea627b258a5389e15ccf9f883cbb182afcd9beef5016300c22795bec6`.
- `phase16_stage_support.py`: `7d3a88a3d170a41c4fd0307296b1b0932e6835c06f417e4c48284cea967abf00`.
- `phase16_controlled_stage_coordinator.py`: `2dccc21218ae6f6b7e28ac68f8c624aa8c9f55410638f7d9b7205a43660d2fc5`.
- `phase16_controlled_stage_ssh_runner.ps1`: `8eb9e2896a58c1cf70a493fcd8f00fd16764505ccdaaca940d78d6ae13a825e7`.

Intended stage resources:

- Application release: `/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-015`.
- Current DB: `/var/lib/amn2-spain/amn2.sqlite3`; checksum-bound Python SQLite online backup сохраняется при rollback.
- Dedicated Docker: `/opt/amn2-spain/docker/bin/docker`, `unix:///run/amn2-spain-docker/docker.sock`.
- AWG3 state/config: `/var/lib/amn2-spain/awg3`, `/var/lib/amn2-spain/awg3/awg3.conf`.
- Service/container: `amn2-spain-awg3.service` / `amn2-spain-awg3`.
- Network/bridge/interface: `amn2sp3` / `amn2sp3br0` / `awg3`.
- UDP: `30002`; container CIDR: `172.29.252.0/28`; VPN CIDR: `10.212.13.0/24`; server: `10.212.13.1/24`.
- Runtime: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`.
- Protocol: `awg3 / 3.1 / amneziawg_v3_1`; runtime capabilities: `disable_cookies`, `random_trailers`.
- Server-only config, zero peers; general issuance остаётся выключенным; AWG2 untouched.

Rollback scope SHA256: `15d6fe8bd131a56bf4d5a6545d4cd7ecf22a785f1da916de6410cd9d9e5167b3`. Scope включает application release, package root, application/runtime/coordinator ledgers, перечисленные AWG3 runtime resources и политику сохранения checksum-bound SQLite backup. Mandatory rollback on failure сохраняется.

Первый операторский клиент по текущему плану — АРМ/Windows; Android и iPhone проверяются отдельно. Immutable resource-plan содержит исходную Android baseline-кандидатуру: она здесь не менялась и не доказывает совместимость АРМ. Pilot config и client acceptance требуют своего следующего gate.

Точный следующий approval (не исполнен):

```text
/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 MANIFEST_SHA256_f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74 STATE_e7b83199c3cef351964746a9f3a60ab665f632f8b4c4a5f8b0ad58494db44c92 ROLLBACK_SCOPE_SHA256_15d6fe8bd131a56bf4d5a6545d4cd7ecf22a785f1da916de6410cd9d9e5167b3 TRANSACTION_phase16-spain-stage-20260827-005 MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED
```

## Статус Phase 16

- ✅ Task 0 — baseline.
- ✅ Task 1 — проверенный package 015.
- ✅ Task 2 — Spain read-only preflight PASS, claim 027.
- ▶️ Task 3 — controlled stage после отдельного approval.
- ⏳ Task 4 — первый AWG3.1-конфиг для АРМ.
- ⏳ Task 4.5 — обязательная AWG2 ↔ AWG3.1 A/B-проверка.
- ⏳ Task 5 — клиентская acceptance после Task 4.5.
- ⏳ Task 6 — closeout.

Проблема нестабильности/скорости AWG2 остаётся предметом Task 4.5, не считается решённой успешным health gate.

Локальная квитанция подлежит отдельному scoped commit. Push не выполнялся: информированное подтверждение публикации накопленной истории в публичный origin остаётся отдельной границей.

Профиль по плану для следующего live-impact gate: GPT-5.6 SOL / High. Рекомендация модели не является разрешением на действие.
