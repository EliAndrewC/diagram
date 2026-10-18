#!/usr/bin/env bash
# test-pair-hooks.sh - prove the gate/review pairing refuses each half alone, allows the pair, takes the
# override, and does NOT fire on a mention of the commands it guards.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 151, GM 2026-08-29)
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/../../scripts/hooks/pair-hooks.sh"
# GUARD_EDIT_OK: feature 164 - this guard RECORDS its firings now (feature 162's log), so the suite
# must write its fixtures to a throwaway directory. Without it the suite pollutes `make audit`, whose
# whole purpose is to price a guard from real firings: 24 fixture entries appeared there the first
# time these conversions ran their suites.
GUARD_LOG_ROOT=$(mktemp -d); export GUARD_LOG_DIR="$GUARD_LOG_ROOT"
trap 'rm -rf "$GUARD_LOG_ROOT"' EXIT

WATCH="$(cd "$(dirname "$0")" && pwd)/../../scripts/hooks/agent-stall-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
CLONE="$TMP/clone"; SKILL="$CLONE"
mkdir -p "$SKILL/dev/bypass-log" "$CLONE/scripts" "$TMP/proj/sid-1/subagents"
(cd "$CLONE" && git init -q)
: > "$TMP/proj/sid-1.jsonl"
KEY=deadbeefcafe0000
printf 'engine-key:\n\t@printf "%%s" %s\n' "$KEY" > "$SKILL/Makefile"   # the fixture's own key: the test never runs the engine
cp -r "$(dirname "$HOOK")/../../scripts/." "$CLONE/scripts/"   # the real scripts/ tree: the guard asks agent-stall-hooks.sh whether an agent is pending, and the review scripts decide what is owed (2026-10-08: one copy of the tree, where the flat layout copied file by file)
DIR="$TMP/proj/sid-1/subagents"
# GUARD_EDIT_OK: feature 231 - THE TRIGGER IS SCRIPTED, so the fixture must say which world it is in. A
# review is owed only when a pool manifest moved against main (GM 2026-09-12), and the two scripts that
# decide it live beside the guard, so the fixture carries them and a moved manifest. `moved`/`unmoved`
# switch the world between cases; every case below section 1 runs in the world it names.
MAPDIR_F="$SKILL/pool/hamlets/testmap"
# GUARD_EDIT_OK: feature 240 - a settlement-review dispatch now asks `review_prereq.py` first, so the fixture
# carries it, spec-lint (whose figure pattern it imports), a stub gate stamp (green while `.git/stub-gate-green`
# exists) and a stub generation cache (current unless `<gen>.stale` exists), and a moved map is a WHOLE map.
# GUARD_EDIT_OK: feature 240 - spec-lint imports `_spec_figures` since feature 239 (the figure pattern's one home)
printf 'import pathlib, subprocess, sys\nroot = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())\nsys.exit(0 if (root / ".git" / "stub-gate-green").exists() else 1)\n' > "$CLONE/scripts/gates/gate-stamp.py"
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

# GUARD_EDIT_OK: feature 375 amendment 7, FR-031 - helpers some cases share, defined once before the cases
# ...and the constants several cases read, set once here (each was set by the first case that used it)
VERDICTS="$CLONE/.git/review-verdicts"
GATE_FULL=$(stdin_for Bash '{"command":"make done FULL=1"}')
STOP=$(printf '{"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$CLONE")
MIRROR="$TMP/mirror"; mkdir -p "$MIRROR/.clones/.session-clones"; (cd "$MIRROR" && git init -q)
MAPDIR_G="$SKILL/pool/hamlets/othermap"
ONE=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"UNIT: settlement-review--testmap\nreview /x/.git/review-snapshot/settlement-review--testmap/clone against main - unlike othermap, which its own agent has"}')
permitted_with() { # label, payload, text the context must carry
  local out; out=$(run_pretool "$2"); local rc=$?
  if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "REVIEW CHECKS OWED" && printf '%s' "$out" | grep -q -- "$3" \
     && ! printf '%s' "$out" | grep -q "updatedInput"; then ok; else bad "$1 (rc=$rc: $out)"; fi
}
verdict() { mkdir -p "$VERDICTS"; printf '{"map":"testmap","engine_key":"%s","verdict":"%s","findings":%s}' "${3:-$KEY}" "$1" "$2" > "$VERDICTS/settlement-review--testmap.json"; }
reset_prereq() { rm -rf "$VERDICTS" "$CLONE/.git/review-dispositions" "$CLONE/specs" "$MAPDIR_F/testmap.gen.py.stale" "$CLONE/.git/stub-gate-green" "$CLONE/.git/pairing-state.json"; }
refused_for() { # label, payload, text the refusal must carry
  local out; out=$(run_pretool "$2"); local rc=$?
  if [ "$rc" -eq 2 ] && printf '%s' "$out" | grep -q -- "$3"; then ok; else bad "$1 (rc=$rc: $out)"; fi
}
green() { touch "$CLONE/.git/stub-gate-green"; }
moved_two() { moved; mkdir -p "$MAPDIR_G"; printf '{"meta":{"name":"othermap"}}' > "$MAPDIR_G/othermap.json"; printf '# othermap\n' > "$MAPDIR_G/othermap.notes.md"; for ext in gen.py svg png html; do : > "$MAPDIR_G/othermap.$ext"; done; }
snap_of() { mkdir -p "$CLONE/.git/review-snapshot/settlement-review--$1/clone"; cp "$SKILL/pool/hamlets/$1/$1".* "$CLONE/.git/review-snapshot/settlement-review--$1/clone/"; }
note_says() { ( cd "$MIRROR" && printf '%s' "$1" | CLONE_MAIN="$MIRROR" "$HOOK" "${2:-pretool}" 2>&1 ); }

case_01() {  # 9 s measured alone 2026-10-12
# --- 1. neither half runs alone: the gate is CORRECTED into the pair, the review is refused --------
# GUARD_EDIT_OK: feature 375 amendment 9 - the case starts from a fresh fixture: dealt after the 06-08 chain (which leaves a green
# gate stub behind) it found the gate green and "a settlement-review alone is refused" failed - an ordering the split's scan missed
reset_prereq
# GUARD_EDIT_OK: feature 383 FR-003, SC-004 (the GM 2026-10-12: "why are we comparing our stuff to main when we're not ready
# to land there?") - THE GATE RUNS AS TYPED, with a review owed (this fixture's moved map) or not: no rewrite into `make
# verify`, no permit naming owed units, and NO review lookup at all - the trace of the hook's run never reaches review_owed.py.
# A review comes due at the checkpoint (`make tick`'s hold) or at the landing (review-gate.sh).
check "the gate runs as typed with a review owed" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...is not rewritten into make verify" '! run_pretool "$GATE" | grep -q "updatedInput"'
check "...says nothing" '[ -z "$(run_pretool "$GATE")" ]'
check "...and records the gate key for the pairing" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'
check "...and asks no review lookup (SC-004)" '! ( cd "$CLONE" && printf "%s" "$GATE" | bash -x "$HOOK" pretool 2>&1 ) | grep -q "review_owed.py"'
for shape in "$GATE_FULL" "$(stdin_for Bash '{"command":"make maps SCOPE=all 2>&1 | tail -60"}')" "$(stdin_for Bash '{"command":"setsid nohup make done > /tmp/done.log 2>&1 &"}')" "$(stdin_for Bash '{"command":"make maps","run_in_background":true}')"; do
  check "every gate shape runs as typed: $(printf '%s' "$shape" | cut -c1-60)" '[ "$(rc_pretool "$shape")" -eq 0 ] && ! run_pretool "$shape" | grep -q "updatedInput"'
done
rm -f "$CLONE/.git/pairing-state.json"
check "a settlement-review alone is refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'
}

case_02() {  # 3 s measured alone 2026-10-12
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
# GUARD_EDIT_OK: feature 383 amendment 4 - its own precondition, no green gate: case_04 leaves one, and once the parts were dealt
# by measured weights case_04 ran before this in the same part and the check failed (found at 2 and 3 parts)
rm -f "$CLONE/.git/stub-gate-green" "$CLONE/.git/verification-state.json"
check "...while a real settlement-review is still refused" '[ "$(rc_pretool "$REVIEW")" -eq 2 ]'
}

case_03() {  # 1 s measured alone 2026-10-12
# --- 3. the pair: a pending review lets the gate through ------------------------------------------
TU='{"type":"assistant","message":{"role":"assistant","stop_reason":"tool_use","content":[{"type":"tool_use","name":"Read","input":{}}]}}'
TR='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"..."}]}}'
# the launch record names the agent; the tool_result must stay LAST, because that is exactly what
# `agent-stall-hooks.sh pending` reads to mean "this agent is still awaiting its next turn"
printf '{"prompt":"settlement-review of the map"}\n%s\n%s\n' "$TU" "$TR" > "$DIR/agent-rev.jsonl"
check "with a review PENDING the gate runs" '[ "$(rc_pretool "$GATE")" -eq 0 ]'
check "...and the gate records its key" 'grep -q "gate_key" "$CLONE/.git/pairing-state.json"'
}

case_04() {  # 1 s measured alone 2026-10-12
# --- 4. with a gate recorded, the review dispatch is allowed --------------------------------------
rm -f "$DIR/agent-rev.jsonl"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; touch "$CLONE/.git/stub-gate-green"
check "with a green record the review runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
}

case_05() {  # 1 s measured alone 2026-10-12
# --- 5. a gate's PAIR_OK escapes nothing since feature 383 (the gate runs as typed): no bypass is logged for it -------
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json" "$CLONE/.git/stub-gate-green"
OVER=$(stdin_for Bash '{"command":"PAIR_OK=\"docs only, no map ink\" make done"}')
check "the gate with PAIR_OK runs" '[ "$(rc_pretool "$OVER")" -eq 0 ]'
check "...and logs no bypass: there was nothing to escape" '! grep -rql "docs only, no map ink" "$SKILL/dev/bypass-log" 2>/dev/null'
}

case_06() {  # 3 s of its chain, measured as one 2026-10-12
# --- 6. stop: RETIRED (feature 383 FR-003) - a turn ends on a green gate with a review owed --------------------------
# GUARD_EDIT_OK: feature 383 SC-004 - the stop verb is a no-op kept for a session whose settings predate the landing: quiet on a
# green gate with the fixture's review owed and none dispatched, and it asks no review lookup
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; touch "$CLONE/.git/stub-gate-green"
rm -f "$CLONE/.git/pairing-state.json"
( cd "$CLONE" && printf '%s' "$STOP" | "$HOOK" stop >/dev/null 2>&1 ); FIRST=$?
check "stop is quiet on a green gate with a review owed" '[ "$FIRST" -eq 0 ]'
check "...and asks no review lookup (SC-004)" '! ( cd "$CLONE" && printf "%s" "$STOP" | bash -x "$HOOK" stop 2>&1 ) | grep -q "review_owed.py"'
}

case_07() {  # 2 s of its chain, measured as one 2026-10-12
# --- 7. a gate with PAIR_OK still runs (feature 383: the waiver is retired with the stop branch, its only reader) -----
rm -f "$CLONE/.git/pairing-state.json"
WAIVE=$(stdin_for Bash '{"command":"PAIR_OK=\"the review read these exact maps and nothing moved\" make done"}')
check "a gate carrying PAIR_OK runs as typed" '[ "$(rc_pretool "$WAIVE")" -eq 0 ] && ! run_pretool "$WAIVE" | grep -q "updatedInput"'
}


case_08() {  # 5 s of its chain, measured as one 2026-10-12
# --- 6. NO LAYOUT CHANGE, NO REVIEW - and since feature 383 none at a gate's start either way ---------------------------
unmoved
rm -f "$CLONE/.git/pairing-state.json" "$CLONE/.git/verification-state.json"
check "with no manifest moved the gate runs as typed, silently" '[ "$(rc_pretool "$GATE")" -eq 0 ] && [ -z "$(run_pretool "$GATE")" ]'
moved
rm -f "$CLONE/.git/pairing-state.json"
check "...and with a moved one, the same" '[ "$(rc_pretool "$GATE")" -eq 0 ] && [ -z "$(run_pretool "$GATE")" ]'
}

case_09() {  # 1 s measured alone 2026-10-12
# --- 7. the guard reads THIS SESSION'S CLONE, not the shell's tree (feature 231) -------------------
# GUARD_EDIT_OK: feature 231 - the defect that cost feature 228 a refusal and a half-open stop: the
# session's shell stood in the MIRROR, so the guard keyed and recorded the mirror's tree. The resolver is
# feature 204's - the claim map, read from the payload's session_id - and the mirror's state stays clean.
printf '%s' "$CLONE" > "$MIRROR/.clones/.session-clones/sid-1"
rm -f "$CLONE/.git/pairing-state.json" "$MIRROR/.git/pairing-state.json"
# `make done FULL=1`, because it is a shape the guard PERMITS and records - the plain gate is rewritten
# into `make verify` and records nothing, which is not what this case is about.
FROM_MIRROR=$(printf '{"tool_name":"Bash","tool_input":{"command":"make done FULL=1"},"transcript_path":"%s","session_id":"sid-1","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
CLONE_MAIN="$MIRROR" bash -c 'cd "$1" && printf "%s" "$2" | "$3" pretool >/dev/null 2>&1' _ "$MIRROR" "$FROM_MIRROR" "$HOOK"
check "standing in the mirror, the gate records the pairing state of the CLONE" '[ -f "$CLONE/.git/pairing-state.json" ]'
check "...and never that of the mirror" '[ ! -f "$MIRROR/.git/pairing-state.json" ]'
}

case_10() {  # 1 s measured alone 2026-10-12
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
}


case_11() {  # 16 s measured alone 2026-10-12
# --- 8b. A REVIEW COUNTS AT ITS VERDICT, AND AN UNVERIFIED FIX BUYS NO ROUND (feature 240, GM 2026-09-13) --
# GUARD_EDIT_OK: feature 240 FR-002 to FR-006 - "procedures which rely on someone ... remembering to do something
# are flawed". The fixture carries the decision module, spec-lint (whose figure pattern it imports), a stub
# gate stamp and a stub generation cache, so each world below is decided by a file the case writes.
moved; reset_prereq
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; green
check "a first review of a current, complete map runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# FR-003: the motivating failure - the pass-13 dispatch, its figures removed, still owes pass 12's finding
verdict NEEDS-WORK '[{"id":"F1","severity":"major","what":"canopy over the caption"}]'
touch "$CLONE/.git/stub-gate-green"
refused_for "a review after findings that nothing verifies is refused, naming the finding" "$REVIEW" "F1"
# GUARD_EDIT_OK: feature 240 - every acting branch records under its own rule (feature 168)
check "...and the refusal is recorded under its own rule" 'grep -rq "review-prerequisites-unmet" "$GUARD_LOG_ROOT"'
mkdir -p "$CLONE/specs/240-x"
printf '{"m:canopy-clear":{"value":0,"unit":"px","command":"make x","taken":"2026-09-13","verifies":"F1","subject":"settlement-review--testmap","quantity":"board to crown edge","source":"tree_crowns"}}' > "$CLONE/specs/240-x/measurements.json"
check "...and runs once a record verifies that finding" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
rm -rf "$CLONE/specs"
( cd "$CLONE" && python3 scripts/reviews/review_prereq.py accept --clone "$CLONE" --map settlement-review--testmap --finding F1 --reason "left on purpose for the fixture" >/dev/null )
check "...or once the finding is ACCEPTED with a reason" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'

# FR-004: a review of fixes needs the gate green, not merely running
rm -f "$CLONE/.git/stub-gate-green"
refused_for "a review of fixes with the gate not green is refused" "$REVIEW" "FR-004"

reset_prereq  # the close case_11 had before its split (feature 383 amendment 4)
}

case_11b() {  # split from case_11 at its own reset (feature 383 amendment 4, plan D28): it was the suite's long pole
moved; reset_prereq
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; green
# FR-005: the map on disk must be what the engine draws now, and whole
reset_prereq; green; touch "$MAPDIR_F/testmap.gen.py.stale"
refused_for "a review of a map whose generation key moved is refused" "$REVIEW" "FR-005"
rm -f "$MAPDIR_F/testmap.gen.py.stale" "$MAPDIR_F/testmap.png"
# GUARD_EDIT_OK: feature 240 FR-005 - the earlier gate cases took a whole snapshot, and a whole snapshot is a
# whole map for the reviewer; so the refusal is proven with the render gone from BOTH places, then permitted
# again from the snapshot alone.
# GUARD_EDIT_OK: feature 240 FR-005 amendment round 1 - the check reads where the reviewer will: a whole STALE
# snapshot beside a render-less pool refuses a dispatch that names no snapshot, and a named whole one permits.
mkdir -p "$CLONE/.git/review-snapshot/settlement-review--testmap/clone"
for ext in json svg png html; do : > "$CLONE/.git/review-snapshot/settlement-review--testmap/clone/testmap.$ext"; done
cp "$MAPDIR_F/testmap.json" "$MAPDIR_F/testmap.svg" "$CLONE/.git/review-snapshot/settlement-review--testmap/clone/"   # a snapshot OF the current map
refused_for "a render-less pool is refused though a whole snapshot sits on disk, when the dispatch names none" "$REVIEW" "pool folder lacks .png"
SNAPREV=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"UNIT: settlement-review--testmap\nreview testmap from .git/review-snapshot/settlement-review--testmap/clone/"}')
check "...and permitted when the dispatch names that whole snapshot" '[ "$(rc_pretool "$SNAPREV")" -eq 0 ]'
# GUARD_EDIT_OK: feature 240 amendment round 2 - a named snapshot of an OLDER map (taken before a fix) is refused
printf 'before the fix' > "$CLONE/.git/review-snapshot/settlement-review--testmap/clone/testmap.svg"
refused_for "...and refused when the snapshot it names is of an older map than the pool's" "$SNAPREV" "older map"
: > "$CLONE/.git/review-snapshot/settlement-review--testmap/clone/testmap.svg"
rm -f "$CLONE/.git/review-snapshot/settlement-review--testmap/clone/testmap.html"
refused_for "...and refused when the snapshot it names is not whole" "$SNAPREV" "make verify"
: > "$MAPDIR_F/testmap.png"

reset_prereq  # the close case_11 had before its split
}

case_11c() {  # split from case_11 (plan D28); FR-005 above left the map current and whole, as this prelude does
moved; reset_prereq
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; green
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

# FR-002: a dispatch is permitted on a green gate (whether a verdict closes the unit is asked at the push, by review-gate.sh,
# since feature 383 retired the stop branch that asked it at each turn's end)
reset_prereq; green
check "the review dispatch runs" '[ "$(rc_pretool "$REVIEW")" -eq 0 ]'
reset_prereq
}


case_12() {  # 4 s of its chain, measured as one 2026-10-12
# --- 10. ONE MAP PER REVIEW AGENT, refused before it starts (feature 248 FR-001, GM 2026-09-14) -----------
# GUARD_EDIT_OK: feature 248 - "could we refuse a map review before it happens if the review asks for a review of
# more than 1 map?" - yes: counted against every pool map (owed or not), no escape token. The fixture gains a second
# map; both are untracked, so both are owed.
moved_two; reset_prereq
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
mkdir -p "$CLONE/.git/review-snapshot/testmap" "$CLONE/.git/review-snapshot/othermap"
printf 'review testmap only\n' > "$CLONE/.git/review-snapshot/testmap/dispatch.md"
printf 'review othermap only\n' > "$CLONE/.git/review-snapshot/othermap/dispatch.md"
TWO=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"review the maps testmap and othermap, the delta only"}')
refused_for "a dispatch naming two maps is refused before the agent starts" "$TWO" "one unit per agent"
check "...and hands back each map's prompt file" 'run_pretool "$TWO" | grep -q "review-snapshot/testmap/dispatch.md" && run_pretool "$TWO" | grep -q "review-snapshot/othermap/dispatch.md"'
check "...recorded under its own rule" 'grep -rl "review-multi-map" "$GUARD_LOG_ROOT" >/dev/null'
TWO_SNAP=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"read /x/.git/review-snapshot/settlement-review--testmap/clone and /x/.git/review-snapshot/settlement-review--othermap/clone"}')
refused_for "...two snapshot directories count as two maps" "$TWO_SNAP" "one unit per agent"
TWO_ESC=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"review testmap and othermap PAIR_OK: the gate is beside this"}')
refused_for "...and there is no escape for the shape" "$TWO_ESC" "no escape"
unmoved; mkdir -p "$SKILL/pool/hamlets/legacya" "$SKILL/pool/hamlets/legacyb"; printf '{}' > "$SKILL/pool/hamlets/legacya/legacya.json"; printf '{}' > "$SKILL/pool/hamlets/legacyb/legacyb.json"
( cd "$CLONE" && git add -A >/dev/null 2>&1 && git -c user.email=t@t -c user.name=t commit -qm maps >/dev/null 2>&1 && git update-ref refs/remotes/origin/main HEAD )
TWO_UNOWED=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"spot-check legacya and legacyb"}')
refused_for "...and two maps NOBODY owes are refused the same way (a spot check serializes too)" "$TWO_UNOWED" "one unit per agent"
rm -rf "$SKILL/pool/hamlets/legacya" "$SKILL/pool/hamlets/legacyb"; ( cd "$CLONE" && git rm -rq --cached .claude >/dev/null 2>&1; git -c user.email=t@t -c user.name=t commit -qm unmaps >/dev/null 2>&1; git update-ref refs/remotes/origin/main HEAD )
moved_two; reset_prereq
# a NAMED snapshot must be whole and current (feature 240), so the fixture's snapshots carry the map's files
snap_of testmap; snap_of othermap
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"; green
check "a ONE-map dispatch that mentions the other map for context is permitted (the snapshot form wins)" '[ "$(rc_pretool "$ONE")" -eq 0 ]'
check "...and records the dispatch: the map, at this key" 'python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get(\"dispatched\",{}).get(\"settlement-review--testmap\",{}).get(\"key\")==sys.argv[2] else 1)" "$CLONE/.git/pairing-state.json" "$KEY"'
}

case_13() {  # 10 s of its chain, measured as one 2026-10-12
# --- 11. the span between two owed maps' dispatches is recorded (feature 248 FR-004) ----------------------------------
# testmap is dispatched (section 10), othermap after it: the span between the two dispatch clocks is recorded as parallel
# or serialized. (The stop branch's demand that every owed map be dispatched before the turn ends is retired, feature 383.)
OTHER=$(stdin_for Agent '{"subagent_type":"settlement-review","prompt":"UNIT: settlement-review--othermap\nreview /x/.git/review-snapshot/settlement-review--othermap/clone against main"}')
FIRST_AT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["dispatched"]["settlement-review--testmap"]["at"])' "$CLONE/.git/pairing-state.json")
check "the second map's dispatch, a fixture-clock half-minute later, is permitted" '[ "$(cd "$CLONE" && printf "%s" "$OTHER" | PAIR_NOW=$((FIRST_AT + 30)) "$HOOK" pretool >/dev/null 2>&1; echo $?)" -eq 0 ]'
check "...and every owed map now dispatched within the span records reviews-parallel" 'grep -rl "reviews-parallel" "$GUARD_LOG_ROOT" >/dev/null'
# the serialized shape: the same two maps dispatched two minutes apart
rm -f "$CLONE/.git/pairing-state.json"; ( cd "$CLONE" && printf '%s' "$ONE" | PAIR_NOW=1000 "$HOOK" pretool >/dev/null 2>&1; printf '%s' "$OTHER" | PAIR_NOW=1120 "$HOOK" pretool >/dev/null 2>&1 )
check "two dispatches a fixture-clock two minutes apart record reviews-serialized" 'grep -rl "reviews-serialized" "$GUARD_LOG_ROOT" >/dev/null'
rm -f "$CLONE/.git/pairing-state.json"; rm -rf "$MAPDIR_G"; moved; reset_prereq
}

case_14() {  # 9 s measured alone 2026-10-12
# --- 12. EVERY CHECK, A GREEN GATE, TWO ROUNDS (feature 294) ------------------------------------------------
# GUARD_EDIT_OK: feature 294 - the five checks are one family (GM 2026-10-01: the glyph check is "a category of thing");
# a review waits for a GREEN gate, never a running one (US6); and a unit gets two rounds per feature (FR-009).
moved; reset_prereq; rm -f "$CLONE/.git/review-rounds.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
GLYPH=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: settlement-review--testmap\njudge it"}')
check "a glyph-check with no green gate is refused like any review" '[ "$(rc_pretool "$GLYPH")" -eq 2 ]'
printf '{"gate_key":"%s"}' "$KEY" > "$CLONE/.git/pairing-state.json"
refused_for "...and so is one beside a gate that is RUNNING but not yet green" "$GLYPH" "no green gate"
green
check "...and runs on a green gate" '[ "$(rc_pretool "$GLYPH")" -eq 0 ]'
check "...counting its round for the active feature" 'grep -q "settlement-review--testmap" "$CLONE/.git/review-rounds.json"'
printf '{"none":{"settlement-review--testmap":["k1","k2"]}}' > "$CLONE/.git/review-rounds.json"
refused_for "a THIRD round of the same unit is refused" "$GLYPH" "the cap is two"
check "...recorded under its own rule" 'grep -rl "review-round-cap" "$GUARD_LOG_ROOT" >/dev/null'
# GUARD_EDIT_OK: feature 375 FR-011 - past the cap the round arbiter rules: the refusal names it, and its `continue` runs the round
refused_for "...and the refusal hands it to the round arbiter" "$GLYPH" "make arbiter-bundle"
rm -f "$CLONE/.git/review-rounds.json" "$CLONE/.git/pairing-state.json"; reset_prereq  # the close case_14 had before its split
}

case_14b() {  # split from case_14 (feature 383 amendment 4, plan D28): with case_11 the suite's long pole
moved; reset_prereq; rm -f "$CLONE/.git/review-rounds.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
GLYPH=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: settlement-review--testmap\njudge it"}')
printf '{"gate_key":"%s"}' "$KEY" > "$CLONE/.git/pairing-state.json"
green
mkdir -p "$CLONE/.specify" "$CLONE/specs/900-x"; printf '{"feature_directory": "specs/900-x"}' > "$CLONE/.specify/feature.json"
printf '{"specs/900-x":{"settlement-review--testmap":["k1","k2"]}}' > "$CLONE/.git/review-rounds.json"
printf '{"trigger": "round:glyph-check|settlement-review--testmap@3", "ruling": "continue", "why": "a new finding"}\n' > "$CLONE/specs/900-x/arbiter.jsonl"
check "a continue ruling runs the third round" '[ "$(rc_pretool "$GLYPH")" -eq 0 ]'
printf '{"trigger": "round:glyph-check|settlement-review--testmap@3", "ruling": "accept", "why": "fine as it stands"}\n' > "$CLONE/specs/900-x/arbiter.jsonl"
refused_for "...an accept closes the unit" "$GLYPH" "the round arbiter closed"
# GUARD_EDIT_OK: feature 374 batch 4, the round arbiter's tooling fix - a landed batch's rounds are spent: two rounds kept before
# the feature's tasks.md landed on origin/main leave the next batch's review its first round
printf '# Tasks\n' > "$CLONE/specs/900-x/tasks.md"
( cd "$CLONE" && git add specs/900-x/tasks.md >/dev/null 2>&1 && git -c user.email=t@t -c user.name=t commit -qm landed >/dev/null 2>&1 && git update-ref refs/remotes/origin/main HEAD )
printf '{"specs/900-x":{"settlement-review--testmap":["k1@1000","k2@1000"]}}' > "$CLONE/.git/review-rounds.json"
check "a batch landed since its two rounds runs the next batch's review" '[ "$(rc_pretool "$GLYPH")" -eq 0 ]'
check "...kept with its time" 'grep -q "@" "$CLONE/.git/review-rounds.json"'
# GUARD_EDIT_OK: feature 374 batch 5, the round arbiter's tooling fix - bare keys kept before the epoch fix are a landed batch's too
printf '{"specs/900-x":{"settlement-review--testmap":["k1","k2"]}}' > "$CLONE/.git/review-rounds.json"
check "two bare-key rounds before the batch landed leave the next batch its first round" '[ "$(rc_pretool "$GLYPH")" -eq 0 ]'
( cd "$CLONE" && git rm -rq --cached specs/900-x/tasks.md >/dev/null 2>&1; git -c user.email=t@t -c user.name=t commit -qm unland >/dev/null 2>&1; git update-ref refs/remotes/origin/main HEAD )
rm -rf "$CLONE/.specify" "$CLONE/specs/900-x" "$CLONE/.git/arbiter-owed.json"
rm -f "$CLONE/.git/review-rounds.json" "$CLONE/.git/pairing-state.json"; reset_prereq  # the close case_14 had before its split
}

case_14c() {  # split from case_14 (plan D28)
moved; reset_prereq; rm -f "$CLONE/.git/review-rounds.json"
printf '{"engine_key":"%s"}' "$KEY" > "$CLONE/.git/verification-state.json"
GLYPH=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: settlement-review--testmap\njudge it"}')
printf '{"gate_key":"%s"}' "$KEY" > "$CLONE/.git/pairing-state.json"
green
printf '{"none":{"settlement-review--testmap":["k1","k2"]}}' > "$CLONE/.git/review-rounds.json"
# GUARD_EDIT_OK: feature 379 FR-010 (the GM 2026-10-10) - the GM's-words waiver is retired: past the cap only the arbiter rules
GLYPH_WAIVED=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: settlement-review--testmap\nREVIEW_ROUNDS_OK=\"the GM said: one more round is fine\""}')
refused_for "...and the retired GM's-words waiver no longer runs it: the arbiter does" "$GLYPH_WAIVED" "make arbiter-bundle"
printf '{"none":{"settlement-review--testmap":["k1","%s"]}}' "$KEY" > "$CLONE/.git/review-rounds.json"
check "a re-dispatch at a key already counted is the same round" '[ "$(rc_pretool "$GLYPH")" -eq 0 ]'
rm -f "$CLONE/.git/review-rounds.json" "$CLONE/.git/pairing-state.json"; reset_prereq
}

case_15() {  # 5 s measured alone 2026-10-12
# --- 9. A FALLBACK ONTO MAIN'S TREE IS DISCLOSED, NEVER SILENT (feature 231's amendment, GM 2026-09-12) --
# GUARD_EDIT_OK: feature 231's amendment - the residual the resolver leaves. An unnamed session, or a clone
# claimed but never created, resolves to nothing; the cwd's git root is still used (a guard that cannot
# resolve a clone must not refuse everything), and when that lands on MAIN's tree every branch that speaks
# says so in ONE shared string. A resolved clone adds nothing, and no silent branch starts speaking.
GHOST=$(printf '{"tool_name":"Bash","tool_input":{"command":"make done FULL=1"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
printf '%s' "$MIRROR/.clones/never-created" > "$MIRROR/.clones/.session-clones/ghost"
moved
# GUARD_EDIT_OK: feature 383 FR-003 - the gate branch says nothing at all now (it runs as typed), and the stop branch is
# retired, so the review refusal is the one branch left that speaks on a fallback
check "a claimed-but-uncreated clone's gate runs as typed, saying nothing" '[ -z "$(note_says "$GHOST")" ]'
GHOSTREV=$(printf '{"tool_name":"Agent","tool_input":{"subagent_type":"settlement-review","prompt":"review it"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
rm -f "$MIRROR/.git/pairing-state.json" "$MIRROR/.git/verification-state.json"
check "the review refusal discloses the fallback" 'note_says "$GHOSTREV" | grep -q "could not be resolved"'
check "...says the verdict was judged against main" 'note_says "$GHOSTREV" | grep -q "judged against MAIN"'
check "...and names the remedy" 'note_says "$GHOSTREV" | grep -q "rename"'
check "a RESOLVED clone adds nothing" '! run_pretool "$GATE_FULL" | grep -q "could not be resolved"'
QUIET_ONE=$(printf '{"tool_name":"Bash","tool_input":{"command":"make quick"},"transcript_path":"%s","session_id":"ghost","cwd":"%s"}' "$TMP/proj/sid-1.jsonl" "$MIRROR")
check "...and a branch that says nothing today still says nothing" '[ -z "$(note_says "$QUIET_ONE")" ]'
check "the disclosure is ONE string, not five copies" '[ "$(grep -c "could not be resolved" "$(dirname "$HOOK")/../../scripts/hooks/pair-hooks.sh")" -eq 1 ]'
}


case_16() {  # 10 s (new)
# --- 10. A GLYPH CHECK IS DISPATCHED ON THE FEATURE'S HOUR (feature 375 amendment 9, the GM 2026-10-12) --
# GUARD_EDIT_OK: feature 375 amendment 9, FR-040 - an owed glyph unit waits for the feature's hour; before it the dispatch is
# refused, naming when it comes due; GLYPH_DUE_OK passes it with a reason; on the hour, or once a push was refused for it, it passes.
reset_prereq
local gm="$SKILL/pool/hamlets/glyphmap" early esc out
mkdir -p "$gm"
printf '{"meta":{"name":"glyphmap"},"ink_classes":{"farmhouse":2}}' > "$gm/glyphmap.json"; printf '# glyphmap\n' > "$gm/glyphmap.notes.md"
( cd "$CLONE" && git add -A pool/hamlets/glyphmap >/dev/null 2>&1 && git -c user.email=t@t -c user.name=t commit -qm glyphmap >/dev/null 2>&1 && git update-ref refs/remotes/origin/main HEAD )
printf '{"meta":{"name":"glyphmap"},"ink_classes":{"farmhouse":2,"kiln":1}}' > "$gm/glyphmap.json"
mkdir -p "$CLONE/specs/999-g" "$CLONE/.specify" "$CLONE/.git/l7r-events"
printf '# 999\n\n**Status**: In progress\n' > "$CLONE/specs/999-g/spec.md"
printf '# Tasks\n\n## Occasions\n\n- none: fixture\n\n## Work\n\n- [ ] T01 x\n' > "$CLONE/specs/999-g/tasks.md"
printf '{"feature_directory": "specs/999-g"}' > "$CLONE/.specify/feature.json"
started() { python3 -c 'import datetime, json, sys, time; print(json.dumps({"t": datetime.datetime.fromtimestamp(time.time() - int(sys.argv[1]), datetime.UTC).isoformat().replace("+00:00", "Z"), "ev": ""}))' "$1" > "$CLONE/.git/l7r-events/999-g.jsonl"; }
started 600; green
early=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: glyph-check--kiln--glyphmap\nDECIDE_OK=\"a fixture feature with no plan\"\njudge it"}')
out="$(run_pretool "$early")"
check "a glyph check before the feature's hour is refused, naming when it comes due" 'printf "%s" "$out" | grep -q "not yet due" && [ "$(rc_pretool "$early")" -eq 2 ]'
esc=$(stdin_for Agent '{"subagent_type":"glyph-check","prompt":"UNIT: glyph-check--kiln--glyphmap\nDECIDE_OK=\"a fixture feature with no plan\"\nGLYPH_DUE_OK=\"the GM asked for this one now\"\njudge it"}')
out="$(run_pretool "$esc")"
check "...GLYPH_DUE_OK with a reason passes the hour" '! printf "%s" "$out" | grep -q "not yet due"'
rm -f "$CLONE/.git/glyph-clock.json" "$CLONE/.git/pairing-state.json"; started 7200; green
out="$(run_pretool "$early")"
check "...on the feature's hour it passes" '! printf "%s" "$out" | grep -q "not yet due"'
rm -f "$CLONE/.git/glyph-clock.json" "$CLONE/.git/pairing-state.json"; started 600; green
python3 "$CLONE/scripts/reviews/review_owed.py" --root "$CLONE" --landing-mark on >/dev/null 2>&1
out="$(run_pretool "$early")"
check "...and once a push was refused for it (the landing mark) it passes without the escape" '! printf "%s" "$out" | grep -q "not yet due"'
rm -rf "$gm" "$CLONE/specs/999-g" "$CLONE/.specify/feature.json" "$CLONE/.git/l7r-events/999-g.jsonl" "$CLONE/.git/glyph-clock.json" "$CLONE/.git/glyph-landing"
( cd "$CLONE" && git rm -rq --cached pool/hamlets/glyphmap >/dev/null 2>&1; git -c user.email=t@t -c user.name=t commit -qm unglyph >/dev/null 2>&1; git update-ref refs/remotes/origin/main HEAD )
reset_prereq
}

# GUARD_EDIT_OK: feature 375 amendment 7 (FR-031) - THE CASES RUN IN PARALLEL PARTS, EACH ITS OWN PROCESS. After a script
# change hooks-test waited on this suite (specs/375-enforced-wave-process/research.md R3). Each part re-runs the setup above in
# its own process - its own fixture, temporary files and guard log - and then only its cases (CASES), dealt longest first by
# the measured seconds beside each case (10 s for a new one). Every check still runs and is counted; a part that ends before
# a case reports fails the suite and names it. SUITE_PARTS=1 runs the cases one after another in this process, as before.
ALL_CASES=(case_01 case_02 case_03 case_04 case_05 case_06 case_07 case_08 case_09 case_10 case_11 case_11b case_11c case_12 case_13 case_14 case_14b case_14c case_15 case_16)
declare -A WEIGHT=([case_01]=9 [case_02]=3 [case_03]=1 [case_04]=1 [case_05]=1 [case_06]=1 [case_07]=1 [case_08]=3 [case_09]=1 [case_10]=1 [case_11]=5 [case_11b]=5 [case_11c]=5 [case_12]=6 [case_13]=3 [case_14]=6 [case_14b]=6 [case_14c]=4 [case_15]=3 [case_16]=6)  # seconds, each alone, measured 2026-10-17 (383 amendment 4)
if [ -n "${CASES:-}" ]; then
  for c in $CASES; do "$c"; echo "@@reported $c"; done
  echo "@@counts $pass $fail"; exit 0
fi
# CHAINS: cases that read the fixture state an earlier case leaves, found by running each case alone and then the shortest run
# of its predecessors that passes (2026-10-12): 07 needs 06, 08 needs 06 and 07, 13 needs 12. A chain is dealt as one unit,
# its cases in order, its weight their sum; every other case is a unit alone.
CHAINS=("case_06 case_07 case_08" "case_12 case_13")
units() {  # "<weight> <case>[,<case>...]" per unit
  local c chained=" ${CHAINS[*]} " w
  for c in "${CHAINS[@]}"; do w=0; for x in $c; do w=$((w + ${WEIGHT[$x]:-10})); done; echo "$w ${c// /,}"; done
  for c in "${ALL_CASES[@]}"; do [[ "$chained" == *" $c "* ]] || echo "${WEIGHT[$c]:-10} $c"; done
}
SUITE_PARTS=${SUITE_PARTS:-8}  # 8, not 4 (feature 383 amendment 4): with case_11 and case_14 split, see the measurement in 383 research R11
# GUARD_EDIT_OK: feature 383 amendment 4 - PARTS_MAX (set by hooks-test's runner) caps the parts, as tests/hooks/parts.sh does: suites x parts hit the shared memory cap
[ -n "${PARTS_MAX:-}" ] && [ "$SUITE_PARTS" -gt "$PARTS_MAX" ] && SUITE_PARTS=$PARTS_MAX
if [ "$SUITE_PARTS" -le 1 ]; then
  for c in "${ALL_CASES[@]}"; do "$c"; done
else
  W=$(mktemp -d); declare -a LOAD PART
  for ((k = 0; k < SUITE_PARTS; k++)); do LOAD[k]=0; PART[k]=""; done
  while read -r w c; do
    best=0; for ((k = 1; k < SUITE_PARTS; k++)); do [ "${LOAD[k]}" -lt "${LOAD[best]}" ] && best=$k; done
    LOAD[best]=$((LOAD[best] + w)); PART[best]="${PART[best]} ${c//,/ }"
  done < <(units | sort -rn)
  for ((k = 0; k < SUITE_PARTS; k++)); do
    [ -n "${PART[k]}" ] && { CASES="${PART[k]}" bash "${BASH_SOURCE[0]}" > "$W/$k.log" 2>&1 & }
  done
  wait
  for ((k = 0; k < SUITE_PARTS; k++)); do
    [ -n "${PART[k]}" ] || continue
    grep -v '^@@' "$W/$k.log"
    counts=$(grep "^@@counts " "$W/$k.log" | tail -1)
    if [ -n "$counts" ]; then set -- $counts; pass=$((pass + $2)); fail=$((fail + $3))
    else
      for c in ${PART[k]}; do grep -qx "@@reported $c" "$W/$k.log" || { echo "FAIL  $c never reported - its part ended before it finished"; fail=$((fail + 1)); }; done
    fi
  done
  rm -rf "$W"
fi

# GUARD_EDIT_OK: the round arbiter's tooling fix on hour:374@2 - past the feature's hour a dispatch or a gate is refused until
# `make step-back` opens the hour; the round arbiter's own dispatch passes
reset_prereq
mkdir -p "$CLONE/specs/998-hour" "$CLONE/.specify" "$CLONE/.git/l7r-events"
printf '# F\n\n**Status**: In progress\n' > "$CLONE/specs/998-hour/spec.md"
printf '# Tasks\n\n- [ ] T01 a task\n' > "$CLONE/specs/998-hour/tasks.md"
printf '{"feature_directory": "specs/998-hour"}' > "$CLONE/.specify/feature.json"
printf '{"t": "2020-01-01T00:00:00Z", "ev": "", "sid": "s1"}\n' > "$CLONE/.git/l7r-events/998-hour.jsonl"
out=$(run_pretool "$(stdin_for Agent '{"subagent_type":"glyph-check","description":"g","prompt":"x"}')")
check "past the hour, a dispatch is refused until the step-back opens" '[[ "$out" == *"make step-back"* ]]'
out=$(run_pretool "$(stdin_for Bash '{"command":"make done"}')")
check "past the hour, a gate is refused until the step-back opens" '[[ "$out" == *"make step-back"* ]]'
out=$(run_pretool "$(stdin_for Agent '{"subagent_type":"round-arbiter","description":"r","prompt":"x"}')")
check "the round arbiter's own dispatch passes" '[[ "$out" != *"make step-back"* ]]'
rm -rf "$CLONE/specs/998-hour" "$CLONE/.specify" "$CLONE/.git/l7r-events"

# --- T22. a refused dispatch is sent again or recorded dropped before the turn ends (feature 385 T22, plan D44) ------------
# GUARD_EDIT_OK: feature 385 T22 - the incident's shape: a decide-first refusal of an impl-drift, never re-sent
TR="$TMP/proj/sid-t22.jsonl"; BUN=/tmp/l7r-check/claims-owed/MANIFEST.md
human() { printf '{"type":"user","timestamp":"%s","origin":{"kind":"human"},"message":{"role":"user","content":"go"}}\n' "$1"; }
call() { printf '{"type":"assistant","timestamp":"%s","message":{"role":"assistant","content":[{"type":"tool_use","id":"%s","name":"Agent","input":{"subagent_type":"impl-drift","description":"d","prompt":"Judge %s"}}]}}\n' "$1" "$2" "$BUN"; }
refused() { printf '{"type":"user","timestamp":"%s","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"%s","is_error":true,"content":"PreToolUse:Agent hook error: [check-bundle-hooks.sh]: \\nBLOCKED: impl-drift on %s: decide first"}]}}\n' "$1" "$2" "$BUN"; }
launched() { printf '{"type":"user","timestamp":"%s","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"%s","content":"Async agent launched successfully."}]}}\n' "$1" "$2"; }
STOP22=$(printf '{"transcript_path":"%s","session_id":"sid-t22","cwd":"%s"}' "$TR" "$CLONE")
rm -f "$CLONE/.git/dropped-dispatches.jsonl"; printf '2026-10-18T03:50:00Z\n' > "$CLONE/.git/dispatch-seen"   # a turn end passed at 03:50
{ call 2026-10-18T03:57:57Z a1; refused 2026-10-18T03:57:58Z a1; human 2026-10-18T03:59:42Z; } > "$TR"
out=$( cd "$CLONE" && printf '%s' "$STOP22" | "$HOOK" stop 2>&1 ); rc=$?
check "IT FIRES: a turn ends with a refused impl-drift never re-sent (the refusal before the GM's next prompt)" '[ "$rc" -eq 2 ]'
check "...naming the check, its bundle and both commands" '[[ "$out" == *"impl-drift on $BUN"* && "$out" == *"make dispatch-dropped TYPE=impl-drift"* ]]'
( cd "$CLONE" && printf '%s' "$STOP22" | "$HOOK" stop >/dev/null 2>&1 ); rc=$?
check "...and again at the next turn end, the blocked one having moved nothing" '[ "$rc" -eq 2 ]'
{ call 2026-10-18T09:40:00Z a2; launched 2026-10-18T09:40:01Z a2; } >> "$TR"
( cd "$CLONE" && printf '%s' "$STOP22" | "$HOOK" stop >/dev/null 2>&1 ); rc=$?
check "STAYS QUIET: the same check on the same bundle sent again and launched" '[ "$rc" -eq 0 ]'
{ call 2026-10-18T10:00:00Z a3; refused 2026-10-18T10:00:01Z a3; } >> "$TR"
( cd "$CLONE" && printf '%s' "$STOP22" | "$HOOK" stop >/dev/null 2>&1 ); rc=$?
check "a refusal after the last passed turn end is held" '[ "$rc" -eq 2 ]'
( cd "$CLONE" && make -s -f "$(dirname "$HOOK")/../../Makefile" dispatch-dropped TYPE=impl-drift BUNDLE="$BUN" WHY="x" >/dev/null 2>&1 ); rc=$?
check "dispatch-dropped refuses a reason of one word" '[ "$rc" -ne 0 ]'
( cd "$CLONE" && python3 scripts/hooks/lib/hm_dropped.py drop --root . --type impl-drift --bundle "$BUN" --why "the round was folded into the next" >/dev/null 2>&1 )
( cd "$CLONE" && printf '%s' "$STOP22" | "$HOOK" stop >/dev/null 2>&1 ); rc=$?
check "STAYS QUIET: the refusal recorded dropped with a reason" '[ "$rc" -eq 0 ]'
rm -f "$CLONE/.git/dispatch-seen" "$CLONE/.git/dropped-dispatches.jsonl" "$TR"

printf '\ntest-pair-hooks: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
