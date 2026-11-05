"""The seating's MARGIN LADDER and its marks (feature 287, homes H03, H14 and plan D2).

What a margin's seating cannot seat, no seat within reach of it can: `stage_homesteads` takes the next margin of `seat_cluster`'s
ranking (`seat["ladder"]`, `margin_ladder`), taking back what the last one seated (`seating_mark`, `unseat_to`), and past the last it
refuses the site (`SiteRefused`), naming it - D2's refusal of an impossible input, before the map exists, never a shortfall and
never a re-roll. The exhaustive pass that lived here is the Rust's since feature 444 T30 (`rust/phases/src/homesteads/grove_rounds.rs`).

Research: seat search - NONE: give-up counts and registry marks; the placer's own tests decide fit
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The exhaustive pass's grid, as a share of `BUNDLE_PITCH`: a third of a pitch (homes H14), so a pocket a homestead's
#: envelope can stand in holds a grid point within the placer's one computed move.

#: A margin's exhaustive pass is given up after this many offers in a row seat no one (feature 306, plan D2; a heuristic,
#: MEASURED: on the margins that filled, the longest run of offers between two takes was 327 (seed 47 at 40 households) and
#: 235 (seed 39); a margin that falls short takes its last house by offer 128-1,206 and offered on to 1,015-1,742 -
#: specs/306-seat-by-packing/research.md R5). A margin given up is one the ladder moves past, as one exhausted.


class SiteRefused(ValueError):
    """No margin of the site seats every declared household (plan D2): the site is refused as impossible input, naming
    the map and the count, before any later stage runs. Raised inside `stage_homesteads` - D2 names `stage_seat` as
    the refusal point, but the ladder can only be judged by seating it, which is the homestead stage's work.

    Research: every household drawn - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html, research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: a site that cannot seat every declared household is refused
    """


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
