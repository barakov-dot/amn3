# SSH Host Key Enrollment Design

Дата: 2026-06-01.

Назначение: зафиксировать safe design для SSH host key enrollment/pinning перед расширением VPS onboarding, web/API remote operations и автоматизированного управления серверами в `amn2`.

Этот документ не является implementation plan. Он не меняет `amn2`, не подключается к VPS, не читает `.env`, не добавляет remote operations и не разрешает live mutation. Он задает policy boundary: production-mode не должен автоматически доверять неизвестному SSH host key.

## Current production baseline

Verified `amn2` baseline уже содержит осторожный remote-operation foundation:

- `server check` использует read-only command allowlist;
- `RemoteOperationRunner` first slice закрывает read-only health operation;
- state-changing dry-run/audit metadata подготовлены в candidate branch `codex/remote-operation-vps-gate-prep`;
- live apply/revoke остается behind explicit operator gate;
- секреты remote operations проходят redaction, PSK не вставляется в remote command string.

Текущий SSH слой:

```text
app/server/ssh.py::SystemSshClient
```

Observed behavior:

- key auth вызывает system `ssh` с `BatchMode=yes`, `ConnectTimeout`, optional `-i`;
- key auth полагается на стандартный OpenSSH `known_hosts` behavior;
- password auth использует `sshpass -e` и `SSHPASS`, не кладет пароль в argv;
- password auth сейчас задает `StrictHostKeyChecking=accept-new`, что удобно для first connect, но не является production-safe onboarding policy;
- в `servers.yml` нет host key fingerprint / known_hosts pin;
- dedicated host key enrollment/pinning flow в `amn2` пока отсутствует.

## Problem

Автоматическое доверие неизвестному SSH host key создает MITM risk именно там, где `amn2` получает высокий remote-control доступ:

- read-only health может раскрывать topology/runtime metadata;
- future apply/revoke меняет VPN peers;
- future install/clear/reboot/backup/import будут high-risk;
- password auth особенно чувствителен, потому что operator credential передается в SSH session.

Поэтому first connection to VPS must be an enrollment event, not a silent side effect of the first remote command.

## Decision

Status: `design-prepared-local-docs`.

Для ближайшего real VPS gate:

- не внедрять новый код;
- добавить Phase 0 evidence: operator confirms SSH host key is already verified/pinned outside AMN3 notes;
- не копировать host public key, private key, password или full `known_hosts` в AMN3/GitHub/chat;
- если SSH client prompts about unknown host key during the gate, stop and verify out-of-band before continuing.

Для будущего `amn2` implementation:

- add app-managed SSH host key enrollment/pinning before any new VPS onboarding or web/API remote operation expansion;
- block live SSH when host key is missing or mismatched;
- allow dry-run commands that do not open SSH;
- make re-enrollment explicit, audited and operator-confirmed.

## Approaches considered

| Approach | Fit | Tradeoff |
| --- | --- | --- |
| Rely only on operator `~/.ssh/known_hosts` | Fits current CLI quickly | Hard to test, hard to audit, hidden trust state |
| App-managed pinned fingerprint only | Best long-term control | Requires schema/config changes and migration plan |
| Hybrid staged model | Recommended | Current gate uses operator verification; future code gets app-managed pinning before route expansion |

Recommended: hybrid staged model.

It avoids blocking the already prepared controlled VPS gate, but prevents accidental normalization of `accept-new` as product behavior.

## Host identity model

Future `amn2` should represent host key identity separately from SSH credentials.

Suggested logical record:

```text
SshHostKeyIdentity
  server_name or server_id
  host
  port
  key_type
  sha256_fingerprint
  public_host_key_material: optional public known_hosts value
  source: operator-confirmed | imported-known-hosts | provider-console | migration
  status: pending | enrolled | mismatch | retired
  enrolled_at
  enrolled_by
  last_verified_at
  rotated_at
  rotation_reason
```

Notes:

- host public key is not a credential-secret, but it is topology-sensitive metadata;
- fingerprint is safe for audit/evidence;
- private SSH keys and passwords are not part of this model;
- changing `host` or `port` invalidates the existing enrollment until re-confirmed.

## Enrollment flow

First enrollment flow:

1. Operator creates or selects server record.
2. System fetches candidate host public key without running arbitrary remote commands.
3. System displays key type and SHA256 fingerprint.
4. Operator verifies fingerprint through an out-of-band channel:
   - VPS provider console;
   - trusted previous `known_hosts`;
   - direct console session;
   - documented manual verification during maintenance window.
5. Operator confirms enrollment.
6. System stores pinned identity.
7. Audit writes `ssh_host_key.enrolled` without secrets.

Important: `ssh-keyscan` can collect a candidate key, but it cannot prove trust by itself. A design that says "run ssh-keyscan and auto-save" is still auto-trust and should be rejected.

## Verification behavior

Before any SSH-backed operation:

| State | Dry-run without SSH | Read-only SSH | Remote state-write |
| --- | --- | --- | --- |
| No host key enrolled | allowed | blocked by default | blocked |
| Host key matches pin | allowed | allowed | allowed if other operation gates pass |
| Host key mismatch | allowed | blocked | blocked |
| Host changed/port changed | allowed | blocked until re-enrollment | blocked until re-enrollment |
| Explicit insecure dev mode | allowed | allowed only in local/dev with visible warning | never allowed for production live mutation |

Mismatch response must be safe and firm:

- show server alias, host, port, expected fingerprint, observed fingerprint;
- do not offer "continue anyway" for production;
- tell operator to verify whether the VPS was reinstalled, DNS/IP changed, or there is a possible MITM;
- require re-enrollment flow if the change is legitimate.

## OpenSSH integration boundary

Future `SystemSshClient` should not rely on ambient global `known_hosts` for product guarantees.

Preferred production behavior:

- generate a temporary or managed `known_hosts` file from the pinned identity;
- call OpenSSH with `StrictHostKeyChecking=yes`;
- use `UserKnownHostsFile=<managed-known-hosts-file>`;
- optionally use `HostKeyAlias=<stable-server-id>` so IP/hostname changes are handled intentionally;
- never use `StrictHostKeyChecking=accept-new` in production live mode.

Password auth remains degraded:

- prefer SSH key auth;
- if password auth is enabled, host key verification must happen before password authentication;
- password auth must not weaken host key checks;
- warning text should say password auth is temporary/degraded and requires stricter operator care.

## Re-enrollment and rotation

Legitimate host key changes happen after VPS reinstall, SSH server regeneration or provider migration.

Re-enrollment requirements:

- existing pin moves to `retired` or audit history remains available;
- new candidate fingerprint is shown;
- operator must confirm out-of-band verification;
- audit event `ssh_host_key.reenrolled` records old fingerprint, new fingerprint, reason and actor;
- live operations stay blocked until re-enrollment completes.

Do not automatically replace a mismatched key during a failed SSH command.

## Backup/restore policy

Redacted backup may include:

- server alias;
- host key fingerprint;
- key type;
- enrollment status;
- timestamps and audit metadata.

Redacted backup should not include:

- SSH private key;
- SSH password;
- full operator `known_hosts`;
- provider console screenshots or raw evidence notes.

Restore default:

- restored host key pins may be restored as metadata;
- if server host/port differs after restore, mark pin as requiring revalidation;
- full trust should not be silently transferred to a new host/IP.

## Audit policy

Audit events:

```text
ssh_host_key.candidate_seen
ssh_host_key.enrolled
ssh_host_key.verified
ssh_host_key.mismatch_blocked
ssh_host_key.reenrolled
ssh_host_key.retired
```

Audit payload may include:

```text
server_id/server_name
host
port
key_type
expected_fingerprint
observed_fingerprint
decision
actor_id
request_id
```

Audit payload must not include:

```text
SSH private key
SSH password
VPS_SSH_PASSWORD
raw command output with secrets
full operator notes
```

## Current VPS gate Phase 0

The prepared VPS gate can proceed only after operator-side host key verification is acknowledged.

Minimum Phase 0 evidence:

```text
host key verified/pinned outside AMN3: yes/no
verification method: provider-console | existing-known-hosts | direct-console | other-redacted
server alias:
host/port:
fingerprint suffix or hash prefix: optional, no private material
```

If `yes/no` is `no`, stop before any live SSH command and perform verification outside AMN3 notes.

This does not replace future app-managed enrollment. It is a temporary bridge for the controlled VPS gate.

## Required future implementation tests

Implementation plan must include tests that:

- missing enrolled host key blocks SSH-backed read-only operation in production mode;
- missing enrolled host key still allows no-SSH dry-run preview;
- matching pinned fingerprint allows read-only SSH command to be attempted;
- mismatched fingerprint blocks before remote command execution;
- host/port change invalidates previous pin;
- password auth cannot use `accept-new` in production mode;
- re-enrollment requires explicit reason and actor;
- mismatch audit includes expected/observed fingerprints but no SSH secrets;
- backup redaction excludes SSH private key/password and does not include full operator `known_hosts`;
- restored host key pin requires revalidation when host/port differs;
- UI/API error message does not offer production "continue anyway".

## First safe implementation boundary

Recommended first code boundary when this moves to `amn2`:

```text
local-only SSH host key identity verifier
```

It may include:

- parsing OpenSSH public host key lines;
- computing SHA256 fingerprint;
- storing logical pinned identity in config or DB metadata;
- fake SSH client tests for match/mismatch/missing pin;
- CLI dry-run/report commands that show safe fingerprint metadata;
- docs update for operator verification.

It must not include:

- automatic trust of unknown keys;
- live VPS mutation;
- web/API remote operation expansion;
- storing SSH private keys or passwords in DB;
- install/clear/reboot flows;
- copying PRVTPRO manager code.
