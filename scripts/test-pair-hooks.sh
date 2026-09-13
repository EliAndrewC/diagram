#!/usr/bin/env bash
# test-pair-hooks.sh - prove the gate/review pairing refuses each half alone, allows the pair, takes the
# override, and does NOT fire on a mention of the commands it guards.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 151, GM 2026-08-29)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/pair-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT

WATCH="$(cd "$(dirname "$0")" && pwd)/agent-stall-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
CLONE="$TMP/clone"; SKILL="$CLONE/.claude/skills/diagram"
mkdir -p "$SKILL/dev/bypass-log" "$CLONE/scripts" "$TMP/proj/sid-1/subagents"
(cd "$CLONE" && git init -q)
: > "$TMP/proj/sid-1.jsonl"
KEY=deadbeefcafe0000
printf 'engine-key:\n\t@printf "%%s" %s\n' "$KEY" > "$SKILL/Makefile"   # the fixture's own key: the test never runs the engine
cp "$WATCH" "$CLONE/scripts/agent-stall-hooks.sh"                        # the guard asks IT whether an agent is pending
DIR="$TMP/proj/sid-1/subagents"
# GUARD_EDIT_OK: feature 231 - THE TRIGGER IS SCRIPTED, so the fixture must say which world it is in. A
# review is owed only when a pool manifest moved against main (GM 2026-09-12), and the two scripts that
# decide it live beside the guard, so the fixture carries them and a moved manifest. `moved`/`unmoved`
# switch the world between cases; every case below section 1 runs in the world it names.
cp "$(dirname "$HOOK")/_review_owed.py" "$(dirname "$HOOK")/_review_snapshot.py" "$CLONE/scripts/"
MAPDIR_F="$SKILL/pool/hamlets/testmap"
# GUARD_EDIT_OK: feature 240 - a settlement-review dispatch now asks `_review_prereq.py` first, so the fixture
# carries it, spec-lint (whose figure pattern it imports), a stub gate stamp (green while `.git/stub-gate-green`
# exists) and a stub generation cache (current unless `<gen>.stale` exists), and a moved map is a WHOLE map.
# GUARD_EDIT_OK: feature 240 - spec-lint imports `_spec_figures` since feature 239 (the figure pattern's one home)
cp "$(dirname "$HOOK")/_review_prereq.py" "$(dirname "$HOOK")/spec-lint.py" "$(dirname "$HOOK")"/_spec_*.py "$(dirname "$HOOK")/_hookmatch.py" "$(dirname "$HOOK")"/_hm_*.py "$CLONE/scripts/"
printf 'import pathlib, subprocess, sys\nroot = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())\nsys.exit(0 if (root / ".git" / "stub-gate-green").exists() else 1)\n' > "$CLONE/scripts/gate-stamp.py"
mkdir -p "$SKILL/l7r/diagram/pipeline"
printf 'import os\n\ndef is_current(gen):\n    return not os.path.exists(gen + ".stale")\n' > "$SKILL/l7r/diagram/pipeline/gencache.py"
# GUARD_EDIT_OK: feature 240 - REGULAR packages, as the engine's are. Under `make hooks-test` the real skill is on
# PYTHONPATH, and a regular `l7r.diagram` anywhere on the path wins over a namespace portion, so a stub without
# `__init__.py` was shadowed by the real generation cache and 14 cases went red that passed when run by hand.
: > "$SKILL/l7r/diagram/__init__.py"; : > "$SKILL/l7r/diagram/pipeline/__init__.py"
moved()   { mkdir -p "$MAPDIR_F"; printf '{"meta":{"name":"testmap"}}' > "$MAPDIR_F/testmap.json"; printf '# testmap\n' > "$MAPDIR_F/testmap.notes.md"; for ext in gen.py svg png html; do : > "$MAPDIR_F/testmap.$ext"; done; }
unmoved() { rm -rf "$SKILL/pool"; }
moved

stdin_for() { printf '{"tool_name":"%s","tool_input":%s,"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$1" "$2" "$TMP/proj/sid-1.jsonl" "$CLONE"; }
run_pretool() { ( cd "$CLONE" && printf '%s' "$1" | "$HOOK" pretool 2>&1 ); }
rc_pretool() { ( cd "$CLONE" && printf '%s' "$1" | "$HOOK" pretool >/dev/null 2>&1 ); echo $?; }

GATE=$(stdin_for Bash '{"command":"make done"}')
REVIEW=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"review the map"}')

# --- 1. neither half runs alone: the gate is CORRECTED into the pair, the review is refused --------
# GUARD_EDIT_OK: feature 164 - the gate branch no longer spends a round trip telling the session to
# type `make verify`; it rewrites the command into it (GM 2026-08-30). The RULE is unchanged - the
# two still run together - but what used to not happen at all now happens correctly. 13 firings of
# the old refusal, 7 escaped with PAIR_OK in the very next call.
GATE_FULL=$(stdin_for Bash '{"command":"make done FULL=1"}')
check "the gate alone is REWRITTEN into the paired command" 'run_pretool "$GATE" | python3 -c "
import json,sys
try: sys.exit(0 if json.load(sys.stdin)[\"hookSpecificOutput\"][\"updatedInput\"][\"command\"] == \"make verify\" else 1)
except Exception: sys.exit(1)"'
check "...and the correction says to dispatch the review in the same turn" 'run_pretool "$GATE" | grep -q "SAME TURN"'
check "...and still names the override for a one-sided case" 'run_pretool "$GATE" | grep -q "PAIR_OK"'
# GUARD_EDIT_OK: feature 212 - a shape `verify` cannot take is RECORDED AND PERMITTED with the
# DISPATCH NOW context, not refused (GM 2026-09-07): the census found the rewrite above fired once
# while every real refusal - eight `make maps`, three detached `make done` - was such a shape.
permitted_with() { # label, payload, text the context must carry
  local out; out=$(run_pretool "$2"); local rc=$?
  if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "DISPATCH NOW" && printf '%s' "$out" | grep -q -- "$3" \
     && ! printf '%s' "$out" | grep -q "updatedInput"; then ok; else bad "$1 (rc=$rc: $out)"; fi
}
rm -f "$CLONE/.git/pairing-state.json"
permitted_with "make done FULL=1 is permitted, told the review is owed, and told it serializes" "$GATE_FULL" "FOREGROUND"
check "...and records the gate key for the pairing" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'
MAPS=$(stdin_for Bash '{"command":"make maps SCOPE=all 2>&1 | tail -60"}')
permitted_with "make maps ... | tail is permitted (foreground: the review follows the gate)" "$MAPS" "make verify"
DETACHED=$(stdin_for Bash '{"command":"setsid nohup make done > /tmp/done.log 2>&1 &"}')
permitted_with "a detached make done is permitted and told the review overlaps" "$DETACHED" "detached"
BGGATE=$(stdin_for Bash '{"command":"make maps","run_in_background":true}')
permitted_with "a run_in_background gate counts as detached" "$BGGATE" "detached"
check "...the permit names PAIR_OK for the one-sided case" 'run_pretool "$MAPS" | grep -q "PAIR_OK"'
rm -f "$CLONE/.git/pairing-state.json"
check "a settlement-review alone is refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'

# --- 2. a MENTION is not an invocation ------------------------------------------------------------
# THE SHAPE THAT BLOCKED THIS FEATURE'S OWN TIME AUDIT, four times in one day: a guard that greps the
# whole command string fires on a script that merely TALKS about the target - an analysis heredoc, a
# grep over the docs, this very test file. A guard nobody can work beside gets worked around.
MENTION=$(stdin_for Bash '{"command":"python3 - <<PY\nprint(\"count the make done runs in the log\")\nPY"}')
QUOTED=$(stdin_for Bash '{"command":"grep -n \"make done\" docs/iteration-loop.md"}')
OTHER=$(stdin_for Bash '{"command":"make quick"}')
check "a heredoc that TALKS about the gate passes" '[ "$(rc_pretool "$MENTION")" -eq 0 ]'
check "a quoted mention passes" '[ "$(rc_pretool "$QUOTED")" -eq 0 ]'
check "another target passes" '[ "$(rc_pretool "$OTHER")" -eq 0 ]'

# ...AND THE SAME RULE ON THE AGENT SIDE, which the guard's own author got wrong (2026-08-29). The
# branch greped the whole tool_input for "settlement-review", so a `spec-fidelity` dispatch that merely
# QUOTED the referent was blocked - a spec review, which owes no gate at all and cannot have one,
# because there is no map. The subagent TYPE is the invocation; the prompt is prose.
SPECREV=$(stdin_for Agent '{"subagent_type":"spec-fidelity","prompt":"the referent is the settlement-review pass of 2026-08-29; judge the spec"}')
READER=$(stdin_for Agent '{"subagent_type":"source-reader","prompt":"read what a settlement-review cited"}')
check "a spec-fidelity dispatch that MENTIONS a settlement-review passes" '[ "$(rc_pretool "$SPECREV")" -eq 0 ]'
check "a source-reader that mentions one passes" '[ "$(rc_pretool "$READER")" -eq 0 ]'
check "...while a real settlement-review is still refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'

# --- 3. the pair: a pending review lets the gate through ------------------------------------------
TU='{"type":"assistant","message":{"role":"assistant","stop_reason":"tool_use","content":[{"type":"tool_use","name":"Read","input":{}}]}}'
TR='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"..."}]}}'
# the launch record names the agent; the tool_result must stay LAST, because that is exactly what
# `agent-stall-hooks.sh pending` reads to mean "this agent is still awaiting its next turn"
printf '{"prompt":"settlement-review of the map"}\n%s\n%s\n' "$TU" "$TR" > "$DIR/agent-rev.jsonl"
check "with a review PENDING the gate runs" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...and the gate records its key" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'

# --- 4. with a gate recorded, the review dispatch is allowed --------------------------------------
rm -f "$DIR/agent-rev.jsonl"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
check "with a green record the review runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# --- 5. the override runs the command and leaves its reason ---------------------------------------
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json"
OVER=$(stdin_for Bash '{"command":"PAIR_OK=\"docs only, no map ink\" make done"}')
check "the override runs the gate alone" '[ "$(rc_pretool "$OVER")" -eq 0 ]'
check "...and logs its reason for the audit" 'grep -rql "docs only, no map ink" "$SKILL/dev/bypass-log"'

# --- 6. stop: a half-open pairing is refused ONCE --------------------------------------------------
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
rm -f "$CLONE/.git/pairing-state.json"
STOP=$(printf '{"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$CLONE")
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); FIRST=$?
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); SECOND=$?
check "stop refuses a half-open pairing" '[ "$FIRST" -eq 2 ]'
check "...and never twice for the same content" '[ "$SECOND" -eq 0 ]'

# --- 7. the documented remedy CLEARS the stop hook -------------------------------------------------
# The stop message says "record why it is not owed: PAIR_OK=... on your next gate run". Before
# 2026-08-29 doing exactly that logged a bypass and changed nothing stop reads, so the hook fired
# again and repeated the remedy the session had just used. An escape that cannot clear its own guard
# is the shape this project's guard rules single out.
rm -f "$CLONE/.git/pairing-state.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
WAIVE=$(stdin_for Bash '{"command":"PAIR_OK=\"the review read these exact maps and nothing moved\" make done"}')
check "the waived gate runs" '[ "$(rc_pretool "$WAIVE")" -eq 0 ]'
check "...and records the waiver against this content" 'grep -q "waived_key" "$CLONE/.git/pairing-state.json"'
STOP2=$(printf '{"transcript_path":"%s","session_id":"sid-2","cwd":"%s"}' "$TMP/proj/sid-2.jsonl" "$CLONE")
( cd "$CLONE" && printf '%s' "$STOP2" | "$HOOK" stop >/dev/null 2>&1 ); WAIVED=$?
check "...so stop does not fire on content the gate waived" '[ "$WAIVED" -eq 0 ]'
# and the waiver is per-CONTENT: a waiver recorded against OTHER content does not cover this one, so
# an engine edit after a waived gate is guarded again rather than riding the old waiver
printf '{"waived_key":"deadbeefdeadbeef"}' > "$CLONE/.git/pairing-state.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
( cd "$CLONE" && printf '%s' "$STOP2" | "$HOOK" stop >/dev/null 2>&1 ); OTHER=$?
check "...but a waiver for OTHER content does not cover this one" '[ "$OTHER" -eq 2 ]'


# --- 6. NO LAYOUT CHANGE, NO REVIEW (feature 231, GM 2026-09-12) -----------------------------------
# GUARD_EDIT_OK: feature 231 - the new branch and its three properties: the gate runs as typed, the stop
# branch stays quiet, and the waiver is RECORDED with its reason so `make audit` can count it. The
# motivating case is feature 228: one path's `d`, a byte-identical manifest, 18.7 minutes of review.
unmoved
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json"
check "with no manifest moved the gate runs as typed" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...and is NOT rewritten into make verify" '! run_pretool "$GATE" | grep -q "updatedInput"'
check "...and the context says no review is owed" 'run_pretool "$GATE" | grep -q "NO SETTLEMENT-REVIEW OWED"'
check "...and says why, in the words of the script" 'run_pretool "$GATE" | grep -q "no pool manifest moved"'
check "...and the context is valid JSON - a quoting slip here is silent" 'run_pretool "$GATE" | python3 -c "import json,sys; json.load(sys.stdin)"'
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); QUIET=$?
check "...and the stop branch does not fire half-open" '[ "$QUIET" -eq 0 ]'
check "...having recorded the automatic waiver" 'grep -q "waived_key" "$CLONE/.git/pairing-state.json"'
check "...with the reason it was waived for" 'grep -q "no pool manifest moved" "$CLONE/.git/pairing-state.json"'
moved
rm -f "$CLONE/.git/pairing-state.json"
check "...while a MOVED manifest owes the review again" 'run_pretool "$GATE" | grep -q "updatedInput"'
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); OWED=$?
check "...and the stop branch fires on it" '[ "$OWED" -eq 2 ]'

# --- 7. the guard reads THIS SESSION'S CLONE, not the shell's tree (feature 231) -------------------
# GUARD_EDIT_OK: feature 231 - the defect that cost feature 228 a refusal and a half-open stop: the
# session's shell stood in the MIRROR, so the guard keyed and recorded the mirror's tree. The resolver is
# feature 204's - the claim map, read from the payload's session_id - and the mirror's state stays clean.
MIRROR="$TMP/mirror"; mkdir -p "$MIRROR/.clones/.session-clones"; (cd "$MIRROR" && git init -q)
printf '%s' "$CLONE" > "$MIRROR/.clones/.session-clones/sid-1"
rm -f "$CLONE/.git/pairing-state.json" "$MIRROR/.git/pairing-state.json"
# `make done FULL=1`, because it is a shape the guard PERMITS and records - the plain gate is rewritten
# into `make verify` and records nothing, which is not what this case is about.
FROM_MIRROR=$(printf '{"tool_name":"Bash","tool_input":{"command":"make done FULL=1"},"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
CLONE_MAIN="$MIRROR" bash -c 'cd "$1" && printf "%s" "$2" | "$3" pretool >/dev/null 2>&1' _ "$MIRROR" "$FROM_MIRROR" "$HOOK"
check "standing in the mirror, the gate records the pairing state of the CLONE" '[ -f "$CLONE/.git/pairing-state.json" ]'
check "...and never that of the mirror" '[ ! -f "$MIRROR/.git/pairing-state.json" ]'

# --- 8. an ESCAPED review is still a review (feature 231) ------------------------------------------
# GUARD_EDIT_OK: feature 231 - the second half of feature 228's pairing incident: the escaped dispatch
# logged a bypass and recorded nothing, so the stop branch fired half-open on a review that had run.
rm -f "$CLONE/.git/pairing-state.json"
ESCREV=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"PAIR_OK: the gate is running beside this - review the map"}')
check "a review escaped with a reason runs" '[ "$(rc_pretool "$ESCREV")" -eq 0 ]'
# GUARD_EDIT_OK: feature 240 FR-002 - the dispatch records WHICH content it reviews, and the review counts
# at its VERDICT. What 231 fixed stays fixed: once that review writes its verdict, the stop branch is quiet.
check "...and records the content it reviews" 'grep -q "review_dispatch_key" "$CLONE/.git/pairing-state.json"'
check "...and no longer counts itself done at dispatch" '! grep -q "\"review_key\"" "$CLONE/.git/pairing-state.json"'
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
mkdir -p "$CLONE/.git/review-verdicts"
printf '{"map":"testmap","engine_key":"%s","verdict":"PASS","findings":[]}' "$KEY" > "$CLONE/.git/review-verdicts/testmap.json"
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); AFTER_ESC=$?
check "...so once its verdict is written the stop branch does not fire half-open on it" '[ "$AFTER_ESC" -eq 0 ]'
rm -rf "$CLONE/.git/review-verdicts"


# --- 8b. A REVIEW COUNTS AT ITS VERDICT, AND AN UNVERIFIED FIX BUYS NO ROUND (feature 240, GM 2026-09-13) --
# GUARD_EDIT_OK: feature 240 FR-002 to FR-006 - "procedures which rely on someone ... remembering to do something
# are flawed". The fixture carries the decision module, spec-lint (whose figure pattern it imports), a stub
# gate stamp and a stub generation cache, so each world below is decided by a file the case writes.
VERDICTS="$CLONE/.git/review-verdicts"
verdict() { mkdir -p "$VERDICTS"; printf '{"map":"testmap","engine_key":"%s","verdict":"%s","findings":%s}' "${3:-$KEY}" "$1" "$2" > "$VERDICTS/testmap.json"; }
reset_prereq() { rm -rf "$VERDICTS" "$CLONE/.git/review-dispositions" "$CLONE/specs" "$MAPDIR_F/testmap.gen.py.stale" "$CLONE/.git/stub-gate-green" "$CLONE/.git/pairing-state.json"; }
refused_for() { # label, payload, text the refusal must carry
  local out; out=$(run_pretool "$2"); local rc=$?
  if [ "$rc" -eq 2 ] && printf '%s' "$out" | grep -q -- "$3"; then ok; else bad "$1 (rc=$rc: $out)"; fi
}
moved; reset_prereq
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
check "a first review of a current, complete map runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# FR-003: the motivating failure - the pass-13 dispatch, its figures removed, still owes pass 12's finding
verdict NEEDS-WORK '[{"id":"F1","severity":"major","what":"canopy over the caption"}]'
touch "$CLONE/.git/stub-gate-green"
refused_for "a review after findings that nothing verifies is refused, naming the finding" "$REVIEW" "F1"
# GUARD_EDIT_OK: feature 240 - every acting branch records under its own rule (feature 168)
check "...and the refusal is recorded under its own rule" 'grep -rq "review-prerequisites-unmet" "$GUARD_LOG_ROOT"'
mkdir -p "$CLONE/specs/240-x"
printf '{"m:canopy-clear":{"value":0,"unit":"px","command":"make x","taken":"2026-09-13","verifies":"F1","subject":"testmap","quantity":"board to crown edge","source":"tree_crowns"}}' > "$CLONE/specs/240-x/measurements.json"
check "...and runs once a record verifies that finding" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
rm -rf "$CLONE/specs"
( cd "$CLONE" && python3 scripts/_review_prereq.py accept --clone "$CLONE" --map testmap --finding F1 --reason "left on purpose for the fixture" >/dev/null )
check "...or once the finding is ACCEPTED with a reason" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# FR-004: a review of fixes needs the gate green, not merely running
rm -f "$CLONE/.git/stub-gate-green"
refused_for "a review of fixes with the gate not green is refused" "$REVIEW" "FR-004"

# FR-005: the map on disk must be what the engine draws now, and whole
reset_prereq; touch "$MAPDIR_F/testmap.gen.py.stale"
refused_for "a review of a map whose generation key moved is refused" "$REVIEW" "FR-005"
rm -f "$MAPDIR_F/testmap.gen.py.stale" "$MAPDIR_F/testmap.png"
# GUARD_EDIT_OK: feature 240 FR-005 - the earlier gate cases took a whole snapshot, and a whole snapshot is a
# whole map for the reviewer; so the refusal is proven with the render gone from BOTH places, then permitted
# again from the snapshot alone.
mv "$CLONE/.git/review-snapshot" "$TMP/snapshot-aside" 2>/dev/null
refused_for "a review of a map missing an artifact in the pool and its snapshot is refused" "$REVIEW" "missing .png"
mkdir -p "$CLONE/.git/review-snapshot/testmap/clone"
for ext in json svg png html; do : > "$CLONE/.git/review-snapshot/testmap/clone/testmap.$ext"; done
check "...and permitted when its review snapshot is whole" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
: > "$MAPDIR_F/testmap.png"

# FR-006: a quoted figure needs a record
FIGREV=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"the caption now clears the canopy by 14 ft"}')
refused_for "a dispatch quoting a figure with no record is refused" "$FIGREV" "FR-006"
FIGOK=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"the caption now clears the canopy by 14 ft, observed 2026-09-13, method: the crown ring measured by hand"}')
check "...and runs with 239's dated one-shot label" '[ "$(rc_pretool "$FIGOK")" -eq 0 ]'

# the escape: logged, and needing a reason
BARE=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"REVIEW_PREREQ_OK=\"x\" the caption clears by 14 ft"}')
refused_for "REVIEW_PREREQ_OK with no real reason is refused" "$BARE" "needs a REASON"
ESC=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"REVIEW_PREREQ_OK=\"a negative fixture left bad on purpose\" the caption clears by 14 ft"}')
check "REVIEW_PREREQ_OK with a reason runs the review" '[ "$(rc_pretool "$ESC")" -eq 0 ]'
check "...and logs its reason for the audit" 'grep -rql "a negative fixture left bad on purpose" "$SKILL/dev/bypass-log"'
check "...and the escape is recorded under its own rule" 'grep -rq "review-prereq-ok" "$GUARD_LOG_ROOT"'

# FR-002: a NOT-REVIEWABLE verdict closes nothing; a PASS for this content closes the pair
reset_prereq
check "the review dispatch runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
# GUARD_EDIT_OK: feature 240 SC-001 - a review stopped before it returns writes no verdict, and closes nothing
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); NONE=$?
check "a dispatched review with NO verdict written leaves the pair open" '[ "$NONE" -eq 2 ]'
rm -f "$CLONE/.git/pairing-state.json"
printf '{"review_dispatch_key":"%s"}' "$KEY" > "$CLONE/.git/pairing-state.json"
verdict NOT-REVIEWABLE '[]'
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); NR=$?
check "a NOT-REVIEWABLE verdict leaves the pair OPEN" '[ "$NR" -eq 2 ]'
rm -f "$CLONE/.git/pairing-state.json"
verdict PASS '[]' feedfacefeedface
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); STALE=$?
check "a PASS for OTHER content leaves it open too" '[ "$STALE" -eq 2 ]'
rm -f "$CLONE/.git/pairing-state.json"
verdict PASS '[]'
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); CLOSED=$?
check "a PASS for this content closes it" '[ "$CLOSED" -eq 0 ]'
reset_prereq


# --- 9. A FALLBACK ONTO MAIN'S TREE IS DISCLOSED, NEVER SILENT (feature 231's amendment, GM 2026-09-12) --
# GUARD_EDIT_OK: feature 231's amendment - the residual the resolver leaves. An unnamed session, or a clone
# claimed but never created, resolves to nothing; the cwd's git root is still used (a guard that cannot
# resolve a clone must not refuse everything), and when that lands on MAIN's tree every branch that speaks
# says so in ONE shared string. A resolved clone adds nothing, and no silent branch starts speaking.
GHOST=$(printf '{"tool_name":"Bash","tool_input":{"command":"make done FULL=1"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
printf '%s' "$MIRROR/.clones/never-created" > "$MIRROR/.clones/.session-clones/ghost"
moved
note_says() { ( cd "$MIRROR" && printf '%s' "$1" | CLONE_MAIN="$MIRROR" "$HOOK" "${2:-pretool}" 2>&1 ); }
check "a claimed-but-uncreated clone falls back and the gate branch DISCLOSES it" 'note_says "$GHOST" | grep -q "could not be resolved"'
check "...and says the verdict was judged against main" 'note_says "$GHOST" | grep -q "judged against MAIN"'
check "...and names the remedy" 'note_says "$GHOST" | grep -q "rename"'
check "...and the context is still valid JSON" 'note_says "$GHOST" | python3 -c "import json,sys; json.load(sys.stdin)"'
GHOSTREV=$(printf '{"tool_name":"Agent","tool_input":{"subagent_type":"settlement-review","prompt":"review it"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
rm -f "$MIRROR/.git/pairing-state.json" "$MIRROR/.git/verification-state.json"
check "the review refusal discloses it too" 'note_says "$GHOSTREV" | grep -q "could not be resolved"'
printf '{"engine_key":"%s"}' "$KEY" > "$MIRROR/.git/verification-state.json"
mkdir -p "$MIRROR/.claude/skills/diagram/pool/hamlets/m"
printf '{"meta":{"name":"m"}}' > "$MIRROR/.claude/skills/diagram/pool/hamlets/m/m.json"   # a manifest, so a review IS owed there
printf 'engine-key:\n\t@printf "%%s" %s\n' "$KEY" > "$MIRROR/.claude/skills/diagram/Makefile"
GHOSTSTOP=$(printf '{"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
check "the half-open stop discloses it too" 'note_says "$GHOSTSTOP" stop | grep -q "could not be resolved"'
check "a RESOLVED clone adds nothing" '! run_pretool "$GATE_FULL" | grep -q "could not be resolved"'
QUIET_ONE=$(printf '{"tool_name":"Bash","tool_input":{"command":"make quick"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
check "...and a branch that says nothing today still says nothing" '[ -z "$(note_says "$QUIET_ONE")" ]'
check "the disclosure is ONE string, not five copies" '[ "$(grep -c "could not be resolved" "$(dirname "$HOOK")/pair-hooks.sh")" -eq 1 ]'

printf '\ntest-pair-hooks: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
