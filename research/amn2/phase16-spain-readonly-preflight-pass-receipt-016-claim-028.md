# Phase 16 — package 016: Spain read-only preflight PASS, claim 028

Дата: 2026-08-28. Квитанция одного завершённого read-only прогона; не разрешение на stage, install или выпуск конфига.

## Результат и границы

- Decision: `pass`; runner exit: `0`; SSH attempts: `1/1`.
- Claim: `phase16-spain-preflight-20260828-028`; terminal status: `completed`, reason: `not_applicable`.
- Окно наблюдения UTC: `2026-08-28T04:30:34Z`–`2026-08-28T04:30:37Z`; Europe/Moscow: 07:30:34–07:30:37.
- Все 23 нормализованных наблюдения приняты; stop/unknown и stop reasons отсутствуют.
- `awg2_health=pass`; AWG3.1 resources free; recovery markers absent.
- Пользователь сообщил, что включил AWG2, затем прислал точный checksum-bound approval. Само сообщение о включении не использовалось как разрешение SSH.
- AWG2 freshness policy неизменна: максимум 600 секунд. PASS относится к окну наблюдения и не доказывает стабильность или скорость AWG2.
- Safety: `ssh_used=true`, `remote_file_written=false`, `live_mutation=false`, `raw_output_persisted=false`.
- Stage/install/client config/peer issuance/global issuance: `0`; AWG2 mutations: `0`.
- Не было дополнительных SSH, collector, diagnostic или preflight retries.
- Package 016 и package 015 не изменялись; materialization, package verifier и регрессии повторно не запускались.

## Exact approval и package bindings

Markdown underscore escaping нормализовано только при интерпретации пользовательского approval.

```text
/APPROVE PHASE16 SPAIN READONLY_PREFLIGHT_EGRESS TO_138.124.181.246 PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-016 IDENTITY_c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b MANIFEST_SHA256_e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc COLLECTOR_SHA256_fdda3146d2e98f544d10b56c2a0d27a2e2039f1b8738bee5d39a6fc14c74b75e RUNNER_SHA256_9e99821cbd7eb7d223b257046cb178e99672d6c1b9cd0b08ed8be374345e5b26 NO_REMOTE_WRITE NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-016`.
- Identity: `c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b`.
- Manifest SHA256: `e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc`.
- Collector SHA256: `fdda3146d2e98f544d10b56c2a0d27a2e2039f1b8738bee5d39a6fc14c74b75e`.
- Preflight runner SHA256: `9e99821cbd7eb7d223b257046cb178e99672d6c1b9cd0b08ed8be374345e5b26`.
- Packaged preflight contract SHA256: `3bba7a103a228202b06161c4358b80f25ad6c172eede167ade664aff39bf5e4d`.
- Pre-run HEAD: `1a5c1837c1c8d4b6d42ef500e7a87b093ad5ab0a`; branch `codex/phase16-awg3-family-3-1-spain-pilot-016`; clean linked worktree.
- Использовался immutable packaged runner. До запуска совпали exact hashes/identity, локальный SSH trust bundle и свободный claim. Strict host checking не отключалось; key/known_hosts contents не выводились.
- Windows PowerShell launched with process-local `-NoProfile -NonInteractive -ExecutionPolicy Bypass`; child PSModulePath removed. No machine/user policy change.

## Локальное evidence

- Issued claim: `2026-08-28T04:29:44Z`; expires: `2026-08-28T04:34:44Z`.
- Canonical future-claim SHA256: `68bf341d26b441f1a09fc6e4c6b2e6ad725258b9e160e7d037e00c2601a3ad22`.
- Future claim был canonical UTF-8 без BOM с ровно одним LF; packaged claim validator подтвердил его до вызова runner.
- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260828-028.json`.
- Outcome bytes: `3616`.
- Outcome SHA256 / observed current-state SHA256: `b2fb288632b0b2c85e3d8c7f2391aa04ee972b1f6629b9da3ddc27c142323976`.
- Terminal claim: `C:\ProgramData\AMN2\phase16\readonly-preflight\claims\phase16-spain-preflight-20260828-028.json`.
- Terminal claim SHA256: `12ee23c467419a1ad03d81f4f368f89297b816ca426c40bf1c6f2130b179277d`.
- Transport disposition: `read_only_completed`.
- Canonical JSON и точное byte-for-byte восстановление evidence через packaged `bind_evidence` проверены локально. Это не новый preflight и не повторный package verifier.
- Terminal claim проверен на exact claim_id, ended_at, completed и not_applicable.
- После проверки исходного SHA удалена только созданная локальная копия `tmp/phase16-spain-preflight-20260828-028.future.json`. Terminal claim/outcome оставлены; consumed claim не переиспользуется. Временная копия содержала только перечисленные несекретные claim bindings.

## Нормализованные наблюдения

- present: `application_state`, `database_state`.
- pass: `architecture`, `awg2_health`, `backup_capability`, `container_capability`, `disk_space`, `firewall`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, `telegram_prerequisites`.
- free: `bridge_amn2sp3br0`, `config_path`, `container_cidr_172_29_252_0_28`, `container_name`, `interface_awg3`, `service_name`, `state_root`, `udp_30002`, `vpn_cidr_10_212_13_0_24`.
- absent: `recovery_markers_phase14_phase15_phase16`.

Сырые выводы серверных команд, private keys, конфиги, raw traffic и packet captures не сохранялись.

## Локальная проверка после прогона

- Незавершённые preflight transactions: `0`; recovery outcomes для claim 028: `0`.
- Оставшиеся Spain SSH процессы: `0`; preflight runner процессы: `0`.
- Claim lock, outcome lock и namespace lock — штатные retained zero-byte files. Освобождение каждого подтверждено read-only открытием существующего файла с `FileShare.None`; handle закрыт, сами lock files не изменены/не удалены.
- Локальные артефакты предложенной stage transaction 007: `0`.
- Последняя локальная проверка locks UTC: `2026-08-28T04:33:09.8248967Z`.
- Это локальные проверки завершения; они не обновляют удалённые наблюдения и не являются непрерывным мониторингом.

## Следующий gate: controlled server-only stage

Предлагаемая новая транзакция: `phase16-spain-stage-20260828-007`. Transaction 006 consumed и не переиспользуется. Stage не запускался; текущий preflight approval не разрешает его.

Stage/rollback asset metadata сверены с manifest; ни stage runner entrypoint, ни coordinator main/execute_stage не вызывались:

- `tooling/packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json`: `dea2c165c4fe0e2959f34e78b722980ba810ea7c9546a2ad1aaaaf5917af82f3`.
- `tooling/scripts/vps/phase16_application_stage_remote.sh`: `6454a6ff52f6f608f126aae7989e74666393d0da6f84c13533d99cb273b9e9f8`.
- `tooling/scripts/vps/phase16_awg31_runtime_stage_remote.sh`: `1aca96948c346286c0e1d5767e4de72778c70ff73faabd3a30b9a3f6e14626ea`.
- `tooling/scripts/vps/phase16_controlled_stage_coordinator.py`: `a016adbdcbf9acd57f6e96e9ffeb5f2289b5b9c1dbe2008e84b36984dbfae4ee`.
- `tooling/scripts/vps/phase16_controlled_stage_ssh_runner.ps1`: `6364d652181cd6f522dbecd25e2c4b36e8c1d06736cb67a2e6a3e4894da7dd77`.
- `tooling/scripts/vps/phase16_stage_support.py`: `67f991d909bbc398afee9e84063728645cb234b96a94a86ae5c61d77d20e4487`.

Intended resources:

- Application release: `/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-016`.
- Current DB: `/var/lib/amn2-spain/amn2.sqlite3`; Python SQLite online backup с checksum binding; backup сохраняется при rollback.
- Dedicated Docker: `/opt/amn2-spain/docker/bin/docker`; socket `unix:///run/amn2-spain-docker/docker.sock`.
- AWG3 state/config: `/var/lib/amn2-spain/awg3`, `/var/lib/amn2-spain/awg3/awg3.conf`.
- Service/container: `amn2-spain-awg3.service` / `amn2-spain-awg3`.
- Network/bridge/interface: `amn2sp3` / `amn2sp3br0` / `awg3`.
- UDP `30002`; container CIDR `172.29.252.0/28`; VPN CIDR `10.212.13.0/24`; server address `10.212.13.1/24`.
- Runtime: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`; source `1f50ad736ecca22a9bfc7b4606805ec9ca49fe48`.
- Protocol `awg3 / 3.1 / amneziawg_v3_1`; required capabilities `disable_cookies`, `random_trailers`.
- Server-only config, zero peers; no client config/issuance; general issuance remains disabled; AWG2 untouched.

Canonical rollback scope SHA256: `9efad64c2a6bfa717d02da9967c49e049e31425722037d91c8d519c31d75fdb2`. Mandatory rollback on failure остаётся обязательным; только созданные транзакцией ресурсы из этого scope, без AWG2 и без удаления checksum-bound backup:

```json
{
  "application_ledger": "/var/lib/amn2-phase16/stage/application.json",
  "application_release": "/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-016",
  "backup_policy": "preserve_checksum_bound_sqlite_backup",
  "coordinator_ledger": "/var/lib/amn2-phase16/stage/coordinator.json",
  "package_root": "/var/lib/amn2-phase16/package",
  "runtime_ledger": "/var/lib/amn2-phase16/stage/awg31-runtime.json",
  "runtime_resources": [
    "/etc/systemd/system/amn2-spain-awg3.service",
    "/var/lib/amn2-spain/awg3",
    "container:amn2-spain-awg3",
    "network:amn2sp3"
  ],
  "schema": "amn2.phase16.controlled-stage-rollback-scope.v1"
}
```

Первый операторский клиент по текущему плану — АРМ/Windows. Immutable resource-plan сохраняет исходную Android baseline-кандидатуру; она не является подтверждением установленного АРМ-клиента. Pilot/client admission требует следующего отдельного gate после принятого stage.

Exact следующий approval — только предложение, не исполнено:

```text
/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-016 IDENTITY_c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b MANIFEST_SHA256_e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc STATE_b2fb288632b0b2c85e3d8c7f2391aa04ee972b1f6629b9da3ddc27c142323976 ROLLBACK_SCOPE_SHA256_9efad64c2a6bfa717d02da9967c49e049e31425722037d91c8d519c31d75fdb2 TRANSACTION_phase16-spain-stage-20260828-007 MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED
```

## Статус Phase 16

- ✅ Task 0 — baseline.
- ✅ Task 1 — проверенный package 016.
- ✅ Task 2 — Spain read-only preflight PASS, claim 028.
- ▶️ Task 3 — controlled stage после отдельного approval.
- ⏳ Task 4 — первый AWG3.1-конфиг для АРМ.
- ⏳ Task 4.5 — обязательная AWG2 ↔ AWG3.1 transport-quality A/B-проверка.
- ⏳ Task 5 — клиентская acceptance после Task 4.5.
- ⏳ Task 6 — closeout.

Проблема нестабильности/скорости AWG2 остаётся открытой для Task 4.5; health PASS не считается её исправлением.

Квитанция подлежит одному scoped local commit. Push не выполнялся: отдельное informed approval публичной публикации накопленной истории остаётся обязательным. Рабочая ветка/worktree сохраняются; никаких package/code edits, повторных suites/verifier или live действий для receipt commit.

Профиль следующего live-impact gate по утверждённому плану: GPT-5.6 SOL / High. Это рекомендация, не разрешение на stage и не утверждение о текущем runtime model/effort.
