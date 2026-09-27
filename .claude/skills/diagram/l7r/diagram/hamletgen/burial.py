"""STAGE 6c (feature 273, the GM 2026-09-27): the hamlet's own burial ground.

The GM ruled that a village district's main village alone keeps the shrine, the headman's house and the cremation
ground, and asked where a hamlet's dead then lie - its own ground, the village's, or bones brought home - to follow
the history where it agrees and to roll a knob where it does not. The history agrees: every form read puts the dead
by their own settlement - a hamlet's burial ground at its edge, the ground a settlement's inhabitants hold in common,
the two-grave system's burial grave on common land with only the visited grave at the village's temple, graves on a
household's own land, and China's family and lineage graves - but the grave at the parish temple was half an
obligation, and most villages' households were registered with temples outside the village. The history does not
point one way, so it is a KNOB, as the GM asked: `hamlet_burial` - "own_ground" (a burial ground at the hamlet's edge,
holding the urns brought back from the village's cremation ground) or "village_ground" (none; its dead lie in the
village's ground, by the shrine that is the setting's parish temple) - at even odds, a GUESS. Research:
research/religion-and-death.html "Where do a hamlet's dead lie?".

WHAT IS MEASURED AND WHAT IS NOT. The ground's AREA is the 750-2,450 sq ft band the record reckons for a hamlet's own
ground (research/religion-and-death.html "How much ground does a village burial ground need, and whose dead lie in
it?") - accurate as a band; where a hamlet falls in it is set by its households, a GUESS. The 1.4 to 1 outline is a
GUESS. The water set-backs are the record's drawn bands (research/religion-and-death.html "How far from water does a
burial ground lie?": about 75 px from a stream, 50 px from a flooded field edge). The 60 ft from houses and wells is
the engine's measure of "outside the settlement" the wayside stones use (`BOUNDARY_STONE_CLEAR_FT`), a GUESS for a
burial ground. Down the fall line first is the village's own ground's side (burial below the houses), borrowed.
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng, seg_dist
from l7r.diagram.settlement._geom import PointGrid, boxed_grid, boxed_ring_hit, boxed_rings, boxed_segs
from l7r.diagram.settlement._knobs import BOUNDARY_STONE_CLEAR_FT

from .consts import Pt
from .plan import SitePlan

BURIAL_FORMS = ("own_ground", "village_ground")  # the knob's two forms, rolled at even odds - a GUESS
GROUND_SQFT = (750.0, 2450.0)  # the record's band for a hamlet's full-body ground; it overstates an urn ground - a GUESS
HOUSEHOLDS_AT = (5, 30)  # the households at the band's floor and top - a GUESS, linear between
ASPECT = 1.4  # long to wide - a GUESS
STREAM_SETBACK_PX = 75.0  # 180's drawn floor from a stream (225 ft on a 3 ft/px city sheet)
FIELD_SETBACK_PX = 50.0  # 180's drawn margin from a flooded field edge (150 ft on a city sheet)
DITCH_MARGIN_FT = 6.0  # an irrigation ditch or channel is not a stream; the ground only keeps off its bank
REACH_FT = 700.0  # how far out from the middle of the houses the scan looks
STEP_FT = 10.0
ANGLES = (0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150, 180)  # off the fall line, nearest first


def ground_size(households: int, ftpx: float) -> tuple[float, float]:
    """The ground's drawn (w, h) in px: its area from the households within the record's band, 1.4 to 1."""
    lo, hi = HOUSEHOLDS_AT
    t = min(1.0, max(0.0, (households - lo) / (hi - lo)))
    area = GROUND_SQFT[0] + t * (GROUND_SQFT[1] - GROUND_SQFT[0])
    w_ft = math.sqrt(area * ASPECT)
    return w_ft / ftpx, (area / w_ft) / ftpx


def _rect_gap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    """The clear distance between two axis-aligned rects given as (cx, cy, w, h); 0 when they touch or overlap."""
    dx = max(0.0, abs(a[0] - b[0]) - (a[2] + b[2]) / 2)
    dy = max(0.0, abs(a[1] - b[1]) - (a[3] + b[3]) / 2)
    return math.hypot(dx, dy)


def _samples(cx: float, cy: float, w: float, h: float) -> list[Pt]:
    """The rect's corners, edge midpoints and center - where a set-back or a ring test is asked."""
    hw, hh = w / 2, h / 2
    return [(cx + fx * hw, cy + fy * hh) for fx in (-1, 0, 1) for fy in (-1, 0, 1)]


class _Ground:
    """What a burial ground must stand clear of, built ONCE before the candidates are tried (constitution X
    clause 15): the houses' and wells' footprints, the streams with their set-back, the irrigation courses with
    their bank margin, and the paddy rings with the field-edge margin."""

    def __init__(self, s: Settlement) -> None:
        ftpx = float(s.M["meta"].get("ftpx", 1.0))
        self.clear_px = BOUNDARY_STONE_CLEAR_FT / ftpx
        self.homes: list[tuple[float, float, float, float]] = []
        for h in s.M.get("houses", []):
            b = (h.get("geom") or {}).get("bbox")
            self.homes.append(tuple(float(v) for v in b) if b else (float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])))  # type: ignore[arg-type]
        self.homes += [(float(w["x"]), float(w["y"]), 2 * float(w.get("r", 8)), 2 * float(w.get("r", 8))) for w in s.M.get("wells", [])]
        streams = [(st["poly"], float(st.get("w", 6)) / 2 + STREAM_SETBACK_PX) for st in s.M.get("streams", []) if len(st.get("poly") or []) >= 2]
        # every drawn watercourse keeps the bank margin; a stream's own entry above carries the larger set-back
        ditches = [(pl, half + DITCH_MARGIN_FT / ftpx) for pl, half in s._watercourse_segs(0.0)]
        self.water: PointGrid = boxed_grid(boxed_segs(streams + ditches))
        rings = [f["outline"] for f in s.M.get("fields", []) if len(f.get("outline") or []) >= 3]
        rings += [m["poly"] for m in s.M.get("marshes", []) if len(m.get("poly") or []) >= 3]
        self.fields: PointGrid = boxed_grid(boxed_rings(rings, FIELD_SETBACK_PX))
        self.dry: PointGrid = boxed_grid(boxed_rings([d["poly"] for d in s.M.get("dry_plots", []) if len(d.get("poly") or []) >= 3], 3.0))

    def clear(self, s: Settlement, cx: float, cy: float, w: float, h: float) -> bool:
        """May a w x h ground stand at (cx, cy)? The engine's own fit, then the burial ground's set-backs."""
        if not (s._fits(cx, cy, w, h) and s._footprint_clear(cx, cy, w, h)):
            return False
        if any(_rect_gap((cx, cy, w, h), home) < self.clear_px for home in self.homes):
            return False
        for px, py in _samples(cx, cy, w, h):
            if any(seg_dist(px, py, a, b) < half for a, b, half, *_ in self.water.near(px, py)):
                return False
            if boxed_ring_hit(px, py, self.fields.near(px, py), FIELD_SETBACK_PX) or boxed_ring_hit(px, py, self.dry.near(px, py), 3.0):
                return False
        return True


def seat_ground(s: Settlement, down_deg: float, w: float, h: float, ground: Any = None) -> Pt | None:
    """The burial ground's seat: the NEAREST seat out from the middle of the houses that clears everything `_Ground`
    names, and among seats equally near, the one nearest the fall line. Nearest first, not fall line first: a scan
    that followed the fall line out to its reach before turning put the ground across a hamlet's paddies from its
    houses, 700 ft off (feature 273, found by its own test), where a side bearing had room 200 ft away. None when
    nothing within the reach clears."""
    houses = s.M.get("houses") or []
    if not houses:
        return None
    ftpx = float(s.M["meta"].get("ftpx", 1.0))
    g = ground if ground is not None else _Ground(s)
    mx = sum(float(q["x"]) for q in houses) / len(houses)
    my = sum(float(q["y"]) for q in houses) / len(houses)
    step, reach = STEP_FT / ftpx, REACH_FT / ftpx
    bearings = [(math.cos(math.radians(down_deg + off)), math.sin(math.radians(down_deg + off))) for off in ANGLES]
    r = step
    while r <= reach:
        for dx, dy in bearings:
            cx, cy = mx + dx * r, my + dy * r
            if g.clear(s, cx, cy, w, h):
                return (cx, cy)
        r += step
    return None


def stage_burial(s: Settlement, plan: SitePlan) -> None:
    """The hamlet's own burial ground, on its knob.

    A hamlet rolls `hamlet_burial`: a burial ground of its own at its edge, holding the urns brought back from the
    main village's cremation ground, or none, its dead lying in the village's (feature 273: the history gives both,
    so it is a knob). A pinned value is honored. It runs after the appurtenances
    and the pond stock because it is seated against the houses, wells and fixtures as placed, and before the lane
    web because it reserves ground the web and the scrub must work around. No seat, no ground - recorded, so a map
    that lacks one says why.

    On its knob, a small common burial ground at the hamlet's edge, as near the houses as it may stand, below them where it can.

    Steps:
        l7r.diagram.hamletgen.burial.ground_size
        l7r.diagram.hamletgen.burial.seat_ground
        l7r.diagram.settlement.Settlement.cemetery
    """
    houses = s.M.get("houses") or []
    if not houses or s.M["meta"].get("scale") != "hamlet":
        return
    form = s.knob_pins.get("hamlet_burial") or BURIAL_FORMS[knob_rng(s.seed, "hamlet_burial").randrange(len(BURIAL_FORMS))]
    if form not in BURIAL_FORMS:
        raise ValueError(f"hamlet_burial: {form!r} is not one of {BURIAL_FORMS}")
    s.M["meta"]["hamlet_burial"] = form
    if form == "village_ground":
        return
    w, h = ground_size(len(houses), float(s.M["meta"].get("ftpx", 1.0)))
    seat = seat_ground(s, plan.down_deg, w, h)
    if seat is None:
        s.M["meta"]["burial_ground"] = "no seat"
        return
    with s.feature("burial ground"):
        s.cemetery(seat[0], seat[1], w, h, parish=False)
    s.M["meta"]["burial_ground"] = "own"
