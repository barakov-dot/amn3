# Traffic Statistics and Config Version Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** add the foundation for traffic statistics and AmneziaWG config version selection (`amneziawg_v1_5` or `amneziawg_v2`) for user and administrator Telegram bot flows.

**Architecture:** first introduce a common config version registry and renderer dispatch. Then extend SQLite schema and repositories with traffic snapshots. After that, `AccessService` accepts the selected config version, and a separate traffic service stores peer traffic through a fake-friendly collector interface.

**Tech Stack:** Python 3.12+, pytest, SQLite, dataclasses, existing repository/service patterns.

---

## File Structure

- Create `app/vpn/config_versions.py`: supported config versions, validation, renderer dispatch.
- Create `app/vpn/amneziawg_v1_5/__init__.py`: v1.5 exports.
- Create `app/vpn/amneziawg_v1_5/config.py`: v1.5 renderer.
- Modify `app/db/schema.py`: add `device_traffic_snapshots`.
- Modify `app/db/repositories.py`: add traffic snapshot and peer lookup methods.
- Modify `app/services/access.py`: accept `config_version` and route renderer.
- Create `app/services/traffic.py`: traffic collector protocol, DTOs, collect/store service, display formatting.
- Add tests in `tests/vpn/`, `tests/db/`, and `tests/services/`.
- Update bilingual docs after implementation if behavior differs from the spec.

---

### Task 1: Config Version Registry and Renderer Dispatch

**Files:**

- Create: `app/vpn/config_versions.py`
- Create: `app/vpn/amneziawg_v1_5/__init__.py`
- Create: `app/vpn/amneziawg_v1_5/config.py`
- Test: `tests/vpn/test_config_versions.py`

- [ ] **Step 1: Write failing tests**

Create `tests/vpn/test_config_versions.py`:

```python
import pytest

from app.vpn.amneziawg_v2.config import ClientConfigInput
from app.vpn.config_versions import (
    SUPPORTED_CONFIG_VERSIONS,
    ConfigVersionError,
    render_client_config_for_version,
    validate_config_version,
)


def _input() -> ClientConfigInput:
    return ClientConfigInput(
        private_key="client-private",
        address="10.8.0.2/32",
        dns="1.1.1.1",
        server_public_key="server-public",
        preshared_key="psk",
        endpoint="vpn.example.com:30001",
        allowed_ips="0.0.0.0/0",
        persistent_keepalive=25,
        jc=4,
        jmin=40,
        jmax=70,
        s1=0,
        s2=0,
        h1=1,
        h2=2,
        h3=3,
        h4=4,
    )


def test_supported_config_versions_are_explicit():
    assert SUPPORTED_CONFIG_VERSIONS == ("amneziawg_v1_5", "amneziawg_v2")


def test_validate_config_version_rejects_unknown_value():
    with pytest.raises(ConfigVersionError, match="Unsupported config version"):
        validate_config_version("wireguard")


def test_v2_renderer_keeps_existing_amneziawg_v2_fields():
    config = render_client_config_for_version(_input(), "amneziawg_v2")

    assert "Jc = 4" in config
    assert "S1 = 0" in config
    assert "H4 = 4" in config


def test_v1_5_renderer_omits_v2_only_s3_s4_and_keeps_basic_shape():
    config = render_client_config_for_version(_input(), "amneziawg_v1_5")

    assert "[Interface]" in config
    assert "PrivateKey = client-private" in config
    assert "[Peer]" in config
    assert "PresharedKey = psk" in config
    assert "S3 =" not in config
    assert "S4 =" not in config
```

- [ ] **Step 2: Run focused test and confirm failure**

Run:

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/vpn/test_config_versions.py -v
```

Expected: FAIL because `app.vpn.config_versions` does not exist.

- [ ] **Step 3: Implement minimal registry and v1.5 renderer**

`config_versions.py` must expose:

- `SUPPORTED_CONFIG_VERSIONS = ("amneziawg_v1_5", "amneziawg_v2")`
- `ConfigVersionError`
- `validate_config_version(version)`
- `render_client_config_for_version(config, version)`

`amneziawg_v1_5.config.render_client_config` can reuse the same input dataclass and render the common AmneziaWG shape needed by current tests.

- [ ] **Step 4: Run focused test**

Expected: PASS.

---

### Task 2: Traffic Snapshot Schema and Repository

**Files:**

- Modify: `app/db/schema.py`
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_traffic_repository.py`

- [ ] **Step 1: Write failing tests**

Create tests for:

- inserting traffic snapshot;
- rejecting negative counters through DB constraint;
- returning newest snapshot for a device;
- resolving device by `(server_id, peer_public_key)`.

Required tests:

```python
def test_record_and_get_latest_device_traffic(tmp_path):
    # Create schema, user, server, and device.
    # Insert two snapshots for the same device.
    # Assert latest snapshot returns the larger collected_at value.
    # Assert total bytes can be computed from rx_bytes + tx_bytes.
    pass


def test_traffic_snapshot_rejects_negative_counters(tmp_path):
    # Create schema and a valid device.
    # Insert rx_bytes=-1 or tx_bytes=-1.
    # Assert sqlite3.IntegrityError is raised.
    pass


def test_get_device_by_server_peer_public_key(tmp_path):
    # Create two devices with distinct peer_public_key values.
    # Assert lookup by server_id and peer_public_key returns the matching device.
    # Assert lookup for an unknown peer returns None.
    pass
```

- [ ] **Step 2: Run focused test and confirm failure**

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests/db/test_traffic_repository.py -v
```

Expected: FAIL because repository methods/table do not exist.

- [ ] **Step 3: Implement schema**

Add `device_traffic_snapshots` table and indexes exactly as defined in the RU/EN spec.

- [ ] **Step 4: Implement repository methods**

Add methods:

```python
record_device_traffic_snapshot(
    *,
    device_id: int,
    server_id: int,
    peer_public_key: str,
    rx_bytes: int,
    tx_bytes: int,
    source: str,
    collected_at: str,
) -> int
get_latest_device_traffic(device_id: int)
get_device_by_server_peer_public_key(server_id: int, peer_public_key: str)
```

Return `None` for missing latest traffic or unknown peer lookup.

- [ ] **Step 5: Run focused test**

Expected: PASS.

---

### Task 3: Access Service Stores Selected Config Version

**Files:**

- Modify: `app/services/access.py`
- Test: `tests/services/test_access_config_version.py`

- [ ] **Step 1: Write failing tests**

Create tests:

```python
def test_approve_order_stores_selected_config_version(tmp_path):
    # Approve an order with config_version="amneziawg_v1_5".
    # Assert returned config has Interface and Peer sections.
    # Assert the saved device row stores config_version="amneziawg_v1_5".
    pass


def test_approve_order_rejects_unknown_config_version_without_creating_device(tmp_path):
    # Approve an order with config_version="wireguard".
    # Assert ConfigVersionError is raised.
    # Assert no device row is created.
    pass
```

The first test approves an order with `config_version="amneziawg_v1_5"` and asserts:

- returned config is valid;
- device row has `config_version == "amneziawg_v1_5"`.

The second test passes `config_version="wireguard"` and asserts no device is created.

- [ ] **Step 2: Run focused test and confirm failure**

Expected: FAIL because `approve_order` does not accept `config_version`.

- [ ] **Step 3: Implement service change**

Add keyword argument:

```python
config_version: str = "amneziawg_v2"
```

Validate before key generation/device creation. Use `render_client_config_for_version`.

- [ ] **Step 4: Run focused test**

Expected: PASS.

---

### Task 4: Traffic Collection Service

**Files:**

- Create: `app/services/traffic.py`
- Test: `tests/services/test_traffic_service.py`

- [ ] **Step 1: Write failing tests**

Create fake collector tests:

```python
def test_collect_and_store_traffic_records_known_peer(tmp_path):
    # Create a device with peer_public_key="known-peer".
    # Fake collector returns traffic for "known-peer".
    # Assert a snapshot is written and report.stored_count == 1.
    pass


def test_collect_and_store_traffic_reports_unknown_peer_without_snapshot(tmp_path):
    # Fake collector returns traffic for "unknown-peer".
    # Assert no snapshot is written and report.unknown_peers contains the peer.
    pass
```

Use dataclass `PeerTraffic` with:

- `peer_public_key`;
- `rx_bytes`;
- `tx_bytes`;
- `collected_at`;
- `source`.

- [ ] **Step 2: Run focused test and confirm failure**

Expected: FAIL because `app.services.traffic` does not exist.

- [ ] **Step 3: Implement traffic service**

Implement:

- `PeerTraffic`
- `TrafficCollectionReport`
- `TrafficCollector` protocol
- `TrafficService.collect_and_store(server_id, collector)`

Known peers create snapshots. Unknown peers are counted/listed in the report and not inserted.

- [ ] **Step 4: Run focused test**

Expected: PASS.

---

### Task 5: Display DTO and Byte Formatting

**Files:**

- Modify: `app/services/traffic.py`
- Test: `tests/services/test_traffic_display.py`

- [ ] **Step 1: Write failing tests**

Test:

- byte formatting for `0 B`, `1.0 KiB`, `1.0 MiB`;
- user-facing DTO includes rx, tx, total, and stale flag;
- missing stats are displayed as unavailable.

- [ ] **Step 2: Implement display helpers**

Add:

```python
format_bytes(value: int) -> str
build_device_traffic_view(device, latest_snapshot, *, stale_after_minutes: int = 60)
```

- [ ] **Step 3: Run focused test**

Expected: PASS.

---

### Task 6: Documentation and Full Verification

**Files:**

- Modify: `docs/DATA_MODEL.ru.md`
- Modify: `docs/DATA_MODEL.en.md`
- Modify: `docs/TECH_SPEC.ru.md`
- Modify: `docs/TECH_SPEC.en.md`

- [ ] **Step 1: Update bilingual docs**

Update both RU and EN docs with the final implemented table, config versions, and traffic display behavior.

- [ ] **Step 2: Run full tests**

```powershell
$env:PYTHONPATH='.codex_deps;.'; python -m pytest tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Run safety checks**

```powershell
git diff --check
rg --pcre2 -n "BEGIN .*PRIVATE KEY|TELEGRAM_BOT_TOKEN=[^C]|APP_SECRET_KEY=(?!CHANGE_ME)|UNFINISHED_MARKER" README.md docs app tests pyproject.toml .env.example .gitignore
```

Expected: no real secrets; only intentional fake test values and regex examples may appear.

---

## Self-Review

Spec coverage:

- Config version selection: Tasks 1 and 3.
- User/admin selected version foundation: Task 3.
- Traffic snapshots: Task 2.
- Fake-friendly collector: Task 4.
- User/admin display data: Task 5.
- Verification and bilingual docs: Task 6.

Deferred:

- Real SSH traffic collection from VPS.
- Telegram inline-button UI.
- Traffic limits and billing by traffic.
- Production DB migrations.
