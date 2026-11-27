#!/bin/bash
# t373: every timed run, one after another (never side by side), 20 counted rounds each. Tables: t373-guards.tsv, t373-sizes.tsv, t373-tools.tsv
cd "$(dirname "$0")" || exit 1
E="edit-doc.PreToolUse:all edit-doc.PostToolUse:all edit-rust.PreToolUse:all edit-rust.PostToolUse:all edit-plan.PreToolUse:all edit-plan.PostToolUse:all write-new.PreToolUse:all write-new.PostToolUse:all"
for st in dirty clean; do python3 t373-time.py t373-guards.tsv 20 $st sess $E || echo "FAILED guards $st"; done
python3 t373-time.py t373-guards.tsv 20 dirty sub edit-doc.PreToolUse:all edit-doc.PostToolUse:all edit-rust.PreToolUse:all || echo "FAILED guards sub"
for st in dirty clean; do for se in none tenth half sess; do python3 t373-time.py t373-sizes.tsv 20 $st $se edit-doc.PreToolUse:full || echo "FAILED sizes $st $se"; done; done
python3 t373-time.py t373-tools.tsv 20 dirty sess bash-true.PreToolUse bash-true.PostToolUse read.PreToolUse read.PostToolUse grep.PreToolUse grep.PostToolUse agent.PreToolUse agent.PostToolUse edit-doc.PreToolUse edit-doc.PreToolUse@realhome || echo "FAILED tools"
echo done
