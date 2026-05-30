# PRVTPRO/Amnezia-Web-Panel: feature gap для `amn2` и гибрида

## Паспорт

- Upstream: https://github.com/PRVTPRO/Amnezia-Web-Panel
- Дата анализа: 2026-05-30
- Область: feature gap, decision queue, переносимость идей, blockers.
- License verdict: GPL-3.0, режим `research-only`.
- Важное ограничение: текущий код `amn2` в этом репозитории отсутствует, поэтому финальные verdict-ы требуют отдельного review в репозитории `amn2`.

## Как читать таблицу

Статусы:

- `candidate-for-amn2-review` - идея может быть полезна для `amn2`, но только как самостоятельный design spec с тест-планом.
- `hybrid-only` - идея слишком широкая для `amn2` или лучше подходит будущему гибридному VPN-продукту.
- `blocked-by-license-or-risk` - прямой перенос заблокирован GPL-3.0, security/operational рисками или обоими факторами.
- `needs-amn2-context` - без просмотра текущего `amn2` нельзя решить, нужна ли функция.
- `rejected-for-production` - подход нельзя использовать как production-модель.

| Область | Upstream идея | Для `amn2` | Для гибрида | License/risk verdict | Следующий шаг |
| --- | --- | --- | --- | --- | --- |
| First-run bootstrap | default admin user и предупреждение сменить пароль | `candidate-for-amn2-review`: forced setup или one-time bootstrap token | полезно как общий onboarding pattern | `rejected-for-production` для default `admin/admin` | подготовить bootstrap design spec |
| Session/auth model | session cookie, роли `admin`, `support`, `user` | `needs-amn2-context`: зависит от текущей auth-модели | полезно для operator/user разделения | переносить только идею role boundary | сравнить с текущими ролями `amn2` |
| API tokens | raw token показывается один раз, хранится hash | `candidate-for-amn2-review`: только со scopes, expiry, audit | полезно для integrations/CI/monitoring | upstream token слишком широкий | сделать scoped token design |
| Route taxonomy | OpenAPI groups для auth/servers/protocols/connections/settings | `candidate-for-amn2-review`: route policy matrix | полезно как product-facing API docs | низкий license-риск для идеи | завести endpoint matrix до новых API |
| Self-service | `/my/*` endpoints для user-owned config | `candidate-for-amn2-review` | полезно для user portal | secret-read surface, нужны ownership tests | описать ownership boundary |
| Public sharing | token-protected config links | `candidate-for-amn2-review`: hashed token, expiry, revoke, audit | полезно как delivery channel | plaintext share token и no mandatory expiry заблокированы | сделать share-link threat model |
| Telegram delivery | отправка config/VPN links через Telegram bot | `needs-amn2-context` | high-signal для гибрида | channel содержит sensitive data | решать после secret delivery policy |
| Backup/restore | download/restore локального state | `candidate-for-amn2-review`: redacted default, encrypted full backup | полезно для small operator installs | raw full backup заблокирован | сделать backup policy spec |
| Local JSON state | простой `data.json` с lock | `needs-amn2-context` | годится только для small/lab deployments | хранение секретов в одном файле рискованно | сравнить с текущим persistence `amn2` |
| Multi-protocol orchestration | AWG, WireGuard, Xray, MTProxy, DNS, AdGuard, SOCKS5 | `needs-amn2-context`: возможно вне scope | `hybrid-only` как core direction | прямой manager-flow не переносить | держать в гибридной архитектуре |
| Protocol managers | общий SSH layer и manager на протокол | `candidate-for-amn2-review` для contract, не кода | high-signal для plugin-like architecture | GPL + remote-exec risks | спроектировать manager interface checklist |
| Attach existing server | определить existing protocols/users/config | `needs-amn2-context` | `hybrid-only` как migration/onboarding flow | auto-detect должен быть read-only до подтверждения | описать reconciliation plan model |
| SSH/sudo execution | Paramiko, sudo, upload scripts | `candidate-for-amn2-review`: safe runner | полезно как control-plane primitive | upstream sudo/password/logging model заблокирован | сделать RemoteOperationRunner spec |
| Destructive operations | reboot, clear, uninstall, raw config save | `candidate-for-amn2-review`: только с dry-run/audit/confirmation | нужна job model | direct endpoints заблокированы | описать operation risk classes |
| Raw config editing | чтение и сохранение server-side config | `blocked-by-license-or-risk` как direct feature | возможно только как advanced operator mode | нужен parser/schema/diff/rollback | не переносить без отдельного spec |
| Status polling | ping/status checks и parallel protocol check | `candidate-for-amn2-review` | полезно для dashboards | нужен timeout/rate/cancel policy | спроектировать health check contract |
| DNS/ad-blocking services | AmneziaDNS и AdGuard Home modes | `hybrid-only` по умолчанию | high-signal для full product | static network/IP risks | оставить для гибридного backlog |
| SOCKS5 proxy | 3proxy service и credential API | `needs-amn2-context` | возможно как adjunct service | plaintext credentials и exposed proxy risk | решать после threat model |
| External sync | Remnawave sync и integrations | `needs-amn2-context` | useful integration pattern | sync-delete destructive risk | анализировать отдельным upstream/integration слоем |
| i18n/RTL | несколько языков и RTL | `needs-amn2-context` | полезно для продукта | низкий license-риск идеи | сверить с текущей UI-стратегией |

## Кандидаты ближайшего проектирования

Если начинать перенос идей в `amn2`, безопаснее идти не от функций, а от foundational specs:

1. `RemoteOperationRunner`: typed command contract, host key enrollment, redaction, audit, dry-run, fake runner.
2. Route policy matrix: endpoint, role, auth method, side effect, risk class, audit, tests.
3. Scoped API tokens: one-time display, hash storage, scopes, expiry, revoke, owner inheritance.
4. Secret inventory and backup policy: redacted default backup, encrypted full backup, restore validation.
5. Public/self-service config delivery: ownership tests, hashed share tokens, expiry, revoke, audit.

## Заблокировано или отклонено

- Прямое копирование кода, manager-flow, Dockerfile, config templates или UI из GPL-3.0 upstream.
- Default `admin/admin` как production bootstrap.
- Ephemeral `SECRET_KEY` без явной production-настройки.
- Admin-equivalent bearer tokens без scopes и expiry.
- Plaintext share tokens.
- Raw `data.json` backup как обычный download.
- Auto-accept unknown SSH host keys.
- Sudo password в shell command string.
- Destructive endpoints без dry-run, confirmation, audit и recovery note.
- Raw config editing без schema validation, diff preview и rollback.
- Docker `latest`, `curl | sh`, target-host build и package repo mutation как неявный manager-flow.

## Что требует контекста `amn2`

Перед любым переносом нужно открыть текущий `amn2` и ответить:

- какие протоколы и server lifecycle уже есть;
- где сейчас проходит auth/session/token boundary;
- есть ли роли admin/support/user или другая модель;
- как хранятся секреты и есть ли backup/export;
- есть ли SSH/control-plane слой или агентная модель;
- есть ли audit log и operation history;
- какие user-facing config delivery channels уже существуют;
- какие тесты покрывают destructive operations;
- какие функции входят в production scope, а какие должны остаться за пределами `amn2`.

## Источники

- Репозиторий: https://github.com/PRVTPRO/Amnezia-Web-Panel
- README: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/README.md
- `app.py`: https://github.com/PRVTPRO/Amnezia-Web-Panel/blob/main/app.py
- Auth/secrets deep-dive: [prvtpro-amnezia-web-panel-auth-secrets.md](prvtpro-amnezia-web-panel-auth-secrets.md)
- API surface deep-dive: [prvtpro-amnezia-web-panel-api-surface.md](prvtpro-amnezia-web-panel-api-surface.md)
- Manager architecture deep-dive: [prvtpro-amnezia-web-panel-manager-architecture.md](prvtpro-amnezia-web-panel-manager-architecture.md)
