#!/bin/sh
# A `then:` step between groups (feature 269): merge main into the clone so the next session sees what the other
# research sessions landed. A conflict is aborted and the queue carries on.
# Extra briefs (2026-09-27): each briefs/extra/*.md not yet queued is queued ONCE here (printing a brief's path queues
# it) - how a finding another session owes a 269 section reaches the running queue without editing the clone under it.
# The first was W1's uncommitted edits (w1-finish.md, queued by its own marker).
C=/diagram/.clones/diagram-supplemental
D=$(dirname "$0")
M=$C/.git/page-sessions/w1-finish-queued
if [ ! -e "$M" ] && git -C $C status --porcelain -- .claude/skills/diagram/research/sources/010-works-cited/ .claude/skills/diagram/research/water/ | grep -q '10[4-6][0-9]0-\|water/'; then
  touch "$M"; echo "$D/w1-finish.md"; exit 0
fi
queued=0
for b in "$D"/extra/*.md; do
  [ -f "$b" ] || continue
  m="$C/.git/page-sessions/extra-$(basename "$b").queued"
  [ -e "$m" ] && continue
  touch "$m"; echo "$b"; queued=1
done
[ $queued = 1 ] && exit 0
[ -z "$(git -C $C status --porcelain --untracked-files=no)" ] || exit 0
git -C $C pull -q --no-rebase --no-edit origin main >/dev/null 2>&1 || git -C $C merge --abort >/dev/null 2>&1
exit 0
