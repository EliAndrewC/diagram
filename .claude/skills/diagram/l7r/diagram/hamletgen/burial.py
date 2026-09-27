"""STAGE 6c (feature 273, the GM 2026-09-27): the hamlet's own burial ground.

The GM ruled that a village district's main village alone keeps the shrine, the headman's house and the cremation
ground, and asked where a hamlet's dead then lie - its own ground, the village's, or bones brought home - to follow
the history where it agrees and to roll a knob where it does not. Most forms read put the dead by their own
settlement - a hamlet's burial ground at its edge, the ground a settlement's inhabitants hold in common, the
two-grave system's burial grave on common land, graves on a household's own land, China's family and lineage
graves - but the grave at the parish temple was half an
obligation, and most villages' households were registered with temples outside the village. The history does not
point one way, so it is a KNOB, as the GM asked: `hamlet_burial` - "own_ground" (a burial ground at the hamlet's edge,
holding the urns brought back from the village's cremation ground) or "village_ground" (none; its dead lie in the
village's ground, by the shrine that is the setting's parish temple) - at even odds, a GUESS. Research:
research/religion-and-death.html "Where do a hamlet's dead lie?".

WHAT IS MEASURED AND WHAT IS NOT. The ground's AREA is the 750-2,450 sq ft band the record reckons for a hamlet's own
ground (research/religion-and-death.html "How much ground does a village burial ground need, and whose dead lie in
it?"), a band for FULL-BODY burial that overstates an urn ground - a GUESS, and where a hamlet falls in it is set by
its households, a GUESS. The 1.4 to 1 outline is a
GUESS. The water set-backs are the record's drawn bands (research/religion-and-death.html "How far from water does a
burial ground lie?": about 75 px from a stream, 50 px from a flooded field edge). The 60 ft from houses and wells is
the engine's measure of "outside the settlement" the wayside stones use (`BOUNDARY_STONE_CLEAR_FT`), a GUESS for a
burial ground. Down the fall line first is the village's own ground's side (burial below the houses), borrowed.
"""

from __future__ import annotations

import math

from l7r.diagram.settlement import Settlement, knob_rng
from l7r.diagram.settlement._knobs import BOUNDARY_STONE_CLEAR_FT
from l7r.diagram.settlement.civic_grounds.edge_seat import EdgeGround, edge_seat

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


def ground_size(households: int, ftpx: float) -> tuple[float, float]:
    """The ground's drawn (w, h) in px: its area from the households within the record's band, 1.4 to 1."""
    lo, hi = HOUSEHOLDS_AT
    t = min(1.0, max(0.0, (households - lo) / (hi - lo)))
    area = GROUND_SQFT[0] + t * (GROUND_SQFT[1] - GROUND_SQFT[0])
    w_ft = math.sqrt(area * ASPECT)
    return w_ft / ftpx, (area / w_ft) / ftpx


def seat_ground(s: Settlement, down_deg: float, w: float, h: float) -> Pt | None:
    """The burial ground's seat, asked of the engine's shared edge seat (`settlement/civic_grounds/edge_seat.py`): 60 ft
    from every house and well, 180's water bands, the nearest seat that clears, below the houses where it can."""
    ftpx = float(s.M["meta"].get("ftpx", 1.0))
    ground = EdgeGround(s, clear_px=BOUNDARY_STONE_CLEAR_FT / ftpx, stream_px=STREAM_SETBACK_PX, ditch_px=DITCH_MARGIN_FT / ftpx, field_px=FIELD_SETBACK_PX)
    return edge_seat(s, down_deg, w, h, ground, reach_px=REACH_FT / ftpx, step_px=STEP_FT / ftpx)


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
        l7r.diagram.settlement.civic_grounds.edge_seat.edge_seat
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
