#!/bin/bash
# t388: the throwaway world an Agent call's hooks are timed in - T373's shape (dev/measurements/2026-11-26/edit-hook/t373-results.md),
# built afresh from tonight's mirror and clone. Everything under $S; the real trees are only READ (git clone, cp).
#   bash t388-build.sh     (once; about 4 GB)
set -euo pipefail
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t388
REAL=/diagram/.clones/diagram-backlog
W=$S/w/diagram
C=$W/.clones/diagram-backlog
mkdir -p "$S"/{gl,ms,payloads,home/.claude/projects/-diagram,target,gate/tool,pristine}
# the mirror stand-in, at the mirror's HEAD (the binary below is built from it), and the clone, at the real clone's HEAD
[ -d "$W/.git" ] || git clone -q /diagram "$W"
[ -d "$C/.git" ] || git clone -q "$REAL" "$C"
# the real clone's non-git state (event logs, the checks state, check passes, caches, the pool registry ...), copied into the sandbox's .git
for f in "$REAL"/.git/*; do
  b=${f##*/}
  case "$b" in HEAD|config|index|refs|objects|logs|hooks|info|packed-refs|description|FETCH_HEAD|ORIG_HEAD|COMMIT_EDITMSG|worktrees|modules|branches|*.lock) continue ;; esac
  cp -a "$f" "$C/.git/"
done
[ -f "$REAL/.specify/feature.json" ] && cp "$REAL/.specify/feature.json" "$C/.specify/feature.json"
# the claim map: every real entry, those naming the real clone re-aimed at the sandbox's, and the sandbox session's own
mkdir -p "$W/.clones/.session-clones"
cp -a /diagram/.clones/.session-clones/. "$W/.clones/.session-clones/"
grep -lx "$REAL" "$W"/.clones/.session-clones/* 2>/dev/null | while read -r m; do printf '%s\n' "$C" > "$m"; done
printf '%s\n' "$C" > "$W/.clones/.session-clones/t388-sess-0001"
# the scratch home: the sessions directory and the coordinating session's transcript (its /rename names diagram-backlog)
cp -a ~/.claude/sessions "$S/home/.claude/"
cp ~/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl "$S/home/.claude/projects/-diagram/t388-sess-0001.jsonl"
# the binaries live hooks run (the mirror's), COPIED and stamped newer than the sandbox's sources so no launcher builds; the gate's
# launcher takes L7R_GATE_TARGET, and L7R_GATE_CARGO=/bin/false (t388-env.sh) makes any build attempt fail where it would be seen
cp ~/.cache/l7r-cargo-target/diagram/l7r-guard.good "$S/target/l7r-guard.good"
cp ~/.cache/l7r-cargo-target/diagram/tool/l7r-gate "$S/gate/tool/l7r-gate"
touch "$S/target/l7r-guard.good" "$S/gate/tool/l7r-gate"
# the pristine state every timed run starts from (t388-time.py restores these before each run, outside its clock)
cp -a "$C/.git/checks-open.json" "$C/.git/check-passes.jsonl" "$S/pristine/"
du -sh "$S"
