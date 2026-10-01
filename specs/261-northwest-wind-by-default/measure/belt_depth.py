"""The windbreak band's depth ACROSS itself on the page, sampled every 5 ft along its near face: the distance from each
sample to the far face, where the nearest stretch of far face is not clamped to the canvas edge (there the page cuts the
band). Prints the thinnest, the median and the share over 120 ft (the record's 80-120, research/vegetation/), now and
at the commit the working tree came from. Where the near face ends is the engine's `meta.belt_near_vertices`."""
import json, math, os, statistics, subprocess, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
def depths(M):
    g = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]
    P = g["poly"]; n = int(M["meta"].get("belt_near_vertices") or len(P) // 2)
    near, far = P[:n], P[n:]
    x0, y0, w, h = M["meta"]["view"]
    W, H = float(M.get("W") or 1e9), float(M.get("H") or 1e9)
    edge = lambda q: q[0] <= 6.5 or q[1] <= 6.5 or q[0] >= W - 6.5 or q[1] >= H - 6.5
    segs = list(zip(far, far[1:])); free = [(a, b) for a, b in segs if not (edge(a) or edge(b))]
    out = []
    for a, b in zip(near[1:-2], near[2:-1]):
        k = max(1, int(math.dist(a, b) // 5))
        for i in range(k):
            p = (a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k)
            if not (x0 <= p[0] <= x0 + w and y0 <= p[1] <= y0 + h) or not free:
                continue
            d = min(segd(p, s, e) for s, e in segs)
            if d == min(segd(p, s, e) for s, e in free):
                out.append(d)
    return out
def summary(ds):
    return (round(min(ds), 1), round(statistics.median(ds), 1), f"{100 * sum(d > 120 for d in ds) / len(ds):.0f}%") if ds else None
for m in sys.argv[1:]:
    now = json.load(open(f"{POOL}/{m}/{m}.json"))
    try:
        head = json.loads(subprocess.check_output(["git", "show", f"HEAD:.claude/skills/diagram/pool/hamlets/{m}/{m}.json"], cwd=os.path.dirname(os.path.abspath(POOL)), stderr=subprocess.DEVNULL))
    except subprocess.CalledProcessError:
        head = None
    print(m, "depth (thinnest, median, over 120 ft): HEAD", summary(depths(head)) if head else None, "now", summary(depths(now)))
