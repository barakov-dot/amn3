# Phase 11 RECOVERY-001: old bundle/key retention decision

Date: 2026-07-14.

Decision: `RETAIN SEALED UNTIL CANONICAL FULL-SECRET RESTORE REHEARSAL; THEN
RETIRE UNDER A SEPARATE EXACT DELETION GATE`.

No ciphertext, checksum receipt, recovery-info receipt or key was deleted,
moved, copied or opened by this decision. Key contents were not read. This is
an evidence-backed retention decision, not restore or retirement execution.

## Current evidence

The old 2026-07-13 encrypted bundle is a valid legacy Fernet fallback. Its
known metadata newline defect affects the canonical metadata contract, but the
legacy verifier previously passed authenticated decrypt, manifest, critical
runtime, SQLite and AWG key/peer contracts. The defect is why it is not the
canonical recovery artifact.

The 2026-07-14 replacement is the canonical recovery artifact. It uses an
RSA-OAEP-SHA256-wrapped Fernet data key, has corrected metadata, passed local
in-memory decrypt and critical contracts, and has a verified independent
ciphertext copy. Its private key remains separate from ciphertext with a
protected current-user-only ACL.

Fresh read-only inventory returned:

```text
old_workspace_ciphertext=present_hash_match
old_external_ciphertext=present_hash_match
old_external_file_count=3
old_external_private_key_like_files=0
old_key=present_separate_from_ciphertext
old_key_acl=current_user_only_protected
canonical_external_ciphertext=present_hash_match
canonical_external_file_count=3
canonical_external_private_key_like_files=0
canonical_private_key=present_separate_from_ciphertext
canonical_private_key_acl=current_user_only_protected
recovery_files_deleted=0
```

The old ciphertext hash matches its accepted `2026-07-13` receipt in both the
ignored workstation copy and removable-media copy. The canonical ciphertext
hash matches its accepted `2026-07-14` receipt. Neither external-media
directory contains a key-like file.

## Why deletion is not safe yet

The canonical bundle has been decrypted and semantically verified, and its
secret-free sanitized fixture passed an isolated staging rehearsal. However,
the canonical production-secret payload has not yet been applied into a clean
trusted disposable environment and exercised through the complete offline
restore procedure. The old bundle is the only independently verified legacy
decrypt path and therefore remains a useful temporary fallback.

Keeping it forever would add unnecessary key/ciphertext inventory and legacy
crypto handling. Deleting it now would remove the fallback before the new
end-to-end operational restore path is proven. Conditional sealed retention is
the lower-risk choice.

## Retirement prerequisite

Before old-artifact deletion can be reviewed, a separately approved
`PHASE11-RESTORE-001A` rehearsal must pass all of these criteria in a trusted
disposable environment:

1. Start from a clean host with key-only operator access and default-deny
   network policy. It is a functional restore environment, not an independent
   provider disaster-recovery domain.
2. Transfer only the canonical ciphertext and its required private key through
   an exact, non-logging path; never place the key on removable media beside
   ciphertext.
3. Decrypt and apply offline with no production endpoint ownership, no public
   web/API, persistent bot disabled, write gates false and no config delivery.
4. Verify manifest, canonical metadata, SQLite integrity/foreign keys, AWG
   server-key and per-peer PSK bindings, systemd unit validity, source marker
   and required file modes/owners.
5. Exercise bounded service startup only under the exact rehearsal gate, prove
   no production interaction, then stop services and securely remove the
   restored secret tree and transferred key.
6. Recheck the production DB/web/AWG baseline independently and retain a
   sanitized success receipt.

This gate transfers production secrets and can start an isolated restored
runtime, so it is not implied by this decision and needs an exact approval.

## Future retirement scope

Only after `PHASE11-RESTORE-001A` passes, prepare a second exact destructive
gate that names all three old-item classes:

- old ignored workstation ciphertext;
- old removable-media ciphertext plus its checksum/info receipts;
- old separate symmetric recovery key.

Immediately before and after deletion, re-verify both canonical ciphertext
copies and the canonical private-key separation/ACL. The retirement gate must
not delete, rotate or move any canonical artifact or key. It must not touch
production, AWG, peers, services or configs.

## Operational consequence

Keep the second disposable VPS temporarily if it remains clean and affordable:
it is the natural candidate for the exact `RESTORE-001A` functional rehearsal.
It is not required for current production P0 and does not provide independent
provider DR. The following second-VPS audit will make the final keep/retire
recommendation and billing-window condition.

Next ordered action: `AUDIT_SECOND_VPS_RETENTION_AFTER_P0`.
