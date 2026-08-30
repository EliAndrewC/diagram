#!/usr/bin/env bash
# finished-run-hooks.sh - a run that has FINISHED cannot be reported as still going (feature 170).
# (GUARD_EDIT_OK: a NEW guard.)
#
# THE DEFECT, in the reporting session's own words (2026-08-30, relayed by the GM): *"I reported the
# gate as 'waiting' when it had actually failed four hours earlier because I never saw the
# notification."* Four hours of a session believing it was waiting on something that had already gone
# red. Nothing in this repository noticed: `agent-stall-hooks.sh` watches subagent TRANSCRIPTS, not
# background commands, and a completion notification that is missed is simply gone.
#
# WHAT IT DOES: every gate run writes a record to `dev/run-log/` when it finishes (the Makefile's
# LOGRUN). This compares the newest record against a marker of what the session has already been
# told, and surfaces anything newer - at the next prompt, and at turn end, so a turn cannot close on
# "still running" for a run that finished. Once surfaced, it is not surfaced again.
#
# IT REPORTS; IT DOES NOT BLOCK. The failure was a session not KNOWING. Blocking a turn would punish
# the wrong thing, and the session may have perfectly good reasons to end a turn after a red run
# (reporting it, for instance). `stop` prints and returns 0.
#
# Modes:
#   prompt  (UserPromptSubmit) one line per unsurfaced finished run, then mark them surfaced
#   stop    (Stop) the same, worded for the moment a turn is about to close
#   check <clone>  one-shot for any clone, marking nothing (the suite uses this)
#   seen <clone>   mark everything currently finished as surfaced (the suite uses this)
set -uo pipefail
MODE=${1:-}
FR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clone_of() { # the working tree this hook is running in, or "" if it is not in one
  git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null
}

report() { # report <clone> <mark|nomark> -> one line per finished run the session has not been told about
  local clone=$1 mark=$2 log seen newest utc target result seconds age now
  log="$clone/.claude/skills/diagram/dev/run-log"
  [ -d "$log" ] || return 0
  seen="$clone/.git/finished-run.seen"
  newest=$(ls -t "$log"/*.json 2>/dev/null | head -1)
  [ -n "$newest" ] || return 0
  # ALREADY TOLD? The marker holds the newest record's basename at the time of the last report.
  [ -f "$seen" ] && [ "$(cat "$seen" 2>/dev/null)" = "$(basename "$newest")" ] && return 0
  utc=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("utc",""))' "$newest" 2>/dev/null)
  target=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("target",""))' "$newest" 2>/dev/null)
  result=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("result",""))' "$newest" 2>/dev/null)
  seconds=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("seconds",""))' "$newest" 2>/dev/null)
  now=$(date -u +%s)
  age=$(( now - $(date -u -d "$utc" +%s 2>/dev/null || echo "$now") ))
  [ "$mark" = mark ] && printf '%s' "$(basename "$newest")" > "$seen" 2>/dev/null
  case "$result" in
    green|already-verified)
      printf 'finished-run: `make %s` finished %s ago: %s (%ss). It is NOT still running.\n' "$target" "$(human "$age")" "$result" "$seconds" ;;
    *)
      printf 'finished-run: `make %s` finished %s ago and it is %s (%ss) - NOT still running. Read it before you report on it.\n' "$target" "$(human "$age")" "$result" "$seconds" ;;
  esac
}

human() { # seconds -> a duration a person reads
  local s=$1
  if [ "$s" -lt 90 ]; then printf '%ss' "$s"
  elif [ "$s" -lt 5400 ]; then printf '%s min' "$(( s / 60 ))"
  else printf '%s h' "$(( s / 3600 ))"; fi
}

case "$MODE" in
  prompt|stop)
    INPUT=$(cat 2>/dev/null || true)
    CWD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd",""))
except Exception: pass' 2>/dev/null)
    CLONE=$(clone_of "${CWD:-$PWD}")
    [ -n "$CLONE" ] || exit 0
    out=$(report "$CLONE" mark)
    if [ -n "$out" ]; then
      printf '%s\n' "$out"
      [ "$MODE" = stop ] && printf 'finished-run: do not end a turn saying a run is still going when this one is not.\n'
      # shellcheck source=/dev/null
      . "$FR_HERE/_guardlog.sh"
      guard_log finished-run reminded "$out" finished-not-running
    fi
    exit 0 ;;
  check) report "${2:?clone}" nomark; exit 0 ;;
  seen)  report "${2:?clone}" mark >/dev/null; exit 0 ;;
  *) echo "usage: $0 prompt|stop|check <clone>|seen <clone>" >&2; exit 2 ;;
esac
