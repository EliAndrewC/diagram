#!/usr/bin/env bash
# test-dmypy-hooks.sh - prove dmypy-hooks.sh stops the daemons of ended sessions and NOTHING else.
# (GUARD_EDIT_OK: the companion of a new guard, GM 2026-08-28)
# A throwaway <main>/.clones/<session> fixture. "Daemons" are sleeps whose argv[0] says dmypy;
# "sessions" are sleeps whose argv[0] says claude, registered as ~/.claude/sessions/<pid>.json.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/dmypy-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d)
PIDS_FILE="$TMP/pids"   # a FILE, not a variable: spawn runs inside $(...) subshells, where a variable never reaches the trap
cleanup() { for p in $(cat "$PIDS_FILE" 2>/dev/null); do kill -KILL "$p" 2>/dev/null; done; rm -rf "$TMP"; }
trap cleanup EXIT
MAIN="$TMP/main"; SESS="$TMP/sessions"; SKILL=.claude/skills/diagram
mkdir -p "$MAIN/.clones/.session-clones" "$SESS" "$MAIN/$SKILL"
export DMYPY_FIXTURE=1 DMYPY_MAIN="$MAIN" DMYPY_SESSIONS_DIR="$SESS"

spawn() { # spawn <argv0-word> -> pid of a sleeping process whose cmdline carries that word
  # stdio to /dev/null: a child holding the runner's stdout open would make the RUNNER hang until the
  # sleeps end (measured 2026-08-28: the first run of this test timed out at 2 min for exactly that)
  bash -c "exec -a '$1' sleep 300" >/dev/null 2>&1 </dev/null & local p=$!; echo "$p" >> "$PIDS_FILE"; sleep 0.05; echo "$p"
}
daemon_in() { # daemon_in <clone-dir> -> pid; writes the clone's .dmypy.json the way dmypy does
  local p; p=$(spawn "python3 -m mypy.dmypy run --"); mkdir -p "$1/$SKILL"
  printf '{"pid": %s, "connection_name": "/tmp/x/dmypy.sock"}' "$p" > "$1/$SKILL/.dmypy.json"; echo "$p"
}
session() { # session <sid> <name> -> a live "claude" process registered under the sessions dir
  local p; p=$(spawn claude); printf '{"sessionId":"%s","name":"%s"}' "$1" "$2" > "$SESS/$p.json"; echo "$p"
}
alive() { kill -0 "$1" 2>/dev/null; }

# ---- the fixture: five clones, as on 2026-08-28
# a: owned by a live session through its CLAIM        (kept)
# b: owned by a live session through its NAME only    (kept - no claim recorded yet)
# c: claimed by a session whose process has EXITED    (stopped - the motivating case)
# d: no session at all, a status file naming a dead pid (stale file removed, nothing to kill)
# main's own tree: a daemon where none may run        (stopped)
mkdir -p "$MAIN/.clones/sess-a" "$MAIN/.clones/sess-b" "$MAIN/.clones/sess-c" "$MAIN/.clones/sess-d"
DA=$(daemon_in "$MAIN/.clones/sess-a"); DB=$(daemon_in "$MAIN/.clones/sess-b"); DC=$(daemon_in "$MAIN/.clones/sess-c"); DM=$(daemon_in "$MAIN")
mkdir -p "$MAIN/.clones/sess-d/$SKILL"; printf '{"pid": 999999999}' > "$MAIN/.clones/sess-d/$SKILL/.dmypy.json"
SA=$(session sid-a "Something Else"); printf '%s' "$MAIN/.clones/sess-a" > "$MAIN/.clones/.session-clones/sid-a"
SB=$(session sid-b "Sess B")
SC=$(session sid-c "Sess C"); printf '%s' "$MAIN/.clones/sess-c" > "$MAIN/.clones/.session-clones/sid-c"
kill -KILL "$SC"; wait "$SC" 2>/dev/null   # session c has ended; its json and claim linger, as they do

echo "1. THE SWEEP stops the orphans and only the orphans"
OUT=$("$HOOK" sweep 2>&1); rc=$?
check "sweep exits 0"                              '[ "$rc" -eq 0 ]'
check "a (claimed, live) survives"                 'alive "$DA"'
check "b (named, live, unclaimed) survives"        'alive "$DB"'
check "c (session exited) is stopped"              '! alive "$DC"'
check "c's status file is gone"                    '[ ! -f "$MAIN/.clones/sess-c/$SKILL/.dmypy.json" ]'
check "main's daemon is stopped"                   '! alive "$DM"'
check "d's stale status file is removed"           '[ ! -f "$MAIN/.clones/sess-d/$SKILL/.dmypy.json" ]'
check "it says what it stopped"                    'printf "%s" "$OUT" | grep -q "sess-c.*no live session owns"'
check "it names main's reason"                     'printf "%s" "$OUT" | grep -q "main is never a workspace"'
check "it does not mention the kept ones"          '! printf "%s" "$OUT" | grep -q "sess-a\|sess-b"'
check "the kept status files remain"               '[ -f "$MAIN/.clones/sess-a/$SKILL/.dmypy.json" ] && [ -f "$MAIN/.clones/sess-b/$SKILL/.dmypy.json" ]'

echo "2. A SECOND SWEEP is silent: nothing left to do"
OUT2=$("$HOOK" sweep 2>&1)
check "quiet when there is nothing to stop"        '[ -z "$OUT2" ]'
check "a and b still alive"                        'alive "$DA" && alive "$DB"'

echo "3. SESSION-END stops the ending session's own daemon while its process is still live"
OUT3=$(printf '{"session_id":"sid-a","reason":"exit"}' | "$HOOK" session-end 2>&1); rc=$?
check "session-end exits 0"                        '[ "$rc" -eq 0 ]'
check "a's daemon is stopped"                      '! alive "$DA"'
check "says its session ended"                     'printf "%s" "$OUT3" | grep -q "sess-a.*its session ended"'
check "b, another live session's, survives"        'alive "$DB"'
check "a session with no claim is harmless"        'printf "{\"session_id\":\"nobody\"}" | "$HOOK" session-end >/dev/null 2>&1 && alive "$DB"'
check "an empty payload is harmless"               'printf "" | "$HOOK" session-end >/dev/null 2>&1 && alive "$DB"'

echo "4. PID REUSE: a status file whose pid is a live NON-dmypy process is not killed"
OTHER=$(spawn "some-other-program"); mkdir -p "$MAIN/.clones/sess-e/$SKILL"
printf '{"pid": %s}' "$OTHER" > "$MAIN/.clones/sess-e/$SKILL/.dmypy.json"
"$HOOK" sweep >/dev/null 2>&1
check "the unrelated process survives"             'alive "$OTHER"'
check "its misleading status file is removed"      '[ ! -f "$MAIN/.clones/sess-e/$SKILL/.dmypy.json" ]'

echo "5. AN UNKNOWN MODE is harmless"
check "an unknown mode exits 0"                    '"$HOOK" bogus >/dev/null 2>&1'
# (the seams-refused-outside-a-fixture rule is NOT exercised here on purpose: a run without the fixture
#  flag sweeps the REAL main and the REAL sessions, and a test must not have side effects on live daemons)

echo
echo "dmypy-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
