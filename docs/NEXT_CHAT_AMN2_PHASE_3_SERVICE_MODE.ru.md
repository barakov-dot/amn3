# NEXT CHAT: AMN2 Phase 3 Service Mode Gate

Дата: 2026-06-09.

Рабочая папка нового чата:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB
```

Назначение нового чата: продолжить Phase 3 для нового target VPS после уже закрытых bootstrap, AWG2 runtime, live disposable peer apply/revoke и manual web/bot readiness gates. Новый чат должен владеть следующим controlled production/service-mode решением: оставаться в manual mode или запускать отдельный gate для `systemd` + HTTPS reverse proxy.

Этот handoff не разрешает public API, public config delivery, production peer writes или service-mode без отдельного решения оператора.

## Current Update 2026-06-09

Phase 3A.1 phone live test peer gate, Phase 3A.2 test peers batch gate, Phase 3B.0 service-mode read-only precheck, Phase 3A critical manual-mode cleanup, Phase 3A protocol identity check and Phase 3A manual-runtime field test partial-pass were completed after this handoff was created. Four operator-approved test peers are intentionally left enabled for phone/desktop/test-zone validation.

```text
phone_live_test_peer_gate: passed
test_peers_batch_gate: passed
service_mode_read_only_precheck: passed
manual_mode_critical_cleanup: passed
protocol_identity_check: passed
manual_runtime_field_test: partial-pass
revoke_by_number_runbook: prepared-not-executed
revoke_by_number_3: passed
revoke_by_number_4: passed-unused-peer-removed
service_mode_B0_preflight: needs-fix-before-B1
service_mode_B0_1_prep: passed
service_mode_B0_repeat: ready-for-B1-loopback-systemd
service_mode_B1_loopback_systemd: passed-after-investigation
service_mode_B2_0_reverse_proxy_preflight: passed-ready-for-choice
service_mode_B2_1_reverse_proxy_readiness: blocked-dns-and-env-baseline
service_mode_no_domain_access_path: ssh-tunnel-selected
service_mode_ssh_tunnel_access: passed
service_mode_web_panel_tunnel_smoke: passed-read-only
service_mode_second_admin_telegram_id_add: passed
service_mode_authenticated_web_panel_smoke: passed-read-only
second_admin_bot_readonly_check: skipped-by-operator
phase3_final_safety_snapshot: passed-source-overlay-git-metadata-unknown
source_overlay_commit: f7f6131
peer_scope: two remaining operator-approved test peers
handshake_seen: yes
rx_nonzero: yes
tx_nonzero: yes
client_core_awg_fields_count: 11
server_core_awg_fields_count: 11
client_i_fields_count: 0
server_i_fields_count: 0
phone_connectivity_first_peer: passed
additional_test_peer_configs_downloaded: yes
named_peer_activity_sample:
  Neobyatnaya-AMNZ-1: traffic-seen
  Neobyatnaya-AMNZ-2: traffic-seen
  Neobyatnaya-AMNZ-3: not-found-on-server
  Neobyatnaya-AMNZ-4: not-found-on-server
connected_or_traffic_seen_count: 2
latest_post_revoke_4_sample:
  Neobyatnaya-AMNZ-1: not-yet
  Neobyatnaya-AMNZ-2: not-yet
  Neobyatnaya-AMNZ-3: not-found-on-server
  Neobyatnaya-AMNZ-4: not-found-on-server
protocol_identity_interpretation: UI/label ambiguity, not wrong plain-WireGuard export
test_peers_left_enabled: yes, except Neobyatnaya-AMNZ-3 and Neobyatnaya-AMNZ-4 revoked by explicit gates
live_peer_count_final: 2
delivery_artifacts_remaining: 0
monitoring_key_files_remaining: 12
tcp_3030_final: present-loopback
tcp_3040_final: absent
VPS_APPLY_ENABLED_final: false
service_mode: enabled-loopback
systemd_units_installed: yes
systemd_web_enabled: enabled
systemd_web_active: active
systemd_bot_enabled: enabled
systemd_bot_active: active
web_bind: 127.0.0.1:3030
web_login_http: 200
reverse_proxy_B2_1_blockers:
  dns_a_count: 0
  dns_aaaa_count: 0
  dns_matches_vps_route_v4: unknown
  VPS_APPLY_ENABLED_file_false: no
no_domain_access:
  public_https_cutover: deferred
  access_path: ssh-local-port-forward
  browser_path: external-browser-localhost
  operator_browser_opened: yes
  tunnel_access_control: passed
  web_panel_smoke: passed-read-only
  protected_get_routes_redirect_to_login: yes
  local_api_3040_connects: no
  authenticated_web_panel_smoke: passed-read-only
  authenticated_overview_pages_200: yes
final_safety_snapshot:
  live_peer_count: 3
  tcp_80: absent
  tcp_443: absent
  tcp_3030: present-loopback
  tcp_3040: absent
  VPS_APPLY_ENABLED_file_false: yes
  production_write_surfaces: not-opened
  config_delivery: not-opened
  reverse_proxy_public_https: not-enabled
telegram_admins:
  count_after_second_admin_add: 2
  raw_ids_recorded: no
  second_admin_bot_readonly_check: skipped-by-operator
reverse_proxy_stack:
  nginx_installed: no
  caddy_installed: no
  certbot_installed: no
  docker_proxy_candidates_count: 0
  tcp_80: absent
  tcp_443: absent
service_mode_B0_blockers:
  amneziya_user_exists: resolved-yes
  settings_web_admin_enabled: resolved-True
  admin_telegram_ids_present: resolved-yes
  reverse_proxy_choice: undecided
reverse_proxy_public_https_cutover: not-enabled
evidence:
  research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md
  research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md
  research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md
  research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md
  research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md
  research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md
  research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md
  research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md
  research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md
  research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md
runbook:
  docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md
  docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md
```

This update does not authorize service-mode `systemd`, HTTPS reverse proxy/public cutover, public API `3040`, direct public web/admin `3030`, production peer/user mutation beyond the four approved test peers, API `config:read`, `/api/clients` write CRUD, public/self-service config delivery, Local Agent write/config mutations, backup/import/reboot routes, or secret-bearing evidence publication.

## Текущая Точка Правды

AMN3 / lab repo:

```text
repo: C:\Users\SooL\Documents\VPS-OPS-LAB
remote: https://github.com/barakov-dot/amn3.git
branch: master
head before this handoff: 615efc7 Record target server manual web bot gate
```

Production repo:

```text
repo: C:\Users\SooL\Documents\Amneziya
remote: https://github.com/barakov-dot/amn2.git
branch: codex-vps-test-prep
current source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch
```

Current AMN3 package:

```text
dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282
source sha256: 720B6C9FE3CADDBC65C19BDEC5B0C811D00C94EB0D095D6311DCD90DD77BE4E1
status: read-only-vps-smoke-pass
```

## Что Уже Закрыто На Новом Target VPS

```text
bootstrap: partial-pass
AWG2 runtime: read-only-smoke-pass
live peer gate: verified-live for exactly one disposable test peer
manual web/bot gate: passed
phone live test peer gate: passed, one operator test peer left enabled
test peers batch gate: passed, three additional operator test peers left enabled
service-mode read-only precheck: passed
manual-mode critical cleanup: passed, delivery artifacts removed, monitoring keys retained
protocol identity check: passed, core AmneziaWG fields present in client and server metadata
manual-runtime field test: partial-pass, 3 of 4 test peers connected-with-traffic
revoke-by-number runbook: prepared
revoke-by-number Neobyatnaya-AMNZ-3: passed
service-mode B0 preflight: needs-fix-before-B1
service-mode B0.1 prep: passed
service-mode B0 repeat: ready-for-B1-loopback-systemd
service-mode B1 loopback systemd: passed-after-investigation
service-mode B2.0 reverse proxy preflight: passed-ready-for-choice
current source overlay: f7f6131
AWG2 container: running
current peer count: 2
delivery artifacts remaining: 0
latest numbered peer sample after revoke: Neobyatnaya-AMNZ-1/-2 traffic-seen; -3/-4 not-found-on-server
latest_post_revoke_4_snapshot: peer count 2, #1/#2 not-yet pending reconnect, #3/#4 not-found-on-server, 3030 loopback-only, 80/443/3040 absent
post_revoke_note: manual reconnect traffic was confirmed for 1/2 before #4 revoke; automatic reconnect remains unproven
direct public web 3030: closed
public API 3040: closed
service-mode systemd: enabled for web/bot loopback
service-mode B0 blockers resolved except reverse proxy undecided for HTTPS cutover
reverse proxy B2.1 readiness: blocked until DNS resolves to the target VPS and explicit `.env` `VPS_APPLY_ENABLED=false` is confirmed
reverse proxy/public HTTPS cutover: deferred because no domain is available, no proxy stack installed yet
no-domain service-mode access path: SSH local port forward to loopback web/admin, then external browser localhost
no-domain SSH tunnel access: passed, operator opened panel successfully; control confirmed web/bot active, /login 200, 3030 loopback, 3040 absent, VPS_APPLY_ENABLED=false
web-panel tunnel smoke: passed read-only; login 200, protected GET routes redirect to /login, local API 3040 not reachable, no POST/write/config delivery
second Telegram admin ID add: passed; configured admin count is 2, raw IDs not recorded, web readiness recovered to /login 200 after restart
second admin bot read-only check: skipped by operator to save time; not recorded as independently passed
authenticated web-panel smoke: passed read-only; overview GET pages returned 200 after login, no POST/write/config delivery
final safety snapshot: passed; peer count 3, #3 absent, #1/#2 traffic-seen, #4 not-yet, web/bot active, 3030 loopback, 80/443/3040 absent, VPS_APPLY_ENABLED=false
revoke-by-number #4: passed; unused peer removed, peer count 2, #3/#4 absent from latest numbered snapshot, web/bot active, 3030 loopback, 80/443/3040 absent, VPS_APPLY_ENABLED=false
VPS_APPLY_ENABLED: false/not-set outside narrow live gates
```

Evidence:

```text
research/amn2/target-server-bootstrap-evidence-2026-06-08.md
research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
research/amn2/target-server-phone-live-test-peer-evidence-2026-06-09.md
research/amn2/target-server-test-peers-batch-evidence-2026-06-09.md
research/amn2/target-server-service-mode-precheck-evidence-2026-06-09.md
research/amn2/target-server-manual-mode-critical-cleanup-evidence-2026-06-09.md
research/amn2/target-server-protocol-identity-and-numbered-peer-evidence-2026-06-09.md
research/amn2/target-server-manual-mode-field-test-evidence-2026-06-09.md
research/amn2/target-server-revoke-by-number-3-evidence-2026-06-09.md
research/amn2/target-server-service-mode-b0-preflight-evidence-2026-06-09.md
research/amn2/target-server-service-mode-b0-1-prep-and-repeat-evidence-2026-06-09.md
research/amn2/target-server-service-mode-b1-loopback-systemd-evidence-2026-06-09.md
research/amn2/target-server-service-mode-b2-0-reverse-proxy-preflight-evidence-2026-06-09.md
research/amn2/target-server-service-mode-b2-1-reverse-proxy-readiness-evidence-2026-06-09.md
research/amn2/target-server-service-mode-no-domain-ssh-tunnel-decision-2026-06-09.md
research/amn2/target-server-service-mode-ssh-tunnel-access-evidence-2026-06-09.md
research/amn2/target-server-service-mode-web-panel-tunnel-smoke-evidence-2026-06-09.md
research/amn2/target-server-service-mode-admin-telegram-id-add-evidence-2026-06-09.md
research/amn2/target-server-service-mode-authenticated-web-panel-smoke-evidence-2026-06-09.md
research/amn2/target-server-phase3-final-safety-snapshot-evidence-2026-06-09.md
research/amn2/target-server-service-mode-second-admin-bot-check-decision-2026-06-09.md
research/amn2/target-server-revoke-by-number-4-evidence-2026-06-09.md
docs/AMN2_MANUAL_MODE_REVOKE_BY_NUMBER_RUNBOOK.ru.md
docs/AMN2_SERVICE_MODE_SSH_TUNNEL_ACCESS_RUNBOOK.ru.md
```

Latest safe manual web/bot result:

```text
bot_check_network: passed
bot_identity: @NeobyatnayaAMNZ_bot
web_login_http: 200
web_listener: 127.0.0.1:3030 during diagnostic check only
web_listener_after_cleanup: stopped
tcp_3030_final: absent
tcp_3040_final: absent
peer_count_final: 0
```

## Обязательно Прочитать В Новом Чате

Start with:

```text
docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
docs/PROJECT_STATUS_CURRENT.ru.md
docs/PROJECT_CONTEXT_IMPORT.ru.md
docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
research/amn2/target-server-bootstrap-evidence-2026-06-08.md
research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
research/amn2/transfer-backlog.md
```

Operator/runbook context:

```text
docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md
```

## Строгие Правила Phase 3

Нельзя публиковать в чат или GitHub:

- `.env`;
- `servers.yml`;
- raw Telegram bot token;
- raw API token;
- Authorization header;
- token hash;
- web admin password hash;
- session secret;
- private key;
- PSK;
- peer public key;
- full `.conf`;
- QR payload/PNG;
- `vpn://`;
- backup contents;
- full logs;
- provider console credentials;
- SSH private key or SSH command with secret-bearing material.

Нельзя без отдельного подтверждения оператора:

- persistent `systemd` enable/start for web or bot;
- HTTPS reverse proxy/public cutover;
- `VPS_APPLY_ENABLED=true`;
- `apply-peer --apply`;
- `revoke-peer --apply`;
- production peer/user mutation;
- public web/API exposure;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent configs/mutations;
- backup/import/reboot routes.

## Recommended Phase 3 Order

### Step 0: local/git sanity

Check AMN3 and AMN2:

```powershell
cd C:\Users\SooL\Documents\VPS-OPS-LAB
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate

cd C:\Users\SooL\Documents\Amneziya
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
& 'C:\Program Files\Git\cmd\git.exe' log -5 --oneline --decorate
```

Expected:

```text
AMN3 master clean and synced with origin/master
AMN2 codex-vps-test-prep clean at the current stable/source-overlay head
```

### Step 1: confirm target VPS final safe baseline

Run only read-only checks first:

```text
source_overlay_commit: f7f6131
AWG2 container: running
peer_count: 0
tcp_3030: absent
tcp_3040: absent
telegram_bot_token: present
web_admin_password_hash: present
web_admin_session_secret: present
VPS_APPLY_ENABLED: false/not-set
```

Do not paste secret values.

### Step 2: decide Phase 3 path

Ask the operator for one explicit choice:

```text
Do we keep Phase 3 in manual runtime mode for now, or proceed to a service-mode gate for web/bot systemd plus HTTPS reverse proxy?
```

If the answer is not explicit, remain in manual mode.

### Step 3A: manual-mode continuation

Allowed without service-mode approval:

- docs/evidence updates;
- read-only API loopback smoke;
- manual web/admin diagnostic check on `127.0.0.1:3030`;
- bot `check-network`;
- local product/API planning;
- local tests and package preparation.

Still blocked:

- persistent public exposure;
- production peer writes;
- config delivery expansion.

### Step 3B: service-mode gate, only after explicit approval

Before enabling anything persistently:

- verify loopback bind for web/admin;
- verify bot token and web secrets are present without printing values;
- decide whether service units are copied/installed or only dry-run checked;
- decide HTTPS reverse proxy path and public access boundary;
- define rollback:
  - stop/disable units;
  - remove reverse proxy route;
  - verify `3030`/`3040` are not public;
  - keep AWG2 peer state unchanged.

Expected service-mode evidence must be safe:

```text
service_mode_gate_status:
web_unit_enabled:
web_unit_active:
bot_unit_enabled:
bot_unit_active:
web_bind:
web_login_http:
direct_public_3030:
public_api_3040:
reverse_proxy_status:
rollback_status:
peer_count:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

## Expected Outcomes

One of:

```text
phase3_manual_mode_pass
phase3_service_mode_pass
phase3_service_mode_deferred
needs-fix with safe AMN2/AMN3 plan
```

No outcome in Phase 3 should unlock broad write API, config delivery, production peer mutation, backup/import/reboot or public API `3040` by default.

## One-Copy Message For Creating The New Chat

```text
Работаем в C:\Users\SooL\Documents\VPS-OPS-LAB.

Новый чат: AMN2 Phase 3 Service Mode Gate.

Сначала прочитай:
- docs/NEXT_CHAT_AMN2_PHASE_3_SERVICE_MODE.ru.md
- docs/PROJECT_STATUS_CURRENT.ru.md
- docs/PROJECT_CONTEXT_IMPORT.ru.md
- docs/AMN_UNIFIED_PROD_GATE_HANDOFF.ru.md
- research/amn2/target-server-bootstrap-evidence-2026-06-08.md
- research/amn2/target-server-awg2-runtime-smoke-evidence-2026-06-09.md
- research/amn2/target-server-live-peer-gate-evidence-2026-06-09.md
- research/amn2/target-server-manual-web-bot-evidence-2026-06-09.md
- research/amn2/transfer-backlog.md
- docs/AMN2_TARGET_SERVER_PREP_GATE.ru.md
- docs/AMN2_TARGET_SERVER_PREP_RUNBOOK.ru.md
- docs/AMN2_CONTROLLED_PROD_READINESS_RUNBOOK.ru.md
- docs/AMN2_API_WEB_PANEL_VPS_TEST_RUNBOOK.ru.md
- docs/AMN2_VPS_API_UPDATE_AND_SMOKE.ru.md

Проверь git status/log:
- AMN3: C:\Users\SooL\Documents\VPS-OPS-LAB, branch master
- amn2: C:\Users\SooL\Documents\Amneziya, branch codex-vps-test-prep

Текущая production/source-overlay точка:
- AMN2 branch: codex-vps-test-prep
- AMN2 source-overlay/package head: f7f6131 Update integration status for c92 manual prelaunch
- AMN3 head before handoff: 615efc7 Record target server manual web bot gate
- package: dist/amn2-vps-update-and-smoke-kit-f7f6131.zip
- package sha256: 19BF96A7E1057C042B89630BF80ADC7A9F5A09A62436E33A8555D7E2991AF282

Что уже закрыто на новом target VPS:
- bootstrap: partial-pass
- AWG2 runtime: read-only-smoke-pass
- live peer gate: verified-live for exactly one disposable test peer
- manual web/bot gate: passed
- final peer count: 0
- direct public web 3030: closed
- public API 3040: closed
- service-mode systemd/reverse proxy: not-enabled

Задача:
1. Начать Phase 3 controlled service-mode/prod-readiness gate.
2. Сначала подтвердить read-only baseline: f7f6131, AWG2 running, peer_count=0, 3030/3040 closed, bot/web secrets present without printing values, VPS_APPLY_ENABLED=false/not-set.
3. Затем отдельно спросить решение: остаемся в manual mode или идем в service-mode gate для web/bot systemd + HTTPS reverse proxy.
4. Если service-mode gate подтвержден, делать только loopback web/admin + controlled HTTPS reverse proxy path, с rollback и safe evidence.
5. Не открывать public API 3040, direct public 3030, config delivery, /api/clients write CRUD, Local Agent mutations, backup/import/reboot или production peer writes без отдельного gate.

Не публиковать:
- .env, servers.yml, raw tokens, Authorization headers, token hash, web password hash, session secret, private keys, PSK, peer public keys, .conf, QR, vpn://, backup contents или full logs.

Ожидаемый результат чата:
- phase3_manual_mode_pass;
- либо phase3_service_mode_pass;
- либо phase3_service_mode_deferred;
- либо needs-fix с безопасным планом исправления.
```
