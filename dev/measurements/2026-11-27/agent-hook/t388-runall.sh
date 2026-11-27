#!/bin/bash
# t388: every timed run, one after another (never side by side), 20 counted rounds each. Tables: t388-guards.tsv, t388-causes.tsv
cd "$(dirname "$0")" || exit 1
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t388
for c in gp sf rf; do
  python3 t388-time.py t388-guards.tsv 20 $c.PreToolUse:hook $c.PreToolUse:bin $c.PreToolUse:ver $c.PreToolUse:only $c.PostToolUse:hook $c.PostToolUse:bin $c.PostToolUse:only || echo "FAILED guards $c"
done
echo done
