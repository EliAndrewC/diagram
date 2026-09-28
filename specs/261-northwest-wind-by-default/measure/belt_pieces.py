"""How many pieces a hamlet's drawn windbreak is in: the tree crowns within 20 ft of the belt's outline, linked where two
crowns stand within 30 ft of each other edge to edge (the settlement-review's own measure of a hole in the belt).
With a git revision after `--rev`, the manifest at that commit is read instead of the working tree's."""
import json, math, os, subprocess, sys
POOL = "pool/hamlets" if os.path.isdir("pool/hamlets") else ".claude/skills/diagram/pool/hamlets"
def seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
def inside(p, poly):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1) + x1:
            c = not c
    return c
def pieces(M):
    g = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]
    P = [tuple(q) for q in g["poly"]]
    flat = M.get("tree_crowns", [])
    cr = [c for c in zip(flat[0::3], flat[1::3], flat[2::3]) if inside((c[0], c[1]), P) or min(seg((c[0], c[1]), a, b) for a, b in zip(P, P[1:] + P[:1])) <= 20.0]
    parent = list(range(len(cr)))
    def f(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    cell = {}
    for i, c in enumerate(cr):
        cell.setdefault((int(c[0] // 60), int(c[1] // 60)), []).append(i)
    for i, c in enumerate(cr):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in cell.get((int(c[0] // 60) + dx, int(c[1] // 60) + dy), []):
                    if j > i and math.dist(c[:2], cr[j][:2]) - c[2] - cr[j][2] <= 30.0:
                        parent[f(i)] = f(j)
    return len({f(i) for i in range(len(cr))}), len(cr)
args = sys.argv[1:]; rev = None
if args and args[0] == "--rev":
    rev, args = args[1], args[2:]
for m in args:
    M = json.loads(subprocess.check_output(["git", "show", f"{rev}:.claude/skills/diagram/pool/hamlets/{m}/{m}.json"], cwd=os.path.dirname(os.path.abspath(POOL + "/../../../../x")))) if rev else json.load(open(f"{POOL}/{m}/{m}.json"))
    print(m, "pieces, crowns:", pieces(M))
