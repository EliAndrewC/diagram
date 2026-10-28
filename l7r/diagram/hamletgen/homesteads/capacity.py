"""The seating floor held where the seats are chosen (feature 287, homes H03, H14 and plan D2).

`stage_homesteads` offers seats in rounds - the front row, the ranks behind it, the rescue cloud - and each round
offers only the seats its shape proposes. A quota those rounds left short was a shortfall the map shipped with
(cohort seed 32: 13 of 14 after the field moved in 508bcd511). The pass here is the last round and the only
EXHAUSTIVE one: every point of the legal ground on the canvas, on a grid a third of a pitch apart,
center-out from the seat, is offered to the same placer (`try_place`) until the quota is met. The placer's own tests
decide fit; this adds no rule of its own. It runs only while the quota is short, so a map the rounds seated is
untouched. A NUCLEATED cluster no longer comes here: it is grown from its first house (`growth.py`, feature 308); the
dispersed form keeps this pass.

What it cannot seat, no seat within reach of this margin can. `stage_homesteads` then takes the next margin of
`seat_cluster`'s ranking (`seat["ladder"]`), and past the last it refuses the site (`SiteRefused`), naming it - D2's
refusal of an impossible input, before the map exists, never a shortfall and never a re-roll.

Research: seat search - NONE: grids, offer order, give-up counts and registry marks; the placer's own tests decide fit
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.work_counts import OPS

from ..consts import BUNDLE_PITCH, Pt

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The exhaustive pass's grid, as a share of `BUNDLE_PITCH`: a third of a pitch (homes H14), so a pocket a homestead's
#: envelope can stand in holds a grid point within the placer's one computed move.
FREE_SEAT_STEP = 1.0 / 3.0

#: A margin's exhaustive pass is given up after this many offers in a row seat no one (feature 306, plan D2; a heuristic,
#: MEASURED: on the margins that filled, the longest run of offers between two takes was 327 (seed 47 at 40 households) and
#: 235 (seed 39); a margin that falls short takes its last house by offer 128-1,206 and offered on to 1,015-1,742 -
#: specs/306-seat-by-packing/research.md R5). A margin given up is one the ladder moves past, as one exhausted.
DRY_SPELL = 400


class SiteRefused(ValueError):
    """No margin of the site seats every declared household (plan D2): the site is refused as impossible input, naming
    the map and the count, before any later stage runs. Raised inside `stage_homesteads` - D2 names `stage_seat` as
    the refusal point, but the ladder can only be judged by seating it, which is the homestead stage's work.

    Research: every household drawn - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html, research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: a site that cannot seat every declared household is refused
    """


def _near_a_house(s: Settlement, q: Pt) -> bool:
    return any(math.hypot(q[0] - float(h["x"]), q[1] - float(h["y"])) < BUNDLE_PITCH * 0.5 for h in s.M.get("houses", []))


def field_distances(field: Sequence[Pt], xs: Any, ys: Any) -> Any:
    """Each point's distance to the field's outline (its ring), in one vectorized call, as an array; zeros where there is no
    field.

    Research: field distance - NONE: a ring's distance to points"""
    import numpy as np  # noqa: PLC0415 - bound on first use

    x, y = np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64)
    if len(field) < 3 or not len(x):
        return np.zeros(x.shape)
    import shapely  # noqa: PLC0415 - bound on first use

    return np.asarray(shapely.distance(shapely.LinearRing(list(field)), shapely.points(x, y)), dtype=np.float64)


def free_seats(s: Settlement, center: Pt, step: float | None = None, field: Sequence[Pt] = ()) -> list[Pt]:
    """Every grid point of the legal ground on the canvas, nearest `center` first (homes H14; no distance from the field
    bounds it, feature 318) - and among points about as near (one grid pitch), the one nearer the `field`'s outline first
    (feature 328: the coordinates broke that tie before).

    A point is dropped unasked only where the answer is already known: in a cell the static ground surely refuses
    (`FreeGround`), or within half a pitch of a standing house (the envelope would lap the
    house's own box). Everything else is offered; the placer decides.

    Research:
        no bound from the field - research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html: no house is refused for its distance from the fields
        the exhaustive seat order - research/questions/0029-farmhouses-minka.drawing.html: every legal grid point on the canvas, nearest the seat first
        about as near, nearer the fields - research/questions/0029-farmhouses-minka.drawing.html: a tie broken by nearness to the field
        about as near - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); one grid pitch
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (seat grid inset 6 px from the sheet edge)
    """
    import numpy as np  # noqa: PLC0415 - bound on first use (feature 237)

    pitch = BUNDLE_PITCH * (FREE_SEAT_STEP if step is None else step)
    x0, y0, x1, y1 = 6.0, 6.0, float(s.W) - 6.0, float(s.H) - 6.0
    fg = getattr(s, "_free_ground", None)
    ni, nj = int(max(0.0, x1 - x0) // pitch) + 1, int(max(0.0, y1 - y0) // pitch) + 1
    # THE GRID AS ARRAYS (feature 427 T07): the points in the order the loops made them (column by column), each asked
    # `point_taken` in one call (`FreeGround.points_taken`, the cells past the grid decided at once as before)
    gx = np.repeat(x0 + np.arange(ni) * pitch, nj)
    gy = np.tile(y0 + np.arange(nj) * pitch, ni)
    keep = ~fg.points_taken(gx, gy) if fg is not None else np.ones(gx.shape, dtype=bool)
    # ...EVERY POINT AGAINST EVERY HOUSE IN ONE NUMPY PASS (feature 427 T04, R3: `_near_a_house`'s `any(math.hypot(...))` per
    # point was 82k calls at 40 households, the T01 survey): the same half-pitch test, `np.hypot` for `math.hypot`
    houses = s.M.get("houses", [])
    if keep.any() and houses:
        hs = np.array([(float(h["x"]), float(h["y"])) for h in houses])
        qx, qy = gx[keep], gy[keep]
        near = (np.hypot(qx[:, None] - hs[None, :, 0], qy[:, None] - hs[None, :, 1]) < BUNDLE_PITCH * 0.5).any(axis=1)
        keep[np.nonzero(keep)[0][near]] = False
    qx, qy = gx[keep], gy[keep]
    out = list(zip(qx.tolist(), qy.tolist(), strict=True))
    # THE FIELD DISTANCE ASKED ONCE FOR EVERY POINT (wave 20's pair: a scan of the outline's edges per point inside the sort
    # cost the homesteads stage up to +1.5 s a roll) - one vectorized shapely call, the same distance
    fd = field_distances(field, qx, qy)
    # ...AND THE SORT ON ARRAYS (feature 427 T07: a key tuple per point): the pitch ring, then the field distance, then the
    # point - `np.lexsort`'s last key first; a stable sort of the same keys keeps the same order
    ring = np.round(np.hypot(qx - center[0], qy - center[1]) / pitch)
    order = np.lexsort((qy, qx, fd, ring))
    return [out[k] for k in order.tolist()]


def seat_the_rest(s: Settlement, plan: SitePlan, placed: int) -> int:
    """The exhaustive pass: `free_seats` offered to the placer until `plan.spec.households` stand, given up after `DRY_SPELL`
    offers in a row seat no one. No near miss is searched again (feature 318: the rescue that re-searched a margin before the
    ladder took its houses back went with the take-back). Returns the new count; records the seats offered and taken (`seat_search.exhaustive_offered`, `exhaustive_took`)."""
    want = plan.spec.households
    if placed >= want:
        return placed
    offered = took = 0
    seats = free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])), field=plan.envelope)
    # ...FROM THE SEAT REGION (feature 297, FR-001, plan B1): the whole list offered at once, only what the region holds
    region = getattr(s, "_seat_region", None)
    if region is not None:
        seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    placed, offered, took = offer_seats(s, seats, placed, want, DRY_SPELL)
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    return placed


def offer_seats(s: Settlement, seats: Sequence[Pt], placed: int, want: int, dry: int | None) -> tuple[int, int, int]:
    """Offer `seats` in order to the placer until `want` stand (or `dry` offers in a row seat no one): `(placed, offered,
    took)`. A seat a house this pass seated now stands on is passed over."""
    offered = took = since = 0
    for q in seats:
        if __debug__:
            OPS["candidate@offer_seats"] += 1
        if placed >= want or (dry is not None and since >= dry):
            break
        if _near_a_house(s, q):
            continue  # a house this pass seated stands here now
        offered += 1
        since += 1
        s._seat_search["candidates"] += 1
        if s.try_place(q[0], q[1], "plain"):
            placed += 1
            took += 1
            since = 0
    return placed, offered, took


def margin_ladder(plan: SitePlan, polder: bool) -> list[dict[str, Any]]:
    """The seat's ranked alternatives (`seat_cluster`'s `ladder`), best first, for when the chosen margin cannot seat
    every household. ON A POLDER only the margins on the chosen seat's own compass flank: the waterward fringe was drawn
    before the houses (`stage_waterward`, WATER's) on every flank the village does not stand on, so a seat on another
    flank would stand in reeds laid for a wet flank - the ladder is confined to margins that leave the fringe valid."""
    ladder = list((plan.seat or {}).get("ladder") or [])
    if not polder:
        return ladder
    return [m for m in ladder if compass(m["out"]) == compass(plan.seat["out"])]


def compass(v: Sequence[float]) -> str:
    """The compass letter a screen-space vector points to - `polder_flanks`' own reading (screen y grows down)."""
    return ("E" if v[0] > 0 else "W") if abs(v[0]) >= abs(v[1]) else ("S" if v[1] > 0 else "N")


def seating_mark(s: Settlement) -> tuple[int, ...]:
    """Where the registries a seating writes stand before it: houses, the placed boxes, the pending farmsteads - and a row
    village's far-row holdings, which `rows.seat_rows` records and blocks as it seats their farms (feature 291)."""
    return (
        len(s.M.get("houses", [])),
        len(s.placed),
        len(s._pending_farmsteads),
        len(s.M.get("row_holdings") or []),
        len(s.block_polys),
        len(s.hard_polys),
    )


def unseat_to(s: Settlement, mark: tuple[int, ...]) -> None:
    """Cut every registry back to `mark` (a margin the ladder leaves, which seated no house - feature 318: only its own
    reservations go). Each registry is cut in place - the `Indexed` lists bump their own version, so no index answers from
    what was cut. A house cut is counted in `meta.houses_taken_back`, which every rolled hamlet holds at 0 (SC-001,
    `tests/gate/hamletgen/test_driver.py`)."""
    h, p, f, rh, bp, hp = mark
    meta = s.M.setdefault("meta", {})
    meta["houses_taken_back"] = int(meta.get("houses_taken_back") or 0) + max(0, len(s.M["houses"]) - h)
    del s.M["houses"][h:]
    del s.placed[p:]
    del s._pending_farmsteads[f:]
    if "row_holdings" in s.M:
        del s.M["row_holdings"][rh:]
    del s.block_polys[bp:]
    del s.hard_polys[hp:]
