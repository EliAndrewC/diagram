#!/usr/bin/env bash
# guard-shim.sh - a guard's suite drives the Rust guard as it drove the shell (feature 449 plan D4, T006 decision (d)).
#
# Each suite calls `"$HOOK" <mode>` with the hook input on stdin. A link named for a ported guard - `tests/hooks/<guard>.sh` ->
# `guard-shim.sh`, standing where the suite's own path arithmetic (`$(dirname "$HOOK")/../..`) still reaches the repository - runs
# `l7r-guard --only <guard> <event>` through the wrapper, which builds the binary from this tree when its sources are newer. So the
# suite's cases replay unchanged against the Rust decider, and `make hooks-test` finds a ported guard by its link.
set -uo pipefail
guard=${0##*/}
guard=${guard%.sh}
case "${1:-}" in
  pretool) event=PreToolUse ;;
  posttool) event=PostToolUse ;;
  stop) event=Stop ;;
  prompt) event=UserPromptSubmit ;;
  *) event=${1:-} ;;
esac
here=${BASH_SOURCE[0]%/*}
case "$here" in /*) ;; *) here="$(cd "$here" && pwd)" ;; esac
exec "${here%/tests/hooks}/scripts/hooks/l7r-guard.sh" --only "$guard" "$event"
