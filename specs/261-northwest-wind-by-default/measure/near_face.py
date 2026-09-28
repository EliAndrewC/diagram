"""How close the windbreak's near face comes to a farmhouse center: per pool hamlet (or per manifest path given), the
least distance from any house center to the near face's polyline (its first `meta.belt_near_vertices` vertices), and
the house it is. The column rule stands the face `BELT_NEAR_FT` + the sun-lane offset from the house a column leads."""
import json, math, os, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
for arg in sys.argv[1:]:
    M = json.load(open(arg if arg.endswith(".json") else f"{POOL}/{arg}/{arg}.json"))
    P = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]["poly"]
    near = P[: int(M["meta"]["belt_near_vertices"])]
    d, h = min((min(segd((h["x"], h["y"]), a, b) for a, b in zip(near, near[1:])), (round(h["x"]), round(h["y"]))) for h in M["houses"])
    print(os.path.basename(arg), "nearest house to the near face", round(d, 1), "ft, house", h)
