# AMN2 Phase 13 — квитанция локальной проверки production disabled-stage и web/data-apply entrypoint

Дата проверки: 2026-08-08

Статус: `local_production_stage_entrypoint_verified_final_package_not_yet_materialized`

## Основание и границы

Проверен отдельный production entrypoint для disabled-stage и web/data apply
миграции bot/web с USA на Spain. Работа выполнена в изолированном
VPS-OPS-LAB worktree от exact base
`1b55f7c83c3453829e24af5dd11facedb2188447`. AMN2 worktree подтверждён
чистым и сохранён без изменений на exact head
`910539eaa8051cb1b59131d38b9fa27b9392744d`.

В проверенный scope вошли только:

- `scripts/phase13_bot_web_migration_production_stage_package.py`;
- `scripts/vps/phase13_bot_web_migration_production_stage_remote.py`;
- `scripts/vps/phase13_bot_web_migration_production_stage_runner.ps1`;
- `tests/test_phase13_bot_web_migration_production_stage.py`.

Reference scripts local-fake stage и cutover не изменялись. Их SHA-256:

- stage: `934bd8daa52f53ef7e0622f47c8c00a5691903de75d3993e9b90f5facd9fb425`;
- cutover: `b8a2db9401baacd2adf3698b6285aaebd0524efa0542429548dee92dec91f2b3`.

Expired и unclaimed outcome `bot-web-spain-stage-20260808-173758` не
использовался и не claimed. Verified merge outcome
`bot-web-merge-ledger-20260808-172510` остаётся immutable source будущей
materialization.

## Реализованный контракт

Public PowerShell entrypoint принимает только `PackageRoot` и
`ExactApprovalPhrase`. Он проверяет exact artifact set, canonical manifest,
expiry, `max_attempts=1`, SHA-256/size каждого artifact, fixed USA/Spain trust
bindings и создаёт claim до network. Production chain допускает ровно три
bounded SSH processes: два read-only audit и один self-contained Spain
stage/apply/verify/rollback process. User-overridable target, host, user, key,
port, trust root, remote path, service и mode отсутствуют; SCP, remote temp
package и retry отсутствуют.

Package builder расшифровывает verified merge inputs только локально в памяти.
До materialization он проверяет SQLite integrity и foreign keys merged
database, вычисляет отдельный SHA-256 фактических plaintext DB bytes и
связывает его с remote apply contract. Логический `merge_result_sha256`
сохраняется отдельно в immutable merge receipt и не подменяет DB-byte digest.
В sealed runtime delta допускаются только USA Telegram bot token и allowlisted
admin identifiers. Spain app secret, web password hash, session secret,
runtime и privileges сохраняются; USA API tokens, sessions, server/device
credentials и usable peer/config material не переносятся.

Remote executor имеет фиксированные Spain paths, fail-closed SIGHUP/SIGTERM
boundary и rollback после начала web-stop boundary. Stage пишет только в
protected migration root, не запускает и не включает bot и не создаёт enable
marker. Live mutation allowlist будущего gate ограничена bounded stop/start
Spain web и atomic replacement/rollback bot/web database.

## Equality и safety controls

Production preflight проверяет exact target-before DB/runtime, Spain web
active/enabled/healthy/loopback-only, Spain bot disabled/inactive/process-zero
и marker absent. AWG2 projection проверяет persistent/live peer equality `7/7`,
UDP `30001`, interface `awgsp0`, route `10.212.12.0/24` через `amn2spbr0`,
container network, restart count `59`, forwarding и ровно три tagged forward
rules. AWG Docker, firewall, network, peers/configs и issuance не изменяются.

Foreign projection сохраняет Phase 12 canonical container/unit semantics,
исключает только AMN2-owned contour, требует `153` persistent entries и exact
stable SHA-256
`f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8`.
Она проверяется до и после Spain-затрагивающей операции, а также после
rollback. Foreign service mutation отсутствует.

## Локальная проверка

- новый focused production-stage test: `24 passed`;
- утверждённый aggregate BOT/WEB + Phase 12 Spain regression scope:
  `175 passed`;
- Python compilation и PowerShell parse: passed;
- `git diff --check`: passed;
- scoped secret scan: `0` secret-material matches;
- scoped mutation review: только fixed protected-root writes, bounded Spain
  web stop/start и atomic DB replace/rollback входят в будущий exact live
  allowlist;
- manual scoped security review: reportable findings `0`.

Новый broad security scan и durable security report не создавались. Все тесты
использовали только local fake SSH/filesystem/service/SQLite harness. Real SSH,
data transfer, live DB apply, service action, bot cutover, USA release и любые
Spain/USA/AWG live mutation не выполнялись.

## Следующая граница

После отдельного commit/push этого verified scope разрешена только локальная
materialization свежего checksum-bound final migration package из committed
production bytes и verified merge artifacts. Сам package не является live
approval. До literal exact approval запрещены SSH, Spain stage/web-data apply,
bot cutover и USA release.

Phase 13 ограничена завершением bot/web migration и достижением
`USA_REINSTALL_READY`. AWG3 полностью перенесена в Phase 14 и в этот scope не
входила.
