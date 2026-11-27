#!/usr/bin/env bash
# hookrun.sh - run ONE guard suite, for the parallel `hooks-test` (feature 172).
#
# Usage: hookrun.sh <work-dir> <gitdir> <guard> <suite> <sha>          run one job: a suite, or one shard of a split suite
#        hookrun.sh --jobs <dir> <suite>...                              each suite's job files: `<suite> <job>...` a line
#        hookrun.sh --orphans <dir> <suite>...                           every shard whose suite is none of these (exit 1 if any)
#        hookrun.sh --close <work-dir> <gitdir> <guard> <sha> <shard>... stamp a split suite green when every shard's job is
#        hookrun.sh --sweep [<gitdir>]                                   remove killed runners' leftover directories, and bound the kept failed logs, once a run
#        hookrun.sh --keep <gitdir> <job> <log>                          keep a failed log no job wrote; print its name
#        hookrun.sh --swept <work-dir> <gitdir> <guard> <suite> <sha>   a job of a run that has swept: it lists no temp directory
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
# sha, its trace and its shard list - only when every shard's job is ok: one line of the suite's stamp, and its key's trace written whole (451 T304).
# No fork per name: `make hooks-test` asks --jobs for every suite before the fan-out, so one call takes them all;
# one call per suite cost 6.9 s for 57 suites on a loaded host, measured 2026-11-20 (57 single-suite --jobs calls beside a full run).
# ONCE A RUN, NOT ONCE A SUITE (feature 451 T372): the glob below reads the whole temp directory - 16.5 ms a suite under a /tmp of 5,443
# entries (200 globs 3.30 s, 0.00 s in an empty directory), 4,051 suite runs on 2026-11-26. `make hooks-test` runs it once before its
# fan-out (`--sweep`) and marks its jobs `--swept`; a job run without the mark, by hand or by a test, sweeps itself as before. A mark
# on the command line, not an exported variable: a suite that runs this runner itself (test-parts) would inherit a variable.
sweep_gone() {
  local d p
  for d in "${TMPDIR:-/tmp}"/l7r-hooks-suite-*-p[0-9]*.*; do
    p=${d##*-p}; p=${p%%.*}
    case $p in '' | *[!0-9]*) continue ;; esac
    [ -d "$d" ] && [ ! -e "/proc/$p" ] && [ -n "$(find "$d" -maxdepth 0 -mmin +180)" ] && rm -rf "$d"
  done
  return 0
}
# A FAILED SUITE'S WHOLE LOG IS KEPT (feature 451 T414): the job's log lives in the run's mktemp work directory, which `make hooks-test`
# removes on exit, so the red state-sync run of 2026-11-26 18:27 UTC left one event line (its name, 94.7 s, exit 1) and nothing a later
# reader (451 T314) could open; the land log that held the printed copy was overwritten by the next landing. A red job's log is copied
# into the COMMON git directory - every worktree of a clone runs its suites there - as `l7r-hooks-failed/<utc>-<job>-p<pid>.log`: the
# time first, to the nanosecond, so the names' order is their age; the job (`<guard>` or a shard's `<guard>.<k>`) and the runner's pid,
# so two trees failing one suite in one instant never write one file; no colon or space, so the name rides in the event line's span.
# Its name relative to that directory is printed (`--keep`) or left in `<job>.kept`, for the FAIL line and the event line. A green
# suite's log is not kept, as before.
keep_failed() { # <gitdir> <job> <log>: copy the log whole, moved into place, and print its name
  local dir=$1/l7r-hooks-failed name
  name=$(date -u +%Y%m%dT%H%M%S.%NZ)-$2-p$$.log
  mkdir -p "$dir" && cp "$3" "$dir/.$name.part" && mv -f "$dir/.$name.part" "$dir/$name" && printf 'l7r-hooks-failed/%s\n' "$name"
}
# THE BOUND (HOOKS_FAILED_KEEP, a GUESS knob: 50, about one fully red run of the 70 suite files' worth of the latest failures): the
# oldest kept logs past it are removed. Nothing a later run reuses is among them: no runner, stamp, key or check reads this directory
# - a run's stamps, seconds and renderings live in `hooks-test/` - so a removed log is only a reader's. It runs ONCE a run, in
# `--sweep <gitdir>` before the fan-out, so no job of the run removes a log another job's FAIL line is about to name (a run's logs
# can outnumber the bound); a job run by hand, unswept, bounds them after keeping its own, the newest.
bound_failed() { # <gitdir>
  local dir=$1/l7r-hooks-failed keep=${HOOKS_FAILED_KEEP:-50} f
  case $keep in '' | *[!0-9]*) keep=50 ;; esac
  [ -d "$dir" ] || return 0
  ls "$dir" | grep -E '^[0-9]{8}T[0-9.]+Z-.+\.log$' | sort | head -n "-$keep" | while IFS= read -r f; do rm -f "$dir/$f"; done
  return 0
}
# THE STAMPS ARE A SET, KEYED BY CONTENT (feature 451 T304): a suite's stamp `hooks-test/<guard>` held ONE key in the COMMON git directory,
# so a tree's green run replaced the key another tree's content had gone green at, and trees run in turn reran each other's suites (60
# of 63 stamps rewritten within an hour with three builders live, 2026-11-26). It is now one line a kept key, newest first - `<key>` or,
# for a split suite, `<key> <shard>...` (its shard list, where `<guard>.jobs` held one list) - and its renderings and traces are kept a
# key each beside it. HOOKS_STAMP_KEEP, a GUESS knob: 6 keys a suite, one for each tree that runs suites at once (the clone, its landing
# and review trees, three pool trees); a key past it reruns its suite once.
stamp_keep() { local k=${HOOKS_STAMP_KEEP:-6}; case $k in '' | *[!0-9]* | 0) k=6 ;; esac; printf '%s' "$k"; }
stamp_key() { # <gitdir> <guard> <key> [<shard>...]: the key first with its shards, the guard's other kept keys after it, bounded
  local f=$1/hooks-test/$2 key=$3 line; shift 3
  line=$key; [ "$#" -eq 0 ] || line="$key $*"
  mkdir -p "${f%/*}" && { printf '%s\n' "$line"; if [ -f "$f" ]; then cat "$f"; echo; fi; } | awk -v k="$key" -v n="$(stamp_keep)" 'NF && (NR == 1 || $1 != k) && ++c <= n' > "$f.$$.part" && mv -f "$f.$$.part" "$f" && rm -f "$f.jobs"   # the one shard list before T304
}
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
  stamp_key "$GITDIR" "$GUARD" "$SHA" "$@" || exit 1
  if [ -n "${HOOKS_SHIM:-}" ]; then
    for s in "$@"; do shard_k "$s" && cat "$WORK/$GUARD.$SK.reads" 2>/dev/null; done > "$WORK/$GUARD.reads"
    "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../scripts/hooks/l7r-guard.sh" trace stamp "$GITDIR" "$GUARD" "$SHA" "$(stamp_keep)" "$WORK/$GUARD.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  fi
  exit 0 ;;
--sweep) sweep_gone; [ -z "${2:-}" ] || bound_failed "$2"; exit 0 ;;
--keep) keep_failed "${2:?gitdir}" "${3:?job}" "${4:?log}"; exit $? ;;
esac
SWEPT=""; if [ "${1:-}" = --swept ]; then SWEPT=1; shift; fi

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
[ -n "$SWEPT" ] || sweep_gone
SUITE_TMP=$(mktemp -d "${TMPDIR:-/tmp}/l7r-hooks-suite-$GUARD-p$$.XXXXXX")
trap 'rm -rf "$SUITE_TMP"' EXIT
trap 'pkill -P $$ 2>/dev/null; exit 130' INT
trap 'pkill -P $$ 2>/dev/null; exit 143' TERM
# GUARD_EDIT_OK: feature 383 amendment 3 (plan D27), adding an operation - under the C-library recorder when make hooks-test built
# it, so a green suite's reads are kept (`l7r-guard trace`): a fixture's copy of scripts/ counts as the file it copies,
# the fixture's cp does not
# feature 451 T170: every message the suite's guards render is kept (`protocol::keep`), and a green suite's set replaces its last in
# the tree's store (below, 451 T281), which `make hooks-test` holds to the budget and the review (`l7r-guard messages check`)
rm -rf "$WORK/$ID.messages" "$WORK/$ID.kept"
export L7R_MESSAGE_CORPUS="$WORK/$ID.messages"
if [ -n "${HOOKS_SHIM:-}" ] && [ -n "${HOOKS_ROOT:-}" ]; then
  rm -f "$WORK/$ID.reads"
  env TMPDIR="$SUITE_TMP" LD_PRELOAD="$HOOKS_SHIM${LD_PRELOAD:+ $LD_PRELOAD}" UV_USE_IO_URING=0 L7R_TEST_DEP_LOG="$WORK/$ID.reads" L7R_TEST_DEP_ROOT="$HOOKS_ROOT" \
    L7R_TEST_DEP_FILE="$GUARD" L7R_TEST_DEP_SKIP="cp" L7R_TEST_DEP_MAP=scripts "$HERE/$SUITE" < /dev/null > "$WORK/$ID.log" 2>&1; rc=$?
else
  TMPDIR="$SUITE_TMP" "$HERE/$SUITE" < /dev/null > "$WORK/$ID.log" 2>&1; rc=$?
fi
# l7r-test-scratch is what a whole Rust test process shares (`beside_binary`), which nothing in it outlives to remove: it goes with
# SUITE_TMP on this runner's exit, as it goes with `make rust-test`'s own run directory; l7r-tmp is the TempDirs' own subdirectory
# (462 T371), which every guard process making one leaves: passed over, and what is inside it named
left=$( { ls -A "$SUITE_TMP" 2>/dev/null | grep -vx -e 'l7r-test-scratch' -e 'l7r-tmp'; ls -A "$SUITE_TMP/l7r-tmp" 2>/dev/null | sed 's|^|l7r-tmp/|'; } | tr '\n' ' ')
if [ -n "$left" ]; then
  printf '\nLEAK: the suite left %s in its TMPDIR, which it must remove\n  fix: make each mktemp with a trap that removes it on EXIT (`d=$(mktemp -d); trap '"'"'rm -rf "$d"'"'"' EXIT`), or remove it before the case returns; a Rust test holds an l7r_guard::shared::tempdir::TempDir\n' "$left" >> "$WORK/$ID.log"
  rc=1
fi
# feature 383 amendment 3 (plan D27): each suite's seconds beside it, so hooks-test can say which suites ran and what each cost
t1=${EPOCHREALTIME/,/.}
awk -v a="$t0" -v b="$t1" 'BEGIN { printf "%.1f", b - a }' > "$WORK/$ID.s"
# feature 451 T153: the suite's span and exit beside it, `<t0> <t1> <rc>`, which `make hooks-test` hands to the one Phase writer in ONE
# call after the fan-out (`l7r-gate measure event-log phase`), so each suite's minutes reach `make where-time` as hook suites and feed the task time breakdown (`make task-time`, 451 T243)
printf '%s %s %s\n' "$t0" "$t1" "$rc" > "$WORK/$ID.span"
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
  # feature 451 T281: the rendering goes to the TREE's store (HOOKS_MESSAGES, `l7r-guard messages store`; one in the common git
  # directory was every worktree's, each tree's run replacing the others' renderings) and, named by the key the job ran at, beside
  # the SHARED stamp, where a tree that skips the suite on this stamp fills its own store from it (`l7r-guard messages gather`).
  # One keyed rendering a job, written before the stamp that names its key and moved into place whole.
  M=${HOOKS_MESSAGES:-$GITDIR/hooks-test/messages}; R=$GITDIR/hooks-test/rendered
  mkdir -p "$M" "$R" && cat "$WORK/$ID.messages/messages.jsonl" > "$M/$ID.jsonl" 2>/dev/null || : > "$M/$ID.jsonl"
  cp "$M/$ID.jsonl" "$R/.$ID.$$.part" && mv -f "$R/.$ID.$$.part" "$R/$ID@$SHA.jsonl"
  # a rendering a kept key (451 T304), the oldest past the bound removed
  ls -t -- "$R/$ID@"*.jsonl | awk -v n="$(stamp_keep)" 'NR > n' | while IFS= read -r f; do rm -f "$f"; done
  # a shard stamps nothing: its suite is stamped by --close once every shard is green
  [ -n "$K" ] || stamp_key "$GITDIR" "$GUARD" "$SHA"
  [ -z "$K" ] && [ -n "${HOOKS_SHIM:-}" ] && "$HERE/../../scripts/hooks/l7r-guard.sh" trace stamp "$GITDIR" "$GUARD" "$SHA" "$(stamp_keep)" "$WORK/$ID.reads" "$HOOKS_ROOT" >/dev/null 2>&1
  printf 'ok' > "$WORK/$ID.rc"
else
  printf 'FAIL' > "$WORK/$ID.rc"
  # feature 451 T414: the whole log kept, the LEAK line above in it, and its name left for the FAIL line and the event line
  keep_failed "$GITDIR" "$ID" "$WORK/$ID.log" > "$WORK/$ID.kept" || rm -f "$WORK/$ID.kept"
  [ -n "$SWEPT" ] || bound_failed "$GITDIR"
fi
exit 0   # never fail the fan-out; the collector reads the .rc files and reports every failure together
