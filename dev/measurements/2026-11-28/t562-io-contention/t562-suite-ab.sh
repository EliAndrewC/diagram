#!/usr/bin/env bash
# t562: a crate's test suite (fixture git repos in its TMPDIR) with git's default fsync against core.fsync=none, ABAB.
# Usage: t562-suite-ab.sh <tree> <crate> <out.tsv> [rounds]
set -u
TREE=$1; CRATE=$2; OUT=$3; R=${4:-3}
J=/proc/fs/jbd2/nvme0n1p3-8/info
req() { sed -n 's/.*(\([0-9]*\) requested).*/\1/p' $J; }
export SPECIFY_FEATURE=462-efficiency-backlog SPECIFY_FEATURE_DIRECTORY=specs/462-efficiency-backlog L7R_BLOCKS=none L7R_RUST_FRESH=1
[ -f "$OUT" ] || printf 'crate\tsetting\tround\twall_s\ttests_s\tjbd2_requested\tload\trc\n' > "$OUT"
for r in $(seq "$R"); do for setting in default fsync-none; do
  extra=(); [ $setting = fsync-none ] && extra=(GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsync GIT_CONFIG_VALUE_0=none)
  l=$(cut -d' ' -f1 /proc/loadavg); q0=$(req); t0=$(date +%s.%N)
  log=${OUT%.tsv}-${CRATE##*/}-$setting-$r.log
  ( cd "$TREE" && env "${extra[@]}" make rust-test CRATE="$CRATE" ) > "$log" 2>&1; rc=$?
  t1=$(date +%s.%N); q1=$(req)
  ts=$(grep -o 'finished in [0-9.]*s' "$log" | tail -1 | grep -o '[0-9.]*')
  printf '%s\t%s\t%s\t%.2f\t%s\t%s\t%s\t%s\n' "${CRATE##*/}" $setting $r "$(echo "$t1-$t0"|bc)" "$ts" $((q1-q0)) "$l" $rc >> "$OUT"
done; done
