#!/bin/bash
# lint-pass.sh OUTDIR  - T325's third lint pass priced: the gate's clippy calls by hand (../cargo-hashes/gate-call.sh, -v for --quiet)
# over the six crates that name themselves in [dev-dependencies]; pass `two` is the lint's two passes, `lib` the third (--lib, no
# dev-dependency read). Each pass twice: `warm` (the configuration's first build in the tree, or fresh), then after a touch of core.
TREE=${TREE:-$(git rev-parse --show-toplevel)}; CALL=$TREE/dev/measurements/2026-11-26/cargo-hashes/gate-call.sh; out=$1; mkdir -p "$out"
SIX="rust/gate/crates/core rust/gate/crates/research rust/gate/crates/registry rust/gate/crates/owed rust/gate/crates/archive rust/guard/shared"
pass() { # name, then the clippy words
  name=$1; shift; mkdir -p "$out/$name"; s=$(date +%s.%N); l0=$(cut -d' ' -f1 /proc/loadavg)
  for c in $SIX; do n=$(basename $c); i=0
    for words in "$@"; do i=$((i+1)); TREE=$TREE LOGS=$out/$name "$CALL" "$n-$i" clippy -v $words --manifest-path "$TREE/$c/Cargo.toml" -- -D warnings; done
  done > "$out/$name.txt" 2>&1
  e=$(date +%s.%N)
  printf '%s: calls=%s rc0=%s driver-runs(l7r)=%s wall=%.1fs load=%s->%s\n' "$name" "$(grep -c 'rc=' "$out/$name.txt")" "$(grep -c 'rc=0' "$out/$name.txt")" \
    "$(cat "$out/$name"/t301-log-*.txt | grep -c '^ *Running `.*--crate-name l7r')" "$(echo "$e - $s" | bc)" "$l0" "$(cut -d' ' -f1 /proc/loadavg)" | tee -a "$out/summary.txt"
}
pass two-warm "--all-targets" "--all-targets --all-features"
pass lib-warm "--lib"
touch "$TREE/rust/gate/crates/core/src/lib.rs" "$TREE/rust/guard/shared/src/lib.rs"
pass two-touched "--all-targets" "--all-targets --all-features"
touch "$TREE/rust/gate/crates/core/src/lib.rs" "$TREE/rust/guard/shared/src/lib.rs"
pass lib-touched "--lib"
