#!/bin/sh
# A `then:` step before the groups that EDIT existing fragments (feature 269 spec, Edge Cases): feature 265's
# unpushed sweeps edited those fragments, so wait until 265 has landed - its close carries scripts/reserve-prefix.py
# to main - then sync. Checks every 10 minutes with no time limit: the spec holds those groups back until 265 lands,
# so a long wait is a stalled queue for the hourly heartbeat to flag, never a reason to go on (plan D2).
C=/diagram/.clones/diagram-supplemental
while :; do
  git -C $C fetch -q origin main >/dev/null 2>&1
  git -C $C cat-file -e origin/main:scripts/reserve-prefix.py 2>/dev/null && break
  sleep 600
done
exec sh "$(dirname "$0")/sync.sh"
