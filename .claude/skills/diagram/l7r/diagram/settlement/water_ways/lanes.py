"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
import re
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    seg_dist,
)
from ._helpers import _FRAY_DEG, _LANE_MIN_FT, _angle_between, _lane_len, _pull_back, fan_rival, junction_floor

if TYPE_CHECKING:
    from ..core import Settlement


class LanesMixin:
    def lane(self: Settlement, pts: Any, width: float = 16, clearance: float = 22, worn: bool = False, connector: bool = False) -> None:  # type: ignore[misc]
        """A village lane or connecting path. `worn=True` draws it as UNPAVED TRODDEN EARTH: a NARROW
        single track (China moved rural goods by WHEELBARROW + shoulder-pole porter + packhorse, not wide
        cart roads, so two carts could not pass), packed dirt with soft worn shoulders and NO center
        marking (a paved road was far beyond a village's means). `worn=False` keeps the legacy wide dashed
        lane (the dispersed pool maps until they are rebuilt). `clearance` is the no-build corridor
        half-width (keep houses off the tread). `connector=True` marks the trodden path that LEAVES the
        village for the wider world - it MUST run off the map edge (checked), never stop mid-landscape.
        See settlements.md 'Village lanes and connecting paths'."""
        rec = {"pts": [[x, y] for x, y in pts], "worn": worn, "w": width, "connector": connector}
        self.M.setdefault("lanes", []).append(rec)
        self._lane_ink.append(self._lane_ink_at(pts, width, worn, rec))
        # `M["lane"]` IS THE SPINE - the longest ordinary way on the map - not whichever lane was
        # drawn last. It used to be assigned unconditionally here, so it held the final `lane()` call
        # of the whole build, and five consumers read it as "the village street": two gate checks
        # (`segments_03b` structures-vs-street, `segments_04c` grove shading), the kosatsuba's route
        # list in `structures/fixtures.py`, and `_geom/ways.py`'s corridor runs. A settlement-review
        # measured what that means in practice (Sawada 2026-08-19): the key held a 45 ft floating
        # fragment in the NW, so two gate checks were adjudicating against a 45 ft orphan instead of
        # the 354 ft spine - they ran, they passed, and they were testing the wrong geometry. That is
        # the "a check that never runs looks exactly like a check that passes" family, one level down
        # at the INPUT rather than at the rule.
        #
        # Longest-wins is monotone, so a mid-build consumer gets the best spine available when it
        # asks rather than an arbitrary one; the connector is excluded because it is the road OUT,
        # not the street. Derived from geometry already on the map, never pinned.
        if not connector:
            _prev = self.M.get("lane")
            _prev_len = sum(math.dist(tuple(a), tuple(b)) for a, b in zip(_prev, _prev[1:], strict=False)) if _prev and len(_prev) > 1 else 0.0
            if sum(math.dist(a, b) for a, b in zip(pts, pts[1:], strict=False)) > _prev_len:
                self.M["lane"] = [[x, y] for x, y in pts]
        self.corridors.append((pts, clearance))
        self._record_tread(pts, width / 2)

    def _lane_ink_at(self: Settlement, pts: Any, width: float, worn: bool, rec: Any) -> tuple[int]:  # type: ignore[misc]
        """Emit a lane's two strokes INTO THE GROUND BLOCK and return the ground entry's index.

        JUNCTIONS RENDER AS ONE STRUCTURE (feature 150 T53, GM 2026-08-28: "When two village lane segments
        intersect ... it looks like one of them is literally just rendered on top of the other ... It should
        look as if they are all essentially one contiguous structure"). Drawn inline, a later lane's soft
        shoulder lay across an earlier lane's tread at every junction. The town streets never had the
        problem because they go through `_ground`: every SHOULDER (edge) in one sub-layer at the bottom,
        every TREAD (bed) above - so treads merge into one continuous surface and no shoulder crosses a
        tread. Lanes now take the same path; `zpri` is the width, so a wider way still wins where two
        treads overlap. `reink_lane` and the stub trimmer rewrite the ground entry, not stream slots."""
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        if worn:
            edge = f'<path d="{dd}" fill="none" stroke="#A98C58" stroke-width="{width + 2.5:.1f}" opacity="0.4" stroke-linejoin="round" stroke-linecap="round"/>'  # soft worn-earth shoulder
            bed = f'<path d="{dd}" fill="none" stroke="#C9AE79" stroke-width="{width:.1f}" opacity="0.9" stroke-linejoin="round" stroke-linecap="round"/>'  # packed-earth tread, no centerline
            self._ground(float(width), rec, "z", edge=edge, bed=bed, cls="village lane")
        else:
            bed = f'<path d="{dd}" fill="none" stroke="#CBB178" stroke-width="{width}" opacity="0.65"/>'
            top = f'<path d="{dd}" fill="none" stroke="#6B4F2A" stroke-width="1.4" stroke-dasharray="8,8" opacity="0.7"/>'
            self._ground(float(width), rec, "z", bed=bed, top=top, cls="village lane")
        return (len(self.ground) - 1,)

    def reink_lane(self: Settlement, i: int) -> None:  # type: ignore[misc]
        """Rewrite lane `i`'s DRAWN path from its record, so the two cannot disagree.

        THE RECORD AND THE INK ARE TWO COPIES OF ONE FACT, and any pass that shortens a lane owns
        both of them. `trim_lane_stubs` always did; the trim-to-service pass at the end of
        `hamletgen.stage_web` did not, and shortened the record alone - so Mizuguchi's field spur was
        DRAWN with a four-point path that hooked into the paddy and RECORDED as the two-point run
        without it. The 32 ft that touched the crop existed on the paper and nowhere else, which
        means `features_do_not_overlap`, `houses_clear_of_lanes` and every crop-margin rule were
        adjudicating a shorter lane than the one the reader sees. That is the skill's standing
        "invisible to every matrix check in both directions" hazard, arrived at from the other side.

        Extracted here rather than copied so there is one way to do it and the next shortening pass
        cannot get it half right."""
        pts = self.M["lanes"][i]["pts"]
        if len(pts) < 2:
            # A DROPPED LANE DRAWS NOTHING (feature 134, found by the browser: Chromium logged
            # `<path> attribute d: Unexpected end of attribute` twice on Inashiro). `hamletgen.ways`
            # retires a lane by emptying its record and re-inking it, and this wrote `d="M"` - a
            # path with no points, which resvg ignores silently and a browser reports as an error
            # on every open. Blank the ink instead, exactly as `trim_lane_stubs` does for a stub.
            for z in self._lane_ink[i]:
                for part in ("edge", "bed", "top"):
                    if self.ground[z].get(part):
                        self.ground[z][part] = ""
            return
        dd = "M" + " L".join(f"{x},{y}" for x, y in pts)
        for z in self._lane_ink[i]:
            for part in ("edge", "bed", "top"):
                if self.ground[z].get(part):
                    self.ground[z][part] = re.sub(r'd="M[^"]*"', f'd="{dd}"', self.ground[z][part], count=1)

    def trim_lane_stubs(self: Settlement, way_reach: float = 40.0, house_reach: float = 90.0, fan_spread: float = 60.0, fan_bearing: float = 25.0) -> int:  # type: ignore[misc]
        """Pull back any internal lane end that REACHES NOTHING. Returns how many ends were trimmed.

        A lane exists to be fronted. The engine already ends an arm where it meets crop or water
        ("shortening the arm is the honest fix: the lane simply ends where the crop starts"), but an
        arm that meets neither runs the full cluster band into open ground - and the thing that says
        where it should stop, namely where the houses actually landed, does not exist when the lanes
        are laid. Lanes must be laid FIRST: a lane is a no-build corridor the homesteads front. So
        the trim happens here instead, after the flush, by rewriting the ink in the stream slots the
        lane already owns - the lane keeps its exact draw position and nothing re-layers.

        MEASURED before it existed: five internal lane ends across the four live scripted hamlets
        (and honda, ubame x4, kikuta x2, tanada, hoshizora among the frozen ones) ended more than
        40 ft from any other way AND more than 90 ft from any farmhouse - a blunt tread stopping in
        bare grass, serving no house, reaching no field, connecting to nothing. On Sawada one such
        arm also ran 13 ft from and near-parallel to the lane it had already met, reading at fit zoom
        as one doubled track rather than a fork.

        TRIMMING ONLY EVER SHORTENS, which is what makes it safe to run after placement: a corridor
        that shrinks cannot invalidate a house already seated against it. The CONNECTOR is exempt and
        must stay whole - it is the track out of the settlement and `connector_lane_runs_off_edge`
        requires it to reach the frame; a path stopping mid-landscape is the defect, not the cure."""
        lanes = self.M.get("lanes") or []
        houses = self.M.get("houses") or []
        trimmed = 0
        _drop: set[int] = set()

        def _fan_rival(q: Pt, bearing: float, house: Pt, mine: float, me: int) -> bool:
            return fan_rival(lanes, q, bearing, house, mine, me, fan_spread, fan_bearing)

        for i, ln in enumerate(lanes):
            if ln.get("connector") or i >= len(self._lane_ink):
                continue
            pts = [(float(x), float(y)) for x, y in ln["pts"]]
            if len(pts) < 2:
                continue

            def _reaches(q: Pt, me: int = i, run: Any = None) -> bool:
                for k, other in enumerate(lanes):
                    if k == me or len(other["pts"]) < 2:
                        continue
                    op = [(float(x), float(y)) for x, y in other["pts"]]
                    _near = min(zip(op, op[1:], strict=False), key=lambda ab: seg_dist(q[0], q[1], ab[0], ab[1]))
                    if seg_dist(q[0], q[1], _near[0], _near[1]) > way_reach:
                        continue
                    # A LANE THAT MEETS ANOTHER CROSSES IT; ONE THAT FRAYS RUNS ALONGSIDE IT.
                    # Proximity alone is not arrival, and taking it as such made this predicate blind
                    # to the very arm the docstring above cites: Sawada's lane 0 ran 90 ft past its
                    # own T with lane 2 and died 13 ft from it on an 8 deg divergence, so it was
                    # "within 40 ft of another way" - the lane it had ALREADY met - and passed. The
                    # adjacency that constitutes the defect was satisfying the test for it.
                    if run is not None and _angle_between(run, _near) < _FRAY_DEG:
                        continue  # near-parallel: this is the same track fraying, not a junction
                    return True
                # A FARMHOUSE DISCHARGES ONE LANE END'S OBLIGATION, NOT THREE.
                #
                # Nothing said a house could only be claimed once, so three ends standing within 40
                # ft of each other, all fronting the same house at 66.9 / 55.1 / 40.0 ft, all passed
                # - and a settlement-review read the result at 3x zoom as a broom: not three ways,
                # one way drawn three times with the ends fanned. The end NEAREST the house keeps it;
                # any other end alongside it, pointing the same way, has to find its own reason to
                # exist or be trimmed back until it does.
                #
                # The bearing clause is what keeps a genuine CROSSROADS legal. Two lanes reaching one
                # house from opposite quarters is a house on a corner - a real thing that reads as
                # one. It is only ends arriving ALONGSIDE each other that the eye merges.
                _my = math.degrees(math.atan2(run[1][1] - run[0][1], run[1][0] - run[0][0])) if run else None
                for h in houses:
                    _d = math.hypot(q[0] - h["x"], q[1] - h["y"])
                    if _d > house_reach:
                        continue
                    if _my is None or not _fan_rival(q, _my, (h["x"], h["y"]), _d, me):
                        return True
                return False

            def _junction_floor(_p: list[Pt], me: int = i) -> float:
                """This lane's junction floor - see `junction_floor`, which holds the body."""
                return junction_floor(_p, lanes, _drop, way_reach, me)

            for _ in range(2):  # each end in turn; a 2-point lane can lose at most one
                if len(pts) >= 2 and not _reaches(pts[-1], run=(pts[-2], pts[-1])):
                    pts = _pull_back(pts, lambda q, _p=pts: _reaches(q, run=(_p[-2], _p[-1])), min_len=_junction_floor(pts))
                    trimmed += 1
                pts.reverse()
            # ...and a lane too SHORT to front anybody is not a lane at all, it is clipping debris.
            # An arm cut back by crop or water can be left as a stub, and a stub cannot be trimmed
            # into legitimacy - shortening it only moves the same unserved end closer in. A lane
            # exists to be fronted and one homestead's frontage is ~71 ft, so below that it fronts
            # nobody by construction. Measured: the shortest genuine internal lane in the whole pool
            # is 90 ft and the median is 361; cohort seed 5 carried a 33 ft fragment whose far end
            # stood 97 ft from the nearest farmhouse and which no amount of trimming could rescue.
            if _lane_len(pts) < _LANE_MIN_FT / max(float(self.M["meta"].get("ftpx", 1) or 1), 0.01):
                _drop.add(i)
                for _z in self._lane_ink[i]:
                    for _part in ("edge", "bed", "top"):
                        if self.ground[_z].get(_part):
                            self.ground[_z][_part] = ""
                trimmed += 1
                continue
            if [list(p) for p in pts] == ln["pts"]:
                continue
            ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in pts]
            self.reink_lane(i)
        if _drop:  # rebuild record and ink together so their indices stay aligned
            self.M["lanes"] = [ln for k, ln in enumerate(lanes) if k not in _drop]
            self._lane_ink = [z for k, z in enumerate(self._lane_ink) if k not in _drop]
        return trimmed

    def street(self: Settlement, pts: Any, width: float | None = None, label: Any = None, main: bool = False) -> None:  # type: ignore[misc]
        """A town street (packed earth): the gate-to-yamen main avenue (main=True) or a
        cross lane off it. Buildings front it; a no-build corridor runs down its center.
        Default real width 24 ft (converted at the map's ftpx, linework-floored)."""
        if width is None:
            width = self.lw(24)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        self.corridors.append(
            (pts, width / 2 + max(32 * self.bscale, 17))
        )  # buildings front the street but their corners stay off the bed (margin at the map's grain, floored at the largest dwelling's half-diagonal)
        st = {"main": main, "w": width, "pts": [[x, y] for x, y in pts], "z": None}
        self.M.setdefault("town_streets", []).append(st)
        self._ground(
            width,
            st,
            "z",
            edge=f'<path d="{dd}" fill="none" stroke="#B49A66" stroke-width="{width}" opacity="0.9" stroke-linejoin="round" stroke-linecap="round"/>',
            bed=f'<path d="{dd}" fill="none" stroke="#D9C8A0" stroke-width="{width - 7}" opacity="1" stroke-linejoin="round" stroke-linecap="round"/>',
        )
        if label:
            mid = pts[len(pts) // 2]
            self.label(mid[0] + 38, mid[1], label, 11, italic=True, color="#5A4326")
