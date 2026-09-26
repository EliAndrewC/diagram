#!/bin/bash
# Tests for check-bundle-hooks.sh - a record check reads a bundle, not the repository (feature 250).
# Run: scripts/test-check-bundle-hooks.sh   (exit 0 = all green)
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
Q=/diagram/.clones/x/.claude/skills/diagram/research/ways/010-how-far-past-the-bank-does-a-bridge-land.html
S=/diagram/.claude/skills/diagram/research/sources/010-works-cited/4220-edo-enwiki.html

echo "1. what is refused"
dispatch record-format "Check ONE entry: $Q and its notes."
[ "$(rc)" -eq 2 ] && ok "a record-format dispatch naming a question fragment is refused" || no "it was allowed" "(rc=$(rc))"
grep -q 'make check-bundle PAGE=ways SECTION=010' "$T/err" && ok "...and the refusal carries the command for THAT question" || no "no compliant command" "$(cat "$T/err")"
grep -q 'MANIFEST.md' "$T/err" && ok "...and says to name the MANIFEST it prints" || no "the message does not say what to re-send"
logged repo-path && ok "...recorded blocked/repo-path" || no "repo-path not recorded"
dispatch source-applicability "Judge the entry $S against its page."
[ "$(rc)" -eq 2 ] && grep -q 'make check-bundle KEY=edo-enwiki' "$T/err" && ok "a registry entry gets the KEY= form" || no "the key form is wrong" "$(cat "$T/err")"
dispatch quote-check "Check .claude/skills/diagram/research/cities/sizing/020-how-densely-is-a-quarter-built.notes.html"
[ "$(rc)" -eq 2 ] && grep -q 'PAGE=cities/sizing SECTION=020' "$T/err" && ok "a cities/ page and a notes file, relative, are read off the path too" || no "the cities path was not read" "$(cat "$T/err")"
dispatch source-reader "Read the passage quoted in .claude/skills/diagram/research/SOURCES.html"
[ "$(rc)" -eq 2 ] && grep -q 'PAGE=<page> SECTION=<question>' "$T/err" && ok "a path the guard cannot map still refuses, with the general form" || no "an unmappable path passed" "(rc=$(rc))"
dispatch record-format "CHECK_BUNDLE_OK=\"x\" read $Q"
[ "$(rc)" -eq 2 ] && logged CHECK_BUNDLE_OK-no-reason && ok "an escape with no real reason is refused and recorded" || no "a bare escape passed" "(rc=$(rc))"

echo "2. what passes"
dispatch record-format "Read /tmp/l7r-check/ways-010/MANIFEST.md and the files it lists. Origin: $Q"
[ "$(rc)" -eq 0 ] && [ ! -s "$T/err" ] && ok "a dispatch naming a bundle passes, silently, even beside an origin path" || no "a bundle dispatch was refused" "(rc=$(rc))"
logged bundle-named && ok "...recorded permitted/bundle-named" || no "bundle-named not recorded"
dispatch source-reader "Report per claim whether https://en.wikipedia.org/wiki/Edo says it."
[ "$(rc)" -eq 0 ] && logged no-repo-path && ok "a dispatch naming no repository file passes (a reader handed URLs)" || no "a URL-only dispatch was refused" "(rc=$(rc))"
dispatch record-format "CHECK_BUNDLE_OK=\"the glossary term file itself is under review\" read $Q"
[ "$(rc)" -eq 0 ] && logged check-bundle-ok && ok "an escape with a reason passes and is recorded" || no "a reasoned escape was refused" "(rc=$(rc))"
dispatch entry-drift "Compare the modal with /diagram/.claude/skills/diagram/research/fields/190-the-wettest.html"
[ "$(rc)" -eq 2 ] && grep -q "PAGE=fields SECTION=190" "$T/err" && ok "an entry-drift dispatch into the tree is refused too" || no "entry-drift passed" "(rc=$(rc))"
dispatch spec-fidelity "Review /diagram/.claude/skills/diagram/research/ways/010-x.html"
[ "$(rc)" -eq 0 ] && ok "an agent that is not a record check is not this guard's business" || no "spec-fidelity was refused" "(rc=$(rc))"
out=$(printf '{"session_id":"t","tool_name":"Bash","tool_input":{"command":"make done"}}' | ( cd "$T" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && [ -z "$out" ] && ok "a Bash call is ignored" || no "a Bash call was not ignored" "(rc=$r)"
out=$(printf 'not json' | ( cd "$T" && "$HOOK" pretool 2>/dev/null )); r=$?
[ "$r" -eq 0 ] && ok "a payload that is not JSON never blocks" || no "a broken payload blocked" "(rc=$r)"

echo "3. the guard and the contracts agree"
ROOT="$(dirname "$HERE")"
for a in quote-check record-format source-applicability source-reader entry-drift; do
  grep -q 'Read the BUNDLE you are given' "$ROOT/.claude/agents/$a.md" && ! grep -q '^tools: .*Write' "$ROOT/.claude/agents/$a.md" \
    && ok "$a's contract reads the bundle, and writes nothing (the harness refuses a subagent's report file)" || no "$a's contract does not match the guard"
done
"$HOOK" bogus >/dev/null 2>&1; [ $? -eq 1 ] && ok "an unknown mode is an error, not a pass" || no "an unknown mode passed"

echo
echo "test-check-bundle-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
