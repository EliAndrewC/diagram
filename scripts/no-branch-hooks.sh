#!/usr/bin/env bash
# no-branch-hooks.sh - Claude Code harness hook that BLOCKS creating a git branch in this project.
#
# WHY (GM 2026-07-27): this project does not use feature branches, spec-kit work included. Isolation
# already comes from the session clone - every session works in its own .clones/<session-name>
# checkout - so a branch on top of that is a SECOND axis of isolation that buys nothing and actively
# costs. The concrete failure: `sync-with-main.sh` pushed `origin main`, which is the local REF NAMED
# main rather than HEAD, so a session sitting on a feature branch pushed a stale ref and hit
# "! [rejected] main -> main (non-fast-forward)" while every diagnostic said it was 4 ahead and 0
# behind. That push is fixed now (HEAD:main), but the branch bought nothing in the first place.
#
# Spec-kit is configured to match: the `before_specify` hook that ran speckit.git.feature is
# `enabled: false` in .specify/extensions.yml. This hook is the backstop for a branch created by
# hand, since documentation alone has never held (the same reasoning as batching-hooks.sh).
#
# WHAT TO DO INSTEAD. Nothing, usually - commit on main inside your clone, which is what the
# stop-work procedure expects. For spec-kit, `export SPECIFY_FEATURE=NNN-slug`: common.sh's
# get_current_branch() returns that ahead of asking git, so check_feature_branch() in setup-plan.sh
# and setup-tasks.sh is satisfied without a branch existing.
#
# ESCAPE HATCH. Put NO_BRANCH_OK in the command, with a note saying why, for the genuine exception
# (a throwaway bisect branch, recovering someone else's work). It is deliberately visible.
#
# Wired from .claude/settings.json alongside the other hooks. Tested by test-no-branch-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

# The command is nested and arbitrary text with escapes and newlines, so it needs a real JSON parse.
CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null || true)
[ -n "$CMD" ] || exit 0

# GUARD_EDIT_OK: feature 168 - records what it does, escape included (GM 2026-08-30). Nothing about
# what this guard refuses changes.
NB_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$NB_HERE/_guardlog.sh"
# GUARD_EDIT_OK: feature 169 - an INVOCATION, not a mention; feature 170 - and it must say WHY.
# `escape_or_refuse` records the reason and permits, or refuses a bare token; it returns 1 when no
# escape was used, which is why this is an `if` and not a bare call.
if escape_or_refuse no-branch NO_BRANCH_OK no-branch-ok "$NB_HERE"; then exit 0; fi

# Only branch CREATION. Switching to an existing branch, listing, and deleting are all fine - a
# session cleaning up someone's leftover branch must not be blocked from doing it.
creates_branch=false
case "$CMD" in
  *"git checkout -b"*|*"git checkout -B"*) creates_branch=true ;;
  *"git switch -c"*|*"git switch -C"*)     creates_branch=true ;;
  *"git switch --create"*)                 creates_branch=true ;;
  *"git checkout --branch"*)               creates_branch=true ;;
esac
$creates_branch || exit 0

# Scoped to this project: a session may legitimately branch in some other repo it is helping with.
case "$CMD" in
  */host-l7r-repo*) exit 0 ;;
esac

echo "BLOCKED (no-branch): this project does not use feature branches - not even for spec-kit.

Isolation already comes from your session CLONE (.clones/<session-name>); a branch on top of it is a
second axis of isolation that buys nothing. It also broke the stop-work procedure for a whole session:
sync-with-main.sh pushed the local ref NAMED main instead of HEAD, so work committed on a branch was
rejected as non-fast-forward while every diagnostic reported it strictly ahead.

Do this instead:
  - Ordinary work: just commit on main inside your clone. That is what sync-with-main.sh done expects.
  - Spec-kit: export SPECIFY_FEATURE=NNN-slug   (common.sh get_current_branch() returns it ahead of
    git, so check_feature_branch() in setup-plan.sh / setup-tasks.sh passes with no branch at all).
    Branch creation is already off - .specify/extensions.yml, before_specify, enabled: false.

If you genuinely need a branch (a throwaway bisect, recovering another session's work), put
NO_BRANCH_OK in the command with a note saying why.

(scripts/no-branch-hooks.sh; GM 2026-07-27)" >&2
guard_log no-branch blocked "$(guard_cmd)" branch-creation   # GUARD_EDIT_OK: feature 168
exit 2
