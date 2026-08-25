# Phase 16 Spain firewall STOP match selector diagnostic receipt 009 V3

- Recorded: `2026-08-25T16:22:47Z`
- Command ID: `PHASE16_FIREWALL_STOP_MATCH_SELECTOR_V3`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `672a0037e0139f9c70a227fa7713d97dcc122a519ecaeeeebf02600d0d100184`
- Bound diagnostic V2 stdout SHA-256: `f18812daa9499c90bc0f9bf0a7a06b041c03d4c07613efeede54dc4d08aab3b3`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `f8df41d5516a109ac90c19c0e292c6411153e6b0aaff9596fa9a510e140a2018`
- Normalized stdout bytes: `4160`
- Normalized stdout SHA-256: `0ffff73e7f300f6f32ee4c05714f2bd2a853bab510e577bcee4ee9c807b43063`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.firewall-stop-match-selector.v3`
- Exact normalized output validation: `pass`

## First rejection

- Rule ordinal: `5`
- Match ordinal: `2`
- Left kind: `payload`
- Selector: `protocol`
- Protocol: `ip`
- Operator: `==`
- Right type: `string`
- Right enum class: `l4proto_allowlisted`
- Rejection locus: `match_payload_field_class`

## Rejection distribution

- Total match expressions: `149`
- Accepted by package 009: `81`
- Rejected by package 009: `68`
- Distinct normalized signatures: `18`
- `match_payload_field_class`: `10`
- `match_meta_descriptor_shape`: `54`
- `match_left_kind`: `3`
- `match_payload_shape`: `1`

## Normalized rejected signatures

- `payload / protocol / ip / == / string / l4proto_allowlisted`: `10`
- `meta / l4proto / == / string / l4proto_allowlisted`: `2`
- `meta / l4proto / == / string / l4proto_other`: `52`
- `ct / state / in / array_string / ct_state_allowlisted`: `2`
- `ct / status / in / string / non_enum_string`: `1`
- `meta / oifname / != / string / resource_checked`: `1`

The V3 evidence establishes that the package 009 parser rejects six bounded selector signatures. Four signatures are already fully classifiable without raw right values: payload protocol selection, allowlisted meta L4 protocol selection, allowlisted connection-tracking state selection, and negative output-interface matching. The remaining two signatures are not yet safe implementation inputs: 52 `meta l4proto` right strings classified as `l4proto_other`, and one `ct status` right string classified only as `non_enum_string`.

A final class-only observation must distinguish whether the 52 L4 strings are bounded decimal protocol numbers or another finite class, and whether the connection-tracking status belongs to a finite allowlist. No right-hand values need to be emitted. Until that classification exists, no parser change or package 010 is authorized by this receipt.

## Safety boundary

- Approved SSH diagnostic attempts: `1`
- Collector executions: `0`
- Remote file written: `false`
- Raw right values emitted: `false`
- Raw values emitted: `false`
- Raw output persisted: `false`
- Live mutation: `false`
- Diagnostic retry attempted: `false`
- Preflight retry attempted: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Temporary diagnostic program after completion: `absent`
- Package revision 009 changed: `false`

This diagnostic is terminal for the approved V3 attempt. It authorizes neither another diagnostic nor a parser change, preflight retry, controlled stage, install, pilot issuance, or AWG2 operation.
