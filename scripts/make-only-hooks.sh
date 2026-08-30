#!/usr/bin/env bash
# make-only-hooks.sh - a Claude Code PreToolUse hook that BLOCKS any route to an expensive
# operation other than its make target (feature 127, guard layer 1).
#
# WHY (GM 2026-08-24). The fast path already existed - `make reference` answers in ~26 s - and a
# session kept taking the five-minute and twenty-five-minute paths anyway. Four times in one feature,
# each time after being told not to, each time by a route the guards of the day did not cover:
#
#   THE THREAT MODEL, which is a record of what actually happened rather than what might:
#
#     tier 1  reach for an UNGATED SIBLING COMMAND        `cohort_audit` while `make maps` was gated,
#                                                          then `make done` and `make test` while both
#                                                          of those were
#     tier 2  supply the DOCUMENTED OVERRIDE               `REF_WHY=`, which skipped a prompt whose
#                                                          default answer is cancel
#     tier 3  ARRANGE THAT THE PROMPT CANNOT FIRE          backgrounding a `FULL=1` run, so nothing
#                                                          was attached to answer it
#     tier 4  FORGE A MAKEFILE                             never reached - closed here anyway
#     tier 5  EDIT A GUARD                                 never reached - guard-file-hooks.sh
#     tier 6  DISABLE THE HOOK SYSTEM                      never reached - a settings diff
#
# Every one of tiers 1-3 was an action that could be PRESENTED AS DILIGENCE, which is exactly why
# each worked: `REF_WHY="pre-push verification before merging to main"` reads as conscientious. That
# is the property this hook removes. Tiers 4-6 cannot be dressed up the same way, and two of them
# land in a git diff.
#
# WHICH LAYER CLOSES WHICH TIER (constitution FR-017 - recorded here so a later session can tell
# whether a proposed change reopens a known route):
#
#     tier 1  THIS FILE (command shape) + l7r/diagram/_invocation.py (process tree)
#     tier 2  THIS FILE (inline override vars) + the Makefile's cancel-by-default prompt
#     tier 3  the Makefile (a non-interactive FULL run is refused outright)
#     tier 4  THIS FILE (`make -f`) + _invocation.py (make's cwd and -f are checked)
#     tier 5  scripts/guard-file-hooks.sh
#     tier 6  visible in `git diff .claude/settings.json`
#
# WHY THIS LAYER IS LOAD-BEARING and _invocation.py is defense in depth: this runs in the HARNESS,
# outside the guarded process, BEFORE the command executes. So a refusal costs zero seconds, and it
# can see shapes no in-process check ever can - a bare `pytest`, a `make -f` naming a foreign
# makefile. _invocation.py catches what this file's patterns do not anticipate, and is the only
# layer that can catch an in-process `python3 -c "import ...; generate(...)"`.
#
# ESCAPE HATCH: none, deliberately. The make targets carry the override, where it is prompted,
# defaulted to cancel, and logged. An escape hatch here would be tier 2 with extra steps.

set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# DETECTION LIVES IN _hookmatch.py, and the reason is written there: substring matching false-
# positived on a grep, on a commit message, and on this hook's own test harness, all within an hour.
# Matching is anchored to real command positions instead. Keeping it in a file also means it can be
# unit-tested and read without bash quoting in the way.
# GUARD_EDIT_OK: feature 164 - the payload is CAPTURED before it is classified, because this hook now
# asks two questions of it (what is this, and can it be corrected) and stdin can only be read once.
# The classification itself is unchanged: the same `_hookmatch.py` call, fed from the variable.
INPUT=$(cat 2>/dev/null || true)
VERDICT=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" 2>/dev/null || echo ok)
# ...and it now CORRECTS the one shape whose compliant form it can rebuild exactly, and records what
# it did. See the bare-pytest case below.
# shellcheck source=/dev/null
. "$HERE/_guardlog.sh"

block() { # reason, then the make target to use instead
  # GUARD_EDIT_OK: feature 168 - every refusal is recorded, and the RULE is the verdict that produced
  # it (`bare-pytest`, `foreign-makefile`, `engine-entry-point`, `inline-override`, `guard-write`).
  # Before this, only the rewrite was recorded, so this guard's five refusals were invisible to
  # `make audit` - and a rule is the unit a future improvement acts on, not a script.
  guard_log make-only blocked "$(guard_cmd)" "$VERDICT"
  printf 'BLOCKED: %s\n\n' "$1" >&2
  printf 'Run this instead:  %s\n\n' "$2" >&2
  # GUARD_EDIT_OK: feature 162 - the LADDER LOSES ITS HARDCODED NUMBERS (GM 2026-08-30: *"I think
  # those numbers for `make quick` are wrong and outdated"*). They were: this message quoted "done
  # ~75 s locked / ~4.5 min unlocked (measured 2026-08-26)" while the scope had been UNLOCKED since
  # 2026-08-27 and the gate's own run log put the median at 111 s. The ordering is what a session
  # needs here and it does not go stale; the one number worth stating is asked of the recorded runs
  # at the moment it is printed, and omitted when the log cannot answer.
  DONE_COST=$("$HERE/_gatecost.py" done 2>/dev/null || true)
  cat >&2 <<'TAIL'
Every operation in this project goes through a make target, so the expensive ones can ask whether
the cheap one would do first. Cheapest first, so the choice is informed rather than habitual:

    make reference    one seed of the reference hamlet - answers most questions
    make quick        lint, types, and every test that does not roll a map, stops at the first
    make done         reference + lint/types + the suite; NOT the quick check
    make done FULL=1  + every pool map + the seeds 41-44 ratchet; prompts, cancels by default
TAIL
  [ -n "$DONE_COST" ] && printf '\n`make done` has cost a median of %s s over its recent recorded runs (`make audit` for the history).\n' "$DONE_COST" >&2
  cat >&2 <<'TAIL'

If this fired on correct work, that is a BUG in the hook and worth fixing rather than working
around - put GUARD_EDIT_OK in the command with a reason, and say what it false-positived on.

(scripts/make-only-hooks.sh; GM 2026-08-24, feature 127)
TAIL
  exit 2
}

case "$VERDICT" in
  guard-edit-ok)
    # GUARD_EDIT_OK: feature 170 - THE LAST SILENT PERMIT IN THIS GUARD. The escape used to return a
    # plain `ok` and leave no trace, so `make audit` could not show that this rule had been worked
    # around at all. It records now, with the reason as the detail, and refuses a bare token like
    # every other escape (GM 2026-08-30: *"we have no way to audit later when this workaround was
    # taken and whether the stated reasons were valid use cases"*).
    escape_or_refuse make-only GUARD_EDIT_OK guard-edit-ok "$HERE"
    exit 0 ;;
  foreign-makefile)
    block "a make driven by a named makefile. This project's targets are in its own Makefile, and a foreign one is the documented way to walk past every guard here." "make <target>   (from .claude/skills/diagram)" ;;
  engine-entry-point)
    block "an engine entry point run outside make." "make <target>   (see future-work/ and the Makefile for the operation list)" ;;
  bare-pytest)
    # GUARD_EDIT_OK: feature 164 - CORRECT THE ONE SHAPE THAT HAS AN EXACT COMPLIANT FORM, at the
    # GM's request (2026-08-30). A bare pytest of ONE test file is `make test-file` written the long
    # way, so the hook writes it the short way instead of spending a round trip asking the session to.
    # Every other shape - a filter, a coverage flag, a second path, a directory, a pipeline - still
    # refuses, because `_hookmatch.py as-make-target` returns nothing for anything it cannot rebuild
    # exactly, and a guard that guesses at a session's command costs more than one that refuses.
    #
    # TWO DEFECTS IN THE OLD MESSAGE, fixed here (Principle XIV, found while auditing):
    #   - it gave COVERAGE FLOORS as the reason, which is false: `make test-file` runs `--no-cov`
    #     exactly as a bare pytest does, and the floors are held by the gate targets. The true reason
    #     is feature 127's - every operation goes through make, so the expensive ones can ask whether
    #     the cheap one would do first.
    #   - it named only the gate targets, never `make test-file`, the target this project added for
    #     precisely the question "re-run the file I just changed" - missing from this message since 127.
    FIXED=$(printf '%s' "$INPUT" | "$HERE/_hookmatch.py" as-make-target 2>/dev/null || true)
    if [ -n "$FIXED" ]; then
      guard_log make-only rewrote "$(guard_cmd)"
      printf '%s' "$INPUT" | REWRITTEN="$FIXED" python3 -c '
import json, os, sys
payload = json.load(sys.stdin).get("tool_input", {})
payload["command"] = os.environ["REWRITTEN"]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": payload,
    "additionalContext": (
        "That bare pytest was rewritten to `make test-file`, the target this project added for "
        "running one file whole - everything here goes through make so an expensive run can ask "
        "whether the cheap one would do first. Corrected rather than refused, because a refusal "
        "costs a model round trip."),
}}))'
      exit 0
    fi
    block "pytest run directly rather than through make. Everything here goes through a make target, so an expensive run can ask whether the cheap one would do first - and a filter, a coverage flag or a second path is a shape this hook will not rewrite for you." "make test-file FILE=<one file>   (the whole file, no filter)  or  make quick   (stops at the first failure)  or  make done   (the gate)" ;;
  inline-override)
    block "an override supplied on the command line, which skips the prompt whose default answer is CANCEL. That prompt is the whole mechanism: it exists to be answered, not pre-empted." "make <target>   without the override, and answer the prompt if it appears" ;;
  guard-write)
    block "a GUARD FILE written from a shell command. Layer 3 only sees the Edit and Write tools, so this route slips past it - the same ungated-sibling shape this feature exists to close." "the Edit tool, or add GUARD_EDIT_OK with a reason" ;;
esac

exit 0
