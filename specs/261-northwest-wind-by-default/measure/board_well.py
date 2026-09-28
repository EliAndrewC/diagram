"""Per pool hamlet: the recorded `meta.kosatsuba_well_ft` beside the drawn board's distance to its nearest well."""
import json, math, os, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
for m in sys.argv[1:]:
    M = json.load(open(f"{POOL}/{m}/{m}.json"))
    k = M["kosatsuba"][-1]
    drawn = min(math.hypot(k["x"] - w["x"], k["y"] - w["y"]) for w in M["wells"]) * float(M["meta"].get("ftpx") or 1)
    print(m, "recorded", M["meta"].get("kosatsuba_well_ft"), "drawn", round(drawn, 1))
