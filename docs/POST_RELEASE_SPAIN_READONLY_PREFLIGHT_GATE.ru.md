# Spain read-only preflight gate

## Статус

Этот gate реализует только checksum-bound read-only инвентаризацию Spain VPS.
Первый отдельно одобренный запуск 2026-07-20 завершился fail-closed до создания
evidence из-за преобразования диагностического stderr `nft` в PowerShell
`NativeCommandError`. Старый approval исчерпан; повторный SSH-запуск не выполнялся.
Исправленный probe подавляет только stderr точной команды `nft list
ruleset`, сохраняя её ненулевой exit status и действие `set -euo pipefail`.
Новый запуск требует отдельного approval, привязанного к новым runner/probe
SHA-256 после origin readback. Telegram API не вызывался, установка и любые
live-изменения не производились.

Runner допускает единственный режим `preflight` и до обращения к private artifacts требует полного точного approval. Approval привязан одновременно к фактическому SHA-256 самого runner, SHA-256 удалённого probe и исходному AMN2 head. При пустом `-Approval` runner печатает одну полностью материализованную строку и завершается с ошибкой до чтения private target или SSH; это безопасный локальный preview, а не live-authority. Частичное совпадение, шаблон или approval другого gate не подходят.

## Повторное использование trust state Task 7

Gate не создаёт второй SSH-контур. Он потребляет уже подготовленные Task 7 artifacts в игнорируемом каталоге:

```text
private-artifacts/post-release/spain-migration/<run_id>/target.env
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain.pub
private-artifacts/post-release/spain-migration/<run_id>/known_hosts_spain
```

Перед SSH runner проверяет защищённые ACL, точную четырёхстрочную схему binding, соответствие `SSH_KEY_PATH` dedicated key, совпадение private/public Ed25519 пары и независимый fingerprint `known_hosts_spain`. Ambient SSH config отключён через `-F none`; обязательны batch mode, только dedicated identity и strict host-key checking.

## Состав evidence

Удалённый probe формирует нормализованный JSON `amn2.spain-readonly-preflight.v1`:

- ОС и kernel без hostname или target address;
- CPU, RAM и ёмкость корневого диска;
- listening sockets только как protocol/scope/port, без адреса;
- безопасные состояния Docker и systemd с хешированными именами;
- digest и количество отображаемых firewall rules без раскрытия адресов;
- allowlist безопасных значений эффективной SSH policy;
- UTC clock и наличие фиксированного набора пакетов;
- `unrelated_service_fingerprint` из kind, name hash, image/unit hash, active state, restart count и bound-port set.

Evidence не содержит environment, config bodies, command line, IP/host, ключи, учётные данные или Telegram-значения. После проверки JSON runner атомарно создаёт `preflight-evidence.json` через create-new/no-replace в том же private run directory, затем отдельно защищает и повторно проверяет ACL. Конкурентный или повторный writer не может заменить уже записанные evidence bytes.

Firewall inventory и effective SSH policy являются обязательными: отсутствие поддерживаемого reader, пустой результат или ошибка чтения закрывают gate. Для systemd fingerprint полное чтение unit content и cgroup socket state также обязательно; недоступный PID, FD, `readlink` или socket table не превращается в ложный пустой port set.

Из `unrelated_service_fingerprint` исключаются только точные deployment-owned имена `amneziya-web.service`, `amneziya-bot.service` и `amnezia-awg2`. Похожие или расширенные имена не исключаются и остаются в fingerprint. Это публичные contract names, а не private resident-service identifiers.

## Граница безопасности

Probe не устанавливает и не обновляет пакеты, не пишет удалённые файлы, не изменяет firewall, Docker или systemd, не запускает и не останавливает сервисы. Он не изменяет AWG, AMN2, Telegram и посторонний сервис. Fingerprint предназначен для последующего точного сравнения до и после отдельно разрешённых этапов.

Наличие этого кода не является live-authority. Будущий оператор сначала
проверяет repository head, SHA runner/probe и Task 7 trust artifacts, затем
получает отдельное точное approval и только после этого запускает gate один раз.
Первый approval не даёт права на retry; исправленный gate ещё не запускался.
