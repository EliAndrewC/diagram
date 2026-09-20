#!/bin/bash
# record-edit-hooks.sh - an edit aimed at an ASSEMBLED record page goes to its fragment (feature 258).
# GUARD_EDIT_OK: feature 258 - a NEW guard, spec FR-028.
#
# THE FAILURE IT CLOSES. Since feature 258 the record's pages are assembled from per-entry fragments
# under `research/<page>/`. An edit that landed in a page instead would be undone by the next
# `make record`, silently, while the fragment every session and every checking agent reads still said
# the old thing. The gate and the push refuse a page that has drifted; this refuses the edit that
# would drift it, one round trip earlier.
#
# REWRITE FIRST, REFUSE ONLY WHERE A CHOICE IS OWED (feature 164's ladder). An Edit whose `old_string`
# stands in exactly ONE fragment is re-aimed at that fragment - which is where the session meant to put
# it - and told to run `make record`. Two cases refuse, both decisions a guard cannot make: text in no
# fragment or in several, and a whole-file Write, which cannot be routed.
#
# NO ESCAPE TOKEN: the compliant edit is always available, and the guard hands it to you.
#
# Modes:
#   pretool (PreToolUse, Edit|Write)   rewrite / refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
RE_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$RE_HERE/_guardlog.sh"

pretool() {
  local verdict rule
  INPUT="$(cat)"
  verdict="$(printf '%s' "$INPUT" | python3 "$RE_HERE/_hm_record.py" 2>/dev/null)" || exit 0
  case "$verdict" in
    *'"verdict": "rewrite"'*)
      printf '%s' "$verdict" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["hook"]))'
      guard_log record-edit rewrote "edit" edit-moved-to-fragment "$verdict"
      exit 0
      ;;
    *'"verdict": "refuse"'*)
      printf '%s' "$verdict" | python3 -c 'import json,sys; print("BLOCKED: " + json.load(sys.stdin)["message"], file=sys.stderr)'
      printf '%s\n' "(scripts/record-edit-hooks.sh; feature 258, spec FR-028)" >&2
      rule="$(printf '%s' "$verdict" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("rule","record-edit"))')"
      guard_log record-edit blocked "edit" "$rule" "$verdict"
      exit 2
      ;;
  esac
  exit 0
}

case "$MODE" in
  pretool) pretool ;;
  --selftest) python3 "$RE_HERE/_hm_record.py" --selftest ;;
  *) echo "usage: record-edit-hooks.sh pretool|--selftest" >&2; exit 64 ;;
esac
