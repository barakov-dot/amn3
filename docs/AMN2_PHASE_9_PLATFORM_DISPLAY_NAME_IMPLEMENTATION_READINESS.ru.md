# AMN2 Phase 9 Platform Display-Name Implementation Readiness

Код `AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS`.
Модель: `ChatGPT 5.3-Spark` (docs-only handoff).
Режим: docs-only, без live/VPS/SSH/config/Telegram/public gates.

## Цель

Подготовить реалистичный handoff по policy именования display-name между платформами для будущей реализации в generator-code repo:

- Canonical config/device/file naming policy: `Neobyatnaya-AMNZ-N`.
- Android import на контролируемом устройстве показывает `Сервер 1`.
- `Сервер 1 / SERVER1` трактуется как documented limitation (`client display-name compatibility gap`).
- Рефакторинг/реализация выполняется только там, где поведение приложения или генератора позволяет это делать без рисков.

## Готовые факты для handoff

```text
canonical_display_name_policy=Neobyatnaya-AMNZ-N
canonical_filename=Neobyatnaya-AMNZ-N.conf
android_observed_display_name=Сервер 1
android_display_name_classification=localized_SERVER1_documented_limitation
ios_automatic_display_name_not_proven=not_proven
```

## Implementation policy by platform

- Windows AmneziaWG standalone:
  - Реализация возможна через filename/basename импорта.
  - Нужный файл: `Neobyatnaya-AMNZ-N.conf`.
  - Ожидаемый display/tunnel name после import: `Neobyatnaya-AMNZ-N`.
- Android AmneziaWG:
  - Автоматическое выравнивание под canonical name после import не подтверждено.
  - Допуск только через documented limitation + `manual rename` fallback.
- iOS Amnezia/DefaultVPN:
  - Автономное display-name поведение не доказано.
  - До отдельного доказанного exact-решения оставить `manual rename` fallback.

## Что нужно заложить в код (будущая реализация в generator-code)

1. Генерация имени конфига/file/device по умолчанию должна быть
   `Neobyatnaya-AMNZ-N` (и `Neobyatnaya-AMNZ-N.conf`).
2. Для Windows оставить поведение basename-based (если это останется единственным
   устойчивым путём для корректного отображения).
3. Для Android/iOS предусмотреть явно помеченную ветку
   `CLIENT_DISPLAY_NAME_COMPATIBILITY_GAP` без авто-accept.
4. Не считать `SERVER1`/`Сервер 1` production naming.
5. Manual rename на стороне клиента должен быть описан как ожидаемый fallback
   до появление доказанного решения.

## Критические ограничения handoff

- Не открывать live/VPS/SSH/config/Telegram/public execution gates.
- Не выполнять public launch/public/self-service config delivery.
- Не создавать peer/config без exact named gate.
- Не менять VPS/config/auth/firewall/users/keys/ports.
- Не выводить `.conf`, `QR`, `vpn://`, private key, PSK, token, password, raw logs.

## Передача в generator-code

Что передать:

- `docs/AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS.ru.md`
- `docs/AMN2_PHASE_9_PRIVATE_SELF_CONFIG_READINESS_WITH_NAMING_REVIEW.ru.md`
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`
- `docs/PROJECT_STATUS_CURRENT.ru.md`
- `docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md`

Рекомендуемая структура future branch:

```text
generator-code/phase9-platform-display-name
├── spec.md (platform policy + fallbacks)
├── tasks.md (Windows filename-based, Android/iOS manual rename gap)
├── test-cases.md (safe non-leaky checks)
└── implementation_notes.md (fallback contract, risk notes)
```

## Следующий docs-only шаг после этой подготовке

Следовать `AMN2_PHASE_9_PLATFORM_DISPLAY_NAME_IMPLEMENTATION_READINESS` как
completed-docs-only-handoff до момента, пока `ChatGPT 5.5` не подтвердит новый
exact-gate outcome для автоматизации на Android.
