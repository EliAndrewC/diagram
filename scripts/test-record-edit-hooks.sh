#!/bin/bash
# Tests for record-edit-hooks.sh - an edit aimed at an assembled record page goes to its fragment.
# Run: scripts/test-record-edit-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 258 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a fixture record, because a grep proves
# a call site exists and not that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# RECORD_EDIT_HOOK lets the proof-of-firing run this suite against a MUTATED copy of the guard (its
# refusal removed) and watch it go red, without touching the real file.
HOOK="${RECORD_EDIT_HOOK:-$HERE/record-edit-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT

FIX="$T/clone"; R="$FIX/.claude/skills/diagram/research"
mkdir -p "$R/ways" "$R/cities/fabric" "$R/citations/cities"
git -C "$FIX" init -q 2>/dev/null
printf '<h2 id="x">X</h2>\nthe deck lands ten feet past the bank\n' > "$R/ways/010-x.html"
printf '<li data-note="ritter">bearing area at beam reactions</li>\n' > "$R/ways/010-x.notes.html"
printf '<h2 id="y">Y</h2>\na shared sentence\n' > "$R/ways/020-y.html"
printf '<h2 id="z">Z</h2>\na shared sentence\n' > "$R/ways/030-z.html"
printf '<h2 id="w">W</h2>\nthe ward wall stands\n' > "$R/cities/fabric/010-w.html"
printf 'assembled\n' > "$R/ways.html"; printf 'assembled\n' > "$R/citations/ways.html"
printf 'assembled\n' > "$R/cities/fabric.html"; printf 'assembled\n' > "$R/citations/cities/fabric.html"
printf 'whole, not split yet\n' > "$R/towns.html"

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
edit() { # edit <tool> <file_path> <old_string> -> rc in $T/rc, stdout in $T/out, stderr in $T/err
  python3 -c '
import json, sys
print(json.dumps({"session_id": "t-record-edit", "cwd": sys.argv[1], "tool_name": sys.argv[2],
                  "tool_input": {"file_path": sys.argv[3], "old_string": sys.argv[4], "new_string": "N"}}))' \
    "$FIX" "$1" "$2" "${3:-}" | ( cd "$FIX" && "$HOOK" pretool >"$T/out" 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
rewrote_to() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["hookSpecificOutput"]["updatedInput"]["file_path"])' "$T/out" 2>/dev/null; }
logged() { grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }

echo "1. an edit whose text stands in exactly one fragment is RE-AIMED at it"
edit Edit "$R/ways.html" "ten feet past the bank"
[ "$(rc)" = 0 ] && [ "$(rewrote_to)" = "$R/ways/010-x.html" ] && ok "research page -> its question fragment" \
  || no "research page -> its question fragment" "rc=$(rc) to=$(rewrote_to)"
edit Edit "$R/citations/ways.html" "bearing area at beam reactions"
[ "$(rc)" = 0 ] && [ "$(rewrote_to)" = "$R/ways/010-x.notes.html" ] && ok "citations page -> the notes fragment beside the question" \
  || no "citations page -> the notes fragment beside the question" "to=$(rewrote_to)"
edit Edit "$R/cities/fabric.html" "the ward wall stands"
[ "$(rc)" = 0 ] && [ "$(rewrote_to)" = "$R/cities/fabric/010-w.html" ] && ok "a cities/ page, one level down" \
  || no "a cities/ page, one level down" "to=$(rewrote_to)"
edit Edit "$R/citations/cities/fabric.html" "the ward wall stands"
[ "$(rewrote_to)" = "$R/cities/fabric/010-w.html" ] && ok "a cities/ citations page resolves to the same directory" \
  || no "a cities/ citations page resolves to the same directory" "to=$(rewrote_to)"
logged edit-moved-to-fragment && ok "the rewrite is recorded" || no "the rewrite is recorded"

echo "2. what is refused, because a guard cannot make the choice"
edit Edit "$R/ways.html" "a shared sentence"
[ "$(rc)" = 2 ] && grep -q "020-y.html" "$T/err" && grep -q "030-z.html" "$T/err" \
  && ok "text in several fragments: refused, and both are named" || no "text in several fragments" "rc=$(rc)"
edit Edit "$R/ways.html" "a sentence on no fragment"
[ "$(rc)" = 2 ] && grep -q "footnote number" "$T/err" \
  && ok "text in no fragment: refused, and says what the assembly writes" || no "text in no fragment" "rc=$(rc)"
edit Write "$R/ways.html" ""
[ "$(rc)" = 2 ] && grep -q "cannot be routed" "$T/err" && ok "a whole-file Write is refused" || no "a whole-file Write is refused"
grep -q "make record" "$T/err" && ok "every refusal names the command that fixes it" || no "every refusal names the command"
logged text-in-several-fragments && ok "the refusal is recorded by its rule" || no "the refusal is recorded by its rule"

echo "3. what it does NOT touch"
edit Edit "$R/ways/010-x.html" "ten feet past the bank"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "an edit already aimed at a fragment passes" || no "an edit aimed at a fragment passes"
edit Edit "$R/towns.html" "whole, not split yet"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "a page whose stage has not landed passes" || no "a page whose stage has not landed passes"
edit Edit "$FIX/docs/guards.md" "anything"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "a file outside the record passes" || no "a file outside the record passes"

echo "4. the decision module's own selftest"
python3 "$HERE/_hm_record.py" --selftest >/dev/null && ok "_hm_record --selftest" || no "_hm_record --selftest"

echo
echo "record-edit-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
