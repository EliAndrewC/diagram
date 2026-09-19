#!/bin/bash
# agent-model-hooks.sh - an AD-HOC agent dispatch names its model, or is refused (feature 252).
# GUARD_EDIT_OK: feature 252 - a NEW guard, the GM's choice of 2026-09-19.
#
# THE FAILURE. An Agent dispatch of a type with no file under `.claude/agents/` (`general-purpose`,
# `claude`, `Explore`, `Plan`, an omitted type) that carries no `model` runs on the SESSION's model.
# Feature 251's census found 72 such runs, 62 of them on Fable - the model the GM said is "simply not
# sufficiently available" - while every NAMED check had its model pinned by a test. Nothing warned.
#
# WHY A REFUSAL AND NOT A DEFAULT. This project's guards correct where they can and refuse only for a
# destructive action or "a decision only the session can supply" (root CLAUDE.md). Which model fits is
# that decision: `sonnet` reads, fetches, translates and extracts; `opus` judges; only the caller knows
# which it is about to ask for. The GM, asked to choose between a hook that fills in a default and a
# written rule: *"isn't there a fourth option, which is to have the hook reject it with a message saying
# that the caller has to specify a model and then reiterating the rules around what should be selected?
# That does seem better because the caller can then make a choice based on those things"*. So: exit 2,
# and the message IS the rule, read from `agent-model-rule.txt` beside this file so it is stated once.
#
# WHAT PASSES. A type that HAS an agent file (its file pins its tier; `tests/test_agent_models.py` holds
# it to that). Any dispatch that names a model - the choice is the caller's, whatever it is. And `fork`:
# a fork always runs on its parent's model and the harness ignores a `model` on it, so refusing one would
# demand a field that changes nothing; it is RECORDED instead, so `make audit` shows that spend.
#
# NO ESCAPE TOKEN: the compliant dispatch is always available and is one field.
#
# Modes:
#   pretool (PreToolUse, Agent)   refuse / pass, recorded
set -uo pipefail

MODE=${1:-}
AM_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
. "$AM_HERE/_guardlog.sh"

pretool() {
  local clone fields tool atype model cwd root
  INPUT="$(cat)"   # the firing log resolves the session's name from INPUT
  fields="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = p.get("tool_input") or {}
# GUARD_EDIT_OK: feature 252 - a unit separator, not a tab: `read` collapses WHITESPACE separators, and
# the model field is usually EMPTY, which shifted the working directory into it and passed the dispatch.
print("\x1f".join(str(v).replace("\x1f", " ").replace("\n", " ") for v in (p.get("tool_name") or "", ti.get("subagent_type") or "general-purpose", ti.get("model") or "", p.get("cwd") or "")))
' 2>/dev/null)" || exit 0
  IFS=$'\x1f' read -r tool atype model cwd <<<"$fields"
  [ "$tool" = "Agent" ] || exit 0
  if [ "$atype" = "fork" ]; then
    guard_log agent-model permitted "a fork runs on its parent's model; a model on it is ignored" fork-inherits
    exit 0
  fi
  if [ -n "$model" ]; then
    guard_log agent-model permitted "$atype on $model" model-named
    exit 0
  fi
  clone="$(printf '%s' "$INPUT" | "$AM_HERE/clone-sync-hooks.sh" resolve 2>/dev/null | tail -1)"
  root="$clone"
  [ -n "$root" ] && [ -d "$root" ] || root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)"
  [ -n "$root" ] || root="$(dirname "$AM_HERE")"
  if [ -f "$root/.claude/agents/$atype.md" ]; then
    guard_log agent-model permitted "$atype pins its tier in its file" pinned-type
    exit 0
  fi
  guard_log agent-model blocked "$atype dispatched with no model" no-model
  {
    printf '\n\033[1mBLOCKED: this `%s` agent names no model, so it would run on the SESSION'"'"'s model.\033[0m\n' "$atype"
    cat "$AM_HERE/agent-model-rule.txt"
    printf '\n(scripts/agent-model-hooks.sh; feature 252, the GM 2026-09-19)\n'
  } >&2
  exit 2
}

case "$MODE" in
  pretool) pretool ;;
  *) echo "agent-model-hooks: unknown mode '$MODE' (want: pretool)" >&2; exit 1 ;;
esac
