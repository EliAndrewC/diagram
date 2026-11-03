"""THE BROOK'S RULES, one predicate each (feature 287, M1, water:W01-W11) - lifted out of the pool and gate tests, read by the
brook's placer (`brook.py`, `feed_brook`) and by the tests alike, so a rule a
placer decides and the rule a test asserts are one function. Split from `brook.py` when the placer's repair took that
file past the 1,000-line bar (constitution X clause 13). See `CLAUDE.md` in this directory.

Research: course measurement - NONE: turns, chords, distances and view bounds read off the drawn course; each rule is claimed on its own unit
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from ..consts import BROOK_FRAME_MARGIN, BROOK_SKIRT, Pt


def turn_deg(p: Pt, q: Pt, r: Pt) -> float:
    """How far the course p -> q -> r turns at `q`, degrees (0 straight on, 180 straight back); 0 where a leg has no
    length, since a vertex on top of its neighbor turns nothing. The one reading of a turn: `max_turn_deg`, `unfold` and
    the pool test all ask it (feature 287, water:W01)."""
    ax, ay, bx, by = q[0] - p[0], q[1] - p[1], r[0] - q[0], r[1] - q[1]
    na, nb = math.hypot(ax, ay), math.hypot(bx, by)
    return math.degrees(math.acos(max(-1.0, min(1.0, (ax * bx + ay * by) / (na * nb))))) if na and nb else 0.0


# ---- THE BROOK'S RULES, one predicate each (feature 287, M1): the placer below judges its candidate with these, and the
# pool tests read the same functions. Every one is measured on the DRAWN course, `finished_course`.

LEVEL_TOL_FT = 4.0  # ... that holds one coordinate within this ...
"""Research: level run tolerance - CONVENTION: a coordinate held within 4 ft"""
RULED_TOL_FT = 3.1  # water:W03 - a straight run: every vertex within this of its chord ...
"""Research: straight run tolerance - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); every vertex within 3.1 ft of its chord"""
# THE MARSH'S VISIBLE EDGE keeps the brook's old straight-run bar (feature 294 B2: `settlement/land/outline.py`, `tools/marsh_edges.py`):
# a straight run of at most 0.4 of the edge in view once 300 ft is in view. The brook itself is held to `RULED_MAX_FT` since
# feature 444 T16 (its claims round, against 0054's ten widths), so these two bind only the marsh.
RULED_SHARE = 0.4  # ... may cover at most this share of a marsh edge's length on the page ...
"""Research: straight run share - GUESS: the record silent on how straight a drawn marsh edge may run; at most 0.4 of the edge's length in view, the bar the brook kept until feature 444 T16"""
RULED_MIN_LEN_FT = 300.0  # ... once that length is at least this (settlement-review of Sawada, round 0ae309f0)
"""Research: straight run floor - GUESS: the record silent on how straight a drawn marsh edge may run; the share applies from 300 ft of edge in view"""
AXIS_EPS_DEG = 1.6  # water:W04 - a segment of a wander stride or more this near a screen axis is a ruled line
"""Research: screen-axis segment - CONVENTION: a segment within 1.6 deg of a screen axis reads as ruled"""
BROOK_DRAWN_W = 5.25  # the width the field stage draws a hamlet's brook at (`field_stage.BROOK_W` is this)
"""Research: brook width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a village creek at roughly three and a half times the 1.5 ft floor, 5.25 ft, narrower than the 6.0 ft head race it feeds"""
# THE ROOM A LEVEL-RUN BEND NEEDS (water:W02): a station held against the frame box still has the skirt's floor 10 px
# inside it, so a bend of the level tolerance plus a foot either way fits between the two. Asserted at import: a consts
# change that took the room away fails here, not on a map.
assert BROOK_FRAME_MARGIN - BROOK_SKIRT >= 2 * (LEVEL_TOL_FT + 1.0), "the frame box leaves the brook no room to bend off a level run"


def _clip_arcs(arcs: list[tuple[float, float]], c: float, half: float) -> list[tuple[float, float]]:
    """`arcs` (bearing intervals, radians, a line's bearing taken mod pi) cut to within `half` of `c` mod pi."""
    out = []
    for lo, hi in arcs:
        for k in (-2, -1, 0, 1, 2):
            a, b = max(lo, c + k * math.pi - half), min(hi, c + k * math.pi + half)
            if a <= b:
                out.append((a, b))
    return out


def straightest_run(pts: Sequence[Pt], tol: float) -> float:
    """The longest chord between two vertices of `pts` (at least one vertex apart) with every vertex between within `tol`
    of its line - the pool test's `_straightest`, lifted (water:W03) and made quadratic: from each start, the bearings a
    chord may take narrow with every vertex passed (a vertex `r` out allows those within asin(tol / r) of its own), and
    once none is left no longer chord from that start can qualify.
    Research: straight run - NONE: the longest chord within a tolerance, geometry that decides nothing itself (the decision is RULED_TOL_FT's and RULED_MAX_FT's); the W03 chord a natural brook is held off
    """
    return straightest_chord(pts, tol)[0]


def straightest_chord(pts: Sequence[Pt], tol: float) -> tuple[float, int, int]:
    """`straightest_run` with the chord's two vertex indices - what the placer's repair bends at the middle of.

    Research: straight run - NONE: the longest chord within a tolerance, geometry that decides nothing itself (the decision is RULED_TOL_FT's and RULED_MAX_FT's); the W03 chord a natural brook is held off
    """
    best, at = 0.0, (0, 0)
    for i, (ax, ay) in enumerate(pts):
        arcs: list[tuple[float, float]] | None = None  # None: every bearing is still open
        for j in range(i + 1, len(pts)):
            qx, qy = pts[j][0] - ax, pts[j][1] - ay
            r = math.hypot(qx, qy)
            phi = math.atan2(qy, qx)
            if j >= i + 2 and r > best and (arcs is None or any(lo <= phi + k * math.pi <= hi for lo, hi in arcs for k in (-2, -1, 0, 1, 2))):
                best, at = r, (i, j)
            if r > tol:
                arcs = _clip_arcs(arcs if arcs is not None else [(phi - math.pi / 2, phi + math.pi / 2)], phi, math.asin(tol / r))
                if not arcs:
                    break
    return best, at[0], at[1]


# THE BROOK'S VIEW'S TWO HELPERS, moved unchanged from settlement/fields/comb.py with the comb's old placement deleted (feature
# 444 T16, the round arbiter's ruling on ask:444-T16-brook-predicates): `reserved_box` is their one live caller.
