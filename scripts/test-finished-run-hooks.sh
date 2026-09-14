#!/usr/bin/env bash
# test-finished-run-hooks.sh - prove a finished run is surfaced once, and never mistaken for a running one.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 170 - constitution XVIII.)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/finished-run-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
export GUARD_LOG_DIR="$T/guard-log"

CLONE=$T/clone
LOG=$CLONE/.claude/skills/diagram/dev/run-log
mkdir -p "$LOG"
git init -q "$CLONE"

rec() { # rec <name> <utc> <target> <result> <seconds>
  printf '{"utc":"%s","target":"%s","scope":"reference","seconds":%s,"result":"%s","commit":"abc1234"}' \
    "$2" "$3" "$5" "$4" > "$LOG/$1.json"
}
say() { printf '{"session_id":"t","cwd":"%s"}' "$CLONE" | "$HOOK" "$1" 2>&1; }
check() { if [ "$2" = "$3" ]; then printf 'ok    %s\n' "$1"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected %s, got %s)\n' "$1" "$2" "$3"; FAIL=$((FAIL+1)); fi; }
has() { case "$1" in *"$2"*) echo yes ;; *) echo no ;; esac; }

echo "--- 1. nothing to say when there is no run at all ---"
check "no run-log, silent" "" "$(say prompt)"

echo "--- 2. THE REPORTED DEFECT: a run that failed hours ago is surfaced, with its age ---"
rec 20260830T000000 "$(date -u -d '4 hours ago' +%Y-%m-%dT%H:%M:%SZ)" done failed 212
OUT=$(say prompt)
check "a failed run four hours old is surfaced" yes "$(has "$OUT" 'finished-run:')"
check "...and says it is NOT still running" yes "$(has "$OUT" 'NOT still running')"
check "...and names the result" yes "$(has "$OUT" failed)"
check "...and gives the age in hours" yes "$(has "$OUT" '4 h')"

echo "--- 3. surfaced ONCE - a session is not nagged about a run it has been told about ---"
check "the same run is not surfaced again" "" "$(say prompt)"
check "...nor at turn end" "" "$(say stop)"

echo "--- 4. a NEW run is surfaced again, and a green one reads differently ---"
rec 20260830T120000 "$(date -u +%Y-%m-%dT%H:%M:%SZ)" done green 47
OUT=$(say stop)
check "a new finished run is surfaced" yes "$(has "$OUT" 'finished-run:')"
check "...a green one still says it is not running" yes "$(has "$OUT" 'NOT still running')"
check "...and at turn end it says not to report it as going" yes "$(has "$OUT" 'do not end a turn')"

echo "--- 5. it reports, it never blocks ---"
say stop >/dev/null; check "stop exits 0 even with a red run" 0 "$?"

echo "--- 6. outside a working tree it says nothing ---"
check "no clone, silent" "" "$(printf '{"session_id":"t","cwd":"/nonexistent"}' | "$HOOK" prompt 2>&1)"

echo "--- 7. it records, with a rule slug (feature 168) ---"
rec 20260830T130000 "$(date -u +%Y-%m-%dT%H:%M:%SZ)" test-full failed 900
say prompt >/dev/null
rules=$(python3 -c "
import json,glob,os,collections
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))" 2>/dev/null)
check "the report records as finished-not-running" yes "$(has "$rules" "'reminded', 'finished-not-running'")"

# GUARD_EDIT_OK: GM 2026-09-12 - THE SECOND RULE: a run still GOING must not be abandoned. The first rule
# reports a run that finished and was never read; this is its mirror image, and it happened the same
# afternoon - a detached `make done` failed 58 s after the turn ended on "the gate is running" and sat
# unread for 52 minutes. Detection is by CWD out of /proc, never by a process pattern, so nothing here can
# match its own command line.
echo "--- 6. a run STILL GOING holds the turn (GM 2026-09-12) ---"
LV=$T/live-clone; mkdir -p "$LV"; git init -q "$LV"
check "a clone with no make running reports nothing live" "" "$("$HOOK" live "$LV")"

cat > "$LV/Makefile" <<'MK'
sleeper:
	@sleep 12
MK
( cd "$LV" && make sleeper >/dev/null 2>&1 & ) ; sleep 1
check "a live make in the clone is found, with its target" yes "$(has "$("$HOOK" live "$LV")" sleeper)"

lstop() { printf '{"session_id":"t","cwd":"%s"%s}' "$LV" "${1:-}" | "$HOOK" stop >/dev/null 2>"$T/fr.err"; }
lstop; check "stop refuses a turn that would close over a live run" 2 "$?"
check "...and says so" yes "$(has "$(cat "$T/fr.err")" 'A MAKE RUN IS STILL GOING')"
check "...and what to do about it" yes "$(has "$(cat "$T/fr.err")" 'REPORT WHAT IT SAID')"
lstop; check "ONCE per run, never a loop" 0 "$?"

# NO TOKEN ESCAPE EXISTS, and this is the test that established why: a Stop payload carries no command, so
# there is nowhere to put one. The once-per-run release is the only way through, and it is enough.
rm -f "$LV/.git/live-run.told"
lstop ',"tool_input":{"command":"true RUN_OK=the GM asked something else"}'
check "a token in a command cannot escape a Stop hook (it never sees one)" 2 "$?"
lstop; check "...and the second attempt closes the turn, which IS the release" 0 "$?"
RULES=$(python3 -c "
import collections, glob, json, os
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))" 2>/dev/null)
check "the refusal is recorded with its own rule" yes "$(has "$RULES" "'blocked', 'run-still-going'")"

# GUARD_EDIT_OK: feature 246 (GM 2026-09-13) - THE SECOND QUESTION: is anyone WAITING for the live run? In its first
# day the rule refused 18 turn-ends on 13 runs, 5 of them repeats on a run it had already refused, every one in the
# measuring session on a run the harness was tracking with a waiter loop armed besides. So a run with an ancestor
# named `claude` (the harness; a background-mode command) and a run with a loop on its log are let through with one
# line each, the refusal keys on the ROOT make so a phase child refuses nothing new, and only a detached run nobody
# watches is refused. Every case drives a REAL process; nothing here is a pattern over a command line.
echo "--- 6b. a run the HARNESS tracks is let through: an ancestor named claude (feature 246) ---"
for p in $("$HOOK" live "$LV" | cut -d' ' -f1); do kill "$p" 2>/dev/null; done; sleep 1; rm -f "$LV/.git/live-run.told"
cat > "$LV/Makefile" <<'MK'
sleeper:
	@sleep 12
phases:
	@$(MAKE) --no-print-directory p1; $(MAKE) --no-print-directory p2
p1:
	@sleep 3
p2:
	@sleep 9
MK
mkdir -p "$T/tasks"; cp "$(command -v bash)" "$T/claude"
# THE FIXTURES DETACH FOR REAL, AND THE STAND-IN HARNESS STAYS ALIVE - two shell facts the first run of this section
# got wrong: a process is reparented to init only when its PARENT exits (so every fixture is started inside a
# subshell that exits at once; started bare, its parent is this suite, whose ancestor is the REAL harness, and the
# judge reports it tracked - correctly); and `bash -c "... && make x"` execs INTO its last command, so the
# `claude`-named shell vanished and left the make with no ancestor at all - the trailing `; :` keeps it a parent.
( "$T/claude" -c "cd $LV && make sleeper; :" > "$T/tasks/t1.output" 2>&1 & ) ; sleep 1
check "the judge sees the run as tracked" yes "$(has "$("$HOOK" judge "$LV")" ' sleeper tracked ')"
OUT=$(printf '{"session_id":"t","cwd":"%s"}' "$LV" | "$HOOK" stop 2>"$T/fr.err"); RC=$?
check "stop lets a tracked run through" 0 "$RC"
check "...with one line of context saying the harness will wake the session" yes "$(has "$OUT" 'harness will wake this session')"
check "...and no refusal text" no "$(has "$(cat "$T/fr.err")" 'STILL GOING')"
for p in $("$HOOK" live "$LV" | cut -d' ' -f1); do kill "$p" 2>/dev/null; done; pkill -f "$T/claude" 2>/dev/null; sleep 1

echo "--- 6c. a detached run with a WAITER on its log is let through; one on another file is not ---"
rm -f "$LV/.git/live-run.told"
( setsid nohup bash -c "cd $LV && exec make sleeper" </dev/null > "$T/run.log" 2>&1 & )
sleep 1
check "detached and unwatched: the judge says so, naming the log" yes "$(has "$("$HOOK" judge "$LV")" " unwatched $T/run.log")"
setsid nohup bash -c "until grep -q NEVER_APPEARS $T/other.log 2>/dev/null; do sleep 3; done" </dev/null >/dev/null 2>&1 &
sleep 1
lstop; check "a waiter on a DIFFERENT file does not count: refused" 2 "$?"
check "...and the refusal prescribes the loop on the run's OWN log" yes "$(has "$(cat "$T/fr.err")" "GATE FAILED\" $T/run.log")"
check "...and says a background-mode run needs no loop" yes "$(has "$(cat "$T/fr.err")" 'needs NO loop')"
setsid nohup bash -c "until grep -q NEVER_APPEARS $T/run.log; do sleep 3; done" </dev/null >/dev/null 2>&1 &
sleep 1
rm -f "$LV/.git/live-run.told"
check "the judge sees the run as watched, with its waiter" yes "$(has "$("$HOOK" judge "$LV")" " sleeper watched ")"
OUT=$(printf '{"session_id":"t","cwd":"%s"}' "$LV" | "$HOOK" stop 2>"$T/fr.err"); RC=$?
check "stop lets a watched run through" 0 "$RC"
check "...with one line naming the waiter" yes "$(has "$OUT" 'a waiter (pid')"
pkill -f "NEVER_APPEARS" 2>/dev/null; for p in $("$HOOK" live "$LV" | cut -d' ' -f1); do kill "$p" 2>/dev/null; done; sleep 1

echo "--- 6d. ONCE PER ROOT RUN: a phase child appearing does not refuse again (the R1 shape) ---"
rm -f "$LV/.git/live-run.told"
( setsid nohup bash -c "cd $LV && exec make phases" </dev/null > "$T/phases.log" 2>&1 & )
sleep 1
check "the two-phase run shows ONE root (the child speaks through it)" 1 "$("$HOOK" judge "$LV" | wc -l)"
FIRST=$("$HOOK" live "$LV" | tr '\n' ' ')
lstop; check "refused once, with p1 live" 2 "$?"
sleep 4
SECOND=$("$HOOK" live "$LV" | tr '\n' ' ')
check "the live set has CHANGED (p2 is the child now)" no "$([ "$FIRST" = "$SECOND" ] && echo yes || echo no)"
check "...and the same root does NOT refuse again" 0 "$(lstop; echo $?)"
for p in $("$HOOK" live "$LV" | cut -d' ' -f1); do kill "$p" 2>/dev/null; done; sleep 1
RULES3=$(python3 -c "
import collections, glob, json, os
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))" 2>/dev/null)
check "the tracked pass records with its own rule" yes "$(has "$RULES3" "'permitted', 'tracked-run'")"
check "the watched pass records with its own rule" yes "$(has "$RULES3" "'permitted', 'waiter-armed'")"

# GUARD_EDIT_OK: GM 2026-09-12 - THE THIRD RULE: a waiter spinning on a DEAD PRODUCER. The GM found three in
# their own status line, re-grepping every 15 s for EIGHT HOURS on logs from the OOM-killed runs of that
# morning - the same incident that produced the proof-of-life clause, whose waiters predate it. Two census
# attempts by this session missed them: at any instant the visible process is the loop's own 15 s `sleep`, so
# filtering by process AGE cannot see the loop and filtering by NAME sees only `sleep`.
echo "--- 7. a waiter spinning on a dead producer is reported (GM 2026-09-12) ---"
DEAD=$T/deadlog.txt; echo stub > "$DEAD"; touch -d "2 hours ago" "$DEAD"
check "no waiter, nothing reported" "" "$("$HOOK" stale)"
setsid nohup bash -c "until grep -q NEVER_APPEARS $DEAD; do sleep 3; done" </dev/null >/dev/null 2>&1 &
sleep 2
check "the spinning waiter is found, with the file it watches" yes "$(has "$("$HOOK" stale)" "$DEAD")"
OUT=$(printf '{"session_id":"t","cwd":"%s"}' "$CLONE" | "$HOOK" stop 2>&1)
check "...and it is reported at turn end" yes "$(has "$OUT" 'SPINNING ON A DEAD PRODUCER')"
check "...with what to do about it" yes "$(has "$OUT" 'stop the loop by its pid')"
check "it REPORTS rather than blocks (the loop is harmless; not knowing is not)" 0 "$(printf '{"session_id":"t","cwd":"%s"}' "$CLONE" | "$HOOK" stop >/dev/null 2>&1; echo $?)"
# a waiter whose producer is ALIVE must not be reported
LIVEF=$T/livelog.txt; : > "$LIVEF"
setsid nohup bash -c "exec 9>>$LIVEF; until grep -q NEVER_APPEARS $LIVEF; do sleep 3; done" </dev/null >/dev/null 2>&1 &
sleep 2
check "a waiter whose file is still held open is NOT reported" no "$(has "$("$HOOK" stale)" "$LIVEF")"
for p in $("$HOOK" stale | cut -d' ' -f1); do kill -TERM "$p" 2>/dev/null; done
pkill -f "NEVER_APPEARS" 2>/dev/null
RULES2=$(python3 -c "
import collections, glob, json, os
rows=[json.load(open(f)) for f in glob.glob(os.path.join('$GUARD_LOG_DIR','*.json'))]
print(dict(collections.Counter((r['event'], r.get('rule')) for r in rows)))" 2>/dev/null)
check "the report records with its own rule" yes "$(has "$RULES2" "waiter-on-a-dead-producer")"

echo "-----"
printf 'test-finished-run-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ] || exit 1
