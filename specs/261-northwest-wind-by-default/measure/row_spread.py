"""Per pool hamlet (optionally at a git revision with `--rev <sha>`): the farmhouses grouped into screen rows by y and
columns by x (a neighbor within 40 ft continues the group), each group of three or more with its spread in feet. The
settlement-review's measure of a lattice: ranks of 5 ft or less."""
import json, os, subprocess, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
def groups(vals):
    vals = sorted(vals); out, cur = [], [vals[0]]
    for v in vals[1:]:
        (cur.append(v) if v - cur[-1] <= 40.0 else (out.append(cur), cur := [v]))
    out.append(cur)
    return [(len(g), round(g[-1] - g[0], 1)) for g in out if len(g) >= 3]
args = sys.argv[1:]; rev = None
if args and args[0] == "--rev":
    rev, args = args[1], args[2:]
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
for m in args:
    M = json.loads(subprocess.check_output(["git", "-C", root, "show", f"{rev}:.claude/skills/diagram/pool/hamlets/{m}/{m}.json"])) if rev else json.load(open(f"{POOL}/{m}/{m}.json"))
    print(m, "rows", groups([h["y"] for h in M["houses"]]), "columns", groups([h["x"] for h in M["houses"]]))
