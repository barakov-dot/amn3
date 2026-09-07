/GO PHASE 16 — AWG3 FAMILY 3.1, SPAIN PREFLIGHT, CONTROLLED STAGE AND ONE PILOT

## Актуальный порядок и gates — 2026-09-05, дополнение 2026-09-07

Это единственный актуальный execution status Phase 16. Датированные разделы
ниже сохраняют историю и не разрешают повторять старые GO, claims или stage.
Локальный baseline аудита: `7450435a59e1f648bdcd8880c146f2c3320678db`.

Завершённый docs-only approval: `/GO PHASE16 APPLY REVIEWED PLAN_AND_GATE_DOCUMENTATION_CORRECTIONS LOCAL_DOCS_ONLY PRESERVE_HISTORICAL_RECEIPTS NO_CODE_CHANGE NO_TEST_RUN NO_PACKAGE NO_LIVE_ACTION NO_PUSH AWG2_UNTOUCHED`.
Документационная поправка зафиксирована в `15e7d2d15922919aefb9d5721dc4f285042490e7`.

Последующий local GO: `/GO PHASE16 FIX_LOCAL_DNS_GENERATOR_TWO_IPV4_COMPATIBILITY TDD_ONE_TARGETED_SUITE NO_REAL_CONFIG_GENERATION PRESERVE_EXISTING_PROFILES PACKAGE016_IMMUTABLE NO_LIVE_ACTION NO_INSTALL NO_PUSH AWG2_UNTOUCHED`.
DNS-исправление завершено локально: RED/GREEN и один итоговый набор 28 PASS.
Это не исправление live runtime и не снятие client/quality blockers. Evidence:
`research/amn2/phase16-local-dns-generator-two-ipv4-compatibility-2026-09-05.md`.
По решению оператора iPhone и проверка двух сетей ОТЛОЖЕНЫ; не запрашивать
повторно импорт/сеть и не запускать A/B, пока оператор не вернётся к этому этапу.

2026-09-07 по операторскому «продолжай» подготовлен
[проект критериев приёмки v1](../../PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md).
Статус `DRAFT_NOT_APPROVED_NOT_EXECUTED`: числа предложены, но не утверждены;
live-методы, endpoint/time/data bindings ещё требуют подготовки. Переоценки
прошлых результатов, повторных тестов, server действий и push не было.

Последующее согласование 2026-09-07: операторское «согласовываю» относится к
критериям v1 в редакции `b165c5b6b4914bb2befd1c25b78dd6cba48e8ab6`.
Текущий статус критериев — `CRITERIA_APPROVED_NOT_EXECUTED`; числа не изменены.
Методы и endpoint/time/data bindings ещё не готовы. Согласование не разрешает
live, stage/install, изменение конфигураций или push; iPhone/A/B остаются отложенными.

### Доказательства и границы

- Android/iPhone connectivity и iPhone reconnect подтверждены предыдущими
  наблюдениями; повторять их только ради того же PASS не требуется.
- Windows: адаптер, адреса, MTU 1280 и default routes присутствовали, прикладной
  трафик не работал. Совпадение симптомов с issue #3043 не доказывает upstream
  root cause. Kill-switch A/B и поиск отсутствующего адаптера уже отработаны.
- Source-bound TCP/IPv4 HTTPS проверяли 28 августа: TCP прошёл, HTTPS дал
  TLS-error/timeout. Общий повтор IPv4 HTTPS без новой гипотезы не планируется.
  Evidence: `research/amn2/phase16-arm-dns9-check-2026-08-28.md`.
- Quality остаётся FAIL для acceptance; строгий Spain AWG2/AWG3.1 A/B неполон.
  Незавершённые speedtest-снимки и ICE timeout не превращаются в итоговые
  измерения или процент потерь. Смена маршрута/площадки ограничивает сравнение
  no-VPN/VPN; post-run CPU не исключает нагрузку во время передачи.
- Release/dev/issue receipts действуют на дату чтения. Сравнение 9 commits /
  78 files от 30 августа не является текущим readback; в этом GO сети нет.
- Spain AWG2 IPHONE d7 ZIP найден и checksum-проверен при подготовке передачи;
  новая выдача не нужна. Импорт на iPhone и тип второй физической сети пока
  требуют ответа оператора. Копия в Downloads не доказывает доставку/импорт.
- Application integration не завершена: прежние stage-попытки STOP; recovery
  transaction 007 наблюдал отсутствие проверенных ресурсов, а не успешный
  stage или доказанный rollback. Minimal pilot не устранил старый transport defect.

### TASK_PLAN_BY_CRITICALITY

1. P0, отложено оператором — подготовка одного A/B: подтвердить импорт d7 и физическую сеть, заранее
   записать метод, цель, лимиты времени/трафика и правила интерпретации.
   Live требует exact approval; текущий docs-only GO его не даёт.
2. P0, отложено оператором — один последовательный same-device/same-app/same-access-network Spain
   AWG2/AWG3.1 A/B с существующими профилями. Если оба пути плохи — исследовать
   общий путь; если только 3.1 — его отличия. Это направление расследования,
   не доказанная причина. Неоднозначность не запускает автоматический повтор.
3. P1 — Windows: следующий bounded test допустим после значимого изменения
   официального клиента/engine ИЛИ новой проверяемой гипотезы. До live approval
   записать отличия от прошлых проверок и вывод для каждого исхода.
4. P1, локально завершено — DNS-генератор принимает два IPv4 DNS и сохраняет
   legacy single-DNS validation. Новая файловая подготовка требует ровно два
   явно заданных адреса до чтения ключей/записи. Независимая проверка формы
   DNS-строки и один итоговый набор 28 PASS; полный Qt import не выполнялся.
   Существующие профили, package 016 и live script не менялись. Это не fix
   Windows/quality. Развёртывание или реальная генерация требуют отдельного approval.
5. P2 — после Windows и quality gates: отдельная checksum/state/rollback-bound
   интеграция. Проверить актуальность состояния, persistence временных правил,
   restart policy, отсутствие утечек и границы отката в разрешённом этапе.
   Затем Task 5 acceptance и Task 6 closeout.

### Политика проверок

- Каждый новый прогон имеет конкретный вопрос, заранее заданные outcomes,
  лимиты и stop-condition. Ошибка инструмента означает UNKNOWN, а не
  неисправность проверяемого компонента.
- Docs/receipt-only: проверка diff, ссылок, согласованности и отсутствия секретов;
  без pytest, materialization, package verifier и повторного server preflight.
- Наш код: один целевой RED/GREEN и один релевантный итоговый набор. Повторять
  после новых изменений/ошибок, не после одной лишь фиксации результата.
- Сохранять checksum, one-shot claims, AWG2 equality, secret redaction и точный
  rollback. Source-string checks не заменяют поведенческие проверки. Исторические
  package checks нужны при затрагивании пакетов/упаковки, не для клиентского A/B.
- TDD требуется для нашего code fix. Исправление upstream или внешней причины
  требует соответствующего evidence и bounded verification, не обязательной
  собственной замены протокола. Root-cause gate не отменяется.
- Численные пределы throughput, loss, RTT/jitter, reconnect, длительность
  stability window и правило missing measurements согласованы в критериях v1.
  Не пересчитывать прошлые результаты задним числом по этим порогам.
  MTU/fragmentation, DNS, server metrics и AWG2/AWG3.1 A/B остаются обязательными.

### Текущий вертикальный статус

- ✅ Task 0 — baseline.
- ✅ Task 1 — package 016/local tooling; DNS follow-up выполнен только локально.
- ✅ Task 2 — исторические Spain gates/diagnostics; не свежий preflight.
- ✅ Task 3A — minimal runtime и прошлые connectivity evidence.
- ⏳ Task 3B — integration не завершена; прежние stage-попытки STOP.
- ❌ Task 4A — Windows application traffic FAIL; root cause не доказана.
- ✅ Task 4B — Android connectivity; performance не принят.
- ✅ Task 4C — iPhone connectivity/reconnect; performance не принят.
- ❌ Task 4.5 — quality FAIL; root cause открыта; strict A/B неполон и отложен.
- ⏳ Task 5 — acceptance заблокирован.
- ⏳ Task 6 — closeout заблокирован.

AWG2_UNTOUCHED; general issuance disabled. iPhone/A/B отложены, не отменены.
Критерии acceptance v1 согласованы. В том же документе подготовлено приложение
«Методика m1»: `METHOD_DRAFT_BLOCKED_NOT_EXECUTED`. Предложены конечные time/body/
probe budgets, но endpoint manifest, устройство/метод, stability coverage и
transport-byte cap enforcement не подтверждены. Следующий gate — разрешить эти
пробелы без подмены устройства/установки/автопрогона; точный live approval пока
не готов. iPhone/A/B остаются отложенными.

2026-09-07 по отдельному `MINIMAL_WINDOWS_MEASUREMENT_HELPER LOCAL_CODE_ONLY
OFFLINE_TDD` GO реализована только локальная часть m1: PowerShell-функции RTT/
throughput и bounded process, без сетевых адаптеров/профилей. RED/GREEN и один
итоговый набор 15 offline tests PASS. Evidence и ограничения — в приложении
«Реализованная локальная часть m1» документа критериев. Полного live runner и
server collector нет; этот PASS не снимает Windows/quality/root-cause gates.
Следующее расширение к сетевому измерителю требует отдельного scope и точных
endpoints/limits; автоматически не создаётся и не запускается.
Push требует отдельного exact approval и в текущем GO запрещён.
Следующий разрешённый HTTP-only GO выполнен локально 2026-09-07:
bounded numeric metadata, один explicit GET/POST через curl и нормализованная
проверка полноты/HTTP/TLS. Итоговый целевой набор 24 offline tests PASS;
HTTP/curl/network не запускались. Evidence и границы — раздел «Минимальный
HTTP-адаптер» того же документа критериев. Статус
`LOCAL_OFFLINE_VERIFIED_NOT_LIVE_VALIDATED`; DNS/ICMP, endpoint admission,
series/transport budget и server/stability observers ещё не готовы.
Следующий полезный локальный шаг — отдельно ограничить scope DNS/ICMP-адаптеров;
не запускать повторный Windows тест и не объявлять методику готовой к live.
Рекомендация модели по запросу оператора: GPT-6 Astra / HIGH, один основной
агент; это не утверждение о runtime effort и не разрешение live action.

## Исторический BOUNDED LOCAL GO — PACKAGE 016, 2026-08-27 (завершён)

- Exact baseline: `392cc339f7f6afaed0a0dc2a0a80139ca030f560`; local-fix receipt SHA256: `549b515ea50e7668f56f433772633a63c674aaba973876f978f0a2ea15f823de`.
- Подготовить `phase16-awg3-family-3-1-spain-pilot-20260824-016`: обновить только package/branch bindings и evidence. Сохранить исправленный scalar exit и BOM-free binary stdin producer; новый transport fix не разрешён.
- Один focused binding RED/GREEN, один итоговый targeted regression, локальные commits, ровно одна materialization и один separate verifier. Не повторять их после receipt-only commit.
- Package 015 immutable; transaction `phase16-spain-stage-20260827-006` consumed и не переиспользуется. Исторические результаты ниже не являются новым remote readback.
- NO_SPAIN_EGRESS, NO_REMOTE_WRITE, NO_STAGE, NO_INSTALL, NO_CONFIG, NO_ISSUANCE, AWG2_UNTOUCHED. Task 2/3 и прежние approvals не разрешают внешний запуск этой ревизии.
- После локального PASS запросить новый exact checksum-bound preflight approval. Сохранить linked worktree и локальную ветку 016; push не выполнять до отдельного informed approval публичной публикации накопленной истории.
- Task 4 — первый pilot для АРМ/Windows; Task 4.5 — обязательный AWG2 ↔ AWG3.1 transport-quality A/B gate до Task 5 и closeout. Client admission/runtime/resource contracts этим GO не меняются.

ИСТОРИЧЕСКИЙ EXECUTION STATUS / ACCEPTANCE GATE — 2026-08-30, route/counter evidence commit `bb266df`

- Task 3A minimal isolated runtime завершён; Task 3B application integration не начинался и не разрешён.
- Android и iPhone подтвердили AWG3.1 connectivity одним checksum-bound peer последовательно. Это не performance/stability acceptance.
- Windows 11 / AmneziaVPN 5.0.1.5 создаёт активный Wintun, получает MTU 1280 и handshake/keepalive, но прикладной IPv4/DNS/HTTPS-трафик не проходит. Отключение kill switch результат не изменило. Граница зафиксирована как Windows client data-plane regression с совпадением по классу с открытой официальной upstream issue #3043; root cause не объявлен доказанным. Evidence: `research/amn2/phase16-windows-awg31-data-plane-regression-2026-08-29.md`.
- Синхронный route/counter watcher подтвердил активные IPv4/IPv6 addresses, MTU 1280 и default routes, а также двусторонний рост интерфейсных byte counters во время одного HTTPS timeout. Отсутствие full-tunnel route исключено; точная Windows tunnel data-plane/session root cause не доказана. Evidence: `research/amn2/phase16-windows-awg31-active-route-counter-diagnostic-2026-08-29.md`.
- Official GitHub status refresh: `5.0.1.5` остаётся Latest release (`prerelease=false`) и является уже установленным Windows x64 path; issue #3043 открыта без maintainer-confirmed fix. Issue #3064 про fallback MTU 1376 не совпадает с фактически применённым MTU 1280 этого пилота. Stable release metadata не отменяет failed compatibility evidence. Evidence: `research/amn2/phase16-windows-official-upstream-status-2026-08-29.md`.
- Source-level refresh: compare `5.0.1.5...dev` содержит 9 commits и 78 файлов, но не меняет Windows tunnel/route/session paths; tag и `dev` используют один `awg-windows/3.1.20260814`. Issue #3043 не имеет linked fix, #3050 остаётся corroborating speed report, а #3073 про ranged H1-H4 не совпадает с fixed values пилота. Повторный live test того же Windows engine path не обоснован. Evidence: `research/amn2/phase16-windows-official-source-level-status-2026-08-30.md`.
- iPhone connectivity/reconnect/DNS/HTTPS прошли, но три AWG3.1 quality-прогона существенно хуже здорового no-VPN baseline. Строгий same-device AWG2 ↔ AWG3.1 A/B не завершён из-за отсутствия актуального Spain AWG2-профиля на iPhone. Evidence: `research/amn2/phase16-iphone-awg31-quality-and-server-metrics-2026-08-29.md`.
- Alternate-network iPhone retest: HTTPS, YouTube, Telegram и reconnect 2–5 секунд прошли, но AWG3.1 против download-limited no-VPN baseline существенно ухудшил upload, latency и jitter до и после reconnect. Baseline loss не измерен из-за ICE timeout; strict Spain AWG2 ↔ AWG3.1 A/B остаётся incomplete. Evidence: `research/amn2/phase16-iphone-awg31-alternate-network-quality-retest-2026-08-30.md`.
- Task 4.5 имеет статус `quality-fail-root-cause-open-strict-ab-incomplete`. Пока AWG3.1 нестабилен, Task 5 acceptance и Task 6 closeout заблокированы.
- Task 3B нельзя начинать до закрытия обоих client gates: Windows должен пройти bounded retest на официально поддерживаемом upstream client path, а AWG3.1 quality — исправленный bounded retest и обязательный последовательный AWG2 ↔ AWG3.1 A/B.
- Не менять server, UDP 30002, DNS, MTU, firewall или профиль наугад. General AWG3 issuance остаётся disabled; AWG2_UNTOUCHED.

Исторический вертикальный статус на 2026-08-30:

- ✅ Task 0 — baseline.
- ✅ Task 1 — package 016/local tooling.
- ✅ Task 2 — Spain gates/diagnostics.
- ✅ Task 3A — minimal isolated AWG3.1 runtime.
- ⏳ Task 3B — application integration: не начат, не разрешён.
- ❌ Task 4A — Windows: upstream-class data-plane/session blocker; route absence excluded, official source fix absent.
- ✅ Task 4B — Android/projector connectivity; performance не принят.
- ✅ Task 4C — iPhone connectivity/reconnect; performance failed on two access networks.
- ❌ Task 4.5 — quality FAIL/root cause open across two networks; strict A/B incomplete.
- ⏳ Task 5 — acceptance заблокирован.
- ⏳ Task 6 — closeout заблокирован.

Ниже — исходный план и сохранённые требования предыдущих ревизий. При конфликте
действует раздел «Актуальный порядок и gates — 2026-09-05»; исторический GO
на сборку package 016 не является текущей очередью действий.

Выполнить единую Phase 16 внутри проекта VPS-OPS-LAB. Эта фаза объединяет ранее предполагавшиеся Phase 16 и Phase 17. Не создавать отдельную Phase 17.

Модель:
- GPT-5.6 SOL High;
- reasoning High;
- один основной агент;
- не использовать subagents и независимых reviewers.

Цель:
1. Довести семейство AWG3 до текущей ревизии 3.1.
2. Один раз собрать новый checksum-bound Phase 16 package.
3. Выполнить checksum-bound Spain read-only preflight.
4. После отдельного approval выполнить controlled stage.
5. После отдельного approval выдать ровно один операторский AWG3.1 pilot config.
6. Проверить его на реальном клиенте и принять либо откатить пилот.

ОПЕРАТОРСКОЕ УТОЧНЕНИЕ — 2026-08-27: ФОРМАТ СТАТУСА И GIT

- После каждого прогона показывать полный статус Phase 16 вертикальным списком: отдельная строка для Task 0, 1, 2, 3, 4, 4.5, 5 и 6. Использовать `✅`, `▶️`, `⏳`, `❌`; не сжимать список в одну строку ни в промежуточных обновлениях, ни в итоговом ответе.
- После завершения одобренного шага коммитить относящиеся к нему изменения и публиковать текущую именованную Phase 16-ветку в уже настроенный `origin`. Не создавать пустые коммиты и не включать unrelated changes.
- Это прямое указание оператора заменяет прежний общий запрет `NO_PUSH` только для указанной Git-публикации. Более поздний явный запрет конкретного запуска сохраняет приоритет.
- Перед push проверять remote, исходящий состав и отсутствие чувствительных данных; после push подтверждать совпадение remote HEAD и локального commit SHA. При блокере не считать push выполненным.
- Не выполнять force-push, merge, push в `master`/`main`, публикацию других веток или создание PR без отдельного указания.
- Рабочую ветку и linked worktree сохранять. Immutable packages не изменять; для receipt-only/doc-only commit не повторять package materialization, verifier или полные suites.
- Разрешение Git commit/push не разрешает Spain SSH, диагностический egress, повтор preflight, stage/install, rollback, создание конфигов или issuance. Их exact approval gates сохраняются; AWG2 не затрагивать.

РАБОЧИЙ КОНТЕКСТ

Основной проект:
C:\Users\SooL\Documents\VPS-OPS-LAB

Exact Phase 15 application source baseline:
- worktree:
  C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness
- HEAD:
  c01c2e34ca506102e485ee3fa50b9420de6e591a

Exact Phase 15 tooling/receipt baseline:
- worktree:
  C:\Users\SooL\Documents\VPS-OPS-LAB-phase15-local-package-bootstrap-readiness
- HEAD:
  1c945dcfcda92c2945fe71ee95f9219546c1f4e3

Phase 15 baseline package:
- package ID:
  phase15-dual-protocol-bootstrap-20260811-001
- package identity:
  00b56972a7e3f3423fb3a1d6437f877910b6f23c690fe9a398ce8263d74faf1d
- manifest:
  d99e6e6b7df651f7cda6f63de2ee9b2a353afef4bfe1c93e82391d5c48aac6df
- collector:
  e122315df1db91f654da0411ef08cadaa15a4a4e6318f1973444ec1d531b6465
- source-readiness receipt:
  0d45708c6aab6b7812ffa8ca05d052f1db175086f57c504b5af8e1f6a99c4eb8
- package-readiness receipt:
  040a9959f60ce725a9aa626d299d482b782da317fed11de0fd39193fe71f911d
- runtime lock:
  a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab
- test lock:
  52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235

Phase 15 package является baseline/readiness evidence. Не использовать его для AWG3.1 staging: текущие stage scripts намеренно inert, а application renderer ещё не содержит AWG3.1 fields.

УТВЕРЖДЁННОЕ ПРОДУКТОВОЕ РЕШЕНИЕ

- `awg3` — постоянное семейство протокола AWG 3.*.
- Текущая активная ревизия — exact `3.1`.
- Не создавать `ProtocolVersion.AWG31`, отдельный protocol profile или отдельную Phase 14.1.
- Сохранять `ProtocolVersion.AWG3 = "awg3"` и существующую dual-protocol модель AWG2/AWG3.
- Для новой выдачи использовать exact config revision `amneziawg_v3_1`.
- Старый `amneziawg_v3` считать известным предыдущим форматом, но не использовать для нового pilot issuance.
- Будущие `3.2`, `3.3` и другие `3.*` относятся к семейству `awg3`, но не принимаются автоматически: exact revision/runtime/capability/client admission остаётся обязательным.

OFFICIAL UPSTREAM BASIS

Использовать только как независимо реализуемый контракт, без копирования GPL client code/UI:

1. AmneziaVPN AWG3.1:
   PR #2984
   merge commit 44c10b39e38471a78f6090c96acffac626faec82

2. Android AWG3.1:
   PR #91
   merge commit d6cd6647465a9a593aa9ccadbbd20c44bf600d5b

3. Runtime AWG3.1:
   amneziawg-go commit
   1f50ad736ecca22a9bfc7b4606805ec9ca49fe48

4. Android pilot candidate:
   AmneziaWG v3.1.20260814
   release commit 5c16489e2cd9ed3a0a7a27c7445bba5238132f86

5. AmneziaVPN 5.0.1.5 официально опубликован как Latest release; GitHub
   metadata сообщает `prerelease=false`. Классифицировать его как
   `release_kind=stable`, но связывать release metadata отдельно от
   compatibility result: Windows data-plane FAIL запрещает global acceptance.

6. Не включать незавершённый `libagw` PR #3028.

TASK 0 — EXACT LOCAL BASELINE

Read-only подтвердить:

- оба exact HEAD;
- named branches;
- linked-worktree state;
- clean tracked worktrees;
- отсутствие unexpected source/tooling diffs;
- Phase 15 package/receipt identities.

Не удалять и не изменять unrelated untracked files.

При несовпадении exact baseline:
STOP и сообщить только конкретное несовпадение.

TASK 1 — BOUNDED LOCAL AWG3.1 DELTA

Application:

1. Сохранить `ProtocolVersion.AWG3 = "awg3"`.

2. Добавить exact config revision:
   `amneziawg_v3_1`.

3. Новая AWG3 issuance должна использовать только `amneziawg_v3_1`.

4. Расширить typed AWG3 config input двумя обязательными параметрами:

   RandomTrailers = on
   DisableCookies = on

5. Использовать точные native config keys:

   `RandomTrailers`
   `DisableCookies`

6. Значения должны иметь строгий typed boolean/on-off contract.
   Blank, malformed, contradictory, missing или unknown capability должны fail closed до генерации ключей, БД и peer/runtime side effects.

7. Связать в provider/receipt identities:

   - protocol_family = awg3;
   - protocol_revision = 3.1;
   - exact runtime identity;
   - exact capability set;
   - exact client application/platform/version/build;
   - exact compatibility evidence.

8. Runtime должен быть закреплён на официальном artifact/digest, реально поддерживающем UAPI:

   - random_trailers;
   - disable_cookies.

9. Не принимать runtime только по названию/tag. Нужны pinned digest и capability evidence.

10. Сохранить AWG2 golden bytes, AWG2 allocation, runtime, profiles, peers и Phase 14 contracts без изменений.

Tooling:

11. Реализовать существующие Phase 15 inert stage envelopes как Phase 16 controlled stage operations.

12. Новый package ID:

   phase16-awg3-family-3-1-spain-pilot-20260824-016

13. Stage scripts должны оставаться checksum-bound, state-bound, claim-bound, fail-closed и rollback-aware.

14. Никаких Spain/SSH/remote действий во время Task 1.

15. Package 014 остаётся checksum-immutable; package 015 сохраняет передачу `StageExpectedHost`, fixed runner STOP/outcome и local hash/length-only transport evidence. Transaction 004 consumed и не переиспользуется.

16. Application stage использует текущую БД `/var/lib/amn2-spain/amn2.sqlite3` и Python `sqlite3.Connection.backup`; зависимость от `sqlite3` CLI запрещена.

17. AWG3.1 runtime использует только `/opt/amn2-spain/docker/bin/docker` и `unix:///run/amn2-spain-docker/docker.sock` под `amn2-spain-docker.service`.

18. Server-only AWG3.1 config генерируется внутри controlled stage, имеет ноль `[Peer]` и не включает global issuance.

19. Controlled stage coordinator обязан проверять exact package manifest/identity, approval checksum, current-state checksum и canonical rollback-scope checksum; при failure удаляются только созданные транзакцией ресурсы, checksum-bound SQLite backup сохраняется.

20. AWG2 freshness policy остаётся 600 секунд и не изменяется этим исправлением.

21. Package 015: claim `consumed` означает только вход. `application_complete`, `runtime_entry`, `runtime_complete`, post-runtime AWG2 snapshot/equality и публикация outcome фиксируются раздельно в ordered transaction-bound `milestones.json`.

22. На failure coordinator сохраняет `failure-locus.json` только с allowlisted locus/class, milestone prefix, claim-entry classes, checksum bindings и normalized runtime-image class. Raw stdout/stderr/exception text не сохраняются; терминальный failure outcome остаётся фиксированным.

23. Milestone `*_entry` означает вход coordinator в вызов этапа; фактическое consumption подтверждается отдельным claim-entry class. Completion записывается только после успешного возврата stage subprocess, а не из status claim.

24. Mandatory rollback выполняется до публикации failure artifact; ошибка одного действия не пропускает остальные действия в прежнем rollback scope. `rollback_attempts_completed`/`attempts_completed_unverified` не равны resource readback или доказательству clean remote; ошибка отмечается как `attempt_failed`. Backup и transaction audit сохраняются.

25. Runtime-image class выводится из успешной bounded выдачи `docker image ls --all --digests --no-trunc`; неизвестная/неуспешная выдача даёт `query_failed`. Текст daemon errors не является доказательством отсутствия image.

Для текущего local `/GO` package 015 разрешены только TDD, локальные commits, одна materialization и один separate verifier. Ни раздел Task 2 ниже, ни прежние approvals не разрешают egress этой ревизии: новый Spain preflight требует нового exact checksum-bound `/APPROVE`. Stage/install/config/issuance запрещены текущим запуском.

TASK 1 TESTING

Использовать TDD, но только targeted tests:

- AWG3.1 typed config rendering;
- exact `RandomTrailers = on`;
- exact `DisableCookies = on`;
- missing/malformed/unknown revision and capability rejection;
- exact config revision mapping;
- runtime/evidence/build/provider content identity;
- stable release metadata does not override failed compatibility evidence or
  permit global acceptance;
- stage claim and rollback boundaries;
- AWG2 preservation tests непосредственно рядом с изменённым кодом.

Не выполнять:

- полный source suite;
- полный legacy tooling suite;
- четыре независимых review;
- whole-branch review;
- Codex Security whole-diff scan;
- повторные fresh-review rounds;
- многократную package materialization;
- повтор verifier после receipt-only commit;
- subagents.

Разрешены:

- один focused RED/GREEN cycle на изменяемый контракт;
- один targeted regression suite;
- `git diff --check`;
- exact changed-file scope check;
- короткий added-line secret scan;
- один package materialization;
- один package verifier pass.

При первом unexpected test failure:
- диагностировать;
- разрешён один bounded scoped correction.

При втором unexpected failure или расширении scope:
STOP и сообщить blocker, без самостоятельного fix/review loop.

TASK 1 OUTPUT

После PASS:

- сделать локальные commits;
- materialize package ровно один раз;
- verifier выполнить ровно один раз;
- вывести exact:
  - application source SHA;
  - tooling SHA;
  - package ID;
  - package identity;
  - manifest SHA-256;
  - collector SHA-256;
  - receipts;
  - runtime/client artifact identities;
  - targeted test result;
  - clean status.

Receipts изменять только при реальном изменении evidence.

TASK 2 — CHECKSUM-BOUND SPAIN READ-ONLY PREFLIGHT

Этот `/GO` явно разрешает после успешного Task 1 выполнить один Spain read-only preflight новым Phase 16 package.

Разрешено:

- один checksum-bound upload/transport нового пакета;
- read-only SSH;
- read-only OS/runtime/application/AWG2/resource inspection;
- проверка exact current-state SHA;
- проверка свободных AWG3 resources;
- проверка rollback prerequisites;
- удаление только созданных этой операцией временных transport artifacts.

Запрещено:

- stage;
- install;
- service mutation;
- container creation/start;
- firewall/routes mutation;
- DB migration;
- peer/config/QR creation;
- issuance;
- AWG2 restart/stop/change;
- live AWG3 runtime start;
- push вне разрешённой текущей Phase 16-ветки, force-push или merge.

При transport timeout:
- проверить отсутствие orphan upload process и partial remote artifact;
- не делать blind retry;
- STOP с точным transport status.

При любом preflight mismatch:
STOP без fix loop и без staging.

TASK 2 OUTPUT / STAGE GATE

После PASS подготовить:

- preflight receipt;
- observed state SHA;
- new package/checksum identities;
- exact intended stage resources;
- rollback scope.

Затем STOP.

Вывести один exact следующий approval:

/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_<PACKAGE_ID> IDENTITY_<PACKAGE_IDENTITY> MANIFEST_SHA256_<MANIFEST_SHA256> STATE_<STATE_SHA256> ROLLBACK_SCOPE_SHA256_<ROLLBACK_SCOPE_SHA256> TRANSACTION_<TRANSACTION_ID> MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED

Не выполнять stage без этого отдельного сообщения пользователя.

TASK 3 — CONTROLLED STAGE

Только после exact `/APPROVE ... STAGE`:

1. Stage application.
2. Stage isolated AWG3.1 runtime.
3. Не включать general issuance.
4. Не создавать peers/configs.
5. Не менять AWG2.
6. Проверить:
   - service/container health;
   - UDP/listener/interface/bridge/CIDR ownership;
   - runtime revision/capabilities;
   - application bootstrap;
   - AWG2 equality;
   - отсутствие recovery markers.

При failure выполнить только заранее ограниченный rollback из approval и подтвердить его readback.

После PASS — STOP.

TASK 3 OUTPUT / PILOT GATE

Зафиксировать:

- staged application/runtime identities;
- AWG2 equality receipt;
- health result;
- exact pilot client candidate;
- exact proposed pilot device/passport;
- exact rollback target.

Затем вывести один approval:

/APPROVE PHASE16 ONE_AWG31_OPERATOR_PILOT CLIENT_<APPLICATION_PLATFORM_VERSION_BUILD> RUNTIME_<RUNTIME_IDENTITY> PACKAGE_<PACKAGE_ID> MANDATORY_PEER_ROLLBACK_ON_FAILURE NO_GLOBAL_ISSUANCE

Не создавать peer/config до этого сообщения.

TASK 4 — ONE AWG3.1 PILOT

Только после exact pilot approval:

1. Принять ровно один exact client build.

2. Предпочтительный Android target:
   AmneziaWG v3.1.20260814, exact installed build readback required.

3. Если используется AmneziaVPN 5.0.1.5:
   - сохранить `release_kind=stable` по текущему official GitHub metadata;
   - сохранить Windows compatibility result как failed/blocked независимо от
     release kind;
   - только admin pilot;
   - не включать global acceptance.

4. Создать ровно один AWG3.1 operator-owned profile/peer/config.

5. Delivery:
   - только `.conf`;
   - не создавать QR;
   - не создавать `vpn://`;
   - не включать public/self-service/global issuance.

6. Config должен содержать:

   - HeaderProtectionKey;
   - ContentPaddingAddition;
   - RekeyAfterTime;
   - RekeyTimeout;
   - RejectAfterTime;
   - KeepaliveTimeout;
   - MaxHandshakeAttempts;
   - RandomTrailers = on;
   - DisableCookies = on;
   - AllowedIPs = 0.0.0.0/0, ::/0.

Не печатать и не сохранять private key, PSK, HPK или полный config в logs/receipts.

TASK 5 — REAL CLIENT ACCEPTANCE

Текущий gate закрыт. Его нельзя открывать только по handshake, Android/iPhone
connectivity или здоровым server metrics. До acceptance обязательны одновременно:

- успешный bounded Windows retest на официально поддерживаемом client path
  с рабочими IPv4, DNS и HTTPS; основание нового прогона — значимое изменение
  клиента/engine или новая проверяемая гипотеза по актуальной политике выше;
- root-cause-bound correction и стабильная проверка AWG3.1 quality по заранее
  согласованным критериям; TDD для нашего кода, соответствующая проверка для
  официального исправления или внешней причины;
- завершённый последовательный same-device/access-network AWG2 ↔ AWG3.1 A/B
  по контракту Task 4.5;
- отдельный checksum/state/rollback-bound approval перед Task 3B application
  integration; успешный минимальный runtime не заменяет этот stage gate.

С участием оператора проверить:

- `.conf` import;
- tunnel activation;
- handshake;
- IPv4 traffic;
- DNS;
- reconnect;
- Wi-Fi/mobile network switch;
- client restart;
- server/application restart, только если отдельно подтверждён в pilot approval;
- отсутствие AWG2 regression.

При pilot failure:

- остановить general progression;
- выполнить только заранее утверждённый pilot peer rollback;
- подтвердить отсутствие orphan peer/profile/reservation;
- AWG3 general issuance оставить disabled.

TASK 6 — CONCISE CLOSEOUT

Подготовить один краткий handoff:

- final source/tooling/package identities;
- preflight result;
- staged runtime result;
- exact client build;
- pilot result;
- AWG2 equality;
- rollback status;
- что разрешено дальше;
- что остаётся disabled.

Не выполнять:

- повторные full suites;
- новые independent reviews;
- whole-branch review;
- повтор package materialization;
- rollout на других пользователей;
- global AWG3 issuance;
- push вне разрешённой текущей Phase 16-ветки, force-push или merge.

ОГРАНИЧЕНИЯ ВСЕЙ PHASE 16

- Один новый чат и одна Phase 16.
- Не создавать Phase 17.
- Не повторять процедуры Task 7/Task 8 Phase 15.
- Не изменять AWG2 golden bytes/runtime/peers.
- Не останавливать AWG2 для тестов.
- Не менять Phase 14 contracts, кроме минимального additive AWG3 revision wiring.
- Не трогать unrelated untracked files.
- Commit/push текущей Phase 16-ветки выполнять по операторскому уточнению от 2026-08-27; остальные ветки и remote-настройки не изменять.
- Не расширять scope на QR, vpn://, general import subsystem, libagw или global rollout.
- Любой scope expansion требует отдельного решения пользователя.

Ожидаемое время при штатном прохождении:
3–5 часов.

Начать с Task 0.
