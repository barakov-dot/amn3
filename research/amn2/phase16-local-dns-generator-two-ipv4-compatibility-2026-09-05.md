# Phase 16 — локальное исправление генератора двух IPv4 DNS

- Дата: 2026-09-05.
- Baseline: `15e7d2d15922919aefb9d5721dc4f285042490e7`.
- Результат: local DNS compatibility correction; runtime/client acceptance не заявляется.
- Approval: `/GO PHASE16 FIX_LOCAL_DNS_GENERATOR_TWO_IPV4_COMPATIBILITY TDD_ONE_TARGETED_SUITE NO_REAL_CONFIG_GENERATION PRESERVE_EXISTING_PROFILES PACKAGE016_IMMUTABLE NO_LIVE_ACTION NO_INSTALL NO_PUSH AWG2_UNTOUCHED`.

## Причина и изменение

`render_pair` передавал всю DNS-строку в `IPv4Address`, поэтому явно заданная
пара отвергалась. Сохранённое исследование импортёра AmneziaVPN 5.0.1.5
показало, что его DNS extraction требует два IPv4 адреса; одноадресный профиль
может импортироваться с fallback DNS вместо заданного значения. Это не доказательство
причины Windows data-plane failure. Исторический источник не изменялся:
`research/amn2/phase16-arm-dns9-check-2026-08-28.md`.

Добавлена узкая нормализация одного legacy DNS или двух явно заданных IPv4 DNS.
Пара записывается как `DNS = IPV4, IPV4`; второй адрес не выбирается автоматически.
Новая файловая подготовка требует ровно два адреса и проверяет их до чтения
ключей/создания каталога. Отвергаются неверные типы, пустые элементы, третий
адрес, IPv6, неверный IPv4, loopback/multicast/unspecified и управляющие символы.
Ошибки содержат только фиксированный token, без входных значений.

Чистый `render_pair` и `validate_pair` сохраняют одноадресную совместимость для
старых входов. Остальные поля, server profile, native validation, root-only
проверки, exclusive creation, approvals, AWG2 equality и rollback не изменены.
Legacy-совместимость не расширяет валидатор на произвольные новые поля профиля.

## TDD evidence

- RED: 4 новых теста, 7 ожидаемых failure/subtest результатов, 0.399 s.
  Два DNS отвергались; numeric/bool ошибочно принимались; файловая подготовка
  читала ключи до проверки неправильного DNS. Setup/import ошибок не было.
- GREEN: те же 4 теста прошли, 0.030 s.
- Единственный итоговый targeted suite: 28 tests PASS, 1.007 s.

Команда итогового набора: bundled Python `-B -m unittest -v
tests.test_phase16_awg31_minimal_pilot tests.test_phase16_awg31_client_recovery`.
26 тестов minimal pilot и 2 client recovery. После документирования повторов нет.

Независимый от renderer regex проверяет документированную форму двух DNS и
буквальные ожидаемые captures. Это narrow characterization, не копия полного
Qt parser, не запуск AmneziaVPN и не новый official-source readback. Проверено
также, что обратная замена только DNS-строки даёт исходные synthetic client bytes,
server bytes совпадают, а повторная файловая подготовка не перезаписывает входы.

Все ключи/профили в тестах синтетические. Файловые операции выполнялись только
в disposable test directories; реальные private artifacts не читались и не
перегенерировались. Docker/systemctl/SSH подменены тестовыми границами;
Git Bash выполнял только `-n` для shell syntax. Установок и сетевых вызовов нет.

## Граница завершения

Исправлен локальный генератор, а не работающий сервер. Существующие профили,
immutable package 016, peers, DNS сервера, firewall, MTU и AWG2 не менялись.
Новая локальная ревизия не переносится на VPS старым approval/hash.
Materialization, package verifier, полный legacy suite и push не запускались.
Task 4A и Task 4.5 остаются blockers. iPhone/две сети отложены по решению оператора,
не отменены. Следующий независимый блок — проект критериев acceptance без live.
