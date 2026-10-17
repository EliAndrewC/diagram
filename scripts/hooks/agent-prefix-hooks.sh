#!/bin/bash
# agent-prefix-hooks.sh - an Agent prompt that shares a large block with an earlier dispatch of its type, after a part that
# differs, is refused: that block is written to the prompt cache fresh every time (feature 383 amendment 6, FR-034).
# GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard, the GM 2026-10-17: "I want to both make sure that we are doing the
# correct thing here and that there are some kind of project guidelines that enforce this".
#
# The decision and its why are `lib/hm_agent_prefix.py`. The fix is always available: put the shared text FIRST in the prompt,
# or - better, for a check dispatched again and again - in the agent's own file, which is its system prompt.
# Escape: `AGENT_PREFIX_OK: <reason>` in the prompt (two words or more), recorded.
#
# Modes:
#   pretool (PreToolUse, Agent)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
AP_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$AP_HERE/lib/guardlog.sh"

pretool() {
  local cwd gitdir got
  INPUT="$(cat)"
  cwd="$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd") or "")
except Exception: pass' 2>/dev/null)"
  gitdir="$(git -C "${cwd:-.}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
  [ -n "$gitdir" ] || exit 0
  got="$(printf '%s' "$INPUT" | python3 "$AP_HERE/lib/hm_agent_prefix.py" "$gitdir" 2>/dev/null)" || exit 0
  [ -z "$got" ] && exit 0
  if [ "$got" = "ESCAPED" ]; then  # the decider read the escape from the prompt; no substring test here
    guard_log agent-prefix escaped "a shared block after a differing part, with a reason" escape
    exit 0
  fi
  guard_log agent-prefix blocked "$got" shared-after-difference
  {
    printf '\n\033[1mBLOCKED: %s.\033[0m\n' "$got"
    printf 'A prompt is cached as a PREFIX: everything after the first character that differs from the earlier dispatch is written\n'
    printf 'to the cache fresh, so this block is paid for in full on every dispatch (the GM 2026-10-17). Fix it one of two ways:\n'
    printf '  - put the shared text at the START of the prompt and the part that differs after it, or\n'
    printf '  - for a check dispatched again and again, move the shared text into its agent file (.claude/agents/<name>.md),\n'
    printf '    which is its system prompt; a bundle then carries only what is particular to its unit.\n'
    printf 'If this shape is right here: AGENT_PREFIX_OK: <reason> in the prompt.\n'
    printf '(scripts/hooks/agent-prefix-hooks.sh; feature 383 amendment 6; `make subagent-cache` measures it)\n'
  } >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "agent-prefix-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
