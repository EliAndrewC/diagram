"""451 T455: every test Phase line of the land crate alone (crates == [rust/gate/crates/land]) in the clone's event log,
deduplicated, beside the memory sampler's 10 s samples over the phase: load1 (mean, max), the container's memory-stall rates
(PSI `mem_full_us` and `mem_some_us`, microseconds of stall per second of wall), cpu stall (`cpu_some_us`), the cgroup's
`cur` against `max`, and how many other test or build phases of any tree overlapped it.
usage: python3 -I phases.py"""
import json, glob, statistics as st
from datetime import datetime
EV = "/diagram/.clones/diagram-backlog/.git/l7r-events/"
f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
seen, land, other = set(), [], []
for p in glob.glob(EV + "*.jsonl"):
    for l in open(p, errors="replace"):
        if '"Phase"' not in l:
            continue
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if e.get("step") not in ("test", "build") or "t0" not in e or "t1" not in e:
            continue
        k = (e["t0"], e["t1"], e.get("clone", ""), e.get("step"), tuple(e.get("crates", [])))
        if k in seen:
            continue
        seen.add(k)
        r = (f(e["t0"]), f(e["t1"]), e["t0"], e.get("clone", "").split("/")[-1], e.get("make", ""), e.get("code"), e["step"])
        if e["step"] == "test" and e.get("crates") == ["rust/gate/crates/land"]:
            land.append(r)
        else:
            other.append(r)
samples = []
for l in open(EV + "samples/mem-samples.jsonl", errors="replace"):
    try:
        s = json.loads(l)
        samples.append((f(s["utc"]), s))
    except (ValueError, KeyError):
        pass
samples.sort(key=lambda z: z[0])
s0 = samples[0][0]
land.sort()
print(f"land test phases: {len(land)}; median {st.median(r[1]-r[0] for r in land):.2f} s; samples from {samples[0][1]['utc']}")
print("t0 (UTC)                  wall s  tree                  make            code  load1 mean/max  memfull us/s  memsome us/s  cpusome us/s  cur/max GB    overlapping test+build")
rows = []
for a, b, t0, tree, mk, code, _ in land:
    if a < s0:
        print(f"{t0}  {b-a:7.1f}  {tree:20s}  {mk:14s}  {code}     (before the sampler)")
        continue
    win = [s for t, s in samples if a - 10 <= t <= b + 10]
    if len(win) < 2:
        continue
    dt = f(win[-1]["utc"]) - f(win[0]["utc"])
    rate = lambda k: (win[-1][k] - win[0][k]) / dt if dt else 0.0
    loads = [s["load1"] for s in win]
    ov = sum(1 for x in other if x[0] < b and x[1] > a)
    row = (t0, b - a, tree, mk, code, st.mean(loads), max(loads), rate("mem_full_us"), rate("mem_some_us"), rate("cpu_some_us"),
           max(s["cur"] for s in win) / 1e9, win[0]["max"] / 1e9, ov)
    rows.append(row)
    print(f"{t0}  {row[1]:7.1f}  {tree:20s}  {mk:14s}  {code}     {row[5]:5.1f}/{row[6]:5.1f}     {row[7]:10.0f}  {row[8]:12.0f}  {row[9]:12.0f}  {row[10]:5.2f}/{row[11]:5.2f}  {ov}")
print("\neach land phase over 30 s (every one, before the sampler too) beside its controls: the other land phases within 10 min of it,"
      " any tree (wall s, tree, minutes after), and the excess over their median")
for a, b, t0, tree, mk, code, _ in land:
    if b - a <= 30:
        continue
    ctl = [(x[1] - x[0], x[3], (x[0] - a) / 60) for x in land if x[0] != a and abs(x[0] - a) <= 600]
    cs = ", ".join(f"{w:.1f} s {tr} {m:+.1f} min" for w, tr, m in ctl) or "none"
    ex = f"{b - a - st.median(w for w, _, _ in ctl):.1f} s" if ctl else "n/a"
    print(f"  {t0}  {b-a:6.1f} s  {tree}  controls: {cs}; excess over their median {ex}")
slow = [r for r in rows if r[1] > 30]
fast = [r for r in rows if r[1] <= 30]
for label, sel in (("slow (> 30 s)", slow), ("the rest", fast)):
    if sel:
        print(f"\n{label}: {len(sel)} phases; median wall {st.median(r[1] for r in sel):.1f} s; median load1 {st.median(r[5] for r in sel):.1f};"
              f" median memfull {st.median(r[7] for r in sel):.0f} us/s; median memsome {st.median(r[8] for r in sel):.0f} us/s;"
              f" median cpusome {st.median(r[9] for r in sel):.0f} us/s; median overlapping {st.median(r[12] for r in sel)}")
