#!/bin/bash
# t373, second pass (the first pass's size sweep and tool rows ran at load 10 to 30): the size sweep by the two guards alone, the builder's
# worktree, and Bash and Agent by guard. One after another, 20 counted rounds each.
cd "$(dirname "$0")" || exit 1
for st in dirty clean; do for se in none tenth half sess; do python3 t373-time.py t373-sizes2.tsv 20 $st $se edit-doc.PreToolUse:guards=clone-sync,event-log || echo "FAILED sizes $st $se"; done; done
python3 t373-time.py t373-worktree.tsv 20 dirty wt edit-doc.PreToolUse:all edit-doc.PostToolUse:all edit-rust.PreToolUse:all edit-plan.PreToolUse:all write-new.PreToolUse:all write-new.PostToolUse:all || echo "FAILED wt"
python3 t373-time.py t373-tools2.tsv 20 dirty sess bash-true.PreToolUse:all bash-true.PostToolUse:all agent.PreToolUse:all agent.PostToolUse:all read.PreToolUse:all grep.PreToolUse:all read.PostToolUse grep.PostToolUse edit-doc.PreToolUse edit-doc.PreToolUse@realhome || echo "FAILED tools"
python3 t373-time.py t373-tools2.tsv 20 dirty wt bash-true.PreToolUse:all bash-true.PostToolUse || echo "FAILED tools wt"
echo done
