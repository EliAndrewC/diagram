#!/usr/bin/env bash
# Tests for scripts/state-sync.sh (`make state-push`, `make state-restore`, feature 451 T258): a clone's check answers
# (<common .git>/record-checks) and event logs (<common .git>/l7r-events) committed into a bare mirror under the common .git and pushed
# to the tooling-state repository on the clone's own branch, the logs as fixed-size segments so an append changes one small file; a
# restore merging both back - an answer by its record's utc (`l7r-gate record merge-answers`), a log by the lines it lacks - and never
# overwriting a newer local answer; a failed push said in one line, logged, and exiting 0 so no landing is refused.
# Run: tests/hooks/test-state-sync.sh   (exit 0 = all green)
#
# THE REMOTE IS A LOCAL BARE FIXTURE, ALWAYS (STATE_REMOTE), and git is held to the file transport (GIT_ALLOW_PROTOCOL=file), so no
# case can reach the real repository; every answer and log line here is made up. The gate is the repository's own (merge-answers).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SYNC="$REPO/scripts/state-sync.sh"
PASS=0; FAIL=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok() { echo "  ok      $1"; PASS=$((PASS+1)); }
no() { echo "  FAIL    $1 ${2:-}"; FAIL=$((FAIL+1)); }
seen() { local text=$1; shift; grep -q "$@" <<< "$text"; }  # a here-string, never a pipe under pipefail (451 T253)
export GIT_ALLOW_PROTOCOL=file GIT_TERMINAL_PROMPT=0
unset GITHUB_TOKEN GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
export STATE_REMOTE="$T/remote.git" STATE_SEGMENT=200
git init -q --bare "$STATE_REMOTE"
rgit() { git --git-dir="$STATE_REMOTE" "$@"; }

clone() { # <dir>: a fixture clone named by its directory, with one commit
  mkdir -p "$1" && git -C "$1" init -q && git -C "$1" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
  mkdir -p "$1/.git/record-checks" "$1/.git/l7r-events"
}
answer() { # <clone> <unit> <utc> <fingerprint> <result>
  printf '{\n  "answered": [\n    "%s"\n  ],\n  "fingerprint": "%s",\n  "result": "%s",\n  "utc": "%s"\n}\n' "$4" "$4" "$5" "$3" > "$1/.git/record-checks/$2.json"
}
lines() { # <clone> <log> <first> <last>: made-up event lines, 40 bytes each
  local i; for i in $(seq "$3" "$4"); do printf '{"t": %04d, "ev": "made-up-line-%04d"}\n' "$i" "$i" >> "$1/.git/l7r-events/$2"; done
}
run() { ( cd "$1" && shift && bash "$SYNC" "$@" ) 2>&1; }
# A BACKGROUND RUN IS WAITED FOR BY ITS CONDITION, NEVER BY A COUNT OF SLEEPS (feature 451 T314): a detached push or a fresh clone's
# restore ends when the machine lets it, and a wait of 100 short sleeps (about 11 s) ran out under a landing gate's load (2026-11-26
# 18:27 UTC, the suite 94.7 s where it takes 4 to 6 s alone), silently, so the case after it went red on good work. The wait ends the
# moment the condition holds; WAIT seconds is only how long a run that never ends is given, a GUESS knob (STATE_SYNC_WAIT): 120 s is
# about 11 times the bound that ran out and 300 times the slowest background run alone (0.4 s). Past it the wait itself is a FAIL
# that says what it waited for, so a wait that ran out never ends green.
WAIT=${STATE_SYNC_WAIT:-120}
await() { # <what it waits for> <condition...>: 0 once the condition holds; past WAIT seconds a FAIL naming what never came, and 1
  local what=$1 end=$((SECONDS + WAIT)); shift
  until "$@"; do
    [ "$SECONDS" -lt "$end" ] || { no "waited $WAIT s for $what, which never came"; return 1; }
    sleep 0.1
  done
}
# THE LOCK IS PROBED LAST, after the sign that the run has taken and used it: the probe holds the lock for an instant, and a detached
# push that met it there would be skipped by its own `flock -n`, logging nothing - the wait would then never end (T314).
idle() { flock -n "$1/.git/tooling-state.lock" true 2>/dev/null; }  # <clone>: no run holds its lock
failed_twice() { [ "$(grep -c '"outcome": "failed' "$A/.git/tooling-state.log")" -ge 2 ] && idle "$A"; }
carried() { seen "$(rgit show 'alpha:record-checks/record-format%3A0007.json' 2>&1)" '"fa"'; }
restored() { [ -f "$F/.git/record-checks/source-reader%3A0004.json" ] && idle "$F"; }

A="$T/a/.clones/alpha"; clone "$A"
answer "$A" "quote-check%3A0001" 2026-11-20T00:00:00Z f1 PASS
answer "$A" "intro-check%3A0002" 2026-11-20T00:00:00Z f2 FAIL
lines "$A" 451-x.jsonl 1 12
echo half > "$A/.git/record-checks/quote-check%3A0001.json.tmp"
echo half > "$A/.git/l7r-events/451-x.jsonl.tmp"

echo "1. a push commits the answers and the logs to the clone's own branch"
OUT=$(run "$A" push); RC=$?
[ "$RC" = 0 ] && seen "$OUT" 'state-push: pushed' && ok "the push says pushed, exit 0" || no "the push says pushed" "rc=$RC $OUT"
[ "$(rgit show 'alpha:record-checks/quote-check%3A0001.json' 2>/dev/null)" = "$(cat "$A/.git/record-checks/quote-check%3A0001.json")" ] && ok "an answer is on the branch alpha as written" || no "an answer is on the branch alpha"
TREE=$(rgit ls-tree -r --name-only alpha 2>/dev/null)
N=$(grep -c '^l7r-events/451-x.jsonl/' <<< "$TREE")
[ "$N" = 3 ] && ok "a 480-byte log is 3 segments of at most 200 bytes" || no "the log is segmented" "$N: $TREE"
[ "$(for s in $(grep '^l7r-events/451-x.jsonl/' <<< "$TREE"); do rgit show "alpha:$s"; done)" = "$(cat "$A/.git/l7r-events/451-x.jsonl")" ] && ok "the segments in order are the log" || no "the segments in order are the log"
seen "$TREE" '\.tmp' && no "a half-written .tmp file was pushed" "$TREE" || ok "no .tmp file is pushed"
[ -d "$A/.git/tooling-state.git" ] && ! grep -q 'x-access-token\|token' "$A/.git/tooling-state.git/config" && ok "the mirror is under the common .git, no credential in its config" || no "the mirror's config"
seen "$(tail -1 "$A/.git/tooling-state.log")" '"action": "push".*"outcome": "pushed' && ok "the run is logged" || no "the run is logged" "$(tail -1 "$A/.git/tooling-state.log" 2>&1)"
[ -e "$A/.git/tooling-state.stage" ] && no "the staging copy is left on disk" || ok "the staging copy is removed"

echo "2. nothing changed: nothing pushed"
TIP=$(rgit rev-parse alpha)
OUT=$(run "$A" push)
seen "$OUT" 'state-push: unchanged' && [ "$(rgit rev-parse alpha)" = "$TIP" ] && ok "an unchanged state pushes nothing" || no "an unchanged state pushes nothing" "$OUT"

echo "3. an append changes the last segment only"
FIRST=$(rgit rev-parse 'alpha:l7r-events/451-x.jsonl/0000')
lines "$A" 451-x.jsonl 13 14
answer "$A" "intro-check%3A0002" 2026-11-21T00:00:00Z f3 PASS
OUT=$(run "$A" push)
[ "$(rgit rev-parse 'alpha:l7r-events/451-x.jsonl/0000')" = "$FIRST" ] && [ "$(rgit diff --name-only "$TIP" alpha | tr '\n' ' ')" = 'l7r-events/451-x.jsonl/0002 record-checks/intro-check%3A0002.json ' ] && ok "the push carries the last segment and the changed answer" || no "the push carries the last segment and the changed answer" "$(rgit diff --name-only "$TIP" alpha)"
rgit merge-base --is-ancestor "$TIP" alpha && ok "the branch moved forward, its history kept" || no "the branch moved forward"

echo "4. a lost container's replacement: the same clone name, restored"
B="$T/b/.clones/alpha"; clone "$B"
OUT=$(run "$B" restore); RC=$?
[ "$RC" = 0 ] && seen "$OUT" 'state-restore: .*2 answers' && ok "the restore says what it brought" || no "the restore says what it brought" "rc=$RC $OUT"
cmp -s "$A/.git/l7r-events/451-x.jsonl" "$B/.git/l7r-events/451-x.jsonl" && ok "the log is back, whole" || no "the log is back"
cmp -s "$A/.git/record-checks/intro-check%3A0002.json" "$B/.git/record-checks/intro-check%3A0002.json" && ok "the answers are back" || no "the answers are back"

echo "5. a restore never overwrites what is newer here"
answer "$B" "quote-check%3A0001" 2026-11-25T00:00:00Z f9 FAIL    # newer here than the pushed record
answer "$B" "intro-check%3A0002" 2026-11-01T00:00:00Z f0 FAIL    # older here
answer "$B" "modal-form%3A0003" 2026-11-25T00:00:00Z f5 PASS     # only here
lines "$B" 451-x.jsonl 15 15                                      # a line only here
sed -i '3d' "$B/.git/l7r-events/451-x.jsonl"                      # and a pushed line this log lacks
lines "$B" 449-y.jsonl 1 2                                        # a log only here
OUT=$(run "$B" restore)
Q=$(cat "$B/.git/record-checks/quote-check%3A0001.json")
seen "$Q" '"result": "FAIL"' && seen "$Q" '"utc": "2026-11-25' && seen "$Q" '"f1"' && seen "$Q" '"f9"' && ok "the newer local record stands, with every fingerprint either answered" || no "the newer local record stands" "$Q"
I=$(cat "$B/.git/record-checks/intro-check%3A0002.json")
seen "$I" '"result": "PASS"' && seen "$I" '"utc": "2026-11-21' && ok "an older local record takes the pushed one" || no "an older local record takes the pushed one" "$I"
[ -f "$B/.git/record-checks/modal-form%3A0003.json" ] && [ -f "$B/.git/l7r-events/449-y.jsonl" ] && ok "what is only here stays" || no "what is only here stays"
L="$B/.git/l7r-events/451-x.jsonl"
[ "$(wc -l < "$L")" = 15 ] && [ "$(sort "$L" | uniq -d | wc -l)" = 0 ] && grep -q 'made-up-line-0003' "$L" && grep -q 'made-up-line-0015' "$L" && ok "the log gains the line it lacked, keeps its own, repeats none" || no "the log merges by line" "$(wc -l < "$L")"
BEFORE=$(cat "$L" "$B"/.git/record-checks/*.json | sha256sum)
run "$B" restore >/dev/null
[ "$(cat "$L" "$B"/.git/record-checks/*.json | sha256sum)" = "$BEFORE" ] && ok "a second restore changes nothing" || no "a second restore changes nothing"

echo "6. the replacement's first push is a fast-forward of the lost container's branch"
TIP=$(rgit rev-parse alpha)
OUT=$(run "$B" push)
seen "$OUT" 'state-push: pushed' && rgit merge-base --is-ancestor "$TIP" alpha && ok "pushed on top of the old history, no force" || no "pushed on top of the old history" "$OUT"
seen "$(rgit show 'alpha:record-checks/modal-form%3A0003.json' 2>&1)" '"f5"' && ok "its new answer is on the branch" || no "its new answer is on the branch"

echo "7. two containers on one branch: the later push merges the other's state first"
answer "$A" "source-reader%3A0004" 2026-11-26T00:00:00Z f6 PASS
lines "$A" 451-x.jsonl 16 16
TIP=$(rgit rev-parse alpha)
OUT=$(run "$A" push)
seen "$OUT" 'state-push: pushed' && rgit merge-base --is-ancestor "$TIP" alpha && ok "a push the remote refused is merged and pushed, nothing forced" || no "a refused push is merged and pushed" "$OUT"
[ -f "$A/.git/record-checks/modal-form%3A0003.json" ] && seen "$(rgit show 'alpha:record-checks/source-reader%3A0004.json' 2>&1)" '"f6"' && seen "$(rgit show 'alpha:record-checks/modal-form%3A0003.json' 2>&1)" '"f5"' && ok "both containers' answers are on the branch and here" || no "both containers' answers are kept"

echo "8. a fresh clone's first push restores first, so it removes nothing from its branch"
C2="$T/c/.clones/alpha"; clone "$C2"
answer "$C2" "glyph-check%3A0005" 2026-11-26T00:00:00Z f7 PASS
OUT=$(run "$C2" push)
seen "$(rgit ls-tree -r --name-only alpha)" 'source-reader%3A0004' && seen "$(rgit ls-tree -r --name-only alpha)" 'glyph-check%3A0005' && [ -f "$C2/.git/record-checks/source-reader%3A0004.json" ] && ok "the branch keeps every answer and the clone has them" || no "a fresh clone's push keeps the branch's answers" "$OUT"

echo "9. another clone's state, by name; a name the repository does not hold"
D="$T/a/.clones/beta"; clone "$D"
OUT=$(run "$D" restore); RC=$?
[ "$RC" = 0 ] && seen "$OUT" 'holds no branch beta' && ok "no branch for this clone: said, exit 0" || no "no branch for this clone" "rc=$RC $OUT"
OUT=$(run "$D" restore alpha)
[ -f "$D/.git/record-checks/source-reader%3A0004.json" ] && [ -f "$D/.git/l7r-events/451-x.jsonl" ] && ok "restore <clone> brings another clone's state" || no "restore <clone> brings another clone's state" "$OUT"
OUT=$(run "$D" push)
[ "$(rgit rev-parse -q --verify beta)" ] && ok "and this clone pushes to its own branch" || no "this clone pushes to its own branch" "$OUT"

echo "10. a worktree pushes its clone's state, under the clone's name"
git -C "$A" worktree add -q --detach "$T/a/.clones/alpha-t9" 2>/dev/null
answer "$A" "record-format%3A0006" 2026-11-26T00:00:00Z f8 PASS
OUT=$(run "$T/a/.clones/alpha-t9" push)
seen "$(rgit show 'alpha:record-checks/record-format%3A0006.json' 2>&1)" '"f8"' && ! rgit rev-parse -q --verify alpha-t9 >/dev/null && ok "the branch is the clone's, never the worktree's" || no "the branch is the clone's" "$OUT"

echo "11. a failed push refuses nothing: one line, logged, exit 0"
answer "$A" "record-format%3A0007" 2026-11-26T00:00:00Z fa PASS
OUT=$(STATE_REMOTE="$T/gone.git" run "$A" push); RC=$?
[ "$RC" = 0 ] && [ "$(grep -c . <<< "$OUT")" = 1 ] && seen "$OUT" 'state-push: FAILED' && ok "a push that cannot reach its remote exits 0 with one line" || no "a failed push exits 0 with one line" "rc=$RC $OUT"
seen "$(tail -1 "$A/.git/tooling-state.log")" '"outcome": "failed' && ok "the failure is logged" || no "the failure is logged"
OUT=$(STATE_REMOTE="$T/gone.git" run "$A" push --detach); RC=$?
[ "$RC" = 0 ] && seen "$OUT" 'the last push FAILED' && seen "$OUT" 'in the background' && ok "a detached push returns at once and says the last one failed" || no "a detached push says the last failure" "rc=$RC $OUT"
await "the failed detached push to log its failure and free the lock" failed_twice  # or the next push is skipped by the lock
OUT=$(run "$A" push --detach)
await "the next detached push to put record-format%3A0007 on the branch alpha" carried
carried && ok "the next detached push carries what the failed one could not" || no "the next detached push carries it" "$OUT"
OUT=$(STATE_REMOTE="$T/gone.git" run "$D" restore); RC=$?
[ "$RC" = 1 ] && seen "$OUT" 'state-restore: FAILED' && ok "a restore that cannot reach its remote says so, exit 1" || no "a failed restore says so" "rc=$RC $OUT"

echo "12. no remote named and the clone is not GitHub main's: nothing is contacted"
E="$T/a/.clones/gamma"; clone "$E"
OUT=$(unset STATE_REMOTE; run "$E" push); RC=$?
[ "$RC" = 0 ] && seen "$OUT" 'skipped' && [ ! -e "$E/.git/tooling-state.git" ] && ok "a push from a clone of anything else is skipped" || no "a push from a clone of anything else is skipped" "rc=$RC $OUT"
OUT=$(unset STATE_REMOTE; run "$E" restore --if-fresh); RC=$?
[ "$RC" = 0 ] && [ ! -e "$E/.git/tooling-state.git" ] && ok "and so is a restore" || no "a restore is skipped" "rc=$RC $OUT"

echo "13. the session-clone setup: a fresh clone restores once, in the background"
F="$T/f/.clones/alpha"; clone "$F"
OUT=$(run "$F" restore --if-fresh); RC=$?
await "the background restore to bring source-reader%3A0004 and free the lock" restored
[ "$RC" = 0 ] && [ -f "$F/.git/record-checks/source-reader%3A0004.json" ] && ok "a clone with no mirror restores its branch" || no "a clone with no mirror restores" "rc=$RC $OUT"
N=$(grep -c . "$F/.git/tooling-state.log")
OUT=$(run "$F" restore --if-fresh)
[ -z "$OUT" ] && [ "$(grep -c . "$F/.git/tooling-state.log")" = "$N" ] && ok "a clone that has its mirror does not restore again" || no "a second --if-fresh does nothing" "$OUT"

echo "14. a log file past the segment size's ceiling for one file is never one blob"
BIG=$(rgit ls-tree -r -l alpha | awk '$4 > 200 && $5 ~ /^l7r-events/' | wc -l)
[ "$BIG" = 0 ] && ok "no log segment on the branch is over the segment size" || no "a log segment is over the segment size" "$BIG"

echo "15. the landings run it, and their exit is their own"
MK=$(cat "$REPO/Makefile")
seen "$(grep -A8 '^land:  ' <<< "$MK")" 'state-sync.sh" push --detach' && seen "$(grep -A3 '^land-tooling:' <<< "$MK")" 'state-sync.sh" push --detach' && ok "make land and make land-tooling push the state after their own push" || no "make land and make land-tooling push the state"
seen "$(grep -A3 '^state-restore:' <<< "$MK")" 'state-sync.sh" restore' && ok "make state-restore restores" || no "make state-restore restores"
seen "$(cat "$REPO/scripts/sync-with-main.sh")" 'state-sync.sh" restore --if-fresh' && ok "sync-in restores a fresh clone" || no "sync-in restores a fresh clone"

echo "16. a wait on a background run ends on its condition, and one that never comes says what it waited for"
echo x > "$T/late"; ( sleep 0.3; rm "$T/late" ) &
OUT=$(await "the file to go" test ! -e "$T/late"); RC=$?
[ "$RC" = 0 ] && [ -z "$OUT" ] && [ ! -e "$T/late" ] && ok "a condition that comes late is waited for, nothing said" || no "a late condition is waited for" "rc=$RC $OUT"
OUT=$(WAIT=0 await "a file nobody writes" test -e "$T/never"); RC=$?
[ "$RC" = 1 ] && seen "$OUT" 'FAIL    waited 0 s for a file nobody writes, which never came' && ok "a condition that never comes ends the wait as a FAIL, saying what it waited for" || no "a wait that runs out says what it waited for" "rc=$RC $OUT"

echo
echo "state-sync: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
