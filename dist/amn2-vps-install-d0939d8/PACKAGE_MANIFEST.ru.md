# Manifest установочного пакета `amn2`

Дата сборки: 2026-06-01.

Источник:

```text
repo: C:\Users\SooL\Documents\Amneziya
branch: codex-vps-test-prep
commit: d0939d8 Merge pull request #6 from barakov-dot/codex/ssh-host-key-identity-verifier
remote: https://github.com/barakov-dot/amn2.git
```

Содержимое папки:

```text
amn2-source-d0939d8.zip      исходники production-проекта из git archive
INSTALL_ON_VPS.ru.md         краткая инструкция установки на VPS
install_on_vps.sh            безопасный helper для распаковки и первичной установки
PACKAGE_MANIFEST.ru.md       этот manifest
SOURCE_FILE_LIST.txt         список tracked-файлов, попавших в source archive
SHA256SUMS.txt               SHA256 checksums файлов пакета
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
- локальные БД, runtime-файлы и любые рабочие секреты.

Границы безопасности:

- пакет не включает реальные Telegram/VPS/web-admin секреты;
- пакет не включает offline wheelhouse; Python-зависимости ставятся через
  `pip install -e .` из PyPI или вашего mirror;
- `VPS_APPLY_ENABLED` должен оставаться `false` до read-only/dry-run проверки;
- helper не включает systemd-сервисы автоматически;
- helper не выполняет live SSH/VPN mutations;
- `apply-peer --apply` и `revoke-peer --apply` требуют отдельного решения оператора.
