# AMN2 Phase 10: VPS provider recovery and live traffic

Дата: 2026-07-13.

## Incident

VPS `4s0806-Prod-USA` был недоступен клиентам, по SSH и ICMP. VMmanager
показывал `Active`, но telemetry была `N/A`, VNC оставался на `Connecting`, а
reboot/stop operations возвращали server-side `500`/`405`. Оператор открыл
provider ticket. Reinstall, recovery mode и disk deletion не выполнялись.

## Recovery evidence

После provider-side восстановления оператор успешно подключился последним
тестовым конфигом через официальный Amnezia Client. Read-only проверка Codex
подтвердила:

```text
ssh_login=passed
icmp=reachable
source_overlay=1c7fb78
container=running|restart_count=0
awg_interface=readable
peer_count=12
fresh_handshake=true
traffic_sample_10s_rx_delta=144512
traffic_sample_10s_tx_delta=1266159
web=active|enabled
bot=inactive|disabled
```

Ни keys, peer identifiers, config payloads, DB rows, tokens, endpoints из
конфигов или secret-bearing logs не публиковались. Codex не выполнял restart,
package apply, peer mutation, config generation/delivery или Telegram action.

## Decision

Provider incident закрыт как recovered with live dataplane evidence. Текущий
локальный AMN2 source head остается `3c91601`, а VPS работает на overlay
`1c7fb78`. Upload нового source/package не смешивается с recovery и остается
отдельным контролируемым gate. Следующая инфраструктурная hardening-задача:
внешний encrypted backup runtime DB/server keys, проверяемый restore и
стабильный domain endpoint/cold-standby design.
