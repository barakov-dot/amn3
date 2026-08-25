# Phase 16 Spain blocking-observations diagnostic receipt 007 V1

- Recorded: `2026-08-25T07:59:33Z`
- Command ID: `PHASE16_BLOCKING_OBSERVATIONS_V1`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-007`
- Package identity: `5065c10c11f82356f3bcf49432512ffae66fd7ea12b61c98c38c4ff5691af5c2`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `ba2aa5e9bb0d52ff9eeb0fd029052150935f2f33786f8c12c889bf1eac1cd348`
- Diagnostic script SHA-256: `d2fc5db5b5162b3d0f06604f38be112eb6322cc8aefee2764d01f6a4f7469fb2`
- Diagnostic script bytes: `14612`
- Started: `2026-08-25T07:58:14Z`
- Ended: `2026-08-25T07:58:16Z`
- SSH exit: `0`
- Timeout: `false`
- Normalized output schema: `amn2.phase16.blocking-observations-diagnostic.v1`
- Normalized output bytes: `3078`
- Normalized output SHA-256: `8b756cb0268e1dfd2293c3a90923b31cf74e119cf3327385dc4bb8702813ba86`
- Stderr present: `false`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## AWG2 normalized readback

- Owner unit state: `active`
- AWG2 container inspect: `ok`
- Container running: `true`
- Container PID positive: `true`
- Restart count: `59`
- Expected `awg0` interface probe: exit `1`
- Expected handshake command probe: exit `127`
- Fresh handshake result: unavailable

The preflight `awg2_health=stop` is therefore reproduced at its interface/handshake boundary even though the owner unit and container are active.

## Container-engine normalized readback

- Dedicated Spain Docker binary executable: `true`
- Dedicated Spain Docker socket present: `true`
- Dedicated inventory: `ok`, schema-valid, container count `1`
- Reserved target container `amn2-spain-awg3` present: `false`
- Dedicated network inventory: `ok`, schema-valid, network count `3`
- Dedicated network inspection command: `ok`
- Diagnostic network inspection schema admission: `false`
- System Docker binary/socket: absent
- Podman binary/socket: absent

No container-name conflict was observed. The target container CIDR remains unadmitted because the network inspection form did not pass the normalized diagnostic schema.

## Route and firewall normalized readback

- Route probe: `ok`
- Route JSON diagnostic schema: valid
- Route count: `21`
- `10.212.13.0/24` overlap count: `0`
- `172.29.252.0/28` overlap count: `0`
- nft probe: `ok`, JSON-valid, entries `271`, rules `195`, target-reference count `0`
- iptables-save probe: `ok`, schema-valid, lines `1`, target-reference count `0`
- iptables-legacy-save probe: `ok`, diagnostic schema-invalid

The normalized counters did not identify a reserved route or firewall target reference. They do not override the original checksum-bound collector STOP: its stricter route/firewall admission remains unsatisfied. The schema-invalid legacy iptables form is independently sufficient to preserve fail-closed firewall status.

## Telegram prerequisite normalized readback

- `amn2-spain-bot.service` ActiveState: `active`
- `amn2-spain-bot.service` UnitFileState: `enabled`

The current preflight contract requires exact `inactive` and `disabled`, so `telegram_prerequisites=stop` is reproduced exactly.

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

This diagnostic narrows the Phase 16 STOP but does not authorize a server-side repair, another diagnostic, a preflight retry, controlled stage, install, pilot issuance, or any AWG2 operation.
