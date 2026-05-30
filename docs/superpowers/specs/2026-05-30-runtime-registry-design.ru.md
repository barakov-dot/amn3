# Runtime Registry Design

## Цель

Собрать runtime-знания проекта в репозитории так, чтобы перед VPS-тестом не искать заново команды, зависимости, шаблоны `servers.yml` и правила безопасности.

## Решение

В Git храним только легкие проверяемые артефакты:

- manifest runtime-требований;
- read-only VPS checker;
- example configs;
- документацию.

Тяжелые или секретные артефакты не храним в Git. Для будущих бинарников используем GitHub Releases или отдельное хранилище, а в репозитории фиксируем только URL, версию и checksum.

## Компоненты

- `deploy/runtime/manifest.yml` - machine-readable manifest зависимостей и поддерживаемых runtime.
- `deploy/runtime/check_vps.sh` - read-only shell-checker для VPS.
- `deploy/examples/servers.host_systemd.example.yml` - пример server config для host/systemd.
- `deploy/examples/servers.docker.example.yml` - пример server config для Docker.
- `deploy/examples/.env.production.example` - production-шаблон `.env` без реальных секретов.
- `docs/RUNTIME_REGISTRY.ru.md` - инструкция для администратора.

## Runtime modes

`host_systemd` остается полноценным runtime для read-only checks и будущего apply/revoke через `awg`/`systemd`.

`docker` на текущем этапе поддерживает диагностику: Docker, контейнер, `awg` внутри контейнера, `awg show`, UDP port. Live `apply-peer`, `revoke-peer`, `collect-traffic` остаются заблокированными до подтверждения постоянного пути к конфигу внутри контейнера.

## Проверка

Добавлен тестовый контракт `tests/deploy/test_runtime_registry.py`, который проверяет наличие manifest, безопасность checker-скрипта, parseability examples и ссылки из документации.
