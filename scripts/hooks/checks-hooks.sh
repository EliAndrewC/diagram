#!/usr/bin/env bash
# checks-hooks.sh - the record checks in flight: each launch and each return (feature 375, FR-003(b)(c), plan D4).
# (GUARD_EDIT_OK: a NEW hook - it records the state that the freeze in record-edit-hooks.sh and the round rule in
# check-bundle-hooks.sh read; it never refuses.)
#
# A check is dispatched at PreToolUse (check-bundle-hooks.sh records it PENDING); its launch is seen here at
# PostToolUse(Agent), which pairs the call's tool_use_id with the agent id the harness gave it, and its return at
# SubagentStop, which carries the same agent id and the agent's last message - whose EDIT blocks are what the apply pass may
# write. Measured before it was built: specs/375-enforced-wave-process/measurements.json `subagent-stop-probe`.
#
# Modes:
#   launched (PostToolUse, Agent)
#   returned (SubagentStop)
CH_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  launched|returned) python3 "$CH_HERE/lib/hm_checks.py" "$1" >/dev/null 2>&1 ;;
  *) echo "usage: checks-hooks.sh launched|returned" >&2; exit 64 ;;
esac
exit 0
