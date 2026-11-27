#!/bin/bash
# rust-test.sh OUTDIR  - the wall seconds of `make rust-test` over the 28 gate manifests (its recipe's own call, `l7r-gate.sh rust test`, a --crate each: the form `make builder-checks` runs) after a real one-line
# edit of rust/gate/crates/core/src/lib.rs, T301 part 1's edit (a constant appended, then removed: two timed runs), the family's
# kept results settled first by one untimed run. One run at a time; the tree's root; nothing else of this tree running.
TREE=${TREE:-$(git rev-parse --show-toplevel)}; out=$1; mkdir -p "$out"; cd "$TREE" || exit 1
f=rust/gate/crates/core/src/lib.rs
run() { date -u +"$1 began %FT%T.000Z" >> "$out/summary.txt"; s=$(date +%s.%N); l0=$(cut -d' ' -f1 /proc/loadavg); scripts/gates/l7r-gate.sh rust test $CR >"$out/$1.out" 2>&1; rc=$?; e=$(date +%s.%N)
  printf '%s: rc=%s wall=%.1fs load=%s->%s\n' "$1" $rc "$(echo "$e - $s" | bc)" "$l0" "$(cut -d' ' -f1 /proc/loadavg)" | tee -a "$out/summary.txt"; }
CR=$(for m in rust/gate rust/gate/crates/*; do printf -- "--crate %s " $m; done)
run settle
printf '\n/// T325 measurement: a constant appended and removed.\npub const T325_MEASURE: u8 = 1;\n' >> $f
run appended
git checkout -- $f
run removed
git status --short $f | tee -a "$out/summary.txt"
