#!/usr/bin/env bash
# l7r-guard.sh <event> - the one hook entry for the Rust guards (feature 449 T004, plan D7).
#
# WHY ONE BINARY BEHIND A WRAPPER (research R1-R2, `m:hooks-bash`): a Bash call ran 26 shell guards and 29 Python starts, 1,045 ms
# of CPU summed, to read one JSON input 26 times. `l7r-guard` reads it once and runs every guard's check in one process.
#
# WHY THE BINARY FROM THIS TREE (research R6): settings run main's copy of this script, so a guard reaches every session once it is
# on main; build output is gitignored, so the binary is built here, from the sources beside this script, when they are newer.
#
# WHY THE LAST GOOD BINARY (D7; the plan review of 2026-11-07): one binary is every guard, so a broken build must not turn them all
# off. Each build that passes `l7r-guard --self-check` is copied to `l7r-guard.good`, and that copy is the one that runs: a build that
# fails to compile, or compiles and fails its self-check, leaves the previous guards standing. It is not retried until the sources
# change again (`guard.failed` stamps the attempt), so a broken tree costs one build, not one a call.
#
# ONLY WITH NONE EVER BUILT does the call go through, with a notice and a guard-log line (`failed-open`): what a guard does today
# when its Python cannot start (`m:python-dead-fails-open` - repo-safety lets a force push to main through), and Claude Code's rule
# for a crashing hook (exit 2 alone blocks).
#
# Test seams: L7R_GUARD_TARGET (the cargo target directory), L7R_GUARD_CARGO (the cargo to build with).
set -uo pipefail
EVENT=${1:-}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "$HERE/../.." && pwd)"
TARGET=${L7R_GUARD_TARGET:-$HOME/.cache/l7r-cargo-target/$(basename "$TREE")}
GOOD="$TARGET/l7r-guard.good"
FAILED="$TARGET/guard.failed"
SOURCES=("$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock")

# newer <stamp>: true when a source is newer than <stamp>, or <stamp> is missing
newer() { [ ! -e "$1" ] || [ -n "$(find "${SOURCES[@]}" -newer "$1" -print -quit 2>/dev/null)" ]; }

# stale: the good binary is older than the sources, and no build since the last change has failed
stale() { newer "$GOOD" && newer "$FAILED"; }

build() {
  local cargo=${L7R_GUARD_CARGO:-}
  [ -n "$cargo" ] || { [ -x "$HOME/.cargo/bin/cargo" ] && cargo="$HOME/.cargo/bin/cargo" || cargo=cargo; }
  mkdir -p "$TARGET" || return 1
  exec 9> "$TARGET/guard.lock"
  flock -w 120 9 || return 1
  stale || return 0  # another call built it while this one waited
  if CARGO_TARGET_DIR="$TARGET" "$cargo" build --release --quiet --manifest-path "$TREE/rust/Cargo.toml" -p l7r_guard >&2 \
    && "$TARGET/release/l7r-guard" --self-check > /dev/null 2>&1; then
    cp "$TARGET/release/l7r-guard" "$GOOD.tmp" && mv -f "$GOOD.tmp" "$GOOD" && rm -f "$FAILED"
  else
    touch "$FAILED"
  fi
  exec 9>&-  # the lock is the build's, not the guard's that runs next
}

LOG="$TARGET/build.log"
if stale; then mkdir -p "$TARGET" && build 2> "$LOG"; fi
if [ -x "$GOOD" ]; then
  exec "$GOOD" "$@"
fi

# none ever built: the call goes through, said and recorded
INPUT=$(cat)
. "$HERE/lib/guardlog.sh"
guard_log l7r-guard failed-open "no good l7r-guard binary has been built (see $LOG)" failed-open
note="l7r-guard: no good guard binary has ever been built from $TREE, so this $EVENT call went through unguarded. The build's output is in $LOG; fix the build and the next call builds it."
case "$EVENT" in
  PreToolUse|PostToolUse|UserPromptSubmit|SessionStart|SubagentStart|PostToolUseFailure)
    printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "$EVENT" "$note" ;;
  *) printf '%s\n' "$note" >&2; exit 1 ;;
esac
exit 0
