#!/usr/bin/env bash
# closing-checks.sh - `make closing-checks` (feature 451 T55): make static, make hooks-test and make quick at once, one combined result.
#
# WHY: after a builder's last code edit its closing checks ran one after another - 63 min in the foreground and 101 min idle on its own
# background runs over 39 builders' transcripts, beside 158 min of model time writing the plan section, running make decide and writing
# the report, none of which needs a check's result (measured 2026-11-21). Started with run_in_background the moment the code is done,
# the three run side by side while the builder writes.
#
# SAFE SIDE BY SIDE (measured 2026-11-21, T55's plan section): `make done` already runs `make static` beside the tests; the three share
# no scratch path (hooks-test's work dir is its own mktemp, static's one temp file, the rust build's stderr in l7r-gate.sh, is a mktemp of its own run, and quick writes none); hooks-test runs no rust
# check in the clone's target directory (its suites' cargo is a fake, their targets their own), so the run lock of 451 T23, which
# counts every check under one outermost `make` as one run, has nothing of hooks-test's to keep apart; the launchers' builds of the
# tool binaries are cargo's, under cargo's own lock.
#
# Each check's output goes to <git dir>/closing-checks/<check>.log; the table names each verdict, its seconds and its log, the tail of
# each red one follows, and the exit is 1 if any is red. A TERM or INT stops all three. CLOSING_MAKE names the make (the suite's stub).
set -u
mk=${CLOSING_MAKE:-make}
dir=${CLOSING_CHECKS_DIR:-$(git rev-parse --absolute-git-dir)/closing-checks}
checks=(static hooks-test quick)
mkdir -p "$dir" || exit 2
pids=()

# every process under pid, deepest first, so a make's recipe shells and their cargo go with it
tree() { local c; for c in $(pgrep -P "$1" 2>/dev/null); do tree "$c"; done; echo "$1"; }
stop() {
  local p
  for p in "${pids[@]}"; do kill -TERM $(tree "$p") 2>/dev/null; done
  printf '\nclosing-checks: stopped - each log is under %s\n' "$dir" >&2
  exit 130
}
trap stop INT TERM

t0=$(date +%s)
for c in "${checks[@]}"; do
  rm -f "$dir/$c.exit"
  ( s=$(date +%s); "$mk" --no-print-directory "$c" > "$dir/$c.log" 2>&1 < /dev/null; rc=$?
    printf '%s %s\n' "$rc" "$(( $(date +%s) - s ))" > "$dir/$c.exit" ) &
  pids+=($!)
done
# `wait` returns early on a trapped signal, so the trap runs while the checks run
for p in "${pids[@]}"; do wait "$p"; done

red=0
printf '\n\033[1mclosing-checks\033[0m (make static, make hooks-test, make quick at once, %ss wall)\n' "$(( $(date +%s) - t0 ))"
for c in "${checks[@]}"; do
  read -r rc secs < "$dir/$c.exit" 2>/dev/null || { rc=missing; secs=?; }
  if [ "$rc" = 0 ]; then v=GREEN; else v="RED (exit $rc)"; red=$((red + 1)); fi
  printf '  %-11s %-15s %5ss  %s\n' "$c" "$v" "$secs" "$dir/$c.log"
done
for c in "${checks[@]}"; do
  read -r rc _ < "$dir/$c.exit" 2>/dev/null || rc=missing
  [ "$rc" = 0 ] && continue
  printf '\n\033[1m== %s: the last 25 lines of %s ==\033[0m\n' "$c" "$dir/$c.log"
  tail -n 25 "$dir/$c.log"
done
# each run recorded, its outcome the combined one (feature 406 T03; CLOSING_GATE is the suite's stub)
record() { "${CLOSING_GATE:-$(dirname "${BASH_SOURCE[0]}")/l7r-gate.sh}" log usage --tool closing-checks --kind check --outcome "$1" 2>/dev/null || true; }
if [ "$red" -gt 0 ]; then
  printf '\n\033[1mclosing-checks: RED\033[0m - %s of %s red; fix them all, then run `make closing-checks` once more (in the background).\n' "$red" "${#checks[@]}"
  record refused
  exit 1
fi
record passed
printf '\n\033[1mclosing-checks: GREEN\033[0m - all three; a plan section edited after this run started is covered by `make quick` (seconds).\n'
