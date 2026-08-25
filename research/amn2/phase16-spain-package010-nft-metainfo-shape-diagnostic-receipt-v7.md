# Phase 16 Spain package 010 nft metainfo shape diagnostic receipt V7

- Recorded: `2026-08-25T18:11:25Z`
- Command ID: `PHASE16_PACKAGE010_NFT_METAINFO_SHAPE_V7`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-010`
- Package identity: `0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `4622f3b6d6d4726ff93377f7127db48d84785dd3bc9e8d7b8471db4ec59a8636`
- Bound V6 normalized stdout SHA-256: `0ce16aba1cefa13bfa0d9b7ab4e33fa39158ed555c17c419fd4395f46338a087`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `025d27217a43de6ee857c0ce0990c4ddade31505f0edcda5a21ecd4db5493e20`
- Normalized stdout bytes: `1138`
- Normalized stdout SHA-256: `703343a0f55de97dd18c6c587b3887ccb14118abfaaa5eb4a20d3f474ad415d1`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.package010-nft-metainfo-shape.v7`
- Exact normalized output validation: `pass`
- Local TDD RED: `AssertionError: diagnostic module missing`
- Local TDD GREEN: `contract=pass;redaction=pass;bounds=pass;fixtures=pass`

## Normalized metainfo result

- Metainfo entry count: `1`
- Entry ordinal: `1`
- `json_schema_version`: safe key name; value type `integer`
- `release_name`: safe key name; value type `string`
- `version`: safe key name; value type `string`
- Package 010 accepts the observed entry: `false`
- First package 010 rejection locus: entry `1`, key `json_schema_version`, reason `value_type`, observed type `integer`

No metainfo value was emitted or persisted. The evidence isolates the package 010 firewall parser STOP to one exact contract mismatch: the observed nft `json_schema_version` is an integer, while package 010 requires every allowed metainfo value to be a string. The observed `release_name` and `version` types already satisfy the current string contract.

This evidence is sufficient for a local TDD change that admits an integer `json_schema_version` while retaining string-only `release_name` and `version`, the existing three-key allowlist, all other firewall validation, and the unchanged AWG2 freshness policy. It does not itself authorize that change or a new package materialization.

## Safety boundary

- Approved SSH diagnostic attempts: `1`
- Remote nft ruleset reads: `1`
- Collector executions: `0`
- AWG2 probes: `0`
- Remote file written: `false`
- Metainfo values emitted: `false`
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

This V7 diagnostic is terminal for the approved attempt. It authorizes neither another diagnostic nor a parser change, preflight retry, controlled stage, install, pilot issuance, config creation, or AWG2 operation.
