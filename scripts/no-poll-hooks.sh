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
# visible in the transcript rather than habitual. The escape permits the WAIT; it does not switch
# off the self-match correction (GUARD_EDIT_OK: GM 2026-09-08, after an escaped waiter looped for
# hours on a gate that had finished) - a literal `pgrep -f` pattern is bracketed on the escaped path too.
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
# GUARD_EDIT_OK: feature 168 - THE ESCAPE IS RECORDED. The escape rate is the number this project has
# actually acted on (162 retired a refusal that was escaped 62% of the time), and it was computable
# for one guard only. The escape itself is unchanged: nothing newly refused, nothing newly permitted.
# Sourced here rather than below, because this branch exits before the later sourcing.
NP_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$NP_HERE/_guardlog.sh"

# bracket_self_match <rule> <context> - if the command carries a literal process-match pattern
# (`pgrep -f "make done"`), emit it REWRITTEN with the bracket trick and exit 0; otherwise return.
# The pattern is part of this very command line, so pgrep -f finds this shell and reports "running"
# forever. A pattern built from a variable ($VAR - the literal text on the command line is the
# variable name) or written with the bracket trick ([m]ake) does not self-match, so both are left
# alone (`_hm_shape.py bracket` returns nothing for them). Shared by the escape branch and section 4.
# GUARD_EDIT_OK: 2026-09-08 (GM) - THE ESCAPE NO LONGER SKIPS THE CORRECTION. A POLL_OK wait exited
# this guard before section 4 ran, so an escaped loop kept its self-matching pattern: a waiter on a
# detached `make page-check` carried `! pgrep -f "make page-check"` in its exit condition, escaped
# with POLL_OK because the loop was legitimately waiting on a detached run's log, and then looped for
# hours on a gate that had finished in 7 s - the exact 2026-07-25 fault, let through by the token.
# The escape decides whether the WAIT is permitted; it says nothing about whether the pattern is
# correct, and the correction is mechanical, so it applies on both paths.
bracket_self_match() {  # rule, context
  printf '%s' "$SCAN" | grep -Eq '\b(pgrep|pkill)\b[^|;&]*[[:space:]]-[a-zA-Z]*f' || return 0
  local fixed
  fixed=$(printf '%s' "$INPUT" | "$NP_HERE/_hm_shape.py" bracket 2>/dev/null || true)
  [ -n "$fixed" ] || return 0
  guard_log no-poll rewrote "$(guard_cmd)" "$1"
  printf '%s' "$INPUT" | REWRITTEN="$fixed" CONTEXT="$2" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
payload["command"] = os.environ["REWRITTEN"]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": os.environ["CONTEXT"],
}}))'
  exit 0
}
# The sanitized copy (heredoc bodies and quoted strings blanked - see the note at section 1) is
# computed here so the escape branch can ask the same question section 4 asks.
SCAN=$(printf '%s' "$INPUT" | "$NP_HERE/_hm_shape.py" sanitize 2>/dev/null || printf '%s' "$CMD")
[ -n "$SCAN" ] || SCAN="$CMD"

# GUARD_EDIT_OK: feature 169 - the escape is an INVOCATION, not a mention (was `case *POLL_OK*`).
# GUARD_EDIT_OK: feature 169 - $NP_HERE, not $HERE. This branch sits at line 60 and `HERE` is not
# defined until line 72, so the path was empty and the escape silently stopped working - caught by
# the new suite within a minute, which is why the escape is tested in BOTH directions.
if escape_or_refuse no-poll POLL_OK poll-ok "$NP_HERE"; then   # GUARD_EDIT_OK: feature 170
  bracket_self_match escaped-self-match \
    "POLL_OK permitted this wait, and its process-match pattern was bracketed for you: a literal pattern is an argument of the command line being searched, so it always finds the searching shell itself and the loop never ends (2026-09-08: an escaped waiter on a detached page-check looped for hours on a gate that finished in 7 s). The escape decides whether you may wait; it does not make the pattern correct."
  exit 0
fi

# GUARD_EDIT_OK: feature 164 - A MENTION IS NOT AN INVOCATION, and this guard was the last common
# offender. It matches substrings, so it refused the very command that was WRITING feature 164's
# specification, because that text quotes the shapes it forbids - and it did the same to a plan and
# to a set of test vectors, four times in one session. `_hm_shape.py sanitize` blanks heredoc bodies
# and quoted strings, which is where prose travels; every pattern below now runs against that, so a
# command that TALKS about a busy-wait passes and one that RUNS one does not. Same fix `gate-hooks`
# took on 2026-08-29, same reason, and CLAUDE.md's standing rule for guards: match INVOCATIONS.
HERE="$NP_HERE"   # GUARD_EDIT_OK: 2026-09-08 - one resolution; SCAN is computed above the escape branch now

block() {  # reason, alternative, RULE
  # GUARD_EDIT_OK: feature 168 - the entry names WHICH rule fired, because this guard enforces three
  # and "no-poll fired 32 times" cannot say which one is carrying the cost. Nothing about what it
  # refuses changes.
  guard_log no-poll blocked "$(guard_cmd)" "${3:-block}"
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
  # GUARD_EDIT_OK: feature 165 - THE ONE WAIT THAT IS NOT A BUSY-WAIT, at the GM's ruling
  # (2026-08-30). A BACKGROUNDED loop watching a FILE is the harness's own documented shape for a
  # single completion notification, and the only way to wait on a run detached with `setsid --fork` -
  # which this repository now requires for a long `make` run, because a non-detached one gets reaped.
  # This guard fired on exactly that twice on the day of the ruling.
  #
  # THE BOUNDARY IS CLOSED AND NARROWER THAN THE RULING'S WORDS, deliberately. The GM was offered
  # "permit whenever backgrounded" and DECLINED it as usable for a general bypass, so the condition
  # must read a file in one of three forms and may contain no command substitution, no pipeline and
  # no OUTPUT redirection - without that last clause `until curl ... > /tmp/out` qualifies and
  # `>/dev/null` on any condition becomes the bypass the GM refused. `_hm_shape.py file-wait` holds
  # the decision, where it is unit-testable; a foreground loop never reaches it.
  # GUARD_EDIT_OK: feature 212 - THE FOREGROUND FORM OF THAT SAME WAIT IS BACKGROUNDED, NOT REFUSED.
  # The permitted shape is this command with `run_in_background` set - the harness's own single
  # completion notification - so a foreground loop that would qualify backgrounded is returned
  # with the flag set and told (GM 2026-09-07: "simply do the correct thing and then inform the
  # session through hook context that we have done it"). The boundary does not move: the same
  # condition test (`_hm_shape.py file-wait-loop`), and a loop on a process or a network call is
  # refused below as before.
  #
  # GUARD_EDIT_OK: feature 227 (GM 2026-09-12) - ...AND THE WAIT GETS A PROOF OF LIFE. A permitted file
  # wait that never asks whether the thing writing the file is still there waits forever when it is not:
  # a detached `make` run finished its work, was killed by the kernel's OOM killer before it could flush
  # stdout (36 firings in this container's /proc/vmstat), and the waiter sat on a pattern that was never
  # going to be printed. The GM's rule for this tooling - *"if you are waiting on output to appear
  # somewhere, but not checking to see whether the process that is supposed to generate that output is
  # still alive, then when possible, the hook should add the second proof of life check to what is being
  # waited for"*, because *"simply telling you to set a watch properly next time is bad engineering
  # practice ... that's just another version of making you remember to do something."* So the clause is
  # ADDED, naming the file the loop itself watches (`_hm_shape.py proof` -> `_writer-alive.sh`), and the
  # permitted-and-already-complete wait is the only one that passes through silently.
  if [ "$(printf '%s' "$INPUT" | "$HERE/_hm_shape.py" file-wait-loop 2>/dev/null)" = "yes" ]; then
    NP_PROOF=$(printf '%s' "$INPUT" | "$HERE/_hm_shape.py" proof "$HERE/_writer-alive.sh" 2>/dev/null || true)
    # inside this branch the condition already qualifies, so `file-wait` answers exactly one question:
    # is it backgrounded?
    NP_BG=$(printf '%s' "$INPUT" | "$HERE/_hm_shape.py" file-wait 2>/dev/null)
    if [ -z "$NP_PROOF" ] && [ "$NP_BG" = "yes" ]; then
      guard_log no-poll permitted "$(guard_cmd)" detached-file-wait   # GUARD_EDIT_OK: feature 168, the rule slug
      exit 0
    fi
    NP_RULE=proof-of-life
    [ "$NP_BG" = "yes" ] || NP_RULE=backgrounded-file-wait
    guard_log no-poll rewrote "$(guard_cmd)" "$NP_RULE"
    printf '%s' "$INPUT" | NP_PROOF="$NP_PROOF" NP_BG="$NP_BG" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
proof, bg = os.environ.get("NP_PROOF") or "", os.environ.get("NP_BG") == "yes"
if proof:
    payload["command"] = proof
payload["run_in_background"] = True
said = []
if not bg:
    said.append(
        "This file-watching wait was BACKGROUNDED for you (run_in_background): in the foreground it would "
        "have held the whole turn at model-turn cost. Its output - including whatever follows the loop - "
        "arrives as a completion notification, so spend the turn on the next thing.")
if proof:
    said.append(
        "A PROOF-OF-LIFE check was added to the loop: `_writer-alive.sh <the file you are watching>`, which "
        "asks the kernel whether anything still holds that file open and when it was last written. Without "
        "it the wait outlives its producer - a detached run that is killed (this container OOM-kills them) "
        "stops writing, the pattern never appears, and the loop runs until somebody notices. When the loop "
        "ends, read what the log DOES have: if the helper printed a line, the run is gone and the log is "
        "truncated, not finished.")
said.append("A wait on a process or a network call is still refused.")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": " ".join(said),
}}))'
    exit 0
  fi
  block "this is a busy-wait loop (a loop containing \`sleep\`)." \
    "Waiting in a loop burns wall-clock at full model-turn cost and, for anything the harness tracks, it
is pure waste: a backgrounded Bash command notifies you the moment it exits." busy-wait-loop
fi

# ---- 3. sleep invoked in a form that only exists to dodge the harness's foreground-sleep guard ----
if printf '%s' "$SCAN" | grep -Eq '(^|[;&|(]|[[:space:]])([\\]|(command|env|busybox)[[:space:]]+|/(bin|usr/bin)/)sleep[[:space:]]+[0-9.]'; then
  block "\`sleep\` was invoked in a form that evades the harness's foreground-sleep block." \
    "The harness blocks foreground \`sleep\` on purpose; \`command sleep\`, \`/bin/sleep\` and \`env sleep\`
are the same thing wearing a hat. Whatever you were about to wait for, there is a better signal for
it - a completion notification for harness-tracked work, or POLL_OK for genuinely external state." disguised-sleep
fi
# (GUARD_EDIT_OK: feature 168 - the rule slug above; nothing about what this refuses changes)

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
# (GM 2026-08-30). `_hm_shape.py bracket` returns nothing for a pattern that is already bracketed or
# built from a variable - neither can match its own command line - so those are untouched as before.
# GUARD_EDIT_OK: 2026-09-08 - the emission moved into `bracket_self_match` above, shared with the
# escape branch; the rule slug `self-match` names this branch in the log (it defaulted to the event).
bracket_self_match self-match \
  "The process-match pattern was bracketed for you: a literal pattern is an argument of the command line being searched, so it always finds the searching shell itself and the wait never ends. Corrected rather than refused - the refusal used to cost a round trip to say the same thing."

exit 0
