#!/usr/bin/env bash
# test-pool-idle-hooks.sh - prove pool-idle-hooks still bites (feature 451 T313): the coordinating session's Stop over a free pool
# tree and a READY queue entry that overlaps nothing in flight is blocked, naming the tree, the task and the one command; a builder
# or any subagent, a clone with no pool, the settled count reached, a queue whose open entries wait or run alone, an overlapping
# entry, a malformed queue and the escape with its reason pass. Red when the guard's block is removed: every expect_block then
# finds no decision.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/pool-idle-hooks.sh"
pass=0 fail=0
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
export GUARD_LOG_DIR="$W/log" HOME="$W/h"
C="$W/c"
mkdir -p "$C/.git" "$C/specs/451-x" "$W/c-b1" "$W/h"
git -C "$C" init -q
export POOL_IDLE_ROOT="$C"
printf -- '- [x] T1 landed\n- [ ] T3 open\n- [ ] T4 open\n- [ ] T5 open\n' > "$C/specs/451-x/tasks.md"

pool() {  # pool <tasks json of the first tree> : the first tree held by them (or free), the second free
  printf '{"trees": [{"tree": "%s", "feature": "451", "tasks": %s, "since": ""}, {"tree": "%s", "feature": "", "tasks": [], "since": ""}]}\n' \
    "$W/c-b0" "$1" "$W/c-b1" > "$C/.git/builder-pool.json"
}
queue() { printf '%b' "$1" > "$C/specs/451-x/queue.txt"; }
run() {  # run <final message> [extra json fields] -> sets RC and OUT
  OUT=$(jq -nc --arg m "$1" --argjson x "${2:-{\}}" '{hook_event_name: "Stop", last_assistant_message: $m} + $x' | "$HOOK" stop 2>&1)
  RC=$?
}
expect_block() {  # <what the case is> <words the block holds> [message]
  run "${3:-The builders are running.}"
  if grep -qF -- '"decision":"block"' <<< "$OUT" && grep -qF -- "$2" <<< "$OUT"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected BLOCK naming '$2' ($1), got rc=$RC: $OUT"; fi
}
expect_allow() {  # <what the case is> [message] [extra json fields]
  run "${2:-The builders are running.}" "${3:-{\}}"
  if [ "$RC" -eq 0 ] && [ -z "$OUT" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: expected ALLOW ($1), got rc=$RC: $OUT"; fi
}

# --- blocked: a free tree, one tree held (under the count of 3), a READY entry that overlaps nothing in flight
pool '["T5"]'
queue 'T5 fix crates=rust/guard files=-\nT3 fix files=rust/guard/src/lib.rs\nT4 fix jobs=2 crates=rust/gate/crates/task files=Makefile\n'
expect_block 'the tree, the task and the command' "$W/c-b1 is free and 451 T4 is READY"
expect_block 'the one command' 'make builder-brief T=T4 F=451 KIND=fix JOBS=2 CRATE=\"rust/gate/crates/task\"'
expect_block 'the escape named' 'POOL_IDLE_OK: <why not, two words or more>'
# nothing held: the first READY entry
pool '[]'
expect_block 'nothing in flight' '451 T5 is READY'
pool '["T5"]'
# the escape with no reason, and a mention of it in a sentence, do not pass
expect_block 'the escape bare' 'POOL_IDLE_OK with no reason' 'POOL_IDLE_OK: ok'
expect_block 'a mention is no escape' '451 T4 is READY' 'I could write POOL_IDLE_OK: but the tree is simply free'
# the token STARTS its line, and the block says so: after a bullet or in backticks it is not taken
expect_block 'the block says where the token goes' 'Or start a line of your final message with: POOL_IDLE_OK: '
expect_block 'a bulleted token is no escape' '451 T4 is READY' $'Stopping.\n- POOL_IDLE_OK: the next entries wait on the GM'
expect_block 'a backticked token is no escape' '451 T4 is READY' '`POOL_IDLE_OK: the next entries wait on the GM`'
expect_block 'the bare escape says where it goes' 'Start a line with: POOL_IDLE_OK: <why the free tree stays free, two words or more>' 'POOL_IDLE_OK:'

# --- allowed: the escape on a line of the final message, with its reason (recorded)
expect_allow 'the escape' $'Stopping for now.\nPOOL_IDLE_OK: the next entries wait on the GM'
grep -rqs '"rule": *"POOL_IDLE_OK"' "$W/log" && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: the escape's use is not in the guard log"; }
# --- allowed: a builder or any subagent
expect_allow 'a subagent' 'done' '{"agent_id": "a1b2"}'
# --- allowed: the settled count reached
L7R_BUILDERS=1 expect_allow 'the count reached'
# --- allowed: every READY entry overlaps the task in flight, waits, or runs alone while a tree is held
queue 'T5 fix crates=rust/guard files=-\nT3 fix files=rust/guard/src/lib.rs\n'
expect_allow 'the READY entry overlaps the task in flight'
queue 'T5 fix crates=rust/guard files=-\nT3 fix files=docs/a.md waits=GM\nT4 fix files=docs/b.md waits=T3\n'
expect_allow 'the open entries wait on the GM and on a task'
queue 'T5 fix crates=rust/guard files=-\nT3 fix files=docs/a.md waits=alone\n'
expect_allow 'the only READY entry runs alone and a tree is held'
queue 'T1 fix files=-\n'
expect_allow 'every entry landed'
# a task whose box the tick archived to tasks-done.md is landed too, and a wait on it is over
printf -- '- [x] T9 archived\n' > "$C/specs/451-x/tasks-done.md"
queue 'T9 fix files=-\n'
expect_allow 'the one entry is archived as landed'
queue 'T9 fix files=-\nT3 fix files=docs/a.md waits=T9\n'
expect_block 'a wait on an archived task is over' '451 T3 is READY'
# --- allowed: no free tree; a clone with no pool; a queue that cannot be read; no queue
queue 'T3 fix files=docs/a.md\n'
printf '{"trees": [{"tree": "%s", "feature": "451", "tasks": ["T5"], "since": ""}]}\n' "$W/c-b0" > "$C/.git/builder-pool.json"
expect_allow 'no free tree'
rm "$C/.git/builder-pool.json"
expect_allow 'no pool: not a coordinator'
pool '["T5"]'
queue 'T3 mend files=docs/a.md\n'
expect_allow 'a malformed line holds nobody'
grep -rqs 'queue-unread' "$W/log" && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: the unread queue is not in the guard log"; }
# another feature's file of the same name that is no builders' queue (a page session's queue.txt, as features 269 and 280 hold)
# hides nothing: the readable queue's READY entry is still reached, and with none to hand out the Stop passes
mkdir -p "$C/specs/269-pages"; printf '/c/briefs/h1-write.md then:/c/briefs/h1-checks.sh\n' > "$C/specs/269-pages/queue.txt"
queue 'T3 fix files=docs/a.md\n'
expect_block "another feature's queue.txt of another form hides nothing" '451 T3 is READY'
queue 'T3 fix files=docs/a.md waits=GM\n'
expect_allow "another feature's queue.txt of another form holds nobody"
rm -r "$C/specs/269-pages"
# --- 451 T313's round-3 ruling (T421): an open performance task of a started feature with no queue line is named FIRST, with the
# command that writes its line, though nothing is READY; its line with waits= quiets it
printf -- '- [ ] T3 open\n- [ ] T6 [perf] the faster gate\n' > "$C/specs/451-x/tasks.md"
printf '{"feature": "451-x", "task": "T3", "utc": "2026-11-27T01:00:00Z"}\n' > "$C/.git/task-starts.jsonl"
expect_block 'an unlisted performance task is named first' 'FIRST, 451 T6 is open performance work with no queue line'
expect_block 'with the command that writes its line' 'make queue-add F=451 T=T6 KIND=fix'
queue 'T3 fix files=docs/a.md waits=GM\nT6 fix files=- waits=GM\n'
expect_allow 'its line with waits= quiets it'
rm "$C/.git/task-starts.jsonl"
# --- 451 T481: a READY fix entry whose task line names a new mechanism is a command make builder-brief refuses: the block says
# make queue's flag under it, with the build-half command
printf -- '- [ ] T3 a new guard over the queue\n' > "$C/specs/451-x/tasks.md"
queue 'T3 fix files=docs/a.md\n'
expect_block 'a refused fix command is flagged' "FLAG: T3 (line 1) is typed fix, but T3's line names a new mechanism"
expect_block 'with the build-half command' 'make builder-brief T=T3 F=451 KIND=build-half ENTRY=1'
rm "$C/specs/451-x/queue.txt"
expect_allow 'no queue'
printf '{}' | "$HOOK" stop >/dev/null 2>&1
[ $? -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: empty input should be a no-op"; }

echo "test-pool-idle-hooks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
