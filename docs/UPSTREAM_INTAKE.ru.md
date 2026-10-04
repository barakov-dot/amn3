# Upstream: единый реестр решений и маршрут до реализации

Обновлено: 2026-10-04. Владелец: проект AMN3 / VPS-OPS-LAB.
Это реестр входящих доработок, не второй execution plan Phase 16.
Актуальная фаза и разрешённая работа определяются через [START_HERE](START_HERE.ru.md).

## Где продолжать

| Вопрос | Каноническое место |
| --- | --- |
| Правила новой задачи и upstream-обзора | [AGENTS](../AGENTS.md), этот файл |
| Что делать с сигналом `format_version` | [План проверки и последующей доработки](superpowers/plans/2026-09-20-upstream-format-version-review.ru.md) |
| Карточки кандидатов | [AMN2](../ideas/candidates-for-amn2.md), [hybrid](../ideas/candidates-for-hybrid.md) |
| Отобранная очередь и устойчивые запреты | [Приоритеты](../ideas/priority-backlog.md), [отклонённое](../ideas/rejected.md) |
| Что фактически изменилось | [CHANGELOG](../CHANGELOG.md), scoped Git diff/commit и receipt конкретной работы |

Подробные критерии задачи хранятся только в связанном плане; карточка идеи и
сообщение в задаче ссылаются на него. Перед реализацией исполнитель определяет
фактические checkout/HEAD/diff. Основной каталог и текущий worktree могут иметь
разную историю; отсутствие файла в старой ветке не доказывает отсутствие работы.
Временный путь Codex worktree не является постоянным идентификатором проекта.

## Приём сигнала

1. Зафиксировать официальный repository, прямой URL, полный commit/release cursor,
   `checked_at` с Europe/Moscow, предыдущий cursor и пределы покрытия.
   Незавершённый обзор не продвигает границу полностью проверенной дельты.
2. Проверить смысловой дубль во всех четырёх `ideas/*`, активном плане,
   истории Git и конкретных исходниках/тестах нужного checkout. Package snapshot
   не заменяет mutable source. Не обследовать соседние проекты вне scope.
3. Назначить ровно один статус: `уже реализовано у нас`, `уже учтено в плане`,
   `новый кандидат для AMN2`, `hybrid-only`, `не подходит/небезопасно`,
   `недостаточно данных`. Последний статус включает точный вопрос и способ проверки.
4. Для принятого кандидата указать проблему, локальный компонент, приоритет,
   фазу/зависимость, минимальную проверку, условия отказа, лицензионные границы.
   Merge в dev не равен stable release; описание PR не доказывает local gap.
5. Доработка проходит связанный план: подтверждение применимости → выбранный
   контракт → ограниченные code/tests → readback/receipt. Переходы с новым scope
   требуют соответствующего разрешения; одно планирование не разрешает rollout.
6. После документационных правок: перечитать diff, проверить ссылки и whitespace,
   записать CHANGELOG. Для кода — целевые проверки и фиксация версии исходников.
   Отдельно сообщать recorded / implemented / verified / deployed.

## Восстановленная фиксация обзора 20.09.2026

Предыдущая standalone-задача 13.09 завершилась `НЕ ВЫПОЛНЕНО` и не дала новых
надёжных SHA. Ниже previous cursors взяты из памяти прогона 07.09 (для AWG Go —
из более раннего наблюдения). Утром 20.09 API подтвердил следующие heads;
поминутные `checked_at` каждого утреннего запроса не сохранены, их не выдумывать.
Узкая перепроверка PR #3184 выполнена в этом дополнении; контрольный readback
документа зафиксирован 20.09.2026 13:54 Europe/Moscow.

| Источник | Previous cursor → observed head / release | Покрытие и пробел |
| --- | --- | --- |
| [PRVTPRO/Amnezia-Web-Panel](https://github.com/PRVTPRO/Amnezia-Web-Panel) | `c3410b9116a23c4a10087265430e405846bd0b10` → `02c1182284d0f5a7b9d5f034a15c77a9fb966c00`; `v1.6.7` | Compare показал 161 commit; просмотрены выбранные PR и недельные commits, весь диапазон и существенные issues не сверены. Полной новой baseline нет |
| [kyoresuas/amnezia-api](https://github.com/kyoresuas/amnezia-api) | `deff5b750e74b0c6b9b9fc96c168e00495deea4b` → тот же SHA; `v2.0.0` | Main и latest release без дельты; отсутствие новых существенных issues/open PR не доказано |
| [amnezia-vpn/amnezia-client](https://github.com/amnezia-vpn/amnezia-client) | `327e5985df0ef16ea03058b611e171b1d3bc0420` → `94b51df24790bf52427afe82d81c87a95460bdfd`; `5.0.1.5` | 12 commits после cursor; подробно разобран #3184, остальные сигналы не считаются полностью закрытыми |
| [amnezia-vpn/amneziawg-go](https://github.com/amnezia-vpn/amneziawg-go) | `1b86b2a` (сохранён только короткий cursor) → `b5928efb6ca19f0153958460c3d141f04abc5c2e` | Два commit от 28.08; после 13.09 новых commits не получено. `/releases/latest` дал 404: это не доказательство отсутствия tags/releases. Остальные официальные AWG-репозитории не покрыты |

Итог исходного weekly-обзора остаётся `ЧАСТИЧНО`. Документальное исправление
не превращает его в полный аудит. Следующий weekly сначала дочитывает непокрытый
диапазон и официальные releases/tags/issues/PR, затем продвигает cursor.
Постоянный список источников автоматически не расширяется.

## Разбор сигналов без выдачи предположений за реализацию

| Сигнал и точный upstream cursor | Статус | Следующее действие |
| --- | --- | --- |
| [Client 5.0.3.0](https://github.com/amnezia-vpn/amnezia-client/releases/tag/5.0.3.0), de93650a90739b87bb47a632872ea9d0adc9412f | уже учтён в плане | [Release/source review 21.09](../research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md): assets Windows/Linux/macOS/Android; Windows AWG pin прежний, traffic fix не доказан; последующая iOS store-проверка ниже. Не продвигает weekly cursor и не разрешает retest |
| [Amnezia iOS 5.0.3](https://apps.apple.com/us/app/amneziavpn/id1600529900), US Store release 21.09.2026 | уже учтён в плане | [Store recheck](../research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md#client-store-recheck-2026-09-21): официальный выпуск подтверждён; installed build/source и исправление прежних дефектов не доказаны. Retest/A/B не возобновляются |
| [DefaultVPN 2.0.2](https://apps.apple.com/ru/app/defaultvpn/id6744725017), Store release 21.09.2026 | уже учтён в плане | [Свежий RU/US lookup](../research/amn2/phase16-amnezia-client-5.0.3.0-release-review-2026-09-21.md#defaultvpn-202-store-confirmed): официальный выпуск подтверждён после уточнения оператора; прежние2.0.1 metadata устарели. Notes: стабильность; binary/source и исправления NAME/MTU/import ещё не доказаны |
| [Client #3184](https://github.com/amnezia-vpn/amnezia-client/pull/3184), `aca1b7dc5cad014a5f22f218655195fd8381cbad`: версия формата | уже учтено в плане | Шаг 2 закрыт решением NO_CHANGE_REQUIRED: добавление поля сейчас не требуется. Матрица/52 offline PASS в связанном плане; exact iPhone build UNKNOWN |
| [Panel #163](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/163), `a0e15af3ac9d7b88c460ebfe2e22525c13e131eb`: sudo secret вне command line | уже учтено в плане | См. `Safe SSH/sudo policy` и отклонённый `Sudo password inside command string`; наличие записи не выдавать за доказанную реализацию |
| [Panel #174](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/174), `cb0a5db3b568befe96792f4278baa493129011f5`: блокирующий SSH и backoff | уже учтено в плане | Web slice: 2069e41, 33 PASS/review без замечаний. Bot design/inline plan утверждены, Tasks 1–4 и fixes независимого review: 1bd7f62, 312 локальных PASS. [Receipt](../research/amn2/phase16-ssh-event-loop-applicability-2026-09-20.md#bot-worker-реализация-и-проверки--2026-09-20); [план](superpowers/plans/2026-09-20-amn2-bot-workflow-worker-plan.ru.md). Retry policy отдельно; не развёрнуто |
| [Panel #175](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/175), `4a3f2f50f874fab8f3b9511cfc893717f66bacab`, и [#176](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/176), `3d30d4e3fbf8e99f193197eb55a17bedbfc7b4c2`: автоматическая смена kernel/userspace | не подходит/небезопасно | Автоматический перенос поведения не совместим с существующими runtime gates. Отдельный read-only контроль совместимости tools/kernel не отклонён этим решением |
| [Panel #165](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/165), `8f1e8a31a0785a4b84cdc8e907aa52a78d33843f`: IPv6 DNS | уже учтено в плане | Существующий hybrid `endpoint/DNS/subnet/IPv6 config model`; не называть двух-IPv4 DNS fix доказательством реализованного IPv6 DNS |
| [AWG Go](https://github.com/amnezia-vpn/amneziawg-go/compare/1b86b2a...b5928efb6ca19f0153958460c3d141f04abc5c2e): padding/cookies | новый кандидат для AMN2 | Declared source отстаёт; image/source binding не подтверждён. P2: происхождение fixed runtime и условная применимость DisableCookies; [результат](../research/amn2/phase16-awg-go-pinned-runtime-review-2026-09-20.md). Никакого автоматического обновления |

Client build/signing/test изменения и остальные Panel UX/ownership PR остаются
в непокрытом диапазоне. Их не объявлять ни новыми AMN2-кандидатами, ни закрытыми.

## Передача рабочей задаче

Передавать путь к этому файлу, связанному плану, baseline SHA и текущий diff,
а не пересказ как новый приказ реализовать всё. Публикация, сообщения другим
задачам и изменение автоматизации допускаются только в scope запроса оператора.
Для этой передачи пользователь разрешил документирование и уведомление актуальной
задачи; runtime, выдача, commit/push и расписание автоматизации не меняются.

<a id="upstream-intake-2026-10-04"></a>

## Применение рекомендаций обзора04.10 — локальные требования, не rollout

Оператор04.10 разрешил применить рекомендации и продолжить Phase16. Применено
в существующих карточках и базе передачи; новый runtime/config/code scope не
открыт. Weekly04.10 имеет собственную фиксацию10:05 Europe/Moscow; её сообщение
не заменяет source/receipt. Здесь12:38:48 Europe/Moscow отдельно проверены
official GitHub metadata PR183/200 и release `v1.7.3`. Это узкая intake-проверка,
не повтор полного weekly и не продвижение historical fully-reviewed cursors.

| Сигнал / exact cursor | Единственный статус / решение | Где применять |
| --- | --- | --- |
| [Panel #183](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/183), merged `40ebb7418659b5c8da40e0fe1507f2ba33dbd7ba` | уже учтено в плане; P3 **отложить** после image/source binding и Phase16 transfer queue | Существующая MTU budget карточка04.10 в [AMN2 candidates](../ideas/candidates-for-amn2.md); не добавлен дубль |
| [Panel #200](https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/200), merged `518f051ef51aed5b4ba57afa0670434a20753982`, [release v1.7.3](https://github.com/PRVTPRO/Amnezia-Web-Panel/releases/tag/v1.7.3) | hybrid-only; P2 при проектировании целевого multi-instance UI, после target contract | Дополнен существующий [HYB-AI-001](../ideas/candidates-for-hybrid.md): context/request binding, delayed response и incomplete snapshot cases |
| [AWG Go #186](https://github.com/amnezia-vpn/amneziawg-go/issues/186), immutable affected `1f50ad736ecca22a9bfc7b4606805ec9ca49fe48` | уже учтено в плане; P2 **отложить** до runtime/image binding и source-contract проверки | Существующая H1–H3/RandomTrailers карточка27.09; это самостоятельный receive-path риск, не MTU budget |

Локальная сверка дополнительно выполнена по активному AMN2 source
`6e682356ed14a62d636ee58039fd3a389e794809` (clean checkout). В AWG3 renderer
проверяются types/one-line fields и S1–S4 >=12; budget MTU/S4/верхняя граница
ContentPaddingAddition не проверяется. Native exporter сохраняет переданный
MTU и предупреждает о client overwrite, это иной слой. Weekly карточка ссылается
на более старый `56540e2`; вывод о целевой доработке сохраняется и для6e68235.
Это не доказанный production defect или root cause исторического quality FAIL.

Будущий независимый contract должен задавать link-MTU input, overhead каждого
поддерживаемого transport/runtime, padding upper bound, явный MTU override и
поведение при insufficient budget. Если budget ниже минимально допустимого MTU выбранного transport, результат —
STOP/insufficient budget; нельзя просто повысить его до порога и объявить
безопасным. Формулу/порог выбирают после exact runtime
source, проверяют synthetic boundary cases; AWG2/legacy и уже выданные профили
не меняются попутно. Upstream GPL code/UI/templates не копируются.

[База передачи](PHASE16_CROSS_PROJECT_KNOWLEDGE_HANDOFF_2026-09-23.ru.md#upstream-recommendations-2026-10-04)
содержит маршрут будущему разработчику, а [receipt](../research/amn2/phase16-upstream-intake-application-2026-10-04.json)
разделяет applied requirements и NOT_IMPLEMENTED/NOT_DEPLOYED. Текущий M0f seal
packet не меняется; deferred client checks не возобновляются. Применение критериев
к новому UI требует его реального кода/target contract; иной проект не обследован.
