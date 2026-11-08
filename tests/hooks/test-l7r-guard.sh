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
cp "$ROOT/scripts/hooks/lib/guardlog.sh" "$T/scripts/hooks/lib/"
printf 'fn main() {}\n' > "$T/rust/guard/src/main.rs"; : > "$T/rust/Cargo.toml"; : > "$T/rust/Cargo.lock"

# the fake cargo: BUILD=ok writes a stub answering with $VERSION, BUILD=broken fails to compile, BUILD=unchecked writes one whose
# self-check fails; each call is appended to $W/cargo.calls
cat > "$W/cargo" <<'EOF'
#!/usr/bin/env bash
echo build >> "$CALLS"
[ "$BUILD" = broken ] && { echo "error[E0308]: mismatched types" >&2; exit 101; }
[ "$BUILD" = slow ] && { echo "Compiling serde" >&2; sleep 3; exit 0; }
mkdir -p "$CARGO_TARGET_DIR/release"
check=0; [ "$BUILD" = unchecked ] && check=1
printf '#!/usr/bin/env bash\n[ "$1" = --self-check ] && exit %s\ncat > /dev/null; echo "%s $*"\n' "$check" "$VERSION" > "$CARGO_TARGET_DIR/release/l7r-guard"
chmod +x "$CARGO_TARGET_DIR/release/l7r-guard"
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
exec 8> "$W/target/guard.lock"; flock 8  # this shell holds the build lock, as a call mid-build would
t0=${EPOCHREALTIME/,/.}; out=$(run ok v0 2>/dev/null)
gone=$(awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { print (b - a < 1) ? "fast" : "waited" }')
check "locked: no wait on another call's build" "$gone" fast
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

# 7. the real crate, built by the real cargo into the clone's own target, answers through the wrapper
CARGO_BIN=$( [ -x "$HOME/.cargo/bin/cargo" ] && echo "$HOME/.cargo/bin/cargo" || command -v cargo)
if [ -n "$CARGO_BIN" ]; then
  R="$W/real"; mkdir -p "$R/scripts/hooks/lib"; cp "$ROOT/scripts/hooks/l7r-guard.sh" "$R/scripts/hooks/"; cp -rp "$ROOT/rust" "$R/rust"
  # the clone's own target, warm after its first build: the sources keep their times (cp -p), so cargo finds nothing to do, and the
  # kept binary is removed so the wrapper still builds, self-checks and keeps one
  RT="$HOME/.cache/l7r-cargo-target/$(basename "$ROOT")-guard"; rm -f "$RT/l7r-guard.good"
  t0=${EPOCHREALTIME/,/.}
  out=$(L7R_GUARD_TARGET="$RT" L7R_GUARD_CARGO="$CARGO_BIN" "$R/scripts/hooks/l7r-guard.sh" --version < /dev/null 2>&1)
  case "$out" in "l7r-guard "*) ok ;; *) bad "real build: --version [$out]" ;; esac
  [ -x "$RT/l7r-guard.good" ] && ok || bad "real build: the self-checked binary kept"
  # the self-check touches nothing: run in a clone with a feature, it writes no event log there (T012)
  SC="$W/sc"; mkdir -p "$SC/.git" "$SC/.specify"; printf '{"feature_directory": "specs/1-x"}' > "$SC/.specify/feature.json"
  ( cd "$SC" && "$RT/l7r-guard.good" --self-check >/dev/null 2>&1 )
  [ ! -e "$SC/.git/l7r-events" ] && ok || bad "real build: the self-check wrote into the tree it ran in"
  awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "real build through the wrapper: %.1f s\n", b - a }'
else
  bad "real build: no cargo found"
fi

printf '%s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
