#!/usr/bin/env bash
# Tests for l7r-guard.sh, the Rust guards' one hook entry (feature 449 T004, plan D7). Run: tests/hooks/test-l7r-guard.sh
#
# The wrapper runs in a scratch tree beside a fake cargo that records each call and "builds" a stub binary, so every case - a
# stale build rebuilt, a fresh one not, a build that fails to compile or fails its self-check falling back to the last good binary,
# none ever built failing open with its notice and its guard-log line - is decided in milliseconds. One case builds the real crate
# with the real cargo, so the wrapper is proven against the binary it exists to run.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0; fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); printf 'FAIL: %s\n' "$1"; }
check() { if [ "$2" = "$3" ]; then ok; else bad "$1: wanted [$3], got [$2]"; fi; }

W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
T="$W/tree"; mkdir -p "$T/scripts/hooks/lib" "$T/rust/guard/src"
cp "$ROOT/scripts/hooks/l7r-guard.sh" "$T/scripts/hooks/"
cp "$ROOT/scripts/hooks/lib/guardlog.sh" "$ROOT/scripts/hooks/lib/lld-path.sh" "$T/scripts/hooks/lib/"
# the guard log's entry is the gate's `log guard` (feature 449 T143), reached through the tree's `l7r-gate.sh`: here the real one, as the
# other suites' fixture trees stand it in, so the no-binary path's entry is written by the binary this clone built
mkdir -p "$T/scripts/gates"
printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$ROOT/scripts/gates/l7r-gate.sh" > "$T/scripts/gates/l7r-gate.sh"; chmod +x "$T/scripts/gates/l7r-gate.sh"
printf 'fn main() {}\n' > "$T/rust/guard/src/main.rs"; : > "$T/rust/Cargo.toml"; : > "$T/rust/Cargo.lock"

# the fake cargo: BUILD=ok writes a stub answering with $VERSION, BUILD=broken fails to compile, BUILD=unchecked writes one whose
# self-check fails; each call is appended to $W/cargo.calls
cat > "$W/cargo" <<'EOF'
#!/usr/bin/env bash
echo build >> "$CALLS"
pwd > "$CALLS.dir"
[ "$BUILD" = broken ] && { echo "error[E0308]: mismatched types" >&2; exit 101; }
[ "$BUILD" = slow ] && { echo "Compiling serde" >&2; sleep 3; exit 0; }
[ "$2 $3" = "--profile tool" ] || { echo "fake cargo: built $2 $3, not --profile tool (T95)" >&2; exit 101; }
mkdir -p "$CARGO_TARGET_DIR/tool"
check=0; [ "$BUILD" = unchecked ] && check=1
printf '#!/usr/bin/env bash\n[ "$1" = --self-check ] && exit %s\ncat > /dev/null; echo "%s $*"\n' "$check" "$VERSION" > "$CARGO_TARGET_DIR/tool/l7r-guard"
chmod +x "$CARGO_TARGET_DIR/tool/l7r-guard"
EOF
chmod +x "$W/cargo"

export L7R_GUARD_TARGET="$W/target" L7R_GUARD_CARGO="$W/cargo" CALLS="$W/cargo.calls" GUARD_LOG_DIR="$W/log"
IN='{"session_id": "s", "cwd": "/c", "tool_name": "Bash", "tool_input": {"command": "ls"}}'
run() { BUILD=$1 VERSION=$2 "$T/scripts/hooks/l7r-guard.sh" PreToolUse < <(printf '%s' "$IN"); }
calls() { wc -l < "$CALLS" 2>/dev/null | tr -d ' ' || echo 0; }
touch_sources() { sleep 0.01; touch "$T/rust/guard/src/main.rs"; }

# 0. none built yet and the build is slow or already running elsewhere: through at once, said and logged, nothing stamped failed
out=$(L7R_GUARD_BUILD_SECS=0.3 run slow v0 2>/dev/null); rc=$?
check "slow: exit" "$rc" 0
case "$out" in *"went through unguarded"*) ok ;; *) bad "slow: notice [$out]" ;; esac
grep -q "passed its 0.3 s limit" "$W/target/build.log" && ok || bad "slow: the limit said in build.log [$(cat "$W/target/build.log")]"
[ ! -e "$W/target/guard.failed" ] && ok || bad "slow: a build cut by its limit is not stamped failed"
check "slow: one build tried" "$(calls)" 1
# THE BOUND IS CALIBRATED (451 T172): the locked call's own work - its notice and the real gate's guard-log entry - timed on the same
# path with no lock to meet (a failed build stamped, so nothing is built and the lock is never asked), the slowest of three, the bound
# three times that and never under the 1 s it was. The hard-coded 1 s failed at load average about 22 (2026-11-23) where nothing waited
# (l7r/diagram/CLAUDE.md: a time bound in a test is scaled by a calibration loop, as 449 T391's diff-run timeout).
touch "$W/target/guard.failed"; slowest=0
for _ in 1 2 3; do
  c0=${EPOCHREALTIME/,/.}; run ok v0 > /dev/null 2>&1
  slowest=$(awk -v a="$c0" -v b="${EPOCHREALTIME/,/.}" -v s="$slowest" 'BEGIN { d = b - a; print (d > s) ? d : s }')
done
rm -f "$W/target/guard.failed" "$W"/log/*.json
bound=$(awk -v s="$slowest" 'BEGIN { b = 3 * s; print (b > 1) ? b : 1 }')
exec 8> "$W/target/guard.lock"; flock 8  # this shell holds the build lock, as a call mid-build would
t0=${EPOCHREALTIME/,/.}; out=$(run ok v0 2>/dev/null)
gone=$(awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" -v n="$bound" 'BEGIN { print (b - a < n) ? "fast" : "waited" }')
check "locked: no wait on another call's build (bound $bound s)" "$gone" fast
check "locked: no second build" "$(calls)" 1
case "$out" in *"went through unguarded"*) ok ;; *) bad "locked: notice [$out]" ;; esac
grep -q "passed its 0.3 s limit" "$W/target/build.log" && ok || bad "locked: the running build's log left alone"
exec 8>&-; : > "$CALLS"; rm -f "$W"/log/*.json

# 1. none ever built: the build fails, the call goes through with its notice and a guard-log line
out=$(run broken v0 2>/dev/null); rc=$?
check "none built: exit" "$rc" 0
case "$out" in *'"additionalContext": "l7r-guard: no good guard binary has ever been built'*) ok ;; *) bad "none built: notice [$out]" ;; esac
log=$(cat "$W"/log/*.json 2>/dev/null)
case "$log" in *'"event": "failed-open"'*'"guard"'*|*'"guard": "l7r-guard"'*'"event": "failed-open"'*) ok ;; *) bad "none built: guard-log line [$log]" ;; esac
grep -q E0308 "$W/target/build.log" && ok || bad "none built: the build's error kept in build.log"
# ...and where the gate has no binary either, the entry is still written, without one (`lib/failed-open-log.sh`, feature 449 T143's plan
# review), byte for byte the text `guard_log`'s Python wrote for this input
rm -f "$W"/log/*.json; cp "$ROOT/scripts/hooks/lib/failed-open-log.sh" "$T/scripts/hooks/lib/"
IN2='{"session_id": 12345678901234567890123, "cwd": "/cé", "tool_name": "Edit", "tool_input": {"command": "", "file_path": "/f"}}'
out=$(IN="$IN2" L7R_GATE_TARGET="$W/no-gate" SID=s run broken v0 2>/dev/null); rc=$?
check "none built, no gate: exit" "$rc" 0
files=$(ls "$W"/log/ 2>/dev/null)
case "$files" in [0-9]*T[0-9]*-[0-9]*.json) ok ;; *) bad "none built, no gate: one entry by name [$files]" ;; esac
want=$(printf '{\n  "utc": "<utc>",\n  "guard": "l7r-guard",\n  "event": "failed-open",\n  "rule": "failed-open",\n  "session": 12345678901234567890123,\n  "session_name": 12345678901234567890123,\n  "cwd": "/c\\u00e9",\n  "tool": "Edit",\n  "transcript": "",\n  "detail": "no good l7r-guard binary has been built (see %s)",\n  "command": "/f",\n  "context": null\n}' "$W/target/build.log")
got=$(sed -E 's/"utc": "[0-9TZ:-]+"/"utc": "<utc>"/' "$W"/log/*.json 2>/dev/null)
check "none built, no gate: the Python's entry, byte for byte" "$got" "$want"
rm -f "$T/scripts/hooks/lib/failed-open-log.sh" "$W"/log/*.json
check "none built: one build tried" "$(calls)" 1
# ...and a Stop event, which takes no additionalContext, is told on stderr with a non-blocking exit
err=$(BUILD=broken VERSION=v0 "$T/scripts/hooks/l7r-guard.sh" Stop < <(printf '{}') 2>&1 >/dev/null); rc=$?
check "none built, Stop: exit" "$rc" 1
case "$err" in *"went through unguarded"*) ok ;; *) bad "none built, Stop: notice [$err]" ;; esac
check "none built: a failed build is not retried until the sources change" "$(calls)" 1

# 2. the sources change and the build passes: built, self-checked, kept and run
touch_sources
check "stale: rebuilt and run" "$(run ok v1)" "v1 PreToolUse"
check "stale: one more build" "$(calls)" 2
# 3. fresh: run without building
check "fresh: run" "$(run ok v1)" "v1 PreToolUse"
check "fresh: no build" "$(calls)" 2

# 4. a build that fails to compile runs the last good binary, and is not retried until the sources change again
touch_sources
check "broken: last good runs" "$(run broken v2 2>/dev/null)" "v1 PreToolUse"
check "broken: no retry" "$(run broken v2 2>/dev/null)" "v1 PreToolUse"
check "broken: one build" "$(calls)" 3
# 5. a build that compiles and fails its self-check is not kept
touch_sources
check "unchecked: last good runs" "$(run unchecked v3)" "v1 PreToolUse"
# 6. a good build after a failed one is kept again
touch_sources
check "recovered: the new build runs" "$(run ok v4)" "v4 PreToolUse"
check "recovered: builds" "$(calls)" 5

# 6b. the build runs from the tree's root, where cargo finds `.cargo/config.toml` (rust-lld, T96), though the hook ran from elsewhere
touch_sources
out=$(cd / && run ok v5)
check "from elsewhere: built and run" "$out" "v5 PreToolUse"
check "from elsewhere: cargo ran in the tree" "$(cat "$CALLS.dir")" "$T"
# 6c. a config whose rust-lld this toolchain lacks: no build tried, the last good runs, the fix in build.log
mkdir -p "$T/.cargo"; printf 'rustflags = ["-C", "link-arg=-B/no/such/gcc-ld"]\n' > "$T/.cargo/config.toml"
check "lld gone: last good runs" "$(run ok v6 2>/dev/null)" "v5 PreToolUse"
check "lld gone: no build tried" "$(calls)" 6
grep -q "rust-lld from /no/such/gcc-ld.*has no ld.lld.*rustc --print sysroot" "$W/target/build.log" && ok || bad "lld gone: the fix in build.log [$(cat "$W/target/build.log")]"
rm -rf "$T/.cargo"; touch_sources
check "lld back: built again" "$(run ok v7)" "v7 PreToolUse"

# 6d. THE RUN'S FRESH BINARY (feature 449 T205): L7R_GUARD_PRINT_FRESH=1 names the good binary where no source is newer, and a call
# given that name in L7R_GUARD_FRESH runs it without walking the sources - no build though they changed - writing their roots to the
# read recorder's log as `c-tree` lines; any other name walks and builds as before
GOOD="$W/target/l7r-guard.good"
check "print-fresh: the fresh binary named" "$(L7R_GUARD_PRINT_FRESH=1 run ok v7)" "$GOOD"
touch_sources
L7R_GUARD_PRINT_FRESH=1 run broken v8 >/dev/null 2>&1; check "print-fresh: a stale binary whose build failed is not named" "$?" 1
check "print-fresh: ...after one build tried" "$(calls)" 8
touch_sources
out=$(L7R_GUARD_FRESH="$GOOD" L7R_TEST_DEP_LOG="$W/dep.log" L7R_TEST_DEP_FILE=s.sh run ok v9)
check "fresh: the named binary runs" "$out" "v7 PreToolUse"
check "fresh: no walk, no build, though the sources changed" "$(calls)" 8
check "fresh: the sources' roots in the recorder's log" "$(grep "$(printf '\tc-tree\t')" "$W/dep.log")" "$(printf 's.sh\tc-tree\t%s\n' "$T/rust/guard" "$T/rust/Cargo.toml" "$T/rust/Cargo.lock" "$T/.cargo/config.toml")"
out=$(L7R_GUARD_FRESH="$W/elsewhere/l7r-guard.good" run ok v9)
check "another name: walked and built as before" "$out" "v9 PreToolUse"
check "another name: one more build" "$(calls)" 9

# 8. THE SETTINGS' HOOK COMMANDS ARE SHORT (feature 451 T169, the GM 2026-11-23 "on hook output length"): the harness prints an
# entry's command with every block or notice it emits, and the ~245-character commands were 1.66M characters of one session's
# transcript (6,665 stored occurrences, measured 2026-11-23). Each entry is the launcher `scripts/hooks/l7r-hook` and its event; what the
# commands carried - the mirror-or-tree choice, the escape marker's reasons - is the launcher's. The budget is a knob, GUESS: the
# longest event's command (`PostToolUseFailure`, 63 characters) and one to spare.
BUDGET=${HOOK_COMMAND_BUDGET:-64}
S="$ROOT/.claude/settings.json"
LAUNCH='"$CLAUDE_PROJECT_DIR"/scripts/hooks/l7r-hook'
entries=$(jq -r '.hooks | to_entries[] | .key as $e | .value[].hooks[] | [$e, (.timeout // 0 | tostring), .command] | @tsv' "$S")
long=$(printf '%s\n' "$entries" | awk -F'\t' -v b="$BUDGET" 'length($3) > b { printf "%s: %d characters\n", $1, length($3) }')
check "settings: every hook command within $BUDGET characters (move what a longer one does into scripts/hooks/l7r-hook, its why into that file's header)" "$long" ""
# ...and each is the launcher with one word, run here as the harness runs it - `sh -c`, CLAUDE_PROJECT_DIR the tree - in a tree of
# stubs with no mirror, so the eight events still reach the dispatcher by their own names, stdin with them, and the setup its script
L="$W/launch"; mkdir -p "$L/scripts/hooks" "$L/scripts/container" "$L/mirror/scripts/hooks" "$L/mirror/scripts/container"
cp "$ROOT/scripts/hooks/l7r-hook" "$L/scripts/hooks/l7r-hook" 2>/dev/null
stub() { printf '#!/usr/bin/env bash\nprintf "%s %%s|%%s" "$*" "$(cat)"; printf "said on stderr" >&2; exit ${STUB_RC:-0}\n' "$2" > "$1"; chmod +x "$1"; }
stub "$L/scripts/hooks/l7r-guard.sh" tree; stub "$L/scripts/container/setup-dev-env.sh" tree-setup
stub "$L/mirror/scripts/hooks/l7r-guard.sh" mirror; stub "$L/mirror/scripts/container/setup-dev-env.sh" mirror-setup
fired=$(printf '%s\n' "$entries" | while IFS=$'\t' read -r ev secs cmd; do
  word=${cmd#"$LAUNCH "}
  case "$cmd:$word" in
    "$LAUNCH "*:*[!A-Za-z]*|*:) printf '%s: not the launcher and one word [%s]\n' "$ev" "$cmd" ;;  # never run: another command may reach the real guards
    "$LAUNCH "*) printf '%s: %s\n' "$ev" "$(printf '{"e": "%s"}' "$ev" | CLAUDE_PROJECT_DIR="$L" CLONE_MAIN="$L/none" sh -c "$cmd" 2>/dev/null)" ;;
    *) printf '%s: not the launcher and one word [%s]\n' "$ev" "$cmd" ;;
  esac
done | sort)
want=$(for ev in PostToolUse PostToolUseFailure PreToolUse SessionStart Stop SubagentStart SubagentStop UserPromptSubmit; do
  printf '%s: tree %s|{"e": "%s"}\n' "$ev" "$ev" "$ev"; done; printf 'SessionStart: tree-setup --ensure|{"e": "SessionStart"}\n'
  printf 'Stop: tree --idle-check|{"e": "Stop"}\n')  # the Stop's background idle check (451 T183)
check "settings: each entry reaches the dispatcher by its event, or the setup (write it as $LAUNCH <event>)" "$fired" "$(printf '%s\n' "$want" | sort)"
# ...each dispatcher entry's timeout above the wrapper's build limit, so a bounded build ends before the harness kills the hook (449 T005)
limit=$(grep -o 'L7R_GUARD_BUILD_SECS:-[0-9]*' "$ROOT/scripts/hooks/l7r-guard.sh" | head -1 | cut -d- -f2)
short=$(printf '%s\n' "$entries" | awk -F'\t' -v l="${limit:-45}" '$3 !~ / setup$/ && $2 + 0 <= l + 0 { printf "%s: %s s\n", $1, $2 }')
check "settings: every dispatcher entry's timeout above the wrapper's ${limit:-?} s build limit" "$short" ""
# 8b. THE LAUNCHER: the mirror's copy where it is executable (its setup where it is a file), else the tree's own - stdin, the event,
# the exit code and stderr passed through unchanged
lr() { printf 'in' | CLAUDE_PROJECT_DIR="$L" "$@" sh -c "$LAUNCH PreToolUse"; }
check "launcher: the mirror's dispatcher first" "$(lr env CLONE_MAIN="$L/mirror" 2>/dev/null)" "mirror PreToolUse|in"
check "launcher: exit 2 passed through" "$(lr env CLONE_MAIN="$L/mirror" STUB_RC=2 >/dev/null 2>&1; echo $?)" 2
check "launcher: stderr passed through" "$(lr env CLONE_MAIN="$L/mirror" 2>&1 >/dev/null)" "said on stderr"
chmod -x "$L/mirror/scripts/hooks/l7r-guard.sh"
check "launcher: a mirror copy not executable, the tree's own" "$(lr env CLONE_MAIN="$L/mirror" 2>/dev/null)" "tree PreToolUse|in"
check "launcher: the mirror's setup first, by bash with --ensure" "$(printf '' | CLAUDE_PROJECT_DIR="$L" CLONE_MAIN="$L/mirror" sh -c "$LAUNCH setup" 2>/dev/null)" "mirror-setup --ensure|"
chmod -x "$L/mirror/scripts/container/setup-dev-env.sh"
check "launcher: a setup that is a file needs no exec bit" "$(printf '' | CLAUDE_PROJECT_DIR="$L" CLONE_MAIN="$L/mirror" sh -c "$LAUNCH setup" 2>/dev/null)" "mirror-setup --ensure|"
rm "$L/mirror/scripts/container/setup-dev-env.sh"
check "launcher: no mirror setup, the tree's own" "$(printf '' | CLAUDE_PROJECT_DIR="$L" CLONE_MAIN="$L/mirror" sh -c "$LAUNCH setup" 2>/dev/null)" "tree-setup --ensure|"

# 7. the real crate, built by the real cargo into the clone's own target, answers through the wrapper
CARGO_BIN=$( [ -x "$HOME/.cargo/bin/cargo" ] && echo "$HOME/.cargo/bin/cargo" || command -v cargo)
if [ -n "$CARGO_BIN" ]; then
  # the clone's own tree through its own wrapper into the wrapper's own target - the one `make done`'s hook calls already build - so
  # a changed guard crate is built once, not twice; the build, self-check and keep paths are cases 1-6's, on the fake cargo. Until
  # 449 T94 a copy of `rust/` was built here into a second `-guard` target: cargo keys a build on the package's path as well as its
  # sources, so the copy recompiled the guard crate on every run (54.9 s and 60.0 s under landings, 2026-11-10/11)
  R="$ROOT"
  RT="$HOME/.cache/l7r-cargo-target/$(basename "$ROOT")"
  t0=${EPOCHREALTIME/,/.}
  # the build's own limit (45 s) is case 1's subject; here a cold target on a loaded machine outran it (2026-11-10 54.9 s, 2026-11-11
  # 60.0 s, both landings), so this case gives the real build room and judges only what it answers
  # (env -u L7R_GUARD_FRESH, T205: make hooks-test names this binary fresh, and this case walks and builds as a session's hook does)
  out=$(env -u L7R_GUARD_FRESH L7R_GUARD_BUILD_SECS=600 L7R_GUARD_TARGET="$RT" L7R_GUARD_CARGO="$CARGO_BIN" "$R/scripts/hooks/l7r-guard.sh" --version < /dev/null 2>&1)
  case "$out" in "l7r-guard "*) ok ;; *) bad "real build: --version [$out]" ;; esac
  [ -x "$RT/l7r-guard.good" ] && ok || bad "real build: the self-checked binary kept"
  # the self-check touches nothing: run in a clone with a feature, it writes no event log there (T012)
  SC="$W/sc"; mkdir -p "$SC/.git" "$SC/.specify"; printf '{"feature_directory": "specs/1-x"}' > "$SC/.specify/feature.json"
  ( cd "$SC" && "$RT/l7r-guard.good" --self-check >/dev/null 2>&1 )
  [ ! -e "$SC/.git/l7r-events" ] && ok || bad "real build: the self-check wrote into the tree it ran in"
  # a tool verb reads no stdin: under `make` it inherits one that never closes, and `read_to_string` waited on it for ever (T050, a window target hung 590 s)
  # stdin from a process substitution, not a pipe: a pipeline waits for its `sleep` (30 s on every run until 449 T94), and its right
  # side ran in a subshell, so this case's ok/bad never reached the counts
  timeout 10 "$RT/l7r-guard.good" deps --bogus >/dev/null 2>&1 < <(sleep 30)
  [ $? -ne 124 ] && ok || bad "real build: a tool verb waited on an open stdin"
  awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "real build through the wrapper: %.1f s\n", b - a }'
else
  bad "real build: no cargo found"
fi

printf '%s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
