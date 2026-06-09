# AMN2 Web Panel Read-Only UX Review Checklist

Дата: 2026-06-09.

Назначение: провести безопасный UX/product review текущей приватной web/admin панели AMN2 после Phase 3 service-mode evidence, без write-действий, без public exposure и без переноса PRVTPRO/Web Panel assumptions.

## Текущая Граница

```text
access_path: external browser over SSH local port forward
remote_web_bind: 127.0.0.1:3030
public_domain: none planned
https_reverse_proxy_public_cutover: no
public_api_3040: absent/closed
tcp_80_443: absent
VPS_APPLY_ENABLED: false
service_mode: web/bot active, loopback-only
validated_so_far: unauth redirects, authenticated overview GET navigation
not_validated: destructive/admin write actions
```

Codex/browser preview не является access path. Панель открывать только в обычном внешнем браузере через SSH tunnel.

## Stop Lines

Во время UX review не выполнять:

- POST/submit/save/reset actions;
- issue/revoke API token;
- sync/health/run operation buttons;
- create/update/delete user, device, peer, server or setting;
- config delivery, `.conf`, QR, `vpn://`, import/export/download;
- backup/import/reboot;
- Local Agent mutation;
- public API `3040` or direct public web/admin `3030`;
- Caddy/nginx/HTTPS reverse proxy setup;
- production peer/user mutation.

Если страница содержит только кнопку, которая выглядит read-only, но непонятно, делает ли она write, не нажимать. Записать как UX ambiguity.

## Preconditions

Перед review должны оставаться верными:

```text
amneziya-web: active/enabled
amneziya-bot: active/enabled
/login over loopback: 200
tcp_3030: present-loopback only
tcp_3040: absent
tcp_80_443: absent
VPS_APPLY_ENABLED: false
operator_access: SSH local port forward
```

## Pages To Review

Разрешены только GET-навигация и визуальный осмотр:

```text
/login
/
/users
/servers
/orders
/logs
/settings
/config-templates
/api-readiness
/integration-status
/api-tokens
/devices/disabled
```

Если новый маршрут найден через меню, открыть его только если это очевидная overview/status page. Если маршрут похож на action, wizard, config delivery or destructive tool, не открывать без отдельного решения.

## What To Observe

Для каждой страницы записать:

```text
route:
loaded: yes/no
auth_state: unauth-redirect | authenticated-200
primary_purpose_clear: yes/no/unclear
empty_state_clear: yes/no/not-applicable
status_labels_clear: yes/no/not-applicable
dangerous_actions_visible: yes/no
dangerous_actions_gated_or_explained: yes/no/not-applicable
secret_artifacts_visible: no | unclear | yes-stop
copy_problem:
layout_problem:
candidate_improvement:
risk_class: read-only-ux | needs-design | blocked-write-gate
```

Не публиковать screenshots, если на них есть токены, endpoint values, peer public keys, configs, QR, backup names with sensitive context, Telegram IDs, session cookies or private URLs. Если нужен screenshot, сначала отдельно решить redaction.

## PRVTPRO Review Lens

PRVTPRO/Amnezia-Web-Panel использовать только как UX/product reference:

- понятность dashboard/status overview;
- группировка разделов и route taxonomy;
- warning/copy около config artifacts;
- role/admin/user wording;
- API token lifecycle copy;
- empty/error states;
- separation between read-only status and dangerous operations;
- visibility of backup/import/reboot risks without enabling them.

Не переносить из PRVTPRO как assumptions:

- public panel exposure;
- HTTPS domain access;
- direct server management from panel;
- backup/import/reboot availability;
- raw config delivery;
- destructive operations;
- GPL code, UI templates, scripts or manager flows.

## Safe Evidence To Return

Вернуть только текстовую сводку:

```text
review_status:
access_path: ssh-local-port-forward
browser: external
routes_reviewed:
unauth_redirects_ok:
authenticated_overview_ok:
write_actions_called: no
config_delivery_requested: no
api_3040_opened: no
public_3030_opened: no
secrets_published: no
top_read_only_ux_findings:
blocked_by_write_gate:
next_recommended_slice:
```

## Decision Rules

`read-only-ux` findings можно переносить в AMN2 planning только если они не требуют POST/write/config/token/sync actions.

`needs-design` findings требуют отдельного design note.

`blocked-write-gate` findings нельзя реализовывать или проверять в service-mode panel без нового explicit gate.
