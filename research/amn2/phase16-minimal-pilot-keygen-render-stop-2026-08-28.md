# Phase 16 — native key/profile preparation STOP and local path correction

Outcome: **preparation stopped before remote mutation; no image pull, key generation or profiles**. One subsequent read-only attribution identified an incompatible non-root parent directory. A one-line local path correction passed one focused RED/GREEN test; it has not been uploaded.

## Authorization and attempted scope

The user replied `разрешаю` to the selected statement authorizing download of the pinned official image, native key generation and exactly one server/Windows profile pair. This was explicit authorization for that scope, not a newly supplied checksum-token command or permission for runtime/application stage, general issuance, ownership changes or public Git push.

- Pre-run local HEAD: `ff8d61db0818ce4b2f17971d00924b02cf69bb46`.
- Attempted source/remote script SHA256: `95f0f52b875328425df54b0564e70bfdcb2bfef4ac2ccac0aeef8fb5c29a2f92`.
- Target `138.124.181.246`, root login with the locally revalidated private trust bundle and pinned strict host-key checking. No trust/ACL changes.
- Original proposed inputs: `/var/lib/amn2-spain/awg31-pilot-keys` and `/var/lib/amn2-spain/awg31-pilot-input`.
- Planned DNS `1.1.1.1`, MTU `1280`, exactly one client; these were announced before dispatch and are not a diagnosis/tuning of AWG2.
- Planned image remained `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`.
- The intended key generator was one stock `awg genkey/pubkey/genpsk` container, `--network none`, no ports, all capabilities dropped, root-only bind directory, `--rm`. None of these mutation steps was reached.

## Single preparation attempt

- UTC `2026-08-28T08:59:14.323037+00:00` to `2026-08-28T08:59:19.345686+00:00`; 5.031 seconds.
- One SSH session using a normal command argument, no uploaded helper or stdin bootstrap. SSH exit `1`, no timeout, no retry.
- Returned fixed marker `PILOT_STEP_STOP:preconditions:1`; no preconditions-complete marker, no subsequent step started.
- The preconditions section contains only reads. Consequently no mkdir, image pull, container start, key generation, render, AWG2 mutation or runtime operation was issued.
- Stdout: 32 bytes, SHA256 `68aeef6dce56ad2a28f2bf3fc7e6f79e570255a60a3cbac00f6c3a5561f44904`; stderr: 0 bytes.
- Ignored payload `tmp/phase16-minimal-pilot-keygen-render-001.sh`, SHA256 `7b7e1f559939bf1c9cf849d2e90b0884866b205cf706ac7afe51adbeefc30c67`.
- Ignored driver `tmp/phase16-minimal-pilot-keygen-render-001.py`, SHA256 `6f388a6a0c9c597d5fb7692b468ad05adcf32b84699d259a82a1875be048d6dd`.
- Consumed `.attempt` SHA256 `d9d50d14720d98a422fe80f5898e83a5b1fff78622be6b177607ec8f162062ee`; normalized `.jsonl` SHA256 `8abf40a79af2ae953185a7cd3d48e1fc7df02e1ba28b4a3d7da48180690329c2` (same filename stem as the driver).
- Driver fields `awg2_snapshot_equal=false` and `profiles_match=false` mean the corresponding observations were never reached, not detected AWG2 drift or mismatching generated files.

## One read-only attribution

Performed as an in-scope, non-mutating diagnostic of this failed preparation; not another preparation attempt. No script, key or profile contents were output.

- UTC `2026-08-28T09:01:13.093201+00:00` to `2026-08-28T09:01:25.862412+00:00`; SSH exit `0`, stderr 0 bytes.
- `/var/lib/amn2-spain`: a directory, **not root-owned**, not group/other-writable. No raw UID or owner name was collected.
- The proposed keys and profiles directories and the named keygen container: absent.
- `/var/lib/amn2-phase16` and its `pilot-tools` directory: root-owned, mode `700`.
- Uploaded script: root-owned regular file, mode `600`, exact old SHA256 matched.
- `/var` and `/var/lib`: root-owned directories, not group/other-writable. Dedicated Docker binary executable; expected socket present.
- The Docker socket's writable mode is not the blocked parent-directory check and was not changed.
- This establishes a concrete mismatch between the chosen input parent and the script's root-only input contract. The preparation marker recorded a section, not the exact historical shell line; the attribution was a later bounded read-back.
- Diagnostic stdout SHA256 `d41f98af945a1b7df5ca92ff5335d89f8b700668f2869fe88a729ff94b79a3de`.
- Ignored diagnostic `tmp/phase16-minimal-pilot-keygen-precondition-readonly-001.py`, SHA256 `93b1d2647b2fb30d5123351b6291e3216cf8c4579d20b61128ace5f4df591ccc`.
- Diagnostic normalized `.json` SHA256 `b4e819e73591a22c4ffe3d7c5e60ab41a60dada191bca2449e513fc1b5797d03`; consumed `.attempt` SHA256 `d828b69ffd55a2f1f27a293ad38e62c01c2141dd1b83ffeac69e269e04fbbf69`.
- Raw transport streams, directory contents, private material and process environments were not persisted. No AWG2 probe was added by this diagnostic.

## Local correction and verification

Only production change: `INPUT_DIR` now points to `/var/lib/amn2-phase16/pilot-input`. Future native keys are to be prepared under `/var/lib/amn2-phase16/pilot-keys`. The already root-owned Phase 16 namespace is separate from the application's non-root state directory.

- No `chown`, chmod of existing remote data, symlink workaround, runtime module override or weakening of the root-owner checks.
- One new test `MinimalPilotTests.test_pilot_inputs_use_root_owned_phase16_namespace`: expected RED on the old path, 0.045 s; GREEN after the constant change, 0.008 s. The same test also proves that a synthetic non-root parent remains rejected.
- No full suite, package materialization or package verifier repeated. Earlier test results are historical, not a full regression run on this revision.
- New local script SHA256: `6f37f40557f9ab6ffde9d1e77705770ed8e718af716fa9a53602899cf1ff5827`.
- No new remote upload was attempted. The old script, package016, old transactions and consumed local attempt records are retained unchanged.
- Proposed new remote version path, not yet created: `/var/lib/amn2-phase16/pilot-tools/v2/phase16_awg31_minimal_pilot.py`.

## Next gate and Phase 16

A new explicit approval must cover one non-overwriting upload of the corrected script into the new root-only version directory and continuation of the same pinned-image/native-key/one-profile-pair preparation. Runtime/application stage, host installation, public issuance and changes to AWG2 or existing ownership remain excluded. New script/state/profile checksums must bind any later runtime authorization.

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 016 retained.
- ✅ Task 1A — local namespace correction, focused test PASS.
- ✅ Task 2 — historical technical check PASS; new version not uploaded or live-checked.
- ❌ Task 3A — preparation stopped before image pull; awaiting corrected-version authorization.
- ⏳ Task 4 — no keys or server/client profiles generated.
- ⏳ Task 4.5 — mandatory transport-quality gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 3B — AMN2 integration after the pilot.
- ⏳ Task 6 — closeout.

AWG2 not modified. Remote writes/image pull/keygen/config/runtime start in this turn: 0. Only local code/test/guide/receipt changes are to be committed; no public push.
