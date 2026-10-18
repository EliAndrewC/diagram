#!/bin/bash
# Re-take feature 387's work counts (SC-001): profile five stages at 10/20/40 households, seed 4, then count.
# usage: bash specs/387-scale-the-placement-loops/retake_counts.sh <counts-before|counts-after> <m:label>
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="$here/$1"
mkdir -p "$out"
for hh in 10 20 40; do
  for st in homesteads field web windbreak hinterland; do
    make -C "$here/../.." --no-print-directory perf-profile SEED=4 STAGE="$st" HOUSEHOLDS="$hh" > "$out/$st-$hh.log" 2>&1
  done
done
python3 "$here/count_work.py" "$out" "$2"
