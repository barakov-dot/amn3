# Phase 16 Spain package 010 blockers differential diagnostic receipt V6

- Recorded: `2026-08-25T17:54:15Z`
- Command ID: `PHASE16_PACKAGE010_BLOCKERS_DIFFERENTIAL_V6`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-010`
- Package identity: `0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `4622f3b6d6d4726ff93377f7127db48d84785dd3bc9e8d7b8471db4ec59a8636`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `a5691289fbeb60d78bf983bc456486f46a21186f72ae1a8d183bc7f6ed0075ef`
- Normalized stdout bytes: `1053`
- Normalized stdout SHA-256: `0ce16aba1cefa13bfa0d9b7ab4e33fa39158ed555c17c419fd4395f46338a087`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.package010-blockers-differential.v6`
- Exact normalized output validation: `pass`
- Local TDD RED: `AssertionError: diagnostic module missing`
- Local TDD GREEN: `contract=pass;redaction=pass;fixtures=pass`

## AWG2 normalized result

- Owner class: `active_stable`
- Container class: `running_stable`
- Interface class: `present`
- Handshake freshness class: `no_fresh_within_600s`
- Health: `stop`

The AWG2 owner, container identity/restart state, and `awgsp0` interface remained stable during the diagnostic. The health predicate stopped only because no handshake was fresh within the existing 600-second policy window. No public key, PID, restart count, timestamp, or other raw AWG2 value was emitted.

## Firewall normalized result

- Classification: `parser_reject`
- nft entry count: `271`
- Rule count: `195`
- Total expression count: `649`
- Accepted expression count: `649`
- Rejected expression count: `0`
- Rejected entry count: `1`
- Target conflict dimensions: none
- First rejection entry ordinal: `1`
- First rejection entry type: `metainfo`
- First rejection rule/expression ordinal: `0` / `0`
- First rejection class: `nft_metainfo`

All 649 current nft expressions are admitted by the package 010 parser contract, and the diagnostic found no target conflict involving the intended AWG3 interface, bridge, UDP port, VPN CIDR, or container CIDR. The remaining firewall STOP is isolated to the structural schema of the first nft `metainfo` entry. V6 intentionally does not reveal its key names or value types, so it is not sufficient evidence for a local parser change.

The next minimal investigation is one separately approved metainfo key/type-shape diagnostic. Before any later preflight, the operator must also generate traffic through the existing Spain/AWG2 configuration so that the unchanged 600-second freshness predicate can pass.

## Safety boundary

- Approved SSH diagnostic attempts: `1`
- Collector executions: `0`
- Remote file written: `false`
- Raw values emitted: `false`
- Raw output persisted: `false`
- Live mutation: `false`
- Diagnostic retry attempted: `false`
- Preflight retry attempted: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Temporary local diagnostic program after completion: `absent`
- Temporary local diagnostic test after completion: `absent`
- Package revision 010 changed: `false`

This V6 diagnostic is terminal for the approved attempt. It authorizes neither another diagnostic nor a parser change, preflight retry, controlled stage, install, pilot issuance, config creation, or AWG2 operation.
