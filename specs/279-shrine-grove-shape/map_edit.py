"""Feature 279 D5: put the one grove layout on the Hoshigaoka village map.

argv: layout.json  in.svg  out.svg  in.json  out.json
- replaces the <g id="shrine-grove"> group with the layout's (the wood behind and at the sides, its own edge);
- extends the map's own scrub scatter into the ground the wood gave up inside the old grove floor, from a donor
  patch just west of the grove, kept only clear of every shrine feature;
- replaces the manifest's village_groves record of role shrine."""

import json
import math
import re
import sys

L = json.load(open(sys.argv[1]))
svg = open(sys.argv[2]).read()
M = json.load(open(sys.argv[4]))


def to_map(x, y):
    return (392 + (x - 440) / 6, 1074 + (y - 500) / 6)


def in_poly(x, y, poly):
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_dist(x, y, poly):
    return min(seg_dist((x, y), a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


# ---- the grove group ----
start = svg.index('<g id="shrine-grove">')
end = svg.index("</g>", start) + len("</g>")
assert "<g" not in svg[start + 3 : end - 4], "the grove group nests a group - read it before replacing it"
old_group = svg[start:end]
old_rec = next(g for g in M["village_groves"] if g.get("role") == "shrine")
OLD_FLOOR = [tuple(p) for p in old_rec["poly"]]

# ---- the shrine's keep-outs, in map px ----
regions = [[to_map(x, y) for x, y in R] for R in L["regions"]]
clear = [to_map(x, y) for x, y in L["clear_poly"]]
ax0, ay0 = to_map(425, 554)
ax1, ay1 = to_map(455, 816)
sacred = (*to_map(L["sacred"][0], L["sacred"][1]), L["sacred"][2] / 6)
basin = to_map(398.0, 570.0)
well = to_map(440.5, 176.5)
path = (to_map(330.0, 440.0), to_map(426.0, 184.0))
torii_y = [1088 + 6 * i for i in range(7)]


def clear_ground(x, y, pad):
    """True where a scatter mark may stand: vacated ground, clear of every shrine feature by pad map px."""
    if not (in_poly(x, y, OLD_FLOOR) or (348 <= x <= 432 and 985 <= y <= 1235)):
        return False  # the ground the old grove held, and the bare strips north and south of it the old reservations left
                      # (settlement-review round 1, F3); beyond them the map's own scatter already stands
    if any(in_poly(x, y, R) or poly_dist(x, y, R) < pad + 1.5 for R in regions):
        return False  # the wood (its edge crowns straddle the region by up to a crown)
    if in_poly(x, y, clear) or poly_dist(x, y, clear) < pad:
        return False
    if ax0 - pad <= x <= ax1 + pad and ay0 - pad <= y <= ay1 + pad:
        return False  # the approach's gravel
    if any(abs(y - ty) < 2 + pad and abs(x - 392) < 5 + pad for ty in torii_y):
        return False  # the arches' beams
    if math.hypot(x - sacred[0], y - sacred[1]) < sacred[2] + pad:
        return False
    if math.hypot(x - basin[0], y - basin[1]) < 2.5 + pad or math.hypot(x - well[0], y - well[1]) < 6 + pad:
        return False
    if seg_dist((x, y), *path) < 1.5 + pad:
        return False
    return True


# ---- the donor scatter: the open ground just west of the grove ----
DONOR = (290.0, 1000.0, 350.0, 1140.0)
tufts = {}  # base -> [line tags] (the tuft group's plain lines)
styled = []  # (anchor, tag)
for m in re.finditer(r"<(line|circle)\b[^>]*/>", svg):
    if start <= m.start() < end:
        continue
    t = m.group(0)
    if m.group(1) == "circle":
        mm = re.search(r'cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', t)
        if not mm or 'fill="#94A063"' not in t:
            continue
        x, y = float(mm.group(1)), float(mm.group(2))
        if DONOR[0] <= x <= DONOR[2] and DONOR[1] <= y <= DONOR[3]:
            styled.append(((x, y), t))
        continue
    mm = re.search(r'x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', t)
    if not mm:
        continue
    x, y = float(mm.group(1)), float(mm.group(2))
    if not (DONOR[0] <= x <= DONOR[2] and DONOR[1] <= y <= DONOR[3]):
        continue
    if "stroke=" not in t:
        tufts.setdefault((x, y), []).append(t)
    # the donor's pines are NOT carried: tiled, one pine per tile read as a planted grid (session look, feature 279)


def shift(tag, dx, dy):
    def mv(m):
        k, v = m.group(1), float(m.group(2))
        return f'{k}="{v + (dx if k in ("x1", "x2", "cx") else dy):.1f}"'
    return re.sub(r'\b(x1|x2|y1|y2|cx|cy)="([\d.]+)"', mv, tag)


# tile the donor over the vacated ground: whole donor widths east, and a half-height step so the tiles do not repeat
# in one visible grid
OFFSETS = [(dx, dy) for dx in (60.0, 120.0) for dy in (0.0, -70.0, 70.0, 140.0)]
new_tufts, new_styled, used = [], [], set()
for dx, dy in OFFSETS:
    for (bx, by), tags in tufts.items():
        x, y = bx + dx, by + dy
        key = (round(x), round(y))
        if key in used or not clear_ground(x, y, 1.5):
            continue
        used.add(key)
        new_tufts += [shift(t, dx, dy) for t in tags]
    for (bx, by), t in styled:
        x, y = bx + dx, by + dy
        key = (round(x), round(y), t[:12])
        if key in used or not clear_ground(x, y, 3.0):
            continue
        used.add(key)
        new_styled.append(shift(t, dx, dy))

scrub = (
    '<g id="shrine-open-ground"><!-- feature 279: the map\'s own scrub, carried into the ground the wood gave up -->'
    + '<g stroke="#A7A860" stroke-width="0.8">' + "".join(new_tufts) + "</g>"
    + "".join(new_styled)
    + "</g>"
)
svg = svg[:start] + scrub + L["grove_svg"] + svg[end:]
open(sys.argv[3], "w").write(svg)

# ---- the manifest ----
recs = L["manifest_add"]["village_groves"]  # one record per flank (feature 279)
keep = [g for g in M["village_groves"] if g.get("role") != "shrine"]
at = next(i for i, g in enumerate(M["village_groves"]) if g.get("role") == "shrine")
M["village_groves"] = keep[:at] + recs + keep[at:]
json.dump(M, open(sys.argv[5], "w"))
print(json.dumps({"tuft_clumps": len(new_tufts) // 3, "styled": len(new_styled), "old_group_chars": len(old_group), "new_group_chars": len(L["grove_svg"])}))
