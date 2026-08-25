# Phase 16 application source readiness receipt

- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-006`
- Baseline application SHA: `c01c2e34ca506102e485ee3fa50b9420de6e591a`
- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-006`
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
- Targeted tooling regression: `33 passed in 3.96s`
- Windows PowerShell 5 stdin BOM TDD: RED proved direct stdin forwarding preserved `EF BB BF`; GREEN strips exactly one required UTF-8 BOM and fails closed with exit `65` when absent
- Collector timestamp admission TDD: `ended_at + 15s` accepted; `ended_at + 16s` and `observed_at < started_at` rejected
- Diagnostic normalization TDD: RED `2 failed, 30 deselected`; GREEN `2 passed, 30 deselected`; empty SHA-256 input and `VoidTaskResult` pipeline output corrected
- Diagnostic normalization correction commit: `c566c63a6ab8c114af6658d04a50103517bb2ad8`
- Diagnostic normalization receipt commit: `4b039658ee09636e914af084aee3d8b094f1fdde`
- Package revision 006 binding commit: `4e3c5647faa02df3c2cda889f17a22776ab81e48`
- Phase 16 revision 005 local correction commit: `a43c91e`
- SSH `ProgramData` TDD correction commit: `18103d21bf3b2180ec126933e063cf8e5c9639b4`
- `git diff --check`: pass
- Added-line secret matches: `0`
- Application tracked status after commit: clean
- Package revision 005 immutability: manifest, collector, runner, and identity hashes match the recorded receipt
- Spain/SSH/stage/install activity during the package revision 006 local correction: none
- AWG2 changes or service operations: none

This receipt records the real Phase 16 application evidence change. It does not authorize Spain staging, runtime creation, pilot issuance, or global AWG3 issuance.
