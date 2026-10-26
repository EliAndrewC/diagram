#!/usr/bin/env bash
# time-push-gates.sh - m:push-gates-records-only (feature 430 T04, SC-003): the three push gates timed on a records-only delta - a
# detached worktree at origin/main with one run record committed, this clone's gates copied in.
set -u
ROOT="$(git rev-parse --show-toplevel)"
wt=$(mktemp -d)/rec
git -C "$ROOT" worktree add -q --detach "$wt" origin/main
cp "$ROOT"/scripts/gates/*.sh "$ROOT/scripts/gates/push_gates.py" "$wt/scripts/gates/"
mkdir -p "$wt/dev/run-log/2026-10" && echo '{}' > "$wt/dev/run-log/2026-10/sc003.json"
git -C "$wt" add -A && git -C "$wt" -c user.name=t -c user.email=t@t commit -qm "a record"
for g in claims-gate entry-gate cohort-gate; do
  s=$(date +%s.%N); out=$(cd "$wt" && "./scripts/gates/$g.sh" 2>&1 | tail -1)
  printf '%s %.2fs: %s\n' "$g" "$(echo "$(date +%s.%N) - $s" | bc)" "$out"
done
git -C "$ROOT" worktree remove --force "$wt"
