#!/bin/sh
# A `then:` step before EVERY group that edits an existing fragment (feature 269 spec, Edge Cases): feature 265's
# unpushed sweeps edited those fragments, so wait until THIS CLONE has 265's landing - its close, 1c2797c99, is an
# ancestor of HEAD - not merely until origin/main has it: sync.sh exits without merging while the tree is dirty, so
# main carrying 265 is not the clone carrying it (plan D2, the plan review's round 2). Checks every 10 minutes with
# no time limit: a long wait is a stalled queue for the hourly heartbeat to flag, never a reason to go on.
C=/diagram/.clones/diagram-supplemental
HAS265=1c2797c99
while :; do
  git -C $C merge-base --is-ancestor $HAS265 HEAD 2>/dev/null && exit 0
  git -C $C fetch -q origin main >/dev/null 2>&1
  git -C $C cat-file -e origin/main:scripts/reserve-prefix.py 2>/dev/null && sh "$(dirname "$0")/sync.sh"
  git -C $C merge-base --is-ancestor $HAS265 HEAD 2>/dev/null && exit 0
  sleep 600
done
