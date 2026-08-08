# Phase 13 Bot Media Read-Only Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Подготовить один checksum-bound USA-only read-only gate, который проверяет и при наличии собирает `data/bot-media-registry.json` и `data/bot-media/**`, шифруя содержимое до первой persistent write.

**Architecture:** Отдельный stdlib-only remote collector читает только fixed USA paths, отклоняет symlink/reparse-like и non-regular entries, строит bounded deterministic frame и не изменяет сервер. Один локальный runner проверяет manifest/approval/expiry, создаёт claim до network, запускает ровно один SSH через fixed pinned USA trust, валидирует frame в памяти и сохраняет только encrypted archive плюс secret-safe receipt; ключ хранится отдельно от artifact root.

**Tech Stack:** Python 3.12 stdlib, existing `scripts/phase10_recovery_crypto.py`, OpenSSH fixed trust bundle, pytest local fake harness.

## Global Constraints

- Phase 13 включает только bot/web migration и `USA_REINSTALL_READY`; AWG3 остаётся в Phase 14.
- Не повторять database/runtime/server-config collection и не обращаться к Spain.
- Разрешён ровно один read-only USA SSH process только после отдельной literal approval.
- Не сохранять plaintext media, registry, raw stdout/stderr, target/user/key/pin/fingerprint или system error.
- Не изменять USA/Spain services, databases, AWG, peers, configs, firewall или foreign service.
- Не трогать `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` и посторонние файлы.
- Не создавать broad security scan или дополнительные schema files.

---

### Task 1: Bounded encrypted bot-media collection gate

**Files:**
- Create: `scripts/vps/phase13_bot_media_readonly_remote.py`
- Create: `scripts/phase13_bot_media_readonly.py`
- Create: `tests/test_phase13_bot_media_readonly.py`
- Include: `docs/superpowers/plans/2026-08-09-phase13-bot-media-readonly-collection.md`

**Interfaces:**
- Produces remote `collect_media_frame(data_root: Path = Path("/opt/amn2/data")) -> bytes` and `parse_media_frame(frame: bytes) -> ParsedMediaFrame`.
- Produces local `materialize_bot_media_package(inputs: BotMediaPackageInputs, output_parent: Path) -> BotMediaPackageReceipt`.
- Produces local `run_bot_media_gate(package_root: Path, exact_approval: str, *, now: datetime, process_runner=run_bounded_process) -> BotMediaRunReceipt`.
- Consumes fixed `C:\ProgramData\AMN2\trust\usa` role binding and `encrypt_hybrid` from the checksum-bound packaged Phase 10 crypto bytes.

- [ ] **Step 1: Write failing remote-collector tests**

Add tests that hand-create a temporary `data` root and assert:

```python
frame = collect_media_frame(data_root)
parsed = parse_media_frame(frame)
assert parsed.evidence == {
    "content_sha256": EMPTY_ARCHIVE_SHA256,
    "file_count": 0,
    "media_root_present": False,
    "registry_present": False,
    "schema": "amn2.phase13.bot-media-readonly-evidence.v1",
    "total_bytes": 0,
}
assert parsed.files == {}
```

For present data, use literal files `bot-media-registry.json` and `bot-media/header.png`; require deterministic byte-identical frames, exact relative members, per-file SHA validation, maximum 256 files, maximum 10 MiB per file, maximum 48 MiB total, and rejection of symlink, directory-as-file, traversal-like, duplicate, oversized, or changing entries.

- [ ] **Step 2: Run remote tests and verify RED**

Run:

```powershell
python -m pytest tests/test_phase13_bot_media_readonly.py -q
```

Expected: collection error because the new modules do not exist.

- [ ] **Step 3: Implement minimal remote collector and parser**

Implement a deterministic gzip/tar frame with fixed magic, canonical JSON evidence, sorted POSIX member names, uid/gid/mtime zero, mode `0600`, and no filesystem writes. The only allowed members are:

```python
"bot-media-registry.json"
"bot-media/<safe relative regular-file path>"
```

Absence of both paths is a valid empty result. Any unsafe or partial path state fails closed with the constant public line `bot_media_collection_failed` and exit `74`.

- [ ] **Step 4: Run remote tests and verify GREEN**

Run the focused test and confirm the remote cases pass.

- [ ] **Step 5: Write failing package/runner tests**

Test two deterministic local materializations, exact artifact allowlist (`runner.py`, `remote.py`, `recovery_crypto.py`, `manifest.json`), lowercase SHA-256/size binding, canonical UTC expiry, `max_attempts=1`, all mutation flags false, and exact approval phrase containing outcome/manifest/runner/collector/crypto SHA values.

With a local fake SSH process assert:

```python
receipt = run_bot_media_gate(package_root, approval, now=BEFORE_EXPIRY, process_runner=fake)
assert receipt.ssh_process_count == 1
assert receipt.remote_collection_completed is True
assert receipt.plaintext_persisted is False
assert receipt.file_count == 2
assert receipt.encrypted_archive_path.suffix == ".enc"
```

Also require approval mismatch, expiry, replay, unsafe package path, checksum mismatch, timeout, non-zero SSH exit, malformed frame, oversized output, and encryption failure to stop before or without a second process and emit only allowlisted sanitized reason/subreason values.

- [ ] **Step 6: Run package/runner tests and verify RED**

Run the focused test and confirm failure because the local package/runner API is missing.

- [ ] **Step 7: Implement the minimal package/runner**

Materialization copies exact runner, collector and Phase 10 crypto bytes into a private create-new package root and writes a canonical manifest. Runtime verifies every byte before claim, loads only the fixed USA binding, uses one SSH process with `BatchMode`, `IdentitiesOnly`, pinned `known_hosts`, 60-second timeout, 1 MiB input cap and 64 MiB output cap, parses in memory, encrypts the archive before writing, clears plaintext buffers, and writes one create-new secret-safe receipt.

The public CLI has only:

```text
materialize --output-parent PATH --outcome-id ID --expires-at UTC
verify-local --package-root PATH
run --package-root PATH --exact-approval PHRASE
```

No host, user, key, port, target, remote path or trust-root override is accepted.

- [ ] **Step 8: Run focused tests and existing regression scope**

Run:

```powershell
python -m pytest tests/test_phase13_bot_media_readonly.py tests/test_phase13_bot_web_migration_fresh_inputs.py -q
python -m py_compile scripts/phase13_bot_media_readonly.py scripts/vps/phase13_bot_media_readonly_remote.py
git diff --check
```

Expected: all tests and syntax checks pass with no warnings attributable to the change.

- [ ] **Step 9: Perform scoped review and materialize fresh package**

Review the exact diff for secret output, mutation primitives, user-overridable transport fields, unsafe path traversal and plaintext persistence. Run `verify-local` twice, record exact SHA-256 values, and output a fresh Russian literal approval phrase. Stop before SSH.

- [ ] **Step 10: Commit the engineering gate without push**

```powershell
git add -- docs/superpowers/plans/2026-08-09-phase13-bot-media-readonly-collection.md scripts/phase13_bot_media_readonly.py scripts/vps/phase13_bot_media_readonly_remote.py tests/test_phase13_bot_media_readonly.py
git commit -m "Add Phase 13 bot media read-only gate"
```

Do not push until the live read-only result has been consumed and the Phase 13 status/receipt scope is known.
