# Phase 16 Spain controlled-stage STOP receipt 013 transaction 003

- Recorded: `2026-08-26T19:57:41Z`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Manifest SHA-256: `a80cd8d651b80cfa24bbe26da3c310a7823db368093d5cc7d9f4edbb864ed47`
- Approved state SHA-256: `05cbf76023426f0f6946e549168a6e6ecd7f98a94696f68fe9bd9fec01f5cf28`
- Rollback-scope SHA-256: `c70437c363cc822b602d90902d095917041e78044bb299426d7fa01aa8f17d85`
- Transaction: `phase16-spain-stage-20260826-003`
- Destination: `root@138.124.181.246`
- Gate decision: `stop-without-outcome-remote-state-unknown`
- Controlled-stage runner invocations: `1/1`
- Controlled-stage runner exit: `64`
- Stage retry attempted: `false`

## Exact runner evidence

- Started: `2026-08-26T19:51:43.3948242Z`
- Ended: `2026-08-26T19:51:44.3956322Z`
- Elapsed: `1.001` seconds
- Timed out: `false`
- Runner stdout length: `0`
- Runner stdout SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Runner stderr length: `43`
- Runner stderr SHA-256: `9e650e4049eb870274ee7321d57cca26007736a1136ff2860ba43c9cd89aeb48`
- Exact UTF-8 stderr token: `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP` followed by CRLF
- Expected local outcome: `C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260826-003.json`
- Local outcome present: `false`
- Matching target SSH processes at the before snapshot: `0`
- Matching target SSH processes at the after snapshot: `0`

The before/after process snapshots do not prove that a short-lived SSH process
was absent between them. Local Security and Sysmon process-creation events were
not available for the exact execution window. The receipt therefore does not
claim zero SSH attempts.

## Deterministic local boundary diagnostics

No stage retry or new egress was used for diagnosis. A Windows PowerShell
`5.1.26100.9168` read-only milestone probe with SSH process creation blocked
confirmed:

- trust-bundle assertion: pass;
- package inventory: `172` file records;
- manifest SHA-256: exact package-013 binding;
- rollback-scope SHA-256: exact approval binding;
- approval comparison: pass;
- in-memory archive construction: pass, `8955276` bytes;
- SSH executable resolution: `C:\Windows\System32\OpenSSH\ssh.exe`;
- SSH argument construction: `36` arguments;
- process-start-info construction: pass;
- SSH started by the probe: `false`.

A separate local argument-boundary probe used the same process-launch mechanism
as the runner wrapper and confirmed:

- package-root length: `116`;
- approval length: `510`;
- approval SHA-256: `8b2028036500f93c207db73cad3661a4c3ed47d86473e6129b1cc796cb59398e`;
- expected state, transaction, outcome path, and host: exact;
- probe exit: `0`;
- probe stderr: empty.

The temporary argument probe was removed after use. Package 013 was not
modified. These results narrow the failure to SSH process start/transport or
the remote bootstrap before a valid controlled-stage outcome reached the local
runner; they do not identify which of those classes occurred.

## Fail-closed remote disposition

- Valid controlled-stage outcome received: `false`
- Remote transaction observed as created: `unknown`
- Remote stage state: `unknown`
- Remote rollback completion: `unknown`
- AWG2 remote equality after the failed attempt: `unknown`
- Pilot peer/config created locally: `false`
- General issuance enabled locally: `false`

Because no authenticated outcome was returned, this receipt does not claim
that remote write, stage, or rollback did or did not occur. A single separate
checksum-bound read-only recovery/state diagnostic must inspect only the
transaction-003 ledgers and intended resource classes before any new stage,
pilot issuance, install, or rollback decision.

## Disposition

Transaction 003 is consumed and must not be reused. No blind retry is allowed.
The next action requires a new exact approval for one read-only SSH diagnostic,
normalized output only, no raw persistence, no remote write, no stage retry,
no install, no config issuance, and AWG2 untouched.
