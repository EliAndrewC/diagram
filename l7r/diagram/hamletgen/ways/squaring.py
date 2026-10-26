"""Every crossing square: the squaring of one run where it crosses the brook and the drawn channels (`square_run`), which the
seating asks of a corridor. The settle's own squaring step over the finished web went in feature 417 T31, measured needless.

Lifted out of `settle.py` at the 1,000-line bar (feature 316, when the research claims were carried over feature 315's merge);
`settle` re-exports every name here, which callers and the tests name as `settle.<name>`. A leaf: nothing here reads a name
the tests monkeypatch on `settle`.

Research: squaring plumbing - NONE: each rule is claimed at its function or constant
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..consts import Poly, Pt
from . import law
from .checks import square_crossings
from .clearance import _ZIGZAG_RUN_FT, kink_spans
from .geom import polyline_len


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in (ln.get("pts") or [])]


SQUARE_PASSES = 4
"""How many times one lane is squared against one water in a round - squaring is idempotent after the first, so this is
the bound for a lane crossing the same course several times."""


SQUARE_MARGIN_FT = 6.0
"""The square leg's reach past the water's half-width (`stage_crossings`' own figure, moved here with the squaring).

Research: the square leg - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); 6 ft past the water's half-width"""


def squared_against(q: Poly, course: Poly, half: float) -> Poly:
    """`q` squared at its crossings of one water course (`square_crossings`, up to `SQUARE_PASSES` times) - with a square leg
    long enough to read as a bend where the usual one leaves a zigzag.

    AN OBLIQUE APPROACH SQUARED ON A SHORT LEG IS A ZIGZAG (feature 328 wave 46, Kashikawa's road over the brook's ford): the
    leg reached the water's half-width and 6 ft past each bank, 21 ft, and its two turns of 60 and 65 degrees stood inside
    0081's 40 ft - a zigzag the lane law refuses and no repair may cut from the track out. Where the usual leg adds a kink,
    the crossing is squared again on a leg reaching half `_ZIGZAG_RUN_FT` and a foot past it each side, so the turns stand
    more than 40 ft apart: a bend, as 0081 reads one.

    Research:
        square crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
        a square leg long enough to bend - research/questions/0081-village-lanes.drawing.html: two turns of more than 50 degrees within 40 ft of path are a zigzag, so the leg runs past 40 ft where the short one leaves one"""

    def squared(reach: float) -> Poly:
        r = list(q)
        for _ in range(SQUARE_PASSES):
            nr = square_crossings(r, course, reach)
            if nr == r:
                break
            r = nr
        return r

    short = squared(half)
    if short == q or len(kink_spans(short)) <= len(kink_spans(q)):
        return short
    return squared(max(half, _ZIGZAG_RUN_FT / 2.0 + 1.0))


# ---- step 1: every crossing square -------------------------------------------------------------------------------------


def square_waters(M: Mapping[str, Any]) -> list[tuple[Poly, float]]:
    """(course, half-width plus the leg's margin) for the brook and every drawn channel - what `stage_crossings` squared.

    Research:
        its figures against 0035's drawing page - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: 8 (stream width fallback, where the page draws a brook 7 ft wide) - a departure the code keeps until feature 417 T34
        its channel width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 4 (drawn channel width fallback, the far supply canal's rung)
    """
    margin = SQUARE_MARGIN_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = [([(float(x), float(y)) for x, y in f["poly"]], float(f.get("w", 8.0)) / 2 + margin) for f in M.get("streams") or [] if len(f.get("poly") or ()) >= 2]
    waters += [([(float(x), float(y)) for x, y in c["pts"]], float(c.get("w0", 4.0)) / 2 + margin) for c in M.get("drawn_channels") or [] if len(c.get("pts") or ()) >= 2]
    return waters


def square_run(M: Mapping[str, Any], run: Poly) -> Poly:
    """`run` squared at every crossing of the brook and the drawn channels (`square_crossings`), as settle step 1 squares
    every lane - so a tree lane is judged, and drawn, square where it crosses water (cohort seed 8: the exit strip crossed the
    brook at its ford 38 degrees off square, and the corridor was refused for it).

    Research:
        square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        square ditch crossing - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html"""
    q = list(run)
    for course, half in square_waters(M):
        if not law.boxes_meet(q, course, half):  # out of its reach the squaring changes nothing (feature 314)
            continue
        q = squared_against(q, course, half)
    return q


def cut_at_shallow_crossing(lanes: Sequence[Mapping[str, Any]], m: int, o: int, houses: Sequence[Pt]) -> tuple[Poly, int] | None:
    """SIDE BY SIDE BECOMES ONE (feature 385 T01, plan D4): lane `m`, crossing way `o` at under `law.NEEDLE_DEG`, cut at the
    crossing - the run past it beside `o` is the same path doubled, and the end left on `o` meets it as a needle the settle
    then re-aims (`settle.reaimed`). Returns the piece kept and the end cut (-1 its last, 0 its first), or None where `m` may
    not be cut there: a tree lane but a household's way (`corridors.is_tree`), a household's way on its door's side (only its
    foot is ever moved), or a cut that would leave the web otherwise than it was (`joints.keeps_the_web`: a lane end left on
    nothing, the web in more pieces, a farmhouse no longer served). An ordinary lane keeps its longer side.

    Research:
        two paths side by side become one - research/questions/0081-village-lanes.drawing.html: the lane cut where it comes alongside, meeting the other as a T
        a household's way keeps its door - research/questions/0081-village-lanes.drawing.html: "cut at its far end, never at its door"
        which side an ordinary lane keeps - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); its longer side; a household's way is cut only onto the connector or a tree lane"""
    from .corridors import ACCESS_ROLE, is_tree  # bound here: `corridors` sits beside this module's callers
    from .joints import keeps_the_web

    ln, p = lanes[m], _pts(lanes[m])
    hit = next(((n, x) for _i, n, _k, x in law.shallow_crossing_at([ln, lanes[o]])), None)  # ...lane `m` first, so `n` is its segment
    if hit is None or ln.get("connector"):
        return None
    n, x = hit
    door, far = [*p[: n + 1], x], [x, *p[n + 1 :]]
    household = ln.get("role") == ACCESS_ROLE
    if is_tree(ln) and not household:
        return None
    # ...A HOUSEHOLD'S WAY ONLY ONTO A WAY THAT STAYS - the connector or another tree lane: an ordinary lane is a repair's to cut
    # or drop, and a household hung on one is left on nothing when it goes (cohort seed 38, this change's first cohort: a
    # household's way cut onto a lane laid to join orphans, and three households' ways then fouled the fabric). The
    # ordinary lane is the one cut instead.
    if household and not (lanes[o].get("connector") or is_tree(lanes[o])):
        return None
    piece, end = (door, -1) if household or polyline_len(door) >= polyline_len(far) else (far, 0)
    return (piece, end) if keeps_the_web(lanes, {m}, p, piece, houses) else None
