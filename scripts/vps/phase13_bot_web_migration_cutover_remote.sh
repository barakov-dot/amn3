#!/usr/bin/env bash
set -eu

umask 077

emit_receipt() {
    stage=$1
    reason=$2
    outcome=$3
    if [ $((USA_PROCESS_COUNT + SPAIN_PROCESS_COUNT)) -eq 1 ]; then
        single_owner=true
    else
        single_owner=false
    fi
    [ "$USA_PROCESS_COUNT" -eq 1 ] && usa_active=true || usa_active=false
    [ "$SPAIN_PROCESS_COUNT" -eq 1 ] && spain_active=true || spain_active=false
    printf '{"awg2_equal":%s,"database_equal":%s,"foreign_equal":%s,"operator_accepted":%s,"outcome":"%s","reason":"%s","rollback_armed":%s,"rolled_back":%s,"schema":"amn2.phase13.bot-web-cutover-receipt.v1","single_owner":%s,"spain_active":%s,"stage":"%s","usa_active":%s}\n' \
        "$AWG2_EQUAL" \
        "$DATABASE_EQUAL" \
        "$FOREIGN_EQUAL" \
        "$OPERATOR_ACCEPTED_RESULT" \
        "$outcome" \
        "$reason" \
        "$ROLLBACK_ARMED" \
        "$ROLLED_BACK" \
        "$single_owner" \
        "$spain_active" \
        "$stage" \
        "$usa_active"
}

fail_without_receipt() {
    printf 'stage=unknown result=failed reason=%s\n' "$1" >&2
    exit 1
}

[ "${1-}" = 'cutover' ] && [ "$#" -eq 1 ] \
    || fail_without_receipt unsupported_mode
[ "${AMN2_PHASE13_LOCAL_FAKE_HARNESS-}" = '1' ] \
    || fail_without_receipt local_fake_harness_required
FAKE_ROOT=${AMN2_PHASE13_FAKE_ROOT-}
case "$FAKE_ROOT" in
    /*|[A-Za-z]:/*) ;;
    *) fail_without_receipt local_fake_root_invalid ;;
esac
case "$FAKE_ROOT" in
    *$'\n'*|*$'\r'*) fail_without_receipt local_fake_root_invalid ;;
esac
[ -d "$FAKE_ROOT" ] && [ ! -L "$FAKE_ROOT" ] \
    || fail_without_receipt local_fake_root_invalid
FAKE_SENTINEL="$FAKE_ROOT/.amn2-phase13-local-fake-harness"
[ -f "$FAKE_SENTINEL" ] && [ ! -L "$FAKE_SENTINEL" ] \
    && [ "$(cat -- "$FAKE_SENTINEL")" = 'task8-local-only' ] \
    || fail_without_receipt local_fake_root_invalid

OBSERVED_ROOT="$FAKE_ROOT/observed"
OBSERVED_STATE="$OBSERVED_ROOT/state"
EVENTS_LOG="$FAKE_ROOT/events.log"
MARKER_PARENT="$FAKE_ROOT/etc/amn2-spain"
BOT_ENABLE_MARKER="$MARKER_PARENT/bot-enabled"

[ -d "$OBSERVED_ROOT" ] && [ ! -L "$OBSERVED_ROOT" ] \
    || fail_without_receipt local_fake_root_invalid
[ -f "$OBSERVED_STATE" ] && [ ! -L "$OBSERVED_STATE" ] \
    || fail_without_receipt observation_invalid
if [ -e "$EVENTS_LOG" ] || [ -L "$EVENTS_LOG" ]; then
    fail_without_receipt local_fake_root_invalid
fi
if [ -e "$FAKE_ROOT/etc" ] || [ -L "$FAKE_ROOT/etc" ]; then
    [ -d "$FAKE_ROOT/etc" ] && [ ! -L "$FAKE_ROOT/etc" ] \
        || fail_without_receipt local_fake_root_invalid
fi

ROLLBACK_ARM_OK='__missing__'
USA_PROCESS_COUNT='__missing__'
SPAIN_PROCESS_COUNT='__missing__'
USA_STOP_RESULT_COUNT='__missing__'
SPAIN_START_RESULT_COUNT='__missing__'
SPAIN_ADMISSION_OK='__missing__'
OPERATOR_ACCEPTED='__missing__'
POSTFLIGHT_OK='__missing__'
SPAIN_WEB_DATA_ACCEPTED='__missing__'
SPAIN_WEB_LOOPBACK_ONLY='__missing__'
TELEGRAM_IDENTITY_OK='__missing__'
TELEGRAM_WEBHOOK_CLEAR='__missing__'
TELEGRAM_BACKLOG_CLEAR='__missing__'
DATABASE_EQUAL='__missing__'
AWG2_EQUAL='__missing__'
FOREIGN_EQUAL='__missing__'
RESTORE_SPAIN_NEEDED='__missing__'
ROLLBACK_RESTORE_OK='__missing__'

read_observed_state() {
    while IFS='=' read -r key value; do
        [ -n "$key" ] || continue
        case "$key" in
            ROLLBACK_ARM_OK|USA_PROCESS_COUNT|SPAIN_PROCESS_COUNT|\
            USA_STOP_RESULT_COUNT|SPAIN_START_RESULT_COUNT|SPAIN_ADMISSION_OK|\
            OPERATOR_ACCEPTED|POSTFLIGHT_OK|SPAIN_WEB_DATA_ACCEPTED|\
            SPAIN_WEB_LOOPBACK_ONLY|TELEGRAM_IDENTITY_OK|TELEGRAM_WEBHOOK_CLEAR|\
            TELEGRAM_BACKLOG_CLEAR|DATABASE_EQUAL|AWG2_EQUAL|FOREIGN_EQUAL|\
            RESTORE_SPAIN_NEEDED|ROLLBACK_RESTORE_OK)
                eval "current=\${$key}"
                [ "$current" = '__missing__' ] || return 1
                printf -v "$key" '%s' "$value"
                ;;
            *) return 1 ;;
        esac
    done < "$OBSERVED_STATE"

    for value in \
        "$ROLLBACK_ARM_OK" "$USA_PROCESS_COUNT" "$SPAIN_PROCESS_COUNT" \
        "$USA_STOP_RESULT_COUNT" "$SPAIN_START_RESULT_COUNT" \
        "$SPAIN_ADMISSION_OK" "$OPERATOR_ACCEPTED" "$POSTFLIGHT_OK" \
        "$SPAIN_WEB_DATA_ACCEPTED" "$SPAIN_WEB_LOOPBACK_ONLY" \
        "$TELEGRAM_IDENTITY_OK" "$TELEGRAM_WEBHOOK_CLEAR" \
        "$TELEGRAM_BACKLOG_CLEAR" "$DATABASE_EQUAL" "$AWG2_EQUAL" \
        "$FOREIGN_EQUAL" "$RESTORE_SPAIN_NEEDED" "$ROLLBACK_RESTORE_OK"
    do
        [ "$value" != '__missing__' ] || return 1
    done
    for value in \
        "$ROLLBACK_ARM_OK" "$SPAIN_ADMISSION_OK" "$OPERATOR_ACCEPTED" \
        "$POSTFLIGHT_OK" "$SPAIN_WEB_DATA_ACCEPTED" \
        "$SPAIN_WEB_LOOPBACK_ONLY" "$TELEGRAM_IDENTITY_OK" \
        "$TELEGRAM_WEBHOOK_CLEAR" "$TELEGRAM_BACKLOG_CLEAR" \
        "$DATABASE_EQUAL" "$AWG2_EQUAL" "$FOREIGN_EQUAL" \
        "$RESTORE_SPAIN_NEEDED" "$ROLLBACK_RESTORE_OK"
    do
        [ "$value" = 'true' ] || [ "$value" = 'false' ] || return 1
    done
    for value in \
        "$USA_PROCESS_COUNT" "$SPAIN_PROCESS_COUNT" \
        "$USA_STOP_RESULT_COUNT" "$SPAIN_START_RESULT_COUNT"
    do
        [ "$value" = '0' ] || [ "$value" = '1' ] || return 1
    done
}

read_observed_state || fail_without_receipt observation_invalid
: > "$EVENTS_LOG"
chmod 0600 "$EVENTS_LOG" || fail_without_receipt local_fake_root_invalid

ROLLBACK_ARMED=false
ROLLED_BACK=false
OPERATOR_ACCEPTED_RESULT=false

record_event() {
    printf '%s\n' "$1" >> "$EVENTS_LOG"
}

ensure_marker_parent() {
    if [ ! -e "$FAKE_ROOT/etc" ] && [ ! -L "$FAKE_ROOT/etc" ]; then
        mkdir -m 0700 -- "$FAKE_ROOT/etc" || return 1
    fi
    [ -d "$FAKE_ROOT/etc" ] && [ ! -L "$FAKE_ROOT/etc" ] || return 1
    if [ ! -e "$MARKER_PARENT" ] && [ ! -L "$MARKER_PARENT" ]; then
        mkdir -m 0700 -- "$MARKER_PARENT" || return 1
    fi
    [ -d "$MARKER_PARENT" ] && [ ! -L "$MARKER_PARENT" ] || return 1
}

remove_exact_marker() {
    if [ ! -e "$BOT_ENABLE_MARKER" ] && [ ! -L "$BOT_ENABLE_MARKER" ]; then
        return 0
    fi
    [ -f "$BOT_ENABLE_MARKER" ] && [ ! -L "$BOT_ENABLE_MARKER" ] || return 1
    rm -f -- "$BOT_ENABLE_MARKER"
}

perform_rollback() {
    original_stage=$1
    original_reason=$2
    rollback_failed=false
    ROLLED_BACK=true

    record_event stop_spain
    SPAIN_PROCESS_COUNT=0
    record_event remove_exact_marker
    remove_exact_marker || rollback_failed=true
    record_event restore_spain_if_needed
    if [ "$ROLLBACK_RESTORE_OK" != 'true' ]; then
        rollback_failed=true
    elif [ "$RESTORE_SPAIN_NEEDED" = 'true' ]; then
        DATABASE_EQUAL=true
    fi
    record_event start_usa
    USA_PROCESS_COUNT=1
    record_event prove_single_usa
    if [ "$USA_PROCESS_COUNT" -ne 1 ] || [ "$SPAIN_PROCESS_COUNT" -ne 0 ]; then
        rollback_failed=true
    fi

    if [ "$rollback_failed" = 'true' ]; then
        emit_receipt rollback ROLLBACK_FAILED failed
    else
        emit_receipt "$original_stage" "$original_reason" failed
    fi
    exit 1
}

record_event preflight
if [ "$USA_PROCESS_COUNT" -ne 1 ] \
    || [ "$SPAIN_PROCESS_COUNT" -ne 0 ] \
    || [ "$SPAIN_WEB_DATA_ACCEPTED" != 'true' ] \
    || [ "$SPAIN_WEB_LOOPBACK_ONLY" != 'true' ] \
    || [ "$TELEGRAM_IDENTITY_OK" != 'true' ] \
    || [ "$TELEGRAM_WEBHOOK_CLEAR" != 'true' ] \
    || [ "$TELEGRAM_BACKLOG_CLEAR" != 'true' ] \
    || [ "$DATABASE_EQUAL" != 'true' ] \
    || [ "$AWG2_EQUAL" != 'true' ] \
    || [ "$FOREIGN_EQUAL" != 'true' ] \
    || [ -e "$BOT_ENABLE_MARKER" ] \
    || [ -L "$BOT_ENABLE_MARKER" ]
then
    emit_receipt preflight PREFLIGHT_FAILED failed
    exit 1
fi

record_event arm_rollback
if [ "$ROLLBACK_ARM_OK" != 'true' ]; then
    emit_receipt arm_rollback ROLLBACK_ARM_FAILED failed
    exit 1
fi
ROLLBACK_ARMED=true

record_event stop_usa
USA_PROCESS_COUNT=$USA_STOP_RESULT_COUNT
record_event prove_usa_zero
if [ "$USA_PROCESS_COUNT" -ne 0 ]; then
    perform_rollback prove_usa_zero USA_BOT_STOP_UNCONFIRMED
fi

record_event start_spain
if ! ensure_marker_parent \
    || [ -e "$BOT_ENABLE_MARKER" ] \
    || [ -L "$BOT_ENABLE_MARKER" ] \
    || ! : > "$BOT_ENABLE_MARKER" \
    || ! chmod 0600 "$BOT_ENABLE_MARKER"
then
    perform_rollback start_spain SPAIN_BOT_ADMISSION_FAILED
fi
SPAIN_PROCESS_COUNT=$SPAIN_START_RESULT_COUNT
if [ "$USA_PROCESS_COUNT" -ne 0 ] \
    || [ "$SPAIN_PROCESS_COUNT" -ne 1 ] \
    || [ "$SPAIN_ADMISSION_OK" != 'true' ]
then
    perform_rollback start_spain SPAIN_BOT_ADMISSION_FAILED
fi

record_event operator_accept
if [ "$OPERATOR_ACCEPTED" != 'true' ]; then
    perform_rollback operator_accept OPERATOR_ACCEPTANCE_FAILED
fi
OPERATOR_ACCEPTED_RESULT=true

record_event postflight
if [ "$POSTFLIGHT_OK" != 'true' ] \
    || [ "$USA_PROCESS_COUNT" -ne 0 ] \
    || [ "$SPAIN_PROCESS_COUNT" -ne 1 ] \
    || [ "$DATABASE_EQUAL" != 'true' ] \
    || [ "$AWG2_EQUAL" != 'true' ] \
    || [ "$FOREIGN_EQUAL" != 'true' ]
then
    perform_rollback postflight POSTFLIGHT_FAILED
fi

emit_receipt postflight NONE passed
