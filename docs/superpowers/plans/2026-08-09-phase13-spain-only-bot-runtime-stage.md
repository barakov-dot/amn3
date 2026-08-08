# AMN2 Phase 13: Spain-only bot runtime stage

## Цель

Подготовить отдельный checksum-bound gate, который на Spain меняет только
`TELEGRAM_BOT_TOKEN` и `ADMIN_TELEGRAM_IDS`, оставляет bot выключенным и не
трогает live database, AWG2, foreign service или USA.

## Обоснование fast path

- bot-media collection `bot-media-check-20260808-213941` завершена успешно:
  registry отсутствует, media root отсутствует, файлов `0`;
- exact AMN2 `55dc243...910539e` меняет только migration/schema файлы;
  bot/web код и встроенные assets не меняются;
- accepted Spain source `55dc243...` поэтому сохраняется без source deploy;
- USA legacy database/merge artifacts не являются live input.

## TDD

1. RED: strict package/approval, exact source-diff proof, encrypted runtime
   delta, fixed Spain trust, claim-before-network и one-SSH contract.
2. GREEN: local materializer/runner и remote runtime-only executor.
3. Remote preflight: web loopback healthy, bot disabled/process-zero, marker
   absent, database integrity, exact accepted source manifest, AWG2 equality и
   foreign equality.
4. Apply: protected rollback copy и atomic runtime.env replacement с изменением
   только двух allowlisted keys; web и bot не перезапускаются.
5. Post-verify/rollback: bot остаётся disabled, web healthy, database/source,
   AWG2 и foreign projection неизменны.
6. Focused tests, Python syntax, `git diff --check`, secret/mutation/manual
   scoped security review; отдельный commit без push.
7. Fresh package materialization и остановка перед exact live approval.

## Запреты

Нет USA access, database apply, source deploy, service action, bot cutover,
AWG action, firewall/config/peer action, foreign-service mutation, AWG3 или
broad security scan.
