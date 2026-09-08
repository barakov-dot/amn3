# Phase 16 — согласованный комментарий для upstream #3043

Статус: текст согласован оператором; публикация не подтверждена.
API-попытка отклонена с `403 Resource not accessible by integration`;
последующий readback не обнаружил комментарий. Browser fallback недоступен.
Повторять отправку автоматически не следует.

Назначение: [amnezia-vpn/amnezia-client#3043](https://github.com/amnezia-vpn/amnezia-client/issues/3043#new_comment_field).
Скопировать только английский текст ниже в комментарий. Не прикладывать этот
файл, конфиги, raw logs или иные артефакты. Перед ручной отправкой проверить,
что совпадающий комментарий ещё не опубликован. Затем сохранить ссылку на него.
Этот черновик не закрывает Windows/quality gates и не разрешает новый live run.

## Текст комментария

Windows 11 Pro 10.0.26200, AmneziaVPN 5.0.1.5.

A sequential AWG3.1 connection establishes a handshake, but application traffic fails. The same pilot profile previously provided connectivity on Android and iPhone; this does not imply performance acceptance.

Confirmed during an active Windows run:
- Tunnel adapter Up; IPv4/IPv6 addresses and default routes present.
- MTU 1280.
- Interface counters increased: RX +9323, TX +11367 bytes.
- A bounded HTTPS request timed out.
- Temporarily disabling the kill switch did not restore connectivity.

These observations exclude missing default-route installation for that run, but do not establish the root cause or successful payload transport.

The retained ring log cannot establish the UDP socket’s selected interface. It differs from the historical checksum and contains no matching binding events for the inspected date.

Could maintainers recommend a supported, narrowly scoped diagnostic to distinguish socket-binding failure from the AWG3.1 payload-processing path? We would prefer not to repeat adapter/route-presence or kill-switch tests.
