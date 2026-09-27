#!/bin/bash
# page-queue.sh - one page's research queue in a SIBLING clone, so up to three pages run at once (feature 265 FR-010).
#
#   scripts/page-queue.sh <n> <page> <task> [<page> <task> ...]
#
# WHY. A page is independent of another page, but two queues in ONE clone would share its git index and rebuild the
# same assembled pages under each other. So queue <n> works in `.clones/<this clone>-<n>`: cloned from this clone the
# first time, fast-forwarded to this clone's HEAD after that. Its briefs are generated THERE, by its own copy of
# `brief.py`, so the check step reads that clone's commits; its sessions are named after that clone, so the clone
# guard routes them. Several pages given in one call run one after another in the same queue.
# `scripts/pull-queue.sh <n>` brings its commits back when it ends. The prefixes a queue allocates come from
# `make reserve` (a host-wide lock), so two queues never take the same one.
set -euo pipefail

N=${1:-}; shift || true
[ -n "$N" ] && [ $# -ge 2 ] && [ $(( $# % 2 )) -eq 0 ] || { echo "usage: page-queue.sh <n> <page> <task> [<page> <task> ...]" >&2; exit 2; }
ROOT=$(git rev-parse --show-toplevel)
Q="$(dirname "$ROOT")/$(basename "$ROOT")-$N"
if [ -d "$Q/.git" ]; then
  if [ -n "$(git -C "$Q" status --porcelain)" ]; then echo "page-queue: $Q has uncommitted work - a queue is still running there, or pull it back first" >&2; exit 2; fi
  git -C "$Q" pull -q --ff-only "$ROOT" HEAD
else
  git clone -q "$ROOT" "$Q"
  git -C "$Q" config user.name "$(git -C "$ROOT" config user.name)"
  git -C "$Q" config user.email "$(git -C "$ROOT" config user.email)"
fi
BRIEFS=""
while [ $# -ge 2 ]; do
  line=$(cd "$Q/specs/250-close-the-record-checks/measure" && python3 brief.py "$1" "$2" | sed -n 's/^ *make page-session BRIEF="\(.*\)"$/\1/p')
  [ -n "$line" ] || { echo "page-queue: brief.py wrote no queue for $1" >&2; exit 2; }
  BRIEFS="$BRIEFS $line"
  shift 2
done
git -C "$Q" add -A && git -C "$Q" commit -q -m "queue $N: the briefs for its pages" || true
echo "page-queue: queue $N in $Q"
cd "$Q" && exec scripts/page-session.sh "${BRIEFS# }"
