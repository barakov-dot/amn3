# Phase 16 Spain read-only preflight PRELAUNCH STOP receipt 014 claim 024

- Recorded: `2026-08-26T21:01:51Z`
- Claim: `phase16-spain-preflight-20260826-024`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-014`
- Package identity: `d741006c3b0d788700020a93ac02a3bb5f35a1ec89d9497902ef7c8ac5726f19`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-26T20:58:46Z`
- Claim expires: `2026-08-26T21:03:46Z`
- Runner exit: `64`
- Runner stderr token: `AMN2_PHASE16_PREFLIGHT_RUNNER_STOP`
- Runner elapsed time: `655 ms`
- Outcome published: `false`
- SSH transport reached: `false`

## Checksum binding

- Manifest SHA-256: `844499afb51ca4cd5eacc8a395c003aabba39ffd02723ae4e95e4d28105b6cb1`
- Collector SHA-256: `59f2849561cfc6bd52a76c2ca809c69a8e4aee2eba98f0d2e6f0921bdb8ba169`
- Preflight runner SHA-256: `10994e09ffa000dbd5bb482d36e8939d6e5fbe524995d5905b8b796bf0231be8`
- Submitted future-claim SHA-256: `47d49d078b692754d4fb94f7a7a2badfc563eb5f28a60f563fb9789a71a98342`

Before invocation, a privileged read-only gate confirmed the exact package ID,
package identity, manifest hash, collector hash, and runner hash. No lifecycle,
transaction, outcome, or temporary claim artifact for claim 024 existed.

## Root-cause evidence

The local claim producer terminated the otherwise canonical JSON with CRLF.
The submitted bytes reproduce SHA-256
`47d49d078b692754d4fb94f7a7a2badfc563eb5f28a60f563fb9789a71a98342`
only with CRLF. The same claim content terminated with the single LF required by
the runner's canonical JSON contract has SHA-256
`9096d773c2ae234086d187477aee5fe462ceb70dcb78b1b04bd8297b1a9ac736`.

The runner rejects non-canonical claim framing before it initializes the claim
lifecycle, reserves an outcome, starts a transaction, or calls the SSH
transport. This is a local invocation-producer error. It is not a package-014
defect and is not evidence about Spain server state.

## Terminal readback

- Matching claim-024 state artifacts: `0`
- Lifecycle artifact: `absent`
- Transaction artifact: `absent`
- Outcome artifact: `absent`
- Recovery-outcome artifact: `absent`
- Temporary future-claim artifact: `absent`
- Active exact `-File` Phase 16 preflight runner processes: `0`
- Active Spain SSH processes: `0`
- Raw remote output persisted: `false`

## Safety boundary and next gate

- Approved runner invocation consumed: `1/1`
- SSH transport attempts: `0`
- Spain egress: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Pilot peer/config created: `false`
- General AWG3 issuance enabled: `false`
- Package revision 014 changed: `false`
- Automatic retry attempted: `false`

Any new preflight must use a new claim, single-LF canonical framing, and a new
exact package-, identity-, manifest-, collector-, runner-, and this
prelaunch-STOP-receipt-bound approval. Controlled stage, install, pilot
issuance, config creation, AWG2 operation, and global AWG3 issuance remain
unauthorized.
