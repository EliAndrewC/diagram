"""What coincides at the memory peaks of the three-builder run (feature 451 T284, measured 2026-11-26, read-only).

Joins the sampler's log (anonymous memory, load, rustc count every 10 s) with the checks' `Phase` lines of the clone's event logs:
which steps were running, in how many trees, at the highest samples; how many compiling cargo calls one tree's own checks run at
once; and the seconds the machine spent at each count of them.

    python3 dev/measurements/2026-11-26/builder-count/slot-coincide.py [EVENTS_DIR] [SAMPLES]

EVENTS_DIR defaults to the clone's `.git/l7r-events` (every tree of a clone writes there), SAMPLES to the three-builder log beside
this file. The same script over a later run's samples is the build slot's re-measurement (`dev/audits/build-slot.md`).
"""
import collections, glob, json, os, statistics, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
EVENTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    subprocess.run(["git", "-C", HERE, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                   capture_output=True, text=True).stdout.strip(), "l7r-events")
SAMPLES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "mem-samples-three-builders.log")
HEAVY = {"cover-build", "lint", "build"}


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


S = []
for l in open(SAMPLES):
    if l.startswith("{"):  # the sampler's JSON line (make sampler-start, feature 451 T274), where the hand loop wrote key=value
        r = json.loads(l)
        S.append((ts(r["utc"]), r["anon"] / 2**30, r["load1"], r["rustc"]))
        continue
    p = l.split()
    d = dict(x.split("=") for x in p[1:])
    S.append((ts(p[0]), int(d["anon"]) / 2**30, float(d["load"]), int(d["rustc"])))
lo, hi = S[0][0], S[-1][0]
P = []
for f in glob.glob(os.path.join(EVENTS, "*.jsonl")):
    for l in open(f, errors="replace"):
        if '"Phase"' not in l:
            continue
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if r.get("ev") != "Phase" or r.get("src") != "rust":
            continue
        a, b = ts(r["t0"]), ts(r["t1"])
        if b < lo or a > hi:
            continue
        P.append((a, b, r["step"], r.get("make"), r.get("clone", "").split("/")[-1]))
print("samples", len(S), "over", round(hi - lo), "s; rust phases in the window", len(P))
dur, n = collections.Counter(), collections.Counter()
for a, b, s, *_ in P:
    dur[s] += b - a
    n[s] += 1
for s in dur:
    ds = sorted(b - a for a, b, st, *_ in P if st == s)
    print(f"  {s:12} n={n[s]:4} total={dur[s]/60:6.1f} min  median={ds[len(ds)//2]:6.1f} s  max={ds[-1]:6.1f} s")


def active(t):
    # a sample is 10 s apart: a phase that ended within the last 10 s still counts
    return [p for p in P if p[0] - 10 <= t <= p[1]]


def show(title, rows):
    print(title)
    for t, an, ld, rc in rows:
        act = active(t)
        c = collections.Counter(p[2] for p in act)
        trees = len(set(p[4] for p in act))
        print(f"  {datetime.fromtimestamp(t, timezone.utc):%H:%M:%S} anon={an:4.1f} GiB load={ld:5.1f} rustc={rc:2} trees={trees} {dict(c)}")


show("the 12 highest memory samples:", sorted(S, key=lambda x: -x[1])[:12])
show("the 8 highest rustc counts:", sorted(S, key=lambda x: -x[3])[:8])
by = collections.defaultdict(list)
for t, an, ld, rc in S:
    act = active(t)
    by[(len(set(p[4] for p in act)), tuple(sorted(set(p[2] for p in act))))].append((an, rc))
print("by (trees, steps running): samples, median GiB, max GiB, max rustc")
for k, v in sorted(by.items(), key=lambda kv: -max(x[0] for x in kv[1]))[:14]:
    print(" ", k, len(v), round(statistics.median(x[0] for x in v), 1), round(max(x[0] for x in v), 1), max(x[1] for x in v))


def maxsim(ps):
    pts = []
    for a, b, *_ in ps:
        pts += [(a, 1), (b, -1)]
    cur = m = 0
    for _, d in sorted(pts):
        cur += d
        m = max(m, cur)
    return m


print("one tree's own closing-checks, most at once: every step, each step, the compiling ones (cover-build, lint, build)")
for tree in sorted(set(p[4] for p in P)):
    mine = [p for p in P if p[4] == tree and p[3] == "closing-checks"]
    if mine:
        print(" ", tree, maxsim(mine), {s: maxsim([p for p in mine if p[2] == s]) for s in sorted(n)}, maxsim([p for p in mine if p[2] in HEAVY]))
allh = [p for p in P if p[2] in HEAVY]
pts = []
for a, b, *_ in allh:
    pts += [(a, 1), (b, -1)]
pts.sort()
cur, last, d = 0, pts[0][0], collections.Counter()
for t, x in pts:
    d[cur] += t - last
    last = t
    cur += x
print("machine-wide, compiling steps at once: most", maxsim(allh), "; seconds at each count", {k: round(v) for k, v in sorted(d.items())})
waits = [(a, b) for a, b, s, *_ in P if s == "slot-wait"]
print("slot waits in the window:", len(waits), "totalling", round(sum(b - a for a, b in waits)), "s")
