#!/usr/bin/env bash
# TOOL_RECORD: a launcher only; each ported subcommand records its own run, as the Python it replaces does
# l7r-gate.sh <subcommand> ... - run the gate's Rust tools from this tree (feature 449 T061): built here when the sources are newer, and unlike the guards' wrapper it fails closed. A gate that
# cannot build its tool must not pass, and a make recipe waits on the build, where a hook could not.
set -uo pipefail
HERE=${BASH_SOURCE[0]%/*}
case "$HERE" in */..*|[!/]*) HERE="$(cd "$HERE" && pwd)" ;; esac  # a hook reaches it through its own `../gates`
TREE=${HERE%/scripts/gates}
# the account's own home, read in this shell (a fixture may set HOME): `getent passwd "$(id -u)" | cut` cost three processes,
# about 4.4 ms of every call (feature 449, observed 2026-11-12); getent stays the fallback for an account /etc/passwd does not hold
real=
while IFS=: read -r _ _ uid _ _ home _; do [ "$uid" = "$UID" ] && { real=$home; break; }; done < /etc/passwd
[ -n "$real" ] || real=$(getent passwd "$UID" | cut -d: -f6)
TARGET=${L7R_GATE_TARGET:-$real/.cache/l7r-cargo-target/${TREE##*/}}
# THE TOOL PROFILE (T95): incremental release, `[profile.tool]` in rust/Cargo.toml, shared with l7r-rust and l7r-guard, into `tool/`
BIN="$TARGET/tool/l7r-gate"
# THE RUST CHECKS ARE THEIR OWN PROGRAM (feature 449 T93): `rust <cmd>` runs `l7r-rust`, built from crates/{core,tree,rustc} alone, so an
# edit of claims (say) no longer rebuilds the release `l7r-gate` before `make rust-test` runs a test - 9.4 s of a claims edit's 15.5 s, 40 s
# of a core edit's 49 s (T92's after-figures, observed 2026-11-11).
PKG=(-p l7r_gate)
SOURCES=("$TREE"/rust/gate)
if [ "${1:-}" = rust ]; then
  shift; BIN="$TARGET/tool/l7r-rust"; PKG=(-p l7r_gate_rustc --bin l7r-rust)
  SOURCES=("$TREE"/rust/gate/crates/core "$TREE"/rust/gate/crates/tree "$TREE"/rust/gate/crates/rustc)
fi
cargo=${L7R_GATE_CARGO:-}
[ -n "$cargo" ] || { [ -x "$real/.cargo/bin/cargo" ] && cargo="$real/.cargo/bin/cargo" || cargo=cargo; }
# every source the binary builds from: the guard crate's too, which both build on - before T93 a guard edit left `l7r-gate` stale
# - one find, stopping at the first newer path, where a bash glob walk of the same 835 paths cost about 1.5 ms more a call (feature 449,
# observed 2026-11-12); it also sees dot files, which the glob skipped, so it errs toward a rebuild
stale() {
  [ -x "$BIN" ] || return 0
  [ -n "$(find "${SOURCES[@]}" "$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock" "$TREE/.cargo/config.toml" \
    -newer "$BIN" -print -quit 2>/dev/null)" ]
}
# L7R_GATE_STALE_OK=1 runs the binary there is, stale or not, and builds none (feature 449 T129): the Makefile's parse-time goals line
# records a make's goals on every make, and a build there would put the release l7r-gate's rebuild back in front of `make rust-test`
# after a gate-crate edit, which T93 took out of that loop; a stale binary writes the same line. With no binary it builds as before.
if [ -n "${L7R_GATE_STALE_OK:-}" ] && [ -x "$BIN" ]; then
  :
elif stale; then
  # THE LINKER (T96): the build runs from the tree's root, where cargo finds `.cargo/config.toml` (rust-lld) whatever directory called it,
  # and refuses with the fix when that file's lld is not this toolchain's
  . "$TREE/scripts/hooks/lib/lld-path.sh"
  lld_missing "$TREE" && { echo "l7r-gate: not built" >&2; exit 1; }
  ( cd "$TREE" && RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}" CARGO_TARGET_DIR="$TARGET" "$cargo" build --profile tool --quiet --manifest-path "$TREE/rust/Cargo.toml" "${PKG[@]}" ) || { echo "l7r-gate: the build failed - fix what cargo names above" >&2; exit 1; }
  touch "$BIN"  # cargo leaves an up-to-date binary's time alone, and a source newer than it would ask again on every call
fi
export L7R_GATE_TREE="$TREE"  # where the binary finds codeid.py: a fixture repository it runs in has none
exec "$BIN" "$@"
