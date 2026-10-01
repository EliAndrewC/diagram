"""TWO WATERCOURSES DO NOT RUN SIDE BY SIDE (feature 294 B4, the review's "parallel twin watercourses" class).

The reviews found twin watercourses four times (2026-08-26 T11, features 145 and 230): two ditches running parallel 12-32 ft
apart for a long stretch. On the comb it is a delivery taking off from the second supply canal and running down beside it -
190 to 310 ft on four of the five hamlets when this was written. The research pass for this feature (specs/294 research R4)
found no premodern source giving a comb's branch spacing: the spacing figures are all modern design standards, set by the
strip of plots a branch serves, tens to hundreds of meters; a supply and a drain ditch paired side by side across every plot is
modern (the Meiji Ishikawa method, postwar field consolidation), and the Edo-period plot was fed paddy to paddy (tagoshi) or
from a side ditch it fronts. So a delivery that would run as such a twin is not drawn - its plots keep their bunds and take
their water over them, as the comb already does where a delivery would sprout at the head fork.

ONE PREDICATE (`twin_run_ft`), asked by the comb as it draws (`comb._comb_canal_pieces`) and by the gate over the shipped
maps (`tests/gate/test_review_rules_294.py`). The band and the run are GUESSES (no source gives one): the band is the
reviewer's recorded observation, the run one sixth of the shortest comb branch."""

from __future__ import annotations

import math
from collections.abc import Sequence

from shapely.geometry import LineString, Point

TWIN_LO_FT = 12.0  # nearer than this the two are one course or a junction, not twins (the recorded band's floor)
TWIN_HI_FT = 32.0  # the recorded band's ceiling
TWIN_DEG = 15.0  # running the same way
TWIN_RUN_FT = 60.0  # longer than this side by side is a twin
TWIN_JOIN_FT = 60.0  # the reach from where one course leaves the other, where running close is the junction itself
_STEP_FT = 5.0


def _bearing(line: LineString, s: float) -> float:
    a = line.interpolate(max(0.0, s - 1.0))
    b = line.interpolate(min(line.length, s + 1.0))
    return math.atan2(b.y - a.y, b.x - a.x)


def twin_run_ft(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], ftpx: float) -> float:
    """The longest stretch, in feet, along which course `a` runs beside course `b`: within `TWIN_LO_FT`-`TWIN_HI_FT` of it,
    within `TWIN_DEG` of its bearing, and more than `TWIN_JOIN_FT` from an end of `a` that stands on `b` (where `a` leaves or
    joins it). Sampled every five feet along `a`."""
    la, lb = LineString(a), LineString(b)
    if la.length == 0 or lb.length == 0:
        return 0.0
    on_b = [lb.distance(Point(p)) * ftpx < TWIN_LO_FT for p in (a[0], a[-1])]
    step = _STEP_FT / ftpx
    best = run = 0
    n = int(la.length // step) + 1
    for k in range(n):
        s = min(k * step, la.length)
        p = la.interpolate(s)
        d = lb.distance(p) * ftpx
        near_join = (on_b[0] and s * ftpx < TWIN_JOIN_FT) or (on_b[1] and (la.length - s) * ftpx < TWIN_JOIN_FT)
        turn = abs((_bearing(la, s) - _bearing(lb, lb.project(p)) + math.pi / 2) % math.pi - math.pi / 2)
        if TWIN_LO_FT <= d <= TWIN_HI_FT and math.degrees(turn) <= TWIN_DEG and not near_join:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best * _STEP_FT


def twins(courses: Sequence[Sequence[Sequence[float]]], ftpx: float) -> list[tuple[int, int, float]]:
    """(i, j, ft) for every pair of courses that run side by side longer than `TWIN_RUN_FT`, either way round."""
    out = []
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            run = max(twin_run_ft(courses[i], courses[j], ftpx), twin_run_ft(courses[j], courses[i], ftpx))
            if run > TWIN_RUN_FT:
                out.append((i, j, run))
    return out


def leaves_from(child: Sequence[Sequence[float]], parent: Sequence[Sequence[float]], ftpx: float) -> bool:
    """Does `child` take off from `parent` - its first point standing on it?"""
    return LineString(parent).distance(Point(child[0])) * ftpx < TWIN_LO_FT


def drop_twin_deliveries(channels: list[dict], first: int, ftpx: float) -> list[dict]:
    """Take out of `channels[first:]` every delivery (`role` branch) that would run beside another course as a twin: the one
    that leaves the other, else the shorter of two deliveries. A supply canal (`role` main) is never taken out. Returns the
    deliveries taken out."""
    mine = list(range(first, len(channels)))
    gone: set[int] = set()
    for i, j, _run in twins([channels[k]["pts"] for k in mine], ftpx):
        a, b = mine[i], mine[j]
        if a in gone or b in gone:
            continue
        ca, cb = channels[a], channels[b]
        if cb.get("role") == "branch" and (ca.get("role") != "branch" or leaves_from(cb["pts"], ca["pts"], ftpx)):
            gone.add(b)
        elif ca.get("role") == "branch" and (cb.get("role") != "branch" or leaves_from(ca["pts"], cb["pts"], ftpx)):
            gone.add(a)
        elif ca.get("role") == "branch" and cb.get("role") == "branch":
            gone.add(a if LineString(ca["pts"]).length < LineString(cb["pts"]).length else b)
    out = [channels[k] for k in sorted(gone)]
    for k in sorted(gone, reverse=True):
        del channels[k]
    return out
