# AMN2 VPS Update And Smoke Kit 1508e3c

Date: 2026-06-10.

Purpose: package AMN2 `codex-vps-test-prep` source candidate `1508e3c4a100b76815b29f91757290f1266f813d` for the `VPS-REBUILD-001` destructive gate. This kit is local package evidence only until the gate later receives provider snapshot confirmation, stop-criteria review and the exact final destructive approval phrase.

Do not run this package on the VPS from this document alone.

```text
package/source overlay commit: 1508e3c4a100b76815b29f91757290f1266f813d
previous VPS-smoked source baseline: f7f6131
source zip sha256: 0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E
package status after local hygiene: package-ready-not-vps-smoked
active gate: VPS-REBUILD-001
gate status: opened-defer-awaiting-final-destructive-approval
destructive_action_authorized: no
reinstall_authorized: no
```

## Boundaries

Allowed later only after the active gate explicitly permits live execution:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv` when used as source overlay;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run only selected read-only post-install checks;
- keep web/admin loopback-only on `127.0.0.1:3030`;
- keep public API `3040` absent/closed unless a separate read-only API smoke gate explicitly chooses a loopback-only temporary API check.

Still blocked without separate approval:

- running this package on a live VPS before `VPS-REBUILD-001` final approval;
- `VPS_APPLY_ENABLED=true`;
- live `apply-peer --apply` or `revoke-peer --apply`;
- public API `3040` exposure;
- direct public web-admin `3030` exposure;
- Caddy/nginx/HTTPS public cutover;
- API `config:read`;
- `/api/clients` write CRUD;
- public/self-service config delivery;
- Local Agent clients/configs/write mutations;
- backup/import/reboot routes;
- publishing `.env`, `servers.yml`, raw token, Authorization header, token hash, private keys, PSK, `.conf`, QR, `vpn://`, or full logs.

## Future Approved Use

Only after the active gate allows live execution:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-1508e3c.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-1508e3c
mkdir -p amn2-vps-update-and-smoke-kit-1508e3c
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-1508e3c.zip amn2-vps-update-and-smoke-kit-1508e3c
cd amn2-vps-update-and-smoke-kit-1508e3c
sha256sum -c amn2-codex-vps-test-prep-1508e3c-source.zip.sha256.txt
```

Expected source SHA:

```text
0F4BBD72651FC99197C857093C24AAC9F3927EC9F5B7B7C364B1A312032EF15E
```

If the gate later selects source overlay apply:

```bash
cd /root/amn2-vps-update-and-smoke-kit-1508e3c
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=1508e3c4a100b76815b29f91757290f1266f813d
```

## Safe Evidence To Return

Return only safe summary fields:

```text
source overlay before:
source overlay after:
source_update_status:
source_commit:
post_install_check_status:
web_admin_loopback_status:
public_api_3040_status:
tcp_80_443_status:
VPS_APPLY_ENABLED:
safe_evidence_dir:
```

Do not return full logs, `.env`, `servers.yml`, raw tokens, Authorization headers, token hashes, private keys, PSK, `.conf`, QR, `vpn://`, or backup contents.
