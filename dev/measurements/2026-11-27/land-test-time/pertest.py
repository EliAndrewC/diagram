"""451 T455: runs.sh's per-test times read back - each run's wall, processor seconds and load; the tests by median and by max
time over the runs; and, for the slowest runs against the fastest, which tests grew (ratio of the test's time in the slow runs to
its median in the fast ones), to tell a wall that scales with load across every test from one test that stands out.
usage: python3 -I pertest.py <runs dir>"""
import json, sys, glob, re, statistics as st, collections
d = sys.argv[1]
runs = {}
for p in glob.glob(d + "/run*.json"):
    i = int(re.search(r"run(\d+)\.json", p).group(1))
    t = {}
    for l in open(p):
        if not l.startswith("{"):
            continue
        e = json.loads(l)
        if e.get("type") == "test" and e.get("event") in ("ok", "failed"):
            t[e["name"]] = e.get("exec_time", 0.0)
    runs[i] = t
log = {}
for l in open(d + "/runs.log"):
    m = re.search(r"run(\d+) rc=(\d+) load1 ([\d.]+) ([\d.]+) wall/user/sys ([\d.]+) ([\d.]+) ([\d.]+)", l)
    if m:
        log[int(m.group(1))] = tuple(float(x) for x in m.groups()[1:])
order = sorted(runs, key=lambda i: log[i][3])
print("run  rc  load1 before/after  wall s  user s  sys s  cpu/wall  sum of tests s")
for i in sorted(runs):
    rc, l0, l1, w, u, s = log[i]
    print(f"{i:3d}  {int(rc)}   {l0:5.1f}/{l1:5.1f}       {w:6.2f}  {u:6.2f}  {s:6.2f}  {(u+s)/w:6.1f}  {sum(runs[i].values()):7.1f}")
names = sorted({n for t in runs.values() for n in t})
fast, slow = order[:len(order)//2], order[-3:]
print(f"\nfast half: runs {sorted(fast)}; slowest three: runs {slow}")
rows = []
for n in names:
    fm = st.median(runs[i].get(n, 0.0) for i in fast)
    sm = st.mean(runs[i].get(n, 0.0) for i in slow)
    mx = max(runs[i].get(n, 0.0) for i in runs)
    rows.append((n, fm, sm, mx, sm / fm if fm > 0.005 else float("nan")))
print("\nthe 20 slowest tests by their mean in the slowest three runs (s): fast-half median, slow-three mean, max over all runs, ratio")
for n, fm, sm, mx, r in sorted(rows, key=lambda z: -z[2])[:20]:
    print(f"  {fm:6.3f}  {sm:6.3f}  {mx:6.3f}  {r:5.1f}  {n}")
ratios = [r for *_, r in rows if r == r]
print(f"\nratio slow/fast over tests with a fast median > 5 ms: median {st.median(ratios):.1f}, max {max(ratios):.1f}, n {len(ratios)}")
print("tests whose max over all runs exceeds 10 s:", [(n, round(mx, 1)) for n, _, _, mx, _ in rows if mx > 10] or "none")
