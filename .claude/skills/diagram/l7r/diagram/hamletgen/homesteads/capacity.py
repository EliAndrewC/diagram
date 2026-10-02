"""The seating floor held where the seats are chosen (feature 287, homes H03, H14 and plan D2).

`stage_homesteads` offers seats in rounds - the front row, the ranks behind it, the rescue cloud - and each round
offers only the seats its shape proposes. A quota those rounds left short was a shortfall the map shipped with
(cohort seed 32: 13 of 14 after the field moved in 508bcd511). The pass here is the last round and the only
EXHAUSTIVE one: every point of the legal ground within the field's reach, on a grid a third of a pitch apart,
center-out from the seat, is offered to the same placer (`try_place`) until the quota is met. The placer's own tests
decide fit; this adds no rule of its own. It runs only while the quota is short, so a map the rounds seated is
untouched. A NUCLEATED cluster no longer comes here: it is grown from its first house (`growth.py`, feature 308); the
dispersed form keeps this pass and its rescue.

What it cannot seat, no seat within reach of this margin can. `stage_homesteads` then takes the next margin of
`seat_cluster`'s ranking (`seat["ladder"]`), and past the last it refuses the site (`SiteRefused`), naming it - D2's
refusal of an impossible input, before the map exists, never a shortfall and never a re-roll.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement.rolling.access import TARGETS_TRIED
from l7r.diagram.settlement.rolling.fit import FIELD_REACH_FT, within_field_reach

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

#: A margin the exhaustive pass leaves at most this many households short is searched again before the ladder gives it up
#: (feature 306, plan D2, research R6 and R9): seed 47's margins reached 38-39 of 40 and were thrown away whole.
RESCUE_SHORT = 3
#: ...on a grid this fine (a sixth of a pitch, the pass's being a third) and with a door's corridor tried to this many of the
#: tree's nearest points (`AccessTree.tried`; the pass's `TARGETS_TRIED` is 12) - a search breadth, never a rule.
RESCUE_STEP = 1.0 / 6.0
RESCUE_TARGETS = 40
#: ...and given up after this many offers in a row seat no one (the perf-audit of feature 306: every rescue that seated its houses
#: on the sixteen reference seeds at 40 households took them by offer 512; seed 39's, two short, offered 2,772 of 2,784 grid
#: points to take one house and still fall short - 7 s that bought no change of margin. With the cap seed 39 is 15.1 -> 9.3 s and
#: the other fifteen seat as before - specs/306-seat-by-packing/research.md R17)
RESCUE_DRY_SPELL = 600


class SiteRefused(ValueError):
    """No margin of the site seats every declared household (plan D2): the site is refused as impossible input, naming
    the map and the count, before any later stage runs. Raised inside `stage_homesteads` - D2 names `stage_seat` as
    the refusal point, but the ladder can only be judged by seating it, which is the homestead stage's work."""


def _near_a_house(s: Settlement, q: Pt) -> bool:
    return any(math.hypot(q[0] - float(h["x"]), q[1] - float(h["y"])) < BUNDLE_PITCH * 0.5 for h in s.M.get("houses", []))


def free_seats(s: Settlement, center: Pt, step: float | None = None) -> list[Pt]:
    """Every grid point of the legal ground within the field's reach, nearest `center` first (homes H14).

    A point is dropped unasked only where the answer is already known: in a cell the static ground surely refuses
    (`FreeGround`), beyond `within_field_reach`, or within half a pitch of a standing house (the envelope would lap the
    house's own box). Everything else is offered; the placer decides."""
    pitch = BUNDLE_PITCH * (FREE_SEAT_STEP if step is None else step)
    reach = s.px(FIELD_REACH_FT)
    pts = [p for ch in (getattr(s, "_site_chains", None) or []) for a, b, _n in ch for p in (a, b)]
    x0, y0, x1, y1 = 6.0, 6.0, float(s.W) - 6.0, float(s.H) - 6.0
    if pts:
        x0, x1 = max(x0, min(p[0] for p in pts) - reach), min(x1, max(p[0] for p in pts) + reach)
        y0, y1 = max(y0, min(p[1] for p in pts) - reach), min(y1, max(p[1] for p in pts) + reach)
    fg = getattr(s, "_free_ground", None)
    out: list[Pt] = []
    for i in range(int(max(0.0, x1 - x0) // pitch) + 1):
        for j in range(int(max(0.0, y1 - y0) // pitch) + 1):
            q = (x0 + i * pitch, y0 + j * pitch)
            if (fg is not None and fg.point_taken(q[0], q[1])) or not within_field_reach(s, q[0], q[1]) or _near_a_house(s, q):
                continue
            out.append(q)
    out.sort(key=lambda q: (math.hypot(q[0] - center[0], q[1] - center[1]), q))
    return out


def seat_the_rest(s: Settlement, plan: SitePlan, placed: int) -> int:
    """The exhaustive pass: `free_seats` offered to the placer until `plan.spec.households` stand, given up after `DRY_SPELL`
    offers in a row seat no one; then, where it left at most `RESCUE_SHORT` households, the rescue (`rescue_the_margin`).
    Returns the new count; records the seats offered and taken (`seat_search.exhaustive_offered`, `exhaustive_took`)."""
    want = plan.spec.households
    if placed >= want:
        return placed
    offered = took = 0
    seats = free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])))
    # ...FROM THE SEAT REGION (feature 297, FR-001, plan B1): the whole list offered at once, only what the region holds
    region = getattr(s, "_seat_region", None)
    if region is not None:
        seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    placed, offered, took = offer_seats(s, seats, placed, want, DRY_SPELL)
    s._seat_search["exhaustive_offered"], s._seat_search["exhaustive_took"] = offered, took
    if 0 < want - placed <= RESCUE_SHORT:  # a margin that holds everyone already needs no rescue (the perf-audit: every seed built
        placed = rescue_the_margin(s, plan, placed)  # its 2,400-3,900-point grid for nothing)
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


def rescue_the_margin(s: Settlement, plan: SitePlan, placed: int) -> int:
    """A NEAR MISS SEARCHED AGAIN (feature 306, plan D2): the margin's free ground on `RESCUE_STEP`'s finer grid, each door's
    corridor tried to `RESCUE_TARGETS` of the tree's nearest points - the same rules, a wider search, for the last few
    households a whole margin would otherwise be thrown away for (seed 47 at 40 households: 7 margins -> 3, research R9).
    The corridor search's memory (`_corridor_memo`) holds candidates found at the narrower breadth, so it is dropped on the
    way in and out, and the tree's breadth set back. Records `seat_search.rescue_offered`, `rescue_took`."""
    seats = free_seats(s, (float(plan.seat["cx"]), float(plan.seat["cy"])), RESCUE_STEP)
    region = getattr(s, "_seat_region", None)
    if region is not None:
        seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
    tree = getattr(s, "_access", None)
    if tree is not None:
        tree.tried, tree._targets = RESCUE_TARGETS, {}
    s.__dict__.pop("_corridor_memo", None)
    try:
        placed, offered, took = offer_seats(s, seats, placed, plan.spec.households, RESCUE_DRY_SPELL)
    finally:
        if tree is not None:
            tree.tried, tree._targets = TARGETS_TRIED, {}
        s.__dict__.pop("_corridor_memo", None)
    s._seat_search["rescue_offered"], s._seat_search["rescue_took"] = offered, took
    return placed


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
    """Take back every house seated since `mark` (a margin the ladder leaves). Each registry is cut in place - the
    `Indexed` lists bump their own version, so no index answers from the houses taken back."""
    h, p, f, rh, bp, hp = mark
    del s.M["houses"][h:]
    del s.placed[p:]
    del s._pending_farmsteads[f:]
    if "row_holdings" in s.M:
        del s.M["row_holdings"][rh:]
    del s.block_polys[bp:]
    del s.hard_polys[hp:]
