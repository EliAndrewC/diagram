#!/usr/bin/env bash
# guardlog.sh - what a guard did, recorded so the next tuning starts from a total (feature 162).
#
# WHY (GM 2026-08-30): *"I notice I've been seeing a lot of this in the output of my claude code
# sessions over time ... Given how expensive that is, should we make it so we start blocking at 2 in
# a row instead of 3 in a row?"* Answering that took a replay of 715 MB of session transcripts,
# because no guard in this repository records anything when it fires. `dev/review-ledger.md` exists
# so that "is it pulling its weight" is a TOTAL for the review subagents; this is the same thing for
# the two guards feature 162 touches.
#
#   guard_log <guard> <blocked|escaped|rewrote|reminded> <detail>
#
# ONE FILE PER ENTRY, never an appended shared file - the reason is `dev/run-log/README.md`'s: several
# clones work at once and a shared append conflicts on every push. HOST-WIDE (~/.claude/guard-log/)
# rather than in a clone, because a hook fires for commands that name no working tree at all and
# main's tree is never written by a session. The cost, stated rather than hidden: the log is not
# versioned. (It DOES survive a container rebuild - `/home/agent/.claude` is a host mount, checked
# against `mount` on 2026-09-07, feature 204; this comment used to say the opposite.)
# (GUARD_EDIT_OK: feature 204 - the record gains the fields an audit needs; nothing a guard DECIDES changes.)
#
# It must never take a guard down with it: every failure here is swallowed.

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
#
# (`escape_or_refuse`, the escape decided in shell, and `guard_cmd`, its parse of the command for the log, were removed with
# `hm_escape.py` - feature 449 T129: no script called either once every guard was ported to Rust. The rule is the guard's
# `shared::escape` (`escape_or_refuse` there), and the shell's one question of it, the reason floor, is `l7r-gate escape reason-ok`.)

# guard_log <guard> <event> <detail> [rule] [context-json]
#
# EVERY ENTRY CARRIES WHAT AN AUDIT NEEDS (feature 204, GM 2026-09-07: *"log the specific commands
# that they blocked along with when this happened and the name of the session in which this occurred.
# and any other context which is loggable at that time"*). The census that motivated it: 2,049 of
# 2,371 entries said `session: unknown`, because this read a shell variable ONE guard set instead of
# the payload's own `session_id`; the command was cut at 200 characters; nothing recorded the cwd, the
# tool, or what the guard was thinking. `utc` was already "when". `detail` stays, truncated, for the
# existing readers; `command` is the whole thing; `context` is the guard's own decision inputs, when
# it passes them. THE NAME IS RESOLVED NOW, NOT AT READ TIME: the transcripts a later lookup would
# need are pruned after 30 days, and the name is the GM's stated requirement - so it costs the claim
# map's one file read on every firing (do not "optimize" this away; a name not recorded at firing
# time cannot be recovered), and the transcript scan only for a session that has never claimed a
# clone. The name is the CLONE's directory name - the project's identity for a session - not the
# verbatim /rename title. The payload reaches python through a file: an environment variable has a
# size limit a heredoc-carrying command can exceed, and an entry that fails to write is the one
# failure this function must never have.
guard_log() {
  { GL_DIR=${GUARD_LOG_DIR:-$HOME/.claude/guard-log}
    mkdir -p "$GL_DIR" 2>/dev/null || return 0
    GL_TS=$(date -u +%Y%m%dT%H%M%S%6N 2>/dev/null || date -u +%Y%m%dT%H%M%S)
    GL_F="$GL_DIR/$GL_TS-$$.json"
    GL_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    GL_NAME=$(printf '%s' "${INPUT:-}" | "$GL_HERE/clone-resolve.sh" resolve 2>/dev/null | tail -1)
    GL_NAME=${GL_NAME##*/}
    GL_IN=$(mktemp 2>/dev/null || echo "$GL_F.in")
    printf '%s' "${INPUT:-}" > "$GL_IN"
    python3 - "$GL_F" "$1" "$2" "$3" "${SID:-unknown}" "${4:-}" "${5:-}" "$GL_NAME" "$GL_IN" <<'PY' 2>/dev/null || true
import json, sys, time
path, guard, event, detail, sid_env, rule, context, name, inp = sys.argv[1:10]
try:
    payload = json.load(open(inp))
except Exception:
    payload = {}
if not isinstance(payload, dict):
    payload = {}
ti = payload.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}
sid = payload.get("session_id") or (sid_env if sid_env not in ("unknown", "nosession") else "") or "unknown"
try:
    ctx = json.loads(context) if context else None
except Exception:
    ctx = context or None
# GUARD_EDIT_OK: fixing a defect found while working (2026-09-27) - `open(path, "w")` created the file
# BEFORE the entry was serialized, so a hook killed mid-write left a zero-byte entry (two on 2026-09-26)
# and `make audit` died reading it. Serialize first, write a temp beside it, rename into place.
import os
text = json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "guard": guard,
                   "event": event, "rule": rule or event, "session": sid, "session_name": name or sid,
                   "cwd": payload.get("cwd") or "", "tool": payload.get("tool_name") or "",
                   "transcript": payload.get("transcript_path") or "", "detail": detail[:200],
                   "command": ti.get("command") or ti.get("file_path") or "", "context": ctx}, indent=2)
with open(path + ".tmp", "w") as fh:
    fh.write(text)
os.replace(path + ".tmp", path)
PY
    rm -f "$GL_IN"
  } >/dev/null 2>&1 || true
  return 0
}
