# Spain systemd MainPID fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Исправить ложный fail-closed Spain preflight для active systemd units без `ControlGroup`, сохранив полный socket fingerprint для живого `MainPID` и отдельный single-use outcome run.

**Architecture:** Remote probe получает две небольшие границы: строгий parser procfs cgroup и resolver `ControlGroup -> MainPID -> procfs`. Resolver вызывается напрямую и возвращает успех через две внутренние result-переменные, чтобы failure-envelope никогда не захватывался command substitution. Проверенный dedicated SSH key/host pin остаётся read-only trust bundle `spain-fresh-20260720-001`; новый outcome/claim создаётся только в `spain-fresh-20260720-002` после нового exact approval. Старый claim и failure receipt не удаляются и не переиспользуются.

**Tech Stack:** Bash 4+, systemd/systemctl, Linux procfs/cgroup v1/v2, Windows PowerShell 7/5.1-compatible runner, Python `unittest`/`pytest`, Git.

## Global Constraints

- Source revision остаётся `55dc243b8e6c6bdb57f8301b56326e4cd4072d19`.
- Remote probe остаётся `set -Eeuo pipefail` и read-only.
- Никаких install/update/remove, start/stop/restart/enable/disable или remote writes.
- Никаких изменений AWG, Telegram, production USA или unrelated service.
- PID, cgroup path, raw stdout/stderr и private target data не попадают в Git, receipt или operator output.
- Старый `spain-fresh-20260720-001` остаётся consumed и immutable.
- Новый outcome run: `spain-fresh-20260720-002`.
- Trust artifacts читаются только из immutable `spain-fresh-20260720-001`.
- Новый SSH запрещён до commit/push/origin readback и отдельной буквальной approval.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не изменять.

---

### Task 1: RED tests для ControlGroup/MainPID/procfs resolver

**Files:**
- Modify: `tests/test_post_release_spain_readonly_preflight.py`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: `extract_bash_function(source, name)`.
- Produces: ожидаемые Bash functions `safe_cgroup_path`, `parse_proc_cgroup_path`, `resolve_unit_cgroup`; result variables `RESOLVED_BOUND_PORT_STATUS` и `RESOLVED_CONTROL_GROUP`.

- [ ] **Step 1: Добавить helper для запуска extracted Bash functions**

```python
def run_bash_harness(source: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(BASH), "-c", source],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
```

- [ ] **Step 2: Добавить RED test для cgroup v2/v1 и unsafe/ambiguous input**

```python
@unittest.skipUnless(BASH.exists(), "Git Bash is required")
def test_proc_cgroup_parser_accepts_one_v2_or_systemd_v1_path_and_rejects_unsafe_input(self) -> None:
    source = REMOTE.read_text(encoding="utf-8")
    functions = extract_bash_function(source, "safe_cgroup_path") + extract_bash_function(source, "parse_proc_cgroup_path")
    harness = functions + r'''
[[ "$(parse_proc_cgroup_path $'0::/system.slice/demo.service\n')" == "/system.slice/demo.service" ]] || exit 10
[[ "$(parse_proc_cgroup_path $'2:cpu:/legacy\n1:name=systemd:/system.slice/legacy.service\n')" == "/system.slice/legacy.service" ]] || exit 11
for bad in $'0::/ok\n0::/duplicate\n' $'1:cpu:/not-systemd\n' $'0::/../../escape\n'; do
    if parse_proc_cgroup_path "$bad" >/dev/null 2>&1; then exit 12; fi
done
'''
    result = run_bash_harness(harness)
    self.assertEqual(result.returncode, 0, result.stderr)
```

- [ ] **Step 3: Добавить RED tests для MainPID=0 и MainPID>0**

```python
@unittest.skipUnless(BASH.exists(), "Git Bash is required")
def test_unit_cgroup_resolver_distinguishes_active_exited_and_live_mainpid(self) -> None:
    source = REMOTE.read_text(encoding="utf-8")
    functions = "".join(extract_bash_function(source, name) for name in (
        "emit_failure", "safe_cgroup_path", "parse_proc_cgroup_path", "resolve_unit_cgroup"
    ))
    with tempfile.TemporaryDirectory() as raw_tmp:
        proc_root = Path(raw_tmp)
        (proc_root / "321").mkdir()
        (proc_root / "321" / "cgroup").write_text("0::/system.slice/live.service\n", encoding="utf-8")
        proc_root_bash = str(proc_root).replace("\\", "/")
        harness = functions + rf'''
systemctl() {{
    if [[ "$*" == *"ControlGroup"* ]]; then printf '\n';
    elif [[ "$*" == *"MainPID"* && "$1" == "show" && "$2" == "exited.service" ]]; then printf '0\n';
    elif [[ "$*" == *"MainPID"* ]]; then printf '321\n';
    else return 90; fi
}}
resolve_unit_cgroup exited.service active '{proc_root_bash}'
[[ "$RESOLVED_BOUND_PORT_STATUS|$RESOLVED_CONTROL_GROUP" == "active_exited_no_live_process|" ]] || exit 20
resolve_unit_cgroup live.service active '{proc_root_bash}'
[[ "$RESOLVED_BOUND_PORT_STATUS|$RESOLVED_CONTROL_GROUP" == "mainpid_cgroup_complete|/system.slice/live.service" ]] || exit 21
'''
        result = run_bash_harness(harness)
    self.assertEqual(result.returncode, 0, result.stderr)
```

- [ ] **Step 4: Добавить RED test для codes 71–73 и отсутствия private output**

```python
def test_mainpid_fallback_is_fail_closed_and_raw_free(self) -> None:
    source = REMOTE.read_text(encoding="utf-8")
    for code in (71, 72, 73):
        self.assertIn(f"emit_failure {code}", source)
        self.assertNotRegex(source, rf"(?m)^\s*exit {code}$")
    self.assertNotIn('printf "$main_pid"', source)
    self.assertNotIn('printf "$proc_cgroup_text"', source)
```

- [ ] **Step 5: Запустить RED tests и подтвердить ожидаемый отказ**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "proc_cgroup_parser or unit_cgroup_resolver or mainpid_fallback"
```

Expected: FAIL из-за отсутствующих `safe_cgroup_path`, `parse_proc_cgroup_path`, `resolve_unit_cgroup` и codes `71..73`.

---

### Task 2: GREEN remote MainPID/proc-cgroup fallback

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_remote.sh`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: systemctl unit name/state и explicit proc root.
- Produces: globals `RESOLVED_BOUND_PORT_STATUS` и `RESOLVED_CONTROL_GROUP`; failure только через `emit_failure 71|72|73` при прямом вызове, без command-substitution capture.

- [ ] **Step 1: Реализовать строгую проверку cgroup path**

```bash
safe_cgroup_path() {
    local path="$1" segment
    [[ "$path" == /* && "$path" != *'|'* && "$path" != *$'\n'* && "$path" != *$'\r'* ]] || return 1
    IFS='/' read -r -a segments <<< "$path"
    for segment in "${segments[@]}"; do
        [[ "$segment" != ".." ]] || return 1
        [[ "$segment" != *[[:cntrl:]]* ]] || return 1
    done
}
```

- [ ] **Step 2: Реализовать deterministic v2-first/v1 parser**

```bash
parse_proc_cgroup_path() {
    local text="$1" hierarchy controllers path extra controller
    local v2_path="" v2_count=0 v1_path="" v1_count=0
    while IFS=: read -r hierarchy controllers path extra; do
        [[ -n "$hierarchy$controllers$path" && -z "${extra:-}" ]] || return 1
        if [[ "$hierarchy" == "0" && -z "$controllers" ]]; then
            safe_cgroup_path "$path" || return 1
            v2_path="$path"; ((v2_count += 1))
            continue
        fi
        IFS=',' read -r -a controller_list <<< "$controllers"
        for controller in "${controller_list[@]}"; do
            if [[ "$controller" == "name=systemd" ]]; then
                safe_cgroup_path "$path" || return 1
                v1_path="$path"; ((v1_count += 1))
            fi
        done
    done <<< "$text"
    if (( v2_count == 1 )); then printf '%s\n' "$v2_path"; return 0; fi
    if (( v2_count == 0 && v1_count == 1 )); then printf '%s\n' "$v1_path"; return 0; fi
    return 1
}
```

- [ ] **Step 3: Реализовать resolver с explicit proc root**

```bash
resolve_unit_cgroup() {
    local unit_name="$1" active_state="$2" proc_root="$3"
    local control_group main_pid proc_file proc_cgroup_text resolved
    RESOLVED_BOUND_PORT_STATUS=""
    RESOLVED_CONTROL_GROUP=""
    control_group="$(systemctl show "$unit_name" --property=ControlGroup --value)"
    if [[ -n "$control_group" ]]; then
        safe_cgroup_path "$control_group" || emit_failure 73
        RESOLVED_BOUND_PORT_STATUS="cgroup_complete"
        RESOLVED_CONTROL_GROUP="$control_group"
        return 0
    fi
    main_pid="$(systemctl show "$unit_name" --property=MainPID --value)"
    [[ "$main_pid" =~ ^(0|[1-9][0-9]*)$ ]] || emit_failure 71
    (( main_pid <= 4194304 )) || emit_failure 71
    if (( main_pid == 0 )); then
        if [[ "$active_state" == "active" ]]; then
            RESOLVED_BOUND_PORT_STATUS="active_exited_no_live_process"
        else
            RESOLVED_BOUND_PORT_STATUS="no_cgroup"
        fi
        return 0
    fi
    proc_file="$proc_root/$main_pid/cgroup"
    [[ -r "$proc_file" ]] || emit_failure 72
    proc_cgroup_text="$(<"$proc_file")" || emit_failure 72
    resolved="$(parse_proc_cgroup_path "$proc_cgroup_text")" || emit_failure 73
    RESOLVED_BOUND_PORT_STATUS="mainpid_cgroup_complete"
    RESOLVED_CONTROL_GROUP="$resolved"
}
```

- [ ] **Step 4: Интегрировать resolver без ослабления ports_for_cgroup**

```bash
resolve_unit_cgroup "$unit_name" "$active_state" /proc
bound_port_status="$RESOLVED_BOUND_PORT_STATUS"
control_group="$RESOLVED_CONTROL_GROUP"
unit_ports=""
if [[ -n "$control_group" ]]; then
    CURRENT_STAGE="systemd_cgroup_ports"
    unit_ports="$(ports_for_cgroup "$control_group")"
fi
```

Static test дополнительно запрещает строку
`resolution="$(resolve_unit_cgroup`, чтобы emitter не оказался внутри
command substitution.

- [ ] **Step 5: Запустить RED subset до GREEN**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py -k "proc_cgroup_parser or unit_cgroup_resolver or mainpid_fallback"
```

Expected: PASS.

- [ ] **Step 6: Запустить весь focused файл**

Run: `python -m pytest -q tests/test_post_release_spain_readonly_preflight.py`

Expected: все Spain preflight tests PASS.

---

### Task 3: Новый single-use outcome run при immutable trust bundle

**Files:**
- Modify: `scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1`
- Modify: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: trust artifacts из `spain-fresh-20260720-001`.
- Produces: новый protected outcome directory/claim только для exact `spain-fresh-20260720-002`.

- [ ] **Step 1: Добавить RED assertions для разделения trust и outcome**

```python
def test_runner_reuses_immutable_trust_bundle_but_claims_new_outcome_run(self) -> None:
    source = RUNNER.read_text(encoding="utf-8")
    self.assertIn('$trustedBundleRunId = "spain-fresh-20260720-001"', source)
    self.assertIn('$expectedRunId = "spain-fresh-20260720-002"', source)
    self.assertIn('$TrustDirectory = Join-Path $ArtifactRoot $trustedBundleRunId', source)
    self.assertIn('$RunDirectory = Join-Path $ArtifactRoot $RunId', source)
    self.assertLess(source.index('Initialize-OutcomeDirectory'), source.index('Write-EvidenceCreateNew $OutcomeClaimPath'))
    self.assertNotIn('Remove-Item', source)
```

- [ ] **Step 2: Обновить approval literal и paths**

```powershell
$trustedBundleRunId = "spain-fresh-20260720-001"
$expectedRunId = "spain-fresh-20260720-002"
$TrustDirectory = Join-Path $ArtifactRoot $trustedBundleRunId
$RunDirectory = Join-Path $ArtifactRoot $RunId
$BindingPath = Join-Path $TrustDirectory "target.env"
$KeyPath = Join-Path $TrustDirectory "id_ed25519_spain"
$PublicKeyPath = "$KeyPath.pub"
$KnownHostsPath = Join-Path $TrustDirectory "known_hosts_spain"
```

Approval literal добавляет точный фрагмент:

```text
IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_002
```

- [ ] **Step 3: Создать новый outcome directory fail-closed после approval**

```powershell
function Initialize-OutcomeDirectory([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        throw "Single-use Spain outcome directory already exists."
    }
    [IO.Directory]::CreateDirectory($Path) | Out-Null
    Protect-PrivatePath $Path
    Assert-PrivatePath $Path
}
```

Вызвать после проверки immutable trust bundle и непосредственно перед
`Write-EvidenceCreateNew $OutcomeClaimPath`.

- [ ] **Step 4: Обновить approval/run-id tests и remote SHA binding**

Test ожидает `TRUST_RUN_ID_SPAIN_FRESH_20260720_002`, immutable bundle fragment
и точный SHA текущих remote bytes. Approval с `001` или любым иным RunId обязан
останавливаться до `Read-Binding`, directory creation и SSH.

- [ ] **Step 5: Запустить focused tests**

Run: `python -m pytest -q tests/test_post_release_spain_readonly_preflight.py`

Expected: PASS; embedded remote checksum совпадает.

---

### Task 4: Документация и evidence sync

**Files:**
- Modify: `docs/POST_RELEASE_SPAIN_READONLY_PREFLIGHT_GATE.ru.md`
- Modify: `docs/POST_RELEASE_SPAIN_PREFLIGHT_STAGE_DIAGNOSTIC_IMPLEMENTATION_EVIDENCE.ru.md`
- Modify: `docs/PROJECT_STATUS_CURRENT.ru.md`
- Create: `docs/POST_RELEASE_SPAIN_SYSTEMD_MAINPID_FALLBACK_IMPLEMENTATION_EVIDENCE.ru.md`
- Test: `tests/test_post_release_spain_readonly_preflight.py`

**Interfaces:**
- Consumes: final runner/remote SHA, test counts, security scan id.
- Produces: secret-free status, consumed run evidence и exact next gate.

- [ ] **Step 1: Зафиксировать consumed run без private runtime values**

Документы записывают только `remote_probe`, `systemd_inventory`, `67`, отсутствие
mutation и факт сохранения old claim/failure receipt. Unit name, PID, cgroup,
target и raw logs запрещены.

- [ ] **Step 2: Обновить runbook новым fallback contract**

Runbook описывает statuses `cgroup_complete`,
`active_exited_no_live_process`, `mainpid_cgroup_complete`, `no_cgroup`, exits
`71..73`, immutable trust bundle `001` и single-use outcome `002`.

- [ ] **Step 3: Создать implementation evidence**

Evidence содержит approvals `9654d77`, plan commit, RED/GREEN receipts, test
counts, parse/diff/security results и final public SHA. В нём явно указать:
`new_live_run=not_executed`.

---

### Task 5: Полная верификация, security review, commit/push/origin

**Files:**
- Review: все изменённые файлы Tasks 1–4.

**Interfaces:**
- Produces: доказанный локальный release candidate и новую approval preview.

- [ ] **Step 1: Scoped и full tests**

Run:

```powershell
python -m pytest -q tests/test_post_release_spain_readonly_preflight.py
python -m pytest -q tests
```

Expected: оба exit `0`, failures/errors `0`.

- [ ] **Step 2: Parse и diff checks**

Run:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -n scripts/vps/post_release_spain_readonly_preflight_remote.sh
[scriptblock]::Create((Get-Content -Raw scripts/vps/post_release_spain_readonly_preflight_ssh_runner.ps1)) | Out-Null
git diff --check
```

Expected: все exit `0`.

- [ ] **Step 3: Added-line secret scan**

Проверить только добавленные строки на private key marker, Spain/USA target
literals, root comment и public-key payload. Expected: `0` для каждой категории.

- [ ] **Step 4: Security diff review**

Применить `codex-security:security-diff-scan` ко всему точному change set.
Reportable findings исправлять отдельным RED/GREEN циклом; финальный snapshot
должен иметь full coverage и `0` незакрытых findings.

- [ ] **Step 5: Точечный commit и push**

Stage только plan/code/tests/status/evidence текущего slice. Не добавлять
посторонние untracked files. Commit message:

```text
Fix Spain systemd cgroup fallback
```

Push branch `codex-spark-phase9-docs-sync`, затем fetch и доказать
`HEAD == origin/codex-spark-phase9-docs-sync`.

- [ ] **Step 6: Безопасный approval preview**

Запустить runner с пустым approval и `RunId=approval-preview`. Expected:
одна буквальная строка с final runner SHA, remote SHA, source, immutable trust
bundle `001` и new outcome run `002`, затем останов до private state/SSH.

Новый непустой approval и SSH не выполнять в рамках implementation plan.
