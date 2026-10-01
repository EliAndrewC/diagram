"""The notice board's seat, decided where the board is sited (feature 287, labels L1-L4, L7, L11, L12, L14).

The one caption placer never refuses a caption (the GM: *"we'll treat labels as mandatory"*), so a caption rule about
the board cannot be held inside the placer by dropping the caption. It is held by the placer that decides the SUBJECT:
`place_kosatsuba` keeps only a board seat whose caption the one placer seats clean (`board_caption_seat`), inside the
view (`board_in_view`), off the title placard (`under_placard`), turned square to its way (`WayFacing.turn`), and - for an `entrance` board - where every household's
way out passes it (`entrance_seat_ok`). The seat it proved rides to the label phase and is drawn as proved. The
functions here are the rules' ONE predicates: the siter calls them and the tests call them (FR-003).

THE CLEAN CAPTION IS A PREFERENCE, NOT A CONDITION OF SITING (plan D12, answered by the GM 2026-09-30: *"The caption
sitting clean is not a hard requirement. It should sit clean when possible but it is okay for it to not sit clean."*).
The board is always posted by its way (every settlement carries it, GM 2026-07-24; `kosatsuba_by_the_road`), and its
caption is sited in three steps, each asked only where the one before found no seat: a seat whose caption the one placer
seats clean beside it (`board_caption_seat`); else a seat whose caption, on a leader or in the key (D10), clears every
way (`terminal_caption`); else the best roadside seat by the other rules, its caption wherever the one placer's normal
fallback puts it (`fallback_caption`) - never no board over its caption.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any, NamedTuple

from ....labels import ObstacleIndex, Placement, caption_clears_ways, keyed, place
from ....labels.geom import rect
from ....labels.obstacles import stands_nearest
from ..._geom import PointGrid, nearest_way_bearing, seg_dist, street_runs
from ..._knobs import KNOBS, Knob, resolve_knob
from ...finish import recorded_caption_quad
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

FACING_DEG = 45.0
"""How far off parallel to its way a board may stand and still face it (`kosatsuba_faces_the_road`, labels L12): past it the
plank is side-on, unreadable to the traffic it was posted for. The retired gate test's `FACING_DEG`, stated once here."""

FACING_TIE_PX = 1.0
"""How near two ways must stand to a board for BOTH to be its "nearest way" (feature 287 wave 6, labels L12). Beside a
lane's corner the seat is equidistant from both arms, and which one is nearest is decided by rounding: the manifest
records the board and every lane vertex to 0.1 px, which moves a distance by up to ~0.15 px. Measured (2026-09-29, method:
cohort seeds 25 and 42 rolled and read by a spec harness): seed 25's board stood 9.449 px from one arm and 9.500 px from
the other, 54.7 degrees apart; seed 42's stood 8.006 px from both arms of a corner 86 degrees apart - each turned to one arm
and judged against the other. One px is several times the rounding and far below any verge step (5 px), so it catches
every such tie and nothing else."""


def off_parallel(a: float, b: float) -> float:
    """Degrees between two bearings read as undirected lines (0-90): a board faces its way when its long axis is PARALLEL
    to the way's bearing, the face normal to it."""
    return abs((a - b + 90.0) % 180.0 - 90.0)


class WayFacing:
    """Every way segment the board is turned by (`street_runs`, the reading `nearest_way_bearing` uses), filed once per
    siting so each candidate asks only its neighborhood (constitution X clause 15): `turn` is `nearest_way_bearing`'s
    answer, the same distance and the same first-in-order tie-break, with the refusal L12 needs."""

    def __init__(self, M: Any, pad: float) -> None:
        self.pad = pad
        self.segs: list[tuple[Any, Any, int]] = []
        for pts in street_runs(M):
            for k in range(len(pts) - 1):
                self.segs.append((pts[k], pts[k + 1], len(self.segs)))
        self.grid = PointGrid()
        self.grid.extend((a, b, n, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b, n in self.segs)

    def _near(self, x: float, y: float) -> list[tuple[float, int, float]]:
        """(distance, manifest order, bearing) of every segment within `FACING_TIE_PX` of the nearest - from the grid when
        the nearest stands inside its pad (a segment within `d` of a point has its box within `d`, so none is missed), else
        from every segment."""
        found = {n: (a, b) for a, b, n, *_box in self.grid.near(x, y, self.pad + FACING_TIE_PX)}
        near = [(seg_dist(x, y, a, b), n, a, b) for n, (a, b) in found.items()]
        if not near or min(d for d, *_ in near) > self.pad:
            near = [(seg_dist(x, y, a, b), n, a, b) for a, b, n in self.segs]
        if not near:
            return []
        least = min(d for d, *_ in near)
        return sorted((d, n, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))) for d, n, a, b in near if d <= least + FACING_TIE_PX)

    def turn(self, x: float, y: float, fallback: float) -> float | None:
        """THE ONE PREDICATE of `kosatsuba_faces_the_road` (labels L12): the bearing a board seated at (x, y) is turned to -
        its nearest way's (`nearest_way_bearing`: the least distance, a tie to the first in manifest order) - or None where
        that turned board cannot face its way: some other way stands as near (within `FACING_TIE_PX`, the corner of a lane)
        more than `FACING_DEG` off parallel to it, so which way it "faces" is decided by rounding. `fallback` where the map
        drew no way."""
        near = self._near(x, y)
        if not near:
            return fallback
        bearing = near[0][2]  # sorted by (distance, manifest order): `nearest_way_bearing`'s strict-less scan
        return bearing if all(off_parallel(b, bearing) <= FACING_DEG for _d, _n, b in near) else None


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
    dwellings a seat's traffic counts, the `kosatsuba_siting` knob and the wells it reads, the crowns, and the ways the
    board is turned by (`WayFacing`)."""

    view: Any
    beds: Any
    spots: list[tuple[float, float]]
    siting: str
    wells: list[tuple[float, float]]
    canopy: Any
    facing: WayFacing


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
    the association term holds it nearer its board than any neighbor - else None.

    THE ASSOCIATION IS PROVED AGAIN ON THE RECORD (labels L6, `stands_nearest`): the search's term measures the exact
    seat, and the map is judged on the manifest, which rounds the caption's box and the board's center and turn to 0.1.
    At the preferred offset a neighbor a hair farther than the board is a tie that rounding can break the other way
    (Kuwabata: a threshing yard 4.008 ft from the recorded caption, its board 4.056 ft), so a seat is accepted only where
    the caption as recorded stands nearer the board as recorded than anything the index holds - the predicate the pool
    test asks of the manifest."""
    nb = nearest_way_bearing(M, x, y)
    turn = nb if nb is not None else rot
    board = recorded_board(x, y, 2 * hw, 2 * hh, turn)

    def nearest(p: Placement) -> bool:
        return stands_nearest(recorded_caption_quad(label, p.lines, p.x, p.y, BOARD_CAPTION_SIZE, p.angle), board, index)

    return place(label, BOARD_CAPTION_SIZE, board_subject(x, y, turn, 2 * hw, 2 * hh), index, frame, strict=True, max_ring=0, accept=nearest)


def recorded_board(x: float, y: float, vw: float, vh: float, rot: float) -> list[tuple[float, float]]:
    """The drawn footprint of a board seated at (x, y) turned `rot`, AS ITS RECORD GIVES IT (`board_record`: the center,
    the marker box and the turn each rounded to 0.1) - what a check of the finished map measures the caption against."""
    return rect(round(x, 1), round(y, 1), round(vw, 1) / 2, round(vh, 1) / 2, round(rot, 1))


def board_at(M: Any, x: float, y: float, hw: float, hh: float, rot: float) -> Any:
    """The caption subject of a board seated at (x, y), turned to its nearest way (`rot` where the map drew none)."""
    nb = nearest_way_bearing(M, x, y)
    return board_subject(x, y, nb if nb is not None else rot, 2 * hw, 2 * hh)


def terminal_caption(M: Any, x: float, y: float, hw: float, hh: float, rot: float, label: str, index: ObstacleIndex, frame: Any) -> Placement | None:
    """THE SECOND STEP of the board's caption (feature 287: `captions_clear_the_ways_they_stand_on`, D10; plan D12): the
    seat the one placer gives the caption of a board seated here when no seat is free beside it - on a leader, or in the
    sheet's key with its numbered mark on the board, never overlapping (D10) - and only where that caption, and the key
    mark it would take, clear every way `index` holds; else None, and the siter goes on to `fallback_caption`.

    THE MARK IS ASKED FIRST, and it is what refuses a verge seat: a mark is set on the board, and a board posted at the
    verge's edge puts it on the tread. Asked before the search (it is the keyed seat's own geometry, `keyed`), it
    refuses such a seat without the full search that would find out whether the caption ends in the key; a seat whose
    mark clears keeps a caption that clears whatever the search decides, since every other seat the search can return
    covers no hard ink, and a way is hard. The drawn caption is asked again, so the predicate holds of what is drawn."""
    subject = board_at(M, x, y, hw, hh, rot)
    if not caption_clears_ways(keyed(label, BOARD_CAPTION_SIZE, subject, None, 0.0).block, index.ways):
        return None
    p = place(label, BOARD_CAPTION_SIZE, subject, index, frame)
    return p if caption_clears_ways(p.block, index.ways) else None


def fallback_caption(M: Any, x: float, y: float, hw: float, hh: float, rot: float, label: str, index: ObstacleIndex, frame: Any) -> Placement:
    """THE LAST STEP of the board's caption (plan D12, GM 2026-09-30: a caption that does not sit clean is allowed): the
    seat the one placer's normal fallback gives the caption of a board seated here - the best free seat it finds, a
    leader, or the key with its mark wherever it lands on the board, as for any caption. Never None, so a board with a
    roadside seat is never dropped over its caption."""
    return place(label, BOARD_CAPTION_SIZE, board_at(M, x, y, hw, hh, rot), index, frame)


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
    (feature 284): the caption's proof is a placement against every obstacle, so the walk stops at the first open fit.

    THE OPEN SEATS ARE PROVED BEFORE ANY SHADED ONE (feature 287, the board's 216 s siting): the walk in one pass proved
    every shaded seat on its way to an open fit, and a board under one wide canopy - every seat shaded - proved all 1,072
    of them where the first that fits was the answer. Walking the open seats in score order and then the shaded ones in
    score order asks the same question of each and returns the same seat."""
    ranked = sorted(seats, key=lambda c: c.score, reverse=True)
    for group in ([c for c in ranked if not c.shaded], [c for c in ranked if c.shaded]):
        for c in group:
            ok, p = proof(c)
            if ok:
                return c, p
    return None


BoardFor = Callable[[str, Proof, bool], "tuple[BoardSeat, Placement | None] | None"]
"""The siter's seat for one placement under one caption proof, `widen` admitting the web lanes (`_board_for`)."""


def site_board(values: Sequence[str], proofs: Sequence[Proof], want: Any, board_for: BoardFor, lane_tier: bool) -> dict[str, tuple[BoardSeat, Placement | None]]:
    """Every placement in `values` the map can site, with its seat and caption - each asked of the caption `proofs` in
    order, the cleaner first (plan D12, GM 2026-09-30: the clean caption is a preference). A later proof is asked only
    where the earlier ones sited nothing - of every placement - or of the pinned placement `want` where they did not site
    it, so a map where some placement takes a clean caption resolves the knob over exactly those, and a pinned placement
    is never refused over its caption. Each proof tries the siting band, then (lane tiers) the band with the web lanes."""
    chosen: dict[str, tuple[BoardSeat, Placement | None]] = {}
    for pf in proofs:
        todo = [v for v in values if v not in chosen and (not chosen or v == want)]  # judged once per proof, before it sites any
        for v in todo:
            got = board_for(v, pf, False)
            if got is None and lane_tier:
                got = board_for(v, pf, True)
            if got is not None:
                chosen[v] = got
    return chosen


def resolve_seat(seed: int, context: dict[str, Any], pinned: dict[str, Any], sitable: set[str]) -> str:
    """The `kosatsuba_seat` knob resolved over the placements this map can SITE (feature 287, labels L1: the knob's value
    space is constrained, the affordance mechanism it already uses for an approach or an official's house). The roll is the
    knob's own (`Knob.roll`: the same per-knob draw) over its typing-filtered values that are sitable, so a map that can site
    every placement rolls exactly as before. A PINNED placement the map cannot site is refused, naming it - declared input
    the site cannot honor (plan D7's kind), never a board drawn against its rules. Its caption is not a reason (plan D12,
    GM 2026-09-30): the siter offers a pinned placement every caption step, so `sitable` lacks it only where no seat
    there takes a board at all."""
    knob = KNOBS["kosatsuba_seat"]
    want = pinned.get("kosatsuba_seat")
    if want is not None:
        if want in knob.value_space and knob.typing_rule(want, context) and want not in sitable:
            raise ValueError(f"knob 'kosatsuba_seat': pinned {want!r}, but no verge in the view takes a board there")
        return str(resolve_knob("kosatsuba_seat", seed, context, pinned))
    return str(Knob("kosatsuba_seat", [v for v in knob.value_space if v in sitable], knob.default, knob.typing_rule).roll(seed, context))
