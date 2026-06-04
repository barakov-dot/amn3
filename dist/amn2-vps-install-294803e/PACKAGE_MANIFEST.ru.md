# Manifest установочного пакета `amn2`

Дата сборки: 2026-06-04.

Источник:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
commit: 294803e Add API readiness and token web pages
full commit: 294803e24fc579c75c4630a1ae6b2afac6776443
remote: https://github.com/barakov-dot/amn2.git
```

Содержимое пакета:

```text
amn2-source-294803e.zip      tracked production source from git archive
INSTALL_ON_VPS.ru.md         operator install instructions
install_on_vps.sh            install helper for fresh VPS setup
amn2_api_loopback_smoke.sh   API-only loopback smoke helper, script version 2026-06-04.2
PACKAGE_MANIFEST.ru.md       this manifest
SOURCE_FILE_LIST.txt         tracked files included in source archive
SHA256SUMS.txt               SHA256 checksums
```

Исключено намеренно:

- `.env`;
- `.git`;
- `.pytest_cache`;
- `tmp`;
- `errors_logs`;
- `data`;
- `logs`;
- `backups`;
- local DB, runtime files and private operator files.

Safety notes:

- пакет не содержит Telegram/VPS/web-admin/API secrets;
- пакет не содержит offline wheelhouse; Python dependencies are installed through `pip install -e .`;
- `VPS_APPLY_ENABLED` must remain `false` for first API/web-panel checks;
- helper does not run live SSH/VPN mutations;
- API smoke remains loopback-only;
- web-panel test must use `127.0.0.1` plus SSH tunnel unless a separate public exposure gate is approved.
