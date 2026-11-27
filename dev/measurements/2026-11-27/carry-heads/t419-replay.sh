#!/usr/bin/env bash
# t419-replay.sh: the carries of T355 (51dec6f1ba onto 72f7684524, the clone before the session moved T399 part B by hand; compared with b991ec95f5) and T308 (1fb7ffff9b onto a6bebcb623; compared with 3012655340) redone by this tree's carry
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t419
T=/diagram/.clones/diagram-backlog-t271
cd $S/replay || exit 1
for pair in "b991ec95f5 51dec6f1ba b991ec95f5~2" "3012655340 1fb7ffff9b 3012655340~1"; do set -- $pair; h=$1; o=$2; on=$3
  git cherry-pick --abort 2>/dev/null; git checkout -q -f --detach $on; git clean -qfdx
  out=$($T/scripts/gates/l7r-gate.sh land --carry /diagram/.clones/diagram-backlog $o 2>&1); code=$?
  d=; [ $code = 0 ] && { d=$(git diff --stat HEAD $h | tr -s ' ' | tr '\n' ';'); [ -z "$d" ] && d=identical; }
  printf '%s <- %s code=%s %s\n   %s\n' $h $o $code "$d" "$(echo "$out" | grep -E '^carry:' | tail -1 | cut -c1-600)"
done
git cherry-pick --abort 2>/dev/null
