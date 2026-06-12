# AMN2 VPS update and smoke kit dd0dd44

Дата: 2026-06-12.

Назначение: operator package for a future named live gate that updates the disposable test VPS from the current installed source to AMN2 `dd0dd44` and then runs read-only loopback API smoke. This document does not authorize live VPS commands by itself.

Важно: этот архив и этот runbook не являются разрешением на live VPS apply.

## Artifacts

```text
AMN2 branch: codex-vps-test-prep
AMN2 commit: dd0dd442f0f25c1113accdc625dd16a96059eba4
source zip: amn2-codex-vps-test-prep-dd0dd44-source.zip
source zip sha256: E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1
package: amn2-vps-update-and-smoke-kit-dd0dd44.zip
```

## Local Status

```text
package_status: package-ready-not-vps-smoked
VPS_APPLY_ENABLED: false
live_commands_authorized: no
ssh_commands_authorized: no
package_apply_authorized: no
service_restart_authorized: no
public_exposure_authorized: no
config_delivery_authorized: no
write_api_authorized: no
```

## Future Named Gate Only

The operator may use this package only after a separate named gate explicitly opens live update work for the disposable test VPS.

Required future live-gate boundary:

- keep web/admin loopback-only;
- keep public API `3040` closed unless the named gate says otherwise;
- keep `VPS_APPLY_ENABLED=false`;
- do not deliver configs;
- do not run write API, Local Agent mutations, backup/import/reboot or production peer/user mutations;
- record safe summaries only, no secrets.

## Future Upload And Verify Example

```bash
sha256sum -c amn2-vps-update-and-smoke-kit-dd0dd44.zip.sha256.txt
rm -rf amn2-vps-update-and-smoke-kit-dd0dd44
python3 -m zipfile -e amn2-vps-update-and-smoke-kit-dd0dd44.zip amn2-vps-update-and-smoke-kit-dd0dd44
cd amn2-vps-update-and-smoke-kit-dd0dd44
sha256sum -c amn2-codex-vps-test-prep-dd0dd44-source.zip.sha256.txt
```

## Future Apply Example

```bash
cd /root/amn2-vps-update-and-smoke-kit-dd0dd44
export AMN2_SOURCE_ZIP=/root/amn2-vps-update-and-smoke-kit-dd0dd44/amn2-codex-vps-test-prep-dd0dd44-source.zip
export AMN2_EXPECTED_SOURCE_SHA=E29DFD7B64727BC75C677EDE2B897C6C972AB25243FD7713B767ABE1E29E2BD1
export AMN2_EXPECTED_SOURCE_COMMIT=dd0dd442f0f25c1113accdc625dd16a96059eba4
bash ./amn2_apply_source_zip.sh
```

## Future Smoke Example

For the current disposable test target, previous evidence showed `AMN2_SERVER_NAME=local` is required.

```bash
cd /opt/amn2
export AMN2_SERVER_NAME=local
export AMN2_EXPECTED_COMMIT=dd0dd44
./amn2_api_loopback_smoke.sh
```

`AMN2_EXPECTED_COMMIT` intentionally uses the short commit because the smoke script checks `git rev-parse --short HEAD`. The full source commit for this package is `dd0dd442f0f25c1113accdc625dd16a96059eba4`.
