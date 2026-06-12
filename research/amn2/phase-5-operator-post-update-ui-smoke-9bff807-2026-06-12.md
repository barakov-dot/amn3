# Phase 5 P5-O001 operator-only post-update UI smoke for AMN2 9bff807

Дата: 2026-06-12.

Статус: `needs-fix`.

## Scope

Named gate: `P5-O001 Operator-only post-update UI smoke for AMN2 9bff807`.

Цель: проверить, что web/admin после `P5-C007` открывается через operator-only SSH local port forward and that the authenticated read-only navigation surface remains usable without crossing write/config/public/destructive stop lines.

Source of truth:

```text
AMN3 before slice: 49b9e27 Record AMN2 9bff807 live smoke
AMN2 selected head: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
AMN2 selected head title: Add local bot media and status summaries
latest VPS-smoked source: 9bff807a1d8fcceb833c1ef864064d2af6aaaff1
latest VPS smoke evidence: research/amn2/phase-5-live-update-smoke-9bff807-2026-06-12.md
web/admin access path: operator SSH local port forward to target loopback web/admin
web/admin bind expected: 127.0.0.1:3030
local tunnel endpoint used by Codex: 127.0.0.1:13030
VPS_APPLY_ENABLED default: false from P5-C007 evidence
public exposure decision: unchanged from P5-C007 evidence
secret publication policy reviewed: yes
```

## Commands And Boundaries

Performed:

- opened an SSH local port forward from the operator workstation to the target loopback web/admin;
- performed a short read-only SSH connectivity check after an initial timeout;
- performed local GET/HEAD checks against `127.0.0.1:13030/login`;
- used the in-app browser after the operator manually entered web/admin credentials;
- navigated only through existing GET links in the authenticated web/admin.

Not performed:

- no package apply or rebuild on the VPS;
- no service restart, deploy, enable, disable or config reload;
- no public listener, firewall, reverse proxy, DNS, Caddy or HTTPS change;
- no write API, `/api/clients` CRUD or Local Agent mutation;
- no config delivery, `.conf`, QR, `vpn://` delivery, export or download;
- no production peer/user mutation;
- no backup/import/reboot;
- no Telegram token use, live bot send or Telegram profile mutation;
- no secret-bearing evidence publication.

## Tunnel And Login

Initial SSH local-forward attempt did not produce a local listener. A direct read-only SSH check then briefly timed out on port 22. A retry succeeded and the tunnel was reopened successfully.

Safe result:

```text
ssh_transport: intermittent timeout observed, recovered with retry
tunnel_status: opened
local_login_get: 200
login_page_title: Вход | Amneziya Admin
operator_manual_login: yes
codex_received_or_published_password: no
```

The tunnel later dropped once while the operator was at the login page; it was reopened and `/login` again returned HTTP 200. This matches the intermittent SSH transport behavior already recorded in `P5-C007`.

## Route Smoke

Routes loaded through authenticated browser GET navigation:

```text
/login: loaded before auth, login form visible
/: loaded after auth, dashboard visible
/users: loaded, user table visible
/servers: loaded, server table visible
/orders: loaded, orders table visible
/logs: loaded, log source/recent-lines view visible
/settings: loaded, settings sections visible
/config-templates: loaded, config template sections visible
/api-readiness: loaded, read-only API readiness sections visible
/integration-status: loaded, operator-only boundary sections visible
/api-tokens: loaded, token page visible
/devices/disabled: loaded, disabled devices page visible
```

Safe route observations:

```text
overview_loaded: yes
users_loaded: yes
servers_loaded: yes
orders_loaded: yes
logs_loaded: yes
settings_loaded: yes
config_templates_loaded: yes
api_readiness_loaded: yes
integration_status_loaded: yes
api_tokens_loaded: yes
disabled_devices_loaded: yes
secret_payloads_visible_in_evidence: no
raw IDs/IPs/names/session cookies published: no
```

## Findings

`P5-O001` did not cross a stop line, but it should not be recorded as a clean `pass`.

Finding 1: several authenticated web/admin pages expose write/create controls during an operator-only smoke:

```text
/users: create/open affordances visible
/servers: create/open affordances visible
/api-tokens: issue-token affordance visible
/config-templates: save/reset-template controls visible
```

No such controls were clicked. The issue is that Phase 5 operator-only smoke expects dangerous actions to be disabled, gated or clearly explained. Current visibility makes the UI depend on operator discipline rather than an explicit in-product gate.

Finding 2: `/config-templates` intentionally contains secret-bearing delivery vocabulary such as config templates, QR/import-link concepts and private-key placeholders. No actual client config, QR, token, key, PSK, endpoint or `vpn://` payload was sampled or published, but the page should keep stronger visible wording that it is a gated/local template editor and not a live config-delivery route.

Finding 3: SSH tunnel stability remains a live-ops friction point. The UI itself recovered after reopening the tunnel, but operator instructions should continue to mention retry/wait behavior for transient SSH banner or connection timeouts.

Finding 4: the authenticated web/admin UI is still visibly mixed-language. During the smoke, navigation and section titles included English labels such as `Servers`, `API`, `Integration`, `About`, `Tokens`, `Orders`, `Disabled devices`, `Users`, `Application logs`, `Settings`, `Runtime`, `Build status` and related table labels. `P5-O002` should include Russian-first menu/section/copy cleanup while preserving stable technical route IDs.

Finding 5: the displayed product/resource identity should be adjusted. The operator preference is to name the resource `AmneziyaDA` and show the user/person identity below it, rather than making the user name look like the primary resource label. This should be handled as local web/admin UX copy/layout work, not as a live server mutation.

Finding 6: dashboard summary cards need layout polish. The operator preference is to center card contents both horizontally and vertically, with the first line as the numeric count and the second line as the entity label, for example `1` then `пользователь`, `1` then `сервер`, `0` then `заявок`, `1` then `устройство`. This is local template/CSS/copy work for `P5-O002`.

## Decision

```text
web_admin_loopback_status: loaded-through-operator-tunnel
bot_dry_local_status: not_checked in this slice
read_only_api_status: from_existing_evidence P5-C007 pass
no_public_exposure_status: from_existing_evidence P5-C007 pass
VPS_APPLY_ENABLED_false: from_existing_evidence P5-C007 explicit false
write_actions_called: no
config_delivery_performed: no
live_vps_commands_by_codex: yes, limited to named-gate SSH connectivity/tunnel only
ssh_commands_by_codex: yes, named-gate read-only connectivity/tunnel only
package_apply_or_rebuild: no
service_restart_or_deploy: no
public_exposure_changed: no
secrets_published: no
blocked_or_unclear_items: authenticated UI still exposes write/create controls and mixed-language/resource-label/dashboard-card UX that need a local-only gated-action/copy cleanup
decision: needs-fix
```

## Next Recommendation

`P5-O002 Web-admin gated-action and Russian-first UX cleanup`: local-only AMN2 implementation/test slice to make create/write/config/token controls visibly gated, disabled or explicitly named-gate-only in operator-only mode, translate visible menu/section/table copy Russian-first, adjust resource/user display so `AmneziyaDA` is the resource name with the user shown below it, and polish dashboard summary cards so their number and label are centered in a two-line layout. This should not run live VPS commands, package apply, service restart, public exposure, config delivery, write API, Local Agent mutation, backup/import/reboot or production peer/user mutation. After it lands locally, rebuild and smoke are separate gates.
