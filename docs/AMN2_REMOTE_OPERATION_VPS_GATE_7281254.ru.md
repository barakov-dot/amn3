# AMN2 Remote Operation VPS Gate 7281254

Дата: 2026-06-04.

Назначение: обновить установленный на VPS `/opt/amn2` до ветки `codex/remote-operation-vps-gate-prep`, head `7281254`, и выполнить только controlled read-only/dry-run gate. Это не разрешение на live `apply-peer --apply`, `revoke-peer --apply`, Docker restart, public web/API exposure или config delivery.

## Package

```text
dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip
dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip.sha256.txt
```

Source zip внутри package:

```text
amn2-remote-operation-vps-gate-7281254-source.zip
sha256: E7D36BE8D0EAD3C1F6C1F4144F93F4017BE24B39527259FB813D352350AB0B78
```

## 1. Загрузить и проверить package

На VPS:

```bash
cd /root

curl -fL -o amn2-remote-operation-vps-gate-7281254-update-kit.zip \
  https://github.com/barakov-dot/amn3/raw/master/dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip

curl -fL -o amn2-remote-operation-vps-gate-7281254-update-kit.zip.sha256.txt \
  https://raw.githubusercontent.com/barakov-dot/amn3/master/dist/amn2-remote-operation-vps-gate-7281254-update-kit.zip.sha256.txt

sha256sum -c amn2-remote-operation-vps-gate-7281254-update-kit.zip.sha256.txt
rm -rf amn2-remote-operation-vps-gate-7281254-update-kit
mkdir -p amn2-remote-operation-vps-gate-7281254-update-kit
python3 -m zipfile -e amn2-remote-operation-vps-gate-7281254-update-kit.zip amn2-remote-operation-vps-gate-7281254-update-kit
cd amn2-remote-operation-vps-gate-7281254-update-kit
sha256sum -c amn2-remote-operation-vps-gate-7281254-source.zip.sha256.txt
```

## 2. Наложить source overlay

```bash
cd /root/amn2-remote-operation-vps-gate-7281254-update-kit
unset AMN2_SOURCE_ZIP AMN2_EXPECTED_SOURCE_SHA AMN2_EXPECTED_SOURCE_COMMIT
export VPS_APPLY_ENABLED=false
export AMN2_DIR=/opt/amn2
export AMN2_SOURCE_ZIP=/root/amn2-remote-operation-vps-gate-7281254-update-kit/amn2-remote-operation-vps-gate-7281254-source.zip
export AMN2_EXPECTED_SOURCE_SHA=E7D36BE8D0EAD3C1F6C1F4144F93F4017BE24B39527259FB813D352350AB0B78
export AMN2_EXPECTED_SOURCE_COMMIT=7281254
bash ./amn2_apply_remote_operation_gate_source_zip.sh
install -m 700 ./amn2_api_loopback_smoke.sh /opt/amn2/amn2_api_loopback_smoke.sh
```

Ожидаемый итог:

```text
source_update_status=passed
source_commit=7281254
```

Проверить:

```bash
cd /opt/amn2
cat .amn2_source_overlay_commit
python - <<'PY'
from pathlib import Path
import app.server.peer_apply as peer_apply

path = Path(peer_apply.__file__)
text = path.read_text(encoding="utf-8")
print("peer_apply_path:", path)
print("source_has_metadata:", "Risk class: remote-state-write" in text)
print("source_has_operation_id:", "Operation ID:" in text)
PY
```

Ожидаемо:

```text
7281254
source_has_metadata: True
source_has_operation_id: True
```

## 3. Optional API loopback sanity

API/web-panel gate уже пройден для `294803e`, но после overlay можно повторить loopback sanity:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export AMN2_RUN_PREFLIGHT=0
export AMN2_SYNC_SERVER_CONFIG=1
export AMN2_REQUIRE_SERVER_DB_SYNC=1
export AMN2_SERVER_NAME=local
bash ./amn2_api_loopback_smoke.sh
```

Не присылать raw API token, Authorization header, token hash, `.env`, `servers.yml`, `.conf`, QR, `vpn://`, private keys или PSK.

## 4. Phase 1: read-only/dry-run remote-operation gate

Настроить shell-переменные под реальный alias сервера:

```bash
cd /opt/amn2
source venv/bin/activate
export VPS_APPLY_ENABLED=false
export SERVER_NAME=local
export DB_PATH=data/amneziya.sqlite3
```

Read-only checks:

```bash
python -m app.cli bot check-network
python -m app.cli server preflight --config servers.yml --server "$SERVER_NAME" --db "$DB_PATH"
python -m app.cli server check --config servers.yml --server "$SERVER_NAME" --dry-run
python -m app.cli server check --config servers.yml --server "$SERVER_NAME"
python -m app.cli server collect-traffic --config servers.yml --server "$SERVER_NAME" --db "$DB_PATH" --dry-run
```

Dry-run mutation previews only:

```bash
export TEST_PEER_PUBLIC_KEY='TEST_PEER_PUBLIC_KEY'
export TEST_PEER_PSK='TEST_PEER_PSK'
export TEST_VPN_IP='TEST_VPN_IP'

python -m app.cli server apply-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --preshared-key "$TEST_PEER_PSK" \
  --vpn-ip "$TEST_VPN_IP" \
  --dry-run

python -m app.cli server revoke-peer \
  --config servers.yml \
  --server "$SERVER_NAME" \
  --public-key "$TEST_PEER_PUBLIC_KEY" \
  --dry-run
```

Ожидаемо в dry-run output:

```text
Operation ID: server.peer.apply
Risk class: remote-state-write
Consistency status: dry-run
Remote side effects:
Rollback note:
```

и для revoke:

```text
Operation ID: server.peer.revoke
Risk class: remote-state-write
Consistency status: dry-run
Remote side effects:
Rollback note:
```

В выводе не должно быть raw PSK, `PrivateKey`, `PresharedKey`, полного `.conf`, QR, `vpn://` или Authorization header.

## 5. Stop point

Остановиться после Phase 1 и вернуть только safe summary/evidence:

- branch/head or `.amn2_source_overlay_commit`;
- `source-update-summary.txt`;
- summary API loopback sanity, если запускался;
- `preflight` summary;
- `server check --dry-run` output;
- read-only `server check` output, если запускался;
- `collect-traffic --dry-run` summary;
- `apply-peer --dry-run` redacted output;
- `revoke-peer --dry-run` redacted output;
- confirmation that `VPS_APPLY_ENABLED=false`;
- confirmation that no live `--apply` command was run.

Live `apply-peer --apply` и `revoke-peer --apply` запускать только после отдельного подтверждения оператора после review Phase 1 evidence.
