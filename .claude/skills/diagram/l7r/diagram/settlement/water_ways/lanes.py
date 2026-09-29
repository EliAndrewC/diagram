"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
    edge_dist,
    point_in_poly,
    rot_rect,
    seg_dist,
)
from ..rolling.fit import houses_meeting
from ._helpers import (
    _FRAY_DEG,
    _LANE_MIN_FT,
    BUND_REACH_FT,
    DOORYARD_REACH_FT,
    HOUSE_SERVE_FT,
    _angle_between,
    _lane_len,
    _pull_back,
    fan_rival,
    junction_floor,
    vertex_behind,
    walked_past,
)

if TYPE_CHECKING:
    from ..core import Settlement


def _house_frame(house: Any, q: Pt) -> tuple[float, float]:
    """`q` in the house's own frame: +x along the ridge, +y out through the FRONT face - the side the threshing yard is
    laid on (`rolling/bundle.py`: the yard at `hy + hh / 2 + gap`, turned with the house by its rake)."""
    th = math.radians(float(house.get("rot") or 0.0))
    dx, dy = q[0] - float(house["x"]), q[1] - float(house["y"])
    return (dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th))


def behind_house(house: Any, q: Pt) -> bool:
    """Does `q` stand BEHIND the house - past its back wall, abreast of it (feature 287, water W57)?"""
    lx, ly = _house_frame(house, q)
    return ly < -float(house["h"]) / 2 and abs(lx) <= float(house["w"]) / 2 + float(house["h"])


def reaches_dooryard(house: Any, q: Pt, reach: float = DOORYARD_REACH_FT) -> bool:
    """THE RULE (feature 287, water W57; 269 B17, research/homesteads/310): a lane end reaches a farmhouse at its DOORYARD -
    within `reach` of its threshing yard or its dooryard beds, or in the band `reach` deep in front of its front face.

    Never by distance to the house itself: 12 ft of the drawn house counted a lane ending behind the BACK wall as
    arrived (Kuwabata's lane 5, 11 ft behind house 1 and 43 ft from its yard - future-work, "A lane end behind a house
    counts as its dooryard"). `trim_lane_stubs` judges its ends with this, and the test of it reads it."""
    rot = float(house.get("rot") or 0.0)
    g = house.get("geom") or {}
    for r in [g[k] for k in ("yard",) if g.get(k) is not None] + list(g.get("gardens") or ()):
        quad = rot_rect(float(r[0]), float(r[1]), float(r[2]), float(r[3]), rot)
        if point_in_poly(q[0], q[1], quad) or edge_dist(q[0], q[1], quad) <= reach:
            return True
    lx, ly = _house_frame(house, q)
    hh = float(house["h"]) / 2
    return hh - 1e-6 <= ly <= hh + reach and abs(lx) <= float(house["w"]) / 2 + reach


class LanesMixin:
    def lane(self: Settlement, pts: Any, width: float = 16, clearance: float = 22, worn: bool = False, connector: bool = False, spur: bool = False) -> None:  # type: ignore[misc]
        """A village lane or connecting path. `worn=True` draws it as UNPAVED TRODDEN EARTH: a NARROW
        single track (China moved rural goods by WHEELBARROW + shoulder-pole porter + packhorse, not wide
        cart roads, so two carts could not pass), packed dirt with soft worn shoulders and NO center
        marking (a paved road was far beyond a village's means). `worn=False` keeps the legacy wide dashed
        lane (the dispersed pool maps until they are rebuilt). `clearance` is the no-build corridor
        half-width (keep houses off the tread). `connector=True` marks the trodden path that LEAVES the
        village for the wider world - it MUST run off the map edge (checked), never stop mid-landscape.
        See research/ways.html 'What vehicle used a village lane, and where could the lane run?'."""
        # a lane KEEPS ITSELF RECORDED (feature 287 M8): the web reshapes lanes in place, and each reshape is asked of the
        # registry of what stands at the write (`Kept`) - so a repair cannot lay a lane on what the overlap matrix forbids
        rec = self.standing.kept("lanes", {"pts": [[x, y] for x, y in pts], "worn": worn, "w": width, "connector": connector, "spur": spur})
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

    def reshape_lane(self: Settlement, ln: Any, pts: Any) -> bool:  # type: ignore[misc]
        """Rewrite lane record `ln` along `pts` (rounded to the record's 0.1 px) where the overlap matrix admits the lane as
        it would become on what stands (feature 287 M8: the question every lane rewrite asks before it writes - `Kept`
        refuses the write it did not ask). Returns whether it was written; a refused rewrite leaves the lane as it was,
        and the pass that asked takes the lane unchanged (its ink is the caller's to redraw, `reink_lane`)."""
        new = [[round(float(x), 1), round(float(y), 1)] for x, y in pts]
        if not self.admits("lanes", {**ln, "pts": new}, ignore=ln):
            return False
        ln["pts"] = new
        return True

    def admits_lane(self: Settlement, pts: Any, width: float) -> bool:  # type: ignore[misc]
        """May a new lane along `pts`, `width` wide, be recorded on what stands (the overlap matrix, feature 287 M8)? Asked as
        `lane` would record it."""
        return len(pts) < 2 or self.admits("lanes", {"pts": [[float(x), float(y)] for x, y in pts], "w": width})

    def admitted_runs(self: Settlement, pts: Any, width: float) -> list[Any]:  # type: ignore[misc]
        """The runs of `pts` a new lane `width` wide may be recorded along (`admits_lane`): the polyline with every segment
        the overlap matrix forbids on what stands taken out, the pieces either side kept (feature 287 M8: the placer that
        lays a draft way offers only what the registry admits, as the web's settle would cut it)."""
        runs: list[Any] = []
        cur: list[Any] = []
        for a, b in zip(pts, pts[1:], strict=False):
            if self.admits_lane([a, b], width):
                cur = cur or [a]
                cur.append(b)
            else:
                if len(cur) >= 2:
                    runs.append(cur)
                cur = []
        if len(cur) >= 2:
            runs.append(cur)
        return runs

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

    def drop_lanes(self: Settlement, idxs: Iterable[int]) -> None:  # type: ignore[misc]
        """Retire lanes `idxs`: blank each one's ink, then remove its record AND its ink slot, back to front.

        THE RECORD LIST AND THE INK LIST ARE INDEXED TOGETHER, and a pass that deletes from one owns the other
        (settlement-review, feature 230 pass 10). Five passes in `hamletgen.ways` removed a dropped lane's record
        with `del lanes[i]` and left `_lane_ink[i]` in place, so every later lane was re-inked into its
        predecessor's slot. It stayed latent while the dropped lane happened to be the last one; feature 230 made
        the field spur a record drawn before the connector, swept it as an orphan, and Inashiro shipped with its
        connector track - its only way off the map - not drawn at all, a web lane drawn at the connector's width,
        and the last lane inked twice. Every check that reads the manifest was green, because the manifest still
        held the connector. `trim_lane_stubs` below always rebuilt both lists together; this is that rule, once."""
        gone = sorted(set(idxs), reverse=True)
        if any(self.M["lanes"][i].get("spur") for i in gone):
            # THE FIELD SPUR NEVER GOES SILENTLY, whichever pass drops it (settlement-review, feature 230 pass 11): two passes
            # recorded their own drop of it and the others did not, so the reference hamlet lost its only path to the rice with
            # nothing in the manifest to say so. A pass that already said why keeps its own words.
            self.M["meta"].setdefault("field_spur_swept", "dropped by a later pass - collapsed, or serving nothing the web does not")
        for i in gone:
            self.M["lanes"][i]["pts"] = []
            self.reink_lane(i)
        for i in gone:
            del self.M["lanes"][i]
            del self._lane_ink[i]

    def trim_lane_stubs(  # type: ignore[misc]
        self: Settlement, way_reach: float = 40.0, house_reach: float = HOUSE_SERVE_FT, dooryard_reach: float = DOORYARD_REACH_FT, fan_spread: float = 60.0, fan_bearing: float = 25.0
    ) -> int:
        """Pull back any internal lane end that REACHES NOTHING. Returns how many ends were trimmed.

        A lane exists to be fronted. The engine already ends an arm where it meets crop or water
        ("shortening the arm is the honest fix: the lane simply ends where the crop starts"), but an
        arm that meets neither runs the full cluster band into open ground - and the thing that says
        where it should stop, namely where the houses actually landed, does not exist when the lanes
        are laid. Lanes must be laid FIRST: a lane is a no-build corridor the homesteads front. So
        the trim happens here instead, after the flush, by rewriting the ink in the stream slots the
        lane already owns - the lane keeps its exact draw position and nothing re-layers.

        A FARMHOUSE IS REACHED AT ITS DOORYARD (269 B17, research/homesteads/310: "a lane that serves a farmhouse ends at
        that house's dooryard ... a lane end that reaches nothing is pulled back to the last house it serves"). An end serves
        a house when it stands within `dooryard_reach` of the house's drawn footprint, yard or beds, or within `house_reach`
        of its center while the house still lies ahead of it - never past it. It was 90 ft from the CENTER, in any
        direction, which let an arm run on past the last steading into the grass (Sawada, Kashikawa). An end on the field's
        bund has arrived too (`BUND_REACH_FT`, research/fields/290).

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
        # the worked ground a lane may end on: the fields' outlines and the dry plots (hamletgen reads the drawn rice too)
        fields = [[(float(a), float(b)) for a, b in f.get("outline") or []] for f in self.M.get("fields") or [] if len(f.get("outline") or []) >= 3]
        fields += [[(float(a), float(b)) for a, b in d["poly"]] for d in self.M.get("dry_plots") or [] if len(d.get("poly") or []) >= 3]
        trimmed = 0
        _drop: set[int] = set()

        def _fan_rival(q: Pt, bearing: float, house: Pt, mine: float, me: int) -> bool:
            return fan_rival(lanes, q, bearing, house, mine, me, fan_spread, fan_bearing)

        for i, ln in enumerate(lanes):
            # THE FIELD SPUR IS NOT A STUB (feature 261): its outer end reaches the FIELD, which is neither a lane nor a
            # house, so this pass read it as a dead end, pulled it back and dropped what was left for being short - on
            # Inashiro the only way to the rice, across the brook at a ford, with no record. Like the connector, whose far
            # end reaches the frame, it is judged by the sweeps, which record a spur they drop (`field_spur_swept`).
            if ln.get("connector") or ln.get("spur") or i >= len(self._lane_ink):
                continue
            pts = [(float(x), float(y)) for x, y in ln["pts"]]
            if len(pts) < 2:
                continue

            def _reaches(q: Pt, me: int = i, run: Any = None, back: Pt | None = None) -> bool:
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
                for h in houses_meeting(houses, (q[0] - house_reach, q[1] - house_reach, q[0] + house_reach, q[1] + house_reach)):
                    _d = math.hypot(q[0] - h["x"], q[1] - h["y"])
                    # AT ITS DOORYARD, OR BESIDE THE HOUSE AND NOT PAST IT (269 B17): within the serving reach of the center
                    # only while the house still lies ahead of the end or level with it - an end that has walked on past
                    # its last house is pulled back to it, as `_trim_to_service` cuts one at its closest approach
                    _from = back if back is not None else (run[0] if run is not None else None)
                    # ...AND NEVER BEHIND IT (feature 287, water W57): the dooryard is the yard and the front, not 12 ft of
                    # any wall, and an end abreast of the back wall is not "beside the house" either - it is behind it.
                    if not reaches_dooryard(h, q, dooryard_reach) and (_d > house_reach or behind_house(h, q) or (_from is not None and walked_past(_from, q, (h["x"], h["y"])))):
                        continue
                    if _my is None or not _fan_rival(q, _my, (h["x"], h["y"]), _d, me):
                        return True
                return any(edge_dist(q[0], q[1], f) <= BUND_REACH_FT for f in fields)

            def _junction_floor(_p: list[Pt], me: int = i) -> float:
                """This lane's junction floor - see `junction_floor`, which holds the body."""
                return junction_floor(_p, lanes, _drop, way_reach, me)

            for _ in range(2):  # each end in turn; a 2-point lane can lose at most one
                if len(pts) >= 2 and not _reaches(pts[-1], run=(pts[-2], pts[-1])):
                    pts = _pull_back(pts, lambda q, _p=pts: _reaches(q, run=(_p[-2], _p[-1]), back=vertex_behind(q, _p)), min_len=_junction_floor(pts))
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
            if self.reshape_lane(ln, pts):
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
            self.label(mid[0] + 38, mid[1], label, 11, italic=True, color="#5A4326", ref=(min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)))
