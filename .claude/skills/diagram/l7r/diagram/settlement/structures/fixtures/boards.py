"""Split from settlement/structures/fixtures.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING

from ..._geom import (
    LABEL_AIR_CAP,
    Poly,
    Pt,
    label_quad,
    label_tilt,
    linear_tilt,
    poly_gap,
    seg_dist,
    segments_cross,
    tilt_caption_seat,
)
from ..._knobs import KOSATSUBA_MARKER_MIN_PX
from ._helpers import CAPTION_LANE_FLOOR_FT, CAPTION_LANE_TARGET_FT, pick_caption_seat

if TYPE_CHECKING:
    from ...core import Settlement


class BoardsMixin:
    def fire_tower(self: Settlement, x: float, y: float, tw: float | None = None, rot: float = 0.0, label: str = "fire tower") -> int:  # type: ignore[misc]
        """A HINOMI-YAGURA (fire-watch tower): a tall, slender braced-timber tower with a lookout
        platform and an alarm bell (hansho), standing in the dense COMMONER quarter of a walled
        town or city where packed wooden rooftops make fire catastrophic. It is a CIVILIAN interior
        structure - the magistrate's fire-watch - distinct from a wall guard tower (military, on the
        rampart): drawn as an OPEN braced frame (not the guard tower's solid block) with a red bell.
        The watchman strikes the bell in a cadence that tells the town how near the fire is. Records
        M['fire_towers'] (an overlap-checked struct: it must stand clear of the wall, roads, and
        buildings) and reserves a small no-build block (it needs clear sightlines). Place it among the
        laborer/merchant blocks. See the settlements.md 'Fire towers' historical grounding."""
        if tw is None:
            tw = self.px(26)  # a real hinomi-yagura frame is ~26 ft square (town-calibrated glyph)
        h = tw / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-h - 2:.0f}" y="{-h - 5:.0f}" width="{tw + 4}" height="5" rx="1" fill="#7A5A30"/>')  # the little roof cap over the lookout platform
        g.append(f'<rect x="{-h:.0f}" y="{-h:.0f}" width="{tw}" height="{tw}" fill="#EFE6CC" fill-opacity="0.45" stroke="#7A5A30" stroke-width="2"/>')  # the open braced-timber frame
        g.append(f'<line x1="{-h:.0f}" y1="{-h:.0f}" x2="{h:.0f}" y2="{h:.0f}" stroke="#7A5A30" stroke-width="1.1"/>')  # cross-braces (an X)
        g.append(f'<line x1="{h:.0f}" y1="{-h:.0f}" x2="{-h:.0f}" y2="{h:.0f}" stroke="#7A5A30" stroke-width="1.1"/>')
        g.append(f'<circle cx="0" cy="0" r="{tw * 0.2:.1f}" fill="#B0462F" stroke="#5A3F1E" stroke-width="0.8"/>')  # the alarm bell (hansho)
        g.append('</g>')
        z = self.add_top(''.join(g))
        self.M["fire_towers"].append({"x": round(x, 1), "y": round(y, 1), "w": tw, "h": tw, "rot": round(rot, 1), "z": z, "label": label})
        self.placed.append((x, y, tw, tw))
        bm = 16
        self.block_polys.append([(x - h - bm, y - h - bm), (x + h + bm, y - h - bm), (x + h + bm, y + h + bm), (x - h - bm, y + h + bm)])
        if label:
            _t = label_tilt(rot)
            _lx, _ly = tilt_caption_seat(x, y, rot, _t, h, h, 14) if _t else (x, y + h + 14)
            self.label(_lx, _ly, label, 9, italic=True, color="#7A5A30", rot=_t)
        return z

    def kosatsuba(self: Settlement, x: float, y: float, rot: float = 0.0, label: str = "notice board", label_above: bool = False, label_xy: Pt | None = None) -> int:  # type: ignore[misc]
        """The KOSATSUBA - the settlement's official notice board: a small roofed frame posting
        the state's STANDING LAW (edicts, porter/packhorse rate tables, ban lists). Sited at the
        most TRAFFICKED public point - the highway frontage, the main street by the gate, a
        bridgehead or market corner - because it is the state talking at everyone who passes
        (Edo's principal board stood at Nihonbashi, the bridgehead). NEVER defaulted to the
        magistrate's manor gate: the manor's own board (Mode A program, buildings.md) posts the
        bench's OUTPUT (verdicts, bounties) for people who come to court, and the manor sits at
        the settlement edge where feet do not pass. True size ~12x5 ft (a 7x3 ft board under a
        small roof); the label carries the read.

        `rot` IS THE ROAD'S BEARING, not a free choice. The glyph's long axis is the board's
        FACE, so a board must stand square to the way it fronts - broadside to the traffic that
        reads it. Turned perpendicular, the face goes edge-on to everyone approaching and the
        institution fails while the siting checks stay green (that is exactly how Nagahara's
        third board shipped, GM 2026-07-27). Hand placements must pass the fronted route's
        bearing; `place_kosatsuba` derives it. Held by `kosatsuba_faces_the_road`. Records M['kosatsuba'] (an overlap-checked
        struct). WHY: settlements.md 'Notice board (kosatsuba)'. Place LAST, on a clear verge
        beside the road, like the fire tower.

        The DRAWN glyph is a LOCATION MARKER at the coarse tiers (GM call 2026-07-24, taking the
        escape settlements.md documented): the true 12x5 ft frame draws 6x2.5 px at village grain
        and 4x1.7 px at city grain - at city scale, rotated upright, that is a 1.7 px sliver that
        reads as gate hardware, not a feature (Nagahara: two of its three boards were invisible
        until the GM went looking, and the one that read did so only by its label). So the glyph
        is floored at KOSATSUBA_MARKER_MIN_PX on its long axis with the 12:5 aspect preserved -
        the wells' doctrine exactly (SKILL.md 'to scale'): the marker denotes the board's
        TO-SCALE LOCATION with legible pixels that are not themselves claimed to be to scale. The
        floor NEVER shrinks a board, so hamlets and towns (1 ft/px) still draw the true 12x5 px;
        only village and city grain lift. The manifest keeps the TRUE w/h (so a size audit reads
        real feet) and records the drawn box as vw/vh, which is what the overlap checks and the
        placement reservation use - the pixels that can actually collide."""
        w, h = self.px(12), self.px(5)
        k = max(1.0, KOSATSUBA_MARKER_MIN_PX / w)  # marker floor, aspect preserved
        vw, vh = w * k, h * k
        hw, hh = vw / 2, vh / 2
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-hw:.1f}" y="{-hh:.1f}" width="{vw:.1f}" height="{vh:.1f}" rx="1" fill="#7A5A30" stroke="#5A3F1E" stroke-width="0.8"/>')  # the little tiled roof, seen from above
        g.append(f'<line x1="{-hw:.1f}" y1="0" x2="{hw:.1f}" y2="0" stroke="#EFE6CC" stroke-width="0.9"/>')  # the ridge
        g.append('</g>')
        z = self.add_top(''.join(g), cls="notice board")
        self.M["kosatsuba"].append({"x": round(x, 1), "y": round(y, 1), "w": w, "h": h, "vw": round(vw, 1), "vh": round(vh, 1), "rot": round(rot, 1), "z": z, "label": label})
        self.placed.append((x, y, vw, vh))
        bm = 6
        self.block_polys.append([(x - hw - bm, y - hh - bm), (x + hw + bm, y - hh - bm), (x + hw + bm, y + hh + bm), (x - hw - bm, y + hh + bm)])
        if label:
            # THE BOARD IS PLACED HERE; ITS CAPTION IS SEATED IN THE LABEL PHASE (feature 157, GM
            # 2026-08-29: *"moving label placement so that the notice board itself is placed during a
            # separate phase than the labels for the map are placed"*). Unlike a `text` caption, whose
            # feature has already chosen its seat, a board's seat is SEARCHED - so the search has to
            # run when the map is finished, not when the plank goes in.
            self._label_queue.append(("kosatsuba", (x, y, rot, vw, vh, label, label_above, label_xy)))
        return z

    def _draw_board_caption(self: Settlement, x: float, y: float, rot: float, vw: float, vh: float, label: str, label_above: bool, label_xy: Pt | None) -> None:  # type: ignore[misc]
        """Seat and draw one notice board's caption, in the LABEL PHASE (feature 157).

        Split out of `kosatsuba` unchanged except for the seat rules below: the board is drawn when it
        is placed, the caption when every map feature exists. Reached through `place_labels`'s one-row
        dispatch table, never called directly."""
        hw, hh = vw / 2, vh / 2
        if label:
            # label_above: for a board standing just inside a gate, the default below-label
            # would hang over the gate structure (labels_clear_of_other_buildings).
            # label_xy: a HAND seat for the caption when BOTH bands are taken - the forcing
            # case was Nagahara's principal board at the market-bend junction, where the
            # below band holds the drum tower, the above band abuts the samurai ward gate's
            # glyph and its caption (settlement-review 2026-08-02: the two stacked captions
            # read as one label on the gate), and the clear ground is diagonal, east along
            # the road edge. Same escape the punishment ground and execution ground carry
            # (label_xy there) and for the same reason: a deferred/derived seat cannot be
            # probed from a gen, so the last resort is an explicit one. Direct-labeled, so
            # label_hugs_its_referent does not govern it - keep a hand seat close enough to
            # read as the board's own. A hand seat keeps its SPOT but the text still tilts
            # with a diagonal board (angled captions, GM 2026-08-02) - same merge as
            # punishment_spot's label_xy.
            # A BOARD IS A LINE SUBJECT, NOT A BUILDING (settlement-review on Kashikawa,
            # 2026-08-17). This used `label_tilt`, which FOLDS mod 90 because a building has two
            # real edge families - and a kosatsuba has ONE meaningful axis, its FACE, the other
            # being its 5 ft depth. The fold is invisible while a board stands nearly square to the
            # page and catastrophic when it does not: a re-pack moved this board onto a lane
            # crossing the old one, its rot went 139.3 -> 49.3, and `label_tilt` returned -40.7 both
            # times - so the caption ran at right angles to the board's face and PARALLEL TO THE
            # OTHER LANE, reading as though it named that way instead. `linear_tilt` clamps rather
            # than folds and goes level past 45 degrees, which is the rule this file's own labels.md
            # docstring states for a line subject ("swapping them" is named there as the trap).
            _t = linear_tilt(rot)
            # THE BOX THE RECORD WILL CARRY, for the HUG and the FABRIC probes too (feature 157, after a
            # settlement-review). `_box_clearance` was taught this in feature 137 - *"THE BOX THE RECORD
            # WILL CARRY, not a one-line guess"* - and `_hug` and `_blocked` were left on the guess:
            # `len * 8 * 0.28` = 26.88 against the recorded 26.40, and a half-height of 5.0 against the
            # recorded 4.20, so the probe box was 19% taller and a hair wider than anything drawn or
            # measured. It cost real centrality the moment the fabric families were widened below - the
            # inflated box just touched a woodpile at the seat directly under the board, so the search
            # walked out to 12 px of lateral for a collision no drawn glyph makes. Placement and its
            # check read ONE geometry: `label_caption_hw` is the expression `_record_label` writes and
            # `label_hugs_its_referent` measures.
            _chw = self.label_caption_hw(label, 8.0)
            _chh = 8.0 * 1.05 / 2.0  # the ONE-LINE recorded box's half-height; see `_cap_quad` on why the probes are not wrap-aware
            # FOUR DIRECTIONS, WALKED OUTWARD - and the outward part is what these boards need. Note
            # which boards arrive here: `linear_tilt` CLAMPS past 45 degrees, so a board at rot 51.6
            # returns tilt 0.0 and takes THIS branch, not the tilted one. All five seeds that gate
            # 0617 catches are in that group, which is why work on the tilted ladder never touched
            # them (I recorded them as "tilted" from their rot and had to correct it - rot is not
            # tilt past the clamp).
            #
            # Four seats at one fixed distance cannot clear a board standing in a lane crotch, and
            # measured on those seeds the BEST achievable clearance over a wide search is 36-51 ft:
            # good ground exists, the search simply was not reaching it. Six distances out to 60 px,
            # the way `clear_label_seat` rings outward for verge-hugging features - and for the same
            # stated reason, that such a feature sits at the busiest node so its surroundings are the
            # most crowded on the map. The default seat is first, so an unblocked board does not move.
            # DENSE ANNULUS, NOT FOUR RAYS. The four axis-aligned rays below are kept exactly as they
            # were - the FIRST entry is still the historical default seat, so an unblocked board does
            # not move - but four rays cannot serve two constraints at once. Measured: with `ref=` now
            # binding `label_hugs_its_referent` to this family, the 24 px hug cap admits only the first
            # rung or two of each ray, i.e. ~8 legal seats on 4 axes, and a board in a lane crotch can
            # have every one of them on a tread. That collision cost 43/48 -> 39/48 (caption-on-tread
            # back on seeds 1, 7, 14; a new hug failure on seed 46).
            #
            # The answer is not to relax either rule - both are right - but to give the lane score real
            # choice among seats that ALL hug. So: twelve bearings at 30-degree steps, at four short
            # standoffs, offset from the board's own half-extents so the caption box clears the glyph.
            # The diagonals are the point: they sample ground the four axes cannot reach while staying
            # well inside the cap, which is exactly the annulus a hugging caption is allowed to use.
            import math as _m

            _cands = [(x, y + hh + 11 + _d) for _d in (0, 12, 24, 36, 48, 60)]
            _cands += [(x, y - hh - 11 - _d) for _d in (0, 12, 24, 36, 48, 60)]
            _cands += [(x + hw + _chw + 8 + _d, y) for _d in (0, 12, 24, 36, 48, 60)]
            _cands += [(x - hw - _chw - 8 - _d, y) for _d in (0, 12, 24, 36, 48, 60)]
            # the diagonals, inside the cap (skipping the four bearings the rays above already cover)
            _cands += [(x + (hw + _chw + 8 + _d) * _m.cos(_m.radians(_a)), y + (hh + 11 + _d) * _m.sin(_m.radians(_a))) for _a in (30, 60, 120, 150, 210, 240, 300, 330) for _d in (0, 8, 16)]

            def _box_clearance(_q: Pt, _chw: float = _chw) -> float:  # noqa: D401 - see caption_lane_clearance
                """Least distance from the caption's BOX to any drawn way's edge (negative = on it)."""
                # READS THE LANE'S EDGE, THE SAME QUANTITY `captions_clear_the_ways_they_stand_on`
                # READS - and it did not, for four attempts. `street_runs` returns polylines with no
                # widths, so this scored distance to the CENTERLINE while the gate scores to the
                # tread EDGE: optimistic by half a lane width, ~2.5-3 px. Every seat the search called
                # best was chosen against a measure the rule does not use, which is why extending the
                # ladder, sliding laterally, walking outward and going 2D all changed nothing on the
                # five failing seeds. The placer and its check must read one source; that is the
                # oldest rule in this engine's CLAUDE.md and I broke it in code written to enforce it.
                _best = 1e9
                # THE BOX THE RECORD WILL CARRY, not a one-line guess (feature 137, tripwire seed 33 and
                # cohort seed 03): "notice board" WRAPS to two lines at 8 pt, so the recorded box is 26
                # by 18, centered 2.2 px above the anchor - while this probe scored a 54 by 10 box on
                # the anchor and called 0.2 px of overlap a 2 ft clearance. Same lines, same arithmetic
                # as `label()` / `_record_label`, so what the seat search scores is what gate 0617 reads.
                _lines = self._caption_lines(label, _q[0], _q[1], 8.0, "middle", _t)
                _n, _lh = len(_lines), 8.0 * 1.15
                _bw = max(len(_ln) for _ln in _lines) * 8.0 * 0.55 / 2.0
                _bh = (8.0 * 1.05 + (_n - 1) * _lh) / 2.0
                _cy = _q[1] - 8.0 * 0.275
                _box = ((_q[0] - _bw, _cy - _bh), (_q[0] + _bw, _cy - _bh), (_q[0] - _bw, _cy + _bh), (_q[0] + _bw, _cy + _bh), (_q[0], _cy))
                for _lane in self.M.get("lanes") or []:
                    _pts = _lane.get("pts") or []
                    _lhalf = float(_lane.get("w") or 3) / 2.0
                    for _i in range(len(_pts) - 1):
                        for _cx, _cy in _box:
                            _best = min(_best, seg_dist(_cx, _cy, _pts[_i], _pts[_i + 1]) - _lhalf)
                # ...AND THE WELLHEAD, which this measured against nothing at all until a review found
                # the caption drawn ON one (Mizuguchi, 2026-08-24: "notice board" overlapping well #1
                # by 14.5 x 8.4 ft, its white halo biting a notch out of the blue disc). The objective
                # was written for lanes because a board stands on a verge, and the verge is exactly
                # where a village well also stands - the two features are drawn to the same node by the
                # same reasoning, so scoring one and not the other was never going to hold.
                #
                # It is a real problem rather than a cosmetic one: the board is a 12x5 ft bar that
                # reads only by its caption, so a caption sitting on the loudest glyph nearby NAMES
                # THE WRONG FEATURE. A reader sees the words over the well.
                for _wl in self.M.get("wells") or []:
                    _wr = float(_wl.get("vr") or _wl.get("r") or 0.0)
                    _wx, _wy = float(_wl["x"]), float(_wl["y"])
                    for _cx, _cy in _box:
                        _best = min(_best, math.hypot(_cx - _wx, _cy - _wy) - _wr)
                return _best

            # SATISFICE, DO NOT MAXIMIZE - the defect that shipped the first version of this search
            # (settlement-review, Inashiro, 2026-08-20). `max(..., key=_box_clearance)` has no cap and
            # no hug term, and clearance rises monotonically along the outward ladder, so the LAST rung
            # always won. Enumerated on Inashiro: the chosen seat bought 30.4 ft of lane clearance at
            # 60 px of drift with a copse clump through the text, while the d=0 seat offered 19.3 ft
            # clear at 8 px from the board and crossed nothing. Gate 0617 asks for 2 ft. The search did
            # not fail to find good ground - it found it, scored it, and threw it away, which is the
            # same shape as the `label_above` bug it was written to replace.
            #
            # So: take every seat that CLEARS the bar, then among those take the one NEAREST the board.
            # Clearance is a constraint to be met, not a quantity to be maximized; distance to the
            # subject is the thing actually worth minimizing, because that is what makes a caption read
            # as belonging to its feature. Only when nothing clears the bar does the best-available seat
            # win, which is the old behavior and the right fallback.
            #
            # WHY 3 FT, AND WHY NOT 5. Gate 0617 requires 2 ft against the tread edge; this keeps 1 ft
            # of margin and no more. It was 5 ft first, on a headroom argument made without looking at
            # what seats a real board is actually offered, and that number REJECTED GATE-LEGAL SEATS:
            # instrumented on cohort seed 14, the two best seats available sit at hug 0.0 with 4.8 and
            # 3.3 ft of clearance - both fine by the rule - and a 5 ft target threw both away and fell
            # through to the fallback. A satisficing bar set above what the ground offers is just a
            # maximizer with extra steps.
            _lane_target = self.px(CAPTION_LANE_TARGET_FT)

            # THE HUG CAP BOUNDS THE SEARCH, IT DOES NOT MERELY JUDGE IT AFTERWARDS. Satisficing on
            # clearance alone still shipped Sawada adrift at 5.0x font: no seat there clears the lane
            # target, so the fallback took the globally-best clearance and walked straight past
            # `label_hugs_its_referent`. That is the SAME unbounded-maximize flaw one level down - a
            # seat outside the cap is a gate failure whatever its clearance, so it is not a candidate
            # at all. Ordering the two rules this way makes them cooperate: hug is the CONSTRAINT,
            # lane clearance the OBJECTIVE inside it, nearness the tie-break when the objective is met.
            _hug_cap = LABEL_AIR_CAP * 8.0  # 8 pt caption; segment 262's own lab_size for this family
            _board_box = (x - hw, y - hh, x + hw, y + hh)
            _board_quad: Poly = [(x - hw, y - hh), (x + hw, y - hh), (x + hw, y + hh), (x - hw, y + hh)]

            def _cap_quad(_q: Pt) -> Poly:
                """The quad `label()` will DRAW at this seat - ONE body for all three probes below.

                REGISTRATION, which is the half the first fix missed (settlement-review round 2). The
                recorded box is `(x0, y - size*0.8, x0 + w, y + size*0.25)`, so its CENTER sits
                `size*0.275` = 2.2 px ABOVE the seat, and the glyph run rotates about that center. The
                probes built their box centered ON the seat, so the whole quad sat 2.2 px low and
                pivoted 2.2 px off - measured on Kuwabata's shipped seat, `_hug` returned 6.292 px
                where `label_hugs_its_referent` reads 4.351, a 1.94 px disagreement between the placer
                and its own check. The sign flips with the side: conservative below, ANTI-conservative
                above, against a cap that is a hard gate.

                WRAP-AWARENESS IS DELIBERATELY NOT HERE, and this is the exception being taken with its
                measurement (Principle XIV). `_box_clearance` below rebuilds the block from
                `_caption_lines`, which is correct and costs it one blocker-list build per call;
                `_caption_lines` calls `label_blocker_quads()` internally, which walks the whole
                manifest. `_hug` is the FIRST predicate on a ladder of ~1,300 seats, so making it
                wrap-aware turns a board with no good ground into ~1,300 whole-manifest walks inside
                one stage. The one-line box is the right approximation until `_caption_lines` takes a
                pre-built blocker list (a one-line signature change with a default, sketched here so
                the next session does not have to re-derive it); the error it leaves is a two-line
                caption probed as one line - wider than drawn, and shorter by one line pitch."""
                _bw, _bh = _chw, _chh
                _cy = _q[1] - 8.0 * 0.275  # the recorded box's center, NOT the seat
                _ca3, _sa3 = math.cos(math.radians(_t)), math.sin(math.radians(_t))
                return [(_q[0] + _dx * _ca3 - _dy * _sa3, _cy + _dx * _sa3 + _dy * _ca3) for _dx, _dy in ((-_bw, -_bh), (_bw, -_bh), (_bw, _bh), (-_bw, _bh))]

            # EVERY BLOCKER THE ENGINE KNOWS ABOUT, DERIVED (settlement-review round 2). The list was
            # nine hand-written family names, then thirteen - and thirteen is still only the families a
            # HAMLET happens to draw. Measured over the pool, ~35 solid built families were invisible to
            # it, `buildings` among them (29 manifests), which is the commonest thing on a town or city
            # sheet: Hirameki's board caption comes to rest **0.66 px** from a `buildings/merchant` the
            # probe cannot see. That matters more after this feature than before it, because the second
            # pass took `label_seat_clear` off the dense ladder in both branches - so on the primary
            # ladder this is the ONLY structure test there is, and no gate check backs it up.
            #
            # `label_blocker_quads` is the DERIVED roster, built for exactly this failure ("a probe that
            # cannot see a feature looks exactly like a probe that passes"), and it already excludes
            # ground (`LABEL_GROUND_KEYS`) and returns true rotated quads. Two additions it structurally
            # cannot make: a RADIUS feature (a wellhead, a persimmon) carries `r`, not `w`/`h`, so those
            # stay explicit; and the captions already drawn in this phase, which the demoted
            # `label_seat_clear` used to be what saw.
            _fabric: list[Poly] = self.label_blocker_quads("kosatsuba")
            _fabric += [
                [
                    (float(_o["x"]) - float(_o.get("vr") or _o.get("r") or 0), float(_o["y"]) - float(_o.get("vr") or _o.get("r") or 0)),
                    (float(_o["x"]) + float(_o.get("vr") or _o.get("r") or 0), float(_o["y"]) - float(_o.get("vr") or _o.get("r") or 0)),
                    (float(_o["x"]) + float(_o.get("vr") or _o.get("r") or 0), float(_o["y"]) + float(_o.get("vr") or _o.get("r") or 0)),
                    (float(_o["x"]) - float(_o.get("vr") or _o.get("r") or 0), float(_o["y"]) + float(_o.get("vr") or _o.get("r") or 0)),
                ]
                for _fam in ("wells", "persimmons")
                for _o in (self.M.get(_fam) or [])
                if isinstance(_o, dict) and (_o.get("vr") or _o.get("r"))
            ]
            _fabric += [label_quad(_lb) for _lb in self.M["labels"] if len(_lb) > 3]

            def _hug(_q: Pt) -> float:
                # MEASURED THE WAY SEGMENT 262 MEASURES IT, which for a TILTED caption is the rotated
                # QUAD and not an axis-aligned box. Getting this wrong cost cohort seed 46 a
                # `label_hugs_its_referent` failure: at a -37 degree tilt the axis-aligned box
                # overstates the gap badly, so every seat looked illegal, the legal pool came out
                # empty, and the fallback took a distant seat that then failed the real check. The
                # placer and its check must read ONE measure - this engine's oldest rule, and the
                # second time I have broken it inside this one function.
                return poly_gap(_cap_quad(_q), _board_quad)

            def _blocked(_q: Pt) -> bool:
                """Does this seat lap a solid feature, or sit across a way from the board it names?

                THE VICTIM ROSTER IS DERIVED, NOT LISTED (settlement-review round 2 - see `_fabric`
                above for the census and the 0.66 px instance on Hirameki). This walked nine
                hand-written family names, then thirteen, and thirteen was still only what a HAMLET
                draws; `label_blocker_quads` is the roster built for exactly that failure.

                THE QUAD DECIDES, THE BOX ONLY PRUNES - this engine's rule for a slow test ("when a
                check is slow, INDEX it - do not coarsen it"). The first version built the caption's
                true quad and then threw it away for `min/max` of its corners, and for a tilted caption
                that box is enormous: at -28.1 degrees a 53.8 x 10 px caption boxes to 52 x 34, more
                than TRIPLING its thickness. That is what refused the seat directly below Kuwabata's
                board - whose true quad clears the nearest structure by 4.43 px - and drove the caption
                35.6 px along its own baseline to the far side of the board, which is the drift the GM
                reported. The same error is written up twice within a hundred lines of here.

                AN EARLIER DRAFT OF THIS COMMENT JUSTIFIED THE OBSTACLE GEOMETRY BY
                `labels_clear_of_other_buildings`, AND THAT CHECK DOES NOT EXIST - deleted in b709c4ae
                (feature 141, "the GM's cut"). NOTHING in the gate measures a caption against a building
                any more, so this probe is the only thing standing between a caption and a roof. The
                restore-or-retire decision, with its census, is in `future-work/cross-cutting.md`."""
                _quad = _cap_quad(_q)
                _qx0, _qx1 = min(_c[0] for _c in _quad), max(_c[0] for _c in _quad)
                _qy0, _qy1 = min(_c[1] for _c in _quad), max(_c[1] for _c in _quad)
                for _o in _fabric:
                    _ox0, _ox1 = min(_c[0] for _c in _o), max(_c[0] for _c in _o)
                    _oy0, _oy1 = min(_c[1] for _c in _o), max(_c[1] for _c in _o)
                    if _qx1 < _ox0 or _ox1 < _qx0 or _qy1 < _oy0 or _oy1 < _qy0:
                        continue  # the prefilter: the caption's quad cannot possibly reach this one
                    if poly_gap(_quad, _o) <= 0.0:
                        return True
                # ...AND NOT ACROSS A WAY FROM ITS SUBJECT: if the straight line from the board to the
                # caption crosses a drawn lane, the reader has a way between the words and the thing.
                for _ln in self.M.get("lanes") or []:
                    _pp = [(float(_a), float(_b)) for _a, _b in (_ln.get("pts") or [])]
                    for _u, _v in zip(_pp, _pp[1:], strict=False):
                        if segments_cross((x, y), (_q[0], _q[1]), _u, _v):
                            return True
                return False

            def _pick(_seats: list[Pt]) -> Pt:
                return pick_caption_seat(_seats, (x, y), _hug, _hug_cap, _box_clearance, _lane_target, _blocked)

            # ONE LADDER, BOTH BRANCHES (feature 157, second pass). The dense ranked ladder was built
            # inside the tilted branch and the LEVEL branch kept its own coarse candidate set - four
            # axis rays at six distances plus eight diagonals at three - and that is where the six
            # cohort seeds the new check caught actually live. A board FACES its lane
            # (`kosatsuba_faces_the_road`), so a lane running square to the page gives rot 0/90/180/270,
            # `aligned_tilt` returns 0, the board takes the LEVEL path, and that path's side rays sit at
            # `hw + _chw + 8 + d` - 40.9 to 100.9 px of pure lateral. After `pull_caption_toward` closes
            # half the air those land at exactly the 28.3 / 32.3 / 36.3 px the cohort reported. The
            # tilted branch was fixed and the level branch was left with the same defect, which is the
            # GM's own reason for caring about this code: *"the code that we write to apply labels will
            # be generally reused for other map features on other types of settlements."*
            #
            # `tilt_caption_seat` at tilt 0 IS the level geometry - and truer than the hand-written rays
            # it replaces, which always offset by the board's half-DEPTH even for a rot=90 board standing
            # on its end, where the half-WIDTH is the perpendicular extent.
            # ...AND ONLY WHEN IT WILL BE WALKED (settlement-review round 2). The ladder is ~1,300
            # `tilt_caption_seat` calls plus a sort, and a caller that HAND-SEATS its caption
            # (`label_xy`, which Nagahara does) walks none of them. Declared empty first so the
            # checker can see it bound on every path - a hand seat never reaches the readers below.
            _ranked: list[tuple[tuple[float, float, int], Pt]] = []
            if not label_xy:
                _lat_reach = _chw + hw + 6
                _lats = [0.0]
                for _i in range(1, int(_lat_reach // 3.0) + 1):
                    _lats += [_i * 3.0, -_i * 3.0]
                if _lat_reach - (_lat_reach // 3.0) * 3.0 > 0.5:  # ...and the reach itself, exactly
                    _lats += [_lat_reach, -_lat_reach]
                _ranked = sorted(
                    ((abs(_lat), _g, _si), tilt_caption_seat(x, y, rot, _t, hw, hh, _g, above=_ab, lateral=_lat))
                    for _lat in _lats
                    for _g in [11.0 + _r for _r in range(26)]
                    for _ab, _si in ((False, 0), (True, 1))
                )
            if label_xy:
                _lx, _ly = label_xy
            elif _t:
                # A TILTED BOARD PUSHES ITS CAPTION FURTHER OFF, because that is the ONE axis that can
                # move it (2026-08-19, third attempt and the first that works). Two levers were tried
                # and measured as EXACT no-ops first, and the reason is worth keeping:
                #
                #   - flipping `above` moves the caption by the board's own 5 ft depth. Not enough.
                #   - sliding LATERALLY along the baseline cannot help AT ALL: `kosatsuba_faces_the_road`
                #     requires the board to FACE its road, so its baseline is PARALLEL to the lane by
                #     rule, and sliding along a parallel line holds the perpendicular distance exactly
                #     constant. Geometrically incapable, not merely mistuned.
                #
                # `gap` is perpendicular to that baseline, so it is the axis that points AWAY from the
                # lane. The ladder stops well inside `LABEL_AIR_CAP` (3 x font size = 24 px at 8 pt),
                # which is what `label_hugs_its_referent` allows before it calls a caption adrift - so a
                # board can buy clearance without losing its subject.
                # THE LADDER MUST REACH PAST THE DIP. Clearance is NOT monotonic in `gap`, because a
                # board sited at the traffic optimum has ways on more than one side - moving away from
                # one lane walks toward another. Enumerated on Kashikawa (12 lanes, board in the lane
                # crotch): 2.0, -1.0, 1.0, -0.3, 7.7 ft at gaps 11/16/21/28/36. A ladder that stopped at
                # 21 took the first rung and left the caption on the tread; the good pocket is at 36.
                # Hug there is 38.5 px. THE PARENTHETICAL THAT USED TO SIT HERE WAS FALSE IN BOTH
                # HALVES - it said inashiro and mizuguchi "sit at 41.0 and pass
                # `label_hugs_its_referent`". They sat at 68.5, and they did not pass it: the check
                # SKIPS any record whose element [6] is null, and no kosatsuba caption carried a
                # referent until `ref=` was added below. An unmeasured number quoted as a passing
                # measurement - exactly what a standing comment must never do.
                _tilted = [
                    tilt_caption_seat(x, y, rot, _t, hw, hh, _g, above=_ab, lateral=_lat) for _ab in (False, True) for _g in (11, 16, 21, 28, 36) for _lat in (0.0, _chw + hw + 6, -(_chw + hw + 6))
                ]
                # A CAPTION STANDS BESIDE ITS BOARD, NOT PAST THE END OF IT (feature 157, GM
                # 2026-08-29: *"rather than being directly below the notice board, it's off to the
                # right a bit ... there is plenty of empty space to put the label directly next to the
                # notice board"*). Two things were wrong with the thirty seats above, and they compound.
                #
                # FIRST, THE LADDER IS TOO COARSE TO FIND THE GOOD GROUND. Five standoffs and three
                # lateral offsets. Measured on Kuwabata: at lateral 0 the board's south side is legal
                # at a standoff of 14 and at NO other sampled value - 11 misses the lane target by
                # 1.1 ft and 16 and beyond genuinely clip a house - so the ladder steps straight over
                # the one seat the GM is asking for. A dense re-scan of the same ground under the same
                # rules finds 97 legal seats. This is the identical failure the LEVEL branch below
                # already fixed once and recorded as "DENSE ANNULUS, NOT FOUR RAYS ... four rays cannot
                # serve two constraints at once"; the fix was never carried across to this branch.
                #
                # SECOND, THE THREE LATERAL OFFSETS ARE DERIVED FROM THE CAPTION, NOT FROM THE SUBJECT:
                # `_chw + hw + 6` is 38.88 px of slide along a 12 px plank. Sliding a caption along its
                # subject is a real convention - `_best_label_spot` does it, and a river's name lies
                # along the river - but there the slides are FRACTIONS OF THE SUBJECT (`span * 0.25`,
                # `span * 0.4`). A 39 px slide along a 12 px board is not "along the subject", it is
                # "away from it", and it is what the GM saw.
                #
                # THE FIX IS THE ORDER OF THE SEARCH, not a new constraint. The reach is KEPT - it is
                # load-bearing, and the note below records why: a board in a lane crotch has no legal
                # seat on the perpendicular line at all, and five cohort seeds are in that position.
                # What changes is that the ground is sampled finely and walked in the order the GM
                # described: least displacement ALONG the caption's own baseline first, then the
                # smallest standoff across it, then below before above. The FIRST fully legal seat in
                # that order wins - so a board with clear ground beneath it gets the caption directly
                # beneath it, and a board in a crotch still reaches the far seats it needs.
                #
                # Straight-line distance, which is what ranked these seats before, cannot tell a 39 px
                # slide from a 39 px standoff; it scores them identically, and only one of the two
                # still reads as "beside".
                # EVALUATED LAZILY, CHEAPEST TEST FIRST, and stopped at the first legal seat: the rank
                # IS the preference, so there is nothing to gain by scoring the rest. That is what keeps
                # a ladder of 1,300 seats cheaper than the 30-seat one it replaces on any board that has
                # somewhere good to put its caption - Kuwabata settles on the sixth.
                # `label_above` NARROWS THE LADDER, it does not name a seat (settlement-review round 2).
                # This branch took a fixed coarse seat - above, gap 11, lateral 0 - judged by none of the
                # three terms, while the level branch honored the same flag by filtering its candidates.
                # The argument against the fixed form is already written twenty lines below, about the
                # level branch: *"Taking a fixed seat on it skipped the lane search entirely ... The good
                # seat was found and then discarded."* It applies verbatim here. Latent rather than live -
                # no pool gen passes `label_above` to `kosatsuba()` - but the two branches now honor the
                # caller's constraint the same way.
                _tld = [_q for _, _q in _ranked if not label_above or _q[1] < y]
                _seat = next((_q for _q in _tld if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _lane_target), None)
                if _seat is not None:
                    _lx, _ly = _seat
                else:
                    # NOTHING CLEARS THE 3 FT TARGET ANYWHERE. Give up the MARGIN before giving up the
                    # board (feature 157, measured on the cohort). The target is 3 ft and gate 0617
                    # requires 2 - one foot of headroom, deliberately - so a board with nowhere good
                    # surrenders that foot rather than surrendering its caption's position: the same
                    # dense ladder, the same order, the same hug and fabric rules, judged against the
                    # rule's own floor instead of against the margin above it.
                    #
                    # WHY THIS RUNG EXISTS AT ALL. Without it the fallback below is `pick_caption_seat`'s
                    # `max(..., key=box_clearance)` - an UNBOUNDED MAXIMIZE with no lateral term, which is
                    # the third recorded instance of that flaw in this one function (see the SATISFICE
                    # note above, and the HUG CAP note below it). Measured across 48 cohort seeds: six
                    # boards took it, and every one landed at the coarse ladder's own +/-38.9 px lateral -
                    # 12.4, 17.7, 28.3, 28.4, 32.3 and 36.3 px along their own baselines, against bounds
                    # of 10.7-11.3. They are the GM's Kuwabata defect, reproduced by the fallback on maps
                    # nobody had looked at.
                    _floor = self.px(CAPTION_LANE_FLOOR_FT)
                    _seat = next((_q for _q in _tld if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _floor), None)
                    if _seat is not None:
                        _lx, _ly = _seat
                    else:
                        # ...and if even the floor is unreachable, exactly the old thirty-seat search, so
                        # a board with genuinely nowhere to put its caption behaves as it always has.
                        _lx, _ly = _pick(_tilted)
            else:
                # THE HALO MUST NOT NOTCH THE WAY THE BOARD STANDS ON (settlement-review on Inashiro,
                # 2026-08-19). The caption is drawn with a 3 px background halo
                # (`paint-order="stroke"`), and a kosatsuba is sited ON a verge by construction - so
                # the below-seat lands on the lane about as often as not. Measured: the board at
                # (1224,1009) with `lanes[1]` passing x~1235 at w=5, and the halo knocked a visible
                # notch out of the map's busiest internal lane, between the words "notice" and
                # "board". That is the founding-run "caption pierced by its own feature" defect
                # inverted - here the caption does the piercing.
                #
                # So the side is CHOSEN rather than fixed: whichever of the two bands sits further
                # from any drawn way. `label_above=True` stays an unconditional override, because its
                # callers set it for a reason the geometry cannot see (a board just inside a gate,
                # whose below-label would hang over the gate structure).
                # CANDIDATE SEATS, SCORED ON THE CAPTION'S OWN BOX. Choosing between above and below
                # was the first cut and it is not enough: it cannot help where BOTH bands sit on a way,
                # which is Mizuguchi (caption box overlapping the tread by 1.9 ft even after picking the
                # better side). So the lateral seats are candidates too, and the score is the clearance
                # of the whole TEXT BOX rather than of its anchor point - the halo is what notches the
                # lane, and the halo follows the box.
                #
                # Half-width is estimated from the string rather than measured, because the seat has to
                # be chosen BEFORE `self.label` lays the text out. 8 pt italic runs ~0.28 em per
                # character: "notice board" estimates 26.9 px against a measured 26.4 on the shipped
                # sheet, which is close enough to rank seats by.
                # ONE SEARCH, BOTH CONSTRAINTS. A caption must clear STRUCTURES and WAYS, and honoring
                # them in separate places is what left two cohort seeds notched. `label_above` is a
                # two-seat STRUCTURE verdict from the caller (`label_seat_clear` on below, then above);
                # it knows nothing about lanes. Taking a fixed seat on it skipped the lane search
                # entirely - instrumented on seed 14, three of the twenty-four candidates clear the
                # structures and the best of those has 7.8 ft of lane clearance, while the seat the
                # flag forced had -1.2 ft. The good seat was found and then discarded.
                #
                # So every candidate is filtered by the engine's own structure probe and scored on lane
                # clearance. That subsumes the flag - the structural question is asked directly of every
                # seat instead of being inherited as a verdict about two of them - and the flag is kept
                # only for the case where nothing clears the structures at all, where its answer is the
                # best information available.
                _boxes = self.label_blockers("kosatsuba")
                _tw_lab = self.label_caption_hw(label, 8.0)
                # `label_above` stays a HARD constraint when a caller sets it: it is that caller's
                # knowledge, not a hint, and `test_kosatsuba_records_a_blocking_struct` pins it. It
                # narrows the pool rather than naming a point, so the lane score still chooses within
                # the allowed side.
                _pool = [_q for _q in _cands if _q[1] < y] if label_above else _cands
                # ...PROBED AT THE CAPTION'S OWN TILT (feature 150, settlement-review of Kuwabata): the seat
                # search cleared the UNROTATED box while the caption is drawn tilted along its lane, so a
                # -32 degree caption's far end reached a threshing yard the level box had cleared.
                # `label_seat_clear` already knows how to probe the rotated AABB; it was not being asked.
                _ok = [_q for _q in _pool if self.label_seat_clear(_q[0], _q[1], _tw_lab, 8.0, _boxes, tilt=_t)]
                # ONE RULE FOR BOTH BRANCHES, and the PRECISE predicates decide it (feature 157, second
                # pass). The dense ladder is walked in the same order the tilted branch uses - least
                # displacement ALONG the caption's baseline, then the smallest standoff, then below
                # before above - and judged by the same three terms: the hug cap, the fabric test, and
                # `_box_clearance` against the lane target.
                #
                # `label_seat_clear` is deliberately NOT the gate on this ladder, and that is the
                # measured half of this change. Its lane test is a CENTER-DISTANCE test with the
                # caption's whole half-diagonal as the radius - `w/2 + 3 + 2 + max(box)/2`, about 32 px
                # for "notice board" - so it refuses every seat within ~32 px of any tread. A kosatsuba
                # stands 6 ft off its own lane BY RULE (`kosatsuba_by_the_road`), so that radius refuses
                # the entire pocket beside the board and the search fell straight through to the coarse
                # set below: gating the dense ladder on it took the cohort's caption failures from 6 to
                # 7 rather than down. `_box_clearance` measures the recorded box's corners against the
                # tread EDGE - the quantity `captions_clear_the_ways_they_stand_on` itself measures - so
                # it is both stricter where it matters and honest about the ground a caption may use.
                # It stays the filter on the coarse fallback below, where it always was.
                _lvl = [_q for _, _q in _ranked if not label_above or _q[1] < y]
                _seat = next((_q for _q in _lvl if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _lane_target), None)
                if _seat is None:  # the same rung the tilted branch takes: give up the MARGIN, never the 2 ft the rule asks
                    _floor = self.px(CAPTION_LANE_FLOOR_FT)
                    _seat = next((_q for _q in _lvl if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _floor), None)
                if _seat is not None:
                    _lx, _ly = _seat
                elif _ok:
                    _lx, _ly = _pick(_ok)
                else:
                    _lx, _ly = (x, y - hh - 11) if label_above else (x, y + hh + 11)
            # OUTSIDE the branch chain - all three seats (hand, tilted, chosen) draw their caption here.
            # It sat one level deeper for one revision and a TILTED board silently lost its label
            # entirely: Kashikawa's rot=145.7 takes the `elif _t` branch, never reached the call, and
            # shipped a 12 x 5 ft glyph that nothing on the sheet identifies. Caught only because the
            # clearance probe returned its "no caption found" sentinel instead of a distance - a
            # measurement that could not tell "infinitely clear" from "not there".
            # `ref=` IS WHAT PUTS THIS CAPTION FAMILY UNDER `label_hugs_its_referent` AT ALL, and its
            # absence hid a 68.5 px drift on three pool hamlets (settlement-review, Inashiro,
            # 2026-08-20). Segment 262 opens `if len(L) < 7 or not L[6]: continue`, so a record with no
            # referent box is SKIPPED - and every kosatsuba caption ever drawn had element [6] null,
            # because this call never passed one. The rule was not lenient here, it was absent, and a
            # comment a few lines up asserted these maps "pass `label_hugs_its_referent`" when nothing
            # had ever measured them. Textbook "a check that never RUNS looks exactly like a check that
            # passes" (this skill's CLAUDE.md), found by a reviewer rather than by the gate.
            # HALF THE AIR (T40, GM 2026-08-27): the chosen seat stands a full standoff off the board;
            # the caption is then pulled half the remaining gap toward the board's own footprint.
            _bq = [
                (x + dx * _m.cos(_m.radians(rot)) - dy * _m.sin(_m.radians(rot)), y + dx * _m.sin(_m.radians(rot)) + dy * _m.cos(_m.radians(rot)))
                for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))
            ]
            if not label_xy:  # a HAND seat is a decision and is honored exactly; only the derived seat is pulled (T40; the town-tier hand-seat test found the pull moving it 13.9 px, 2026-08-28)
                _lx, _ly = self.pull_caption_toward((_lx, _ly), label, 8, "middle", _t, _bq)
            self.label(_lx, _ly, label, 8, italic=True, color="#7A5A30", rot=_t, ref=(x - hw, y - hh, x + hw, y + hh), cls="notice board")  # the caption shares the board's class (feature 134 FR-006)
