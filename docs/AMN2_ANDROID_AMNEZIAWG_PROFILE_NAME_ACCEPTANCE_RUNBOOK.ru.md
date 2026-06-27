# Runbook: AMN2 Android AmneziaWG profile-name acceptance

Дата: 2026-06-27.
Статус: `prepared-docs-only`.

## Назначение

Подготовить безопасный future exact gate для подтверждения имени профиля после import
в Android AmneziaWG и отличить `Neobyatnaya-AMNZ-N` (ожидаемый canonical name)
от `SERVER1`/generic fallback.

## Exact gate for execution

```text
ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
```

Этот runbook не выполняется до подтверждения gate.

## Разрешено для runbook-подготовки (current chat)

- обновить и подписать runbook/результат;
- добавить/обновить task matrix;
- зафиксировать статус hold.

## Запрещено для execution без нового gate

- live/VPS/SSH/Telegram/public actions;
- generation/delivery real config;
- peer creation;
- конфиги `.conf`, QR, `vpn://` payloads;
- keys/PSK/token/password/raw logs.

## Как должен проводиться exact gate (если подтвержден отдельно)

1. Оператор подтверждает exact gate и фиксирует `run_id`.
2. Определяет один контролируемый Android device для проверки.
3. Генерирует/выбирает private/self артефакт с canonical naming:
   - logical name: `Neobyatnaya-AMNZ-N`;
   - filename: `Neobyatnaya-AMNZ-N.conf`.
4. Импортирует профиль только в локальное контрольное Android устройство (без
   массовой доставки).
5. Записывает фактически отображаемое имя после импорта в `Observed profile display
   name`.
6. При необходимости проверяет, помогает ли manual rename и требуется ли metadata
   path fix.
7. Закрывает все локальные/сервисные процессы по завершении эксперимента.
8. Заполняет result template.

## Safe output template при выполнении gate

В чат не передаём payloads. Передаём только метрики совместимости:

```text
run_id=YYYYMMDDTHHMMSSZ
gate_opened=ANDROID_AMNEZIAWG_PROFILE_NAME_ACCEPTANCE_GATE
android_device=operator-controlled
source_name=Neobyatnaya-AMNZ-N
source_filename=Neobyatnaya-AMNZ-N.conf
observed_display_name=SERVER1|Neobyatnaya-AMNZ-N|other
observed_match_expected=true|false|not-tested
manual_rename_used=true|false
manual_rename_required_for_ok=false|true
final_gate_status=passed|failed|deferred
peer_creation_performed=false
config_delivery_performed=false
secret_values_printed=false
```

## Stop lines

- Если нужен массовый import/или public/self-service путь.
- Если требуется доставлять реальные `.conf`/QR/`vpn://`.
- Если попытка выполнить import из-за lock/падения приложений вне контрольного сценария.
- Если возникает запрос на изменение `sshd`, firewall, пользователей, ключей или ports.
