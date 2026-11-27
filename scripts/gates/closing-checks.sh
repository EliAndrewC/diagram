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
# Each check's output goes to <git dir>/closing-checks/<run id>/<check>.log, the run id its start's UTC time and its pid; the table
# names each verdict, its seconds and its log, the tail of each red one follows, and the exit is 1 if any is red. A TERM or INT stops
# all three. CLOSING_MAKE names the make (the suite's stub); CLOSING_CHECKS_DIR the directory the runs' directories sit in.
#
# ONE DIRECTORY A RUN (451 T72): two runs in one clone (parallel builders) shared one directory, each deleting the other's exit files at
# its start and truncating its logs, so a run read the other's verdict as its own - T69's builder's run of 09:38:33Z beside another's of
# 09:38:06Z, 2026-11-21, the first reading the second's quick verdict and its static.log holding both runs' lines. A run now reads its
# own directory alone. `latest` names the run started last (one rename, so a reader never finds it missing); beside a parallel builder
# that may be another's run, so cite the path the table prints.
#
# THE PRUNE: a run's start removes every other run's directory, and the old layout's <check>.log and .exit files, not changed for
# CLOSING_CHECKS_KEEP_MIN minutes (a GUESS knob, 360: 36 times the longest run in this clone's usage records, 601 s of 25 runs,
# measured 2026-11-21 (`.git/tool-usage.jsonl`, each closing-checks start paired with its end), so no live run is pruned; at about five
# runs an hour, measured the same way, some 30 directories kept). The directory `latest` names is never pruned.
#
# THE CALLER'S TASK (451 T86): `make closing-checks T=<task> [F=<feature>]` judges the files and crates the caller's task changed. About
# 12 of 2026-11-21's closing runs went red only on another builder's half-done files in the same clone - a second `make static` under
# STATIC_OK or a verdict left owed each (measured 2026-11-21, T86's plan section). The caller's files are the clone's uncommitted files
# less those another task's edits alone name: a builder's Edit, Write or NotebookEdit line in any feature's event log, or a Bash call's
# end naming the file in its `writes` (the files the tree walk says it wrote, 451 T93; the exact path, never a directory's files) - not
# a fallback line, whose task is a guess; not one older than the file's last commit or than its own task's last landing, a landed
# task's (451 T93) - naming another task and never this one. A file no line names - a write the walk cannot see (a `make` target's, a generator's, a `git mv`'s), a generated page - is
# the caller's, so a miss costs a saving, never a wrong verdict. The listing
# goes to `make static` alone as L7R_RUST_CALLER: a crate whose check key reads none of it is red APART, not counted (`rustc.rs`), so
# static runs on to its tree-wide steps. Those, hooks-test and quick stay counted whole (T86's plan section: every suite's key reads the
# guard's and the gate's crates; the tree-wide steps fired on another task's file 0 times that night); a red whose every error names
# another task's file is marked BLOCKED, still red. With no T= every file and crate is the caller's, as before. `make done` and a
# landing never set it.
#
# THE TASK'S FEATURE (451 T303): a task number alone is several features' (449 and 451 each have a T281). Without F= the feature was the
# last task-starts.jsonl row naming the number, whatever its feature, tree or age: 451 T281's builder's run of 2026-11-26T15:57:37Z, in a
# pool tree, took 449's start of 2026-11-22 (the only T281 row then), set all 6 of its own files apart as "T281@451-..." and said GREEN
# over its own lint and format red. The feature is now, in order: F=; SPECIFY_FEATURE; the pool registry's holder of this tree
# (<git common dir>/builder-pool.json, 451 T285) where it holds one of the tasks; this tree's own started-task mark of one of the tasks
# (task-marks/<feature>/<task>/<tree key>.json, one a tree, 451 T369; <task>.json before it; 451 T254, the newest). None: REFUSED, exit 2, the command printed, before any check runs - never
# another feature's or another tree's start. And a run that sets files apart while NO uncommitted file is one the task's own edits name
# is REFUSED the same way (the wrong feature given, or the wrong task): it would judge none of the task's work, and its GREEN would read
# as the task's. The verdict line repeats how many files were judged, how many of them the task's own edits name, and how many set apart.
set -u
mk=${CLOSING_MAKE:-make}
base=${CLOSING_CHECKS_DIR:-$(git rev-parse --absolute-git-dir)/closing-checks}
keep_min=${CLOSING_CHECKS_KEEP_MIN:-360}
checks=(static hooks-test quick)
mkdir -p "$base" || exit 2
id=$(date -u +%Y%m%dT%H%M%SZ)-$$
dir=$base/$id
# a plain mkdir: a run id taken twice fails here, never shares a directory
mkdir "$dir" || { printf "closing-checks: could not make this run's directory %s\n" "$dir" >&2; exit 2; }
ln -sfn "$id" "$base/.latest.$$" && mv -Tf "$base/.latest.$$" "$base/latest"
cur=$(readlink "$base/latest" 2>/dev/null)
find "$base" -mindepth 1 -maxdepth 1 -mmin +"$keep_min" \( -type d -name '[0-9]*T[0-9]*Z-[0-9]*' -o -type f \( -name '*.log' -o -name '*.exit' \) \
  -o -type l -name '.latest.*' \) -print0 2>/dev/null | while IFS= read -r -d '' p; do
  case ${p##*/} in "$id" | "$cur") continue ;; esac
  rm -rf -- "$p"
done
# the caller's files and another task's (451 T86, the header): <run dir>/caller-files and <run dir>/others ("<path>\t<task>@<feature> ...")
task=${CLOSING_TASK:-} caller=""
if [ -n "$task" ]; then
  common=$(git rev-parse --path-format=absolute --git-common-dir)
  # the split is the gate's (`rust/gate/crates/task/src/closing_split.rs`, 451 T311: the Python block it was, the repository's last, ported);
  # exit 0 split, 3 REFUSED, any other (git unreadable, or the gate not built) every file the caller's
  "$(dirname "${BASH_SOURCE[0]}")/l7r-gate.sh" closing-split "$(git rev-parse --show-toplevel)" "${L7R_EVENTS_DIR:-$common/l7r-events}" "$common" \
    "${CLOSING_FEATURE:-}" "$task" "$dir" "${SPECIFY_FEATURE:-}" > "$dir/split.txt" 2>&1 < /dev/null
  case $? in
    0) caller=$dir/caller-files; cat "$dir/split.txt" ;;
    3) cat "$dir/split.txt" >&2; exit 2 ;;
    *) printf 'closing-checks: could not tell T=%s files from another task'"'"'s, so every file is judged as yours:\n' "$task"; cat "$dir/split.txt" ;;
  esac
else
  printf 'closing-checks: no T= - every crate and file in the clone is judged as yours; `make closing-checks T=<task>` judges your task'"'"'s alone, another task'"'"'s red reported apart (451 T86)\n'
fi
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
  ( s=$(date +%s); if [ "$c" = static ] && [ -n "$caller" ]; then export L7R_RUST_CALLER=$caller; fi
    "$mk" --no-print-directory "$c" > "$dir/$c.log" 2>&1 < /dev/null; rc=$?
    printf '%s %s\n' "$rc" "$(( $(date +%s) - s ))" > "$dir/$c.exit" ) &
  pids+=($!)
done
# `wait` returns early on a trapped signal, so the trap runs while the checks run
for p in "${pids[@]}"; do wait "$p"; done

# another task's files whose path is, or ends in, each path on stdin (a cargo error names a path from the workspace's directory). The
# list is told apart by its NAME, never by NR == FNR: an empty list makes NR == FNR hold on stdin too, so each path was read as one of
# another task's and none printed - and "every error is another task's" held vacuously, "BLOCKED ... - ()" on the caller's own errors
# (451 T230/T239: 449 T224's and T433's runs, 2026-11-24/25, no other task's file in the clone)
theirs() { awk -F'\t' -v o="$dir/others" 'FILENAME == o { p[$1] = $2; next } $0 != "" { for (k in p) if (k == $0 || substr(k, length(k) - length($0)) == "/" $0) { print k "\t" p[k]; next } print "-\t" $0 }' "$dir/others" -; }
# a counted red whose every error line names another task's file: nothing of the caller's was judged there (451 T86). Cover's lines no
# test reaches name files too, read as the errors' are (451 T95: T81's second closing run, 2026-11-21, red on cover alone, its lines in
# T88's files). Only the counted crates' lines are read: an APART crate's block, from its header to the next rust-checks line, is
# another task's red, not this one's. A failed coverage run's marker (`<crate> - lines no test reaches: 0`) names a crate, not a file,
# and is not read: its cause is the tail printed before it, as a 2026-11-21 12:47Z run's mode_a, its build broken on another task's
# tree.rs, kept BLOCKED
blocked() {
  local named hit what why
  named=$(awk '/^rust-checks: APART / { apart = 1; next } /^rust-checks: / { apart = 0 } apart { next }
    match($0, /^( *-->|Diff in) [^ :]+/) { s = substr($0, RSTART, RLENGTH); sub(/^( *-->|Diff in) /, "", s); print "e\t" s; next }
    match($0, /^thread .* panicked at [^ :]+:[0-9]/) { s = substr($0, RSTART, RLENGTH); sub(/^thread .* panicked at /, "", s); sub(/:[0-9]$/, "", s); print "e\t" s; next }
    /^[^ ]+ - lines no test reaches: [1-9]/ { print "c\t" $1 }' "$dir/$1.log" | sed "s#\t$(git rev-parse --show-toplevel)/#\t#" | sort -u)
  if [ -z "$named" ]; then
    # no line names a file: nothing is attributed, so nothing is another task's (451 T230) - said for static, the one check whose files
    # are attributed (hooks-test and quick stay counted whole), with its own failure lines, an APART crate's left out
    [ "$1" = static ] || return 0
    printf '\n  %s: no error line %s printed names a file - none could be attributed, so all are counted as yours:\n' "$1" "$1"
    awk '/^rust-checks: APART / { apart = 1; next } /^rust-checks: / { apart = 0 } apart { next }
      /^(error|FAIL)|FAILED|^thread .* panicked at |^  pub fn / { print "    " $0; if (++n == 8) exit }' "$dir/$1.log"
    return 0
  fi
  hit=$(printf '%s\n' "$named" | cut -f2 | sort -u | theirs)
  # BLOCKED only on a named file of another task's for every line: an empty or unmatched attribution is the caller's
  [ -n "$hit" ] || return 0
  grep -q '^-' <<< "$hit" && return 0
  case $(printf '%s\n' "$named" | cut -f1 | sort -u | paste -sd' ' -) in
    e) what="every error $1 printed"; why="nothing of yours was judged there, so it stays red: re-run once they compile" ;;
    c) what="every line no test reaches that $1 printed"; why="yours are covered, so it stays red: re-run once their tests reach them" ;;
    *) what="every error and line no test reaches that $1 printed"; why="nothing of yours failed there, so it stays red: re-run once they compile and their tests reach them" ;;
  esac
  printf '\n\033[1m  BLOCKED\033[0m: %s is in another task'"'"'s files - %s; %s\n' \
    "$what" "$(printf '%s\n' "$hit" | awk -F'\t' '{print $1 " (" $2 ")"}' | sort -u | paste -sd, - | sed 's/,/, /g')" "$why"
}
# the crates the rust checks reported APART: red on another task's files alone, not counted (451 T86, rustc.rs)
apart() {
  local lines
  lines=$(grep -E '^rust-checks: APART ' "$dir/static.log" 2>/dev/null | sed -E 's/^rust-checks: APART ([a-z-]+ red on [^ ]+).*/\1/' | sort -u)
  [ -n "$lines" ] || return 0
  printf '\n\033[1manother task'"'"'s red\033[0m, reported apart and not counted (451 T86; each in %s):\n' "$dir/static.log"
  printf '%s\n' "$lines" | while read -r cmd _ _ crate; do
    printf '  %s red on %s - %s\n' "$cmd" "$crate" "$(awk -F'\t' -v c="$crate/" 'index($1, c) == 1 { print $2 ": " $1 }' "$dir/others" | sort -u | head -4 | paste -sd';' - | sed 's/;/; /g; s/^$/no task'"'"'s file inside it (a crate it builds from is red)/')"
  done
}
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
  [ -n "$caller" ] && blocked "$c"
done
[ -n "$caller" ] && apart
# each run recorded, its outcome the combined one (feature 406 T03; CLOSING_GATE is the suite's stub)
record() { "${CLOSING_GATE:-$(dirname "${BASH_SOURCE[0]}")/l7r-gate.sh}" log usage --tool closing-checks --kind check --outcome "$1" 2>/dev/null || true; }
if [ "$red" -gt 0 ]; then
  # the rerun as the caller starts it (451 T86): a bare one judges the whole clone, another task's red counted
  # the feature as this run resolved it (451 T303), so the rerun judges the same task
  [ -n "$caller" ] && feature=$(cat "$dir/feature") || feature=${CLOSING_FEATURE:-}
  again="make closing-checks${task:+ T=$task}${feature:+ F=$feature}"
  printf '\n\033[1mclosing-checks: RED\033[0m - %s of %s red; fix them all, then run `%s` once more (in the background).%s\n' "$red" "${#checks[@]}" "$again" "${caller:+ ($(cat "$dir/judged"))}"
  record refused
  exit 1
fi
record passed
printf '\n\033[1mclosing-checks: GREEN\033[0m - all three%s; a plan section edited after this run started is covered by `make quick` (seconds).\n' "${caller:+ ($(cat "$dir/judged"))}"
