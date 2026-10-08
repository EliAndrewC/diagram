"""Every crossing square: the lanes squared where they cross the brook and the drawn channels - the settle's step 1
(`square_every_crossing`) and the same squaring of one run (`square_run`), which the seating asks of a corridor.

Lifted out of `settle.py` at the 1,000-line bar (feature 316, when the research claims were carried over feature 315's merge);
`settle` re-exports every name here, which callers and the tests name as `settle.<name>`. A leaf: nothing here reads a name
the tests monkeypatch on `settle`.

Research: squaring plumbing - NONE: each rule is claimed at its function or constant
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from ..consts import Poly
from . import law
from .checks import square_crossings
from .clearance import _ZIGZAG_RUN_FT, kink_spans


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in (ln.get("pts") or [])]


SQUARE_PASSES = 4
"""How many times one lane is squared against one water in a round - squaring is idempotent after the first, so this is
the bound for a lane crossing the same course several times."""


SQUARE_MARGIN_FT = 6.0
"""The square leg's reach past the water's half-width (`stage_crossings`' own figure, moved here with the squaring).

Research: the square leg - UNRESEARCHED: 6 ft past the water's half-width"""


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
    """(course, half-width plus the leg's margin) for the brook and every drawn channel - what `stage_crossings` squared."""
    margin = SQUARE_MARGIN_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = [([(float(x), float(y)) for x, y in f["poly"]], float(f.get("w", 8.0)) / 2 + margin) for f in M.get("streams") or [] if len(f.get("poly") or ()) >= 2]
    waters += [([(float(x), float(y)) for x, y in c["pts"]], float(c.get("w0", 4.0)) / 2 + margin) for c in M.get("drawn_channels") or [] if len(c.get("pts") or ()) >= 2]
    return waters


def square_every_crossing(s: Any) -> int:
    """Square every lane at every crossing of the brook and the drawn channels (`square_crossings`), the connector's too.
    Returns the lanes changed.

    Research:
        square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the track out too
        square ditch crossing - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the drawn channels
        a moved end keeps its joint - NONE: another lane ending there is moved with it"""
    waters = square_waters(s.M)
    lanes = s.M.get("lanes") or []
    changed = 0
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2:
            continue
        q = p
        for course, half in waters:
            q = squared_against(q, course, half)
        if q != p and s.reshape_lane(ln, q):
            s.reink_lane(i)
            changed += 1
            # AN END THE SQUARING MOVED CARRIES ITS JOINT WITH IT: another lane that ended at the same point still ends
            # where this one does, so the two stay one way (Mizuguchi: the field path and the lane it continued met at the
            # brook's bank, and squaring the path's crossing left the lane 10 ft short of it)
            for old, new in ((p[0], q[0]), (p[-1], q[-1])):
                if math.dist(old, new) < 1e-6:
                    continue
                for j, other in enumerate(lanes):
                    op = other.get("pts") or []
                    for e in (0, -1):
                        if j != i and len(op) >= 2 and math.dist((float(op[e][0]), float(op[e][1])), old) <= 1.0:
                            moved = [list(q) for q in op]
                            moved[e] = [round(new[0], 1), round(new[1], 1)]
                            if s.reshape_lane(other, moved):
                                s.reink_lane(j)
    return changed


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
