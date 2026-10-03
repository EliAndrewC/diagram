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
reviewer's recorded observation, the run one sixth of the shortest comb branch.

Research: twin geometry - NONE: polyline sampling, nearest-leg distances and box prefilters
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

TWIN_LO_FT = 12.0  # nearer than this the two are one course or a junction, not twins (the recorded band's floor)
"""Research: twin band floor - GUESS: 12 ft, the floor of the spacing the reviews measured between side-by-side pairs"""
TWIN_HI_FT = 32.0  # the recorded band's ceiling
"""Research: twin band ceiling - GUESS: 32 ft, the ceiling of the spacing the reviews measured"""
TWIN_DEG = 15.0  # running the same way
"""Research: running the same way - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: within 15 deg of the other's bearing"""
TWIN_RUN_FT = 60.0  # longer than this side by side is a twin
"""Research: twin run - GUESS: more than 60 ft side by side, a sixth of the shortest delivery"""
TWIN_JOIN_FT = 60.0  # the reach from where one course leaves the other, where running close is the junction itself
"""Research: junction reach - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: running close within 60 ft of where one course leaves the other is the junction"""
_STEP_FT = 5.0


def _samples(a: Any, step: float) -> tuple[Any, Any, float]:
    """(points every `step` along polyline `a`, the unit direction of the leg each lies on, `a`'s length) - numpy arrays."""
    import numpy as np

    legs = np.diff(a, axis=0)
    lens = np.hypot(legs[:, 0], legs[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(lens)])
    total = float(cum[-1])
    s = np.minimum(np.arange(int(total // step) + 1) * step, total)
    k = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(legs) - 1)
    k = np.where(lens[k] == 0, np.argmax(lens > 0), k)
    f = (s - cum[k]) / np.where(lens[k] == 0, 1.0, lens[k])
    pts = a[k] + legs[k] * f[:, None]
    return pts, legs[k] / lens[k][:, None], total


def _nearest(pts: Any, b: Any) -> tuple[Any, Any]:
    """(each point's distance to polyline `b`, the unit direction of the leg of `b` nearest it) - numpy arrays."""
    import numpy as np

    a0, legs = b[:-1], np.diff(b, axis=0)
    l2 = (legs**2).sum(axis=1)
    keep = l2 > 0
    a0, legs, l2 = a0[keep], legs[keep], l2[keep]
    rel = pts[:, None, :] - a0[None, :, :]
    t = np.clip((rel * legs[None, :, :]).sum(axis=2) / l2[None, :], 0.0, 1.0)
    d = np.hypot(*(rel - t[:, :, None] * legs[None, :, :]).transpose(2, 0, 1))
    k = d.argmin(axis=1)
    return d[np.arange(len(pts)), k], legs[k] / np.sqrt(l2[k])[:, None]


def twin_run_ft(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], ftpx: float) -> float:
    """The longest stretch, in feet, along which course `a` runs beside course `b`: within `TWIN_LO_FT`-`TWIN_HI_FT` of it,
    within `TWIN_DEG` of its bearing, and more than `TWIN_JOIN_FT` from an end of `a` that stands on `b` (where `a` leaves or
    joins it). Sampled every five feet along `a`; the bearing at a sample is the leg's it lies on.

    IN NUMPY, NOT SHAPELY (feature 294's own perf bookend): a shapely `interpolate`/`project`/`distance` per five-foot sample
    made this 7.6 s of seed 25's 10.9 s field stage (cProfile, 2026-10-01) - every pair of a comb's courses, both ways round.

    Research: twin run measure - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: the longest stretch within the band, the same way, past the junction reach
    """
    import numpy as np

    pa, pb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if len(pa) < 2 or len(pb) < 2 or not np.hypot(*np.diff(pa, axis=0).T).sum() or not np.hypot(*np.diff(pb, axis=0).T).sum():
        return 0.0
    ends, _ = _nearest(pa[[0, -1]], pb)
    on_b = ends * ftpx < TWIN_LO_FT
    pts, dir_a, total = _samples(pa, _STEP_FT / ftpx)
    s = np.minimum(np.arange(len(pts)) * (_STEP_FT / ftpx), total)
    d, dir_b = _nearest(pts, pb)
    d = d * ftpx
    near_join = (on_b[0] & (s * ftpx < TWIN_JOIN_FT)) | (on_b[1] & ((total - s) * ftpx < TWIN_JOIN_FT))
    turn = np.degrees(np.arccos(np.clip(np.abs((dir_a * dir_b).sum(axis=1)), 0.0, 1.0)))
    ok = (d >= TWIN_LO_FT) & (d <= TWIN_HI_FT) & (turn <= TWIN_DEG) & ~near_join
    best = run = 0
    for flag in ok.tolist():
        run = run + 1 if flag else 0
        best = max(best, run)
    return best * _STEP_FT


def _apart(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], gap: float) -> bool:
    """Do the two courses' boxes stand more than `gap` apart - too far for either to run beside the other?"""
    xa, ya = [p[0] for p in a], [p[1] for p in a]
    xb, yb = [p[0] for p in b], [p[1] for p in b]
    return min(xa) - max(xb) > gap or min(xb) - max(xa) > gap or min(ya) - max(yb) > gap or min(yb) - max(ya) > gap


def twins(courses: Sequence[Sequence[Sequence[float]]], ftpx: float) -> list[tuple[int, int, float]]:
    """(i, j, ft) for every pair of courses that run side by side longer than `TWIN_RUN_FT`, either way round. A pair whose
    boxes stand further apart than `TWIN_HI_FT` is not measured.

    Research: twin pairs - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: every pair running side by side longer than the twin run
    """
    out = []
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            if len(courses[i]) < 2 or len(courses[j]) < 2 or _apart(courses[i], courses[j], TWIN_HI_FT / ftpx):
                continue
            run = max(twin_run_ft(courses[i], courses[j], ftpx), twin_run_ft(courses[j], courses[i], ftpx))
            if run > TWIN_RUN_FT:
                out.append((i, j, run))
    return out


def leaves_from(child: Sequence[Sequence[float]], parent: Sequence[Sequence[float]], ftpx: float) -> bool:
    """Does `child` take off from `parent` - its first point standing on it?"""
    from shapely.geometry import LineString, Point

    return LineString(parent).distance(Point(child[0])) * ftpx < TWIN_LO_FT


def drop_twin_deliveries(channels: list[dict[str, Any]], first: int, ftpx: float) -> list[dict[str, Any]]:
    """Take out of `channels[first:]` every delivery (`role` branch) that would run beside another course as a twin: the one
    that leaves the other, else the shorter of two deliveries. A supply canal (`role` main) is never taken out. Returns the
    deliveries taken out.

    Research:
        twin delivery dropped - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: the delivery that would run as a twin is not drawn, its plots watered over the bund
        which one goes - UNRESEARCHED: the delivery that leaves the other, else the shorter; a supply canal never
    """
    from shapely.geometry import LineString

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
