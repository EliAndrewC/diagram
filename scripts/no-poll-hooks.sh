#!/usr/bin/env bash
# no-poll-hooks.sh - a Claude Code PreToolUse hook that BLOCKS busy-wait polling in Bash calls.
#
# WHY (GM 2026-07-25, from a transcript profile of a 31-minute feature): 10.9 minutes of it - 35% of
# the whole task - was spent polling a background gate that had ALREADY FINISHED. The session
# backgrounded `make done` correctly and then blocked on this:
#
#     for i in $(seq 1 80); do if ! pgrep -f "make done" >/dev/null 2>&1; then break; fi; command sleep 5; done
#
# Two independent faults, and each one alone was enough to waste the time:
#
#   1. `pgrep -f "make done"` MATCHES ITS OWN SHELL. The pattern is an argument of the very command
#      line being searched for, so pgrep always finds the polling process itself and the `break`
#      can never fire. Both waits ran their full iteration budget: the gates took 97s and 98s, the
#      waits took 351s and 401s. This is not a rare footgun - `pgrep -f <literal>` issued from a
#      shell is self-matching BY CONSTRUCTION, every time.
#   2. POLLING WAS NEVER NEEDED. The harness sends a completion notification and re-invokes the
#      session when a backgrounded command finishes; the Bash tool's own docs say not to poll for
#      it. The correct shape is: background the work, do something useful, act on the notification.
#
# It also defeats the harness's own foreground-`sleep` guard: plain `sleep` is blocked, and
# `command sleep` / `/bin/sleep` / `env sleep` exist here only as ways around that block.
#
# This is a CONTROL, not a reminder, for the same reason batching-hooks.sh is: the project had a
# documented "background the final gate" rule at the time, and the session followed it and then
# blocked on the gate anyway. Instructions you must remember perfectly every time are a worse
# design than a thing that simply cannot happen.
#
# ESCAPE HATCH: genuine waits on EXTERNAL state the harness cannot notify about (a dev server's
# port opening, a remote queue) are legitimate - put the token POLL_OK in the command, ideally as a
# comment naming what is being waited on. The token is deliberately explicit so the choice is
# visible in the transcript rather than habitual.
#
# Wired from .claude/settings.json alongside batching-hooks.sh / clone-sync-hooks.sh (every session
# runs MAIN's copy via an absolute path, so a change here takes effect everywhere at once).
# Tested by test-no-poll-hooks.sh - keep it green.
set -euo pipefail

MODE=${1:-pretool}
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

# The command is nested (tool_input.command) and is arbitrary text with escapes and newlines, so it
# needs a real JSON parse - grep would mangle it. Only Bash calls reach this hook, and those already
# cost seconds, so python's startup is not a factor here (batching-hooks.sh, which fires on every
# Read/Grep/Glob too, avoids python for exactly that reason).
CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)
[ -n "$CMD" ] || exit 0

# Explicit, visible opt-out for a real external-state wait.
case "$CMD" in *POLL_OK*) exit 0 ;; esac

# GUARD_EDIT_OK: feature 164 - A MENTION IS NOT AN INVOCATION, and this guard was the last common
# offender. It matches substrings, so it refused the very command that was WRITING feature 164's
# specification, because that text quotes the shapes it forbids - and it did the same to a plan and
# to a set of test vectors, four times in one session. `_hookmatch.py sanitize` blanks heredoc bodies
# and quoted strings, which is where prose travels; every pattern below now runs against that, so a
# command that TALKS about a busy-wait passes and one that RUNS one does not. Same fix `gate-hooks`
# took on 2026-08-29, same reason, and CLAUDE.md's standing rule for guards: match INVOCATIONS.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$HERE/_guardlog.sh"
SCAN=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" sanitize 2>/dev/null || printf '%s' "$CMD")
[ -n "$SCAN" ] || SCAN="$CMD"

block() {
  guard_log no-poll blocked "$(guard_cmd)"
  echo "BLOCKED (no-poll): $1

$2

Do this instead: background the work (run_in_background), spend the turn on something useful - docs,
the commit message, the next edit - and act on the completion notification when it arrives. The
harness re-invokes you; you never have to watch for it. If you truly must wait on EXTERNAL state the
harness cannot see (a server port, a remote queue), put POLL_OK in the command with a note saying
what you are waiting for.

(scripts/no-poll-hooks.sh. Measured 2026-07-25: two such waits cost 10.9 minutes - 35% - of a
31-minute feature, watching gates that had finished in 97s and 98s.)" >&2
  exit 2
}

# ---- 2. a loop containing a sleep: a busy-wait ---------------------------------------------------
SLEEP_RE='(^|[;&|(]|[[:space:]]|\bdo\b|\bthen\b)[\\]?((command|env|busybox)[[:space:]]+)?(/(bin|usr/bin)/)?sleep[[:space:]]+[0-9.]'
if printf '%s' "$SCAN" | grep -Eq '(^|[;&|[:space:]])(while|until|for)[[:space:]]' && printf '%s' "$SCAN" | grep -Eq "$SLEEP_RE"; then
  block "this is a busy-wait loop (a loop containing \`sleep\`)." \
    "Waiting in a loop burns wall-clock at full model-turn cost and, for anything the harness tracks, it
is pure waste: a backgrounded Bash command notifies you the moment it exits."
fi

# ---- 3. sleep invoked in a form that only exists to dodge the harness's foreground-sleep guard ----
if printf '%s' "$SCAN" | grep -Eq '(^|[;&|(]|[[:space:]])([\\]|(command|env|busybox)[[:space:]]+|/(bin|usr/bin)/)sleep[[:space:]]+[0-9.]'; then
  block "\`sleep\` was invoked in a form that evades the harness's foreground-sleep block." \
    "The harness blocks foreground \`sleep\` on purpose; \`command sleep\`, \`/bin/sleep\` and \`env sleep\`
are the same thing wearing a hat. Whatever you were about to wait for, there is a better signal for
it - a completion notification for harness-tracked work, or POLL_OK for genuinely external state."
fi

# ---- 4. a STANDALONE self-matching process match: corrected, not refused ------------------------
#
# ORDER IS LOAD-BEARING HERE, and this guard's own suite proved it (feature 164). The correction used
# to sit FIRST, and in that position it pre-empted both refusals above: the original 2026-07-25
# command - a `for` loop, a self-matching pattern and a disguised `sleep` on one line - was rewritten
# and ALLOWED, which is precisely the 10.9-minute busy-wait this guard exists to stop. So a rewrite
# may only reach a command the refusals have already declined to take, and it runs last. What
# survives to here is a process match with no loop and no sleep around it: a legitimate question
# ("is it still running?") asked in a way that answers itself wrongly.
# The pattern is part of this very command line, so pgrep -f finds this shell and reports "running"
# forever. A pattern built from a variable ($VAR - the literal text on the command line is the
# variable name) or written with the bracket trick ([m]ake) does not self-match, so both are allowed.
# GUARD_EDIT_OK: feature 164 - THE FIX IS APPLIED, NOT RECOMMENDED. This branch refused the command
# and then told the session, in prose, to use the bracket trick. That recommendation is a mechanical
# substitution, so the hook performs it: the command runs, correctly, and no round trip is spent
# (GM 2026-08-30). `_hookmatch.py bracket` returns nothing for a pattern that is already bracketed or
# built from a variable - neither can match its own command line - so those are untouched as before.
if printf '%s' "$SCAN" | grep -Eq '\b(pgrep|pkill)\b[^|;&]*[[:space:]]-[a-zA-Z]*f'; then
  FIXED=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" bracket 2>/dev/null || true)
  if [ -n "$FIXED" ]; then
    guard_log no-poll rewrote "$(guard_cmd)"
    printf '%s' "$INPUT" | REWRITTEN="$FIXED" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
payload["command"] = os.environ["REWRITTEN"]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": (
        "The process-match pattern was bracketed for you: a literal pattern is an argument of the "
        "command line being searched, so it always finds the searching shell itself and the wait "
        "never ends. Corrected rather than refused - the refusal used to cost a round trip to say "
        "the same thing."),
}}))'
    exit 0
  fi
fi

exit 0
