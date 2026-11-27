#!/usr/bin/env bash
# t452-wall.sh <wrapper> <label>: the hook's wall when its build passes its limit (stub cargo, 10 runs), and whether the next call
# runs the new binary. A good binary stands, the sources are touched, the stub cargo sleeps 3 s, the limit is 1 s.
set -uo pipefail
WRAP=$1 LABEL=$2 ROOT=/diagram/.clones/diagram-backlog-t269
W=$(mktemp -d); trap 'sleep 4; rm -rf "$W"' EXIT
T="$W/tree"; mkdir -p "$T/scripts/hooks/lib" "$T/rust/guard/src" "$T/scripts/gates"
cp "$WRAP" "$T/scripts/hooks/l7r-guard.sh"; chmod +x "$T/scripts/hooks/l7r-guard.sh"
cp "$ROOT/scripts/hooks/lib/guardlog.sh" "$ROOT/scripts/hooks/lib/lld-path.sh" "$T/scripts/hooks/lib/"
printf 'fn main() {}\n' > "$T/rust/guard/src/main.rs"; : > "$T/rust/Cargo.toml"; : > "$T/rust/Cargo.lock"
cat > "$W/cargo" <<'EOF'
#!/usr/bin/env bash
sleep "${SLOW_SECS:-3}"
mkdir -p "$CARGO_TARGET_DIR/tool"
printf '#!/usr/bin/env bash\n[ "$1" = --self-check ] && exit 0\ncat > /dev/null; echo "%s"\n' "$VERSION" > "$CARGO_TARGET_DIR/tool/l7r-guard"
chmod +x "$CARGO_TARGET_DIR/tool/l7r-guard"
EOF
chmod +x "$W/cargo"
export L7R_GUARD_TARGET="$W/target" L7R_GUARD_CARGO="$W/cargo" GUARD_LOG_DIR="$W/log"
run() { VERSION=$1 "$T/scripts/hooks/l7r-guard.sh" PreToolUse < /dev/null 2>/dev/null; }
SLOW_SECS=0 run v0 > /dev/null  # the first good binary
newer=0
for i in $(seq 1 10); do
  sleep 0.01; touch "$T/rust/guard/src/main.rs"
  t0=${EPOCHREALTIME/,/.}; L7R_GUARD_BUILD_SECS=1 run "v$i" > /dev/null
  wall=$(awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.3f", b - a }')
  sleep 3.5  # the detached build, if any, ends
  got=$(SLOW_SECS=0 L7R_GUARD_BUILD_SECS=1 run "x$i")  # x: a rebuild here would say it was not the slow build's binary
  [ "$got" = "v$i" ] && newer=$((newer+1))
  printf '%s\trun %s\twall %s s\tnext call ran %s\n' "$LABEL" "$i" "$wall" "$got"
done
printf '%s\tthe next call ran the slow build'"'"'s binary %s of 10\tload %s\n' "$LABEL" "$newer" "$(cut -d' ' -f1-3 /proc/loadavg)"
