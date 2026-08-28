# Phase 16 — minimal pilot script upload and read-only check

Result: **PASS** for this bounded operation. This is not runtime installation, client acceptance or permission for the next mutation.

## Approval and bindings

The operator supplied the following exact approval; Markdown escapes before underscores were normalized only for interpretation.

```text
/APPROVE PHASE16 SPAIN MINIMAL_PILOT_SCRIPT_UPLOAD_AND_READONLY_CHECK TO_138.124.181.246 SCRIPT_SHA256_95f0f52b875328425df54b0564e70bfdcb2bfef4ac2ccac0aeef8fb5c29a2f92 REMOTE_PATH_/var/lib/amn2-phase16/pilot-tools/phase16_awg31_minimal_pilot.py ONE_SCRIPT_UPLOAD CREATE_PARENT_DIRS_IF_ABSENT ROOT_ONLY_PERMISSIONS NO_OVERWRITE VERIFY_REMOTE_SHA256_BEFORE_RUN ONE_CHECK CHECK_TIMEOUT_60S STRICT_HOST_KEY_CHECKING NORMALIZED_OUTPUT_ONLY NO_RETRY NO_OTHER_REMOTE_WRITE NO_STAGE NO_INSTALL NO_KEYGEN NO_CONFIG NO_ISSUANCE AWG2_UNTOUCHED
```

- Source commit: `a762f83eb0ef019138e80463345e4aab9eeea2f8`.
- Source: `scripts/vps/phase16_awg31_minimal_pilot.py`; SHA256 `95f0f52b875328425df54b0564e70bfdcb2bfef4ac2ccac0aeef8fb5c29a2f92`.
- Target: `root@138.124.181.246`; remote file: `/var/lib/amn2-phase16/pilot-tools/phase16_awg31_minimal_pilot.py`.
- Existing private SSH trust bundle validated locally, including ownership/ACL and pinned host fingerprint `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`.
- Sandbox restrictions on local trust reads required an elevated read-only context; no ACL was changed. Local preparation errors started no SSH.

## Execution and allowed writes

- UTC window: `2026-08-28T08:24:17.430108+00:00` to `2026-08-28T08:24:31.163041+00:00` (11:24:17–11:24:31 Moscow), about 13.73 seconds.
- Three ordinary OpenSSH sessions: directory preparation, one SFTP upload, remote hash/mode verification followed by one `check`. All exited `0`, with zero stderr bytes; no retry.
- Parent directories were verified without following symlinks. Missing `/var/lib/amn2-phase16` was allowed to be created; its existing-versus-created status was not separately collected. Its root-only `0:700` mode was verified.
- The leaf `pilot-tools` directory was created exclusively as root with mode `700`. An already-existing leaf directory would have stopped this operation before upload, so no pre-existing destination file was overwritten.
- Stock OpenSSH SFTP used `/usr/lib/openssh/sftp-server -u 077`; exactly one source file was transferred. There was no custom stdin framing or collector/coordinator bootstrap.
- Remote regular-file/non-symlink status, root owner, mode `600` and the exact approved SHA256 were verified before executing the script.
- Executed once: `/usr/bin/timeout 60s /usr/bin/python3 -I -B /var/lib/amn2-phase16/pilot-tools/phase16_awg31_minimal_pilot.py check`.
- Hash-and-check SSH session: 1.593 seconds, no timeout. This includes connection and verification time, not just Python execution.
- No remote write outside the approved script/parent-directory scope was issued. No software/image pull, installation, stage, key generation, client/server profile, peer issuance, rollback or AWG2 mutation was performed.
- The uploaded script remains inert until another separately authorized command. No service, scheduled job or automatic retry was configured.

## Normalized result

```json
{"script_sha256":"95f0f52b875328425df54b0564e70bfdcb2bfef4ac2ccac0aeef8fb5c29a2f92","state":{"awg2_snapshot":"a388df65b034843923d2193741a3c931f4650848862370d7312d967439a883d0","image":"docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d","ready":true,"target":"138.124.181.246"},"state_sha256":"63570c1d80b6631f51cfe894a6d92a1922bdd0a7f7bbaaf1f427e24bd08f1988"}
```

The state hash was recomputed locally from canonical compact sorted JSON of `state`, without a trailing LF. The response field sets, fixed target/image/script hash and fingerprint formats passed local validation.

Technical check passed: Ubuntu 24.04/amd64/root, dedicated Docker/socket, TUN, existing IPv4 forwarding, target address, reserved container/network/bridge/UDP-port absence, and IPv4 route/Docker-subnet non-overlap. The AWG2 snapshot was obtained read-only; no client traffic or handshake freshness was required.

This does **not** certify firewall policy applicability, an installed client's actual AWG3.1 parser, tunnel traffic, performance, or before/after AWG2 equality. The AWG2 value is one normalized fingerprint, not a new health or throughput verdict. The image string is the pinned plan target, not evidence of an image pull.

## Local retained evidence

Only normalized results, byte counts, SHA256 values and timing metadata were persisted. Raw transport streams, private keys, peer lists and complete configurations were not persisted or printed.

- Ignored one-shot driver: `tmp/phase16-minimal-pilot-upload-check-001.py`, SHA256 `b89416d384b2cd0d11f224b56c57a1764741629f82055fc0bc4dd37678b54756`.
- Ignored standard SFTP batch: `tmp/phase16-minimal-pilot-upload-check-001.sftp`, SHA256 `33bffdcc98799853769c89bf85ba7c2d59260161bcdc1cc6549635494213853a`.
- Durable consumed local reservation: `tmp/phase16-minimal-pilot-upload-check-001.attempt`, SHA256 `1fb17ff28136f4553d936ee74050560d22e0f9d994a238ca80175a0a72fbf5c6`.
- Normalized journal: `tmp/phase16-minimal-pilot-upload-check-001.jsonl`, SHA256 `3540fe5b18a99e2cc1784fe7020be05e8c8335e9576c0707ad890e8b2e00218c`.
- Hash/check stdout: 464 bytes, SHA256 `bd2f7f7cc26f7e4e4fadfa4fbd0ad386bd5e7e269ce42a652f3df5f764988ab3` (marker plus normalized script response); raw stream not retained.
- All three stderr streams: 0 bytes, SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

No test suite, package materialization or package verifier was repeated. Source and immutable packages were not changed. Only this receipt is intended for the local commit; no public push is authorized.

## Next boundary and Phase 16

This approval is consumed. The next mutation needs a separate exact approval for protected native key/profile preparation and, subsequently, the isolated pilot runtime. Do not replay this upload/check, old package016 approvals or transaction007. Future apply must bind the exact script, then-current checked state, and the generated server/client profile hashes; firewall/client compatibility and transport quality remain acceptance gates.

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 016 retained.
- ✅ Task 1A — independent minimal pilot implementation.
- ✅ Task 2 — one script uploaded; bounded technical read-only check PASS.
- ▶️ Task 3A — isolated runtime preparation awaits new authorization.
- ⏳ Task 4 — first AWG3.1 profile for the Windows workstation.
- ⏳ Task 4.5 — AWG2/AWG3.1 transport-quality gate.
- ⏳ Task 5 — client acceptance.
- ⏳ Task 3B — AMN2 integration after the pilot.
- ⏳ Task 6 — closeout.

AWG2 unchanged by this operation; stage/install/keygen/config/issuance: 0.
