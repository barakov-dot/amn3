# AMN2 Phase 13: перенос bot/web с USA на Spain — design spec

Дата: 2026-08-02.

## 1. Решение

AMN2 переносит existing private Telegram bot, web-панель и требуемое
application state с USA на уже принятую Spain installation. USA не считается
освобождённой, пока одновременно не выполнены:

1. checksum-bound encrypted source backup;
2. versioned logical database merge в копию Spain DB;
3. Spain web/data stage и acceptance;
4. single-instance bot cutover с USA на Spain;
5. rollback и postflight evidence;
6. отдельное operator confirmation, что USA можно переустанавливать.

Эта спецификация не разрешает implementation, package build, data transfer,
database write, service action, Telegram API call, deploy, cutover, USA
shutdown/reinstall/reuse или любую AWG mutation.

## 2. Authoritative baselines

```text
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
spain_operational_overlay=f1bf099ddb47da26a4080714376babaf5b0de92c
usa_production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
phase13_root_head_at_audit=0435090fb6d34d3e6aab368b776992619ab49ce1
audit_receipt=research/amn2/phase13-usa-spain-bot-web-migration-readonly-audit-2026-08-02.md
```

Git ancestry показывает, что `0b858c5` является merge-base и предком
`55dc243`. Spain source уже включает USA bot/web behavior и более новые Spain
lifecycle surfaces. Source overlay с USA не копируется и downgrade не
выполняется.

Accepted Spain state остаётся обязательным invariant:

- один user и семь active/indefinite d1–d7;
- семь device passports, lifecycle events и completed issuance receipts;
- DB/persistent/live peer equality 7/7/7;
- AWG running, restart count 59;
- ровно три AMN2-tagged forward rules;
- foreign persistent equality: entries 153, changed 0, stable SHA-256
  `F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8`;
- foreign equality receipt SHA-256
  `BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704`;
- Spain web только `127.0.0.1:3031`;
- Spain bot inactive/static с отсутствующим enable marker.

## 3. Audit facts

Read-only audit подтвердил:

| Surface | USA | Spain |
|---|---:|---:|
| Web | active/enabled, loopback `3030`, healthy | active/enabled, loopback `3031`, healthy |
| Bot | active/enabled, restart 0 | inactive/static, restart 0 |
| DB integrity/FK | ok / 0 | ok / 0 |
| Tables | 15 | 18 |
| Total rows | 88 | 46 |
| Users | 6 | 1 |
| Devices | 8 | 7 |
| Plans/orders | 8/8 | 0/0 |
| API tokens | 12 | 0 |
| Admin actions | 45 | 14 |
| Configured bot admins | 2 | не настроены в текущем runtime env |

Одноразовый secret-safe HMAC proof установил, что bot token,
`APP_SECRET_KEY`, web password hash и web session secret различаются.

## 4. Рассмотренные варианты

### Вариант A: blind USA DB restore

Отклонён. Он заменил бы Spain server/device/passport/issuance state, сделал бы
USA encrypted device material несовместимым с Spain `APP_SECRET_KEY` и нарушил
бы d1–d7/foreign equality.

### Вариант B: чистый запуск bot/web без данных

Отклонён. Он не переносит шесть users, планы, orders, legacy-device history и
existing Telegram identity.

### Вариант C: encrypted source snapshot + logical merge + disabled stage

Принят. Он сохраняет Spain как target source of truth, переносит полезное
application state по явной таблице policy и отделяет data/web acceptance от
single-instance Telegram cutover.

## 5. Package topology

Будущий package имеет плоский checksum-bound artifact root:

```text
phase13-bot-web-migration/
  manifest.json
  migration-plan.json
  source-audit.json
  target-audit.json
  source-full-backup.enc
  source-full-backup.manifest.json
  target-before-backup.enc
  target-before-backup.manifest.json
  merged-target.sqlite3.enc
  merge-preview.json
  rollback-plan.json
  remote-stage.sh
  remote-cutover.sh
  ssh-runner.ps1
```

Manifest связывает SHA-256 каждого artifact, exact source/target role,
source/target schema SHA-256, source/target counts SHA-256, root/source heads,
approval expiry и unique outcome ID. Archive/container image/AWG runtime
package не создаются.

Encryption key не хранится внутри artifact root. Manifest и receipts содержат
только secret classes, sizes и checksums, а не raw values.

## 6. Database migration policy

Spain DB всегда является target. Работа начинается с SQLite online backup
Spain DB в приватный temporary file; source USA DB открывается только
read-only. Preview не пишет live database.

### 6.1 Live merge

| Table/data | Policy |
|---|---|
| `users` | Merge по `telegram_id`; отсутствующие users создаются. Existing Spain row и `is_admin` не перезаписываются. `operator_label` collision fail closed. |
| `plans` | Создать отсутствующие exact IDs. Existing ID с отличающимися duration/max_devices/price/currency/free/active блокирует apply. |
| `orders` | Импортировать с remapped user/plan/device IDs и исходными status/timestamps. Source/target ID binding фиксируется в migration ledger. |
| `devices` | Импортировать только как `external_only`, `revoked`, без usable private/PSK material и без peer apply. Legacy USA server представлен disabled metadata-only record без host/credential binding. |
| `message_templates` | Exact-key create; divergent existing key блокирует apply. На текущем audit source/target counts равны 0. |
| migration ledger | Новая таблица хранит migration ID, source table, source row fingerprint и target ID для idempotency; raw source identifiers и secrets в receipt не выводятся. |

### 6.2 Archive-only или excluded

| Table/data | Policy |
|---|---|
| `admin_actions` USA | Сохранить в encrypted source backup; не смешивать с canonical Spain admin audit. В live DB записать только одну aggregate migration action. |
| `api_tokens` | Не импортировать token hashes и не активировать. Preview сообщает `reissue_required=12`. |
| `servers`, health, ignored peers, traffic | Не импортировать. Spain server remains authoritative. |
| USA device private keys/PSK/configs | Не импортировать и не перевыпускать. |
| enrollment/recovery tokens | Не импортировать независимо от expiry. |
| USA sessions | Не переносить. |
| Spain passports, issuance requests/receipts, lifecycle and assignment rows | Сохранить byte/row-equivalent; source USA не может их перезаписать. |

### 6.3 Merge invariants

До и после merge-copy должны совпасть:

- Spain server row fingerprint;
- семь d1–d7 row fingerprints и peer public-key set hash;
- семь passport fingerprints;
- два issuance request и семь completed receipt fingerprints;
- seven lifecycle event fingerprints;
- schema initialized from exact `55dc243`;
- `PRAGMA integrity_check=ok` и foreign-key issues `0`.

Любой ambiguous user/plan/device/order mapping завершает preview как
`not_approved`; apply package не создаётся.

## 7. Secret policy

### Переносится только через encrypted package

- existing USA `TELEGRAM_BOT_TOKEN`;
- allowlisted `ADMIN_TELEGRAM_IDS`;
- полный USA recovery snapshot для rollback/archive;
- source DB and required application metadata.

### Не заменяется на Spain

- Spain `APP_SECRET_KEY`;
- Spain web password hash;
- Spain web session secret;
- Spain AWG/server keys and configs;
- Spain SSH trust bundle.

### Не оживляется

- USA API tokens;
- USA sessions;
- enrollment/recovery tokens;
- USA device private keys, PSK и generated configs.

При stage runtime env обновляется атомарно из exact before/after hashes. Raw
env не появляется в manifest, receipt, terminal или journal.

## 8. Service lifecycle

### 8.1 Package preparation

Только read-only source/target collection, encrypted backup, offline merge
preview и local verification. Spain и USA services не меняются.

### 8.2 Spain stage

- package checksums verified;
- bot token/admin identifiers staged в protected env;
- bot marker отсутствует;
- bot inactive/process 0;
- web остаётся active на `127.0.0.1:3031`;
- merged DB staged как отдельный file, не live target;
- USA bot остаётся active.

### 8.3 Web/data apply

Отдельный exact approval разрешает bounded Spain web maintenance:

1. подтвердить bot inactive и USA bot active;
2. сделать encrypted backup-before-write Spain DB/env;
3. остановить только Spain web;
4. atomic DB replacement из verified merged copy;
5. сохранить Spain web credentials/session secret;
6. запустить Spain web;
7. проверить loopback-only listener, login, DB integrity/FK и d1–d7 invariants;
8. при любой ошибке восстановить exact Spain DB/env и web state.

AWG, Docker AWG container, network, firewall и foreign service не трогаются.

### 8.4 Single-instance bot cutover

Cutover выполняется отдельным two-host checksum-bound orchestrator:

1. preflight: Spain web/data accepted, Spain bot inactive, USA bot exactly one;
2. Telegram identity/webhook/backlog checks без raw identifiers;
3. arm rollback watchdog до первой mutation;
4. stop/disable USA bot;
5. доказать USA bot process count 0;
6. создать exact Spain bot-enable marker;
7. start Spain bot; после unit hardening — enable persistent boot ownership;
8. подтвердить ровно один polling owner, restart 0 и watchdog healthy;
9. получить manual operator acceptance по одному свежему `/start` или
   утверждённому private bot status flow;
10. cancel rollback watchdog и выполнить independent postflight.

Ни на одном шаге USA и Spain bot не могут быть одновременно active. Если
Spain admission/acceptance не проходит, rollback останавливает Spain bot,
удаляет только его marker/env delta, восстанавливает target DB при
необходимости и возвращает USA bot в accepted active state.

Текущий Spain bot unit `static` и не имеет boot enable contract. До live
cutover package обязан добавить и локально проверить controlled persistent
enable/disable lifecycle, сохраняя disabled-first marker.

## 9. Web boundary

Spain web всегда слушает только `127.0.0.1:3031`. Запрещены:

- direct public `3031`;
- TCP `80/443`/reverse-proxy addition в этом migration;
- public API/self-service;
- broad write surfaces;
- перенос USA session cookies.

Acceptance выполняется через loopback probe и операторский SSH tunnel.

## 10. Rollback levels

### До data apply

Удаляется только staged migration root; services и live DB не менялись.

### После data apply, до bot cutover

Восстанавливаются exact Spain DB/env/web state. USA bot остаётся active.

### После USA bot stop, до Spain bot acceptance

Spain bot stop/marker removal, target DB/env rollback при необходимости,
USA bot start/enable, затем independent single-instance postflight.

### После acceptance

USA сохраняется неизменной до отдельной фразы `USA_REINSTALL_READY`. Перенос
не выполняет shutdown, cleanup или provider operation.

## 11. Fail-closed taxonomy

```text
SOURCE_AUDIT_MISMATCH
TARGET_AUDIT_MISMATCH
SCHEMA_UNSUPPORTED
USER_IDENTITY_CONFLICT
PLAN_SEMANTIC_CONFLICT
LEGACY_DEVICE_MAPPING_AMBIGUOUS
ORDER_MAPPING_AMBIGUOUS
TOKEN_REISSUE_REQUIRED
SPAIN_INVARIANT_MISMATCH
PACKAGE_CHECKSUM_MISMATCH
STAGE_BOT_NOT_DISABLED
WEB_NOT_LOOPBACK_ONLY
BOT_TOKEN_BINDING_MISMATCH
MULTIPLE_POLLING_OWNERS
USA_BOT_STOP_UNCONFIRMED
SPAIN_BOT_ADMISSION_FAILED
ROLLBACK_FAILED
FOREIGN_EQUALITY_MISMATCH
AWG2_EQUALITY_MISMATCH
```

Raw exception, target, Telegram identifier, token, DB row, path, stdout/stderr
или peer key не входят в failure receipts.

## 12. Acceptance criteria

Package preparation может получить approval, только если:

- source/target read-only audit fresh и checksum-bound;
- source USA и target Spain DB integrity/FK pass;
- merge preview deterministic и повторный preview byte-identical;
- Spain d1–d7/passports/receipts/lifecycle/server invariants unchanged;
- usable secret/token/config resurrection count `0`;
- USA API token reissue count явно зафиксирован;
- bot token/admin transfer присутствует только в encrypted payload;
- Spain APP/web secrets preserve policy passed;
- stage/cutover/rollback scripts прошли local fake-harness TDD;
- static mutation allowlist и secret scan passed;
- manifest binds every byte and expires;
- live mutation flags remain false.

## 13. Последовательность gates

```text
GATE 1  LOCAL TDD IMPLEMENTATION
GATE 2  PACKAGE PREPARATION FROM READ-ONLY USA/SPAIN INPUTS
GATE 3  SPAIN DISABLED STAGE
GATE 4  SPAIN WEB/DATA APPLY AND ACCEPTANCE
GATE 5  TWO-HOST SINGLE-INSTANCE BOT CUTOVER
GATE 6  FINAL SPAIN ACCEPTANCE AND USA_REINSTALL_READY
```

Каждый gate получает новую literal approval, unique outcome ID, exact SHA-256
и отдельный rollback boundary. Approval одного gate не переносится на другой.
