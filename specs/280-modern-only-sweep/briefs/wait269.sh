#!/bin/sh
# A `then:` step before the first group that edits a section feature 269 rewrote (feature 280 spec, Edge Cases; plan
# D3): 269's research is committed in its clone and not yet on main, so wait until the last commit there that touched
# the record is on origin/main, then sync. Checks every 10 minutes, for up to 10 hours; past that it syncs and goes on,
# and the write brief's claims check (make lines on RESEARCH-CLAIMS.md) keeps it off any section still held.
C=/diagram/.clones/diagram-supplemental-2
S=/diagram/.clones/diagram-supplemental
n=0
while [ $n -lt 60 ]; do
  git -C $C fetch -q origin main >/dev/null 2>&1
  h=$(git -C $S log -1 --format=%H -- .claude/skills/diagram/research 2>/dev/null)
  [ -n "$h" ] && git -C $C merge-base --is-ancestor "$h" origin/main 2>/dev/null && break
  n=$((n + 1)); sleep 600
done
exec sh "$(dirname "$0")/sync.sh"
