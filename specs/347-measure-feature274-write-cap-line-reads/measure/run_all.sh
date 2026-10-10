#!/usr/bin/env bash
# Feature 347: every figure in 274's research.md R3, from the transcripts. Writes results.txt beside it.
# sessions-*.json are rebuilt by collect.py and not committed (they are derived, ~0.9 MB); the groups-*.json are.
set -euo pipefail
cd "$(dirname "$0")"
{
  python3 collect.py r1
  python3 collect.py post
  for sel in "r1 2026-09-27T22:30" "r1 2026-09-27T22:30 269" "post - 269" "post - 269,280,291,317" "post - 292" "post - 319" "post -"; do
    echo; echo "=== analyze.py $sel"
    # shellcheck disable=SC2086
    python3 analyze.py $sel
  done
  echo; echo "=== split.py"; python3 split.py
  for sel in "r1 2026-09-27T22:30" "post - 269,280,291,317" "post -"; do
    echo; echo "=== coord.py $sel"
    # shellcheck disable=SC2086
    python3 coord.py $sel
  done
  echo; echo "=== continuations in every clone's run logs"
  cat /diagram/.clones/*/.git/page-sessions/run-*.log | grep -c '^continued' || true
} > results.txt 2>&1
echo "results.txt written"
