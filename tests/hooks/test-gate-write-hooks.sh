#!/usr/bin/env bash
# test-gate-write-hooks.sh - gate-write-hooks.sh refuses a write to the tree while this tree's `make done` runs, and nothing
# else (feature 385 T02, plan D13). GUARD_EDIT_OK: feature 385 - the new guard's test companion.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/gate-write-hooks.sh"
PASS=0; FAIL=0
LOGROOT=$(mktemp -d); export GUARD_LOG_DIR="$LOGROOT"
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
bad() { echo "  FAIL    $1"; FAIL=$((FAIL+1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected $2, got $3)"; fi; }

R=$(mktemp -d); OTHER=$(mktemp -d)
# THE FAKE GATE'S OWN SLEEP: a bare `pkill -f "sleep 30"` killed every such sleep on the machine - another copy of this suite's
# fake gate (a second session, a builder beside it) among them, three cases then read "let through" (449 T242's run, 2026-11-20);
# each run sleeps a length of its own, and kills only that
NAP="30.$$"

git -C "$R" init -q; git -C "$OTHER" init -q
printf 'done:\n\t@sleep %s\n' "$NAP" > "$R/Makefile"
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
for _ in $(seq 1 50); do ( cd "$R" && "$HERE/../../scripts/gates/l7r-gate.sh" own-make done ) && break; sleep 0.1; done
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
# 451 T33: a shell write into the tree, as a builder's `git apply` and `cp` under T34's landing were; a write outside it runs
check "a cp into the tree: refused (451 T33)" 2 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"cp /tmp/x a.txt"}}')"
check "a git apply in the tree: refused (451 T33)" 2 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"git apply /tmp/p.patch"}}')"
check "a tee to /tmp: let through (451 T33)" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"echo x | tee /tmp/t33-gate-write-suite"}}')"
check "the escape: let through" 0 "$(run "$R" '{"tool_name":"Bash","tool_input":{"command":"GATE_WRITE_OK=\"a deliberate fix for the gate itself\" git -C . commit -qm x"}}')"
check "another tree's command, its own gate not running: let through" 0 "$(run "$OTHER" "$COMMIT")"
check "an Edit outside this tree: let through" 0 "$(run "$R" "$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/b.txt"}}' "$OTHER")")"
# 451 T307: a commit in ANOTHER tree, sent from the gated one (the session standing in the clone, committing a builder's worktree:
# refused 2026-11-26 07:51), moves nothing this gate compares; the same commit aimed back at the gated tree is still held
check "a commit after a cd into another tree: let through (451 T307)" 0 "$(run "$R" "$(printf '{"tool_name":"Bash","tool_input":{"command":"cd %s && git add -u; git commit -qm x"}}' "$OTHER")")"
check "git -C another tree add: let through (451 T307)" 0 "$(run "$R" "$(printf '{"tool_name":"Bash","tool_input":{"command":"git -C %s add -A"}}' "$OTHER")")"
check "a commit aimed back at the gated tree from another: refused (451 T307)" 2 "$(run "$R" "$(printf '{"tool_name":"Bash","tool_input":{"command":"cd %s && git -C %s commit -qm x"}}' "$OTHER" "$R")")"
check "a Write under the tree's .git (a handoff): let through (451 T307)" 0 "$(run "$R" "$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s/.git/l7r-handoffs/T1-a.md","content":"x"}}' "$R")")"
# 451 T406: the same commit sent INTO the gated tree from a session standing in another is held; that tree's own commit is not
check "git -C the gated tree commit, from another tree: refused (451 T406)" 2 "$(run "$OTHER" "$(printf '{"tool_name":"Bash","tool_input":{"command":"git -C %s commit -qm x"}}' "$R")")"
check "make -C the gated tree tick, from another tree: refused (451 T406, T409)" 2 "$(run "$OTHER" "$(printf '{"tool_name":"Bash","tool_input":{"command":"make -C %s tick F=1 T=T1 NOTE=x"}}' "$R")")"
# 451 T430: an Edit or a shell write sent INTO the gated tree from another is held; that tree's own is not
check "an Edit of the gated tree, from another tree: refused (451 T430)" 2 "$(run "$OTHER" "$EDIT")"
check "a cp into the gated tree, from another tree: refused (451 T430)" 2 "$(run "$OTHER" "$(printf '{"tool_name":"Bash","tool_input":{"command":"cp /tmp/x %s/a.txt"}}' "$R")")"
check "a cp in another tree, from it: let through (451 T430)" 0 "$(run "$OTHER" '{"tool_name":"Bash","tool_input":{"command":"cp /tmp/x a.txt"}}')"
pkill -f "sleep $NAP" 2>/dev/null

echo "--- 3. a change the gate does not see (feature 405 T41, D15) ---"
# a tree with the gate's own tools: a claims-round record passes; code does not, nor a `.rs` comment (never unseen), nor a `.py`
# docstring since feature 449 T247 deleted `codeid.py`, which this section copied in (a `.py` file's id is its blob id now)
S=$(mktemp -d); git -C "$S" init -q
mkdir -p "$S/scripts/gates" "$S/l7r/diagram" "$S/rust/x" "$S/dev"
# (`preflight.py` and `usage_log.py` were copied here too, and are gone: the preflight is the gate's since 449 T071, the usage log's
# writer since 449 T129; the gate's wrapper below answers for both)
printf '#!/usr/bin/env bash\nexec "%s" "$@"\n' "$(cd "$HERE/../.." && pwd)/scripts/gates/l7r-gate.sh" > "$S/scripts/gates/l7r-gate.sh"; chmod +x "$S/scripts/gates/l7r-gate.sh"
printf 'def f(x):\n    """Research: a claim - NONE"""\n    return x\n' > "$S/l7r/diagram/m.py"
printf '// Research: a claim - NONE\nfn f(x: i32) -> i32 {\n    x + 1\n}\n' > "$S/rust/x/m.rs"
printf '{}\n' > "$S/dev/claims-index.json"
printf 'done:\n\t@sleep %s\n' "$NAP" > "$S/Makefile"
git -C "$S" add -A; git -C "$S" -c user.email=t@t -c user.name=t commit -qm base
"$S/scripts/gates/l7r-gate.sh" preflight --root "$S" --tree-snap "$S/.git/gate-tree.json"
( cd "$S" && setsid nohup make done </dev/null >/dev/null 2>&1 & )
for _ in $(seq 1 50); do ( cd "$S" && "$HERE/../../scripts/gates/l7r-gate.sh" own-make done ) && break; sleep 0.1; done
DOC=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/rust/x/m.rs","old_string":"a claim - NONE","new_string":"a claim reworded - NONE"}}' "$S")
PYDOC=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/l7r/diagram/m.py","old_string":"a claim - NONE","new_string":"a claim reworded - NONE"}}' "$S")
CODE=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/rust/x/m.rs","old_string":"x + 1","new_string":"x + 2"}}' "$S")
check "an Edit of a claim comment in a .rs file: refused" 2 "$(run "$S" "$DOC")"
check "an Edit of a .py docstring: refused, its id its bytes since 449 T247" 2 "$(run "$S" "$PYDOC")"
check "an Edit of a code token: refused" 2 "$(run "$S" "$CODE")"
check "a Write of a claims-round record: let through" 0 "$(run "$S" "$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s/dev/claims-index.json","content":"{\\"k\\": 1}\\n"}}' "$S")")"
printf '{"k": 1}\n' > "$S/dev/claims-index.json"
check "a commit of only those: let through" 0 "$(run "$S" "$COMMIT")"
# 451 T530: an append by heredoc, then on its next line a commit of it - the tree unmoved at the hook, so the real tree check called
# the commit unseen and the guard returned there (2026-11-27 about 17:40Z, a commit reached the clone while its gate ran)
HEREDOC_COMMIT='{"tool_name":"Bash","tool_input":{"command":"cat >> rust/x/m.rs <<'"'"'EOF'"'"'\n// a; b & c | it'"'"'s\nEOF\ngit add rust/x/m.rs && git commit -q -F - <<'"'"'EOF'"'"'\nmsg; x\nEOF\necho rc=$?"}}'
check "a heredoc append, then its commit on the next line: refused (451 T530)" 2 "$(run "$S" "$HEREDOC_COMMIT")"
check "...naming the append" yes "$(grep -q 'a shell write of rust/x/m.rs' "$R/err" && echo yes || echo no)"
git -C "$S" -c user.email=t@t -c user.name=t commit -qam claims
check "...and the gate's tree check reads the run as unmoved" 0 "$("$S/scripts/gates/l7r-gate.sh" preflight --root "$S" --tree-check "$S/.git/gate-tree.json" >/dev/null; echo $?)"
sed -i 's/x + 1/x + 2/' "$S/rust/x/m.rs"
check "a commit holding code: refused" 2 "$(run "$S" "$COMMIT")"
check "...and the tree check names it" 1 "$("$S/scripts/gates/l7r-gate.sh" preflight --root "$S" --tree-check "$S/.git/gate-tree.json" >/dev/null; echo $?)"
pkill -f "sleep $NAP" 2>/dev/null
rm -rf "$S"

# (section 4, a write while `make cache-audit` ran, left with that target - deleted by feature 449 T218 - and its guard, T223)

echo "-----"
printf 'test-gate-write-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
rm -rf "$R" "$OTHER" "$LOGROOT"
[ "$FAIL" = 0 ] || exit 1
