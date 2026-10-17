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
# THE RUN ENDS WHEN ITS WRITER DOES, not at the first verdict-shaped line: the gate's preflight prints its own `make quick`
# verdict ("verification-state: green-local (quick)") long before the gate's, and a wait on that line ended mid-gate
# (feature 385, the first run of this script). So wait until nothing holds the log open, then read the whole log.
deadline=$(( $(date +%s) + ${VERIFY_WAIT_S:-5400} ))
while [ -n "$(fuser "$log" 2>/dev/null)" ]; do
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "verify-wait: WAIT TIMED OUT on $log"
    exit 4
  fi
  sleep "${VERIFY_WAIT_STEP_S:-15}"
done
tail -4 "$log"
if grep -qE 'GATE FAILED|GATE NOT GREEN' "$log"; then exit 1; fi
if grep -qE 'gate green' "$log"; then exit 0; fi
echo "verify-wait: the gate writing $log ended with no verdict - it died (an OOM kill?); read the log's tail"
exit 5
