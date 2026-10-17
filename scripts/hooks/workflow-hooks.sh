#!/bin/bash
# workflow-hooks.sh - a Workflow call is held to the guards its agents would meet as Agent calls (feature 383 amendment 7,
# FR-045, plan D48): no hook of the Agent tool fires for an agent a workflow spawns (research R20).
# GUARD_EDIT_OK: feature 383 amendment 7 - a NEW guard, the GM 2026-10-17: "please take a look at that and then implement its
# recommendations".
#
# The decision and its why are `lib/hm_workflow.py`: an untyped `agent(` is refused (escape `GP_OK: <reason>` in the script);
# a defined agent of this project runs through the saved `check-wave` workflow, whose every unit is put through the Agent hooks.
# WORKFLOW_SETTINGS (tests) names the settings file whose Agent hooks a unit meets; else the project's own.
#
# Modes:
#   pretool (PreToolUse, Workflow)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
WF_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$WF_HERE/lib/guardlog.sh"

pretool() {
  local cwd root settings got kind
  INPUT="$(cat)"
  cwd="$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd") or "")
except Exception: pass' 2>/dev/null)"
  root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)" || exit 0
  settings="${WORKFLOW_SETTINGS:-$root/.claude/settings.json}"
  [ -f "$settings" ] || exit 0
  got="$(printf '%s' "$INPUT" | python3 "$WF_HERE/lib/hm_workflow.py" "$root" "$settings" 2>/dev/null)" || exit 0
  [ -z "$got" ] && exit 0
  if [ "$got" = "WAVE-PASSED" ]; then  # the measurement is named when the wave starts, never remembered (FR-046, plan D50)
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"check-wave: every unit passed the Agent guards. When this run finishes, `make wave-report` measures it - each agent'"'"'s first-request cache read and write, and the main session'"'"'s wakes - against the last hand-launched wave (feature 383 FR-046)."}}\n'
    exit 0
  fi
  if [ "$got" = "ESCAPED" ]; then
    guard_log workflow escaped "an untyped agent() stage, with a reason" escape
    exit 0
  fi
  kind="${got%% *}"
  guard_log workflow blocked "${got%%$'\n'*}" "$(printf '%s' "$kind" | tr 'A-Z' 'a-z')"
  {
    case "$kind" in
      UNTYPED)
        printf '\n\033[1mBLOCKED: an agent() call with no agentType: %s\033[0m\n' "${got#UNTYPED }"
        printf 'A workflow'"'"'s default subagent loads every CLAUDE.md and every tool - ~35k tokens written at its first request,\n'
        printf 'against ~4k for a typed agent whose file omits them (feature 383 research R20). Pass agentType: "<its .claude/agents/ name>"\n'
        printf 'on every agent() call. A deliberate general-purpose stage: GP_OK: <reason> in the script, and name its model.\n' ;;
      MODEL)
        printf '\n\033[1mBLOCKED: an ad-hoc agent() call names no model: %s\033[0m\n' "${got#MODEL }"
        printf 'As an ad-hoc Agent call must (agent-model-hooks.sh): model: "sonnet" to read, fetch, translate or extract, "opus" for\n'
        printf 'anything that judges.\n' ;;
      GUARDED)
        printf '\n\033[1mBLOCKED: `%s` runs through the check-wave workflow, not a script of its own.\033[0m\n' "${got#GUARDED }"
        printf 'No Agent hook fires inside a workflow, so a defined check is held to its guards (bundle, owed, freeze, round caps,\n'
        printf 'decide-first) only when its units are known before the run - as check-wave'"'"'s args are:\n'
        printf '  Workflow({name: "check-wave", args: {agentType: "<job>", units: [{label: "<unit>", prompt: "<its prompt>"}, ...]}})\n'
        printf 'An agentType computed at run time is refused the same way: name it literally.\n' ;;
      UNIT)
        printf '\n\033[1mBLOCKED: check-wave unit %s - a guard of its type refused it:\033[0m\n' "$(printf '%s' "${got#UNIT }" | head -1)"
        printf '%s\n' "$(printf '%s' "$got" | tail -n +2)"
        printf 'The whole wave is refused: fix or drop that unit, and run check-wave again.\n' ;;
      *)
        printf '\n\033[1mBLOCKED: %s\033[0m\n' "${got#* }" ;;
    esac
    printf '(scripts/hooks/workflow-hooks.sh; feature 383 amendment 7)\n'
  } >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) exit 0 ;;
esac
