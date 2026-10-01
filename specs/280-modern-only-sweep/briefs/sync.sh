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
L=/diagram/.clones/.tools/logs/sync-280.log
# 2026-09-29: this step used to skip a dirty tree and abort a conflicting merge SILENTLY, and the sweep drifted 514
# commits behind main unseen. Every skip and abort is now logged, and the driver stops on them.
# Assembled output a session regenerated but did not commit (research/<page>.html, citations/, SOURCES.html, the glossary
# builds) is derivable, so it is committed here rather than blocking the merge (2026-09-29: V1's check left SOURCES.html).
GEN='^\.claude/skills/diagram/(research/[a-z-]+\.html|research/contents.json#cities[a-z-]+\.html|research/citations/.*|research/SOURCES\.html|research/assets/glossary(\.js|-variants\.txt)|l7r/diagram/interactive/assets/glossary\.json)$'
dirty=$(git -C $C status --porcelain --untracked-files=no | cut -c4-)
if [ -n "$dirty" ] && [ -z "$(printf '%s\n' "$dirty" | grep -Ev "$GEN")" ]; then
  printf '%s\n' "$dirty" | xargs git -C $C add -- && git -C $C commit -q -m "280: assembled pages a session regenerated and left uncommitted" && echo "$(date -u +%FT%TZ) committed leftover assembled pages" >> $L
fi
if [ -n "$(git -C $C status --porcelain --untracked-files=no)" ]; then echo "$(date -u +%FT%TZ) SKIPPED: tracked edits left uncommitted: $(git -C $C status --porcelain --untracked-files=no | cut -c4- | tr '\n' ' ' | cut -c1-200)" >> $L; exit 0; fi
if git -C $C pull -q --no-rebase --no-edit origin main >/dev/null 2>&1; then echo "$(date -u +%FT%TZ) merged main" >> $L; else git -C $C merge --abort >/dev/null 2>&1; echo "$(date -u +%FT%TZ) ABORTED: merge conflict with main" >> $L; fi
exit 0
