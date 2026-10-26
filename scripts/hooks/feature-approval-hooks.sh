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

# the cheap bail-out (plan D6), no wider than the parser: a git add or commit, or a push through sync-with-main.sh
# (GUARD_EDIT_OK: feature 377 amendment 1 - a new operation, the GM 2026-10-10: a feature reopened and left open is
# judged by what LANDS, so the push is read too)
case "$INPUT" in
  *sync-with-main.sh*) ;;
  *git*) case "$INPUT" in *add*|*commit*) ;; *) exit 0 ;; esac ;;
  *) exit 0 ;;
esac

FA_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAD=$(printf '%s' "$INPUT" | FA_CWD="$PWD" python3 "$FA_HERE/lib/hm_approval.py" judge 2>/dev/null || true)
[ -n "$BAD" ] || exit 0

# shellcheck source=/dev/null
. "$FA_HERE/lib/guardlog.sh"
{
  # GUARD_EDIT_OK: feature 377 amendment 1 - one header for both rules (a new feature, a reopen left open)
  printf '\n\033[1mBLOCKED: this would add a feature with open work the GM has not approved.\033[0m\n'
  printf '%s\n' "$BAD" | while IFS=$'\t' read -r why path; do
    case "$why" in
      no-line)   printf '  %s: no approval line\n' "$path" ;;
      short)     printf '  %s: the approval quote is under three words - a bare "yes" approves nothing\n' "$path" ;;
      not-found) printf '  %s: the quoted words are in no message the GM wrote in this session\n' "$path" ;;
      # GUARD_EDIT_OK: feature 377 amendment 1 - the reopen refusals, new
      reopened)  printf '  %s: closed before, and this push lands it OPEN - finish its work and close it again, or add the GM'"'"'s approval\n' "$path" ;;
      reopened-not-found) printf '  %s: reopened and left open; the approval line it adds quotes words the GM did not write in this session\n' "$path" ;;
      # GUARD_EDIT_OK: feature 377 amendment 1 - FR-012, open work hidden under a closed status, new
      hidden-open) printf '  %s: an unticked task added under a status line that still says closed - speckit-todo would never show it\n' "$path" ;;
      # GUARD_EDIT_OK: feature 377 amendment 1 plan review - FR-012's own not-found wording (its status never changed)
      hidden-open-not-found) printf '  %s: a task added under a closed status; the approval line it adds quotes words the GM did not write in this session\n' "$path" ;;
      *)         printf '  %s: %s\n' "$path" "$why" ;;
    esac
  done
  # GUARD_EDIT_OK: feature 377 amendment 1 - a reopen's refusal names the approval-free route first (FR-011, FR-005)
  # GUARD_EDIT_OK: feature 377 amendment 1 plan review - FR-012's route is "do the work and tick the task"
  case "$BAD" in *reopened*)
    printf '\nReopening a feature to do its work yourself needs no approval: finish the work and close the feature\n'
    printf 'again (status Done, or every task ticked), THEN push. Until then the work stays committed in your clone,\n'
    printf 'backed up by every refused push. Only a feature you mean to land OPEN needs the GM'"'"'s approval below.\n' ;;
  esac
  case "$BAD" in *hidden-open*)
    printf '\nAdding a task under a closed status to do it yourself needs no approval: do the work and tick the task,\n'
    printf 'THEN push. Until then it stays committed in your clone, backed up by every refused push. Only work you mean\n'
    printf 'to land undone needs the GM'"'"'s approval below - and then its status line should say it is open.\n' ;;
  esac
  # GUARD_EDIT_OK: feature 383, the round arbiter's tooling fix on hour:383-tooling-caches-and-hourly-step-back@6 - a command
  # that writes the approval line AND lands in one go is judged on spec.md as it stood BEFORE the command ran
  case "$INPUT" in *spec.md*)
    printf '\nThis command itself touches a spec.md, but the guard judged the file as it stands NOW, before the command\n'
    printf 'runs: an approval line the command would write is not seen. Write and commit the approval line in its own\n'
    printf 'command first, then run the git add / commit / sync-with-main.sh step on its own.\n' ;;
  esac
  # GUARD_EDIT_OK: feature 428 - the GM's 2026-10-18 standing approval of the requests gm-assistant files for him
  case "$BAD" in *not-found*)
    printf '\nAn issue gm-assistant filed for the GM (request.md opens "# Request: EliAndrewC/diagram#N") is approved by\n'
    printf 'his standing words (2026-10-18) - quote them on the line:\n'
    printf '  **Approved**: the GM, 2026-10-18, "you should treat features that I have asked to be filed as automatic approval"\n' ;;
  esac
  printf '\nA feature is filed only when the GM says to (the GM, 2026-10-10). Ask the GM in this session, in your\n'
  printf 'final message rather than mid-stream, and prefer extending and reopening the feature the work came from.\n'
  printf 'Once the GM approves, put their words on a line of its own in the spec.md, verbatim:\n'
  printf '  **Approved**: the GM, %s, "<the GM'"'"'s words, verbatim>"\n' "$(date +%F)"
  printf 'This guard reads the GM'"'"'s own messages in this transcript (a picked AskUserQuestion answer is quoted\n'
  # GUARD_EDIT_OK: feature 377 amendment 1 - the reopen sentence moved up, to the reopen refusal alone
  printf 'with its question). There is no escape variable.\n\n'
} >&2
guard_log feature-approval blocked "$(printf '%s' "$BAD" | cut -f1 | sort -u | tr '\n' ' ')" unapproved-feature
exit 2
