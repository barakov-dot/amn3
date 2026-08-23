# Phase 15 package and read-only preflight readiness receipt

Date: 2026-08-23

Status: `PACKAGE_VERIFIED_LOCAL`

This receipt records the deterministic local package for the separate future
Spain read-only preflight gate. It is not an authorization or execution of
remote preflight, SSH, stage, issuance, deployment, push, or live mutation.

## Package identity

- Package ID: `phase15-dual-protocol-bootstrap-20260811-001`
- Package identity SHA-256: `cfb1dfd5452ab24039502a0842327dddb04b5264937bc3ea29d9dd6ca6b3043b`
- Manifest SHA-256: `537a458ce8b1ffa2074ec1a1d956c027c0081f4172397425f2798513410730be`
- Manifest entries: `168`
- Exact source branch/head: `codex/phase15-local-package-bootstrap-readiness` / `6b138784e9d0f02d852548de6414816b7224e145`
- Exact tooling head embedded by materialization: `0b2bdd4e6adb75fc55cd256a4e42f1fe78900fa8`
- Phase 14 receipt SHA-256: `d33e69b53c7397c567b16c4f1caea12af97969d9436d3e95e6038148054aa982`
- Phase 15 source receipt SHA-256: `642f12a6f268ee90bdd043d8268f0a7b5e2700c3064acbdbddb0b740000a79da`
- Runtime lock SHA-256: `e87133ab00e86b542092d3b4d1976fdbfc7a6339ffda27d5c85be508fe236961`
- Test lock SHA-256: `323d855f3a3aa8fa75796f3f33f6a32debeb7bd43df4f7b8fe9266398c4b1118`
- Read-only Spain collector SHA-256: `e122315df1db91f654da0411ef08cadaa15a4a4e6318f1973444ec1d531b6465`
- Resource-plan SHA-256: `39611b182535aed3226c007ae346c86a27b20af47d5a7100ba72f3b68dc55610`

## Materialization and verification evidence

- One successful checksum-bound materialization produced `168` files from the exact clean source HEAD.
- First local verifier: `verified`, identity `cfb1dfd5452ab24039502a0842327dddb04b5264937bc3ea29d9dd6ca6b3043b`.
- Focused package/contract/stage/preflight suite: `460 passed in 315.05s`.
- Per-file SHA-256 inventory was produced after the focused suite.
- Second local verifier: `verified`, with the same package identity and the same manifest SHA-256.

## Resource plan

The packaged plan is future-only and preserves AWG2 unchanged. It reserves
only AWG3 resources: interface `awg3`, bridge `amn2sp3br0`, UDP `30002`, VPN
CIDR `10.212.13.0/24`, container CIDR `172.29.252.0/28`, service
`amn2-spain-awg3.service`, container `amn2-spain-awg3`, and state root
`/var/lib/amn2-spain/awg3`.

## Secret and scope audit

- No Telegram token, SQLite header, `.env` path, or unexpected binary file was found.
- The only binary payloads are the three contract-pinned brand PNGs.
- PEM and WireGuard markers are scanner/validation text or runtime/template expressions; no raw private key or PSK material is present.
- `vpn://` matches are policy text, redaction expressions, documentation, or runtime URI construction; no issued import URI is embedded.
- The only password-shaped assignment is the hash-pinned `PASSWORD_HASH_ERROR` metadata literal; it is not a credential.
- No synthetic test token, credential, or private material is included in the package.

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
