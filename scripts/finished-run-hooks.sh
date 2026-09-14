#!/usr/bin/env bash
# finished-run-hooks.sh - a run that has FINISHED cannot be reported as still going (feature 170).
# (GUARD_EDIT_OK: a NEW guard.)
#
# THE DEFECT, in the reporting session's own words (2026-08-30, relayed by the GM): *"I reported the
# gate as 'waiting' when it had actually failed four hours earlier because I never saw the
# notification."* Four hours of a session believing it was waiting on something that had already gone
# red. Nothing in this repository noticed: `agent-stall-hooks.sh` watches subagent TRANSCRIPTS, not
# background commands, and a completion notification that is missed is simply gone.
#
# WHAT IT DOES: every gate run writes a record to `dev/run-log/` when it finishes (the Makefile's
# LOGRUN). This compares the newest record against a marker of what the session has already been
# told, and surfaces anything newer - at the next prompt, and at turn end, so a turn cannot close on
# "still running" for a run that finished. Once surfaced, it is not surfaced again.
#
# THE FINISHED-RUN RULE REPORTS AND DOES NOT BLOCK. The failure there was a session not KNOWING, and
# blocking a turn would punish the wrong thing: a session may have perfectly good reasons to end a turn
# after a red run - reporting it, for instance.
#
# ...AND THE SECOND RULE, WHICH DOES BLOCK: A RUN STILL GOING MUST NOT BE ABANDONED (GM 2026-09-12).
# The first rule covers a run that finished and was never read. Its mirror image is a run that has not
# finished and is walked away from, and that is what happened the same afternoon: a session started
# `make done INCREMENTAL=0` detached, wrote its report, ended the turn, and never waited - the gate failed
# 58 seconds later on five uncovered lines and sat unread for 52 minutes, until the GM asked whether
# something had gone wrong. Nothing caught it, because the finished-run rule fires at the NEXT prompt, and
# the next prompt is exactly the moment the damage is already done. The GM:
#
#   "So we just put in a tooling fix specifically to stop this kind of thing from happening. So how do we
#   make that not happen? Since the issue in this case is that you ended your turn without waiting for it,
#   then is that something that can be detected in a hook? Like, if there is a makefile command running and
#   your turn ends, then we have a hook that errors or triggers you or sends you context to say, hey. Hold
#   on. You need to wait for that makefile command."
#
# It is detectable exactly, with no pattern matching and so no self-match trap: walk `/proc` for a process
# whose `comm` is `make` and whose `cwd` lies inside THIS session's clone. A `pgrep -f "make done"` would
# find the searching shell, which is the 2026-07-25 defect `no-poll-hooks.sh` exists for; a cwd read from
# the kernel cannot.
#
# ONCE PER RUN IS THE WHOLE RELEASE VALVE, AND THERE IS NO TOKEN ESCAPE - because a Stop hook's payload
# carries no command, so there is nowhere for a session to put one (tried, and the suite caught it). The turn
# is refused the first time it would close over a given live run, keyed on the ROOT make of the run, which is
# enough to force the decision; a second attempt goes through. That matters: a session answering the GM while
# a gate runs is doing the right thing and must not be trapped, and the marker is cleared the moment nothing
# is live, so the next run gets its own single refusal.
#
# ...AND THE GUARD ASKS THE SECOND QUESTION: IS ANYONE WAITING? (feature 246, GM 2026-09-13: "the fact that
# we keep seeing this message over and over again makes me wonder whether we should take a different
# approach ... it seems generally not good if we keep stepping on the same rake over and over again"). In
# its first day the rule refused 18 turn-ends on 13 runs, 5 of them repeats on a run it had already refused,
# and every one in the session that measured it landed on a state that was already right: a `make done`
# started through the Bash tool's background mode, which the harness wakes the session for when it exits,
# with a waiter loop armed on its log besides (`specs/246-*/research.md` R1-R3). Two things were wrong. The
# marker held EVERY live make pid, and a gate is four phases each with its own child pid, so "once per run"
# was once per phase. And the rule asked only "is a make alive", never "will anything wake the session" -
# so it could not tell the run the 2026-09-12 incident was about (detached with `setsid nohup`, nobody
# watching) from the two shapes that need nothing. Both are answered from `/proc`, by pid, never by pattern:
#   TRACKED   an ancestor of the make is the `claude` process - the harness itself - which is what every
#             background-mode command looks like (R2: the command's shell writes to the task file, and its
#             parent is `claude`); the harness notifies at exit.  -> let through, one line of context.
#   WATCHED   a loop of the shape `stale_waiters` recognizes (`until`/`while` ... `grep` ... `sleep`), outside
#             this hook's own ancestry, names the file the make's stdout goes to.  -> let through, one line.
#   UNWATCHED neither: a detached run with no watcher, the one shape that can go unread.  -> REFUSED, once
#             per root make, exactly as before.
# The refusal's remedy names the run's own log in the loop it prescribes, and says a background-mode run
# needs no loop - the old text sent sessions to build a second wakeup for an event the harness already
# reports (R3). A periodic "are you still waiting" timer was priced and declined (R4): polling with a period
# at a turn per tick, where the event wakeup exists twice over and did not fail.
#
# Modes:
#   prompt  (UserPromptSubmit) one line per unsurfaced finished run, then mark them surfaced
#   stop    (Stop) the same, PLUS the refusal above when a make run is still going
#   check <clone>  one-shot for any clone, marking nothing (the suite uses this)
#   seen <clone>   mark everything currently finished as surfaced (the suite uses this)
#   live <clone>   print one line per live make run in that clone (the suite and `make audit` use this)
#   judge <clone>  one line per ROOT live make run with its status - tracked | watched | unwatched (feature 246)
#   stale          print one line per waiter loop whose producer is dead (the suite uses this)
set -uo pipefail
MODE=${1:-}
FR_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clone_of() { # the working tree this hook is running in, or "" if it is not in one
  git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null
}

live_runs() { # live_runs <clone> -> "<pid> <target>" per live make run whose cwd is inside that clone
  # BY CWD, NOT BY PATTERN. The kernel knows each process's working directory, so nothing here can match
  # its own command line - the trap that made `pgrep -f "make done"` loop for 10.9 minutes in 2026-07-25.
  python3 - "$1" <<'PY'
import glob, os, sys

clone = os.path.realpath(sys.argv[1])
for d in glob.glob("/proc/[0-9]*"):
    try:
        if open(f"{d}/comm").read().strip() not in ("make", "gmake"):
            continue
        if not os.path.realpath(os.readlink(f"{d}/cwd")).startswith(clone):
            continue
        argv = open(f"{d}/cmdline").read().split("\0")
    except OSError:
        continue   # the process went away between the glob and the read, which is the common case
    # the TARGET is the first bare word after the make binary - what a session would wait on
    target = next((a for a in argv[1:] if a and not a.startswith("-") and "=" not in a), "")
    print(f"{d.rsplit('/', 1)[-1]} {target or 'make'}")
PY
}

judge_runs() { # judge_runs <clone> -> "<pid> <target> <status> <detail>" per ROOT live make run (feature 246)
  # ROOT = a live make none of whose ancestors is a live make: the `done` of a four-phase gate, not its
  # `static`/`_reference`/`test-full`/`test` children, so the refusal marker keys on something that does not
  # change at every phase boundary (R1: that is what turned "once per run" into once per phase).
  # STATUS is answered from the kernel by pid - `comm` and the stdout link of each ancestor, the cmdline of
  # every other process for a waiter - never by a pattern over this hook's own command line.
  python3 - "$1" "$$" <<'PY'
import glob, os, re, sys

clone, mine = os.path.realpath(sys.argv[1]), int(sys.argv[2])

def ppid(p):
    try:
        return int(open(f"/proc/{p}/stat").read().rsplit(") ", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        return 0

def comm(p):
    try:
        return open(f"/proc/{p}/comm").read().strip()
    except OSError:
        return ""

def stdout_of(p):
    try:
        return os.readlink(f"/proc/{p}/fd/1")
    except OSError:
        return ""

def ancestors(p):  # p's parent, grandparent, ... up to init
    out, q = [], ppid(p)
    while q > 1:
        out.append(q)
        q = ppid(q)
    return out

live = {}
for d in glob.glob("/proc/[0-9]*"):
    p = int(d.rsplit("/", 1)[-1])
    try:
        if comm(p) not in ("make", "gmake"):
            continue
        if not os.path.realpath(os.readlink(f"{d}/cwd")).startswith(clone):
            continue
        argv = open(f"{d}/cmdline").read().split("\0")
    except OSError:
        continue
    live[p] = next((a for a in argv[1:] if a and not a.startswith("-") and "=" not in a), "") or "make"

hook_tree = set(ancestors(mine)) | {mine}
loops = []  # (pid, cmdline) of every file-watching loop that is not this hook's own tree
for d in glob.glob("/proc/[0-9]*"):
    p = int(d.rsplit("/", 1)[-1])
    if p in hook_tree:
        continue
    try:
        cmd = open(f"{d}/cmdline").read().replace("\0", " ")
    except OSError:
        continue
    if re.search(r"\b(until|while)\b.*\bgrep\b", cmd) and "sleep" in cmd:
        loops.append((p, cmd))

for p, target in sorted(live.items()):
    anc = ancestors(p)
    if any(a in live for a in anc):
        continue  # a phase child: its root speaks for it
    tracked = next((a for a in anc if comm(a) == "claude"), None)
    if tracked is not None:
        # the task file is the stdout of the harness's own shell - the child of `claude` on this chain
        shell = [a for a in anc if ppid(a) == tracked]
        print(f"{p} {target} tracked {stdout_of(shell[0]) if shell else 'the harness'}")
        continue
    log = stdout_of(p)
    if log.startswith("/") and os.path.isfile(log):
        waiter = next((lp for lp, cmd in loops if log in cmd), None)
        if waiter is not None:
            print(f"{p} {target} watched {waiter} {log}")
            continue
    print(f"{p} {target} unwatched {log or '(no file)'}")
PY
}

stale_waiters() { # stale_waiters -> "<pid> <file>" per waiter loop whose producer is dead
  # THE THIRD RULE (GM 2026-09-12, who found three of these in their own status line after this session had
  # twice reported that nothing was running). A waiter is a loop watching a file; when the thing writing that
  # file dies, the loop spins forever. Three had been re-grepping every 15 s for EIGHT HOURS on logs from the
  # `make placement-stages` runs the OOM killer ended that morning - the same incident that produced the
  # proof-of-life clause, whose waiters predate it and so never got one.
  #
  # WHY NOTHING SAW THEM, which is the part worth keeping: at any instant the visible process is the loop's
  # own `sleep`, which lives 15 seconds, so a census that filters by process AGE cannot see the loop and a
  # census that filters by command NAME sees only `sleep`. The reliable question is asked of every process's
  # cmdline, and then of the file it names - exactly what `_writer-alive.sh` answers.
  #
  # SELF-MATCH IS EXCLUDED BY PID, not by pattern: this hook's own process tree carries the words `until grep`
  # in the command that searches for them, which is the 2026-07-25 trap in its purest form.
  # THE HELPER'S PATH IS PASSED IN, not derived: this python reads from STDIN, so `__file__` is not the script
  # and `os.path.abspath` resolved it against the CWD - which made the probe look for the helper in whatever
  # directory the hook happened to run from (caught by its own first real test, 2026-09-12).
  python3 - "$$" "$FR_HERE" <<'PY'
import glob, os, re, subprocess, sys

mine, here = int(sys.argv[1]), sys.argv[2]
alive = os.path.join(here, "_writer-alive.sh")
ancestry = set()
pid = mine
while pid > 1:                      # this hook, its shell, and everything above: never reported
    ancestry.add(pid)
    try:
        pid = int(open(f"/proc/{pid}/stat").read().rsplit(") ", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        break
for d in glob.glob("/proc/[0-9]*"):
    p = int(d.rsplit("/", 1)[-1])
    if p in ancestry:
        continue
    try:
        cmd = open(f"{d}/cmdline").read().replace("\0", " ")
    except OSError:
        continue
    if not re.search(r"\b(until|while)\b.*\bgrep\b", cmd) or "sleep" not in cmd:
        continue
    # the file it watches: the last path-shaped operand in the loop's condition
    paths = re.findall(r"(?:/[\w.-]+)+\.\w+", cmd)
    for f in dict.fromkeys(paths):
        if not os.path.exists(f):
            continue
        if subprocess.run([alive, f], capture_output=True).returncode != 0:
            print(f"{p} {f}")
            break
PY
}

report() { # report <clone> <mark|nomark> -> one line per finished run the session has not been told about
  local clone=$1 mark=$2 log seen newest utc target result seconds age now
  log="$clone/.claude/skills/diagram/dev/run-log"
  [ -d "$log" ] || return 0
  seen="$clone/.git/finished-run.seen"
  newest=$(ls -t "$log"/*.json 2>/dev/null | head -1)
  [ -n "$newest" ] || return 0
  # ALREADY TOLD? The marker holds the newest record's basename at the time of the last report.
  [ -f "$seen" ] && [ "$(cat "$seen" 2>/dev/null)" = "$(basename "$newest")" ] && return 0
  utc=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("utc",""))' "$newest" 2>/dev/null)
  target=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("target",""))' "$newest" 2>/dev/null)
  result=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("result",""))' "$newest" 2>/dev/null)
  seconds=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("seconds",""))' "$newest" 2>/dev/null)
  now=$(date -u +%s)
  age=$(( now - $(date -u -d "$utc" +%s 2>/dev/null || echo "$now") ))
  [ "$mark" = mark ] && printf '%s' "$(basename "$newest")" > "$seen" 2>/dev/null
  case "$result" in
    green|already-verified)
      printf 'finished-run: `make %s` finished %s ago: %s (%ss). It is NOT still running.\n' "$target" "$(human "$age")" "$result" "$seconds" ;;
    *)
      printf 'finished-run: `make %s` finished %s ago and it is %s (%ss) - NOT still running. Read it before you report on it.\n' "$target" "$(human "$age")" "$result" "$seconds" ;;
  esac
}

human() { # seconds -> a duration a person reads
  local s=$1
  if [ "$s" -lt 90 ]; then printf '%ss' "$s"
  elif [ "$s" -lt 5400 ]; then printf '%s min' "$(( s / 60 ))"
  else printf '%s h' "$(( s / 3600 ))"; fi
}

case "$MODE" in
  prompt|stop)
    INPUT=$(cat 2>/dev/null || true)
    CWD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd",""))
except Exception: pass' 2>/dev/null)
    CLONE=$(clone_of "${CWD:-$PWD}")
    [ -n "$CLONE" ] || exit 0
    out=$(report "$CLONE" mark)
    if [ -n "$out" ]; then
      printf '%s\n' "$out"
      [ "$MODE" = stop ] && printf 'finished-run: do not end a turn saying a run is still going when this one is not.\n'
      # shellcheck source=/dev/null
      . "$FR_HERE/_guardlog.sh"
      guard_log finished-run reminded "$out" finished-not-running
    fi
    # ...AND THE TURN MAY NOT CLOSE OVER A RUN THAT IS STILL GOING (GM 2026-09-12; see the header).
    if [ "$MODE" = stop ]; then
      LIVE=$(live_runs "$CLONE")
      if [ -n "$LIVE" ]; then
        # shellcheck source=/dev/null
        . "$FR_HERE/_guardlog.sh"
        SEEN_F="$CLONE/.git/live-run.told"
        ROOTS=$(judge_runs "$CLONE")
        UNWATCHED=$(printf '%s\n' "$ROOTS" | awk '$3 == "unwatched"')
        if [ -z "$UNWATCHED" ]; then
          # EVERY ROOT RUN WILL WAKE THE SESSION (feature 246): tracked by the harness, or watched by a loop on
          # its log. One line each, recorded, and the turn closes - the wait is already armed.
          while read -r pid target status detail; do
            [ -n "$pid" ] || continue
            if [ "$status" = tracked ]; then
              printf 'finished-run: `make %s` (pid %s) is still going; the harness will wake this session when it finishes (its output: %s). Nothing more to arm.\n' "$target" "$pid" "$detail"
              guard_log finished-run permitted "$pid $target $detail" tracked-run
            else
              printf 'finished-run: `make %s` (pid %s) is still going; a waiter (pid %s) is watching %s and will wake this session. Nothing more to arm.\n' "$target" "$pid" "${detail%% *}" "${detail#* }"
              guard_log finished-run permitted "$pid $target $detail" waiter-armed
            fi
          done <<< "$ROOTS"
        else
          # keyed on the UNWATCHED ROOTS, so a phase child appearing under the same run refuses nothing new
          PIDS=$(printf '%s\n' "$UNWATCHED" | cut -d' ' -f1 | tr '\n' ',')
          if [ "$(cat "$SEEN_F" 2>/dev/null)" = "$PIDS" ]; then
            exit 0   # already told for exactly these runs: never a loop, and a turn may close deliberately
          fi
          printf '%s' "$PIDS" > "$SEEN_F" 2>/dev/null || true
          printf 'A MAKE RUN IS STILL GOING, NOTHING WILL WAKE THIS SESSION FOR IT, and this turn was about to end:\n' >&2
          printf '%s\n' "$LIVE" | sed 's/^/  pid /' >&2
          while read -r pid target status detail; do
            [ -n "$pid" ] || continue
            case "$status" in
              unwatched) printf '\npid %s `make %s` is DETACHED with no watcher - its output goes to %s.\n' "$pid" "$target" "$detail" >&2
                         printf 'Wait for it: background a loop on that log (`until grep -qE "verification-state|GATE FAILED" %s; do sleep 20; done`)\n' "$detail" >&2
                         printf 'and the no-poll guard will add the proof-of-life check for you. Then REPORT WHAT IT SAID.\n' >&2 ;;
              tracked)   printf '\npid %s `make %s` is fine: started through the Bash tool'"'"'s background mode, the harness wakes this session at exit.\n' "$pid" "$target" >&2 ;;
              watched)   printf '\npid %s `make %s` is fine: a waiter (pid %s) is on its log.\n' "$pid" "$target" "${detail%% *}" >&2 ;;
            esac
          done <<< "$ROOTS"
          printf '\nA run started through the Bash tool'"'"'s background mode needs NO loop - the harness wakes the session\n' >&2
          printf 'when it exits and this guard sees that. The loop is for a run detached with setsid/nohup, which nothing else watches.\n' >&2
          printf 'Reporting a result you have not seen is the thing this prevents: on 2026-09-12 a detached gate failed 58 s\n' >&2
          printf 'after a turn ended on "the gate is running" and sat unread for 52 minutes.\n' >&2
          printf 'Ending the turn deliberately (the GM asked something else) is fine: end it again and this lets it through.\n' >&2
          guard_log finished-run blocked "$LIVE" run-still-going
          exit 2
        fi
        exit 0
      fi
      rm -f "$CLONE/.git/live-run.told" 2>/dev/null || true   # nothing live: the next run starts clean
      # ...AND A WAITER WHOSE PRODUCER IS DEAD IS REPORTED, NEVER LEFT SPINNING (the third rule; see
      # `stale_waiters`). It REPORTS rather than blocks: the loop is harmless in itself, the session simply has
      # to know it will never end - and it is what the GM sees in their own status line, reported as running.
      STALE=$(stale_waiters 2>/dev/null)
      if [ -n "$STALE" ]; then
        printf 'A WAITER IS SPINNING ON A DEAD PRODUCER - it will never finish on its own:\n'
        printf '%s\n' "$STALE" | sed 's/^/  pid /'
        printf 'Nothing is writing that file any more. Read what it DOES have, then stop the loop by its pid.\n'
        printf 'These show in the GM status line as running shells, which is how three of them went unnoticed\n'
        printf 'for eight hours on 2026-09-12 while this session twice reported that nothing was running.\n'
        # shellcheck source=/dev/null
        . "$FR_HERE/_guardlog.sh"
        guard_log finished-run reminded "$STALE" waiter-on-a-dead-producer
      fi
    fi
    exit 0 ;;
  check) report "${2:?clone}" nomark; exit 0 ;;
  seen)  report "${2:?clone}" mark >/dev/null; exit 0 ;;
  live)  live_runs "${2:?clone}"; exit 0 ;;
  judge) judge_runs "${2:?clone}"; exit 0 ;;
  stale) stale_waiters; exit 0 ;;
  *) echo "usage: $0 prompt|stop|check <clone>|seen <clone>|live <clone>" >&2; exit 2 ;;
esac
