# Phase 15 package and read-only preflight readiness receipt

Date: 2026-08-24

Status: `PACKAGE_VERIFIED_LOCAL`

This receipt records the deterministic local package for the separate future
Spain read-only preflight gate. It is not an authorization or execution of
remote preflight, SSH, stage, issuance, deployment, push, or live mutation.

## Package identity

- Package ID: `phase15-dual-protocol-bootstrap-20260811-001`
- Package identity SHA-256: `00b56972a7e3f3423fb3a1d6437f877910b6f23c690fe9a398ce8263d74faf1d`
- Manifest SHA-256: `d99e6e6b7df651f7cda6f63de2ee9b2a353afef4bfe1c93e82391d5c48aac6df`
- Manifest entries: `168`
- Exact source branch/head: `codex/phase15-local-package-bootstrap-readiness` / `c01c2e34ca506102e485ee3fa50b9420de6e591a`
- Exact tooling head embedded by materialization: `b2d37b830c27360dee7405dc7d6219af5523c3fa`
- Phase 14 receipt SHA-256: `d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982`
- Phase 15 source receipt SHA-256: `0d45708c6aab6b7812ffa8ca05d052f1db175086f57c504b5af8e1f6a99c4eb8`
- Runtime lock SHA-256: `a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab`
- Test lock SHA-256: `52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235`
- Read-only Spain collector SHA-256: `e122315df1db91f654da0411ef08cadaa15a4a4e6318f1973444ec1d531b6465`
- Resource-plan SHA-256: `39611b182535aed3226c007ae346c86a27b20af47d5a7100ba72f3b68dc55610`

## Materialization and verification evidence

- One successful checksum-bound materialization produced `168` files from the exact clean source HEAD.
- First local verifier on the final package root: `verified`, identity `00b56972a7e3f3423fb3a1d6437f877910b6f23c690fe9a398ce8263d74faf1d`.
- Focused package/contract/stage/preflight suite: `460 passed in 315.80s`.
- Per-file SHA-256 inventory was produced after the focused suite.
- Second local verifier: `verified`, with the same package identity and the same manifest SHA-256.

## Resource plan

The packaged plan is future-only and preserves AWG2 unchanged. It reserves
only AWG3 resources: interface `awg3`, bridge `amn2sp3br0`, UDP `30002`, VPN
CIDR `10.212.13.0/24`, container CIDR `172.29.252.0/28`, service
`amn2-spain-awg3.service`, container `amn2-spain-awg3`, and state root
`/var/lib/amn2-spain/awg3`.

## Secret and scope audit

- No Telegram token, SQLite header, `.env` file, database/key/config suffix, or unexpected binary file was found.
- The only binary payloads are the three contract-pinned brand PNGs.
- PEM and WireGuard markers are scanner/validation text or runtime/template expressions; no raw private key or PSK material is present.
- `vpn://` matches are policy text, redaction expressions, documentation, or runtime URI construction; no issued import URI is embedded.
- The only password-shaped assignment is the hash-pinned `PASSWORD_HASH_ERROR` metadata literal; it is not a credential.
- No credential, issued token, or private material is included in the package.

## Control and execution state

```text
AWG2_DEFAULT_PRESERVED=true
AWG3_GLOBAL_ACCEPTANCE_REQUIRED=true
AWG3_PER_USER_ADMIN_APPROVAL_REQUIRED=false
PACKAGE_MATERIALIZED=true
PACKAGE_VERIFIED_LOCAL=true
REMOTE_PREFLIGHT_RUN=false
SSH_USED=false
APPLICATION_STAGED=false
AWG3_RUNTIME_STAGED=false
AWG3_PILOT_ISSUED=false
AWG3_GLOBAL_ACCEPTED=false
AWG3_ISSUANCE_ENABLED=false
LIVE_MUTATION=false
```

## Boundary

Remote preflight, SSH, stage, issuance, deployment, push, and every live
mutation did not occur. The next separately authorized action may be only a
checksum-bound Spain read-only preflight using the exact package identity and
collector hash recorded above.
