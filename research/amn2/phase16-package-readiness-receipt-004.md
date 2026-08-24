# Phase 16 package revision 004 readiness receipt

- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-004`
- Package identity SHA-256: `aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48`
- Manifest SHA-256: `d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9`
- Collector SHA-256: `cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842`
- Runner SHA-256: `16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f`
- Resource-plan SHA-256: `741b69d531331a2d0d9e4ea7d13fe75b9b3f7ae5a0bfdc452f907b6dfc22c5b0`
- Source-readiness receipt SHA-256: `4eea01b615c507fbcf180468990a7521793768bdbfed1f4a689fa764a55c7db7`
- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-004`
- Packaged tooling source SHA: `91b0e581a8db14e926b03d5fe6b9a24426ecded7`
- Ubuntu 24.04 and dedicated Docker admission correction commit: `31c185e267552f3f65cfe3b977e89e0bd0ba519c`
- Package revision commit: `e730d9e863716efe00121fc572becede8f4d9397`
- Tooling branch gate correction commit: `484970a280eb8230a6c8bb52b0beaa9e307504a8`
- Source-readiness receipt commit: `91b0e581a8db14e926b03d5fe6b9a24426ecded7`
- Spain prerequisite evidence SHA-256: `24dc77231bea9ceb738ff1b2ac6efef143546a7dcfd073bb4fb4825ded43d3d6`
- Exact collector diagnostic stdout SHA-256: `5a83427b0b45b4b4e9eb6c66f0e7d63a4a104cfb77e7668a57601d6531fa474a`
- Exact Spain OS admission: `ubuntu:24.04`; Debian and every other OS fail closed
- Container admission: dedicated Spain Docker is mandatory; absent system Docker and Podman are accepted, while launch failures and conflicts fail closed
- Materialized manifest entry count: `168`
- Total package file count including manifest: `169`
- Actual materialization count: `1`
- Separate verifier count: `1`
- Verifier result: `verified`
- Targeted application regression: `279 passed in 27.94s`
- Targeted tooling regression: `24 passed in 1.71s`
- Windows PowerShell 5 full-payload async transport diagnostic: pass; production runner transport logic unchanged
- PowerShell, shell and Python syntax checks: pass
- Canonical JSON contracts: `4` pass
- Added-line secret matches: `0`
- Matching Phase 16 Spain SSH processes after local verification: `0`
- Spain egress, remote write, stage, install, and AWG2 activity during package revision 004: none
- Historical package `phase16-awg3-family-3-1-spain-pilot-20260824-003` remained immutable; manifest SHA-256 stayed `526ed0afda915f3ded0679a48899922c0081bf664b97849ee73f8892b205408c`
- Historical package 003 collector SHA-256 stayed `971b2fb1d49f09c448ecbe9a33e942eb065261b21e57bc546b6e5a4043f7093a`
- Historical package 003 runner SHA-256 stayed `6b3ed7fd32a4db2ef8c27feac4d09bb854310b7bdf9b60fbdf833b5cb2972ce6`

The first materializer invocation was rejected at the repository branch gate before staging-directory or package-output creation. A RED/GREEN regression then separated the application and tooling branch gates. The corrected invocation performed the single actual materialization into the exact new package directory, followed by the single separate verifier.

This readiness receipt records a verified local correction package. It does not authorize Spain preflight, application stage, runtime stage, pilot issuance, or global AWG3 issuance.
