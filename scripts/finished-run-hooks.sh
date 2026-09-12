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
# THE FINISHED-RUN RULE REPORTS AND DOES NOT BLOCK. The failure there was a session not KNOWING, and
# blocking a turn would punish the wrong thing: a session may have perfectly good reasons to end a turn
# after a red run - reporting it, for instance.
#
# ...AND THE SECOND RULE, WHICH DOES BLOCK: A RUN STILL GOING MUST NOT BE ABANDONED (GM 2026-09-12).
# The first rule covers a run that finished and was never read. Its mirror image is a run that has not
# finished and is walked away from, and that is what happened the same afternoon: a session started
# `make done INCREMENTAL=0` detached, wrote its report, ended the turn, and never waited - the gate failed
# 58 seconds later on five uncovered lines and sat unread for 52 minutes, until the GM asked whether
# something had gone wrong. Nothing caught it, because the finished-run rule fires at the NEXT prompt, and
# the next prompt is exactly the moment the damage is already done. The GM:
#
#   "So we just put in a tooling fix specifically to stop this kind of thing from happening. So how do we
#   make that not happen? Since the issue in this case is that you ended your turn without waiting for it,
#   then is that something that can be detected in a hook? Like, if there is a makefile command running and
#   your turn ends, then we have a hook that errors or triggers you or sends you context to say, hey. Hold
#   on. You need to wait for that makefile command."
#
# It is detectable exactly, with no pattern matching and so no self-match trap: walk `/proc` for a process
# whose `comm` is `make` and whose `cwd` lies inside THIS session's clone. A `pgrep -f "make done"` would
# find the searching shell, which is the 2026-07-25 defect `no-poll-hooks.sh` exists for; a cwd read from
# the kernel cannot.
#
# ONCE PER RUN IS THE WHOLE RELEASE VALVE, AND THERE IS NO TOKEN ESCAPE - because a Stop hook's payload
# carries no command, so there is nowhere for a session to put one (tried, and the suite caught it). The turn
# is refused the first time it would close over a given live run, keyed on the make PIDs, which is enough to
# force the decision; a second attempt goes through. That matters: a session answering the GM while a gate
# runs is doing the right thing and must not be trapped, and the marker is cleared the moment nothing is
# live, so the next run gets its own single refusal.
#
# Modes:
#   prompt  (UserPromptSubmit) one line per unsurfaced finished run, then mark them surfaced
#   stop    (Stop) the same, PLUS the refusal above when a make run is still going
#   check <clone>  one-shot for any clone, marking nothing (the suite uses this)
#   seen <clone>   mark everything currently finished as surfaced (the suite uses this)
#   live <clone>   print one line per live make run in that clone (the suite and `make audit` use this)
set -uo pipefail
MODE=${1:-}
FR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clone_of() { # the working tree this hook is running in, or "" if it is not in one
  git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null
}

live_runs() { # live_runs <clone> -> "<pid> <target>" per live make run whose cwd is inside that clone
  # BY CWD, NOT BY PATTERN. The kernel knows each process's working directory, so nothing here can match
  # its own command line - the trap that made `pgrep -f "make done"` loop for 10.9 minutes in 2026-07-25.
  python3 - "$1" <<'PY'
import glob, os, sys

clone = os.path.realpath(sys.argv[1])
for d in glob.glob("/proc/[0-9]*"):
    try:
        if open(f"{d}/comm").read().strip() not in ("make", "gmake"):
            continue
        if not os.path.realpath(os.readlink(f"{d}/cwd")).startswith(clone):
            continue
        argv = open(f"{d}/cmdline").read().split("\0")
    except OSError:
        continue   # the process went away between the glob and the read, which is the common case
    # the TARGET is the first bare word after the make binary - what a session would wait on
    target = next((a for a in argv[1:] if a and not a.startswith("-") and "=" not in a), "")
    print(f"{d.rsplit('/', 1)[-1]} {target or 'make'}")
PY
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
    # ...AND THE TURN MAY NOT CLOSE OVER A RUN THAT IS STILL GOING (GM 2026-09-12; see the header).
    if [ "$MODE" = stop ]; then
      LIVE=$(live_runs "$CLONE")
      if [ -n "$LIVE" ]; then
        # shellcheck source=/dev/null
        . "$FR_HERE/_guardlog.sh"
        SEEN_F="$CLONE/.git/live-run.told"
        PIDS=$(printf '%s\n' "$LIVE" | cut -d' ' -f1 | tr '\n' ',')
        if [ "$(cat "$SEEN_F" 2>/dev/null)" = "$PIDS" ]; then
          exit 0   # already told for exactly these runs: never a loop, and a turn may close deliberately
        fi
        printf '%s' "$PIDS" > "$SEEN_F" 2>/dev/null || true
        printf 'A MAKE RUN IS STILL GOING and this turn was about to end without waiting for it:\n' >&2
        printf '%s\n' "$LIVE" | sed 's/^/  pid /' >&2
        printf '\nWait for it: background a loop on its log (`until grep -qE "verification-state|GATE FAILED" <log>; do sleep 20; done`)\n' >&2
        printf 'and the no-poll guard will add the proof-of-life check for you. Then REPORT WHAT IT SAID.\n' >&2
        printf 'Reporting a result you have not seen is the thing this prevents: on 2026-09-12 a gate failed 58 s\n' >&2
        printf 'after a turn ended on "the gate is running" and sat unread for 52 minutes.\n' >&2
        printf 'Ending the turn deliberately (the GM asked something else) is fine: end it again and this lets it through.\n' >&2
        guard_log finished-run blocked "$LIVE" run-still-going
        exit 2
      fi
      rm -f "$CLONE/.git/live-run.told" 2>/dev/null || true   # nothing live: the next run starts clean
    fi
    exit 0 ;;
  check) report "${2:?clone}" nomark; exit 0 ;;
  seen)  report "${2:?clone}" mark >/dev/null; exit 0 ;;
  live)  live_runs "${2:?clone}"; exit 0 ;;
  *) echo "usage: $0 prompt|stop|check <clone>|seen <clone>|live <clone>" >&2; exit 2 ;;
esac
