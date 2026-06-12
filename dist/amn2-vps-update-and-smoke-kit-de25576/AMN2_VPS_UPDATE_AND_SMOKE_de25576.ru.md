# AMN2 VPS Update And Smoke Kit de25576

Date: 2026-06-12.

Purpose: package AMN2 `codex-vps-test-prep` source candidate `de2557639cd3853e6973002be3cab24033d2f722` for Phase 5 controlled operator-only pilot. This kit is local package evidence only until a later named live gate explicitly permits VPS execution.

Do not run this package on the VPS from this document alone.

```text
package/source overlay commit: de2557639cd3853e6973002be3cab24033d2f722
previous package candidate: 1508e3c
source zip sha256: CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
package status after local hygiene: package-ready-not-vps-smoked
active local gate: P5-C001
required later live gate: P5-C003
VPS_APPLY_ENABLED: false
destructive_action_authorized: no
reinstall_authorized: no
package_apply_authorized: no
```

## Boundaries

Allowed later only after a separate named live gate explicitly permits execution:

- preserve existing `/opt/amn2/.env`, `/opt/amn2/servers.yml`, `/opt/amn2/data`, `/opt/amn2/venv` when used as source overlay;
- apply tracked source overlay from this source zip;
- keep `VPS_APPLY_ENABLED=false`;
- run only selected read-only post-install checks;
- keep web/admin loopback-only on `127.0.0.1:3030`;
- keep public API `3040` absent/closed unless a separate read-only API smoke gate explicitly chooses a loopback-only temporary API check.

Still blocked without separate approval:

- running this package on a live VPS before `P5-C003` final approval;
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

Only after the active live gate allows execution:

```bash
cd /root
sha256sum -c amn2-vps-update-and-smoke-kit-de25576.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-de25576
mkdir -p amn2-vps-update-and-smoke-kit-de25576
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-de25576.zip amn2-vps-update-and-smoke-kit-de25576
cd amn2-vps-update-and-smoke-kit-de25576
sha256sum -c amn2-codex-vps-test-prep-de25576-source.zip.sha256.txt
```

Expected source SHA:

```text
CFF46C44CFB8F321DEB88CE64A0F5D2154CFC02CD3931CF9955DDC466615B8CC
```

If the gate later selects source overlay apply:

```bash
cd /root/amn2-vps-update-and-smoke-kit-de25576
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_EXPECTED_COMMIT=de25576
bash ./amn2_apply_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Expected update result:

```text
source_update_status=passed
source_commit=de2557639cd3853e6973002be3cab24033d2f722
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
