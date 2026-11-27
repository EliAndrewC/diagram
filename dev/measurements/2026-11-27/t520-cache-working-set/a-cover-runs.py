#!/usr/bin/env python3
"""T520 (a): every coverage build (cover-build phase) in a pool tree since 2026-11-25, from the clone's event logs.

Run: grep -h '"step":"cover-build"' /diagram/.clones/diagram-backlog/.git/l7r-events/*.jsonl | python3 -I a-cover-runs.py
Prints one row a build (UTC start, tree, make target, task, seconds, crates), then per tree the count and seconds before and
after the GM's 2026-11-26 reversal (builders run no coverage), recorded 23:38Z.
"""
import collections
import datetime
import json
import sys

REVERSAL = "2026-11-26T23:38"  # the reversal recorded, docs/process-decisions.md 9b5e948896 (18:37 EST); the brief block 3012655340, 03:34Z
rows = []
for line in sys.stdin:
    try:
        e = json.loads(line)
    except ValueError:
        continue
    clone = e.get("clone", "")
    tree = clone.rsplit("diagram-backlog", 1)[-1].lstrip("-") or "clone"
    if tree not in {"t269", "t270", "t271", "b1"} or e["t0"] < "2026-11-25":
        continue
    a = datetime.datetime.fromisoformat(e["t0"].rstrip("Z"))
    b = datetime.datetime.fromisoformat(e["t1"].rstrip("Z"))
    rows.append((e["t0"][:16], tree, e.get("make"), e.get("task"), (b - a).total_seconds(),
                 ",".join(c.split("/")[-1] for c in e.get("crates", []))))
rows.sort()
for r in rows:
    print("%s %-4s %-14s %-5s %6.1fs %s" % r)
agg = collections.defaultdict(lambda: [0, 0.0, 0, 0.0])
for t0, tree, *_rest in rows:
    secs = _rest[2]
    k = agg[tree]
    if t0 < REVERSAL:
        k[0] += 1
        k[1] += secs
    else:
        k[2] += 1
        k[3] += secs
print("\ntree  builds<reversal  secs   builds>=reversal  secs")
for tree, (n0, s0, n1, s1) in sorted(agg.items()):
    print("%-5s %6d %10.0f %10d %10.0f" % (tree, n0, s0, n1, s1))
