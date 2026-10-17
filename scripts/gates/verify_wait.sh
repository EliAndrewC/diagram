#!/usr/bin/env bash
# verify_wait.sh - wait for the gate `make verify` started to end, reading ITS OWN log, and print its verdict.
#
# `make verify` starts its gate detached, so the harness tracks no run and nothing wakes the session when it ends. Its log
# was one file every run appended to, so a wait could match an EARLIER run's verdict line (the round arbiter's tooling fix on
# hour:385-approach-checklist@3: a stale match, two no-poll refusals and a POLL_OK override in one hour). Now each run writes
# `.git/verify-gate-<epoch>.log` and `.git/verify-gate.log` links to the newest; this script resolves the link ONCE, at its
# start, and waits on that file alone. Run it with run_in_background: its exit is the notification.
#
# Exit 0 green, 1 red or not green, 3 no gate log, 4 timed out (90 min), 5 the gate's writer is gone with no verdict.
set -uo pipefail
root=$(git rev-parse --show-toplevel)
link="$root/.git/verify-gate.log"
log=$(readlink -f "$link" 2>/dev/null || true)
if [ -z "$log" ] || [ ! -f "$log" ]; then
  echo "verify-wait: no gate log at $link - start one with make verify"
  exit 3
fi
verdict='verification-state|GATE FAILED|GATE NOT GREEN|gate green'
deadline=$(( $(date +%s) + ${VERIFY_WAIT_S:-5400} ))
while ! grep -qE "$verdict" "$log"; do
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "verify-wait: WAIT TIMED OUT on $log"
    exit 4
  fi
  if [ -z "$(fuser "$log" 2>/dev/null)" ] && [ -n "${VERIFY_WAIT_STRICT:-1}" ] && ! grep -qE "$verdict" "$log"; then
    # ...the gate's writer is gone and no verdict line came: the run died (an OOM kill), the log is truncated, not finished
    sleep 2
    grep -qE "$verdict" "$log" || { echo "verify-wait: the gate writing $log is gone with no verdict - it died; read the log's tail"; tail -5 "$log"; exit 5; }
  fi
  sleep "${VERIFY_WAIT_STEP_S:-15}"
done
tail -4 "$log"
grep -qE 'GATE FAILED|GATE NOT GREEN' "$log" && exit 1
exit 0
