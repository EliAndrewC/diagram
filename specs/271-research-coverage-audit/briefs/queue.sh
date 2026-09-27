#!/bin/bash
# queue.sh <n> <GROUP> [<GROUP> ...] - feature 271: run write-then-check sessions for inventory groups in queue clone <n>
# (`.clones/<this clone>-<n>`), one group after another, as `scripts/page-queue.sh` does for 250's pages. Each group is
# its write brief, then `<g>-checks.sh`, which makes the check briefs from the write session's handoff when it ends.
# Pull the queue back with `scripts/pull-queue.sh <n>` once it has ended.
set -euo pipefail
N=${1:?usage: queue.sh <n> <GROUP> ...}; shift
ROOT=$(git rev-parse --show-toplevel)
Q="$(dirname "$ROOT")/$(basename "$ROOT")-$N"
REL=specs/271-research-coverage-audit/briefs
if [ -d "$Q/.git" ]; then
  [ -z "$(git -C "$Q" status --porcelain)" ] || { echo "queue.sh: $Q has uncommitted work - a queue is still running, or pull it back first" >&2; exit 2; }
  git -C "$Q" pull -q --ff-only "$ROOT" HEAD
else
  git clone -q "$ROOT" "$Q"
fi
LIST=""
for G in "$@"; do
  g=$(echo "$G" | tr 'A-Z' 'a-z')
  (cd "$Q" && python3 "$REL/gen.py" write "$G" >/dev/null)
  printf '#!/bin/sh\n# the check briefs for group %s, made from its write session'"'"'s handoff when that session ends\nexec python3 %s/%s/gen.py checks %s\n' "$G" "$Q" "$REL" "$G" > "$Q/$REL/$g-checks.sh"
  chmod +x "$Q/$REL/$g-checks.sh"
  LIST="$LIST $REL/$g-write.md then:$REL/$g-checks.sh"
done
git -C "$Q" add -A && git -C "$Q" commit -q -m "271 queue $N: the write briefs for $*" || true
cd "$Q" && exec scripts/page-session.sh "${LIST# }"
