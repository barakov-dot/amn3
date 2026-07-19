# POST-RELEASE-SPAIN-001: локальная готовность перед read-only preflight

Дата проверки: 2026-07-19.

## Решение

Phase 11 уже закрыта как `completed-controlled-private-release`. Этот пакет не
переоткрывает релиз и не переносит production автоматически. Он готовит
post-release fresh-start на отдельном Spain VPS: новые подписанные оператором
конфиги, связь получатель–устройство–Device Passport, admin-only доставка и
отдельный проверяемый SSH trust boundary.

## Реализованный продуктовый контур AMN2

- оператор задаёт получателя и физическое устройство;
- canonical identity использует утверждённое имя `NEOBYATNAYA.NET`;
- выдача создаёт/связывает Device Passport и хранит безопасные метаданные,
  необходимые для дальнейшего disable/revoke;
- manifest идемпотентен, а нормализованные дубликаты отклоняются до мутаций;
- Telegram workflow допускает только admin-only handoff, проверяет write gate
  до обращения к БД/VPS и использует стабильный request id для replay;
- повтор завершённого запроса возвращает существующую выдачу, не создавая
  второго peer или второго конфига.

Проверенный source: `codex-vps-test-prep` на
`51fdba29ee1b33442bd109a0d0611c4d1348f4da`.

## Spain SSH и read-only gate

Локальный onboarding создаёт отдельный Ed25519 key, private target binding и
independent host-key pin. Пароль используется оператором только интерактивно
через provider console или системный SSH и не передаётся в Codex, Git, arguments
или evidence.

Read-only runner привязан к трём значениям:

```text
runner_sha256=4000D3B21549EBF96C773DF476492A1C9D741D27DBAF73D5DB7008DD1F6513CF
remote_probe_sha256=5485260DF91713B742E45793C079F6A18BC1B83D54AF72556EB8E6A3CC0AB345
amn2_source=51fdba29ee1b33442bd109a0d0611c4d1348f4da
```

Probe собирает только безопасную инвентаризацию ОС, capacity, ports, Docker,
systemd, firewall, effective SSH policy, clock и fingerprint постороннего
сервиса. Он не устанавливает пакеты, не меняет конфиги, не запускает и не
останавливает сервисы и не трогает AWG.

## Verification evidence

```text
amn2_scoped_tests=210_passed
amn2_full_tests=1003_passed|1_skipped|1_preexisting_starlette_httpx_warning
amn3_spain_scoped_tests=21_passed
amn3_full_tests=184_passed
diff_check=pass_after_status_sync
amn2_security_scan=20260719T_final_8b28903_51fdba2
amn2_security_coverage=20_of_20_complete|deferred_0|findings_0
amn2_security_snapshot=6728b518df4b1596417791e1846b81a0c5117e93d45d9ca3be18241dac30d7c9
amn3_security_scan=20260719T_final_a3c63a4_20ee9a6
amn3_security_coverage=2_of_2_complete|deferred_0|findings_0
amn3_security_snapshot=a3d734713e4ba006977a49afd36053f5d556fa3591438519435ab8592dd100c4
```

## Негативные гарантии

- Spain network/SSH connection не выполнялся;
- dedicated key и private binding ещё не создавались;
- provider и Spain VPS не изменялись;
- install/restart/stop/config actions не выполнялись;
- Telegram не вызывался;
- production bot, web и database не менялись;
- production AWG не останавливался и не изменялся;
- USA source server сохранён без изменений;
- идентификатор постороннего Spain service остаётся private и должен быть
  подтверждён fingerprint до и после будущего переноса;
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не изменялся и остаётся вне scope.

## Следующий отдельный gate

Сначала требуется локальный dedicated Spain SSH onboarding и ручное добавление
public key через provider console. После независимой сверки host-key pin оператор
повторяет точную checksum-bound approval-фразу для единственного read-only
preflight. Fresh install и перенос данных требуют следующего отдельного design,
rollback и live approval после анализа preflight evidence.
