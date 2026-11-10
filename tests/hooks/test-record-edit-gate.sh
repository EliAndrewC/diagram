#!/bin/bash
# Tests for the `record-edit-gate` guard (feature 449 T053): the record-edit suite's own cases through the gate, what it does with no
# repository, and that a plain call starts no Python - the point of the gate, which a wall time cannot show.
# GUARD_EDIT_OK: feature 449 T053 - the gate's companion suite.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/record-edit-hooks.sh"
PASS=0; FAIL=0
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
T=$(mktemp -d); export GUARD_LOG_DIR="$T/log"; mkdir -p "$GUARD_LOG_DIR"; trap 'rm -rf "$T"' EXIT

echo "1. the record-edit suite's cases, through the guard's prefilter"
if RECORD_EDIT_HOOK="$GATE" "$HERE/test-record-edit-hooks.sh" >"$T/suite" 2>&1; then ok "every case keeps its verdict ($(tail -1 "$T/suite"))"
else no "a case changed through the guard" "$(grep FAIL "$T/suite" | head -5)"; fi

payload() { # payload <cwd> <tool> <field> <value>
  jq -nc --arg cwd "$1" --arg tool "$2" --arg field "$3" --arg value "$4" '{"session_id": "t", "tool_use_id": "u", "cwd": $cwd, "tool_name": $tool, "tool_input": {($field): $value, "old_string": "o", "new_string": "n"}}'
}

echo "2. with no repository a plain call is passed"
NR="$T/no-repository"; mkdir -p "$NR"
quiet() { # quiet <label> <tool> <field> <value>
  local p rc out; p=$(payload "$NR" "$2" "$3" "$4")
  out=$(cd "$NR" && printf '%s' "$p" | "$GATE" pretool 2>/dev/null); rc=$?
  { [ "$rc" = 0 ] && [ -z "$out" ] && ok "$1"; } || no "$1" "rc=$rc out='$out'"
}
quiet "a plain Bash call" Bash command "ls"
quiet "a plain Edit" Edit file_path "$NR/notes.md"

echo "3. a plain call starts no Python, and the sentinel would have seen one"
mkdir -p "$T/bin"; REAL=$(command -v python3)
printf '#!/bin/bash\ntouch %q\nexec %q "$@"\n' "$T/python-started" "$REAL" > "$T/bin/python3"; chmod +x "$T/bin/python3"
R="$T/repo"; mkdir -p "$R"; git -C "$R" init -q
call() { payload "$R" "$1" "$2" "$3" > "$T/in"; rm -f "$T/python-started"; ( cd "$R" && PATH="$T/bin:$PATH" "$GATE" pretool < "$T/in" >/dev/null 2>&1 ); }
call Bash command "ls"; [ ! -e "$T/python-started" ] && ok "a plain Bash call" || no "a plain Bash call started Python"
call Edit file_path "$R/notes.md"; [ ! -e "$T/python-started" ] && ok "a plain Edit" || no "a plain Edit started Python"
printf '{\n "plan_holds": {},\n "dispatches": {}\n}\n' > "$R/.git/checks-open.json"
call Bash command "ls"; [ ! -e "$T/python-started" ] && ok "a plain Bash call after a hold has ended (the key stays, empty)" || no "the empty key started Python"
call Bash command "make done"; [ ! -e "$T/python-started" ] && ok "a make done starts no Python: the freeze is Rust (feature 449 T86)" || no "a make done started Python"

printf '{"plan_holds": {"never-launched": {"feature": "f", "task": "T1", "blocks": [], "t": 1, "state": "pending"}}, "dispatches": {}}\n' > "$R/.git/checks-open.json"
call Bash command "ls"; [ ! -e "$T/python-started" ] && grep -q '"plan_holds": {}' "$R/.git/checks-open.json" && ok "a hold that never launched is purged, and starts nothing" || no "the stale hold was not purged" "$(cat "$R/.git/checks-open.json")"
call Bash command "ls"; [ ! -e "$T/python-started" ] && ok "...and the next plain call starts nothing" || no "a plain call started Python"

echo
echo "record-edit-gate: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
