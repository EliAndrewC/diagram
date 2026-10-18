#!/bin/bash
# agent-prefix-hooks.sh - an Agent prompt that repeats a large block of an earlier dispatch of its type is refused, wherever the
# block sits: only the agent file is reused across launches (feature 383 amendment 6, FR-034, research R16); and a 4th launch of one
# type within seconds goes through the check-wave workflow instead (amendment 7, FR-045).
# GUARD_EDIT_OK: feature 383 amendment 6 - a NEW guard, the GM 2026-10-17: "I want to both make sure that we are doing the
# correct thing here and that there are some kind of project guidelines that enforce this".
#
# The decision and its why are `lib/hm_agent_prefix.py`. The fix is always available: move the shared text into the agent's own
# file, its system prompt; for a wave of 4 or more, the check-wave workflow.
# Escapes: `AGENT_PREFIX_OK: <reason>` (a repeated block), `WAVE_OK: <reason>` (a hand-launched wave), in the prompt, recorded.
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
    WAVE*)
      kind="${got#WAVE }"
      guard_log agent-prefix blocked "a 4th $kind launch within seconds" wave
      {
        printf '\n\033[1mBLOCKED: a 4th `%s` launch within seconds - a wave goes through the check-wave workflow.\033[0m\n' "$kind"
        printf 'Every agent launched by hand wakes the main session when it finishes, and each wake re-reads its whole context\n'
        printf '(5,544 wakes a month, a median 405k tokens each - feature 383 research R20). A workflow staggers the launches by itself\n'
        printf 'and wakes the session once, and its guard holds each unit to every check this one would have:\n'
        # GUARD_EDIT_OK: feature 385 T58 (the round arbiter's fix on hour:385-approach-checklist@21) - A HEADLESS SESSION HAS NO
        # WORKFLOW TOOL: a queued page session (`L7R_DISPATCHER`, page_session_runner.headless_env) was pointed at Workflow(...) it
        # lacks, refused twice, and relaunched by hand; it is told its one route
        if [ -n "${L7R_DISPATCHER:-}" ]; then
          printf 'This session has no Workflow tool (a headless page session): put WAVE_OK: <reason> in each prompt of the batch.\n'
        elif python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import hm_workflow; sys.exit(sys.argv[2] not in hm_workflow.WAVE_JOBS)' "$AP_HERE/lib" "$kind" 2>/dev/null; then
          printf '  Workflow({name: "check-wave", args: {agentType: "%s", units: [{label: "<unit>", prompt: "<its prompt>"}, ...]}})\n' "$kind"
          printf 'Two or three of a type stay plain Agent calls. If this batch must stay hand-launched: WAVE_OK: <reason> in the prompt.\n'
        else
          printf '`%s` is not one of check-wave'"'"'s authorized jobs, so that route is closed to it: send at most three now and the\n' "$kind"
          printf 'rest in the next message, or, if this batch must go together: WAVE_OK: <reason> in the prompt.\n'
        fi
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
