#!/usr/bin/env python3
"""451 T347: one sampled run's memory by the Phase lines it wrote - for each step's span (and the whole run) the peak of the summed
anonymous memory, of the summed resident memory, the sum of the VmHWM of the processes last seen in the span (upper bound), the most
rustc and linkers alive at once, the span's seconds, and the gap between samples there (the sampler's blind spot).
usage: windows.py <samples.tsv> <events.jsonl> <first new line of it> <the tree's path>"""
import datetime, json, sys
rows = [tuple(float(x) for x in l.split()) for l in open(sys.argv[1])]
hw = [l.split("\t") for l in open(sys.argv[1] + ".hwm")]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
spans = [("run", rows[0][0], rows[-1][0])]
for i, l in enumerate(open(sys.argv[2])):
    if i + 1 < int(sys.argv[3]) or '"ev":"Phase"' not in l: continue
    e = json.loads(l)
    if e.get("clone") == sys.argv[4]: spans.append((e["step"], ts(e["t0"]), ts(e["t1"])))
G = 2 ** 20
for step, a, b in spans:
    r = [x for x in rows if a - 0.02 <= x[0] <= b + 0.02] or [(0,) * 7]
    gap = max([y[0] - x[0] for x, y in zip(r, r[1:])] or [0])
    h = sum(int(x[3]) for x in hw if a - 0.05 <= float(x[0]) <= b + 0.05)
    print(f"  {step:10s} {b - a:6.2f} s  anon {max(x[1] for x in r) / G:5.0f} MiB  rss {max(x[2] for x in r) / G:5.0f} MiB  hwm_sum {h / G:5.0f} MiB  "
          f"rustc {int(max(x[3] for x in r))}  linkers {int(max(x[4] for x in r))}  max gap {gap * 1000:.0f} ms")
