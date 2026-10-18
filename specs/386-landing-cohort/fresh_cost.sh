#!/usr/bin/env bash
# fresh_cost.sh - what a fresh block costs the per-fix cohort (feature 386, plan D3; spec FR-002, SC-003). Rolls cold cohorts of 16,
# 18 and 20 maps (10, 12 and 14 fixed seeds plus the six pinned rows, served once warm - so the cold maps number 10, 12, 14), three
# repeats interleaved, each on seeds no run has used (from 2000 + 100 i, below the fresh range so they stand for fixed seeds), and
# prints the median wall time of each. 16 maps with FRESH=0 is the per-fix run; 20 is it with a 4-seed block. Minutes, so `make
# figures` runs it only on demand. Run from the repository root: bash specs/386-landing-cohort/fresh_cost.sh [first seed offset]
set -uo pipefail
off=${1:-$(( (RANDOM % 50) * 1000 + 20000 ))}
declare -A t
i=0
for rep in 1 2 3; do
  for n in 6 8 10; do
    i=$((i + 1)); seed=$((off + i * 100))
    s=$(date +%s.%N); make --no-print-directory cohort N=$((n + 4)) SEED=$seed FRESH=0 >/dev/null 2>&1; e=$(date +%s.%N)
    t[$n]="${t[$n]:-} $(python3 -c "print(round($e - $s, 1))")"
  done
done
python3 - "${t[6]}" "${t[8]}" "${t[10]}" <<'PY'
import json, statistics, sys
print(json.dumps({maps: statistics.median(float(x) for x in v.split()) for maps, v in zip(("16 maps", "18 maps", "20 maps"), sys.argv[1:])}))
PY
