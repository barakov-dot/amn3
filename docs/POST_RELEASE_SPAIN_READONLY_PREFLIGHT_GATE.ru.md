# Spain read-only preflight gate

## Текущий статус: run 008 выявил CRLF transport defect; финальный run 009

Run 008 consumed. Claim создан, success/failure evidence отсутствуют. Локальный
probe содержит только LF, но прежний PowerShell object pipeline добавил CRLF
при передаче string в native stdin. Поэтому удалённый Bash получил лишний CR
после последней строки; это доказанный локальный transport defect.

Исправленный runner передаёт checksum-validated byte array напрямую через
`StandardInput.BaseStream`. Локальный end-to-end regression подтвердил, что
payload `41 0A` достигает child process ровно как `410A`, без добавленного CR.

```text
outcome_run=spain-fresh-20260721-009|not_created|not_run|approval_required|final_allowed_attempt
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=26ED19344B9E7F56069BFEBAC9864BB5779B413767312B4AAB411B7DBF859D76
tests=focused_33_passed|full_209_passed
remaining_live_attempt_cap=run_009_only_then_stop_and_switch_approach
```

Run 009 требует отдельной exact approval. Независимо от результата он является
последним attempt в этой цепочке.

## Текущий статус: safe envelope rejection diagnostic готов для run 008

Strict parser остаётся authority для remote failure envelope. При наличии
prefix и parser rejection новый runner записывает только безопасную
классификацию `envelope_rejected`, `stage=unavailable`, process exit и одну
причину из `prefix_count|shape|stage|exit|stage_exit_mapping|unavailable`.
Raw line, parsed stage и private remote values не сериализуются.

```text
outcome_run=spain-fresh-20260721-008|not_created|not_run|approval_required
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=C4F00EC9E0C53D9B9582B083ED8598BD3CB3F7DC202AA638AF7B197F8B730652
tests=focused_30_passed|full_206_passed
remaining_live_attempt_cap=run_008_then_at_most_one_proven_fix_run_009
```

Run 008 требует отдельной exact approval. При его неуспехе разрешён максимум
один доказательно обоснованный run 009; далее gate переводится на provider
console/другой способ, а не на новый повтор.

## Текущий статус: run 007 envelope rejection fail-closed

Run `spain-fresh-20260720-007` выполнен один раз. Failure prefix был замечен,
но strict parser вернул `$null`; runner остановился до sanitized failure JSON.
Outcome claim присутствует, success/failure evidence отсутствуют. Raw output не
сохранён. Run consumed и не даёт authority на retry.

```text
outcome_run=spain-fresh-20260720-007|fail_closed|approval_consumed|never_repeat
classification=envelope_rejected
prefix=present
parser_result=rejected
stage=not_proven
exit=not_proven
claim=present
failure_evidence=absent
success_evidence=absent
next_outcome_run=spain-fresh-20260721-008|required_after_safe_envelope_rejection_diagnostic
```

Локальная synthetic reproduction exact prefix/shape/exit успешно проходит
текущий parser boundary, поэтому общий PowerShell stream/cast defect не доказан.
Следующий local-only slice должен выдавать safe rejection reason, не сохраняя
raw envelope или target values. Без нового exact approval SSH не выполняется.

## Предыдущий локальный transport diagnostic contract для run 007

Runner будущего `spain-fresh-20260720-007` временно принимает combined
OpenSSH output в память и классифицирует только `exit=255`. Разрешены safe
subreason: `connect_timeout`, `connection_refused`, `no_route`,
`name_resolution`, `host_key`, `authentication`, `remote_closed`,
`remote_reset`. Ровно одна distinct category обязательна; иначе сохраняется
только `unavailable`.

Raw output, target/user/port/path, host-key values и regex captures не
переносятся в evidence и очищаются до evidence construction/write. Отдельных
stderr files, network probes или remediation нет. Run `007` не создан и не
выполнялся; без точного approval новый SSH/preflight не выполняется.

```text
transport_subreason_diagnostic=implemented_locally|tdd_red_green_verified
transport_capture=in_memory_only|no_raw_persistence
outcome_run=spain-fresh-20260720-007|not_created|not_run|approval_required
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=9A6BCA57930A685B6D8B997E85972336A37F289D7D39073058EDAD4625DC34A3
tests=focused_29_passed|full_205_passed
```

## Предыдущий статус: run 006 transport fail-closed

Run `spain-fresh-20260720-006` выполнен один раз. Claim создан, но OpenSSH
вернул exit `255` без remote diagnostic envelope; runner сохранил только
sanitized transport failure evidence. Это не является подтверждением remote
render/OS state. Run consumed, retry запрещён; без отдельного transport
subreason diagnostic contract новый SSH/preflight не выполняется.

```text
outcome_run=spain-fresh-20260720-006|fail_closed|approval_consumed|never_repeat
classification=transport
stage=unavailable
subreason=unavailable
exit=255
claim=present
failure_evidence=present|sanitized
success_evidence=absent
next_outcome_run=spain-fresh-20260720-007|required_after_transport_diagnostic
```

## Предыдущий локальный diagnostic contract для run 006

До JSON rendering remote probe проверяет только шесть already-used external
dependencies. Exact пары `render/81..86` маппятся runner-ом соответственно в
`sha256sum`, `cut`, `tr`, `awk`, `sort`, `paste`. Незнакомая пара или
malformed/mixed envelope не получает подпричину и закрывает gate. Никакие raw
stderr/stdout, command path/name beyond the allowlisted label, private target,
unit, PID, FD, socket или config value не сохраняются.

`spain-fresh-20260720-006` ещё не создан, SSH/preflight не выполнялся и
требует отдельную checksum-bound literal approval. Run `005` consumed и
повторять его нельзя; fresh-install/Phase12 migration gate остаётся закрытым
до успешного `006`.

```text
render_subreason_diagnostic=implemented_locally|tdd_red_green_verified
render_safe_pairs=81:sha256sum|82:cut|83:tr|84:awk|85:sort|86:paste
outcome_run=spain-fresh-20260720-006|not_created|not_run|approval_required
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
runner_sha256=FF9D9B731A2AEE12C7E1A98CA0AACB8B533F051D666E1D4C4352BFDE0F6B143D
tests=focused_28_passed|full_204_passed
```

## Предыдущий статус

Corrected single-use gate для `spain-fresh-20260720-005` выполнен ровно один
раз и завершился fail-closed на sanitized `remote_probe/render/exit=127`.
Он подтвердил закрытие прежнего ложного `pid/76` на пустом `cgroup.procs`, но
не открыл fresh-install gate: success evidence отсутствует, approval consumed,
retry запрещён. Следующий запуск требует отдельного render subreason diagnostic
contract, нового outcome id и новой checksum-bound literal approval; без
точного approval новый SSH/preflight не выполняется. Для future run `006`
SSH/preflight ещё не выполнялся.

```text
outcome_run=spain-fresh-20260720-005|fail_closed|approval_consumed|never_repeat
classification=remote_probe
stage=render
subreason=unavailable
exit=127
claim=present
failure_evidence=present|sanitized
success_evidence=absent
immutable_trust_bundle=spain-fresh-20260720-001
remote_probe_sha256=B45764A57E4258C8DD1AFC1570FE5F4359C755C146449225EAC0B74044E3F3F1
runner_sha256=B42EEE2ED6D63DDC81BCDAF337B9A1581757C8B1E5B1475FACFF69322DD75C82
tests=focused_27_passed|full_203_passed|bash_powershell_parse_pass
security=codex_diff_scan_complete|reportable_findings_0|secret_matches_0
```

Локальный review render stage показывает redacted JSON rendering through shell
helpers and allowlisted external commands. Текущий failure envelope намеренно не
сохраняет raw stdout/stderr и не раскрывает, какая именно команда отсутствует;
поэтому исправление должно быть отдельным diagnostic slice с allowlisted
subreason, а не ad-hoc remote probing.

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
