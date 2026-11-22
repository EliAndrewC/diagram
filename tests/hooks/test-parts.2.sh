#!/usr/bin/env bash
# test-parts.2.sh - the second shard of parts.sh's suite (feature 451 T20 split it, plan D17): hookrun.sh, the runner of every suite -
# its sweep of a gone runner's directory and its TERM (feature 449 T101), its `c-tree` expansion (449 T205), and the shard form
# (451 T20): a shard's job stamps nothing, `--close` stamps the suite only when every shard is green, `--jobs` names a suite's job
# files and refuses a suite beside its shards, `--orphans` names a shard no guard's suite owns.
set -u
P="$(cd "$(dirname "$0")" && pwd)/parts.sh"
pass=0 fail=0
check() { if eval "$2"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1"; fi; }
D=$(mktemp -d)
trap 'pkill -P $$ 2>/dev/null; rm -rf "$D"' EXIT


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
# feature 451 T153: each suite leaves its span and exit, `<t0> <t1> <rc>`, for make hooks-test's one Phase-writer call
check "a suite leaves its span for the Phase line" 'read -r a b c < "$H/w/ok.span" && [ "$c" = 0 ] && awk -v a="$a" -v b="$b" "BEGIN { exit !(b >= a && a > 1e9) }"'
TMPDIR="$H/tmp2" bash "$H/hookrun.sh" "$H/w" "$H/g" slow slow.sh sha &
pid=$!
for _ in $(seq 100); do [ -n "$(ls -A "$H/tmp2")" ] && break; timeout 0.05 tail -f /dev/null; done
kill -TERM "$pid"; wait "$pid"
check "a TERM of the runner leaves nothing" '[ -z "$(ls -A "$H/tmp2")" ]'

# GUARD_EDIT_OK: feature 449 T205 - hookrun.sh expands a launcher's `c-tree` lines (its sources' roots, written where the run's fresh
# binary skipped the walk) into every path under them, as the walk's reads were recorded: a directory listed and stat'ed, a file
# stat'ed, a missing root stat'ed - so `trace stamp` still ties the suite to the sources (rust/Cargo.lock, ignored by git, among them,
# which keeps such a suite untraced and on its `deps` key, as the walk did)
S="$H/src"; mkdir -p "$S/sub"; : > "$S/sub/a.rs"
printf '#!/bin/sh\nprintf "tree.sh\\tc-tree\\t%%s\\n" "%s" "%s" "%s" >> "$L7R_TEST_DEP_LOG"\n' "$S" "$S" "$H/gone.toml" > "$H/tree.sh"; chmod +x "$H/tree.sh"
TMPDIR="$H/tmp" HOOKS_SHIM=/dev/null HOOKS_ROOT="$H" bash "$H/hookrun.sh" "$H/w" "$H/g" tree.sh tree.sh sha
want=$(printf 'tree.sh\tc-dir\t%s\n' "$S" "$S/sub"; printf 'tree.sh\tc-file\t%s\n' "$S" "$S/sub" "$S/sub/a.rs" "$H/gone.toml")
# (only the lines of those paths: under make hooks-test this suite runs beneath the read recorder, which adds the fake suite's own reads)
got=$(grep -v "$(printf '\tc-tree\t')" "$H/w/tree.sh.reads" | grep -E "$(printf '\t')($S|$H/gone.toml)" | sort)
check "a c-tree root expands to every path under it, once" '[ "$got" = "$(printf "%s\n" "$want" | sort)" ]'

# THE SHARD FORM (feature 451 T20): two shards of a fixture suite `fx.sh`, the second red until its flag file exists; each run
# outside make hooks-test's read recorder (HOOKS_SHIM unset), whose trace stamp is not what these cases pin
S="$D/sh"; mkdir -p "$S/w" "$S/g" "$S/tmp"
cp "$(dirname "$P")/hookrun.sh" "$S/"
printf '#!/bin/sh\nexit 0\n' > "$S/test-fx.1.sh"; printf '#!/bin/sh\n[ -f "%s/green" ]\n' "$S" > "$S/test-fx.2.sh"
chmod +x "$S/test-fx.1.sh" "$S/test-fx.2.sh"
run() { env -u HOOKS_SHIM TMPDIR="$S/tmp" bash "$S/hookrun.sh" "$@"; }
run "$S/w" "$S/g" fx.sh test-fx.1.sh k1
check "a green shard's job stamps nothing" '[ ! -e "$S/g/hooks-test/fx.sh" ] && [ "$(cat "$S/w/fx.sh.1.rc")" = ok ]'
check "a shard's seconds are its own" '[ -f "$S/w/fx.sh.1.s" ] && [ -f "$S/g/hooks-test/fx.sh.1.s" ] && [ ! -e "$S/w/fx.sh.s" ]'
run "$S/w" "$S/g" fx.sh test-fx.2.sh k1
check "a red shard's job is its own" '[ "$(cat "$S/w/fx.sh.2.rc")" = FAIL ] && [ -f "$S/w/fx.sh.2.log" ]'
run --close "$S/w" "$S/g" fx.sh k1 test-fx.1.sh test-fx.2.sh; code=$?
check "a red shard keeps the suite unstamped" '[ "$code" = 1 ] && [ ! -e "$S/g/hooks-test/fx.sh" ] && [ ! -e "$S/g/hooks-test/fx.sh.jobs" ]'
run --close "$S/w" "$S/g" fx.sh k1 test-fx.1.sh test-fx.2.sh test-fx.3.sh; code=$?
check "a shard that never ran keeps the suite unstamped" '[ "$code" = 1 ] && [ ! -e "$S/g/hooks-test/fx.sh" ]'
: > "$S/green"
run "$S/w" "$S/g" fx.sh test-fx.2.sh k1
run --close "$S/w" "$S/g" fx.sh k1 test-fx.1.sh test-fx.2.sh
check "every shard green stamps the suite" '[ "$(cat "$S/g/hooks-test/fx.sh")" = k1 ]'
check "the stamp keeps its shard list" '[ "$(cat "$S/g/hooks-test/fx.sh.jobs" | tr "\n" " ")" = "test-fx.1.sh test-fx.2.sh " ]'
# --jobs: each suite's job files, one line a suite - its shards in order, or the suite; none is the suite alone, the suite beside its
# shards `<suite> !` with the fix
printf '#!/bin/sh\nexit 0\n' > "$S/test-fx.10.sh"
check "a split suite's jobs are its shards, in order" '[ "$(run --jobs "$S" test-fx.sh)" = "test-fx.sh test-fx.1.sh test-fx.2.sh test-fx.10.sh" ]'
rm "$S/test-fx.10.sh"; : > "$S/test-fx.notes.sh"
check "a name whose middle is not a number is no shard" '[ "$(run --jobs "$S" test-fx.sh)" = "test-fx.sh test-fx.1.sh test-fx.2.sh" ]'
: > "$S/test-whole.sh"
check "an unsplit suite is its own job" '[ "$(run --jobs "$S" test-whole.sh)" = "test-whole.sh test-whole.sh" ]'
check "a guard with neither has no jobs" '[ "$(run --jobs "$S" test-none.sh)" = test-none.sh ]'
check "every suite asked is answered, in one call" '[ "$(run --jobs "$S" test-whole.sh test-none.sh test-fx.sh | cut -d" " -f1 | tr "\n" " ")" = "test-whole.sh test-none.sh test-fx.sh " ]'
: > "$S/test-fx.sh"
out=$(run --jobs "$S" test-fx.sh 2> "$S/err")
check "a suite beside its shards is refused with the fix" '[ "$out" = "test-fx.sh !" ] && case $(cat "$S/err") in *"SUITE AND SHARDS BOTH"*"fix: "*) true ;; *) false ;; esac'
rm "$S/test-fx.sh"
# --orphans: a lone shard, whose suite no guard on the roster owns, would never run - named, with the fix
: > "$S/test-lone.1.sh"
out=$(run --orphans "$S" test-fx.sh test-whole.sh); code=$?
check "a lone shard is named, with the fix (exit 1)" '[ "$code" = 1 ] && case $out in *"SHARD WITHOUT ITS SUITE: test-lone.1.sh"*"fix: "*) true ;; *) false ;; esac'
check "an owned shard is not named" 'case $out in *test-fx.1.sh*) false ;; *) true ;; esac'
run --orphans "$S" test-fx.sh test-whole.sh test-lone.sh > /dev/null; code=$?
check "every shard owned passes" '[ "$code" = 0 ]'

echo "parts.2: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
