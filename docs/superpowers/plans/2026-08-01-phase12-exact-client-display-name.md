# Phase 12 Exact Client Display Name Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repackage the three already generated Spain configs so AmneziaVPN imports each as exact `NEOBYATNAYA.NET` while retaining unique recipient/slot identity outside the config bytes.

**Architecture:** A focused offline packager consumes the existing safe issuance manifest and three immutable `.conf` files, maps each manifest item to its existing device-ID filename, and emits one deterministic ZIP per slot. Every ZIP contains exact `NEOBYATNAYA.NET.conf` plus a secret-free canonical manifest; a verifier independently proves byte equality, uniqueness, and allowed membership.

**Tech Stack:** Python 3 standard library (`argparse`, `hashlib`, `json`, `pathlib`, `zipfile`), pytest, Git, Markdown.

## Global Constraints

- Never regenerate or alter config bytes, keys, peers, DB rows, or live Spain state.
- Inner filename is exactly `NEOBYATNAYA.NET.conf` for every slot.
- Recipient/device/device-ID/slot identity exists only in the unique outer archive name and package manifest.
- Never print config text, private keys, PSKs, QR payloads, or import URIs.
- Do not reboot Spain until the separate controlled-reboot approval is repeated and accepted.
- Do not touch the foreign Spain service, USA data, or protected monitoring documents.

---

### Task 1: Offline package contract and verifier

**Files:**
- Create: `scripts/phase12_spain_client_display_package.py`
- Create: `tests/test_phase12_spain_client_display_package.py`

**Interfaces:**
- Consumes: `build_packages(manifest_path: Path, configs_dir: Path, output_dir: Path) -> dict[str, object]`.
- Produces: deterministic per-slot ZIPs and `verify_packages(receipt: dict[str, object], configs_dir: Path, output_dir: Path) -> None`.

- [ ] **Step 1: Write failing exact-name and byte-preservation test**

```python
def test_builds_unique_archives_with_exact_inner_name_and_unchanged_bytes(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")
    assert len({item["archive_filename"] for item in receipt["items"]}) == 3
    for item in receipt["items"]:
        with ZipFile(tmp_path / "out" / item["archive_filename"]) as archive:
            assert archive.namelist() == ["NEOBYATNAYA.NET.conf", "package-manifest.json"]
            source = configs / item["source_filename"]
            assert archive.read("NEOBYATNAYA.NET.conf") == source.read_bytes()
```

- [ ] **Step 2: Run RED test**

Run: `python -m pytest -q tests/test_phase12_spain_client_display_package.py`
Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement minimal deterministic packager**

Implement exact manifest schema validation, safe ASCII archive slugs,
device-ID extraction from existing source filenames, canonical JSON, fixed ZIP
timestamp `(1980, 1, 1, 0, 0, 0)`, `ZIP_STORED`, and create-new output policy.

- [ ] **Step 4: Add collision, overwrite, determinism and secret-free tests**

```python
def test_rejects_duplicate_slot_identity(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["items"].append(dict(value["items"][0]))
    manifest.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(package.PackageError, match="duplicate slot identity"):
        package.build_packages(manifest, configs, tmp_path / "out")

def test_refuses_existing_output(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    output = tmp_path / "out"
    output.mkdir()
    with pytest.raises(FileExistsError):
        package.build_packages(manifest, configs, output)

def test_repeated_builds_are_byte_identical(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    first = package.build_packages(manifest, configs, tmp_path / "one")
    second = package.build_packages(manifest, configs, tmp_path / "two")
    assert first == second
    for item in first["items"]:
        assert (tmp_path / "one" / item["archive_filename"]).read_bytes() == (
            tmp_path / "two" / item["archive_filename"]
        ).read_bytes()

def test_outer_manifest_contains_hash_not_config_material(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")
    for item in receipt["items"]:
        with ZipFile(tmp_path / "out" / item["archive_filename"]) as archive:
            metadata = archive.read("package-manifest.json")
            assert item["config_sha256"].encode() in metadata
            assert b"PrivateKey" not in metadata
            assert b"PresharedKey" not in metadata

def test_verifier_rejects_changed_inner_bytes(tmp_path):
    manifest, configs = sample_three_slot_inputs(tmp_path)
    receipt = package.build_packages(manifest, configs, tmp_path / "out")
    source = configs / receipt["items"][0]["source_filename"]
    source.write_bytes(source.read_bytes() + b"\n")
    with pytest.raises(package.PackageError, match="source config drift"):
        package.verify_packages(receipt, configs, tmp_path / "out")
```

- [ ] **Step 5: Run GREEN scoped test**

Run: `python -m pytest -q tests/test_phase12_spain_client_display_package.py`
Expected: all tests pass.

### Task 2: Repackage the authoritative three existing configs

**Files:**
- Read: `private-artifacts/phase12-spain-config-issuance-20260730/sool-test-manifest.json`
- Read: `private-artifacts/phase12-spain-config-issuance-20260730/configs/*.conf`
- Create: ignored directory `private-artifacts/phase12-spain-config-issuance-20260730/client-display-packages/`
- Create: ignored receipt `private-artifacts/phase12-spain-config-issuance-20260730/client-display-package-receipt.json`

**Interfaces:**
- Consumes: immutable source config files and safe issuance manifest.
- Produces: three unique archives and a hash-only batch receipt.

- [ ] **Step 1: Record source SHA-256 and sizes without printing bytes**

Run: `Get-FileHash -Algorithm SHA256 <three exact config paths>` and `Get-Item <paths> | Select Length`.

- [ ] **Step 2: Build packages**

Run:
`python scripts/phase12_spain_client_display_package.py build --manifest private-artifacts/phase12-spain-config-issuance-20260730/sool-test-manifest.json --configs-dir private-artifacts/phase12-spain-config-issuance-20260730/configs --output-dir private-artifacts/phase12-spain-config-issuance-20260730/client-display-packages --receipt private-artifacts/phase12-spain-config-issuance-20260730/client-display-package-receipt.json`

- [ ] **Step 3: Independently verify packages**

Run the same script with `verify` and exact receipt/config/output paths.
Expected: `result=passed`, three unique archives, inner filename exact, source
and inner hashes equal for all items.

### Task 3: Regression, security and documentation gate

**Files:**
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Modify: `docs/AMN2_PHASE_12_SPAIN_MIGRATION_ENTRY.ru.md`
- Modify: `docs/AMN2_PHASE_12_SPAIN_OPERATOR_ADOPTION_RECEIPT.ru.md`
- Modify: `docs/NEXT_CHAT_AMN2_PHASE_12_SPAIN_MIGRATION.ru.md`
- Test: `tests/test_phase12_spain_client_display_package.py`

**Interfaces:**
- Consumes: hash-only package receipt and test outputs.
- Produces: current Phase 12 acceptance state without secret material.

- [ ] **Step 1: Run scoped and full tests**

Run: `python -m pytest -q tests/test_phase12_spain_client_display_package.py`
Run: `python -m pytest -q tests -k phase12_spain`
Run: the repository full pytest command discovered from `pyproject.toml`.

- [ ] **Step 2: Run diff and secret review**

Run: `git diff --check`.
Search the tracked diff for `[Interface]`, `PrivateKey`, `PresharedKey`, raw
config payloads, QR payloads, `vpn://`, and private artifact contents. Expected:
none. Manually verify the packager is offline-only, create-new, path-bounded,
and never logs config bytes.

- [ ] **Step 3: Synchronize status documents**

Record package/receipt SHA-256, test counts, exact display-name contract, and
the remaining real AmneziaVPN import confirmation. Do not embed `.conf` bytes.

- [ ] **Step 4: Commit and push tracked changes**

Stage only the spec, plan, packager, focused tests, and four Phase 12 documents.
Commit with `Package exact Spain client display names`, push branch
`codex-spark-phase9-docs-sync`, fetch, and require local/origin SHA equality.

### Task 4: Real AmneziaVPN acceptance and Phase 12 closure

**Files:**
- Modify after operator confirmation: `docs/AMN2_PHASE_12_SPAIN_OPERATOR_ADOPTION_RECEIPT.ru.md`
- Create after all acceptance gates: `docs/AMN2_PHASE_12_FINAL_CLOSEOUT_PACKET.ru.md`

**Interfaces:**
- Consumes: one operator import result and later controlled-reboot persistence result.
- Produces: accepted display-name evidence and final Phase 12 closeout/Phase 13 handoff.

- [ ] **Step 1: Request one real-client import confirmation**

Operator imports one selected archive's `NEOBYATNAYA.NET.conf` and reports:
`AMNEZIAVPN DISPLAY NAME: PASSED — BIG HEADER NEOBYATNAYA.NET — SERVERS LIST NEOBYATNAYA.NET`.

- [ ] **Step 2: Repeat controlled-reboot authorization**

Re-issue the exact Spain controlled-reboot persistence approval literal after
the display-name confirmation; do not reboot before that approval.

- [ ] **Step 3: Close Phase 12 only after both gates pass**

Persist the real-client and reboot receipts, authoritative Spain source/overlay,
USA rollback-contour decision, foreign-service equality receipt, prioritized
remaining product plan, and complete placeholder-free Phase 13 opening text.
