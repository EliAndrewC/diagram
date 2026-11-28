"""461 T23: every landing gate from START on, by tree - its minutes, its rust steps' minutes and crates compiled.

A gate is a `land`/`gate` Phase line (src land, step gate); its rust steps are the src=rust Phase lines of
make=land in the same clone inside its span. Load is the sampler's median `load` over the span.
Usage: python3 -I t23-gates.py COMMON_GIT_DIR START
"""
import json, sys, glob, statistics
from datetime import datetime as D
from collections import defaultdict

g, start = sys.argv[1], sys.argv[2]
ts = lambda s: D.fromisoformat(s.replace("Z", "+00:00"))
phases = []
for fn in glob.glob(f"{g}/l7r-events/*.jsonl"):
    with open(fn) as f:
        for l in f:
            if '"Phase"' not in l:
                continue
            try:
                d = json.loads(l)
            except Exception:
                continue
            if d.get("t0", "") >= start and d.get("make") == "land":
                phases.append(d)
samples = []
for fn in glob.glob(f"{g}/l7r-events/samples/*.jsonl"):
    with open(fn) as f:
        for l in f:
            try:
                d = json.loads(l)
            except Exception:
                continue
            t = d.get("utc") or d.get("t")
            if t and t >= start and "load1" in d:
                samples.append((t.replace("Z", ".000Z") if len(t) == 20 else t, d["load1"], len(d.get("held") or [])))
gates = sorted((d for d in phases if d["src"] == "land" and d["step"] == "gate"), key=lambda d: d["t0"])
print("t0 (UTC)             tree                 task  gate_min code  rust steps (min, crates compiled)            load_med")
for gd in gates:
    lo, hi, clone = gd["t0"], gd["t1"], gd["clone"]
    steps = defaultdict(lambda: [0.0, 0])
    for d in phases:
        if d["src"] == "rust" and d["clone"] == clone and lo <= d["t0"] <= hi:
            s = steps[d["step"]]
            s[0] += (ts(d["t1"]) - ts(d["t0"])).total_seconds() / 60
            c = d.get("compiled")
            s[1] += len(c) if isinstance(c, list) else (c or 0)
    loads = [v for t, v, h in samples if lo <= t <= hi]
    held = [h for t, v, h in samples if lo <= t <= hi]
    lm = (f"{statistics.median(loads):.1f} held {statistics.median(held):.0f}") if loads else "-"
    dur = (ts(hi) - ts(lo)).total_seconds() / 60
    st = ", ".join(f"{k} {v[0]:.1f} ({v[1]})" for k, v in sorted(steps.items()))
    print(f"{lo[:19]}  {clone.split('/')[-1]:<20} {str(gd.get('task')):<5} {dur:6.1f}  {gd['code']:>3}   {st:<46} {lm}")
