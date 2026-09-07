# Карта кода AMN3 / VPS-OPS-LAB

Дата: 2026-09-07. Source baseline: `a4a592636b648550fa9c98dc1f084db9690615d1`.
Статическое чтение; runtime-тесты и operational scripts не запускались.
[Архитектура](ARCHITECTURE.ru.md), [вход](START_HERE.ru.md), [правила](../AGENTS.md).

Карта отвечает на вопрос «куда смотреть», а не «что запустить». Основная детализация
относится к Phase 16. Старые семейства ниже — навигация, не повторный аудит.
Наличие теста не означает полный coverage или его текущий PASS.

## Phase 16: инструменты и риск выполнения

| Вопрос | Модуль / полезные точки входа | Side effects и граница |
| --- | --- | --- |
| Состав и идентичность package016 | [phase16_awg31_package.py](../scripts/phase16_awg31_package.py): `materialize_package`, `verify_package` | Materialization читает заданные repos и создаёт пакет; immutable 016 не пересобирать ради docs/fix вне packaging |
| Формат preflight claim/evidence | [phase16_preflight_contract.py](../scripts/phase16_preflight_contract.py): `validate_claim`, `consume_claim` | Проверка/преобразование данных контракта; потребление claim в данных не равно разрешению на SSH |
| Read-only collector и его транспорт | [runner](../scripts/vps/phase16_spain_readonly_preflight_ssh_runner.ps1), [collector](../scripts/vps/phase16_spain_readonly_preflight_remote.sh) | SSH; runner пишет локальные journals/outcome. Требуется точный read-only live scope |
| Дополнительные stage prerequisites | [gate](../scripts/vps/phase16_stage_prerequisite_gate_remote.py), [runner](../scripts/vps/phase16_stage_prerequisite_gate_ssh_runner.ps1) | Диагностика target; название prerequisite не разрешает stage или повторный server run |
| Упаковка/передача controlled stage | [stage runner](../scripts/vps/phase16_controlled_stage_ssh_runner.ps1) | Проверка approval, archive/frame, SSH stdin/stdout и нормализованные failures; реальный запуск не является локальным dry-run |
| Порядок stage и rollback | [coordinator](../scripts/vps/phase16_controlled_stage_coordinator.py): `validate_stage_request`, `execute_stage`, `classify_stage_failure` | Распаковка и перенос пакета на target, claims/milestones, запуск stage, ограниченный rollback |
| Application snapshot | [application-stage](../scripts/vps/phase16_application_stage_remote.sh) | DB backup, новый release snapshot и ledger; не завершённая application activation |
| Runtime без peers | [runtime-stage](../scripts/vps/phase16_awg31_runtime_stage_remote.sh) | Docker pull, server config, network, systemd/start; отдельный install/stage approval |
| Backup/config/unit helpers | [stage support](../scripts/vps/phase16_stage_support.py): `online_sqlite_backup`, `render_server_only_awg31_config`, `render_awg31_runtime_unit` | CLI может создавать backup и чувствительный config; чтение helper не разрешает вызов |
| Минимальный peer/profile pilot | [minimal pilot](../scripts/vps/phase16_awg31_minimal_pilot.py): `normalize_dns`, `prepare_profiles`, `preflight`, `apply_pilot` | `plan` декларативен; `render` пишет профили, `check` читает target, `apply` создаёт ресурсы. Не взаимозаменяемые режимы |
| Временный forwarding/NAT | [pilot firewall](../scripts/vps/phase16_awg31_pilot_firewall.py): `render`, `baseline`, `apply_rules`, `rollback` | Helper с callbacks; live executor меняет nft rules. Не persistent firewall solution |
| Checksum-bound клиентский кандидат | [client recovery](../scripts/vps/phase16_awg31_client_recovery.py): `parse_and_validate`, `render_candidate`, `create_candidate` | Создаёт новый секретный профиль с recovery-полями, исходный не перезаписывает. Это не доказанный Windows fix и не разрешение новой выдачи |

## Связанные проверки — только при соответствующем изменении

| Что меняется | Где находятся проверки | Что они не заменяют |
| --- | --- | --- |
| DNS/render/prepare, pilot lifecycle и ownership | [minimal pilot tests](../tests/test_phase16_awg31_minimal_pilot.py) | Реальный Qt import, клиентский performance и live persistence |
| Recovery-кандидат, hash/exclusive-write | [client recovery tests](../tests/test_phase16_awg31_client_recovery.py) | Windows data-plane acceptance |
| Firewall batch, equality, state fence и rollback | [pilot firewall tests](../tests/test_phase16_awg31_pilot_firewall.py) | Readback правил на конкретном target |
| Package/preflight/stage-support contracts | [AWG31 tooling tests](../tests/test_phase16_awg31_tooling.py) | Общий live PASS; файл включает разные классы проверок и исторические package bindings |
| Coordinator milestones и failure locus | [failure locus tests](../tests/test_phase16_controlled_stage_failure_locus.py) | Успешный live rollback всей интеграции |
| PowerShell transport, процесс/потоки/ранний выход | [local transport tests](../tests/test_phase16_controlled_stage_local_transport.py) | Работу реального SSH/Windows VPN tunnel |
| Передача host параметров runner | [host forwarding tests](../tests/test_phase16_controlled_stage_runner_host_forwarding.py) | Состояние сети target; слово forwarding здесь не означает nft packet forwarding |
| Идентичность 016 / сохранность исторических пакетов | [package binding tests](../tests/test_phase16_package_016_binding.py) | Разрешение пересборки пакета или его установки |

Часть проверок использует unittest/fakes и subprocess harnesses, часть — pytest
и исходные/binding assertions. Не выдавать статическое совпадение строки за
поведенческое доказательство и не запускать весь набор по любой правке Markdown.
Перед code fix выбрать конкретное поведение и связанные тесты по [AGENTS.md](../AGENTS.md).

## Прежние семейства: указатели, не текущая очередь выполнения

| Область | Начать чтение | Пример связанного теста |
| --- | --- | --- |
| Recovery bundle / offline runtime archive | [bundle](../scripts/phase10_full_recovery_bundle.py), [runtime validator](../scripts/phase11_recovery_runtime.py) | [runtime tests](../tests/test_phase11_recovery_runtime.py) |
| Spain package / installer / backend | [package](../scripts/phase12_spain_package.py), [installer](../scripts/phase12_spain_installer.py), [backend](../scripts/phase12_spain_live_backend.py) | [package tests](../tests/test_phase12_spain_package_tooling.py) |
| Bot/web migration contracts | [contract](../scripts/phase13_bot_web_migration_contract.py) | [contract tests](../tests/test_phase13_bot_web_migration_contract.py) |
| Dual-protocol package/preflight | [package](../scripts/phase15_dual_protocol_package.py), [preflight](../scripts/phase15_preflight_contract.py) | [package tests](../tests/test_phase15_dual_protocol_package.py) |
| Старый Phase 9 progress guard | [harness](../scripts/phase9_progress_harness.py) | [harness tests](../tests/test_phase9_progress_harness.py) |
| Markdown control-character hygiene | [checker](../scripts/check_markdown_hygiene.py) | [checker tests](../tests/test_markdown_hygiene.py) |

Именованные transaction/recovery runners в `scripts/vps/` принадлежат своим
историческим approvals и исходному состоянию. Не выбирать «последний по имени»
и не повторять старую recovery-команду для новой ошибки.

## Code notes: что легко перепутать

1. Mutable tooling в `scripts/` и frozen `tooling/` внутри package016 — разные
   артефакты. Локальный DNS-fix не перенесён в существующие profiles/package/runtime.
2. Preflight collector, его runner и pure contract module — разные границы:
   read-only наблюдения на сервере не отменяют локальные записи/claim lifecycle.
3. Stage без peers и пилот с одним peer не равны общей issuance. App snapshot
   не равен переключению приложения; состав outcome сверять с конкретным gate.
4. `apply_rules` не делает remote calls на import, но вызванный live executor
   изменяет firewall. Аналогично наличие безопасного `plan` не делает безопасным `apply`.
5. Сроки, hashes и rollback limits принадлежат текущему контракту/approval;
   не брать их из примеров этого обзора. Здесь намеренно нет готовых live-команд.
6. Детали схемы БД брать из отдельно разрешённого актуального AMN2 source, а не
   выводить из SQLite backup helper или SQL в старом плане.

## Поддержка карты

Обновлять при переносе entrypoint, изменении side effects или соответствия тестов.
Не дописывать каждую функцию. Неточность в карте исправлять по исходнику, не
менять код, чтобы он соответствовал документации. Runtime-status и очередь
остаются в [плане Phase 16](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
