#!/usr/bin/env bash
# _writer-alive.sh <path> [stale-seconds] - IS THE PROCESS THAT WRITES <path> STILL THERE?
#
# GUARD_EDIT_OK: new file, feature 227 - the proof-of-life half of a wait on a detached run.
#
# WHY THIS EXISTS (GM 2026-09-12, after a 51-minute stall): a session detached `make placement-stages`,
# waited on its log with `until grep -qE "^wrote |Error|Traceback" $S/out.log; do sleep 15; done`, and sat
# there for 51 minutes on a command that had finished its work at 15:16:18 and was then killed before it
# could flush stdout. Killed by the KERNEL'S OOM KILLER, which has fired 36 times in this container
# (`oom_kill 36` in /proc/vmstat) - so yes, a `make` run here does get killed, and the harness also reaps
# background tasks under memory pressure. The pattern the loop waited for was never going to appear.
#
# The GM's ruling is the general one this project already works by: *"if you are waiting on output to appear
# somewhere, but not checking to see whether the process that is supposed to generate that output is still
# alive, then when possible, the hook should add the second proof of life check to what is being waited
# for"* - and *"simply telling you to set a watch properly next time is bad engineering practice because
# that's just another version of making you remember to do something."* So `no-poll-hooks.sh` ADDS a call to
# this script to every file-watching wait that does not already carry one, and this script is the answer to
# "is anything still writing that file?".
#
# WHY IT ASKS THE FILE AND NOT A PROCESS PATTERN. A pattern is what the 2026-07-25 incident was about: a
# literal `pgrep -f "make done"` matches the searching shell itself and can never report "gone". The file
# being waited on has no such problem - it names exactly one thing, the hook already knows it (it is the
# operand in the condition), and `fuser` answers from the kernel's own open-file table.
#
# THREE ANSWERS, and only the last one is death:
#   - the file does not exist yet      -> ALIVE. The producer is starting; nothing can be concluded.
#   - some process holds it open       -> ALIVE. A detached `cmd > log` holds that descriptor for its
#                                        whole run, which is what every detached run in this repository
#                                        looks like, so this is the branch that normally answers.
#   - written within <stale-seconds>   -> ALIVE. The belt for a producer that opens and closes per write
#                                        (`cmd1 > log; cmd2 >> log`), where `fuser` can find nothing
#                                        during the gap between the two.
#   - otherwise                        -> DEAD, and it says so on stdout, because the session is about to
#                                        read a log that stops in the middle and should be told why.
#
# The failure direction is deliberate: a wrong answer here ends a wait early and the session reads a
# truncated log, which it can see. The failure it replaces was a wait that never ended at all.
#
# Tested by test-no-poll-hooks.sh section 6 (it is the hook's own rewrite target, so the hook's suite owns it).
set -uo pipefail

P=${1:-}
STALE=${2:-45}

[ -n "$P" ] || exit 0                      # nothing named: no claim either way
[ -e "$P" ] || exit 0                      # not created yet: the producer is still starting
fuser -s "$P" 2>/dev/null && exit 0        # a live process holds the descriptor

NOW=$(date +%s)
MTIME=$(stat -c %Y "$P" 2>/dev/null || echo "$NOW")
if [ $((NOW - MTIME)) -lt "$STALE" ]; then
  exit 0
fi

echo "writer-alive: nothing holds $P open and it has not been written for $((NOW - MTIME))s - the run that was producing it is gone (a killed or OOM'd detached run looks exactly like this). Read what the log DOES have; the thing you were waiting for may never have been printed."
exit 1
