"""The tail pond's bank (feature 385 T08): bare, or planted sparsely with mulberry and cudrania, rolled per hamlet.

0061 has the two forms from one Song passage - Chen Fu's *Nongshu*: "on the bank plant mulberry and cudrania sparsely, to
which cattle can be tethered ... the bank is trodden by the cattle and becomes firm" - and the bare bank of today's mown and
burned embankment. Neither gives a share, a spacing or a size; each is labeled where it is set (`consts.POND_BANKS`,
`POND_BANK_PITCH_FT`, `POND_BANK_CROWN_FT`).

The trees are seated AFTER the houses, ways and wells (`driver.STAGES`), so each is asked of what stands and none is forced
onto it; a seat that would put a crown on a roof, a wellhead or a yard's or bed's sun ground, or a trunk on a tread, crop or
water, is passed over, and a planted bank with no free seat draws no tree (`meta.pond_bank_trees` 0).
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist

from .consts import POND_BANK_CROWN_FT, POND_BANK_PITCH_FT, POND_BANKS, Pt
from .plan import SitePlan, _roll
from .sink import SINK_FRINGE

TREE_TONES = {"mulberry": ("#6E8B4A", "#4F6E33"), "cudrania": ("#4F6E33", "#3C5526")}
"""A bank tree's crown fill and its rim: the cudrania a shade darker than the mulberry.

Research: the two trees' marks - CONVENTION: the dike's standard tree, two greens so the two kinds read apart"""


def pond_bank(plan: SitePlan) -> str:
    """This hamlet's bank form: the spec's, else rolled from its seed between the two (`POND_BANKS`); none without a tail pond.

    Research: pond bank form - research/questions/0061-reservoir-ponds-tameike.drawing.html: a bare bank, or one planted sparsely with mulberry and cudrania"""
    if plan.sink_pond is None:
        return ""
    return plan.spec.pond_bank or str(_roll(plan.spec.seed, "pond_bank", POND_BANKS))


def bank_seats(s: Settlement, pond: tuple[float, float, float, float]) -> list[Pt]:
    """The seats round the bank, `POND_BANK_PITCH_FT` apart along the ring a crown's radius beyond the reed fringe, each jittered
    by its position (`_hjit`) a quarter pitch along the ring.

    Research:
        on the bank, beyond the reeds - research/questions/0061-reservoir-ponds-tameike.drawing.html: reeds at the shore, the embankment beyond them
        sparsely - GUESS: one tree about every 30 ft of bank (`POND_BANK_PITCH_FT`)"""
    cx, cy, rx, ry = pond
    off = SINK_FRINGE + s.px(POND_BANK_CROWN_FT)
    ax, ay = rx + off, ry + off
    perimeter = math.pi * (3 * (ax + ay) - math.sqrt((3 * ax + ay) * (ax + 3 * ay)))  # Ramanujan's
    n = max(int(perimeter // s.px(POND_BANK_PITCH_FT)), 1)
    out: list[Pt] = []
    for k in range(n):
        a = 2 * math.pi * k / n
        a += (s._hjit(cx + ax * math.cos(a), cy + ay * math.sin(a), 61.0) - 0.5) * 0.5 * 2 * math.pi / n
        out.append((cx + ax * math.cos(a), cy + ay * math.sin(a)))
    return out


def seat_free(s: Settlement, x: float, y: float, r: float) -> bool:
    """May a bank tree stand at (x, y): its crown off every roof and wellhead (`_canopy_keepouts`) and every yard's and bed's sun
    ground (`_sun_keepouts`), on the canvas, and its trunk off every tread (`_on_a_tread`), crop, marsh and stream?

    Research:
        no crown on a roof or a wellhead - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: against a wall, never on it
        out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no canopy over a yard's or bed's sun ground
        no trunk on a way, crop or water - NONE: a tree stands on open ground"""
    if not (r <= x <= s.W - r and r <= y <= s.H - r):
        return False
    box = (x - r, y - r, x + r, y + r)
    rects, circles = s._canopy_keepouts(box)
    if s._crown_covers(x, y, r, rects, circles, s.CANOPY_PAD) or s._crown_covers(x, y, r, s._sun_keepouts(box), (), s.CANOPY_PAD):
        return False
    if s._on_a_tread(x, y, 1.0, 1.0):
        return False
    M = s.M
    rings = [f["outline"] for f in M.get("fields") or [] if f.get("outline")] + [d["poly"] for d in M.get("dry_plots") or [] if d.get("poly")]
    rings += [m["poly"] for m in M.get("marshes") or [] if len(m.get("poly") or ()) >= 3]
    if any(point_in_poly(x, y, [(float(a), float(b)) for a, b in ring]) for ring in rings):
        return False
    for st in M.get("streams") or []:
        pts = [(float(a), float(b)) for a, b in st.get("poly") or []]
        if any(seg_dist(x, y, p, q) < float(st.get("w", 9.0)) / 2 + 1.0 for p, q in zip(pts, pts[1:], strict=False)):
            return False
    return True


def draw_bank_trees(s: Settlement, trees: list[tuple[float, float, float, str]]) -> None:
    """Each tree its crown and rim (`TREE_TONES`), one string of the "pond-bank tree" class; the crowns recorded in
    `tree_crowns` so every structure test reads them, and the trees with their kinds in `pond_bank_trees`."""
    if not trees:
        return
    g = ['<g class="pond-bank">']
    for x, y, r, kind in trees:
        fill, rim = TREE_TONES[kind]
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{rim}" stroke-width="0.8" opacity="0.92"/>')
    g.append("</g>")
    s.add("".join(g), cls="pond-bank tree")
    s._record_crowns([(x, y, r) for x, y, r, _k in trees])
    s.M["pond_bank_trees"] = [[round(x, 1), round(y, 1), round(r, 1), kind] for x, y, r, kind in trees]


def stage_pond_bank(s: Settlement, plan: SitePlan) -> None:
    """A tail pond's bank: its form rolled (`pond_bank`); a planted bank's trees seated round it where they stand free
    (`bank_seats`, `seat_free`), mulberry and cudrania in turn, drawn (`draw_bank_trees`); the form and the count recorded
    (`meta.pond_bank`, `meta.pond_bank_trees`).

    Steps:
        l7r.diagram.hamletgen.pondbank.pond_bank
        l7r.diagram.hamletgen.pondbank.bank_seats
        l7r.diagram.hamletgen.pondbank.seat_free
        l7r.diagram.hamletgen.pondbank.draw_bank_trees

    Research:
        the two trees in turn - GUESS: 0061 names mulberry and cudrania, not their order; they alternate round the ring
        after the houses, ways and wells - UNRESEARCHED: seated against what stands, before the hinterland's scrub and copse"""
    form = pond_bank(plan)
    if not form:
        return
    trees: list[tuple[float, float, float, str]] = []
    if form == "planted" and plan.sink_pond is not None:
        r = s.px(POND_BANK_CROWN_FT)
        for x, y in bank_seats(s, plan.sink_pond):
            if seat_free(s, x, y, r) and all(math.hypot(x - a, y - b) >= 2 * r for a, b, _r, _k in trees):
                trees.append((x, y, r, ("mulberry", "cudrania")[len(trees) % 2]))
        draw_bank_trees(s, trees)
    meta: dict[str, Any] = s.M["meta"]
    meta["pond_bank"] = form
    meta["pond_bank_trees"] = len(trees)
