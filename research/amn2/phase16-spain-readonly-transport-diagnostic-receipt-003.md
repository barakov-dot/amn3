# Phase 16 Spain read-only transport diagnostic receipt 003

- Failed preflight claim: `phase16-spain-preflight-20260824-003`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-002`
- Package identity: `7189748b7c0b1852b9c3e47de6789ece9a1fa4f6d4713d33dd8309041f9555bd`
- Failed outcome SHA-256: `a5197f9ddb854a6e9951475e82436231e1899549e824d104e07247e0327f7179`
- Diagnostic authorization: one bounded SSH handshake attempt, no remote command or write

## Root cause

The packaged runner clears the `ProcessStartInfo.EnvironmentVariables` collection before launching Windows OpenSSH, then restores `SYSTEMROOT`, `WINDIR`, `PATH`, `HOME`, and `USERPROFILE` but not `ProgramData`.

On this host, `C:\Windows\System32\OpenSSH\ssh.exe` version `OpenSSH_for_Windows_9.5p2` exits locally with code `255` and zero stdout/stderr when invoked in that exact environment. Adding only the inherited `ProgramData` value changes the local `ssh -V` control to exit `0` and emits the expected version. This reproduces and isolates the original immediate `transport_failed` before any remote collector execution.

The runner's `--` argument was tested independently with local-only `ssh -G` after restoring `ProgramData`; both variants exited `0` and produced equivalent configuration output. It is not the cause.

## Diagnostic disposition

- Corrected network handshake performed: `false`
- Reason: the root cause was established with local-only `ssh -V` and `ssh -G`; further egress was unnecessary
- Remote command executed by this diagnostic: `false`
- Remote file written: `false`
- Preflight retried: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`

An initial diagnostic wrapper invocation used malformed local argv quoting and exited in `22 ms` with code `255` and zero stdout/stderr. It did not provide server evidence and was discarded. The corrected checks were local-only.

## Required remediation boundary

Package `phase16-awg3-family-3-1-spain-pilot-20260824-002` remains immutable and must not be retried. The source runner requires a TDD correction that restores a validated `ProgramData` value in the cleared SSH environment, followed by a new package identity, materialization, verification, and separate read-only preflight authorization. No stage authorization is valid from this receipt.
