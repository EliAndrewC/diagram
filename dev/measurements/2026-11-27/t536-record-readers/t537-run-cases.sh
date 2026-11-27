#!/bin/bash
# t537: run the T536 reader cases on the copy, one ONLY substring each; $1 = output file
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t537-after-copy
R=/diagram/.clones/diagram-backlog-t271/dev/measurements/2026-11-27/t536-record-readers/t536-readers-run.py
F=$S/repo/specs/451-time-retro-and-efficiency
: > "$1"
for c in "plan-section T=T537" "decide F=451" "plan-delta" "make queue" "builder-next" "speckit-todo" "T=T499" "task-add"; do
  ONLY="$c" T536_OPEN=T537 RUNS=${RUNS:-3} python3 -I "$R" "$S" >> "$1" 2>&1
  cp $S/flat/tasks.md $S/flat/plan.md $F/
  rm -f $S/repo/.git/task-add-reserved* 2>/dev/null
done
echo "END" >> "$1"
