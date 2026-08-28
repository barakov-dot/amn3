# Phase 16 — v3 upload and existing-profile check PASS

One corrected script was uploaded and one fresh read-only check passed. The existing AWG3.1 server/Windows profile pair was not regenerated or changed. The AWG3.1 runtime is not started and the Windows profile has not been downloaded to the operator workstation.

## Authorization and fixed scope

- Operator approval: `разрешаю` in direct response to the selected next step: upload the comparison correction and check the existing pair, without regenerating keys or profiles.
- This permission was applied to that nearest step only, not the later runtime start or client delivery.
- Pre-run HEAD: `b49587b068822b4ed44bc4c3e8ff7980255c540c`.
- Local source SHA256: `a9c728a4bf7116286b126c7458af13f0c67e71ce1501bc26d66df303781c76e2`.
- Original v2 receipt SHA256: `c63bb03be5d1846267e40ec1f0eaa72fb21358ad018c2b89d59bf3f7340640c5`; preserved, including its original aggregate STOP. This new PASS does not rewrite the earlier observation interval.
- No production code was changed in this step. No full regression, package materialization or package verifier was repeated.

## Actual execution

- UTC `2026-08-28T10:33:22.460669+00:00` to `2026-08-28T10:33:43.112176+00:00` (13:33:22–13:33:43 Moscow), about 20.7 seconds.
- Private SSH trust bundle revalidated read-only with `Assert-Phase16SpainTrustBundle`; pinned host fingerprint `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`. No trust or ACL changes.
- Stock OpenSSH, strict host-key checking, one connection attempt per session, no password/agent fallback or forwarding.
- Three sessions: exclusive new directory creation (2.125 s), one SFTP upload (16.969 s), remote hash/permissions verification and one `check --with-profiles` (1.563 s).
- Each SSH/SFTP exit was `0`, all stderr streams empty, no timeouts or retries.
- New directory `/var/lib/amn2-phase16/pilot-tools/v3`, root-owned mode `700`. Existing v1/v2 directories and scripts were not overwritten.
- Uploaded `/var/lib/amn2-phase16/pilot-tools/v3/phase16_awg31_minimal_pilot.py`, verified root-owned, regular/non-symlink, mode `600`, exact source SHA256 before execution.
- The read-only command used `/usr/bin/timeout 60s /usr/bin/python3 -I -B` and the uploaded script's `check --with-profiles` mode.
- Fresh technical readiness was `true`. Existing profile parent/file protection and narrow profile-contract checks passed; returned profile hashes exactly matched the v2 preparation receipt.
- This check does not establish native AWG parser acceptance, applicable firewall policy, client compatibility or live traffic performance. Those remain later gates.

## Bound result

| Field | SHA256 |
| --- | --- |
| Corrected script | `a9c728a4bf7116286b126c7458af13f0c67e71ce1501bc26d66df303781c76e2` |
| Fresh state | `caebba5ff4f3d830976a73817d22197d5d05b07300071a4e117ad1bcaae2cc03` |
| Canonical AWG2 snapshot | `998dda7323cbbe356ad997921fdce22e539924803ce38eadcd1ed3d0aa4e500b` |
| Existing `server.conf` | `cb365343f62d7a2ab4e393d33f3f126b818b1aacdd38d14c30abfe81fd6ce1de` |
| Existing `windows.conf` | `490e029656fce7dc425266078bab1c328e4e395ee80f045b6700715edbc49d2a` |
| Hash/check stdout, 643 bytes | `637afbee574729c7c4180ab80d11de0371698063fcf7cb35757166d27ae1183a` |

The profiles remain under `/var/lib/amn2-phase16/pilot-input`. This operation collected one fresh canonical AWG2 snapshot; it did not retrospectively prove equality for the old v2 preparation interval. No AWG2 mutation command was issued.

## Local evidence

Stem: `tmp/phase16-minimal-pilot-v3-upload-check-001` (ignored execution artifacts, no secrets).

- `.py`: `b96f8a9b9b85c60b075a9e724cd06382cedd4b5cc0ac9c92c15c43942793481a`.
- `.sftp`: `cea9d507301ab4507a60757100969efc312261cfa628d96dd74c62117a6ff514`.
- `.attempt`, consumed: `c13946b8165939c8e449b69b462ac71585c06f136580508ce5dd304d69b4ece5`.
- `.jsonl`, normalized results: `8042859719ca56e667658c59bb49fa3d3eea2c5e3ba5dce9609adc92102663ce`.
- Before egress, source/helper hashes, exact SFTP batch and shell syntax were checked locally. Default local readiness mode returned `ssh_started=false`.
- Only normalized fields, counts, hashes, exit statuses and timestamps were retained. No raw transport streams, keys, profile contents or traffic were persisted locally.

## Status and next boundary

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 016 retained.
- ✅ Task 1A — corrected v3 script uploaded.
- ✅ Task 2 — fresh existing-pair technical check PASS.
- ▶️ Task 3A — separately authorized isolated AWG3.1 runtime start is next; not executed.
- ⏳ Task 4 — deliver the existing Windows profile to the workstation after successful runtime start.
- ⏳ Task 4.5 — mandatory AWG2/AWG3.1 transport-quality comparison.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 3B — AMN2 integration after the pilot.
- ⏳ Task 6 — closeout.

The next runtime action must be bound to the script/state/profile hashes above, with a fresh one-use claim and rollback of only that attempt's resources on failure. It requires separate operator permission. No runtime start, native parser container, port publication, image pull, keygen, rendering, application stage, host installation, global issuance, AWG2 reconfiguration or client-profile download occurred in this step. No public push is authorized.
