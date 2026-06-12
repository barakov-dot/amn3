# Amnezia VPN / DefaultVPN upstream refresh 2026-06-12

Дата: 2026-06-12.

Источник:

- GitHub API: `https://api.github.com/repos/amnezia-vpn/amnezia-client`
- GitHub API: `https://api.github.com/repos/amnezia-vpn/DefaultVPN`
- GitHub release API: `https://api.github.com/repos/amnezia-vpn/amnezia-client/releases/latest`

Лицензия/граница:

- upstream code, UI, templates and workflows were not copied;
- this note records public metadata and product compatibility signals only;
- any AMN2 implementation must remain independent and locally tested.

## Freshness

GitHub metadata checked on 2026-06-12:

- `amnezia-vpn/amnezia-client`: default branch `dev`, branch head `594635e5cfcfb74ece31cb7e8a6b0536b56d1bca`, repository `pushed_at=2026-06-12T09:44:43Z`;
- `amnezia-vpn/amnezia-client` latest release: `4.8.18.0`, `published_at=2026-06-11T04:48:30Z`, `updated_at=2026-06-11T10:04:23Z`;
- release assets currently include Android 9+ APKs, `AmneziaVPN_4.8.18.0_linux_x64.tar`, macOS pkg and Windows x64 exe;
- `amnezia-vpn/DefaultVPN`: default branch `dev`, branch head `d139fb55704cbe0e867ab947208b2905f769572f`, repository `pushed_at=2026-06-11T04:16:05Z`;
- `DefaultVPN` has no latest GitHub release endpoint result at this check (`404 Not Found`).

## Compatibility Signal

The previous 2026-06-11 matrix already captured the main import guidance: `.conf` remains the reliable fallback, `vpn://` should remain separate/copyable, QR must not be promised as universal, and native `.vpn` / Amnezia JSON delivery stays behind a separate config-delivery design gate.

The 2026-06-12 release asset list refines Linux wording:

- AMN2 should not keep saying that Debian 12 / Ubuntu 22.04.x builds are simply unavailable as the only Linux guidance;
- AMN2 may say that a generic Linux x64 tar is available in the current upstream release;
- AMN2 must still avoid promising distro-specific packages or universal Linux install support;
- Linux GUI dependency caveats remain relevant.

## AMN2 Action

Closed by AMN2 commit `dd0dd44 Refresh client platform guidance` on branch `codex-vps-test-prep`.

The commit updates:

- `app/vpn/client_compatibility.py`;
- `tests/vpn/test_client_compatibility.py`;
- `docs/WEB_PANEL_AND_BOT_SETUP.ru.md`.

## Negative Controls

- No upstream code copied.
- No live VPS command.
- No SSH command.
- No deploy/restart/package apply on VPS.
- No public exposure.
- No real config delivery.
- No Telegram token use or live bot send.
- No write API or Local Agent mutation.
- No backup/import/reboot.
- No production peer/user mutation.
- No secret-bearing evidence stored.
