#!/usr/bin/env bash
# gate-hooks.sh - Claude Code harness hook that BLOCKS `make done` when the only local test run
# since the last edit was a `-k` SUBSET.
#
# WHY (GM 2026-08-08). The dev-loop doc has said this since 2026-07-25, in its own section heading:
# "Before the gate, run the WHOLE affected test file - not a `-k` subset". The reasoning is that a
# `-k` filter selects the tests you were THINKING about, and the ones a change breaks are by
# definition the ones you were not. It is written down, it is correct, and a session followed it
# with `-k "kura_side or punishment"`, went to the gate, and the gate died on
# `test_place_punishment_spot_probes_for_a_clear_caption_seat` - a test in the same file, on the
# same function, that the filter did not select. That cost a full gate cycle: 3.9 minutes of idle
# plus the fix turns, on a change whose whole-file run takes ~45 seconds.
#
# Same lesson as batching-hooks.sh and no-poll-hooks.sh, for the third time: a rule that lives only
# in a document is not a control. This is the control.
#
# WHAT IT DOES. It watches Bash commands:
#   - a pytest run WITH `-k`      -> remembers "the last local test run was a subset"
#   - a pytest run WITHOUT `-k`   -> clears that (a whole-file/whole-suite run happened)
#   - an Edit/Write to a .py file -> clears it too: any local run now PREDATES the current code, so
#                                    it cannot vouch for it either way and the state is meaningless
#   - `make done` (the gate)      -> if the flag is set, BLOCK once, then clear it
# It blocks at most ONCE per subset run, so it can never deadlock: re-issuing the gate goes through.
#
# ESCAPE HATCH: put GATE_OK in the command with a reason (e.g. a docs-only diff, or a change whose
# affected test file genuinely ran green under a different invocation).
#
# LIMITATION, stated rather than hidden: the classifier is a substring test, so a command that merely
# MENTIONS pytest (a grep for it, a doc edit quoting it) is read as a run. That direction fails SAFE -
# a mention without `-k` only clears a flag, and a mention with `-k` costs at most one block, which
# GATE_OK clears. Tightening it to a real command parse is not worth the false-negative risk.
#
# Wired from .claude/settings.json. Tested by scripts/test-gate-hooks.sh.
set -euo pipefail

MODE=${1:-}
INPUT=$(cat 2>/dev/null || true)
STATE_DIR=${GATE_STATE_DIR:-/tmp/claude-gate}

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # `_hookmatch.py` lives beside this hook
# GUARD_EDIT_OK: feature 162 - this guard now RECORDS what it does (blocked, rewrote, escaped), so
# "is it worth what it costs" is a total rather than an impression. See scripts/_guardlog.sh.
# shellcheck source=/dev/null
. "$HERE/_guardlog.sh"

json_str() { printf '%s' "$INPUT" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//'; }
# The command can contain escaped quotes and newlines, so take everything between "command":" and
# the closing quote of that field rather than trying to be clever - only substring tests follow.
json_cmd() { printf '%s' "$INPUT" | tr '\n' ' ' | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p' | head -1; }

SID=$(json_str session_id); SID=${SID:-nosession}
TOOL=$(json_str tool_name); TOOL=${TOOL:-unknown}
mkdir -p "$STATE_DIR"
STATE="$STATE_DIR/${SID//[^A-Za-z0-9_-]/_}.subset"

case "$MODE" in
  pretool)
    CMD=$(json_cmd)
    case "$TOOL" in
      Edit|Write|NotebookEdit)
        # a source edit invalidates every earlier local run, subset or not
        fp=$(json_str file_path)
        case "$fp" in *.py) rm -f "$STATE" ;; esac
        exit 0
        ;;
    esac
    [ "$TOOL" = Bash ] || exit 0
    # GUARD_EDIT_OK: feature 168 - the escape is recorded. Its RATE is the number this project acts on.
    # GUARD_EDIT_OK: feature 169 - the escape is an INVOCATION, not a mention. This was
    # `case "$CMD" in *GATE_OK*)`, so a grep for the token, or a commit message quoting it, both
    # escaped the guard AND ran `rm -f "$STATE"`, silently disarming it for the next command. The
    # escape is still checked FIRST; only the match changed.
    if [ -n "$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" escape GATE_OK 2>/dev/null)" ]; then
      guard_log gate escaped "$(guard_cmd)" gate-ok; rm -f "$STATE"; exit 0
    fi

    # WHICH TARGETS DOES THIS COMMAND ACTUALLY INVOKE? Asked of `_hookmatch.py`, which anchors the match
    # to a real command position and blanks heredoc bodies and quoted strings first. Until 2026-08-29 this
    # hook tested substrings, and in one day it blocked six pieces of correct work whose TEXT contained
    # its two target names: a script analysing how often they had been run, a plan document quoting them,
    # twice the guard-test file that exists to prove guards do not do this, and the command that fixed it.
    # (GM 2026-08-29: "the small follow-up".) A guard that fires on correct work teaches a session to
    # reach for the escape as a matter of routine, which costs more than the duplication it prevents.
    TARGETS=" $(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" targets 2>/dev/null | tr '\n' ' ')"

    # QUICK AND DONE IN ONE COMMAND ARE COMBINED, NOT REJECTED (GM 2026-08-30, feature 162).
    #
    # GUARD_EDIT_OK: FIXING A GUARD THAT FIRES ON CORRECT WORK, at the GM's request and on measured
    # evidence. From 2026-08-26 to 2026-08-30 this refused such a command with exit 2. The refusal
    # was measured over this project's own transcripts and it did not pay: **37 firings, 23 of them
    # escaped with `GATE_OK` in the very next call** - 62% of the time the guard spent a round trip
    # and prevented nothing, which is the shape `CLAUDE.md` names as teaching a session to bypass
    # every guard. What it was protecting is one warm `make quick`, measured at 4.1 s (25.3 s cold),
    # against a round trip the GM prices in their own words: *"bouncing back a command forces another
    # pass through the LLM engine, which also takes time."*
    #
    # So the hook REWRITES instead. A `PreToolUse` hook may return `updatedInput` (the command the
    # session actually runs) and `additionalContext` (a line the model reads), both at exit 0 and
    # both free - verified against the installed harness before this was written, not read off a
    # document. `_hookmatch.py combine` decides: it returns the command with the `quick` work removed
    # when it can rebuild the shape exactly, and NOTHING when it cannot - a heredoc, an unbalanced
    # fragment, a rewrite that would not leave `done` standing alone. Silence means the command goes
    # through UNCHANGED. The guard never guesses at a session's command, because a wrong rewrite
    # costs the session its command while the fallback costs 4.1 s.
    COMBINED=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" combine 2>/dev/null || true)
    if [ -n "$COMBINED" ]; then
      guard_log gate rewrote "$(guard_cmd)"
      printf '%s' "$INPUT" | REWRITTEN="$COMBINED" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
payload["command"] = os.environ["REWRITTEN"]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": (
        "`make quick` was dropped from this command and `make done` runs alone: done is a superset "
        "(the same lint, format and typecheck, and a strict superset of the tests), so nothing you "
        "asked has gone unasked. Combined rather than refused because a refusal would have cost a "
        "model round trip to save one warm quick (4.1 s measured)."),
}}))'
      exit 0
    fi
    # the GATE itself
    case "$TARGETS" in
      *" done "*)
        if [ -f "$STATE" ]; then
          WAS=$(cat "$STATE" 2>/dev/null || true)
          rm -f "$STATE"          # block ONCE - re-issuing the gate goes straight through
          # GUARD_EDIT_OK: feature 162 - the message loses its two hardcoded durations ("a full
          # 3.9-minute gate cycle", "~45s") and names the make target rather than a bare pytest line.
          # The incident that set this rule is still recorded in the WHY at the top of this file,
          # where a date sits beside it; a number inside a MESSAGE has nothing to date it and goes
          # stale unremarked, which is the defect the GM caught in the other message here.
          echo "BLOCKED: the only local test run since your last edit was a \`-k\` SUBSET (${WAS:-pytest -k ...}). A subset selects the tests you were THINKING about; the ones a change breaks are the ones you were not - which is exactly how a session ran \`-k \"kura_side or punishment\"\`, went to the gate, and lost a whole gate cycle to a test in the SAME file it had not selected. Run the WHOLE test file(s) for the modules you touched first - \`make test-file FILE=tests/.../test_<mod>.py\` - then run the gate. (.claude/skills/diagram/CLAUDE.md, 'Before the gate, run the WHOLE affected test file'. Override: put GATE_OK in the command with a reason.)" >&2
          guard_log gate blocked "$(guard_cmd)" k-subset-before-gate   # GUARD_EDIT_OK: feature 168
          exit 2
        fi
        exit 0
        ;;
    esac

    # a local pytest run: subset or whole?
    #
    # AND A PYTEST MENTION IS NOT A PYTEST RUN (GM 2026-08-29, the same follow-up as the target matching
    # above). This branch tested for the substring `pytest` and then for ` -k `, so the guard's OWN test
    # file - whose vectors read `pytest tests/test_x.py -k foo` - set the subset flag, and the next gate
    # was blocked for a subset nobody had run. Seventh false positive of this shape in one day. The
    # matcher decides whether pytest is actually INVOKED: at a command position (`bare-pytest`), or
    # through the make targets that run tests.
    VERDICT=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" 2>/dev/null || echo ok)
    RUNS_TESTS=no
    [ "$VERDICT" = "bare-pytest" ] && RUNS_TESTS=yes
    case "$TARGETS" in *" test-file "*|*" test "*|*" quick "*) RUNS_TESTS=yes ;; esac
    if [ "$RUNS_TESTS" = yes ]; then
      case "$CMD" in
        *" -k "*|*" -k="*)  printf '%s' "$CMD" | head -c 120 > "$STATE" ;;
        *)                  rm -f "$STATE" ;;   # a whole-file / whole-suite run vouches for the code
      esac
    fi
    exit 0
    ;;
  status)
    if [ -f "$STATE" ]; then echo "subset_pending=1 cmd=$(cat "$STATE")"; else echo "subset_pending=0"; fi
    ;;
  *)
    echo "gate-hooks: unknown mode '$MODE' (want: pretool | status)" >&2
    exit 1
    ;;
esac
exit 0
