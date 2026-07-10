# Phase 10 review packet for 5.6 SOL

Date: 2026-07-10.

Purpose: independent review input for AMN2 Phase 10 from source recovery at
`4326cae` through the single Android TV peer/config gate.

This packet contains no config payload, private key, PSK, token, `.env`,
`servers.yml`, raw Docker config or full logs.

## Scope Reviewed

```text
AMN2 source head=4326cae
VPS source-overlay smoke=passed
Android TV device_id=8
config_version=amneziawg_v2
server-side peer present=true
client acceptance=not proven
```

## Findings

### P1: owner was selected implicitly

The one-off gate selected the first active user. The resulting owner is active
but not admin, and there was no explicit operator choice proving that this is the
intended owner.

Required correction:

- require explicit `owner_user_id` or `owner_telegram_id`;
- verify that the owner exists and is active;
- never fall back to the first active user or create a synthetic owner;
- keep device `8` ownership provisional without mutation until Android TV
  import/connect acceptance identifies whether correction is needed.

### P1: working config was overclaimed

The peer exists in live AmneziaWG config and the generated file has AWG v2
shape, but the 2026-07-10 audit found no handshake and zero traffic. Current
status must remain `server-side-prepared-awaiting-device-acceptance`.

Required correction:

- import on the intended Android TV device;
- connect and generate traffic;
- verify a recent handshake and non-zero RX/TX for device `8`;
- only then record `working-config-pass`.

### P1: product workflow and audit were bypassed

The one-off script used private helpers and `repo._conn`. Device `8` has no
linked order and no target-device admin action. It also bypassed the normal
maximum-device check.

Required product slice:

```text
START_PHASE10_OPERATOR_SINGLE_DEVICE_CREATE_PATH_HARDENING_SLICE
```

The slice should provide a supported operator-only service/CLI entry point that
requires explicit owner, server, device name, duration and config version, while
using `AccessService` or an equivalent public orchestration boundary.

### P1: rollback coverage is incomplete

The script rolls back Docker config for Docker write/restart failures and one
`sqlite3.IntegrityError` case. Other failures after remote mutation, including
encryption/repository/config-output failures, can leave partial state.

Required correction:

- render and validate the client config before remote mutation;
- model remote-applied/local-failed as an explicit result;
- roll back or emit a deterministic reconciliation record for every exception;
- test remote success plus DB, encryption, audit and artifact-write failures.

### P2: secret-file permissions were initially too broad

The local `.conf` inherited Modify access for sandbox users. Two remote backup
files were `0644` inside a root-only directory.

Correction completed 2026-07-10:

```text
local_config_acl=SooL|SYSTEM|Administrators full-control only
remote_private_files=0600
remote_gate_script=0700
```

### P2: one-time gate consumption is not explicit enough

Historical/global stop-lines still say peer creation and config generation are
closed, while a one-device exact gate was consumed. This is safe in effect but
ambiguous in status text.

Required correction:

- record that the one-device scope was consumed and closed;
- keep global peer creation/config generation/config delivery disabled;
- require a fresh exact gate for any additional device or delivery action.

### P3: private artifact retention is undefined

The remote gate script, DB backup, raw pre-change server config and generated
config remain under `/root`. They are now root-only, but no retention deadline or
verified cleanup procedure is recorded.

Required correction:

- define retention purpose and expiry;
- verify the local private copy before cleanup;
- use a separately reviewed cleanup command that cannot target another run;
- retain safe summary/evidence without retaining unnecessary secret payloads.

## Questions For 5.6 SOL

1. Is a new operator-only orchestration service preferable to extending
   `AccessService.approve_order`, and what is the smallest public API that avoids
   private helper imports?
2. What transaction/reconciliation state machine best covers remote peer applied
   but DB/audit/artifact persistence failed?
3. Should private config artifact creation happen before DB commit, after DB
   commit, or through an encrypted temporary file with atomic rename?
4. How should one-time exact gates be represented so global stop-lines remain
   closed without contradictory status keys?
5. Which tests are mandatory before replacing the one-off script: owner
   selection, max-device enforcement, duplicate IP race, rollback matrix,
   artifact ACL/permissions, and post-connect handshake evidence?

## Recommended Order

```text
1=leave existing device 8 ownership provisional without mutation
2=implement supported operator single-device create path with tests
3=run Android TV import/connect acceptance when device is available
4=verify handshake, traffic and intended owner
5=correct owner only if proven wrong and record working-config-pass after evidence
6=perform separately reviewed private-artifact retention cleanup
```
