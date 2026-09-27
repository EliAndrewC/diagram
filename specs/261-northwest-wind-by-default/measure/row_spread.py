"""Per pool hamlet: how the farmhouses fall into ranks - houses grouped by depth from the field (within 40 ft), and each
group's spread in feet. A lattice shows ranks of 5 ft or less."""
import json, math, os, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
for m in sys.argv[1:]:
    M = json.load(open(f"{POOL}/{m}/{m}.json"))
    d = math.radians(float(M["meta"].get("down_deg") or 0.0))
    hs = sorted(h["x"] * math.cos(d) + h["y"] * math.sin(d) for h in M["houses"])
    groups, cur = [], [hs[0]]
    for v in hs[1:]:
        if v - cur[-1] <= 40.0:
            cur.append(v)
        else:
            groups.append(cur); cur = [v]
    groups.append(cur)
    print(m, "ranks", [(len(g), round(g[-1] - g[0], 1)) for g in groups if len(g) > 1])
