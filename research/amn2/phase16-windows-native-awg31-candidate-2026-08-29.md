# Phase 16 — граница native AWG3.1-кандидата для Windows

- Recorded: `2026-08-29`
- Status: `superseded-by-primary-client-data-plane-regression-evidence`
- Scope: bounded Windows client-path isolation only
- Server action, install or config change: `false`
- AWG2 changed: `false`

## Текущая граница

На Windows 11 установлен AmneziaVPN `5.0.1.5`. С checksum-bound Spain
AWG3.1-профилем клиент показывал подключение, но не создавал наблюдаемый
стандартный tunnel adapter, адрес или маршруты и не пропускал Интернет-трафик.
Тот же профиль последовательно пропускал прикладной трафик на Android и iPhone,
поэтому сервер, peer/config и базовая UDP-достижимость не объясняют Windows
failure.

Read-only local inventory 2026-08-29 подтвердил:

- Windows OS architecture: x64;
- установленный продукт: AmneziaVPN `5.0.1.5`;
- native AmneziaWG не зарегистрирован как установленный продукт;
- `C:\Program Files\AmneziaWG` содержит только прежний каталог `Data`, без
  исполняемого файла native-клиента.

Каталог `Data` не открывался; клиентские логи и защищённые конфиги этим
inventory не читались.

## Официальный upstream

Официальная FAQ Amnezia рекомендует основной AmneziaVPN для Windows 10/11 x64.
Для этой машины текущий рекомендуемый upstream-клиент — уже установленный
AmneziaVPN `5.0.1.5`:

https://docs.amnezia.org/faq/

Отдельные официальные страницы альтернативных клиентов и native AmneziaWG
также публикуют Windows 10/11 x64 asset и разрешают импорт AWG3.1 native
`.conf`. Это подтверждает техническую совместимость, но не превращает native
приложение в основной рекомендованный клиент для этой Windows 11 x64:

https://docs.amnezia.org/documentation/instructions/use-amneziawg-app/

Официальный GitHub release `3.1.0`, commit `ca5dd3b`, опубликован 2026-08-21
и помечен Latest. Release включает merged AWG3.1 support и обновлённый
`awg-go`:

https://github.com/amnezia-vpn/amneziawg-windows-client/releases/tag/3.1.0

Потенциальный secondary diagnostic asset для этой x64 Windows 10/11:

`amneziawg-amd64-3.1.0.msi`

Issue `amnezia-client#3043` содержит похожий внешний отчёт о Windows 11 /
AmneziaVPN 5.0.1.5 с handshake без transport traffic. Это corroborating user
report в официальном repository, а не maintainer-confirmed root cause или fix:

https://github.com/amnezia-vpn/amnezia-client/issues/3043

Read-only compare официального tag `5.0.1.5` с текущей веткой `dev` показал
девять последующих commits. В опубликованном списке нет Windows AWG3.1
transport/tunnel fix; присутствуют исправления `wg show` parsing и unrelated
platform/application changes. Следовательно, текущий `dev` нельзя считать
готовым официальным исправлением наблюдаемого Windows failure:

https://github.com/amnezia-vpn/amnezia-client/compare/5.0.1.5...dev

## Диагностическая гипотеза, не следующий основной шаг

Гипотеза: наблюдаемый Windows failure находится в client/tunnel integration
пути AmneziaVPN 5.0.1.5. Native AmneziaWG 3.1.0 теоретически мог бы изолировать
этот путь без изменения Spain server, peer, port, DNS, MTU или firewall, но он
остаётся secondary A/B-кандидатом. Он не заменяет bounded-диагностику основного
рекомендованного AmneziaVPN 5.0.1.5 и не должен скачиваться первым шагом.

Результат native-клиента будет интерпретироваться так:

- native PASS: failure локализован к пути AmneziaVPN 5.0.1.5; это не снимает
  отдельный iPhone quality blocker;
- native FAIL с отсутствующим adapter/address/routes: Windows/native tunnel
  integration остаётся общей границей;
- native создаёт tunnel и bidirectional traffic, но качество плохое: Windows
  присоединяется к отдельной transport-quality границе;
- любой иной результат: STOP и сбор только нового bounded evidence, без
  изменения server/config параметров.

## Текущий decision gate

Download native AmneziaWG 3.1.0 сейчас не запрашивается. Следующий основной
шаг — bounded read-only диагностика уже установленного AmneziaVPN 5.0.1.5:
точные client/service/tunnel logs, service lifecycle, adapter/address/routes и
сопоставление с официальным upstream implementation.

Для этого нужен ровно один короткий sequential live run с отключёнными iPhone
и Android. Он должен собирать только локальные sanitized classifications;
Spain SSH и server read/write для него не требуются.

Если эта диагностика не локализует failure и secondary native A/B всё ещё будет
обоснован, его download, checksum/signature readback, install и sequential live
test потребуют отдельных approvals. Android и iPhone должны быть отключены,
один peer используется только на Windows, профиль не копируется в Git и его
секреты не выводятся.

Этот документ не разрешает download, install, запуск клиента, импорт профиля,
Spain egress, SSH, server write, signal, restart, config issuance, stage,
изменение AWG2 или general AWG3.1 issuance.

## Follow-up 2026-08-29

Последующая checksum-bound диагностика AmneziaVPN `5.0.1.5` получила более
сильное доказательство, чем первоначальный polling watcher: Wintun создавался,
интерфейс поднимался, AWG handshake и keepalive проходили, а tunnel ring-log не
регистрировал transport error. При этом операторский прикладной трафик за
примерно `57` секунд не заработал. Временное отключение kill switch также не
исправило VPN-трафик. Ring-log является событийным журналом, а не packet
capture, поэтому отсутствие data-packet записей не трактуется как точный
нулевой счётчик пакетов.

Результат и официальный upstream match записаны отдельно:

`research/amn2/phase16-windows-awg31-data-plane-regression-2026-08-29.md`

Native AmneziaWG остаётся неустановленным secondary-кандидатом и не является
следующим шагом. Основной Windows path заблокирован до официального upstream
исправления либо отдельно одобренного checksum-bound официального build.
