"""THE BROOK (feature 230) - the stream that is tapped at an intake and runs on past the fan, and what stands at the tap.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory. The course's leaf helpers moved to `brook_course.py` (feature 316), re-exported here.

Research: plumbing - NONE: geometry, tolerances and the repair's bounds; every unit that decides something carries its own claims
"""

from __future__ import annotations

from collections.abc import Sequence

from l7r.diagram.settlement._knobs import Knob, register_knob

from ..consts import (
    BROOK_MAX_TURN_DEG,
    WEIR_THICK_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .brook_course import (  # noqa: F401 - re-exported where callers and tests import them
    FILLET_MIN_TURN_DEG,
    JOIN_ON_COURSE,
    course_corner,
    drawn_course,
    finished_course,
    join_vertices,
    round_the_brooks,
)
from .brook_rules import (
    axis_segments,
    course_enters,
    crosses_mid_run,
    ends_off_canvas,
    level_runs_any_view,
    max_turn_deg,
    monotone_down,
    reserved_box,
    ruled_excess,
    tap_index,
    without_straight_joins,
)

# THE WEIR'S FORM (269 B22; research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html): a fence of stakes woven with brushwood (feature 280 M36: the woven stake
# fence is in the Man'yoshu, the reed weave only in a present-day weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html), a frame of stakes and logs packed
# with clay, a crib of timber packed with stone, or a course of stone-filled baskets, each drawn at its own thickness
# (`WEIR_THICK_FT`). "The rule the map follows: a weir hamlet's weir takes one of four forms, rolled per settlement
# with an even chance" - the EVEN chance a GUESS, no source counting them. `crib` is the default because it is the
# one form the glyph drew before the knob. Declared as `meta.weir_form` on a weir hamlet only.
WEIR_FORM = register_knob(Knob("weir_form", list(WEIR_THICK_FT), default="crib"))
"""Research: weir form - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: fence, frame, crib or gabion rolled per weir hamlet with even odds, crib the default"""


def brook_violations(course: Sequence[Pt], plan: SitePlan, sluice: Pt, ditches: Sequence[Poly] = (), joins: Sequence[Pt] = ()) -> list[str]:
    """Which of the brook's rules the DRAWN course (`drawn_course` of `course`, its tap and any confluence `joins` held)
    breaks - empty for a course the placer may take. One predicate per rule: W01 `max_turn_deg`, W02 `level_runs_along_frame` over the whole canvas, W03
    `ruled_excess`, W04 `axis_segments`, W06 `course_enters`, W07 `ends_off_canvas` (the off-map source and the mouth), W08
    `crosses_mid_run`, W11 `monotone_down` below the tap.

    Research:
        no fold-back - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25) - 0054 gives a bend radius of two to three widths and no turn cap or loop rule; no vertex turns past BROOK_MAX_TURN_DEG (100 deg), a natural brook does not double back
        no level run - CONVENTION: no run held level along the frame, in any view
        no ruled run - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: a natural stream rarely runs straight more than about ten times its own width - the straightest run on the canvas within RULED_MAX_FT, ten drawn widths (`ruled_excess`)
        no screen axis - CONVENTION: no segment along a screen axis, the tap run excepted
        out of the field - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the course never enters the field's envelope
        off-map ends - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the source and the mouth both off the canvas
        no crossing - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the course crosses no ditch mid-run
        runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: below the tap every step runs down the fall or level, none climbing (strictly under 90)
    """
    fin = drawn_course(course, [sluice], joins)
    W, H = float(plan.W), float(plan.H)
    box = reserved_box(course, plan)
    run, bound, _a, _b = ruled_excess(without_straight_joins(fin, joins, JOIN_ON_COURSE), W, H, box)
    checks = {
        "fold": max_turn_deg(fin) > BROOK_MAX_TURN_DEG,
        "level": bool(level_runs_any_view(fin, W, H, box)),
        "ruled": run > bound,
        "axis": bool(axis_segments(fin, [sluice])),
        "enters": course_enters(fin, [plan.envelope]),
        "source": not ends_off_canvas(fin, W, H, ends=(0,)),
        "mouth": not ends_off_canvas(fin, W, H, ends=(-1,)),  # the brook runs on past the fan and leaves the map (feature 230)
        "crosses": any(crosses_mid_run(fin, d) for d in ditches),
        "climbs": not monotone_down(fin[tap_index(fin, [sluice]) :], plan.fall),
    }
    return [k for k, bad in checks.items() if bad]
