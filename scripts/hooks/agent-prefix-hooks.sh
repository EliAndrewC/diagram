#!/bin/bash
# agent-prefix-hooks.sh - an Agent prompt that repeats a large block of an earlier dispatch of its type is refused, wherever the
# block sits: only the agent file is reused across launches (feature 383 amendment 6, FR-034, research R16); and a fan-out of one
# type launches its first alone (FR-039).
# GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard, the GM 2026-10-17: "I want to both make sure that we are doing the
# correct thing here and that there are some kind of project guidelines that enforce this".
#
# The decision and its why are `lib/hm_agent_prefix.py`. The fix is always available: move the shared text into the agent's own
# file, its system prompt; for a fan-out, send the first and the rest in the next message.
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
  case "$got" in
    FANOUT*)
      guard_log agent-prefix blocked "${got#FANOUT }" fan-out
      {
        printf '\n\033[1mBLOCKED: %s.\033[0m\n' "${got#FANOUT }"
        printf 'A cache entry is readable only once the request that writes it has started, so dispatches of one type sent\n'
        printf 'together each write the shared prefix (the agent file) fresh. Send the FIRST alone - it went out - and the rest in\n'
        printf 'your next message, where they read it from the cache (feature 383 amendment 6, plan D42).\n'
        printf 'If this fan-out is right here: AGENT_PREFIX_OK: <reason> in the prompt.\n'
      } >&2 ;;
    *)
      guard_log agent-prefix blocked "$got" repeated-block
      {
        printf '\n\033[1mBLOCKED: %s.\033[0m\n' "$got"
        printf 'Only a subagent'"'"'s system prompt - its agent file - is reused across launches: its first message, the launch\n'
        printf 'prompt included, has no cache breakpoint, so a block the prompts repeat is written fresh on every dispatch WHEREVER it\n'
        printf 'sits (feature 383 research R16). Move the shared text into the agent file (.claude/agents/<name>.md) - a new defined\n'
        printf 'agent if this is a general-purpose job that recurs - and let the prompt carry only what is particular to the unit.\n'
        printf 'If this shape is right here: AGENT_PREFIX_OK: <reason> in the prompt.\n'
      } >&2 ;;
  esac
  printf '(scripts/hooks/agent-prefix-hooks.sh; feature 383 amendment 6; `make subagent-cache` measures it)\n' >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "agent-prefix-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
