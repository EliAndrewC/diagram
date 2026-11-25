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
  # A NEIGHBOR'S UNCOMPILING FILE (feature 451 T41): builders share a clone, so one builder's guard or gate-crate edit that does not
  # compile failed every other builder's gate command - `make decide`, `make format`, `make speckit-todo`, each check - in 0.2-2.7 s, with
  # a line telling them to fix it (measured 2026-11-20, a scratch clone with a broken rust/guard/src/shared.rs, then gate/crates/owed).
  # The refusal now names each file cargo points at, from the tree's root, and what to do when it is not yours. It does NOT fall back to
  # the binary built before: that binary is behind every source newer than it, and the gate links the guard's shared code (speckit
  # parsing, regexes, logs, house style) into nearly every command, so its verdicts and records could come from code older than the code
  # they judge. The commands that render no verdict and write no record a gate trusts (`rust format` writing, a bare `speckit-todo`
  # listing, `coord lines`) were 6% of the week's 12,700 make targets (`.git/tool-usage.jsonl`, 2026-11-13 to 20), too few for the risk.
  # A BUILD INSIDE A COVER RUN (feature 451 T247): a crate's coverage tests run with the cover's environment, and one that calls this
  # launcher after a gate source edit rebuilt the tool inside it - instrumented, so every later call dropped a default_*.profraw where it
  # ran (21 hook-suite tests failed on their fixture clones, 2026-11-25). The flag rides RUSTC_WORKSPACE_WRAPPER (`rustc/cover.rs`'
  # `workspace_only` moves it out of RUSTFLAGS), so clearing RUSTFLAGS alone keeps it (a toy workspace under that wrapper, 2026-11-25):
  # the build clears every variable `cargo llvm-cov show-env` sets and every flag or wrapper channel cargo reads, and the tool's own
  # flags come from `.cargo/config.toml`, as outside a cover run.
  plain=(-u RUSTFLAGS -u CARGO_ENCODED_RUSTFLAGS -u CARGO_BUILD_RUSTFLAGS -u RUSTDOCFLAGS -u CARGO_ENCODED_RUSTDOCFLAGS -u RUSTC_WORKSPACE_WRAPPER
    -u RUSTC_WRAPPER -u LLVM_PROFILE_FILE -u CARGO_LLVM_COV -u CARGO_LLVM_COV_SHOW_ENV -u CARGO_LLVM_COV_TARGET_DIR -u CARGO_LLVM_COV_BUILD_DIR)
  build() { ( cd "$TREE" && env "${plain[@]}" RUSTUP_HOME="${RUSTUP_HOME:-$real/.rustup}" CARGO_HOME="${CARGO_HOME:-$real/.cargo}" CARGO_TARGET_DIR="$TARGET" "$cargo" build --profile tool --quiet --manifest-path "$TREE/rust/Cargo.toml" "${PKG[@]}" ) 2> "$err"; }
  err=$(mktemp); build; rc=$?
  # A STALE INCREMENTAL UNIT (feature 451 T142): the tool profile is incremental release (T95), and rustc 1.87 can reuse one codegen unit's
  # post-ThinLTO object while the unit that defines a symbol it imports is rebuilt under a new `.llvm.<hash>` name: the crate's rlib then
  # holds an undefined hidden symbol no member defines, its fingerprint is fresh, and every incremental link fails on it until a source
  # of that crate moves (measured 2026-11-22: l7r_gate_task's unit ads6op1mfn3gc3gvm7k1udw55, its object dated 11-21 12:01, reused into
  # the rebuilds of 23:53, 00:14 and 00:15, about eight failed gate commands; l7r_shared's units failed l7r-rust twice the same night).
  # A CARGO_INCREMENTAL=0 build is a separate artifact set (its own profile hash), so it linked once and left the bad rlib for the next
  # incremental build - "it came back". The fix drops exactly what the linker names - the session holding that unit and that crate's
  # fingerprint (cargo's own `.cargo-lock` held, so no build is mid-flight in them) - and rebuilds once incrementally: that crate is
  # compiled from nothing, 4.8 s in a scratch copy of this cache. A link error naming no unit retries once with CARGO_INCREMENTAL=0.
  if [ "$rc" -ne 0 ] && grep -q 'undefined hidden symbol' "$err"; then
    grep 'rust-lld: error' "$err" | sed 's/^ *= note: //' | head -5 >&2  # not the link line: thousands of words
    dropped=() units=()
    for u in $(grep -o '[A-Za-z0-9_]*-[0-9a-f]\{16\}\.[a-z0-9]\{1,\}\.rcgu\.o' "$err" | sort -u); do
      crate=${u%%-*} rest=${u#*-}; meta=${rest%%.*} cgu=${rest#*.}; cgu=${cgu%.rcgu.o}
      units+=("$crate's unit $cgu")
      for o in "$TARGET"/tool/incremental/"$crate"-*/s-*/"$cgu".o; do [ -e "$o" ] && dropped+=("${o%/*/*}"); done
      [ -d "$TARGET/tool/.fingerprint/$crate-$meta" ] && dropped+=("$TARGET/tool/.fingerprint/$crate-$meta")
    done
    if [ "${#units[@]}" -gt 0 ]; then
      mapfile -t dropped < <(printf '%s\n' "${dropped[@]}" | awk 'NF && !seen[$0]++')
      [ "${#dropped[@]}" -gt 0 ] && flock "$TARGET/tool/.cargo-lock" rm -rf "${dropped[@]}"
      what=$(printf '%s\n' "${dropped[@]}" | sed "s|^$TARGET/||" | awk 'NF' | paste -sd'\t' - | sed 's/\t/ and /g')
      echo "l7r-gate: the link failed on stale incremental state (rust-lld: undefined hidden symbol, referenced from $(IFS=,; echo "${units[*]}" | sed 's/,/, /g')): dropped ${what:-nothing (no session holds that unit)}, rebuilding once (feature 451 T142)" >&2
      build; rc=$?
    else
      echo "l7r-gate: the link failed on stale incremental state (rust-lld: undefined hidden symbol) but names no unit to drop, rebuilding once with CARGO_INCREMENTAL=0 (feature 451 T142)" >&2
      CARGO_INCREMENTAL=0 build; rc=$?
    fi
    if [ "$rc" -eq 0 ]; then echo "l7r-gate: rebuilt and linked" >&2; else echo "l7r-gate: the rebuild after dropping the stale state failed too:" >&2; fi
  fi
  cat "$err" >&2
  if [ "$rc" -ne 0 ]; then
    # cargo's `  --> guard/src/x.rs:36:18`: relative to the workspace, rust/; an absolute path (a registry crate's) is kept as it is
    files=$(sed -n 's/^ *--> \([^:]*\):[0-9].*/\1/p' "$err" | awk '!seen[$0]++ { print (substr($0, 1, 1) == "/" ? $0 : "rust/" $0) }' | paste -sd, - | sed 's/,/, /g')
    rm -f "$err"
    if [ -n "$files" ]; then
      case $files in *", "*) verb="do not compile" them=them ;; *) verb="does not compile" them=it ;; esac
      echo "l7r-gate: $files $verb, so ${BIN##*/} is not built and no command runs on the one built before $them (a verdict must come from the code it judges)" >&2
      echo "l7r-gate: yours? fix what cargo names above. Not yours? another builder in this tree is mid-edit: leave it alone and re-run once it compiles (\`git -C $TREE status --short\` lists the uncommitted edits)" >&2
    else
      echo "l7r-gate: the build failed - fix what cargo names above" >&2
    fi
    exit 1
  fi
  rm -f "$err"
  # NEVER LEFT INSTRUMENTED (T247): a binary that carries LLVM's profile counters (`__llvm_prf_cnts`, a section only an instrumented build
  # has: 0 of the 19 tool binaries in every clone's target, 2026-11-25) is removed, not run, whatever put the flag in - read here, at a
  # build, never on a call
  if grep -qaF __llvm_prf_cnts "$BIN"; then
    rm -f "$BIN" "$BIN.build.json"
    echo "l7r-gate: ${BIN##*/} came out instrumented for coverage, so it is removed and nothing runs on it (it would drop a default_*.profraw wherever it runs): find what adds -C instrument-coverage outside the cover run (\`.cargo/config.toml\`'s rustflags, a cargo config's rustc-wrapper) and re-run" >&2
    exit 1
  fi
  touch "$BIN"  # cargo leaves an up-to-date binary's time alone, and a source newer than it would ask again on every call
  # THE BUILD'S ID (feature 451 T197): HEAD and each uncommitted file the binary is built from at its blob ("deleted" where gone),
  # written beside it, so an answer it records says what judged it - this tree holds other builders' uncommitted code
  {
    printf '{"commit": "%s", "dirty": {' "$(git -C "$TREE" rev-parse HEAD 2>/dev/null)"; sep=
    while IFS= read -r p; do
      b=deleted; [ -e "$TREE/$p" ] && b=$(git -C "$TREE" hash-object -- "$TREE/$p")
      p=${p//\\/\\\\}; printf '%s"%s": "%s"' "$sep" "${p//\"/\\\"}" "$b"; sep=', '
    done < <(git -C "$TREE" -c core.quotePath=false status --porcelain=v1 -uall -- "${SOURCES[@]}" "$TREE/rust/guard" "$TREE/rust/Cargo.toml" \
      "$TREE/rust/Cargo.lock" "$TREE/.cargo/config.toml" 2>/dev/null | cut -c4- | sed 's/.* -> //')
    printf '}}'
  } > "$BIN.build.json"
fi
L7R_GATE_BUILD=
[ -r "$BIN.build.json" ] && L7R_GATE_BUILD=$(cat "$BIN.build.json")
export L7R_GATE_BUILD  # empty for a binary built before T197: it records no build
# GUARD_EDIT_OK: feature 449 T205 - L7R_GATE_PRINT_FRESH=1: the binary, built above when stale, printed where it is now fresh
# (exit 1 where it is not: a failed build, or STALE_OK's stale binary), for `make hooks-test` to export as L7R_GATE_FRESH
if [ -n "${L7R_GATE_PRINT_FRESH:-}" ]; then stale && exit 1; printf '%s\n' "$BIN"; exit 0; fi
export L7R_GATE_TREE="$TREE"  # the gate's own tree (closing list, review state), which a fixture repository it runs in lacks
exec "$BIN" "$@"
