# Local Agent Write Settings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the guarded settings/config slice for a dedicated Local Agent write token after VPS `GO-1`.

**Architecture:** This is a code-ready post-VPS plan. It keeps `LOCAL_AGENT_WRITE_ENABLED=false` as the default, preserves the current read-only token, and adds a separate dedicated write token set that is only accepted when `LOCAL_AGENT_WRITE_ENABLED=true`. The slice changes settings and token assembly only; it adds no write routes and does not mutate peers.

**Tech Stack:** Python 3.12, Pydantic Settings, existing `app.agent.auth.AgentToken`, existing `app.agent.config.build_agent_tokens`, pytest.

---

## Scope And Gates

Execute this plan only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Until `GO-1` remains true:

- `LOCAL_AGENT_WRITE_ENABLED=false`;
- `LOCAL_AGENT_TOKEN_SCOPES remains read-only`;
- `agent:clients:write must not be added to LOCAL_AGENT_TOKEN_SCOPES`;
- no write routes;
- no peer apply/revoke mutation;
- no raw token, private key, PSK, QR, `vpn://`, or full client config in logs, docs, screenshots, bot messages, or issue comments.

The new write settings are an authorization boundary only. They do not create `/agent/clients*` routes, do not register write policies, and do not deliver client configuration secrets.

## File Structure

- Modify `tests/config/test_settings.py`: prove defaults, validation, and token-scope separation.
- Modify `app/config/settings.py`: add explicit write settings and validators.
- Modify `tests/agent/test_config.py`: prove `build_agent_tokens()` returns a separate `AgentToken` for write mode.
- Modify `app/agent/config.py`: assemble read-only token and write token without mixing scopes.
- Keep `app/agent/auth.py`: existing `missing_scope` behavior remains the auth boundary; only change it if a RED test proves a missing contract.
- Keep `tests/agent/test_policy.py`: write routes remain blocked by `get_policy()` until the endpoint slice.
- Keep `tests/test_file_hygiene.py`: `.env.example` and `deploy/examples/.env.production.example` keep safe defaults and do not expose `agent:clients:write`.

## Settings Contract

Default state:

```text
LOCAL_AGENT_WRITE_ENABLED=false
LOCAL_AGENT_TOKEN_SCOPES remains read-only
agent:clients:write must not be added to LOCAL_AGENT_TOKEN_SCOPES
```

Post-`GO-1` explicit state:

```text
LOCAL_AGENT_WRITE_ENABLED=true
LOCAL_AGENT_WRITE_TOKEN_ID=local-write-controller
LOCAL_AGENT_WRITE_TOKEN_HASH=sha256:<generated-write-token-hash>
LOCAL_AGENT_WRITE_TOKEN_OWNER=local-write-controller
LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write
LOCAL_AGENT_WRITE_TOKEN_EXPIRES_AT=<optional-utc-expiry>
LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH=/opt/amn2/secrets/local-agent-write.token
```

The `dedicated write token set` is separate from the existing read-only token:

- read-only token scopes: `agent:health`, `agent:read`, `agent:protocols:read`;
- write token scopes: exactly `agent:clients:write`;
- write token must not be accepted for read-only routes because `app/agent/auth.py` returns `missing_scope`;
- read-only token must not be accepted for write routes because it has no `agent:clients:write`.

## Task 1: Settings Fields And Default Safety

**Files:**
- Modify: `tests/config/test_settings.py`
- Modify: `app/config/settings.py`

- [ ] **Step 1: Write the failing default/settings tests**

Append these tests to `tests/config/test_settings.py` near the existing Local Agent settings tests:

```python
WRITE_TOKEN_HASH = (
    "sha256:"
    "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
)


def test_settings_keeps_local_agent_write_disabled_without_write_token():
    settings = Settings(
        _env_file=None,
        telegram_bot_token="TEST_TOKEN",
        app_secret_key="test-secret",
        local_agent_enabled=True,
        local_agent_token_hash=(
            "sha256:"
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        ),
    )

    assert settings.local_agent_write_enabled is False
    assert settings.local_agent_write_token_hash == ""
    assert settings.local_agent_write_token_scopes == "agent:clients:write"


def test_settings_requires_write_token_hash_when_write_enabled():
    with pytest.raises(ValidationError, match="LOCAL_AGENT_WRITE_TOKEN_HASH"):
        Settings(
            _env_file=None,
            telegram_bot_token="TEST_TOKEN",
            app_secret_key="test-secret",
            local_agent_enabled=True,
            local_agent_token_hash=(
                "sha256:"
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
            local_agent_write_enabled=True,
        )


def test_settings_rejects_write_scope_in_read_only_token_even_when_write_enabled():
    with pytest.raises(ValidationError, match="LOCAL_AGENT_TOKEN_SCOPES"):
        Settings(
            _env_file=None,
            telegram_bot_token="TEST_TOKEN",
            app_secret_key="test-secret",
            local_agent_enabled=True,
            local_agent_token_hash=(
                "sha256:"
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
            local_agent_token_scopes="agent:health,agent:clients:write",
            local_agent_write_enabled=True,
            local_agent_write_token_hash=WRITE_TOKEN_HASH,
            local_agent_controller_enabled=True,
            local_agent_controller_token_path="/opt/amn2/secrets/local-agent-read.token",
            local_agent_controller_write_token_path="/opt/amn2/secrets/local-agent-write.token",
        )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/config/test_settings.py::test_settings_keeps_local_agent_write_disabled_without_write_token tests/config/test_settings.py::test_settings_requires_write_token_hash_when_write_enabled tests/config/test_settings.py::test_settings_rejects_write_scope_in_read_only_token_even_when_write_enabled -v
```

Expected: fail because the `LOCAL_AGENT_WRITE_*` settings do not exist yet.

- [ ] **Step 3: Add write settings fields**

Add these fields to `Settings` in `app/config/settings.py` directly after the existing read-only Local Agent token fields:

```python
    local_agent_write_enabled: bool = Field(default=False, alias="LOCAL_AGENT_WRITE_ENABLED")
    local_agent_write_token_id: str = Field(
        default="local-write-controller",
        alias="LOCAL_AGENT_WRITE_TOKEN_ID",
    )
    local_agent_write_token_hash: str = Field(
        default="",
        alias="LOCAL_AGENT_WRITE_TOKEN_HASH",
    )
    local_agent_write_token_owner: str = Field(
        default="local-write-controller",
        alias="LOCAL_AGENT_WRITE_TOKEN_OWNER",
    )
    local_agent_write_token_scopes: str = Field(
        default="agent:clients:write",
        alias="LOCAL_AGENT_WRITE_TOKEN_SCOPES",
    )
    local_agent_write_token_expires_at: str = Field(
        default="",
        alias="LOCAL_AGENT_WRITE_TOKEN_EXPIRES_AT",
    )
    local_agent_controller_write_token_path: str = Field(
        default="",
        alias="LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH",
    )
```

- [ ] **Step 4: Add hash normalization helper**

Add this helper below `Settings` in `app/config/settings.py`:

```python
def _normalize_optional_sha256_token_hash(setting_name: str, token_hash: str) -> str:
    normalized = token_hash.strip()
    if not normalized:
        return ""

    digest = normalized.removeprefix("sha256:")
    if (
        not normalized.startswith("sha256:")
        or len(digest) != 64
        or any(char not in "0123456789abcdef" for char in digest)
    ):
        raise ValueError(f"{setting_name} must be a sha256 token hash")
    return normalized
```

- [ ] **Step 5: Replace the existing Local Agent token hash validation**

In `validate_vpn_port_bounds()`, replace the current `token_hash = self.local_agent_token_hash.strip()` block with:

```python
        self.local_agent_token_hash = _normalize_optional_sha256_token_hash(
            "LOCAL_AGENT_TOKEN_HASH",
            self.local_agent_token_hash,
        )
        if self.local_agent_enabled and not self.local_agent_token_hash:
            raise ValueError(
                "LOCAL_AGENT_TOKEN_HASH must be set when LOCAL_AGENT_ENABLED=true"
            )
```

This preserves existing read-only behavior and removes duplicated hash parsing.

- [ ] **Step 6: Add write-mode validation**

Still inside `validate_vpn_port_bounds()`, immediately after read-only token validation, add:

```python
        allowed_write_scopes = {"agent:clients:write"}
        unknown_write_scopes = set(self.local_agent_write_scopes) - allowed_write_scopes
        if unknown_write_scopes:
            raise ValueError(
                "LOCAL_AGENT_WRITE_TOKEN_SCOPES contains unsupported write scope(s): "
                + ", ".join(sorted(unknown_write_scopes))
            )
        if set(self.local_agent_write_scopes) != allowed_write_scopes:
            raise ValueError(
                "LOCAL_AGENT_WRITE_TOKEN_SCOPES must be exactly agent:clients:write"
            )
        self.local_agent_write_token_hash = _normalize_optional_sha256_token_hash(
            "LOCAL_AGENT_WRITE_TOKEN_HASH",
            self.local_agent_write_token_hash,
        )
        self.local_agent_controller_write_token_path = (
            self.local_agent_controller_write_token_path.strip()
        )
        if self.local_agent_write_enabled:
            if not self.local_agent_enabled:
                raise ValueError(
                    "LOCAL_AGENT_ENABLED must be true when LOCAL_AGENT_WRITE_ENABLED=true"
                )
            if not self.local_agent_write_token_hash:
                raise ValueError(
                    "LOCAL_AGENT_WRITE_TOKEN_HASH must be set when "
                    "LOCAL_AGENT_WRITE_ENABLED=true"
                )
            if (
                self.local_agent_controller_enabled
                and not self.local_agent_controller_write_token_path
            ):
                raise ValueError(
                    "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH must be set for "
                    "controller write flow"
                )
```

- [ ] **Step 7: Add cached write scopes property**

Add this property under `local_agent_scopes`:

```python
    @cached_property
    def local_agent_write_scopes(self) -> list[str]:
        return [
            part.strip()
            for part in self.local_agent_write_token_scopes.split(",")
            if part.strip()
        ]
```

- [ ] **Step 8: Run tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/config/test_settings.py -v
```

Expected: pass.

- [ ] **Step 9: Commit**

```powershell
git add tests/config/test_settings.py app/config/settings.py
git commit -m "Add Local Agent write settings"
```

## Task 2: Dedicated Write Token Assembly

**Files:**
- Modify: `tests/agent/test_config.py`
- Modify: `app/agent/config.py`

- [ ] **Step 1: Write failing token assembly tests**

Add this constant under `TOKEN_HASH` in `tests/agent/test_config.py`:

```python
WRITE_TOKEN_HASH = (
    "sha256:"
    "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
)
```

Add these tests:

```python
def test_build_agent_tokens_returns_read_only_token_only_when_write_disabled():
    tokens = build_agent_tokens(_settings(local_agent_write_enabled=False))

    assert len(tokens) == 1
    assert tokens[0].token_id == "agent-token-1"
    assert tokens[0].scopes == frozenset({"agent:health", "agent:read"})


def test_build_agent_tokens_adds_dedicated_write_token_when_write_enabled():
    tokens = build_agent_tokens(
        _settings(
            local_agent_write_enabled=True,
            local_agent_write_token_hash=WRITE_TOKEN_HASH,
            local_agent_write_token_id="write-token-1",
            local_agent_write_token_owner="write-controller",
            local_agent_write_token_scopes="agent:clients:write",
        )
    )

    assert tokens == (
        AgentToken(
            token_id="agent-token-1",
            token_hash=TOKEN_HASH,
            scopes=frozenset({"agent:health", "agent:read"}),
            expires_at=None,
            owner="controller",
        ),
        AgentToken(
            token_id="write-token-1",
            token_hash=WRITE_TOKEN_HASH,
            scopes=frozenset({"agent:clients:write"}),
            expires_at=None,
            owner="write-controller",
        ),
    )


def test_build_agent_tokens_never_adds_write_scope_to_read_only_token():
    read_token, write_token = build_agent_tokens(
        _settings(
            local_agent_write_enabled=True,
            local_agent_write_token_hash=WRITE_TOKEN_HASH,
            local_agent_write_token_scopes="agent:clients:write",
        )
    )

    assert "agent:clients:write" not in read_token.scopes
    assert write_token.scopes == frozenset({"agent:clients:write"})
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_config.py::test_build_agent_tokens_returns_read_only_token_only_when_write_disabled tests/agent/test_config.py::test_build_agent_tokens_adds_dedicated_write_token_when_write_enabled tests/agent/test_config.py::test_build_agent_tokens_never_adds_write_scope_to_read_only_token -v
```

Expected: at least one test fails because `build_agent_tokens()` returns only the read-only `AgentToken`.

- [ ] **Step 3: Implement dedicated token assembly**

Replace `build_agent_tokens()` in `app/agent/config.py` with:

```python
def build_agent_tokens(settings: Settings) -> tuple[AgentToken, ...]:
    require_agent_enabled(settings)
    tokens = [
        AgentToken(
            token_id=settings.local_agent_token_id.strip(),
            token_hash=settings.local_agent_token_hash.strip(),
            scopes=parse_agent_scopes(settings.local_agent_token_scopes),
            expires_at=parse_agent_expiry(settings.local_agent_token_expires_at),
            owner=settings.local_agent_token_owner.strip(),
        )
    ]

    if settings.local_agent_write_enabled:
        tokens.append(
            AgentToken(
                token_id=settings.local_agent_write_token_id.strip(),
                token_hash=settings.local_agent_write_token_hash.strip(),
                scopes=parse_agent_scopes(settings.local_agent_write_token_scopes),
                expires_at=parse_agent_expiry(settings.local_agent_write_token_expires_at),
                owner=settings.local_agent_write_token_owner.strip(),
            )
        )

    return tuple(tokens)
```

This keeps `parse_agent_scopes` as the common parser and keeps `AgentToken` instances separate.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_config.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add tests/agent/test_config.py app/agent/config.py
git commit -m "Assemble Local Agent write token separately"
```

## Task 3: Auth And Policy Boundaries

**Files:**
- Modify: `tests/agent/test_auth.py`
- Modify only if the RED test proves a gap: `app/agent/auth.py`
- Verify: `tests/agent/test_policy.py`

- [ ] **Step 1: Write failing-or-confirming auth boundary tests**

Add these tests to `tests/agent/test_auth.py`:

```python
def test_write_token_missing_read_scope_is_rejected_with_missing_scope():
    raw_token = "write-token-value"
    agent_token = AgentToken(
        token_id="write-token",
        token_hash=hash_agent_token(raw_token),
        scopes=frozenset({"agent:clients:write"}),
        owner="write-controller",
    )

    with pytest.raises(AgentAuthError) as error:
        authenticate_agent_token(
            raw_token,
            tokens=[agent_token],
            required_scope="agent:health",
        )

    assert error.value.reason == "missing_scope"


def test_read_only_token_missing_write_scope_is_rejected_with_missing_scope():
    raw_token = "read-token-value"
    agent_token = AgentToken(
        token_id="read-token",
        token_hash=hash_agent_token(raw_token),
        scopes=frozenset({"agent:health", "agent:read", "agent:protocols:read"}),
        owner="local-controller",
    )

    with pytest.raises(AgentAuthError) as error:
        authenticate_agent_token(
            raw_token,
            tokens=[agent_token],
            required_scope="agent:clients:write",
        )

    assert error.value.reason == "missing_scope"
```

- [ ] **Step 2: Run tests to verify behavior**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_auth.py::test_write_token_missing_read_scope_is_rejected_with_missing_scope tests/agent/test_auth.py::test_read_only_token_missing_write_scope_is_rejected_with_missing_scope -v
```

Expected: pass if `app/agent/auth.py` already enforces `missing_scope`; fail only if the auth boundary regressed.

- [ ] **Step 3: Keep `app/agent/auth.py` unchanged when tests pass**

If the tests pass, do not edit `app/agent/auth.py`. If a test fails because `missing_scope` is not returned, make the smallest correction inside `authenticate_agent_token()` so the existing branch:

```python
        if required_scope not in token.scopes:
            raise AgentAuthError(
                f"Missing required scope: {required_scope}",
                reason="missing_scope",
            )
```

is preserved.

- [ ] **Step 4: Verify policy still blocks write routes**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py::test_local_contract_write_routes_remain_inactive_before_vps_smoke -v
```

Expected: pass; settings support does not activate routes.

- [ ] **Step 5: Commit**

```powershell
git add tests/agent/test_auth.py app/agent/auth.py
git commit -m "Verify Local Agent token scope separation"
```

If `app/agent/auth.py` stayed unchanged, stage only `tests/agent/test_auth.py`.

## Task 4: Examples And File Hygiene

**Files:**
- Verify: `.env.example`
- Verify: `deploy/examples/.env.production.example`
- Verify or modify only if needed: `tests/test_file_hygiene.py`

- [ ] **Step 1: Keep public examples safe**

Do not add this line to `.env.example` or `deploy/examples/.env.production.example`:

```text
LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write
```

The public examples remain safe with:

```text
LOCAL_AGENT_WRITE_ENABLED=false
```

Write token values are documented in `docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md` and are supplied only in a private VPS rollout step after `GO-1`.

- [ ] **Step 2: Run file hygiene tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/test_file_hygiene.py -v
```

Expected: pass. The test `test_env_examples_keep_local_agent_write_scope_disabled_until_vps_smoke` must still prove that `agent:clients:write` is absent from both public examples.

- [ ] **Step 3: Commit only if a test file needed a precision update**

```powershell
git add tests/test_file_hygiene.py
git commit -m "Keep Local Agent write examples disabled"
```

Skip this commit when there is no diff.

## Task 5: Final Verification

**Files:**
- Verify: `tests/config/test_settings.py`
- Verify: `tests/agent/test_config.py`
- Verify: `tests/agent/test_policy.py`
- Verify: `tests/test_file_hygiene.py`
- Verify: `tests/deploy/test_runtime_registry.py`

- [ ] **Step 1: Run focused settings/config safety suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/config/test_settings.py tests/agent/test_config.py tests/agent/test_policy.py tests/test_file_hygiene.py -v
```

Expected: pass; this command intentionally contains `pytest tests/config/test_settings.py tests/agent/test_config.py tests/agent/test_policy.py tests/test_file_hygiene.py`.

- [ ] **Step 2: Run deployment registry docs suite**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py -v
```

Expected: pass; the registry suite keeps this implementation plan linked from the handoff, post-VPS map, and settings contract.

- [ ] **Step 3: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 4: Commit complete settings implementation slice**

```powershell
git add tests/config/test_settings.py tests/agent/test_config.py tests/agent/test_auth.py app/config/settings.py app/agent/config.py docs/AMN3_NEXT_CHAT_HANDOFF.ru.md docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md
git commit -m "Implement Local Agent write settings"
```

Use this final commit only if Tasks 1-4 were intentionally batched. Prefer the smaller task commits above during normal execution.
