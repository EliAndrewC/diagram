"""the lane law's SHAPE of a lane: its constants, bends, hooks and husks (split from `law.py` at the 1,000-line bar, feature 417 T54).

Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, rot_rect, seg_dist
from l7r.diagram.settlement.city.bridges import DECK_SPAN_DEFAULT_FT as DECK_SPAN_DEFAULT_FT
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT as PLANK_DITCH_FT
from l7r.diagram.settlement.city.bridges import deck_covers as deck_covers
from l7r.diagram.settlement.city.bridges import undeckable_at as undeckable_at

from ...consts import FIELD_REACH_FT as _FIELD_REACH_FT
from ...consts import Pt
from ..clearance import _HAIRPIN_DEG, _ZIGZAG_DEG, _ZIGZAG_RUN_FT, kink_spans
from ..fabric import _LANE_JOIN_FT, _WEB_MIN_FT
from ..forced import Blocked, forced_turn, lazy_ground
from ..geom import _HOOK_DEG, _HOOK_FT, _TOUCH_GAP, _turn_deg
from ..law_water import _ways, lane_pts

Lanes = Sequence[Mapping[str, Any]]

# THE BEND. A turn this sharp is a path doubling back on itself - nobody walks that; two real turns closer together than
# the run is a kink rather than a bend: a walker rounding something takes one arc, not a zig and an immediate zag. The
# figures are `clearance`'s (`lanes_bend_like_paths`, the rule's own thresholds), named here as the rule reads them.
DOUBLE_BACK_DEG = _HAIRPIN_DEG
"""Research: hairpin - research/questions/0081-village-lanes.drawing.html: 140 degrees"""
KINK_DEG = _ZIGZAG_DEG
"""Research: zigzag turn - research/questions/0081-village-lanes.drawing.html: 50 degrees"""
BEND_RUN_FT = _ZIGZAG_RUN_FT
"""Research: zigzag run - research/questions/0081-village-lanes.drawing.html: 40 ft"""

JOIN_TOL = _TOUCH_GAP
"""How near two lanes' treads must come (`geom.lanes_share_tread`) before the two count as one network - the web's own join
tolerance (the ink's), which every network test reads; a looser bar would call a near-miss a junction."""

DOORSTEP_FT = 80.0
"""A lane end this near a farmhouse's center is at its dooryard for the settle: the end a fan of ways is cut back past
(`settle_ends`), and the reach `Lawful.fault` looks up the houses a run may hit within. Whether an end REACHES a farmhouse,
0246's measure, is `reach_to_steading` (feature 328 wave 43; this was that test too, at 80 ft from the center; the yards a
lane may not come near read the lane's owner since 405 T18, and the field router's own dooryard the reach since 405 T91).
Research: a dooryard's reach for the settle - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end within 60 ft of a house is at it (the page's GUESS) - the settle allows 80 ft, a departure the code keeps until feature 417 T32; 80 ft from the house's center; 0246's own reach is 60 ft of the house or 12 ft of its built ground"""
HOUSE_REACH_FT = 60.0
"""Research: an end reaches a farmhouse - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: "within 60 ft of the house, or within 12 ft of the steading's built ground" (the page's own guess)"""
STEADING_REACH_FT = 12.0
"""Research: an end reaches a steading - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of its house, byre, shed, threshing yard or garden"""
_STEADING_PARTS = ("byres", "farm_sheds", "threshing_yards", "gardens")
"""Research: a steading's built ground - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: its house, byre, shed, threshing yard or garden"""


def reach_to_steading(end: Pt, house: Mapping[str, Any], M: Mapping[str, Any]) -> bool:
    """Does a lane end reach this farmhouse as 0246 measures it - within `HOUSE_REACH_FT` of the house's center (the page's grounds
    note: "to a way's line or a farmhouse's center", as `geom.end_serves` measures it), or within `STEADING_REACH_FT` of its
    steading's built ground, footprints (the house, and the byres, sheds, yards and gardens recorded `of` it)? Feature 328: it
    was 80 ft from the center, `DOORSTEP_FT`; wave 43 measured the 60 ft to the footprint, which the page does not.

    Research: an end reaches a farmhouse - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of the house or 12 ft of its built ground, the page's own guess"""

    def gap(poly: Sequence[Pt]) -> float:
        return 0.0 if point_in_poly(end[0], end[1], list(poly)) else min(seg_dist(end[0], end[1], a, b) for a, b in zip(poly, [*poly[1:], poly[0]], strict=False))

    hx, hy = float(house["x"]), float(house["y"])
    body = rot_rect(hx, hy, float(house.get("w", 0.0)), float(house.get("h", 0.0)), float(house.get("rot", 0.0)))
    if math.dist(end, (hx, hy)) <= HOUSE_REACH_FT or gap(body) <= STEADING_REACH_FT:
        return True
    for key in _STEADING_PARTS:
        for r in M.get(key) or []:
            own = r.get("of")
            if not own or math.dist((float(own[0]), float(own[1])), (hx, hy)) > 0.5:
                continue
            poly = (
                [(float(a), float(b)) for a, b in r["poly"]]
                if r.get("poly")
                else (rot_rect(float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), float(r.get("rot", 0.0))) if r.get("w") else None)
            )
            if poly and gap(poly) <= STEADING_REACH_FT:
                return True
    return False


DOORSTEP_MAX = 2
"""...and one farmhouse may absolve this many of them. Three reads as a fan of stubs pointing at one door (consts.py's
0611 ruling).
Research: ends one house may absolve - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); no page gives how many ends meet at one; two"""

BREAK_SPAN_FT = 60.0
"""A lane segment longer than this whose midpoint stands in a building's box has run straight through it
(`lanes_do_not_break_mid_run`): the tread was drawn across the solid, or it vanished there and resumed beyond.
Research: no tread through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a segment over 60 ft"""

FIELD_REACH_FT = _FIELD_REACH_FT  # feature 417 T05: the one constant
"""On a brook map one of the hamlet's own ways (not the track out) comes this near the field - its paddy or its dry hem -
the reach `lanes_reach_something` asks of the field (feature 261, FR-012). 60 ft until 405 T22: no 0014 page states it, and
0014 draws the path JOINING the bund, a lane end within 6 ft of the paddy's edge read as joining it.
(`track.SPUR_REACH_FT`, the field spur's copy, went with the spur in feature 417 T50.)
Research:
    a way reaches the field - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a way runs from the hamlet to the field's outer bund
    the reach - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a lane end that stops within 6 ft of the paddy's edge is drawn as joining it
    a dry plot's edge arrived at - research/questions/0081-village-lanes.drawing.html: a lane runs along the edge of the hem of dry fields and the spur stops at the hem's edge; the 6 ft read as joining it is 0014's GUESS (`the reach`)"""


CONNECTOR_START_FT = 1.5
"""A lane end this near the connector's first point meets the connector's START - the figure `fold_the_connector_hairpin` repaired by
until feature 417 T26 took that pass away, kept so the hairpin this law refuses is the set it was."""

# A NEEDLE JOIN - a lane's last leg meeting another way's tread at a shallow angle and running back along it, leaving a
# sliver of ground between two treads instead of a T (R3; Mizuguchi's 35 ft leg at 16 degrees, a ~250 sq ft needle).
# MAP DRAWING CONVENTION, not a finding: 20 degrees is where two treads 4-6 ft wide stop reading as a junction and start
# reading as one smudged wedge (Mizuguchi's 16 inside it with room), and a leg of 20 ft or less is the approach to the
# junction itself - under a quarter of the Mizuguchi leg, and short enough that the wedge it leaves is under the treads'
# own ink. No rule of the record states either figure; they are recorded here, at the constant.
NEEDLE_DEG = 20.0
"""Research: a needle, not a T - CONVENTION: under 20 degrees two treads read as one smudged wedge"""
NEEDLE_FT = 20.0
"""Research: needle leg - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a leg over 20 ft, shorter is the approach to the junction"""

JOIN_REACH_FT = _LANE_JOIN_FT
"""A free lane end this near another way, making for it, is a join that stops short (`near_misses`) - the web's own join
reach (`fabric._LANE_JOIN_FT`, 25 ft), ONE tolerance for the placer that draws a join and the rule that asks whether it
touched. Future-work 2c measured every stopped-short join in the pool inside it (16.7, 28.0, 28.1, 29.2, 29.6 ft) - the
dead band between the generator's then 30 ft and the ink's 4 ft that neither half owned.
Research: a join that stops short - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined"""

FRAGMENT_FT = _WEB_MIN_FT
"""A lane shorter than this that earns nothing is debris (`short_fragments`) - the web's own debris floor (`_WEB_MIN_FT`),
asked of the finished web rather than only when a run is drawn.
Research: shortest way - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); 30 ft"""

AIM_DEG = 60.0
"""...and "making for it" is the way standing within this many degrees of the end's own heading. MAP DRAWING CONVENTION: a
tread that stops pointing at a way within a turn of 60 degrees reads as meant to meet it; one pointing away from it, or past
it at a glance, is a lane that ends beside a way, not a broken join.
Research: making for a way - CONVENTION: within 60 degrees of the end's heading"""


def kinks(pts: Sequence[Pt]) -> list[tuple[str, int, int]]:
    """Where a lane fails to bend like a path: a turn of more than `DOUBLE_BACK_DEG` ("doubles back"), or two turns of
    more than `KINK_DEG` whose summed path between them is `BEND_RUN_FT` or less ("kinks") - the whole run between the two
    turns, not one segment. The body is `clearance.kink_spans`, which every web pass asks too (ways W18, FR-003).
    Research: bends like a path - research/questions/0081-village-lanes.drawing.html: no hairpin, no zigzag"""
    p = list(pts)
    return [(kind, round(p[ka][0]), round(p[ka][1])) for kind, ka, _kb in kink_spans(p)]


def bends_badly(pts: Sequence[Pt]) -> bool:
    """Does this run fail to bend like a path (`kinks`)?"""
    return bool(kinks(pts))


def lanes_that_kink(M: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    """`kinks` over every lane, the track out included (`lanes_bend_like_paths`; feature 328 wave 46 - the connector was
    exempt, and 0081 exempts no lane: "Every lane is pulled taut like a string").
    Research: bends like a path - research/questions/0081-village-lanes.drawing.html: every lane, the track out with them"""
    blocked = lazy_ground(M)
    return [(kind, round(p[ka][0]), round(p[ka][1])) for ln in (M.get("lanes") or []) for p in [lane_pts(ln)] for kind, ka, _kb in kink_faults(p, float(ln.get("w") or 3.0), blocked)]


def kink_faults(p: Sequence[Pt], width: float, blocked: Blocked | None = None) -> list[tuple[str, int, int]]:
    """`clearance.kink_spans` of a run but the turns the ground forces (`forced.forced_turn`, plan D2 of feature 385): a
    zigzag or a hairpin whose chord - the vertex before its first turn to the vertex after its last - is not lawful ground is
    a path round what stands there. With no ground (`blocked` None) every span is a fault, as before.
    Research: a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - the chord the vertex before the first turn to the vertex after the last"""
    p = list(p)
    return [k for k in kink_spans(p) if not (k[1] >= 1 and k[2] + 1 < len(p) and forced_turn(blocked, p[k[1] - 1], p[k[2] + 1], width))]


def hook_faults(p: Sequence[Pt], width: float, blocked: Blocked | None = None) -> list[int]:
    """`hooked` ends of a run but those the ground forces: a hook whose chord - the vertex before the turn to the end - is not
    lawful ground is the walk round a corner (`forced.forced_turn`, plan D2 of feature 385).
    Research: a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - the chord the vertex before the hook's turn to the end"""
    p = list(p)
    return [e for e in hooked(p) if not forced_turn(blocked, *((p[-3], p[-1]) if e == -1 else (p[2], p[0])), width)]


def hooked(pts: Sequence[Pt]) -> list[int]:
    """Which ends of a run are hooked, as -1 (its last) and 0 (its first): a leg of `_HOOK_FT` or less turning `_HOOK_DEG` or more.
    Research: a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: 12 ft, 90 degrees"""
    p = list(pts)
    if len(p) < 3:
        return []
    return [end for end, q in ((-1, p), (0, p[::-1])) if math.dist(q[-2], q[-1]) <= _HOOK_FT and _turn_deg(q[-3], q[-2], q[-1]) >= _HOOK_DEG]


def hooks(pts: Sequence[Pt]) -> list[tuple[int, int]]:
    """The vertex before each hooked end (`hooked`)."""
    p = list(pts)
    return [(round(p[-2 if end == -1 else 1][0]), round(p[-2 if end == -1 else 1][1])) for end in hooked(p)]


def hooked_ends(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`hooks` over EVERY lane, the connector included - but a hook the ground forces (`hook_faults`)."""
    blocked = lazy_ground(M)
    out = []
    for ln in M.get("lanes") or []:
        p = lane_pts(ln)
        out += [(round(p[-2 if e == -1 else 1][0]), round(p[-2 if e == -1 else 1][1])) for e in hook_faults(p, float(ln.get("w") or 3.0), blocked)]
    return out


def husks(M: Mapping[str, Any]) -> list[int]:
    """The lane records that draw nothing: under two points, or under 1 ft long."""
    return [i for i, p in enumerate(_ways(M)) if len(p) < 2 or sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False)) < 1.0]
