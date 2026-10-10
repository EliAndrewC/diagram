#!/usr/bin/env bash
# feature-approval-hooks.sh - BLOCK a `git add` or `git commit` that would stage a NEW spec-kit feature the GM did not
# approve. (GUARD_EDIT_OK: feature 377 - a NEW guard, the GM's instruction 2026-10-10.)
#
# WHY (the GM, 2026-10-10, specs/377-feature-filing-needs-approval/request.md): "I have had problems where past Claude
# Code sessions have seen that there was work to be done, and then without asking me, filing a [spec-kit] feature for
# it, and then maybe they told me, but they told me in the middle of like two days worth of scrolling text ... So I
# think that spec kit features should not be filed without my explicit approval ... can't be committed at all, like not
# even to a branch, because why are you even putting it in a branch if I didn't say to make it?"
#
# THE RULE: the spec.md of a NEW feature numbered 377 or above carries
#     **Approved**: the GM, YYYY-MM-DD, "<the GM's words, verbatim>"
# and the quote (three words or more) is in a message the GM typed in THIS session, or in the GM's answer to an
# AskUserQuestion. The decider, and the one definition of the line, is lib/hm_approval.py; spec-lint's check 6 re-checks
# the form at the push for what this cannot see (a commit outside a session, or inside a make target or script).
#
# WHY AT THE COMMIT, IN A SESSION HOOK, not a git pre-commit hook: only a session hook can read the transcript, which is
# what makes the approval the GM's words rather than a line a session typed (spec D2). Features below 377 are never
# checked ("only be with new features um, going forward"); an edit to an existing feature, or a renumber, is not new.
#
# ESCAPE: none, deliberately (spec FR-006). The GM's approval is the way through.
#
# Wired from .claude/settings.json beside conflict-marker-hooks.sh. Tested by test-feature-approval-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0

# the cheap bail-out (plan D6), no wider than the parser: a git add or commit, and a spec directory somewhere near it
case "$INPUT" in *git*) ;; *) exit 0 ;; esac
case "$INPUT" in *add*|*commit*) ;; *) exit 0 ;; esac

FA_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAD=$(printf '%s' "$INPUT" | FA_CWD="$PWD" python3 "$FA_HERE/lib/hm_approval.py" judge 2>/dev/null || true)
[ -n "$BAD" ] || exit 0

# shellcheck source=/dev/null
. "$FA_HERE/lib/guardlog.sh"
{
  printf '\n\033[1mBLOCKED: this would file a new spec-kit feature without the GM'"'"'s approval.\033[0m\n'
  printf '%s\n' "$BAD" | while IFS=$'\t' read -r why path; do
    case "$why" in
      no-line)   printf '  %s: no approval line\n' "$path" ;;
      short)     printf '  %s: the approval quote is under three words - a bare "yes" approves nothing\n' "$path" ;;
      not-found) printf '  %s: the quoted words are in no message the GM wrote in this session\n' "$path" ;;
      *)         printf '  %s: %s\n' "$path" "$why" ;;
    esac
  done
  printf '\nA feature is filed only when the GM says to (the GM, 2026-10-10). Ask the GM in this session, in your\n'
  printf 'final message rather than mid-stream, and prefer extending and reopening the feature the work came from.\n'
  printf 'Once the GM approves, put their words on a line of its own in the spec.md, verbatim:\n'
  printf '  **Approved**: the GM, %s, "<the GM'"'"'s words, verbatim>"\n' "$(date +%F)"
  printf 'This guard reads the GM'"'"'s own messages in this transcript (a picked AskUserQuestion answer is quoted\n'
  printf 'with its question). There is no escape variable.\n\n'
} >&2
guard_log feature-approval blocked "$(printf '%s' "$BAD" | cut -f1 | sort -u | tr '\n' ' ')" unapproved-feature
exit 2
