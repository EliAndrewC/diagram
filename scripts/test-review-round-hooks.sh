#!/usr/bin/env bash
# Tests for review-round-hooks.sh - a spec-fidelity round after the first reads the diff (feature 249).
# Run: scripts/test-review-round-hooks.sh   (exit 0 = all green)
# GUARD_EDIT_OK: feature 249 - a NEW guard's companion suite.
#
# Every case drives the REAL hook with a REAL payload against a fixture clone, because a grep proves a
# call site exists and not that it fires (`tests/tooling/test_guard_firing_log.py`'s rule).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/review-round-hooks.sh"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0

T=$(mktemp -d); trap 'rm -rf "$GUARD_LOG_ROOT" "$T"' EXIT
FIX="$T/clone"; mkdir -p "$FIX/specs/301-fixture" "$FIX/specs/302-history"
git -C "$FIX" init -q 2>/dev/null
cat > "$FIX/specs/301-fixture/spec.md" <<'EOF'
# Feature 301 - fixture

## Functional requirements

**FR-001 - the first requirement.** It stands.

## Review history

(none yet)
EOF
cp "$FIX/specs/301-fixture/spec.md" "$FIX/specs/302-history/spec.md"
cat >> "$FIX/specs/302-history/spec.md" <<'EOF'
- **Round 1 (2026-09-14), `spec-fidelity`: CHANGES REQUIRED**, one item, applied: FR-001 restated.
EOF
# the session transcript path the payload carries; its subagents dir holds two spec-fidelity transcripts
TP="$T/sess.jsonl"; SUB="$T/sess/subagents"; mkdir -p "$SUB"
transcript() { # transcript <file> <prompt> <final text>
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
f, prompt, final = sys.argv[1:4]
with open(f, "w") as fh:
    fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": prompt}}) + "\n")
    fh.write(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Read"}]}}) + "\n")
    fh.write(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": final}]}}) + "\n")
PY
}
transcript "$SUB/agent-1.jsonl" "MODE 2 review of specs/301-fixture" "## review\n\n1. FR-001 is vague and was ruled FAITHFUL nowhere.\n\n**CHANGES REQUIRED**"
touch -d '2026-01-01' "$SUB/agent-1.jsonl"

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

agent() { # agent <subagent_type> <prompt> [transcript_path] -> the hook's stdout; rc via rc(), stderr in $T/err
  # GUARD_EDIT_OK: feature 249 - the rc goes through a file because callers capture stdout in a subshell
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t-review-round","cwd":sys.argv[3],"transcript_path":sys.argv[4],"tool_name":"Agent","tool_input":{"subagent_type":sys.argv[1],"prompt":sys.argv[2],"description":"x"}}))' "$1" "$2" "$FIX" "${3:-$TP}" \
    | ( cd "$FIX" && "$HOOK" pretool 2>"$T/err" ); echo $? > "$T/rc"
}
rc() { cat "$T/rc"; }
logged() { grep -rlq "\"rule\": *\"$1\"" "$GUARD_LOG_ROOT" 2>/dev/null || grep -rlq "$1" "$GUARD_LOG_ROOT" 2>/dev/null; }
state() { "$HOOK" state "$FIX" "$1"; }
prompt_of() { python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]["prompt"])'; }

echo "1. what passes untouched"
out=$(printf '{"session_id":"t-review-round","tool_name":"Bash","tool_input":{"command":"make done"}}' | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )); rc=$?
[ "$rc" -eq 0 ] && [ -z "$out" ] && ok "a Bash call is ignored" || no "a Bash call was not ignored" "(rc=$rc out=${out:0:40})"
out=$(agent settlement-review "review Inashiro, see specs/301-fixture")
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && ok "another agent type is ignored" || no "settlement-review was touched"
out=$(agent spec-fidelity "MODE 4: PLAN REVIEW of specs/301-fixture - read the whole plan.md")
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && ok "a MODE 4 plan review passes untouched" || no "MODE 4 was touched" "(out=${out:0:60})"
logged other-mode && ok "...recorded permitted/other-mode" || no "other-mode not recorded"
[ "$(state 301-fixture)" = "round=0 snapshot=no" ] && ok "...and took no snapshot" || no "MODE 4 took a snapshot" "($(state 301-fixture))"
out=$(agent spec-fidelity "MODE 1: EXCEPTION CHECK on specs/301-fixture - am I carving out a case?")
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && [ "$(state 301-fixture)" = "round=0 snapshot=no" ] && ok "a MODE 1 exception check passes untouched, no snapshot" || no "MODE 1 was touched or snapshotted"
out=$(agent spec-fidelity "MODE 2 review of specs/999-nowhere")
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && ok "a feature the clone does not hold passes untouched" || no "a missing feature was touched"
logged no-feature && ok "...recorded permitted/no-feature" || no "no-feature not recorded"

echo "2. the first dispatch takes the snapshot silently"
out=$(agent spec-fidelity "MODE 2: SPECIFICATION REVIEW of specs/301-fixture against request.md")
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && ok "the first spec review is silent" || no "the first spec review emitted something" "(out=${out:0:60})"
[ "$(state 301-fixture)" = "round=1 snapshot=yes" ] && ok "...and left a snapshot at round 1" || no "no snapshot after the first dispatch" "($(state 301-fixture))"
logged first-round && ok "...recorded permitted/first-round" || no "first-round not recorded"
[ -d "$FIX/.git/review-round/301-fixture/snapshot" ] && ok "...under the clone's .git" || no "the state is not under .git"

echo "3. the second dispatch is REWRITTEN into MODE 3 with the verdict and the diff"
printf '\n**FR-002 - the second requirement.** Added after round 1.\n' >> "$FIX/specs/301-fixture/spec.md"
ORIG="MODE 3 round 2 of specs/301-fixture. Confirm the item; note the plan review question and any exception in plan.md; check every FR has an SC."
out=$(agent spec-fidelity "$ORIG")
[ "$(rc)" -eq 0 ] && ok "the dispatch is allowed" || no "the dispatch was refused" "(rc=$(rc))"
printf '%s' "$out" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null && ok "...with valid JSON on stdout" || no "stdout is not valid JSON" "(${out:0:80})"
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
case "$P" in "MODE 3 (VERIFY) - round 2 of feature 301-fixture"*) ok "...the prompt opens with the MODE 3 preamble naming round 2";; *) no "the preamble is missing or names the wrong round" "(${P:0:80})";; esac
printf '%s' "$P" | grep -q '^+\*\*FR-002' && ok "...carrying the diff of the change" || no "the diff does not show FR-002 added"
printf '%s' "$P" | grep -q 'FR-001 is vague' && ok "...and the previous verdict verbatim from the transcript" || no "the previous verdict is not in the preamble"
printf '%s' "$P" | grep -q 'VERBATIM from the reviewer' && ok "...marked as the reviewer's own words" || no "the verdict is not marked verbatim"
tail_ok=$(printf '%s' "$P" | ORIG="$ORIG" python3 -c 'import os,sys; p=sys.stdin.read(); m="=== The session'"'"'s prompt follows ===\n"; print("yes" if p.endswith(m+os.environ["ORIG"]) else "no")')
[ "$tail_ok" = yes ] && ok "...and ends with the session's prompt unchanged" || no "the session's prompt was altered or lost"
printf '%s' "$out" | grep -q '"additionalContext"' && ok "...with a context line saying so" || no "no additionalContext on the rewrite"
logged mode-3-preamble && ok "...recorded rewrote/mode-3-preamble" || no "mode-3-preamble not recorded"
[ "$(state 301-fixture)" = "round=2 snapshot=yes" ] && ok "...state advanced to round 2" || no "state did not advance" "($(state 301-fixture))"
printf '%s' "$P" | grep -q 'plan review' && ok "the MODE 3 prompt that mentions plan review, exception and plan.md was still rewritten (round 2's own shape)" || no "the mention-words case did not carry through"

echo "4. the snapshot advances: a third dispatch diffs against the second, not the first"
printf '\n**FR-003 - the third.**\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity "MODE 3 round 3 of specs/301-fixture")
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
printf '%s' "$P" | grep -q '^+\*\*FR-003' && ok "the third dispatch shows FR-003" || no "FR-003 missing from the diff"
printf '%s' "$P" | grep -q '^+\*\*FR-002' && no "FR-002 is still in the diff - the snapshot did not advance" || ok "...and not FR-002: the snapshot advanced"
[ "$(state 301-fixture)" = "round=3 snapshot=yes" ] && ok "...round 3" || no "round did not advance to 3" "($(state 301-fixture))"

echo "5. a recovered FAITHFUL starts a new pass at round 1"
transcript "$SUB/agent-2.jsonl" "MODE 3 round 3 of specs/301-fixture" "Items confirmed; CHANGES REQUIRED nowhere remains.\n\n## FAITHFUL\n\nAside: none."
printf '\n**FR-004 - an amendment after acceptance.**\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity "MODE 3 amendment review of specs/301-fixture")
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
case "$P" in "MODE 3 (VERIFY) - round 1 of feature 301-fixture"*) ok "the round restarts at 1 after a FAITHFUL" ;; *) no "the round did not restart" "(${P:0:70})";; esac
printf '%s' "$P" | grep -q 'NEW PASS' && ok "...and the preamble says it is a new pass" || no "no new-pass line"
printf '%s' "$P" | grep -q 'Aside: none' && ok "...with the FAITHFUL verdict verbatim (the last verdict word decides)" || no "the FAITHFUL transcript was not the one recovered"

echo "6. no transcript answers: the Review history is the fallback, marked as the session's summary"
agent spec-fidelity "MODE 2 review of specs/302-history" "$T/other.jsonl" >/dev/null   # first sight, with history
logged history-without-snapshot && ok "a spec with history and no snapshot is told (reminded/history-without-snapshot)" || no "history-without-snapshot not recorded"
out=$(agent spec-fidelity "MODE 2 review of specs/302-history" "$T/other.jsonl")
printf '%s' "$out" | grep -q 'no earlier' && no "the second dispatch still says no snapshot" || ok "...once only: the snapshot now exists"
printf '\nmore\n' >> "$FIX/specs/302-history/spec.md"
out=$(agent spec-fidelity "MODE 3 round 2 of specs/302-history" "$T/other.jsonl")
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
printf '%s' "$P" | grep -q "as the SESSION recorded it" && ok "the fallback is marked as the session's summary" || no "the fallback is not marked" "(${P:0:200})"
printf '%s' "$P" | grep -q 'FR-001 restated' && ok "...and carries the history entry" || no "the history entry is missing"

echo "7. the first dispatch on a spec WITH history carries the context line"
out=$(agent spec-fidelity "MODE 2 review of specs/302-history" "$T/third.jsonl")
rm -rf "$FIX/.git/review-round/302-history"
out=$(agent spec-fidelity "MODE 2 review of specs/302-history" "$T/third.jsonl")
printf '%s' "$out" | grep -q 'no earlier snapshot' && ok "...the line names the missing snapshot" || no "the context line is missing" "(${out:0:80})"
printf '%s' "$out" | grep -q '"updatedInput"' && no "the history-without-snapshot case rewrote the prompt" || ok "...and does not rewrite"

echo "8. the escape"
out=$(agent spec-fidelity 'MODE 3 of specs/301-fixture REVIEW_ROUND_OK="the spec was restructured, read it whole"')
[ "$(rc)" -eq 0 ] && [ -z "$out" ] && ok "REVIEW_ROUND_OK with a reason passes the dispatch untouched" || no "the escape did not pass untouched" "(rc=$(rc) out=${out:0:60})"
logged review-round-ok && ok "...recorded escaped/review-round-ok" || no "the escape was not recorded"
printf '\n**FR-005**\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity "MODE 3 of specs/301-fixture")
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
printf '%s' "$P" | grep -q '^+\*\*FR-004' && no "the escape did not refresh the snapshot" || ok "...and refreshed the snapshot (FR-004 no longer in the next diff)"
out=$(agent spec-fidelity 'MODE 3 of specs/301-fixture REVIEW_ROUND_OK')
[ "$(rc)" -ne 0 ] && ok "a bare REVIEW_ROUND_OK is refused" || no "a bare token was allowed"
grep -q 'no reason' "$T/err" && ok "...saying it needs a reason" || no "the refusal does not ask for a reason"
logged REVIEW_ROUND_OK-no-reason && ok "...recorded blocked/REVIEW_ROUND_OK-no-reason" || no "the no-reason refusal was not recorded"

# GUARD_EDIT_OK: feature 251 - two new cases for the routing the guard gained (a rewritten round goes to the
# medium-effort twin; a hand dispatch of the twin is a round of the same review); no existing case changes.
echo "9. a rewritten round is ROUTED to spec-fidelity-verify, and a hand dispatch of the twin is the same review"
type_of() { python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"].get("subagent_type",""))'; }
printf '\n**FR-006**\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity "MODE 3 of specs/301-fixture")
[ "$(printf '%s' "$out" | type_of 2>/dev/null)" = "spec-fidelity-verify" ] && ok "a rewritten spec-fidelity round carries the twin's subagent_type" || no "the rewrite did not route to the twin" "(${out:0:120})"
printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin)["hookSpecificOutput"]["updatedInput"]; sys.exit(0 if d.get("description")=="x" else 1)' && ok "...with every other field of the dispatch kept" || no "the rewrite dropped a field of the dispatch"
printf '%s' "$out" | grep -q 'ROUTED to' && ok "...and the context line says it was routed" || no "the context line does not mention the routing"
printf '\n**FR-007**\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity-verify "Round N of specs/301-fixture, dispatched by hand")
P=$(printf '%s' "$out" | prompt_of 2>/dev/null)
printf '%s' "$P" | grep -q '^+\*\*FR-007' && ok "a HAND dispatch of the twin gets the preamble and the diff" || no "the twin's own dispatch was not rewritten" "(${out:0:120})"
printf '%s' "$P" | grep -q '^+\*\*FR-006' && no "the twin's diff reaches back past the previous round" || ok "...diffed against the previous round's snapshot"
[ "$(printf '%s' "$out" | type_of 2>/dev/null)" = "spec-fidelity-verify" ] && ok "...and stays the twin" || no "the twin's type was changed"
grep -q 'FR-007' "$FIX/.git/review-round/301-fixture/snapshot/spec.md" && ok "...and the snapshot was refreshed, so the round after it has something to diff against" || no "the twin's dispatch did not refresh the snapshot"
out=$(agent settlement-review "look at specs/301-fixture")
[ -z "$out" ] && ok "any other agent still passes untouched" || no "an unrelated agent was rewritten"

# GUARD_EDIT_OK: feature 253 - new cases for the operation the guard gained (the old value is looked for before
# a later round is spent); no existing case changes.
echo "10. a value changed and its OLD value still stands beside its subject: the round is refused before it is spent"
# GUARD_EDIT_OK: feature 253 - the fixture spec ends in its Review history, which the search rightly skips, so
# the new lines open a section of their own.
printf '\n## More requirements\n\n| `gizmo` | sonnet | high |\n\n**FR-009** `gizmo` runs on Sonnet at high effort.\n' >> "$FIX/specs/301-fixture/spec.md"
out=$(agent spec-fidelity "MODE 3 of specs/301-fixture")
[ "$(rc)" -eq 0 ] && ok "lines only ADDED carry no old value: the round goes through (and the snapshot now holds them)" || no "an append was refused" "(rc=$(rc))"
python3 - "$FIX/specs/301-fixture/spec.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace("| `gizmo` | sonnet | high |", "| `gizmo` | opus | high |"))
PY
before=$(state 301-fixture)
out=$(agent spec-fidelity "MODE 3 of specs/301-fixture")
[ "$(rc)" -eq 2 ] && [ -z "$out" ] && ok "the table moved to opus and FR-009 still says Sonnet: the dispatch is REFUSED" || no "a stale value was dispatched to a reviewer" "(rc=$(rc))"
grep -q 'spec.md:[0-9]' "$T/err" && grep -q 'gizmo' "$T/err" && grep -qi 'sonnet' "$T/err" && ok "...naming the line, the subject and the old value" || no "the refusal does not name the candidate"
grep -q 'STALE_TERMS_OK' "$T/err" && grep -q 'make stale-terms' "$T/err" && ok "...and both ways on" || no "the refusal does not say what to do"
[ "$(state 301-fixture)" = "$before" ] && grep -q 'sonnet | high' "$FIX/.git/review-round/301-fixture/snapshot/spec.md" && ok "...with no round counted and the snapshot unmoved" || no "a refused dispatch moved the state"
logged stale-terms && ok "...recorded blocked/stale-terms" || no "stale-terms not recorded"
out=$(agent spec-fidelity 'MODE 3 of specs/301-fixture STALE_TERMS_OK')
[ "$(rc)" -eq 2 ] && ok "a bare STALE_TERMS_OK is refused" || no "a bare token was allowed"
out=$(agent spec-fidelity 'MODE 3 of specs/301-fixture STALE_TERMS_OK="FR-009 describes the proposal, not the landing"')
[ "$(rc)" -eq 0 ] && [ "$(printf '%s' "$out" | type_of 2>/dev/null)" = "spec-fidelity-verify" ] && ok "with a reason the round is rewritten and routed as ever" || no "the escape did not pass" "(rc=$(rc))"
logged mode-3-preamble-stale-ok && ok "...and the escape is recorded with its reason" || no "the escape was not recorded"
out=$(agent spec-fidelity "MODE 3 of specs/301-fixture")
[ "$(rc)" -eq 0 ] && ok "the next round, with nothing replaced since, is untouched by the search" || no "a clean round was refused" "(rc=$(rc))"

echo
echo "test-review-round-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
