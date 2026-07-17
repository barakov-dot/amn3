# Phase 11 remote orchestrator transport binding hardening

Date: 2026-07-17.

Decision: `LOCAL-HARDENING-PASS-LIVE-GATE-NOT-CONSUMED`.

This slice fixes the local executable-resolution boundary identified by the
Phase 11 diff security review. It does not upload, apply, rollback or contact
the VPS, SSH target, Telegram, database, provider or AWG.

## Scope and invariant

Changed files:

- `scripts/vps/phase11_0b858c5_combined_ssh_runner.ps1`
- `tests/test_phase11_0b858c5_rollout_executor.py`

The reviewed remote executor remains byte-bound to SHA-256
`A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72`.
The exact approval phrase, package hash, pinned key and strict known-host
options remain unchanged in scope.

## Implemented hardening

- `ssh.exe` and `scp.exe` resolve only from the absolute system OpenSSH
  directory `%WINDIR%\System32\OpenSSH`.
- Both binaries are required to exist as regular files before any transport
  input is read or a process is started.
- `Invoke-CapturedProcess` rejects non-absolute paths and rejects every path
  outside the two trusted OpenSSH executable identities.
- Upload, chmod and preflight/postflight/apply transport call-sites pass the
  trusted variables; no bare `ssh.exe`/`scp.exe` call remains.
- The already reviewed remote script is read once as bytes, hashed, and the
  same byte array is sent to SSH stdin.

## Evidence

TDD and verification:

```text
focused Phase 11 tests: 9 passed
canonical tests suite: 95 passed
PowerShell parser: pass
Bash -n: pass
git diff --check: pass (only LF/CRLF normalization warnings)
```

Post-fix security rescan:

```text
bare_transport_calls=0
trusted_transport_calls=3
remote_sha=A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72
postfix_security_rescan=pass
```

The prior three medium/P2 unqualified-executable paths are closed by direct
counterevidence in the changed runner. No new reportable issue was found in
the bounded post-fix review.

## Safety boundary and next gate

No live operation was performed. Regular bot remains disabled, Telegram
profile remains unchanged, production database and web state are untouched,
and AWG remains untouched.

The next action is repository status synchronization, scoped final review,
intentional commit and push. A new, non-reusable approval phrase must be
prepared after origin verification; this fix does not authorize a live gate.
