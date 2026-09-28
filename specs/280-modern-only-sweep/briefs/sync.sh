#!/bin/sh
# A `then:` step between groups (feature 280, as 269's sync.sh): merge main into the clone so the next session sees what
# the other research sessions landed. A conflict is aborted and the queue carries on.
# Extra briefs: each briefs/extra/*.md not yet queued is queued ONCE here (printing a brief's path queues it) - how a
# finding another session owes a 280 section reaches the running queue without editing the clone under it.
C=/diagram/.clones/diagram-supplemental-2
D=$(dirname "$0")
queued=0
for b in "$D"/extra/*.md; do
  [ -f "$b" ] || continue
  m="$C/.git/page-sessions/extra-280-$(basename "$b").queued"
  [ -e "$m" ] && continue
  mkdir -p "$C/.git/page-sessions"; touch "$m"; echo "$b"; queued=1
done
[ $queued = 1 ] && exit 0
[ -z "$(git -C $C status --porcelain --untracked-files=no)" ] || exit 0
git -C $C pull -q --no-rebase --no-edit origin main >/dev/null 2>&1 || git -C $C merge --abort >/dev/null 2>&1
exit 0
