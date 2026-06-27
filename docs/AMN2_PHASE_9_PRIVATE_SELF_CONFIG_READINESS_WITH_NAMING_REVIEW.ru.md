# AMN2 Phase 9 private self-config readiness with naming review

Дата: 2026-06-27.
Модель решения: `ChatGPT 5.5`.
Статус: `completed-docs-only-review`.

Этот review использует Phase 8 final closeout, Phase 9 entry brief, Phase 9 task
matrix refresh, new-chat handoff и уже подготовленные Phase 9 docs/commits как
existing material.

Live/VPS/SSH/config/Telegram/public execution gate этим review не открывался.
Config generation/delivery не выполнялись. Peer/config не создавались. VPS,
auth, firewall, users, keys и ports не менялись. Public launch, public
self-service delivery и production rollout не разрешались. Secrets, keys,
tokens, client payloads и raw logs не выводились.

## Decision

```text
review_name=AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW
review_status=passed
selected_first_track=PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING
phase8_status=accepted-closed-launch-ready-with-explicit-limitations
phase9_prepared_material_status=accepted-existing-material
public_launch_go=false
public_self_service_go=false
config_for_everyone_go=false
private_self_config_execution_go=false
peer_creation_go=false
android_display_name_execution_go=false
future_exact_gate_required_for_real_config_or_import=true
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Итог: первым Phase 9 треком считается closed private/self/operator config
readiness with naming. Это не public launch, не public self-service, не
массовая выдача config и не разрешение на создание нового peer/config сейчас.

## Track boundary

`PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING` означает подготовку безопасного
контракта для будущего закрытого self/operator path:

- один контролируемый private/self target за exact gate;
- operator-local или иной заранее выбранный private handoff channel;
- no public route, no public link, no self-service download;
- no Telegram live config send by default;
- no broad rollout;
- no secret-bearing evidence in docs, chat, GitHub or public logs.

Этот review разрешает только docs/review-only работу: risk model, naming
contract, pass/fail criteria, stop-lines и подготовку будущих checklists.

## Naming contract

`Neobyatnaya-AMNZ-N` является canonical config/device/file naming policy, а не
примером и не временным обходом.

```text
canonical_config_device_name=Neobyatnaya-AMNZ-N
config_filename_policy=Neobyatnaya-AMNZ-N.conf
forbidden_generic_names=SERVER1,server1,third-party-android-device-N,android-device-N
generic_name_as_normal_result_allowed=false
windows_amneziawg_filename_based_display_name=true
android_display_name_manual_rename_fallback=true
ios_display_name_manual_rename_fallback_until_proven=true
```

Будущий private/self flow должен проверять три разных слоя:

- generated logical device/config name: `Neobyatnaya-AMNZ-N`;
- user-visible artifact filename: `Neobyatnaya-AMNZ-N.conf`;
- imported app profile/server display name: expected `Neobyatnaya-AMNZ-N` or a
  documented client limitation/fallback.

Если generated name или filename становятся generic, gate должен остановиться.

## SERVER1 display-name issue

Observed issue:

```text
app_display_name_issue=SERVER1_observed_after_import
issue_class=client-display-name-product-compatibility-gap
not_yet_classified_as_generation_bug=true
```

`SERVER1` / `Сервер 1` нельзя считать приемлемым финальным UX по умолчанию.
Ручное Android observation показало `Сервер 1`, то есть localized generic
client display-name. Это не доказывает ошибку AMN2 generator и не отменяет
canonical filename policy.

Текущая platform decision:

- Windows AmneziaWG standalone: где возможно, закладываем реализацию через
  filename/basename. Required artifact filename: `Neobyatnaya-AMNZ-N.conf`.
- Android Amnezia app: automatic display-name из `.conf` не подтвержден; оставляем
  documented limitation + fallback `manual rename`.
- iOS Amnezia app: automatic display-name из `.conf` не доказан; до отдельного
  iOS exact gate оставляем documented limitation + fallback `manual rename`.

Решение сейчас: не подменять проблему публичной выдачей или новым delivery
flow. Сначала нужен controlled Android AmneziaWG profile-name acceptance gate.

## Future exact gate

Для реальной проверки Android display name нужен отдельный exact named gate:

```text
future_gate=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
execution_approved_now=false
```

Такой gate должен быть минимальным и closed/private. Он может быть открыт только
после отдельного operator confirmation и должен явно назвать target, handoff
channel, cleanup/rollback expectation, pass/fail criteria и redaction rules.

Allowed только внутри будущего exact gate:

- проверить canonical generated name and filename by safe metadata;
- выполнить exactly scoped private/operator import observation;
- зафиксировать только safe result: display name matched / still generic /
  manual rename needed / import failed;
- не публиковать secret-bearing artifacts or raw payloads.

Forbidden без такого gate:

- создавать peer/config;
- генерировать или доставлять real config;
- запускать Telegram live config send;
- открывать public/self-service route;
- менять VPS/auth/firewall/users/keys/ports;
- выполнять package apply/restart/reboot/restore/import/provider action;
- выводить client payload, QR, import URI, keys, PSK, token/password или raw
  logs.

## Risk model

Assets:

- client config secret material;
- real peer/server state;
- operator private handoff channel;
- user device identity and device-to-config mapping;
- public trust boundary around docs/GitHub/chat evidence;
- product UX correctness for profile naming.

Primary risks:

- generic `SERVER1` causes wrong-profile selection, support confusion or stale
  config reuse;
- config/device/file naming drift creates mismatch between AMN2 records,
  handoff artifact and imported app state;
- a private/self readiness step accidentally becomes public or self-service;
- review evidence leaks secret-bearing payloads;
- fixing display-name by changing generator/template without compatibility
  proof breaks import or existing AWG compatibility;
- live peer/config creation happens before exact gate and target selection.

Controls:

- keep public launch and self-service closed;
- keep real config generation/import behind exact named gate;
- require canonical naming at generated metadata and filename layers;
- treat Android display-name as separate client compatibility acceptance;
- allow manual rename only as documented fallback, not silent success;
- use safe summaries only.

## Pass criteria for Phase 9 readiness decision

Docs/review layer passes when:

```text
phase8_closed_status_accepted=true
phase9_existing_material_accepted=true
first_track_private_self_config_with_naming=true
public_launch_go=false
public_self_service_go=false
canonical_naming_policy_fixed=true
server1_issue_classified_as_display_name_gap=true
android_display_name_future_exact_gate_required=true
payload_output_allowed=false
```

Future execution/import gate can pass only if it records safe evidence that:

- generated name is `Neobyatnaya-AMNZ-N`;
- filename is `Neobyatnaya-AMNZ-N.conf`;
- Windows AmneziaWG receives filename-based naming where applicable;
- imported Android/iOS Amnezia display name is either `Neobyatnaya-AMNZ-N` or a
  documented limitation with explicit manual rename fallback;
- connectivity/import acceptance, if tested, does not require publishing
  secret-bearing artifacts;
- no public/self-service route was used or created.

## Fail / stop criteria

Stop and mark blocked if:

- any step requires public launch, public route or self-service download;
- any step requires creating peer/config without exact named gate;
- generated name or filename uses a generic value;
- app still displays `SERVER1` and no documented fallback/acceptance decision is
  chosen;
- evidence would expose client payload, QR, import URI, keys, PSK,
  token/password or raw logs;
- Android import behavior requires template/metadata changes without local or
  exact-gated compatibility proof;
- target/user/device/handoff channel is ambiguous.

## Model split

`ChatGPT 5.5` owns:

- risk decision;
- exact gate review;
- naming/product compatibility decision;
- pass/fail/rollback/stop-line model;
- decision whether `SERVER1` is acceptable only as documented limitation.

`ChatGPT 5.3-Spark` may do after this review:

- docs-only sync;
- runbook/checklist update;
- task matrix and next-chat refresh;
- safe secret-pollution scan;
- diff check, commit and push for docs-only changes.

`ChatGPT 5.3-Spark` should not open execution gates, decide public launch,
approve config generation/delivery or classify `SERVER1` as acceptable without
the 5.5 decision above.

## Next safe actions

```text
recommended_next_for_5_3_spark=AMN2_PHASE_9_NAMING_DOCS_SYNC
recommended_docs_sync_targets=task_matrix,next_chat,project_status_if_needed
required_pre_commit_scan=SECRET_POLLUTION_SCAN
execution_go=false
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

If operator later wants real Android display-name validation, use a new exact
gate request for `ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE`.
