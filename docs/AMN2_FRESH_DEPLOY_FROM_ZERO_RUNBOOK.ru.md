# AMN2 Fresh Deploy From Zero Runbook

Дата: 2026-06-11.

Назначение: подготовить понятный operator runbook для будущего развертывания AMN2 с нуля на чистой Ubuntu VPS из текущего package/source baseline `1508e3c`, сохраняя no-domain service-mode boundary. Этот документ не является разрешением запускать команды сейчас. Любой wipe/reinstall/package apply остается за `VPS-REBUILD-001` и требует retention-path decision, stop-criteria review и точную финальную destructive phrase.

## Current Baseline

```text
source_commit: 1508e3c4a100b76815b29f91757290f1266f813d
package: dist/amn2-vps-update-and-smoke-kit-1508e3c.zip
package_sha256: 03C51891AF83B9BD2B435AF5F77EEBBAE0DC7289CD107803DE7FB9877C4BFDA3
source_zip: dist/amn2-codex-vps-test-prep-1508e3c-source.zip
source_zip_sha256: 0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E
target_mode: no-domain service-mode
web_admin_bind: 127.0.0.1:3030
operator_access: SSH tunnel only
public_api_3040: absent/closed
tcp_80_443: absent unless a future public gate changes this
VPS_APPLY_ENABLED: false
```

## What This Can Recreate

- AMN2 application source from the selected package/source.
- Python virtualenv and application dependencies.
- Web/admin process or systemd service bound to `127.0.0.1:3030`.
- Bot process or systemd service after operator-provided Telegram/admin secrets.
- Read-only service-mode baseline and loopback login smoke.
- SSH-tunnel-only operator access.
- Safe evidence format without publishing secrets, target IP, keys, configs, QR or `vpn://`.

## What This Does Not Recreate By Itself

- Provider snapshot or rollback point.
- Raw `.env`, `servers.yml`, bot token, session/admin secrets or API tokens.
- Local SQLite state if no approved backup/export is provided.
- Existing Amnezia runtime state, private keys, PSKs, peer configs or QR payloads.
- Production peers/users.
- Public HTTPS/domain/Caddy setup.
- Config delivery, write API, Local Agent mutations, backup/import/reboot routes.

## Stop Line Before Running This Live

Do not run this runbook live until `VPS-REBUILD-001` records:

```text
target_identity_confirmed_out_of_repo: yes
retention_path_decision: provider_backup_confirmed | disposable_target_accepted | defer
stop_criteria_review: passed
final_destructive_phrase: GO VPS-REBUILD-001 WIPE TARGET
```

If the selected retention path is `defer`, stop here.

## Phase 0: Local Package Staging

Run locally before any VPS action:

```powershell
git status --short --branch
Get-FileHash .\dist\amn2-vps-update-and-smoke-kit-1508e3c.zip -Algorithm SHA256
Get-FileHash .\dist\amn2-codex-vps-test-prep-1508e3c-source.zip -Algorithm SHA256
```

Expected safe summary:

```text
local_repo_clean: yes
package_sha256_match: yes
source_zip_sha256_match: yes
package_ready: yes
```

## Phase 1: Fresh OS Baseline

Future live run only, after explicit approval.

```bash
set -euo pipefail
echo "fresh_deploy_phase=1_os_baseline"

hostnamectl
. /etc/os-release
printf 'os_id=%s\n' "$ID"
printf 'os_version=%s\n' "$VERSION_ID"
date -u '+time_utc=%Y-%m-%dT%H:%M:%SZ'
ss -ltnp || true
```

Expected safe summary:

```text
os_family: ubuntu-or-debian-lts
time_utc_ok: yes
public_3030_present: no
public_3040_present: no
public_80_present: no
public_443_present: no
```

## Phase 2: Base Packages

Future live run only.

```bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl git unzip rsync python3 python3-venv python3-pip openssl sudo

timedatectl set-ntp true || true
python3 --version
git --version
```

Expected safe summary:

```text
base_packages_installed: yes
python3_present: yes
git_present: yes
time_sync_requested: yes
```

## Phase 3: AMN2 Service User And Directories

Future live run only.

```bash
set -euo pipefail

id amneziya >/dev/null 2>&1 || useradd --system --home /opt/amn2 --shell /usr/sbin/nologin amneziya
install -d -o amneziya -g amneziya -m 0750 /opt/amn2
install -d -o amneziya -g amneziya -m 0750 /opt/amn2/data
install -d -o amneziya -g amneziya -m 0750 /opt/amn2/logs
install -d -o amneziya -g amneziya -m 0750 /opt/amn2/backups
```

Expected safe summary:

```text
service_user_present: yes
opt_amn2_present: yes
data_logs_backups_present: yes
```

## Phase 4: Upload And Verify Package

Operator local shell, future live run only. Use a private channel; do not paste target IP or full paths with secrets into chat.

```powershell
scp .\dist\amn2-vps-update-and-smoke-kit-1508e3c.zip root@TARGET_HOST:/tmp/amn2-vps-update-and-smoke-kit-1508e3c.zip
scp .\dist\amn2-vps-update-and-smoke-kit-1508e3c.zip.sha256.txt root@TARGET_HOST:/tmp/amn2-vps-update-and-smoke-kit-1508e3c.zip.sha256.txt
```

On the VPS:

```bash
set -euo pipefail
cd /tmp
sha256sum -c amn2-vps-update-and-smoke-kit-1508e3c.zip.sha256.txt
rm -rf /tmp/amn2-vps-update-and-smoke-kit-1508e3c
unzip -q /tmp/amn2-vps-update-and-smoke-kit-1508e3c.zip -d /tmp/amn2-vps-update-and-smoke-kit-1508e3c
find /tmp/amn2-vps-update-and-smoke-kit-1508e3c -maxdepth 2 -type f | sed 's#^#/##' | sort
```

Expected safe summary:

```text
package_uploaded: yes
package_sha256_match: yes
package_extracted: yes
package_entries_present: yes
```

## Phase 5: Install Source Into `/opt/amn2`

Future live run only.

```bash
set -euo pipefail
cd /tmp/amn2-vps-update-and-smoke-kit-1508e3c

install -m 0755 amn2_apply_source_zip.sh /tmp/amn2_apply_source_zip.sh
/tmp/amn2_apply_source_zip.sh \
  --source-zip /tmp/amn2-vps-update-and-smoke-kit-1508e3c/amn2-codex-vps-test-prep-1508e3c-source.zip \
  --target-dir /opt/amn2

chown -R amneziya:amneziya /opt/amn2
cd /opt/amn2
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -e .
```

Expected safe summary:

```text
source_apply_status: passed
source_commit_expected: 1508e3c
venv_created: yes
editable_install: passed
```

## Phase 6: Operator Secrets And Safe Defaults

Future live run only. Create `.env` and `servers.yml` through the operator local/private channel. Do not paste either file into chat or GitHub.

Required `.env` boundary:

```text
VPS_APPLY_ENABLED=false
WEB_ADMIN_ENABLED=true
WEB_HOST=127.0.0.1
WEB_PORT=3030
```

Required safe summary after writing private files:

```bash
set -euo pipefail
cd /opt/amn2
chown amneziya:amneziya .env servers.yml
chmod 0640 .env servers.yml
grep -q '^VPS_APPLY_ENABLED=false$' .env && echo 'vps_apply_enabled_false=yes'
grep -q '^WEB_HOST=127.0.0.1$' .env && echo 'web_host_loopback=yes'
```

Expected safe summary:

```text
env_present: yes
servers_yml_present: yes
file_modes_restricted: yes
vps_apply_enabled_false: yes
web_host_loopback: yes
```

## Phase 7: Read-Only Import And Smoke

Future live run only.

```bash
set -euo pipefail
cd /opt/amn2
sudo -u amneziya ./venv/bin/python -m app.cli bot check-network
sudo -u amneziya ./venv/bin/python -m app.cli server preflight --config servers.yml --server local --db data/amneziya.sqlite3
sudo -u amneziya ./venv/bin/python -m app.cli server check --config servers.yml --server local --dry-run
```

Expected safe summary:

```text
bot_check_network: ok
server_preflight: ok
server_check_dry_run: ok
live_peer_mutation: no
config_delivery: no
```

## Phase 8: Service-Mode Loopback

Future live run only.

Use systemd only after the prior phases pass and the operator still wants service-mode. Services must bind web/admin to loopback.

Expected safe summary after service-mode:

```text
service_amneziya_web_enabled: enabled
service_amneziya_web_active: active
service_amneziya_bot_enabled: enabled
service_amneziya_bot_active: active
loopback_login_http: 200
listener_3030_present: yes
listener_3030_loopback_only: yes
listener_3040_present: no
listener_80_present: no
listener_443_present: no
vps_apply_enabled_false: yes
secret_publication: none
```

## Phase 9: SSH Tunnel Operator Access

Operator workstation, future live run only:

```powershell
ssh -N -L 127.0.0.1:3030:127.0.0.1:3030 root@TARGET_HOST
```

Open in an external browser:

```powershell
Start-Process "http://127.0.0.1:3030/login"
```

Expected safe summary:

```text
operator_access: ssh_tunnel_only
external_browser_used: yes
public_web_admin: no
```

## Acceptance Criteria

Fresh deploy is acceptable only when safe evidence says:

```text
ssh_transport: ok
amneziya_web_active_enabled: yes
amneziya_bot_active_enabled: yes
loopback_login_http: 200
listener_3030_loopback_only: yes
public_api_3040_absent: yes
tcp_80_absent: yes
tcp_443_absent: yes
vps_apply_enabled_false: yes
config_delivery_performed: no
write_api_opened: no
local_agent_mutation: no
backup_import_reboot_performed: no
production_peer_user_mutation: no
secret_publication: none
```

## Still Separate Gates

- Retention path and destructive `GO`.
- Amnezia runtime install/attach if a clean OS has no Amnezia runtime yet.
- Recreating production peers/users.
- Config delivery.
- Write API.
- Public API `3040`.
- Direct public web/admin `3030`.
- Caddy/HTTPS/domain cutover.
- Backup/import/reboot.
- Local Agent mutations.
