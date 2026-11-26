#!/usr/bin/env python3
"""451 T315: what the recorded runs of 2026-11-25/26 took - every `Phase` line of the clone's event log (`.git/l7r-events/*.jsonl`)
whose step is `build`, `test` or `slot-wait` (the wait for one of the machine's build slots, 451 T284, which is INSIDE the `build` line it precedes) and which names ONE crate, by crate: the count, the median, the 90th centile and the longest.
usage: phase-history.py <events dir> <YYYY-MM-DD> [<YYYY-MM-DD> ...]"""
import sys, json, glob, datetime, statistics, collections
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
days = set(sys.argv[2:]); rows = collections.defaultdict(list)
for f in glob.glob(sys.argv[1] + "/*.jsonl"):
    for l in open(f, errors="replace"):
        if '"ev":"Phase"' not in l or '"src":"rust"' not in l: continue
        try: e = json.loads(l)
        except ValueError: continue
        if e.get("step") not in ("build", "test", "slot-wait") or len(e.get("crates", [])) != 1 or e["t0"][:10] not in days or e.get("code") != 0: continue
        rows[(e["crates"][0], e["step"])].append(ts(e["t1"]) - ts(e["t0"]))
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
print("crate | step | runs | not found fresh (>= 0.5 s) | median of those s | 90th centile s | longest s")
for (c, s), v in sorted(rows.items()):
    w = [x for x in v if x >= 0.5]
    if w: print(f"{c} | {s} | {len(v)} | {len(w)} | {statistics.median(w):.1f} | {q(w, 0.9):.1f} | {max(w):.1f}")
