#!/usr/bin/env bash
# Tests for scripts/land-tooling.sh - a clone's tooling lands on main alone, mid-feature (feature 379 amendment 1, SC-003).
# Run: tests/hooks/test-land-tooling.sh   (exit 0 = all green)
#
# Real git repos: an origin, a clone under .clones/ holding engine work AND a guard fix, and another session moving main
# meanwhile. The checks and the push are replaced through the script's own seams (a push is `git push`, as sync-with-main's).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAND="$HERE/../../scripts/land-tooling.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
export LAND_TOOLING_CHECKS=true LAND_TOOLING_PUSH="git push -q origin HEAD:main" LAND_TOOLING_LEDGER=true

ok() { if eval "$2"; then echo "  ok      $1"; PASS=$((PASS+1)); else echo "  FAIL    $1"; FAIL=$((FAIL+1)); fi; }
# (an assertion pipes into `grep PATTERN >/dev/null`, never `grep -q`: under `pipefail` a `grep -q` that exits on its first match
# can kill the writer with SIGPIPE, and the pipeline fails though the line is there - "the clone holds a merge" failed so, now
# and then, inside a land-tooling run, feature 387)

# origin with main; a clone at $T/m/.clones/c with an engine commit and a tooling commit; main moved by another session
setup() {
  rm -rf "$T/o.git" "$T/m" "$T/seed"
  git init -q --bare "$T/o.git"; git -C "$T/o.git" symbolic-ref HEAD refs/heads/main
  git init -q -b main "$T/seed"
  mkdir -p "$T/seed/scripts" "$T/seed/l7r"
  printf 'one\ntwo\n' > "$T/seed/scripts/a.sh"; printf 'x\n' > "$T/seed/scripts/b.sh"; printf 'e = 1\n' > "$T/seed/l7r/e.py"
  git -C "$T/seed" add -A; git -C "$T/seed" commit -qm base; git -C "$T/seed" push -q "$T/o.git" main
  mkdir -p "$T/m/.clones"; git clone -q "$T/o.git" "$T/m/.clones/c"
  C="$T/m/.clones/c"
  printf 'e = 2\n' > "$C/l7r/e.py"; git -C "$C" commit -qam "engine work"
  printf 'one\nTWO\n' > "$C/scripts/a.sh"; git -C "$C" commit -qam "a guard fix"
  printf 'other\n' > "$T/seed/other.txt"; git -C "$T/seed" add -A; git -C "$T/seed" commit -qm "another session"; git -C "$T/seed" push -q "$T/o.git" main
}
land() { ( cd "$C" && "$LAND" "$@" ) >"$T/out" 2>&1; }
on_main() { git -C "$T/o.git" show "main:$1" 2>/dev/null; }

echo "1. it asks for the files, naming the compliant command, and refuses what is not tooling"
setup
land; rc=$?
ok "no FILES: exit 2" '[ "$rc" -eq 2 ]'
ok "no FILES: the command lists the tooling changed, not the engine" 'grep -q "FILES=\"scripts/a.sh\"" "$T/out" && ! grep -q "l7r/e.py\"" "$T/out"'
land scripts/a.sh l7r/e.py; rc=$?
ok "an engine path is refused, named" '[ "$rc" -ne 0 ] && grep -q "l7r/e.py is not tooling" "$T/out" && [ "$(on_main l7r/e.py)" = "e = 1" ]'
printf 'dirty\n' >> "$C/scripts/a.sh"; land scripts/a.sh; rc=$?
ok "uncommitted changes in FILES are refused" '[ "$rc" -ne 0 ] && grep -q "uncommitted" "$T/out"'
git -C "$C" checkout -q -- scripts/a.sh
# GUARD_EDIT_OK: feature 383 amendment 7 - a saved workflow (.claude/workflows/) is tooling, as an agent file is
mkdir -p "$C/.claude/workflows"; printf 'export const meta = {}\n' > "$C/.claude/workflows/w.js"; git -C "$C" add -A; git -C "$C" commit -qm "a saved workflow"
land; ok "a saved workflow is offered as tooling" 'grep -q ".claude/workflows/w.js" "$T/out"'
setup  # section 2 counts the clone's commits from a fresh setup

echo "1b. a Makefile lands only with the clone's make-targets page current, and the page lands beside it (385 T46)"
setup
mkdir -p "$C/docs"; printf 'all:\n' > "$C/Makefile"; printf 'page v1\n' > "$C/docs/make-targets.html"; git -C "$C" add -A; git -C "$C" commit -qm "a target"
LAND_TOOLING_DOCS_CHECK=false land Makefile; rc=$?
ok "a stale page refuses the landing, naming make docs" '[ "$rc" -ne 0 ] && grep "make docs" "$T/out" >/dev/null && [ -z "$(on_main Makefile)" ]'
LAND_TOOLING_DOCS_CHECK=true land Makefile; rc=$?
ok "a current page lands beside the Makefile" '[ "$rc" -eq 0 ] && grep "docs/make-targets.html lands too" "$T/out" >/dev/null && [ "$(on_main docs/make-targets.html)" = "page v1" ]'
setup

echo "1c. the Python that lands is linted first, and a failure lands nothing, naming the fix (385 T52)"
setup
printf 'x = 1\n' > "$C/scripts/c.py"; git -C "$C" add -A; git -C "$C" commit -qm "a script"
LAND_TOOLING_LINT=false land scripts/c.py; rc=$?
ok "a lint failure lands nothing and names ruff format" '[ "$rc" -ne 0 ] && grep "ruff format scripts/c.py" "$T/out" >/dev/null && [ -z "$(on_main scripts/c.py)" ]'
LAND_TOOLING_LINT=true land scripts/c.py; rc=$?
ok "a clean file lands" '[ "$rc" -eq 0 ] && [ "$(on_main scripts/c.py)" = "x = 1" ]'
ok "the lint step is timed in the log" 'grep "^land-tooling: step lint [0-9.]* s$" "$C/.git/land-tooling.log" >/dev/null'
printf 'y = 1\n' > "$C/scripts/e.py"; git -C "$C" add -A; git -C "$C" commit -qm "another script"
LAND_TOOLING_LINT=false LAND_TOOLING_TOOLING="touch $T/tests-ran" LAND_TOOLING_GUARDS="touch $T/guards-ran" land scripts/e.py; rc=$?
ok "a lint failure stops before the tests and the guard suites start (385 T67)" '[ "$rc" -ne 0 ] && [ ! -e "$T/tests-ran" ] && [ ! -e "$T/guards-ran" ]'
ok "...and the run leaves its record, failed, for make tick (385 T79)" 'tail -1 "$C/.git/land-tooling.jsonl" | grep -q "\"outcome\": \"failed: " && tail -1 "$C/.git/land-tooling.jsonl" | grep -q "scripts/e.py"'
LAND_TOOLING_LINT=true land scripts/e.py; rc=$?
ok "...and a landed run records landed" '[ "$rc" -eq 0 ] && tail -1 "$C/.git/land-tooling.jsonl" | grep -q "\"outcome\": \"landed\""'
printf 'z  =  1\n' > "$C/scripts/f.py"; git -C "$C" add -A; git -C "$C" commit -qm "a badly formatted script"
( cd "$C" && env -u LAND_TOOLING_LINT LAND_TOOLING_TOOLING="touch $T/t91-tests" "$LAND" scripts/f.py ) >"$T/out" 2>&1; rc=$?
ok "the lint runs first, in the clone, before anything else (385 T91)" '[ "$rc" -ne 0 ] && grep -q "feature 385 T91" "$T/out" && [ ! -e "$T/t91-tests" ] && [ -z "$(on_main scripts/f.py)" ]'
setup

echo "1e. the landing's lint keeps the gate's scope: an excluded file is not refused (385 T55)"
setup
printf '[tool.ruff]\nextend-exclude = ["scripts"]\n' > "$T/seed/pyproject.toml"; git -C "$T/seed" add -A; git -C "$T/seed" commit -qm "the lint scope"; git -C "$T/seed" push -q "$T/o.git" main
printf 'import sys\nsys.exit(0)\n' > "$C/scripts/d.py"; mkdir -p "$C/tests"; printf 'import sys\nsys.exit(0)\n' > "$C/tests/test_d.py"
git -C "$C" add -A; git -C "$C" commit -qm "an excluded script and a test, both unformatted"
land scripts/d.py; rc=$?
ok "an excluded script lands, as the gate never lints it" '[ "$rc" -eq 0 ] && [ -n "$(on_main scripts/d.py)" ]'
LAND_TOOLING_TEST="true " land tests/test_d.py; rc=$?
ok "an included file that fails is still refused" '[ "$rc" -ne 0 ] && grep "ruff format tests/test_d.py" "$T/out" >/dev/null'
setup

echo "1d. owed ledger rows are refused before any check runs (385 T53)"
setup
LAND_TOOLING_LEDGER="echo owed-row-here >&2; false" LAND_TOOLING_CHECKS="touch $T/checks-ran" land scripts/a.sh; rc=$?
ok "an owed pass refuses at once, naming the rows and the command" '[ "$rc" -ne 0 ] && grep "owed-row-here" "$T/out" >/dev/null && grep "make ledger-owed WRITE" "$T/out" >/dev/null'
ok "...before any check ran, and nothing landed" '[ ! -e "$T/checks-ran" ] && [ "$(on_main scripts/a.sh | tail -1)" = "two" ]'
LEDGER_ROWS_OK="a fixture's waiver" LAND_TOOLING_LEDGER="false" land scripts/a.sh; rc=$?
ok "LEDGER_ROWS_OK waives it, as it waives the push's" '[ "$rc" -eq 0 ]'
setup

echo "2. the tooling lands alone, on top of main, and the clone merges main cleanly (SC-003)"
land scripts/a.sh; rc=$?
ok "landed" '[ "$rc" -eq 0 ] && grep -q "landed scripts/a.sh" "$T/out"'
ok "main carries the guard fix" '[ "$(on_main scripts/a.sh | tail -1)" = "TWO" ]'
ok "main carries none of the engine work" '[ "$(on_main l7r/e.py)" = "e = 1" ]'
ok "main keeps the other session's work" '[ "$(on_main other.txt)" = "other" ]'
ok "the worktree is gone" '[ ! -e "$T/m/.clones/c-tooling" ] && ! git -C "$C" worktree list | grep c-tooling >/dev/null'
ok "each step is timed in the log (383 amendment 2, FR-017)" 'for s in prepare worktree patch guard-suites tooling-tests checks push; do grep -q "^land-tooling: step $s [0-9.]* s$" "$C/.git/land-tooling.log" || exit 1; done'
ok "...and the landing's steps are one JSON line" 'python3 -c "import json,sys; r=json.loads(open(sys.argv[1]).readlines()[-1]); sys.exit(not (r[\"outcome\"] == \"push-exit-0\" and set(r[\"steps\"]) == {\"prepare\", \"worktree\", \"patch\", \"guard-suites\", \"tooling-tests\", \"lint\", \"checks\", \"push\"}))" "$C/.git/land-tooling-steps.jsonl"'
ok "the clone's history is untouched" '[ "$(git -C "$C" log --format=%s -1)" = "a guard fix" ]'
git -C "$C" pull -q --no-rebase --no-edit origin main >"$T/out" 2>&1; rc=$?
ok "the clone's next merge of main is clean" '[ "$rc" -eq 0 ] && [ "$(cat "$C/l7r/e.py")" = "e = 2" ]'

echo "2b. the guard suites and the tooling tests run side by side, each timed; a failing one is named (383 amendment 2, D22)"
setup
LAND_TOOLING_CHECKS= LAND_TOOLING_GUARDS='sleep 1' LAND_TOOLING_TOOLING='sleep 1' land scripts/a.sh; rc=$?
ok "landed with both jobs" '[ "$rc" -eq 0 ]'
ok "they overlapped: the checks took less than the two jobs one after the other" 'python3 -c "import json,sys; s=json.loads(open(sys.argv[1]).readlines()[-1])[\"steps\"]; sys.exit(not (s[\"guard-suites\"] >= 1 and s[\"tooling-tests\"] >= 1 and s[\"checks\"] < 1.8))" "$C/.git/land-tooling-steps.jsonl"'
setup
LAND_TOOLING_CHECKS= LAND_TOOLING_GUARDS='echo guard-out; exit 1' LAND_TOOLING_TOOLING='true' land scripts/a.sh; rc=$?
ok "a failing job is named and lands nothing" '[ "$rc" -ne 0 ] && grep -q "checks failed in the worktree (guard-suites" "$T/out" && grep -q guard-out "$C/.git/land-tooling.log" && [ "$(on_main scripts/a.sh | tail -1)" = "two" ]'
ok "...and leaves no job file behind" '! ls "$C/.git/" | grep "land-tooling.log\\." >/dev/null'

echo "3. a change that does not apply cleanly onto main, and a failed check, land nothing"
setup
printf 'y\n' > "$C/scripts/b.sh"; git -C "$C" commit -qam "b here"
printf 'z\n' > "$T/seed/scripts/b.sh"; git -C "$T/seed" commit -qam "b there"; git -C "$T/seed" push -q "$T/o.git" main
land scripts/b.sh; rc=$?
ok "a conflicting change is refused" '[ "$rc" -ne 0 ] && grep -q "do not apply cleanly" "$T/out" && [ "$(on_main scripts/b.sh)" = "z" ]'
ok "...the merge it tried is aborted, the clone as it was (385 T24)" '! git -C "$C" rev-parse -q --verify MERGE_HEAD >/dev/null && [ "$(git -C "$C" log -1 --format=%s)" = "b here" ]'
ok "and its worktree is gone" '[ ! -e "$T/m/.clones/c-tooling" ]'
LAND_TOOLING_CHECKS=false land scripts/a.sh; rc=$?
ok "a failed check lands nothing" '[ "$rc" -ne 0 ] && grep -q "checks failed" "$T/out" && [ "$(on_main scripts/a.sh | tail -1)" = "two" ]'

echo "3c. a stale base that merges cleanly lands on the first try (feature 385 T24: three landings refused in one day for this)"
setup
printf '1\n2\n3\n' > "$T/seed/scripts/c.sh"; git -C "$T/seed" add -A; git -C "$T/seed" commit -qm "c"; git -C "$T/seed" push -q "$T/o.git" main
git -C "$C" pull -q --no-rebase --no-edit origin main
printf '1\n2\nTHREE\n' > "$C/scripts/c.sh"; git -C "$C" commit -qam "c here, line 3"
printf 'ONE\n2\n3\n' > "$T/seed/scripts/c.sh"; git -C "$T/seed" commit -qam "c there, line 1"; git -C "$T/seed" push -q "$T/o.git" main
land scripts/c.sh; rc=$?
ok "the patch's context moved on main, the merge is clean: landed" '[ "$rc" -eq 0 ] && [ "$(on_main scripts/c.sh)" = "$(printf "ONE\n2\nTHREE")" ]'
ok "...saying it merged main in" 'grep -q "merged origin/main into the clone" "$T/out"'
ok "...and the clone holds a merge, never a rewrite" '[ "$(git -C "$C" log -1 --format=%P | wc -w)" -eq 2 ] && git -C "$C" log --format=%s | grep "c here, line 3" >/dev/null'
# feature 385 T30: ...but never under a running gate - the merge is refused and the clone left as it was
setup
printf '1\n2\n3\n' > "$T/seed/scripts/c.sh"; git -C "$T/seed" add -A; git -C "$T/seed" commit -qm "c"; git -C "$T/seed" push -q "$T/o.git" main
git -C "$C" pull -q --no-rebase --no-edit origin main
printf '1\n2\nTHREE\n' > "$C/scripts/c.sh"; git -C "$C" commit -qam "c here, line 3"
printf 'ONE\n2\n3\n' > "$T/seed/scripts/c.sh"; git -C "$T/seed" commit -qam "c there, line 1"; git -C "$T/seed" push -q "$T/o.git" main
mkdir -p "$C/scripts/gates"; cp "$HERE/../../scripts/gates/gate_lock.py" "$C/scripts/gates/"; git -C "$C" add scripts/gates; git -C "$C" commit -qm "the lock"
(exec -a make bash -c 'sleep 120; :' done) & GL=$!
sleep 0.3; printf '{"pid": %s, "t": 0}' "$GL" > "$C/.git/gate.lock"
BEFORE=$(git -C "$C" rev-parse HEAD)
land scripts/c.sh; rc=$?
kill "$GL" 2>/dev/null; wait "$GL" 2>/dev/null
ok "a stale patch under a running gate is refused, nothing merged (385 T30)" '[ "$rc" -ne 0 ] && grep "a gate is running in this clone" "$T/out" >/dev/null && [ "$(git -C "$C" rev-parse HEAD)" = "$BEFORE" ]'

echo "3b. a landed test is run, and one needing the clone's unlanded engine work is refused"
setup
mkdir -p "$C/tests"
printf 'import pathlib, sys\nsys.exit(0 if pathlib.Path("l7r/e.py").read_text() == "e = 2\\n" else 1)\n' > "$C/tests/test_e.py"
git -C "$C" add tests; git -C "$C" commit -qm "the engine work's test"
LAND_TOOLING_TEST="python3 " land tests/test_e.py; rc=$?
ok "a test failing without the held engine work is refused" '[ "$rc" -ne 0 ] && grep -q "checks failed" "$T/out" && [ -z "$(on_main tests/test_e.py)" ]'
printf 'import sys\n\nsys.exit(0)\n' > "$C/tests/test_ok.py"; git -C "$C" add tests; git -C "$C" commit -qm "a test standing alone"
LAND_TOOLING_TEST="python3 " land tests/test_ok.py; rc=$?
ok "a test standing alone lands" '[ "$rc" -eq 0 ] && [ -n "$(on_main tests/test_ok.py)" ]'

echo "4. the review ledger lands with the tooling (the push checks the clone's passes against the ledger it lands - 368, 2026-10-11)"
setup
mkdir -p "$C/dev"; printf '| row |\n' > "$C/dev/review-ledger.md"; git -C "$C" add dev; git -C "$C" commit -qm "the checks' rows"
land scripts/a.sh dev/review-ledger.md; rc=$?
ok "the ledger's rows land beside the guard fix" '[ "$rc" -eq 0 ] && [ "$(on_main dev/review-ledger.md)" = "| row |" ]'
# GUARD_EDIT_OK: feature 383 (the GM 2026-10-13) - and unnamed: a clone that changed its ledger lands it with any FILES
setup
mkdir -p "$C/dev"; printf '| row 2 |\n' > "$C/dev/review-ledger.md"; git -C "$C" add dev; git -C "$C" commit -qm "the checks' rows"
land scripts/a.sh; rc=$?
ok "the ledger lands unnamed when the clone changed it" '[ "$rc" -eq 0 ] && [ "$(on_main dev/review-ledger.md)" = "| row 2 |" ]'
ok "...and says so" 'grep -q "dev/review-ledger.md lands too" "$T/out"'

echo "6. the push runs with the backup off: the worktree is not a clone (a stale backup/<clone>-tooling, 2026-10-11)"
setup
LAND_TOOLING_PUSH='echo "backup=${SYNC_BACKUP:-on}" >&2; exit 1' land scripts/a.sh; rc=$?
ok "the push saw SYNC_BACKUP=off, and a refusal's reason is shown" '[ "$rc" -ne 0 ] && grep -q "backup=off" "$T/out"'

echo "7. the checks run without the caller's escapes, the push with them (a LEDGER_ROWS_OK waived the suites' refusals, 2026-10-12)"
setup
LEDGER_ROWS_OK="for the push" LAND_TOOLING_CHECKS='[ -z "${LEDGER_ROWS_OK:-}" ]' LAND_TOOLING_PUSH='echo "push=${LEDGER_ROWS_OK:-none}" >&2; exit 1' land scripts/a.sh; rc=$?
ok "the checks saw no escape, the push saw it" '[ "$rc" -ne 0 ] && grep -q "push=for the push" "$T/out"'

echo "5. outside a session clone it refuses"
( cd "$T/seed" && "$LAND" scripts/a.sh ) >"$T/out" 2>&1; rc=$?
ok "not under .clones/" '[ "$rc" -ne 0 ] && grep -q "not a session clone" "$T/out"'

echo
echo "land-tooling: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
