#!/usr/bin/env bash
# t300-replay.sh <out-file>: each hand-resolved carry of 2026-11-26 redone by the tree's carry in the scratch clone, compared with the session's commit
S=/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t300
T=/diagram/.clones/diagram-backlog-t271
cd $S/t300-replay || exit 1
grep CONFLICT $S/t300-plain.txt | while read h o rest; do
  git cherry-pick --abort 2>/dev/null; git checkout -q -f --detach $h~1; git clean -qfdx
  out=$($T/scripts/gates/l7r-gate.sh land --carry /diagram/.clones/diagram-backlog $o 2>&1); code=$?
  if [ $code = 0 ]; then d=$(git diff --stat HEAD $h | sed 's#specs/451-time-retro-and-efficiency/##' | tr -s ' ' | tr '\n' ';'); [ -z "$d" ] && d=identical; d="$d pin-lost=$(python3 -c "import sys; sys.path.insert(0,'$S'); m=__import__('t300-pin'); print(m.lost('$h~1','$o','HEAD'))")"; else d=; fi
  printf '%s %s code=%s %s\n   %s\n' "$h" "$(echo $rest | cut -c1-22)" "$code" "$d" "$(echo "$out" | grep -E "^carry:" | tail -1 | sed "s#/tmp/claude-1000[^ ]*t300-replay#REPLAY#g; s#specs/451-time-retro-and-efficiency/##g" | cut -c1-900)"
done > "$1"
git cherry-pick --abort 2>/dev/null
grep -c 'code=0' "$1"; grep -c 'code=0 identical' "$1"
