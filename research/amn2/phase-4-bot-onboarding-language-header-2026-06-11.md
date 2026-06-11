# Phase 4 bot onboarding language/header

Дата: 2026-06-11.

## Итог

Статус: `completed-local-only`.

AMN2 branch:

```text
codex/bot-onboarding-language-header
```

AMN2 commit:

```text
137d471 Add bot onboarding language header
```

Commit also fast-forwarded into:

```text
amn2/codex-vps-test-prep
```

## Что изменено

- Added bot-specific header asset `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`.
- Added `/start` onboarding with the supplied bot header image.
- Added bilingual prompt: `🌐 Выберите язык / Choose your language:`.
- Added language buttons: `🇷🇺 Русский` and `🇬🇧 English`.
- Russian remains the default user locale through `users.locale DEFAULT 'ru'`.
- Added `users.locale` schema migration and repository/workflow helpers.
- Added language choice callback that persists `ru|en` and renders the main menu in the selected locale.

## Asset boundary

Used in this slice:

```text
NEOBYATNAYA-AMNZ-BOT.png
```

Recorded for future planning only, not copied into the current bot runtime:

```text
NEOBYATNAYA-AMNZ-ADMIN-PANEL.png
NEOBYATNAYA-AMNZ-SUPPORT-BOT.png
NEOBYATNAYA-AMNZ-NEWS-BOT.png
```

The support/news bot images belong to the future separate bot split, not to the current access bot.

## Verification

RED before implementation:

```text
tests/bot/test_telegram_ux.py
tests/bot/test_bot_handlers.py
result: import errors for missing language callback/handler as expected
```

Focused verification:

```text
tests/bot/test_telegram_ux.py::test_language_keyboard_defaults_to_russian_and_offers_english
tests/bot/test_bot_handlers.py::test_handle_start_sends_header_and_language_choices_with_russian_default
tests/bot/test_bot_handlers.py::test_handle_language_choice_persists_locale_and_renders_selected_menu
tests/db/test_repositories.py::test_user_locale_defaults_to_russian_and_can_be_updated
tests/db/test_repositories.py::test_schema_migrates_existing_users_table_to_locale_default
result: 5 passed
```

Full AMN2 suite:

```text
654 passed, 1 StarletteDeprecationWarning
```

Staged hygiene:

```text
git diff --cached --check: passed
```

## Boundaries

No live VPS command, SSH command, service restart, live bot deploy, real config delivery by Codex, production peer/user mutation, public exposure, `/api/clients` CRUD, Local Agent mutation, backup/import/reboot or upstream code copy was performed.

Previous VPS rebuild package evidence remains based on older AMN2 `1508e3c`; any future VPS package apply/rebuild must rebuild from the selected current AMN2 head and rerun source/package precheck first.

## Следующая рекомендация

Do not return to `P4-BOT-ONBOARDING-001`; it is closed. The original next recommendation, `P5-I003` Runtime/toolchain standardization, was completed later in `research/amn2/phase-5-runtime-toolchain-standardization-2026-06-11.md`. `P5-I002` external-only backfill rehearsal and `P5-I004` operator-only smoke checklist were also completed later. Current next safe local-only recommendation: `P5-M003` AMN3 evidence discipline.
