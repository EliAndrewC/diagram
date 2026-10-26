#!/usr/bin/env bash
# US5's independent test (feature 427 T03): an extra loop in a stage, on a scratch worktree, refuses the push's check.
set -u
ROOT=/diagram/.clones/diagram-backlog
wt=$(mktemp -d)/us5
git -C "$ROOT" worktree add -q --detach "$wt" HEAD
cd "$wt"
mkdir -p specs/999-us5 && echo '# x' > specs/999-us5/spec.md
make --no-print-directory perf LABEL=999-start > "$wt.start.log" 2>&1; tail -1 "$wt.start.log"
python3 - <<'PY'
p='l7r/diagram/hamletgen/sink.py'
s=open(p).read()
a="def stage_sink(s: Settlement, plan: SitePlan) -> None:\n"
i=s.index(a)+len(a)
j=s.index('\n', s.index('"""', s.index('"""', i)+3))+1 if s[i:].lstrip().startswith('"""') else i
s=s[:j]+"    for _ in range(300_000):\n        _us5_extra()\n"+s[j:]
s+="\n\ndef _us5_extra() -> None:\n    return None\n"
open(p,'w').write(s)
PY
make --no-print-directory perf LABEL=999-end > "$wt.end.log" 2>&1; tail -1 "$wt.end.log"
SPECIFY_FEATURE=999-us5 make --no-print-directory perf-review; echo "perf-review rc=$?"
git -C "$ROOT" worktree remove --force "$wt"
