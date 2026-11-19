"""What the audit's Python reads of the compound engine: its three distances, its palette and its three predicates with the box gap they
measure by (feature 449 T152: moved here from `compound_model.py` and `compound_parts.py` when the Python compound engine was deleted - the
generator is `rust/mode_a/src/compound/`, and the audit's Rust holds the same figures in `rust/mode_a/src/compound.rs`, which the
lockstep `rust/mode_a/src/parse/lockstep_checks.rs` holds equal to these).

Research: the engine's audit rules - NONE: the distances and predicates held as the audit reads them, deciding nothing here that the claims on each do not
"""

from __future__ import annotations

import math
from collections.abc import Sequence

#: A box in feet: (x0, y0, x1, y1).
Box = tuple[float, float, float, float]

TUB_MAX_GAP_FT: float = 3.5
"""How far from its building a fire-water tub may stand (feature 287, homes H29b): the number `pack_audit`'s
`fire_water_adrift` registers - a gutter-fed tub hugs its eaves - held equal to it by a test.

Research: fire-water tub reach from its building - GUESS: a gutter-fed tub stands within 3.5 ft of its building's eaves; 0100 puts tubs beside a building's door and is silent on the distance."""

TUB_DOOR_MAX_FT: float = 10.5
"""How far a fire-water tub's center may stand from a door of the building it serves (feature 372 wave 106): research 0100
keeps standing water at a wooden building's ENTRANCE, so a tub stands beside a door. The kitchen's two tubs side by side
at one 6 ft door set the figure: along the face, the door's half-width and the foot its approach keeps (4 ft), the
draft's 1 ft clearance, the near tub (2.6 ft), another foot and the far tub's half (1.3 ft) - 9.9 ft - at 2.5 ft out, ~10.2
ft; a short face's tub round the corner nearest its door stands ~8.6 ft off. The 10.5 ft is a CONVENTION of this project;
the number `pack_audit`'s `tubs_off_their_doors` registers, held equal to it by sharing this name.

Research: fire-water tub reach from a door - CONVENTION: a tub's center stands within 10.5 ft of a door of its building, a figure fixed by the kitchen's two tubs beside a 6 ft door; research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html records how near counts as beside the door, within about 10 ft, as a convention of this project."""

NOTICE_BOARD_MAX_FT: float = 40.0
"""How far from the main gate's opening the compound's notice board may stand (feature 287, homes H29b): the number
`pack_audit`'s `notice_board_adrift` registers, held equal to it by a test. 40 ft since feature 372 wave 104 (it was 20,
set while boards stood against the wall): the gate opens straight onto the road it stands on (0088), so its board stands
beside that road on the far verge facing the gate (0190), across as much as the Imperial road's 30 ft.

Research: board by the gate - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: the notice board stands within about 15 ft of a gate in the wall - it is allowed 40 ft, a departure the code keeps until feature 417 T33; within 40 ft of the opening, this project's figure, so a board beside the road (0190) can face its gate across the Imperial road's 30 ft (0088)"""

# palette keys -> (fill, stroke) reused from the Mode A vocabulary (SKILL.md)
KINDS: dict[str, tuple[str, str]] = {
    "lord": ("#DDB87A", "#5A3F1E"),
    "service": ("#C9A57A", "#6B4F2A"),
    "plain": ("#E8D2A8", "#6B4F2A"),
    "kura": ("#F2EFE4", "#4A3318"),
    # 0098's raised timber storehouse (takakura): slatted walls on posts, the hand sheets' form (feature 374 wave 128)
    "takakura": ("url(#granary-slats)", "#5A3F1E"),
    "shrine": ("#C9876C", "#6B2A18"),
    "cell": ("#B89868", "#5C4318"),
    "dark": ("#8C6F3E", "#4A3318"),
}
"""Research: the palette's fills - CONVENTION: each palette role's fill and stroke, the slatted granary's pattern among them, is how a sheet shows a building's kind, not its real color."""


def _gap(a: Box, b: Box) -> float:
    """The clear distance between two boxes (0 where they touch or overlap)."""
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5


def tub_by_its_eaves(tub: tuple[float, float], host: Box) -> bool:
    """THE ONE PREDICATE of `fire_water_adrift` (feature 287, homes H29b), in feet: a fire-water tub's CENTER stands within
    `TUB_MAX_GAP_FT` of the building whose gutter feeds it. The draft's tub seat asserts it of every seat it offers, and
    the pack audit (`tools/pack_audit/checks.py:fire_water_adrift`) calls it on every tub of every sheet, generated or hand
    drawn - one rule, one measure. (Until wave 4a this measured the drawn circle's EDGE, 1.27 ft looser than the audit's
    center measure, so a seat 3.5-4.8 ft off its eaves passed the placer and failed the audit.)"""
    return _gap((tub[0], tub[1], tub[0], tub[1]), host) <= TUB_MAX_GAP_FT


def tub_by_its_door(tub: tuple[float, float], doors: Sequence[tuple[float, float]]) -> bool:
    """THE ONE PREDICATE of `tubs_off_their_doors` (feature 372 wave 106), in feet: a fire-water tub's CENTER stands within
    `TUB_DOOR_MAX_FT` of the center of one of its building's doors - research 0100's water kept at the entrance."""
    return any(math.hypot(tub[0] - dx, tub[1] - dy) <= TUB_DOOR_MAX_FT for dx, dy in doors)


def board_by_a_gate(board: Box, openings: Sequence[tuple[float, float]]) -> bool:
    """THE ONE PREDICATE of `notice_board_adrift` (feature 287, homes H29b), in feet: a notice board is read where people
    pass, so the nearest edge of its box stands within `NOTICE_BOARD_MAX_FT` of the middle of a gate opening. The pack
    audit calls it with every opening it reads off a sheet's ink; the draft (`board_by_the_gate`) with its main gate."""
    return any(_gap((ox, oy, ox, oy), board) <= NOTICE_BOARD_MAX_FT for ox, oy in openings)
