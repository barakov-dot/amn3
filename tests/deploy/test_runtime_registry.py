from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_manifest_describes_supported_modes_and_git_policy():
    manifest_path = ROOT / "deploy/runtime/manifest.yml"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["project"] == "amn2"
    assert set(manifest["runtime_modes"]) == {"host_systemd", "docker"}
    assert "docker" in manifest["runtime_modes"]["docker"]["required_commands"]
    assert "awg" in manifest["runtime_modes"]["host_systemd"]["required_commands"]
    assert "sshpass" in manifest["common"]["optional_commands"]
    assert "data" in manifest["common"]["project_dirs"]
    assert "config_templates" in manifest["common"]["project_dirs"]
    assert ".env" in manifest["git_policy"]["never_store"]
    assert "servers.yml" in manifest["git_policy"]["never_store"]
    assert "deploy/runtime/collect_debug_snapshot.sh" in manifest["diagnostics"]["scripts"]
    assert "APP_SECRET_KEY" in manifest["diagnostics"]["redacted_keys"]


def test_runtime_checker_is_read_only_and_knows_both_runtimes():
    checker_path = ROOT / "deploy/runtime/check_vps.sh"

    text = checker_path.read_text(encoding="utf-8")

    assert "AMN_RUNTIME" in text
    assert "host_systemd" in text
    assert "docker" in text
    assert "docker ps --format '{{.Names}}'" in text
    assert 'docker exec "$AMN_CONTAINER_NAME" awg show "$AMN_INTERFACE"' in text
    assert 'docker exec "$AMN_CONTAINER_NAME" command -v awg' not in text
    assert "systemctl is-active" in text
    assert "optional_command sshpass" in text
    for mutating in ("apt install", "systemctl restart", "docker rm", "rm -", "ufw allow"):
        assert mutating not in text


def test_debug_snapshot_script_is_read_only_and_redacts_secrets():
    script_path = ROOT / "deploy/runtime/collect_debug_snapshot.sh"

    text = script_path.read_text(encoding="utf-8")

    assert "AMN_RUNTIME" in text
    assert "AMN_LOG_LINES" in text
    assert "AMN_AGENT_PORT" in text
    assert "redact_stream" in text
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "APP_SECRET_KEY" in text
    assert "WEB_ADMIN_SESSION_SECRET" in text
    assert "LOCAL_AGENT_TOKEN_HASH" in text
    assert "python -m app.cli server check" in text
    assert "deploy/runtime/check_vps.sh" in text
    assert "systemctl is-active amneziya-agent" in text
    assert "journalctl -u amneziya-agent" in text
    assert "docker inspect" in text
    assert 'docker exec "$AMN_CONTAINER_NAME" awg show "$AMN_INTERFACE"' in text
    assert 'docker exec "$AMN_CONTAINER_NAME" command -v awg' not in text
    for mutating in ("apt install", "systemctl restart", "docker rm", "rm -", "ufw allow", "docker stop"):
        assert mutating not in text


def test_runtime_examples_are_parseable_and_cover_host_and_docker():
    host_path = ROOT / "deploy/examples/servers.host_systemd.example.yml"
    docker_path = ROOT / "deploy/examples/servers.docker.example.yml"

    host = yaml.safe_load(host_path.read_text(encoding="utf-8"))
    docker = yaml.safe_load(docker_path.read_text(encoding="utf-8"))

    assert host["servers"][0]["runtime"] == {
        "type": "host_systemd",
        "service_name": "awg-quick@awg0",
    }
    assert docker["servers"][0]["runtime"] == {
        "type": "docker",
        "container_name": "amnezia-awg",
        "config_path": "/opt/amnezia/awg/awg0.conf",
    }
    assert host["servers"][0]["vpn"]["port"] == 30001
    assert docker["servers"][0]["vpn"]["interface"] == "awg0"


def test_runtime_docs_point_to_manifest_checker_and_examples():
    doc_path = ROOT / "docs/RUNTIME_REGISTRY.ru.md"

    text = doc_path.read_text(encoding="utf-8")

    assert "deploy/runtime/manifest.yml" in text
    assert "deploy/runtime/check_vps.sh" in text
    assert "deploy/runtime/collect_debug_snapshot.sh" in text
    assert "deploy/examples/servers.docker.example.yml" in text
    assert "docker exec amnezia-awg command -v awg" not in text
    assert "Не храним в Git" in text


def test_vps_log_collection_doc_lists_commands_and_redaction_rules():
    doc_path = ROOT / "docs/VPS_LOG_COLLECTION.ru.md"

    text = doc_path.read_text(encoding="utf-8")

    assert "deploy/runtime/collect_debug_snapshot.sh" in text
    assert "git log -1 --oneline" in text
    assert "python -m app.cli server check" in text
    assert "docker ps --format" in text
    assert "docker exec amnezia-awg command -v awg" not in text
    assert "journalctl -u amneziya-web" in text
    assert "journalctl -u amneziya-agent" in text
    assert "tail -n 200 logs/app.log" in text
    assert "TELEGRAM_BOT_TOKEN" in text
    assert "APP_SECRET_KEY" in text


def test_local_agent_vps_smoke_runbook_lists_safe_install_and_checks():
    doc_path = ROOT / "docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md"
    local_agent_doc_path = ROOT / "docs/LOCAL_AGENT.ru.md"
    checklist_path = ROOT / "docs/PRODUCTION_VPS_CHECKLIST.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    local_agent_doc = local_agent_doc_path.read_text(encoding="utf-8")
    checklist = checklist_path.read_text(encoding="utf-8")

    assert "LOCAL_AGENT_ENABLED=true" in text
    assert "LOCAL_AGENT_HOST=127.0.0.1" in text
    assert "LOCAL_AGENT_TOKEN_HASH=sha256:" in text
    assert "LOCAL_AGENT_CONTROLLER_ENABLED=true" in text
    assert "LOCAL_AGENT_CONTROLLER_TOKEN_PATH=/opt/amn2/secrets/local-agent.token" in text
    assert "python -m app.cli agent hash-token" in text
    assert "install -m 0600" in text
    assert "read -rsp" in text
    assert "sudo install -m 0644 deploy/systemd/amneziya-agent.service.example /etc/systemd/system/amneziya-agent.service" in text
    assert "sudo systemctl enable --now amneziya-agent" in text
    assert "curl -fsS -H \"Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN\" http://127.0.0.1:3031/agent/health" in text
    assert "curl -fsS -H \"Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN\" http://127.0.0.1:3031/agent/runtime" in text
    assert "curl -fsS -H \"Authorization: Bearer $LOCAL_AGENT_RAW_TOKEN\" http://127.0.0.1:3031/agent/protocols" in text
    assert "python -m app.cli agent probe --base-url http://127.0.0.1:3031" in text
    assert "ssh -N -L 3031:127.0.0.1:3031" in text
    assert "bash deploy/runtime/collect_debug_snapshot.sh" in text
    assert "--host 0.0.0.0" not in text
    assert "LOCAL_AGENT_RAW_TOKEN=" not in text
    assert "docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md" in local_agent_doc
    assert "docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md" in checklist


def test_amn3_local_agent_smoke_checklist_tracks_current_branch_and_safe_paths():
    doc_path = ROOT / "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md"
    checklist_path = ROOT / "docs/PRODUCTION_VPS_CHECKLIST.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    checklist = checklist_path.read_text(encoding="utf-8")

    assert "https://github.com/barakov-dot/amn3.git" in text
    assert "codex/local-agent-production-wiring" in text
    assert "fdc471a" in text
    assert "git push -u origin codex/local-agent-production-wiring" in text
    assert "git fetch origin codex/local-agent-production-wiring" in text
    assert "LOCAL_AGENT_CONTROLLER_ENABLED=true" in text
    assert "LOCAL_AGENT_CONTROLLER_TOKEN_PATH=/opt/amn2/secrets/local-agent.token" in text
    assert "sudo install -m 0600 -o amneziya -g amneziya /dev/null /opt/amn2/secrets/local-agent.token" in text
    assert "sudo systemctl enable --now amneziya-agent" in text
    assert "python -m app.cli agent probe --base-url http://127.0.0.1:3031" in text
    assert "curl -i http://127.0.0.1:3030/login" in text
    assert "--host 0.0.0.0 --port 3031" not in text
    assert "LOCAL_AGENT_RAW_TOKEN=" not in text
    assert "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md" in checklist


def test_amn3_next_chat_handoff_points_to_current_integration_docs():
    doc_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"

    text = doc_path.read_text(encoding="utf-8")

    assert "https://github.com/barakov-dot/amn3.git" in text
    assert "codex/local-agent-production-wiring" in text
    assert "fdc471a" in text
    assert "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md" in text
    assert "docs/LOCAL_AGENT_VPS_SMOKE_RUNBOOK.ru.md" in text
    assert "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md" in text
    assert "git status --short --branch" in text
    assert "git log -5 --oneline --decorate" in text
    assert "python -m pytest tests/deploy/test_runtime_registry.py" in text
    assert "write API" in text
    assert "app/agent/write_contracts.py" in text
    assert "tests/agent/test_write_contracts.py" in text
    assert "Локально до реального VPS smoke" in text
    assert "Только после реального VPS smoke" in text
    assert "не включать write routes" in text


def test_local_agent_write_plan_separates_local_work_from_vps_gated_work():
    doc_path = ROOT / "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md"

    text = doc_path.read_text(encoding="utf-8")

    assert "## Execution Split" in text
    assert "### Local-Only Work Before VPS Smoke" in text
    assert "### VPS-Gated Work After Read-Only Smoke" in text
    assert "Можно делать локально до VPS" in text
    assert "Нельзя делать до VPS smoke" in text
    assert "Do not implement write routes before these gates are true." in text


def test_amn3_kyoresuas_api_analysis_records_local_candidates_without_code_copying():
    doc_path = ROOT / "docs/AMN3_KYORESUAS_API_ANALYSIS.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")

    assert "https://github.com/kyoresuas/amnezia-api" in text
    assert "Код не копируем" in text
    assert "MIT" in text
    assert "Fastify" in text
    assert "x-api-key" in text
    assert "AmneziaWG" in text
    assert "AmneziaWG 2.0" in text
    assert "Xray" in text
    assert "GET /clients" in text
    assert "POST /clients" in text
    assert "PATCH /clients" in text
    assert "DELETE /clients" in text
    assert "GET /server/load" in text
    assert "backup/import/reboot" in text
    assert "agent:clients:write" in text
    assert "dry-run" in text
    assert "не переносим как есть" in text
    assert "docs/AMN3_KYORESUAS_API_ANALYSIS.ru.md" in handoff


def test_amn3_write_api_policy_matrix_doc_tracks_vps_gated_scope_and_errors():
    doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")

    assert "app/agent/write_policy_matrix.py" in text
    assert "tests/agent/test_write_policy_matrix.py" in text
    assert "local_agent.clients.apply.dry_run" in text
    assert "local_agent.clients.apply" in text
    assert "local_agent.clients.revoke" in text
    assert "agent:clients:write" in text
    assert "state-write" in text
    assert "VPS smoke required" in text
    assert "preflight_required" in text
    assert "runtime_degraded" in text
    assert "mutation_failed" in text
    assert "не активирует маршруты" in text
    assert "не возвращает private key, PSK, QR или vpn://" in text
    assert "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md" in handoff


def test_amn3_vps_smoke_result_template_records_go_no_go_and_runtime_evidence():
    doc_path = ROOT / "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    smoke_path = ROOT / "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    smoke = smoke_path.read_text(encoding="utf-8")

    assert "Commit" in text
    assert "Runtime" in text
    assert "Local Agent status" in text
    assert "Web admin status" in text
    assert "Degraded reasons" in text
    assert "Rollback checked" in text
    assert "Go / no-go" in text
    assert "agent:clients:write" in text
    assert "raw token" in text
    assert "journalctl -u amneziya-agent" in text
    assert "bash deploy/runtime/collect_debug_snapshot.sh" in text
    assert "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md" in handoff
    assert "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md" in smoke


def test_amn3_write_api_ux_flow_doc_maps_surfaces_without_enabling_routes():
    doc_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")

    assert "dry-run -> confirmation -> apply/revoke -> audit -> rollback" in text
    assert "Web admin" in text
    assert "Telegram bot" in text
    assert "CLI" in text
    assert "local_agent.clients.apply.dry_run" in text
    assert "local_agent.clients.apply" in text
    assert "local_agent.clients.revoke" in text
    assert "agent:clients:write" in text
    assert "LOCAL_AGENT_WRITE_ENABLED" in text
    assert "VPS smoke required" in text
    assert "preflight_required" in text
    assert "runtime_degraded" in text
    assert "mutation_failed" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "docs/AMN3_WRITE_API_UX_FLOW.ru.md" in handoff
    assert "docs/AMN3_WRITE_API_UX_FLOW.ru.md" in policy_doc


def test_amn3_write_api_audit_model_doc_tracks_safe_audit_contracts():
    doc_path = ROOT / "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")

    assert "app/agent/write_audit.py" in text
    assert "tests/agent/test_write_audit.py" in text
    assert "web_admin" in text
    assert "telegram_bot" in text
    assert "cli" in text
    assert "dry_run_planned" in text
    assert "mutation_applied" in text
    assert "mutation_revoked" in text
    assert "mutation_failed" in text
    assert "rollback_applied" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "peer_public_key_fingerprint" in text
    assert "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md" in handoff
    assert "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md" in ux_flow
    assert "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md" in policy_doc


def test_amn3_write_audit_storage_decision_selects_app_db_and_redaction_boundaries():
    doc_path = ROOT / "docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    audit_doc_path = ROOT / "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    audit_doc = audit_doc_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")

    assert "Decision: application SQLite DB" in text
    assert "DATABASE_PATH" in text
    assert "local_agent_write_audit_events" in text
    assert "admin_actions is not the write audit store" in text
    assert "append-only JSONL mirror is fallback/export" in text
    assert "operation_id UNIQUE" in text
    assert "audit_id UNIQUE" in text
    assert "details_json" in text
    assert "peer_public_key_fingerprint" in text
    assert "no full peer_public_key" in text
    assert "record audit before mutation" in text
    assert "if audit write fails, block mutation" in text
    assert "encrypted backup" in text
    assert "app/db/schema.py" in text
    assert "app/db/repositories.py" in text
    assert "tests/db/test_repositories.py" in text
    assert "app/agent/write_audit.py" in text
    assert "tests/agent/test_write_audit.py" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md" in handoff
    assert "docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md" in audit_doc
    assert "docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md" in post_vps


def test_amn3_write_audit_storage_schema_plan_is_code_ready_without_enabling_routes():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    storage_decision_path = ROOT / "docs/AMN3_WRITE_AUDIT_STORAGE_DECISION.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    storage_decision = storage_decision_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")

    assert "# Local Agent Write Audit Storage Schema Implementation Plan" in text
    assert "pre-VPS code-ready plan" in text
    assert "does not implement storage before GO-1" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "no write routes" in text
    assert "local_agent_write_audit_events" in text
    assert "app/db/schema.py" in text
    assert "app/db/repositories.py" in text
    assert "tests/db/test_repositories.py" in text
    assert "tests/agent/test_write_audit.py" in text
    assert "app/agent/write_audit.py" in text
    assert "WriteAuditEvent" in text
    assert "record_write_audit_event" in text
    assert "list_write_audit_events_for_user" in text
    assert "list_write_audit_events_for_device" in text
    assert "list_write_audit_events_for_server" in text
    assert "operation_id UNIQUE" in text
    assert "audit_id UNIQUE" in text
    assert "details_json" in text
    assert "peer_public_key_fingerprint" in text
    assert "no full peer_public_key" in text
    assert "schema creates table and indexes idempotently" in text
    assert "repository rejects duplicate operation_id" in text
    assert "if audit write fails, block mutation" in text
    assert "encrypted backup" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "GO-1" in text
    assert "pytest tests/db/test_repositories.py tests/agent/test_write_audit.py" in text
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md" in storage_decision
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md" in post_vps


def test_amn3_local_agent_write_settings_contract_keeps_read_only_token_separate():
    doc_path = ROOT / "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    release_gate_path = ROOT / "docs/AMN3_LOCAL_RELEASE_GATE.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    release_gate = release_gate_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")

    assert "LOCAL_AGENT_WRITE_ENABLED=false remains default" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=true only after GO-1" in text
    assert "LOCAL_AGENT_TOKEN_SCOPES remains read-only" in text
    assert "agent:clients:write must not be added to LOCAL_AGENT_TOKEN_SCOPES" in text
    assert "dedicated write token set" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_ID" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_HASH" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_OWNER" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_EXPIRES_AT" in text
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in text
    assert "missing_scope" in text
    assert "VPS smoke required" in text
    assert "no write routes" in text
    assert "app/config/settings.py" in text
    assert "app/agent/config.py" in text
    assert "app/agent/auth.py" in text
    assert "tests/config/test_settings.py" in text
    assert "tests/agent/test_config.py" in text
    assert "tests/test_file_hygiene.py" in text
    assert ".env.example" in text
    assert "deploy/examples/.env.production.example" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md" in handoff
    assert "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md" in release_gate
    assert "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md" in post_vps
    assert "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md" in policy_doc


def test_amn3_local_agent_write_settings_implementation_plan_is_code_ready_and_safe():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md"
    contract_path = ROOT / "docs/AMN3_LOCAL_AGENT_WRITE_SETTINGS_CONTRACT.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    contract = contract_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")

    assert "# Local Agent Write Settings Implementation Plan" in text
    assert "GO-1" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=true" in text
    assert "LOCAL_AGENT_TOKEN_SCOPES remains read-only" in text
    assert "agent:clients:write must not be added to LOCAL_AGENT_TOKEN_SCOPES" in text
    assert "dedicated write token set" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_ID" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_HASH" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_OWNER" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_SCOPES" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_EXPIRES_AT" in text
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in text
    assert "build_agent_tokens" in text
    assert "parse_agent_scopes" in text
    assert "AgentToken" in text
    assert "missing_scope" in text
    assert "tests/config/test_settings.py" in text
    assert "tests/agent/test_config.py" in text
    assert "tests/agent/test_policy.py" in text
    assert "tests/test_file_hygiene.py" in text
    assert "app/config/settings.py" in text
    assert "app/agent/config.py" in text
    assert "app/agent/auth.py" in text
    assert ".env.example" in text
    assert "deploy/examples/.env.production.example" in text
    assert "read-only token" in text
    assert "write token" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "no write routes" in text
    assert "pytest tests/config/test_settings.py tests/agent/test_config.py tests/agent/test_policy.py tests/test_file_hygiene.py" in text
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md" in contract
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md" in post_vps


def test_amn3_local_agent_peer_command_adapter_plan_is_code_ready_and_vps_gated():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    write_api_plan_path = ROOT / "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    preflight_path = ROOT / "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md"
    identity_path = ROOT / "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    write_api_plan = write_api_plan_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    preflight = preflight_path.read_text(encoding="utf-8")
    identity = identity_path.read_text(encoding="utf-8")

    assert "# Local Agent Peer Command Adapter Implementation Plan" in text
    assert "GO-1" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=true" in text
    assert "app/agent/peer_commands.py" in text
    assert "tests/agent/test_peer_commands.py" in text
    assert "app/server/peer_apply.py" in text
    assert "app/agent/write_contracts.py" in text
    assert "app/agent/write_confirmation.py" in text
    assert "app/agent/write_audit.py" in text
    assert "AgentPeerApplyRequest" in text
    assert "AgentPeerRevokeRequest" in text
    assert "AgentPeerMutationResult" in text
    assert "LocalPeerCommandAdapter" in text
    assert "LocalRuntimeAdapter" in text
    assert "LocalRuntimeResult" in text
    assert "PeerCommandError" in text
    assert "build_peer_apply_dry_run" in text
    assert "build_peer_revoke_dry_run" in text
    assert "PeerApplyInput" in text
    assert "apply_peer" in text
    assert "revoke_peer" in text
    assert "host_systemd" in text
    assert "docker" in text
    assert "local commands only" in text
    assert "no SSH from inside Local Agent" in text
    assert "dry-run before mutation" in text
    assert "confirmation nonce" in text
    assert "rollback_reference" in text
    assert "peer_public_key_fingerprint" in text
    assert "user_id" in text
    assert "device_id" in text
    assert "client_id" in text
    assert "server_alias" in text
    assert "protocol=amneziawg" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "full client config" in text
    assert "pytest tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py" in text
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in post_vps
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in write_api_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in ux_flow
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in preflight
    assert "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md" in identity


def test_amn3_local_agent_write_endpoints_plan_wires_gates_without_opening_routes():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    write_api_plan_path = ROOT / "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md"
    settings_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-settings-implementation.ru.md"
    audit_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-audit-storage-schema.ru.md"
    peer_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md"
    preflight_path = ROOT / "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    write_api_plan = write_api_plan_path.read_text(encoding="utf-8")
    settings_plan = settings_plan_path.read_text(encoding="utf-8")
    audit_plan = audit_plan_path.read_text(encoding="utf-8")
    peer_plan = peer_plan_path.read_text(encoding="utf-8")
    preflight = preflight_path.read_text(encoding="utf-8")

    assert "# Local Agent Write Endpoints Implementation Plan" in text
    assert "GO-1" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=true" in text
    assert "agent:clients:write" in text
    assert "dedicated write token set" in text
    assert "read-only token remains read-only" in text
    assert "app/agent/api.py" in text
    assert "tests/agent/test_api.py" in text
    assert "app/agent/policy.py" in text
    assert "tests/agent/test_policy.py" in text
    assert "app/agent/config.py" in text
    assert "tests/agent/test_config.py" in text
    assert "app/agent/peer_commands.py" in text
    assert "tests/agent/test_peer_commands.py" in text
    assert "app/agent/write_contracts.py" in text
    assert "app/agent/write_confirmation.py" in text
    assert "app/agent/write_audit.py" in text
    assert "local_agent_write_audit_events" in text
    assert "POST /agent/clients/dry-run" in text
    assert "POST /agent/clients" in text
    assert "DELETE /agent/clients/{id}" in text
    assert "write_slice_policies" in text
    assert "get_policy() remains read-only" in text
    assert "create_agent_app" in text
    assert "write_enabled=False" in text
    assert "write_enabled=True" in text
    assert "LocalPeerCommandAdapter" in text
    assert "WritePreflightReference" in text
    assert "WriteConfirmationChallenge" in text
    assert "ensure_mutation_allowed" in text
    assert "WritePreflightRequiredError" in text
    assert "preflight_required" in text
    assert "runtime_degraded" in text
    assert "mutation_failed" in text
    assert "WriteAuditEvent" in text
    assert "audit write fails, block mutation" in text
    assert "rollback_reference" in text
    assert "peer_public_key_fingerprint" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "full client config" in text
    assert "pytest tests/agent/test_policy.py tests/agent/test_api.py tests/agent/test_peer_commands.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py tests/agent/test_write_audit.py" in text
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in post_vps
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in write_api_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in settings_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in audit_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in peer_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md" in preflight


def test_amn3_local_agent_controller_client_plan_wires_write_flow_without_secret_leakage():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    write_api_plan_path = ROOT / "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md"
    endpoints_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-write-endpoints-implementation.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    write_api_plan = write_api_plan_path.read_text(encoding="utf-8")
    endpoints_plan = endpoints_plan_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")

    assert "# Local Agent Controller Client Implementation Plan" in text
    assert "GO-1" in text
    assert "LOCAL_AGENT_CONTROLLER_BASE_URL" in text
    assert "LOCAL_AGENT_CONTROLLER_TOKEN_PATH" in text
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in text
    assert "read-only token" in text
    assert "write token" in text
    assert "dedicated write token set" in text
    assert "raw token" in text
    assert "bearer token" in text
    assert "LocalAgentClient" in text
    assert "AgentTransport" in text
    assert "AgentHttpResponse" in text
    assert "UrlLibAgentTransport" in text
    assert "app/agent/client.py" in text
    assert "tests/agent/test_client.py" in text
    assert "app/web/local_agent_actions.py" in text
    assert "app/web/server_health.py" in text
    assert "tests/web/test_server_health.py" in text
    assert "app/cli.py" in text
    assert "probe_local_agent_controller" in text
    assert "peer_apply_dry_run" in text
    assert "apply_peer" in text
    assert "revoke_peer" in text
    assert "POST /agent/clients/dry-run" in text
    assert "POST /agent/clients" in text
    assert "DELETE /agent/clients/{id}" in text
    assert "AgentPeerApplyRequest" in text
    assert "AgentPeerRevokeRequest" in text
    assert "AgentPeerMutationResult" in text
    assert "WritePreflightReference" in text
    assert "WriteConfirmationChallenge" in text
    assert "dry-run -> confirmation -> apply/revoke -> audit -> rollback" in text
    assert "preflight_required" in text
    assert "runtime_degraded" in text
    assert "mutation_failed" in text
    assert "missing_scope" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "full client config" in text
    assert "do not log Authorization" in text
    assert "pytest tests/agent/test_client.py tests/web/test_server_health.py tests/agent/test_write_contracts.py tests/agent/test_write_confirmation.py" in text
    assert "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md" in post_vps
    assert "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md" in write_api_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md" in endpoints_plan
    assert "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md" in ux_flow


def test_amn3_web_admin_preflight_ux_plan_wires_operator_flow_without_enabling_mutations():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    write_api_plan_path = ROOT / "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md"
    controller_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-local-agent-controller-client-implementation.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    write_api_plan = write_api_plan_path.read_text(encoding="utf-8")
    controller_plan = controller_plan_path.read_text(encoding="utf-8")

    assert "# Web Admin Preflight UX Implementation Plan" in text
    assert "GO-1" in text
    assert "Phase 4 - web admin preflight" in text
    assert "LOCAL_AGENT_WRITE_ENABLED" in text
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in text
    assert "agent:clients:write" in text
    assert "dry-run -> confirmation -> apply/revoke -> audit -> rollback" in text
    assert "run_local_agent_peer_apply_preflight" in text
    assert "run_local_agent_peer_apply_confirmation" in text
    assert "run_local_agent_peer_revoke_preflight" in text
    assert "run_local_agent_peer_revoke_confirmation" in text
    assert "peer_apply_dry_run" in text
    assert "apply_peer" in text
    assert "revoke_peer" in text
    assert "WritePreflightReference" in text
    assert "WriteConfirmationChallenge" in text
    assert "AgentPeerApplyRequest" in text
    assert "AgentPeerRevokeRequest" in text
    assert "AgentPeerMutationResult" in text
    assert "preflight_required" in text
    assert "runtime_degraded" in text
    assert "mutation_failed" in text
    assert "expired_preflight" in text
    assert "confirmation nonce" in text
    assert "one click mutation" in text
    assert "POST /servers/{server_id}/devices/{device_id}/agent/apply/preview" in text
    assert "POST /servers/{server_id}/devices/{device_id}/agent/apply/confirm" in text
    assert "POST /servers/{server_id}/peers/{client_id}/agent/revoke/preview" in text
    assert "POST /servers/{server_id}/peers/{client_id}/agent/revoke/confirm" in text
    assert "Preview peer apply" in text
    assert "Confirm apply" in text
    assert "Revoke peer" in text
    assert "Apply blocked" in text
    assert "app/web/app.py" in text
    assert "app/web/local_agent_actions.py" in text
    assert "app/web/server_health.py" in text
    assert "app/web/templates/server_detail.html" in text
    assert "app/web/templates/server_health.html" in text
    assert "app/web/static/admin.css" in text
    assert "tests/web/test_app.py" in text
    assert "tests/web/test_server_health.py" in text
    assert "tests/security/test_redaction.py" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "full client config" in text
    assert "do not log Authorization" in text
    assert "pytest tests/web/test_app.py tests/web/test_server_health.py tests/security/test_redaction.py" in text
    assert "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md" in post_vps
    assert "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md" in ux_flow
    assert "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md" in write_api_plan
    assert "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md" in controller_plan


def test_amn3_preflight_confirmation_doc_tracks_nonce_expiry_and_vps_gate():
    doc_path = ROOT / "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")

    assert "app/agent/write_confirmation.py" in text
    assert "tests/agent/test_write_confirmation.py" in text
    assert "dry-run reference" in text
    assert "confirmation nonce" in text
    assert "nonce_fingerprint" in text
    assert "expires_at_epoch" in text
    assert "preflight_required" in text
    assert "ensure_mutation_allowed" in text
    assert "LOCAL_AGENT_WRITE_ENABLED" in text
    assert "VPS smoke required" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md" in handoff
    assert "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md" in ux_flow
    assert "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md" in policy_doc


def test_amn3_user_device_peer_identity_model_defines_stable_terms_and_links():
    doc_path = ROOT / "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    audit_doc_path = ROOT / "docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md"
    preflight_doc_path = ROOT / "docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    audit_doc = audit_doc_path.read_text(encoding="utf-8")
    preflight_doc = preflight_doc_path.read_text(encoding="utf-8")

    assert "user_id" in text
    assert "device_id" in text
    assert "client_id" in text
    assert "peer_public_key" in text
    assert "peer_public_key_fingerprint" in text
    assert "device_label" in text
    assert "server_alias" in text
    assert "amneziawg" in text
    assert "one user -> many devices" in text
    assert "one device -> one active peer per server" in text
    assert "client_id is controller-owned" in text
    assert "peer_public_key is runtime-owned" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "raw token" in text
    assert "agent:clients:write" in text
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in handoff
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in policy_doc
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in ux_flow
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in audit_doc
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in preflight_doc


def test_amn3_vps_test_packet_coordinates_neighbor_chat_smoke_run():
    doc_path = ROOT / "docs/AMN3_VPS_TEST_PACKET.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    smoke_path = ROOT / "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    smoke = smoke_path.read_text(encoding="utf-8")

    assert "Переводим AMN на API" in text
    assert "https://github.com/barakov-dot/amn3.git" in text
    assert "codex/local-agent-production-wiring" in text
    assert "/opt/amn2" in text
    assert "git fetch origin codex/local-agent-production-wiring" in text
    assert "git log -1 --oneline --decorate" in text
    assert "python -m app.cli agent probe --base-url http://127.0.0.1:3031" in text
    assert "bash deploy/runtime/collect_debug_snapshot.sh" in text
    assert "docs/AMN3_LOCAL_AGENT_VPS_SMOKE_CHECKLIST.ru.md" in text
    assert "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "write routes" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "Go / no-go" in text
    assert "docs/AMN3_VPS_TEST_PACKET.ru.md" in handoff
    assert "docs/AMN3_VPS_TEST_PACKET.ru.md" in smoke


def test_amn3_local_release_gate_locks_write_api_until_vps_smoke():
    doc_path = ROOT / "docs/AMN3_LOCAL_RELEASE_GATE.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    policy_doc_path = ROOT / "docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    policy_doc = policy_doc_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")

    assert "LOCAL_AGENT_WRITE_ENABLED=false" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=true" in text
    assert "/agent/clients*" in text
    assert "agent:clients:write" in text
    assert "read-only token" in text
    assert "VPS smoke required" in text
    assert "get_policy()" in text
    assert "tests/agent/test_policy.py" in text
    assert "tests/test_file_hygiene.py" in text
    assert "docs/AMN3_VPS_TEST_PACKET.ru.md" in text
    assert "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md" in text
    assert "Go / no-go" in text
    assert "docs/AMN3_LOCAL_RELEASE_GATE.ru.md" in handoff
    assert "docs/AMN3_LOCAL_RELEASE_GATE.ru.md" in policy_doc
    assert "docs/AMN3_LOCAL_RELEASE_GATE.ru.md" in ux_flow


def test_amn3_post_vps_implementation_map_links_smoke_evidence_to_write_api_tasks():
    doc_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    release_gate_path = ROOT / "docs/AMN3_LOCAL_RELEASE_GATE.ru.md"
    smoke_result_path = ROOT / "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    release_gate = release_gate_path.read_text(encoding="utf-8")
    smoke_result = smoke_result_path.read_text(encoding="utf-8")

    assert "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md" in text
    assert "docs/AMN3_LOCAL_RELEASE_GATE.ru.md" in text
    assert "docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md" in text
    assert "docs/superpowers/plans/2026-05-31-local-agent-write-api-slice.ru.md" in text
    assert "GO-1" in text
    assert "NO-GO" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false -> true" in text
    assert "Phase 0 - VPS evidence intake" in text
    assert "Phase 1 - write policy activation" in text
    assert "Phase 2 - Local Agent endpoints" in text
    assert "Phase 3 - controller client" in text
    assert "Phase 4 - web admin preflight" in text
    assert "Phase 5 - first VPS mutation test" in text
    assert "app/agent/policy.py" in text
    assert "app/agent/api.py" in text
    assert "app/agent/client.py" in text
    assert "app/agent/peer_commands.py" in text
    assert "app/agent/write_contracts.py" in text
    assert "app/agent/write_confirmation.py" in text
    assert "app/agent/write_audit.py" in text
    assert "app/agent/write_policy_matrix.py" in text
    assert "tests/agent/test_policy.py" in text
    assert "tests/agent/test_api.py" in text
    assert "tests/agent/test_client.py" in text
    assert "tests/agent/test_peer_commands.py" in text
    assert "agent:clients:write" in text
    assert "dry-run -> confirmation -> apply/revoke -> audit -> rollback" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md" in handoff
    assert "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md" in release_gate
    assert "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md" in smoke_result


def test_amn3_first_vps_mutation_test_plan_coordinates_apply_revoke_without_secret_leakage():
    plan_path = ROOT / "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md"
    handoff_path = ROOT / "docs/AMN3_NEXT_CHAT_HANDOFF.ru.md"
    post_vps_path = ROOT / "docs/AMN3_POST_VPS_IMPLEMENTATION_MAP.ru.md"
    vps_packet_path = ROOT / "docs/AMN3_VPS_TEST_PACKET.ru.md"
    smoke_result_path = ROOT / "docs/AMN3_VPS_SMOKE_RESULT_TEMPLATE.ru.md"
    ux_flow_path = ROOT / "docs/AMN3_WRITE_API_UX_FLOW.ru.md"
    web_admin_plan_path = ROOT / "docs/superpowers/plans/2026-06-01-web-admin-preflight-ux-implementation.ru.md"

    text = plan_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    post_vps = post_vps_path.read_text(encoding="utf-8")
    vps_packet = vps_packet_path.read_text(encoding="utf-8")
    smoke_result = smoke_result_path.read_text(encoding="utf-8")
    ux_flow = ux_flow_path.read_text(encoding="utf-8")
    web_admin_plan = web_admin_plan_path.read_text(encoding="utf-8")

    assert "# First VPS Mutation Test Implementation Plan" in text
    assert "Phase 5 - first VPS mutation test" in text
    assert "GO-2" in text
    assert "GO-1" in text
    assert "LOCAL_AGENT_WRITE_ENABLED=false -> true -> false" in text
    assert "LOCAL_AGENT_CONTROLLER_WRITE_TOKEN_PATH" in text
    assert "LOCAL_AGENT_WRITE_TOKEN_SCOPES=agent:clients:write" in text
    assert "test-only user/device/peer binding" in text
    assert "dry-run -> confirmation -> apply/revoke -> audit -> rollback" in text
    assert "Preview peer apply" in text
    assert "Confirm apply" in text
    assert "Revoke peer" in text
    assert "POST /agent/clients/dry-run" in text
    assert "POST /agent/clients" in text
    assert "DELETE /agent/clients/{id}" in text
    assert "python -m app.cli agent probe --base-url http://127.0.0.1:3031" in text
    assert "curl -fsS -H \"Authorization: Bearer $LOCAL_AGENT_WRITE_TOKEN\" http://127.0.0.1:3031/agent/clients/dry-run" in text
    assert "journalctl -u amneziya-agent -n 200 --no-pager" in text
    assert "bash deploy/runtime/collect_debug_snapshot.sh" in text
    assert "audit event" in text
    assert "rollback_reference" in text
    assert "peer_public_key_fingerprint" in text
    assert "runtime state" in text
    assert "revoke or rollback" in text
    assert "NO-GO" in text
    assert "Decision: go | no-go" in text
    assert "raw token" in text
    assert "private key" in text
    assert "PSK" in text
    assert "QR" in text
    assert "vpn://" in text
    assert "full client config" in text
    assert "do not paste secrets" in text
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in handoff
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in post_vps
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in vps_packet
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in smoke_result
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in ux_flow
    assert "docs/superpowers/plans/2026-06-01-first-vps-mutation-test.ru.md" in web_admin_plan


def test_vps_retest_protocol_doc_lists_repeatable_test_steps():
    doc_path = ROOT / "docs/VPS_RETEST_PROTOCOL.ru.md"
    checklist_path = ROOT / "docs/PRODUCTION_VPS_CHECKLIST.ru.md"

    text = doc_path.read_text(encoding="utf-8")
    checklist = checklist_path.read_text(encoding="utf-8")

    assert "git pull origin codex-vps-test-prep" in text
    assert "git log -1 --oneline" in text
    assert "python -m pip install -e ." in text
    assert "python -m app.cli bot check-network" in text
    assert "python -m app.cli server check --config servers.yml --server debian-vps-1 --dry-run" in text
    assert "bash deploy/runtime/check_vps.sh" in text
    assert "AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/collect_debug_snapshot.sh" in text
    assert "что нажимал" in text
    assert "docs/VPS_RETEST_PROTOCOL.ru.md" in checklist
