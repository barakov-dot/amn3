# Amnezia ecosystem client/defaultvpn refresh 2026-06-14

Дата: 2026-06-14.

Automation source: `amnezia-weekly-upstream-refresh` aggregator output was not
available in the AMN2 working thread or local AMN3 evidence during intake. This
note uses direct public GitHub metadata refresh and marks the automation report
as `missing-input`.

License boundary: mixed upstream licenses. GPL repositories remain
research-only; permissively licensed repositories are still used as signals
only unless a separate AMN2 implementation decision exists. Do not copy
upstream code, UI, assets, templates, scripts or workflows.

## Observed upstream state

| Repo | License | Latest observed commit/release | Interpretation |
| --- | --- | --- | --- |
| `amnezia-vpn/amnezia-client` | GPL-3.0 | commit `594635e`, release `4.8.18.0` published 2026-06-11 | No new AMN2 action beyond already recorded platform/client compatibility watch. |
| `amnezia-vpn/DefaultVPN` | GPL-3.0 | commit `d139fb5` | Keeps DefaultVPN as the practical iOS/RF delivery path already documented in AMN2. |
| `amnezia-vpn/amneziawg-android` | Apache-2.0 | commit `fb64e74`, release `2.0.1` published 2026-06-12 | Useful watch-only signal for Android AmneziaWG client compatibility. |
| `amnezia-vpn/amneziawg-apple` | MIT | commit `0c4d98d`, awg-go version bump | Watch-only signal for installed/legacy iOS AmneziaWG users. |
| `amnezia-vpn/amneziawg-windows` | unknown in metadata | commit `4bab562`, awg version bump | Watch-only desktop compatibility signal. |

## AMN2 interpretation

No new public/config/write/live action is required. The data reinforces the
client matrix already added in Phase 6:

- iOS/RF default path: DefaultVPN-oriented guidance;
- installed/legacy iOS path: standalone AmneziaWG remains important for users
  who already have it;
- Android path: standalone AmneziaWG has a recent release and remains a useful
  supported import target;
- desktop path: keep `.conf`/`vpn://`/QR wording conservative and testable.

## Candidate impact

- No new active Phase 6 candidate is required from this refresh alone.
- Keep client compatibility as `watch-only` unless a concrete import failure,
  app-store availability change or protocol/config format change appears.

## Gated or deferred

- Real config delivery remains behind `P6-C002`.
- Public/self-service client flows remain behind `P6-C001` and `P6-C002`.
- Telegram live send/profile/media mutation remains behind explicit Telegram
  gates.

## Для цепочки

- Treat Android AmneziaWG `2.0.1` as watch-only client compatibility evidence.
- Keep DefaultVPN/AmneziaWG copy already added in `b3102db` as current baseline.
- No live VPS or bot update follows from this refresh by itself.
