# AMN2 Web Panel Read-Only UX Review Evidence Template

Дата: 2026-06-09.

Назначение: безопасно вернуть результат UX/product review приватной AMN2 web/admin панели после прохода по `docs/AMN2_WEB_PANEL_READ_ONLY_UX_REVIEW_CHECKLIST.ru.md`.

Этот шаблон не разрешает POST/write/config/token/sync/backup/reboot действия и не требует скриншотов.

## Safe Summary

```text
review_status:
review_date:
access_path: ssh-local-port-forward
browser: external
panel_url_local:
service_mode: loopback-web-bot
amneziya_web_status:
amneziya_bot_status:
login_loopback_http:
tcp_3030:
tcp_3040:
tcp_80_443:
VPS_APPLY_ENABLED:
routes_reviewed:
unauth_redirects_ok:
authenticated_overview_ok:
write_actions_called: no
config_delivery_requested: no
api_token_issue_revoke_called: no
sync_or_health_actions_called: no
backup_import_reboot_called: no
api_3040_opened: no
public_3030_opened: no
secrets_published: no
screenshots_published: no
```

`panel_url_local` можно указать как `127.0.0.1:3030` или альтернативный локальный tunnel-порт. Не указывать публичный IP, домен, SSH details или provider URL.

## Route Notes

Заполнять только по GET/визуальному осмотру. Если маршрут не открывался, поставить `not-reviewed`.

```text
/login:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/users:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/servers:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/orders:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/logs:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/settings:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/config-templates:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/api-readiness:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/integration-status:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/api-tokens:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:

/devices/disabled:
  loaded:
  auth_state:
  primary_purpose_clear:
  empty_state_clear:
  status_labels_clear:
  dangerous_actions_visible:
  dangerous_actions_gated_or_explained:
  secret_artifacts_visible:
  copy_problem:
  layout_problem:
  candidate_improvement:
  risk_class:
```

## Findings

```text
top_read_only_ux_findings:
  1.
  2.
  3.

blocked_by_write_gate:
  1.
  2.
  3.

needs_design:
  1.
  2.
  3.

safe_quick_wins:
  1.
  2.
  3.

next_recommended_slice:
```

## Secret Hygiene

Подтвердить:

```text
no_env_published: yes
no_servers_yml_published: yes
no_raw_tokens_published: yes
no_authorization_headers_published: yes
no_token_hashes_published: yes
no_private_keys_or_psk_published: yes
no_conf_qr_vpn_links_published: yes
no_session_cookie_published: yes
no_full_logs_published: yes
```

## Decision

```text
decision:
read_only_ux_review_gate:
approved_for_local_docs_planning:
requires_amn2_code_change:
requires_new_explicit_gate:
```

Если `requires_new_explicit_gate=yes`, указать какой именно gate нужен: `write-action`, `config-delivery`, `api-token`, `sync-health`, `backup-import-reboot`, `public-exposure`, `production-peer-mutation` или другой.
