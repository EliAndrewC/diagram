"""Every figure the pool notes' feature-261 entries state, derived from the shipped manifests (and main's, from the review
snapshot): the house moves, the belt's clumps, bearing and arc, the copse, the entrance board's distance from the last
join and the ways out that pass it, the connector's first leg, the drawn aspect, the homestead plots and the nearest dry
ground, the brook's longest straight run on the page. Run from the repository root or the skill directory."""
import json, math, os, subprocess, sys
here = os.getcwd()
skill = here if os.path.isdir(os.path.join(here, "pool/hamlets")) else os.path.join(here, ".claude/skills/diagram")
sys.path.insert(0, skill)
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes, kosatsuba_handover, routes_missed  # noqa: E402
root = subprocess.check_output(["git", "-C", skill, "rev-parse", "--show-toplevel"], text=True).strip()


def straightest(pts, tol=3.1):
    best = 0.0
    for i in range(len(pts)):
        for j in range(i + 2, len(pts)):
            a, b = pts[i], pts[j]; span = math.dist(a, b)
            if span > best and all(abs((b[0] - a[0]) * (a[1] - q[1]) - (a[0] - q[0]) * (b[1] - a[1])) / span <= tol for q in pts[i : j + 1]):
                best = span
    return best


for m in sys.argv[1:]:
    M = json.load(open(f"{skill}/pool/hamlets/{m}/{m}.json"))
    main = json.load(open(f"{root}/.git/review-snapshot/{m}/main/{m}.json"))
    hs = [(h["x"], h["y"]) for h in M["houses"]]
    moves = sorted(min(math.dist(p, (q["x"], q["y"])) for q in main["houses"]) for p in hs)
    cx, cy = sum(p[0] for p in hs) / len(hs), sum(p[1] for p in hs) / len(hs)
    belt = [g for g in M["village_groves"] if g["role"] == "windbreak"][0]["clumps"]
    bs = [math.degrees(math.atan2(c[0] - cx, -(c[1] - cy))) % 360 for c in belt]
    mean = math.degrees(math.atan2(sum(math.sin(math.radians(b)) for b in bs), sum(math.cos(math.radians(b)) for b in bs))) % 360
    rel = sorted(((b - mean + 180) % 360) - 180 for b in bs)
    k = M["kosatsuba"][-1]; hand = kosatsuba_handover(M)
    conn = [ln for ln in M["lanes"] if ln.get("connector")][0]["pts"]
    leg = math.degrees(math.atan2(conn[1][0] - conn[0][0], -(conn[1][1] - conn[0][1]))) % 360
    dry = [d["poly"] for d in M.get("dry_plots") or []]
    near_dry = sorted(min(math.dist(p, (sum(q[0] for q in d) / len(d), sum(q[1] for q in d) / len(d))) for d in dry) for p in hs) if dry else []
    x0, y0, w, h = M["meta"]["view"]
    brook = [(float(a), float(b)) for a, b in (M.get("streams") or [{"poly": []}])[0]["poly"] if x0 <= a <= x0 + w and y0 <= b <= y0 + h]
    blen = sum(math.dist(a, b) for a, b in zip(brook, brook[1:]))
    print(m, {
        "houses": len(hs), "move_median_ft": round(moves[len(moves) // 2]), "roll": M["meta"].get("roll_attempt"),
        "belt_clumps": len(belt), "belt_bearing": round(mean), "belt_arc": round(rel[-1] - rel[0]),
        "copse": (M["meta"].get("copse_clumps"), M["meta"].get("copse_house_ft")),
        "board_from_join_ft": round(math.dist((k["x"], k["y"]), hand), 1) if hand else None,
        "ways_missing_board": routes_missed(departure_routes(M), k["x"], k["y"], 20.0) if hand else None,
        "connector_first_leg": round(leg), "aspect": M["meta"].get("cluster_aspect_drawn"),
        "unhonored": M["meta"].get("cluster_shape_unhonored"), "homestead_fields": M["meta"].get("homestead_fields"),
        "near_dry_median_ft": round(near_dry[len(near_dry) // 2]) if near_dry else None,
        "brook_straight_ft": (round(straightest(brook)), round(blen)) if len(brook) > 2 else None,
    })
