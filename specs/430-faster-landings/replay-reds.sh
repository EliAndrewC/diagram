#!/usr/bin/env bash
# replay-reds.sh - m:coverage-reds-replay, re-runnable (feature 430 FR-003a; the spec review's round-3 and round-4 notes).
# For each of 2026-10-26's coverage reds: the base is the last landing commit before it ('ticked (make land)' or
# 'Tooling from'); each named line is ADDED (inside a + hunk of base..red) or EXISTING, and its module IN the delta or not.
set -u
ROOT="$(git rev-parse --show-toplevel)"
# red | path | first line | last line ("-" for a red that names a module, not lines)
REDS='31f739f5d l7r/diagram/hamletgen/ways/settle/ends.py 321 321
31f739f5d l7r/diagram/hamletgen/ways/settle/shapes.py 161 167
31f739f5d l7r/diagram/hamletgen/ways/tree.py 404 404
d92ff2c90 l7r/diagram/hamletgen/ways/tree.py 298 300
7f209090b l7r/diagram/hamletgen/ways/law.py 933 933
449e7df7b l7r/diagram/hamletgen/ways/checks.py 141 141
39ea51383 l7r/diagram/pipeline/gencache.py 227 228
39ea51383 l7r/diagram/pipeline/gencache.py 238 241
9a157cc4b l7r/diagram/tools/cohort_audit.py - -'
printf '%s\n' "$REDS" | while read -r red path a b; do
  base=$(git -C "$ROOT" log --format=%h -1 --grep='ticked (make land)' --grep='Tooling from' "$red~1")
  if git -C "$ROOT" diff --name-only "$base" "$red" -- "$path" | grep -q .; then indelta=in-delta; else indelta=NOT-in-delta; fi
  if [ "$a" = - ]; then printf '%s %s %s (names no lines)\n' "$red" "$path" "$indelta"; continue; fi
  added=$(git -C "$ROOT" diff -U0 "$base" "$red" -- "$path" | awk -v a="$a" -v b="$b" '
    /^@@/ { split($3, n, ","); s = substr(n[1], 2) + 0; c = (n[2] == "" ? 1 : n[2] + 0); if (s <= b && s + c - 1 >= a && c > 0) hit = 1 }
    END { print (hit ? "ADDED" : "EXISTING") }')
  printf '%s %s:%s-%s %s %s\n' "$red" "$path" "$a" "$b" "$added" "$indelta"
done
