"""451 T367/T411: a builder's slot-tell lines (code 0 told alone, 1 not) since T347 landed, by kind (a test build's telling lies
just before its `build` line, a lint pass's inside its `lint` line), and whether each was the tree's first of that crate and kind
after a handout (the pool's log); then each wide `slot-wait` line and the build it lay in. Read-only. Run: python3 -I tellings.py"""
import glob
import json
from datetime import datetime, timedelta

SINCE = "2026-11-27T00:20"
# the window ends at this tree's handout for T367, so the builder's own runs of the new code are not in it
UNTIL = "2026-11-27T03:30:03"
CLONE = "/diagram/.clones/diagram-backlog/.git"
P = lambda s: datetime.fromisoformat(s.rstrip("Z"))
ev = []
for f in glob.glob(f"{CLONE}/l7r-events/*.jsonl"):
    for line in open(f):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("ev") == "Phase" and r.get("src") == "rust" and SINCE <= r.get("t0", "") < UNTIL:
            r["a"], r["b"] = P(r["t0"]), P(r["t1"])
            ev.append(r)
ev.sort(key=lambda r: r["a"])
takes = [(P(r["utc"]), r["tree"]) for r in map(json.loads, open(f"{CLONE}/builder-pool.log")) if r["event"] == "take" and SINCE <= r["utc"] < UNTIL]
K = lambda r: (r.get("clone"), tuple(r.get("crates", [])))
by = lambda s: [r for r in ev if r["step"] == s]
builds, lints, tells, waits = by("build"), by("lint"), by("slot-tell"), by("slot-wait")
taken = lambda clone, at: max((u for u, tr in takes if tr == clone and u <= at), default=None)
seq = {}
for t in tells:
    if t.get("make") == "prewarm":
        continue
    lint = any(K(l) == K(t) and l["a"] <= t["a"] <= l["b"] for l in lints)
    seq.setdefault((t["clone"], taken(t["clone"], t["a"]), t["crates"][0] if t["crates"] else "", "lint" if lint else "test"), []).append(t)
agg = {}
for (clone, tk, crate, kind), ts in seq.items():
    # a lint's first run is its passes told within seconds of its first
    for t in ts:
        first = tk is not None and (t["a"] - ts[0]["a"]) < timedelta(seconds=30 if kind == "lint" else 0.001)
        k = (kind, "pool tree" if tk else "clone or before its handout", t["code"], "first after handout" if first else "later")
        agg[k] = agg.get(k, 0) + 1
print(f"slot-tell lines {SINCE}Z to {UNTIL}Z, handouts {len(takes)}")
for k in sorted(agg):
    print(" ", k, agg[k])
print(f"slot-wait lines {len(waits)}, {sum((w['b'] - w['a']).total_seconds() for w in waits):.1f} s:")
for w in waits:
    s = next((r for r in builds + lints if r.get("clone") == w.get("clone") and r["a"] <= w["a"] <= r["b"]), None)
    tk = s and taken(s["clone"], s["a"])
    key = s and (s["clone"], tk, s["crates"][0], "lint" if s["step"] == "lint" else "test")
    first = bool(s and key in seq and abs((seq[key][0]["a"] - s["a"]).total_seconds()) < 3)
    print(f"  {w['t0']} {(w['b'] - w['a']).total_seconds():5.1f} s {s and s['step']} {s and s['crates']}{' FIRST AFTER HANDOUT' if first else ''}")
