#!/usr/bin/env bash
# writer-alive.sh <path> [stale-seconds] - IS THE PROCESS THAT WRITES <path> STILL THERE?
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
# operand in the condition), and the kernel's own open-file table (`/proc/<pid>/fd`, each descriptor's
# access mode in its `fdinfo`) answers who holds it.
#
# THE ANSWERS, and only the last one is death:
#   - the file does not exist yet      -> ALIVE. The producer is starting; nothing can be concluded.
#   - a process holds it for WRITING   -> ALIVE. A detached `cmd > log` holds that descriptor for its
#                                        whole run, which is what every detached run in this repository
#                                        looks like, so this is the branch that normally answers. A
#                                        descriptor held only for reading is no producer (451 T61, below).
#   - written within <stale-seconds>   -> ALIVE. The belt for a producer that opens and closes per write
#                                        (`cmd1 > log; cmd2 >> log`), where no descriptor is held during
#                                        the gap between the two.
#   - a live process writes it         -> ALIVE (451 T61). The run that appends between its steps, quiet
#                                        far past the belt: its own process, asked by pid, writes the file
#                                        on its command line or in its script (see the last branch below).
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
# a live process holds a descriptor on it OPEN FOR WRITING (451 T61). `fuser -s` counted any holder, and a reader holds one too:
# the Monitor tool's `tail -f f | grep` keeps f open read-only for as long as it watches (measured 2026-11-21: `fuser -s f` exited 0
# over `tail -f f | grep X`, f two hours unwritten), so a dead run's wait under a Monitor was held to its 90-minute ceiling. Each
# descriptor that resolves to the file is read for its access mode, the low two bits of fdinfo's octal `flags` (O_WRONLY 1, O_RDWR 2).
REAL_P=$(realpath -m -- "$P" 2>/dev/null || printf '%s' "$P")
while IFS= read -r FD; do
  FLAGS=$(sed -n 's/^flags:[[:space:]]*//p' "${FD%/fd/*}/fdinfo/${FD##*/}" 2>/dev/null)
  [ -n "$FLAGS" ] && (( 8#$FLAGS & 3 )) && exit 0
done < <(find /proc/[0-9]*/fd -maxdepth 1 -type l -printf '%p\t%l\n' 2>/dev/null | awk -F'\t' -v f="$REAL_P" '$2 == f { print $1 }')

NOW=$(date +%s)
MTIME=$(stat -c %Y "$P" 2>/dev/null || echo "$NOW")
if [ $((NOW - MTIME)) -lt "$STALE" ]; then
  exit 0
fi

# A QUIET FILE OVER A LIVE RUN (feature 451 T61): a run that appends a line between its steps (`for c in a b; do make $c > $c.log;
# echo "$c rc=$?" >> sum.txt; done`) holds the summary open only for each echo, so between steps nothing holds it and it ages past
# the belt while the run goes on. Read alone, that was death: T55's builder's `until grep -q ^total seq.times` ended at 55 s, exit
# 3, while its run ran, and 8 of the 11 firings whose wait's output was still on disk (2026-11-17 to 21) were followed by a write to
# the file. So the last question is the run's own process, asked of the kernel by pid (`l7r-guard --finished-run alive`, the /proc
# walk of rust/guard/src/guards/finished_run_hooks/runs.rs): is a live process - not this wait's own ancestry, not a waiter - WRITING
# the file (a `>`, `>>` or `tee` into it) on its command line or in the script it runs? Naming it is not enough: a reader names it
# too, inside the harness's `bash -c` wrapper (a Monitor's `tail -f f | grep`, a file-test wait `until [ -s f ]`). Only its printed
# `alive` line is life: any other answer (no binary built yet, an older one without the verb) leaves the answer this script always gave.
HERE=${BASH_SOURCE[0]%/*}
[ "$HERE" = "${BASH_SOURCE[0]}" ] && HERE=.
# the wrapper finds its built binary under HOME, which a suite's part moves (tests/hooks/parts.sh): asked under a moved HOME it had
# none and the run read as gone (measured 2026-11-21, tests/hooks/test-no-poll-hooks.sh run alone: both new alive cases of 6b red
# with the verb built and answering `alive` outside the suite) -
# so the real home, from the password database, as tests/hooks/guard-shim.sh pins it
REAL=$(getent passwd "$(id -u)" | cut -d: -f6)
# and the wrapper by its directory's clean path: it names its tree, its cargo target and its sources from the path it was called by,
# and called as `.../lib/../l7r-guard.sh` it took `..` for the tree's name - its target ~/.cache itself, its sources a path that does
# not exist - so the binary it built there once was never rebuilt (measured 2026-11-21: ~/.cache/l7r-guard.good, built 03:56, still
# answered `names it` after the walk's source said `writes it`, and 1 GB of cargo output sat in ~/.cache/tool)
HOOKS=$(cd "$HERE/.." 2>/dev/null && pwd)
RUN=$(HOME=${REAL:-$HOME} "$HOOKS/l7r-guard.sh" --finished-run alive "$P" </dev/null 2>/dev/null)
case "$RUN" in alive\ *) exit 0 ;; esac

echo "writer-alive: nothing holds $P open for writing, no live process writes it, and it has not been written for $((NOW - MTIME))s - the run that was producing it is gone (a killed or OOM'd detached run looks exactly like this). Read what the log DOES have; the thing you were waiting for may never have been printed."
exit 1
