"""The sharpest turn (degrees) at any vertex of each pool hamlet's recorded brook."""
import os as _os
POOL = "pool/hamlets" if _os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
import json, math, sys
for m in sys.argv[1:]:
    M = json.load(open(POOL + f"/{m}/{m}.json"))
    out = []
    for s in M.get("streams", []):
        p = s["poly"]
        out.append(round(max(abs((math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0])) + 180) % 360 - 180) for a, b, c in zip(p, p[1:], p[2:])), 1))
    print(m, out)
