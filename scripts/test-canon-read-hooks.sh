#!/bin/bash
# Tests for canon-read-hooks.sh - the setting canon is searched with `make canon`, every term at once (feature 250 D16).
# Run: scripts/test-canon-read-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 250 D16 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload; the window cases write a real transcript file.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# CANON_HOOK lets the proof-of-firing run this suite against a mutated copy of the guard and watch it go red.
HOOK="${CANON_HOOK:-$HERE/canon-read-hooks.sh}"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
: > "$T/transcript.jsonl"
call() { # call <tool> <json tool_input> -> rc in $T/rc
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-canon","tool_name":sys.argv[1],"tool_use_id":"now","transcript_path":sys.argv[3],"tool_input":json.loads(sys.argv[2])}))' "$1" "$2" "$T/transcript.jsonl" \
    | "$HOOK" pretool 2>"$T/err"; echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
earlier() { # earlier <command> ... - the transcript's previous Bash calls, oldest first
  : > "$T/transcript.jsonl"
  local n=0
  for c in "$@"; do
    n=$((n+1))
    python3 -c 'import json,sys; print(json.dumps({"type":"assistant","message":{"content":[{"type":"tool_use","id":"t"+sys.argv[2],"name":"Bash","input":{"command":sys.argv[1]}}]}}))' "$c" "$n" >> "$T/transcript.jsonl"
  done
}

echo "1. a direct read of the canon is refused, with the command to use"
call Bash '{"command":"grep -n -i \"imperial road\" /host-l7r-repo/setting/budgets.md | head"}'
[ "$(rc)" -eq 2 ] && ok "grep on an absolute canon path" || no "allowed" "(rc=$(rc))"
grep -q 'make canon TERMS=' "$T/err" && ok "...the message names make canon" || no "no compliant command in the message"
call Bash '{"command":"cd /host-l7r-repo; grep -n -i merchant setting/l7r.md | cut -c1-200"}'
[ "$(rc)" -eq 2 ] && ok "a cd into the host repo, then a relative setting/ path" || no "allowed" "(rc=$(rc))"
call Bash '{"command":"sed -n 250,280p /host-l7r-repo/gm-assistant/setting/economics.md"}'
[ "$(rc)" -eq 2 ] && ok "sed on a gm-assistant setting file" || no "allowed" "(rc=$(rc))"
call Read '{"file_path":"/host-l7r-repo/setting/budgets.md"}'
[ "$(rc)" -eq 2 ] && ok "the Read tool on a canon file" || no "allowed" "(rc=$(rc))"
call Grep '{"pattern":"road","path":"/host-l7r-repo/gm-assistant/setting"}'
[ "$(rc)" -eq 2 ] && ok "the Grep tool on the setting directory" || no "allowed" "(rc=$(rc))"

echo "2. what is not a canon read"
call Bash '{"command":"echo see /host-l7r-repo/setting/budgets.md for the figures"}'
[ "$(rc)" -eq 0 ] && ok "a mention (echo) of the path" || no "a mention was refused"
call Bash '{"command":"grep -rn imperial .claude/skills/diagram/research/cities/"}'
[ "$(rc)" -eq 0 ] && ok "a grep over the record, not the canon" || no "refused"
call Read '{"file_path":"/diagram/.clones/x/.claude/skills/diagram/research/cities/fabric/040-q.html"}'
[ "$(rc)" -eq 0 ] && ok "a Read of a record file" || no "refused"
earlier 'ls'
call Bash '{"command":"cd .claude/skills/diagram && make canon TERMS=\"imperial road|merchant\""}'
[ "$(rc)" -eq 0 ] && ok "make canon itself" || no "make canon was refused" "(rc=$(rc))"

echo "3. make canon again within three calls is refused unless it folds the earlier terms"
earlier 'ls' 'make canon TERMS="imperial road|merchant"'
call Bash '{"command":"make canon TERMS=\"artisan\""}'
[ "$(rc)" -eq 2 ] && ok "a second call naming a new term only" || no "allowed" "(rc=$(rc))"
grep -q 'fold' "$T/err" && ok "...the message says to fold" || no "the message does not say fold"
call Bash '{"command":"make canon TERMS=\"Imperial road|merchant|artisan\""}'
[ "$(rc)" -eq 0 ] && ok "the fold - every earlier term and the new one - passes" || no "the fold was refused" "(rc=$(rc))"
earlier 'make canon TERMS="road"' 'ls' 'ls' 'ls'
call Bash '{"command":"make canon TERMS=\"artisan\""}'
[ "$(rc)" -eq 0 ] && ok "a call three or more tool calls later passes" || no "refused outside the window" "(rc=$(rc))"

echo "4. the escape, and the record"
call Bash '{"command":"sed -n 250,280p /host-l7r-repo/setting/budgets.md  # CANON_OK: the whole road-upkeep section in order"}'
[ "$(rc)" -eq 0 ] && ok "CANON_OK with a reason passes" || no "the escape was refused" "(rc=$(rc))"
call Bash '{"command":"sed -n 250,280p /host-l7r-repo/setting/budgets.md  # CANON_OK"}'
[ "$(rc)" -eq 2 ] && ok "CANON_OK with no reason is refused" || no "a bare escape passed" "(rc=$(rc))"
grep -rlq 'direct' "$GUARD_LOG_ROOT" 2>/dev/null && ok "refusals are recorded by rule" || no "no direct-rule entry recorded"

echo "-----"
if [ "$FAIL" -eq 0 ]; then echo "all canon-read-hook tests passed ($PASS)"; exit 0; fi
echo "SOME TESTS FAILED ($FAIL of $((PASS+FAIL)))"; exit 1
