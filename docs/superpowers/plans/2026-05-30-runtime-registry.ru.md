# Runtime Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight runtime registry to the repository so VPS runtime requirements, examples, and read-only checks are easy to find and keep current.

**Architecture:** Keep runtime knowledge in `deploy/runtime` and `deploy/examples`, with human-facing docs in `docs`. Do not store secrets, databases, generated configs, Docker images, or virtual environments in Git.

**Tech Stack:** YAML, Bash, pytest, existing Python test runtime.

---

### Task 1: Runtime Registry Contract

**Files:**
- Create: `tests/deploy/test_runtime_registry.py`

- [x] **Step 1: Write failing tests**

Add tests that require:

```python
manifest_path = ROOT / "deploy/runtime/manifest.yml"
checker_path = ROOT / "deploy/runtime/check_vps.sh"
host_path = ROOT / "deploy/examples/servers.host_systemd.example.yml"
docker_path = ROOT / "deploy/examples/servers.docker.example.yml"
doc_path = ROOT / "docs/RUNTIME_REGISTRY.ru.md"
```

- [x] **Step 2: Verify RED**

Run:

```bash
python -m pytest tests/deploy/test_runtime_registry.py
```

Expected: fails because runtime registry files do not exist yet.

### Task 2: Manifest, Checker, And Examples

**Files:**
- Create: `deploy/runtime/manifest.yml`
- Create: `deploy/runtime/check_vps.sh`
- Create: `deploy/examples/servers.host_systemd.example.yml`
- Create: `deploy/examples/servers.docker.example.yml`
- Create: `deploy/examples/.env.production.example`
- Create: `deploy/examples/nginx-proxy-manager-notes.ru.md`

- [x] **Step 1: Add manifest**

Manifest must define:

```yaml
schema_version: 1
project: amn2
runtime_modes:
  host_systemd:
  docker:
```

- [x] **Step 2: Add read-only checker**

Checker must support:

```bash
bash deploy/runtime/check_vps.sh
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg bash deploy/runtime/check_vps.sh
```

It must not install packages, change firewall rules, restart services, remove files, or mutate Docker containers.

- [x] **Step 3: Add example configs**

Examples must parse as YAML and include exact runtime blocks:

```yaml
runtime:
  type: host_systemd
  service_name: awg-quick@awg0
```

```yaml
runtime:
  type: docker
  container_name: amnezia-awg
```

### Task 3: Documentation

**Files:**
- Create: `docs/RUNTIME_REGISTRY.ru.md`
- Create: `docs/RUNTIME_REGISTRY.en.md`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.ru.md`
- Modify: `docs/PRODUCTION_VPS_CHECKLIST.en.md`
- Modify: `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`
- Modify: `docs/SERVER_CONFIG_TEMPLATE.ru.md`
- Modify: `docs/SERVER_CONFIG_TEMPLATE.en.md`

- [x] **Step 1: Document Git policy**

Document that the repo stores manifests, checkers, examples, and docs, but not real `.env`, `servers.yml`, keys, databases, backups, generated configs, Docker images, virtual environments, or dependency folders.

- [x] **Step 2: Link examples and checker from setup docs**

Add copy commands:

```bash
cp deploy/examples/servers.host_systemd.example.yml servers.yml
cp deploy/examples/servers.docker.example.yml servers.yml
```

Add checker commands:

```bash
bash deploy/runtime/check_vps.sh
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg bash deploy/runtime/check_vps.sh
```

### Task 4: Verification And Commit

**Files:**
- All files above.

- [x] **Step 1: Run targeted tests**

```bash
python -m pytest tests/deploy/test_runtime_registry.py
```

Expected: all tests pass.

- [x] **Step 2: Run full tests**

```bash
python -m pytest tests
```

Expected: all tests pass.

- [x] **Step 3: Commit and push**

```bash
git add -A
git commit -m "Add runtime registry"
git push origin codex-vps-test-prep
```
