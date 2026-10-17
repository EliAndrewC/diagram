#!/usr/bin/env bash
# test-gate-write-hooks.sh - gate-write-hooks.sh refuses a write to the tree while this tree's `make done` runs, and nothing
# else (feature 385 T02, plan D13). GUARD_EDIT_OK: feature 385 - the new guard's test companion.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/gate-write-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL    $1"; FAIL=$((FAIL+1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected $2, got $3)"; fi; }

R=$(mktemp -d); OTHER=$(mktemp -d)
git -C "$R" init -q; git -C "$OTHER" init -q
printf 'done:\n\t@sleep 30\n' > "$R/Makefile"
run() {  # run <dir> <json payload>: the hook's exit code, from that directory
  ( cd "$1" && printf '%s' "$2" | "$HOOK" pretool >/dev/null 2>"$R/err" ); echo $?
}
EDIT=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/a.txt","old_string":"a","new_string":"b"}}' "$R")
COMMIT='{"tool_name":"Bash","tool_input":{"command":"git -C . commit -qm x"}}'
APPEND='{"tool_name":"Bash","tool_input":{"command":"make append FILE=dev/review-ledger.md LINE=x"}}'
ADD='{"tool_name":"Bash","tool_input":{"command":"git -C . add -A"}}'
RECORD='{"tool_name":"Bash","tool_input":{"command":"make record-checked CHECK=quote-check BUNDLE=/tmp/b RESULT=ok"}}'
READ='{"tool_name":"Bash","tool_input":{"command":"tail -3 .git/verify-gate.log"}}'

echo "--- 1. no gate running: nothing is refused ---"
check "an Edit with no gate running" 0 "$(run "$R" "$EDIT")"
check "a commit with no gate running" 0 "$(run "$R" "$COMMIT")"

echo "--- 2. this tree's make done running ---"
( cd "$R" && setsid nohup make done </dev/null >/dev/null 2>&1 & )
for _ in $(seq 1 50); do pgrep -f "[m]ake done" >/dev/null && break; sleep 0.1; done
check "an Edit inside the tree: refused" 2 "$(run "$R" "$EDIT")"
check "...naming make verify-wait" yes "$(grep -q 'make verify-wait' "$R/err" && echo yes || echo no)"
check "a git commit: refused" 2 "$(run "$R" "$COMMIT")"
check "make append (the ledger): refused" 2 "$(run "$R" "$APPEND")"
check "git add: refused (a staged new file is in what the gate compares)" 2 "$(run "$R" "$ADD")"
check "make record-checked: refused (a REPLY files rows in a tracked found.jsonl)" 2 "$(run "$R" "$RECORD")"
check "make modal-triaged (writes under .git only): let through" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"make modal-triaged BUNDLE=/tmp/b REPLY=/tmp/r"}}')"
check "a read: let through" 0 "$(run "$R" "$READ")"
check "the escape: let through" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"GATE_WRITE_OK=\"a deliberate fix for the gate itself\" git -C . commit -qm x"}}')"
check "another tree's command, its own gate not running: let through" 0 "$(run "$OTHER" "$COMMIT")"
check "an Edit outside this tree: let through" 0 "$(run "$R" "$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/b.txt"}}' "$OTHER")")"
pkill -f "sleep 30" 2>/dev/null

echo "-----"
printf 'test-gate-write-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
rm -rf "$R" "$OTHER" "$LOGROOT"
[ "$FAIL" = 0 ] || exit 1
