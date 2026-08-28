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
# LIMITATION, stated rather than hidden: the classifier is a substring test, like its siblings, so a
# command that merely MENTIONS `make test-full` (a grep, a doc edit quoting it) counts as a run. That
# direction fails safe - it costs at most one block, which MEASURE_OK clears - and a real command
# parse is not worth the false-negative risk.
#
# Wired from .claude/settings.json. Tested by scripts/test-measure-hooks.sh.
set -euo pipefail

MODE=${1:-}
INPUT=$(cat 2>/dev/null || true)
STATE_DIR=${MEASURE_STATE_DIR:-/tmp/claude-measure}
BUDGET=${MEASURE_BUDGET:-2}   # two in a row is a before/after pair; the third is the habit this stops

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
    case "$CMD" in *MEASURE_OK*) : > "$STATE"; exit 0 ;; esac
    case "$CMD" in *"git commit"*) : > "$STATE"; exit 0 ;; esac

    case "$CMD" in
      *"make test-full"*|*"make -C"*test-full*|*"done FULL=1"*)
        N=$(( $(count) + 1 ))
        if [ "$N" -gt "$BUDGET" ]; then
          : > "$STATE"   # block ONCE - re-issuing goes straight through, so this cannot deadlock
          cat >&2 <<'MSG'
BLOCKED: that is the third EXPENSIVE measurement in a row with no engine change and no commit between.

`make test-full` costs 2.5-4 minutes; `make quick` costs ~4 seconds and `make test-file` 1-3. Measured on
feature 146: 20 test-full runs, about an hour, almost all of it re-deriving a coverage worklist the session
had already written down.

Do this instead:
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
