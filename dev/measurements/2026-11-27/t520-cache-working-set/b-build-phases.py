#!/usr/bin/env python3
"""T520 (b), (d): the build / test-build phases a tree ran, from the clone's event logs.

Run: grep -h '"src":"rust"' /diagram/.clones/diagram-backlog/.git/l7r-events/*.jsonl | python3 -I b-build-phases.py TREE [SINCE]
TREE is the clone directory's suffix (b1, t269, land) or 'clone'; SINCE an ISO prefix (default 2026-11-25).
Prints each build-like phase (UTC start, make target, step, task, seconds, crates) and the sum of seconds per make target.
"""
import collections
import datetime
import json
import sys

want = sys.argv[1]
since = sys.argv[2] if len(sys.argv) > 2 else "2026-11-25"
BUILDY = {"build", "cover-build", "prewarm", "test-build", "lint"}
rows = []
for line in sys.stdin:
    try:
        e = json.loads(line)
    except ValueError:
        continue
    clone = e.get("clone", "")
    tree = clone.rsplit("diagram-backlog", 1)[-1].lstrip("-") or "clone"
    if not clone.startswith("/diagram/.clones/diagram-backlog") or tree != want or e.get("t0", "") < since:
        continue
    if e.get("step") not in BUILDY and "prewarm" not in str(e.get("make")):
        continue
    a = datetime.datetime.fromisoformat(e["t0"].rstrip("Z"))
    b = datetime.datetime.fromisoformat(e["t1"].rstrip("Z"))
    rows.append((e["t0"][:16], str(e.get("make")), e.get("step"), str(e.get("task")), (b - a).total_seconds(),
                 ",".join(c.split("/")[-1] for c in e.get("crates", []))))
rows.sort()
for r in rows:
    print("%s %-14s %-12s %-6s %7.1fs %s" % r)
tot = collections.Counter()
for r in rows:
    tot[(r[1], r[2])] += r[4]
print("\nmake step seconds")
for (m, s), v in sorted(tot.items()):
    print("%-14s %-12s %8.0f" % (m, s, v))
