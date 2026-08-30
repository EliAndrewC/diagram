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
# escape_or_refuse <guard> <token> <rule> <here-dir>
#
# THE ESCAPE, DECIDED IN ONE PLACE (feature 170, GM 2026-08-30: *"force the Claude Code session, which
# is performing the workaround to specify why they are doing it ... otherwise, we have no way to audit
# later when this workaround was taken and whether the stated reasons were valid use cases"*).
#
# Returns 0 when the session escaped WITH a reason - having recorded it, with the REASON as the entry's
# detail, because reading the reasons is the audit. EXITS 2 when the token is there and the reason is
# not: that is a refusal rather than a rewrite, because the missing thing is the session's reasoning
# and no tool can supply it. Returns 1 when no escape was used, so the caller carries on.
#
# Every guard calls this instead of writing the rule a seventh time. `$INPUT` is the hook payload the
# caller already read.
escape_or_refuse() {
  local guard=$1 token=$2 rule=$3 here=$4 reason
  printf '%s' "${INPUT:-}" | "$here/_hookmatch.py" escape "$token" 2>/dev/null | grep -q yes || return 1
  reason=$(printf '%s' "${INPUT:-}" | "$here/_hookmatch.py" escape-reason "$token" 2>/dev/null)
  if [ -z "$reason" ]; then
    {
      printf 'BLOCKED: %s with no reason given.\n\n' "$token"
      printf 'An escape is a workaround, and a workaround nobody can audit is indistinguishable from the\n'
      printf 'rule not existing. Say why, in the command, and it ships with it:\n\n'
      printf '    <your command>  # %s: <why this case is legitimate>\n\n' "$token"
      printf 'Two words and eight characters is the whole bar - "CI is down" clears it. What it stops is a\n'
      printf 'bare token and "%s: ok", which record that a rule was bypassed and nothing about why.\n' "$token"
      printf '(GM 2026-08-30, feature 170; the reasons are what `make audit` shows you.)\n'
    } >&2
    guard_log "$guard" blocked "$(guard_cmd)" "${token}-no-reason"
    exit 2
  fi
  guard_log "$guard" escaped "$reason" "$rule"
  return 0
}

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
