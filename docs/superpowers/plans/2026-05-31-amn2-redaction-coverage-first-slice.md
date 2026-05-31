# AMN2 Redaction Coverage First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть P0 redaction coverage для `vpn://`, QR/config artifacts, raw/hash tokens, Local Agent headers и remote command output перед расширением state-changing remote operations.

**Architecture:** Расширяем существующий централизованный `app/security/redaction.py`, не создавая новый sanitizer. Добавляем focused failing-first tests вокруг redaction primitives, config delivery artifacts, web/email audit metadata и peer apply/revoke output. Production behavior меняется только там, где строка проходит через `redact()`; delivery channels продолжают получать реальные `.conf`, QR и `vpn://` artifacts.

**Tech Stack:** Python, pytest, FastAPI TestClient, текущие модули `app/security`, `app/bot`, `app/services`, `app/server`, `app/web`.

---

## File Structure

- Modify: `app/security/redaction.py` - добавить explicit patterns для reversible links, provisioning URIs, bearer/agent headers и future 2FA/recovery secret names.
- Modify: `tests/security/test_redaction.py` - focused failing-first tests для новых secret formats.
- Modify: `tests/bot/test_delivery.py` - доказать, что delivery artifacts корректны, но redacted при попадании в text output.
- Modify: `tests/services/test_config_delivery.py` - закрепить redaction behavior для `ConfigDeliveryResult`.
- Modify: `tests/web/test_email_delivery.py` - усилить audit metadata assertions для `vpn://`, raw token, private key и PSK.
- Modify: `tests/server/test_peer_apply.py` - усилить redaction tests для Docker/host stdout/stderr failures.
- Modify: `docs/RUNTIME_REGISTRY.ru.md` - зафиксировать QR PNG и `vpn://` как secret-bearing artifacts.
- Optional mirror: `docs/RUNTIME_REGISTRY.en.md` - обновить английское зеркало, если оно поддерживается в текущей ветке.

## Task 1: Redaction Primitives

**Files:**
- Modify: `tests/security/test_redaction.py`
- Modify: `app/security/redaction.py`

- [ ] **Step 1: Write failing tests for reversible links, auth headers and future secret names**

Append these tests to `tests/security/test_redaction.py`:

```python
def test_redaction_removes_vpn_links_agent_headers_and_bearer_tokens():
    unsafe = """
    Import link: vpn://W0ludGVyZmFjZV0KUHJpdmF0ZUtleSA9IGNsaWVudC1wcml2YXRl
    Authorization: Bearer local-agent-token-value
    Proxy-Authorization: Bearer proxy-token-value
    X-Amneziya-Agent-Token: agent-header-token
    LOCAL_AGENT_TOKEN=agent-env-token
    AGENT_SHARED_SECRET="agent shared secret"
    """

    safe = redact(unsafe)

    for unsafe_value in [
        "vpn://",
        "W0ludGVyZmFjZV0KUHJpdmF0ZUtleSA9IGNsaWVudC1wcml2YXRl",
        "local-agent-token-value",
        "proxy-token-value",
        "agent-header-token",
        "agent-env-token",
        "agent shared secret",
    ]:
        assert unsafe_value not in safe
    assert "[REDACTED]" in safe


def test_redaction_removes_totp_otpauth_and_recovery_codes():
    unsafe = """
    otpauth://totp/Amneziya:root?secret=JBSWY3DPEHPK3PXP&issuer=Amneziya
    TOTP_SECRET=totp-secret-value
    MFA_SECRET='mfa secret value'
    OTP_SECRET="otp secret value"
    BACKUP_CODE=backup-code-value
    RECOVERY_CODE=recovery-code-value
    """

    safe = redact(unsafe)

    for unsafe_value in [
        "otpauth://",
        "JBSWY3DPEHPK3PXP",
        "totp-secret-value",
        "mfa secret value",
        "otp secret value",
        "backup-code-value",
        "recovery-code-value",
    ]:
        assert unsafe_value not in safe
    assert safe.count("[REDACTED]") >= 6
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
pytest tests/security/test_redaction.py -v
```

Expected: the two new tests fail because `vpn://`, `otpauth://`, bearer headers or recovery-code names are still visible.

- [ ] **Step 3: Extend redaction patterns**

Update `app/security/redaction.py` so `PATTERNS` includes these cases before the broad key/value pattern:

```python
    re.compile(r"\bvpn://[A-Za-z0-9_-]+={0,2}", re.IGNORECASE),
    re.compile(r"\botpauth://[^\s\"'<>]+", re.IGNORECASE),
    re.compile(
        r"((?:Authorization|Proxy-Authorization)\s*:\s*Bearer\s+)[^\s,}]+",
        re.IGNORECASE,
    ),
    re.compile(
        r"((?:X-Amneziya-Agent-Token|X-Agent-Token)\s*:\s*)[^\s,}]+",
        re.IGNORECASE,
    ),
```

Then expand the key-name fragment inside the existing broad key/value pattern from:

```python
(?:PASSWORD_HASH|PASSWORD|TOKEN|SECRET|PRIVATE_KEY)
```

to:

```python
(?:PASSWORD_HASH|PASSWORD|TOKEN|SECRET|PRIVATE_KEY|BACKUP_CODE|RECOVERY_CODE|OTP|TOTP|MFA)
```

- [ ] **Step 4: Run the focused test and verify it passes**

Run:

```bash
pytest tests/security/test_redaction.py -v
```

Expected: all redaction tests pass.

- [ ] **Step 5: Commit the primitive coverage**

Run:

```bash
git add app/security/redaction.py tests/security/test_redaction.py
git diff --cached --check
git commit -m "Expand redaction primitive coverage"
```

## Task 2: Config Delivery Artifact Coverage

**Files:**
- Modify: `tests/bot/test_delivery.py`
- Modify: `tests/services/test_config_delivery.py`

- [ ] **Step 1: Write failing delivery redaction tests**

In `tests/bot/test_delivery.py`, import `redact`:

```python
from app.security.redaction import redact
```

Append this test:

```python
def test_config_delivery_artifacts_redact_when_rendered_as_text():
    config_text = (
        "[Interface]\n"
        "PrivateKey = client-private\n"
        "Address = 10.8.0.2/32\n"
        "[Peer]\n"
        "PublicKey = server-public\n"
        "PresharedKey = client-psk\n"
        "Endpoint = vpn.example.com:30001\n"
    )
    package = build_config_delivery(
        device_id=9,
        config_version="amneziawg_v2",
        config_text=config_text,
        template_text="Import link: {vpn_link}",
    )

    unsafe_text = "\n".join(
        [
            package.message_text,
            package.vpn_import_link,
            package.qr_payload_text,
            package.config_bytes.decode("utf-8"),
        ]
    )
    safe = redact(unsafe_text)

    for unsafe_value in [
        "vpn://",
        "client-private",
        "client-psk",
        "[Interface]",
        "[Peer]",
    ]:
        assert unsafe_value not in safe
    assert "[CONFIG REDACTED]" in safe
    assert "[REDACTED]" in safe
```

In `tests/services/test_config_delivery.py`, import `redact`:

```python
from app.security.redaction import redact
```

Add these assertions to `test_device_config_delivery_preserves_utf8_artifacts_from_template` after the existing delivery assertions:

```python
    redacted_delivery_text = redact(
        "\n".join(
            [
                result.delivery.message_text,
                result.delivery.vpn_import_link,
                result.delivery.qr_payload_text,
            ]
        )
    )
    assert "vpn://" not in redacted_delivery_text
    assert "client-private" not in redacted_delivery_text
    assert "client-psk" not in redacted_delivery_text
    assert "[Interface]" not in redacted_delivery_text
```

- [ ] **Step 2: Run the focused tests and verify the expected failure**

Run:

```bash
pytest tests/bot/test_delivery.py tests/services/test_config_delivery.py -v
```

Expected before Task 1 implementation is present: delivery redaction fails because `vpn://` remains visible. Expected after Task 1 implementation: tests pass.

- [ ] **Step 3: Run again after Task 1 is merged**

Run:

```bash
pytest tests/bot/test_delivery.py tests/services/test_config_delivery.py -v
```

Expected: all tests pass without changing config delivery behavior.

- [ ] **Step 4: Commit delivery coverage**

Run:

```bash
git add tests/bot/test_delivery.py tests/services/test_config_delivery.py
git diff --cached --check
git commit -m "Add config delivery redaction coverage"
```

## Task 3: Web Email Audit Coverage

**Files:**
- Modify: `tests/web/test_email_delivery.py`

- [ ] **Step 1: Strengthen audit assertions for config email**

In `test_verified_user_device_config_email_sends_without_exposing_encrypted_secrets`, extend the metadata assertions:

```python
        assert "vpn://" not in metadata
        assert "psk-phone" not in metadata
        assert "PrivateKey" not in metadata
        assert "PresharedKey" not in metadata
```

- [ ] **Step 2: Strengthen audit assertions for recovery flow**

In `test_recovery_start_link_sends_config_to_verified_email_and_is_one_time`, after the final token row assertions, add:

```python
    with _repo(Path(settings.database_path)) as repo:
        actions = repo.list_admin_actions_for_target_user(user_id)
        serialized_actions = "\n".join(str(action["metadata_json"]) for action in actions)
        assert token not in serialized_actions
        assert "vpn://" not in serialized_actions
        assert "private-phone" not in serialized_actions
        assert "psk-phone" not in serialized_actions
```

- [ ] **Step 3: Run web email tests**

Run:

```bash
pytest tests/web/test_email_delivery.py -v
```

Expected: all tests pass. If any assertion fails, fix the route metadata to record only ids/status/purpose and never config/link/token values.

- [ ] **Step 4: Commit audit coverage**

Run:

```bash
git add tests/web/test_email_delivery.py
git diff --cached --check
git commit -m "Harden config email audit coverage"
```

## Task 4: Remote Output Coverage

**Files:**
- Modify: `tests/server/test_peer_apply.py`
- Modify if needed: `app/server/peer_apply.py`

- [ ] **Step 1: Add Docker stderr redaction tests**

Append these tests to `tests/server/test_peer_apply.py`:

```python
def test_docker_config_read_failure_redacts_secret_stderr(tmp_path):
    server = _docker_server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )
    ssh = RecordingSshClient(
        result=CommandResult(
            exit_code=1,
            stdout="[Interface]\nPrivateKey = server-private\n[Peer]\nPresharedKey = secret-psk\n",
            stderr=(
                "failed with vpn://W0ludGVyZmFjZV0K and "
                "Authorization: Bearer remote-token-value"
            ),
        )
    )

    with pytest.raises(PeerApplyError) as exc_info:
        apply_peer(server, peer, ssh_client=ssh)

    message = str(exc_info.value)
    assert "server-private" not in message
    assert "secret-psk" not in message
    assert "vpn://" not in message
    assert "remote-token-value" not in message


def test_docker_restart_failure_redacts_secret_output(tmp_path):
    server = _docker_server(tmp_path)
    peer = PeerApplyInput(
        public_key="peer-public",
        preshared_key="secret-psk",
        vpn_ip="10.8.0.2",
    )
    ssh = RecordingSshClient(
        results=[
            CommandResult(exit_code=0, stdout=_docker_config(), stderr=""),
            CommandResult(exit_code=0, stdout="", stderr=""),
            CommandResult(
                exit_code=1,
                stdout="restart failed with secret-psk",
                stderr="Authorization: Bearer docker-restart-token",
            ),
        ]
    )

    with pytest.raises(PeerApplyError) as exc_info:
        apply_peer(server, peer, ssh_client=ssh)

    message = str(exc_info.value)
    assert "secret-psk" not in message
    assert "docker-restart-token" not in message
```

- [ ] **Step 2: Run peer apply tests and verify failure if output is still visible**

Run:

```bash
pytest tests/server/test_peer_apply.py -v
```

Expected: if `secret-psk` remains in Docker restart failure output, the new test fails.

- [ ] **Step 3: Redact Docker restart stdout/stderr with peer-aware replacement**

If the restart failure test fails, update `_restart_docker_container()` in `app/server/peer_apply.py` to avoid raw stdout/stderr leakage. The minimal safe form is:

```python
        raise PeerApplyError(
            redact(
                "Docker container restart failed "
                f"(exit_code={result.exit_code}). "
                f"stdout={_stream_status(result.stdout)} "
                f"stderr={result.stderr!r}"
            )
        )
```

If a test still exposes `secret-psk` through stderr, route the message through `redact()` and keep PSK-bearing data out of stdout.

- [ ] **Step 4: Run remote tests**

Run:

```bash
pytest tests/server/test_peer_apply.py tests/server/test_operation_runner.py tests/server/test_checks.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit remote output coverage**

Run:

```bash
git add app/server/peer_apply.py tests/server/test_peer_apply.py
git diff --cached --check
git commit -m "Harden remote output redaction coverage"
```

## Task 5: Runtime Docs and Hygiene

**Files:**
- Modify: `docs/RUNTIME_REGISTRY.ru.md`
- Modify if present and mirrored: `docs/RUNTIME_REGISTRY.en.md`
- Modify only if missing patterns are found: `tests/test_file_hygiene.py`, `tests/deploy/test_runtime_registry.py`

- [ ] **Step 1: Document secret-bearing artifacts in Russian runtime docs**

Add a short subsection to `docs/RUNTIME_REGISTRY.ru.md` under the runtime/security or diagnostics area:

```markdown
### Secret-bearing delivery artifacts

`.conf`, QR payload/PNG и `vpn://` import link считаются `client-config-secret`.
Их нельзя включать в runtime diagnostics, plain backups, audit metadata, logs или error output.
Если такой artifact попадает в текстовый diagnostic output, он должен проходить через `app.security.redaction.redact()`.
```

- [ ] **Step 2: Mirror in English docs when the file is maintained**

If `docs/RUNTIME_REGISTRY.en.md` exists in the branch, add:

```markdown
### Secret-bearing delivery artifacts

`.conf`, QR payload/PNG, and `vpn://` import links are `client-config-secret` artifacts.
They must not be included in runtime diagnostics, plain backups, audit metadata, logs, or error output.
If such an artifact reaches text diagnostic output, it must pass through `app.security.redaction.redact()`.
```

- [ ] **Step 3: Run hygiene/runtime tests**

Run:

```bash
pytest tests/test_file_hygiene.py tests/deploy/test_runtime_registry.py -v
```

Expected: all tests pass. If docs tests require a manifest entry, update only the documented runtime/security section and avoid unrelated doc rewrites.

- [ ] **Step 4: Commit docs and hygiene coverage**

Run:

```bash
git add docs/RUNTIME_REGISTRY.ru.md docs/RUNTIME_REGISTRY.en.md tests/test_file_hygiene.py tests/deploy/test_runtime_registry.py
git diff --cached --check
git commit -m "Document secret-bearing delivery artifacts"
```

## Task 6: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused security/delivery/remote verification**

Run:

```bash
pytest tests/security/test_redaction.py tests/bot/test_delivery.py tests/services/test_config_delivery.py tests/web/test_email_delivery.py tests/server/test_peer_apply.py tests/server/test_operation_runner.py tests/server/test_checks.py tests/test_file_hygiene.py tests/deploy/test_runtime_registry.py -v
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full test suite**

Run:

```bash
pytest tests -v
```

Expected: all tests pass. The known external `StarletteDeprecationWarning` from `fastapi.testclient` can remain if no new warning class appears.

- [ ] **Step 3: Update lab status after implementation**

After the `amn2` branch is verified, update `VPS-OPS-LAB/research/amn2/redaction-coverage-plan.md`:

```markdown
Статус: `redaction-coverage-first-slice-verified`.
```

Add the branch name, focused test result, full suite result and any known warning.

- [ ] **Step 4: Commit lab status separately**

Run from `C:\Users\SooL\Documents\VPS-OPS-LAB`:

```bash
git add research/amn2/redaction-coverage-plan.md ideas/priority-backlog.md
git diff --cached --check
git commit -m "Mark redaction coverage slice verified"
```
