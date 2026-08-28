#!/usr/bin/env bash
# test-idle-tests-hooks.sh - prove idle-tests-hooks.sh does what feature 136 says, in seconds.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 136)
# A throwaway <main>/.clones/<session> fixture; the clocks, the tick, the wait, the lock's home,
# the sessions directory and the command run are injected through the IDLE_* seams, which the
# hook honors only inside a fixture (proved below too).
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/idle-tests-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
MAIN="$TMP/main"; mkdir -p "$MAIN/.clones"
git -C "$MAIN" init -q; git -C "$MAIN" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
mkclone() { git clone -q "$MAIN" "$MAIN/.clones/$1"; mkdir -p "$MAIN/.clones/$1/.claude/skills/diagram"; }
mkclone sess-a; mkclone sess-b; mkclone sess-c
CA="$MAIN/.clones/sess-a"; CB="$MAIN/.clones/sess-b"; CC="$MAIN/.clones/sess-c"
HOMEDIR="$TMP/home"; SESS="$TMP/sessions"; mkdir -p "$HOMEDIR" "$SESS"
# a live "session": the sessions json is named by a live pid (this shell's)
printf '{"sessionId":"sid-a"}' > "$SESS/$$.json"
CLOCKF="$TMP/clock"; echo 1000000 > "$CLOCKF"
CLOCK="$TMP/clock.sh"; printf '#!/bin/sh\ncat %s\n' "$CLOCKF" > "$CLOCK"; chmod +x "$CLOCK"
tick_clock() { echo $(( $(cat "$CLOCKF") + ${1:-1} )) > "$CLOCKF"; }
# a run stand-in that records start/end and sleeps a little
RUNNER="$TMP/run.sh"; RUNLOG="$TMP/runs.log"
printf '#!/bin/sh\necho "start $(date +%%s.%%N) $PWD" >> %s; sleep 0.6; echo "end $(date +%%s.%%N) $PWD" >> %s; echo FAKE-OK\n' "$RUNLOG" "$RUNLOG" > "$RUNNER"; chmod +x "$RUNNER"
export IDLE_FIXTURE=1 IDLE_TICK=0.2 IDLE_SUSPEND_S=100 IDLE_HOME="$HOMEDIR" IDLE_SESSIONS_DIR="$SESS" IDLE_CLOCK="$CLOCK" IDLE_RUN="$RUNNER" IDLE_GIVE_UP_S=100000 IDLE_BUSY_CMD="false"
hook() { # hook <mode> <clone> [sid] -> RC, OUT
  OUT=$(printf '{"cwd":"%s","session_id":"%s"}' "$2" "${3:-sid-a}" | (cd "$2" && IDLE_ROOT="$2" "$HOOK" "$1" 2>&1)); RC=$?
}
wait_for() { # wait_for <file-glob> <seconds>
  local i=0; while [ $i -lt $(( ${2:-5} * 10 )) ]; do ls $1 >/dev/null 2>&1 && return 0; sleep 0.1; i=$((i+1)); done; return 1
}
wait_count() { # wait_count <file-glob> <n> <seconds> - until at least n files match
  local i=0; while [ $i -lt $(( ${3:-5} * 10 )) ]; do [ "$(ls $1 2>/dev/null | wc -l)" -ge "$2" ] && return 0; sleep 0.1; i=$((i+1)); done; return 1
}
wait_grep_n() { # wait_grep_n <pattern> <file> <n> <seconds> - until the pattern matches at least n lines
  local i=0; while [ $i -lt $(( ${4:-5} * 10 )) ]; do [ "$(grep -c "$1" "$2" 2>/dev/null)" -ge "$3" ] && return 0; sleep 0.1; i=$((i+1)); done; return 1
}
wait_grep() { # wait_grep <pattern> <file> <seconds>
  local i=0; while [ $i -lt $(( ${3:-5} * 10 )) ]; do grep -q "$1" "$2" 2>/dev/null && return 0; sleep 0.1; i=$((i+1)); done; return 1
}
# a clock that advances by itself while a timer waits: every 0.1 s adds 1 "second"
ticker() { while [ -f "$TMP/ticking" ]; do tick_clock 1; sleep 0.1; done; }

# --- 1. the stagger: inside [60, 120], deterministic, differs between names
a=$("$HOOK" stagger sess-a); b=$("$HOOK" stagger sess-b); a2=$("$HOOK" stagger sess-a)
check "stagger in band ($a)" '[ "$a" -ge 60 ] && [ "$a" -le 120 ]'
check "stagger deterministic" '[ "$a" = "$a2" ]'
check "stagger differs between names ($a vs $b)" '[ "$a" != "$b" ]'

# --- 2. never in main
hook stop "$MAIN"
check "stop in main arms nothing" '[ "$RC" -eq 0 ] && [ ! -f "$MAIN/.git/idle-tests.json" ]'

# --- 3. arm, no-op re-arm, disarm kills the timer
export IDLE_WAIT_S=1000000  # never finishes on its own
hook stop "$CA"; check "stop arms" '[ -f "$CA/.git/idle-tests.json" ]'
pid1=$(python3 -c "import json;print(json.load(open('$CA/.git/idle-tests.json'))['timer_pid'])")
sleep 0.3; check "timer alive" '[ -d /proc/$pid1 ]'
hook stop "$CA"; pid2=$(python3 -c "import json;print(json.load(open('$CA/.git/idle-tests.json'))['timer_pid'])")
check "re-arm is a no-op" '[ "$pid1" = "$pid2" ]'
hook prompt "$CA"; sleep 0.6
check "prompt disarms and the timer exits" '[ ! -f "$CA/.git/idle-tests.json" ] && [ ! -d /proc/$pid1 ]'

# --- 4. the wait runs the tests once, records, surfaces once, does not re-arm
export IDLE_WAIT_S=3; : > "$RUNLOG"; touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"
check "record written after the wait" 'wait_for "$CA/.claude/skills/diagram/dev/idle-log/*-sess-a.json" 8'
sleep 0.5
check "arming consumed" '[ ! -f "$CA/.git/idle-tests.json" ]'
check "the run happened once, in the clone" '[ "$(grep -c "^start" "$RUNLOG")" = 1 ] && grep -q "$CA" "$RUNLOG"'
hook prompt "$CA"; check "verdict surfaced at the next prompt" 'printf "%s" "$OUT" | grep -q "idle-tests: ran .* clean"'
hook prompt "$CA"; check "surfaced once only" '! printf "%s" "$OUT" | grep -q "idle-tests: ran"'
# --- 4b. D10: a new arming on a clone unchanged since that green run rolls nothing and records the skip
hook stop "$CA"
check "second record (the skip)" 'wait_count "$CA/.claude/skills/diagram/dev/idle-log/*-sess-a.json" 2 10'
check "no second run on unchanged content" '[ "$(grep -c "^start" "$RUNLOG")" = 1 ] && grep -q "skipped" "$(ls -t "$CA"/.claude/skills/diagram/dev/idle-log/*-sess-a.json | head -1)"'
hook prompt "$CA"; check "the skip surfaces" 'printf "%s" "$OUT" | grep -q "skipped - unchanged"'
# a change to the clone makes the next arming roll again
git -C "$CA" -c user.email=t@t -c user.name=t commit -q --allow-empty -m change
hook stop "$CA"; sleep 0.2
check "changed content rolls again" 'wait_grep_n "^end" "$RUNLOG" 2 10 && [ "$(grep -c "^start" "$RUNLOG")" = 2 ]'
hook prompt "$CA"
rm -f "$TMP/ticking"; wait $TK 2>/dev/null

# --- 5. a suspend restarts the full wait: the clock jumps past the threshold mid-wait
export IDLE_WAIT_S=4; : > "$RUNLOG"; rm -f "$CA"/.claude/skills/diagram/dev/idle-log/*.json
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; sleep 0.6; tick_clock 500   # a 500 s jump = a suspend
t_jump=$(date +%s.%N)
check "record after the restart" 'wait_for "$CA/.claude/skills/diagram/dev/idle-log/*-sess-a.json" 10'
rec=$(ls "$CA"/.claude/skills/diagram/dev/idle-log/*-sess-a.json | head -1)
sus=$(python3 -c "import json;print(json.load(open('$rec'))['suspends'])")
t_start=$(grep "^start" "$RUNLOG" | head -1 | awk '{print $2}')
check "the suspend was counted ($sus)" '[ "$sus" -ge 1 ]'
check "the run started a FULL wait after the jump" 'python3 -c "import sys; sys.exit(0 if float(\"$t_start\") - float(\"$t_jump\") >= 0.35 else 1)"'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null

# --- 6. one runner at a time: three sessions armed together never overlap, losers defer and still run
export IDLE_WAIT_S=1 IDLE_DEFER_S=1; : > "$RUNLOG"
for c in "$CA" "$CB" "$CC"; do rm -f "$c"/.claude/skills/diagram/dev/idle-log/*.json; done
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; hook stop "$CB"; hook stop "$CC"
check "three records" 'wait_for "$CA/.claude/skills/diagram/dev/idle-log/*.json" 12 && wait_for "$CB/.claude/skills/diagram/dev/idle-log/*.json" 12 && wait_for "$CC/.claude/skills/diagram/dev/idle-log/*.json" 12'
sleep 0.3
check "no two runs overlapped" 'python3 - "$RUNLOG" <<'"'"'PY'"'"'
import sys
ev = []
for line in open(sys.argv[1]):
    k, t, *_ = line.split()
    ev.append((float(t), 1 if k == "start" else -1))
ev.sort(); depth = 0
for _t, d in ev:
    depth += d
    assert depth <= 1, "overlap"
PY'
defs=$(cat "$CA"/.claude/skills/diagram/dev/idle-log/*.json "$CB"/.claude/skills/diagram/dev/idle-log/*.json "$CC"/.claude/skills/diagram/dev/idle-log/*.json | python3 -c "import sys,re; print(sum(int(x) for x in re.findall(r'\"deferrals\": (\d+)', sys.stdin.read())))")
check "the losers deferred ($defs)" '[ "$defs" -ge 1 ]'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null

# --- 7. a make running in the clone defers the run (FR-006b b)
export IDLE_WAIT_S=1 IDLE_DEFER_S=1 IDLE_BUSY_CMD="$TMP/busy.sh"; printf '#!/bin/sh\n[ -f %s/busyflag ]\n' "$TMP" > "$TMP/busy.sh"; chmod +x "$TMP/busy.sh"
: > "$RUNLOG"; rm -f "$CA"/.claude/skills/diagram/dev/idle-log/*.json; touch "$TMP/busyflag"; touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; sleep 1.5
check "no run while a make runs" '[ ! -s "$RUNLOG" ]'
rm -f "$TMP/busyflag"
check "runs once the make is gone" 'wait_for "$CA/.claude/skills/diagram/dev/idle-log/*.json" 8'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; export IDLE_BUSY_CMD="false"

# --- 8. the session is gone: the timer exits without running
export IDLE_WAIT_S=2; : > "$RUNLOG"; rm -f "$CA"/.claude/skills/diagram/dev/idle-log/*.json
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA" sid-gone; sleep 1.5
check "no run for a session that no longer exists" '[ ! -s "$RUNLOG" ] && [ ! -d /proc/$(python3 -c "import json;print(json.load(open(\"$CA/.git/idle-tests.json\"))[\"timer_pid\"])" 2>/dev/null || echo 999999) ]'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; rm -f "$CA/.git/idle-tests.json"

# --- 9. a prompt during a run aborts it (D9): a slow runner, a prompt mid-run, an aborted record, no end line
SLOW="$TMP/slow.sh"; printf '#!/bin/sh\necho "start $(date +%%s.%%N) $PWD" >> %s; sleep 5; echo "end $(date +%%s.%%N) $PWD" >> %s\n' "$RUNLOG" "$RUNLOG" > "$SLOW"; chmod +x "$SLOW"
export IDLE_WAIT_S=1 IDLE_RUN="$SLOW"; : > "$RUNLOG"; rm -f "$CA"/.claude/skills/diagram/dev/idle-log/*.json
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; wait_grep "^start" "$RUNLOG" 8; sleep 0.3
hook prompt "$CA"; sleep 0.5
check "the run was aborted on the prompt" '! grep -q "^end" "$RUNLOG" && [ ! -f "$CA/.git/idle-tests.running" ]'
check "an aborted record exists and surfaces" 'grep -q "aborted" "$CA"/.claude/skills/diagram/dev/idle-log/*.json && printf "%s" "$OUT" | grep -q "aborted on your prompt"'
sleep 5; check "no end line ever" '! grep -q "^end" "$RUNLOG"'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; export IDLE_RUN="$RUNNER"

# --- 10. seams are refused outside a fixture: the real tree ignores them and says so
REAL=$(cd "$(dirname "$HOOK")/.." && pwd)
out=$(cd "$REAL" && IDLE_FIXTURE=1 IDLE_ROOT="$REAL" IDLE_WAIT_MIN=1 IDLE_WAIT_SPAN=0 "$HOOK" stagger sess-a 2>&1)
check "seams ignored in the repository's own tree" 'printf "%s" "$out" | grep -q "ignored" && [ "$(printf "%s" "$out" | tail -1)" -ge 60 ]'

echo "idle-tests hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
