#!/bin/bash
# pull-queue.sh - bring a finished queue's commits back into this clone, and rebuild what is generated (feature 265 FR-010).
#
#   scripts/pull-queue.sh <n>
#
# A local `git pull` from `.clones/<this clone>-<n>` - never a push. The pages this feature regenerates are then
# REBUILT, always, never merged by hand (plan review): a conflict in one of them takes this side and is rebuilt; a
# conflict anywhere else stops here for a person; and whether or not the merge was clean, `make glossary`, `make
# record` and `make citations` run after it and whatever they change is committed.
set -euo pipefail

N=${1:-}
[ -n "$N" ] || { echo "usage: pull-queue.sh <n>" >&2; exit 2; }
ROOT=$(git rev-parse --show-toplevel)
Q="$(dirname "$ROOT")/$(basename "$ROOT")-$N"
[ -d "$Q/.git" ] || { echo "pull-queue: no queue clone at $Q" >&2; exit 2; }
# the check briefs a queue's write session generates are left untracked by the sessions that run them (queue 2 of
# feature 265, the first pull-back); they are the queue's record, so a finished queue's are committed here
if [ -n "$(git -C "$Q" status --porcelain)" ] && [ -z "$(git -C "$Q" status --porcelain | grep -v '^?? specs/[^/]*/briefs/')" ]; then
  git -C "$Q" add specs && git -C "$Q" commit -q -m "queue $N: the check briefs its sessions ran"
fi
[ -z "$(git -C "$Q" status --porcelain)" ] || { echo "pull-queue: $Q has uncommitted work - its queue is still running" >&2; exit 2; }
[ -z "$(git -C "$ROOT" status --porcelain)" ] || { echo "pull-queue: commit this clone's work first" >&2; exit 2; }

# the files this feature regenerates - rebuilt below, so either side of a conflict in them will do
GENERATED='(^|/)research/[^/]+\.html$|(^|/)research/cities/[^/]+\.html$|(^|/)research/citations/|(^|/)research/SOURCES\.html$|(^|/)assets/glossary\.(json|js)$|(^|/)research/assets/glossary'
# the run and bypass logs are NOT in it: nothing rebuilds them, so taking one side would lose the other's entry
# (plan review round 2) - a conflict in one stops for a person like any hand-written file
if ! git -C "$ROOT" pull -q --no-rebase --no-edit "$Q" HEAD; then
  others=$(git -C "$ROOT" diff --name-only --diff-filter=U | grep -Ev "$GENERATED" || true)
  if [ -n "$others" ]; then
    echo "pull-queue: conflicts outside the generated pages - resolve these by hand, then re-run the rebuild:" >&2
    printf '  %s\n' $others >&2
    exit 1
  fi
  git -C "$ROOT" diff --name-only --diff-filter=U | while read -r f; do git -C "$ROOT" checkout -q --ours -- "$f"; git -C "$ROOT" add -- "$f"; done
  git -C "$ROOT" commit -q --no-edit
fi
# PULL_QUEUE_REBUILD replaces the three targets in the tests, which have no Makefile
if [ -n "${PULL_QUEUE_REBUILD:-}" ]; then ( cd "$ROOT" && eval "$PULL_QUEUE_REBUILD" ); else
  ( cd "$ROOT/.claude/skills/diagram" && make glossary >/dev/null && make record >/dev/null && make citations >/dev/null ); fi
if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
  git -C "$ROOT" add -A && git -C "$ROOT" commit -q -m "queue $N pulled back: the generated pages rebuilt"
fi
echo "pull-queue: queue $N is in $(basename "$ROOT") at $(git -C "$ROOT" log --oneline -1)"
