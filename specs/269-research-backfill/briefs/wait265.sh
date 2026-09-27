#!/bin/sh
# A `then:` step before the groups that EDIT existing fragments (feature 269 spec, Edge Cases): feature 265's
# unpushed sweeps edited those fragments, so wait until 265 has landed - its close carries scripts/reserve-prefix.py
# to main - then sync. Checks every 10 minutes, for up to 10 hours; past that it syncs and goes on regardless.
C=/diagram/.clones/diagram-supplemental
n=0
while [ $n -lt 60 ]; do
  git -C $C fetch -q origin main >/dev/null 2>&1
  git -C $C cat-file -e origin/main:scripts/reserve-prefix.py 2>/dev/null && break
  n=$((n + 1)); sleep 600
done
exec sh "$(dirname "$0")/sync.sh"
