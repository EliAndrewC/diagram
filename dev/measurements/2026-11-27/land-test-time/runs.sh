#!/bin/bash
# 451 T455: the land crate's test binary run N times as cargo runs it (from the crate's directory, every test, libtest's default
# threads), each run's per-test times (libtest's `--report-time`, unlocked on the stable toolchain by RUSTC_BOOTSTRAP=1, the
# binary's own flag and nothing else), its wall, user and system seconds (/usr/bin/time) and load1 before and after.
# usage: runs.sh <test binary> <out dir> <N> [<pause s between runs>]
set -u
bin=$1 out=$2 n=$3 pause=${4:-5}
mkdir -p "$out"
cd "$(dirname "$0")/../../../../rust/gate/crates/land" || exit 2
for i in $(seq 1 "$n"); do
  l0=$(cut -d' ' -f1 /proc/loadavg)
  RUSTC_BOOTSTRAP=1 /usr/bin/time -f '%e %U %S' -o "$out/run$i.time" "$bin" -Z unstable-options --report-time --format json \
    > "$out/run$i.json" 2> "$out/run$i.err"
  rc=$?
  l1=$(cut -d' ' -f1 /proc/loadavg)
  printf '%s run%s rc=%s load1 %s %s wall/user/sys %s\n' "$(date -u +%FT%TZ)" "$i" "$rc" "$l0" "$l1" "$(cat "$out/run$i.time")" >> "$out/runs.log"
  sleep "$pause"
done
