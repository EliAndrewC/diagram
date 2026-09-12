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

echo "-----"
printf 'test-finished-run-hooks: passed %s, failed %s\n' "$PASS" "$FAIL"
[ "$FAIL" = 0 ] || exit 1
