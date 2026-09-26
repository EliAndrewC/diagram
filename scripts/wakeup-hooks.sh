#!/usr/bin/env bash
# wakeup-hooks.sh - a timed wakeup cannot outlive its purpose (feature 263).
# (GUARD_EDIT_OK: a NEW guard.)
#
# THE DEFECT (2026-09-26). A session scheduled a `ScheduleWakeup` as a fallback while a background agent ran.
# The agent reported back and the work landed; the wakeup stayed pending, so every later turn ended with a
# session cron, and the GM's tab - whose title hook reads `session_crons` from the Stop payload - showed the
# hourglass ("background work will bring it back") while the session was waiting for them. The fallback was never
# needed: `ScheduleWakeup`'s own contract is /loop-only, the harness wakes a session when background work finishes,
# and `agent-stall-hooks.sh` reports a stalled agent. The session's first remedy was a memory note. The GM:
#
#   "these kinds of things need to be mechanical. It needs to be literally impossible for them to do the wrong
#   thing. Or else we will just end up doing the wrong thing a lot."
#
# TWO LAYERS, because either alone leaves a way through:
#   pretool (PreToolUse, ScheduleWakeup) - REFUSE the call unless this session is running /loop. The source.
#   stop    (Stop) - BLOCK the turn from ending while a wakeup is pending outside /loop, naming `CronDelete <id>`.
#           The backstop, for a wakeup made any other way: before this guard, through the escape, or by a loop
#           abandoned without `stop: true`.
#
# WHAT IS A WAKEUP (measured, specs/263-stale-wakeup-guard/research.md R1). In the Stop payload a pending cron is
# `{id, schedule, recurring, prompt}` - a `ScheduleWakeup` and a `CronCreate` reminder are the SAME shape, no field
# says which tool made it. The transcript does: a wakeup's `prompt` is verbatim the `prompt` of a `ScheduleWakeup`
# call in the session's own transcript, and the hook is handed `transcript_path`. So a cron made by `CronCreate` -
# a reminder the GM asked for - is never named or blocked here.
#
# A LOOP IS LIVE, not merely once run (measured, research.md R3): a /loop wakeup's prompt is the loop input
# prefixed with `/loop ` (or the autonomous sentinel), and the loop is live while the transcript's latest loop
# event is a /loop invocation rather than a `ScheduleWakeup(stop: true)`. Only that loop's own wakeup passes; a
# fallback timer set inside a live loop is refused like any other.
#
# EVERY TURN END, NEVER ONCE: the Stop layer blocks each time a stale wakeup is pending. A once-only valve (the
# shape `escalation-hooks.sh` needs for a block the session cannot always satisfy) would hand the decision back
# to the session - the memory-note remedy the GM rejected - and this block is always satisfiable by one
# `CronDelete <id>`.
#
# NO ESCAPE (spec-fidelity round 1, 2026-09-26): no case needs a ScheduleWakeup outside a live loop, and an escape
# on the Stop layer would let the incident itself through ("WAKEUP_OK guarding the agent"). A case that seems to
# need one is a question for the GM.
#
# A guard that cannot read its inputs does not refuse on a guess: an unreadable payload or transcript exits 0.
set -uo pipefail
MODE=${1:-}
WH_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$WH_HERE/_guardlog.sh"

# decide <mode> -> prints "PASS <why>" | "REFUSE <why>" | "BLOCK" then one "id|schedule|prompt" line per wakeup
# (GUARD_EDIT_OK: feature 263 - a comment brought in line with the no-escape rule of spec-fidelity round 1)
decide() {
  # THE PAYLOAD GOES THROUGH A FILE: the program is this heredoc, which IS python's stdin - a payload piped in as
  # well is silently replaced by it, and the first cut of this guard judged an empty payload every time.
  local f rc
  f=$(mktemp) || return 0
  printf '%s' "$INPUT" > "$f"
  python3 - "$1" "$WH_HERE" "" "$f" <<'PY'
import json, os, sys
mode, here, state_dir, payload_path = sys.argv[1:5]
SENTINEL = "<<autonomous-loop-dynamic>>"

def is_loop_prompt(text):
    """A loop's own wakeup (measured, research.md R3): its prompt is the loop input prefixed with `/loop `, or the
    autonomous sentinel. Anything else a ScheduleWakeup carries is a fallback timer."""
    t = (text or "").strip()
    return t.startswith("/loop ") or t == "/loop" or t == SENTINEL

try:
    p = json.loads(open(payload_path, encoding="utf-8").read() or "{}")
    if not isinstance(p, dict):
        raise ValueError
except Exception:
    # FAIL CLOSED ON THE CALL, OPEN ON THE TURN END (plan review, 2026-09-26; GUARD_EDIT_OK: feature 263). The
    # PreToolUse matcher already says this IS a ScheduleWakeup, and one that cannot be shown to belong to a live loop
    # is refused - failing open here would let the incident through whole, since the Stop layer (which must fail
    # open, or it would block reminders it cannot tell from wakeups) cannot name it either.
    print("REFUSE unreadable" if mode == "pretool" else "PASS unreadable-payload"); sys.exit(0)
if mode == "pretool" and p.get("tool_name") not in (None, "ScheduleWakeup"):
    # GUARD_EDIT_OK: feature 263 plan review - decided BEFORE the transcript read, so failing closed on an unreadable
    # transcript can never touch another tool (the matcher names ScheduleWakeup; this is the belt to its braces)
    print("PASS not-a-wakeup"); sys.exit(0)

# THE TRANSCRIPT, IN ORDER: every ScheduleWakeup prompt (what makes a pending cron a wakeup - research.md R1), and
# whether a loop is LIVE - its latest event a /loop invocation (the command entry, or the `loop` skill) rather than
# a ScheduleWakeup(stop: true) (research.md R3). A session that ran /loop once and stopped it is not a loop session.
tpath = p.get("transcript_path") or ""
wakeup_prompts, loop_live = set(), False
try:
    for line in open(tpath, encoding="utf-8"):
        if "/loop" not in line and "ScheduleWakeup" not in line and '"loop"' not in line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        content = (r.get("message") or {}).get("content")
        if r.get("type") == "user":
            texts = [content] if isinstance(content, str) else [b.get("text", "") for b in content or [] if isinstance(b, dict)]
            if any("<command-name>/loop</command-name>" in t for t in texts if isinstance(t, str)):
                loop_live = True
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict) or b.get("type") != "tool_use":
                continue
            inp = b.get("input") or {}
            if b.get("name") == "ScheduleWakeup":
                if inp.get("stop"):
                    loop_live = False
                elif inp.get("prompt"):
                    wakeup_prompts.add(inp["prompt"])
            elif b.get("name") == "Skill" and inp.get("skill") == "loop":
                loop_live = True
except Exception:  # GUARD_EDIT_OK: feature 263 plan review - an unreadable or unparsable transcript: closed on the call
    if mode == "pretool" and not (p.get("tool_input") or {}).get("stop"):
        print("REFUSE unreadable"); sys.exit(0)
    print("PASS no-transcript"); sys.exit(0)

if mode == "pretool":
    if p.get("tool_name") != "ScheduleWakeup":
        print("PASS not-a-wakeup"); sys.exit(0)
    ti = p.get("tool_input") or {}
    if ti.get("stop"):
        print("PASS ending-a-loop"); sys.exit(0)
    if loop_live and is_loop_prompt(ti.get("prompt")):
        print("PASS live-loop"); sys.exit(0)
    print("REFUSE " + ("not-the-loop-prompt" if loop_live else "outside-loop")); sys.exit(0)

# stop: EVERY turn end that would leave a stale wakeup pending is blocked - no once-only valve, because the fix is
# always one CronDelete (spec-fidelity round 1, 2026-09-26: a valve hands the decision back to the session).
stale = [c for c in p.get("session_crons") or []
         if isinstance(c, dict) and c.get("id") and c.get("prompt") in wakeup_prompts
         and not (loop_live and is_loop_prompt(c.get("prompt")))]
if not stale:
    print("PASS no-stale-wakeup"); sys.exit(0)
print("BLOCK")
for c in stale:  # one per line: id|schedule|prompt
    print("%s|%s|%s" % (c["id"], c.get("schedule", ""), (c.get("prompt") or "")[:80].replace("\n", " ").replace("|", "/")))
PY
  rc=$?
  rm -f "$f"
  return $rc
}

pretool() {
  local verdict
  INPUT="$(cat)"
  verdict="$(decide pretool 2>/dev/null)"
  case "$verdict" in
    "REFUSE not-the-loop-prompt")
      printf 'BLOCKED: a live /loop paces itself with its OWN prompt - "/loop <the loop input>" - and this wakeup carries\nsomething else, which makes it a fallback timer riding on the loop (feature 263). Re-arm with the loop prompt.\n' >&2
      guard_log wakeup blocked "ScheduleWakeup" not-the-loop-prompt; exit 2 ;;
    "REFUSE outside-loop")
      {
        printf 'BLOCKED: ScheduleWakeup outside /loop (feature 263).\n\n'
        printf 'ScheduleWakeup is the /loop pacing tool. Outside a loop it is a fallback timer, and a fallback outlives\n'
        printf 'its purpose: on 2026-09-26 one stayed pending after the work it guarded had landed, and the GM'"'"'s tab\n'
        printf 'showed the hourglass instead of waiting-for-you. You do not need one:\n'
        printf '  - background work (a shell, an agent, a workflow) wakes this session by itself when it finishes;\n'
        printf '  - a stalled agent is reported by agent-stall-hooks.sh;\n'
        printf '  - a reminder the GM asked for ("remind me at 3pm") is CronCreate'"'"'s job, not this tool'"'"'s.\n'
        printf 'There is no escape: a case that seems to need one is a question for the GM, not a token.\n'
      } >&2
      guard_log wakeup blocked "ScheduleWakeup" outside-loop; exit 2 ;;
    PASS*) exit 0 ;;
    *)
      # GUARD_EDIT_OK: feature 263 plan review - REFUSE unreadable, an empty verdict (the decision crashed) or
      # anything unforeseen is CLOSED: the call cannot be shown to belong to a live loop, so it is refused
      printf 'BLOCKED: ScheduleWakeup, and this guard could not establish that the session is running a live /loop\n(its transcript was unreadable, or the check itself failed - %s). Outside a loop, background work wakes\nthe session by itself; a reminder the GM asked for is CronCreate'"'"'s job. (feature 263)\n' "${verdict:-no verdict}" >&2
      guard_log wakeup blocked "ScheduleWakeup" unreadable; exit 2 ;;
  esac
}

stop() {
  local verdict line
  INPUT="$(cat)"
  verdict="$(decide stop 2>/dev/null)"
  case "$verdict" in
    BLOCK*)
      {
        printf 'A WAKEUP WOULD OUTLIVE THIS TURN (feature 263): a ScheduleWakeup is still pending outside /loop.\n'
        printf 'It keeps the GM'"'"'s tab on the hourglass and brings this session back for nothing. Cancel it:\n'
        printf '%s\n' "$verdict" | tail -n +2 | while IFS='|' read -r id sched prompt; do
          [ -n "$id" ] && printf '    CronDelete %s      (%s: %s)\n' "$id" "$sched" "$prompt"
        done
        printf 'Background work wakes this session by itself when it finishes; nothing needs a timer.\n'
      } >&2
      guard_log wakeup blocked "stop" stale-wakeup
      exit 2 ;;
    *) exit 0 ;;
  esac
}

case "$MODE" in
  pretool) pretool ;;
  stop) stop ;;
  *) exit 0 ;;
esac
