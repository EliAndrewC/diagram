"""Per pool hamlet: copse crowns, and how many stand more than 5 ft windward of their nearest belt crown (the wind is the
manifest's `meta.windward`, as a compass point)."""
import json, math, os, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
VEC = {"N": (0, -1), "NE": (0.7071, -0.7071), "E": (1, 0), "SE": (0.7071, 0.7071), "S": (0, 1), "SW": (-0.7071, 0.7071), "W": (-1, 0), "NW": (-0.7071, -0.7071)}
for m in sys.argv[1:]:
    M = json.load(open(f"{POOL}/{m}/{m}.json"))
    wx, wy = VEC[M["meta"]["windward"]]
    belt = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]["clumps"]
    cop = [g for g in M["village_groves"] if g["role"] == "copse"][0]["clumps"]
    out = sum(1 for c in cop if (lambda b: (c[0] - b[0]) * wx + (c[1] - b[1]) * wy > 5.0)(min(belt, key=lambda q: math.dist(q, c))))
    print(m, M["meta"].get("copse_siting"), "copse", len(cop), "windward of the belt", out)
