#!/usr/bin/env bash
# stall-watchdog-hooks.sh - a stall is seen from OUTSIDE every session (feature 295 item 4).
# (GUARD_EDIT_OK: feature 295 - a NEW guard.)
#
# THE DEFECT (request item 4, 2026-09-30). Nothing outside a session sees it stop: R12's headless check session sat two
# and a half hours with its work done and unreported, and the in-session hourly CronCreate check added that day dies with
# its session. The GM asked for a watchdog that notices a session idle over an hour with unfinished work and chose how it
# reaches them: "Tab title + bell", and "Nudge if prompt empty" (spec Clarifications).
#
# WHAT IT DOES. `prompt` (UserPromptSubmit) starts the loop, detached, when its pid file names no live process - any
# session's prompt revives it, so it outlives every session and comes back after a container restart at the first
# prompt. `run` is the loop: one instance by `flock`, then a pass every STALL_PERIOD seconds (300: the threshold is an
# hour, so a stall is marked within five minutes of it, for one short python run). Each pass is a fresh
# `_stall_watchdog.py pass`, so an update to the decision takes effect without restarting the loop. What a stall is and
# what is done about it are that file's; every action is a line in `$STATE/log`.
#
# Modes:
#   prompt   (UserPromptSubmit) start the loop when it is not running; prints nothing
#   run      the loop (started by `prompt`; exits at once when another holds the lock)
#   once     one pass, printing what it did (the suite and a session use this)
set -uo pipefail
MODE=${1:-}
SW_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE=${STALL_STATE_DIR:-$HOME/.claude/stall-watchdog}
PERIOD=${STALL_PERIOD:-300}

case "$MODE" in
  prompt)
    cat >/dev/null 2>&1 || true
    mkdir -p "$STATE" 2>/dev/null || exit 0
    pid=$(cat "$STATE/pid" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then exit 0; fi
    setsid -f "$SW_HERE/stall-watchdog-hooks.sh" run </dev/null >/dev/null 2>&1
    # shellcheck source=/dev/null
    . "$SW_HERE/_guardlog.sh"
    guard_log stall-watchdog started "${pid:-none}" watchdog-started
    exit 0 ;;
  run)
    mkdir -p "$STATE" || exit 1
    exec 9>"$STATE/lock"
    flock -n 9 || exit 0   # one watchdog on the host
    printf '%s' "$$" > "$STATE/pid"
    # GUARD_EDIT_OK: feature 295, the new guard's own fix - the lock's descriptor is closed for the loop's children
    # (`9>&-`): a `sleep` that inherited it outlived a killed loop holding the lock, and no prompt could revive the
    # watchdog until it ended (caught by the suite's own run)
    while :; do
      python3 "$SW_HERE/_stall_watchdog.py" pass >/dev/null 2>>"$STATE/errors" 9>&-
      sleep "$PERIOD" 9>&-
    done ;;
  once) exec python3 "$SW_HERE/_stall_watchdog.py" pass ;;
  *) echo "usage: $0 prompt|run|once" >&2; exit 2 ;;
esac
