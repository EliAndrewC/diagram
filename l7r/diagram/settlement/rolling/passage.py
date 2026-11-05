"""A household reached across a neighbor's yard (feature 317, plan D2-D5).

THE CUSTOM (research/questions/0081-village-lanes.html): passage over a neighbor's land for land with no road access of its own -
"where A's land is so situated that he cannot reach the highway without passing over B's land, A has the right to do so"
(Wigmore 1892, Part V Section 8; seven provinces, three of them towns) - and as a chain, Echigo's plot C passing over both B's
and A's. No page read states that every house in a clustered village fronted a lane of its own.

WHERE IT CAN ARISE: the grown cluster parts every two homesteads by a lane's threading gap (`growth.grow_gap`), so no household
stood behind a neighbor's land and the custom's condition never arose (research R3: the nearest neighbor's yard 64 ft at the
least from any door refused a path). So, within the settlement's rolled share (`passage_budget`), each standing house also
offers TIGHT seats - at the parting with no path's strip (`hamletgen/homesteads/growth.py`) - and a household offered one is
seated there only by passage: it asks first whether it has a way of its own (`opens`: its yard onto lane ground connected to
the way out, feature 318 - no path is searched while houses are seated), a household that has one is refused the tight seat,
and one that has none is admitted where:

- its own ground ADJOINS the neighbor's: its land (the reach the growth parted its seat by, `growth.settled_seat`'s allotted
  reach over every garden layout, carried with its house) within the parting and `PASSAGE_ADJOIN_FT` of the neighbor's land
  (the neighbor's footprint as the growth parts it) - the custom's condition, never a walking distance (`adjoins`). One
  layout's box, or the reach rolled at the final seat alone, stands back from that line (measured at 15 households: 6.6-36 px
  and 3-16.6 px apart, all but one refused);
- a walk from one of its dooryard doors to the neighbor's threshing yard stays on the two households' land (`on_their_land`)
  and clears both households' houses, beds, sheds and fixtures, every other homestead, the static ground the site refuses and
  the reserved wood seats (`walk_clear`) - ROUTED round them as a household's own path is (`route.search`, `route.taut`,
  `walk_of`): a straight walk from the door ran through its own house, beds or fixtures, or the neighbor's, on 95 of the 109
  tight-seat layouts with no corridor at 15 households, seeds 1-16 (3 passages found);
- the neighbor itself is reached - by a corridor, or by a passage whose chain to one is under `PASSAGE_CHAIN` (`depth_of`).

The walk is NOT DRAWN as a lane: a dooryard and a yard are open trodden ground and the walk across them is the custom, not a
way (this record's reading, a GUESS). It is kept clear of every later homestead as a corridor is (`AccessTree.bar`), and the
ways count the household reached where its neighbor is (`hamletgen/ways/checks.py:unreached_houses`).

Research: passage machinery - NONE: box geometry, the chain's bookkeeping and the walk's sampling; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from .._geom import Pt
from .._knobs import knob_rng
from .access import reserve

if TYPE_CHECKING:
    from ..core import Settlement

#: How far beyond the growth's 2 px parting a household's envelope may stand from its neighbor's land and still ADJOIN it, in
#: feet: a GUESS - a foot of tolerance for the placer's rounding; the custom's condition is land against land, not a reach.
#: The longest chain of passages from a household to a corridor: a GUESS citing Wigmore's Echigo entry, where plot C passes over
#: both B's and A's to the highway - the longest chain the record reads.
#: The share of a nucleated settlement's households that may be reached by passage, rolled per settlement: a GUESS - the record
#: attests the custom, not how common it was, and a clustered village whose rear households all walked through their neighbors'
#: yards is not what its entries describe (alleys to the rear houses, Morse; blind alleys to the houses, the Manchu survey).
PASSAGE_SHARE_BAND = (0.0, 0.25)
"""Research: share reached by passage - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: from none up to a quarter of the households"""
#: The pitch the walk is sampled at to ask that it stays on the two households' land, in px.

Box = tuple[float, float, float, float]


def passage_share(seed: int) -> float:
    """The settlement's share of households that may be reached by passage, rolled from the map's seed within
    `PASSAGE_SHARE_BAND` (the knob doctrine: it depends on the seed and the knob's name, never on draw order).

    Research: share reached by passage - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: rolled per settlement within the band
    """
    lo, hi = PASSAGE_SHARE_BAND
    return round(lo + knob_rng(seed, "passage_share").random() * (hi - lo), 3)


def passage_budget(share: float, households: int) -> int:
    """How many of a settlement's `households` may be reached by passage at its rolled `share`.

    Research: share reached by passage - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: rounded down to whole households
    """
    return int(math.floor(share * households))


def grown(box: Any, by: float) -> Box:
    """The box `(cx, cy, w, h)` grown by `by` on every side."""
    cx, cy, w, h = (float(v) for v in box[:4])
    return (cx, cy, w + 2.0 * by, h + 2.0 * by)


def apart(a: Any, b: Any) -> float:
    """How far apart two boxes `(cx, cy, w, h)` stand: the larger of their gaps on the two axes (negative where they overlap on
    both) - the measure the growth parts footprints by (`growth.keeps_its_distance`)."""
    ax, ay, aw, ah = (float(v) for v in a[:4])
    bx, by, bw, bh = (float(v) for v in b[:4])
    return max(abs(ax - bx) - (aw + bw) / 2.0, abs(ay - by) - (ah + bh) / 2.0)


def reserve_way(s: Settlement, rec: dict[str, Any], geom: Any, at: Pt) -> None:
    """Reserve the way the household seated at `at` as `rec` was admitted with: its corridor (`access.reserve`, feature 287 plan
    M3), or its walk across a neighbor's yard (`passage_of`) - kept clear of every later homestead as a corridor is
    (`AccessTree.bar`), counted against the settlement's share, and recorded on `rec`: whom it is reached across, the chain's
    depth and the walk.

    Research:
        walk not drawn as a lane - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the walk is recorded and kept clear, never drawn
        the corridor reserved as it is seated - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the older village maps find, and so reserve, each path as they seat a house
        the walk reserved as it is seated - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no way is kept while the houses are seated, the reserve-as-seated recorded there for a village-scale map only - a hamlet's reserve is unrecorded, a departure the code keeps until feature 417 T32; the walk kept as no-build ground while the houses are seated, so later houses keep off it
    """
    if geom.get("access") is not None:
        reserve(s, geom["access"], at)
    passage = geom.get("passage")
    if passage is None:
        return
    for a, b in zip(passage["walk"], passage["walk"][1:], strict=False):
        s._access.bar(a, b)
    s._passage_left = getattr(s, "_passage_left", 0) - 1  # type: ignore[attr-defined]
    rec["reached_across"] = [round(passage["of"][0], 1), round(passage["of"][1], 1)]
    rec["passage_depth"] = passage["depth"]
    rec["passage"] = [[round(q[0], 1), round(q[1], 1)] for q in passage["walk"]]
