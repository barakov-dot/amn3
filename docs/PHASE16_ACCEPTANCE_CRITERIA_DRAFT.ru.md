# Phase 16 — согласованные критерии приёмки v1

Дата: 2026-09-07. Статус: `CRITERIA_APPROVED_NOT_EXECUTED`.
Основание: операторское «продолжай» после локального DNS-исправления,
baseline `7f867be92a75f401d9b061e41bf6605b8f9e5d14`.
Область — согласованные критерии; live, установка, изменение конфигов и push
не разрешаются. iPhone/две сети остаются отложенными по решению оператора.

Согласование: 2026-09-07 оператор ответил «согласовываю» на предложение
согласовать этот документ. Согласована редакция v1 из commit
`b165c5b6b4914bb2befd1c25b78dd6cba48e8ab6`; числа и правила решений не изменены.
Это согласование требований, не PASS, не снятие blockers и не live approval.
Путь с суффиксом DRAFT сохранён для совместимости ссылок; актуален статус выше.

Числа ниже — согласованные инженерные требования к операторскому пилоту для
обычного веба, видео и мессенджеров. Это не норматив, не гарантия скорости сервера
и не обещание качества 4K/игр. Согласование получено ДО acceptance-прогона.
Ранее записанный quality FAIL по этому проекту не пересчитывается.

Актуальная очередь: [план Phase 16](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
Обязательное сравнение: [Task 4.5](../research/amn2/phase16-spain-transport-quality-ab-gate-2026-08-26.md).

## Согласованные критерии

| Проверка | Согласованный критерий | Доказательство и граница |
| --- | --- | --- |
| HTTPS | 3/3 успешных ответа с проверкой TLS, каждый до 5 s | Начало, середина и конец одного окна; свежий запрос к согласованному origin, не только кэш. Connected не заменяет ответ |
| DNS | 5/5 успешных разрешений имени, каждое до 2 s | Один метод; фиксировать только count/time/result. Кэшированный успех не доказывает использование нужного upstream DNS |
| Throughput | Download не ниже 20 Mbps, upload не ниже 5 Mbps | Завершённый замер обоих направлений одним методом; полезные bytes/time. Пик и незавершённый экран не принимаются |
| AWG2 comparison | Не ниже 70% AWG2 в каждом направлении, если AWG2 сам проходит абсолютные критерии | Сопоставимые endpoint/device/app/network. Плохой AWG2 не снижает требования к AWG3.1 |
| Idle RTT | Медиана до 180 ms, p95 до 250 ms | Не менее 100 успешных samples одного метода/endpoint вне нагрузки; число неответивших проб сохраняется отдельно |
| Idle jitter | До 30 ms | Среднее абсолютных разностей соседних успешных RTT; пропуски отдельно в loss; не смешивать с loaded jitter |
| Loaded latency | p95 RTT под download и под upload до 400 ms | Не менее 30 успешных проб на каждое направление. Мало samples — INCOMPLETE, без автоматического продления |
| Потери | Не более 1% из минимум 100 отправленных проб | Заранее выбранный успешно установленный probe path; sent/received/timeouts. ICMP, TURN и HTTPS failure не смешиваются |
| Краткая стабильность | 15 минут, 0 самопроизвольных разрывов и подтверждённых перебоев доступа дольше 5 s | Обычная работа и проверки выше внутри одного окна. Это bounded acceptance, не доказательство суточной надёжности |
| Reconnect | Один плановый reconnect, восстановление HTTPS до 5 s | От команды повторного подключения до успешного ответа; отдельно от самопроизвольных разрывов |
| MTU/fragmentation | MTU соответствует профилю; нет воспроизводимого size-dependent stall | До запуска выбрать конечный набор packet sizes и DF/эквивалентный метод. Большой HTTPS download сам по себе не доказывает PMTU |
| Server health | Нет новых относящихся к тесту interface/UDP errors и drops | Один bounded read-only сбор под трафиком: interface, Docker/netns, listener, firewall counters, CPU/softirq. Абсолютные counters не равны потерям этого прогона |

CPU после теста не заменяет наблюдения под нагрузкой. Устойчивое насыщение
vCPU/softirq при плохом трафике — основание расследовать серверный путь,
не готовый диагноз. Изменения counters host interface требуют атрибуции:
посторонний трафик нельзя объявлять ошибкой AWG3.1.

## Сопоставимость и достаточность

- Один peer используется только последовательно. Для A/B — существующие Spain
  AWG2 d7 и AWG3.1, одно устройство/приложение/физическая сеть, другие VPN выключены.
  Старый USA-профиль не является Spain AWG2 контролем.
- No-VPN baseline характеризует ёмкость сети. Согласованный минимум пригодности
  сети — 25/6.25 Mbps (запас 25% к цели 20/5). Более слабая сеть пригодна для
  диагностики, но не для принятия производительности по этому профилю требований;
  её ограничение не доказывает серверную причину.
- Смена test origin/edge, физической сети или метода делает относительную часть
  несопоставимой. No-VPN latency не является прямым эталоном маршрута через Spain.
- ICE timeout означает отсутствие loss measurement. Рабочий TURN-процент
  характеризует TURN-путь, не прямое измерение потерь AWG. Нужна валидная
  сопоставимая методика; повторять тест до появления числа не следует.
- Прошлые import/handshake/connectivity — prerequisites, не отдельные повторные
  кампании. Итоговый доступ и reconnect проверяются внутри одного разрешённого
  acceptance-окна после исправления причины.

## Минимальные этапы и остановка

1. После возврата оператора к A/B — один bounded диагностический сеанс с
   существующими профилями. Он выбирает направление расследования и не заменяет
   acceptance после root-cause-bound correction.
2. После исправления причины — одно 15-минутное AWG3.1 acceptance-окно.
   DNS/HTTPS, нагрузку, RTT, server metrics и один reconnect совмещать внутри него.
   Время и трафик всех действий входят в общий approved budget.
3. Windows остаётся отдельным обязательным gate. Новый тест требует изменения
   официального клиента/engine или новой различающей гипотезы; iPhone PASS не
   закрывает Windows. Повторные generic IPv4/kill-switch тесты не планируются.
4. Persistence после server/application restart, IPv4/IPv6/DNS leaks, итоговая
   AWG2 equality и scoped rollback — отдельный разрешённый integration/Task 5 этап.
   Временный firewall и restart=no не получают production PASS.

STOP: concurrent peer use, смена профиля/endpoint вне плана, невосстановившаяся
потеря доступа, неконтролируемый трафик, достижение approved time/data cap или
нарушение области. Воспроизведённый устойчивый отказ не требует досиживать окно
ради второго FAIL. Не отключать kill switch и не менять MTU/DNS/порт ради замера.
Автоматического retry нет. Для повтора указать устранённую причину невалидности
или новую гипотезу и получить соответствующее разрешение.

## Решения

- PASS: все обязательные измерения валидны и удовлетворяют согласованной версии
  критериев; root-cause correction подтверждён. Полный closeout также требует
  Windows, strict A/B и успешной отдельной интеграции.
- FAIL: валидное измерение нарушает критерий или воспроизводится отказ доступа.
  Исправление следует из evidence; повтор тех же настроек не является fix.
- INCOMPLETE: нет метода/результата, лимит достигнут до достаточной выборки,
  baseline недостаточен или нарушена сопоставимость. Не повышать до PASS.
  Независимый валидный FAIL сохраняется даже при других INCOMPLETE измерениях.
- AWG2 FAIL / AWG3.1 PASS: отдельный AWG2 remediation без изменения AWG2 в этом
  scope; AWG3.1 может перейти к следующим gates. Оба FAIL: исследовать общий путь,
  сохраняя возможность двух разных причин. Оба PASS: прошлый симптом не
  воспроизведён, это не доказательство его устранения.

## Что ещё нужно до исполнимого разрешения

Критерии согласованы, но это не готовый live-runner и не /APPROVE. До запуска нужно:

- выбрать доступный на устройстве метод без установки, дающий sample counts,
  p95, валидный loss и size/MTU evidence. Одних скриншотов недостаточно. Если
  метода нет, обозначить пробел; не создавать инфраструктуру без отдельного решения;
- закрепить точные probe endpoints, число/размер передач, общий upper bound
  трафика, wall-clock timeout и отмену каждого вызова. Неконтролируемый browser
  speedtest не считать исполняющим точный byte cap;
- получить exact live approval с профилем, состоянием устройств и отдельной
  read-only областью SSH, если нужен серверный сбор. Одобрение чисел не разрешает
  SSH, установку, рестарт, изменение конфигов или общую выдачу.

Проверка этого документа: diff, ссылки и сохранение gates. Тесты, сборки,
package verifiers и live-прогоны не нужны. Исторические receipts неизменны.

## Методика m1 — локальная подготовка, не разрешение запуска

Подготовлено 2026-09-07 по операторскому «приступай» после согласования v1.
Статус методики: `METHOD_DRAFT_BLOCKED_NOT_EXECUTED`. Согласованные критерии
выше неизменны; предложенные ниже методы и бюджеты НЕ согласованы автоматически.
Это приложение к критериям, не второй execution plan и не готовый runner.

### Проверенные возможности и границы

- Локально через Get-Command обнаружены curl.exe, ping.exe, Resolve-DnsName,
  Get-NetAdapter, Get-NetIPInterface, Get-NetAdapterStatistics и Get-NetRoute.
  Проверялось только наличие команд, без их сетевого запуска. Версия, точность
  таймеров, отмена и byte-limit enforcement этим не проверены.
- Эти средства относятся к Windows-хосту. Их результаты нельзя выдавать за
  измерения iPhone; Windows пока имеет незакрытый application-traffic blocker.
  Устройство acceptance этим документом не выбрано и не подменено.
- Для iPhone не подтверждён уже установленный способ получить исходные RTT
  samples, ограниченный upload, DNS/DF evidence и принудительную отмену.
  Импорт d7 и вторая сеть остаются отложенными; новых вопросов о них сейчас нет.
- Прежние speedtest-скриншоты сохраняются как evidence своих прогонов, но
  не заменяют sample export и ограничитель трафика. ICE timeout не равен loss.
- Существующий phase16_spain_readonly_preflight_ssh_runner.ps1 имеет собственный
  package/claim workflow. Это не готовый collector для окна качества; повторный
  preflight, materialization или расходование claim ради metrics не нужны.

### Контракт одного будущего окна

Ни один пункт ниже не запускается до root-cause-bound correction и отдельного
exact approval. T0 — согласованный оператором старт после проверки prerequisites;
все вызовы и их отмена входят в 900 s, фоновые задачи после deadline запрещены.
Нормальное завершение — 900 s; устойчивый отказ или общий аварийный cap — STOP.
Завершение разрешённого числа объектов/проб заканчивает только соответствующую
фазу, не всё окно. Попытка превысить body cap или общий deadline прекращает окно;
допустимый транспортный cap ещё предстоит выбрать и обеспечить до live approval.
Неполная длительность не получает stability PASS. Baseline и диагностический
A/B не прячутся в этом окне: им нужны отдельные лимиты и разрешения.

| Измерение | Предложенный конечный метод и лимит | Что препятствует готовности |
| --- | --- | --- |
| HTTPS | 3 fresh GET в T0, T0+450 s, T0+890 s; каждый <=5 s, body <=64 KiB, TLS verification, redirects/retries off | Утвердить точный HTTPS origin/path и проверяемый ожидаемый ответ; получать страницы из кэша недостаточно |
| DNS | 5 однократных A-query в первые 120 s, каждый <=2 s; один метод и resolver path из профиля, без смены системного DNS | Выбрать 5 имён и способ отличить resolver query от локального кэша; без raw DNS output. Ограничение caller timeout без отмены запроса недостаточно |
| Idle RTT/loss/jitter | Одна серия 120 IPv4 ICMP echo к одному literal IP; payload 32 B, timeout 1 s, пауза 200 ms после результата; <=150 s | ICMP endpoint/path заранее должен допускать пробы. Нет валидного ответа на setup — INCOMPLETE, а не 100% AWG loss; не переключаться на другой endpoint в том же окне |
| Download | Последовательно не более 8 объектов по 8 MiB, без искусственного rate limit; общий phase timeout 60 s | Нужен endpoint, возвращающий точный размер, и проверенная отмена при превышении. Cloudflare UI сам по себе этого не гарантирует |
| Upload | Последовательно не более 8 тел по 2 MiB, phase timeout 60 s; ответ каждого <=64 KiB; никаких пользовательских файлов | Нужен разрешённый точный sink и способ ограниченного тела в памяти без установки/создания файлов. Наличие curl.exe не доказывает готовность этой цепочки |
| Loaded RTT | Только во время фактической передачи каждого направления: тот же ICMP path, payload 32 B, timeout 1 s; <=600 проб на направление, не чаще 1/100 ms, не более одной одновременно | Нужно >=30 успешных samples на направление. При раннем byte cap или быстрой передаче — INCOMPLETE; не увеличивать трафик и не добавлять retry автоматически |
| MTU/size | Read-only MTU; 4 IPv4 ICMP payload sizes: 32, 548, 1172, 1252 B; по 3 DF-пробы, timeout 1 s, всего 12 и <=20 s | Для inner MTU 1280 это IPv4+ICMP размеры 60, 576, 1200, 1280 B. Тот же подтверждённый ICMP path; rate limiting/filtering не объявлять fragmentation. Это не IPv6 PMTU и не outer-path MTU |
| Stability | Наблюдать один tunnel lifecycle и весь доступ в течение 900 s; использовать уже перечисленные пробы | Три GET не доказывают отсутствие всех перебоев >5 s. Нужен доступный журнал/наблюдатель достаточного разрешения; пока coverage gap, а не PASS |
| Reconnect | Одна операторская пара disconnect/connect после нагрузок, например T0+720 s; monotonic timer от connect; <=5 fresh GET, общий deadline 5 s, без одновременных запросов, body <=64 KiB каждый | Согласовать доступный способ timestamp; плановый разрыв классифицировать отдельно. Это не автоматический retry других failed измерений |
| Server metrics | Один SSH-сеанс; setup <=10 s внутри общего окна; легкие aggregate samples раз в 5 s, максимум 180; state snapshots start/end; stdout <=1 MiB | Exact checksum-bound read-only collector пока не подготовлен. Полный nft/Docker/netns dump каждые 5 s не нужен; peer/keys/endpoints/DNS не выводить |

Порядок: idle и DNS в начале; download и upload последовательно после idle,
до reconnect; HTTPS по указанным точкам; server observer и stability coverage
параллельно внутри того же окна. Отсутствие действительной нагрузки не даёт
loaded-latency samples. Нехватка времени/выборки не разрешает продлить окно.
Системные таймеры должны быть monotonic; timestamps согласовать с сервером,
не меняя часы. Server collection не использует сигнал/restart/config write.

### Бюджет и расчёт результатов

- Предложенный body budget: download <=64 MiB; upload <=16 MiB; суммарно
  <=80 MiB. Все HTTPS response bodies вне download вместе <=1 MiB
  (3 основных + до 5 reconnect + до 8 upload acknowledgements, по 64 KiB).
  Общий HTTP application-body cap — 81 MiB, одна попытка на объект.
- ICMP budget <=1332 echo requests: 120 idle + 1200 loaded + 12 size;
  DNS <=5 логических query. Внутренние DNS retransmits должны быть учтены
  выбранным методом; пять API-вызовов не являются гарантией пяти UDP-пакетов.
- Эти числа НЕ являются wire-byte cap: TLS/HTTP headers, TCP retransmissions,
  AWG overhead/junk/keepalive, DNS и SSH имеют дополнительный трафик.
  Точный transport-byte bound и механизм принудительной остановки пока не
  доказаны. Не выдавать 81 MiB за точный объём Spain egress и не писать approval
  с таким обещанием. Browser/YouTube/Telegram фон в bounded load не включать.
- Размеры — MiB = 1048576 B; throughput — decimal Mbps = payload_bytes * 8 /
  elapsed_seconds / 1000000. Учитывать полное время серии одного направления,
  включая установление соединения и межзапросные задержки; не выбирать peak.
  Валидный throughput требует завершённых передач и подтверждённых размеров;
  timeout/неполная передача не превращаются в успешный замер скорости.
- RTT хранить как sequence/result/duration без адресов. p95 — nearest rank
  ceil(0.95*N) отсортированных успешных samples; median — обычная медиана;
  loss — timeout_count/sent_count при валидном probe path. Send error/cancel
  учитывать отдельно, не выдавать за remote packet loss. Jitter — среднее
  абсолютных разностей соседних успешных RTT; пропуски явно помечать.
- Для относительного AWG2 сравнения нужны один endpoint/edge, устройство,
  приложение, сеть и метод. Если edge/маршрут нельзя сопоставить — относительный
  результат INCOMPLETE. ICMP loss характеризует этот ICMP path, не прямую долю
  потерь внешнего AWG UDP; post-run interface delta не заменяет flow attribution.
- При отсутствии достаточного stability observer, <100 успешных idle samples,
  <30 loaded samples на направление или отсутствующем MTU/DNS evidence —
  соответствующий gate INCOMPLETE. Независимый валидный FAIL сохраняется.

### Admission: что ещё действительно требуется

1. После снятия соответствующей отсрочки выбрать конкретное устройство и уже
   доступный метод, закрывающий перечисленные coverage gaps. Нельзя автоматически
   заменить iPhone Windows-хостом, установить приложение или написать runner.
2. Согласовать endpoint manifest: HTTPS origin/path/expected response,
   download URL/размер, upload URL/метод/тело/ответ, ICMP IP, DNS question set и
   resolver path, server identity. Сейчас manifest не выбран: это blocker,
   не предложение опросить произвольный публичный сервис. Ни одного endpoint
   или upload sink в этой локальной работе не проверяли.
3. Подтвердить enforceable time/data caps, отмену дочерних вызовов, отсутствие
   внешнего fallback и безопасный normalized output. Если нужен новый helper,
   получить отдельное local code GO с targeted TDD; текущая задача его не создаёт.
4. Привязать runner/collector SHA, неизменный profile SHA, текущий state,
   восстановление клиентского baseline и exact live approval. До этого — STOP.
   Не просить live approval для методики, которая ещё не может исполнить cap.

Самопроверка m1: все строки критериев имеют метод либо явно указанный coverage
gap; runtime возможностей не заявлено. iPhone/A/B не возобновлены, Windows и
root-cause gates не сняты; leaks/persistence/rollback остаются отдельной интеграцией.

### Реализованная локальная часть m1 — 2026-09-07

Approval: `/GO PHASE16 MINIMAL_WINDOWS_MEASUREMENT_HELPER LOCAL_CODE_ONLY OFFLINE_TDD ONE_TARGETED_SUITE NO_NETWORK NO_REAL_CONFIG_READ NO_INSTALL NO_LIVE_ACTION NO_PUSH AWG2_UNTOUCHED`.
Source baseline: `fb659933868ce9b82eeb53d306cab988743123da`.

Добавлен [Windows helper](../scripts/vps/phase16_windows_measurement_helper.ps1)
и [его offline tests](../tests/test_phase16_windows_measurement_helper.py).
Загрузка .ps1 только определяет функции; endpoints, чтения профиля и live entrypoint нет.
Рабочая среда проверки: PowerShell 7.6.5 / Windows 10.0.26200. Это не PS5.1-поддержка.

- Get-Phase16RttSummary: строгий нормализованный sequence/status/rtt_ms,
  median, nearest-rank p95, chronological jitter, раздельные timeout/send_error/
  canceled. Невалидный probe path и неполные данные не становятся нулевым loss/PASS.
- Get-Phase16ThroughputSummary: decimal Mbps по подтверждённым payload bytes
  и времени всей серии. Partial body или незавершённая передача дают INCOMPLETE.
  MEASURED означает наличие расчёта, а не прохождение acceptance thresholds.
- Invoke-Phase16BoundedProcess: явные executable/arguments без shell expansion,
  ограниченный input в памяти, stdout/stderr drainage без сохранения содержания,
  time budget с резервом cleanup и kill direct process/tree при необходимости.
  Файл не выбирает и не запускает curl/ping/SSH автоматически; вызывающий слой
  по-прежнему обязан получить соответствующий exact approval.

Граница: stdout cap ограничивает чтение pipe (до cap+1 sentinel), не сетевой
трафик. stdin_bytes=null при прерванной записи означает неизвестную длину префикса.
process_exited относится к непосредственному child; detached descendants этим
не подтверждаются. Cleanup failure и deadline overrun сохраняются явно, не PASS.
Ограничение времени и завершение проверены на offline fixtures; универсальная
hard-wall гарантия при зависании ОС/драйвера не доказана. Full HTTP/TLS adapter, DNS/ICMP collector, server observer,
stability observer, endpoint manifest и запуск 900-секундного окна НЕ реализованы.

TDD evidence: RED отсутствующих функций; затем focused GREEN. Исправлены
обнаруженные тестами лишний async output, ложный zero при partial stdin и
допуск RTT за пределами окна. Один итоговый targeted suite: 15 tests PASS,
8.685 s, без сети. Команда: Python `-B -m unittest -v
tests.test_phase16_windows_measurement_helper`. Дочерние fixtures только
передавали синтетические байты, завершались или спали; реальные профили не читались.
Статус helper — `LOCAL_OFFLINE_VERIFIED`; методика остаётся
`METHOD_DRAFT_BLOCKED_NOT_EXECUTED`. Полного measurement runner ещё нет.

### Минимальный HTTP-адаптер — 2026-09-07

Approval: `/GO PHASE16 MINIMAL_WINDOWS_HTTP_MEASUREMENT_ADAPTER BOUNDED_METADATA OFFLINE_TDD ONE_TARGETED_SUITE NO_NETWORK NO_REAL_CONFIG_READ NO_INSTALL NO_LIVE_ACTION NO_PUSH AWG2_UNTOUCHED`.
Source baseline: `d87c07e3828192a48c22fa927026101124ddb9af`.
Это последующее расширение тех же helper/tests, не изменение предыдущего receipt.

- New-Phase16HttpRequest строит один явный HTTPS GET/POST без исполнения.
  Нет default endpoint: URL задаётся вызывающим слоем; HTTP, userinfo, fragment,
  control characters и URL globbing исключены. Внутренний request содержит URL/
  body и НЕ является объектом для экспорта или записи в журнал.
- Invoke-Phase16HttpMeasurement использует явный доверенный путь curl, stdin
  byte array и существующий bounded process. Curl >=8.16 необходим для out-null;
  конкретный binary/version/checksum предстоит связать с будущим live approval.
  Нет чтения профиля, пользовательского файла, автопоиска binary или установки.
- Один download: 1 B–8 MiB; один upload: 1 B–2 MiB, длина массива должна точно
  совпадать; upload response cap 1 B–64 KiB. Process budget 1–60 s с 500 ms
  cleanup reserve; curl max-time получает оставшееся рабочее время.
  Retries, redirects, proxy, curlrc и automatic decompression не включаются.
  Тело ответа отбрасывается out-null; SSLKEYLOGFILE удаляется только из окружения
  дочернего curl-mode процесса, окружение оператора не меняется.
- Curl-mode stdout <=4 KiB, overflow читается только до cap+1 sentinel.
  В памяти временно разбирается одна точная строка из семи числовых полей;
  raw stdout/stderr, URL и arbitrary fields не возвращаются. Неверная схема,
  дубликаты, nonfinite/locale numbers и overflow не становятся успехом.
- MEASURED требует exit 0, завершённый процесс без deadline overrun, HTTP 200,
  успешную проверку TLS, отсутствие proxy/redirect и точные payload counts.
  Для upload также нужен полностью записанный stdin и ограниченный ответ.
  HTTP 204/206/3xx/5xx, partial transfer и неизвестная длина stdin — INCOMPLETE.
  Числовые HTTP/TLS failure evidence сохраняются, Mbps при отказе отсутствует.
  Скорость одного объекта считается по полному времени процесса, не по peak;
  curl time_total возвращается отдельно. Это НЕ throughput всей серии.

Официальный контракт curl проверен read-only в предыдущем ходе:
[manpage](https://curl.se/docs/manpage.html), включая max-filesize, max-time,
data-binary, out-null и write-out. Сам curl, Cloudflare endpoints и TLS/HTTP
в этой реализации НЕ запускались: offline-тесты не доказывают поведение
конкретного binary, сервера, транспортный byte cap или Windows VPN fix.
HTTP body limit не равен wire-byte limit. Upload 200 + счётчики не доказывают
сохранение тела сервером; download размер не проверяет смысл содержимого.
Endpoint/expected-content admission остаётся отдельным gate.

TDD: RED отсутствующего parser/adapter; focused GREEN 7 tests. Дополнительные
RED/GREEN закрыли наследование TLS keylog и потерю числового failure evidence.
Итоговый целевой набор: `python -B -m unittest -v tests.test_phase16_windows_measurement_helper`
— **24 tests PASS, 16.621 s, exit 0**. Первый итоговый вызов потерял окончание
вывода инструмента и не засчитан как PASS; повторён тот же набор для получения
полного результата. Другие suites, сеть, реальные configs не использовались.

Статус HTTP-адаптера: `LOCAL_OFFLINE_VERIFIED_NOT_LIVE_VALIDATED`.
Загрузка скрипта по-прежнему инертна. Отдельный вызов Invoke-функции способен
создать трафик и требует exact live approval; код сам его не выдаёт.
DNS/ICMP, server/stability collectors, endpoint manifest, общий series budget
и 900 s runner не реализованы. m1, Windows/quality/root-cause gates неизменны;
iPhone/A/B остаются отложенными. AWG2/package016/stage/install/push не затронуты.

### Минимальный ICMP-адаптер — 2026-09-07

Основание: операторское «согласовываю» после предложения отдельно согласовать
минимальный локальный ICMP-адаптер. Сохранены offline TDD, NO_NETWORK,
NO_REAL_CONFIG_READ, NO_INSTALL, NO_LIVE_ACTION, NO_PUSH и AWG2_UNTOUCHED.
Source baseline: `2187146aeebe537f54b5384db78a0e6ac92d2ead`.

В том же helper добавлен Invoke-Phase16IcmpSample: одна явная IPv4-проба через
штатный .NET Ping.SendPingAsync с CancellationToken. Target только canonical
literal IPv4; имена/IPv6/сокращённые адреса отвергаются до создания Ping.
Нет DNS, default target, retry или цикла серии. New-Phase16PingClient отделяет
platform boundary; в тестах он заменён, реальные Ping/ICMP не запускались.
Наличие нужного cancelable overload отдельно подтверждено reflection без вызова.

- Payload 1–1252 B в памяти, default 32 B; TTL 64, явный bool DontFragment.
  Общий budget 200–1000 ms. Default: reply timeout 800 ms, внешний рабочий
  deadline 900 ms, ещё 100 ms на отмену/cleanup. Фактический reply_timeout_ms
  возвращается явно. Это не обещание полноценного ожидания ответа 1000 ms.
  Меньший бюджет использует max(1, budget−200) ms ожидания ответа.
  Будущий endpoint/method approval должен фиксировать этот метод одинаково
  для сравниваемых серий; согласованные acceptance thresholds не изменены.
- sample содержит только sequence/status/rtt_ms и совместим с RTT-summary.
  Native TimedOut → timeout; исключение/ICMP error → send_error; caller/deadline
  cancellation → canceled. PacketTooBig отмечается отдельно, без заключения
  о root cause или полном PMTU. Target, reply address/buffer и исключения не выводятся.
- Внешний deadline отменяет pending Task; completion проверяется в оставшемся
  бюджете. Cleanup failure или overrun не оставляют успешный sample.
  cleanup_unconfirmed требует STOP будущего окна, а не следующей пробы.
  Dispose сам по себе не доказывает завершение pending operation. Универсальная
  hard-wall гарантия при зависании native API/ОС НЕ доказана; таймер/Task doubles
  не подтверждают реальный сетевой cancellation path.
- Одно успешное измерение не включает ProbePathValidated автоматически,
  не доказывает AWG route и не выдаёт quality/loss acceptance.

TDD: RED отсутствующего ICMP adapter; focused GREEN. Отдельный RED показал,
что timeout вплотную к внешнему deadline превращается в canceled; добавлены
явный API-return reserve и поле фактического reply timeout, затем GREEN.
Один итоговый набор `python -B -m unittest -v tests.test_phase16_windows_measurement_helper`:
**32 tests PASS, 24.921 s, exit 0**. Восемь новых ICMP tests проверяют binding,
классификацию, no-retry, pre/in-flight cancellation, unconfirmed cleanup,
неверные данные, redaction и совместимость с прежним summary.
HTTP/RTT/process regression tests прошли в том же наборе; других suites не было.

Статус: `LOCAL_OFFLINE_VERIFIED_NOT_LIVE_VALIDATED`. DNS, series runner,
endpoint admission, transport budget, stability/server observers не реализованы.
Загрузка скрипта инертна; live требует отдельного exact approval. Windows/quality
blockers, отсрочка iPhone/A/B, AWG2, package016, stage/install/push не изменены.

### DNS cancellation/lifecycle contract d1 — 2026-09-07

Уточнение после официального чтения: различие API lifetime и консервативной
политики модели, а также текущий STOP реализации описаны в
[Official DNS source check](#official-dns-source-check-2026-09-07).
Ниже сохранён исторический контракт; его модельные ограничения не следует
выдавать за дословные требования Microsoft.

Основание: операторское «согласовываю» на подготовку локального DNS-контракта
без реализации и сетевых запросов. Baseline: `a47c137d694e8592f7a3ebfdcf247d56552824a5`.
Статус: `CONTRACT_DEFINED_IMPLEMENTATION_GATED_NOT_EXECUTED`.
Это уточнение методики m1, не новый execution plan, не готовый адаптер и не
утверждение о реализуемости hard-wall ограничения на данном native runtime.

**Штатный путь.** Кандидат — асинхронный Windows DnsQueryEx + DnsCancelQuery.
Resolve-DnsName -QuickTimeout не даёт документированного предела 2 s; ожидание
с Task timeout без отмены native query не удовлетворяет контракту.
Собственный DNS wire client, новый публичный resolver, установка библиотеки
и fallback на другой метод сюда не входят. Основание — уже прочитанные
[DnsQueryEx](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsqueryex),
[DnsCancelQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnscancelquery)
и [DNS_QUERY_REQUEST](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-dns_query_request).
В текущем docs-only ходе источники по сети повторно не запрашивались.

**Вход и resolver path.** Одна A-query на один заранее согласованный ASCII
FQDN с завершающей точкой, sequence 1–5, один явный literal IPv4 resolver и
положительный interface index. Пустые/default/all-interface значения запрещены.
Resolver и интерфейс поступают из отдельного approved endpoint/state manifest;
профиль не читается адаптером. Соответствие профилю и существующему tunnel
проверяется отдельным admission, не предположением из переданного числа.
Если binding недоступен/устарел — STOP, без выбора запасного resolver/interface.
Список из двух DNS в профиле не разрешает две попытки для одной query.

Требуется запрос к resolver, а не ответ из локального кэша/hosts/локального
имени; LLMNR/NetBIOS/multicast и добавление search suffix исключены.
Использовать документированные native query options для обхода локальных
источников; точные flags, ABI/layout и их сочетание проверить до interop.
Не очищать системный кэш и не менять системный DNS/NRPT. Кэш upstream resolver
не исключается: это проверка resolver path, не рекурсивной цепочки без кэширования.
Один API-вызов не доказывает ровно один сетевой пакет: native retries/UDP→TCP
могут существовать; wire-byte cap остаётся отдельным незакрытым gate.

**Время и ownership.** Monotonic T0 начинается до выделения request resources.
Один общий budget — 2000 ms, включая setup, обработку ответа и освобождение.
На T0+1800 ms незавершённая операция получает запрос отмены; последние 200 ms
зарезервированы для completion/cleanup. Caller cancel инициирует отмену раньше.
Это предложенный метод, а не изменение критерия DNS 5/5 <=2 s.
Если setup исчерпал рабочий бюджет, DnsQueryEx уже не вызывается.

| Событие | Обязательный переход и владение |
| --- | --- |
| Invalid input / cancel до dispatch | Нет native query; нет создаваемых для неё handles |
| Синхронное завершение DnsQueryEx | Обработать результат по sync-контракту API; единственный владелец освобождает ресурсы |
| DNS_REQUEST_PENDING | Request/result/server-list/context и callback delegate остаются живы до подтверждённого completion |
| Callback и возврат DnsQueryEx пересеклись | Completion может прийти до возврата API; синхронизация не теряет результат и не допускает двойной публикации/освобождения |
| Caller cancel / рабочий deadline | Один запрос DnsCancelQuery, если query ещё pending; сам return отмены НЕ является completion |
| Ответ пришёл после принятой отмены | Освободить после безопасного completion; поздний успешный ответ не повышает canceled до success |
| На 2000 ms pending callback или cleanup | cleanup_unconfirmed, STOP всего будущего окна; не начинать следующую query |

Владение должно быть единственным и проверяемым: DnsRecordListFree ровно один
раз для полученного record list; request/result/context/callback delegate —
не раньше точки, в которой native код больше к ним не обращается. Сигнал
«результат готов» в начале callback не доказывает, что callback уже покинут.
Не выполнять PowerShell scriptblock на произвольном native callback thread;
конкретный interop bridge должен обеспечить thread-safe completion и lifetime.
Это требование реализации, не разрешение сейчас писать bridge или запускать код.

Если callback остаётся pending, немедленный Free/Dispose опасен; сохранение
ресурсов до позднего callback не доказывает остановку сетевой операции к deadline.
Поэтому одного возврата cleanup_unconfirmed недостаточно для live admission.
Нужна отдельно проверенная стратегия containment для такого исхода. Новый worker
process/service, его принудительное завершение или фоновая дочистка не добавляются
автоматически. Пока containment не обоснован, in-process вариант не объявляется
готовым к hard-wall live-запуску; численный предел не ослабляется.

**Выход.** Только schema, sequence, outcome, query_duration_ms, total_elapsed_ms,
answer_a_count, cancel_requested, cleanup_confirmed, deadline_exceeded.
Никаких FQDN, DNS-addresses/answers, interface identity, raw records/errors,
handles/pointers; optional native status допустим лишь как нормализованный код.
query_duration_ms — от dispatch до принятого terminal result; total_elapsed_ms —
до безопасного завершения cleanup. Неполученные величины null, не нули.
Output record <=4 KiB; обход native records ограничен 32 записями; превышение —
answer_limit, без дальнейшего разбора и без успешного результата.

success требует положительного A-result именно запрошенного имени (с учётом
допустимого CNAME разрешения штатным resolver), завершения и освобождения в
общем бюджете. Самого return code 0 или любого record count недостаточно.
NXDOMAIN, no_data, server_error, native_timeout, canceled, start_error,
answer_limit и cleanup_unconfirmed различаются. Отмена/ошибка инструмента —
не доказательство потери DNS-пакета, неисправности AWG или root cause.
DNS 5/5 может оцениваться только после пяти последовательных допустимых
результатов с заранее проверенным binding; d1 не создаёт цикл и не выдаёт PASS.

**Следующий implementation gate.** Отдельный local GO и один targeted offline
TDD набор: sync/pending, callback-before-return, cancel/completion race, поздний
callback, отсутствие completion, ровно одно освобождение, ошибки/пустой ответ,
лимиты и redaction. Fakes не должны вызывать DnsQueryEx/DnsCancelQuery, читать
профили или генерировать пакеты. Offline PASS не закрывает native containment/
resolver-binding evidence; live и дополнительные процессы требуют своих approvals.
В этом ходе проверены только readback, diff/whitespace, ссылки и согласованность;
код, tests, runtime и прежние receipts не изменены. AWG2_UNTOUCHED; NO_PUSH.

### Offline DNS lifecycle model d1 — 2026-09-07

Основание: операторское «приступай» после предложения offline TDD lifecycle,
без native DNS-вызовов и новых worker/process. Source baseline:
`0dcc82316b1f7aa7cabb4f6fd82e8fa7042406e6`. Статус:
`LIFECYCLE_MODEL_OFFLINE_VERIFIED_NATIVE_ADAPTER_NOT_IMPLEMENTED`.

Добавлена отдельная чистая [Python-модель](../scripts/vps/phase16_dns_lifecycle.py)
и [целевые тесты](../tests/test_phase16_dns_lifecycle.py). Она не подключена к
PowerShell helper: вход — до 64 нормализованных событий с виртуальным временем
0–60000 ms; выход — решения, а не исполнение действий. Поле `model_only=true`
и отдельная schema отличают trace от native measurement; `effects` и
`stop_required` существуют только в модели. Данные ответа — заранее заданные
счётчики, а не DNS-records. Raw/неизвестные поля и неверный порядок отвергаются
фиксированной ошибкой без повторения входа. Выход ограничен формой <4 KiB.

Проверены sync/pending, callback до возврата API, оба порядка cancel/completion,
отложенная отмена во время API-вызова, отсутствие completion, границы 1800/2000 ms,
ошибки/пустой ответ/лимит записей и однократные решения об освобождении.
Сигнал результата не равен выходу callback; возврат отмены не равен completion.
Для освобождения требуются завершение исходного API, выход callback при pending
и возврат уже начатого вызова отмены. Success не публикуется без cleanup ACK.
Поздний ответ не повышает canceled; поздний cleanup не снимает sticky STOP.
События с одинаковым временем обрабатываются в заданном порядке: это проверка
сценариев, не доказательство синхронизации реальных OS threads.
Deadline наблюдается только на переданных событиях: без tick на 1800 ms
просроченная отмена принимается при следующем событии, без заднего изменения
времени. Если это событие уже содержит результат, native cancel intent не нужен,
но outcome остаётся canceled. Такая trace не доказывает своевременную отмену.

TDD: исходный RED отсутствующей модели, focused GREEN. Дополнительный RED
воспроизвёл преждевременное решение free_context, когда callback вышел, а вызов
отмены ещё выполнялся; добавлено ожидание cancel_return, затем focused GREEN.
Read-only ревью выявило несогласованный deadline_exceeded до dispatch для
поздних cancel/invalid_input; отдельный RED подтвердил его, общий time guard
исправлен. Native API и существующий набор HTTP/ICMP не затронуты.
Один итоговый целевой набор:
`python -B -m unittest -v tests.test_phase16_dns_lifecycle` —
**16 tests PASS, 0.004 s, exit 0**. Другие suites не запускались; прежние
HTTP/ICMP результаты не пересчитывались. После тестов — readback, проверка
diff/whitespace, новых локальных ссылок и отсутствия секретов в изменениях.

Ограничения: нет native bridge, ABI/layout, resolver/interface admission,
проверки FQDN/CNAME, обхода native records или реального управления памятью.
Виртуальные дедлайны не гарантируют wall-clock containment. Callback-exit и
cleanup ACK заданы тестом и требуют самостоятельного доказательства в bridge.
Модель позднего cleanup не разрешает фоновую дочистку в приложении.
Следующий отдельный gate — обосновать native bridge/containment и binding;
новые процессы, interop и live DNS этим GO не разрешены. Windows/quality gates
не сняты; iPhone/A/B отложены. AWG2/package016/stage/install/push не затронуты.

### Native DNS bridge: локальная оценка допуска — 2026-09-07

Основание: «согласовываю» на локальное обоснование после commit
`6ca2e0aa4ca241b3d203704a972a24adb9991c99`. Это анализ реализуемости по d1 и
исходнику модели, не реализация, новый API-аудит или подтверждение native фактов.
Сеть, SDK/ABI-проверки и тесты в этом ходе не выполнялись. Статус:
`LOCAL_ASSESSMENT_COMPLETE_NATIVE_ADMISSION_BLOCKED`.

**Вывод.** Имеющихся доказательств недостаточно для допуска in-process bridge
с общим hard-wall 2000 ms. Это не доказательство невозможности Windows API:
не закрыты отдельные обязательства по lifetime, остановке и binding.
Разрабатывать ещё одну модель либо переносить replay() в PowerShell не нужно.
DNS measurement не является исправлением установленного Windows VPN-клиента.

| Вариант | Что требуется сверх текущей модели | Решение этого scope |
| --- | --- | --- |
| In-process bridge к штатному DNS API | Доказанный lifetime и прекращение незавершённого запроса в общем бюджете | Кандидат, не допущен к реализации/live |
| Изолированный worker с контролем родителя | Отдельное разрешение на процесс; доказательства завершения/cleanup и отсутствия оставшейся DNS-операции, включая возможную работу вне worker | Не выбран; kill процесса сам по себе не доказательство остановки DNS |
| Пока оставить DNS measurement нереализованным | Сохранить missing/blocked и обязательный DNS gate | Рекомендуемый текущий режим, без понижения acceptance |

**Минимальный проект lifetime, не готовый bridge.** Один владелец request,
result, server list, context и callback; terminal outcome фиксируется один раз.
Возврат исходного вызова, конец вызова отмены и завершение callback учитываются
раздельно. Решение об освобождении и выполнение освобождения также раздельны;
cleanup ACK публикуется только после фактической безопасной очистки.
Объекты с разным native lifetime нельзя автоматически объединять в free_context.

Важный незакрытый переход: SetEvent/Task completion либо флаг в последней строке
callback не доказывает возврат callback через native/managed trampoline.
Поэтому событие callback_exit из модели нельзя буквально заменить таким флагом.
Будущий bridge должен предъявить подтверждённое правило отсутствия дальнейших
обращений отдельно для данных запроса и callback/delegate; до этого освобождение
не допускается. Постоянно удерживать delegate или откладывать cleanup без лимита
не является автоматически согласованным решением. PowerShell callback scriptblock,
новая потоковая обвязка и уничтожение runspace не предлагаются как обход этого gate.

**Время.** Принять cancel, вернуться к вызывающему коду, завершить native query
и освободить её ресурсы — четыре разных наблюдения. Нужны доказательства для
dispatch, cancel, callback и cleanup в общем бюджете, а не только timeout ожидания.
В модели tick подаётся извне; она не доказывает запуск отмены ровно на 1800 ms.
Если на 2000 ms завершение не подтверждено, остаётся cleanup_unconfirmed/STOP;
безопасное удержание памяти само по себе не доказывает остановку сетевой работы.
Ни один успешный пробный запрос не закрывает ветку отсутствующего callback.

**Binding и результат.** До будущего вызова потребуется approved manifest с
одним FQDN, resolver IPv4, интерфейсом и идентичностью текущего tunnel/session.
Совпадение interface index само по себе недостаточно для допуска после reconnect.
Проверка актуального интерфейса/маршрута будет отдельным разрешённым наблюдением;
не делать её сейчас и не читать профиль для заполнения manifest.
Нужно подтвердить применимость полей/flags выбранного API: explicit server и
interface, исключение локальных источников/search suffix, отсутствие fallback.
Без подтверждения — STOP, не другой resolver/метод. Отдельно остаются ABI/layout,
соответствие A/CNAME запрошенному имени, ownership record list и transport cap.
Полный туннельный маршрут или положительный A-count не заменяют эти доказательства.

**Один следующий gate, без серии реализаций.** Предлагается отдельное точное
read-only разрешение на официальные Microsoft Learn/Windows SDK материалы:
проверить lifetime после callback/cancel, наличие документированного bounded
completion и применимость resolver/interface binding. Результат — source-backed
матрица «подтверждено / не гарантировано / не установлено» с прямыми основаниями.
Если ограничение 2000 ms не обосновано — остановить эту ветку, не писать bridge,
не создавать worker и не ослаблять критерии; альтернативу согласовать отдельно.
Если доказательства достаточны — представить один минимальный design для approval,
после него отдельный offline TDD scope. Никаких live probes для получения допуска.

Проверки этого docs-only изменения: readback, diff/whitespace, согласованность
с d1/model и отсутствие секретов. Исторический результат 16 tests не повторялся
и не объявляется native verification. Новых внешних источников не прочитано;
ссылки предыдущего раздела остаются исторической базой, не свежей проверкой.

### Official DNS source check 2026-09-07

Статус: `OFFICIAL_SOURCE_CHECK_COMPLETE_DNS_BRIDGE_STOP`.
Локальная фиксация завершена 2026-09-08; дата source check остаётся 2026-09-07.
Source baseline фиксации: `67fbbdc9398d59bd3095039a49d3c175c60d7e65`.
Основание записи: `/GO PHASE16 RECORD OFFICIAL_DNS_SOURCE_CHECK HARD_WALL_2000MS_NOT_GUARANTEED CORRECT_API_VS_MODEL_LIFETIME DNS_BRIDGE_STOP LOCAL_DOCS_ONLY NO_CODE_CHANGE NO_TEST_RUN NO_LIVE_ACTION NO_PUSH AWG2_UNTOUCHED`.
Предшествующее чтение 2026-09-07 разрешено exact approval
`READ_ONLY OFFICIAL_MICROSOFT_LEARN_AND_WINDOWS_SDK DNS_BRIDGE_LIFETIME_CANCELLATION_2000MS_RESOLVER_INTERFACE_BINDING` с NO_PROBE/NO_DOWNLOAD/NO_INSTALL/NO_FILE_WRITE/NO_LIVE_SPAIN_ACTION/AWG2_UNTOUCHED.
Прочитаны страницы Microsoft Learn по API/структурам windns.h и managed interop;
локальный SDK/ABI не проверялся. Этот GO только сохраняет результат: повторного
сетевого чтения и диагностических запусков нет.

| Вопрос | Официальное основание и граница вывода |
| --- | --- |
| Общий hard-wall 2000 ms, в том числе 200 ms после cancel | В просмотренных [DnsQueryEx](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsqueryex) и [DnsCancelQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnscancelquery) численная гарантия не найдена. DnsCancelQuery не ожидает completion; pending query отслеживается по callback. Внешний timeout ожидания не доказывает завершение native операции/cleanup. |
| Result и cancel handle | [DnsQueryEx](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnsqueryex) запрещает освобождать result до вызова callback. [DnsCancelQuery](https://learn.microsoft.com/en-us/windows/win32/api/windns/nf-windns-dnscancelquery) связывает lifetime cancel handle с вызовом callback и завершением DnsCancelQuery. Возвращённые RR sets освобождаются DnsRecordListFree согласно [DNS_QUERY_RESULT](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-dns_query_result). |
| Managed delegate | Указатель сам не удерживает delegate от GC; при сохранении указателя native-кодом после возврата исходного вызова delegate нужно удерживать весь срок его использования. [Marshal.GetFunctionPointerForDelegate](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getfunctionpointerfordelegate?view=net-9.0). Это не проверка lifetime конкретного bridge. |
| Explicit resolver/interface | В [DNS_QUERY_REQUEST](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-dns_query_request) документированы pDnsServerList и InterfaceIndex; 0 рассматривает все интерфейсы. Это подтверждает наличие API-механизма, но не фактический AWG tunnel/session, ABI или отсутствие обходного пути на машине оператора. |
| Локальные источники и suffix | [DNS constants](https://learn.microsoft.com/en-us/windows/win32/dns/dns-constants) описывает BYPASS_CACHE, WIRE_ONLY, NO_LOCAL_NAME, NO_HOSTS_FILE, NO_NETBT и TREAT_AS_FQDN; NO_MULTICAST перечислен без пояснения. Рабочая комбинация flags и её фактическое применение здесь не проверены. |
| NRPT и REQUEST3 | Для pCustomServers документация [DNS_QUERY_REQUEST3](https://learn.microsoft.com/en-us/windows/win32/api/windns/ns-windns-dns_query_request3) прямо указывает приоритет совпавшего NRPT-правила. Нельзя обещать безусловный обход системной политики; этот вывод не переносится автоматически на pDnsServerList V1. |

**Поправка API vs model.** Требование d1/replay() ждать полного выхода callback
для всех объектов — наша консервативная политика, не дословный контракт API.
Документация использует границу вызова callback для result и дополнительное
завершение cancel-вызова для cancel handle. Не смешивать lifetime данных запроса,
кода callback и managed delegate. Это не разрешение немедленно освобождать всё
в начале callback: будущая реализация должна учитывать свои обращения и гонки.
Модель сохранена без правок как проверка выбранной политики, не native verifier;
прежние 16 tests PASS не подтверждают API-интеграцию или реальный deadline.

**Решение по заранее установленному stop-condition.** DNS bridge остановлен
при текущем hard-wall контракте: не писать interop/worker, не добавлять модели,
не повторять VPN-прогоны ради этого доказательства. Отсутствие найденной гарантии
не доказывает дефект Windows API, невозможность любого DNS-измерителя или причину
AWG3.1 traffic FAIL. DNS gate остаётся обязательным и непроверенным.

При возврате к DNS нужен отдельный scope на методику: различить критерий ответа
5/5 <=2 s и бюджет безопасного завершения операции, сохранив явные stop/cleanup
правила. В этом GO численные критерии и d1 budget не изменены, новая методика
не согласована. P0 quality/A/B остаётся отложенным; Windows требует новой
проверяемой гипотезы либо изменения официального engine; интеграция ждёт gates.

Проверки фиксации: readback, diff/whitespace, точные ссылки ранее прочитанных
источников, согласованность и отсутствие секретов в добавлениях. Код/тесты,
исторические receipts, protected profiles, AWG2/package016 не менялись.
NO_TEST_RUN; NO_LIVE_ACTION; NO_PUSH; stage/install/issuance не выполнялись.
