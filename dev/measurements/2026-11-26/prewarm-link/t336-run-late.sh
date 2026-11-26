#!/bin/bash
# 451 T336: the late cuts (8 to 11 s into an 11 s build) by signal
cd /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work
export T336_FULL=11 T336_LO=8
for arm in "cut1 10 21" "int1 10 22" "kill1 10 23"; do
  set -- $arm
  python3 /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-harness.py $1 $2 $3 /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-results-late.jsonl >> /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-run-late.log 2>&1
  echo "$1 done $(date +%T) load $(cut -d' ' -f1 /proc/loadavg)" >> /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t336-work/t336-run-late.log
done
