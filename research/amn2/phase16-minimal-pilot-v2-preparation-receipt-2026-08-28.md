# Phase 16 — v2 native preparation and AWG2 fingerprint ordering

**Artifact preparation completed; original aggregate safety gate remains STOP.** One official image, six protected native key files and exactly one server/Windows profile pair were prepared. No AWG3.1 runtime, published ports, application stage, host installation or general issuance was started. A subsequent read-only diagnostic reproduced an order-sensitive fingerprint defect; a one-line local fix is not yet uploaded.

## Exact operator authorization

Markdown escapes before underscores were normalized without changing fields:

```text
/APPROVE PHASE16 SPAIN MINIMAL_PILOT_V2_UPLOAD_AND_PREPARE TO_138.124.181.246 SCRIPT_SHA256_6f37f40557f9ab6ffde9d1e77705770ed8e718af716fa9a53602899cf1ff5827 REMOTE_PATH_/var/lib/amn2-phase16/pilot-tools/v2/phase16_awg31_minimal_pilot.py ONE_SCRIPT_UPLOAD CREATE_PARENT_DIRS_IF_ABSENT VERIFY_REMOTE_SHA256 PINNED_IMAGE_PULL_FROM_SCRIPT KEY_DIRECTORY_/var/lib/amn2-phase16/pilot-keys PROFILE_DIRECTORY_/var/lib/amn2-phase16/pilot-input ONE_EPHEMERAL_KEYGEN_CONTAINER NETWORK_NONE NO_PUBLISHED_PORTS ONE_SERVER_AND_WINDOWS_PROFILE_PAIR DNS_1.1.1.1 MTU_1280 STRICT_HOST_KEY_CHECKING ROOT_ONLY_PERMISSIONS NO_OVERWRITE NO_EXISTING_OWNERSHIP_CHANGE NORMALIZED_OUTPUT_ONLY NO_RETRY NO_RUNTIME_START NO_APP_STAGE NO_HOST_INSTALL NO_GLOBAL_ISSUANCE AWG2_UNTOUCHED
```

- Pre-run HEAD `0f5e5fc6429954f1f15c88ed7e0a49b6337ae208`; old immutable packages/transactions were not reused.
- Locally verified v2 source SHA256 `6f37f40557f9ab6ffde9d1e77705770ed8e718af716fa9a53602899cf1ff5827`.
- Private SSH trust bundle was revalidated read-only, pinned fingerprint `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`; strict checking, no agent/password fallback or trust updates.
- Source and standard transfer commands were syntax/binding checked locally. No full regression, package build/materialization or package verifier was repeated.

## One upload and one preparation

- UTC `2026-08-28T09:17:07.539167+00:00` to `2026-08-28T09:17:41.367457+00:00` (12:17:07–12:17:41 Moscow), about 33.83 seconds.
- Three OpenSSH sessions: exclusive new v2 directory, one standard SFTP upload, verification/preparation. All three remote exits `0`; no timeout or retry. All stderr streams empty.
- Directory session 4.157 s, SFTP session 10.406 s, verification/preparation session 19.266 s.
- New directory `/var/lib/amn2-phase16/pilot-tools/v2`, mode `700`; one file uploaded via stock SFTP server with umask `077`. Existing versions were not overwritten.
- Uploaded file root owner, regular/non-symlink type, mode `600` and exact v2 SHA256 were verified before any image/key operation.
- One pull of `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`; Docker image lookup by pinned reference and `linux/amd64` check succeeded.
- One ephemeral container `amn2-spain-awg31-pilot-keygen-002`, label `amn2.phase16.operation=minimal-v2-keygen-render-001`, `--network none`, no ports, read-only root filesystem, all capabilities dropped, no-new-privileges, logging disabled, `--rm`.
- It ran only native `awg genkey` (server/client/HPK), `awg pubkey` (server/client) and `awg genpsk`, writing directly to the new protected bind directory. No key was an argument, environment variable, log entry or stdout result.
- Container absence was confirmed after completion. Six expected key files were counted and each verified root-owned, non-symlink, mode `600`, length 45 bytes; key directory mode `700`.
- Existing application-owned `/var/lib/amn2-spain` was neither changed nor used for the new secret files. Existing ownership/modes were not changed.
- v2 `render --key-directory /var/lib/amn2-phase16/pilot-keys --dns 1.1.1.1 --mtu 1280` created exactly two new profile files, root-owned mode `600` under a mode `700` directory. No overwrite or regeneration.
- Before-check and final `check --with-profiles` returned `ready=true`; the rendered file hashes matched final read-back. This validates the script's narrow profile contract, not the native AWG config parser, firewall applicability or actual client compatibility/traffic.

## Existing protected artifacts — do not regenerate

| Remote artifact | SHA256 |
| --- | --- |
| `/var/lib/amn2-phase16/pilot-input/server.conf` | `cb365343f62d7a2ab4e393d33f3f126b818b1aacdd38d14c30abfe81fd6ce1de` |
| `/var/lib/amn2-phase16/pilot-input/windows.conf` | `490e029656fce7dc425266078bab1c328e4e395ee80f045b6700715edbc49d2a` |

The six native keys remain in `/var/lib/amn2-phase16/pilot-keys`. No profile/key was downloaded to the workstation, printed, committed or published. The image remains in the dedicated Docker cache. No persistent pilot container/network/interface/listener was created by this operation.

## Original STOP, retained without retrospective PASS

- Original AWG2 fingerprint before: `50b3ec57fa0ead040045705af1d6de19457dbd82dc33cbf2de3718ca62139894`.
- Original AWG2 fingerprint after: `5b9f3af5ccde6432b55206b8e19041ce5abce5f030c5122a2f6a41c75d63f0a0`.
- v2 before state SHA256 `82a2ef2014d0a276159cdba43e47eee952d030f772a5b1715a491f5b58053ef0`; after state SHA256 `b6002913fa72760795016deb13a6b6c5e13ae7beae37169f0270e908b8d87cc8`.
- All five preparation completion markers and `profiles_match=true` were observed. The local aggregate gate returned STOP solely because `awg2_snapshot_equal=false`.
- Verification/preparation stdout: 1463 bytes, SHA256 `af4ddd9a154549c111d7334c2d86f743a383457c07b0433d3db571a5f4165ee5`; raw transport stream not retained.
- No mutation command targeted AWG2. Nevertheless, the original hashes do not establish semantic equality for that original observation interval; no raw snapshots were retained for retrospective canonicalization.

## One additional read-only attribution

- One SSH diagnostic, no preparation retry or mutation, UTC `2026-08-28T09:23:20.977972+00:00` to `2026-08-28T09:23:24.023583+00:00`; remote exit `0`, empty stderr.
- Two bounded samples of the same AWG2 owner/container/interface components were collected in memory. Only normalized hashes/counts/booleans were retained; no raw peer keys, container JSON, environment or traffic.
- Only `peers_order` differed. Both samples had seven peer lines, identical sorted-peer hash, and identical owner, container ID/image/HostConfig/Mounts/restart-count/running/started component hashes.
- Sorted-peer diagnostic hash: `4d49f8a1b53073a21fa4f9528bcc29a944daf06b5d4e3ee8d406f5375536960f`.
- The old fingerprint algorithm therefore demonstrably changes for an unchanged membership returned in a different order. This confirms an implementation defect without proving every historical state transition between the earlier and later sessions.
- Historical reconstruction flags were false. Peer permutation enumeration was deliberately limited to five entries; the observed seven-peer list exceeded that bound. These flags are not proof of a real historical peer change.
- Diagnostic stdout SHA256 `e69d36ea009a8cd744c44e59d393a7fb8b4a4f27b0d7cabc9f6db53232a3d8dc`.

## Local fix and next boundary

- Only production change: sort peer lines before hashing in `awg2_snapshot`. No deduplication, ownership change, freshness-policy change, altered profile fields or server command changes.
- One new test `test_awg2_fingerprint_ignores_peer_order_but_preserves_peer_changes`: RED 0.046 s, GREEN 0.008 s. It covers reordering equality plus membership change and duplicate preservation. No full test suite rerun.
- Corrected local source SHA256 `a9c728a4bf7116286b126c7458af13f0c67e71ce1501bc26d66df303781c76e2`; not uploaded or run remotely.
- A future v3 upload must use a new path, `/var/lib/amn2-phase16/pilot-tools/v3/phase16_awg31_minimal_pilot.py`, preserving v1/v2. A fresh read-only check must validate the existing profile hashes and canonical state. No image pull, keygen or render is needed for that check.
- Any later runtime/application/port-publication action requires new explicit authorization. Current upload/preparation approval and attempts are consumed.

## Local evidence and status

- `tmp/phase16-minimal-pilot-v2-prepare-001.py` SHA256 `bb1a5ba87c7f2f3c5de1e4b697206131f446be71ea0a8f8c72b861357eb0049c`; its transformed in-memory shell payload SHA256 `649adfebebf23a0de11a938671b1667cad15b262034486a10c9af35864f60476`.
- Same-stem `.sftp` SHA256 `6cd61a5ac2bffbddd13acca854200cbdde0fd79a091ff389e3c5c6a6826dad48`; consumed `.attempt` SHA256 `18e6569d392d2b7b850c20e3b78fcd649859bcb49c8d876d1a2373107d6755a5`; normalized `.jsonl` SHA256 `fef5d270fa0d4150646b8bb65b1f429a19b4f9dd5cce65361b75cc42c576f938`.
- `tmp/phase16-minimal-pilot-v2-awg2-fingerprint-readonly-001.py` SHA256 `c3442f8c25a49aa409b1f068a68906dde77f0facbd231cca007a8326601db840`; its normalized `.json` SHA256 `210c2377e58690354928f17703dde83a056dc8fb4cd2ed868dcb49ec8aea27e1`.

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 016 retained.
- ✅ Task 1A — v2 uploaded; subsequent fingerprint correction ready locally.
- ✅ Task 2 — v2 technical checks passed; corrected canonical-state check remains pending.
- ❌ Task 3A — artifact preparation completed; aggregate equality gate STOP retained, runtime not started.
- ▶️ Task 4 — exactly one profile pair prepared on the server, not delivered/installed.
- ⏳ Task 4.5 — transport-quality gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 3B — AMN2 integration after the pilot.
- ⏳ Task 6 — closeout.

Only the local correction/test/guide/receipt are to be committed. No secrets, ignored operation helpers or protected packages are staged. No public Git push is authorized.
