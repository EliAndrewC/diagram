"""A household reached across a neighbor's yard (feature 317, plan D2-D5).

THE CUSTOM (research/questions/0081-village-lanes.html): passage over a neighbor's land for land with no road access of its own -
"where A's land is so situated that he cannot reach the highway without passing over B's land, A has the right to do so"
(Wigmore 1892, Part V Section 8; seven provinces, three of them towns) - and as a chain, Echigo's plot C passing over both B's
and A's. No page read states that every house in a clustered village fronted a lane of its own.

WHERE IT CAN ARISE: the grown cluster parts every two homesteads by a path's whole strip (`growth.grow_gap`), so no household
stood behind a neighbor's land and the custom's condition never arose (research R3: the nearest neighbor's yard 64 ft at the
least from any door refused a path). So, within the settlement's rolled share (`passage_budget`), each standing house also
offers TIGHT seats - at the parting with no path's strip (`hamletgen/homesteads/growth.py`) - and a household offered one is
seated there only by passage: it asks for a corridor first (`access.access_corridor`), a household that finds one is refused
the tight seat, and one that finds none is admitted where:

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
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from .._geom import Pt
from .._knobs import knob_rng
from .access import doors_of, fixtures_clear, house_clear, house_gap, parts_clear, seg_box_within, site_edge_samples, site_samples_clear

if TYPE_CHECKING:
    from ..core import Settlement

#: How far beyond the growth's 2 px parting a household's envelope may stand from its neighbor's land and still ADJOIN it, in
#: feet: a GUESS - a foot of tolerance for the placer's rounding; the custom's condition is land against land, not a reach.
PASSAGE_ADJOIN_FT = 1.0
#: The longest chain of passages from a household to a corridor: a GUESS citing Wigmore's Echigo entry, where plot C passes over
#: both B's and A's to the highway - the longest chain the record reads.
PASSAGE_CHAIN = 2
#: The share of a nucleated settlement's households that may be reached by passage, rolled per settlement: a GUESS - the record
#: attests the custom, not how common it was, and a clustered village whose rear households all walked through their neighbors'
#: yards is not what its entries describe (alleys to the rear houses, Morse; blind alleys to the houses, the Manchu survey).
PASSAGE_SHARE_BAND = (0.0, 0.25)
#: The pitch the walk is sampled at to ask that it stays on the two households' land, in px.
WALK_STEP_PX = 4.0

Box = tuple[float, float, float, float]


def passage_share(seed: int) -> float:
    """The settlement's share of households that may be reached by passage, rolled from the map's seed within
    `PASSAGE_SHARE_BAND` (the knob doctrine: it depends on the seed and the knob's name, never on draw order)."""
    lo, hi = PASSAGE_SHARE_BAND
    return round(lo + knob_rng(seed, "passage_share").random() * (hi - lo), 3)


def passage_budget(share: float, households: int) -> int:
    """How many of a settlement's `households` may be reached by passage at its rolled `share`."""
    return int(math.floor(share * households))


def depth_of(rec: Any) -> int | None:
    """How many passages lie between a seated household and a corridor: 0 for one with a corridor of its own, its passage's
    depth for one reached across a yard, None for one with neither (no household the tree reaches)."""
    if rec.get("passage_depth") is not None:
        return int(rec["passage_depth"])
    return 0 if (rec.get("geom") or {}).get("access") is not None else None


def box_foot(p: Pt, box: Any) -> Pt:
    """The point of the box `(cx, cy, w, h)` nearest `p`."""
    cx, cy, w, h = (float(v) for v in box[:4])
    return (min(max(p[0], cx - w / 2), cx + w / 2), min(max(p[1], cy - h / 2), cy + h / 2))


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


def adjoins(own: Any, land: Any, tol: float) -> bool:
    """Does the envelope `own` stand against the neighbor's `land` - no farther from it than `tol`?"""
    return apart(own, land) <= tol


def on_their_land(a: Pt, b: Pt, lands: Any, step: float) -> bool:
    """Does every point of the walk a-b, sampled every `step`, lie on one of the `lands` (boxes `(cx, cy, w, h)`)?"""
    n = max(1, int(math.ceil(math.dist(a, b) / step)))
    for k in range(n + 1):
        t = k / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if not any(abs(x - float(bx[0])) <= float(bx[2]) / 2.0 + 1e-9 and abs(y - float(bx[1])) <= float(bx[3]) / 2.0 + 1e-9 for bx in lands):
            return False
    return True


def walk_clear(s: Settlement, door: Pt, foot: Pt, geom: Any, rec: Any, hgap: float, half: float, wood: Any) -> bool:
    """Is the walk `door`-`foot` clear (`passage_of`)? Of the household's own house, beds and fixtures by the corridor's own
    leg tests; of the neighbor's house, beds, sheds and fixtures by the same (its yard is the ground the walk arrives on); of
    every other placed homestead whole; of the static ground the site refuses; of the reserved wood seats."""
    if not (house_clear(door, foot, geom, hgap) and fixtures_clear(s, door, foot, geom) and parts_clear(s, door, foot, geom)):
        return False
    nb = rec.get("geom") or {}
    if not (house_clear(door, foot, nb, hgap) and fixtures_clear(s, door, foot, nb) and parts_clear(s, door, foot, nb)):
        return False
    mine = tuple(float(v) for v in (nb.get("bbox") or ())[:4])
    x0, y0, x1, y1 = min(door[0], foot[0]), min(door[1], foot[1]), max(door[0], foot[0]), max(door[1], foot[1])
    for it in s._reach_index(s.placed, "placed_reach").near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + half):
        box = (float(it[0]), float(it[1]), float(it[2]), float(it[3]))
        if mine and all(abs(p - q) < 1e-6 for p, q in zip(box, mine, strict=True)):
            continue  # the neighbor's own homestead: its parts were asked one by one above
        if seg_box_within(door, foot, box, half):
            return False
    edge = site_edge_samples(s, door, foot)
    if edge is None or not site_samples_clear(s, edge):
        return False
    return not (wood is not None and wood.corridor_bars(door, foot))


def walk_of(s: Settlement, geom: Any, rec: Any, door: Pt, yard: Any, lands: Any, hgap: float, half: float, wood: Any) -> tuple[Pt, ...] | None:
    """The walk from `door` to the neighbor's `yard`, routed on the map's own router (`route.search`, `route.taut`) over the
    cells on the two households' `lands` that clear both households' houses, beds, sheds and fixtures (`route.own_parts`), every
    other placed homestead, the site's taken ground and the reserved wood seats, and pulled taut through `walk_clear` and
    `on_their_land`; its last point on the yard's edge. None where no walk is found."""
    from .access import doubles_back
    from .route import ROUTE_LEGS, ROUTE_STEP_PX, ROUTE_WEIGHT, own_parts, search, taut

    step = ROUTE_STEP_PX
    nb = rec.get("geom") or {}
    keep = [
        *own_parts(s, geom, (geom.get("boxes") or {}).get("house") or geom["house"], hgap, half),
        *own_parts(s, nb, (nb.get("boxes") or {}).get("house") or nb["house"], hgap, half),
    ]
    mine = tuple(float(v) for v in (nb.get("bbox") or ())[:4])
    placed = s._reach_index(s.placed, "placed_reach")
    fg = getattr(s, "_free_ground", None)
    x0, y0 = door

    def at(c: tuple[int, int]) -> Pt:
        return (x0 + c[0] * step, y0 + c[1] * step)

    def is_open(c: tuple[int, int]) -> bool:
        p = at(c)
        if not any(abs(p[0] - float(b[0])) <= float(b[2]) / 2.0 and abs(p[1] - float(b[1])) <= float(b[3]) / 2.0 for b in lands):
            return False
        if fg is not None and fg.point_taken(p[0], p[1]):
            return False
        if any(seg_box_within(p, p, b, g) for b, g in keep):
            return False
        for it in placed.near(p[0], p[1], half):
            box = (float(it[0]), float(it[1]), float(it[2]), float(it[3]))
            if not (mine and all(abs(u - v) < 1e-6 for u, v in zip(box, mine, strict=True))) and seg_box_within(p, p, box, half):
                return False
        return not (wood is not None and wood.corridor_bars(p, p))

    def goal_of(c: tuple[int, int]) -> Pt | None:
        p = at(c)
        foot = box_foot(p, yard)
        return foot if math.dist(p, foot) <= step else None

    def first_ok(c: tuple[int, int]) -> bool:
        p = at(c)
        return house_clear(door, p, geom, hgap) and fixtures_clear(s, door, p, geom) and parts_clear(s, door, p, geom)

    def leg_ok(a: Pt, b: Pt) -> bool:
        return on_their_land(a, b, lands, s.px(WALK_STEP_PX)) and walk_clear(s, a, b, geom, rec, hgap, half, wood)

    span = max(max(float(b[2]), float(b[3])) for b in lands)
    found = search(is_open, goal_of, [((float(yard[0]) - x0) / step, (float(yard[1]) - y0) / step)], int(span / step) + 2, ROUTE_WEIGHT, (0, 0), first_ok)
    if found is None:
        return None
    cells, q = found
    return taut([door, *(at(c) for c in cells[1:]), q], leg_ok, doubles_back, ROUTE_LEGS)


def passage_of(s: Settlement, geom: Any) -> dict[str, Any] | None:
    """The passage a household laid as `geom` at a TIGHT seat (`s._tight_of`: the neighbor's record, its land as the growth
    parts it, the household's own allotted reach, the parting) is reached by, or None (the module's account):
    `{"walk", "of", "depth"}`, the walk from its first dooryard door that has one (`walk_of`). None off a tight seat, past the
    settlement's share (`s._passage_left`), or where the chain would run past `PASSAGE_CHAIN`."""
    tight = getattr(s, "_tight_of", None)
    tree = getattr(s, "_access", None)
    if tight is None or tree is None or getattr(s, "_passage_left", 0) <= 0:
        return None
    rec, land, gap = tight["rec"], tight["land"], float(tight["gap"])
    depth = depth_of(rec)
    yard = ((rec.get("geom") or {}).get("boxes") or {}).get("yard")
    if depth is None or depth >= PASSAGE_CHAIN or yard is None:
        return None
    hx, hy = (float(v) for v in ((geom.get("boxes") or {}).get("house") or geom["house"])[:2])
    w, e, n, so = (float(v) for v in tight["own"])
    own = (hx + (e - w) / 2.0, hy + (so - n) / 2.0, w + e, n + so)  # its land, carried with its house
    tol = gap + s.px(PASSAGE_ADJOIN_FT)
    if not adjoins(own, land, tol):
        return None
    lands = [grown(own, tol), grown(land, tol)]
    hgap, half, wood = house_gap(s), float(tree.half), getattr(s, "_wood", None)
    for door in doors_of(geom, half)[:2]:
        walk = walk_of(s, geom, rec, door, yard, lands, hgap, half, wood)
        if walk is not None:
            return {"walk": walk, "of": (float(rec["x"]), float(rec["y"])), "depth": depth + 1}
    return None
