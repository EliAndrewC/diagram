#!/usr/bin/env bash
# hookrun.sh - run ONE guard suite, for the parallel `hooks-test` (feature 172).
#
# Usage: hookrun.sh <work-dir> <gitdir> <guard> <suite> <sha>          run one job: a suite, or one shard of a split suite
#        hookrun.sh --jobs <dir> <suite>...                              each suite's job files: `<suite> <job>...` a line
#        hookrun.sh --orphans <dir> <suite>...                           every shard whose suite is none of these (exit 1 if any)
#        hookrun.sh --close <work-dir> <gitdir> <guard> <sha> <shard>... stamp a split suite green when every shard's job is
#
# WHY THIS EXISTS: `hooks-test` ran its 21 suites one after another - 94 s, against 17 s for the
# entire 2,286-test Python suite, which pytest runs in parallel. When a shared helper changes, the
# derived dependency set is still 19-20 suites (`guardlog.sh` calls `hookmatch.py`), so the
# dependency refinement cannot help the common case and concurrency is the only thing that does.
#
# WHY A SEPARATE SCRIPT rather than a subshell in the Makefile: each job needs its own log file and
# its own exit-code file, and a recipe line that already carries three levels of quoting is where
# that goes wrong silently. It also makes the unit testable on its own.
#
# The stamp is written HERE, by the job, and only on success - so a suite that goes green in a run
# where another fails is still recorded green, exactly as the serial version did.
set -uo pipefail

# THE SHARD FORM (feature 451 T20, plan D17): a suite `test-<name>.sh` may be split into `test-<name>.<k>.sh` (k all digits) beside
# nothing else of that name; each shard is a job of its own, so one long suite no longer holds every run's wall time:
# l7r-gate.sh 38.3 s and entry-gate.sh 34.0 s of a 40.8 s full run, measured 2026-11-20 (HOOKS_ALL=1 make hooks-test, its "ran" line).
# A shard's job writes only its own .rc, .log, .s and .reads under `<guard>.<k>`; `--close`, after the fan-out, stamps the suite - its
# sha, its trace and its shard list - only when every shard's job is ok: one stamp a suite, as `trace stamp` rewrites its trace whole.
# No fork per name: `make hooks-test` asks --jobs for every suite before the fan-out, so one call takes them all;
# one call per suite cost 6.9 s for 57 suites on a loaded host, measured 2026-11-20 (57 single-suite --jobs calls beside a full run).
shard_k() { SK=${1%.sh}; SK=${SK##*.}; case $SK in '' | *[!0-9]*) return 1 ;; esac; }
shards_of() { local f; local -a by=(); for f in "$1/${2%.sh}".*.sh; do [ -f "$f" ] && shard_k "$f" && by[10#$SK]=${f##*/}; done; SH="${by[*]}"; }
case ${1:-} in
--jobs)
  # one line a suite: `<suite> <job>...`, the suite alone where it has no job; a suite beside its shards is `<suite> !`
  dir=${2:?dir}; shift 2
  for suite in "$@"; do
    shards_of "$dir" "$suite"
    if [ -n "$SH" ] && [ -f "$dir/$suite" ]; then
      printf '\n\033[1mSUITE AND SHARDS BOTH: %s beside %s\033[0m\n' "$suite" "$SH" >&2
      printf 'A suite is one file or its shards (feature 451 D17), never both: the runner would run one and leave the other.\n' >&2
      printf '  fix: fold the shards back into %s, or move its cases into the shards and remove it\n\n' "$suite" >&2
      printf '%s !\n' "$suite"
    elif [ -n "$SH" ]; then printf '%s %s\n' "$suite" "$SH"
    elif [ -f "$dir/$suite" ]; then printf '%s %s\n' "$suite" "$suite"
    else printf '%s\n' "$suite"; fi
  done
  exit 0 ;;
--orphans)
  dir=${2:?dir}; shift 2; bad=""
  for f in "$dir"/test-*.*.sh; do
    [ -f "$f" ] && shard_k "$f" || continue
    s=${f##*/}; s=${s%.*.sh}.sh
    case " $* " in *" $s "*) ;; *) bad="$bad ${f##*/}" ;; esac
  done
  [ -z "$bad" ] && exit 0
  for f in $bad; do
    printf '\n\033[1mSHARD WITHOUT ITS SUITE: %s is a shard of %s, a suite no guard on the roster owns\033[0m\n' "$f" "${f%.*.sh}.sh"
    printf 'Nothing would ever run it (feature 451 D17: a shard is test-<name>.<k>.sh of a guard <name> make hooks-test runs).\n'
    printf '  fix: rename it test-<guard>.<k>.sh after the guard it tests, or remove it\n'
  done
  exit 1 ;;
--close)
  WORK=${2:?work dir}; GITDIR=${3:?gitdir}; GUARD=${4:?guard}; SHA=${5:?sha}; shift 5
  [ "$#" -gt 0 ] || exit 1
  for s in "$@"; do shard_k "$s" && [ "$(cat "$WORK/$GUARD.$SK.rc" 2>/dev/null)" = ok ] || exit 1; done
  mkdir -p "$GITDIR/hooks-test" && printf '%s' "$SHA" > "$GITDIR/hooks-test/$GUARD" && printf '%s\n' "$@" > "$GITDIR/hooks-test/$GUARD.jobs"
  if [ -n "${HOOKS_SHIM:-}" ]; then
    for s in "$@"; do shard_k "$s" && cat "$WORK/$GUARD.$SK.reads" 2>/dev/null; done > "$WORK/$GUARD.reads"
    "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../scripts/hooks/l7r-guard.sh" trace stamp "$GITDIR" "$GUARD" "$WORK/$GUARD.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  fi
  exit 0 ;;
esac

WORK=${1:?work dir}; GITDIR=${2:?gitdir}; GUARD=${3:?guard}; SUITE=${4:?suite}; SHA=${5:?sha}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# a shard's job is `<guard>.<k>`: its own log, rc, seconds and reads; its suite's stamp waits for --close
if shard_k "$SUITE"; then K=$SK; ID=$GUARD.$K; else K=""; ID=$GUARD; fi

# A SUITE GETS AN EMPTY STDIN (feature 449 T054): a case that runs the guard binary with no input of its own inherited this shell's, which in a tool's shell is a socket that never closes, and the binary reads to its end (hung 10 minutes, 2026-11-08).
t0=${EPOCHREALTIME/,/.}
# GUARD_EDIT_OK: 405 batch 8 - A SUITE RUNS WITH NO SESSION'S ESCAPE SET: `PLAN_REVIEW_OK=... make land` carried the escape through
# `make done` into every suite, and sync-with-main's "it fires" cases came back escaped (rc 0 where 1 was asserted). Each
# `*_OK` variable the session set is cleared here; a case that tests an escape sets its own.
while IFS="=" read -r name _; do case "$name" in *_OK) unset "$name" 2>/dev/null ;; esac; done < <(env)
# GUARD_EDIT_OK: feature 383 amendment 4 - beside other suites a split suite runs in at most PARTS_MAX parts (make hooks-test sets it from the cores and the suites running; two when run without it): eight
# suites of eight parts each hit the containers' shared 10 GB memory cap (2026-10-17). A suite run alone keeps its own count.
export PARTS_MAX=${PARTS_MAX:-2}
# THE LEAK PIN (feature 449 T101): each suite runs with its own TMPDIR, and anything it leaves there fails it, by name - the checks
# and tests that never removed their scratch directories left about 329,000 of them, roughly 126 GB, in the GM's /tmp (2026-11-11).
# It sits under the temp directory itself, so a guard that knows a fixture by its /tmp/ path still does. A SIGKILL cannot be
# caught, so a killed suite's own traps never run: this runner removes the directory whole after the suite, on every path out of it,
# an INT or a TERM exiting through it after stopping the suite; and a runner stopped by SIGKILL, whose trap never ran, leaves its
# directory to the next run, which removes every l7r-hooks-suite-*-p<pid>.* whose pid is gone and which has not changed in three hours
# (the GM 2026-11-11: "don't touch dirs younger than a few hours (a running gate may own them)" - a killed runner's suite can still be
# running in it); directories of the form before T101 are left to the GM's laptop session.
for d in "${TMPDIR:-/tmp}"/l7r-hooks-suite-*-p[0-9]*.*; do
  p=${d##*-p}; p=${p%%.*}
  case $p in '' | *[!0-9]*) continue ;; esac
  [ -d "$d" ] && [ ! -e "/proc/$p" ] && [ -n "$(find "$d" -maxdepth 0 -mmin +180)" ] && rm -rf "$d"
done
SUITE_TMP=$(mktemp -d "${TMPDIR:-/tmp}/l7r-hooks-suite-$GUARD-p$$.XXXXXX")
trap 'rm -rf "$SUITE_TMP"' EXIT
trap 'pkill -P $$ 2>/dev/null; exit 130' INT
trap 'pkill -P $$ 2>/dev/null; exit 143' TERM
# GUARD_EDIT_OK: feature 383 amendment 3 (plan D27), adding an operation - under the C-library recorder when make hooks-test built
# it, so a green suite's reads are kept (`l7r-guard trace`): a fixture's copy of scripts/ counts as the file it copies,
# the fixture's cp does not
if [ -n "${HOOKS_SHIM:-}" ] && [ -n "${HOOKS_ROOT:-}" ]; then
  rm -f "$WORK/$ID.reads"
  env TMPDIR="$SUITE_TMP" LD_PRELOAD="$HOOKS_SHIM${LD_PRELOAD:+ $LD_PRELOAD}" UV_USE_IO_URING=0 L7R_TEST_DEP_LOG="$WORK/$ID.reads" L7R_TEST_DEP_ROOT="$HOOKS_ROOT" \
    L7R_TEST_DEP_FILE="$GUARD" L7R_TEST_DEP_SKIP="cp" L7R_TEST_DEP_MAP=scripts "$HERE/$SUITE" < /dev/null > "$WORK/$ID.log" 2>&1; rc=$?
else
  TMPDIR="$SUITE_TMP" "$HERE/$SUITE" < /dev/null > "$WORK/$ID.log" 2>&1; rc=$?
fi
# l7r-test-scratch is what a whole Rust test process shares (`beside_binary`), which nothing in it outlives to remove: it goes with
# SUITE_TMP on this runner's exit, as it goes with `make rust-test`'s own run directory
left=$(ls -A "$SUITE_TMP" 2>/dev/null | grep -vx 'l7r-test-scratch' | tr '\n' ' ')
if [ -n "$left" ]; then
  printf '\nLEAK: the suite left %s in its TMPDIR, which it must remove\n  fix: make each mktemp with a trap that removes it on EXIT (`d=$(mktemp -d); trap '"'"'rm -rf "$d"'"'"' EXIT`), or remove it before the case returns; a Rust test holds an l7r_guard::shared::tempdir::TempDir\n' "$left" >> "$WORK/$ID.log"
  rc=1
fi
# feature 383 amendment 3 (plan D27): each suite's seconds beside it, so hooks-test can say which suites ran and what each cost
awk -v a="$t0" -v b="${EPOCHREALTIME/,/.}" 'BEGIN { printf "%.1f", b - a }' > "$WORK/$ID.s"
# feature 449 T125: kept beside the suite's stamp, pass or fail, so the next run starts the longest suites first
mkdir -p "$GITDIR/hooks-test" && cp "$WORK/$ID.s" "$GITDIR/hooks-test/$ID.s"
# GUARD_EDIT_OK: feature 449 T205 - THE LAUNCHERS' SOURCES, EXPANDED ONCE: a launcher given the run's fresh binary
# (L7R_GATE_FRESH, L7R_GUARD_FRESH) skips the walk of its Rust sources and writes their roots here as `c-tree` lines instead; each
# root becomes every path under it - a directory listed and stat'ed, a file stat'ed, a missing one stat'ed - as the walk read them, so
# `trace stamp` keeps the suite tied to those sources exactly as before, from one walk a suite where there was one a call
if [ "$rc" -eq 0 ] && [ -n "${HOOKS_SHIM:-}" ] && grep -q "$(printf '\tc-tree\t')" "$WORK/$ID.reads" 2>/dev/null; then
  grep "$(printf '\tc-tree\t')" "$WORK/$ID.reads" | cut -f3 | sort -u | while IFS= read -r p; do
    if [ -e "$p" ]; then find "$p" -type d -printf "%p\n" | sed "s|^|$GUARD\tc-dir\t|"; find "$p" -printf "%p\n" | sed "s|^|$GUARD\tc-file\t|"
    else printf '%s\tc-file\t%s\n' "$GUARD" "$p"; fi
  done >> "$WORK/$ID.reads"
fi
if [ "$rc" -eq 0 ]; then
  # a shard stamps nothing: its suite is stamped by --close once every shard is green
  [ -n "$K" ] || { mkdir -p "$GITDIR/hooks-test" && printf '%s' "$SHA" > "$GITDIR/hooks-test/$GUARD"; }
  [ -z "$K" ] && [ -n "${HOOKS_SHIM:-}" ] && "$HERE/../../scripts/hooks/l7r-guard.sh" trace stamp "$GITDIR" "$GUARD" "$WORK/$ID.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  printf 'ok' > "$WORK/$ID.rc"
else
  printf 'FAIL' > "$WORK/$ID.rc"
fi
exit 0   # never fail the fan-out; the collector reads the .rc files and reports every failure together
