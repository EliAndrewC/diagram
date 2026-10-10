#!/usr/bin/env bash
# archive-first-hooks.sh - the FIRST WebFetch of a page the source archive already holds is refused with the archived
# text's path; fetching the same URL again passes. (GUARD_EDIT_OK: feature 376 FR-006, plan D6 - a NEW guard.)
#
# WHY (the GM, 2026-10-10: "search our existing research findings prior to going out and doing new research"; 376's
# research.md R2): since the source archive landed (feature 309), agents fetched 960 pages the archive already held -
# 773 of them quote-check's, 512 of those PDFs read through a model's summary - and ad-hoc agents fetched 14 that
# nothing told them were kept.
#
# THE TWO-STEP is deliberate: the archived copy is the cheap and exact first read, and a second fetch of the same URL by
# the same actor (a session, or one agent of it) is the actor saying it needs the LIVE page - whether a link is still
# public is the live page's question (quote-check's READABLE). The decider is lib/hm_archive_first.py.
#
# ESCAPE: the second fetch itself. Wired from .claude/settings.json on WebFetch. Tested by test-archive-first-hooks.sh.

set -u
MODE="${1:-}"
INPUT=$(cat 2>/dev/null || true)
[ "$MODE" = "pretool" ] || exit 0
case "$INPUT" in *WebFetch*) ;; *) exit 0 ;; esac

AF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GOT=$(printf '%s' "$INPUT" | AF_CWD="$PWD" python3 "$AF_HERE/lib/hm_archive_first.py" judge 2>/dev/null || true)
[ -n "$GOT" ] || exit 0

# shellcheck source=/dev/null
. "$AF_HERE/lib/guardlog.sh"
TEXT=${GOT%%$'\t'*}
WHEN=${GOT#*$'\t'}
{
  printf '\n\033[1mThe source archive already holds this page (captured %s) - read it first:\033[0m\n' "$WHEN"
  printf '  %s\n' "$TEXT"
  printf '\nRead that file (its readable text; a PDF'"'"'s extracted). It is exact where a fetch gives a summary.\n'
  printf 'If you need the LIVE page - is the link still public, has it changed - fetch the same URL again: the second\n'
  printf 'fetch passes. (The GM, 2026-10-10: look at what we have before going out to the web.)\n\n'
} >&2
guard_log archive-first blocked "first-fetch" archived-page
exit 2
