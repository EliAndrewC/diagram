#!/usr/bin/env bash
# main-tree-hooks.sh - a `cd` into the MIRROR ROOT that then WRITES is refused (feature 169).
# (GUARD_EDIT_OK: a NEW guard.)
#
# WHAT THIS IS, STATED HONESTLY. `CLAUDE.md`'s "NAME THE TREE IN THE COMMAND" rule (2026-08-17) is
# about a different failure - a read-only diagnostic that confidently reports the WRONG TREE, which
# is worse than an error because it looks like an answer - and the GM priced a hook for that and
# DECLINED it, because the only mechanisms anyone could design fired on nearly every correct command.
# **This guard does not meet that rule's reopening condition and does not replace it.** It excludes
# read-only commands by construction, and it cannot see a section header, which is where the
# mislabeling lives. That rule remains deliberately unenforced.
#
# What this guard IS: the WRITE half, which nothing catches today. Writing in main is supposedly
# caught three ways - `webapp/mainguard.py`, the Makefile's `guard`, and
# `settlement._assert_not_main_tree` - and not one of them sees a `git commit`. So on 2026-08-30,
# twice in one day, a session ran a bare `cd /diagram` for a read, the cd leaked into the next
# command exactly as CLAUDE.md warns, and the session edited and COMMITTED in the mirror. Each time
# the commit existed on no branch anywhere else; each time it blocked EVERY clean clone in the
# container on the stale-base check, and sent them all at a `sync-in` that could not fix it. Cost of
# the second: two sessions, ~20 minutes.
#
# THE SHAPE, deliberately narrow - a command that BOTH enters the mirror root AND writes:
#   cd /diagram && vim x        -> refused        cd /diagram && git log        -> allowed (read)
#   cd /diagram; git commit -am -> refused        git -C /diagram log           -> allowed (no cd)
#   cd /diagram/.clones/x && .. -> allowed (a clone is a workspace; only the ROOT is guarded)
#
# Render-sync is the one legitimate write in main, and it runs through `sync-with-main.sh`, which
# names the tree with `git -C` and never cds. ESCAPE: MAIN_TREE_OK with a reason - matched as an
# INVOCATION through `_hookmatch.py` (feature 169's own rule: a guard's escape means a session
# escaped, never that a command mentioned a token), and recorded like every other branch.
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
if [ -n "$(printf '%s' "$INPUT" | "$MT_HERE/_hookmatch.py" escape MAIN_TREE_OK 2>/dev/null)" ]; then
  guard_log main-tree escaped "$(guard_cmd)" main-tree-ok
  exit 0
fi

# THE MIRROR ROOT IS DERIVED FROM GIT, never hardcoded (feature 131 moved this repository once
# already, and every guard here derives its root). From a clone, main is two levels up from
# `.clones/<name>`; from main itself it is the toplevel.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
case "$ROOT" in
  */.clones/*) MAIN=${ROOT%/.clones/*} ;;
  *)           MAIN=$ROOT ;;
esac
[ -n "$MAIN" ] || exit 0

# Does the command cd INTO the mirror root itself? Not a clone under it, and not a read of a path.
# `_hookmatch.py sanitize` blanks heredoc bodies and quoted strings first, so a `cd /diagram` inside
# a commit message or a document is a MENTION - the rule this whole feature is about.
SCAN=$(printf '%s' "$INPUT" | "$MT_HERE/_hookmatch.py" sanitize 2>/dev/null || printf '%s' "$CMD")
printf '%s' "$SCAN" | grep -qE "(^|[;&|]|&&)[[:space:]]*cd[[:space:]]+\"?${MAIN}/?\"?([[:space:]]*(;|&&|\||$))" || exit 0

# ...and does it then WRITE? A read in main is legitimate and stays legitimate.
WRITES='git[[:space:]]+(commit|add|merge|rebase|reset|checkout|restore|rm|mv|apply|am|stash|cherry-pick|push|pull|clean|tag|branch[[:space:]]+-)'
WRITES="$WRITES|(^|[[:space:]])(vim|vi|nano|emacs|sed[[:space:]]+-i|tee|touch|mkdir|rmdir|rm|mv|cp|chmod|chown|ln|truncate|install)[[:space:]]"
WRITES="$WRITES|>[^&]|>>|python3?[[:space:]]+-c|make[[:space:]]"
printf '%s' "$SCAN" | grep -qE "$WRITES" || exit 0

cat >&2 <<TAIL
BLOCKED: this command cds into $MAIN - the MIRROR, which is main's tree - and then writes there.

Main is the integration point, never a workspace. The only thing a session runs in it is render-sync,
and that names the tree with \`git -C\` rather than cd-ing into it.

This is the leak CLAUDE.md warns about under "NAME THE TREE IN THE COMMAND": a bare \`cd\` persists
for the REST of the command and into the NEXT Bash call, so a block that opens with a read in main
silently answers about main for everything after it. On 2026-08-30 that happened twice in one day,
and both times the session committed its work into the mirror, where it existed on no branch at all
and blocked every other clone in the container until someone worked out what had happened.

Do this instead:
  - \`git -C $MAIN <read>\` for anything you want to KNOW about main - no cd, and the tree is named in
    the command text, so a mislabeled section header cannot survive a re-read of what you ran;
  - \`( cd <your clone> && ... )\` in a subshell for anything you want to DO.

If this genuinely needs to write in main, put MAIN_TREE_OK in the command with the reason, and the
reason ships with it.

(scripts/main-tree-hooks.sh; feature 169)
TAIL
guard_log main-tree blocked "$(guard_cmd)" write-in-mirror
exit 2
