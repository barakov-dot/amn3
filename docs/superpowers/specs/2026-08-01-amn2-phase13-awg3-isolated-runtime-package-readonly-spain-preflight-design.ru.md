# AMN2 Phase 13 — проект пакета изолированного runtime с контрольными суммами и предварительной проверки Spain только для чтения

Дата: 2026-08-01

Статус: `written_spec_pending_operator_review`

## 1. Разрешение и граница

Оператор разрешил только product/engineering evidence, локальное
проектирование checksum-bound isolated-runtime package, diff/secret/security
review и подготовку read-only Spain conflict/equality preflight для AWG3
candidate.

Этот проект не разрешает и не выполняет:

- package build или deploy;
- SSH mutation или удалённую запись;
- создание, изменение или удаление config/peer/key;
- остановку, restart, recreate или upgrade принятого Spain AWG2;
- reboot или rollback rehearsal;
- изменение постороннего Spain-сервиса;
- USA shutdown, cleanup или reuse;
- production AWG3 issuance.

До появления нового одноразового `outcome_id`, exact SHA-256 runner,
collector, schema и manifest, а также отдельной literal approval, SSH preflight
не запускается.

## 2. Авторитетная исходная точка

- AMN2 base: `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Phase 13 reviewed head:
  `ff115b63ca1329640ca13ae0a502d155f99b456b`.
- Spain operational overlay:
  `f1bf099ddb47da26a4080714376babaf5b0de92c`.
- USA rollback overlay:
  `0b858c5cdbc5b565cc265966a2edfe2d339d65e0`.
- Spain AWG2: primary, accepted, UDP `30001`, VPN CIDR
  `10.212.12.0/24`, route через `amn2spbr0`.
- Принятые устройства d1–d7: `7`; persistent/live peers: `7/7` exact.
- AWG restart count: `59`, должен оставаться неизменным в рамках preflight.
- Web: только `127.0.0.1:3031`; bot disabled.
- AMN2-tagged forward rules: ровно `3`.
- Foreign persistent entries: `153`, changed `0`.
- Foreign persistent stable SHA-256:
  `F5767F361A9441DD4B5361C07DA164A3059E0D1347D5217594534797D367B7E8`.
- Final foreign equality receipt SHA-256:
  `BC9065B3FA7CAB40F5EEFEBBFD8093F2D62477E972777FE665E8D9F6028AA704`.

Локальная реализация Phase 13 имеет полный набор тестов `1108 passed, 1 skipped,
1 warning`. Запечатанный отчёт безопасности имеет `0` значимых findings и одно
ограниченное последующее действие для будущего writer отрицательного
compatibility evidence.

## 3. Выбранная архитектура

Принят вариант: неизменяемая основа equality Phase 12 плюс новый Phase 13
wrapper/schema.

### 3.1 Неизменяемая основа проверки равенства Phase 12

Принятые нормализация, foreign projection и equality semantics Phase 12 не
переписываются и не расширяются эвристическими исключениями. Новый wrapper
вызывает их как отдельную версионированную зависимость и проверяет их exact
SHA-256 до запуска.

Новый AWG3 candidate не добавляется в foreign allowlist. Во время read-only
preflight он ещё отсутствует, поэтому любой обнаруженный объект с candidate
identity является конфликтом, а не допустимой AMN2-owned delta.

### 3.2 Наблюдение изолированного runtime Phase 13

Новый collector наблюдает только свойства, необходимые для решения
`pass|stop`:

- занятость UDP port;
- существование interface, bridge, container, service и config path;
- addresses, routes и CIDR overlap;
- Docker/systemd capability и их наблюдаемое состояние;
- accepted AWG2 invariants;
- foreign persistent equality;
- неоднозначность ownership.

Collector не формирует install commands, не создаёт каталоги и не меняет
runtime state.

### 3.3 Контейнер доказательств Phase 13

Локальный wrapper связывает exact runner, collector, schema, manifest,
authoritative source и candidate resource plan. Он создаёт локальный protected
claim до SSH и допускает ровно один outcome. Raw stdout/stderr не сохраняются.

## 4. План ресурсов-кандидатов

Следующие значения являются только кандидатами для read-only проверки и не
являются разрешением на создание ресурсов:

| Поле | Значение-кандидат |
|---|---|
| `runtime_instance_id` | `spain-awg3-candidate-001` |
| `protocol_version` | `awg3` |
| `lifecycle_state` | `planned` |
| `interface_name` | `awg3` |
| host bridge | `amn2sp3br0` |
| UDP port | `30002` |
| VPN CIDR | `10.212.13.0/24` |
| server VPN address | `10.212.13.1/24` |
| container CIDR | `172.29.252.0/28` |
| candidate container | `amn2-spain-awg3` |
| candidate service | `amn2-spain-awg3.service` |
| candidate state root | `/var/lib/amn2-spain/awg3` |
| candidate config path | `/var/lib/amn2-spain/awg3/awg3.conf` |

Все значения fail closed при существовании, занятости, пересечении или
неоднозначном результате наблюдения. Автоматический поиск другого свободного
значения запрещён: изменение candidate требует нового manifest и новой
approval.

## 5. Проектируемый состав будущего комплекта предварительной проверки

Комплект будет содержать только локальные read-only/preparation artifacts:

1. `phase13-awg3-preflight-manifest.json` — canonical manifest.
2. `phase13_spain_awg3_readonly_preflight_remote.sh` — удалённый read-only
   collector без записи.
3. `phase13_spain_awg3_readonly_preflight_ssh_runner.ps1` — локальный
   checksum/outcome/transport wrapper.
4. `phase13-awg3-readonly-preflight.schema.json` — строгая schema evidence.
5. `phase13-awg3-readonly-preflight-failure.schema.json` — строгая schema
   sanitized failure evidence.
6. Локальные fixtures и tests для pass, conflict, ambiguity, checksum mismatch,
   transport failure и replay.
7. Exact reference на неизменённый Phase 12 equality collector и его SHA-256.

Текущий design gate не создаёт эти файлы и не собирает archive. Runtime image,
Docker bundle, installer, rollback executor, server/client config и secret
material в preflight-комплект не входят.

## 6. Контракт канонического manifest

Manifest использует document type
`amn2.phase13.awg3-readonly-preflight-manifest.v1` и содержит:

- `outcome_id`;
- `created_at` и `expires_at`;
- `target_role=spain-primary` без IP, hostname, username и SSH port;
- exact AMN2 base/head и Spain overlay;
- exact candidate resource plan из раздела 4;
- SHA-256 runner, collector, schemas и Phase 12 foundation;
- expected foreign baseline count/hash/receipt;
- expected AWG2 safe invariants;
- read-only command families;
- запрещённые действия;
- `max_attempts=1`;
- `remote_write_allowed=false`;
- `package_build_allowed=false`;
- `live_action_authorized=false`.

Canonical JSON использует UTF-8 без BOM, LF, отсортированные keys и отсутствие
необъявленных полей. Любое изменение bytes аннулирует checksum и approval.

## 7. Схема evidence

Успешный документ имеет type
`amn2.phase13.awg3-readonly-preflight.v1` и обязательные группы:

### 7.1 Идентификация

- `outcome_id`;
- `checked_at`;
- `source_head`;
- `manifest_sha256`;
- `runner_sha256`;
- `collector_sha256`;
- `schema_sha256`;
- `phase12_foundation_sha256`.

### 7.2 Наблюдение ресурсов-кандидатов

Для каждого candidate resource записывается только:

- declared value;
- `absent|free|conflict|ambiguous|unavailable`;
- safe count или normalized hash при необходимости;
- conflict category без raw command output.

### 7.3 Проверка равенства AWG2

- container/service/interface observed state;
- UDP port `30001` equality;
- VPN CIDR/route equality;
- persistent/live peer counts `7/7`;
- normalized peer-set equality hash без raw public keys/endpoints;
- restart count `59` equality;
- три AMN2-tagged forward rules;
- web/bot state equality.

### 7.4 Проверка равенства постороннего сервиса

- persistent count `153`;
- stable normalized SHA-256;
- `changed=0`;
- final baseline receipt reference;
- `equal=true|false`.

### 7.5 Квитанция безопасности

- `mutation_attempted=false`;
- `remote_file_written=false`;
- `service_action_attempted=false`;
- `container_action_attempted=false`;
- `firewall_action_attempted=false`;
- `secret_bearing_config_accessed=false`;
- `raw_peer_identifiers_emitted=false`;
- `raw_output_persisted=false`;
- `decision=pass|stop`;
- ordered `stop_reasons`.

Unknown fields, missing groups, duplicate keys, invalid enum, non-canonical
hash или inconsistent `decision` завершаются fail closed.

## 8. Классификация конфликтов

| Код | Условие |
|---|---|
| `udp_port_conflict` | UDP `30002` занят или ownership не доказан |
| `interface_conflict` | `awg3` или `amn2sp3br0` уже существует |
| `vpn_cidr_overlap` | `10.212.13.0/24` пересекается с address/route/runtime |
| `container_cidr_overlap` | `172.29.252.0/28` пересекается с Docker/network/route |
| `container_name_conflict` | `amn2-spain-awg3` существует |
| `service_name_conflict` | `amn2-spain-awg3.service` существует или masked/aliased |
| `state_path_conflict` | candidate root/config path существует или ownership неоднозначен |
| `runtime_capability_unavailable` | Docker/systemd observation неполна |
| `awg2_equality_mismatch` | любой accepted AWG2 invariant отличается |
| `foreign_equality_mismatch` | count/hash/changed/equal не совпадает |
| `observation_ambiguous` | команда, parser или permission не дают точного результата |
| `artifact_checksum_mismatch` | любой локальный artifact не равен manifest |
| `outcome_replay` | claim/outcome уже существует или срок истёк |
| `schema_validation_failed` | evidence не соответствует exact schema |
| `secret_pattern_detected` | output содержит запрещённый secret-bearing pattern |

Любой conflict создаёт `decision=stop`. Списки предупреждений, допускающих
продолжение, не используются.

## 9. Граница команд только для чтения

Collector может использовать только заранее перечисленные read-only families:

- OS/kernel/capacity observation;
- `systemctl show` и `systemctl list-units` без action verbs;
- `ss` для listening sockets;
- `ip -json address|route|link`;
- read-only Docker info/list/inspect;
- read-only nftables ruleset listing;
- existence/type/owner/mode/hash observation через `test`, `stat`, `readlink`,
  `sha256sum` и bounded file inventory;
- sanitized AWG2 state projection без config bodies, private keys, PSK,
  endpoints или raw peer identifiers.

Запрещены `systemctl start|stop|restart|reload|enable|disable`, `docker run`,
`docker create`, `docker start|stop|restart|rm`, `ip add|del|replace`, `nft add|delete|flush`,
`wg|awg set`, shell redirection, upload на remote filesystem, package manager,
reboot и любые wildcard operations.

## 10. Контракт результата и транспорта

1. Runner проверяет local manifest и все SHA-256.
2. Runner create-new создаёт protected local claim.
3. Claim связывает exact `outcome_id`, manifest hash и target role.
4. Один checksum-verified collector передаётся в stdin удалённому shell; remote
   filesystem не используется.
5. Runner принимает один bounded JSON document либо bounded sanitized transport
   failure.
6. Raw stdout/stderr остаются только в памяти процесса и не включаются в
   evidence.
7. Schema, cross-field equality и secret scan выполняются до local evidence
   write.
8. Evidence создаётся локально через create-new/no-replace и получает SHA-256.
9. Claim остаётся consumed при success и failure; повтор запрещён.

Transport timeout, лишние bytes, CRLF corruption, non-JSON output, duplicate
document или неизвестный exit code считаются stop, а не partial success.

## 11. Коды завершения

| Exit | Значение |
|---|---|
| `0` | validated pass evidence создан локально |
| `64` | invalid invocation или manifest |
| `65` | artifact checksum mismatch |
| `66` | outcome replay/expired/claim conflict |
| `67` | transport failure или timeout |
| `68` | evidence schema/canonicalization failure |
| `69` | foreign equality mismatch |
| `70` | AWG2 equality mismatch |
| `71` | candidate resource conflict |
| `72` | observation ambiguous/unavailable |
| `73` | runtime capability unavailable |
| `74` | secret-pattern rejection |
| `75` | protected local evidence write/ACL failure |

Неизвестный exit code нормализуется в `67` с safe subreason
`unknown_remote_outcome`.

## 12. Перечень локальных TDD-проверок для следующего плана

Отдельный TDD plan после review этой spec должен покрыть:

- canonical manifest и strict schema;
- exact candidate values и запрет автоматической замены;
- immutable Phase 12 foundation checksum;
- every conflict category;
- AWG2/foreign equality positive и negative fixtures;
- empty port/process sets как валидное наблюдение;
- permission/parser/partial-output ambiguity как stop;
- CRLF, BOM, extra bytes и duplicate JSON rejection;
- outcome replay, expiry и create-new/no-replace;
- secret-pattern rejection и отсутствие raw persistence;
- командный allowlist и запрет всех mutation verbs;
- один success document либо один sanitized failure document;
- unchanged AMN2 source worktree и отсутствие package/runtime artifacts.

Известный correctness follow-up в `ProtocolAdmissionService` должен получить
отдельный local-only TDD slice до любого будущего package build, deploy или
AWG3 issuance: более новое `FAILED|SUPERSEDED` evidence обязано блокировать
старое `PASSED`.

## 13. Критерии завершения проектного этапа

Проектный этап завершён только когда:

- spec утверждена оператором;
- placeholder/ambiguity/scope self-review пройден;
- отдельный TDD implementation plan записан только после review spec;
- status и secret-free receipt синхронизированы;
- commit/push/origin equality подтверждены;
- implementation, package build и SSH не выполнялись.

Следующее разрешение после TDD должно быть checksum-bound и разрешать только
локальную реализацию wrapper/schema/tests. Отдельное SSH approval формируется
лишь после готовых hashes и не может быть объединено с deploy approval.

## 14. Граница отключения и перепрофилирования USA

Этот preflight не является evidence готовности отключения USA. Даже `pass` не
изменяет `live_action_authorized=false`. USA остаётся rollback contour до
полного отдельного readiness gate и exact live approval.
