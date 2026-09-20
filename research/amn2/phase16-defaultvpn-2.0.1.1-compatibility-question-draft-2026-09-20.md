# DefaultVPN 2.0.1.1 — черновик уточнения разработчикам

Статус: SENT_OPERATOR_REPORTED / WAITING_REPLY, 2026-09-20. Оператор сообщил
«отправил» после получения русского текста письма и адреса support@dfvpn.com.
Доставка адресату и ответ независимо не проверены. По просьбе оператора
DefaultVPN отложен как несрочный; новые тесты и повторная отправка не нужны.
Ниже сохранён исходный английский черновик; точная отправленная копия не сверялась.
Адресат: support@dfvpn.com — контакт из раздела «О приложении» на скриншоте
оператора. Альтернативный контакт там же: @DefaultVPNSupport.
В официальном GitHub-репозитории DefaultVPN приём issues отключён.
Это запрос о проверяемости совместимости, не утверждение об ошибке MTU.
Письмо отправлял оператор; агент не выполнял отправку и не создавал issue.

## Тема письма

iOS 2.0.1.1 (cb7ea0c): source revision and per-profile native import verification

## Текст письма

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
