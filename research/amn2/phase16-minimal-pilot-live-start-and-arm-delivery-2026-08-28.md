# Phase 16 — AWG3.1 pilot running, Windows profile delivered

Server startup and protected delivery passed. The operator's first workstation connection/traffic test is still pending; this is not Phase 16 acceptance or closeout.

## Authorization and scope

- Operator: «разрешаю все нужные запуски до стадии достижения результата = тест на арм», responding to one isolated AWG3.1 pilot on UDP 30002, scoped rollback on failure, then protected Windows-profile delivery.
- Scope remained the one-peer pilot and necessary diagnostics/correction. No AMN2 application/DB/Telegram stage, host installation, AWG2 reconfiguration, general issuance or public Git push.
- Pre-turn HEAD: dbee8c04e812bacf435bddefe36b605334188922. Immutable package 016 and prior packages/transactions were not changed or replayed.
- Every SSH/SFTP operation revalidated the existing private trust bundle with strict host-key checking. No trust, key-file or existing ownership/ACL changes.

## First attempt and diagnosis

- Claim pilot-spain-awg31-arm-20260828-001 was consumed at UTC 10:48:31–10:48:43. Exit 64: native_validation_failed_owned_resources_removed, before persistent network/container/port creation.
- Its journal reported rollback=owned_resources_removed but awg2_state_equal=false. That historical false remains recorded; its exact cause was not established and was not retroactively changed to PASS.
- Diagnostic 001 stopped before creating a diagnostic container because it compared the entire expected rollback record, including an assumed true AWG2 flag.
- Diagnostic 002 read the actual rollback fields, confirmed pilot resources absent, and ran one network-none ephemeral native check. Both key-pair checks and the userspace socket passed; server setconf returned Invalid argument. Native tools version: v3.1.20260812.
- Diagnostic container removal was verified. Before/after AWG2 fingerprints both equalled the earlier baseline 998dda7323cbbe356ad997921fdce22e539924803ce38eadcd1ed3d0aa4e500b; owner, identity, image, HostConfig, Mounts, restart count, running state, start time and peer components matched.
- The official tagged tools source maps AdvancedSecurity to WGPEER_HAS_AWG and deliberately returns EINVAL for that flag in userspace. This explains the observed native rejection, not a key-pair or SSH failure.
- Sources: [tagged userspace implementation](https://github.com/amnezia-vpn/amneziawg-tools/blob/v3.1.20260812/src/ipc-uapi.h#L107), [official config parser](https://github.com/amnezia-vpn/amneziawg-tools/blob/v3.1.20260812/src/config.c), [Windows parser](https://github.com/amnezia-vpn/amneziawg-windows/blob/master/conf/parser.go).

## Minimal correction

- Removed only AdvancedSecurity = on from both rendered profiles. HeaderProtectionKey, S1–S4=12, other AWG3.1 parameters, endpoint, DNS, MTU and the one peer were preserved.
- Source input directory versioned to /var/lib/amn2-phase16/pilot-input-v2; original input/key directories and v1–v3 scripts preserved.
- One regression test first failed on the incompatible flag (0.045 s); the complete targeted file then passed 22 tests in 0.328 s. Tests use synthetic keys/local fakes.
- New source SHA256: 3700284de8ac226a958b0fc4f1d88d93763987698ee080029858b872f9789649.
- One upload to /var/lib/amn2-phase16/pilot-tools/v4/phase16_awg31_minimal_pilot.py; new root-only directory/file and exact hash verified.
- Between UTC 11:10:20 and 11:10:30, exactly one occurrence of the incompatible line was removed from each hash-bound original profile into a new directory (mode 700) and two files (mode 600). No new keys or peer identity were generated. All other profile bytes were preserved.
- One check --with-profiles passed. State SHA256: caebba5ff4f3d830976a73817d22197d5d05b07300071a4e117ad1bcaae2cc03.
- Server profile SHA256: d16a187670044069902d788d4dc1febff331e6f1172d059fbf88b1d0df76c6d3.
- Windows profile SHA256: 0f97d55814824e7d34121143f8c8ed516984b0822e8a12a658d6059c69acfa65.

## Successful server startup

- Claim pilot-spain-awg31-arm-20260828-002; UTC 11:11:32.984228–11:11:41.895893 (14:11 Moscow), 8.906 s.
- Pinned official image retained: docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d.
- Native server/client parser checks, isolated runtime startup and health all passed. Result: pilot_started_client_test_pending; peer_count=1; awg2_state_equal=true; general_issuance_enabled=false.
- Container amn2-spain-awg31-pilot, network amn2sp31pilot, bridge amn2sp31p0, UDP 30002. Userspace AWG interface awg3 is inside the container. Automatic restart is disabled.
- Only this attempt's labelled resources are eligible for rollback. The image cache, protected profile snapshots and attempt journal remain intentionally retained.

## Protected workstation delivery

- One SFTP download, UTC 11:16:02.616085–11:16:10.750074. Exit 0, empty stderr; no retry.
- Source: the successful claim's protected windows.conf snapshot, not a regenerated profile.
- Destination: C:\Users\SooL\AppData\Local\AMN2\private-artifacts\phase16-pilot-spain-awg31-arm-20260828-002\Spain-AWG31-ARM.conf.
- New directory and file were verified non-reparse, owned by the current user, with protected ACLs and exactly one explicit FullControl allow entry for that user. Existing parent ACLs were inspected, not changed.
- File hash matched 0f97d55814824e7d34121143f8c8ed516984b0822e8a12a658d6059c69acfa65.
- Running AmneziaVPN FileVersion was verified as 5.0.1.5.
- No client installation, auto-import or tunnel enable was performed. A read-only address query found no 10.212.13.2 address yet; the operator connection is pending.
- Secret contents were not printed or committed. The downloaded private profile is retained only in the protected user directory outside the repository.

## Normalized evidence hashes

| Local ignored evidence | SHA256 |
| --- | --- |
| tmp/phase16-minimal-pilot-apply-001.json | 41700fc118bdf032cb62669a3129ae562735d7b77f58ed4ccdc655ffae877425 |
| tmp/phase16-minimal-native-diagnostic-001.json | 5cc19ad306282c4f5cf7bf4f06c7093f18701d3126e93c9b092fc8662aab5ed2 |
| tmp/phase16-minimal-native-diagnostic-002.json | 9fa57f2fb72742c624303a8f306697c92eb8a4ed3fae478270265f069e080751 |
| tmp/phase16-minimal-pilot-v4-upload-check-001.jsonl | 63159bb8c46ddf0f688c2d1b79f094b4d6a368f94ce041abb7bf4205c9361ee2 |
| tmp/phase16-minimal-pilot-apply-002.json | ae1e17cc59525285c980f81d5d5aff277e3ca24f99e35aac0123f421ac140233 |
| tmp/phase16-minimal-client-download-001.json | 9a1a634d5d4df64401b6e586dd4d5ba49578bf7b078399445f13b898970911d0 |

## Phase status and next action

- ✅ Task 0 — baseline.
- ✅ Task 1 — immutable package 016 retained.
- ✅ Task 1A — userspace correction and 22 tests PASS.
- ✅ Task 2 — corrected existing-key pair checked.
- ✅ Task 3A — isolated AWG3.1 runtime started.
- ✅ Task 4 — Windows profile delivered with verified user-only ACL.
- ▶️ Task 4.5 — first workstation connection, then bounded AWG2/AWG3.1 quality comparison.
- ⏳ Task 5 — client acceptance and the planned mobile checks.
- ⏳ Task 3B — AMN2 integration after pilot validation.
- ⏳ Task 6 — closeout.

Next: import the delivered file into Amnezia, disconnect other workstation VPNs for the test and enable this profile briefly. Confirm a fresh handshake and traffic before reporting a successful live test. If connectivity drops, disable the client profile. No additional broad server approval is needed for the already authorized first-test checks. Unrelated changes and Phase 16 closeout remain outside this step.
