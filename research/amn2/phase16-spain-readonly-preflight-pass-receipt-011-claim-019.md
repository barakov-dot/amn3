# Phase 16 Spain read-only preflight PASS receipt 011 claim 019

- Recorded: `2026-08-25T19:46:52Z`
- Claim: `phase16-spain-preflight-20260825-019`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-011`
- Package identity: `d04679e145551117ce1dcab762304cf54f6b67ea9ca028a5ffc367cdeb507e99`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-25T19:31:03Z`
- Collector evidence started: `2026-08-25T19:31:03Z`
- Collector evidence ended: `2026-08-25T19:31:18Z`
- Runner exit: `0`
- Decision: `pass`
- Stop reasons: none
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `7275a07be0039ef418d52791df5ee9557c5ff00e6e369d35cf80deb17ff4d0fb`
- Collector SHA-256: `60c312fa42fc34680e348927624b458eb28f0844cc1e72e33f8deb9068af426d`
- Runner SHA-256: `29edab80f7fad171078ffd51fbcddc0ded06878327919585c4fb81e790514623`
- Ephemeral future-claim SHA-256: `265675f23fc399dd7cb75a335315cdf9b67fcf274952a9e19cc31f8c5df023ff`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`
- Resource-plan SHA-256: `2b86bf4790e1daab940dc029668f9a82d02c5d03d652bc8640ff53ae93104e65`
- Application-stage envelope SHA-256: `3561d9070afdeea84dd7251f33a5837d4855db30ff2e55cbb2b8d8cedf7d2307`
- AWG3.1-runtime-stage envelope SHA-256: `952a6be47df6a8a70ad1f75b3ce840af6837c825ace560aaa609bac0461c3230`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-019.json`
- Canonical preflight outcome / observed current-state SHA-256: `49a128e123d323e34536f6625e7d134a5c7c8299eda468457030961ec7931dfa`
- Terminal claim SHA-256: `3440545680c53fda0ed67ca2dc8c14050902c0c9d05132c0d9aaf7c1a2688207`
- Exact package-bound Python contract validation: `pass`
- Exact terminal evidence properties and decision binding: `pass`
- Observation count: `23`
- Blocking observations: none
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Temporary claim artifacts: `0`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Raw remote output persisted: `false`

## Observation summary

- `present`: `application_state`, `database_state`
- `pass`: `architecture`, `awg2_health`, `backup_capability`, `container_capability`, `disk_space`, `firewall`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, `telegram_prerequisites`
- `free`: `bridge_amn2sp3br0`, `config_path`, `container_cidr_172_29_252_0_28`, `container_name`, `interface_awg3`, `service_name`, `state_root`, `udp_30002`, `vpn_cidr_10_212_13_0_24`
- `absent`: `recovery_markers_phase14_phase15_phase16`
- `stop` or `unknown`: none

## Intended controlled-stage resources

- Application release: `/opt/amn2-spain/releases/phase16-awg3-family-3-1-spain-pilot-20260824-011`
- Checksum-bound database backup: `/var/lib/amn2-phase16/rollback/application/49a128e123d323e34536f6625e7d134a5c7c8299eda468457030961ec7931dfa.sqlite3`
- Isolated AWG3.1 state root and config: `/var/lib/amn2-spain/awg3`, `/var/lib/amn2-spain/awg3/awg3.conf`
- Service, container, Docker network, and bridge: `amn2-spain-awg3.service`, `amn2-spain-awg3`, `amn2sp3`, `amn2sp3br0`
- AWG3 interface, UDP port, container CIDR, and VPN CIDR: `awg3`, `30002`, `172.29.252.0/28`, `10.212.13.0/24`
- Runtime identity: `docker.io/amneziavpn/amneziawg-go@sha256:4e1fd2840f8d26eb6ec8bc1598e66f2f17f5d0201cd2baadbde560c104d4fc9d`
- General issuance remains disabled and no peer/config is created during stage.

## Mandatory rollback scope

- Application-stage failure removes only the newly created release/staging paths; the checksum-bound database backup remains available for controlled recovery.
- AWG3.1-runtime-stage failure removes only resources created by that attempt: `amn2-spain-awg3.service`, `amn2-spain-awg3`, `amn2sp3`, and `/var/lib/amn2-spain/awg3`.
- AWG2 runtime, interface, peers, golden bytes, routes, and firewall ownership are outside rollback scope and must remain equal before and after stage.
- Any stage failure requires rollback readback and STOP; no pilot progression is allowed.

## Safety boundary and stage gate

- Approved package-011 runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- General AWG3 issuance enabled: `false`
- Pilot peer/config created: `false`

This receipt completes the read-only Task 2 evidence. It does not authorize controlled stage, install, pilot issuance, config creation, AWG2 operation, or global AWG3 issuance. The next action requires the exact checksum- and state-bound stage approval recorded by the Phase 16 plan.
