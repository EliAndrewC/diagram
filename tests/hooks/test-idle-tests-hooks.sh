#!/usr/bin/env bash
# test-idle-tests-hooks.sh - prove idle-tests-hooks.sh does what feature 136 says, in seconds.
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 136)
# A throwaway <main>/.clones/<session> fixture; the clocks, the tick, the wait, the lock's home,
# the sessions directory and the command run are injected through the IDLE_* seams, which the
# hook honors only inside a fixture (proved below too).
set -u
source "$(dirname "${BASH_SOURCE[0]}")/seen.sh"  # seen VAR <grep args>: a run's text grepped from a here-string, never a pipe (451 T253)
HOOK="$(cd "$(dirname "$0")" && pwd)/idle-tests-hooks.sh"
pass=0 fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL: $1"; }
check() { if eval "$2"; then ok; else bad "$1"; fi; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
MAIN="$TMP/main"; mkdir -p "$MAIN/.clones"
git -C "$MAIN" init -q; git -C "$MAIN" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
mkclone() { git clone -q "$MAIN" "$MAIN/.clones/$1"; mkdir -p "$MAIN/.clones/$1"; }
mkclone sess-a; mkclone sess-b; mkclone sess-c
CA="$MAIN/.clones/sess-a"; CB="$MAIN/.clones/sess-b"; CC="$MAIN/.clones/sess-c"
HOMEDIR="$TMP/home"; SESS="$TMP/sessions"; mkdir -p "$HOMEDIR" "$SESS"
# a live "session": the sessions json is named by a live pid (this shell's)
printf '{"sessionId":"sid-a"}' > "$SESS/$$.json"
CLOCKF="$TMP/clock"; echo 1000000 > "$CLOCKF"
CLOCK="$TMP/clock.sh"; printf '#!/bin/sh\ncat %s\n' "$CLOCKF" > "$CLOCK"; chmod +x "$CLOCK"
# The ticker and the suspend jumps advance the clock at once: a plain `> "$CLOCKF"` truncated the file while the other writer
# or the hook read it, so a read saw it empty or torn (`01620 + 1: arithmetic syntax error`, three cases red, 2026-11-11 in
# T95's landing and again alone). One writer at a time (flock), and a rename, so a reader sees the old value or the new, whole.
tick_clock() { ( flock 9; n=$(( $(cat "$CLOCKF") + ${1:-1} )); echo "$n" > "$CLOCKF.$BASHPID"; mv -f "$CLOCKF.$BASHPID" "$CLOCKF" ) 9>"$CLOCKF.lock"; }
# a run stand-in that records start/end and sleeps a little
RUNNER="$TMP/run.sh"; RUNLOG="$TMP/runs.log"
printf '#!/bin/sh\necho "start $(date +%%s.%%N) $PWD" >> %s; sleep 0.6; echo "end $(date +%%s.%%N) $PWD" >> %s; echo FAKE-OK\n' "$RUNLOG" "$RUNLOG" > "$RUNNER"; chmod +x "$RUNNER"
# IDLE_ARM=1: the GM disabled ARMING on 2026-09-06 (DEF_ARM=0 in the hook), and the machinery it
# switches off is still wanted and still tested - so the fixture arms explicitly and every case below
# goes on exercising the timer, the stagger, the lock and the abort. Section 11 is the one case that
# leaves IDLE_ARM unset, and it is what proves the switch actually reaches `do_stop`.
# THE WAITS IN FRACTIONS OF A SECOND (feature 449 T122): the timer counts awake time in its own ticks, so a wait of N whole seconds
# was N real seconds, and the suite took 35.0 s, the full hook run's longest (2026-11-12). The seams take fractions, and a tick
# of 0.05 s keeps a fraction exact; the ticker's simulated second a 0.1 s still drifts far under the 100 s suspend threshold.
export IDLE_ARM=1 IDLE_FIXTURE=1 IDLE_TICK=0.05 IDLE_SUSPEND_S=100 IDLE_HOME="$HOMEDIR" IDLE_SESSIONS_DIR="$SESS" IDLE_CLOCK="$CLOCK" IDLE_RUN="$RUNNER" IDLE_GIVE_UP_S=100000 IDLE_BUSY_CMD="false"
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
# A TIMER'S EXIT AND ITS ARMING FILE'S REMOVAL ARE WAITED FOR, TO A DEADLINE, NEVER SLEPT ON (451 T115): a fixed 0.5-1.0 s went red
# on a timer slowed to exit or to remove the file, and each check after a wait is unchanged, so a state that never comes still
# fails. The deadline, WAIT_TRIES of 0.1 s (30 s), is a GUESS only a red run pays (a killed process measured gone in at most
# 0.059 s at a load of 16-17, 451 T111).
WAIT_TRIES=300
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
pid1=$(jq -r .timer_pid "$CA/.git/idle-tests.json")
sleep 0.3; check "timer alive" '[ -d /proc/$pid1 ]'
hook stop "$CA"; pid2=$(jq -r .timer_pid "$CA/.git/idle-tests.json")
check "re-arm is a no-op" '[ "$pid1" = "$pid2" ]'
hook prompt "$CA"
for _ in $(seq "$WAIT_TRIES"); do [ ! -f "$CA/.git/idle-tests.json" ] && [ ! -d /proc/$pid1 ] && break; sleep 0.1; done
check "prompt disarms and the timer exits" '[ ! -f "$CA/.git/idle-tests.json" ] && [ ! -d /proc/$pid1 ]'

# --- 4. the wait runs the tests once, records, surfaces once, does not re-arm
export IDLE_WAIT_S=0.3; : > "$RUNLOG"; touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"
check "record written after the wait" 'wait_for "$CA/dev/idle-log/*-sess-a.json" 8'
# the timer removes the arming file after its record, its last step
for _ in $(seq "$WAIT_TRIES"); do [ ! -f "$CA/.git/idle-tests.json" ] && break; sleep 0.1; done
check "arming consumed" '[ ! -f "$CA/.git/idle-tests.json" ]'
check "the run happened once, in the clone" '[ "$(grep -c "^start" "$RUNLOG")" = 1 ] && grep -q "$CA" "$RUNLOG"'
hook prompt "$CA"; check "verdict surfaced at the next prompt" 'seen OUT -q "idle-tests: ran .* clean"'
hook prompt "$CA"; check "surfaced once only" '! seen OUT -q "idle-tests: ran"'
# --- 4b. D10: a new arming on a clone unchanged since that green run rolls nothing and records the skip
hook stop "$CA"
# the wait is an upper bound, so a green run pays nothing for it: 10 s timed out in land-tooling's worktree under load (feature 449 T065)
check "second record (the skip)" 'wait_count "$CA/dev/idle-log/*-sess-a.json" 2 30'
check "no second run on unchanged content" '[ "$(grep -c "^start" "$RUNLOG")" = 1 ] && grep -q "skipped" "$(ls -t "$CA"/dev/idle-log/*-sess-a.json | head -1)"'
hook prompt "$CA"; check "the skip surfaces" 'seen OUT -q "skipped - unchanged"'
# a change to the clone makes the next arming roll again
git -C "$CA" -c user.email=t@t -c user.name=t commit -q --allow-empty -m change
hook stop "$CA"; sleep 0.2
# GUARD_EDIT_OK: feature 374 batch 5 - this wait timed out once in land-tooling's worktree under load (passed in the clone at once):
# the background roll is the hook's own, so give it 90 s, as all 56 suites side by side need (twice under 30, 2026-11-08)
check "changed content rolls again" 'wait_grep_n "^end" "$RUNLOG" 2 90 && [ "$(grep -c "^start" "$RUNLOG")" = 2 ]'
hook prompt "$CA"
rm -f "$TMP/ticking"; wait $TK 2>/dev/null

# --- 5. a suspend restarts the full wait: the clock jumps past the threshold mid-wait
# A SINGLE JUMP IS A BET ON A WINDOW; SEVERAL CANNOT MISS (feature 169). A jump is seen only if it lands between `wait_ms`'s
# baseline reading (`last = now()`) and its next one, and a fixed pre-jump sleep cannot promise that: the first fix for this
# flake raised the sleep from 0.6 s to 1.5 s and it still went red at the gate on 2026-08-30 while passing 30/30 standalone. The
# lost-update race between a ticker and the jump was measured and ruled out first (0 of 40). Eight jumps over ~1 s, so at least
# one lands inside the window; each extra one only restarts the wait. Even eight missed it once the shell lagged as long as the
# wait (with the suite's `sleep` 1.0 s late, 5 of 8 "the suspend was counted (0)", 2026-11-21): the first jump landed before the
# timer's first reading and the next came after its wait (and a wait for that reading, polled, saw it a lagged poll late). So the
# case's clock HOLDS the timer: a read by the `--idle-tests timer` process, once its value is taken, writes `t` and waits while a
# gate file stands. The timer is then frozen inside its baseline reading with no awake time counted, the first jump is written,
# and the gate goes: whatever the shell's lag, the first jump lands inside the wait (the guard's `ask` waits on the clock with no
# limit, so a held read is never cut off into a reading of 0).
# THE FULL WAIT IS PINNED BY THE GUARD'S OWN EVENT, NOT BY SLACK (feature 451 T99). The check took its time AFTER the last jump's
# `sleep 0.15` and a fork of `date`, and asked 0.35 s of the 0.6 s wait to remain past it, so the test shell's own lag ate the
# margin: red at a load of 16.5 beside a make done (2026-11-21, green on the rerun unchanged), and 8 of 8 red with the suite's
# own `date` started 0.5 s late (1 of 8 at 0.2 s). Now each jump's time is taken BEFORE it is written, so the timer cannot have
# seen it earlier; jump k moves the clock B * 2^(k-1) s and no ticker runs, so the timer's log line "wall jumped N s" spans
# exactly N + 1 s, and that span's highest bit names the latest jump the timer saw. The run must start a full IDLE_WAIT_S after
# that jump's time - twelve sleeps of IDLE_TICK, which load can lengthen and never shorten - and after twelve of the timer's own
# ticks counted from its first sight of it (its clock reads, below), since seconds alone let a timer that never restarts pass
# once its ticks ran slower than real time. A shell that stalls long enough for
# the wait to end between two jumps is no failure: the jumps after it were never seen, and the bound is on the last one that was.
# Case 4 waits under the ticker, so a clock that moves while the timer waits is still proved not to be a suspend.
export IDLE_WAIT_S=0.6; : > "$RUNLOG"; rm -f "$CA"/dev/idle-log/*.json
B=300  # every jump past IDLE_SUSPEND_S (100), the eight together (B * 255 = 76,500) inside IDLE_GIVE_UP_S (100,000) of armed_at
READS="$TMP/clock.reads"; GATE="$TMP/clock.gate"; CLOCK5="$TMP/clock5.sh"; : > "$READS"; touch "$GATE"; c0=$(cat "$CLOCKF")
# the timer's reads logged as `t <value> <time>`: two a tick (`alive` and `now`), so they count its awake time in its own units
cat > "$CLOCK5" <<EOF5
#!/bin/sh
v=\$(cat "$CLOCKF"); echo "\$v"
case "\$(tr '\\0' ' ' < /proc/\$PPID/cmdline 2>/dev/null)" in *" --idle-tests timer "*)
  echo "t \$v \$(date +%s.%N)" >> "$READS"; while [ -f "$GATE" ]; do sleep 0.01; done ;; esac
EOF5
chmod +x "$CLOCK5"; export IDLE_CLOCK="$CLOCK5"
hook stop "$CA"
check "the timer took its first reading and is held there" 'wait_grep "^t " "$READS" 10'
# THE JUMPS PACED BY THE TIMER'S TICKS, NOT BY `sleep`: each next jump waits for four of the timer's reads after the last, so at
# least one tick is counted between two jumps whatever the load. A timer that counts them without restarting then runs short of
# a full wait after its last jump; paced by a 0.15 s sleep, beside 22 burners the ticks came slower than the jumps and such a timer
# passed 8 of 8 (2026-11-21). The pacing ends once the run has started: the wait is over and no jump after it is seen.
paced() { local i=0; while [ $i -lt 100 ]; do [ "$(grep -c "^t " "$READS")" -ge "$1" ] && return 0; grep -q "^start" "$RUNLOG" && return 1; sleep 0.1; i=$((i+1)); done; return 1; }
t_before=()
# bash's own clock, no fork: a `date` before each jump spread the jumps by its lag, and with the suite's dates 1.0 s late, before
# the gate, the whole wait ended before any jump (8 of 8 "the suspend was counted (0)", 2026-11-21); a locale may write a comma
for k in 1 2 3 4 5 6 7 8; do
  t_before[k]=${EPOCHREALTIME/,/.}; tick_clock $(( B << (k - 1) )); rm -f "$GATE"
  [ $k -lt 8 ] && { paced $(( $(grep -c "^t " "$READS") + 4 )) || break; }
done
check "record after the restart" 'wait_for "$CA/dev/idle-log/*-sess-a.json" 10'
rec=$(ls "$CA"/dev/idle-log/*-sess-a.json | head -1)
sus=$(jq -r .suspends "$rec")
t_start=$(grep "^start" "$RUNLOG" | head -1 | awk '{print $2}')
# each restart line's span as the jumps it covers, lowest bit to highest: a span off the B grid, or a gap inside one or between
# two, is a misread, and the decode says "bad" rather than name a jump; it prints the verdict, the lines read, the latest jump seen
read -r dec lines seen < <(grep -o "wall jumped [0-9]*s" "$CA/.git/idle-tests.log" | awk -v B=$B '
  { s = $3 + 1; if (s % B) { bad = 1; next }
    q = s / B; lo = 0
    for (k = 1; q > 0; k++) { if (q % 2) { if (lo && k != hi + 1) bad = 1; if (!lo) lo = k; hi = k }; q = int(q / 2) }
    if (n && lo != last + 1) bad = 1
    last = hi; n++ }
  END { print (bad || !n ? "bad" : "ok"), n + 0, last + 0 }')
check "the suspend was counted ($sus)" '[ "$sus" -ge 1 ]'
check "the timer's restart lines decode to the jumps ($dec, $lines lines, $sus counted)" '[ "$dec" = ok ] && [ "$lines" = "$sus" ]'
waited=$(awk -v s="$t_start" -v j="${t_before[seen]:-}" 'BEGIN { if (s == "" || j == "") print "none"; else printf "%.6f", s - j }')
check "the run started a FULL wait after the last jump the timer saw (jump $seen, ${waited}s)" 'awk -v w="$waited" -v need="$IDLE_WAIT_S" "BEGIN { exit !(w != \"none\" && w + 0 >= need + 0) }"'
# the same restart in the guard's own units: its reads after its first sight of that jump and before the run started; a full wait
# owes two a tick for IDLE_WAIT_S / IDLE_TICK ticks, and the reads after the wait (one `alive` after the lock, the run's start)
# only add to them
owed=$(awk -v w="$IDLE_WAIT_S" -v t="$IDLE_TICK" 'BEGIN { printf "%d", 2 * w / t + 0.5 }')
ticks=$(awk -v c=$(( c0 + B * ((1 << seen) - 1) )) -v s="$t_start" '$1 == "t" && $2 >= c { if (hit) { if (s != "" && $3 < s) n++ } else hit = 1 } END { print n + 0 }' "$READS")
check "the timer counted a FULL wait of ticks after that jump ($ticks reads, $owed owed)" '[ "$seen" -ge 1 ] && [ "$ticks" -ge "$owed" ]'
export IDLE_CLOCK="$CLOCK"

# --- 6. one runner at a time: three sessions armed together never overlap, losers defer and still run
export IDLE_WAIT_S=0.2 IDLE_DEFER_S=0.2; : > "$RUNLOG"
for c in "$CA" "$CB" "$CC"; do rm -f "$c"/dev/idle-log/*.json; done
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; hook stop "$CB"; hook stop "$CC"
check "three records" 'wait_for "$CA/dev/idle-log/*.json" 12 && wait_for "$CB/dev/idle-log/*.json" 12 && wait_for "$CC/dev/idle-log/*.json" 12'
sleep 0.3
check "no two runs overlapped" 'sort -k2,2n -k1,1 "$RUNLOG" | awk "\$1 == \"start\" { d++ } \$1 != \"start\" { d-- } d > 1 { exit 1 }"'
defs=$(cat "$CA"/dev/idle-log/*.json "$CB"/dev/idle-log/*.json "$CC"/dev/idle-log/*.json | jq -s 'map(.deferrals // 0) | add // 0')
check "the losers deferred ($defs)" '[ "$defs" -ge 1 ]'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null

# --- 7. a make running in the clone defers the run (FR-006b b)
export IDLE_WAIT_S=0.2 IDLE_DEFER_S=0.2 IDLE_BUSY_CMD="$TMP/busy.sh"; printf '#!/bin/sh\n[ -f %s/busyflag ]\n' "$TMP" > "$TMP/busy.sh"; chmod +x "$TMP/busy.sh"
: > "$RUNLOG"; rm -f "$CA"/dev/idle-log/*.json; touch "$TMP/busyflag"; touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; sleep 0.8
check "no run while a make runs" '[ ! -s "$RUNLOG" ]'
rm -f "$TMP/busyflag"
# an upper bound, so a green run pays nothing for it: 8 s was red in 3 of 64 copies run at once beside 22 CPU burners (a load of
# 79.7, feature 451 T99, 2026-11-21), and 4b's background roll already owns 90 s for the same load
check "runs once the make is gone" 'wait_for "$CA/dev/idle-log/*.json" 90'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; export IDLE_BUSY_CMD="false"

# --- 8. the session is gone: the timer exits without running
export IDLE_WAIT_S=0.3; : > "$RUNLOG"; rm -f "$CA"/dev/idle-log/*.json
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA" sid-gone; pid8=$(jq -r .timer_pid "$CA/.git/idle-tests.json")
# the timer's exit waited for, then no run asked: once it has exited none can come. The check read its pid as `\"$CA/...\"`,
# quotes and all, so jq never found the file and the half asked of /proc/999999 held of any timer, one that never exits too
# (451 T115); it asks of the pid the stop recorded.
for _ in $(seq "$WAIT_TRIES"); do [ ! -d "/proc/$pid8" ] && break; sleep 0.1; done
check "no run for a session that no longer exists" '[ ! -s "$RUNLOG" ] && [ "$pid8" -gt 0 ] 2>/dev/null && [ ! -d "/proc/$pid8" ]'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; rm -f "$CA/.git/idle-tests.json"

# --- 9. a prompt during a run aborts it (D9): a slow runner, a prompt mid-run, an aborted record, no end line
SLOW="$TMP/slow.sh"; printf '#!/bin/sh\necho "start $(date +%%s.%%N) $PWD" >> %s; sleep 3; echo "end $(date +%%s.%%N) $PWD" >> %s\n' "$RUNLOG" "$RUNLOG" > "$SLOW"; chmod +x "$SLOW"
export IDLE_WAIT_S=0.2 IDLE_RUN="$SLOW"; : > "$RUNLOG"; rm -f "$CA"/dev/idle-log/*.json
touch "$TMP/ticking"; ticker & TK=$!
hook stop "$CA"; wait_grep "^start" "$RUNLOG" 8; sleep 0.3
hook prompt "$CA"; sleep 0.5
# the aborted record is written as the run dies: waited for, not slept on (a landing's parallel suites made 0.5 s too short,
# 2026-11-11, the land-tooling worktree's run of this suite)
wait_for "$CA/dev/idle-log/*.json" 8
check "the run was aborted on the prompt" '! grep -q "^end" "$RUNLOG" && [ ! -f "$CA/.git/idle-tests.running" ]'
check "an aborted record exists and surfaces" 'grep -q "aborted" "$CA"/dev/idle-log/*.json && seen OUT -q "aborted on your prompt"'
sleep 3; check "no end line ever" '! grep -q "^end" "$RUNLOG"'
rm -f "$TMP/ticking"; wait $TK 2>/dev/null; export IDLE_RUN="$RUNNER"

# --- 10. seams are refused outside a fixture: the real tree ignores them and says so
REAL=$(cd "$(dirname "$HOOK")/../.." && pwd)
out=$(cd "$REAL" && IDLE_FIXTURE=1 IDLE_ROOT="$REAL" IDLE_WAIT_MIN=1 IDLE_WAIT_SPAN=0 "$HOOK" stagger sess-a 2>&1)
check "seams ignored in the repository's own tree" 'seen out -q "ignored" && [ "$(printf "%s" "$out" | tail -1)" -ge 60 ]'

# --- 11. THE GM'S DISABLE (2026-09-06). Two properties, because "disabled" has to mean both halves:
# arming does nothing, and everything else is untouched. Proven by DELETING the guard line and
# watching this go red, per the add-a-guard rule.
rm -f "$CA/.git/idle-tests.json"
OUT=$(printf '{"cwd":"%s","session_id":"sid-a"}' "$CA" | (cd "$CA" && IDLE_ARM=0 IDLE_ROOT="$CA" "$HOOK" stop 2>&1)); RC=$?
check "disabled: a Stop arms nothing"        '[ "$RC" -eq 0 ] && [ ! -f "$CA/.git/idle-tests.json" ]'
check "disabled: and says nothing"           '[ -z "$OUT" ]'
check "the shipped default IS disabled"      'grep -q "pub const DEF_ARM: bool = false;" "$REAL/rust/guard/src/guards/idle_tests_hooks.rs"'
# the disarm half stays live: a timer armed BEFORE the switch must still be cleanable
printf '{"session":"s","session_id":"sid-a","armed_at":1,"wait_min":9,"timer_pid":999999}' > "$CA/.git/idle-tests.json"
hook prompt "$CA" >/dev/null 2>&1
check "disabled: prompt still disarms a leftover" '[ ! -f "$CA/.git/idle-tests.json" ]'

echo "idle-tests hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
