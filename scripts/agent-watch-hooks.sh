#!/usr/bin/env bash
# agent-watch-hooks.sh - catch a HUNG subagent (GM 2026-08-28: "can you add something to catch hung agents next time?").
#
# WHY. On feature 134 a research agent launched with a ~40-fetch budget stopped answering after ~50 fetches
# and never returned. The harness re-invokes a session only when a background task COMPLETES or the user
# types, so a hung agent produces no signal at all: the session ended its turn "waiting on the
# notification" and waited 8+ hours - 13 hours of wall clock, almost all of it idle. Nothing warned,
# because nothing was watching.
#
# WHAT THE TRANSCRIPT SAYS. Every subagent writes ~/.claude/projects/<cwd>/<session>/subagents/agent-<id>.jsonl.
# A FINISHED agent's last record is an `assistant` message with stop_reason `end_turn`; a PENDING one ends on
# a `user` tool_result (or an assistant tool_use) that never got its next turn. Its mtime is when it last
# did anything. That is enough to tell finished from hung without touching the harness.
#
# THREE MODES, one mechanism:
#   stop     (Stop hook)             - if an agent is pending, refuse to end the turn ONCE per agent (exit 2)
#                                       and hand the session the watchdog command. A refused Stop is the one
#                                       way a hook can make the session act; it is not repeated, because a
#                                       session that has launched the watchdog is allowed to wait.
#   prompt   (UserPromptSubmit hook) - report any agent idle past the limit as PROBABLY HUNG, so a returning
#                                       GM's first prompt surfaces it.
#   watchdog <agent-id|all> [min]    - what the session runs IN THE BACKGROUND (run_in_background): polls the
#                                       transcript's mtime every 30 s and EXITS when the agent finishes (0)
#                                       or has been idle past the limit (3, default 20 min) - and a background
#                                       command exiting is precisely what re-invokes the session. The loop is
#                                       inside this script on purpose: no-poll-hooks.sh forbids wait-loops in
#                                       a Bash call because polling a HARNESS-TRACKED task is waste; an agent's
#                                       transcript is external state the harness does not track for us.
#   scan <subagents-dir> [min]       - the shared scanner (one line per agent), for the test and for hand use.
#
# GUARD PROPERTIES (CLAUDE.md "When you add a guard"): it matches TRANSCRIPT STATE, not mentions; its escape is
# to launch the watchdog (the Stop refusal never repeats for an agent); and scripts/test-agent-watch-hooks.sh
# proves each mode fires on a fixture.
set -u
MODE=${1:-}
DEF_STALE_MIN=20
DEF_TICK=30
DEF_CAP_S=28800

scan() { # scan <dir> <stale_min> -> one line per agent: <id> <finished|pending|stale> <idle_s> <last_tool>
  python3 - "$1" "$2" <<'PY'
import glob, json, os, sys, time
d, stale = sys.argv[1], float(sys.argv[2])
for p in sorted(glob.glob(os.path.join(d, "agent-*.jsonl"))):
    aid = os.path.basename(p)[len("agent-"):-len(".jsonl")]
    last, last_tool = None, "-"
    try:
        with open(p, "rb") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    except OSError:
        continue
    for ln in reversed(lines):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if last is None:
            last = r
        m = r.get("message") if isinstance(r.get("message"), dict) else {}
        for c in (m.get("content") if isinstance(m.get("content"), list) else []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                inp = c.get("input") or {}
                arg = inp.get("url") or inp.get("query") or inp.get("command") or inp.get("file_path") or ""
                last_tool = f"{c.get('name')}({str(arg)[:70]})"
                break
        if last_tool != "-":
            break
    if last is None:
        continue
    m = last.get("message") if isinstance(last.get("message"), dict) else {}
    finished = last.get("type") == "assistant" and m.get("stop_reason") == "end_turn"
    idle = int(time.time() - os.path.getmtime(p))
    print(aid, "finished" if finished else ("stale" if idle > stale * 60 else "pending"), idle, last_tool)
PY
}

field() { printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin); print(d.get('$1', '') or '')
except Exception:
    print('')"; }

subagents_dir() { # from the hook's stdin: <dir of transcript>/<session_id>/subagents
  local tp sid
  tp=$(field transcript_path); sid=$(field session_id)
  [ -n "$tp" ] && [ -n "$sid" ] && printf '%s/%s/subagents' "$(dirname "$tp")" "$sid"
}

fmt_idle() { local s=$1; if [ "$s" -ge 3600 ]; then printf '%dh%02dm' $((s/3600)) $((s%3600/60)); else printf '%dm%02ds' $((s/60)) $((s%60)); fi; }

do_stop() {
  local dir; dir=$(subagents_dir); [ -n "$dir" ] && [ -d "$dir" ] || exit 0
  local nag="$dir/../agent-watch.nagged"; touch "$nag"
  local blocked=""
  while read -r aid state idle tool; do
    [ "$state" = finished ] && continue
    grep -qx "$aid" "$nag" 2>/dev/null && continue
    echo "$aid" >> "$nag"
    blocked="$blocked
  agent $aid - $state, idle $(fmt_idle "$idle"), last tool $tool"
  done < <(scan "$dir" "$STALE_MIN")
  [ -z "$blocked" ] && exit 0
  cat >&2 <<MSG
AGENT STILL RUNNING - do not end the turn on the assumption its notification will come:$blocked
A hung agent never completes, so nothing re-invokes you (feature 134: 8+ hours waited on one). Launch a WATCHDOG
in the background (run_in_background: true) - it exits when the agent finishes OR stalls, and either exit
re-invokes you:
  $OWN/scripts/agent-watch-hooks.sh watchdog all $STALE_MIN
Then end the turn. (This refusal fires once per agent; with the watchdog running, waiting is correct.)
MSG
  exit 2
}

do_prompt() {
  local dir; dir=$(subagents_dir); [ -n "$dir" ] && [ -d "$dir" ] || exit 0
  while read -r aid state idle tool; do
    [ "$state" = stale ] || continue
    echo "agent-watch: agent $aid is PROBABLY HUNG - idle $(fmt_idle "$idle") (limit ${STALE_MIN} min), last tool $tool. Do not wait on it; redo its work in-session or relaunch it with a smaller budget."
  done < <(scan "$dir" "$STALE_MIN")
  exit 0
}

do_watchdog() { # watchdog <agent-id|all> [stale_min] [--dir D] [--tick S] [--cap S]
  local want=${1:-all} stale=${2:-$DEF_STALE_MIN}; shift; shift 2>/dev/null || true
  local dir="" tick=$DEF_TICK cap=$DEF_CAP_S
  while [ $# -gt 0 ]; do case "$1" in --dir) dir=$2; shift 2 ;; --tick) tick=$2; shift 2 ;; --cap) cap=$2; shift 2 ;; *) shift ;; esac; done
  if [ -z "$dir" ]; then
    local cwdm; cwdm=$(pwd | sed 's#/#-#g')
    dir=$(ls -d "${HOME:-/home/agent}/.claude/projects/$cwdm"/*/subagents 2>/dev/null | head -1)
    [ -n "${CLAUDE_SESSION_ID:-}" ] && [ -d "${HOME:-/home/agent}/.claude/projects/$cwdm/$CLAUDE_SESSION_ID/subagents" ] && dir="${HOME:-/home/agent}/.claude/projects/$cwdm/$CLAUDE_SESSION_ID/subagents"
  fi
  [ -d "$dir" ] || { echo "agent-watch: no subagents directory ($dir)"; exit 1; }
  local t0; t0=$(date +%s)
  while :; do
    local pending=0 stale_hit=""
    while read -r aid state idle tool; do
      [ "$want" = all ] || [ "$aid" = "$want" ] || continue
      case "$state" in finished) ;; stale) stale_hit="$stale_hit
  agent $aid STALLED - idle $(fmt_idle "$idle") past the ${stale} min limit; last tool $tool" ;; *) pending=1 ;; esac
    done < <(scan "$dir" "$stale")
    if [ -n "$stale_hit" ]; then
      echo "agent-watch: HUNG AGENT$stale_hit"
      echo "Treat it as dead: redo the work in-session (parallel fetches) or relaunch with a smaller budget. Its transcript is in $dir."
      exit 3
    fi
    if [ "$pending" -eq 0 ]; then echo "agent-watch: watched agent(s) finished"; exit 0; fi
    if [ $(( $(date +%s) - t0 )) -ge "$cap" ]; then echo "agent-watch: gave up after ${cap}s with an agent still pending"; exit 4; fi
    sleep "$tick"
  done
}

HERE=$(cd "$(dirname "$0")" && pwd); OWN=$(cd "$HERE/.." && pwd)
STALE_MIN=${AGENT_WATCH_STALE_MIN:-$DEF_STALE_MIN}
INPUT=""
case "$MODE" in
  stop) INPUT=$(cat 2>/dev/null || true); do_stop ;;
  prompt) INPUT=$(cat 2>/dev/null || true); do_prompt ;;
  watchdog) shift; do_watchdog "$@" ;;
  scan) scan "${2:?dir}" "${3:-$DEF_STALE_MIN}" ;;
  *) echo "usage: agent-watch-hooks.sh stop|prompt|watchdog <agent-id|all> [stale-min] [--dir D] [--tick S]|scan <dir> [stale-min]" >&2; exit 1 ;;
esac
