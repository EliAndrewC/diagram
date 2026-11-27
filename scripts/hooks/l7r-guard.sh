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
# Test seams: L7R_GUARD_TARGET (the cargo target directory), L7R_GUARD_CARGO (the cargo to build with), L7R_GUARD_BUILD_SECS (how
# long a call waits for its build), L7R_GUARD_DETACHED_SECS (the detached build's own ceiling).
set -uo pipefail
EVENT=${1:-}
# the paths by expansion, not by `$(cd ...)`: each subshell was a fork on every call, 7.7 ms of the wrapper's 8.6 (100 calls, 2026-11-07)
HERE=${BASH_SOURCE[0]%/*}
case "$HERE" in */..*|[!/]*) HERE="$(cd "$HERE" && pwd)" ;; esac  # settings call it by its absolute path; a relative call, or one through `..` (451 T61: writer-alive.sh reached it as lib/../, read `..` as the tree and ran a stale build), resolves
TREE=${HERE%/scripts/hooks}
TARGET=${L7R_GUARD_TARGET:-$HOME/.cache/l7r-cargo-target/${TREE##*/}}
GOOD="$TARGET/l7r-guard.good"
FAILED="$TARGET/guard.failed"
HEALED="$TARGET/guard.healed"  # a link failure's heal tried (451 T449), cleared by a good build
LOG="$TARGET/build.log"
SOURCES=("$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock" "$TREE/.cargo/config.toml")

# newer <stamp>: true when a source is newer than <stamp>, or <stamp> is missing; a directory counts, so a file added or removed is a
# change too. ONE `find -newer -print -quit` (451 T439): bash's `-nt` over a globstar walk was chosen to save find's fork when the walk
# was small, but at 449 paths it cost 8.8 ms a call in place and find 4.7 (20 and 40 runs, load 23, 2026-11-27,
# dev/measurements/2026-11-27/hook-floor/results.md) - every hook call pays it. Only the sources that exist are named (`.cargo/config.toml`
# may be absent, and find fails on a missing start path). A find that fails falls back to the walk, never to "fresh". No kept stamp
# replaces the walk: an edit moves only its file's time, so any stamp must still look at every file - or trust a signal that an edit
# made through Bash, a git fast-forward or another session never gives.
shopt -s globstar nullglob
newer() {
  [ -e "$1" ] || return 0
  local f src=()
  for f in "${SOURCES[@]}"; do [ -e "$f" ] && src+=("$f"); done
  if f=$(find "${src[@]}" -newer "$1" -print -quit 2>/dev/null); then [ -n "$f" ]; return; fi
  for f in "${SOURCES[@]}" "$TREE"/rust/guard/**; do [ "$f" -nt "$1" ] && return 0; done
  return 1
}

# stale: the good binary is older than the sources, and no build since the last change has failed
stale() { newer "$GOOD" && newer "$FAILED"; }

# BOUNDED, AND NEVER WAITED ON (T004, measured 2026-11-07): a clone's first build took 5.7 s idle and 19.1 s with every core busy,
# past the 10 s most hook entries allow - and a hook killed by its timeout stamps nothing and logs nothing, so every call would go
# through unguarded with no record. The call waits for its build at most L7R_GUARD_BUILD_SECS, inside the entry's timeout. A call that
# finds another building does not wait for the lock either (waiting is the same silent kill): it runs what is there.
#
# PAST THE LIMIT THE BUILD IS LEFT TO FINISH, NOT CUT (feature 451 T452): until T452 the limit was `timeout`'s SIGTERM to cargo, and a
# build cut mid-write broke the next link 16 of 31 times on rust/guard (T336, dev/measurements/2026-11-26/prewarm-link/) - the likely
# writer of 2026-11-27's bad libl7r_guard rlib, 49 minutes of every hook on an old binary (T449). Now the build runs in a session of its
# own (`setsid`: a hook's process group killed, or the session ending, leaves it running), its stdin /dev/null and its output in
# build.log, holding guard.lock - taken by the call and handed down, so no second call starts another - and the call stops WAITING at
# the limit and runs the last good binary, as it did. The build writes its result when it ends: the good binary's copy and self-check,
# or guard.failed, each stamped with the build's START time, so a source edited while it ran is newer than what it built and the next
# call builds again. Its one cut left is a ceiling for a hung build, L7R_GUARD_DETACHED_SECS (600 s, a GUESS knob: case 7's figure for
# a real build on a loaded machine), cut there unstamped as any build at a limit was.
#
# A NEVER-BUILT GUARD BEFORE A MAKE STEP (451 T286): hooks run the mirror's copy of this script, so a tree's own binary is first built
# by its own `make` - the disk floor of `make closing-checks`, `make done` and `make land` (`DISK_FLOOR`) - and with none ever built that
# call's only answer is exit 1: a fresh tree's first closing checks died there twice at load 56 (2026-11-26), the cold build past 45 s.
# L7R_GUARD_COLD_SECS, which only such a caller sets (no hook entry: its harness timeout is the bound above), gives a call with NO good
# binary that bound in seconds for the whole of it - waiting for another call's build, then building - so it builds instead of dying.
# With a good binary, stale or not, the seam changes nothing: the last good one runs at once as before.
build() {
  local secs=${L7R_GUARD_BUILD_SECS:-45} lock=-n began=${EPOCHREALTIME/,/.} wait
  if [ -n "${L7R_GUARD_COLD_SECS:-}" ] && [ ! -x "$GOOD" ]; then
    secs=$L7R_GUARD_COLD_SECS lock="-w $L7R_GUARD_COLD_SECS"
    echo "l7r-guard: no guard binary has been built in $TREE yet; building it first (up to $secs s; its log $LOG)" >&2
  fi
  exec 9> "$TARGET/guard.lock"
  flock $lock 9 && stale || { exec 9>&-; return 0; }  # another call is building, or built it since this one looked
  : > "$LOG"  # truncated under the lock: a second call never truncates the log of the build it skipped
  # the build, detached, inherits fd 9 and so the lock; this call lets its own copy go and waits on the lock for what is left of its limit
  L7R_GUARD_DETACHED=$secs setsid bash "$HERE/${BASH_SOURCE[0]##*/}" < /dev/null >> "$LOG" 2>&1 &
  exec 9>&-
  wait=$secs
  # what the wait for the lock left of a cold call's bound (451 T286); a hook's call never waited, so its limit stands whole
  [ "$lock" = -n ] || wait=$(awk -v s="$secs" -v a="$began" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { l = s - (b - a); print (l > 0.1) ? l : 0.1 }')
  flock -w "$wait" "$TARGET/guard.lock" true 2>/dev/null || detached=1
  [ -z "${detached:-}" ] || echo "l7r-guard: the build passed this call's $secs s limit; it carries on detached (pid $!), and the next call after it ends runs what it built (feature 451 T452)" >> "$LOG"
}

# the detached build (feature 451 T452): its whole run, the lock already held on fd 9; `hook` is the limit its call waited
detached_build() {
  local hook=$1 cargo=${L7R_GUARD_CARGO:-} secs=${L7R_GUARD_DETACHED_SECS:-600} started="$TARGET/guard.started" f
  [ -n "$cargo" ] || { [ -x "$HOME/.cargo/bin/cargo" ] && cargo="$HOME/.cargo/bin/cargo" || cargo=cargo; }
  # never under the limit its call waits: a caller that waits longer (`make builder-tree`'s 1800 s, hooks-test's 600 s) keeps its bound
  secs=$(awk -v c="$secs" -v h="$hook" 'BEGIN { print (h + 0 > c + 0) ? h : c }')
  # every descriptor but its stdio and the lock closed: one inherited from the caller (a harness pipe, a test's lock) is not held to its end
  for f in /proc/$$/fd/*; do f=${f##*/}; case $f in 0|1|2|9|255) ;; *) eval "exec $f>&-" 2>/dev/null ;; esac; done
  touch "$started"
  # THE LINKER (T96): a hook runs from the session's directory, which may be outside this tree; the build runs from the tree's root,
  # where cargo finds `.cargo/config.toml` (rust-lld), and a toolchain that moved is a failed build that says the fix in the log
  cd "$TREE" || return 0
  . "$HERE/lib/lld-path.sh"
  if lld_missing "$TREE"; then touch -r "$started" "$FAILED"; return 0; fi
  # the tool profile (T95): incremental release, shared with l7r-gate, so a guard edit rebuilds in about 1.5 s, not 15 s
  local t0=${EPOCHREALTIME/,/.} left rc
  CARGO_TARGET_DIR="$TARGET" timeout "$secs" "$cargo" build --profile tool --quiet --manifest-path "$TREE/rust/Cargo.toml" -p l7r_guard >&2 9>&-
  rc=$?
  # A LINK FAILURE IS HEALED ONCE (feature 451 T449): from 2026-11-27T05:47Z the clone's l7r_guard rlib held ten `.llvm.<n>` symbols no
  # member defined (rust-lld: undefined hidden symbol) while its fingerprint was fresh, so every build relinked the binary against it,
  # stamped guard.failed and left every hook on the 05:03Z binary for 49 minutes; moving the incremental directories aside did not
  # help (cargo never recompiled the "fresh" crate), moving the two crates' deps and fingerprints aside made it link in 40 s. So a
  # link failure drops those (and their incremental sessions; every other crate's kept), under cargo's own lock of the profile, and
  # rebuilds once in what is left of the ceiling - cut there, it is not stamped failed, as any build at its limit. ONCE A SOURCE CHANGE,
  # not once a call: `guard.healed` marks the heal tried, so a link that fails again before the sources move is stamped failed - a
  # real linker fault, or a rebuild that a cut re-broke, costs one heal, never the ceiling on every call. The lock is waited on within
  # the ceiling and the time left taken after it (detached, a gate build holding the profile is waited out, 451 T452).
  left() { awk -v s="$secs" -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { l = s - (b - a); print (l > 0.05) ? l : 0 }'; }
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 124 ] && grep -q -e 'undefined hidden symbol' -e 'linking with' "$LOG"; then
    local tool="$TARGET/tool"
    if [ -e "$HEALED" ] && ! newer "$HEALED"; then
      echo "l7r-guard: the link failed again, and its heal was tried since the sources last changed: stamped failed (feature 451 T449)" >&2
    elif mkdir -p "$tool" && flock -w "$(left)" "$tool/.cargo-lock" rm -rf "$tool"/deps/*l7r_guard* "$tool"/deps/*l7r_shared* \
      "$tool"/.fingerprint/l7r_guard-* "$tool"/.fingerprint/l7r_shared-* "$tool"/incremental/l7r_guard-* "$tool"/incremental/l7r_shared-* 9>&-; then
      touch -r "$started" "$HEALED"
      echo "l7r-guard: the link failed (rust-lld: undefined hidden symbol, or the link line); dropped tool/deps, tool/.fingerprint and tool/incremental of l7r_guard and l7r_shared, rebuilding once (feature 451 T449)" >&2
      left=$(left); rc=124
      if [ "$left" != 0 ]; then
        CARGO_TARGET_DIR="$TARGET" timeout "$left" "$cargo" build --profile tool --quiet --manifest-path "$TREE/rust/Cargo.toml" -p l7r_guard >&2 9>&-
        rc=$?
      fi
      [ "$rc" -eq 0 ] && echo "l7r-guard: rebuilt and linked" >&2
    else
      echo "l7r-guard: the link failed, and cargo's lock of tool/ stayed held to the limit: dropped nothing; the next call heals it (feature 451 T449)" >&2
      rc=124
    fi
  fi
  if [ "$rc" -eq 124 ]; then
    echo "l7r-guard: the build passed its $secs s limit; the next call carries it on" >&2
  elif [ "$rc" -ne 0 ]; then
    touch -r "$started" "$FAILED"
  elif "$TARGET/tool/l7r-guard" --self-check > /dev/null 9>&-; then
    cp "$TARGET/tool/l7r-guard" "$GOOD.tmp" && touch -r "$started" "$GOOD.tmp" && mv -f "$GOOD.tmp" "$GOOD" && rm -f "$FAILED" "$HEALED"
  else
    echo "l7r-guard: the build compiled and failed its --self-check" >&2
    touch -r "$started" "$FAILED"
  fi
  awk -v h="$hook" -v a="$t0" -v b="${EPOCHREALTIME/,/.}" \
    'BEGIN { if (b - a > h) printf "l7r-guard: the build took %.1f s, past the hook'"'"'s %s s limit; it finished detached (feature 451 T452)\n", b - a, h }' >&2
}
if [ -n "${L7R_GUARD_DETACHED:-}" ]; then
  hook=$L7R_GUARD_DETACHED; unset L7R_GUARD_DETACHED
  detached_build "$hook"; exit 0
fi

# GUARD_EDIT_OK: feature 449 T205 - THE RUN'S FRESH BINARY, as `l7r-gate.sh`'s: `make hooks-test` asks once, before its fan-out,
# which good binary is fresh (L7R_GUARD_PRINT_FRESH=1 prints it, below) and exports it as L7R_GUARD_FRESH; a call whose $GOOD is
# that binary skips the walk of rust/guard (about 2,000 paths a call, 266,643 lines of sync-with-main's read log on 2026-11-19).
# Under the read recorder the walk tied a suite to the guard's sources, so the call writes those roots to its log as `c-tree`
# lines, which tests/hooks/hookrun.sh expands to every path under them before `trace stamp`. Another target walks as before.
if [ -n "${L7R_GUARD_FRESH:-}" ] && [ "$L7R_GUARD_FRESH" = "$GOOD" ] && [ -x "$GOOD" ]; then
  if [ -n "${L7R_TEST_DEP_LOG:-}" ]; then
    for p in "${SOURCES[@]}"; do printf '%s\tc-tree\t%s\n' "${L7R_TEST_DEP_FILE:-}" "$p"; done >> "$L7R_TEST_DEP_LOG"
  fi
elif stale; then mkdir -p "$TARGET" && build; fi
# L7R_GUARD_PRINT_FRESH=1 (T205): the good binary, built above when stale, printed where no source is newer than it (exit 1 where
# one is: a failed build, a build past its limit, none ever built). With none named, its stderr is ONE line, the reason (feature 451 T449):
# the build log's first error line where the build failed, so `make hooks-test` and test-parts.3.sh stop on it instead of running fixtures
# that exec an empty path (14 FAIL, `exec: : Permission denied`, 2026-11-27); otherwise the limit, or that none is built yet
# A print-fresh call is never a hook's, so where another call's build holds the lock it WAITS for it, within the limit, and asks again
# (a hook's own build in the clone while `make hooks-test` starts must not read as a guard that does not build)
if [ -n "${L7R_GUARD_PRINT_FRESH:-}" ]; then
  fresh() { [ -x "$GOOD" ] && ! newer "$GOOD"; }
  failed() { [ -e "$FAILED" ] && ! newer "$FAILED"; }
  held=
  # (a build this call started and left running past the limit, 451 T452, is said as one past the limit, not waited for again)
  if ! fresh && ! failed && [ -z "${detached:-}" ]; then
    if flock -w "${L7R_GUARD_BUILD_SECS:-45}" "$TARGET/guard.lock" true 2>/dev/null; then stale && build; else held=1; fi
  fi
  if fresh; then printf '%s\n' "$GOOD"; exit 0; fi
  if failed; then
    why=$(grep -m1 'error' "$LOG" 2>/dev/null); printf '%s\n' "${why:-the build failed and $LOG says no error}" >&2
  elif [ -n "$held" ]; then
    printf "another call's build held the lock past the %s s limit; run again\n" "${L7R_GUARD_BUILD_SECS:-45}" >&2
  else
    printf 'its build did not finish inside the %s s limit; run again and it carries on\n' "${L7R_GUARD_BUILD_SECS:-45}" >&2
  fi
  exit 1
fi
if [ -x "$GOOD" ]; then
  export L7R_GUARD_TREE="$TREE"  # the tree a decider asks its tools in (T006: the tools stay theirs until phase 3)
  exec "$GOOD" "$@"
fi

# none ever built: the call goes through, said and recorded
INPUT=$(cat)
. "$HERE/lib/guardlog.sh"
# the entry is the gate's (`l7r-gate log guard`, feature 449 T143); where the gate has no binary either, the one entry written without
# one (`lib/failed-open-log.sh`, the T143 plan review): the only record that the guards did not run, on the tree where nothing else leaves one
if ! _guard_log_write l7r-guard failed-open "no good l7r-guard binary has been built (see $LOG)" failed-open >/dev/null 2>&1; then
  . "$HERE/lib/failed-open-log.sh"
  failed_open_log "no good l7r-guard binary has been built (see $LOG)" "$TREE" >/dev/null 2>&1 || true
fi
note="l7r-guard: no good guard binary has ever been built from $TREE, so this $EVENT call went through unguarded. The build's output is in $LOG; fix the build and the next call builds it."
case "$EVENT" in
  PreToolUse|PostToolUse|UserPromptSubmit|SessionStart|SubagentStart|PostToolUseFailure)
    printf '{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "%s"}}\n' "$EVENT" "$note" ;;
  *) printf '%s\n' "$note" >&2; exit 1 ;;
esac
exit 0
