#!/usr/bin/env bash
# TOOL_RECORD: a launcher only; each ported subcommand records its own run, as the Python it replaces does
# l7r-gate.sh <subcommand> ... - run the gate's Rust tools from this tree (feature 449 T061): built here when the sources are newer, and unlike the guards' wrapper it fails closed. A gate that
# cannot build its tool must not pass, and a make recipe waits on the build, where a hook could not.
set -uo pipefail
HERE=${BASH_SOURCE[0]%/*}
case "$HERE" in */..*|[!/]*) HERE="$(cd "$HERE" && pwd)" ;; esac  # a hook reaches it through its own `../gates`
TREE=${HERE%/scripts/gates}
real=$(getent passwd "$(id -u)" | cut -d: -f6)
TARGET=${L7R_GATE_TARGET:-$real/.cache/l7r-cargo-target/${TREE##*/}}
BIN="$TARGET/release/l7r-gate"
cargo=${L7R_GATE_CARGO:-}
[ -n "$cargo" ] || { [ -x "$real/.cargo/bin/cargo" ] && cargo="$real/.cargo/bin/cargo" || cargo=cargo; }
stale() {
  [ -x "$BIN" ] || return 0
  local f; shopt -s globstar nullglob
  for f in "$TREE"/rust/gate/** "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock"; do [ "$f" -nt "$BIN" ] && return 0; done
  return 1
}
if stale; then
  RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}" CARGO_TARGET_DIR="$TARGET" "$cargo" build --release --quiet --manifest-path "$TREE/rust/Cargo.toml" -p l7r_gate || { echo "l7r-gate: the build failed - fix what cargo names above" >&2; exit 1; }
fi
export L7R_GATE_TREE="$TREE"  # where the binary finds codeid.py: a fixture repository it runs in has none
exec "$BIN" "$@"
