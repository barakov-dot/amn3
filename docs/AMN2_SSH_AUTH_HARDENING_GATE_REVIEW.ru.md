# AMN2 SSH auth hardening gate review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Статус: `completed-docs-only-review`.

Этот review использует существующие Phase 8 final closeout evidence, Phase 9
hardening docs gaps, Telegram no-long-SSH result, SSH server log diagnostic
result и key-based SSH prep result.

Live/VPS/SSH/Telegram/public execution gate этим review не открывался.
`sshd`, auth, firewall, users, keys и ports не менялись. Package
apply/upload, service restart, reboot, restore/import и provider action не
выполнялись. Secrets, keys, tokens, configs и raw logs не выводились.

## Decision

```text
gate_name=AMN2_SSH_AUTH_HARDENING_GATE_REVIEW
review_status=passed
execution_recommended_now=false
execution_gate_required_for_any_mutation=true
selected_current_policy=keep-key-based-no-long-ssh-operational-pattern
ssh_auth_noise_observed=true
ssh_auth_noise_is_current_blocker=false
public_exposure_status=closed-by-default
config_delivery_status=not-approved
peer_creation_status=not-approved
production_rollout_status=not-approved
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

Итог: SSH auth-noise mitigation полезен как future hardening, но сейчас не
нужен как немедленный execution. Текущий операционный blocker уже снят более
мягким способом: key-based SSH + no-long-SSH Telegram flow + короткие SSH
команды + remote watchdog + final no-polling guard.

## Цель SSH auth-noise mitigation

Цель не в том, чтобы "починить Telegram" или "ускорить AMN2". Доказанный
Telegram no-long-SSH flow уже прошел.

Цель будущего SSH auth hardening:

- снизить внешний brute-force/password-auth фон на SSH;
- уменьшить вероятность `exit 255`/connection close при сериях SSH-команд;
- снизить шум в `sshd`/auth logs;
- уменьшить риск случайной блокировки controlled gates из-за SSH pressure;
- подготовить более спокойный контур для будущих production/hardening gates.

## Что считаем шумом

Шумом считаем только безопасно агрегированные признаки из server-side
diagnostic evidence:

- множественные failed password attempts для `root`, `admin`, `test` и других
  пользователей;
- PAM authentication failures;
- `Connection closed ... [preauth]` и `Disconnected ... [preauth]`;
- высокий счетчик failed password / PAM / connection closed в коротком окне;
- повторяющиеся внешние попытки входа, не относящиеся к оператору.

Не считаем шумом:

- успешные operator root sessions;
- штатное закрытие сессии оператором;
- AMN2 runtime behavior;
- Telegram bot behavior;
- public web/API exposure;
- DB state.

Текущее evidence показывает heavy auth-noise, но не доказывает `MaxStartups`,
OOM, conntrack exhaustion, fatal sshd error или kernel kill.

## Что уже снижает риск без SSH hardening

Уже доказано:

```text
ssh_key_based_access_prep_gate_status=passed
key_login_test_status=passed
source_overlay_match=yes
telegram_no_long_ssh_retry_status=passed
ssh_session_open_during_manual_window=false
remote_watchdog_started=true
final_no_polling_guard_status=passed
public_closed_probes_before_status=passed
public_closed_probes_after_status=passed
```

Поэтому current safe policy остается:

- использовать key-based SSH;
- не держать долгую SSH-сессию во время manual Telegram window;
- использовать короткие SSH precheck/start/final-guard команды;
- останавливать gate после первого транспортного blocker;
- не повторять один и тот же SSH helper много раз.

## Допустимые изменения только после отдельного execution gate

Только после отдельного exact named execution gate, с rollback/provider-console
boundary, можно рассматривать:

- запрет root password login при сохранении proven root key login;
- отключение password authentication только после повторного key-login check;
- rate limiting / fail2ban-like policy;
- provider-side allowlist только при подтвержденном out-of-band recovery path;
- SSH port move только как отдельный risky gate, не в первом hardening gate;
- backup current sshd/auth/firewall state before mutation;
- final key-login, public-closed-probes и no-lockout guard после изменения.

Рекомендуемый будущий first execution scope, если оператор позже решит делать
hardening: самый маленький вариант, без port move и без firewall allowlist.

## Запрещено

Запрещено этим review и без нового exact gate:

- менять `sshd_config`;
- отключать password auth;
- отключать root login полностью;
- менять SSH port;
- менять firewall/provider security rules;
- удалять или перезаписывать `authorized_keys`;
- устанавливать/настраивать rate limiting или fail2ban;
- restart/stop/start `sshd` или другие сервисы;
- reboot/restore/import/provider rebuild;
- открывать public exposure;
- запускать Telegram polling/live send;
- генерировать или доставлять config;
- создавать peer/config;
- выводить secrets, keys, tokens, configs или raw logs.

## Risk / rollback model

Основной риск: lockout оператора из VPS.

Минимальные preconditions для будущего execution:

```text
provider_console_or_recovery_access_confirmed=true
key_based_root_login_confirmed=true
operator_public_key_fingerprint_recorded_safe=true
authorized_keys_preserve_existing_entries=true
sshd_config_backup_required=true
rollback_command_prepared=true
no_firewall_or_port_change_in_first_gate=true
operator_lockout_risk_accepted=true
```

Rollback model:

- перед изменением сохранить текущие SSH/auth settings;
- выполнять одну категорию изменения за gate;
- не менять port/firewall в том же gate, где меняется auth;
- после изменения открыть новую key-based session before closing the old
  recovery path;
- если key-login не проходит, откатить auth change immediately;
- provider console остается emergency recovery boundary.

## Pass criteria для будущего execution gate

Execution gate можно считать passed только если:

```text
key_based_login_before_change=passed
selected_mutation_exactly_one_category=true
authorized_keys_preserved=true
ssh_port_unchanged=true
firewall_unchanged=true
sshd_restart_or_reload_scope_explicit=true
key_based_login_after_change=passed
password_root_login_policy_observed_as_expected=true
public_closed_probes_after_status=passed
no_telegram_polling_started=true
no_config_delivery_performed=true
secret_values_printed=false
rollback_not_needed_or_rollback_verified=true
```

## Fail criteria

Execution gate должен остановиться и считаться failed/blocked если:

- key login не проходит до изменения;
- provider-console/recovery path не подтвержден;
- current `authorized_keys` нельзя сохранить безопасно;
- изменение требует одновременно auth + firewall/port;
- после изменения key login не проходит;
- public closed probes меняют статус не по плану;
- появляется необходимость restart/reboot вне заявленного scope;
- helper хочет вывести raw logs, keys, tokens или configs;
- SSH session получает `exit 255` до safe remote marker.

## Stop-lines

Stop immediately:

- нет recovery/provider console boundary;
- нет confirmed key-based login;
- требуется отключить root login полностью;
- требуется менять port/firewall в первом gate;
- требуется удалить существующие authorized keys;
- требуется public exposure;
- требуется package upload/apply или service rollout;
- требуется Telegram live send/polling;
- требуется config generation/delivery или peer creation;
- требуется reboot/restore/import/provider action;
- появляется secret-bearing output.

## Нужно ли execution сейчас

Нет. Execution сейчас лучше не делать.

Причина:

- Phase 8 private/operator RC уже закрыта с ограничениями;
- SSH auth-noise признан optional hardening, не blocker;
- key-based access already passed;
- Telegram no-long-SSH result already passed;
- current gates могут работать через short key-based SSH pattern;
- auth/firewall mutations дают реальный lockout risk.

Рекомендация:

```text
recommended_now=leave_as_future_hardening
next_execution_go=false
next_state=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```

## Exact command, если оператор все равно хочет execution позже

Если оператор позже решит принять lockout risk и открыть execution, использовать
отдельную команду:

```text
AMN2_SSH_AUTH_HARDENING_EXECUTION_GATE

Открыть exact gate для минимального SSH auth hardening execution.

Использовать AMN2_SSH_AUTH_HARDENING_GATE_REVIEW,
Phase 8 final closeout evidence, SSH server log diagnostic result,
key-based SSH prep result и Telegram no-long-SSH result.

Target VPS: 89.185.80.166.
Expected AMN2 head:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.
Operator public key fingerprint:
SHA256:cNrkGhxuCg3lHXlSC+73/qVhJQDJSbJAqBnpJcHlG8c.

Allowed:
- key-based SSH precheck;
- provider-console/recovery readiness confirmation;
- backup current SSH/auth settings;
- apply exactly one minimal SSH auth hardening change;
- preserve existing authorized_keys entries;
- no SSH port change;
- no firewall/provider security rule change;
- key-based login verification after change;
- public closed probes for 3030, 3040, 80, 443;
- safe evidence only.

Forbidden:
- disable root login completely;
- change SSH port;
- change firewall/provider security rules;
- remove or overwrite authorized_keys;
- package upload/apply;
- broad service restart;
- public exposure;
- Telegram live send/polling;
- config generation/delivery;
- peer creation;
- .conf/QR/vpn:// output;
- private key/PSK/token/password output;
- raw logs output;
- reboot/restore/import/provider action.

Stop at first failed gate and report exact blocker.
```

До такого explicit execution gate текущий статус остается:

```text
ssh_auth_hardening_execution_approved=false
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
