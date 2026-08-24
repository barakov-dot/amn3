# Phase 16 package revision 003 readiness receipt

- Package ID: `phase16-awg3-family-3-1-spain-pilot-20260824-003`
- Package identity SHA-256: `d47a189a86fb4ca3a475e2ec3acde20ededf0ae12a82a2d06f8e086daef4e128`
- Manifest SHA-256: `526ed0afda915f3ded0679a48899922c0081bf664b97849ee73f8892b205408c`
- Collector SHA-256: `971b2fb1d49f09c448ecbe9a33e942eb065261b21e57bc546b6e5a4043f7093a`
- Runner SHA-256: `6b3ed7fd32a4db2ef8c27feac4d09bb854310b7bdf9b60fbdf833b5cb2972ce6`
- Resource-plan SHA-256: `45a3bc2df42a8e86360c63d5b390edf41b409594e4687a7284187b23e992e41a`
- Source-readiness receipt SHA-256: `7d86e2709be134475d6ea52e62107ccd9aba8b181807d7e5ea2a4a94fd376c5c`
- Application source SHA: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Packaged tooling source SHA: `708613da0c55d4a90f105cb2873bd90d4fe0bb03`
- SSH `ProgramData` TDD correction commit: `18103d21bf3b2180ec126933e063cf8e5c9639b4`
- Package revision commit: `9c1f6e0`
- Source-readiness receipt commit: `708613d`
- Materialized manifest entry count: `168`
- Total package file count including manifest: `169`
- Materialization count: `1`
- Separate verifier count: `1`
- Verifier result: `verified`
- Targeted application regression: `279 passed in 27.94s`
- Targeted tooling regression: `16 passed in 1.94s`
- ProgramData TDD targeted regression: `3 passed in 0.62s`
- Mutation check: removing the packaged `PROGRAMDATA` assignment reproduced `ssh exit 255`
- Packaged OpenSSH local control: `0|0|OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2`
- PowerShell, shell and Python syntax checks: pass
- Canonical JSON contracts: `4` pass
- Added-line secret matches: `0`
- Matching Phase 16 Spain SSH processes after local verification: `0`
- Spain/SSH/stage/install activity during package revision 003 local correction: none
- Historical package `phase16-awg3-family-3-1-spain-pilot-20260824-001` remained immutable; manifest SHA-256 stayed `dd8737141c4aa8ef5999a96f42c70037530670e62cd6f2097ed7041507b8ed47`
- Historical package `phase16-awg3-family-3-1-spain-pilot-20260824-002` remained immutable; manifest SHA-256 stayed `7a373c6818825944b9ada204aaa18b64ccd8dbc278aba04f3393f6648dd310dc`

One initial CLI invocation used the non-empty parent `packaging` directory as `--output-root`. The materializer rejected it at its pre-write output check before repository inspection, staging directory creation, or package output creation. The corrected invocation then performed the single actual materialization into the exact new package directory.

This readiness receipt records a verified local correction package. It does not authorize Spain preflight, application stage, runtime stage, pilot issuance, or global AWG3 issuance.
