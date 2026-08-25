# Phase 16 application source readiness receipt

- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Baseline application SHA: `c01c2e34ca506102e485ee3fa50b9420de6e591a`
- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-007`
- Protocol family: `awg3`
- Protocol revision: `3.1`
- Config revision: `amneziawg_v3_1`
- Runtime source commit: `1f50ad736ecca22a9bfc7b4606805ec9ca49fe48`
- Runtime artifact: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`
- Runtime capabilities: `disable_cookies`, `random_trailers`
- Pilot client: `amneziawg/android/v3.1.20260814/12`
- Pilot client artifact: `github:amnezia-vpn/amneziawg-android/releases/v3.1.20260814/AmneziaWG-3.1.202060814.apk@sha256:74f109a948f012e8b90b4055e98bb9bee77bbb8e5d0fe7d5a057dd9698009697`
- Targeted application regression: `279 passed in 29.86s`
- Spain prerequisite evidence SHA-256: `24dc77231bea9ceb738ff1b2ac6efef143546a7dcfd073bb4fb4825ded43d3d6`
- Exact collector diagnostic stdout SHA-256: `5a83427b0b45b4b4e9eb6c66f0e7d63a4a104cfb77e7668a57601d6531fa474a`
- Exact Spain OS admission: `ubuntu:24.04`; Debian and every other OS fail closed
- Container admission: dedicated Spain Docker is mandatory; absent system Docker and Podman are accepted, while launch failures and conflicts fail closed
- Targeted tooling regression: `34 passed in 3.64s`
- Package 006 diagnostic: exact SSH/filter exit `65`, zero stdout/stderr, no collector schema; receipt commit `a541737545bd4b5963edbb048d49c10cc22a193c`
- Windows PowerShell 5 producer/filter TDD: RED `2 failed, 31 deselected`; GREEN `2 passed, 31 deselected in 0.50s`; raw and single-BOM inputs restore the exact checksum-bound collector while tampered and double-BOM inputs fail closed with exit `65`
- Package revision 007 binding TDD: RED `3 failed, 1 passed, 30 deselected`; GREEN `5 passed, 29 deselected in 0.52s`
- Collector timestamp admission TDD: `ended_at + 15s` accepted; `ended_at + 16s` and `observed_at < started_at` rejected
- Diagnostic normalization TDD: RED `2 failed, 30 deselected`; GREEN `2 passed, 30 deselected`; empty SHA-256 input and `VoidTaskResult` pipeline output corrected
- Diagnostic normalization correction commit: `c566c63a6ab8c114af6658d04a50103517bb2ad8`
- Diagnostic normalization receipt commit: `4b039658ee09636e914af084aee3d8b094f1fdde`
- Package revision 006 binding commit: `4e3c5647faa02df3c2cda889f17a22776ab81e48`
- Package revision 007 producer/filter correction commit: `4ba5d80546c55e140d08b4bf1b95d92d654c8111`
- Phase 16 revision 005 local correction commit: `a43c91e`
- SSH `ProgramData` TDD correction commit: `18103d21bf3b2180ec126933e063cf8e5c9639b4`
- `git diff --check`: pass
- Added-line secret matches: `0`
- Application tracked status after commit: clean
- Package revision 006 immutability: manifest `36c79003e5b5db564380fbb4471d464e5525d2439a5cfbfd2711cd1376421fe0`, collector `ed9b645839b50de4fe7fcd0fa7572ba6cbd874c7f7222e3f0f58e5c6da1b42e3`, runner `3d96607c7d5b011da1bd7db299861098cd56705a67c41298f9bb3b14244a56ad`, identity `172aba5925719473056b8d291b8f42fc0ae54e217e11094b54b81ef588efffa4`
- Spain/SSH/stage/install activity during the package revision 007 local correction: none
- AWG2 changes or service operations: none

This receipt records the real Phase 16 application evidence change. It does not authorize Spain staging, runtime creation, pilot issuance, or global AWG3 issuance.
