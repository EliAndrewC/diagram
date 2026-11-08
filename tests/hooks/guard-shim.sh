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
# A SUITE MAY MOVE HOME (tests/hooks/parts.sh gives each parallel part its own), and the wrapper finds its built binary and cargo
# under HOME - so a part would build from nothing, past its limit, and fail open (T009, 2026-11-08: 115 of 115 cases green in one
# part, about 90 failing in six). The real home, from the password database, pins both.
real=$(getent passwd "$(id -u)" | cut -d: -f6)
tree=${here%/tests/hooks}
export L7R_GUARD_TARGET="${L7R_GUARD_TARGET:-$real/.cache/l7r-cargo-target/${tree##*/}}"
[ -x "$real/.cargo/bin/cargo" ] && export L7R_GUARD_CARGO="${L7R_GUARD_CARGO:-$real/.cargo/bin/cargo}"
# ...and rustup's own homes, which its cargo proxy reads from HOME to choose a toolchain (T010: a suite that moves HOME left the
# build with "rustup could not choose a version of cargo to run")
export RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}"
# idle-tests' printed stagger is the guard's entry that is no hook event (T014 decision (a))
[ "$event" = stagger ] && exec "$tree/scripts/hooks/l7r-guard.sh" --idle-tests "$@"
# agent-stall's tool modes likewise (T015 decision (a))
# ...and the watchdog's (T016 decision (a))
case "$event" in run|once) exec "$tree/scripts/hooks/l7r-guard.sh" --stall-watchdog "$@" ;; esac
case "$event" in check|watch|pending|ack) exec "$tree/scripts/hooks/l7r-guard.sh" --agent-stall "$@" ;; esac
exec "$tree/scripts/hooks/l7r-guard.sh" --only "$guard" "$event"
