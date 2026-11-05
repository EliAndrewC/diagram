"""The households' ways' JOIN AND KNOT REACHES, and a household PINCHED across its neighbor's yard (feature 318).

Every household's way is laid in the gaps in Rust since feature 444 T30 (`rust/phases/src/homesteads/gap_ways.rs`, recorded by
`hamletgen/homesteads/household_ways.lay_the_ways`); the reaches it was laid by stay here for the ways' later passes that read them
(`ways/knots.py`, `ways/lay.py`, `ways/smooth.py`), and `pinch` records a household the Rust names as reached across a yard.

Research: the ways' plumbing - NONE: the reaches carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

#: The lane raster's cell, in px: the 6 ft band a way's line has between two homesteads parted by the threading gap always holds a
#: cell's center (MEASURED, research R4: 4 px reached as many houses and cost 0.3 s more a map; 6 px left houses unreached).
#: How far past the homesteads the raster runs, in px: room for a way round the cluster's outside.
#: The flood runs this far past the last household's ring, in px: room for a household's search to choose among its exits.
#: How much dearer a step beside blocked ground is - the share of blocked cells within `CENTER_CELLS` of it, times this: a way
#: keeps to the middle of its gap (a GUESS for a worn path's taking the open middle of the ground between two plots).
#: The ring about a homestead where its search meets the flood, in cells past the corridor's half-width.
#: How many distinct ways out a household tries (MEASURED, research R4: one way out reached every house on 5 of 9 maps, six on 6).
#: ...AND THREE TIMES AS MANY BEFORE A KNOTTED FOOT IS KEPT (feature 328 wave 54): where every exit tried leaves its foot
#: beside a junction it cannot be gathered onto, the search runs on past `GAP_TRIES` for an exit that gives a gathered or
#: knot-free join (Kuwabata: lane 11's foot was kept 21.8 ft from lane 9's door, inside that dooryard, where no gather of
#: the settled web is lawful; a later exit gave a knot-free way). Only a household whose first six exits are all knotted
#: pays for it.
#: The most legs a way may take (`route.taut`): a gap way bends at plot corners, more often than a straight path does.
#: A way coming within this of a way already laid joins it there, at a T, rather than running beside it: under the shadow rule's
#: 30 ft (`WEB_SHADOW_FT`, a way beside another past a pitch), MEASURED (research R4: 10 of 14 refusals were the doubled band).
#: ...and where a way joined there breaks the tree's lane law, it is tried joined farther off (`JOIN_FAR_FT`), then run on to the way
#: out, the first the law admits taken (MEASURED, research R5).
JOIN_FAR_FT = 45.0
"""Research: a farther join - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); a way joins a way laid before it at a T; tried 45 ft off where the nearer join breaks the lane law"""

#: Ends of ways this close are joined at ONE point (`gathered_foot`): the lane page's knot reach.
KNOT_FT = 25.0
"""Research: lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined at a single point"""

#: ...the reach, in KNOT_FT's, within which a foot is gathered onto a junction: 1.0, the page's own 25 ft. Feature 328 wave 4
#: first set 1.5 to catch a foot slid just past the reach (Inashiro: slid to 25.18 ft, the knot still drawn); the slide was
#: removed, and the margin went past the page, so it is the page's reach now.
KNOT_MARGIN = 1.0
"""Research: a knot's margin - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point - the page's own reach, no margin past it (feature 328: a 1.5 margin went past the page, and the slide it guarded against is gone)"""


def pinch(rec: dict[str, Any], others: Sequence[dict[str, Any]]) -> bool:
    """Reach the household `rec` across the yard of the nearest household with a way of its own (`others`, each with a laid
    corridor): recorded as feature 317's passage is (`reached_across`, `passage_depth`, the walk from its house to that yard),
    with `passage_kind` "pinch" - the walk not drawn. False where no household has a way.

    Research: reached across a neighbor's yard in a pinch - CANON: the GM's ruling of 2026-10-03, "it's okay for people to cut through neighbors' yards in a pinch"; the adjoining-land condition of an ordinary passage does not bind it
    """
    hx, hy = float(rec["x"]), float(rec["y"])
    near = min(others, key=lambda o: math.hypot(float(o["x"]) - hx, float(o["y"]) - hy), default=None)
    if near is None:
        return False
    yard = ((near.get("geom") or {}).get("boxes") or {}).get("yard") or (float(near["x"]), float(near["y"]))
    rec["reached_across"] = [round(float(near["x"]), 1), round(float(near["y"]), 1)]
    rec["passage_depth"] = 1
    rec["passage"] = [[round(hx, 1), round(hy, 1)], [round(float(yard[0]), 1), round(float(yard[1]), 1)]]
    rec["passage_kind"] = "pinch"
    return True
