#!/usr/bin/env python3
"""Feature 347: 274's R1 figures, computed the same way for a sessions file from collect.py.

Usage: analyze.py r1|post [UNTIL] [FEATURES]
  UNTIL     only sessions starting before this ISO time (R1 was taken at 2026-09-27T22:30, before 274 landed)
  FEATURES  a comma list of features to keep (e.g. 269,280,291,317 for the like-for-like research groups)

Writes groups-<which>[-<features>].json and prints: the group table, then the summary R1 reported - per thing checked (median, IQR)
over complete groups (a write session, a check session and something checked), the largest context of any turn, the
write sessions' turns / mean turn / peak, and the continuations (coordination reads: coord.py).
"""

import collections
import json
import pathlib
import statistics
import sys

H = pathlib.Path(__file__).parent
M = 1e6
which = sys.argv[1] if len(sys.argv) > 1 else "post"
until = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else "9999"
feats = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
S = [s for s in json.loads((H / f"sessions-{which}.json").read_text()) if s["start"] < until and (not feats or s["feature"] in feats)]


def quartiles(xs):
    if len(xs) < 2:
        return xs[0] if xs else 0, xs[0] if xs else 0, xs[0] if xs else 0
    q = statistics.quantiles(xs, n=4)
    return q[0], statistics.median(xs), q[2]


groups = collections.OrderedDict()
for s in sorted(S, key=lambda s: s["start"]):
    groups.setdefault(s["group"], []).append(s)

rows = []
for g, ss in groups.items():
    main = sum(s["tot"] for s in ss)
    agt = sum(a["tot"] for s in ss for a in s["agents"])
    drift = sum(1 for s in ss for a in s["agents"] if a["type"] == "entry-drift")
    ho = next((s["handoff"] for s in ss if s["handoff"]), None)
    if ho:
        q, k = ho
    else:  # R1's way: the check briefs' own lists
        q = sum(s["q"] for s in ss if s["kind"] in ("check", "owed"))
        k = sum(s["k"] for s in ss if s["kind"] in ("check", "owed"))
    kinds = collections.Counter(s["kind"] for s in ss)
    things = q + drift + k
    rows.append({"group": g, "start": ss[0]["start"][:16], "sessions": len(ss), "kinds": dict(kinds), "q": q, "m": drift, "k": k,
                 "things": things, "total": main + agt, "main": main, "agents": agt, "peak": max(s["peak"] for s in ss),
                 "per_thing": (main + agt) / things if things else None,
                 "complete": bool(kinds["write"] and kinds["check"] and things)})

print(f"{'group':<46}{'start':<17}{'ses':>4}{'q/m/k':>9}{'total M':>9}{'peak K':>7}{'/thing M':>9}")
for r in rows:
    pt = f"{r['per_thing'] / M:.2f}" if r["per_thing"] else "-"
    print(f"{r['group'][:45]:<46}{r['start']:<17}{r['sessions']:>4}{f'{r[chr(113)]}/{r[chr(109)]}/{r[chr(107)]}':>9}{r['total'] / M:>9.2f}{r['peak'] / 1e3:>7.0f}{pt:>9}{'' if r['complete'] else '  (incomplete)'}")
(H / f"groups-{which}{'-' + '-'.join(sorted(feats)) if feats else ''}.json").write_text(json.dumps(rows, indent=1))

done = [r for r in rows if r["complete"]]
w = [s for s in S if s["kind"] == "write"]
lo, med, hi = quartiles([r["per_thing"] for r in done])
print(f"\n{which} until {until} features {sorted(feats) if feats else 'all'}: {len(S)} sessions, {len(rows)} groups, {len(done)} complete, {sum(s['tot'] for s in S) / M:.0f} M main")
print(f"per thing checked (complete groups): median {med / M:.2f} M (IQR {lo / M:.2f}-{hi / M:.2f}); group total median {statistics.median(r['total'] for r in done) / M:.1f} M for a median {statistics.median(r['things'] for r in done)} things")
print(f"largest context of any turn: {max(s['peak'] for s in S) / 1e3:.0f} K; complete groups' peak median {statistics.median(r['peak'] for r in done) / 1e3:.0f} K")
if w:
    print(f"write sessions: {len(w)}, turns median {statistics.median(s['turns'] for s in w):.0f} (max {max(s['turns'] for s in w)}), "
          f"mean turn {sum(s['tot'] for s in w) / sum(s['turns'] for s in w) / 1e3:.0f} K, peak median {statistics.median(s['peak'] for s in w) / 1e3:.0f} K, max {max(s['peak'] for s in w) / 1e3:.0f} K")
print(f"continuations: {sum(1 for s in S if s['kind'] == 'continuation')}")
