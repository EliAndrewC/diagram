#!/bin/bash
# 451 T455: each of the land crate's tests run alone (`--exact`, one thread), with a `git` on PATH ahead of the real one that logs a
# line a call and execs `/usr/bin/git` (strace is refused here: no ptrace in the container, observed 2026-11-27), and the kernel's
# last pid (/proc/loadavg's fifth field) read before and after - so `tasks` counts every process AND thread the machine started in
# the test's wall, other sessions' too (an upper bound; the baseline is measured idle beside it). A git called by absolute path is
# missed by the shim. One line a test: name, git calls, pid delta, wall, user, sys.
# usage: procs.sh <test binary> <out file>
set -u
bin=$1 out=$2
tmp=$(mktemp -d)
real=$(command -v git)
mkdir -p "$tmp/bin"
printf '#!/bin/sh\necho x >> "%s/git.log"\nexec %s "$@"\n' "$tmp" "$real" > "$tmp/bin/git"
chmod +x "$tmp/bin/git"
cd "$(dirname "$0")/../../../../rust/gate/crates/land" || exit 2
"$bin" --list --format terse 2>/dev/null | sed -n 's/: test$//p' > "$tmp/names"
lastpid() { cut -d' ' -f5 /proc/loadavg; }
: > "$out"
while read -r t; do
  : > "$tmp/git.log"
  p0=$(lastpid)
  PATH="$tmp/bin:$PATH" /usr/bin/time -f '%e %U %S' -o "$tmp/t" "$bin" --exact "$t" --test-threads=1 >/dev/null 2>&1
  p1=$(lastpid)
  printf '%s\t%s\t%s\t%s\n' "$t" "$(wc -l < "$tmp/git.log")" "$((p1 - p0))" "$(tr ' ' '\t' < "$tmp/t")" >> "$out"
done < "$tmp/names"
# the idle baseline: the pid counter's rise over 10 s with nothing of ours running
p0=$(lastpid); sleep 10; p1=$(lastpid)
echo "baseline: $((p1 - p0)) pids in 10 s with no test running" >> "$out"
rm -rf "$tmp"
