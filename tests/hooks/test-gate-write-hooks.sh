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
# THE FIXTURE'S OWN GATE, AS THE GUARD SEES IT (405 T61): `pgrep -f "make done"` also matched a real gate running elsewhere on the
# machine - the landing's, beside its cohort - so the wait ended before this fixture's started and three cases read "let through"
for _ in $(seq 1 50); do ( cd "$R" && "$HERE/../../scripts/hooks/lib/own-make.sh" done ) && break; sleep 0.1; done
check "an Edit inside the tree: refused" 2 "$(run "$R" "$EDIT")"
check "...naming make verify-wait" yes "$(grep -q 'make verify-wait' "$R/err" && echo yes || echo no)"
check "a git commit: refused" 2 "$(run "$R" "$COMMIT")"
check "make append (the ledger, a claims-round record): let through (405 T41)" 0 "$(run "$R" "$APPEND")"
check "make claims-checked: let through (405 T41)" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"make claims-checked BUNDLE=/tmp/b REPLY=/tmp/r"}}')"
check "make tick: refused" 2 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"make tick F=405 T=T01 NOTE=x"}}')"
check "git add: refused (a staged new file is in what the gate compares)" 2 "$(run "$R" "$ADD")"
check "make record-checked: refused (a REPLY files rows in a tracked found.jsonl)" 2 "$(run "$R" "$RECORD")"
check "make modal-triaged (writes under .git only): let through" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"make modal-triaged BUNDLE=/tmp/b REPLY=/tmp/r"}}')"
check "a read: let through" 0 "$(run "$R" "$READ")"
check "the escape: let through" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"GATE_WRITE_OK=\"a deliberate fix for the gate itself\" git -C . commit -qm x"}}')"
check "another tree's command, its own gate not running: let through" 0 "$(run "$OTHER" "$COMMIT")"
check "an Edit outside this tree: let through" 0 "$(run "$R" "$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/b.txt"}}' "$OTHER")")"
pkill -f "sleep 30" 2>/dev/null

echo "--- 3. a change the gate does not see (feature 405 T41, D15) ---"
# a tree with the gate's own tools: a docstring or comment in an engine file, or a claims-round record, passes; code does not
S=$(mktemp -d); git -C "$S" init -q
mkdir -p "$S/scripts/gates" "$S/l7r/diagram" "$S/dev"
cp "$HERE/../../scripts/gates/preflight.py" "$HERE/../../scripts/gates/gate-stamp.py" "$HERE/../../scripts/gates/codeid.py" "$S/scripts/gates/"; mkdir -p "$S/scripts/hooks/lib"; cp "$HERE/../../scripts/hooks/lib/usage_log.py" "$S/scripts/hooks/lib/"
printf 'def f(x):\n    """Research: a claim - NONE"""\n    return x + 1\n' > "$S/l7r/diagram/m.py"
printf '{}\n' > "$S/dev/claims-index.json"
printf 'done:\n\t@sleep 30\n' > "$S/Makefile"
git -C "$S" add -A; git -C "$S" -c user.email=t@t -c user.name=t commit -qm base
python3 "$S/scripts/gates/preflight.py" --root "$S" --tree-snap "$S/.git/gate-tree.json"
( cd "$S" && setsid nohup make done </dev/null >/dev/null 2>&1 & )
for _ in $(seq 1 50); do ( cd "$S" && "$HERE/../../scripts/hooks/lib/own-make.sh" done ) && break; sleep 0.1; done
DOC=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/l7r/diagram/m.py","old_string":"a claim - NONE","new_string":"a claim reworded - NONE"}}' "$S")
CODE=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/l7r/diagram/m.py","old_string":"x + 1","new_string":"x + 2"}}' "$S")
check "an Edit of a claim docstring: let through" 0 "$(run "$S" "$DOC")"
check "an Edit of a code token: refused" 2 "$(run "$S" "$CODE")"
check "a Write of a claims-round record: let through" 0 "$(run "$S" "$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s/dev/claims-index.json","content":"{\\"k\\": 1}\\n"}}' "$S")")"
sed -i 's/a claim - NONE/a claim reworded - NONE/' "$S/l7r/diagram/m.py"; printf '{"k": 1}\n' > "$S/dev/claims-index.json"
check "a commit of only those: let through" 0 "$(run "$S" "$COMMIT")"
git -C "$S" -c user.email=t@t -c user.name=t commit -qam claims
check "...and the gate's tree check reads the run as unmoved" 0 "$(python3 "$S/scripts/gates/preflight.py" --root "$S" --tree-check "$S/.git/gate-tree.json" >/dev/null; echo $?)"
sed -i 's/x + 1/x + 2/' "$S/l7r/diagram/m.py"
check "a commit holding code: refused" 2 "$(run "$S" "$COMMIT")"
check "...and the tree check names it" 1 "$(python3 "$S/scripts/gates/preflight.py" --root "$S" --tree-check "$S/.git/gate-tree.json" >/dev/null; echo $?)"
pkill -f "sleep 30" 2>/dev/null
rm -rf "$S"

echo "--- 4. while make cache-audit runs (feature 426 T10: 335cfa840 swept in the audit's perturbation) ---"
A=$(mktemp -d); git -C "$A" init -q; mkdir -p "$A/l7r/diagram" "$A/docs"
printf 'cache-audit:\n\t@sleep 31\n' > "$A/Makefile"
( cd "$A" && setsid nohup make cache-audit </dev/null >/dev/null 2>&1 & )
for _ in $(seq 1 50); do ( cd "$A" && "$HERE/../../scripts/hooks/lib/own-make.sh" cache-audit ) && break; sleep 0.1; done
check "a commit during the audit: refused" 2 "$(run "$A" "$COMMIT")"
check "an Edit of an engine file during the audit: refused, even a docstring" 2 "$(run "$A" "$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/l7r/diagram/m.py","old_string":"a","new_string":"b"}}' "$A")")"
check "an Edit of a doc during the audit: let through" 0 "$(run "$A" "$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/docs/x.md","old_string":"a","new_string":"b"}}' "$A")")"
check "the escape during the audit: let through" 0 "$(run "$A" '{"tool_name":"Bash","tool_input":{"command":"GATE_WRITE_OK=\"a deliberate commit beside the audit\" git -C . commit -qm x"}}')"
pkill -f "sleep 31" 2>/dev/null
sleep 0.3
check "a commit once the audit has ended: let through" 0 "$(run "$A" "$COMMIT")"
rm -rf "$A"

echo "-----"
printf 'test-gate-write-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
rm -rf "$R" "$OTHER" "$LOGROOT"
[ "$FAIL" = 0 ] || exit 1
