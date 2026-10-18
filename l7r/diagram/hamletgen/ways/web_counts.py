"""THE WEB'S WHOLE-RULE COUNTS, ASKED OF A TRIAL BY WHAT IT CHANGED (feature 387, plan D2b).

A knot's gather (`knots.settle_knots`) is judged by, among other things, whether the trial web holds more breaches than the web
as it stands of each whole-web rule (`knots._WHOLE_RULES`). A gather moves only the lanes it edits - their ends and, by
`teed_onto` and `contracted`, their middles - so of those counts four are re-asked here only where an edit can change them,
from the web's own verdicts kept once per web (rebuilt only once a gather is applied, as `settle_knots`' `had` is):

- `doubled_tails` / `shadows`: a lane counts when it has a partner (`WebMemo.pair`); each lane's partners are kept, and a trial
  asks only the pairs holding an edited lane.
- `doorstep_ends`: the free ends each house discharges (`law.fronting_ends`); each end's junction and house are kept, and a trial
  re-asks the edited lanes' ends and the ends within `JOIN_TOL` of an edited lane's old or new line (a junction can only appear
  or vanish there - `fronting_ends` measures an end to the whole way).
- `needle_loops`: the faces of the treads (`tree_base.Faces`): a face that meets no edited lane's old or new line is the same
  face in both webs, so only the faces that meet one are judged (the trial is still polygonized whole, one shapely call).

`way_outs` stays whole: each household's way out is a route through the whole web, which one moved end can re-route anywhere.
Every count equals the whole rule's on the trial; the equivalence is tested count by count (`tests/hamletgen/ways/test_web_counts.py`).

Research: plumbing - NONE: how the whole web's rules (`law.LAW`, `knots._WHOLE_RULES`) are counted on a trial
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_dist
from l7r.diagram.settlement._geom.indexes import PointGrid

from ..consts import Poly, Pt
from . import law
from .tree_base import _near_segs, _seg_items

_JOIN = law.JOIN_TOL


def _counted(lanes: Sequence[Mapping[str, Any]], ways: Sequence[Poly], i: int) -> bool:
    return not lanes[i].get("connector") and len(ways[i]) >= 2


class Partners:
    """Each lane's partners under one pair rule ("doubled" or "beside") on the web as it stands - the lanes `WebMemo.pair` says it
    runs on beside - and the trial's count of lanes with a partner, asking only the pairs that hold an edited lane."""

    __slots__ = ("kind", "partners")

    def __init__(self, kind: str, pair: Callable[[str, int, int], bool], lanes: Sequence[Mapping[str, Any]], ways: Sequence[Poly], ids: Sequence[int]) -> None:
        self.kind = kind
        self.partners: dict[int, set[int]] = {i: {j for j in range(len(ways)) if j != i and pair(kind, ids[i], ids[j])} for i in range(len(ways)) if _counted(lanes, ways, i)}

    def count(self) -> int:
        return sum(1 for p in self.partners.values() if p)

    def trial(self, pair: Callable[[str, int, int], bool], lanes: Sequence[Mapping[str, Any]], tw: Sequence[Poly], ti: Sequence[int], edits: Sequence[int]) -> int:
        """`memo.count(kind, trial, tw, ti)`: the lanes of the trial with a partner, the edited lanes asked of every lane and every
        other lane asked of the edited ones only."""
        edited = set(edits)
        n = 0
        for i in range(len(tw)):
            if not _counted(lanes, tw, i):
                continue
            if i in edited:
                n += any(j != i and pair(self.kind, ti[i], ti[j]) for j in range(len(tw)))
            else:
                n += bool(self.partners.get(i, set()) - edited) or any(e != i and pair(self.kind, ti[i], ti[e]) for e in edits)
        return n


class WebEnds:
    """Every lane end of the web as it stands, with its junction (within `JOIN_TOL` of another way) and, for a free one, the house
    that discharges it (`law.fronting_ends`), and the count of houses discharging more than `DOORSTEP_MAX`
    (`law.doorstep_ends`); a trial's count re-asks only the ends an edit can change."""

    __slots__ = ("counts", "egrid", "ends", "segs")

    def __init__(self, M: Mapping[str, Any], lanes: Sequence[Mapping[str, Any]], ways: Sequence[Poly]) -> None:
        self.segs = PointGrid()
        for i, p in enumerate(ways):
            if len(p) >= 2:
                self.segs.extend(_seg_items(i, p, _JOIN))
        self.egrid = PointGrid()
        self.ends: dict[tuple[int, int], tuple[Pt, int | None]] = {}  # (lane, end) -> (point, the house discharging it or None)
        houses = M.get("houses") or []
        for i, p in enumerate(ways):
            if not houses or not _counted(lanes, ways, i):
                continue
            for e, end in ((0, p[0]), (-1, p[-1])):
                self.ends[(i, e)] = (end, None if self._joined(end, i, ways, ()) else _discharger(end, houses, M))
                self.egrid.extend([(i, e, end[0], end[1], end[0], end[1])])
        self.counts: dict[int, int] = {}
        for _q, h in self.ends.values():
            if h is not None:
                self.counts[h] = self.counts.get(h, 0) + 1

    def _joined(self, end: Pt, i: int, ways: Sequence[Poly], edits: Sequence[int], moved: Mapping[int, Poly] | None = None) -> bool:
        """Is `end` (of lane `i`) within the junction gap of another way - the web's, the edited lanes' new lines standing for their old?"""
        if any(k != i and k not in edits and seg_dist(end[0], end[1], a, b) <= _JOIN for k, a, b, *_ in self.segs.near(end[0], end[1], 0.0)):
            return True
        return any(k != i and len(p) >= 2 and law._min_dist(end, p) <= _JOIN for k, p in (moved or {}).items())

    def count(self) -> int:
        return sum(1 for n in self.counts.values() if n > law.DOORSTEP_MAX)

    def trial(self, M: Mapping[str, Any], lanes: Sequence[Mapping[str, Any]], ways: Sequence[Poly], tw: Sequence[Poly], edits: Sequence[int]) -> int:
        """`len(law.doorstep_ends(trial))`, from `trial_counts`."""
        return sum(1 for n in self.trial_counts(M, lanes, ways, tw, edits).values() if n > law.DOORSTEP_MAX)

    def trial_counts(self, M: Mapping[str, Any], lanes: Sequence[Mapping[str, Any]], ways: Sequence[Poly], tw: Sequence[Poly], edits: Sequence[int]) -> dict[int, int]:
        """`law.fronted_ends(trial)` (with zeros where a house lost its last end): the edited lanes' ends judged anew, and every
        other end within the junction gap of an edited lane's old or new line re-asked its junction."""
        houses = M.get("houses") or []
        if not houses:
            return {}
        counts = dict(self.counts)
        moved = {k: tw[k] for k in edits}
        near: set[tuple[int, int]] = set()
        for k in edits:
            for p in (ways[k], tw[k]):
                if len(p) >= 2:
                    near |= {key for it in _near_segs(self.egrid, p, _JOIN) if (key := (it[0], it[1])) in self.ends and it[0] not in moved}
        for key in near:
            q, h = self.ends[key]
            now = None if self._joined(q, key[0], ways, edits, moved) else (h if h is not None else _discharger(q, houses, M))
            if h is not None:
                counts[h] -= 1
            if now is not None:
                counts[now] = counts.get(now, 0) + 1
        for k in edits:
            for e in (0, -1):
                old = self.ends.get((k, e))
                if old is not None and old[1] is not None:
                    counts[old[1]] -= 1
            if _counted(lanes, tw, k):
                for end in (tw[k][0], tw[k][-1]):
                    if not self._joined(end, k, ways, edits, moved):
                        h = _discharger(end, houses, M)
                        if h is not None:
                            counts[h] = counts.get(h, 0) + 1
        return counts


def _discharger(end: Pt, houses: Sequence[Mapping[str, Any]], M: Mapping[str, Any]) -> int | None:
    """The house a free end at `end` is discharged by - its nearest, the first of the nearest - when it reaches that steading."""
    best = min(range(len(houses)), key=lambda h: math.hypot(end[0] - houses[h]["x"], end[1] - houses[h]["y"]))  # `fronting_ends`' own key
    return best if law.reach_to_steading(end, houses[best], M) else None
