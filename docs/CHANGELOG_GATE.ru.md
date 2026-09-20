# Автоматическая проверка CHANGELOG

[Правило](../AGENTS.md#обязательный-changelog--правило-перед-commit-и-push)
действует с commit `5bb1b14ad3109f7df796e009a31d1f555444e9cd`.
[Проверка](../scripts/check_changelog.py) автоматизирует его формальную часть.
Требуются Git с поддержкой --no-lazy-fetch и Python 3.10+; сторонние Python-пакеты не нужны.

## Что проверяется

- `commit-msg` проверяет именно index: запись на диске вне staging не засчитывается.
- `pre-push` получает отправляемые refs от Git и проверяет каждый новый commit.
  Запись в последнем commit не покрывает предыдущие.
- `CHANGELOG.md` должен содержать новую или изменённую непустую запись списка
  под датой `## YYYY-MM-DD`. Дата должна быть календарно допустимой.
  Переносы, пробелы, замена только даты и отдельное «обновлено/updated» не подходят.
- Достаточность описания, причина, проверка и ограничения оцениваются по diff
  человеком/агентом. Скрипт не доказывает смысловое соответствие.
- Исключение для орфографии, форматирования или ремонта ссылки без изменения
  смысла требует финального блока trailers в commit body:

  ```text
  docs: correct spelling

  Changelog: not-needed (исправлена опечатка без изменения инструкции)
  ```

  Пустая причина, шаблонное «причина/reason», «docs-only» и такая строка в
  subject/цитате не засчитываются. Скрипт выводит EXCEPTION, но не доказывает
  правомерность причины. Обход для других изменений не разрешён. Буквальные
  строки # не удаляются: в редакторе удалить служебные комментарии после trailer
  либо передать subject/body через git commit -m, чтобы trailer оставался последним.
- История до введения политики и сам вводящий commit не проверяются задним
  числом. Для новой ветки проверяются все её commits после введения политики.
  Нет нужного SHA/полной истории — ERROR, а не PASS. Сначала получить необходимую
  историю разрешённым способом; не менять policy-start ради обхода. Все Git-чтения
  запускаются с --no-lazy-fetch: partial clone не скачивает отсутствующие blobs.
  Git без поддержки этого флага также останавливает проверку.
- В диапазоне учитываются commits боковых веток. Merge дополнительно сравнивается
  с первым родителем: если слияние не приносит новой записи, нужен свой changelog
  либо правомерное обоснование отсутствия смысловых изменений. Для amend локальная
  проверка консервативно сравнивает index с текущим HEAD; диапазон проверяет итоговую
  историю. Пустой tree diff не требует записи.
- Проверка refs не разрешает push, удаление веток, force или публикацию.
  Согласование точных HEAD/origin/ref остаётся отдельным правилом.

Exit codes: `0` — формальное соответствие; `1` — нет записи/исключения;
`2` — проверку выполнить не удалось. В вывод не попадают diff, ключи или commit body.

## Подключение в рабочем worktree

Версионируемые hooks: [commit-msg](../.githooks/commit-msg),
[pre-push](../.githooks/pre-push). В Git они хранятся исполняемыми, с LF.
Перед подключением проверить текущие `core.hooksPath` и `changelog.python`:
чужие hooks не заменять, сначала согласовать совместное выполнение.

В этом проекте `extensions.worktreeConfig=true` уже включено. Проверить:

```powershell
git config --get extensions.worktreeConfig
git config --show-origin --get core.hooksPath
git config --show-origin --get changelog.python
```

Если расширение отключено/не задано — сначала отдельно разобрать конфигурацию
worktrees; не подменять `--worktree` на общий `--local` или `--global`.

При отсутствии чужих hooks подключить только выбранный worktree.
Указать реально существующий Python, а не WindowsApps alias:

```powershell
git config --worktree changelog.python C:/path/to/python.exe
git config --worktree core.hooksPath .githooks
git config --show-origin --get core.hooksPath
git config --show-origin --get changelog.python
```

После подключения ручной запуск проверки не требуется при обычных commit/push.
Другой clone/worktree автоматически не наследует локальную настройку.
Если настроенного Python нет, hook остановит операцию; это ошибка среды.

Для read-only проверки вручную:

```text
python scripts/check_changelog.py --staged
python scripts/check_changelog.py --staged --message-file path/to/commit-message.txt
python scripts/check_changelog.py --range BASE_SHA HEAD_SHA
python -m unittest discover -s tests -p test_changelog_gate.py -v
```

Откат настройки после согласования: восстановить прежние значения именно в
worktree config. Если их раньше не было — `git config --worktree --unset core.hooksPath`
и аналогично `changelog.python`. Исходники и история при этом не меняются.

## GitHub и границы защиты

[Workflow](../.github/workflows/changelog.yml) подготовлен для push веток и PR:
полная история, точные base/head SHA, Python stdlib tests и проверка диапазона.
У токена только contents:read, checkout не сохраняет credentials; внешних
комментариев и deployments нет. Checkout закреплён по SHA официального
[actions/checkout](https://github.com/actions/checkout); правила событий —
[GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

Локальный PASS не означает выполненный GitHub run. После первого разрешённого
push нужен readback CI. Required status check/branch protection не настраивались:
workflow сам по себе не запрещает merge и не отменяет уже принятый push.
Локальные hooks также можно технически отключить; это страховка от пропуска,
а не защита от намеренного обхода.

## Локальная проверка 2026-09-20

Hooks подключены только в активном worktree этой задачи через config.worktree;
readback core.hooksPath=.githooks и отдельного changelog.python выполнен.
Общие/глобальные настройки hooks и соседние worktrees не менялись.
Диапазон от policy-start до HEAD на момент проверки (2 новых commits) PASS.

26 integration tests PASS (Git 2.54.0.windows.1) на временных Git-репозиториях: stage/unstaged,
пустые/недатированные записи, исключения, история и merges, новые refs,
ошибки истории, реальный commit hook и реальный pre-push hook. Для push-теста
используется только временный локальный bare repository, без сетевого сервера;
отклонённый push оставляет его ref неизменным. Тестовые данные синтетические.
RED/GREEN подтвердил исправления пути из вложенной папки, буквальных # строк
после trailer и неявной загрузки blobs. Partial-clone тест использует file://
источник в temp, проверяет ERROR и неизменность списка отсутствующих объектов.
Это проверка Git workflow, а не VPN, сервера или Phase16 acceptance.

Два существующих markdown-hygiene tests также PASS. GitHub/Linux run ещё не выполнен.
