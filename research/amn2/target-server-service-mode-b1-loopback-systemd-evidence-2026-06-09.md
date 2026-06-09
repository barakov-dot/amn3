# Target Server Service-Mode B1 Loopback Systemd Evidence - 2026-06-09

Status: `phase3_service_mode_B1_loopback_systemd_passed_after_investigation`.

Scope: controlled B1 gate for installing and enabling `amneziya-web` and `amneziya-bot` systemd units in loopback-only mode. This gate did not create or change any reverse proxy route. It did not open public API `3040`, direct public web/admin `3030`, config delivery, Local Agent mutation, backup/import/reboot or peer mutation.

## Initial B1 Execution

```text
phase3_B1_loopback_systemd: done
source_overlay_commit: f7f6131
tcp_3030_before: absent
tcp_3040_before: absent
VPS_APPLY_ENABLED_process: false
amneziya_user_exists: yes
web_template_loopback: yes
web_template_no_wildcard: yes
bot_template_entry: yes
amneziya-web_unit_file_present: yes
amneziya-bot_unit_file_present: yes
amneziya-web_enabled: enabled
amneziya-web_active: active
amneziya-bot_enabled: enabled
amneziya-bot_active: active
web_login_http: curl_rc_7
tcp_3030_after: absent
tcp_3040_after: absent
reverse_proxy_changed: no
public_api_3040_opened: no
VPS_APPLY_ENABLED_final: false
B1_status: needs-investigation
```

Initial interpretation: units installed/enabled/active, but the immediate web listener and `/login` probe did not observe readiness. Investigation was required before claiming B1 pass.

## B1 Investigation

```text
B1_investigation: done
amneziya-web_is_enabled: enabled
amneziya-web_is_active: active
amneziya-web_show_MainPID: present
amneziya-web_show_Result: success
amneziya-web_show_NRestarts: 0
amneziya-web_show_ExecMainStatus: 0
amneziya-web_show_WorkingDirectory: /opt/amn2
amneziya-web_show_User: amneziya
amneziya-web_show_Group: amneziya
amneziya-bot_is_enabled: enabled
amneziya-bot_is_active: active
amneziya-bot_show_MainPID: present
amneziya-bot_show_Result: success
amneziya-bot_show_NRestarts: 0
amneziya-bot_show_ExecMainStatus: 0
amneziya-bot_show_WorkingDirectory: /opt/amn2
amneziya-bot_show_User: amneziya
amneziya-bot_show_Group: amneziya
tcp_3030_lines_count: 1
tcp_3030_bind: 127.0.0.1:3030
tcp_3040_lines_count: 0
curl_login_rc: 0
curl_login_http: 200
amneziya-web_journal_rc: 0
amneziya-web_journal_markers: startup_complete, uvicorn_loopback_3030, login_200
amneziya-bot_journal_rc: 0
amneziya-bot_journal_markers: started
```

## Final Result

B1 loopback systemd passed after investigation. The initial `curl_rc_7`/absent-listener sample is treated as an early readiness timing sample, not the final state.

Final safe state:

```text
B1_final_status: passed-loopback-systemd
amneziya-web_enabled: enabled
amneziya-web_active: active
amneziya-bot_enabled: enabled
amneziya-bot_active: active
web_bind: 127.0.0.1:3030
web_login_http: 200
public_api_3040: absent
direct_public_web_3030: absent
reverse_proxy_changed: no
VPS_APPLY_ENABLED_final: false
service_mode_systemd: enabled
```

## Remaining Gates

- HTTPS reverse proxy/public cutover remains a separate explicit B2 gate.
- Public API `3040` remains closed.
- Direct public web/admin `3030` remains closed.
- Config delivery, production peer/user mutation beyond the remaining approved test peers, Local Agent mutations, backup/import/reboot and public/self-service config delivery remain blocked until separate gates.

## Secret Handling

No public IP, SSH credentials, host key material, `.env`, raw `servers.yml`, raw tokens, Authorization headers, token hashes, web password hash, session secret, private keys, PSK, peer public keys, client `.conf`, QR payloads, VPN URLs, endpoint values, backup contents or full logs were copied into this evidence.
