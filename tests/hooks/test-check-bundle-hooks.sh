#!/bin/bash
# Tests for check-bundle-hooks.sh - a record check reads a bundle, not the repository (feature 250).
# Run: tests/hooks/test-check-bundle-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 250 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload, because a grep proves a call site exists and not
# that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# CHECK_BUNDLE_HOOK lets the proof-of-firing run this suite against a MUTATED copy of the guard.
HOOK="${CHECK_BUNDLE_HOOK:-$HERE/check-bundle-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
dispatch() { # dispatch <subagent_type> <prompt> -> rc in $T/rc, stderr in $T/err
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-check-bundle","cwd":"/tmp","tool_name":"Agent","tool_input":{"subagent_type":sys.argv[1],"prompt":sys.argv[2],"description":"x"}}))' "$1" "$2" \
    | ( cd "$T" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }
Q=/diagram/.clones/x/research/questions/0087-road-bridges-over-rivers-and-canals-hashi.html
S=/diagram/research/sources/010-works-cited/4220-edo-enwiki.html
# GUARD_EDIT_OK: feature 311 - the bundles the suite names are its own, written here with the owed section a bundle carries
mkdir -p "$T/q-0087" "$T/q-old"
printf '# Check bundle - question 0087\n\n## Owed (feature 311)\n\nowed-checks: record-format\nunit: record-format:0087 abc\n' > "$T/q-0087/MANIFEST.md"
printf '# Check bundle - question 0087\n' > "$T/q-old/MANIFEST.md"

echo "1. what is refused"
dispatch record-format "Check ONE entry: $Q and its notes."
[ "$(rc)" -eq 2 ] && ok "a record-format dispatch naming a question fragment is refused" || no "it was allowed" "(rc=$(rc))"
grep -q 'make check-bundle Q=0087' "$T/err" && ok "...and the refusal carries the command for THAT question" || no "no compliant command" "$(cat "$T/err")"
grep -q 'MANIFEST.md' "$T/err" && ok "...and says to name the MANIFEST it prints" || no "the message does not say what to re-send"
logged repo-path && ok "...recorded blocked/repo-path" || no "repo-path not recorded"
# GUARD_EDIT_OK: feature 292 - the new record-style check is refused the same way, and told to build ITS bundle
dispatch record-style "Judge the style of $Q and its notes."
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle Q=0087 FOR=record-style' "$T/err" && ok "a record-style dispatch into the repository is refused with its own bundle's command" || no "record-style was not refused, or the command lacks FOR=" "$(cat "$T/err")"
dispatch translation-check "Judge the translations in $Q and its notes."
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle Q=0087 FOR=translation-check' "$T/err" && ok "a translation-check dispatch into the repository is refused with its own bundle's command" || no "translation-check was not refused, or the command lacks FOR=" "$(cat "$T/err")"
dispatch source-applicability "Judge the entry $S against its page."
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle KEY=edo-enwiki' "$T/err" && ! grep -q 'WHOLE=1' "$T/err" && ok "a registry entry gets the KEY= form (the excerpt, for source-applicability)" || no "the key form is wrong" "$(cat "$T/err")"
# GUARD_EDIT_OK: feature 250 D19 - a source-reader's command is the whole page in parts, never the excerpt
dispatch source-reader "Read the entry $S and find the passage behind the claim."
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle KEY=edo-enwiki WHOLE=1' "$T/err" && ok "a source-reader gets KEY= WHOLE=1 - the whole page, not the excerpt" || no "source-reader was not given WHOLE=1" "$(cat "$T/err")"
# GUARD_EDIT_OK: feature 303 - a question's files are research/questions/NNNN-<slug>...; the command names its number
dispatch quote-check "Check research/questions/0151-how-densely-is-a-quarter-built.drawing.notes.html"
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle Q=0151' "$T/err" && ok "a drawing page's notes file, relative, is read off the path too" || no "the drawing notes path was not read" "$(cat "$T/err")"
dispatch source-reader "Read the passage quoted in research/SOURCES.html"
[ "$(rc)" -eq 2 ] && grep -q 'Q=<question number>' "$T/err" && ok "a path the guard cannot map still refuses, with the general form" || no "an unmappable path passed" "(rc=$(rc))"
dispatch record-format "CHECK_BUNDLE_OK=\"x\" read $Q"
[ "$(rc)" -eq 2 ] && logged CHECK_BUNDLE_OK-no-reason && ok "an escape with no real reason is refused and recorded" || no "a bare escape passed" "(rc=$(rc))"

echo "2. what passes"
dispatch record-format "Read $T/q-0087/MANIFEST.md and the files it lists. Origin: $Q"
[ "$(rc)" -eq 0 ] && [ ! -s "$T/err" ] && ok "a dispatch naming a bundle passes, silently, even beside an origin path" || no "a bundle dispatch was refused" "(rc=$(rc))"
logged bundle-named && ok "...recorded permitted/bundle-named" || no "bundle-named not recorded"
dispatch source-reader "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 0 ] && logged no-repo-path && ok "a dispatch naming no repository file passes (a reader handed URLs)" || no "a URL-only dispatch was refused" "(rc=$(rc))"
dispatch record-format "CHECK_BUNDLE_OK=\"the glossary term file itself is under review\" read $Q"
[ "$(rc)" -eq 0 ] && logged check-bundle-ok && ok "an escape with a reason passes and is recorded" || no "a reasoned escape was refused" "(rc=$(rc))"
dispatch entry-drift "Compare the modal with /diagram/research/questions/0007-the-wettest.html"
[ "$(rc)" -eq 2 ] && grep -q "Q=0007" "$T/err" && ok "an entry-drift dispatch into the tree is refused too" || no "entry-drift passed" "(rc=$(rc))"
dispatch spec-fidelity "Review /diagram/research/questions/0010-x.html"
[ "$(rc)" -eq 0 ] && ok "an agent that is not a record check is not this guard's business" || no "spec-fidelity was refused" "(rc=$(rc))"
out=$(printf '{"session_id":"t","tool_name":"Bash","tool_input":{"command":"make done"}}' | ( cd "$T" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && [ -z "$out" ] && ok "a Bash call is ignored" || no "a Bash call was not ignored" "(rc=$r)"
out=$(printf 'not json' | ( cd "$T" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && ok "a payload that is not JSON never blocks" || no "a broken payload blocked" "(rc=$r)"

echo "3. what is not owed (feature 311)"
dispatch quote-check "Read $T/q-0087/MANIFEST.md."
[ "$(rc)" -eq 2 ] && grep -q "owes: record-format" "$T/err" && logged not-owed && ok "a check the MANIFEST does not owe is refused, naming what it owes" || no "an unowed check passed" "(rc=$(rc))"
dispatch record-format "Read $T/q-old/MANIFEST.md."
[ "$(rc)" -eq 2 ] && grep -q "build it again" "$T/err" && ok "a bundle with no owed section (from before 311) is refused" || no "an old bundle passed" "(rc=$(rc))"
dispatch quote-check "CHECK_NOT_OWED_OK=\"the GM asked for an audit\" Read $T/q-0087/MANIFEST.md."
[ "$(rc)" -eq 0 ] && logged check-not-owed-ok && ok "CHECK_NOT_OWED_OK with a reason passes and is recorded" || no "a reasoned escape was refused" "(rc=$(rc))"
dispatch quote-check "CHECK_NOT_OWED_OK=\"x\" Read $T/q-0087/MANIFEST.md."
[ "$(rc)" -eq 2 ] && logged CHECK_NOT_OWED_OK-no-reason && ok "a bare CHECK_NOT_OWED_OK is refused" || no "a bare escape passed" "(rc=$(rc))"
dispatch record-style "Read $T/q-old/MANIFEST.md."
[ "$(rc)" -eq 0 ] && ok "record-style is owed by its sweep, never refused here" || no "record-style was refused" "(rc=$(rc))"
dispatch intro-check "Check $Q"
[ "$(rc)" -eq 2 ] && ok "intro-check is a bundle-reading check too" || no "intro-check read the tree" "(rc=$(rc))"
mkdir -p "$T/claims-x"; printf '# Bundle for impl-drift (feature 316)\nowed-checks: impl-drift\n' > "$T/claims-x/MANIFEST.md"
dispatch impl-drift "Read $T/claims-x/MANIFEST.md."
[ "$(rc)" -eq 0 ] && logged bundle-named && ok "impl-drift on a claims bundle that owes it passes (feature 316)" || no "impl-drift on its bundle was refused" "(rc=$(rc))"
dispatch impl-drift "Read $T/q-0087/MANIFEST.md."
[ "$(rc)" -eq 2 ] && ok "impl-drift on a bundle that does not owe it is refused" || no "impl-drift on a record bundle passed" "(rc=$(rc))"

echo "5. decide first judges the check's own task, never the mark's (449 T258)"
# a clone of two open tasks, through the clone's real gate (the wrapper sets L7R_GUARD_TREE to its own tree): T2's plan section carries
# no verdict, T1 owes none (no section); the mark's form (no task) names the first open task, T2, as the real gate's did for every one
# of T197 G1's checks
C="$T/clone"; mkdir -p "$C/.specify" "$C/specs/449-x/briefs"; git init -q "$C"
printf '{"feature_directory": "specs/449-x"}\n' > "$C/.specify/feature.json"
printf -- '- [ ] T2 two\n- [ ] T1 one\n' > "$C/specs/449-x/tasks.md"
printf '# plan\n\n## T2 two\n\n- a decision\n' > "$C/specs/449-x/plan.md"
printf '# Brief - feature 449 task T2, group G1: check and apply\n' > "$C/specs/449-x/briefs/t2-checks.md"
mkdir -p "$C/.git/page-sessions"; printf 'sid-2 %s\n' "$C/specs/449-x/briefs/t2-checks.md" > "$C/.git/page-sessions/index.txt"
own() { # own <description> <prompt> -> rc in $T/rc, stderr in $T/err, from the clone
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-check-bundle","cwd":sys.argv[3],"tool_name":"Agent","tool_input":{"subagent_type":"source-reader","prompt":sys.argv[2],"description":sys.argv[1]}}))' "$1" "$2" "$C" \
    | ( cd "$C" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
own "449 T1: source-reader on 0221" "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 0 ] && ok "a check naming a task that owes no decision passes while another open task is undecided" || no "it was judged on another task" "$(cat "$T/err")"
own "449 T2: source-reader on 0221" "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 2 ] && grep -q '449-x T2: its plan section' "$T/err" && ok "...and one naming the undecided task is refused on that task's verdict" || no "the undecided task's check passed" "(rc=$(rc)) $(cat "$T/err")"
own "source-reader on 0221" "449 T1's claims re-check: report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 0 ] && ok "a task its prompt's first line names is its own" || no "the prompt's task was not read" "$(cat "$T/err")"
own "source-reader on 0221" "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 2 ] && grep -q 'names no task it serves' "$T/err" && grep -q '449-x T2' "$T/err" && ok "a check that names no task is held by the mark and told to name its task" || no "a check naming no task passed silently" "(rc=$(rc)) $(cat "$T/err")"
export L7R_PAGE_SESSION=sid-2
own "source-reader on 0221" "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 2 ] && grep -q '449-x T2' "$T/err" && ok "a page session's check is judged on its brief's task" || no "the brief's task was not read" "(rc=$(rc)) $(cat "$T/err")"
unset L7R_PAGE_SESSION

echo "4. the guard and the contracts agree"
ROOT="$(cd "$HERE/../.." && pwd)"
for a in quote-check record-format source-applicability source-reader entry-drift; do
  grep -q 'Read the BUNDLE you are given' "$ROOT/.claude/agents/$a.md" && ! grep -q '^tools: .*Write' "$ROOT/.claude/agents/$a.md" \
    && ok "$a's contract reads the bundle, and writes nothing (the harness refuses a subagent's report file)" || no "$a's contract does not match the guard"
done
"$HOOK" bogus >/dev/null 2>&1; [ $? -eq 1 ] && ok "an unknown mode is an error, not a pass" || no "an unknown mode passed"

echo
echo "test-check-bundle-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
