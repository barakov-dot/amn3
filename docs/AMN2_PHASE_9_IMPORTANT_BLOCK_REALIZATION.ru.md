# AMN2 Phase 9 important block realization

Дата: 2026-06-27.
Модель выполнения: `GPT-5`.
Тип задачи: `Codex-Spark-safe docs-only`.
Статус: `completed-docs-only`.

Этот документ реализует важный блок Phase 9 без открытия live/VPS/SSH/DB/config/
Telegram/public gates:

- `AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW`;
- `AMN2_DB_AGGREGATE_COUNTS_REVIEW`;
- `AMN2_IOS_ACCEPTANCE_DECISION_REVIEW`.

## Итоговое решение

```text
gate_name=AMN2_PHASE_9_IMPORTANT_BLOCK_REALIZATION
selected_phase9_lane=HARDENING_PRODUCTIZATION
realization_status=completed-docs-only
ssh_auth_noise_execution_approved=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
next_live_or_mutating_step_requires_exact_named_gate=true
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Что именно реализовано

### 1. SSH auth-noise

Решение:

```text
ssh_auth_noise_observed=true
ssh_auth_hardening_execution_approved=false
ssh_auth_hardening_current_lane_blocker=false
current_safe_policy=key-based-short-ssh-no-long-manual-windows
future_gate_review=AMN2_SSH_AUTH_HARDENING_GATE_REVIEW
future_execution_gate=AMN2_SSH_AUTH_HARDENING_GATE
```

Реализованный practical rule:

- используем key-based SSH path;
- избегаем long SSH manual windows;
- не повторяем один и тот же failed helper 10-20 раз;
- при transport failure фиксируем blocker и переходим на другой helper shape;
- не меняем `sshd`, firewall, users, keys, root login, password auth, SSH port
  или rate limiting без отдельного rollback/provider-console boundary.

### 2. DB aggregate counts

Решение:

```text
db_runtime_path_classification=resolved-for-path-existence
db_aggregate_counts_required_for_current_lane=false
db_aggregate_counts_status=optional-confidence-not-hardening-blocker
db_live_observation_approved=false
future_gate_review=AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE_REVIEW
future_execution_gate=AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE
```

Реализованный practical rule:

- не делаем новый ad-hoc SQL/SSH quoting retry;
- если counts понадобятся, используем short key-based SSH + safe sqlite helper;
- выводим только `table_exists` и aggregate `count`;
- не выводим rows, payload, DB copy/download или secret-bearing values.

### 3. iOS DefaultVPN acceptance

Решение:

```text
ios_acceptance_required_for_current_lane=false
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ios_release_acceptance_status=deferred-not-hardening-blocker
ios_release_claim_allowed=false
ios_config_delivery_claim_allowed=false
future_gate_review=AMN2_IOS_ACCEPTANCE_GATE_REVIEW
future_execution_gate=AMN2_IOS_ACCEPTANCE_GATE
```

Реализованный practical rule:

- iOS DefaultVPN не считаем рабочим/release-ready path;
- не заявляем iOS support или production readiness;
- не создаём iOS peer/config и не доставляем config без future exact gate;
- если iOS снова открывается, сначала выбираем конкретный client path, потом
  one fresh per-device config, private handoff, import/connect/traffic и
  server-side observation при возможности.

## Порядок, если оператор захочет выполнять live часть

Выполнять только по одному направлению за раз.

1. SSH hardening:
   - сначала `AMN2_SSH_AUTH_HARDENING_GATE_REVIEW`;
   - затем, при отдельном подтверждении, `AMN2_SSH_AUTH_HARDENING_GATE`;
   - обязательны rollback/provider-console boundary и key-based login proof.

2. DB aggregate counts:
   - сначала `AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE_REVIEW`;
   - затем `AMN2_DB_AGGREGATE_COUNTS_OBSERVATION_GATE`;
   - только read-only counts, без row dump и DB copy/download.

3. iOS acceptance:
   - сначала `AMN2_IOS_ACCEPTANCE_GATE_REVIEW`;
   - затем `AMN2_IOS_ACCEPTANCE_GATE`;
   - только private per-device handoff, no payload output.

## Stop-lines

До отдельного exact named gate нельзя:

- менять `sshd_config`, firewall/provider rules, users, keys, root login,
  password auth, SSH port или rate limiting;
- запускать service start/restart/stop;
- выполнять live DB observation, row dump или DB copy/download;
- создавать peer/config или доставлять config;
- заявлять iOS как working/release-ready path;
- открывать public exposure;
- запускать Telegram polling/live send/config delivery;
- выполнять restore/import/reboot/provider rebuild/production rollout;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password или другой
  secret/payload.

## Phase 9 status after this realization

```text
important_block_realization_status=completed-docs-only
ssh_auth_noise_blocker=false
db_aggregate_counts_blocker=false
ios_acceptance_blocker=false
hardening_lane_can_continue=true
next_default_action=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
