#!/usr/bin/env bash
# test-parts.sh - parts.sh's run_parts leaves nothing in the temp directory, on a normal end and on a TERM of a suite run alone, and
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

# hookrun.sh, the runner of every suite: a run whose runner is gone (SIGKILL, never its trap) leaves its directory to the next run,
# which removes it; a live run's and one of the form before T101 (the GM's pile) stay; a TERM removes the run's own
H="$D/h"; mkdir -p "$H/w" "$H/g" "$H/tmp" "$H/tmp2"
cp "$(dirname "$P")/hookrun.sh" "$H/"
printf '#!/bin/sh\nexit 0\n' > "$H/ok.sh"; printf '#!/bin/sh\nsleep 1\n' > "$H/slow.sh"; chmod +x "$H/ok.sh" "$H/slow.sh"
mkdir -p "$H/tmp/l7r-hooks-suite-x-p99999991.abc/in" "$H/tmp/l7r-hooks-suite-x-p$$.abc" "$H/tmp/l7r-hooks-suite-x.abc" \
  "$H/tmp/l7r-hooks-suite-x-p99999992.abc"
touch -d '4 hours ago' "$H/tmp/l7r-hooks-suite-x-p99999991.abc" "$H/tmp/l7r-hooks-suite-x-p$$.abc" "$H/tmp/l7r-hooks-suite-x.abc"
TMPDIR="$H/tmp" bash "$H/hookrun.sh" "$H/w" "$H/g" ok ok.sh sha
check "a gone runner's directory goes with the next run" '[ ! -e "$H/tmp/l7r-hooks-suite-x-p99999991.abc" ]'
check "a gone runner's directory changed within three hours stays" '[ -d "$H/tmp/l7r-hooks-suite-x-p99999992.abc" ]'
check "a live runner's directory stays" '[ -d "$H/tmp/l7r-hooks-suite-x-p$$.abc" ]'
check "a directory of the form before T101 stays" '[ -d "$H/tmp/l7r-hooks-suite-x.abc" ]'
check "the run removes its own" '[ "$(ls -A "$H/tmp" | wc -l)" -eq 3 ] && [ "$(cat "$H/w/ok.rc")" = ok ]'
TMPDIR="$H/tmp2" bash "$H/hookrun.sh" "$H/w" "$H/g" slow slow.sh sha &
pid=$!
for _ in $(seq 100); do [ -n "$(ls -A "$H/tmp2")" ] && break; timeout 0.05 tail -f /dev/null; done
kill -TERM "$pid"; wait "$pid"
check "a TERM of the runner leaves nothing" '[ -z "$(ls -A "$H/tmp2")" ]'

echo "parts: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
