# PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_REVIEW

Дата: 2026-06-26.

Статус: `completed-docs-only`.

Использованы существующие Phase 8 evidence, SSH auth-noise mitigation review и
provider-console diagnostic review.

Live/VPS/SSH/config/Telegram/public gates этим review не открывались.

## Review verdict

```text
review_go=true
execution_gate_go=conditional-go-after-provider-console-or-current-password-access-is-available
target_vps=89.185.80.166
expected_amn2_head_if_checked=187949bffb927a0a6d6c1f260fc0bb9ebb972447
recommended_gate=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE
disable_password_auth_go=false
disable_root_login_go=false
move_ssh_port_go=false
firewall_allowlist_go=false
telegram_operation_retry_go=false
```

Цель будущего gate - подготовить и доказать key-based access как дополнительный
безопасный путь, не ломая текущий password access. Это prep, а не hardening.

## Boundary

Разрешаемая идея будущего gate:

- сгенерировать/выбрать operator public SSH key локально;
- добавить ровно один public key для root/operator login, если operator явно
  подтвердит;
- проверить login по key;
- оставить password auth/root password path неизменным;
- не менять port/firewall/sshd hardening settings;
- записать rollback/console fallback.

Этот review не разрешает live action сам по себе.

## Private inputs readiness

Для будущего execution gate нужны приватно:

```text
provider_console_or_current_ssh_password_available=true_required
operator_public_ssh_key_available=true_required
operator_private_key_stays_private=true_required
key_comment_safe_label=amn2-private-rc-operator
rollback_boundary_defined=true_required
```

Не вставлять в чат:

- private key;
- password;
- token;
- `.conf`;
- QR/vpn payload;
- raw authorized_keys with unrelated keys.

## Allowed actions for future execution gate

Только после explicit gate:

- local public key fingerprint observation;
- one controlled SSH/password or provider-console access path to append one
  operator public key;
- permissions check for `.ssh` and `authorized_keys`;
- key-based login test;
- read-only AMN2 source marker check after key login;
- final proof that password auth/root login settings were not changed;
- safe evidence only.

## Forbidden actions

Запрещено:

- disable password auth;
- disable root login;
- move SSH port;
- add firewall allowlist;
- install/configure fail2ban/rate limiting;
- remove existing authorized keys;
- print private key or full unrelated authorized_keys contents;
- reboot/rebuild/restore/import;
- package upload/apply;
- service restart/stop;
- public exposure;
- Telegram polling/live send;
- config generation/delivery;
- peer creation.

## Pass criteria

```text
operator_public_key_fingerprint_recorded=true
authorized_keys_append_count=1
private_key_output_performed=false
password_auth_setting_changed=false
root_login_setting_changed=false
ssh_port_changed=false
firewall_changed=false
key_login_test_status=passed
amn2_source_marker_match=yes
public_exposure_performed=false
secret_values_printed=false
```

## Fail criteria / stop-lines

Stop immediately if:

- provider-console/current SSH access is unavailable;
- operator public key is missing or ambiguous;
- helper would print private key/password;
- existing `authorized_keys` would be overwritten;
- key login test fails;
- any step proposes disabling password auth/root login before key path is
  proven;
- SSH/firewall/port/rate-limit hardening is bundled into the prep gate.

## Exact copy/paste execution gate command

```text
PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE

Открыть exact gate для подготовки key-based SSH access без hardening.

Использовать существующие Phase 8 evidence:
- PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW;
- PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_REVIEW;
- PRIVATE_RC_TELEGRAM_OPERATION_SINGLE_SESSION_RESULT.

Target VPS: 89.185.80.166.
Expected AMN2 runtime/source head if checked:
187949bffb927a0a6d6c1f260fc0bb9ebb972447.

Private inputs:
- provider console or current SSH password available privately;
- operator public SSH key available;
- private key/password must not be pasted into chat or evidence.

Allowed:
- observe local public key fingerprint;
- append exactly one operator public key to the intended authorized_keys file;
- preserve existing authorized_keys entries;
- verify permissions for .ssh and authorized_keys;
- test key-based login;
- read-only AMN2 source marker check after key login if SSH works;
- verify password/root/port/firewall settings were not changed;
- safe evidence only.

Forbidden:
- disable password auth;
- disable root login;
- change SSH port;
- change firewall/listener/TLS/proxy;
- install/configure rate limiting or fail2ban;
- remove existing keys;
- print private key/password/token or full unrelated authorized_keys;
- reboot/restore/import/provider rebuild;
- package upload/apply;
- service start/restart/stop;
- public exposure;
- Telegram polling/live send;
- config generation/delivery;
- peer creation.

Stop at first failed gate and report exact blocker.
```

## Recommendation

```text
recommended_next_after_provider_console=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE
auth_hardening_gate_go=false_until_key_login_passed
telegram_operation_retry_go=false_until_transport_access_path_stable
```
