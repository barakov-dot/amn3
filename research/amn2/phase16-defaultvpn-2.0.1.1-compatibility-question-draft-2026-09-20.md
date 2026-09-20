# DefaultVPN 2.0.1.1 — обращение и ответ поддержки

Статус: REPLY_RECEIVED_OPERATOR_PROVIDED / CLARIFICATION_NEEDED, 2026-09-20.
Оператор ранее сообщил «отправил», теперь предоставил текст ответа DefaultVPN
Team с отметкой 20:42. Почтовый ящик, заголовки и исходящая копия независимо не
проверялись. Ответ сопоставлен с русским текстом, подготовленным в этой задаче,
а не с порядком вопросов в первоначальном английском черновике ниже.
DefaultVPN остаётся отложенным несрочным направлением; новых тестов/отправок нет.
Исходный английский черновик сохранён как история, не как порядок ответов I–IV.
Адресат: support@dfvpn.com — контакт из раздела «О приложении» на скриншоте
оператора. Альтернативный контакт там же: @DefaultVPNSupport.
В официальном GitHub-репозитории DefaultVPN приём issues отключён.
Это запрос о проверяемости совместимости, не утверждение об ошибке MTU.
Письмо отправлял оператор; агент не выполнял отправку и не создавал issue.

## Тема исходного английского черновика

iOS 2.0.1.1 (cb7ea0c): source revision and per-profile native import verification

## Текст исходного английского черновика

The About screen of the installed iOS app displays:
DefaultVPN v. 2.0.1.1 (Aug 22 2026, cb7ea0c).

We are checking a synthetic AmneziaWG import, without a working VPN endpoint:

- Importing Neobyatnaya.NET.conf resulted in the displayed name "Server 1".
- A previous native vpn:// import with JSON description "Neobyatnaya.NET"
  displayed that exact name. The version of that earlier test was not recorded,
  so we do not assume both tests used an identical build.
- The synthetic config specifies MTU 1280 and AWG fields. We have not verified
  their saved or effective values inside the installed iOS client.
- The user could not find a parameter viewer or export for just one profile.
  We do not want to export a backup containing unrelated working profiles.

Could you please clarify:

1. Which public source commit or tag corresponds to iOS 2.0.1.1 / cb7ea0c?
   GitHub commit lookup did not resolve cb7ea0c in amnezia-vpn/DefaultVPN or
   amnezia-vpn/amnezia-client.
2. For .conf import, is there a supported filename rule or metadata field that
   preserves a custom display name instead of "Server 1"?
3. Does native vpn:// import in this build preserve an explicit MTU of 1280
   and the AWG parameters? Is the effective iOS configuration taken from the
   embedded raw config or reconstructed from the native JSON metadata?
4. Is there a supported way to inspect or export only the selected synthetic
   profile to verify these values without exposing other profiles?

We are not reporting a confirmed MTU bug or a connectivity failure. The naming
workaround is already available through the native format; the remaining question
is parameter preservation before enabling that export path in our delivery code.


## Ответ поддержки, предоставленный оператором — 2026-09-20

Источник: вставка оператора в этой задаче, без вложений и конфигураций.
Текст ответа сохранён полностью:

> Здравствуйте!
>
> I. К сожалению, такой возможности нет.
>
> II. Нет
>
> III. Вы можете отдельно создать файл конфигурации или ключ.
>
> IV. Это можно проверить на странице GitHub и сверить данные с информацией в AppStore.

Русская версия вопросов восстановлена из финального ответа задачи
«Продолжить Phase 16 recovery», turn 01a0bfce-956c-7312-b133-e4133b6945b0,
message msg_0fbd1656f474d658016ab0142e952887d2a811257c6c608af0.
Тема русского письма: «DefaultVPN iOS 2.0.1.1: имя профиля и сохранение параметров при импорте».
Оператор сообщил об отправке после этого текста. Его фактическая исходящая
копия не предоставлена; соответствие ниже предполагает сохранение этого порядка.

| Пункт | Вопрос русского письма | Что следует из ответа |
| --- | --- | --- |
| I | Как задать имя профиля при импорте .conf? Поддерживается ли имя файла или специальное поле? | По ответу поддержки такой возможности нет. Это согласуется с наблюдавшимся Server 1; не означает, что имя нельзя задать через любой другой формат или переименовать вручную |
| II | Сохраняет ли импорт родного vpn:// в этой версии указанные MTU и параметры AmneziaWG? | Поддержка ответила отрицательно на составной вопрос. Нельзя считать полное сохранение подтверждённым или включать native delivery. Не установлено, какие именно поля меняются, теряется ли MTU, и какие значения фактически используются; это не измеренный MTU_FAIL |
| III | Как посмотреть параметры или экспортировать только один профиль, без резервной копии остальных? | Поддержка пишет об отдельном создании файла/ключа, но не даёт пути по интерфейсу и не поясняет, экспортирует ли это уже импортированный профиль. Возможность сверить сохранённые/effective параметры остаётся неподтверждённой |
| IV | Какой публичный коммит или тег исходников соответствует сборке cb7ea0c? В репозиториях DefaultVPN и amnezia-client этот коммит найти не удалось | Предложено сравнить GitHub и AppStore; конкретный commit/tag/URL не назван. Привязка установленной сборки к source остаётся UNKNOWN; новый lookup не выполнялся |

### Решение для проекта

- `.conf`: NAME_FAIL по ручному тесту сохранён; SUPPORTED_NAME_FIELD_UNAVAILABLE
  по ответу поддержки. Не добавлять выдуманные поля/comment metadata ради имени.
- Native `vpn://`: исторический NAME_PASS сохранён только как проверка имени на
  незаписанной версии; SUPPORT_REPLIED_NO на полное сохранение MTU/AWG параметров.
  Сохранённые/effective значения по-прежнему UNKNOWN, точный дефект не локализован.
- Не переключать DefaultVPN delivery и не считать эту версию совместимой только
  потому, что отображается Neobyatnaya.NET. Готовый генератор Amnezia envelope
  не является доказательством сохранения параметров установленным iOS-клиентом.
- Не переносить этот ответ на AmneziaVPN/AmneziaWG или другие версии DefaultVPN.
  Рабочий профиль «Испания», серверы, package016 и общая issuance не меняются.
- Ответ получен; прежний WAITING_REPLY завершён. Следующий возможный шаг — узкое
  уточнение ниже. Оно ещё НЕ ОТПРАВЛЕНО, нового ожидания ответа на него нет.
  Работа по боту остаётся отдельной; выбор его архитектуры этим письмом не задан.

### Короткое уточнение, подготовлено, не отправлено

Здравствуйте! Спасибо за ответ. Уточните, пожалуйста, для DefaultVPN iOS
2.0.1.1 (Aug 22 2026, cb7ea0c):

1. В ответе II «Нет» относится к MTU, параметрам AmneziaWG или обоим? Если
   импортировать vpn:// с MTU 1280, какие поля не сохраняются и какие значения
   используются вместо них?
2. В ответе III вы имеете в виду экспорт уже импортированного профиля? Укажите,
   пожалуйста, точные шаги в iOS для создания файла/ключа только этого профиля.
   Содержит ли результат параметры, фактически сохранённые приложением?
3. Пришлите, пожалуйста, прямую ссылку на публичный коммит или тег сборки cb7ea0c.
   Ранее этот SHA не нашёлся в amnezia-vpn/DefaultVPN и amnezia-vpn/amnezia-client.

Рабочие конфиги и резервную копию остальных профилей не прикладываем.

## Основания и границы

- [Скриншоты, hashes и результаты](phase16-client-import-acceptance-checklist-2026-09-09.md#результат-conf--скриншот-получен-2026-09-20).
- [Официальный репозиторий](https://github.com/amnezia-vpn/DefaultVPN).
- [Lookup DefaultVPN cb7ea0c](https://api.github.com/repos/amnezia-vpn/DefaultVPN/commits/cb7ea0c): 422 No commit found, 20.09.
- [Lookup amnezia-client cb7ea0c](https://api.github.com/repos/amnezia-vpn/amnezia-client/commits/cb7ea0c): тот же ответ.
- Это отсутствие результата по двум запросам, не доказательство отсутствия source
  вообще или непубликации любых иных refs. Полный поиск refs/releases не выполнен.
- iOS version UNKNOWN; имя build отображено в UI, подпись/двоичный файл не проверены.
- Без keys, PSK, raw config, backup, изображений, данных «Испании» и рабочих endpoint.
- [Метаданные репозитория](https://api.github.com/repos/amnezia-vpn/DefaultVPN):
  has_issues=false на 20.09.2026. Список /issues?state=all&per_page=100 вернул
  44 записи, все являются pull requests; это не 44 пользовательских issues.
- [PR #23](https://github.com/amnezia-vpn/DefaultVPN/pull/23), «Add dynamic server
  name from config», merged 30.07.2025, меняет только заголовок страницы
  PageSettingsApiServerInfo.qml. Он не исправляет parser/import .conf и не
  доказывает сохранение имени файла или параметров в установленной версии.
- Проверка обсуждений ограничена этим официальным репозиторием; отсутствие дубля
  в других каналах не утверждается. Маршрут обращения — поддержка из приложения;
  не писать в нерелевантные PR или Windows #3043. Статус отправки уточнён выше.
