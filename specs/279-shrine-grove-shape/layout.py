"""Feature 279 (from 268 T08/T09 and 270): lay out the Hoshigaoka shrine grove ONCE, in sheet px, and emit
(1) the village-map fragments (map px = sheet px / 6 about the hall) and manifest additions,
(2) the tree list for the sheet. Pure Python; no engine import. Deterministic."""

import json
import math
import random
import sys

OUT = sys.argv[1]

# sheet <-> map: the hall's center is sheet (440, 500) = map (392, 1074); 6 sheet px = 1 map px
def to_map(x, y):
    return (392 + (x - 440) / 6, 1074 + (y - 500) / 6)

# The grove (the precinct): a near-rectangle, sheet px
GX0, GY0, GX1, GY1 = 220.0, 170.0, 630.0, 816.0  # the precinct (research 124) - the ground, not the wood
# THE WOOD (feature 279, research religion-and-death 129): AT THE SIDES - the hall stands at the top of its slope and
# the approach climbs to it from the south, so the candidates are behind-and-sides and sides; the roll on the map's
# name gave sides. Two flanks, from about the hall's back line down past it to ragged tips; the ground behind the hall
# (the well and its path) and the lower approach are open. Each flank's edge is its crowns' own (a guess): a
# smooth-noise outline about a base shape, never a ruled line.
_WEST = [(206, 372), (262, 352), (300, 368), (292, 420), (270, 470), (264, 540), (276, 596), (322, 622), (356, 672),
         (344, 722), (318, 772), (276, 792), (232, 770), (204, 700), (186, 600), (190, 500), (196, 430)]
_EAST = [(548, 300), (600, 282), (652, 300), (684, 370), (690, 460), (676, 560), (650, 628), (612, 650), (574, 640),
         (560, 610), (572, 560), (576, 480), (566, 440), (548, 410), (536, 350)]
def _resample(poly, step=10.0):
    pts = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        pts += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
    return pts
def _noisy(poly, seed=279):
    pts = _resample(poly)
    rr = random.Random(seed)
    waves = [(f, a, rr.uniform(0, 2 * math.pi)) for f, a in ((2, 12.0), (3, 12.0), (5, 9.0), (9, 8.0), (14, 7.0), (22, 7.0), (34, 5.0))]
    n = len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        (px, py), (qx, qy) = pts[i - 1], pts[(i + 1) % n]
        tx, ty = qx - px, qy - py
        tl = math.hypot(tx, ty) or 1.0
        nx, ny = ty / tl, -tx / tl  # outward normal for a clockwise ring in y-down coordinates
        d = sum(a * math.sin(2 * math.pi * f * i / n + ph) for f, a, ph in waves)
        out.append((round(x + nx * d, 1), round(y + ny * d, 1)))
    return out
REGIONS = [_noisy(_WEST, 2791), _noisy(_EAST, 2794)]
REGION = [p for r in REGIONS for p in r]  # every outline point, for the bounding box


def in_wood(x, y):
    return any(in_poly(x, y, r) for r in REGIONS)
CLEAR = (272.0, 394.0, 566.0, 672.0)  # the clearing's bounding box (the frame of the ragged patch below)
# THE CLEARING IS A RAGGED PATCH hugging what it holds (research 'Why does that swept ground have a ragged edge?'):
# the sanctuary behind the hall, the hall and its eaves, the kitchen garden and privy at the west gable, the
# forecourt before the step - never a ruled rectangle (settlement-review round 2, 2026-09-27)
_CLEAR_CORE = [(414, 400), (440, 390), (466, 400), (474, 432), (552, 440), (564, 500), (560, 560), (566, 610), (530, 648),
               (510, 672), (372, 672), (350, 640), (318, 600), (276, 574), (272, 500), (276, 456), (318, 442),
               (360, 432), (404, 430)]
_cr = random.Random(2682)
CLEAR_POLY = [(x + _cr.uniform(-5, 5), y + _cr.uniform(-5, 5)) for x, y in _CLEAR_CORE]          # the swept clearing: hall, sanctuary, garden, privy, forecourt
APPROACH = (410.0, 548.0, 470.0, 820.0)       # the approach corridor with the arches' span
SACRED = (518.0, 746.0, 45.0)                 # the sacred tree beside the approach (center, canopy r)
WELL = (440.5, 176.5, 30.0)                   # the map's shrine well + its pad
LABELS_OLD = [(308.0, 594.0, 348.0, 614.0), (412.0, 332.0, 514.0, 356.0), (374.0, 598.0, 412.0, 616.0), (536.0, 672.0, 596.0, 692.0)]  # seated captions: sanctuary, basin, sacred tree
PATH = ((330.0, 440.0), (426.0, 184.0))  # from the clearing's north-west edge to the well       # the household's footpath to the well, from the clearing's NW
PATH_HALF = 11.0
BASIN = (398.0, 570.0)


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def in_poly(x, y, poly):
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def poly_dist(x, y, poly):
    return min(seg_dist((x, y), a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


def rect_gap(x, y, r):
    """Distance from a circle's edge to each exclusion (negative = overlap)."""
    return r


def clear_of(x, y, r):
    # an edge crown may straddle the grove's edge by up to half its crown, so the wood's edge is ragged, not a file
    if not in_wood(x, y) or x - r < 154 or x + r > 698:
        return False
    if in_poly(x, y, CLEAR_POLY) or poly_dist(x, y, CLEAR_POLY) < r + 2:
        return False
    for (x0, y0, x1, y1) in (APPROACH, *LABELS):
        nx, ny = min(max(x, x0), x1), min(max(y, y0), y1)
        if math.hypot(x - nx, y - ny) < r + 2:
            return False
    sx, sy, sr = SACRED
    if math.hypot(x - sx, y - sy) < r + sr:
        return False
    wx, wy, wr = WELL
    if math.hypot(x - wx, y - wy) < r + wr:
        return False
    if seg_dist((x, y), *PATH) < r + PATH_HALF:
        return False
    return True


LABELS = []  # set from the seated captions after the first seat-label pass
import os
if os.path.exists(OUT + '.labels'):
    LABELS = json.load(open(OUT + '.labels'))
rng = random.Random(2794)
trees = []  # (x, y, r) sheet px
# dart-throwing, big crowns first, then fill with smaller ones: canopies may touch, never overlap
for r_lo, r_hi, tries in ((25.0, 30.0, 80000), (19.5, 25.0, 120000)):
    for _ in range(tries):
        r = rng.uniform(r_lo, r_hi)
        x, y = rng.uniform(160, 692), rng.uniform(150, 780)
        if not clear_of(x, y, r):
            continue
        if any(math.hypot(x - tx, y - ty) < 0.55 * (r + tr) for tx, ty, tr in trees):
            continue
        trees.append((round(x, 1), round(y, 1), round(r, 1)))

area_px = sum(abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(R, R[1:] + R[:1]))) / 2 for R in REGIONS)
area_sqft = area_px / 9.0
_cov = sum(1 for gx in range(int(GX0), int(GX1), 4) for gy in range(int(GY0), int(GY1), 4) if in_wood(gx, gy) and any(math.hypot(gx - tx, gy - ty) <= tr for tx, ty, tr in trees + [SACRED]))
_open = sum(1 for gx in range(int(GX0), int(GX1), 4) for gy in range(int(GY0), int(GY1), 4) if in_wood(gx, gy) and (clear_of(gx, gy, 0.0) or any(math.hypot(gx - tx, gy - ty) <= tr for tx, ty, tr in trees + [SACRED])))
canopy = _cov * 16.0
canopy_of_allowed = _cov / max(_open, 1)
clear_px = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(CLEAR_POLY, CLEAR_POLY[1:] + CLEAR_POLY[:1]))) / 2
meas = {
    "precinct_sheet_px": [GX0, GY0, GX1, GY1],
    "grove_bbox_sheet_px": [min(x for x, _ in REGION), min(y for _, y in REGION), max(x for x, _ in REGION), max(y for _, y in REGION)],
    "grove_sqft": round(area_sqft),
    "grove_tsubo": round(area_sqft / 35.58, 1),
    "clearing_share": round(clear_px / area_px, 3),
    "hall_share": round((180 * 144) / area_px, 3),
    "trees": len(trees),
    "canopy_share": round(canopy / area_px, 3),
    "canopy_of_allowed_ground": round(canopy_of_allowed, 3),
}

# ---- the village map ----
PAL = [("#7C9A4E", "#3C5526"), ("#6E8B43", "#3C5526"), ("#496733", "#3C5526")]
map_trees = []
parts = ['<g id="shrine-grove">']
# the grove's floor: a ragged outline about the precinct (the wood's edge is not ruled), then the swept clearing
edge = list(REGIONS[0])  # the wood's floor is the region: its edge the wood's own (feature 279)
for _ring in REGIONS:
    parts.append('<polygon points="' + " ".join(f"{to_map(x, y)[0]:.1f},{to_map(x, y)[1]:.1f}" for x, y in _ring) + '" fill="#B9BE8A" fill-opacity="0.85"/>')
FLOOR = edge
parts.append('<polygon points="' + " ".join(f"{to_map(x, y)[0]:.1f},{to_map(x, y)[1]:.1f}" for x, y in CLEAR_POLY) + '" fill="#E6DCC4"/>')
# the approach's 10 ft gravel under the arches, from the step to the grove's edge (as the sheet draws it)
_ax0, _ay0 = to_map(425, 554); _ax1, _ay1 = to_map(455, 816)
parts.append(f'<rect x="{_ax0:.1f}" y="{_ay0:.1f}" width="{_ax1 - _ax0:.1f}" height="{_ay1 - _ay0:.1f}" fill="#D9CFB4"/>')
for i, (x, y, r) in enumerate(trees):
    mx, my = to_map(x, y)
    mr = r / 6
    fill, stroke = PAL[i % 3]
    parts.append(f'<ellipse cx="{mx + 0.4:.1f}" cy="{my + 0.9:.1f}" rx="{mr:.1f}" ry="{mr * 0.72:.1f}" fill="#59703E" fill-opacity="0.30"/>')
    parts.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{mr:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="0.6"/>')
    parts.append(f'<circle cx="{mx - mr * 0.3:.1f}" cy="{my - mr * 0.3:.1f}" r="{mr * 0.4:.1f}" fill="#9DB46A" opacity="0.6"/>')
    map_trees.append([round(mx, 1), round(my, 1)])
smx, smy = to_map(SACRED[0], SACRED[1])
parts.append(f'<circle cx="{smx:.1f}" cy="{smy:.1f}" r="{SACRED[2] / 6:.1f}" fill="#4F6E36" stroke="#2E4220" stroke-width="0.8"/>')
parts.append(f'<circle cx="{smx:.1f}" cy="{smy:.1f}" r="1.7" fill="none" stroke="#F2EBC8" stroke-width="1.0" stroke-dasharray="0.9 0.5"/>')
bmx, bmy = to_map(*BASIN)
# the basin drawn at 3 map px (6 ft) where it is 3 ft: a map drawing convention so it can be seen at all
parts.append(f'<rect x="{bmx - 1.5:.1f}" y="{bmy - 1.5:.1f}" width="3" height="3" fill="#9AA1A4" stroke="#43403A" stroke-width="0.5"/>')
(pax, pay), (pbx, pby) = to_map(*PATH[0]), to_map(*PATH[1])
parts.insert(3, f'<line x1="{pax:.1f}" y1="{pay:.1f}" x2="{pbx:.1f}" y2="{pby:.1f}" stroke="#E6DCC4" stroke-width="2" stroke-linecap="round"/>')
parts.append("</g>")
grove_svg = "".join(parts)

# the seven arches at the pitch, in plan (torii_plan_svg at ftpx 2, span 16)
s2, beam = 4.0, 1.9
post = beam * 1.35
p2 = s2 * 12 / 19
torii_svg = "".join(
    f'<g transform="translate(392,{1088 + 6 * i})"><line x1="{-s2:.1f}" y1="0" x2="{s2:.1f}" y2="0" stroke="#A03020" stroke-width="{beam:.2f}"/>'
    f'<rect x="{-p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/>'
    f'<rect x="{p2 - post / 2:.2f}" y="{-post / 2:.2f}" width="{post:.2f}" height="{post:.2f}" fill="#7A2418"/></g>'
    for i in range(7)
)
def _ring_of(x, y):
    return min(range(len(REGIONS)), key=lambda k: poly_dist(x, y, REGIONS[k]))
def _flank_record(k):
    R = REGIONS[k]
    pts = [to_map(x, y) for x, y in R]
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    clumps = [list(map_trees[i]) for i, (x, y, r) in enumerate(trees) if _ring_of(x, y) == k]
    return {"x": round((min(xs) + max(xs)) / 2, 1), "y": round((min(ys) + max(ys)) / 2, 1), "w": round(max(xs) - min(xs), 1),
            "h": round(max(ys) - min(ys), 1), "rot": 0, "role": "shrine", "r": 4.0, "clumps": clumps,
            "poly": [[round(x, 1), round(y, 1)] for x, y in pts]}
_bx = [x for x, _ in REGION]; _by = [y for _, y in REGION]
mx0, my0 = to_map(min(_bx), min(_by))
mx1, my1 = to_map(max(_bx), max(_by))
manifest_add = {
    "village_groves": [_flank_record(k) for k in range(len(REGIONS))],
    "tree_crowns": [round(smx, 1), round(smy, 1), round(SACRED[2] / 6, 1)],
    "basin": {"x": round(bmx, 1), "y": round(bmy, 1), "r": 1, "vr": 0.9, "shrine": True, "private": False, "basin": True},
    "torii_y": [1088 + 6 * i for i in range(7)],
    "map_grove_px": [round(mx0, 1), round(my0, 1), round(mx1, 1), round(my1, 1)],
}

# STRAIGHT_RUN (spec SC-002; research.md R2): the edge crowns, ordered along the outline; a window of four whose
# centers all lie within 2 ft (6 sheet px) of the line through its first and last is a ruled run
def _off_line(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    L = math.hypot(bx - ax, by - ay) or 1.0
    return abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / L
def _nearest_index(R, x, y):
    return min(range(len(R)), key=lambda i: math.hypot(R[i][0] - x, R[i][1] - y))
runs = []
m_all = 0
for k, R in enumerate(REGIONS):
    edge_crowns = sorted(((_nearest_index(R, x, y), x, y) for x, y, r in trees if _ring_of(x, y) == k and poly_dist(x, y, R) <= r + 6), key=lambda t: t[0])
    m = len(edge_crowns)
    m_all += m
    for i in range(m):
        w = [edge_crowns[(i + q) % m][1:] for q in range(4)]
        if m >= 4 and all(_off_line(w[q], w[0], w[3]) <= 6.0 for q in (1, 2)) and math.hypot(w[3][0] - w[0][0], w[3][1] - w[0][1]) > 30:
            runs.append([list(t) for t in w])
meas["edge_crowns"] = m_all
meas["straight_runs"] = len(runs)
meas["straight_run_windows"] = runs
json.dump({"regions": REGIONS, "region": REGION, "floor": [[round(x, 1), round(y, 1)] for x, y in FLOOR], "clear_poly": [[round(x, 1), round(y, 1)] for x, y in CLEAR_POLY], "meas": meas, "trees": trees, "sacred": SACRED, "grove_svg": grove_svg, "torii_svg": torii_svg, "manifest_add": manifest_add}, open(OUT, "w"), indent=1)
print(json.dumps(meas))
