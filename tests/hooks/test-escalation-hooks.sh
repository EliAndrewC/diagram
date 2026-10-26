#!/usr/bin/env bash
# Tests for escalation-hooks.sh - a review's findings do not reach the GM unfiltered (2026-09-12).
# Run: tests/hooks/test-escalation-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL hook with a REAL payload, because a grep proves a call site exists and
# not that it fires - the rule `tests/tooling/test_guard_firing_log.py` was written to enforce.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../../scripts/hooks/escalation-hooks.sh"
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
PASS=0; FAIL=0

# a throwaway git work tree, so the hook's clone detection and its state file are real
FIX=$(mktemp -d)/test-clone; mkdir -p "$FIX"
git -C "$FIX" init -q 2>/dev/null
# GUARD_EDIT_OK: 2026-09-26 - stderr is captured in a file of THIS run's own, not a fixed /tmp path that every
# concurrent hooks-test (one per session's gate) rewrote under the others (it failed the batching suite's greps).
HOOK_ERR=$(mktemp)
trap 'rm -rf "$GUARD_LOG_ROOT" "$HOOK_ERR" "$(dirname "$FIX")"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

agent() { # agent <subagent_type> <prompt> -> run the pretool hook in the fixture, print its stdout
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t1","tool_name":"Agent","tool_input":{"subagent_type":sys.argv[1],"prompt":sys.argv[2]}}))' "$1" "$2" \
    | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )
}
bash_call() { # a non-Agent tool must be ignored entirely
  python3 -c 'import json; print(json.dumps({"session_id":"t1","tool_name":"Bash","tool_input":{"command":"make done"}}))' \
    | ( cd "$FIX" && "$HOOK" pretool 2>/dev/null )
}
stop_call() { # run the stop hook in the fixture, return its exit code, stderr to a file
  printf '{"session_id":"t1"}' | ( cd "$FIX" && "$HOOK" stop 2>"$HOOK_ERR" );
}
armed_by() { ( cd "$FIX" && "$HOOK" state ) | awk '/^armed by/{print $3}'; }

echo "1. a review dispatch ARMS the requirement, and says so for free"
out=$(agent settlement-review "DELTA review of Inashiro")
[ "$(armed_by)" = "settlement-review" ] && ok "settlement-review arms it" || no "settlement-review did not arm it"
printf '%s' "$out" | grep -q additionalContext && ok "...and the dispatch carries the context, costing no round trip" || no "no additionalContext on the dispatch"
printf '%s' "$out" | grep -q "escalation-check" && ok "...naming the filter to dispatch" || no "the context does not name the filter"

echo "2. the turn cannot close while findings are unfiltered"
stop_call; rc=$?
[ "$rc" -ne 0 ] && ok "stop refuses with a review armed" || no "stop allowed the turn to close" "(rc=$rc)"
grep -q "FINDINGS UNFILTERED" "$HOOK_ERR" && ok "...and says what is wrong" || no "the refusal does not say what is wrong"
grep -q "process narrative" "$HOOK_ERR" && ok "...and what the filter is for" || no "the refusal does not say what the filter cuts"
stop_call; rc=$?
[ "$rc" -eq 0 ] && ok "ONCE per armed review, never a loop" || no "stop refused twice for one review" "(rc=$rc)"

echo "3. the filter DISARMS it"
agent escalation-check "here is my draft writeup" >/dev/null
[ -z "$(armed_by)" ] && ok "an escalation-check dispatch disarms it" || no "still armed after the filter ran"
stop_call; rc=$?
[ "$rc" -eq 0 ] && ok "...and the turn may close" || no "stop still refuses after the filter" "(rc=$rc)"

echo "4. the escape works, and it is recorded"
agent settlement-review "review Sawada" >/dev/null
agent settlement-review 'review Sawada ESCALATION_OK="nothing from this pass is relayed, it is a confirmation run"' >/dev/null
[ -z "$(armed_by)" ] && ok "ESCALATION_OK in the dispatch disarms it" || no "the escape did not disarm it"
grep -rlq "escalation-ok" "$GUARD_LOG_ROOT" && ok "...and the escape is recorded with its rule" || no "the escape was not recorded"

echo "5. what must NOT arm it"
agent source-reader "read these three pages" >/dev/null
[ -z "$(armed_by)" ] && ok "an agent whose output the session does not relay (source-reader) does not arm it" || no "source-reader armed it"
agent quote-check "check these footnotes" >/dev/null
[ -z "$(armed_by)" ] && ok "quote-check does not arm it" || no "quote-check armed it"
bash_call >/dev/null
[ -z "$(armed_by)" ] && ok "a Bash call is ignored entirely" || no "a Bash call armed it"
agent building-review "review this manor plan" >/dev/null
[ "$(armed_by)" = "building-review" ] && ok "building-review arms it too" || no "building-review did not arm it"
agent escalation-check "draft" >/dev/null

echo "6. the guard records every acting branch, per RULE (feature 168)"
for rule in review-dispatched filter-ran escalation-ok findings-unfiltered; do
  grep -rlq "$rule" "$GUARD_LOG_ROOT" && ok "recorded: $rule" || no "never recorded: $rule"
done

echo "7. the seams refuse outside a fixture"
( cd "$FIX" && "$HOOK" arm /diagram/.clones/diagram-performance >/dev/null 2>&1 ) && no "arm took a real clone path" || ok "arm refuses a path that is not a fixture"
( cd "$FIX" && "$HOOK" disarm /diagram >/dev/null 2>&1 ) && no "disarm took the mirror" || ok "disarm refuses the mirror"

echo "7b. feature 375 FR-007: owed only for findings left open (GUARD_EDIT_OK: new cases for the disposal rule)"
mkdir -p "$FIX/dev"
LEDGER_HEAD='## Review checks, measured (feature 294 on)

| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-10 | glyph-check | an earlier row | PASS | - | nothing | - | - | 10 s | 1k in (1k cached) / 1.0k out |'
printf '%s\n' "$LEDGER_HEAD" > "$FIX/dev/review-ledger.md"
agent settlement-review "DELTA review of x" >/dev/null
printf '%s\n' '| 2026-10-11 | settlement-review | bath on ochiba | PASS | the steam arcs off center | judgment | no | fixed: arcs re-centered | 90 s | 300k in (250k cached) / 8.0k out |' >> "$FIX/dev/review-ledger.md"
rc=0; stop_call || rc=$?
[ "$rc" -eq 0 ] && [ -z "$(armed_by)" ] && ok "a review whose findings are all disposed owes nothing, and disarms" || no "a disposed review still owed the filter" "(rc=$rc)"
printf '%s\n' "$LEDGER_HEAD" > "$FIX/dev/review-ledger.md"
agent settlement-review "DELTA review of x" >/dev/null
printf '%s\n' '| 2026-10-11 | settlement-review | bath on ochiba | NEEDS-WORK | the door band | judgment | yes | held for the GM | 90 s | 300k in (250k cached) / 8.0k out |' >> "$FIX/dev/review-ledger.md"
rc=0; stop_call || rc=$?
[ "$rc" -eq 2 ] && [ "$(armed_by)" = "settlement-review" ] && ok "a finding left for the GM still owes the filter" || no "an open finding was let through" "(rc=$rc)"
( cd "$FIX" && "$HOOK" disarm "$FIX" >/dev/null 2>&1 ); rm -f "$FIX/dev/review-ledger.md"

echo "9. a QUESTION to the GM with no review behind it is filtered too (feature 429 FR-002)"
TR="$FIX/../transcript.jsonl"
gm_said() { printf '{"type":"user","message":{"content":"%s"}}\n' "$1" >> "$TR"; }
filtered() { printf '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Agent","input":{"subagent_type":"escalation-check","prompt":"draft"}}]}}\n' >> "$TR"; }
final_stop() { # final_stop <last assistant message>
  python3 -c 'import json,sys; print(json.dumps({"session_id":"t1","transcript_path":sys.argv[1],"last_assistant_message":sys.argv[2]}))' "$TR" "$1" \
    | ( cd "$FIX" && "$HOOK" stop 2>"$HOOK_ERR" )
}
Q417='Everything in my last message stands, including the questions waiting for you:
1. Should I switch off the settle'"'"'s 16 repair steps one at a time, as I did for the lane web?
2. For T27, should the track be drawn from where its households'"'"' ways meet it, or should the ways be laid to the track'"'"'s start?'
: > "$TR"; gm_said "work 417"
rc=0; final_stop "$Q417" || rc=$?
[ "$rc" -eq 2 ] && ok "the 2026-10-25 shape (two choices put to the GM, no filter) is refused" || no "the 10-25 shape passed" "(rc=$rc)"
grep -q "escalation-check" "$HOOK_ERR" && ok "...and the refusal names escalation-check" || no "the refusal does not name the filter"
rc=0; final_stop "$Q417" || rc=$?
[ "$rc" -eq 0 ] && ok "the same message is refused once, never a loop" || no "the same message was refused twice" "(rc=$rc)"
rc=0; final_stop 'Landed on main. To verify: `make maps-moved` prints "no pool manifest moved against HEAD".' || rc=$?
[ "$rc" -eq 0 ] && ok "a report that asks nothing passes" || no "a report was refused" "(rc=$rc)"
rc=0; final_stop '## Answers
- "should we follow the research?": yes - the record answers it, so I followed it.
> Do you want me to file it?' || rc=$?
[ "$rc" -eq 0 ] && ok "the GM's own question, quoted, and a block quote pass" || no "a quoted question was refused" "(rc=$rc)"
filtered
rc=0; final_stop "Shall I file it as feature 430?" || rc=$?
[ "$rc" -eq 0 ] && ok "an escalation-check since the GM's last message lets the question through" || no "a filtered question was refused" "(rc=$rc)"
gm_said "and one more thing"
rc=0; final_stop "Shall I file it as feature 431?" || rc=$?
[ "$rc" -eq 2 ] && ok "a filter BEFORE the GM's last message does not count" || no "an old filter let a new question through" "(rc=$rc)"
rm -f "$TR"

echo "10. an OFFER is not a question, but owes the significance test (feature 429 amendment 1)"
: > "$TR"; gm_said "carry on"
rc=0; final_stop 'I kept the 104 ft homestead ground. I can switch to the attested 75 ft if you would rather.' || rc=$?
[ "$rc" -eq 2 ] && ok "an offer-only message is refused once" || no "an unfiltered offer passed" "(rc=$rc)"
grep -q "OFFER UNFILTERED" "$HOOK_ERR" && grep -q "significant" "$HOOK_ERR" && ok "...with the significance instruction, not the question one" || no "the offer refusal text" "$(cat "$HOOK_ERR")"
rc=0; final_stop 'I kept the 104 ft ground; I can switch it if you would rather. Shall I file the lane fix as a new task?' || rc=$?
[ "$rc" -eq 2 ] && grep -q "QUESTION UNFILTERED" "$HOOK_ERR" && ok "a message with an ask and an offer is refused as a question" || no "ask+offer" "(rc=$rc)"
rm -f "$TR"

echo "11. a question KEPT for the GM is named in the turn's final message (feature 432 FR-002)"
mkdir -p "$FIX/specs/374-x"
: > "$TR"; printf '{"type":"user","timestamp":"2026-10-26T18:00:00.000Z","message":{"content":"clear the backlog"}}\n' >> "$TR"
filtered   # the filter ran this turn: only the naming is judged here
printf '%s\n' '{"kind": "question", "status": "kept", "question": "redraw the three sheets or record the deviation?", "kept": "2026-10-26T18:05:00Z", "source": "ask:b7"}' \
  '{"kind": "question", "status": "kept", "question": "an old kept question", "kept": "2026-10-25T10:00:00Z", "source": "ask:old"}' \
  '{"kind": "question", "status": "owed", "question": "not yet judged by escalation-check", "source": "hour:1"}' > "$FIX/specs/374-x/gm-review.jsonl"
rc=0; final_stop 'The backlog is cleared.' || rc=$?
[ "$rc" -eq 2 ] && grep -q "QUESTION KEPT, NOT NAMED" "$HOOK_ERR" && grep -q "374#0: redraw" "$HOOK_ERR" && ok "a question kept this turn and not named is refused" || no "an unnamed kept question passed" "(rc=$rc) $(cat "$HOOK_ERR")"
grep -q "374#1\|374#2" "$HOOK_ERR" && no "an older kept question or an owed one was named in the refusal" || ok "...naming only the one kept since the GM's last message"
rc=0; final_stop 'The backlog is cleared.' || rc=$?
[ "$rc" -eq 0 ] && ok "the same message is refused once, never a loop" || no "refused twice" "(rc=$rc)"
rc=0; final_stop 'The backlog is cleared. Yours to decide: 374#0, redraw the three sheets or record the deviation.' || rc=$?
[ "$rc" -eq 0 ] && ok "a final message naming it passes" || no "a named kept question was refused" "(rc=$rc) $(cat "$HOOK_ERR")"
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"Yours to decide: 374#0, the sheets."}]}}\n' >> "$TR"
rc=0; final_stop 'Still landing T04.' || rc=$?
[ "$rc" -eq 0 ] && ok "named once since the GM's last message is enough; a later message need not repeat it" || no "the check re-demanded a named question" "(rc=$rc) $(cat "$HOOK_ERR")"
: > "$TR"; printf '{"type":"user","timestamp":"2026-10-26T18:10:00.000Z","message":{"content":"carry on"}}\n' >> "$TR"
rc=0; final_stop '- **374#0:** Should I redraw the three sheets, or record the deviation?' || rc=$?
[ "$rc" -eq 0 ] && ok "a kept question, named and asked, is no unfiltered question (escalation-check kept it)" || no "the two Stop checks refused each other" "(rc=$rc) $(cat "$HOOK_ERR")"
rc=0; final_stop 'Should I also redraw the gate house?' || rc=$?
[ "$rc" -eq 2 ] && grep -q "QUESTION UNFILTERED" "$HOOK_ERR" && ok "...a new question beside it still owes the filter" || no "a new question passed" "(rc=$rc)"
rm -rf "$FIX/specs" "$TR"

echo "8. outside a work tree the hook does nothing"
OUT=$(mktemp -d)
rc=0; printf '{"session_id":"t1"}' | ( cd "$OUT" && "$HOOK" stop 2>/dev/null ) || rc=$?
[ "$rc" -eq 0 ] && ok "stop is silent outside a git tree" || no "stop fired outside a git tree" "(rc=$rc)"
rm -rf "$OUT"

echo
echo "escalation-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
