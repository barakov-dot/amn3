# Phase16: AWG Go — source pin, два исправления и происхождение образа

Дата: 2026-09-20; фиксация read-only результатов в 16:30 Europe/Moscow.
Baseline AMN3: `3eb18f64374e1c279295d0b434302dcee90377ae`.
Scope: два commits от 28.08 и их связь с закреплённым runtime.
Это не полный weekly review, не диагностика VPS/Windows и не разрешение обновления.

## Решение

**DECLARED_SOURCE_BEHIND; IMAGE_SOURCE_BINDING_UNVERIFIED.**
Оба исправления отсутствуют в заявленной source-ревизии. Однако её соответствие
бинарнику Docker-образа не подтверждено. Не переносить этот вывод на фактический
процесс сервера или версию engine внутри Windows/iPhone приложения.

Практическая очередь: кандидат P2 на проверку происхождения и совместимости
фиксированного runtime, затем на отдельное обновление при подтверждённой необходимости.
Наш Python exporter менять по этому сигналу не требуется. Blind image/tag upgrade,
перепаковка package016 и новый live test не выполняются.

## Локальные привязки

[Resource plan](../../packaging/phase16-awg3-family-3-1-spain-pilot-contract/resource-plan.json),
[package builder](../../scripts/phase16_awg31_package.py) и frozen resource plan
package016 указывают:

- source: `1f50ad736ecca22a9bfc7b4606805ec9ca49fe48`;
- image: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`;
- capabilities: disable_cookies, random_trailers.

[Минимальный pilot](../../scripts/vps/phase16_awg31_minimal_pilot.py) закрепляет тот же
digest. Его текущий render_pair задаёт ContentPaddingAddition=0, RandomTrailers=on,
DisableCookies=on. Это чтение шаблона, не readback действующего secret-bearing профиля.

Связь с [receipt016](phase16-package-readiness-receipt-016.md) проверена по Git blobs:
manifest SHA256 `e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc`;
frozen resource-plan SHA256 `dea2c165c4fe0e2959f34e78b722980ba810ea7c9546a2ad1aaaaf5917af82f3`.
Оба совпали. Первичная byte-проверка файлов checkout не совпала: Windows добавил
CRLF. Сверка установила только отличие CRLF/LF; immutable файлы не исправлялись.
Это проверка двух Git blobs, а не повтор полного package verifier.

## Официальная дельта

[Compare двух commits](https://github.com/amnezia-vpn/amneziawg-go/compare/1b86b2ae0e493e7ea93f8c1a0f0cb6735b1551f1...b5928efb6ca19f0153958460c3d141f04abc5c2e)
подтвердил ahead=2. [Compare от нашего declared source](https://github.com/amnezia-vpn/amneziawg-go/compare/1f50ad736ecca22a9bfc7b4606805ec9ca49fe48...b5928efb6ca19f0153958460c3d141f04abc5c2e)
дал ahead=5, behind=0; merge-base равен declared source.

| Commit | Смысл по source diff | Применимость к прочитанному pilot template |
| --- | --- | --- |
| [da11c9f](https://github.com/amnezia-vpn/amneziawg-go/commit/da11c9fadc49333d654c4d7ac18fc8d63f4e8000), 28.08 | Дополнительный content padding ограничивается окном UDP peer с учётом служебных байтов вместо опоры только на MTU | При ContentPaddingAddition=0 этот путь возвращает fallback; дефект padding не установлен для нашего шаблона. Для будущего ненулевого значения нужен отдельный тест |
| [b5928ef](https://github.com/amnezia-vpn/amneziawg-go/commit/b5928efb6ca19f0153958460c3d141f04abc5c2e), 28.08 | При DisableCookies отключается ветка under-load, включающая MAC2/cookie и rate-limit проверки | Условно релевантно: старый source при under-load мог отклонять handshake без MAC2, одновременно запрещая ответ cookie. Наличие under-load на нашем сервере не проверено |
| [1b86b2a](https://github.com/amnezia-vpn/amneziawg-go/commit/1b86b2ae0e493e7ea93f8c1a0f0cb6735b1551f1), 13.08 | Исправлен размер буфера cookie response со случайным trailer | Дополнительный найденный predecessor: отсутствует в declared source. При DisableCookies=on старый sender возвращается до выделения буфера; это не доказанная причина текущего отказа |

Два других commits в диапазоне от declared source: `75ea550a642a9ebef674411c228bb272213a1c23`
меняет Dockerfile awg-tools pin с v3.0.20260730 на v3.1.20260812;
`08271d00b330999cde4ec41edd067e7e1b1d9e89` добавляет socket-FD getters в Windows.
Поэтому переход всего диапазона включает больше, чем два исправления.
Серверный Linux-образ не обновляет Windows-приложение; этот Windows commit отдельно
не исследован как причина нашего traffic FAIL.

Source conditions проверены по pinned
[send.go](https://github.com/amnezia-vpn/amneziawg-go/blob/1f50ad736ecca22a9bfc7b4606805ec9ca49fe48/device/send.go)
и [receive.go](https://github.com/amnezia-vpn/amneziawg-go/blob/1f50ad736ecca22a9bfc7b4606805ec9ca49fe48/device/receive.go).
Это source analysis, не воспроизведение дефекта под нагрузкой.

## Что удалось подтвердить для публичного образа

Прочитаны manifest/config и один слой с /usr/bin/amneziawg-go из официального
[репозитория образа](https://hub.docker.com/r/amneziavpn/amneziawg-go).
Registry: registry-1.docker.io/v2/amneziavpn/amneziawg-go.
Запросы только к публичным upstream; Docker/бинарник не запускались.

| Артефакт | Проверенное значение |
| --- | --- |
| Manifest | sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d; linux/amd64 |
| Config | sha256:777f70bf17917842a532ffba9643e92284ffc003e054a567e64fca74f97b8aff |
| Image created | 2026-08-13T19:39:18.858659407Z |
| Единственный слой COPY бинарника | sha256:d8f3bd9a20a8ecc987aa6071d0901d22bbc6885f77b8eabef2c7d742dd4d9b08; 3 313 703 bytes |
| Бинарник | sha256:6d96502ebd9ed6f9d17bdecd637cba7502c9960fed1b6922b3882784417a036d; 6 132 608 bytes |

SHA256 manifest/config/layer сверены с адресующими digest до разбора.
Labels org.opencontainers.image.revision/source/version отсутствуют. Поиск стандартных
встроенных строк Go build vcs.revision/vcs.modified/vcs.time совпадений не дал.
Это не полная экспертиза executable и не доказательство отсутствия всех иных
способов установить происхождение. Нельзя объявлять бинарник сборкой exact 1f50ad7.

Дата сборки после исправления 1b86b2a и до двух исправлений 28.08 поддерживает
предположение о более поздней, чем declared source, августовской сборке.
Дата и отсутствие labels не доказывают ни включение третьего fix, ни полный
состав бинарника. Live digest/процесс отдельно не читались.

Чтение было ограничено JSON до 2 MB, сжатым слоем до 16 MB и бинарником до 32 MB.
Слой прочитан в память, tar member проверен как regular file по точному пути;
на диск образ/бинарник не извлекались, код не исполнялся, новых зависимостей нет.
В Git сохраняется только этот отчёт, без upstream source, бинарника и auth token.

## Следующий шаг и критерии

1. Установить проверяемую связь image digest → source revision → awg-tools revision:
   официальная provenance/attestation либо отдельно согласованная воспроизводимая
   сборка из exact commits с зафиксированными инструментами и binary hash.
2. Если нужен новый runtime — отдельный candidate с fixed digest; изолированные
   проверки DisableCookies on/off с under-load, ContentPaddingAddition 0/nonzero
   с учётом UDP overhead и cookie/RandomTrailers. Проверить совместимость tools.
3. Только затем рассматривать отдельный pilot change и разрешённый client/quality gate.
   Не использовать это исследование как разрешение live mutation или доказательство
   Windows root cause. Package016, AWG2, general issuance и отложенный A/B сохранены.

Новый полный release/PR audit не выполнялся, weekly cursor не продвигался.
Runtime tests/сборка/SSH/stage/install не запускались. Source/registry readback и
checksums завершены; code fix текущего exporter не требуется.
