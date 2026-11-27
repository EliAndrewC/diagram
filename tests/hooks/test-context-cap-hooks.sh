#!/usr/bin/env bash
# Tests for context-cap-hooks (feature 451 T12, FR-006, plan D8 and D9): a builder's tool call past CONTEXT_CAP_TOKENS (300,000) is
# refused naming its handoff file and the next step, but for that file's Write; a builder under the cap, the main session and a
# defined agent pass; CONTEXT_OK="<reason>" in a Bash command escapes, recorded. A SendMessage resuming a builder past the cap, or
# whose task has landed, is refused, the escape in its summary (D10, 451 T13); `make context-ok` lets a builder past the cap (D9).
# Run: tests/hooks/test-context-cap-hooks.sh   (exit 0 = all green)
#
# Every case drives the REAL guard (through the shim, `l7r-guard --only context-cap-hooks PreToolUse`) with the REAL payloads pinned in
# rust/guard/src/guards/context_cap_hooks/payloads.json (captured from Claude Code 2.1.325), their cwd and transcript path moved to a
# fixture clone and session; the handoff's Write runs through the WHOLE chain too, since it is the cap's one exit.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/seen.sh"  # seen VAR <grep args>: a run's text grepped from a here-string, never a pipe (451 T253)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
HOOK="$HERE/context-cap-hooks.sh"
PINNED="$REPO/rust/guard/src/guards/context_cap_hooks/payloads.json"
PASS=0; FAIL=0
T=$(mktemp -d); export GUARD_LOG_DIR="$T/guard-log"
unset L7R_EVENTS_DIR L7R_FEATURE_DIRECTORY SPECIFY_FEATURE
trap 'rm -rf "$T"' EXIT

ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }

AID=af3dc58915037d8d6
C="$T/clone"; S="$T/proj/sess.jsonl"; OWN="$T/proj/sess/subagents/agent-$AID.jsonl"
mkdir -p "$C/.git" "$C/.claude/agents" "$(dirname "$OWN")"
printf -- '---\n' > "$C/.claude/agents/review-x.md"
H="$C/.git/l7r-handoffs/$AID.md"

context() {  # context <tokens>: the builder's last model call
  printf '{"type":"assistant","message":{"id":"m","usage":{"input_tokens":2,"cache_read_input_tokens":%s,"cache_creation_input_tokens":0}}}\n' "$(($1 - 2))" > "$OWN"
}
payload() {  # payload <builder|main|defined> <tool> <tool_input json>
  jq -c --arg w "$1" --arg tool "$2" --argjson ti "$3" --arg cwd "$C" --arg tp "$S" \
    '.[$w] | .cwd = $cwd | .transcript_path = $tp | .tool_name = $tool | .tool_input = $ti' "$PINNED"
}
run() {  # run <who> <tool> <tool_input json>: OUT and RC
  OUT=$(payload "$1" "$2" "$3" | "$HOOK" pretool 2>&1); RC=$?
}
bash_in() { jq -nc --arg c "$1" '{command: $c}'; }

echo "1. a builder past the wrap-up band's ceiling is refused, every tool, naming its handoff and the next step"
context 350000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && seen OUT -q '350000 tokens, past the cap of 300000' && ok "a Bash call past the cap is refused" || no "the call passed" "(rc=$RC: $OUT)"
seen OUT -qF "$H" && seen OUT -q 'Stop, and reply with that path' && ok "...naming the handoff file and the next step" || no "the refusal names no handoff" "($OUT)"
[ -n "$(ls "$GUARD_LOG_DIR" 2>/dev/null)" ] && grep -lq 'past-cap' "$GUARD_LOG_DIR"/* && ok "...and the firing is logged" || no "no guard-log record"
run builder Edit "$(jq -nc --arg f "$C/x.rs" '{file_path: $f, old_string: "a", new_string: "b"}')"
[ "$RC" -eq 2 ] && ok "an Edit past the cap is refused" || no "the Edit passed" "(rc=$RC)"

echo "2. its handoff's Write passes, alone and through the whole chain; another file does not"
WRITE=$(jq -nc --arg f "$H" '{file_path: $f, content: "done: T12 red; left: the green"}')
run builder Write "$WRITE"
[ "$RC" -eq 0 ] && ok "the handoff's Write passes" || no "the handoff's Write refused" "(rc=$RC: $OUT)"
grep -lq '"handoff"' "$GUARD_LOG_DIR"/* && ok "...recorded" || no "the handoff's pass left no record"
OUT=$(payload builder Write "$WRITE" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "the handoff's Write passes every guard of the chain" || no "a guard of the chain refused the handoff" "(rc=$RC: $OUT)"
OUT=$(payload builder Write "$(jq -nc --arg f "$C/.git/l7r-handoffs/T12-$AID.md" '{file_path: $f, content: "done; left"}')" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "...and so does the task-named handoff a real builder is given (T<n>-<agent id>.md)" || no "a guard of the chain refused the task-named handoff" "(rc=$RC: $OUT)"
OUT=$(payload builder Write "$(jq -nc --arg f "$C/notes.md" '{file_path: $f, content: "x"}')" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
[ "$RC" -eq 2 ] && seen OUT -q 'past the cap' && ok "...while the chain refuses any other Write (the guard is registered)" || no "the chain let another Write through" "(rc=$RC: $OUT)"
run builder Write "$(jq -nc --arg f "$C/.git/l7r-handoffs/a0000000000000000.md" '{file_path: $f, content: "x"}')"
[ "$RC" -eq 2 ] && ok "another agent's handoff is refused" || no "another agent's handoff passed" "(rc=$RC)"

echo "3. a builder under the cap passes"
context 250000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 0 ] && ok "a builder at 250k passes" || no "a builder under the cap refused" "(rc=$RC: $OUT)"

echo "4. the main session, and a defined agent past the cap, pass"
context 900000
run main Bash "$(bash_in 'make quick')"
[ "$RC" -eq 0 ] && ok "the main session passes" || no "the main session refused" "(rc=$RC: $OUT)"
OUT=$(payload builder Bash "$(bash_in 'make quick')" | jq -c '.agent_type = "review-x"' | "$HOOK" pretool 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "a defined agent past the cap passes" || no "a defined agent refused" "(rc=$RC: $OUT)"

echo "5. the escape"
before=$(ls "$GUARD_LOG_DIR" | wc -l)
run builder Bash "$(bash_in 'CONTEXT_OK="the landing needs it" make land')"
[ "$RC" -eq 0 ] && ok "CONTEXT_OK with a reason passes" || no "the escape was refused" "(rc=$RC: $OUT)"
[ "$(ls "$GUARD_LOG_DIR" | wc -l)" -gt "$before" ] && grep -lq 'the landing needs it' "$GUARD_LOG_DIR"/* && ok "...and is recorded" || no "the escape left no record"
run builder Bash "$(bash_in 'make quick CONTEXT_OK')"
[ "$RC" -eq 2 ] && seen OUT -q 'CONTEXT_OK with no reason' && ok "a bare CONTEXT_OK is refused" || no "a bare escape passed" "(rc=$RC)"

echo "6. a SendMessage resuming a builder (D10): past the cap or landed refused, the escape in its summary"
META="$T/proj/sess/subagents/agent-$AID.meta.json"
meta() { jq -nc --arg k "$1" --arg d "$2" '{agentType: $k, isBuiltIn: false, description: $d, toolUseId: "toolu_d"}' > "$META"; }
send() { jq -nc --arg to "$AID" --arg s "$1" '{to: $to, summary: $s, message: "go on"}'; }
meta general-purpose "451 T05: build it"
context 310000
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 2 ] && seen OUT -q "resuming builder $AID: its context is 310000 tokens" && seen OUT -q "make context-ok AID=$AID" && ok "a resume past the cap is refused, naming the fresh dispatch and the permit" || no "the resume passed" "(rc=$RC: $OUT)"
grep -lq 'resume-past-cap' "$GUARD_LOG_DIR"/* && ok "...recorded" || no "no record of the refused resume"
run main SendMessage "$(send 'CONTEXT_OK="one pass to write its handoff" go on')"
[ "$RC" -eq 0 ] && grep -lq 'one pass to write its handoff' "$GUARD_LOG_DIR"/* && ok "CONTEXT_OK in the summary passes, recorded" || no "the summary's escape refused" "(rc=$RC: $OUT)"
mkdir -p "$C/specs/451-x" "$C/.specify"
printf '{"feature_directory": "specs/451-x"}' > "$C/.specify/feature.json"
printf -- '- [x] T05 a\n' > "$C/specs/451-x/tasks.md"
context 120000
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 2 ] && seen OUT -q 'T05 has landed or is ticked' && ok "a resume of a builder whose task is ticked is refused" || no "the landed resume passed" "(rc=$RC: $OUT)"
printf -- '- [ ] T05 a\n' > "$C/specs/451-x/tasks.md"
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 0 ] && ok "a resume under the cap, its task open, passes" || no "an open resume refused" "(rc=$RC: $OUT)"
meta general-purpose "a builder"; rm -f "$C/.specify/feature.json"
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 0 ] && grep -lq 'resume-no-task' "$GUARD_LOG_DIR"/* && ok "no task found passes, with its no-task record" || no "the task-less resume" "(rc=$RC: $OUT)"
rm -f "$META"
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 0 ] && grep -lq 'resume-no-meta' "$GUARD_LOG_DIR"/* && ok "a resume of an agent with no meta file passes, recorded" || no "the meta-less resume" "(rc=$RC: $OUT)"
meta review-x "451 T05: review"; context 900000
run main SendMessage "$(send 'go on')"
[ "$RC" -eq 0 ] && ok "a resume of a defined agent past the cap passes" || no "a defined agent's resume refused" "(rc=$RC: $OUT)"

echo "7. D9's permit, end to end: the resume escaped, make context-ok, the builder's next call through"
meta general-purpose "451 T05: build it"; context 310000
git init -q "$C"
# the Makefile runs the clone's own scripts/hooks/l7r-guard.sh: the fixture's hands on to this tree's
mkdir -p "$C/scripts/hooks"; printf '#!/usr/bin/env bash\nexec "%s/scripts/hooks/l7r-guard.sh" "$@"\n' "$REPO" > "$C/scripts/hooks/l7r-guard.sh"; chmod +x "$C/scripts/hooks/l7r-guard.sh"
run main SendMessage "$(send 'CONTEXT_OK="one pass to write its handoff" go on')"
[ "$RC" -eq 0 ] && ok "the resume escaped" || no "the escaped resume refused" "(rc=$RC: $OUT)"
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && ok "...its next call still refused before the permit" || no "the call passed with no permit" "(rc=$RC)"
OUT=$(make -s -f "$REPO/Makefile" -C "$C" context-ok AID= WHY="x y" 2>&1); RC=$?
[ "$RC" -ne 0 ] && seen OUT -q 'Usage: make context-ok AID=' && ok "make context-ok with no AID prints its usage" || no "a bare make context-ok" "(rc=$RC: $OUT)"
OUT=$(make -s -f "$REPO/Makefile" -C "$C" context-ok AID="$AID" WHY="the resumed builder finishes its step" 2>&1); RC=$?
[ "$RC" -eq 0 ] && grep -q "context-cap:$AID" "$C/.git/l7r-guard-permits.jsonl" && ok "make context-ok grants the agent's permit in the clone's store" || no "the grant failed" "(rc=$RC: $OUT)"
seen OUT -q "^context-ok: agent $AID may pass the context cap until .* - the resumed builder finishes its step" && ok "...saying so in its own words" || no "the grant's wording" "($OUT)"
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 0 ] && grep -lq 'context-ok-permit' "$GUARD_LOG_DIR"/* && ok "...and the builder's next call past the cap passes, recorded" || no "the permitted call refused" "(rc=$RC: $OUT)"

echo "8. the builder split (451 T237): a code builder - its brief carries a STOP POINT line - dispatches no claims agent"
brief() {  # brief <prompt text> <tokens>: the builder's own transcript, its brief first
  jq -nc --arg p "$1" '{type: "user", message: {role: "user", content: $p}}' > "$OWN"
  printf '{"type":"assistant","message":{"id":"m","usage":{"input_tokens":2,"cache_read_input_tokens":%s,"cache_creation_input_tokens":0}}}\n' "$(($2 - 2))" >> "$OWN"
}
agent_in() { jq -nc --arg t "$1" --arg p "${2:-Triage the claims bundle}" '{subagent_type: $t, prompt: $p, description: "x"}'; }
CODE=$'Build feature 451 task T05 in the clone.\n\nSTOP POINT. Your work ends when ALL of these hold:\n - make claims-triage has run'
brief "$CODE" 120000
run builder Agent "$(agent_in claims-triage)"
[ "$RC" -eq 2 ] && seen OUT -q 'STOP POINT' && seen OUT -q 'make claims-owed' && ok "a code builder's claims-triage dispatch is refused, naming the stop point and what to report" || no "the claims-triage dispatch passed" "(rc=$RC: $OUT)"
grep -lq 'builder-split' "$GUARD_LOG_DIR"/* && ok "...recorded" || no "no record of the split's refusal"
run builder Agent "$(agent_in impl-drift)"
[ "$RC" -eq 2 ] && ok "...and its impl-drift dispatch" || no "the impl-drift dispatch passed" "(rc=$RC: $OUT)"
run builder Agent "$(agent_in spec-fidelity 'MODE 4: PLAN REVIEW')"
[ "$RC" -eq 0 ] && ok "its spec-fidelity dispatch passes" || no "a plan review refused" "(rc=$RC: $OUT)"
run builder Workflow '{"name":"check-wave","args":{"agentType":"impl-drift","units":[{"label":"a","prompt":"p"}]}}'
[ "$RC" -eq 2 ] && ok "...and a check-wave of impl-drift is refused it too" || no "the wave passed" "(rc=$RC: $OUT)"
run builder Agent "$(agent_in impl-drift 'SPLIT_OK="the GM asked for it" Judge the bundle')"
[ "$RC" -eq 0 ] && grep -lq 'the GM asked for it' "$GUARD_LOG_DIR"/* && ok "SPLIT_OK with a reason in the prompt passes, recorded" || no "the split's escape" "(rc=$RC: $OUT)"
run builder Agent "$(agent_in impl-drift 'Judge the bundle SPLIT_OK')"
[ "$RC" -eq 2 ] && seen OUT -q 'SPLIT_OK with no reason' && ok "a bare SPLIT_OK is refused" || no "a bare SPLIT_OK" "(rc=$RC: $OUT)"
brief $'Run the claims round for feature 449 task T431 in the clone.\nSTOP POINT. quoted from the builder brief' 120000
run builder Agent "$(agent_in claims-triage)"
[ "$RC" -eq 0 ] && ok "a claims-round dispatch passes, a STOP POINT line quoted in it or not" || no "the claims round refused" "(rc=$RC: $OUT)"
brief 'Build feature 449 task T427 (a brief with no stop point)' 120000
run builder Agent "$(agent_in impl-drift)"
[ "$RC" -eq 0 ] && ok "a builder whose brief has no STOP POINT line passes" || no "an unmarked builder refused" "(rc=$RC: $OUT)"
run main Agent "$(agent_in impl-drift)"
[ "$RC" -eq 0 ] && ok "the main session's dispatch passes" || no "the main session refused" "(rc=$RC: $OUT)"
echo "9. the cap's handoff names the split for a code builder, and only for one"
rm -f "$C/.git/l7r-guard-permits.jsonl"  # case 7's permit would let the call through
brief "$CODE" 350000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && seen OUT -q 'does not run the claims round' && ok "a code builder past the cap is told it hands off at its stop point" || no "the handoff names no split" "(rc=$RC: $OUT)"
brief 'Run the claims round for feature 449 task T431' 350000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && ! seen OUT -q 'claims round' && ok "...and a claims-round dispatch past it is not" || no "the claims round's handoff" "(rc=$RC: $OUT)"

echo "10. the wrap-up band (451 T417): from the cap to 340000 the stop point's steps pass, recorded; all else refused, saying what is left"
HB="$C/.git/l7r-handoffs/T05-build.md"
BRIEFED="$CODE"$'\nEND at a handoff, '"$HB"$', by about 200k.'
for tokens in 300001 340000; do
  brief "$BRIEFED" "$tokens"
  for cmd in "cd $C && export SPECIFY_FEATURE=451-x && make decide F=451 T=T05" 'make plan-delta F=451' 'make claims-triage' \
      'make claims-owed' 'make task-add F=451 TITLE="found: a gap; see T05"' 'make task-withdraw F=451 T=T9 WHY="a duplicate"' \
      'make plan-verdict F=451 FILE=/tmp/v.json' 'make builder-checks CRATE="rust/guard" 2>&1 | tail -20' 'git -C /t status --short' 'git diff'; do
    run builder Bash "$(bash_in "$cmd")"
    [ "$RC" -eq 0 ] && ok "at $tokens: $cmd passes" || no "at $tokens: $cmd refused" "(rc=$RC: $OUT)"
  done
  for tool in Read Grep; do
    run builder "$tool" '{"file_path": "/t/x.rs", "pattern": "x"}'
    [ "$RC" -eq 0 ] && ok "at $tokens: a $tool passes" || no "at $tokens: a $tool refused" "(rc=$RC: $OUT)"
  done
  run builder Agent "$(agent_in spec-fidelity 'MODE 4: PLAN REVIEW of 2 changed block(s) of feature 451')"
  [ "$RC" -eq 0 ] && ok "at $tokens: the plan review's dispatch passes" || no "at $tokens: the plan review refused" "(rc=$RC: $OUT)"
  for cmd in 'make quick' 'make land F=451 T=T05' 'cargo build' 'make decide F=451 T=T05 && rm -rf x' 'echo "make decide"' 'git commit -m x'; do
    run builder Bash "$(bash_in "$cmd")"
    [ "$RC" -eq 2 ] && seen OUT -q "in its wrap-up band, up to 340000" && seen OUT -q 'Still allowed: make decide, plan-delta' && seen OUT -qF "$HB" \
      && ok "at $tokens: $cmd refused, naming the band, what is left and the handoff" || no "at $tokens: $cmd" "(rc=$RC: $OUT)"
  done
  for call in "Edit|$(jq -nc --arg f "$C/x.rs" '{file_path: $f, old_string: "a", new_string: "b"}')" \
      "Write|$(jq -nc --arg f "$C/x.rs" '{file_path: $f, content: "b"}')" \
      "Agent|$(agent_in general-purpose 'build T06')" "Agent|$(agent_in claims-triage)" "SendMessage|$(send 'go on')"; do
    run builder "${call%%|*}" "${call#*|}"
    [ "$RC" -eq 2 ] && seen OUT -q 'wrap-up band' && ok "at $tokens: a ${call%%|*} ($(cut -c1-40 <<<"${call#*|}")) refused" || no "at $tokens: ${call%%|*} passed" "(rc=$RC: $OUT)"
  done
done
grep -lq '"wrap-up"' "$GUARD_LOG_DIR"/* && grep -lq 'wrap-up-refused' "$GUARD_LOG_DIR"/* && ok "the band's passes and refusals are recorded" || no "the band left no record"
brief "$BRIEFED" 340001
run builder Bash "$(bash_in 'make decide F=451 T=T05')"
[ "$RC" -eq 2 ] && seen OUT -q 'Stop, and reply with that path' && ! seen OUT -q 'wrap-up band' && ok "past the ceiling (340001) make decide is refused as before" || no "past the ceiling" "(rc=$RC: $OUT)"

echo "11. the handoff the brief names (451 T352): its Write passes past the ceiling, through the whole chain"
brief "$BRIEFED" 350000
run builder Bash "$(bash_in 'make quick')"
[ "$RC" -eq 2 ] && seen OUT -qF "$HB" && ok "the refusal names the brief's handoff" || no "the refusal's handoff" "(rc=$RC: $OUT)"
for f in "$HB" "$C/.git/l7r-handoffs/done-pending-T05.md"; do
  [ "$f" = "$HB" ] || brief "$BRIEFED"$'\nIf your context passes 200k, stop with a handoff at '"$f." 350000
  OUT=$(payload builder Write "$(jq -nc --arg f "$f" '{file_path: $f, content: "built; left: the closing half"}')" | "$REPO/scripts/hooks/l7r-guard.sh" PreToolUse 2>&1); RC=$?
  [ "$RC" -eq 0 ] && ok "the Write of $(basename "$f") passes every guard of the chain" || no "the briefed handoff refused" "(rc=$RC: $OUT)"
done
run builder Write "$(jq -nc --arg f "$C/.git/l7r-handoffs/T05-other.md" '{file_path: $f, content: "x"}')"
[ "$RC" -eq 2 ] && ok "a handoff-directory file the brief does not name stays refused" || no "an unnamed file passed" "(rc=$RC)"

echo "12. a redirect in the band (451 T427) lands only under /tmp or in the handoff; a source file's is refused; a \`>& FILE\` and a \`cd\`'s redirect judged by place (451 T460)"
brief "$BRIEFED" 300001
# the fixture lives under /tmp, so a refused target is an absolute path outside it
for cmd in 'tail -n 0 x > /diagram/.clones/t427-x/rust/guard/src/a.rs' "grep '' a >> /diagram/.clones/t427-x/b.rs" \
    'tail -n 0 x >& /diagram/.clones/t427-x/rust/a.rs' 'cd /tmp > /diagram/.clones/t427-x/c.rs && make decide F=451 T=T05'; do
  run builder Bash "$(bash_in "$cmd")"
  [ "$RC" -eq 2 ] && seen OUT -q 'Refused: a redirect writing /diagram/.clones/t427-x/' && seen OUT -q 'only under /tmp or in the handoff' \
    && ok "$cmd refused, naming where it writes" || no "$cmd" "(rc=$RC: $OUT)"
done
for cmd in 'make decide F=451 T=T05 > /tmp/t427-decide.log 2>&1' 'make claims-triage >/dev/null 2>&1' 'make plan-delta F=451 2>&1 | tail -5' \
    'grep -c x a > /tmp/claude-1000/-diagram/s/scratchpad/t427-hits.txt' 'tail -n 0 x >& /tmp/t460-x.log' \
    'cd /tmp > /tmp/t460-cd.log && make decide F=451 T=T05' 'pushd /tmp >> /tmp/t460-pushd.log'; do
  run builder Bash "$(bash_in "$cmd")"
  [ "$RC" -eq 0 ] && ok "$cmd passes" || no "$cmd refused" "(rc=$RC: $OUT)"
done

echo
echo "context-cap-hooks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
