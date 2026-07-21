#!/bin/sh
set -eu

active=0

cleanup() {
  trap - EXIT INT TERM
  if [ "$active" -eq 1 ]; then
    awg-quick down awgsp0
  fi
}

shutdown() {
  cleanup
  exit 0
}

trap cleanup EXIT
trap shutdown INT TERM
awg-quick up awgsp0
active=1

if [ -n "$(awg show awgsp0 peers)" ]; then
  echo "unexpected_peer" >&2
  exit 1
fi

while :; do
  sleep 3600 &
  wait "$!" || true
done
