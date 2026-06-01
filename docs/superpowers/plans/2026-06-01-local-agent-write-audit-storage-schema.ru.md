# Local Agent Write Audit Storage Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the authoritative SQLite storage slice for future Local Agent write audit events after VPS `GO-1`.

**Architecture:** This is a pre-VPS code-ready plan: it defines exact tests, schema, repository methods, and verification, but does not implement storage before GO-1. The implementation stores redacted `WriteAuditEvent` records in `local_agent_write_audit_events` inside the application SQLite DB from `DATABASE_PATH`, keeps `LOCAL_AGENT_WRITE_ENABLED=false` until the post-VPS gate, and adds no write routes.

**Tech Stack:** Python 3.12, sqlite3, existing `app.db` schema/repository layer, `app.agent.write_audit.WriteAuditEvent`, pytest.

---

## Scope And Gates

This plan is ready for execution only after `GO-1` in `docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md`.

Until then:

- `LOCAL_AGENT_WRITE_ENABLED=false`;
- no write routes;
- do not edit `app/agent/api.py` to register `/agent/clients*`;
- do not add `agent:clients:write` to the read-only token;
- do not mutate a real VPS.

The plan implements only authoritative audit storage. It does not implement peer apply/revoke endpoints.

Endpoint wiring plan that consumes this storage: `docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md`.

## File Structure

- Modify `app/db/schema.py`: create `local_agent_write_audit_events` and indexes idempotently.
- Modify `app/db/repositories.py`: add repository methods for insert and read paths.
- Modify `tests/db/test_repositories.py`: add schema, insert, duplicate, redaction, and list ordering tests.
- Keep `app/agent/write_audit.py`: source event contract; change only if a test proves a storage field is missing.
- Keep `tests/agent/test_write_audit.py`: contract tests for `WriteAuditEvent` and repr redaction.
- Update `docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md` only if implementation discovers a contract mismatch.

## Storage Contract

Table name:

```text
local_agent_write_audit_events
```

Required uniqueness:

```text
operation_id UNIQUE
audit_id UNIQUE
```

Required redaction:

```text
peer_public_key_fingerprint yes
no full peer_public_key
details_json redacted only
```

Sensitive values that must never be stored: raw token, private key, PSK, QR, `vpn://`, full client config, raw
confirmation nonce, full `.env`, SSH credentials.

Acceptance anchors:

- schema creates table and indexes idempotently;
- repository rejects duplicate operation_id;
- if audit write fails, block mutation;
- encrypted backup includes the table because the whole SQLite file is backed up.

## Task 1: Schema And Indexes

**Files:**
- Modify: `app/db/schema.py`
- Test: `tests/db/test_repositories.py`

- [ ] **Step 1: Write the failing schema test**

Add this test to `tests/db/test_repositories.py`:

```python
def test_schema_creates_local_agent_write_audit_events_table_and_indexes(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)

    table = conn.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'local_agent_write_audit_events'
        """
    ).fetchone()
    assert table is not None
    table_sql = str(table["sql"])
    assert "audit_id TEXT NOT NULL UNIQUE" in table_sql
    assert "operation_id TEXT NOT NULL UNIQUE" in table_sql
    assert "details_json TEXT NOT NULL DEFAULT '{}'" in table_sql
    assert "peer_public_key_fingerprint TEXT NOT NULL" in table_sql
    assert "peer_public_key " not in table_sql

    index_rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
          AND tbl_name = 'local_agent_write_audit_events'
        """
    ).fetchall()
    index_names = {str(row["name"]) for row in index_rows}
    assert "idx_write_audit_server_created" in index_names
    assert "idx_write_audit_client_created" in index_names
    assert "idx_write_audit_user_created" in index_names
    assert "idx_write_audit_device_created" in index_names
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_schema_creates_local_agent_write_audit_events_table_and_indexes -v
```

Expected: fail because `local_agent_write_audit_events` does not exist.

- [ ] **Step 3: Implement minimal schema**

Add to `initialize_schema()` in `app/db/schema.py`:

```python
        CREATE TABLE IF NOT EXISTS local_agent_write_audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id TEXT NOT NULL UNIQUE,
            operation_id TEXT NOT NULL UNIQUE,
            actor_surface TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            result_state TEXT NOT NULL,
            risk_class TEXT NOT NULL DEFAULT 'state-write',
            server_alias TEXT NOT NULL,
            server_id INTEGER,
            user_id INTEGER,
            device_id INTEGER,
            device_label TEXT,
            client_id TEXT NOT NULL,
            protocol TEXT NOT NULL DEFAULT 'amneziawg',
            peer_public_key_fingerprint TEXT NOT NULL,
            dry_run_reference TEXT NOT NULL,
            rollback_reference TEXT NOT NULL,
            message TEXT NOT NULL,
            details_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_write_audit_server_created
            ON local_agent_write_audit_events(server_alias, created_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_write_audit_client_created
            ON local_agent_write_audit_events(client_id, created_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_write_audit_user_created
            ON local_agent_write_audit_events(user_id, created_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_write_audit_device_created
            ON local_agent_write_audit_events(device_id, created_at DESC, id DESC);
```

- [ ] **Step 4: Run schema test to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_schema_creates_local_agent_write_audit_events_table_and_indexes -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/db/schema.py tests/db/test_repositories.py
git commit -m "Add write audit storage schema"
```

## Task 2: Repository Insert And Redaction

**Files:**
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`

- [ ] **Step 1: Write the failing repository test**

Add imports:

```python
from app.agent.write_audit import WriteAuditEvent
```

Add test:

```python
def test_repository_records_write_audit_event_with_redacted_details(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id, server_id = _create_user_and_server(repo)
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=7,
        vpn_ip="10.8.0.55",
        peer_public_key="public-for-storage-test",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )
    event = WriteAuditEvent(
        audit_id="audit-1",
        operation_id="op-1",
        actor_surface="web_admin",
        actor_id="admin:1",
        server_alias="debian-vps-1",
        client_id=f"device:{device_id}",
        peer_public_key="full-public-key-that-must-not-be-stored",
        dry_run_reference="preflight-1",
        result_state="dry_run_planned",
        rollback_reference="rollback-1",
        message="planned without private key secret-private",
        details={
            "private": "secret-private",
            "token": "raw-token-value",
            "safe": "visible",
        },
        secret_values=("secret-private", "raw-token-value"),
    )

    audit_db_id = repo.record_write_audit_event(
        event,
        user_id=user_id,
        device_id=device_id,
        device_label="phone",
        server_id=server_id,
        protocol="amneziawg",
    )

    row = conn.execute(
        "SELECT * FROM local_agent_write_audit_events WHERE id = ?",
        (audit_db_id,),
    ).fetchone()
    assert row is not None
    assert row["audit_id"] == "audit-1"
    assert row["operation_id"] == "op-1"
    assert row["peer_public_key_fingerprint"].startswith("sha256:")
    assert "full-public-key-that-must-not-be-stored" not in dict(row).values()
    assert "secret-private" not in row["message"]
    assert "raw-token-value" not in row["details_json"]
    assert "[REDACTED]" in row["details_json"]
```

- [ ] **Step 2: Run test to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_repository_records_write_audit_event_with_redacted_details -v
```

Expected: fail because `record_write_audit_event` does not exist.

- [ ] **Step 3: Implement minimal repository method**

Add import in `app/db/repositories.py`:

```python
from app.agent.write_audit import WriteAuditEvent
```

Add method to `Repository`:

```python
    def record_write_audit_event(
        self,
        event: WriteAuditEvent,
        *,
        user_id: int | None,
        device_id: int | None,
        device_label: str | None,
        server_id: int | None,
        protocol: str = "amneziawg",
    ) -> int:
        record = event.redacted_record()
        cursor = self._conn.execute(
            """
            INSERT INTO local_agent_write_audit_events (
                audit_id,
                operation_id,
                actor_surface,
                actor_id,
                result_state,
                risk_class,
                server_alias,
                server_id,
                user_id,
                device_id,
                device_label,
                client_id,
                protocol,
                peer_public_key_fingerprint,
                dry_run_reference,
                rollback_reference,
                message,
                details_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record["audit_id"]),
                str(record["operation_id"]),
                str(record["actor_surface"]),
                str(record["actor_id"]),
                str(record["result_state"]),
                str(record["risk_class"]),
                str(record["server_alias"]),
                server_id,
                user_id,
                device_id,
                device_label,
                str(record["client_id"]),
                protocol,
                str(record["peer_public_key_fingerprint"]),
                str(record["dry_run_reference"]),
                str(record["rollback_reference"]),
                str(record["message"]),
                json.dumps(record["details"], ensure_ascii=False, sort_keys=True),
            ),
        )
        self._commit()
        return int(cursor.lastrowid)
```

- [ ] **Step 4: Run repository test to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_repository_records_write_audit_event_with_redacted_details -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/db/repositories.py tests/db/test_repositories.py
git commit -m "Store redacted write audit events"
```

## Task 3: Uniqueness And Query Paths

**Files:**
- Modify: `app/db/repositories.py`
- Test: `tests/db/test_repositories.py`

- [ ] **Step 1: Write failing tests**

Add helper:

```python
def _write_audit_event(*, audit_id: str, operation_id: str, client_id: str = "client-1") -> WriteAuditEvent:
    return WriteAuditEvent(
        audit_id=audit_id,
        operation_id=operation_id,
        actor_surface="web_admin",
        actor_id="admin:1",
        server_alias="debian-vps-1",
        client_id=client_id,
        peer_public_key=f"public-{audit_id}",
        dry_run_reference=f"preflight-{audit_id}",
        result_state="dry_run_planned",
        rollback_reference=f"rollback-{audit_id}",
        message="safe message",
    )
```

Add tests:

```python
def test_repository_rejects_duplicate_operation_id(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)

    repo.record_write_audit_event(
        _write_audit_event(audit_id="audit-1", operation_id="op-duplicate"),
        user_id=None,
        device_id=None,
        device_label=None,
        server_id=None,
    )

    with pytest.raises(sqlite3.IntegrityError):
        repo.record_write_audit_event(
            _write_audit_event(audit_id="audit-2", operation_id="op-duplicate"),
            user_id=None,
            device_id=None,
            device_label=None,
            server_id=None,
        )


def test_repository_lists_write_audit_events_for_user_device_and_server(tmp_path):
    conn = connect(tmp_path / "test.sqlite3")
    initialize_schema(conn)
    repo = Repository(conn)
    user_id, server_id = _create_user_and_server(repo)
    device_id = repo.create_device(
        user_id=user_id,
        server_id=server_id,
        name="phone",
        duration_days=7,
        vpn_ip="10.8.0.77",
        peer_public_key="query-public",
        peer_private_key_encrypted="v1:encrypted-private",
        preshared_key_encrypted="v1:encrypted-psk",
        config_version="amneziawg_v2",
    )

    first_id = repo.record_write_audit_event(
        _write_audit_event(audit_id="audit-1", operation_id="op-1", client_id="client-query"),
        user_id=user_id,
        device_id=device_id,
        device_label="phone",
        server_id=server_id,
    )
    second_id = repo.record_write_audit_event(
        _write_audit_event(audit_id="audit-2", operation_id="op-2", client_id="client-query"),
        user_id=user_id,
        device_id=device_id,
        device_label="phone",
        server_id=server_id,
    )

    assert [row["id"] for row in repo.list_write_audit_events_for_user(user_id)] == [second_id, first_id]
    assert [row["id"] for row in repo.list_write_audit_events_for_device(device_id)] == [second_id, first_id]
    assert [row["id"] for row in repo.list_write_audit_events_for_server("debian-vps-1")] == [second_id, first_id]
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_repository_rejects_duplicate_operation_id tests/db/test_repositories.py::test_repository_lists_write_audit_events_for_user_device_and_server -v
```

Expected: duplicate test may pass through SQLite once schema exists; list test fails until list methods exist.

- [ ] **Step 3: Implement list methods**

Add to `Repository`:

```python
    def list_write_audit_events_for_user(
        self,
        user_id: int,
        *,
        limit: int = 50,
    ) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT *
            FROM local_agent_write_audit_events
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    def list_write_audit_events_for_device(
        self,
        device_id: int,
        *,
        limit: int = 50,
    ) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT *
            FROM local_agent_write_audit_events
            WHERE device_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (device_id, limit),
        ).fetchall()

    def list_write_audit_events_for_server(
        self,
        server_alias: str,
        *,
        limit: int = 50,
    ) -> list[sqlite3.Row]:
        return self._conn.execute(
            """
            SELECT *
            FROM local_agent_write_audit_events
            WHERE server_alias = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (server_alias, limit),
        ).fetchall()
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_repository_rejects_duplicate_operation_id tests/db/test_repositories.py::test_repository_lists_write_audit_events_for_user_device_and_server -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add app/db/repositories.py tests/db/test_repositories.py
git commit -m "Add write audit query paths"
```

## Task 4: Backup And Existing Contract Verification

**Files:**
- Modify: `tests/db/test_repositories.py`
- Test: `tests/db/test_repositories.py`, `tests/agent/test_write_audit.py`, backup tests if present

- [ ] **Step 1: Write the failing backup-aware test**

Add a DB-level assertion that the table is part of the SQLite file and survives reopen. This proves encrypted backup will
include it because backup packages the entire database file.

```python
def test_write_audit_storage_survives_database_reopen_for_encrypted_backup(tmp_path):
    db_path = tmp_path / "test.sqlite3"
    conn = connect(db_path)
    initialize_schema(conn)
    repo = Repository(conn)
    repo.record_write_audit_event(
        _write_audit_event(audit_id="audit-backup", operation_id="op-backup"),
        user_id=None,
        device_id=None,
        device_label=None,
        server_id=None,
    )
    conn.close()

    reopened = connect(db_path)
    row = reopened.execute(
        """
        SELECT audit_id, operation_id, details_json
        FROM local_agent_write_audit_events
        WHERE operation_id = ?
        """,
        ("op-backup",),
    ).fetchone()

    assert row is not None
    assert row["audit_id"] == "audit-backup"
    assert row["details_json"] == "{}"
```

- [ ] **Step 2: Run test to verify RED or GREEN**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py::test_write_audit_storage_survives_database_reopen_for_encrypted_backup -v
```

Expected: fail before repository implementation; pass after Tasks 1-3.

- [ ] **Step 3: Run contract tests**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py tests/agent/test_write_audit.py -v
```

Expected: pass. This command must include `pytest tests/db/test_repositories.py tests/agent/test_write_audit.py`.

- [ ] **Step 4: Confirm no route activation**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/agent/test_policy.py tests/test_file_hygiene.py -v
```

Expected: pass; write routes remain inactive and `LOCAL_AGENT_WRITE_ENABLED=false` defaults remain.

- [ ] **Step 5: Commit**

```powershell
git add tests/db/test_repositories.py
git commit -m "Verify write audit storage persistence"
```

## Task 5: Final Verification

**Files:**
- Modify: none unless a previous task changed docs.
- Test: full focused suite.

- [ ] **Step 1: Run focused storage and contract checks**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/db/test_repositories.py tests/agent/test_write_audit.py tests/agent/test_policy.py tests/test_file_hygiene.py -v
```

Expected: pass.

- [ ] **Step 2: Run documentation gate**

Run:

```powershell
$env:PYTHONPATH='C:\Users\SooL\Documents\Amneziya\.codex_deps'
& 'C:\Users\SooL\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests/deploy/test_runtime_registry.py -v
```

Expected: pass.

- [ ] **Step 3: Run whitespace and status checks**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected: `git diff --check` has no output; status shows only intended files before commit or clean after commit.

- [ ] **Step 4: Push**

```powershell
git push origin codex/local-agent-production-wiring
```

Expected: branch updates on `barakov-dot/amn3`.

## Self-Review

- Spec coverage: schema, repository, redaction, uniqueness, query paths, backup inclusion, and route safety are covered.
- Placeholder scan: no placeholder steps; each code step includes concrete snippets.
- Type consistency: repository methods use `WriteAuditEvent`, `sqlite3.Row`, `operation_id`, `audit_id`, `details_json`, and `peer_public_key_fingerprint` consistently.
- Scope: this plan prepares only audit storage. It does not implement Local Agent endpoints or enable write routes.
