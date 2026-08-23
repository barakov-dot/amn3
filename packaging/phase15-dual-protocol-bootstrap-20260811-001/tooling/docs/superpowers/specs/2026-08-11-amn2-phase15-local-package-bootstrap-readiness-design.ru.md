# AMN2 Phase 15: local package, production bootstrap и read-only preflight readiness

Дата: 2026-08-11

Статус: design approved in dialogue; written-spec review pending

Область: только локальная разработка, package materialization и локальная
проверка tooling. Фактический SSH/read-only preflight и любые live-действия
требуют отдельного разрешения после завершения Phase 15.

## 1. Цель и итог фазы

Phase 15 превращает локально проверенный dual-protocol application snapshot
Phase 14 в воспроизводимый checksum-bound package с устойчивым Telegram
callback flow, fail-closed production composition root и подготовленным
read-only Spain preflight collector.

Логический итог Phase 15:

- AWG2 остаётся протоколом по умолчанию и продолжает работать;
- AWG3 handlers, providers и production issuer связаны через fail-closed
  bootstrap, но общая выдача остаётся выключенной;
- Telegram selection и confirmation используют короткие restart-safe handles;
- тестовое окружение использует `httpx2` без Starlette deprecation warning;
- создан новый самостоятельный Phase 15 package;
- package полностью проверен локально;
- read-only Spain collector готов, но SSH не запускался;
- создан secret-free closeout receipt;
- процесс остановлен перед любым remote preflight или stage.

## 2. Авторитетные якоря

Phase 15 начинается только при точном совпадении:

- source repository:
  `C:\Users\SooL\Documents\amn2-phase14-dual-protocol-application`;
- source branch: `codex/phase14-dual-protocol-application-local`;
- source HEAD: `36981d7afc1fcd9eb17386c62f70adf175d76263`;
- Phase 14 receipt:
  `research/amn2/phase14-dual-protocol-application-readiness-receipt.md`;
- receipt commit: `4e1052c079e1e25031a6c80f4dae1763e457ca48`;
- receipt SHA-256:
  `D33E69B53C7397C567B16C4F1CAEA12AF97969D9436D3E95E6038148054AA982`;
- approved source base:
  `4547af1b23e4774822119f98004568c6eb039303`.

Implementation создаёт новый изолированный worktree и ветку от точного Phase
14 HEAD. Рабочее имя ветки:
`codex/phase15-local-package-bootstrap-readiness`.

Phase 13 и старые Phase 14 package/preflight trees разрешены только как
read-only reference. Их manifest, outcome, evidence и package identity нельзя
копировать, переименовывать или использовать как доказательство готовности.

Любой mismatch HEAD, branch, receipt path/hash или tracked cleanliness означает
`BLOCKED` до отдельного решения.

## 3. Неподвижные инварианты

1. AWG2 не заменяется, не останавливается и остаётся default.
2. Наличие AWG3-кода, package или успешного local verification не включает
   AWG3 issuance.
3. AWG3 требует global acceptance, exact accepted build, fresh evidence,
   accepted runtime и отдельный issuance enable.
4. Per-user admin approval после global enable не требуется.
5. Неизвестный, stale, failed, superseded или security-revoked exact build
   блокирует новую AWG3 выдачу.
6. AWG2 fallback требует явного выбора пользователя.
7. Production bootstrap не выполняет remote observation или issuer при старте.
8. Raw config, private key, PSK, QR payload, bot token и SSH credentials не
   попадают в callback, DB audit, logs, manifest, evidence или receipt.
9. Package, preflight, stage, pilot, acceptance и enable являются отдельными
   gates. Успех одного не разрешает следующий.
10. Любая двусмысленность или mismatch останавливает выполнение без blind
    retry и автоматического расширения file list.

## 4. Архитектура и gates Phase 15

### Gate 15.0. Source and receipt sync

Read-only проверяются exact source HEAD, branch, clean tracked state, Phase 14
receipt commit/hash и отсутствие конфликта с post-Phase-14 изменениями.

### Gate 15.1. Application hardening

Реализуются compact Telegram callbacks, durable selection/confirmation state
и `httpx2` test dependency contract. Gate выполняется TDD и завершается
focused/full application verification.

### Gate 15.2. Fail-closed production bootstrap

Создаётся явный composition root для Telegram router, callback repository,
runtime/evidence/build providers, AWG3 control state, issuer, delivery builder
и audit sink. Bootstrap может зарегистрировать AWG3 handlers, но не включает
выдачу и не вызывает issuer при старте.

### Gate 15.3. Package tooling and materialization

Создаются новый builder, manifest schema, verifier и самостоятельный Phase 15
versioned package tree. Phase 13 package data не является входом готовности.

### Gate 15.4. Local package and preflight-tooling verification

Локально проверяются package inventory, checksums, identity, dependency
contracts, fail-closed bootstrap, отсутствие секретов и строго read-only
характер Spain collector. SSH runner и collector удалённо не запускаются.

### Gate 15.5. Closeout

Выполняются final focused/full suites, whole-branch review, package verification
и secret-free receipts. Затем обязательный STOP перед фактическим SSH
read-only preflight.

## 5. Telegram callback и durable confirmation contract

### 5.1. Wire format

Callback grammar:

- AWG3 selection: `a3s:<handle>`;
- AWG3 confirmation: `a3c:<token>`.

Каждая строка должна быть не длиннее 64 UTF-8 bytes. Raw passport ID, build ID,
version, config data или другое payload содержимое в callback запрещено.

Handle/token содержит не менее 128 бит криптографической случайности и
кодируется URL-safe alphabet. Максимальная длина дополнительно проверяется до
создания `InlineKeyboardButton`.

### 5.2. Durable selection ledger

Selection handle хранится server-side и включает structured поля:

- digest handle;
- owner user/Telegram identity;
- exact passport ID;
- application/platform/version/build;
- created/expiry timestamps;
- consumed timestamp и terminal reason.

Selection TTL равен 15 минутам. Raw handle в БД не хранится. Resolve всегда
повторно проверяет owner, private-chat boundary, passport ownership/revocation
и текущую exact-build allowlist.

### 5.3. Durable issuance confirmation

Process-only `SelfServiceIssuanceService._pending` и
`BotWorkflow._awg3_pending_requests` заменяются durable confirmation ledger.
Запись содержит token digest, owner, structured request snapshot,
request fingerprint, created/expiry/consumed timestamps и terminal reason.

Confirmation TTL остаётся 5 минут. Raw confirmation token в БД не хранится.
Wrong-owner attempt не потребляет запись. Success и terminal outcomes потребляют
её атомарно; transient outcome сохраняет её до TTL. Restart создаёт новый
service/workflow instance, но не теряет допустимую pending confirmation.

Параллельные подтверждения одного token могут вызвать issuer не более одного
раза. Consumption, admission recheck и issuance reservation используют
существующие durable transaction/barrier guarantees Phase 14.

## 6. `httpx2` и dependency contract

Текущий dev dependency `httpx>=0.27,<1` заменяется на
`httpx2>=2.10,<3`. Прямых импортов `httpx` в application/tests нет; FastAPI/
Starlette `TestClient` должен использовать `httpx2` backend.

Acceptance требует:

- отсутствие `StarletteDeprecationWarning`;
- полный test suite на target-compatible Python 3.12 environment;
- deterministic dependency lock и hashes;
- отдельную классификацию runtime и dev/test dependencies;
- отсутствие автоматической установки latest dependencies во время stage.

`pyproject.toml` сохраняет target Python `>=3.12,<3.13`. Проверки на другом
Python могут быть дополнительным сигналом, но не единственным package evidence.

## 7. Fail-closed production bootstrap

Composition root связывает:

- существующий Telegram router;
- durable callback/confirmation repository;
- runtime instance provider;
- exact client-build/evidence provider;
- AWG3 control-state provider;
- production config issuer;
- config/QR delivery builder;
- secret-safe audit sink.

Перед каждым issuer call заново проверяются:

- exact installed/package identity;
- accepted runtime lifecycle;
- global acceptance и issuance enable;
- exact accepted client build;
- fresh required evidence;
- active user/passport/profile/barrier state.

Отсутствующая dependency, mismatch или provider failure блокирует AWG3 до
secret generation/peer side effect. AWG2 и остальные bot routes продолжают
работать. Пользователь получает безопасный unavailable result.

Production issuer не является synthetic. Phase 15 проверяет его composition и
boundary локальными doubles; реальный server issuer не вызывается. Bootstrap
startup не выполняет SSH, remote observation, config generation или peer
mutation.

## 8. Monitoring deferral

Phase 15 фиксирует только interface taxonomy будущих событий:

- `server_unavailable`;
- `awg2_unavailable`;
- `awg3_unavailable`.

Реальный scheduler, remote health collection и Telegram-отправка только bot
admin IDs не активируются. Этот контур проектируется после установки runtime и
появления первых конфигов. Обычные пользователи такие уведомления не получают.

## 9. Новый checksum-bound package contract

Package создаётся как новый versioned directory tree:

`packaging/phase15-dual-protocol-bootstrap-<package-id>/`

Он включает:

- exact Phase 15 application snapshot;
- additive DB migrations;
- callback/confirmation components;
- bootstrap/providers/issuer adapters;
- isolated AWG3 runtime artifacts;
- будущие gated application/runtime stage scripts;
- read-only preflight collector;
- manifest/schema/verifier;
- Python 3.12 dependency contracts;
- operator gates и rollback documentation.

Он не содержит bot/SSH credentials, keys, PSK, raw config, QR, production DB
backup, peer records или stale Phase 13 outcome.

### 9.1. Manifest

Для каждого файла фиксируются normalized relative path, size, SHA-256, logical
role, executable mode, secret classification, allowed gate и rollback boundary.

Top-level manifest фиксирует source HEAD/branch, Phase 14 receipt path/hash,
Phase 15 source receipt, dependency contract, complete inventory и
`package_identity_sha256`.

Canonical manifest bytes: deterministic JSON, sorted normalized paths, UTF-8
без BOM. Канонический package — directory tree, а не transport archive. Любое
изменение файла после materialization делает verification недействительным.

### 9.2. Dependency artifacts

Создаются отдельные hash-bound runtime и dev/test dependency locks для target
Python 3.12. Package verifier блокирует несовместимый Python, architecture или
dependency artifact. Stage не разрешает network resolution плавающих версий.

### 9.3. Stage classifications

Manifest разделяет будущие scripts по gates:

- `APPLICATION_STAGE`;
- `AWG3_RUNTIME_STAGE`;
- `ADMIN_PILOT`;
- `ACCEPTANCE`;
- `ENABLE_ISSUANCE`.

Наличие script не разрешает его запуск. Перед application stage требуется
checksum-bound DB backup; перед runtime stage повторно проверяются AWG2 health
и resource conflicts.

## 10. Read-only Spain preflight tooling

Collector подготавливается, но удалённо не запускается. После отдельного `/GO`
он должен read-only проверить:

- OS, architecture и Python 3.12;
- disk space и backup capability;
- current application/database layout;
- systemd/container capabilities;
- AWG2 health без restart/stop/change;
- Telegram service composition prerequisites без раскрытия token;
- отсутствие конфликтов для `awg3`, `amn2sp3br0`, UDP `30002`, закреплённых
  CIDR, container/service names и state paths;
- firewall/routes только чтением;
- отсутствие незавершённой stage/recovery операции.

Collector передаётся через stdin или иной non-persistent transport и не
создаёт remote-файлы. Evidence содержит только безопасные states, hashes и
классифицированные blocking reasons.

## 11. TDD и review contract

Каждая implementation task выполняется как отдельная единица:

1. fresh implementer;
2. ожидаемый RED;
3. minimal GREEN;
4. focused tests;
5. `git diff --check`;
6. secret/scope review;
7. отдельный локальный commit;
8. spec-compliance review;
9. code-quality review.

Перед materialization выполняются whole-source focused и full suites. После
materialization повторяются manifest/inventory/checksum/secret проверки. Перед
receipt выполняется независимый whole-branch review.

### 11.1. Callback/confirmation tests

- callback UTF-8 length не превышает 64 bytes;
- selection/confirmation работают после restart;
- owner/private-chat boundaries enforced;
- wrong owner не потребляет handle;
- expired/used/malformed handle fail-closed;
- terminal consumes, transient preserves до TTL;
- concurrent confirmation вызывает issuer максимум один раз;
- callback/audit/log не содержит secret material.

### 11.2. Dependency tests

- Python 3.12 compatibility;
- Starlette TestClient использует `httpx2`;
- deprecation warning отсутствует;
- lock/hashes reproducible;
- incompatible Python/artifact fail-closed.

### 11.3. Bootstrap tests

- package/provider/issuer/gate absence блокирует AWG3;
- AWG2 routes остаются рабочими;
- startup не вызывает issuer;
- fresh admission выполняется перед каждым issuer call;
- synthetic issuer отсутствует в production composition;
- restart сохраняет pending confirmations;
- private owner delivery boundary сохранена.

### 11.4. Package/preflight-tooling tests

- manifest deterministic;
- file mutation ломает verification;
- stale Phase 13 inputs отсутствуют;
- absolute local paths отсутствуют;
- secret scan clean;
- scripts классифицированы и не запускались;
- collector не содержит mutating commands;
- clean/conflict/mismatch/incomplete-recovery fixtures дают точные outcomes.

## 12. План задач по критичности

### Critical

1. Exact source/receipt gate и isolated worktree.
2. Durable callback/confirmation ledger и callback ≤64 bytes.
3. `httpx2` и reproducible Python 3.12 dependency contract.
4. Fail-closed production bootstrap/providers/issuer composition.
5. Package builder, manifest schema и verifier.

### Very important

6. Package materialization и local verification.
7. Read-only Spain collector и fixture verification.

### Important closeout

8. Whole-branch review, focused/full suites, secret review, source receipt и
   package/preflight readiness receipt.

## 13. STOP-условия

Немедленный STOP без blind retry при:

- source HEAD/receipt hash mismatch;
- unexpected test failure;
- callback >64 bytes;
- невозможности restart-safe durable confirmation;
- dependency resolution/hash ambiguity;
- package checksum/inventory mismatch;
- secret-shaped material;
- новом file-list expansion;
- stale Phase 13 dependency;
- потенциальной mutating collector command;
- SQLite lock timeout;
- contract ambiguity.

При STOP выводятся одна причина и одна точная `/GO` команда разблокировки.

## 14. Запрещённые действия

В Phase 15 запрещены:

- SSH и фактический remote preflight;
- application/runtime stage;
- config/QR/peer или real issuance;
- admin pilot;
- runtime/build/global acceptance;
- enable AWG3 issuance;
- deploy, service, firewall, route или live mutation;
- push;
- изменение AWG2 golden/runtime;
- изменение `CLIENT_RELEASE_MONITOR_BASELINE.ru.md`;
- изменение Phase 13 package trees и посторонних untracked-файлов.

## 15. Closeout state

Phase 15 receipt должен зафиксировать:

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
PACKAGE_MATERIALIZED=true
PACKAGE_VERIFIED_LOCAL=true
REMOTE_PREFLIGHT_RUN=false
SSH_USED=false
APPLICATION_STAGED=false
AWG3_RUNTIME_STAGED=false
AWG3_PILOT_ISSUED=false
AWG3_GLOBAL_ACCEPTED=false
AWG3_ISSUANCE_ENABLED=false
LIVE_MUTATION=false
```

После closeout обязательный STOP. Следующий шаг — отдельная команда на точный
checksum-bound SSH/read-only Spain preflight.

## 16. Модель и оценка

Рекомендуемая модель для всех задач: `GPT-5.6_SOL_HIGH`, effort `HIGH`.
Снижение до Medium до whole-branch review не рекомендуется из-за сочетания
security, persistence, concurrency, dependency и checksum boundaries.

Оценка локальной Phase 15: 8–16 часов, включая TDD, отдельные commits, reviews,
full suites, package materialization и receipts.
