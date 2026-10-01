#!/usr/bin/env bash
# test-stall-watchdog-hooks.sh - prove the stall watchdog marks, rings and nudges exactly what it should (feature 295 item 4).
# (GUARD_EDIT_OK: the companion of a NEW guard, feature 295.)
#
# Every session here is a REAL live process (a `sleep`) with a registry file, a transcript whose age is set, and a clone
# that is a real git repository beside a real mirror; tmux is a stand-in that answers `display` and `capture-pane` from
# files and records `send-keys`. One fixture per branch of spec SC-004, and one per exemption of FR-005a.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/stall-watchdog-hooks.sh"
PASS=0; FAIL=0
T=$(mktemp -d)
PIDS=()
# every stand-in is started with its descriptors on /dev/null, and its children are ended with it, so none outlives the
# suite holding a caller's pipe open (the first run hung on a `sleep` left behind by a killed `bash -c`)
cleanup() { for p in "${PIDS[@]}"; do pkill -P "$p" 2>/dev/null; kill "$p" 2>/dev/null; done; rm -rf "$T"; }
trap cleanup EXIT
export GUARD_LOG_DIR="$T/guard-log" STALL_SESSIONS_DIR="$T/sessions" STALL_PROJECTS_DIR="$T/projects" \
       STALL_STATE_DIR="$T/state" STALL_CLONES_MAP="$T/map" STALL_MIRROR="$T/mirror" STALL_TMUX="$T/tmux"
mkdir -p "$T/sessions" "$T/projects/p" "$T/map" "$T/state"
check() { if [ "$2" = "$3" ]; then printf 'ok    %s\n' "$1"; PASS=$((PASS+1));
          else printf 'FAIL  %s (expected %s, got %s)\n' "$1" "$2" "$3"; FAIL=$((FAIL+1)); fi; }
has() { case "$1" in *"$2"*) echo yes ;; *) echo no ;; esac; }

# the stand-in tmux: a pane's tty is a file, its screen a file, every send-keys a line
cat > "$T/tmux" <<EOF
#!/usr/bin/env bash
case "\$1" in
  display) touch "$T/tty-\$4"; echo "$T/tty-\$4" ;;
  capture-pane) cat "$T/screen-\$4" 2>/dev/null ;;
  send-keys) echo "\$*" >> "$T/sent" ;;
esac
EOF
chmod +x "$T/tmux"
screen() { printf 'some output\n────────────────────\n%s\n────────────────────\n  status line\n' "$2" > "$T/screen-$1"; }

git init -q -b main "$T/mirror" && git -C "$T/mirror" -c user.email=t@t -c user.name=t commit -q --allow-empty -m one
for c in dirty clean lone; do git clone -q "$T/mirror" "$T/$c" 2>/dev/null; done
touch "$T/dirty/work.txt" "$T/lone/work.txt"

# session <sid> <kind> <status> <clone> <pane|-> <transcript age> [extra json] [env for the process]
session() {
  local sid=$1 kind=$2 status=$3 clone=$4 pane=$5 age=$6 extra=${7:-} envs=${8:-}
  env $envs sleep 600 </dev/null >/dev/null 2>&1 & local pid=$!; PIDS+=("$pid")
  local tm=""; [ "$pane" != - ] && tm=",\"tmux\":\"@1.$pane\""
  printf '{"pid":%s,"sessionId":"%s","name":"%s","kind":"%s","status":"%s","cwd":"%s"%s%s}' \
    "$pid" "$sid" "name-$sid" "$kind" "$status" "$T/$clone" "$tm" "$extra" > "$T/sessions/$pid.json"
  printf '%s' "$T/$clone" > "$T/map/$sid"
  printf '{"type":"assistant","message":{"content":[{"type":"text","text":"done for now"}]}}\n' > "$T/projects/p/$sid.jsonl"
  touch -d "$age" "$T/projects/p/$sid.jsonl"
}

session own      interactive idle dirty %1 "2 hours ago";  screen %1 "❯ "
session typed    interactive idle dirty %4 "2 hours ago";  screen %4 "❯ half a sentence the GM is typing"
session disp     interactive idle dirty %2 "1 minute ago";  screen %2 "❯ "   # empty, so only the own-pane rule keeps the nudge out
session headless interactive idle dirty -  "2 hours ago" "" "L7R_DISPATCHER=disp"
session parker   interactive idle dirty %3 "1 minute ago" ',"parkedJobId":"job-9"';  screen %3 "❯ "
session bgjob    bg          idle dirty -  "2 hours ago" ',"jobId":"job-9"'
session orphan   interactive idle lone  -  "2 hours ago"
session tidy     interactive idle clean %5 "2 hours ago"
session asked    interactive waiting dirty %6 "2 hours ago"
session question interactive idle dirty %7 "2 hours ago"
printf '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"AskUserQuestion","input":{}}]}}\n' > "$T/projects/p/question.jsonl"
touch -d "2 hours ago" "$T/projects/p/question.jsonl"
session recent   interactive idle dirty %8 "10 minutes ago"

echo "--- 1. one pass: what is marked, where, and what is nudged (SC-004) ---"
OUT=$("$HOOK" once)
check "the stalled session is marked in its OWN pane" yes "$(has "$OUT" 'stalled name-own (own) idle 120 min, uncommitted changes')"
check "...its tab retitled, with the bell" yes "$(grep -q $'STALLED 2h00m - name-own\007\a' "$T/tty-%1" && echo yes || echo no)"
check "...and nudged, because its input line is empty" yes "$(has "$(cat "$T/sent")" '-t %1 -l watchdog (feature 295): this session has been idle 120 min')"
check "...and Enter pressed after the text" yes "$(has "$(cat "$T/sent")" 'send-keys -t %1 Enter')"
check "a stalled session whose input line holds text is marked but NOT nudged" "yes no" \
  "$(has "$OUT" 'stalled name-typed') $(has "$(cat "$T/sent")" '-t %4')"
check "a headless session is marked on its DISPATCHER's tab" yes "$(grep -q 'STALLED 2h00m - name-headless' "$T/tty-%2" && echo yes || echo no)"
check "...never nudged there (the GM approved its own pane only)" no "$(has "$(cat "$T/sent")" '-t %2')"
check "...and its log line gives the command that resumes it" yes "$(has "$OUT" 'marked %2 (host); resume: cd ')"
check "a bg job is marked on the tab that parked it, not nudged" "yes no" \
  "$(grep -q 'name-bgjob' "$T/tty-%3" 2>/dev/null && echo yes || echo no) $(has "$(cat "$T/sent")" '-t %3')"
check "a paneless session with no host: logged only" yes "$(has "$OUT" 'stalled name-orphan (orphan) idle 120 min, uncommitted changes in '"$T"'/lone; no tab, logged only')"
check "a clean clone is not a stall" no "$(has "$OUT" name-tidy)"
check "a session waiting on the GM (status) is not a stall" no "$(has "$OUT" name-asked)"
check "a pending AskUserQuestion is not a stall" no "$(has "$OUT" name-question)"
check "ten minutes of quiet is not a stall" no "$(has "$OUT" name-recent)"
check "the active dispatcher and parker are not stalls" "no no" "$(has "$OUT" 'stalled name-disp') $(has "$OUT" 'stalled name-parker')"
check "every action is a line in the watchdog's log" 5 "$(wc -l < "$T/state/log")"

echo "--- 2. once per stall: a second pass rings and nudges nothing more; new activity is a new stall ---"
: > "$T/sent"; : > "$T/tty-%1"
"$HOOK" once >/dev/null
check "the second pass re-titles (the idle time moves)" yes "$(grep -q 'STALLED 2h00m - name-own' "$T/tty-%1" && echo yes || echo no)"
check "...without the bell (a BEL after the title's own terminating BEL)" no "$(grep -q $'\a\a' "$T/tty-%1" && echo yes || echo no)"
check "...and without a second nudge" "" "$(cat "$T/sent")"
touch -d "70 minutes ago" "$T/projects/p/own.jsonl"
"$HOOK" once >/dev/null
check "activity since, then quiet again: a new stall, nudged again" yes "$(has "$(cat "$T/sent")" '-t %1 -l watchdog')"

echo "--- 3. a page-session queue in its usage-limit retry wait (FR-005a; plan review round 1) ---"
mkdir -p "$T/lone/.git/page-sessions"
RL="$T/lone/.git/page-sessions/run-abc.log"
printf 'started orphan x.md\nfailed orphan rc=1 - waiting 15 min (reset in 40), then resuming it (limit)\n' > "$RL"
check "a retry line with NO live runner exempts nothing" yes "$(has "$("$HOOK" once)" 'stalled name-orphan')"
bash -c 'sleep 600; :' _page_session_runner.py --work "$RL" </dev/null >/dev/null 2>&1 & PIDS+=("$!")
sleep 0.5
check "a live runner and a current retry line: the queue's session is not a stall" no "$(has "$("$HOOK" once)" 'stalled name-orphan')"
touch -d "30 minutes ago" "$RL"
check "...a retry line older than its wait plus five minutes exempts nothing" yes "$(has "$("$HOOK" once)" 'stalled name-orphan')"
sed -i 's/^started orphan/started someone-else/' "$RL"
touch "$RL"
check "...nor does another session's queue in the same clone" yes "$(has "$("$HOOK" once)" 'stalled name-orphan')"

echo "--- 4. the loop: one instance, revived by any prompt ---"
export STALL_PERIOD=3600
printf '{}' | "$HOOK" prompt; sleep 1
P1=$(cat "$T/state/pid" 2>/dev/null)
check "the first prompt starts the loop" yes "$([ -n "$P1" ] && kill -0 "$P1" 2>/dev/null && echo yes || echo no)"
printf '{}' | "$HOOK" prompt; sleep 1
check "a second prompt starts no other" "$P1" "$(cat "$T/state/pid")"
"$HOOK" run </dev/null >/dev/null 2>&1 & R2=$!; sleep 1
check "a second loop started by hand exits at once on the lock" no "$(kill -0 "$R2" 2>/dev/null && echo yes || echo no)"
pkill -P "$P1" 2>/dev/null; kill "$P1" 2>/dev/null; sleep 1
printf '{}' | "$HOOK" prompt; sleep 1
P3=$(cat "$T/state/pid")
check "a dead loop is revived by the next prompt" yes "$([ "$P3" != "$P1" ] && kill -0 "$P3" 2>/dev/null && echo yes || echo no)"
pkill -P "$P3" 2>/dev/null; kill "$P3" 2>/dev/null

echo
echo "test-stall-watchdog-hooks: passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
