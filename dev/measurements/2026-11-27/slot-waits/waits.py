"""451 T420 (1)-(2): each wide `slot-wait` of 5 s or more from 2026-11-27T00:20Z to this tree's handout for T420, the build it
lay in, what told it wide, and who held the two wide slots meanwhile. Read-only: the clone's event logs (every feature's, a line
written to two logs counted once) and the pool's log. Run: python3 -I waits.py > waits.txt

Holders are read from `Phase` spans: a slot is held by a compiling cargo call (`rustc.rs` `cargo_in`, `cover.rs`), so a holder is
a `build` span told wide (its own `slot-wait` cut off its head), a `lint` span (a lint whose every pass took the lane is dropped),
a `cover-build` span or a `prewarm` span (the pre-warm takes a slot only with another spare, `prewarm.rs`). `format`, `cover-run`, a `test` span (side by side: the executables run with no slot, only doc tests take one, unsaid) and a
gate's non-cargo steps hold none. The lines name no slot index, so a wait whose
window shows fewer than two holders is said so ("unseen"): a stage's `cargo run` or a span still open at the end."""
import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

SINCE = "2026-11-27T00:20"
UNTIL = "2026-11-27T03:56:52"  # T420's handout of this tree: its own runs are not in the window
CLONE = "/diagram/.clones/diagram-backlog/.git"
RUST = "/diagram/.clones/diagram-backlog/rust"
MIN_WAIT = 5.0
# A MEASUREMENT'S OWN WAITS, not contention: 451 T355's lint-wait.sh held both wide slots of a SCRATCH slot directory
# (`L7R_BUILD_SLOT_DIR`) with `flock <file> sleep 60` around `make builder-checks` of reviews in this tree (its transcript: the script
# written 01:48:50Z, its last row "knob-off" 02:01:25Z); the event log has no field that tells such a line from a real one.
SYNTH = [("/diagram/.clones/diagram-backlog-t270", "2026-11-27T01:48:50", "2026-11-27T02:01:30", "451 T355 lint-wait.sh (scratch slots)")]
P = lambda s: datetime.fromisoformat(s.rstrip("Z"))
short = lambda c: c.rsplit("/", 1)[-1] if c else "?"

phase, edits, seen = [], [], set()
for f in sorted(glob.glob(f"{CLONE}/l7r-events/*.jsonl")):
    for line in open(f):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("ev") == "Phase" and SINCE <= r.get("t0", "") < UNTIL:
            k = (r.get("src"), r.get("step"), r["t0"], r.get("clone"), tuple(r.get("crates", [])))
            if k in seen:
                continue
            seen.add(k)
            r["a"], r["b"] = P(r["t0"]), P(r["t1"])
            r["d"] = (r["b"] - r["a"]).total_seconds()
            phase.append(r)
        elif r.get("ev") == "PostToolUse" and r.get("tool") in ("Edit", "Write") and r.get("path") and SINCE <= r["t"] < UNTIL:
            k = ("edit", r["t"], r["path"])
            if k not in seen:
                seen.add(k)
                edits.append((P(r["t"]), r["path"]))
phase.sort(key=lambda r: r["a"])
pool = [json.loads(l) for l in open(f"{CLONE}/builder-pool.log")]
takes = [(P(r["utc"]), r["tree"]) for r in pool if r["event"] == "take" and r["utc"] < UNTIL]

# the crates' path dependencies, from their manifests: crate dir (from the repo root) -> the dirs it builds on, transitively
deps = {}
for m in glob.glob(f"{RUST}/**/Cargo.toml", recursive=True):
    if "/target/" in m:
        continue
    d = os.path.dirname(m)
    rel = os.path.relpath(d, os.path.dirname(RUST))
    deps[rel] = {os.path.normpath(os.path.relpath(os.path.join(d, p), os.path.dirname(RUST)))
                 for p in re.findall(r'path\s*=\s*"([^"]+)"', open(m).read())}
def closure(c, out=None):
    out = set() if out is None else out
    for x in deps.get(c, ()):
        if x not in out:
            out.add(x)
            closure(x, out)
    return out
def owner(path):
    rel = path.split("/", 5)[-1] if path.startswith("/diagram/.clones/") else path
    best = max((c for c in deps if rel.startswith(c + "/")), key=len, default=None)
    return best, rel

by = lambda s: [r for r in phase if r.get("src") == "rust" and r["step"] == s]
waits, smalls, tells = by("slot-wait"), by("slot-small"), by("slot-tell")
inside = lambda x, r: r["a"] <= x["a"] <= r["b"] and x.get("clone") == r.get("clone")
taken = lambda clone, at: max((u for u, tr in takes if tr == clone and u <= at), default=None)

# a lane wait is one a `slot-small` line starts with (its span is the wait for the lane)
# runs that took NO real slot, so their spans hold none: 451 T355's lint-run.sh memory runs in this tree, `L7R_BUILD_SLOTS=0`
# (its transcript: first run 01:40:02Z; its lint-wait.sh rows follow from 01:48:50Z, in SYNTH)
NO_SLOT = [("/diagram/.clones/diagram-backlog-t270", "2026-11-27T01:40:00", "2026-11-27T01:48:50", "451 T355 lint-run.sh (L7R_BUILD_SLOTS=0)")]
def synth(w):
    return next((why for c, a, b, why in SYNTH if w["clone"] == c and a <= w["t0"] < b), None)
def lane(w):
    return any(s["clone"] == w["clone"] and abs((s["a"] - w["a"]).total_seconds()) < 0.05 for s in smalls)

# the wide holders' spans
holders = []
for r in phase:
    if r.get("src") != "rust":
        continue
    s, a, b = r["step"], r["a"], r["b"]
    if s in ("build", "lint", "test"):
        own_small = [x for x in smalls if inside(x, r)]
        own_tells = [x for x in tells if inside(x, r) or (x["clone"] == r["clone"] and 0 <= (r["a"] - x["b"]).total_seconds() < 0.05)]
        if s == "build" and own_small:
            continue
        if s == "lint" and own_tells and all(t["code"] == 0 for t in own_tells):
            continue
        if s == "test":
            continue  # `make rust-test`/`builder-checks` run "test" side by side (`rustc.rs` owed_together, `side.rs`): the test
            # executables by `run_in`, no slot; only a crate's doc tests (`cargo test --doc`) take one, which the line does not say
        own_wait = [x for x in waits if inside(x, r) and not lane(x)]
        if own_wait:
            a = max(x["b"] for x in own_wait)
    elif s not in ("cover-build", "prewarm"):
        continue
    if any(r["clone"] == c and x <= r["t0"] < y for c, x, y, _ in SYNTH + NO_SLOT):
        continue  # a synthetic run's builds held its scratch slots, not the machine's
    kind = {"cover-build": "coverage build", "prewarm": "pre-warm"}.get(s, f"{s} (told wide)" if s != "test" else "cargo test run")
    where = "clone" if r["clone"].endswith("/diagram-backlog") else ("landing tree" if r["clone"].endswith("-land") else "pool/other tree")
    holders.append(dict(a=a, b=b, kind=kind, make=r.get("make"), clone=r["clone"], where=where, crates=r.get("crates", []), step=s))

def reason(w, step):
    """What told this build wide: the `slot-tell` line before the wait in its tree and crate, and what came before it."""
    clone = w["clone"]
    crate = step["crates"][0] if step and step.get("crates") else None
    if step and step["step"] == "cover-build":
        return "coverage build (never told: always wide)"
    t = max((x for x in tells if x["clone"] == clone and x["a"] <= w["a"] and (w["a"] - x["a"]).total_seconds() < 120
             and (crate is None or x["crates"][:1] == [crate])), key=lambda x: x["a"], default=None)
    if step and step["step"] == "lint" and t is not None and not inside(t, step):
        t = None  # a lint pass is told inside its own span (T355, about 01:53Z); a test build's telling before it is not the lint's
    if t is None:
        return "untold (no slot-tell: a FRESH run, the landing's gate, or a step no telling covers)"
    if t["code"] == 0:
        return "told alone, but waited wide (?)"
    tk = taken(clone, t["a"])
    kind = "lint" if step and step["step"] == "lint" else "test"
    earlier = [x for x in tells if x["clone"] == clone and x["crates"][:1] == t["crates"][:1] and x["a"] < t["a"] - timedelta(seconds=30 if kind == "lint" else 0.5)
               and (tk is None or x["a"] >= tk) and x.get("make") != "prewarm"]
    if tk is not None and not earlier:
        return "first build of this crate after the handout"
    # edits in this tree since the crate's last build, to the crates it builds on
    last = max(x["a"] for x in earlier) if earlier else (tk or P(SINCE))
    deps_of = closure(crate) if crate else set()
    ed = defaultdict(int)
    own = 0
    for at, path in edits:
        if last <= at <= t["a"] and path.startswith(clone + "/"):
            o, rel = owner(path)
            if o in deps_of:
                ed[o] += 1
            elif o == crate:
                own += 1
            elif rel.endswith(("Cargo.toml", "Cargo.lock")):
                ed["(a manifest)"] += 1
    prev = [x for x in phase if x.get("src") == "rust" and x["step"] == step["step"] and x["clone"] == clone
            and x.get("crates", [])[:1] == [crate] and x["b"] <= t["a"] and x["b"] >= last] if step else []
    failed = prev and prev[-1].get("code", 0) != 0
    if ed:
        return "moved dependency: " + ", ".join(f"{short(k)} ({v} edits)" for k, v in sorted(ed.items()))
    if failed:
        return "the last wide build of it failed (a failed wide build keeps no key)"
    if clone.endswith("/diagram-backlog") or clone.endswith("-land"):
        return "a carry or landing moved files (no Edit in this tree since its last build)"
    return f"other: no edit to a dependency seen ({own} own-crate edits) - a carry, a sync or a lint key"

print(f"window {SINCE}Z to {UNTIL}Z; slot-wait lines {len(waits)}, {sum(w['d'] for w in waits):.1f} s; "
      f"wide {sum(1 for w in waits if not lane(w))}, {sum(w['d'] for w in waits if not lane(w)):.1f} s; "
      f"lane {sum(1 for w in waits if lane(w))}, {sum(w['d'] for w in waits if lane(w)):.1f} s")
for name, pick in [("synthetic (a measurement's scratch slots)", lambda w: synth(w)), ("real wide", lambda w: not synth(w) and not lane(w)),
                   ("real lane", lambda w: not synth(w) and lane(w))]:
    ws = [w for w in waits if pick(w)]
    print(f"  {name}: {len(ws)}, {sum(w['d'] for w in ws):.1f} s; of 5 s or more {sum(1 for w in ws if w['d'] >= MIN_WAIT)}, "
          f"{sum(w['d'] for w in ws if w['d'] >= MIN_WAIT):.1f} s")
t367 = [w for w in waits if w["t0"] < "2026-11-27T03:30:03"]
print(f"  T367's window (to 03:30:03Z): {len(t367)} lines, {sum(w['d'] for w in t367):.1f} s, of them synthetic "
      f"{sum(w['d'] for w in t367 if synth(w)):.1f} s and in the lane {sum(w['d'] for w in t367 if lane(w) and not synth(w)):.1f} s")
big = [w for w in waits if not lane(w) and (w["d"] >= MIN_WAIT or not synth(w))]
print(f"wide waits of {MIN_WAIT:.0f} s or more, and every real wide wait whatever its length: {len(big)}, {sum(w['d'] for w in big):.1f} s\n")
kinds = defaultdict(float)
reasons = defaultdict(lambda: [0, 0.0])
for w in big:
    step = next((r for r in phase if r.get("src") == "rust" and r["step"] in ("build", "lint", "cover-build", "test") and inside(w, r)), None)
    if step is None:  # a coverage build's wait comes before its span
        step = next((r for r in phase if r.get("src") == "rust" and r["step"] == "cover-build" and r["clone"] == w["clone"]
                     and 0 <= (r["a"] - w["b"]).total_seconds() < 1), None)
    ran = (step["b"] - w["b"]).total_seconds() if step else float("nan")
    why = reason(w, step)
    real = not synth(w)  # the tables below count the real waits; a synthetic one is listed, its holders were a script's flock
    if real:
        reasons[why.split(":")[0]][0] += 1
        reasons[why.split(":")[0]][1] += w["d"]
    if synth(w):
        print(f"{w['t0'][11:19]} wait {w['d']:5.1f} s  tree {short(w['clone'])}  SYNTHETIC: {synth(w)} - its row in "
              f"dev/measurements/2026-11-27/lint-memory/lint-wait-rows.txt holds this wait; its holders were the script's flock\n")
        continue
    print(f"{w['t0'][11:19]} wait {w['d']:5.1f} s  tree {short(w['clone'])}  make {w.get('make')}  task {w.get('task')}")
    print(f"    in: {step and step['step']} {step and [short(c) for c in step.get('crates', [])]}  ran {ran:.1f} s after the wait (code {step and step.get('code')})")
    print(f"    told wide by: {why}")
    held = [h for h in holders if h["a"] < w["b"] and h["b"] > w["a"] and not (h["clone"] == w["clone"] and h["a"] >= w["a"])]
    for h in held:
        ov = (min(h["b"], w["b"]) - max(h["a"], w["a"])).total_seconds()
        kinds[(h["kind"], h["where"], h["make"])] += ov if real else 0
        print(f"    held: {h['kind']:18} {short(h['clone']):22} make {h['make']:15} {[short(c) for c in h['crates']][:4]} "
              f"{h['a'].strftime('%H:%M:%S')}-{h['b'].strftime('%H:%M:%S')} ({ov:.1f} s of the wait)")
    cover = sum((min(h["b"], w["b"]) - max(h["a"], w["a"])).total_seconds() for h in held)
    unseen = 2 * w["d"] - cover
    if unseen > 0.5:
        kinds[("unseen", "", "")] += unseen if real else 0
        print(f"    unseen: {unseen:.1f} slot-s of the 2 x {w['d']:.1f} the wait implies")
    print()
print("the REAL wide waits, told wide by (count, seconds waited):")
for k, (n, s) in sorted(reasons.items(), key=lambda x: -x[1][1]):
    print(f"  {n:3} {s:7.1f} s  {k}")
print("\nholders during the REAL wide waits (slot-seconds of overlap with a wait; two slots, so a wait of w s is 2w slot-s):")
tot = sum(kinds.values())
for k, s in sorted(kinds.items(), key=lambda x: -x[1]):
    print(f"  {s:7.1f} slot-s {100 * s / tot:5.1f}%  {k[0]:18} {k[1]:16} make {k[2]}")
print(f"  {tot:7.1f} slot-s total")

# the whole window: how busy were the two slots, by holder kind (slot-minutes), and how many seconds had both held
print("\nthe window's wide slot use by holder kind (minutes, overlapping spans summed):")
use = defaultdict(float)
for h in holders:
    use[(h["kind"], h["where"], h["make"])] += (h["b"] - h["a"]).total_seconds() / 60
for k, m in sorted(use.items(), key=lambda x: -x[1])[:20]:
    print(f"  {m:7.1f} min  {k[0]:18} {k[1]:16} make {k[2]}")
edges = sorted([(h["a"], 1) for h in holders] + [(h["b"], -1) for h in holders])
n, last, at = 0, None, defaultdict(float)
for t, dlt in edges:
    if last is not None:
        at[min(n, 3)] += (t - last).total_seconds()
    n, last = n + dlt, t
print("seconds with 0 / 1 / 2 / 3+ wide holders seen: " + " / ".join(f"{at[i]:.0f}" for i in range(4)))

# THE LANE'S WAITS: each wait for the small lane, and who held the lane (a build or lint pass that took it: its `slot-small` line's
# end to its span's end) - its tree, crate and how long that alone-told build ran
print("\nthe lane's waits (every one), the build told alone that waited and the lane's holder:")
lane_hold = []
for x in smalls:
    span = next((r for r in phase if r.get("src") == "rust" and r["step"] in ("build", "lint") and inside(x, r)), None)
    if span:
        lane_hold.append(dict(a=x["b"], b=span["b"], clone=span["clone"], crates=span.get("crates", []), step=span["step"], make=span.get("make")))
lane_total = defaultdict(float)
for w in [w for w in waits if lane(w) and not synth(w)]:
    step = next((r for r in phase if r.get("src") == "rust" and r["step"] in ("build", "lint") and inside(w, r)), None)
    ran = (step["b"] - w["b"]).total_seconds() if step else float("nan")
    print(f"{w['t0'][11:19]} wait {w['d']:5.1f} s  tree {short(w['clone'])} make {w.get('make')}  {step and step['step']} "
          f"{step and [short(c) for c in step.get('crates', [])]} ran {ran:.1f} s after")
    for h in lane_hold:
        if h["a"] < w["b"] and h["b"] > w["a"] and h["clone"] != w["clone"] or (h["clone"] == w["clone"] and h["b"] <= w["a"] + timedelta(seconds=0) and h["b"] > w["a"]):
            ov = (min(h["b"], w["b"]) - max(h["a"], w["a"])).total_seconds()
            if ov <= 0:
                continue
            lane_total[(h["step"], short(h["crates"][0]) if h["crates"] else "?")] += ov
            print(f"    lane held: {h['step']} {short(h['clone'])} make {h['make']} {[short(c) for c in h['crates']]} "
                  f"{h['a'].strftime('%H:%M:%S')}-{h['b'].strftime('%H:%M:%S')} ({(h['b'] - h['a']).total_seconds():.1f} s alone-told, {ov:.1f} s of the wait)")
print("lane holders during lane waits (s):", ", ".join(f"{k[0]} {k[1]} {v:.1f}" for k, v in sorted(lane_total.items(), key=lambda x: -x[1])))
lb = sorted((h["b"] - h["a"]).total_seconds() for h in lane_hold)
if lb:
    print(f"the lane's builds in the window: {len(lb)}, median {lb[len(lb) // 2]:.1f} s, longest {lb[-1]:.1f} s, over 10 s {sum(1 for x in lb if x > 10)}")

# where three or more wide holders are seen at once (two slots: the model over-counts there), which spans they are
edges = sorted([(h["a"], 1, i) for i, h in enumerate(holders)] + [(h["b"], -1, i) for i, h in enumerate(holders)])
live, last, shown = set(), None, 0
for t, dlt, i in edges:
    if last is not None and len(live) >= 3 and (t - last).total_seconds() > 1 and shown < 8:
        shown += 1
        print(f"3+ at {last.strftime('%H:%M:%S')} for {(t - last).total_seconds():.1f} s: " + "; ".join(
            f"{holders[j]['kind']} {short(holders[j]['clone'])} {holders[j]['make']} {[short(c) for c in holders[j]['crates']][:2]}" for j in sorted(live)))
    (live.add if dlt > 0 else live.discard)(i)
    last = t

# LEVER (4e): a build told alone that finds the lane held takes a FREE WIDE slot instead of waiting - how much of each lane wait
# had a wide slot free (fewer than two wide holders seen), at 0.1 s steps
print("\nthe lane's waits with a wide slot free (an alone-told build could have taken it):")
free_total = 0.0
for w in [w for w in waits if lane(w) and not synth(w)]:
    t, free = w["a"], 0.0
    while t < w["b"]:
        if sum(1 for h in holders if h["a"] <= t < h["b"] and h["clone"] != w["clone"]) < 2:
            free += 0.1
        t += timedelta(seconds=0.1)
    free_total += min(free, w["d"])
    print(f"  {w['t0'][11:19]} {short(w['clone'])} wait {w['d']:5.1f} s, a wide slot free {min(free, w['d']):5.1f} s of it")
print(f"  total: {free_total:.1f} s of {sum(w['d'] for w in waits if lane(w) and not synth(w)):.1f} s")
