"""461 T23: each lane batch from lane.jsonl - changes, runs, run minutes, wall minutes, stops (by cause), resumes, outcome.
Usage: python3 -I t23-batches.py LANE_JSONL"""
import json, sys, re
from datetime import datetime as D
ts = lambda s: D.fromisoformat(s.replace("Z", "+00:00"))
B = {}
order = []
cur = None
for l in open(sys.argv[1]):
    d = json.loads(l)
    b = d.get("batch")
    ev = d["event"]
    if ev == "batch":
        B[b] = dict(first=d["utc"], last=d["utc"], changes=len(d["changes"]), runs=0, run_min=0.0, stops=[], resumes=0,
                    reds=[], ejects=[], landed=None, pushes=0)
        order.append(b); cur = b
        continue
    if ev == "start" and d.get("why", "").startswith("resume") and cur:
        B[cur]["resumes"] += 1
    if ev == "stop" and cur and B[cur]["landed"] is None:
        w = d.get("why", "")
        cause = ("carry NOT VERIFIED" if "NOT VERIFIED" in w else "carry conflict" if "conflicting: " in w and "conflicting: )" not in w
                 else "first-pass row naming no change" if "first pass refused" in w else "lane-stop by hand" if "lane-stop" in w else w[:60])
        B[cur]["stops"].append(cause)
    if b not in B:
        continue
    r = B[b]
    r["last"] = d["utc"]
    if ev == "run":
        r["runs"] += 1; r["run_min"] += d.get("minutes", 0)
        if d.get("code"):
            r["reds"].append((d.get("red") or ["(none placed)"])[0][:70] if isinstance(d.get("red"), list) else str(d.get("red"))[:70])
    if ev == "eject":
        r["ejects"].append((d["change"][:10], d["why"], d["repair"]))
    if ev == "push":
        r["pushes"] += 1
    if ev == "landed":
        r["landed"] = (len(d["landed"]), len(d["ejected"]), d["runs"], d["minutes"])
for b in order:
    r = B[b]
    wall = (ts(r["last"]) - ts(r["first"])).total_seconds() / 60
    from collections import Counter
    print(f"{b}: {r['first'][11:19]}-{r['last'][11:19]}Z wall {wall:.1f} min; {r['changes']} change(s); runs {r['runs']} ({r['run_min']:.1f} min);"
          f" pushes by the lane {r['pushes']}; stops {dict(Counter(r['stops']))}; resumes {r['resumes']}; end {r['landed']} (landed, ejected, runs, minutes)")
    for x in r["reds"]:
        print(f"    red: {x}")
    for e in r["ejects"]:
        print(f"    eject: {e}")
