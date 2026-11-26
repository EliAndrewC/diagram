#!/bin/bash
# 451 T336: the arms, one after another, one cargo at a time
cd /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work
export T336_FULL=20
for arm in "control 20 11" "cut1 20 12" "cut2 20 13" "cut2inc0 20 14" "int1 10 15" "kill1 10 16"; do
  set -- $arm
  python3 /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-harness.py $1 $2 $3 /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-results.jsonl >> /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-run-all.log 2>&1
  echo "$1 done $(date +%T) load $(cut -d' ' -f1 /proc/loadavg)" >> /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-run-all.log
done
