# Phase 16 package revision 005 readiness receipt

- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-005`
- Package identity SHA-256: `08e39f4425f0ad433759caabc6cbb5a83fcfd57fde37c3016bde2e05bb2b8306`
- Manifest SHA-256: `0237057d79e45a129198ff15765df89319d9fa6b85366af37036dee2d44137d2`
- Collector SHA-256: `f56841cb701f8bddbe8d5f88f5d6c02d45028ee2191e70dde47f61bdcedce9be`
- Runner SHA-256: `87e3809a208306898f8e5c12e7bf12f2c140ae3c4565912da74c22b101eae7ab`
- Resource-plan SHA-256: `5289488eb38c16de7af62932b91df72e10b7c1698e18bcf9cfaee8950118aeb9`
- Source-readiness receipt SHA-256: `85392f55bdd6b41aeb6514c701a5ea08545b576360bd29c09d332b83c9c94742`
- Application branch: `codex/phase16-awg3-family-3-1-spain-pilot`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Tooling branch: `codex/phase16-awg3-family-3-1-spain-pilot-005`
- Packaged tooling source SHA: `083cd2e23317f41a9c1c95f9045a75d44dae6426`
- PowerShell 5 stdin BOM and bounded clock-skew correction commit: `a43c91e9903db9000dc714ae2e50cf042f780f48`
- Source-readiness receipt commit: `083cd2e23317f41a9c1c95f9045a75d44dae6426`
- Package revision commit: `0fe6f0a5612a4677bc162ba911bc749ec3c33807`
- Spain prerequisite evidence SHA-256: `24dc77231bea9ceb738ff1b2ac6efef143546a7dcfd073bb4fb4825ded43d3d6`
- Exact collector diagnostic stdout SHA-256: `5a83427b0b45b4b4e9eb6c66f0e7d63a4a104cfb77e7668a57601d6531fa474a`
- Exact Spain OS admission: `ubuntu:24.04`; Debian and every other OS fail closed
- Container admission: dedicated Spain Docker is mandatory; absent system Docker and Podman are accepted, while launch failures and conflicts fail closed
- Materialized manifest entry count: `168`
- Total package file count including manifest: `169`
- Actual materialization count: `1`
- Separate verifier count: `1`
- Verifier result: `verified`
- Targeted application regression: `279 passed in 29.86s`
- Targeted tooling regression: `30 passed in 3.11s`
- Windows PowerShell 5 stdin BOM filter: strips exactly one required `EF BB BF` prefix; missing prefix fails closed with exit `65`
- Maximum accepted future collector clock skew: `15s`; `16s` and timestamps before transport start fail closed
- PowerShell, shell and Python syntax checks: pass
- Canonical JSON contracts: `4` pass
- Added-line secret matches: `0`
- AWG2 path matches in the source correction diff: `0`
- Matching Phase 16 Spain SSH processes after local verification: `0`
- Historical package `phase16-awg3-family-3-1-spain-pilot-20260824-004` remained immutable
- Historical package 004 manifest SHA-256: `d19327ccb101febaa4d9cbb7a29cfb6101a62a67554e1c409909f49a3bd9b5c9`
- Historical package 004 collector SHA-256: `cb71fcfff529361c2f9c79cf65b332be884add5309703f76751ff511e36b0842`
- Historical package 004 runner SHA-256: `16475d543fdcf1934b51c58ad47b2f849c17af68badc41bd2313b3063dd6a62f`
- Historical package 004 identity SHA-256: `aec11e7ca78ba6f5f77c55e05506c613c582ec3c1bdb87f4a1338d9e3cac6d48`
- Spain egress, remote write, stage, install, and AWG2 activity during package revision 005: none

The TDD RED run demonstrated the PowerShell 5 stdin BOM and strict zero-skew failures before the production correction. GREEN and the complete tooling regression then proved exact BOM removal, fail-closed missing-BOM behavior, and the bounded `15s` future-skew contract. One actual materialization created the exact package directory, followed by one separate verifier invocation.

This readiness receipt records a verified local correction package. It does not authorize Spain preflight, application stage, runtime stage, pilot issuance, or global AWG3 issuance.
