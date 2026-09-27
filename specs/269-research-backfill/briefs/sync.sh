#!/bin/sh
# A `then:` step between groups (feature 269): merge main into the clone so the next session sees what the other
# research sessions landed. A conflict is aborted and the queue carries on.
# 2026-09-27: W1's check left source-applicability edits to the water registry uncommitted, failing two water tests.
# Once, when they are still there, this step queues w1-finish.md (printing a brief's path queues it) and skips the merge.
C=/diagram/.clones/diagram-supplemental
M=$C/.git/page-sessions/w1-finish-queued
if [ ! -e "$M" ] && git -C $C status --porcelain -- .claude/skills/diagram/research/sources/010-works-cited/ .claude/skills/diagram/research/water/ | grep -q '10[4-6][0-9]0-\|water/'; then
  touch "$M"; echo "$(dirname "$0")/w1-finish.md"; exit 0
fi
[ -z "$(git -C $C status --porcelain --untracked-files=no)" ] || exit 0
git -C $C pull -q --no-rebase --no-edit origin main >/dev/null 2>&1 || git -C $C merge --abort >/dev/null 2>&1
exit 0
