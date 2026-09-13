#!/usr/bin/env bash
# house-style-hooks.sh - the two house-style rules that a regex can actually decide.
#
# CLAUDE.md states both project-wide, for EVERYTHING: generated content, prose, docs, specs, skill
# files, tests, comments, and code identifiers.
#
#   1. Hyphens only - no em-dash (U+2014) or en-dash (U+2013), anywhere.
#   2. American spellings, never British ones. The word list is CLAUDE.md's own.
#
# WHY THESE TWO AND NOT THE REST OF THE STYLE GUIDE. They are decidable without judgment. The rules
# next to them are NOT, and enforcing those would be a mistake: "people" has a caste meaning but is
# correct in narrative and vow voice; office-holders are they/them generically but named characters
# keep their pronouns. A hook cannot see voice, and one that fires on correct prose teaches a session
# to bypass every hook - which this project has already paid for.
#
# THE VIOLATIONS ARE REAL, not hypothetical (audit 2026-08-24): `licence` shipped in
# specs/123-lane-web-and-cluster-shape/tasks.md and `centre` in specs/125-lanes-do-not-break/spec.md,
# both against a rule documented project-wide since long before either.
#
# THREE EXEMPTIONS, and all three are load-bearing:
#
#   - THE GM'S OWN WRITING. Never "correct" text inside a <!-- SOURCE: GM NOTES --> block, or in
#     l7r.md, or a direct quotation of either. Their prose is theirs.
#   - A FILE THAT STATES THE RULE quotes the forbidden words by necessity - CLAUDE.md lists every
#     British spelling it forbids. Flagging those would make the rule unwritable.
#   - A QUOTATION OF SOMEONE ELSE'S TEXT (GUARD_EDIT_OK: GM 2026-09-06: *"The house style should not
#     normalize british spellings or em-dashes inside things we are quoting, because that requires us
#     to edit other people's quotes, which I don't think we should do"*). A passage inside 「」, 『』,
#     “” or <q>/<blockquote> anywhere, or inside straight double quotes in a PROSE file (.md/.html/.txt
#     - in code a double-quoted string is a string, and the rule covers code), keeps the source's own
#     characters. Found by feature 194's backfill: the readers' reports recorded a dozen en-dashes and
#     four British spellings hyphenated and Americanized INSIDE verbatim quotes as they were saved.
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0
INPUT=$(cat)

# GUARD_EDIT_OK: feature 236 - the scan itself now needs this directory (it shares `_hm_escape`'s
# search-segment rule rather than writing a second copy of it), so the path is resolved BEFORE the
# scan instead of only before the log.
HS_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export HS_HERE

# GUARD_EDIT_OK: feature 239 FR-001 - THE DECISION IS A FUNCTION NOW. The program that stood here, 275
# lines inside a single-quoted string, is `report()` in `_hm_house.py`, lifted mechanically, so the
# bench can call it in process and an apostrophe in a comment can no longer end it.
REPORT=$(printf '%s' "$INPUT" | python3 "$HS_HERE/_hm_house.py" decide 2>"${TMPDIR:-/tmp}/house-style-$$.err")
STATUS=$?
if [ "$STATUS" -ne 0 ]; then
  # GUARD_EDIT_OK: plan P3 - a decision that cannot run WARNS rather than falling silent. A guard never
  # takes the session down, and it never goes quiet about being down: with the decision in the module,
  # a module that fails to load leaves nothing to act with, so the session is told the guard is off.
  ERR=$(tail -1 "${TMPDIR:-/tmp}/house-style-$$.err" 2>/dev/null | tr -d '"\\' | cut -c1-200)
  rm -f "${TMPDIR:-/tmp}/house-style-$$.err"
  printf '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "The house-style guard could not run (%s) - American spellings and hyphens are NOT being checked on this edit. scripts/_hm_house.py is the decision; fix it before relying on the guard."}}\n' "$ERR"
  exit 0
fi
rm -f "${TMPDIR:-/tmp}/house-style-$$.err"

[ -z "$REPORT" ] && exit 0
# GUARD_EDIT_OK: feature 164 - a JSON verdict is a CORRECTION to pass through, not a report to block on,
# and either way the firing is recorded so `make audit` can price this guard like the others.
# shellcheck source=/dev/null
. "$HS_HERE/_guardlog.sh"
case "$REPORT" in
  # GUARD_EDIT_OK: feature 236 - there are TWO JSON verdicts now, and they are different branches for
  # the audit: a CORRECTION applied to an edit, and a WARNING on a Bash payload that is left as typed.
  '{'*)
    # GUARD_EDIT_OK: feature 236 amendment 2 - a correction now lands on a COMMAND as well as on an
    # edit, and the two are different rules for the audit: the command half is the new one, and
    # "is it correcting the right things" is a question about it alone.
    if printf '%s' "$REPORT" | grep -q '"updatedInput"'; then
      if printf '%s' "$REPORT" | grep -q '"command":'; then
        guard_log house-style rewrote "$(guard_cmd)" corrected-command
      else
        guard_log house-style rewrote "$(guard_cmd)" corrected-edit
      fi
    else
      guard_log house-style warned "$(guard_cmd)" bash-payload
    fi
    printf '%s\n' "$REPORT"; exit 0 ;;
esac
guard_log house-style blocked "$(guard_cmd)"

cat >&2 <<TAIL
BLOCKED: house style ($REPORT).

CLAUDE.md, project-wide and for everything - generated content, prose, docs, specs, tests, comments
and code identifiers alike:

  - HYPHENS ONLY. No em-dash (U+2014), no en-dash (U+2013). Use " - ".
  - AMERICAN SPELLINGS. color, center, gray, honor, judgment, catalog, labeled, behavior, neighbor,
    analyze/organize/recognize, artifact, defense, license, practice, skeptic, story, while,
    traveled, modeled, program, meter, liter, mold, plow, curb, draft, aging, marvelous, jewelry,
    skillful. And "domain", never "demesne".

NOT flagged, deliberately: the GM's own writing (a SOURCE block, l7r.md, or a direct quotation of
either), and the files that must quote the rule to state it.

If this fired on a legitimate quotation of the GM, that is a bug in this hook worth fixing rather
than working around.

(scripts/house-style-hooks.sh; CLAUDE.md "Generation Behavior")
TAIL
exit 2
