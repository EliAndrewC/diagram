#!/usr/bin/env bash
# blocked-fetch-hooks.sh - a Claude Code PreToolUse hook on WebFetch and Bash (feature 312, FR-002, FR-017, FR-018).
# GUARD_EDIT_OK: feature 312 FR-002 - a NEW guard: a blocked domain is refused at every fetch route outside Python.
#
# WHY (the GM, 2026-10-02): *"we should definitely make sure that our citation rules are enforced by tooling and not just
# remembering to do the correct thing. Like if we can literally block ourselves from even checking Grokopedia, that's
# good"*, then *"I accept your recommendation about blocking Grokopedia entirely"*. The Python routes ask
# `record/blocked.py` themselves; this hook covers what Python never sees - an agent's WebFetch and a shell fetch
# (`curl`, `wget`, ...) - and a make fetch target before it starts.
#
# AND IT RECORDS (FR-017, FR-018): every other WebFetch or shell fetch is an attempt on the clone's attempts log (what
# was sought: the prompt, or the command), and the URL's earlier attempts and the filter's verdict come back as
# context, so the reader sees what was tried before. Nothing is ever refused for having been tried.
#
# ESCAPE: none, deliberately - the GM ruled the domain blocked across the board, and a blocked page's facts are found
# on another page. A domain leaves the list only by the GM's edit of `research/blocked-domains.json`.
#
# DECISION: `_hm_fetch.py` (what is a fetch, which URL it names). The bash filter below only keeps python off the
# commands that cannot be a fetch.
set -uo pipefail

MODE=${1:-}
BF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pretool() {
  local out decision
  INPUT="$(cat)"
  case "$INPUT" in
    *'"tool_name": "WebFetch"'*|*'"tool_name":"WebFetch"'*) ;;
    *curl*|*wget*|*lynx*|*w3m*|*xh\ *|*http\ *|*https\ *|*urllib*|*source-pages*|*archive*|*reserve*|*source-outcome*|*quote-verbatim*) ;;
    *) exit 0 ;;
  esac
  out="$(printf '%s' "$INPUT" | python3 "$BF_HERE/_hm_fetch.py" 2>/dev/null)" || exit 0
  decision="$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("decision","pass"))' 2>/dev/null)"
  if [ "$decision" = block ]; then
    # shellcheck source=/dev/null
    . "$BF_HERE/_guardlog.sh"
    guard_log blocked-fetch blocked "$(guard_cmd)" blocked-domain
    printf '%s' "$out" | python3 -c 'import json,sys; print("BLOCKED: " + json.load(sys.stdin)["message"])' >&2
    exit 2
  fi
  printf '%s' "$out" | python3 -c '
import json, sys
c = json.load(sys.stdin).get("context", "")
if c:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": c}}))
' 2>/dev/null
  exit 0
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "blocked-fetch-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
