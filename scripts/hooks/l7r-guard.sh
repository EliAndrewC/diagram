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
# Test seams: L7R_GUARD_TARGET (the cargo target directory), L7R_GUARD_CARGO (the cargo to build with), L7R_GUARD_BUILD_SECS (the
# build's limit).
set -uo pipefail
EVENT=${1:-}
# the paths by expansion, not by `$(cd ...)`: each subshell was a fork on every call, 7.7 ms of the wrapper's 8.6 (100 calls, 2026-11-07)
HERE=${BASH_SOURCE[0]%/*}
case "$HERE" in /*) ;; *) HERE="$(cd "$HERE" && pwd)" ;; esac  # settings call it by its absolute path; a relative call resolves
TREE=${HERE%/scripts/hooks}
TARGET=${L7R_GUARD_TARGET:-$HOME/.cache/l7r-cargo-target/${TREE##*/}}
GOOD="$TARGET/l7r-guard.good"
FAILED="$TARGET/guard.failed"
LOG="$TARGET/build.log"
SOURCES=("$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock")

# newer <stamp>: true when a source is newer than <stamp>, or <stamp> is missing - by bash's own `-nt` over a globstar walk, no
# process (`find -newer` was a fork on every call); a directory counts, so a file added or removed is a change too
shopt -s globstar nullglob
newer() {
  [ -e "$1" ] || return 0
  local f
  for f in "${SOURCES[@]}" "$TREE"/rust/guard/**; do [ "$f" -nt "$1" ] && return 0; done
  return 1
}

# stale: the good binary is older than the sources, and no build since the last change has failed
stale() { newer "$GOOD" && newer "$FAILED"; }

# BOUNDED, AND NEVER WAITED ON (T004, measured 2026-11-07): a clone's first build took 5.7 s idle and 19.1 s with every core busy,
# past the 10 s most hook entries allow - and a hook killed by its timeout stamps nothing and logs nothing, so every call would go
# through unguarded with no record. The build stops itself at L7R_GUARD_BUILD_SECS, inside the entry's timeout, and is NOT stamped
# failed: cargo keeps what it finished, and the next call carries it on. A call that finds another building does not wait for the
# lock either (waiting is the same silent kill): it runs what is there.
build() {
  local cargo=${L7R_GUARD_CARGO:-} secs=${L7R_GUARD_BUILD_SECS:-45}
  [ -n "$cargo" ] || { [ -x "$HOME/.cargo/bin/cargo" ] && cargo="$HOME/.cargo/bin/cargo" || cargo=cargo; }
  (
    flock -n 9 || exit 0
    stale || exit 0  # another call built it since this one looked
    exec 2> "$LOG"  # opened under the lock: a second call never truncates the log of the build it skipped
    CARGO_TARGET_DIR="$TARGET" timeout "$secs" "$cargo" build --release --quiet --manifest-path "$TREE/rust/Cargo.toml" -p l7r_guard >&2
    rc=$?
    if [ "$rc" -eq 124 ]; then
      echo "l7r-guard: the build passed its $secs s limit; the next call carries it on" >&2
    elif [ "$rc" -ne 0 ]; then
      touch "$FAILED"
    elif "$TARGET/release/l7r-guard" --self-check > /dev/null; then
      cp "$TARGET/release/l7r-guard" "$GOOD.tmp" && mv -f "$GOOD.tmp" "$GOOD" && rm -f "$FAILED"
    else
      echo "l7r-guard: the build compiled and failed its --self-check" >&2
      touch "$FAILED"
    fi
  ) 9> "$TARGET/guard.lock"
}

if stale; then mkdir -p "$TARGET" && build; fi
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
