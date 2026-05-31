# PRVTPRO/Amnezia-Web-Panel: config delivery integrity

## Паспорт

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата анализа: 2026-05-31
- Область: выдача VPN-конфигов через `.conf`, QR, `vpn://`, self-service и public share.
- Лицензия upstream: GNU GPL v3.0.
- Статус для `amn2`: `research-only`, без копирования кода или UI-реализации.

## Что проверялось

Проверялись не только README и общая архитектура, а конкретные участки, которые влияют на доставку пользовательского конфига:

- `app.py`: `generate_vpn_link`, public share endpoints и self-service config endpoint.
- `templates/server.html`, `templates/my_connections.html`, `templates/user_share.html`: UI-потоки показа `.conf`, `vpn://` и QR.
- `static/js/qrcode.min.js`: клиентская генерация QR.
- `managers/wireguard_manager.py` и `managers/awg_manager.py`: сигнатуры `get_client_config`.
- GitHub issues #41, #49 и #51 как сигналы реальных пользовательских поломок.

## Как устроена выдача конфига в upstream

В upstream есть несколько поверхностей выдачи secret-bearing config:

- admin/operator flow на странице сервера: создание connection и кнопка показа config;
- self-service endpoint `/api/my/connections/{connection_id}/config`;
- public share endpoint `/api/share/{token}/config/{connection_id}`;
- вкладки UI: raw config, `vpn://` link и QR.

`generate_vpn_link` в `app.py` строит `vpn://` как base64 от UTF-8 текста конфига. Это важно: `vpn://` не является безопасной ссылкой без секрета, а обратимо кодирует тот же config body.

В UI QR генерируется из raw config text, а не из `vpn://` link. Это может быть корректно для стандартного WireGuard-import сценария, но не должно быть неявным поведением: для каждого protocol/client target нужно явно знать, что именно должен содержать QR - `.conf` payload или import URI.

Public share использует token-protected ссылку без panel session. Это удобно, но превращает share endpoint в `secret-read` поверхность, где обязательны ownership check, expiry, revoke, rate limit, audit и redaction.

## GitHub-сигналы

### Issue #41: QR и Android import

Issue #41 описывает ситуацию, где QR для AWG не импортируется на Android, а также ломается import из `.conf`. Автор показывает byte-level симптом: в QR-потоке теряются байты UTF-8 для кириллического символа. Это не косметический UI-баг, а сигнал, что config delivery надо проверять на уровне байтов и реального импорта.

Вывод для `amn2`: нельзя считать QR успешным только потому, что картинка отрисовалась. Нужно декодировать QR в тесте и сравнивать payload с ожидаемым UTF-8 byte stream.

### Issue #51: повторный сигнал по Android QR

Issue #51 короче, но подтверждает тот же класс проблемы: QR не работает на Android. Для lab это усиливает приоритет тестов совместимости с Android/client import.

### Issue #49: manager export contract mismatch

Issue #49 показывает runtime error при показе WireGuard config: handler вызывает `get_client_config` с protocol, client id, host и port, а `WireGuardManager.get_client_config` принимает другой набор аргументов.

В `app.py` уже есть helper `_manager_call`, который учитывает отличие WireGuard manager-а, но self-service/share config endpoints по проверенному фрагменту все еще вызывают `manager.get_client_config(...)` напрямую. Даже если upstream позже исправит это локально, для нас важен сам класс риска: config export должен быть единым контрактом manager-а, а не набором похожих, но несовместимых сигнатур.

## Технические наблюдения

- `.conf`, QR и `vpn://` - разные delivery artifacts. Они могут содержать один и тот же секрет, но формат, target client и тесты у них разные.
- QR-генерация на клиенте через старый bundled `qrcode.min.js` повышает риск encoding regressions, особенно для non-ASCII names. Для production-направления лучше иметь тестируемую генерацию с явным UTF-8 payload.
- Ошибки config export не должны возвращать пользователю raw `str(e)`, если там может быть внутренняя сигнатура, путь, command output или другой diagnostic detail.
- Public share token нельзя воспринимать как обычный UI state. Это authorization material, особенно если по нему можно получить private key или импортируемый config.
- Manager contract должен включать не только `add/remove/list`, но и `export_config`/`export_artifacts` с единым результатом и capability flags.

## Требования, которые стоит перенести в `amn2`

### 1. Явная модель delivery artifacts

Для `amn2` стоит проектировать выдачу конфига как набор typed artifacts:

- `wireguard_conf`: raw text `.conf`;
- `amnezia_import_uri`: `vpn://` или будущий аналог;
- `qr_payload`: что именно кодируется в QR;
- `download_file`: имя файла, MIME/type, encoding;
- `client_target`: Amnezia Android, Amnezia desktop, WireGuard Android, WireGuard desktop и т.п.

Каждый artifact должен иметь `secret_class=secret-read`, owner/resource check, audit summary без payload и redaction policy.

### 2. Byte-level и import-level тесты

Минимальный тест-план перед production-переносом:

- round-trip `.conf` как UTF-8 bytes;
- non-ASCII connection/user/server names, включая кириллицу;
- QR decode test: декодированный payload строго равен ожидаемому payload;
- `vpn://` decode test: base64 возвращает исходный config без потерь;
- Android/import compatibility smoke на уровне доступного parser/fixture;
- тесты, что config, QR payload и `vpn://` не попадают в logs, audit, metrics и error response.

### 3. Единый manager export contract

Для каждого protocol manager-а нужен один контракт, например capability `export_config`, который возвращает нормализованный результат:

- protocol id;
- connection/client id;
- raw config text, если доступен;
- import URI, если применим;
- список supported delivery artifacts;
- warnings, например private key отсутствует и config нельзя восстановить;
- sanitized error model.

Этот контракт должен проверяться contract tests для каждого manager-а, чтобы ошибка класса #49 не доходила до UI.

### 4. Public/self-service guardrails

Если в `amn2` появится public/self-service delivery:

- share token хранить только как hash;
- raw token показывать один раз;
- поддержать expiry, revoke и rate limit;
- обязательно проверять ownership connection-а;
- audit писать без raw token, config body, QR payload и import link;
- ошибки наружу отдавать как безопасные категории, а detail оставлять только в redacted server log.

### 5. UI/UX правило

UI должен явно показывать, что пользователь получает:

- `.conf` file;
- import link;
- QR для конкретного target client.

Если для разных клиентов нужен разный QR payload, это должно быть отдельным выбором или отдельными кнопками, а не скрытой логикой.

## Вывод

Эта тема уже применима к `amn2`, но не как перенос фичи из PRVTPRO. Правильный перенос - добавить в наш design/test checklist требование: config delivery считается готовой только после проверки формата, байтов, import compatibility, secret redaction и manager contract tests.

Ближайший практический шаг для `amn2`: расширить `Public/Self-service Config Delivery` spec тест-планом на `.conf`, QR, `vpn://` и manager export contract. До этого public share и QR/import UX лучше не расширять.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- `templates/server.html`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/templates/server.html
- `templates/my_connections.html`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/templates/my_connections.html
- `templates/user_share.html`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/templates/user_share.html
- `static/js/qrcode.min.js`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/static/js/qrcode.min.js
- `managers/wireguard_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/wireguard_manager.py
- `managers/awg_manager.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/managers/awg_manager.py
- Issue #41: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/41
- Issue #49: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/49
- Issue #51: https://github.com/PRVTPRO/Amnezia-Web-Panel/issues/51
