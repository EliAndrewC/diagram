#!/usr/bin/env bash
# _guardlog.sh - what a guard did, recorded so the next tuning starts from a total (feature 161).
#
# WHY (GM 2026-08-30): *"I notice I've been seeing a lot of this in the output of my claude code
# sessions over time ... Given how expensive that is, should we make it so we start blocking at 2 in
# a row instead of 3 in a row?"* Answering that took a replay of 715 MB of session transcripts,
# because no guard in this repository records anything when it fires. `docs/review-ledger.md` exists
# so that "is it pulling its weight" is a TOTAL for the review subagents; this is the same thing for
# the two guards feature 161 touches.
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
guard_cmd() {
  printf '%s' "${INPUT:-}" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", "")[:200])
except Exception:
    pass' 2>/dev/null || true
}

guard_log() {
  { GL_DIR=${GUARD_LOG_DIR:-$HOME/.claude/guard-log}
    mkdir -p "$GL_DIR" 2>/dev/null || return 0
    GL_TS=$(date -u +%Y%m%dT%H%M%S%6N 2>/dev/null || date -u +%Y%m%dT%H%M%S)
    GL_F="$GL_DIR/$GL_TS-$$.json"
    python3 - "$GL_F" "$1" "$2" "$3" "${SID:-unknown}" <<'PY' 2>/dev/null || true
import json, sys, time
path, guard, event, detail, session = sys.argv[1:6]
json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "guard": guard,
           "event": event, "session": session, "detail": detail[:200]},
          open(path, "w"), indent=2)
PY
  } >/dev/null 2>&1 || true
  return 0
}
