# Spain read-only preflight gate

## Статус

Corrected single-use gate для `spain-fresh-20260720-005` подготовлен только
локально и ещё не запускался. Он принимает успешно прочитанный пустой
`cgroup.procs` как завершённый empty port set, сохраняя строгий отказ для любой
существующей nonnumeric PID-строки и прежние FD/readlink/socket проверки. До
получения точного approval после commit/push/origin readback runner не читает
private state, не создаёт outcome; SSH для run `005` не выполнялся.

```text
outcome_run=spain-fresh-20260720-005|not_created|not_run
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=B45764A57E4258C8DD1AFC1570FE5F4359C755C146449225EAC0B74044E3F3F1
runner_sha256=B42EEE2ED6D63DDC81BCDAF337B9A1581757C8B1E5B1475FACFF69322DD75C82
tests=focused_27_passed|full_203_passed|bash_powershell_parse_pass
security=codex_diff_scan_complete|reportable_findings_0|secret_matches_0
```

Run `spain-fresh-20260720-004` выполнен ровно один раз и завершился fail-closed
на safe pair `systemd_cgroup_ports/pid/exit=76`. Claim и sanitized failure
evidence присутствуют, success evidence отсутствует; все checksum/source
bindings совпали. Approval consumed, retry запрещён. Fresh-install gate остаётся
закрытым.

Локальная reproduction установила, что пустой результат `cgroup.procs`
передаётся в `while read` через here-string и создаёт одну синтетическую пустую
итерацию, которую collector принимает за malformed PID. Новый TDD correction
должен считать ноль process rows валидным завершённым empty port set, сохранив
fail-closed проверку каждой непустой PID-строки. Это изменение и новый live run
требуют отдельных approvals.

Этот gate реализует только checksum-bound read-only инвентаризацию Spain VPS.
Run `spain-fresh-20260720-003` завершился fail-closed после SSH на sanitized
`remote_probe/systemd_cgroup_ports/exit=1`. Claim и failure evidence созданы,
success evidence отсутствует; approval consumed и не подлежит повтору.
Этот исторический prerequisite был выполнен перед run `004`; сам run `004`
теперь consumed и не подлежит повтору. Любой будущий preflight требует нового
исправленного code, новых runner/probe SHA, нового outcome id и новой literal
approval после commit/push/origin readback.

Две отдельно одобренные попытки 2026-07-20 завершились fail-closed до создания
evidence. Первая выявила преобразование диагностического stderr `nft` в
PowerShell `NativeCommandError`; вторая после узкого nft correction вернула
ненулевой SSH status без безопасной классификации. Оба approval исчерпаны.

Версия, с которой выполнялся run `004`, добавляет stage-coded failure envelope без raw stderr,
corrected systemd `ControlGroup -> MainPID -> procfs` resolver и закрытый
cgroup-port subreason allowlist. Run `004` выполнен и завершился fail-closed;
его code/SHA/outcome/approval больше не дают live authority. Новый запуск
возможен только после отдельной TDD-коррекции и approval, привязанного к новым
runner/probe SHA-256, source, immutable trust bundle
`spain-fresh-20260720-001` и новому outcome run после origin readback. Telegram API не вызывался,
установка и любые live-изменения не производились.

Consumed runner допускает единственный режим `preflight` и был привязан к exact
run id `spain-fresh-20260720-004`. Повторно вызывать его запрещено. Его approval
был привязан одновременно к фактическому
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
claim/evidence создаются только в новом run `spain-fresh-20260720-005`. Перед
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
Такие ошибки переводятся только в пары `systemd_cgroup_ports/exit=75..80` и
safe subreason `cgroup_procs`, `pid`, `fd_directory`, `fd_readlink`,
`socket_table`, `socket_parse`. До конвертации каждый hex port строго
валидируется; частичная нормализация запрещена. Runner отклоняет любую другую
пару stage/exit и не сохраняет raw unit/PID/FD/path/socket values.

Из `unrelated_service_fingerprint` исключаются только точные deployment-owned имена `amneziya-web.service`, `amneziya-bot.service` и `amnezia-awg2`. Похожие или расширенные имена не исключаются и остаются в fingerprint. Это публичные contract names, а не private resident-service identifiers.

## Граница безопасности

Probe не устанавливает и не обновляет пакеты, не пишет удалённые файлы, не изменяет firewall, Docker или systemd, не запускает и не останавливает сервисы. Он не изменяет AWG, AMN2, Telegram и посторонний сервис. Fingerprint предназначен для последующего точного сравнения до и после отдельно разрешённых этапов.

Наличие этого кода не является live-authority. Будущий оператор сначала
проверяет repository head, SHA runner/probe и Task 7 trust artifacts, затем
получает отдельное точное approval и только после этого запускает gate один раз.
Approvals runs `001`–`004` consumed и не дают права на retry. Будущий corrected
gate обязан использовать новый outcome id и новую checksum-bound literal approval.
