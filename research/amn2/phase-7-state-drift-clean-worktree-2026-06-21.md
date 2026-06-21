# Phase 7 clean worktree state-drift guard

Date: 2026-06-21.

Status: `completed-clean-worktree-selected-no-live-action`.

Scope: local-only evidence/status guard after manual upstream-refresh and
mobile VPN acceptance debugging. No live VPS/SSH command, package upload/apply,
service restart, public exposure, config delivery, Telegram action,
restore/import/reboot, provider mutation, write execution or secret-bearing
output was performed.

## Reason

The original AMN2 checkout still contains older local work and is behind the
current Phase 7 branch. Continuing fixes there would mix pre-RC local edits with
the already pushed and VPS-smoked Phase 7 commits.

Phase 7 fixes must therefore use the clean AMN2 worktree:

```text
C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current
```

## Verified State

AMN3/evidence workspace:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB
branch=master
head=0122251 Record Windows desktop acceptance
status=clean
```

Clean AMN2 worktree:

```text
path=C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\amn2-phase7-current
branch=codex/phase7-current-fixes
tracking=amn2/codex-vps-test-prep
head=471bca8 Downgrade DefaultVPN iOS compatibility
status=clean
```

Historical dirty AMN2 checkout:

```text
path=C:\Users\SooL\Documents\Amneziya
branch=codex-vps-test-prep
head=b121865 Add multi instance conflict model
remote_state=behind amn2/codex-vps-test-prep by 4 commits
status=dirty
```

Observed dirty files in the historical checkout:

```text
app/services/fresh_install_wizard.py
app/services/integration_status.py
app/vpn/client_compatibility.py
docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md
docs/FRESH_INSTALL_WIZARD.ru.md
tests/api/test_api_integration_status.py
tests/services/test_fresh_install_wizard.py
tests/vpn/test_client_compatibility.py
docs/RELEASE_NOTES_RC_SKELETON.ru.md
```

## Current Phase 7 Truth

- AMN2 code work continues from clean `471bca8`.
- Latest VPS-smoked/package head remains `6d5cf3e` until a new exact package
  apply/smoke gate is opened.
- `471bca8` is local/pushed source policy work that downgraded DefaultVPN iOS
  from primary path to experimental/unreliable.
- Mobile acceptance is not closed. Android AmneziaWG 2.0.1 and real live-peer
  connectivity remain the next acceptance gap.
- The historical dirty checkout must be preserved only as a compare/porting
  input until explicitly reviewed.

## Stop Lines

Do not work in `C:\Users\SooL\Documents\Amneziya` for Phase 7 fixes unless a
separate state-merge/porting task is opened.

Do not open any of the following without a fresh exact named gate:

- public exposure, Cloudflare, ngrok or public tunnels;
- secret-bearing config delivery;
- write/install execution;
- backup restore/import/reboot;
- Telegram live send/profile/media mutation;
- destructive VPS/provider actions;
- upstream/GPL implementation copy.

## Result

`state_drift_guard_status=completed-clean-worktree-selected-no-live-action`.

The next local-only step is to execute the Phase 7 current-fixes plan from the
clean worktree. The next live diagnostic, if selected later, is a separate
read-only exact gate such as `P7-C011f` live AWG handshake observation.
