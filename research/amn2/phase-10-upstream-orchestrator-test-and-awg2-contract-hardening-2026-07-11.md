# Phase 10: тестовый upstream orchestrator и AWG2 contract hardening

Дата: 2026-07-11.

Статус: `completed-integrated-into-phase10`.

## Границы

Прогон выполнен последовательно: PRVTPRO, kyoresuas, официальная экосистема
Amnezia, затем общая продуктовая матрица AMN2.

Во время прогона не выполнялись live VPS/SSH/Telegram/public/config delivery,
peer creation, runtime mutation, package apply или secret-bearing действия.
Upstream-код, шаблоны, managers и workflows не копировались.

## AMN2 baseline

```text
active_phase=Phase 10 product recovery with progress harness
source_baseline=amn2/codex-vps-test-prep@ecf8563
selected_product_direction=safe VPN access lifecycle control plane
launch_scope_change=false
```

AMN2 рассматривается не как multi-protocol installer или копия web-panel, а
как безопасный control plane жизненного цикла пользователя и физического
устройства: compatibility, diagnostics, preview/apply/verify/rollback,
secret-safe delivery и recovery.

## Source cursors

### PRVTPRO/Amnezia-Web-Panel

```text
previous_cursor=a62f958
previous_release=v1.4.4
observed_head=dd8bda3ac182685b48553b2c8970097ba47bddb1
observed_release=v1.5.0
coverage=complete-for-commits-release-readme-and-relevant-prs
```

Источники:

- https://github.com/PRVTPRO/Amnezia-Web-Panel/commit/dd8bda3ac182685b48553b2c8970097ba47bddb1
- https://github.com/PRVTPRO/Amnezia-Web-Panel/releases/tag/v1.5.0
- https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/68
- https://github.com/PRVTPRO/Amnezia-Web-Panel/pull/70

Новый release добавляет WARP, marketplace/templates, multi-protocol,
NGINX/Let's Encrypt, alpha backup/migration и Telegram admin role. Для AMN2
это преимущественно `better-left-upstream`: эти функции не усиливают текущую
продуктовую специализацию и не входят в launch scope.

Два полезных negative-learning сигнала:

- AWG2 H1-H4 должны корректно разбираться как single values или ranges, а
  диапазоны разных message types не должны пересекаться;
- VPN subnet должен иметь единый runtime source of truth для server config,
  NAT/firewall и client IP allocation, иначе изменение Address оставляет stale
  startup rules.

Лицензия PRVTPRO: GPL-3.0. Допустим только самостоятельный дизайн поведения и
локальные тесты без переноса реализации.

### kyoresuas/amnezia-api

```text
previous_cursor=96a1f54c5942f7d8572e743ac90a018b60ce483a
observed_head=96a1f54c5942f7d8572e743ac90a018b60ce483a
observed_release=none
coverage=no-delta
```

Источник:

- https://github.com/kyoresuas/amnezia-api/commit/96a1f54c5942f7d8572e743ac90a018b60ce483a

Новых коммитов после сохраненного cursor не обнаружено. Старые сигналы про
atomic config write, mutation lock, lifecycle, time contract и QR не
переоткрываются как новые задачи.

### Official Amnezia ecosystem

```text
amnezia_client_previous=0f6847219b87e94e9948bee3f57a4d7a2465acb4
amnezia_client_observed=5e70eb20c9ce38b76ca64c32d98847eb07987237
amnezia_client_latest_release=4.8.19.0
amneziawg_android_latest_release=2.0.1
amneziawg_windows_client_observed=e628cbd6092ae783d5ee6d376ddaaaba8c467ddc
amneziawg_windows_client_latest_release=2.0.1
amneziawg_go_observed=c1e9bb3758e71bb1adc402598465565bfc9663fd
coverage=complete-for-relevant-deltas-plus-lightweight-radar
```

Источники:

- https://github.com/amnezia-vpn/amnezia-client/commit/5e70eb20c9ce38b76ca64c32d98847eb07987237
- https://github.com/amnezia-vpn/amnezia-client/pull/2763
- https://github.com/amnezia-vpn/amnezia-client/releases/tag/4.8.19.0
- https://github.com/amnezia-vpn/amneziawg-android/releases/tag/2.0.1
- https://github.com/amnezia-vpn/amneziawg-windows-client/commit/e628cbd6092ae783d5ee6d376ddaaaba8c467ddc
- https://github.com/amnezia-vpn/amneziawg-go/commit/f6542209f40f3f8f9e3dc9403d331ad2881fd7e3
- https://github.com/amnezia-vpn/amneziawg-go/blob/c1e9bb3758e71bb1adc402598465565bfc9663fd/README.md

Свежий `amnezia-client` dev delta исправляет file picker для Android TV 9/10
и блокирует повторный запуск restore. Published release пока не изменился,
поэтому Android TV сигнал остается `watch-only`: повторная acceptance нужна
после опубликованного release, а не на unreleased dev head.

Официальный `amneziawg-go` подтверждает uint32 single/range format H1-H4 и
неоднозначность пересекающихся ranges. Это усиливает independent AMN2
contract-test, но не разрешает автоматическую смену live defaults.

В lightweight radar добавлены:

- `amneziawg-go`, `amneziawg-tools`, `amneziawg-linux-kernel-module`;
- `amneziawg-windows-client`, `amneziawg-apple`, `amneziawg-android`;
- `amneziawg-exporter` как источник privacy-safe metrics lessons;
- `amneziawg-openwrt` как post-launch client/platform watch;
- `amnezia-libxray`, `amnezia-xray-core`, `DefaultVPN`.

## Decision matrix

### Candidate now: AWG2 magic-header contract

Классификация: `candidate-now-engineering-check`.

Результат: отдельный local-only slice от `ecf8563` был реализован в ветке
`codex/phase10-upstream-contract-hardening`, commit `dc0ed92`. После проверки
ancestry он интегрирован fast-forward в текущую Phase 10 ветку без слепого
переключения рабочей ветки.

Покрыто:

- H1-H4 принимают uint32 single values и `min-max` ranges;
- malformed, descending и out-of-uint32 значения отклоняются;
- четыре ranges/single values не могут пересекаться;
- проверка применяется к Settings, defaults и render input;
- текущие проверенные single-value defaults не изменены;
- live server/client migration не выполнялась.

Проверка:

```text
focused=56 passed
expanded=123 passed, 1 warning
full=840 passed, 1 skipped, 1 warning
python_3_12_13_compile_and_runtime_smoke=passed
live_actions=false
```

### Integration result

```text
phase10_branch=codex-vps-test-prep
integration_base=ecf85632216724ff22da48314321d01339f416e9
upstream_commit=dc0ed92f3280903570fcc3cfbb4329e0bf880800
integration_method=fast-forward-only
review_fix=44287d4_require_ascii_awg_magic_headers
integrated_head=44287d4
candidate_status=integrated-do-not-reoffer-dc0ed92
```

Перед интеграцией подтверждено, что `ecf8563` является прямым предком
`dc0ed92`; текущая Phase 10 ветка вперед не ушла. Первичный diff ограничен
Settings, AWG2 config contract и их тестами. Повторно воспроизведены исходные
результаты `56/123/840`.

Diff review выявил один дополнительный wire-contract edge case: `\d` в
Python принимает Unicode decimal digits, хотя H1-H4 должны иметь ASCII
uint32/range syntax. В `44287d4` lexical contract сужен до `[0-9]`, добавлен
регрессионный тест на Unicode digits.

Финальная проверка интегрированного head:

```text
focused=57 passed
expanded=124 passed, 1 warning
full=841 passed, 1 skipped, 1 warning
python_3_12_13_compile_and_runtime_smoke=passed
diff_review=passed
live_actions=false
```

Ранее подготовленный пакет `ecf8563` не загружался и теперь заблокирован как
устаревший относительно интегрированного source head `44287d4`. Package/live
gate этим engineering check не открывался.

### Candidate later: subnet source of truth

Классификация: `post-launch-product-candidate`.

Нужен machine-checkable preflight, в котором один CIDR contract управляет
server config, NAT/firewall, next-IP allocation и generated client metadata.
Это должно расширить существующий IPAM conflict model, но не входит в текущий
launch slice и не должно открывать live multi-instance apply.

### Watch: Android TV import

Классификация: `candidate-later-exact-gate`.

После следующего published Amnezia Client release повторить import/connect на
Android TV 9/10. До release текущий cross-client pass на `4.8.19.0` остается
baseline и не пересматривается.

### Watch: restore idempotency

Классификация: `candidate-later-exact-gate`.

Когда restore apply/UI будет разрешен, обязательны single-flight lock,
idempotency token, preview, backup-before-write, verify и rollback. Сейчас
restore apply остается закрыт, отдельный implementation slice не нужен.

## Better left upstream

AMN2 не должен включать в launch scope WARP, SOCKS5, AdGuard, NGINX/domain
automation, marketplace/templates, public tunnels, raw config editor или
широкую multi-protocol parity. Это функции универсальных панелей, а не
отличие AMN2.

## Launch decision

Текущий Phase 10 launch plan не меняется. Добавленный AWG2 contract является
engineering hardening и не создает новый live gate. Следующий product step
должен завершить уже выбранную Phase 10 задачу; Android TV reacceptance и IPAM
runtime source-of-truth остаются trigger-based/post-launch.
