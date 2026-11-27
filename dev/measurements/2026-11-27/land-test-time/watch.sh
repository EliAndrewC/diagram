#!/bin/bash
# 451 T455: a passive watcher - every 2 s it looks for a land crate test binary (`l7r_gate_land-*`, any tree, anyone's run) alive
# more than 20 s and, once a run, dumps what it is doing: its threads' names (libtest names each test's thread after the test), each
# thread's state and wait channel, and every descendant process with its command line, state, wait channel and age. Nothing is
# started or signalled; it reads /proc only.
# usage: watch.sh <out file> <seconds to watch>
set -u
out=$1 until=$(( $(date +%s) + $2 ))
declare -A seen
while [ "$(date +%s)" -lt "$until" ]; do
  for pid in $(pgrep -f 'deps/l7r_gate_land-' 2>/dev/null); do
    # the binary itself, not a script whose arguments name it
    case $(readlink "/proc/$pid/exe" 2>/dev/null) in */deps/l7r_gate_land-*) ;; *) continue ;; esac
    age=$(ps -o etimes= -p "$pid" 2>/dev/null | tr -d ' ') || continue
    [ -n "$age" ] && [ "$age" -gt 20 ] || continue
    n=${seen[$pid]:-0}
    [ "$n" -lt 6 ] || continue          # at most six dumps a run, 2 s apart
    seen[$pid]=$((n + 1))
    {
      echo "=== $(date -u +%FT%TZ) pid $pid age ${age}s load $(cut -d' ' -f1-3 /proc/loadavg) cwd $(readlink /proc/$pid/cwd)"
      echo "--- threads (name state wchan)"
      for t in /proc/$pid/task/*; do
        printf '%s %s %s\n' "$(cat $t/comm 2>/dev/null)" "$(awk '{print $3}' $t/stat 2>/dev/null)" "$(cat $t/wchan 2>/dev/null)"
      done
      echo "--- descendants (pid ppid etimes stat wchan cwd args)"
      ps -e -o pid=,ppid=,etimes=,stat=,wchan:24=,args= | awk -v root="$pid" '
        { p[$1] = $2; line[$1] = $0 } END {
          for (k in p) { a = k; while (a in p && a != root && a > 1) a = p[a]; if (a == root && k != root) print k }
        }' | while read -r d; do
          printf '%s cwd=%s\n' "$(ps -o pid=,ppid=,etimes=,stat=,wchan:24=,args= -p "$d" | cut -c1-300)" "$(readlink /proc/$d/cwd 2>/dev/null)"
        done
    } >> "$out"
  done
  sleep 2
done
