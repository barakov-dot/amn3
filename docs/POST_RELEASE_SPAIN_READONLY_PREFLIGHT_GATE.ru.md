# Spain read-only preflight gate

## Статус

Этот gate реализует только checksum-bound read-only инвентаризацию Spain VPS.
Run `spain-fresh-20260720-003` завершился fail-closed после SSH на sanitized
`remote_probe/systemd_cgroup_ports/exit=1`. Claim и failure evidence созданы,
success evidence отсутствует; approval consumed и не подлежит повтору.
Следующий live run запрещён до отдельного subreason diagnostic contract,
commit/push/origin readback и новой literal approval.

Две отдельно одобренные попытки 2026-07-20 завершились fail-closed до создания
evidence. Первая выявила преобразование диагностического stderr `nft` в
PowerShell `NativeCommandError`; вторая после узкого nft correction вернула
ненулевой SSH status без безопасной классификации. Оба approval исчерпаны.

Текущая локальная версия добавляет stage-coded failure envelope без raw stderr
и corrected systemd `ControlGroup -> MainPID -> procfs` resolver. Новый
live-запуск не выполнялся. Новый запуск требует отдельного approval,
привязанного к новым runner/probe SHA-256, source, immutable trust bundle
`spain-fresh-20260720-001` и отдельному outcome run
`spain-fresh-20260720-003` после origin readback. Telegram API не вызывался,
установка и любые live-изменения не производились.

Runner допускает единственный режим `preflight` и до обращения к private
artifacts требует полного точного approval и exact trust run id
`spain-fresh-20260720-003`. Approval привязан одновременно к фактическому
SHA-256 самого runner, SHA-256 удалённого probe, исходному AMN2 head и этому run
id. При пустом `-Approval` runner печатает одну полностью материализованную
строку и завершается с ошибкой до чтения private target или SSH; это безопасный
локальный preview, а не live-authority. Частичное совпадение, шаблон, другой run
id или approval другого gate не подходят.

## Повторное использование trust state Task 7

Gate не создаёт второй SSH-контур. Он потребляет уже подготовленные Task 7 artifacts в игнорируемом каталоге:

```text
private-artifacts/post-release/spain-migration/<run_id>/target.env
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain.pub
private-artifacts/post-release/spain-migration/<run_id>/known_hosts_spain
```

Trust artifacts читаются только из protected local copy immutable run
`spain-fresh-20260720-001` под `%LOCALAPPDATA%\AMN2`, а
claim/evidence создаются только в новом run `spain-fresh-20260720-003`. Перед
SSH runner до любого trust read проверяет current-user-only owner/ACL всей
заранее подготовленной private-artifact parent chain, отвергает reparse points,
проверяет точную четырёхстрочную схему
binding, соответствие `SSH_KEY_PATH` dedicated key, совпадение private/public
Ed25519 пары и независимый fingerprint `known_hosts_spain`. Ambient SSH config
отключён через `-F none`; обязательны batch mode, только dedicated identity и
strict host-key checking.

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

До SSH runner атомарно создаёт защищённый `preflight-outcome.claim`. Claim
остаётся постоянным single-use marker и не позволяет повторно использовать gate
в том же exact trust run. При remote failure принимается только одна строка
`AMN2_SPAIN_PREFLIGHT_FAILURE_V1` с allowlisted stage и exit code, совпадающим с
OpenSSH exit code. Malformed, duplicate или mixed envelope закрывает gate.
Успех создаёт только `preflight-evidence.json`; классифицированная ошибка —
только `preflight-failure-evidence.json`. Raw stdout/stderr не сохраняется.

Firewall inventory и effective SSH policy являются обязательными: отсутствие
поддерживаемого reader, пустой результат или ошибка чтения закрывают gate. Для
systemd fingerprint полное чтение unit content и cgroup socket state также
обязательно. Пустой `ControlGroup` у active unit разрешается только как
`active_exited_no_live_process` при `MainPID=0`; при живом `MainPID` procfs
cgroup принимается только после canonical unit-id binding и повторной проверки
стабильности PID, process starttime и cgroup. Недоступный или сменившийся PID,
FD, `readlink` или socket table не превращается в ложный пустой port set.

Из `unrelated_service_fingerprint` исключаются только точные deployment-owned имена `amneziya-web.service`, `amneziya-bot.service` и `amnezia-awg2`. Похожие или расширенные имена не исключаются и остаются в fingerprint. Это публичные contract names, а не private resident-service identifiers.

## Граница безопасности

Probe не устанавливает и не обновляет пакеты, не пишет удалённые файлы, не изменяет firewall, Docker или systemd, не запускает и не останавливает сервисы. Он не изменяет AWG, AMN2, Telegram и посторонний сервис. Fingerprint предназначен для последующего точного сравнения до и после отдельно разрешённых этапов.

Наличие этого кода не является live-authority. Будущий оператор сначала
проверяет repository head, SHA runner/probe и Task 7 trust artifacts, затем
получает отдельное точное approval и только после этого запускает gate один раз.
Два старых approval не дают права на retry; stage-coded gate ещё не запускался.
