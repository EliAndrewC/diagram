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
# THE BROWSER IS ITS OWN PROGRAM (feature 449 T146, `ask:449-phase4-slices` Q4): `browser <cmd>` runs `l7r-browser`, the one crate that
# drives Chromium (`rust/browser/`), built alone from its own sources and the Chromium pin; neither `l7r-gate` nor `l7r-guard` depends
# on it, so their builds never compile it. The gate reaches it as a program (`record archive`'s fetch, `record modal-bundle`'s crop).
if [ "${1:-}" = browser ]; then
  shift; BIN="$TARGET/tool/l7r-browser"; PKG=(-p l7r_browser --bin l7r-browser)
  SOURCES=("$TREE"/rust/browser "$TREE"/scripts/container/chromium.pin)
fi
# THE EMBEDDER IS ITS OWN PROGRAM (feature 449 T138, `ask:449-phase4-slices` Q11): `embed <cmd>` runs `l7r-embed`, the one crate that
# runs BGE-M3 through ONNX Runtime (`rust/embed/`), built alone from its own sources and the runtime's pin; neither `l7r-gate` nor
# `l7r-guard` depends on it, so their builds never compile the runtime's bindings or the tokenizer. The gate's `record semantic` and
# `record search` reach it as a program.
if [ "${1:-}" = embed ]; then
  shift; BIN="$TARGET/tool/l7r-embed"; PKG=(-p l7r_embed --bin l7r-embed)
  SOURCES=("$TREE"/rust/embed "$TREE"/scripts/container/onnxruntime.pin)
fi
# THE MODE A ENGINE IS ITS OWN PROGRAM (feature 449 T168, the engine port's step 1): `mode-a <cmd>` runs `l7r-mode-a` (`rust/mode_a/`),
# built from its own sources and the gate crates it reads (the registry, and what the registry builds on); neither `l7r-gate` nor
# `l7r-guard` depends on it, so their builds never compile the geometry and rendering crates the engine will pull.
if [ "${1:-}" = mode-a ]; then
  shift; BIN="$TARGET/tool/l7r-mode-a"; PKG=(-p l7r_mode_a --bin l7r-mode-a)
  # GUARD_EDIT_OK: feature 449 T220 - the pool walk's crate, which the engine's pool sweep and audit build on
  SOURCES=("$TREE"/rust/mode_a "$TREE"/rust/gate/crates/registry "$TREE"/rust/gate/crates/research "$TREE"/rust/gate/crates/core "$TREE"/rust/gate/crates/pool)
fi
# THE HAMLET DRIVER AS AN ENGINE (feature 449 T221): `hamlet <spec>` runs `rust/phases`' `hamlet` binary built in the tool profile, so
# the generation cache (`make map`) asks for it as it asks for `l7r-mode-a` - `L7R_GATE_PRINT_FRESH=1` builds it where stale and prints
# its path, whose GNU build id is the hamlets' engine id. `make hamlet` and the cohorts keep running it by cargo (HAMLET_RUN).
# GUARD_EDIT_OK: feature 449 T221 - a launcher arm for the hamlet driver, which the generation cache identifies by its built binary
# (only as the first word: `rust hamlet ...`, the Rust checks' counting runs, has shifted `rust` off above and is `l7r-rust`'s)
if [ "${1:-}" = hamlet ] && [ "$BIN" = "$TARGET/tool/l7r-gate" ]; then
  shift; BIN="$TARGET/tool/hamlet"; PKG=(-p l7r_phases --bin hamlet)
  SOURCES=("$TREE"/rust/phases)
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
# L7R_GATE_NO_BUILD=1 builds none even where there is no binary, and exits 1 (feature 449 T143): `guard_log` runs `log guard` from
# `l7r-guard.sh`'s no-binary path, inside a hook's timeout, where a build of the gate from nothing is the wait a hook must never take.
# GUARD_EDIT_OK: feature 449 T205 - THE RUN'S FRESH BINARY: `make hooks-test` asks once, before its fan-out, which binary is fresh
# (L7R_GATE_PRINT_FRESH=1 prints it, below) and exports it as L7R_GATE_FRESH; a call whose $BIN is that binary skips the walk of
# its sources. The walk was most of the suites' system time: sync-with-main's run called this launcher 689 times, each walk
# about 1,400 paths, every path a line of the read recorder's log (975,624 of its 1,260,877 lines, 2026-11-19). Under the
# recorder the walk is also what ties a suite to the Rust sources, so the call writes those roots to its log as `c-tree`
# lines, which tests/hooks/hookrun.sh expands to every path under them before `trace stamp`, as the walk recorded them.
# Another binary - a variant (rust, browser, embed, mode-a) or another target - walks as before.
if [ -n "${L7R_GATE_FRESH:-}" ] && [ "$L7R_GATE_FRESH" = "$BIN" ] && [ -x "$BIN" ]; then
  if [ -n "${L7R_TEST_DEP_LOG:-}" ]; then
    for p in "${SOURCES[@]}" "$TREE/rust/guard" "$TREE/rust/Cargo.toml" "$TREE/rust/Cargo.lock" "$TREE/.cargo/config.toml"; do
      printf '%s\tc-tree\t%s\n' "${L7R_TEST_DEP_FILE:-}" "$p"
    done >> "$L7R_TEST_DEP_LOG"
  fi
elif [ -n "${L7R_GATE_STALE_OK:-}" ] && [ -x "$BIN" ]; then
  :
elif [ -n "${L7R_GATE_NO_BUILD:-}" ] && [ ! -x "$BIN" ]; then
  echo "l7r-gate: not built, and L7R_GATE_NO_BUILD builds none" >&2; exit 1
elif stale; then
  # THE LINKER (T96): the build runs from the tree's root, where cargo finds `.cargo/config.toml` (rust-lld) whatever directory called it,
  # and refuses with the fix when that file's lld is not this toolchain's
  . "$TREE/scripts/hooks/lib/lld-path.sh"
  lld_missing "$TREE" && { echo "l7r-gate: not built" >&2; exit 1; }
  ( cd "$TREE" && RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}" CARGO_TARGET_DIR="$TARGET" "$cargo" build --profile tool --quiet --manifest-path "$TREE/rust/Cargo.toml" "${PKG[@]}" ) || { echo "l7r-gate: the build failed - fix what cargo names above" >&2; exit 1; }
  touch "$BIN"  # cargo leaves an up-to-date binary's time alone, and a source newer than it would ask again on every call
fi
# GUARD_EDIT_OK: feature 449 T205 - L7R_GATE_PRINT_FRESH=1: the binary, built above when stale, printed where it is now fresh
# (exit 1 where it is not: a failed build, or STALE_OK's stale binary), for `make hooks-test` to export as L7R_GATE_FRESH
if [ -n "${L7R_GATE_PRINT_FRESH:-}" ]; then stale && exit 1; printf '%s\n' "$BIN"; exit 0; fi
export L7R_GATE_TREE="$TREE"  # where the binary finds codeid.py: a fixture repository it runs in has none
exec "$BIN" "$@"
