# Config Delivery Artifact Integrity First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить в `amn2` первый проверяемый слой целостности delivery artifacts для текущей выдачи `.conf`, QR payload и `vpn://`.

**Architecture:** Текущий production path остается прежним: `app.services.config_delivery.build_device_config_delivery()` собирает config, а `app.bot.delivery.build_config_delivery()` делает package для пользователя. Первый slice добавляет явную metadata на уровне `ConfigDeliveryPackage`, чтобы тесты могли проверять secret class, UTF-8 bytes, QR payload и import link без новой тяжелой QR decoder dependency.

**Tech Stack:** Python 3.12, pytest, dataclasses, `qrcode[pil]`, `base64.urlsafe_b64decode`, текущие `Repository` и `SecretBox`.

---

## Scope

Входит:

- delivery-level artifact metadata для уже существующего `ConfigDeliveryPackage`;
- тесты, что `.conf` bytes равны UTF-8 encoded config text;
- тесты, что `vpn://` reversibly decodes в исходный config text;
- тесты, что QR payload явно равен raw config text;
- non-ASCII fixture с кириллицей через custom client config template;
- targeted и full pytest verification.

Не входит:

- public/self-service endpoints;
- новые share tokens;
- Telegram UX changes;
- новая QR decode dependency;
- manager export contract для новых protocol manager-ов;
- изменение формата AmneziaWG config.

## Current Code Map

- `app/bot/delivery.py`
  - `ConfigDeliveryPackage` сейчас содержит filenames, `.conf` bytes, QR PNG bytes и `vpn_import_link`.
  - `_build_qr_png(config_text)` генерирует QR PNG из raw config text.
  - `build_config_delivery()` уже строит `.conf`, QR и `vpn://`.
- `app/services/config_delivery.py`
  - `build_device_config_delivery()` decrypt-ит device secrets, renders config и вызывает `build_config_delivery()`.
- `app/vpn/config_templates.py`
  - `build_vpn_import_link(config_text)` делает `vpn://` через urlsafe base64 без padding.
- `tests/bot/test_delivery.py`
  - Уже проверяет, что package создает `.conf`, QR PNG и `vpn://`.
- `tests/services/test_config_delivery.py`
  - Уже проверяет, что device delivery использует `ClientConfigDefaults`.
- `tests/vpn/test_config_templates.py`
  - Уже проверяет round-trip для `build_vpn_import_link()`.

## Task 1: Add Delivery Artifact Metadata

**Files:**

- Modify: `app/bot/delivery.py`
- Modify: `tests/bot/test_delivery.py`

- [ ] **Step 1: Write the failing delivery metadata test**

In `tests/bot/test_delivery.py`, add `import base64` at the top and add this helper near imports:

```python
def _decode_vpn_link(link: str) -> str:
    payload = link.removeprefix("vpn://")
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding).decode("utf-8")
```

Add this test after `test_build_config_delivery_creates_conf_and_qr_png_bytes()`:

```python
def test_build_config_delivery_preserves_utf8_secret_artifacts():
    config_text = (
        "[Interface]\n"
        "# Profile = телефон-Ф\n"
        "PrivateKey = client-private\n"
        "Address = 10.8.0.2/32\n"
        "[Peer]\n"
        "Endpoint = vpn.example.com:30001\n"
    )

    package = build_config_delivery(
        device_id=8,
        config_version="amneziawg_v2",
        config_text=config_text,
        template_text="Import link: {vpn_link}",
    )

    assert package.config_bytes == config_text.encode("utf-8")
    assert package.qr_payload_text == config_text
    assert package.config_secret_class == "client-config-secret"
    assert package.config_content_encoding == "utf-8"
    assert package.vpn_import_link_encoding == "base64-url-no-padding"
    assert _decode_vpn_link(package.vpn_import_link) == config_text
    assert "client-private" not in package.vpn_import_link
```

- [ ] **Step 2: Run the focused failing test**

Run from `C:\Users\SooL\Documents\Amneziya`:

```powershell
python -m pytest tests/bot/test_delivery.py::test_build_config_delivery_preserves_utf8_secret_artifacts -q
```

Expected: FAIL with `AttributeError` for `qr_payload_text` or the first missing metadata field.

- [ ] **Step 3: Add metadata fields to `ConfigDeliveryPackage`**

In `app/bot/delivery.py`, update the dataclass:

```python
@dataclass(frozen=True)
class ConfigDeliveryPackage:
    template_key: str
    message_text: str
    config_filename: str
    config_bytes: bytes
    qr_filename: str
    qr_png_bytes: bytes
    vpn_import_link: str
    qr_payload_text: str = ""
    config_secret_class: str = "client-config-secret"
    config_content_encoding: str = "utf-8"
    vpn_import_link_encoding: str = "base64-url-no-padding"
```

Update the `build_config_delivery()` return block:

```python
    return ConfigDeliveryPackage(
        template_key=CONFIG_READY_TEMPLATE_KEY,
        message_text=render_template(template_text, context),
        config_filename=f"amneziya-device-{device_id}.conf",
        config_bytes=config_text.encode("utf-8"),
        qr_filename=f"amneziya-device-{device_id}.qr.png",
        qr_png_bytes=_build_qr_png(config_text),
        vpn_import_link=vpn_import_link,
        qr_payload_text=config_text,
    )
```

This keeps existing named construction in older tests working because the new fields have defaults.

- [ ] **Step 4: Run delivery tests**

Run:

```powershell
python -m pytest tests/bot/test_delivery.py -q
```

Expected: all tests in `tests/bot/test_delivery.py` pass.

- [ ] **Step 5: Commit Task 1**

```powershell
git add app/bot/delivery.py tests/bot/test_delivery.py
git commit -m "Add config delivery artifact metadata"
```

## Task 2: Add Device-Level UTF-8 Artifact Test

**Files:**

- Modify: `tests/services/test_config_delivery.py`

- [ ] **Step 1: Add a `vpn://` decode helper**

At the top of `tests/services/test_config_delivery.py`, add:

```python
import base64
```

Add this helper after imports:

```python
def _decode_vpn_link(link: str) -> str:
    payload = link.removeprefix("vpn://")
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding).decode("utf-8")
```

- [ ] **Step 2: Write the device-level custom template test**

Add this test after `test_device_config_delivery_uses_client_config_defaults()`:

```python
def test_device_config_delivery_preserves_utf8_artifacts_from_template(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "amneziawg_v2.conf.tpl").write_text(
        (
            "# Profile = телефон-Ф\n"
            "[Interface]\n"
            "PrivateKey = {private_key}\n"
            "Address = {address}\n"
            "DNS = {dns}\n"
            "[Peer]\n"
            "PublicKey = {server_public_key}\n"
            "PresharedKey = {preshared_key}\n"
            "Endpoint = {endpoint}\n"
            "AllowedIPs = {allowed_ips}\n"
            "PersistentKeepalive = {persistent_keepalive}\n"
            "Jc = {jc}\n"
            "Jmin = {jmin}\n"
            "Jmax = {jmax}\n"
            "S1 = {s1}\n"
            "S2 = {s2}\n"
            "H1 = {h1}\n"
            "H2 = {h2}\n"
            "H3 = {h3}\n"
            "H4 = {h4}\n"
        ),
        encoding="utf-8",
    )
    conn = connect(tmp_path / "delivery.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    secret_box = SecretBox.from_app_secret("test-secret-for-config-delivery-123456")
    user_id = repo.upsert_user(
        telegram_id=1002,
        username="ivan",
        first_name="Иван",
        last_name="Тест",
    )
    server_id = repo.ensure_default_server(name="moscow", network_cidr="10.8.0.0/24")
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="телефон-Ф",
        duration_days=7,
        vpn_ip="10.8.0.3",
        peer_public_key="client-public",
        peer_private_key_encrypted=secret_box.encrypt_text("client-private"),
        preshared_key_encrypted=secret_box.encrypt_text("client-psk"),
        config_version="amneziawg_v2",
    )

    result = build_device_config_delivery(
        repo=repo,
        secret_box=secret_box,
        device=repo.get_device(device_id),
        client_config_template_dir=str(template_dir),
    )

    assert "# Profile = телефон-Ф" in result.config_text
    assert result.delivery.config_bytes == result.config_text.encode("utf-8")
    assert result.delivery.qr_payload_text == result.config_text
    assert _decode_vpn_link(result.delivery.vpn_import_link) == result.config_text
    assert result.delivery.config_secret_class == "client-config-secret"
```

- [ ] **Step 3: Run the new device-level test**

Run:

```powershell
python -m pytest tests/services/test_config_delivery.py::test_device_config_delivery_preserves_utf8_artifacts_from_template -q
```

Expected: PASS after Task 1 metadata exists.

- [ ] **Step 4: Run service delivery tests**

Run:

```powershell
python -m pytest tests/services/test_config_delivery.py -q
```

Expected: all tests in `tests/services/test_config_delivery.py` pass.

- [ ] **Step 5: Commit Task 2**

```powershell
git add tests/services/test_config_delivery.py
git commit -m "Add config delivery utf8 artifact tests"
```

## Task 3: Verify Existing Import Link Tests Still Cover Encoding

**Files:**

- Read: `tests/vpn/test_config_templates.py`

- [ ] **Step 1: Run existing import link test**

Run:

```powershell
python -m pytest tests/vpn/test_config_templates.py::test_vpn_import_link_encodes_config_without_raw_secret_text -q
```

Expected: PASS. This confirms `build_vpn_import_link()` still decodes back to original text.

- [ ] **Step 2: Run the combined config delivery suite**

Run:

```powershell
python -m pytest tests/bot/test_delivery.py tests/services/test_config_delivery.py tests/vpn/test_config_templates.py -q
```

Expected: all selected tests pass.

- [ ] **Step 3: Run the full suite**

Run:

```powershell
python -m pytest tests -q
```

Expected: full suite passes.

- [ ] **Step 4: Check git diff**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected: `git diff --check` prints no errors. `git status --short --branch` shows only intended files if commits from Tasks 1 and 2 were not already pushed.

## Acceptance Criteria

- `ConfigDeliveryPackage` exposes `qr_payload_text`, `config_secret_class`, `config_content_encoding` and `vpn_import_link_encoding`.
- `build_config_delivery()` sets `qr_payload_text` to the exact raw config text used for QR generation.
- `.conf` bytes equal `config_text.encode("utf-8")`.
- `vpn://` decodes to the exact original config text.
- A device-level test covers a Cyrillic config line from a custom client config template.
- No public/self-service endpoint is added in this slice.
- No new runtime dependency is added in this slice.
- Targeted delivery tests and full test suite pass.

## Follow-Up Slice

After this first slice, a separate plan can introduce the broader manager export contract. That later slice should not start until the current delivery artifact tests are merged, because those tests become the guardrail for any new export path.

## Self-Review

Spec coverage:

- `.conf` UTF-8 bytes: Task 1 and Task 2.
- QR payload integrity: Task 1 and Task 2 through explicit `qr_payload_text`.
- `vpn://` round-trip: Task 1, Task 2 and existing Task 3 verification.
- Non-ASCII coverage: Task 1 and Task 2.
- No new public delivery surface: Scope and acceptance criteria.
- Manager export contract: intentionally deferred to a separate follow-up slice after artifact guardrails exist.

Red-flag scan:

- The plan avoids unresolved markers.
- Every code-changing step includes concrete code.
- Every verification step includes an exact command and expected result.
