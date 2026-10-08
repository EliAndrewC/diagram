#!/bin/bash
# Tests for record-edit-hooks.sh - an edit aimed at a built record page goes to the fragment holding its text.
# Run: tests/hooks/test-record-edit-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 258 - a NEW guard's companion suite.
# GUARD_EDIT_OK: feature 303 - the fixture is the flat layout: questions in research/questions/, the registry's fragments
# in research/sources/; a built page of the site is re-aimed among them. The same cases, nothing loosened.
#
# Every case drives the REAL hook with a REAL payload against a fixture record, because a grep proves
# a call site exists and not that it fires.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# RECORD_EDIT_HOOK lets the proof-of-firing run this suite against a MUTATED copy of the guard (its
# refusal removed) and watch it go red, without touching the real file.
HOOK="${RECORD_EDIT_HOOK:-$HERE/../../scripts/hooks/record-edit-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT

FIX="$T/clone"; R="$FIX/research"; Q="$R/questions"
mkdir -p "$Q" "$R/sources/010-works-cited" "$R/site/q" "$R/site/sources"
git -C "$FIX" init -q 2>/dev/null
printf '<h2 id="x">X</h2>\nthe deck lands ten feet past the bank\n' > "$Q/0010-x.html"
printf '<li data-note="ritter">bearing area at beam reactions</li>\n' > "$Q/0010-x.notes.html"
printf '<h2 id="y">Y</h2>\na shared sentence\n' > "$Q/0020-y.html"
printf '<h2 id="z">Z</h2>\na shared sentence\n' > "$Q/0030-z.html"
printf '<h3 id="fei-1939"><code>fei-1939</code></h3>\n<p>Fei, a book on the village</p>\n' > "$R/sources/010-works-cited/0010-fei-1939.html"
printf 'the deck lands ten feet past the bank\n' > "$R/site/q/x.html"; cp "$R/site/q/x.html" "$R/site/all.html"
printf 'bearing area at beam reactions\n' > "$R/site/q/x-notes.html"
printf 'Fei, a book on the village\n' > "$R/site/sources/fei-1939.html"

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
edit Edit "$R/site/q/x.html" "ten feet past the bank"
[ "$(rc)" = 0 ] && [ "$(rewrote_to)" = "$Q/0010-x.html" ] && ok "a question's page of the site -> its question file" \
  || no "a question's page of the site -> its question file" "rc=$(rc) to=$(rewrote_to)"
edit Edit "$R/site/q/x-notes.html" "bearing area at beam reactions"
[ "$(rc)" = 0 ] && [ "$(rewrote_to)" = "$Q/0010-x.notes.html" ] && ok "a note shown on the site -> the notes file beside its question" \
  || no "a note shown on the site -> the notes file" "to=$(rewrote_to)"
edit Edit "$R/site/sources/fei-1939.html" "Fei, a book on the village"
[ "$(rewrote_to)" = "$R/sources/010-works-cited/0010-fei-1939.html" ] && ok "a registry entry's page -> its registry fragment" \
  || no "a registry entry's page -> its registry fragment" "to=$(rewrote_to)"
edit Edit "$R/site/all.html" "ten feet past the bank"
[ "$(rewrote_to)" = "$Q/0010-x.html" ] && ok "the single page -> the one fragment holding it, the site itself never a holder" \
  || no "the single page -> the one fragment holding it" "to=$(rewrote_to)"
edit Edit "$R/fields.html" "ten feet past the bank"
[ "$(rewrote_to)" = "$Q/0010-x.html" ] && ok "a page the record assembled before feature 301 -> the question holding the text" \
  || no "a page assembled before 301" "to=$(rewrote_to)"
logged edit-moved-to-fragment && ok "the rewrite is recorded" || no "the rewrite is recorded"

echo "2. what is refused, because a guard cannot make the choice"
edit Edit "$R/site/q/x.html" "a shared sentence"
[ "$(rc)" = 2 ] && grep -q "0020-y.html" "$T/err" && grep -q "0030-z.html" "$T/err" \
  && ok "text in several fragments: refused, and both are named" || no "text in several fragments" "rc=$(rc)"
edit Edit "$R/site/q/x.html" "a sentence on no fragment"
[ "$(rc)" = 2 ] && grep -q "footnote number" "$T/err" \
  && ok "text in no fragment: refused, and says what the assembly writes" || no "text in no fragment" "rc=$(rc)"
edit Write "$R/site/q/x.html" ""
[ "$(rc)" = 2 ] && grep -q "cannot be routed" "$T/err" && ok "a whole-file Write is refused" || no "a whole-file Write is refused"
grep -q "make record" "$T/err" && ok "every refusal names the command that fixes it" || no "every refusal names the command"
logged text-in-several-fragments && ok "the refusal is recorded by its rule" || no "the refusal is recorded by its rule"

echo "3. what it does NOT touch"
edit Edit "$Q/0010-x.html" "ten feet past the bank"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "an edit already aimed at a question file passes" || no "an edit aimed at a question file passes"
edit Edit "$R/sources/010-works-cited/0010-fei-1939.html" "Fei"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "an edit aimed at a registry fragment passes" || no "an edit aimed at a registry fragment passes"
edit Edit "$FIX/docs/guards.md" "anything"
[ "$(rc)" = 0 ] && [ -z "$(rewrote_to)" ] && ok "a file outside the record passes" || no "a file outside the record passes"

echo "4. the decision module's own selftest"
python3 "$HERE/../../scripts/hooks/lib/hm_record.py" --selftest >/dev/null && ok "_hm_record --selftest" || no "_hm_record --selftest"

echo
echo "record-edit-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
