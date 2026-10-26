#!/usr/bin/env bash
# replay-cover.sh - m:cover-replay (feature 430 T03, SC-002): the new cover_changed.py on each in-scope coverage red of
# 2026-10-26, against a gate baseline of the red's own base. For each red: a detached worktree at its base (the last landing
# commit before it, as replay-reds.sh finds it) runs `make done` to record the baseline it had, then moves to the red's commit
# and runs `make cover-changed BASE=<base>` with the new check, timed. A baseline taken from another day's tree does not do: its
# coverage paths name another tree and its contexts name tests the red had deleted (both tried, 2026-10-26).
#     bash specs/430-faster-landings/replay-cover.sh [red ...]
set -u
ROOT="$(git rev-parse --show-toplevel)"
NEW="$ROOT/scripts/gates/cover_changed.py"
REDS="${*:-31f739f5d d92ff2c90 39ea51383}"
for red in $REDS; do
  base=$(git -C "$ROOT" log --format=%h -1 --grep='ticked (make land)' --grep='Tooling from' "$red~1")
  wt=$(mktemp -d)/wt
  git -C "$ROOT" worktree add -q --detach "$wt" "$base"
  ( cd "$wt" && make --no-print-directory done > "$wt.base-gate.log" 2>&1 )
  printf '%s: base %s gate %s\n' "$red" "$base" "$(tail -1 "$wt.base-gate.log" | cut -c1-80)"
  git -C "$wt" checkout -q --detach "$red"
  cp "$NEW" "$wt/scripts/gates/cover_changed.py"
  start=$(date +%s)
  out=$(cd "$wt" && make --no-print-directory cover-changed BASE="$base" 2>&1 | grep -E '^cover-changed: l7r|Error|REFUSED' | cut -c1-400)
  printf '  check %ss\n%s\n' "$(( $(date +%s) - start ))" "${out:-  (named nothing)}"
  git -C "$ROOT" worktree remove --force "$wt"
done
