#!/bin/bash
# Back to back, alternating per seed: abab.sh <households> <seeds,...> <base root> <new root> <out prefix>
h=$1; seeds=$2; base=$3; new=$4; out=$5
cd "$(dirname "$0")"
: > $out-base.log; : > $out-new.log
export CLOCK
for s in ${seeds//,/ }; do
  ROOT=$base timeout 1500 python3 refusals.py $h $s 2>&1 | grep -E "^ *[0-9]+ " >> $out-base.log
  ROOT=$new timeout 1500 python3 refusals.py $h $s 2>&1 | grep -E "^ *[0-9]+ " >> $out-new.log
done
for leg in base new; do awk -v l=$leg '{t+=$2; n+=$3} END {printf "%s: %d seeds, stage %.1f s, %d houses\n", l, NR, t, n}' $out-$leg.log; done
