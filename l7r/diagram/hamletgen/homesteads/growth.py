"""Which plans GROW their cluster (feature 308), and the built share every grown map reports (FR-007).

A nucleated cluster is grown from its first house in Rust since feature 444 T30 (`rust/phases/src/homesteads/place.rs` `grow`, its
account and the GM's words of 2026-10-02 there); what Python keeps is the question the stage asks of a plan, and the figure it
records after.

Research: growth plumbing - NONE: a form's test and a share reported; the units that decide carry their own claims
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement._geom.primitives import convex_hull
from l7r.diagram.sitegen.geom import poly_area

if TYPE_CHECKING:
    from ..plan import SitePlan

#: The jitter on a seat's direction, in degrees either way AT EIGHT DIRECTIONS: a GUESS for the GM's "a little randomized jitter
#: ... so that it's not just an unrealistic grid" - 12 of the eight-direction ring's 45-degree step either way, and scaled with the
#: step at any other count (`grow_jitter`: 6 at sixteen), so neighboring directions never cross (at sixteen, 12 either way of a
#: 22.5-degree step did). The record gives no spacing variance for a nucleated hamlet.
#: ...and on its distance, as a share added to the least distance (never subtracted - the least is the rule): a GUESS, as above.
#: The growth's widening, (directions, rings) - each ring a multiple of the least distance - offered in turn while households are
#: left and the seats run dry, and past the table one ring further each level (`grow_level`): MEASURED on the reference at 40
#: households (feature 308, research R5): at eight directions and one ring a margin seated 29-36 of 40 and was thrown away; with the
#: three levels all sixteen seeds seat on the first or second margin. MAIN'S BREADTH (feature 318, Amendment 3, the GM: "the
#: tie-break thing for the real speedup"): one level of sixteen directions at three rings offered at once, nearest the field first,
#: tried and refused the near-field seats the field hemmed in (seed 4: 281 seats offered against 80) - withdrawn (research R1, R4).
GROW_LEVELS: tuple[tuple[int, tuple[float, ...]], ...] = ((8, (1.0,)), (12, (1.0, 1.5)), (16, (1.25, 1.75, 2.0)))
"""Research: the growth's widening - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 8, then 12, then 16 directions at rings 1.0 to 2.0 times the least distance, a search breadth (measured: feature 308 R5)"""
#: The width of the rings of distance from the margin's seat center inside which the growth counts two seats EQUAL (feature 318,
#: FR-003a, the GM: "all else being equal, try this first"), and tries the one nearer the field first: a GUESS - about the parting
#: between two neighbors' houses, so a ring holds the seats one growth step offers and no more. A distance on a continuous scale
#: is never exactly equal (an exact tie would never fire); a ring wide enough to hold several steps would make the field the
#: primary order again, which the GM ruled out.
#: Half a woodlot clump's width about a reserved wood seat, in px: the copse's clump (`COPSE_CLUMP_BS` at hamlet scale is 24)
#: How many times a seat is moved out to clear its own envelope rolled where it stands (`settled_seat`) before it is dropped:
#: each move only grows the reach it clears, and a roll that keeps outgrowing it is a seat not offered (a search breadth).
#: The position-hash salts of a seat's direction and distance jitter (`Settlement._hjit`), one per direction index
_SALT_DIRECTION, _SALT_DISTANCE = 300.0, 400.0


def grows(plan: SitePlan) -> bool:
    """Is this hamlet's cluster grown (FR-007)? The nucleated form's; the dispersed form keeps the front row, the ranks and
    the exhaustive pass, and the linear form seats its rows (the spec's round-1 rulings)."""
    return plan.settlement_form == "nucleated"


#: The parting a TIGHT seat leaves between two footprints, in px: the 2 px the growth parts every two homesteads by, with no path's
#: strip - a household seated there stands against its neighbor's land, and is taken only by passage across the neighbor's yard
#: (feature 317, plan D2; `settlement/rolling/passage.py`).


#: How far off the bearing from a standing house to its threshing yard a TIGHT seat may stand, in degrees (feature 317): the side of
#: the house its yard lies on, as the drawing page places such a household. MEASURED (research R7): behind the house - 135 and 180
#: degrees off - a walk had to go round it and seated 1 household in 194 tight tries on 13 settlements at 15 households, the yard's
#: side 15 in 304. It was 112.5, past the perpendicular, until the impl-drift check held it to the page (research R9): at 15
#: households on seeds 1-16, 23 households were reached by passage at either value. A search breadth, not a rule of the custom: a
#: household behind its neighbor is still seated, by the growth's ordinary seats and a way of its own.


def built_share(houses: Sequence[dict[str, Any]]) -> float:
    """The share of a nucleated cluster's outline its homesteads cover (feature 318, FR-007): the homesteads' boxes (house,
    yard, gardens and the homestead grove, `geom.bbox`) over the convex hull of their corners. REPORTED, never enforced - page
    0032's quarter-built floor binds a village, and "a hamlet is rightly loose and is not held to it". 0.0 under three
    homesteads (no outline).

    Research: the built share reported - research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html: the quarter-built figure measured on every nucleated map, refusing nothing
    """
    boxes = [(rec.get("geom") or {}).get("bbox") for rec in houses]
    boxes = [b for b in boxes if b]
    if len(boxes) < 3:
        return 0.0
    corners = [(float(x) + sx * float(w) / 2.0, float(y) + sy * float(h) / 2.0) for x, y, w, h in boxes for sx in (-1, 1) for sy in (-1, 1)]
    hull = convex_hull(corners)
    area = poly_area(hull) if len(hull) >= 3 else 0.0
    return round(min(1.0, sum(float(b[2]) * float(b[3]) for b in boxes) / area), 3) if area > 0.0 else 0.0
