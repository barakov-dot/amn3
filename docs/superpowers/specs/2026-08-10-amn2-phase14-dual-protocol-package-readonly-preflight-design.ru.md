# AMN2 Phase 14: dual-protocol application, checksum-bound package и read-only preflight

Дата: 2026-08-10
Статус: design approved in dialogue; written-spec review pending
Область: локальный design/status gate без package materialization, preflight run, SSH, push и live mutation

## 1. Цель

Phase 14 готовит AMN2 к параллельной работе двух поколений протокола:

- AWG2 продолжает выпускаться и остаётся протоколом по умолчанию;
- AWG3 добавляется как изолированный runtime и отдельный вариант выдачи;
- бот, web-интерфейс, админка и модель данных понимают оба протокола;
- совместимый пользователь после глобального принятия AWG3 может получить AWG3 без индивидуального ожидания администратора;
- установка приложения, установка runtime, пилот, принятие и включение общей выдачи разделены на независимые разрешения;
- любой этап должен сохранять работоспособность и конфигурации AWG2.

Этот документ определяет будущий package и read-only preflight contract. Он не является разрешением на создание package, запуск preflight, SSH, установку, выдачу конфигов или изменение сервера.

## 2. Авторитетные якоря

Дизайн привязан к следующим неизменяемым входам:

- source worktree: `C:\Users\SooL\Documents\amn2-phase14-awg3-readiness`;
- source branch: `codex/phase14-awg3-readiness-local`;
- source HEAD: `4547af1b23e4774822119f98004568c6eb039303`;
- verification receipt: `research/amn2/phase14-awg3-readiness-local-verification-receipt-2026-08-09.md`;
- receipt SHA-256: `3DF5A62B23C5BE565E08383288269AA7F486EE23F9E1A60D4D767D53A240316B`;
- целевой сервер будущего preflight/runtime: Spain;
- Phase 13 tooling и документы допустимы только как read-only reference.

Несовпадение HEAD, branch, receipt hash или состава исходников означает `BLOCKED`. Нельзя автоматически выбирать другой commit, remote, branch, package или старый outcome.

## 3. Явные ограничения текущего gate

В текущем gate разрешены только status/design/plan документы и один локальный commit в `VPS-OPS-LAB` после review.

Запрещены:

- materialization package, manifest или outcome;
- фактический preflight и создание preflight outcome;
- SSH и любые удалённые команды;
- создание ключей, конфигов, QR, VPN payload или peer-записей;
- установка, запуск, остановка или изменение service/container/interface/bridge;
- firewall, route, client или иная live mutation;
- push;
- изменение source branch или remotes AMN2;
- изменение `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`;
- изменение старых VPN-документов, Phase 13 packaging trees и посторонних untracked-файлов.

## 4. Неподвижные инварианты

1. AWG2 не заменяется и не завершается.
2. AWG2 остаётся вариантом по умолчанию.
3. AWG3 не должен изменять, перезапускать или переиспользовать runtime-ресурсы AWG2.
4. Успешный package, preflight, stage или pilot не включает следующую стадию автоматически.
5. Реальная общая выдача AWG3 закрыта до `GLOBAL_AWG3_ACCEPTED` и отдельного `ENABLE_AWG3_ISSUANCE`.
6. Индивидуальное одобрение администратора для совместимого пользователя после глобального enable не требуется.
7. Неизвестная или не принятая точная сборка клиента блокирует AWG3 fail-closed.
8. AWG2 нельзя выдавать как молчаливый fallback: пользователь должен явно согласиться.
9. Секреты не попадают в audit, logs, diagnostics, status, manifest или outcome.
10. Любой mismatch, конфликт или двусмысленность приводит к остановке без blind retry и автоматического расширения scope.

## 5. Компоненты и границы ответственности

### 5.1. Dual-protocol application

Единый application snapshot содержит код бота, web, админки, сервисов и модели данных из точного source HEAD. Приложение:

- хранит AWG2 и AWG3 как разные protocol profiles одного логического устройства;
- применяет общий user/device lifecycle cascade;
- применяет отдельный lifecycle каждого protocol config;
- проверяет точную совместимость AWG3;
- не превращает наличие AWG3-кода в разрешение выдачи.

### 5.2. Compatibility matrix

Единица совместимости — точная комбинация:

`platform + application + version + build`

Пользователь видит понятные названия приложения и версии. Точный build и evidence остаются внутренними данными системы и доступны администратору.

Запись-кандидат формируется только на основании:

- stable upstream release;
- точной идентичности platform/application/version/build;
- свежего `local_import` evidence;
- свежего `full_data` evidence.

Automation может подготовить candidate, но не может сама глобально принять его. Администратор один раз принимает или отклоняет точную сборку. Per-user bypass и свободный ввод версии не допускаются.

### 5.3. AWG3 admission

AWG3 admission разрешён, только если одновременно выполнены условия:

- runtime принят глобально;
- точная клиентская сборка принята;
- `GLOBAL_AWG3_ACCEPTED=true`;
- `ENABLE_AWG3_ISSUANCE=true`;
- пользователь и устройство активны;
- для устройства нет второго активного AWG3-конфига или недопустимого replacement state.

Заявление пользователя «поддерживает 3.0 или выше» само по себе не является evidence. Оно должно разрешиться в точную принятую запись allowlist.

### 5.4. Isolated AWG3 runtime

AWG3 использует только следующие заранее закреплённые ресурсы:

| Ресурс | Точное значение |
|---|---|
| Интерфейс | `awg3` |
| Bridge | `amn2sp3br0` |
| UDP port | `30002` |
| VPN CIDR | `10.212.13.0/24` |
| Server address | `10.212.13.1/24` |
| Container CIDR | `172.29.252.0/28` |
| Container | `amn2-spain-awg3` |
| Service | `amn2-spain-awg3.service` |
| State root | `/var/lib/amn2-spain/awg3` |
| Runtime config | `/var/lib/amn2-spain/awg3/awg3.conf` |

При занятости любого имени, адреса, порта, пути или диапазона процесс блокируется. Автоматический подбор альтернативы, adoption существующего ресурса, переименование или удаление запрещены.

## 6. Пользовательская модель и выдача

### 6.1. Device passport

Одно физическое устройство представлено одним логическим device passport. На нём могут одновременно находиться разные программы для AWG2 и AWG3.

Для одного device passport допускаются:

- максимум один активный AWG2 config;
- максимум один активный AWG3 config;
- максимум один pending replacement на протокол.

Оба protocol profile считаются одним логическим устройством для лимитов устройств, но имеют независимые config lifecycle и revoke.

### 6.2. Простой пользовательский flow

После глобального enable пользователь:

1. открывает карточку устройства в Telegram-боте;
2. выбирает приложение и понятную версию из allowlist;
3. нажимает `Получить AWG3`;
4. видит краткое подтверждение, что AWG3 поддерживается, а AWG2 останется активным;
5. подтверждает выдачу;
6. получает config-файл и QR-код двумя отдельными сообщениями.

Дополнительное одобрение администратора не требуется. При incompatible/unknown build AWG3 не создаётся; бот объясняет причину и отдельно предлагает AWG2.

### 6.3. Telegram delivery

Доставка разрешена только:

- точному владельцу по Telegram user ID;
- в private chat;
- через личный кабинет пользователя в существующем боте.

Config отправляется document-файлом, QR — отдельным сообщением. Срок хранения Telegram-сообщений не ограничивается приложением.

Raw config нельзя дублировать в текстовом сообщении, log или audit event.

### 6.4. Admin access

Все администраторы, определённые текущей моделью bot admins, могут открыть raw config и QR в карточке конкретного конфига. Дополнительная capability или повторное подтверждение не требуются.

Открытие автоматически создаёт secret-free audit event с actor, временем, config ID и причиной/контекстом просмотра. Содержимое config и QR в audit не записывается.

## 7. Lifecycle и revoke

### 7.1. Cascade

- USER block/disable отключает все AWG2 и AWG3 configs пользователя на всех устройствах.
- DEVICE disable отключает AWG2 и AWG3 только данного устройства.
- CONFIG revoke отключает только выбранный protocol config.
- Отключение AWG3 issuance не отключает уже выданные конфиги.

### 7.2. Обычный reissue

Обычный перевыпуск использует двухфазное состояние `pending_replacement`:

1. старый конфиг остаётся активным;
2. создаётся новый конфиг того же протокола;
3. после подтверждённой активации нового выполняется атомарное переключение и отзыв старого;
4. профиль другого протокола не изменяется.

### 7.3. Compromise reissue

При подозрении на утечку:

1. старый конфиг немедленно отзывается;
2. создаётся новый конфиг того же протокола;
3. при ошибке выпуска старый конфиг автоматически не восстанавливается;
4. повтор операции должен быть идемпотентным и аудируемым как `compromise_reissue`.

Пользователь может выполнить emergency revoke/reissue своего конфига. Администратор может выполнить его для любого конфига. Разрушительное действие требует явного подтверждения.

## 8. Client-build lifecycle

Поддерживаются следующие изменения статуса принятой сборки:

- `superseded`: новые выдачи запрещены; действующие конфиги продолжают работать; пользователю предлагается обновление;
- `compatibility_rejected`: новые выдачи запрещены; существующие конфиги получают `review_required`, но автоматически не отзываются;
- `security_revoked`: новые выдачи запрещены; формируется отдельное предложение emergency suspend или batch revoke; автоматический массовый отзыв запрещён.

## 9. Audit и модель состояния

Audit является versioned append-only потоком событий. Текущее состояние строится как проекция, а не перезаписывает историю.

Для административных и чувствительных действий фиксируются:

- actor;
- timestamp;
- reason;
- evidence reference;
- предыдущее и новое состояние;
- идентификаторы пользователя, устройства и конфига без секретного материала.

События включают принятие runtime/build, переключение issuance, просмотр raw config, выдачу, revoke, reissue, pilot и emergency actions.

## 10. Независимые gates

### Gate 0. `PACKAGE_MATERIALIZATION`

Будущая отдельная команда создаёт новый Phase 14 package. Этот design gate package не создаёт.

### Gate 1. `APPLICATION_PREFLIGHT`

Read-only проверка перед application stage. Успешный результат означает только готовность к отдельному запросу разрешения.

### Gate 2. `APPLICATION_STAGE`

После отдельного разрешения:

1. повторно сверяются package/manifest/head/checksums;
2. непосредственно перед изменениями создаётся checksum-bound backup БД;
3. применяется application snapshot и additive schema migration;
4. выполняются AWG2, bot, web и admin smoke checks;
5. AWG3 runtime не запускается, общая выдача остаётся выключенной.

До этого gate read-only preflight только проверяет возможность backup; сам backup не создаёт.

### Gate 3. `AWG3_RUNTIME_PREFLIGHT`

Read-only проверка изоляции и отсутствия resource conflicts. Успех не разрешает установку.

### Gate 4. `AWG3_RUNTIME_STAGE`

После отдельного разрешения устанавливает только изолированные AWG3 runtime resources. Общая выдача остаётся выключенной.

### Gate 5. `AWG3_ADMIN_PILOT`

После отдельного разрешения допускается исключение из общего запрета production AWG3 records:

- один администраторский тестовый аккаунт;
- одно зарегистрированное тестовое устройство;
- один реальный AWG3 peer/config/QR;
- одна точная candidate client build;
- полная audit trail.

Обычные пользователи по-прежнему не могут получить AWG3. Пилот можно отдельно revoke/reissue. Успех пилота не принимает runtime/build и не включает общую выдачу автоматически.

### Gate 6. `AWG3_ACCEPTANCE`

Администратор отдельно принимает:

- конкретный runtime candidate;
- каждую точную platform/application/version/build запись.

`GLOBAL_AWG3_ACCEPTED=true` только при принятом runtime и наличии хотя бы одной принятой точной клиентской сборки.

### Gate 7. `ENABLE_AWG3_ISSUANCE`

Отдельное административное решение открывает автоматическую выдачу AWG3 совместимым пользователям. Оно не меняет AWG2 и не требует per-user approval.

Отключение переключателя запрещает только новые AWG3 issuance.

## 11. Новый checksum-bound package contract

Phase 14 package является новым самостоятельным артефактом. Старые Phase 13 manifest и outcome не копируются, не переименовываются и не используются как вход готовности.

Package должен содержать:

- полный интегрированный application source snapshot из точного HEAD;
- отдельные AWG3 runtime artifacts;
- additive migration code как часть source snapshot;
- scripts/checks, необходимые для будущей проверки и разрешённых stages;
- новый manifest schema Phase 14;
- документацию операторских gates и rollback.

Миграционный код не должен предоставляться как самостоятельный обходной entrypoint. Его выполнение возможно только внутри отдельно разрешённого `APPLICATION_STAGE` после backup.

Manifest для каждого файла фиксирует как минимум:

- relative path;
- byte size;
- SHA-256;
- logical role;
- разрешённый gate/stage;
- executable flag или ожидаемый mode;
- secret classification;
- rollback boundary.

Manifest верхнего уровня фиксирует:

- Phase 14 package schema/version;
- source HEAD и branch;
- verification receipt path/hash;
- timestamp materialization;
- полный file inventory;
- отсутствие ссылок на stale Phase 13 outcome;
- `package_identity_sha256`.

Каноническим package является versioned directory tree, а не transport archive.
Файлы в manifest сортируются по normalized relative path; canonical JSON
сериализуется как UTF-8 без BOM. `package_identity_sha256` равен SHA-256 этих
canonical manifest bytes. Поскольку manifest содержит SHA-256 и размер каждого
файла, его hash транзитивно связывает весь directory tree. Если позднее для
транспорта создаётся archive или multipart envelope, его собственный hash
является дополнительным transport evidence и не меняет package identity.

## 12. `APPLICATION_PREFLIGHT` contract

Будущий read-only application preflight проверяет:

- точный package identity, manifest и checksums;
- source HEAD и receipt hash;
- текущую версию приложения и schema;
- применимость только additive migration path;
- возможность создать backup и наличие достаточного свободного места;
- текущее здоровье приложения, Telegram-бота, web и admin surface;
- здоровье и неизменность AWG2 issuance/runtime;
- отсутствие AWG3 user configs/peers/secrets, кроме ранее отдельно разрешённого pilot state;
- отсутствие секретов в package/report surface.

Preflight не создаёт backup, не пишет в БД, не перезапускает сервисы и не изменяет файлы сервера.

## 13. `AWG3_RUNTIME_PREFLIGHT` contract

Будущий read-only runtime preflight проверяет:

- доступность точного UDP port;
- отсутствие interface/bridge/container/service/path conflicts;
- отсутствие пересечения VPN/container CIDR с routes, interfaces и container networks;
- необходимые kernel/runtime capabilities;
- наличие места и допустимые ownership/mode prerequisites без их изменения;
- текущее здоровье AWG2;
- отсутствие рестартов и изменений AWG2 во время проверки;
- соответствие package runtime artifacts manifest.

Любой неожиданный существующий ресурс означает `BLOCKED`. Preflight не присваивает ресурс, не переименовывает его и не предлагает автоматически альтернативу.

## 14. Outcome semantics

Будущие preflight outcomes должны иметь однозначное состояние:

- `READY_FOR_APPLICATION_STAGE` или `READY_FOR_AWG3_RUNTIME_STAGE`: подтверждена только read-only готовность; live authorization отсутствует;
- `BLOCKED`: указан точный `BLOCKED_REASON`, сохранено evidence и выведена одна `EXACT_NEXT_COMMAND` для нового решения оператора.

Outcome не может содержать конфиги, ключи, QR, VPN payload или другие секреты. Повтор после `BLOCKED` допускается только после устранения причины и новой явной команды; blind retry запрещён.

Каждый будущий preflight использует новый одноразовый `preflight_run_id`,
bounded `created_at`/`expires_at` и локальный create-new/no-replace claim,
связанный с package identity, target role и точными hashes runner/collector/schema.
Один claim допускает ровно один sanitized success либо failure outcome и после
использования считается consumed. Старый Phase 13 claim/outcome не может быть
входом Phase 14.

## 15. Rollback boundaries

### 15.1. `APPLICATION_STAGE`

- Перед изменениями обязателен checksum-bound backup БД.
- При failed smoke восстанавливается предыдущий application code.
- Additive schema физически не удаляется.
- AWG3 issuance остаётся выключенной.
- До enable отсутствуют обычные пользовательские AWG3 records; разрешён только отдельно одобренный pilot после runtime stage.

### 15.2. `AWG3_RUNTIME_STAGE`

- При ошибке останавливаются и удаляются только созданные этим stage AWG3 resources.
- AWG2, БД, bot, web, admin и application code не откатываются.
- Общая AWG3 issuance остаётся выключенной.

### 15.3. `AWG3_ACCEPTANCE_AND_ENABLE`

- Нормальный rollback отключает новые AWG3 issuance.
- Уже выданные AWG3 configs продолжают работать.
- Runtime stop и revoke существующих configs являются отдельными emergency operations.

## 16. Emergency boundary

`EMERGENCY_SUSPEND_AWG3_RUNTIME` требует отдельного точного разрешения и затрагивает только AWG3.

При suspend:

- AWG3 runtime останавливается;
- configs не удаляются и получают `temporarily_unavailable`;
- AWG2 продолжает работать;
- возобновление требует свежего read-only preflight и отдельного разрешения.

Mass revoke никогда не следует автоматически из suspend и требует отдельного решения.

## 17. Проверка и acceptance evidence

### 17.1. Package verification

Будущий package проходит clean-room проверку:

- manifest schema;
- inventory;
- sizes и SHA-256;
- source/receipt anchors;
- отсутствие неожиданных файлов, secrets и stale outcomes;
- соответствие каждого файла разрешённому stage.

### 17.2. Application stage verification

Проверяются:

- application start/health;
- additive schema compatibility;
- bot workflows;
- web/admin workflows;
- AWG2 issuance и существующие AWG2 records;
- отсутствие общей AWG3 issuance.

### 17.3. Runtime stage verification

Проверяются:

- точные AWG3 resources;
- сетевой isolation boundary;
- отсутствие изменения/restart AWG2;
- отсутствие общей AWG3 issuance.

### 17.4. Admin pilot verification

Пилот подтверждает полный путь:

- точная client identity/build;
- создание peer/config/QR;
- две отдельные Telegram-доставки;
- успешный import;
- свежее `local_import` evidence;
- свежее `full_data` evidence;
- connect/use result;
- revoke;
- безопасный same-protocol reissue.

### 17.5. Negative verification

Обязательны проверки блокировки:

- unknown или не принятой build;
- устаревшего evidence;
- issuance до global acceptance/enable;
- второго активного config того же протокола;
- resource conflict;
- mismatch HEAD/hash/manifest;
- попытки silent AWG2 fallback;
- любого неразрешённого влияния на AWG2.

## 18. Error handling

Ошибки классифицируются по gate и ресурсу. Любая ошибка должна:

- завершить текущий gate без перехода к следующему;
- сохранить secret-free evidence;
- не выполнять cleanup за пределами ресурсов, созданных текущим отдельно разрешённым stage;
- не выполнять автоматический retry;
- не расширять file/resource list;
- вернуть один точный следующий операторский шаг.

## 19. Monitoring backlog

Уведомления администраторам о недоступности сервера или отдельного AWG2/AWG3 runtime полезны, но отложены до появления runtime и конфигов.

Будущий monitoring design может использовать текущий Telegram-бот только как sender и отправлять сообщения исключительно bot admin IDs. Обычные пользователи такие operational alerts не получают. Реализация monitoring не входит в текущий Phase 14 package/preflight scope.

## 20. Критерии завершения design/status gate

Текущий gate завершён, когда:

- этот design-spec прошёл self-review и пользовательский review;
- создан отдельный implementation plan без выполнения его шагов;
- синхронизированы только разрешённые Phase 14 status-документы;
- diff не содержит protected/unrelated files;
- выполнен review документов и `git diff --check`;
- создан один точный локальный commit в `VPS-OPS-LAB` без push.

Завершение текущего gate не означает готовность package, прохождение preflight, принятие клиента, установку runtime или разрешение live rollout.
