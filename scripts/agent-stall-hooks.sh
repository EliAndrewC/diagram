#!/usr/bin/env bash
# agent-stall-hooks.sh - a background subagent that has silently stalled is REPORTED, never assumed running.
# (GUARD_EDIT_OK: a NEW guard, feature 143 - the GM 2026-08-28: "build that so that future sessions,
# including yourself and anyone else that might run into this, will not get stuck in the way that you
# have repeatedly gotten stuck")
#
# THE FAILURE (2026-08-28, feature 143): a `source-reader` agent launched at 02:31Z hit a bad TLS
# certificate on a Chinese host at 02:35Z and never produced another record - and the harness sent NO
# completion notification. Its sibling agents finished in ~7 minutes each. The parent session assumed
# it was still running for TEN HOURS, until the GM asked. A relaunch stalled the same way 13 minutes in.
# The session's next move - foreground WebFetch batches - was worse: one hung fetch blocked the whole
# turn and the GM's message queued for an hour behind it.
#
# THE SHAPE OF A STALL: a subagent transcript (~/.claude/projects/<proj>/<session>/subagents/agent-<id>.jsonl)
# whose LAST record is a `user` record (a tool_result waiting for the assistant's next turn) and whose
# mtime has not moved for STALE seconds. A finished agent ends on an `assistant` record. Nothing else
# distinguishes the two - the harness gives no liveness signal (research note in specs/143 ledger).
#
# Modes:
#   prompt                  (UserPromptSubmit hook) one-shot: list the session's stalled agents on stdout
#                           so the next prompt opens with them. Silent when there are none.
#   check <subagents-dir>   one-shot report for any directory (the test uses this).
#   watch <subagents-dir>   the loop for a `Monitor`: one line per stall, once per stall (POLL_OK - the
#                           harness does not notify on a stall; this watches EXTERNAL state).
#   pending <subagents-dir> one bare agent id per line for every agent still awaiting a reply (feature 149's
#                           pairing guard: has the settlement-review it launched finished?).
#   ack <subagents-dir> <id> the session has handled this stall (TaskStop + relaunch): never report it
#                           again (a stopped agent's transcript still ends on a tool_result).
# Env: AGENT_STALE_S (default 300); AGENT_RECENT_S (default 172800 - older transcripts are ignored).
set -u
MODE=${1:-}
STALE=${AGENT_STALE_S:-300}
RECENT=${AGENT_RECENT_S:-172800}

last_type() { # the `type` of the last JSON record of a transcript, or ''
  tail -n 1 "$1" 2>/dev/null | python3 -c '
import json,sys
try: print(json.loads(sys.stdin.read()).get("type",""))
except Exception: print("")'
}

report() { # report <dir> [seen-file] -> prints "STALLED <id> <age>s" per stalled transcript (once, if seen-file)
  local dir=$1 seen=${2:-} now f id age t
  [ -d "$dir" ] || return 0
  now=$(date +%s)
  for f in "$dir"/agent-*.jsonl; do
    [ -f "$f" ] || continue
    age=$(( now - $(stat -c %Y "$f") ))
    [ "$age" -gt "$RECENT" ] && continue
    id=$(basename "$f" .jsonl); id=${id#agent-}
    [ -e "$dir/../stall-ack/$id" ] && continue
    if [ "$age" -ge "$STALE" ]; then
      t=$(last_type "$f")
      if [ "$t" = "user" ]; then
        if [ -n "$seen" ] && grep -qx "$id" "$seen" 2>/dev/null; then continue; fi
        [ -n "$seen" ] && echo "$id" >> "$seen"
        printf 'STALLED %s: transcript unchanged for %ss, last record a tool_result with no reply - stop it (TaskStop) and relaunch its batch, or read the rest yourself in a NEW background agent; never in a foreground WebFetch batch; then `agent-stall-hooks.sh ack <dir> <id>`\n' "$id" "$age"
      fi
    elif [ -n "$seen" ]; then
      grep -qx "$id" "$seen" 2>/dev/null && sed -i "/^$id\$/d" "$seen"
    fi
  done
}

case "$MODE" in
  prompt)
    INPUT=$(cat 2>/dev/null || true)
    TP=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("transcript_path",""))
except Exception: print("")')
    [ -n "$TP" ] || exit 0
    DIR="${TP%.jsonl}/subagents"
    out=$(report "$DIR")
    if [ -n "$out" ]; then
      printf 'agent-stall: %s\n' "$out"
      printf 'agent-stall: a stalled reader is not "still running" - act on it now (scripts/agent-stall-hooks.sh).\n'
    fi
    exit 0 ;;
  check)
    report "${2:?subagents dir}"; exit 0 ;;
  pending)
    # `pending <dir>` -> one bare agent id per line, for every transcript still awaiting a reply
    # (last record a tool_result), stalled or not. Feature 149's pairing guard asks whether a
    # settlement-review it launched has finished; that is the SAME determination `report` makes on
    # the stall side, so it is answered here rather than kept as a second copy of the rule.
    for f in "${2:?subagents dir}"/agent-*.jsonl; do
      [ -f "$f" ] || continue
      [ "$(last_type "$f")" = "user" ] || continue
      id=$(basename "$f" .jsonl); echo "${id#agent-}"
    done
    exit 0 ;;
  ack)
    mkdir -p "${2:?subagents dir}/../stall-ack" && touch "$2/../stall-ack/${3:?agent id}"; exit 0 ;;
  watch)
    DIR=${2:?subagents dir}; SEEN=$(mktemp); trap 'rm -f "$SEEN"' EXIT
    while true; do report "$DIR" "$SEEN"; sleep "${AGENT_TICK_S:-30}"; done ;;
  *)
    echo "usage: $0 prompt|check <dir>|watch <dir>" >&2; exit 2 ;;
esac
