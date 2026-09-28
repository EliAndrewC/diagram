"""How far each farmhouse of a pool hamlet stands from the nearest farmhouse of the same map at a git revision:
`house_moves.py <rev> <map>...` prints the moves that are not zero, and the map's meta.homestead_fields then and now."""
import json, math, os, subprocess, sys
here = os.getcwd()
skill = here if os.path.isdir(os.path.join(here, "pool/hamlets")) else os.path.join(here, ".claude/skills/diagram")
root = subprocess.check_output(["git", "-C", skill, "rev-parse", "--show-toplevel"], text=True).strip()
rev = sys.argv[1]
for m in sys.argv[2:]:
    now = json.load(open(f"{skill}/pool/hamlets/{m}/{m}.json"))
    then = json.loads(subprocess.check_output(["git", "-C", root, "show", f"{rev}:.claude/skills/diagram/pool/hamlets/{m}/{m}.json"]))
    moves = sorted(round(min(math.dist((a["x"], a["y"]), (b["x"], b["y"])) for b in then["houses"]), 1) for a in now["houses"])
    print(m, "moved", [v for v in moves if v > 0.05], "homestead_fields", then["meta"].get("homestead_fields"), "->", now["meta"].get("homestead_fields"))
