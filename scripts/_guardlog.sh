#!/usr/bin/env bash
# _guardlog.sh - what a guard did, recorded so the next tuning starts from a total (feature 162).
#
# WHY (GM 2026-08-30): *"I notice I've been seeing a lot of this in the output of my claude code
# sessions over time ... Given how expensive that is, should we make it so we start blocking at 2 in
# a row instead of 3 in a row?"* Answering that took a replay of 715 MB of session transcripts,
# because no guard in this repository records anything when it fires. `docs/review-ledger.md` exists
# so that "is it pulling its weight" is a TOTAL for the review subagents; this is the same thing for
# the two guards feature 162 touches.
#
#   guard_log <guard> <blocked|escaped|rewrote|reminded> <detail>
#
# ONE FILE PER ENTRY, never an appended shared file - the reason is `dev/run-log/README.md`'s: several
# clones work at once and a shared append conflicts on every push. HOST-WIDE (~/.claude/guard-log/)
# rather than in a clone, because a hook fires for commands that name no working tree at all and
# main's tree is never written by a session. The cost, stated rather than hidden: the log is not
# versioned, and a container rebuild loses it.
#
# It must never take a guard down with it: every failure here is swallowed.
# THE COMMAND, PARSED PROPERLY, for the log only. Both hooks read the command with a greedy sed that
# takes everything to the last quote of the payload - deliberately, because every OTHER use is a
# substring test where over-reading is safe. A log entry is read by a person, so it gets the real
# thing; the parse costs a python start and only ever runs when something is being recorded.
#
# ... OR THE FILE PATH, when the tool has no command (feature 168). `readme`, `source-block` and
# `guard-file`'s Read reminder all guard the Edit/Write/Read tools, whose payload carries `file_path`
# and no `command` at all - so each of them was recording an entry with an EMPTY detail, which says
# that something fired but not what on. One body, because the two are the same question: what did the
# session try to do. (Found while auditing FR-002's coverage; fixed here per Principle XIV.)
guard_cmd() {
  printf '%s' "${INPUT:-}" | python3 -c '
import json, sys
try:
    ti = json.load(sys.stdin).get("tool_input", {}) or {}
    print((ti.get("command") or ti.get("file_path") or "")[:200])
except Exception:
    pass' 2>/dev/null || true
}

# guard_log <guard> <event> <detail> [rule]
#
# THE RULE IS THE FOURTH FIELD (feature 168, GM 2026-08-30: *"the firing log should record more data
# for us to be able to use to make improvements in the future"*). Several guards enforce more than one
# thing, and "no-poll fired 32 times" cannot say which of its three rules is carrying the cost - the
# unit a future improvement acts on is a RULE, not a script. Absent, it records as the event.
#
# AN ESCAPE IS A BRANCH, and the one that matters most: the escape RATE is what this project has
# actually acted on (feature 162 retired a refusal that was being escaped 62% of the time), and before
# this feature it was computable for exactly one guard.
guard_log() {
  { GL_DIR=${GUARD_LOG_DIR:-$HOME/.claude/guard-log}
    mkdir -p "$GL_DIR" 2>/dev/null || return 0
    GL_TS=$(date -u +%Y%m%dT%H%M%S%6N 2>/dev/null || date -u +%Y%m%dT%H%M%S)
    GL_F="$GL_DIR/$GL_TS-$$.json"
    python3 - "$GL_F" "$1" "$2" "$3" "${SID:-unknown}" "${4:-}" <<'PY' 2>/dev/null || true
import json, sys, time
path, guard, event, detail, session, rule = sys.argv[1:7]
json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "guard": guard,
           "event": event, "rule": rule or event, "session": session, "detail": detail[:200]},
          open(path, "w"), indent=2)
PY
  } >/dev/null 2>&1 || true
  return 0
}
