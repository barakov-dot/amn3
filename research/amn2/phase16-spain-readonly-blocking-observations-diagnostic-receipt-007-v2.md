# Phase 16 Spain blocking-observations diagnostic receipt 007 V2

- Recorded: `2026-08-25T08:14:20Z`
- Command ID: `PHASE16_BLOCKING_OBSERVATIONS_V2`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Package identity: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `ba2aa5e9bb0d52ff9eeb0fd029052150935f2f33786f8c12c889bf1eac1cd348`
- Bound V1 normalized output SHA-256: `8b756cb0268e1dfd2293c3a90923b31cf74e119cf3327385dc4bb8702813ba86`
- Diagnostic script SHA-256: `7ffb355bcc4944bdd3d1ed8f899b3c09450460a5782acb16333c53980d6a4135`
- Diagnostic script bytes: `11475`
- Remote observation time: `2026-08-25T08:10:45Z`
- SSH exit: `0`
- Timeout: `false`
- Normalized output schema: `amn2.phase16.blocking-observations-diagnostic.v2`
- Normalized output bytes: `2703`
- Normalized output SHA-256: `75135675fbc7cd080c1b20e3882d99e36901f6620cce7e7ebe1e1789ffdbb4db`
- Stderr present: `false`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## AWG2 interface and tool-path readback

- Owner container inspect schema: valid
- Container running: `true`
- Container PID positive: `true`
- Restart count: `59`
- Network-namespace interfaces: `awgsp0`, `eth0`, `lo`
- Rejected interface names: `0`
- Host `/usr/bin/awg`: absent
- Host `/usr/local/bin/awg`: absent
- Container-root `/usr/bin/awg`: present and executable
- Container-root `/usr/local/bin/awg`: absent

The checksum-bound collector expects interface `awg0` and invokes host path `/usr/bin/awg` after entering only the container network namespace. The observed AWG2 uses `awgsp0`, while the executable exists only below the container root. This reproduces the `awg2_health=stop` interface/tool-path contract mismatch without changing AWG2.

## Dedicated Docker network schema readback

- Network list: `ok`
- Network-ID schema: valid
- Network count: `3`
- Inspection parse failures: `0`
- User bridge: IPAM `Config` is an array with one `Gateway`/`Subnet` entry
- Built-in host network: IPAM `Config=null`, `Options=null`, no subnet
- Built-in none network: IPAM `Config=null`, `Options=null`, no subnet
- Reserved `172.29.252.0/28` overlap: `false` for all three networks

The collector requires Docker IPAM `Config` to be a list before it reaches its built-in none-network exception. It also does not admit the built-in host network's empty IPAM form. These schema assumptions reproduce the combined `container_capability`, `container_name`, and container-CIDR STOP even though no target-name or target-CIDR conflict was observed.

## Route schema readback

- Route command: `ok`
- Route JSON list schema: valid
- Route count: `21`
- Entries missing `dst`: `0`
- Observed key inventory: `dev`, `dst`, `flags`, `gateway`, `metric`, `pref`, `prefsrc`, `protocol`, `scope`, `table`, `type`
- Collector-unsupported key: `pref`
- Entries containing `pref`: `10`
- Nested route objects: none

The route collector allowlist omits the normal string-valued `pref` key, so its strict item admission returns STOP before conflict classification. V1 already established zero overlap with both reserved target networks.

## Legacy iptables schema readback

- Command: `ok`
- Exit: `0`
- Stderr present: `false`
- UTF-8: valid
- Output bytes: `0`
- Output lines: `0`
- Blank output: `true`
- CR present: `false`

The collector always parses every successful iptables backend as non-empty canonical save text. A successful empty `iptables-legacy-save` result therefore raises its missing-table/canonical-text guard and forces `firewall=stop`, even though V1 found no target reference in nft or iptables-save.

## Remaining reproduced prerequisite mismatch

V1 observed `amn2-spain-bot.service` as exact `active/enabled`; the current collector admits only exact `inactive/disabled`. This remains a separate local preflight-contract mismatch and was not re-probed by V2.

## Safety boundary

- SSH remote-command attempts: `1`
- Collector executions: `0`
- Preflight retries: `0`
- Raw stdout persisted: `false`
- Raw stderr persisted: `false`
- Remote file written: `false`
- Service/container/firewall/route mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Package manifest after completion: unchanged
- Collector after completion: unchanged
- Runner after completion: unchanged
- Preflight outcome after completion: unchanged

This V2 diagnostic closes the read-only evidence gap for the blocking observation schemas. It does not authorize a local collector correction, package materialization, another Spain egress, preflight retry, controlled stage, install, pilot issuance, or any AWG2 operation.
