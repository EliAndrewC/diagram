"""Iterate in a worktree: cut every engine name that only frozen exhibits (or nothing) reference, since BASE's live census, to a fixpoint."""
import ast, subprocess, sys
from pathlib import Path
sys.path.insert(0, 'scripts/measure')
import dead_closure as dc
root = Path('.')
cutpy = sys.argv[1]
base_dead = None
rounds = []
while True:
    now = dc._tree_now(root)
    live = {k: v for k, v in now.items() if not k.startswith('legacy-hand-authored-pool')}
    lrefs, ldefs, _ = dc.census(live)
    dead = {n for n, at in ldefs.items() if not n.startswith('__') and lrefs[n] <= len(at)}
    if base_dead is None:
        base_dead = set(n for n in dead if not dc.census(now)[0][n] > lrefs[n])  # pre-existing truly dead: no exhibit uses them
    todo = sorted(dead - base_dead)
    if not todo:
        break
    rounds.append(todo)
    byfile = {}
    for n in todo:
        for at in ldefs[n]:
            byfile.setdefault(at.split(':')[0], set()).add(n)
    for f, names in byfile.items():
        r = subprocess.run([sys.executable, cutpy, f, *sorted(names)], capture_output=True, text=True)
        if r.returncode:
            print("CUT FAIL", f, r.stderr.strip()[:200])
    base_dead |= set(todo)
for i, r in enumerate(rounds):
    print(f"round {i}: {len(r)}: {' '.join(r)}")
