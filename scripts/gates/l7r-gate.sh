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
# THE RUST CHECKS ARE THEIR OWN PROGRAM (feature 449 T93): `rust <cmd>` runs `l7r-rust`, built from crates/{core,tree,rustc} alone, so an
# edit of claims (say) no longer rebuilds the release `l7r-gate` before `make rust-test` runs a test - 9.4 s of a claims edit's 15.5 s, 40 s
# of a core edit's 49 s (T92's after-figures, observed 2026-11-11).
PKG=(-p l7r_gate)
SOURCES=("$TREE"/rust/gate)
if [ "${1:-}" = rust ]; then
  shift; BIN="$TARGET/release/l7r-rust"; PKG=(-p l7r_gate_rustc --bin l7r-rust)
  SOURCES=("$TREE"/rust/gate/crates/core "$TREE"/rust/gate/crates/tree "$TREE"/rust/gate/crates/rustc)
fi
cargo=${L7R_GATE_CARGO:-}
[ -n "$cargo" ] || { [ -x "$real/.cargo/bin/cargo" ] && cargo="$real/.cargo/bin/cargo" || cargo=cargo; }
# every source the binary builds from: the guard crate's too, which both build on - before T93 a guard edit left `l7r-gate` stale
stale() {
  [ -x "$BIN" ] || return 0
  local f d; shopt -s globstar nullglob
  for d in "${SOURCES[@]}" "$TREE/rust/guard"; do
    for f in "$d"/**; do [ "$f" -nt "$BIN" ] && return 0; done
  done
  for f in "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock"; do [ "$f" -nt "$BIN" ] && return 0; done
  return 1
}
if stale; then
  RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}" CARGO_TARGET_DIR="$TARGET" "$cargo" build --release --quiet --manifest-path "$TREE/rust/Cargo.toml" "${PKG[@]}" || { echo "l7r-gate: the build failed - fix what cargo names above" >&2; exit 1; }
  touch "$BIN"  # cargo leaves an up-to-date binary's time alone, and a source newer than it would ask again on every call
fi
export L7R_GATE_TREE="$TREE"  # where the binary finds codeid.py: a fixture repository it runs in has none
exec "$BIN" "$@"
