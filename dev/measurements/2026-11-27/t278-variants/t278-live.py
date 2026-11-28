#!/usr/bin/env python3
"""T278: per build directory, the groups (store, variant) holding more than 2 entries built since T325 landed - the variants a
smaller keep would weigh against each other - with each entry's age in hours. lstat only. usage: t278-live.py DIR [MIN]"""
import importlib.util, os, sys, time
spec = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)), "t278-count.py"))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
root, least = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3
now = time.time()
g = {}
for store in c.stores(root):
    for e in os.scandir(store):
        t, b = c.walk(e.path)
        g.setdefault((os.path.relpath(store, root), c.variant_of(e.name)), []).append((t, b, e.name))
for k, v in sorted(g.items()):
    live = [x for x in v if x[0] >= c.T325]
    if len(live) >= least:
        print(k[0], k[1], len(v), "since-T325:", len(live), " ".join(f"{(now - t) / 3600:.1f}h" for t, _, _ in sorted(v, reverse=True)))
