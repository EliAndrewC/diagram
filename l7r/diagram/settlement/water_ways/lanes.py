"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: lane records and their ink - NONE
"""

import math
import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from l7r.diagram.overlap.registry import refuse_unadmitted

from .._geom import (
    Pt,
    edge_dist,
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
    dooryard_dist,
    fan_rival,
    junction_floor,
)

if TYPE_CHECKING:
    from ..core import Settlement


def reaches_dooryard(house: Any, q: Pt, reach: float = DOORYARD_REACH_FT) -> bool:
    """THE RULE (269 B17; research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html): a lane end
    reaches a farmhouse within `reach` of the steading's built ground - its house, byre, shed, threshing yard or garden - on
    ANY side (`dooryard_dist`). Feature 287's water W57 counted only the yard, the beds and a band before the front face, so
    that Kuwabata's lane 5, ending 11 ft behind house 1's back wall, would not read as arrived; 0246 counts every side, as
    wave 45 did for the scripted tier's twins (`off_the_back`, `settle_ends`), and feature 328 wave 66 took this one there.

    Research: a lane reaches the steading - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of its house, byre, shed, threshing yard or garden, on any side"""
    return dooryard_dist(house, q) <= reach


STREET_W_FT = 24.0
"""Research: street width - research/questions/0136-town-streets-side-lanes-and-back-alleys-roji.drawing.html: a town street 24 ft by default"""


class LanesMixin:
    def lane(self: Settlement, pts: Any, width: float = 16, clearance: float = 22, worn: bool = False, connector: bool = False, spur: bool = False) -> None:  # type: ignore[misc]
        """A village lane or connecting path. `worn=True` draws it as UNPAVED TRODDEN EARTH: a NARROW
        single track (China moved rural goods by WHEELBARROW + shoulder-pole porter + packhorse, not wide
        cart roads, so two carts could not pass), packed dirt with soft worn shoulders and NO center
        marking (a paved road was far beyond a village's means). `worn=False` keeps the legacy wide dashed
        lane (the dispersed pool maps until they are rebuilt). `clearance` is the no-build corridor
        half-width (keep houses off the tread). `connector=True` marks the trodden path that LEAVES the
        village for the wider world - it MUST run off the map edge (checked), never stop mid-landscape.
        See research/questions/0081-village-lanes.html.

        Research:
            a worn earth track - research/questions/0081-village-lanes.html, research/questions/0081-village-lanes.drawing.html: narrow, packed earth, no centerline; every hamlet caller passes `worn=True`, the dashed default is the town tier's
            lane width - NONE: the caller's width; the 16 px default is the town tier's, every hamlet caller passes its own
            nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a no-build corridor of the clearance the caller passes (the 22 px default is the town tier's)
            the track out runs off the map - research/questions/0081-village-lanes.drawing.html: the connector flag
        """
        # a lane KEEPS ITSELF RECORDED (feature 287 M8): the web reshapes lanes in place, and each reshape is asked of the
        # registry of what stands at the write (`Kept`) - so a repair cannot lay a lane on what the overlap matrix forbids
        # ...AND IT IS ASKED BEFORE IT IS RECORDED OR INKED (feature 287, water W53): every placer that lays a lane chose it among
        # what the registry admits (`admits_lane`, `admitted_runs`, the settle's `Lawful`, the connector's `connector_keeps_the_law`),
        # so a refusal here names the engine defect by name before any of its ink is emitted, as the one-candidate writers do
        # (`registry.refuse_unadmitted`; a Kuwabata lane was the last record the census found written unasked)
        new = {"pts": [[x, y] for x, y in pts], "worn": worn, "w": width, "connector": connector, "spur": spur}
        refuse_unadmitted(self.M, "lanes", new)
        rec = self.standing.kept("lanes", new)
        self.M.setdefault("lanes", []).append(rec)
        self._lane_ink.append(self._lane_ink_at(pts, width, worn, rec))
        # NO `M["lane"]` IS WRITTEN (feature 287 wave 6). It held "the spine" - the longest ordinary way drawn so far - kept by
        # `lane()` alone, so every later rewrite of that lane (the web's passes, the settle's cuts and drops) left it standing
        # as a copy of a lane no longer on the map: on cohort seeds 25 and 42 it was none of `M["lanes"]`. Every reader of a
        # generated map reads `M["lanes"]` (`_geom/ways.street_runs`, `lane_runs`); `M["lane"]` is read only where a hand-built
        # fixture carries it and no `lanes`.
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
        treads overlap. `reink_lane` and the stub trimmer rewrite the ground entry, not stream slots.

        Research:
            lane strokes - CONVENTION: a soft shoulder and an earth tread; the legacy lane a dashed center line
            junctions as one surface - CONVENTION: every shoulder under every tread
        """
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
        self: Settlement, way_reach: float | None = None, house_reach: float = HOUSE_SERVE_FT, dooryard_reach: float = DOORYARD_REACH_FT, fan_spread: float = 60.0, fan_bearing: float = 25.0
    ) -> int:
        """Pull back any internal lane end that REACHES NOTHING. Returns how many ends were trimmed.

        A lane exists to be fronted. The engine already ends an arm where it meets crop or water
        ("shortening the arm is the honest fix: the lane simply ends where the crop starts"), but an
        arm that meets neither runs the full cluster band into open ground - and the thing that says
        where it should stop, namely where the houses actually landed, may not exist when a lane is laid. So the trim
        is asked after the lanes are drawn - in the scripted hamlet, right after the web's runs, against the placed
        houses - by rewriting the ink in the stream slots the lane already owns: the lane keeps its exact draw position and
        nothing re-layers. It also drops an internal lane shorter than `_LANE_MIN_FT` (71 ft).

        A FARMHOUSE IS REACHED AT ITS DOORYARD (269 B17, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: "a lane that serves a farmhouse ends at
        that house's dooryard ... a lane end that reaches nothing is pulled back to the last house it serves"). An end serves
        a house when it stands within `dooryard_reach` of the steading's built ground (its house, byre, shed, threshing yard
        or garden) or within `house_reach` of the house, on any side (0246; feature 328 wave 67 retired the dooryard-only
        and never-past refusals). It was 90 ft from the CENTER, which let an arm run on past the last steading into the
        grass (Sawada, Kashikawa); 0246's 60 ft is the reach now. An end on the field's bund has arrived too (`BUND_REACH_FT`, research/questions/0014-bunds-between-the-paddies-aze.drawing.html).

        MEASURED before it existed: five internal lane ends across the four live scripted hamlets
        (and honda, ubame x4, kikuta x2, tanada, hoshizora among the frozen ones) ended more than
        40 ft from any other way AND more than 90 ft from any farmhouse - a blunt tread stopping in
        bare grass, serving no house, reaching no field, connecting to nothing. On Sawada one such
        arm also ran 13 ft from and near-parallel to the lane it had already met, reading at fit zoom
        as one doubled track rather than a fork.

        TRIMMING ONLY EVER SHORTENS, which is what makes it safe to run after placement: a corridor
        that shrinks cannot invalidate a house already seated against it. The CONNECTOR is exempt and
        must stay whole - it is the track out of the settlement and `connector_lane_runs_off_edge`
        requires it to reach the frame; a path stopping mid-landscape is the defect, not the cure.

        Research:
            an end reaching nothing is pulled back - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: to the last house, way or bund it serves
            served at the dooryard - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of the steading's built ground or 60 ft of the house's drawn footprint, on any side, at the map's scale
            arrival at the bund - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: within 6 ft of a field's or dry plot's edge, at the map's scale (the page gives no figure)
            meeting another way - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of it, at 20 degrees or more
            one end per house and bearing - UNRESEARCHED: a second end within 60 ft and 25 degrees of another fronting the same house is trimmed
            short lanes dropped - UNRESEARCHED: an internal lane under 71 ft
            the track out and the field spur stay whole - research/questions/0081-village-lanes.drawing.html
            a row street stays whole - research/questions/0033-row-villages-resson.drawing.html: the street runs on off the map as the road into it, its ends not pulled back as a lane's are
        """
        way_reach = self.px(60.0) if way_reach is None else way_reach  # 0246: within 60 ft of another way, at the map's scale
        # 0246's two reaches, at the map's scale (feature 328 wave 67: they were read as pixels, right only at 1 ft/px)
        house_px, dooryard_px = self.px(house_reach), self.px(dooryard_reach)
        lanes = self.M.get("lanes") or []
        houses = self.M.get("houses") or []
        # the worked ground a lane may end on: the fields' outlines and the dry plots (hamletgen reads the drawn rice too)
        fields = [[(float(a), float(b)) for a, b in f.get("outline") or []] for f in self.M.get("fields") or [] if len(f.get("outline") or []) >= 3]
        fields += [[(float(a), float(b)) for a, b in d["poly"]] for d in self.M.get("dry_plots") or [] if len(d.get("poly") or []) >= 3]
        trimmed = 0
        _drop: set[int] = set()

        def _fan_rival(q: Pt, bearing: float, house: Pt, mine: float, me: int) -> bool:
            return fan_rival(lanes, q, bearing, house, mine, me, self.px(fan_spread), fan_bearing)  # the 60 ft at the map's scale (feature 328 wave 67)

        for i, ln in enumerate(lanes):
            # THE FIELD SPUR IS NOT A STUB (feature 261): its outer end reaches the FIELD, which is neither a lane nor a
            # house, so this pass read it as a dead end, pulled it back and dropped what was left for being short - on
            # Inashiro the only way to the rice, across the brook at a ford, with no record. Like the connector, whose far
            # end reaches the frame, it is judged by the sweeps, which record a spur they drop (`field_spur_swept`).
            if ln.get("connector") or ln.get("spur") or ln.get("street") or i >= len(self._lane_ink):  # a row village's street is laid whole (feature 291)
                continue
            pts = [(float(x), float(y)) for x, y in ln["pts"]]
            if len(pts) < 2:
                continue

            def _reaches(q: Pt, me: int = i, run: Any = None) -> tuple[Any, ...] | None:
                """WHAT this end reaches - a way, a house or a field, named - or None: `_pull_back` holds an end to the one
                thing it served last (0246), so it has to know which (feature 328 wave 66)."""
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
                    return ("way", k)
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
                # the index files each house by its whole steading's extent (`house_extent`: house, yard, shed, byre, beds),
                # so a box of the larger reach round the end meets every house either reach could find
                _box = max(house_px, dooryard_px)
                for h in houses_meeting(houses, (q[0] - _box, q[1] - _box, q[0] + _box, q[1] + _box)):
                    _d = math.hypot(q[0] - h["x"], q[1] - h["y"])  # from the center: the fan rule's measure, not the reach's
                    # WITHIN 60 FT OF THE HOUSE - its drawn footprint - OR 12 FT OF ITS BUILT GROUND, ON ANY SIDE (0246): the
                    # dooryard-only and never-past refusals of feature 287 (water W57, 269 B17) are retired (feature 328 wave 67)
                    _house = {"x": h["x"], "y": h["y"], "w": h["w"], "h": h["h"], "rot": h.get("rot")}
                    if not reaches_dooryard(h, q, dooryard_px) and dooryard_dist(_house, q) > house_px:
                        continue
                    if _my is None or not _fan_rival(q, _my, (h["x"], h["y"]), _d, me):
                        return ("house", id(h))
                return next((("field", fi) for fi, f in enumerate(fields) if edge_dist(q[0], q[1], f) <= self.px(BUND_REACH_FT)), None)

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
            if self.reshape_lane(ln, pts):
                self.reink_lane(i)
        if _drop:  # rebuild record and ink together so their indices stay aligned
            self.M["lanes"] = [ln for k, ln in enumerate(lanes) if k not in _drop]
            self._lane_ink = [z for k, z in enumerate(self._lane_ink) if k not in _drop]
        return trimmed

    def street(self: Settlement, pts: Any, width: float | None = None, label: Any = None, main: bool = False) -> None:  # type: ignore[misc]
        """A town street (packed earth): the gate-to-yamen main avenue (main=True) or a
        cross lane off it. Buildings front it; a no-build corridor runs down its center.
        Default real width 24 ft (converted at the map's ftpx, linework-floored).

        Research:
            street width - research/questions/0136-town-streets-side-lanes-and-back-alleys-roji.drawing.html: 24 ft by default
            buildings front the street - research/questions/0119-how-a-town-is-zoned-shops-on-the-street-housing-behind.html: a no-build corridor of the half-width plus max(32 x bscale, 17) px
            street strokes - CONVENTION: an earth edge and a lighter bed
        """
        if width is None:
            width = self.lw(STREET_W_FT)
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
