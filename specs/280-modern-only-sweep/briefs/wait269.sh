#!/bin/sh
# A `then:` step before the first group that edits a section feature 269 rewrote (feature 280 spec, Edge Cases; plan
# D3): 269's research is committed in its clone and not yet on main, so wait until the last commit there that touched
# the record is on origin/main, then sync. Checks every 10 minutes, for up to 24 hours. If 269 has still not landed, it
# STOPS the queue - it never goes on into the 269-held groups: it prints a brief path that does not exist, which the
# runner refuses ("STOPPED ...: no such brief" in the run log) and clears the queue. The rest is queue-269.txt, to be
# started with `make page-session BRIEF="$(cat .../queue-269.txt)"` once 269 has landed (plan D3).
C=/diagram/.clones/diagram-supplemental-2
S=/diagram/.clones/diagram-supplemental
n=0
while [ $n -lt 144 ]; do
  git -C $C fetch -q origin main >/dev/null 2>&1
  h=$(git -C $S log -1 --format=%H -- .claude/skills/diagram/research 2>/dev/null)
  [ -n "$h" ] && git -C $C merge-base --is-ancestor "$h" origin/main 2>/dev/null && break
  n=$((n + 1)); sleep 600
done
if [ $n -ge 144 ]; then
  echo "$(dirname "$0")/STOPPED-269-has-not-landed-restart-with-queue-269.txt"
  exit 0
fi
exec sh "$(dirname "$0")/sync.sh"
