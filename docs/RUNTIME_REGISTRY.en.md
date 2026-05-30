# Runtime Registry

This document records the runtime dependencies for Amneziya, where they live in the repository, and how to verify a VPS before another production test.

## Stored In Git

The repository stores lightweight, auditable artifacts only:

- `deploy/runtime/manifest.yml` - runtime requirement manifest;
- `deploy/runtime/check_vps.sh` - read-only VPS checker;
- `deploy/runtime/collect_debug_snapshot.sh` - read-only debug snapshot collector;
- `deploy/examples/servers.host_systemd.example.yml` - host/systemd server config example;
- `deploy/examples/servers.docker.example.yml` - Docker server config example;
- `deploy/examples/.env.production.example` - production `.env` template without real secrets;
- `deploy/examples/nginx-proxy-manager-notes.ru.md` - reverse proxy notes for the web panel.

## Not Stored In Git

Do not store real `.env`, `servers.yml`, SSH private keys, bot tokens, `APP_SECRET_KEY`, SQLite databases, backup archives, generated client configs, QR images, Docker images, virtual environments, `node_modules`, or logs with private data.

If heavy artifacts are needed later, put them in GitHub Releases or separate storage. Keep only URL, version, and checksum in the repository.

## Quick VPS Check

Host/systemd runtime:

```bash
cd /opt/amn2
bash deploy/runtime/check_vps.sh
```

Docker runtime:

```bash
cd /opt/amn2
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/check_vps.sh
```

The script does not install packages, change firewall rules, restart services, or write files. It only reads VPS state and exits with code `1` when critical errors are found.

## Debug Snapshot

When a full VPS report is needed:

```bash
cd /opt/amn2
bash deploy/runtime/collect_debug_snapshot.sh
```

For Docker runtime:

```bash
cd /opt/amn2
AMN_RUNTIME=docker AMN_CONTAINER_NAME=amnezia-awg AMN_INTERFACE=awg0 bash deploy/runtime/collect_debug_snapshot.sh
```

The detailed command list and redaction rules are documented in `docs/VPS_LOG_COLLECTION.ru.md`.
