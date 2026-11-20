#!/usr/bin/env bash
# test-parts.1.sh - the first shard of parts.sh's suite (feature 451 T20 split it, plan D17): run_parts leaves nothing in the temp
# directory, on a normal end and on a TERM of a suite run alone, and
# keeps the suite's own EXIT trap (feature 449 T101; the GM 2026-11-11, relayed: "remove it on exit, including failure and interrupt").
# Before T101 a TERM left run_parts' work directory behind; a second `trap ... EXIT` replacing the suite's own was the leak two other
# suites had, so the suite's trap is checked to still run.
set -u
P="$(cd "$(dirname "$0")" && pwd)/parts.sh"
pass=0 fail=0
check() { if eval "$2"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1"; fi; }
D=$(mktemp -d)
trap 'pkill -P $$ 2>/dev/null; rm -rf "$D"' EXIT

# suite <file> <case body>: a suite of two cases dealt into two parts, its own EXIT trap writing $D/own-<file>
suite() {
  printf '%s\n' \
    "source '$P'" \
    "trap 'echo ran > $D/own-$1' EXIT" \
    "case_a() { $2; }" \
    "case_b() { $2; }" \
    "CASES=(case_a case_b); declare -A WEIGHT=()" \
    "run_parts 2" > "$D/$1.sh"
}

# a normal end: nothing left, the suite's trap ran
mkdir "$D/t1"; suite done "true"
TMPDIR="$D/t1" bash "$D/done.sh" > /dev/null 2>&1
check "a normal end leaves nothing" '[ -z "$(ls -A "$D/t1")" ]'
check "the suite's own EXIT trap still runs" '[ -f "$D/own-done" ]'

# a TERM mid-run: the work directory goes, the suite ends 143, its own trap runs
mkdir "$D/t2"; suite term "sleep 5"
TMPDIR="$D/t2" bash "$D/term.sh" > /dev/null 2>&1 &
pid=$!
for _ in $(seq 100); do [ -n "$(ls -A "$D/t2")" ] && break; timeout 0.05 tail -f /dev/null; done
check "the run made its work directory" '[ -n "$(ls -A "$D/t2")" ]'
kill -TERM "$pid"; wait "$pid"; code=$?
check "a TERM ends the suite with 143 ($code)" '[ "$code" = 143 ]'
check "a TERM leaves nothing" '[ -z "$(ls -A "$D/t2")" ]'
check "the suite's own EXIT trap runs on a TERM" '[ -f "$D/own-term" ]'

echo "parts.1: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
