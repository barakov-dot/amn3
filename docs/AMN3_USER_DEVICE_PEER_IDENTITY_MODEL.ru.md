# AMN3 User / Device / Peer Identity Model

Этот документ фиксирует локальную identity model для первого будущего `agent:clients:write` slice. Цель - заранее
согласовать, как AMN3 будет связывать пользователя, устройство, controller-side client record и runtime peer на
AmneziaWG-сервере. Документ не включает write routes, не включает `LOCAL_AGENT_WRITE_ENABLED`, не добавляет endpoints и
не меняет runtime.

Связанные документы:

- `docs/AMN3_WRITE_API_POLICY_MATRIX.ru.md`
- `docs/AMN3_WRITE_API_UX_FLOW.ru.md`
- `docs/AMN3_WRITE_API_AUDIT_MODEL.ru.md`
- `docs/AMN3_WRITE_API_PREFLIGHT_CONFIRMATION.ru.md`
- `docs/AMN3_LOCAL_RELEASE_GATE.ru.md`

## 1. Gate

Модель можно поддерживать локально до VPS smoke, потому что она описывает термины и границы ответственности. Реальный
apply/revoke peer остается закрытым до зеленого read-only VPS smoke и отдельного решения по `agent:clients:write`.

```text
LOCAL_AGENT_WRITE_ENABLED=false
VPS smoke required
/agent/clients* remains rejected by policy
agent:clients:write is not added to read-only token
```

## 2. Core terms

| Term | Owner | Stable | Meaning |
| --- | --- | --- | --- |
| `user_id` | controller | yes | Внутренний идентификатор пользователя AMN3. Telegram id, email или внешний CRM id могут быть связаны с ним, но не заменяют его. |
| `device_id` | controller | yes | Внутренний идентификатор устройства пользователя. Один пользователь может иметь несколько устройств. |
| `device_label` | operator/user | no | Человеческое имя устройства: laptop, phone, office router. Переименование не должно менять peer. |
| `client_id` | controller | yes | Идентификатор записи клиента, которым web admin, Telegram bot и CLI обращаются к Local Agent. |
| `server_alias` | controller/runtime config | yes | Локальное имя VPN-сервера из конфигурации, например `debian-vps-1`. |
| `protocol` | controller | yes | Первый протокол: `amneziawg`. Другие протоколы добавляются только отдельным контрактом. |
| `peer_public_key` | runtime | conditionally | Публичный ключ peer в AmneziaWG/WireGuard runtime. Не секрет, но в broad logs и audit используется fingerprint. |
| `peer_public_key_fingerprint` | controller/runtime | yes | Безопасная ссылка на peer для audit, preflight, UI и ошибок, например `sha256:<prefix>`. |

Короткие правила владения:

- `client_id is controller-owned`
- `peer_public_key is runtime-owned`
- `device_label` mutable, но `device_id` и `client_id` stable.
- `server_alias` не является hostname и не должен раскрывать SSH details.

## 3. Relationships

Базовая модель первого write slice:

```text
one user -> many devices
one device -> many server bindings over time
one device -> one active peer per server
one peer_public_key -> one active device binding per server
one client_id -> one current user/device/server binding
```

Практические следствия:

- У пользователя может быть телефон, ноутбук и роутер, каждый со своим `device_id`.
- Одно устройство может получить peer на нескольких серверах, но для одного `server_alias` активен только один peer.
- Если устройство переименовали через `device_label`, ключи не ротируются.
- Если нужно заменить ключ устройства, старый peer сначала должен быть отозван или явно заменен через подтвержденный flow.
- Повторное использование `peer_public_key` для другого пользователя или другого `device_id` на том же сервере запрещено.

## 4. Surface mapping

Web admin:

- показывает `user_id`, `device_id`, `device_label`, `client_id`, `server_alias`, status и `peer_public_key_fingerprint`;
- не показывает raw token, private key, PSK, QR, `vpn://` или полный client config в write mutation flow;
- использует `device_label` для удобного UX, но подтверждает mutation по стабильным id.

Telegram bot:

- показывает короткие label и безопасный fingerprint;
- не кладет raw token, private key, PSK, QR, `vpn://` или полный config в callback data;
- при confirmation отображает, какой `user_id`, `device_id`, `server_alias` и action подтверждаются.

CLI:

- принимает явные `client_id`, `server_alias` и operation;
- в JSON output печатает redacted summary и `peer_public_key_fingerprint`;
- не печатает raw token, private key, PSK, QR, `vpn://`, full client config или raw confirmation nonce.

Local Agent:

- работает ближе к runtime-терминам: `server_alias`, `protocol`, `peer_public_key`, planned commands;
- не должен знать Telegram/web labels как источник истины;
- возвращает только безопасные поля mutation/preflight response.

## 5. Future request mapping

Будущий apply dry-run должен получать нормализованный controller payload:

- `operation_id`;
- `user_id`;
- `device_id`;
- `device_label`;
- `client_id`;
- `server_alias`;
- `protocol=amneziawg`;
- `peer_public_key`;
- `peer_public_key_fingerprint`;
- planned VPN address or allocation reference, если allocation уже сделан controller-side.

Будущий apply mutation использует тот же request hash, свежий dry-run reference и confirmation nonce. Mutation response не
является delivery response: private key, PSK, QR, `vpn://` и полный client config остаются вне `agent:clients:write`.

Будущий revoke flow должен ссылаться минимум на:

- `operation_id`;
- `client_id`;
- `server_alias`;
- `peer_public_key_fingerprint`;
- actor surface/id;
- fresh preflight/confirmation reference.

Если revoke получает только `client_id`, controller обязан перед обращением к Local Agent разрешить его в текущий
`server_alias` и `peer_public_key_fingerprint`, иначе вернуть `validation_failed`.

## 6. Secret boundaries

Эта модель намеренно разделяет identity и delivery. В identity/write контрактах нельзя хранить или возвращать:

- raw token;
- private key;
- PSK;
- QR;
- `vpn://`;
- full client config;
- содержимое `.env`;
- SSH credentials;
- raw confirmation nonce.

`peer_public_key` не является private key, но полный public key не нужен в broad audit и UI списках. Для журналов,
preflight records, confirmation records и ошибок использовать `peer_public_key_fingerprint`.

## 7. Audit and preflight fields

Audit и preflight должны использовать одни и те же identity fields:

- `operation_id`;
- `actor_surface`;
- `actor_id`;
- `user_id`;
- `device_id`;
- `device_label`;
- `client_id`;
- `server_alias`;
- `protocol`;
- `peer_public_key_fingerprint`;
- `result_state`;
- `risk_class`;
- `rollback_reference`.

Полный `peer_public_key` допустим только в узком runtime adapter context и planned command context, если он нужен для
реального `awg`/`wg` command. В audit он заменяется fingerprint до сериализации.

## 8. Collision and rename rules

- `user_id` нельзя менять при смене Telegram username, email или внешнего account mapping.
- `device_id` нельзя менять при смене `device_label`.
- `client_id` не должен зависеть от mutable `device_label`.
- Один `peer_public_key` не может быть активен у двух разных `client_id` на одном `server_alias`.
- Revoke освобождает binding, но не делает старые secrets пригодными для повторной доставки.
- Key rotation создает новый peer binding и отдельный audit trail.

## 9. What this enables locally

- Единый словарь для web admin, Telegram bot, CLI и Local Agent.
- Подготовку первого `agent:clients:write` API без открытия write routes.
- Более точные тексты confirmation: оператор видит user/device/server, а не только key fingerprint.
- Синхронизацию audit/preflight/policy docs до VPS.

## 10. What this does not enable

- Не включает `LOCAL_AGENT_WRITE_ENABLED`.
- Не добавляет `/agent/clients*` endpoints.
- Не генерирует private key, PSK, QR или `vpn://`.
- Не меняет production defaults.
- Не делает Local Agent публичным.
- Не копирует код или runtime-подходы из сторонних проектов.
