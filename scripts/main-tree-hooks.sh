#!/usr/bin/env bash
# main-tree-hooks.sh - a write that would LAND in the MIRROR is moved to the session's clone; one that
# NAMES the mirror is refused (feature 169, reworked by feature 204).
# (GUARD_EDIT_OK: feature 204 - the guard refused 173 commands in a week and 171 of them were correct work.)
#
# THE HISTORY, because the verdict changed shape and a reader deserves to know why. Feature 169 built
# this for one incident: on 2026-08-30, twice in one day, a session ran a bare `cd /diagram` for a
# read, the cd leaked into the next command exactly as CLAUDE.md's "NAME THE TREE IN THE COMMAND"
# warns, and the session COMMITTED in the mirror - a commit on no branch anywhere, which blocked every
# clean clone in the container until someone worked out what had happened. Feature 170 then taught it
# that the real incident puts the cd in one command and the write in the NEXT, so it began refusing any
# write-shaped command while the payload's cwd was in main; 172 and 177 patched the false positives
# that produced (a cd OUT of main, `2>/dev/null`, the subshell form its own message recommends).
#
# THE CENSUS THAT REWROTE IT (feature 204, GM 2026-09-07: *"I keep seeing this error pop up ... I
# wonder if there is a better outcome"*). All 173 refusals from 2026-08-30 to 2026-09-07, recovered
# with their full commands from the session transcripts: TWO were `git commit`; 146 had
# no `cd` at all - a subagent whose shell started in the mirror (a session's cwd IS /diagram until it
# cds out) writing to the scratchpad or to a clone by absolute path; 127 of the 173 were subagents'.
# Not one named a write inside main by its path. The 16 escapes all misdiagnosed the cause, because
# the refusal said "this command cds into /diagram" when it had not. So the question this guard asks
# changed from "where does the shell stand" to "where does the write LAND":
#
#   git -C /diagram commit             -> REFUSED (names main; a guard never guesses at that)
#   cd /diagram && git commit          -> REWRITTEN: cd <clone> && git commit, and the session is told
#   git commit          (cwd /diagram) -> REWRITTEN: cd <clone> && git commit
#   cat > /tmp/x        (cwd /diagram) -> allowed, silently (the write lands in /tmp)
#   C=<clone>; git -C $C rm x  (cwd /diagram) -> allowed (the variable is read from the command)
#   ( cd <clone> && make quick )       -> allowed
#   cd /diagram && git log             -> allowed (a read)
#
# The verdict is `_hm_tree.py judge` - the effective directory walked through the command's own cds,
# variables and subshells, every write classified by where it lands, and every REWRITE re-judged
# before it is emitted so this guard never returns a command it would itself refuse. The rewrite is
# what moves the shell (spec D4): `cd <clone>` is prepended, so the persisted cwd ends in the clone
# and the leak the guard exists for is cured for the following commands, not just this one. The
# corpus is `scripts/fixtures/main-tree-refusals-2026-09.json`; the companion suite replays it.
#
# Render-sync is the one legitimate write in main, and it runs through `sync-with-main.sh`, which
# names the tree with `git -C` and never cds. ESCAPE: MAIN_TREE_OK with a reason - matched as an
# INVOCATION through `_hm_escape.py` (feature 169's own rule), and recorded like every other branch.
#
# What this guard is NOT (unchanged since 169): the 2026-08-17 rule that a bare `cd` into main for a
# READ is a mislabeling hazard was priced by the GM and DECLINED as unenforceable; this guard excludes
# read-only commands by construction and does not reopen that decision.
set -uo pipefail
[ "${1:-}" = "pretool" ] || exit 0
INPUT=$(cat 2>/dev/null || true)
MT_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception: pass' 2>/dev/null)
[ -n "$CMD" ] || exit 0

# shellcheck source=/dev/null
. "$MT_HERE/_guardlog.sh"

# THE ESCAPE IS CHECKED FIRST (CLAUDE.md: a guard that cannot be repaired through the channel it
# guards is a worse defect than the one it prevents).
if escape_or_refuse main-tree MAIN_TREE_OK main-tree-ok "$MT_HERE"; then exit 0; fi

# THE MIRROR ROOT IS DERIVED FROM GIT, never hardcoded (feature 131 moved this repository once
# already, and every guard here derives its root). From a clone, main is two levels up from
# `.clones/<name>`; from main itself it is the toplevel.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
case "$ROOT" in
  */.clones/*) MAIN=${ROOT%/.clones/*} ;;
  *)           MAIN=$ROOT ;;
esac
[ -n "$MAIN" ] || exit 0

# ONE python start on the common path: judge without a clone. `allow` is by far the commonest verdict
# and it costs exactly this; the clone is resolved only when a write would land in main.
VERDICT=$(printf '%s' "$INPUT" | "$MT_HERE/_hm_tree.py" judge "$MAIN" 2>/dev/null) || exit 0
case "$VERDICT" in
  *'"verdict": "allow"'*) exit 0 ;;
  *'"verdict": "needs-clone"'*)
    # THIS SESSION'S CLONE, from the same resolver clone-sync uses (feature 204 FR-011): the claim map
    # first, then the transcript's last /rename, then the sessions json. A SUBAGENT's payload carries
    # its parent's session_id, so it resolves to the parent's clone - measured, and proved by the
    # clone-sync suite, because the wrong answer here writes one session's work into another's tree.
    CLONE=$(printf '%s' "$INPUT" | "$MT_HERE/clone-sync-hooks.sh" resolve 2>/dev/null | tail -1 || true)
    VERDICT=$(printf '%s' "$INPUT" | "$MT_HERE/_hm_tree.py" judge "$MAIN" "$CLONE" 2>/dev/null) || exit 0
    ;;
esac

case "$VERDICT" in
  *'"verdict": "rewrite"'*)
    # A `PreToolUse` hook may return `updatedInput` (the command the session actually runs) and
    # `additionalContext` (a line the model reads), both at exit 0 and both free (feature 164's
    # ladder: REWRITE where the guard can produce the compliant command; a refusal costs a round trip).
    printf '%s' "$VERDICT" | "$MT_HERE/_hm_tree.py" hook
    guard_log main-tree rewrote "$(guard_cmd)" moved-to-clone "$(printf '%s' "$VERDICT" | "$MT_HERE/_hm_tree.py" log-context)"
    exit 0
    ;;
esac

# REFUSED - and the text names the ACTUAL cause (FR-007): standing in main, a cd into main, or a path
# that names main, because the old text named the second in all three cases and every recorded escape
# misread it.
printf '%s' "$VERDICT" | "$MT_HERE/_hm_tree.py" explain "$MAIN" >&2
RULE=$(printf '%s' "$VERDICT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("reason", "write-in-mirror"))' 2>/dev/null || echo write-in-mirror)
guard_log main-tree blocked "$(guard_cmd)" "$RULE" "$(printf '%s' "$VERDICT" | "$MT_HERE/_hm_tree.py" log-context)"
exit 2
