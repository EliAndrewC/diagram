"""The windbreak band's thinnest depth ACROSS itself on the page: each near-face vertex's distance to the far face."""
import os as _os
POOL = "pool/hamlets" if _os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
import json, math, subprocess, sys
def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
def thin(M):
    g = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]
    P = g["poly"]; n = len(P) // 2
    near, far = P[:n], P[n:]
    x0, y0, w, h = M["meta"]["view"]
    ds = [min(segd(p, a, b) for a, b in zip(far, far[1:])) for p in near[1:-1] if x0 <= p[0] <= x0 + w and y0 <= p[1] <= y0 + h]
    return round(min(ds), 1) if ds else None
for m in sys.argv[1:]:
    head = json.loads(subprocess.check_output(["git", "-C", "/diagram/.clones/diagram-kashikawa", "show", f"HEAD:.claude/skills/diagram/pool/hamlets/{m}/{m}.json"]))
    now = json.load(open(POOL + f"/{m}/{m}.json"))
    print(m, "thinnest band depth across itself ft: HEAD", thin(head), "now", thin(now))
