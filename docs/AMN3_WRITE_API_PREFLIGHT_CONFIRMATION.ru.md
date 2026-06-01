# AMN3 Write API Preflight And Confirmation

Этот документ фиксирует локальный contract для dry-run reference и confirmation challenge будущего
`agent:clients:write` slice. Он нужен, чтобы mutation не могла пройти без свежего dry-run, короткоживущего
confirmation nonce и проверки `preflight_required`.

Кодовая основа:

- `app/agent/write_confirmation.py`
- `tests/agent/test_write_confirmation.py`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md`
- `docs/AMN3_USER_DEVICE_PEER_IDENTITY_MODEL.ru.md`
- `docs/superpowers/plans/2026-06-01-local-agent-peer-command-adapter.ru.md`

## 1. Gate

Этот contract не включает write routes, не включает `LOCAL_AGENT_WRITE_ENABLED`, не создает endpoints и не меняет
runtime. Он остается локальной подготовкой до реального VPS smoke.

```text
VPS smoke required
LOCAL_AGENT_WRITE_ENABLED=false
/agent/clients* remains rejected by policy
```

## 2. Dry-run reference

`dry-run reference` создается только после успешного preflight. Минимальные поля:

- `preflight_id`;
- `operation_id`;
- `actor_surface`;
- `actor_id`;
- `server_alias`;
- `user_id`;
- `device_id`;
- `device_label`;
- `client_id`;
- `peer_public_key_fingerprint`;
- `request_hash`;
- `issued_at_epoch`;
- `expires_at_epoch`;
- `result_state`;
- `message`.

Полный `peer_public_key` не сериализуется наружу. Для проверки связности используется fingerprint.

`result_state`:

- `passed` - mutation может перейти к confirmation, если reference свежий;
- `blocked` - UI должен показать причину и не предлагать confirmation;
- `failed` - нужен новый dry-run после диагностики.

## 3. Confirmation nonce

`confirmation nonce` живет коротко и не хранится в открытом виде. Наружу выходит только `nonce_fingerprint`.

Confirmation payload содержит:

- `confirmation_id`;
- `preflight_id`;
- `operation_id`;
- `actor_surface`;
- `actor_id`;
- `server_alias`;
- `client_id`;
- `peer_public_key_fingerprint`;
- `nonce_fingerprint`;
- `issued_at_epoch`;
- `expires_at_epoch`;
- `expires_in_seconds`;
- `message`.

Payload не содержит raw token, private key, PSK, QR, `vpn://`, full client config, raw nonce или `.env`.

## 4. Mutation gate

Перед будущей mutation вызывается `ensure_mutation_allowed`.

Она должна отклонить mutation с `preflight_required`, если:

- `operation_id` не совпадает с dry-run reference;
- actor surface или actor id не совпадают;
- confirmation не относится к этому `preflight_id`;
- dry-run reference истек;
- confirmation nonce истек;
- dry-run был `blocked` или `failed`.

После `runtime_degraded`, `mutation_failed` или rollback attempt нужен новый dry-run reference.

## 5. Surface behavior

Web admin:

- запускает dry-run;
- показывает preflight summary и expiry;
- создает confirmation challenge только после `passed`;
- блокирует кнопку apply/revoke после expiry.

Telegram bot:

- confirmation nonce должен истекать быстро;
- callback data не хранит secrets;
- повторный tap после expiry получает `preflight_required`.

CLI:

- `--confirm` без свежего preflight должен получать `preflight_required`;
- JSON output должен быть redacted;
- raw nonce не печатается.

## 6. Redaction rules

Preflight и confirmation records не должны раскрывать:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- raw confirmation nonce.

`repr()` объектов должен быть безопасным для логов и audit.
