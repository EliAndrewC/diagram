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

from l7r.diagram.settlement import seg_dist

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


def free_seats(s: Settlement, center: Pt, step: float | None = None, field: Sequence[Pt] = ()) -> list[Pt]:
    """Every grid point of the legal ground on the canvas, nearest `center` first (homes H14; no distance from the field
    bounds it, feature 318) - and among points about as near (one grid pitch), the one nearer the `field`'s outline first
    (feature 328: the coordinates broke that tie before).

    A point is dropped unasked only where the answer is already known: in a cell the static ground surely refuses
    (`FreeGround`), or within half a pitch of a standing house (the envelope would lap the
    house's own box). Everything else is offered; the placer decides.

    Research:
        no bound from the field - research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html: no house is refused for its distance from the fields
        the exhaustive seat order - UNRESEARCHED: every legal grid point on the canvas, nearest the seat first
        about as near, nearer the fields - research/questions/0029-farmhouses-minka.drawing.html: a tie broken by nearness to the field
        about as near - UNRESEARCHED: one grid pitch
    """
    pitch = BUNDLE_PITCH * (FREE_SEAT_STEP if step is None else step)
    x0, y0, x1, y1 = 6.0, 6.0, float(s.W) - 6.0, float(s.H) - 6.0
    fg = getattr(s, "_free_ground", None)
    ni, nj = int(max(0.0, x1 - x0) // pitch) + 1, int(max(0.0, y1 - y0) // pitch) + 1
    if fg is not None:  # ...the cells past the grid's window decided in one call, not one each (`FreeGround.decide_beyond`)
        fg.decide_beyond([x0 + i * pitch for i in range(ni) for _j in range(nj)], [y0 + j * pitch for _i in range(ni) for j in range(nj)])
    out: list[Pt] = []
    for i in range(ni):
        for j in range(nj):
            q = (x0 + i * pitch, y0 + j * pitch)
            if (fg is not None and fg.point_taken(q[0], q[1])) or _near_a_house(s, q):
                continue
            out.append(q)
    edges = list(zip(field, [*field[1:], *field[:1]], strict=False)) if field else []
    out.sort(key=lambda q: (round(math.hypot(q[0] - center[0], q[1] - center[1]) / pitch), min((seg_dist(q[0], q[1], a, b) for a, b in edges), default=0.0), q))
    return out


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
