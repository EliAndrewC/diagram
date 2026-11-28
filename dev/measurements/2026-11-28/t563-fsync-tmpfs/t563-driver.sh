#!/usr/bin/env bash
# t563 driver: windows of ONE setting each through `make under-load` (COPIES copies of t563-trial.sh, LOOPS runs each), in the
# order given (an ABBA order so drift hits every arm), each window bracketed by an AMBIENT slice of the same tree idle for AMB s:
# the jbd2 forced-commit rate with no trial running, beside the rate while the window ran.
# Usage: t563-driver.sh <outdir> <copies> <loops> <amb-seconds> <setting>...
set -u
O=${1:?}; C=${2:?}; L=${3:?}; AMB=${4:?}; shift 4
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad
J=/proc/fs/jbd2/nvme0n1p3-8/info
req() { sed -n 's/.*(\([0-9]*\) requested).*/\1/p' $J; }
psi() { sed -n 's/^some avg10=\([0-9.]*\).*/\1/p' /proc/pressure/io; }
mkdir -p "$O"
W=$O/windows.tsv
[ -s "$W" ] || printf 'kind\tsetting\tseconds\tforced\tforced_per_s\tload_start\tpsi_start\n' > "$W"
export SPECIFY_FEATURE=462-efficiency-backlog SPECIFY_FEATURE_DIRECTORY=specs/462-efficiency-backlog
for set in "$@"; do
  l=$(cut -d' ' -f1 /proc/loadavg); p=$(psi); q0=$(req); t0=$(date +%s.%N)
  sleep "$AMB"
  t1=$(date +%s.%N); q1=$(req); dt=$(echo "$t1-$t0" | bc)
  printf 'ambient\t-\t%.1f\t%s\t%.2f\t%s\t%s\n' "$dt" $((q1-q0)) "$(echo "($q1-$q0)/$dt" | bc -l)" "$l" "$p" >> "$W"
  l=$(cut -d' ' -f1 /proc/loadavg); p=$(psi); q0=$(req); t0=$(date +%s.%N)
  make -C /diagram/.clones/diagram-backlog-t271 under-load CMD="bash $S/t563-trial.sh $set $O/runs.tsv $S/t563-bins.txt" \
    COPIES="$C" LOOPS="$L" MAX_MINUTES=12 >> "$O/under-load.log" 2>&1
  t1=$(date +%s.%N); q1=$(req); dt=$(echo "$t1-$t0" | bc)
  printf 'window\t%s\t%.1f\t%s\t%.2f\t%s\t%s\n' "$set" "$dt" $((q1-q0)) "$(echo "($q1-$q0)/$dt" | bc -l)" "$l" "$p" >> "$W"
done
echo DRIVER-DONE
