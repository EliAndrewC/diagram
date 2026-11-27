"""451 T445: every test Phase line of the clone's event log (any tree, any make target), one line a phase (deduplicated across
the feature files); each crate's median test phase; the phases far past their crate's median, before and after 451 T364 landed.
usage: python3 -I hangs.py [SINCE]   (SINCE defaults to the T364 commit's time, 2026-11-27T05:24:05Z)"""
import sys, json, glob, statistics as st, collections
from datetime import datetime
EV = "/diagram/.clones/diagram-backlog/.git/l7r-events/"
T364 = sys.argv[1] if len(sys.argv) > 1 else "2026-11-27T05:24:05Z"
f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
seen, rows = set(), []
for p in glob.glob(EV + "*.jsonl"):
    for l in open(p, errors="replace"):
        if '"Phase"' not in l or '"test"' not in l:
            continue
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if e.get("step") != "test" or "t0" not in e or "t1" not in e:
            continue
        k = (e["t0"], e["t1"], e.get("clone", ""), e.get("make", ""), tuple(e.get("crates", [])))
        if k in seen:
            continue
        seen.add(k)
        crates = e.get("crates", []) or ["?"]
        rows.append((e["t0"], f(e["t1"]) - f(e["t0"]), e.get("clone", "").split("/")[-1], e.get("make", ""),
                     "+".join(c.split("/")[-1] for c in crates), e.get("code"), e.get("task", "")))
rows.sort()
by = collections.defaultdict(list)
for r in rows:
    by[r[4]].append(r[1])
med = {c: st.median(v) for c, v in by.items()}
far = lambda r: r[1] > max(60.0, 10 * med[r[4]])
print(f"test phases: {len(rows)}, {rows[0][0]} to {rows[-1][0]}; T364 at {T364}")
for label, sel in (("before T364", [r for r in rows if r[0] < T364]), ("since T364", [r for r in rows if r[0] >= T364])):
    hung = [r for r in sel if far(r)]
    print(f"\n{label}: {len(sel)} phases, {len(hung)} past max(60 s, 10 x their crate's median), {round(sum(r[1] for r in hung))} s")
    for r in hung:
        print(f"  {r[0]}  {r[1]:7.1f} s  median {med[r[4]]:.2f}  {r[2]}  {r[3]}  {r[4]}  code {r[5]}  {r[6]}")
print("\nlongest since T364, by crate (runs, median s, max s):")
since = collections.defaultdict(list)
for r in rows:
    if r[0] >= T364:
        since[r[4]].append(r[1])
for c, v in sorted(since.items(), key=lambda z: -max(z[1]))[:12]:
    print(f"  {c}: {len(v)}, {st.median(v):.2f}, {max(v):.1f}")
