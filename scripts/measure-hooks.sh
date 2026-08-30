#!/usr/bin/env bash
# GUARD_EDIT_OK: a NEW guard, added at the GM's request (2026-08-28, feature 146) - see WHY below.
#
# measure-hooks.sh - Claude Code harness hook that BLOCKS a repeated EXPENSIVE MEASUREMENT
# (`make test-full`, `make done FULL=1`) when nothing about the code has changed enough to justify
# re-deriving the numbers.
#
# WHY (GM 2026-08-28, feature 146). The GM read a session's transcript and asked: *"Are you adding
# tests one at a time and then rerunning all of the tests? because that seems really inefficient
# since you know what lines need to be covered ... I thought that our project had some guidelines
# about this. Does it not? or is it the case that you are not following them?"* It does, and the
# session was not: `CLAUDE.md` has said *"Iterate on ONE artifact; run the full test bed exactly
# once, at the end"* since 2026-08-23. Measured on that feature: **20 `make test-full` runs at
# 2.5-4 minutes each - about an hour**, almost all of it re-deriving a coverage worklist the session
# already had written down. The cheap loop (`make quick`, ~4 s; `make test-file`, ~1-3 s) is not the
# problem and is never blocked; the expensive re-measurement is.
#
# The GM's own framing of the fix: *"if the tests are run within the same session more than a
# certain number of times ... then we fail, with a message instructing you to ... make batches of
# changes rather than rerunning the tests after making each individual change."*
#
# WHAT IT DOES. Per session it counts EXPENSIVE measurements since the last one that was worth
# taking, and blocks the (BUDGET+1)th:
#   - `make test-full` / `make done FULL=1` / `make -C ... test-full`  -> count one
#   - an Edit/Write to a file under `l7r/` (ENGINE code)               -> reset: the numbers really
#                                                                        are stale now, measure away
#   - a `git commit`                                                   -> reset: a landed batch is
#                                                                        the unit this rule is about
# Test edits do NOT reset it, deliberately: writing one test and re-measuring is the exact loop the
# GM asked to stop. Write the batch, run `make quick` between (free), and measure once.
#
# It blocks at most ONCE per over-budget streak (the counter resets on the block), so it can never
# deadlock: re-issuing the measurement goes through.
#
# ESCAPE HATCH: put MEASURE_OK in the command with a reason - a legitimate re-run after fixing a red
# (the measurement failed and you fixed the cause), or a deliberate before/after pair for a record.
#
# GUARD_EDIT_OK: feature 164 - FIXING A GUARD THAT FIRES ON CORRECT WORK. A MENTION IS NOT AN
# INVOCATION. This file used to record the opposite as an accepted limitation: *"the classifier is a
# substring test ... a command that merely MENTIONS a full run counts as one ... a real command parse
# is not worth the false-negative risk."* That trade-off was made before `_hookmatch.py` existed. It
# does now, `gate-hooks` has used it since 2026-08-29, and the cost of the old reading was measured on
# this feature's own work: a command writing PROSE that named a gate target spent a budget slot, so
# the next genuine measurement would have been refused for something nobody ran. The patterns below
# match the SANITIZED command - heredoc bodies and quoted strings blanked, which is where prose
# travels - so a document about the guard passes and a measurement does not. The BLOCK itself, its
# budget and its escape are untouched: that block is the point.
#
# Wired from .claude/settings.json. Tested by scripts/test-measure-hooks.sh.
set -euo pipefail

MODE=${1:-}
INPUT=$(cat 2>/dev/null || true)
STATE_DIR=${MEASURE_STATE_DIR:-/tmp/claude-measure}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# GUARD_EDIT_OK: feature 162, at the GM's request - this guard now records what it does, and asks the
# run log what a target costs instead of quoting a number typed in August.
# shellcheck source=/dev/null
. "$HERE/_guardlog.sh"
# THE BUDGET IS ONE (GM 2026-08-30): *"should we make it so we start blocking at 2 in a row instead of
# 3 in a row?"* So the SECOND expensive measurement in a streak is refused, not the third.
#
# WHAT THAT COSTS, recorded rather than hidden. Replaying this project's transcripts through this
# state machine (specs/162-guard-block-economics/measure/replay.py) says the tighter budget roughly
# doubles the firings - 30 -> 56 over the recorded history - and 5 of the 9 real firings so far ended
# with the measurement running anyway (4 via MEASURE_OK). A firing spends a model round trip, so a
# budget only pays through DETERRENCE. What makes this one pay is the reminder below, which arrives
# on the FIRST run and costs nothing at all. If the escape rate stays above about half once the
# firing log can measure it, this number is the thing to revisit - which is why it is one line.
BUDGET=${MEASURE_BUDGET:-1}

json_str() { printf '%s' "$INPUT" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//'; }
json_cmd() { printf '%s' "$INPUT" | tr '\n' ' ' | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p' | head -1; }

SID=$(json_str session_id); SID=${SID:-nosession}
TOOL=$(json_str tool_name); TOOL=${TOOL:-unknown}
mkdir -p "$STATE_DIR"
STATE="$STATE_DIR/${SID//[^A-Za-z0-9_-]/_}.measures"

count() { cat "$STATE" 2>/dev/null || echo 0; }

case "$MODE" in
  pretool)
    CMD=$(json_cmd)
    case "$TOOL" in
      Edit|Write|NotebookEdit)
        # AN ENGINE EDIT MAKES THE NUMBERS GENUINELY STALE. A test edit does not: the whole point is
        # that you can write twenty tests against a worklist you already have and measure once.
        fp=$(json_str file_path)
        case "$fp" in
          */tests/*) ;;                       # tests: no reset, that is the loop being discouraged
          *l7r/*.py) : > "$STATE" ;;          # engine: reset
        esac
        exit 0
        ;;
    esac
    [ "$TOOL" = Bash ] || exit 0
    # GUARD_EDIT_OK: feature 162 - the escape is RECORDED, so the escape rate is a total rather than
    # an impression. The escape itself is unchanged; nothing is blocked that was not blocked before.
    # GUARD_EDIT_OK: feature 169 - the escape is an INVOCATION, not a mention, and this guard is the
    # one the defect was measured on: all six recorded `measure escaped` entries of 2026-08-30 were
    # mentions (four heredoc bodies and commit messages, two word lists from an audit enumerating the
    # tokens), so `make audit` reported a 100% escape rate for a guard nobody had escaped. Worse, the
    # branch clears $STATE - the repeat-measurement counter - so a session that merely GREPPED for the
    # token switched the guard off for its next expensive run. The escape is still checked first.
    # GUARD_EDIT_OK: feature 170 - and it must say WHY. The counter reset stays on the PERMIT path:
    # a refused bare token must not clear the state that decides whether the NEXT run is refused.
    if escape_or_refuse measure MEASURE_OK measure-ok "$HERE"; then : > "$STATE"; exit 0; fi
    case "$CMD" in *"git commit"*) : > "$STATE"; exit 0 ;; esac

    # GUARD_EDIT_OK: feature 164 - the shapes are matched against the SANITIZED command (see the note
    # at the top). `SCAN` falls back to the raw command if the matcher cannot be reached, so a broken
    # helper makes this guard stricter rather than blind.
    SCAN=$(printf '%s' "$INPUT" | "$HERE/_hm_shape.py" sanitize 2>/dev/null || printf '%s' "$CMD")
    [ -n "$SCAN" ] || SCAN="$CMD"
    case "$SCAN" in
      *"make test-full"*|*"make -C"*test-full*|*"done FULL=1"*)
        N=$(( $(count) + 1 ))
        if [ "$N" -gt "$BUDGET" ]; then
          : > "$STATE"   # block ONCE - re-issuing goes straight through, so this cannot deadlock
          # GUARD_EDIT_OK: feature 162 - the budget dropped to 1 at the GM's request, so the message
          # names the SECOND run rather than the third, and the firing is recorded.
          guard_log measure blocked "$(guard_cmd)"
          cat >&2 <<'MSG'
BLOCKED: that is the second EXPENSIVE measurement in a row with no engine change and no commit between.

This is the expensive one; `make quick`, `make test-file` and `make cov-file` are the cheap loop and are
never blocked, however often they run. Measured on feature 146: 20 test-full runs, about an hour, almost all
of it re-deriving a coverage worklist the session already had written down.
(GUARD_EDIT_OK: feature 162 - the durations that used to be quoted here are gone rather than restated. A
number typed into a guard message in August is wrong in September and nothing tells anybody; `make audit`
and `scripts/_gatecost.py` answer from the run log instead.)

Do this instead:
 - ASKING WHICH LINES A TEST REACHES? That is what the third run is usually for, and this is the slowest way
   to be told. `make cov-file FILE=tests/... MOD=l7r/diagram/...` answers it in seconds, for one test file,
   and it is the only command here that answers it at all. It catches the commonest mistake this guard sees:
   a test that covers the guard ABOVE the branch it was aimed at (measured twice on feature 146, at ten
   minutes an answer).
 - You already know what the measurement will say. Work from the LIST, not from the run: write the whole
   batch of tests or fixes in one go.
 - Between edits run `make quick` (or `make test-file FILE=...`) - free, and it catches a broken test at once.
 - Measure ONCE when the batch is done. `CLAUDE.md`: "Iterate on ONE artifact; run the full test bed exactly
   once, at the end."

(Escape: put MEASURE_OK in the command with a reason - a re-run after fixing a red the measurement itself
found, or a deliberate before/after pair for a record. An engine edit or a git commit resets this too.)
MSG
          exit 2
        fi
        printf '%s' "$N" > "$STATE"
        # THE REMINDER ARRIVES ON THE FIRST RUN, NOT AT THE FIRST FAILURE (GM 2026-08-30,
        # GUARD_EDIT_OK: a new non-blocking behavior, nothing newly refused). *"should the output of
        # the FIRST successful expensive measurement emit a reminder about this so that you don't
        # need to wait until the first failure ... That might inform future sessions before they see
        # the failure."*
        #
        # A block costs a model round trip. `additionalContext` on an ALLOWED call costs nothing and
        # reaches the model just as surely - so the teaching happens where it is free, and the block
        # is left to be the thing that catches a session which was told and carried on anyway.
        # Once per streak: the counter is what distinguishes the first run from the rest.
        if [ "$N" -eq 1 ]; then
          guard_log measure reminded "$(guard_cmd)"
          COST=$("$HERE/_gatecost.py" done full 2>/dev/null || true)
          COST_LINE=""
          [ -n "$COST" ] && COST_LINE="The last runs of this measurement recorded a median of ${COST} s. "
          REMIND="REMINDER (measure-hooks, once per batch of work): this is the expensive measurement. ${COST_LINE}The NEXT one in this streak is refused unless an engine edit or a git commit comes between - a test edit deliberately does not reset it, because writing one test and re-measuring is the loop this guard exists to stop (measured on feature 146: about an hour of re-deriving a coverage worklist the session already had). Work from the list instead: write the whole batch, run \`make quick\` or \`make test-file FILE=...\` between edits, and ask \`make cov-file FILE=... MOD=...\` which lines one test file actually reaches - it is the only command here that answers that, and the commonest wrong answer is that the test covered the guard ABOVE the branch it was aimed at."
          REMIND="$REMIND" python3 -c '
import json, os
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                         "additionalContext": os.environ["REMIND"]}}))'
        fi
        exit 0
        ;;
    esac
    exit 0
    ;;
  status)
    echo "measurements_since_reset=$(count) budget=$BUDGET"
    ;;
  *)
    echo "measure-hooks: unknown mode '$MODE' (want: pretool | status)" >&2
    exit 1
    ;;
esac
exit 0
