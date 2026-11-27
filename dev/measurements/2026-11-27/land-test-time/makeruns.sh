#!/bin/bash
# 451 T455: the land crate's tests run N times the way the slow runs ran, through `make rust-test CRATE=rust/gate/crates/land FRESH=1`
# (the runner's own TMPDIR, env and pipes), each run's wall, libtest's `finished in` and load1 before and after; watch.sh runs beside
# it so a run past 20 s is caught alive.
# usage: makeruns.sh <out dir> <N> [<pause s>]
set -u
out=$1 n=$2 pause=${3:-10}
tree=$(cd "$(dirname "$0")/../../../.." && pwd)
mkdir -p "$out"
"$(dirname "$0")/watch.sh" "$out/watch.txt" $(( n * (pause + 60) )) &
for i in $(seq 1 "$n"); do
  l0=$(cut -d' ' -f1 /proc/loadavg); t0=$(date +%s.%N)
  make -C "$tree" --no-print-directory rust-test CRATE=rust/gate/crates/land FRESH=1 REASON="T455 measurement run $i" > "$out/make$i.log" 2>&1
  rc=$?
  t1=$(date +%s.%N); l1=$(cut -d' ' -f1 /proc/loadavg)
  fin=$(grep -o 'finished in [0-9.]*s' "$out/make$i.log" | tail -1)
  printf '%s make%s rc=%s load1 %s %s wall %.2f %s\n' "$(date -u +%FT%TZ)" "$i" "$rc" "$l0" "$l1" "$(echo "$t1 - $t0" | bc)" "$fin" >> "$out/makeruns.log"
  sleep "$pause"
done
wait
