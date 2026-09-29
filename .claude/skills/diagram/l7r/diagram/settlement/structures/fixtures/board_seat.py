"""The notice board's seat, decided where the board is sited (feature 287, labels L1-L4, L7, L11, L12, L14).

The one caption placer never refuses a caption (the GM: *"we'll treat labels as mandatory"*), so a caption rule about
the board cannot be held inside the placer by dropping the caption. It is held by the placer that decides the SUBJECT:
`place_kosatsuba` keeps only a board seat whose caption the one placer seats clean (`board_caption_seat`), inside the
view (`board_in_view`), off the title placard (`under_placard`), and - for an `entrance` board - where every household's
way out passes it (`entrance_seat_ok`). The seat it proved rides to the label phase and is drawn as proved. The
functions here are the rules' ONE predicates: the siter calls them and the tests call them (FR-003).

THE TERMINAL IS THE GM'S QUESTION (plan D12): where no verge in the view takes a board whose caption clears roofs,
lanes, crowns and neighbors, every option breaks one of the GM's own rulings - no board (against "every settlement
carries the board", 2026-07-24), a board off the way (against `kosatsuba_by_the_road`), or a caption breaking a caption
rule (against the caption rules). Until the GM answers, the siter keeps the behavior it had (`D12_AWAITING_THE_GM`).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any, NamedTuple

from ....labels import ObstacleIndex, Placement, place
from ..._geom import nearest_way_bearing
from ..._knobs import KNOBS, Knob, resolve_knob
from ._helpers import KOSATSUBA_ANCHOR_BAND_FT, KOSATSUBA_ENTRANCE_REACH_FT, KOSATSUBA_HANDOVER_BAND_FT, RouteReach
from .boards import BOARD_CAPTION_SIZE, board_subject

KOSATSUBA_WAY_REACH_FT = 60.0
"""How far from a route the board's candidate seats are sampled, in real feet - `kosatsuba_by_the_road`'s ~60 ft band.
Stated once (feature 287, labels L11): the siter samples within it and the test reads it, where the gate test carried a
separate, looser 90 px."""

PLACARD_KEEP_FT = 4.0
"""How far a board stands off the title placard (feature 287, labels L14): the placard is drawn after the crop and the
board after the placard, and nothing kept the plank from being posted under the card. Four feet is the reading gap
every other "these two inked things are separate" rule on these maps uses (`CAPTION_FEATURE_GAP`)."""

D12_AWAITING_THE_GM = True
"""D12: awaiting the GM. With no board seat in the view whose caption the one placer seats clean, the siter keeps the
behavior it had before feature 287 - the board at the best-ranked seat, its caption at the least-cost seat
(`place(least=True)`) - and records `meta.kosatsuba_d12`, so the maps reaching the question can be counted."""


class BoardSeat(NamedTuple):
    """A candidate board seat: its traffic count and score, its center and bearing, its gap from the tread edge to the
    board's edge, whether trees stand over it, and whether it stands on the approach itself."""

    busy: int
    score: float
    x: float
    y: float
    rot: float
    gap: float
    shaded: bool
    approach: bool


class SiteEnv(NamedTuple):
    """What every candidate seat is tested against, built once per siting: the view, the way beds' segment index, the
    dwellings a seat's traffic counts, the `kosatsuba_siting` knob and the wells it reads, and the crowns."""

    view: Any
    beds: Any
    spots: list[tuple[float, float]]
    siting: str
    wells: list[tuple[float, float]]
    canopy: Any


def board_in_view(view: Sequence[float] | None, x: float, y: float, w: float, h: float) -> bool:
    """Does a board of drawn `w` x `h` seated at (x, y) stand wholly inside the view (x, y, width, height), at any turn -
    inset by the footprint's own half-diagonal (feature 287, labels L2; the frame's re-seat's `_inset`, lifted)? True
    where no view is recorded yet."""
    if not view:
        return True
    vx, vy, vw, vh = (float(v) for v in view)
    inset = math.hypot(w, h) / 2
    return vx + inset <= x <= vx + vw - inset and vy + inset <= y <= vy + vh - inset


def under_placard(M: Any, x: float, y: float, w: float, h: float, keep: float) -> bool:
    """Would a board seated at (x, y) stand within `keep` of the title placard (feature 287, labels L14)?"""
    title = M.get("title") or {}
    box = title.get("placard") or title.get("bbox")
    if not box:
        return False
    half = math.hypot(w, h) / 2 + keep
    return bool(float(box[0]) - half < x < float(box[2]) + half and float(box[1]) - half < y < float(box[3]) + half)


def board_caption_seat(M: Any, x: float, y: float, hw: float, hh: float, rot: float, label: str, index: ObstacleIndex, frame: Any) -> Placement | None:
    """THE ONE PREDICATE of the board's caption rules (feature 287, labels L4-L7): the seat the one placer gives the
    caption of a board seated here, AT THE ANGLE THE BOARD WILL BE DRAWN AT (the nearest way's bearing - a half-turn
    flips which side the placer ranks first), when that seat is FREE and BESIDE the board - clear of every roof, lane,
    crown and caption `index` holds (`place(strict=True)`), inside `frame`, at the preferred offset with no leader, where
    the association term holds it nearer its board than any neighbor - else None."""
    nb = nearest_way_bearing(M, x, y)
    turn = nb if nb is not None else rot
    return place(label, BOARD_CAPTION_SIZE, board_subject(x, y, turn, 2 * hw, 2 * hh), index, frame, strict=True, max_ring=0)


def entrance_seat_ok(seat: BoardSeat, anchor: tuple[float, float], reach: RouteReach | None, ftpx: float) -> bool:
    """THE ONE PREDICATE of an entrance board's ground (feature 287, labels L1): within
    `KOSATSUBA_ENTRANCE_REACH_FT + KOSATSUBA_ANCHOR_BAND_FT` of the entrance anchor, and - at a handover - passed by every
    household's way out within `KOSATSUBA_HANDOVER_BAND_FT`."""
    if math.hypot(seat.x - anchor[0], seat.y - anchor[1]) > (KOSATSUBA_ENTRANCE_REACH_FT + KOSATSUBA_ANCHOR_BAND_FT) / ftpx:
        return False
    return reach is None or reach.missed(seat.x, seat.y, KOSATSUBA_HANDOVER_BAND_FT / ftpx) == 0


Proof = Callable[[BoardSeat], "tuple[bool, Placement | None]"]
"""A seat's caption proof: whether its caption fits, and the seat the placer gives it (None for a board with no caption)."""


def choose_board(seats: list[BoardSeat], proof: Proof) -> tuple[BoardSeat, Placement | None] | None:
    """The board's seat among `seats`, walked in the order of their score (stably, so a tie keeps the first): the first
    whose caption fits in the OPEN, else the first whose caption fits under the trees (the GM, 2026-08-29: a board under a
    canopy is fine "as long as there is a label attached to it and the label is visible"), else None. ASKED LAZILY
    (feature 284): the caption's proof is a placement against every obstacle, so the walk stops at the first open fit."""
    shaded: tuple[BoardSeat, Placement | None] | None = None
    for c in sorted(seats, key=lambda c: c.score, reverse=True):
        ok, p = proof(c)
        if not ok:
            continue
        if not c.shaded:
            return c, p
        if shaded is None:
            shaded = (c, p)
    return shaded


def resolve_seat(seed: int, context: dict[str, Any], pinned: dict[str, Any], sitable: set[str]) -> str:
    """The `kosatsuba_seat` knob resolved over the placements this map can SITE (feature 287, labels L1: the knob's value
    space is constrained, the affordance mechanism it already uses for an approach or an official's house). The roll is the
    knob's own (`Knob.roll`: the same per-knob draw) over its typing-filtered values that are sitable, so a map that can site
    every placement rolls exactly as before. A PINNED placement the map cannot site is refused, naming it - declared input
    the site cannot honor (plan D7's kind), never a board drawn against its rules."""
    knob = KNOBS["kosatsuba_seat"]
    want = pinned.get("kosatsuba_seat")
    if want is not None:
        if want in knob.value_space and knob.typing_rule(want, context) and want not in sitable:
            raise ValueError(f"knob 'kosatsuba_seat': pinned {want!r}, but no verge in the view takes a board there whose caption stands clear")
        return str(resolve_knob("kosatsuba_seat", seed, context, pinned))
    return str(Knob("kosatsuba_seat", [v for v in knob.value_space if v in sitable], knob.default, knob.typing_rule).roll(seed, context))
