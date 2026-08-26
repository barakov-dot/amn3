# Phase 16 Spain controlled-stage recovery-state diagnostic receipt 014 transaction 004 V1

- Recorded: `2026-08-26T21:48:17Z`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-014`
- Package identity: `d741006c3b0d788700020a93ac02a3bb5f35a1ec89d9497902ef7c8ac5726f19`
- Manifest SHA-256: `844499afb51ca4cd5eacc8a395c003aabba39ffd02723ae4e95e4d28105b6cb1`
- Transaction inspected: `phase16-spain-stage-20260827-004`
- Bound STOP receipt SHA-256: `8dfae3e5a27b3f1ce7ac9914f9d9babf71ee1640cf1b8a4d3969449731ef360d`
- Bound local outcome SHA-256: `c52073128fab75a6e20051e93bbe6f8a9e1d84c49f8dd833b9cc8dd8d7cdfd9a`
- Bound runner-failure SHA-256: `a6ecc0d112fdf7bb1d05a5d263de94f5cc2835c92213f362a31c1ddddfba29d9`
- Destination: `root@138.124.181.246`
- Command: `PHASE16_TRANSACTION004_RECOVERY_STATE_V1`
- SSH remote command attempts: `1/1`
- Decision: `semantic_stop_runtime_or_post_runtime_failure_locus_unproven`

## Exact transport evidence

- Started: `2026-08-26T21:48:10.8884530Z`
- Ended: `2026-08-26T21:48:17.2819233Z`
- Elapsed: `6.393` seconds
- Timed out: `false`
- SSH exit: `0`
- SSH command-line length: `26424`
- Normalized stdout length: `1196`
- Normalized stdout SHA-256: `dfc4e42185c440d24bb9e8f93396fa71998669ab891a1bbf55a87dacbe79832c`
- Stderr length: `0`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Diagnostic source length: `19141`
- Diagnostic source SHA-256: `dd502db08c30f1b7378edfd4aa13a5f4fdd3296ceec9a6b9daba4b4f2dc61fa8`
- Output schema: `amn2.phase16.transaction004-recovery-state.v1`
- Canonical JSON and structural schema validation: `pass`
- Matching target SSH processes after completion: `0`
- Raw output persisted: `false`
- Remote write performed by diagnostic: `false`
- Rollback, stage retry, install, config, and issuance performed: `false`

Two local launch preparations stopped before `ssh.exe` was created: the first
was a local wrapper parse error and the second was Windows command-line error
206. Neither consumed an SSH attempt. The only started SSH process is the
successful `1/1` attempt recorded above. The temporary local diagnostic source
was checksum-verified before launch and removed after collection.

## Normalized transaction-004 recovery state

- Transaction root: `present`
- Transaction entries: `expected_only`
- Transaction outcome: `valid_rolled_back`
- Application claim: `valid_consumed`
- Runtime claim: `valid_consumed`
- State-bound application backup: `present`
- Remote package root and manifest: `absent`
- Application release: `absent`
- Application, runtime, and coordinator ledgers: `absent`
- AWG3.1 service: `inactive`
- AWG3.1 service unit: `absent`
- AWG3.1 container and network: `absent`
- AWG3.1 state root and config: `absent`
- AWG3.1 bridge, host interface, and UDP 30002 listener: `absent`
- AWG3.1 container interface and peers: `not_queryable` because the container is absent
- Runtime image: `query_failed`; its presence or absence was not proven
- Collector overall: `ambiguous` solely because the runtime-image class was unresolved

Apart from the unresolved runtime-image class, the result contains no observed
package, release, ledger, unit, service, container, network, state, config,
interface, bridge, or listener residue. The transaction audit record and the
state-bound backup are intentionally preserved.

## AWG2 health classes

- Owner: `active`
- Container: `running`
- Container stability across the diagnostic: `stable`
- Interface: `present`
- Handshake schema: `valid`
- Handshake freshness: `stale_gt_600_or_zero`
- Overall collector-policy health: `stop`

The only AWG2 health stop is the existing 600-second traffic-recency policy.
The diagnostic did not stop, restart, rewrite, reissue, or otherwise mutate
AWG2.

## Semantic correction and trustworthy failure boundary

The V1 collector emitted the derived label
`application_and_runtime_completed_post_stage_failure`. Local code-order review
shows that this label is too strong because each stage script consumes its
claim near the start of execution, before its substantive work.

The trustworthy interpretation is narrower:

1. The application stage completed successfully, because the coordinator only
   invoked the runtime stage after the application subprocess returned a valid
   envelope.
2. The runtime stage started, validated its claim, and consumed it.
3. The available artifacts do not prove whether the runtime stage completed.
4. The failure therefore occurred either inside the runtime stage after claim
   consumption or in the coordinator's immediate post-runtime AWG2 snapshot,
   equality, or outcome-publication boundary.
5. The coordinator produced a canonical rollback outcome and the observed
   mutable stage resources are absent, subject only to the unresolved runtime
   image classification.

Structural schema validation is `pass`, but semantic acceptance is fail-closed
because the emitted stage-boundary label overstates the evidence. V1 must not
be used as proof that the runtime stage completed.

## Next bounded disposition

Transaction 004 is consumed and must not be retried. Package 014 remains
immutable. Before another Spain stage, a local TDD package revision must add an
allowlisted, no-raw coordinator milestone/failure-class artifact that
distinguishes at least application completion, runtime entry, runtime
completion, post-runtime AWG2 snapshot, AWG2 equality, outcome publication,
and rollback completion. The recovery classifier must also represent claim
consumption without equating it to stage completion and must classify the
runtime-image query without exposing raw daemon text.

This receipt authorizes no Spain egress, rollback, stage retry, install,
config/peer issuance, general issuance, or AWG2 operation.
