"""The settlement's public street furniture and civic fixtures, and the two auto-siters that place them on the traffic.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.
"""

import math
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import (
    LABEL_AIR_CAP,
    Pt,
    box_gap,
    label_tilt,
    linear_tilt,
    point_in_poly,
    poly_gap,
    seg_dist,
    segments_cross,
    street_runs,
    tilt_caption_seat,
    way_beds,
)
from .._knobs import KOSATSUBA_MARKER_MIN_PX, PUNISHMENT_SPOT_FT, resolve_knob

# The lane clearance a notice-board caption must MEET before nearness decides the seat. See the long
# note beside `_pick` in `kosatsuba` for why this satisfices rather than maximizes, and why 5 ft.
CAPTION_LANE_TARGET_FT = 3.0

# THE RULE'S OWN FLOOR, as opposed to the target above it. `captions_clear_the_ways_they_stand_on`
# (gate 0617) requires 2 ft between a caption's box and a lane's tread edge; the 3 ft target keeps one
# foot of margin over it and no more. A board that can reach the target takes it; a board that cannot
# gives up the margin - never the two feet the rule actually asks for, and never its position beside
# the board it names. Feature 157: the rung between "the good seat" and the old unbounded fallback.
CAPTION_LANE_FLOOR_FT = 2.0

# THE BOARD IS ROADSIDE (GM 2026-08-26, feature 133 T13: *"I would expect it to be essentially
# roadside ... puts it right next to one of the village lanes"*). Real feet from the tread's EDGE to
# the board's near edge. Research (research/urban-features.md): the kosatsu stood where traffic
# passed - the village entrance, the roadside, a crossroads, a bridgehead, the headman's gate - so a
# board 24 ft off its lane (Inashiro before this) is set back from the very thing it is for. The
# placer searched out to 60 ft and ranked caption clearance above nearness, which is how it walked
# out. Now: at the hamlet and village tiers only seats inside this band are eligible when any fits
# (the 60 ft band remains the fallback, and `kosatsuba_by_the_road` tightens to this band at those
# tiers); towns and cities keep the 60 ft rule until their pool maps are re-rolled at unlock.
KOSATSUBA_VERGE_FT = 6.0

if TYPE_CHECKING:
    from ..core import Settlement


def pick_caption_seat(
    seats: Sequence[Pt],
    at: Pt,
    hug: Callable[[Pt], float],
    hug_cap: float,
    box_clearance: Callable[[Pt], float],
    lane_target: float,
    blocked: Callable[[Pt], bool] | None = None,
) -> Pt:
    """The board's caption seat: the NEAREST seat that clears the ways by `lane_target`, and if none does,
    the legal seat that clears them best.

    LIFTED OUT OF `place_kosatsuba` (feature 146, GM 2026-08-28 on inner functions and testability). It took
    two closures and two numbers, all of which a test can hand it directly; reaching it through the placer
    meant building a settlement whose every seat was blocked. The tie-break is (distance, then ORDER), which
    is what keeps an unblocked board on its historical seat when a diagonal ties with it.
    """
    # `blocked` IS A THIRD LEGALITY TERM, and it degrades in the same direction as the other two
    # (feature 152 T12). The filter scored hug and lane clearance and NOTHING ELSE, so a caption could
    # be seated on top of a garden, or with a whole lane between it and the thing it names - Inashiro's
    # "notice board" stood with the full 6 ft width of lane 1 between the caption and its board, and a
    # shrine 22 ft away on the caption's own side, so the words read as naming the shrine. The comment
    # under the satisfice rule already knew the shape ("a copse clump through the text") and chose lane
    # clearance as the only bar anyway. If every seat is blocked the term is dropped rather than the map
    # left captionless, which is the same "or list(seats)" fallback the hug cap has always had.
    _hug_ok = [q for q in seats if hug(q) <= hug_cap] or list(seats)
    legal = _hug_ok
    # `blocked` REFINES AMONG SEATS THAT ALREADY CLEAR THE WAYS - it does not outrank the lane bar
    # (feature 152 T12). Applied as a filter over ALL legal seats it changed which seat the ladder fell
    # back to, and tripwire seed 33 came out with its caption standing on a way
    # (`captions_clear_the_ways_they_stand_on`) - trading the defect this term was written for against a
    # worse one. Lane clearance is the older and harder rule; the fabric and way-side terms pick BETWEEN
    # the seats that already satisfy it, and drop away entirely when none of them is unblocked.
    clear = [q for q in legal if box_clearance(q) >= lane_target]
    _unblocked = [q for q in clear if not (blocked and blocked(q))]
    clear = _unblocked or clear
    if clear:
        ix = {id(q): i for i, q in enumerate(seats)}
        return min(clear, key=lambda q: (round((q[0] - at[0]) ** 2 + (q[1] - at[1]) ** 2, 3), ix[id(q)]))
    # ...AND THE FALLBACK REFINES BY IT TOO (settlement-review x3, feature 154). This returned
    # `max(legal, key=box_clearance)` and never consulted `blocked` at all - so on a board where NO
    # seat reaches the lane target, which is every board standing close beside a way, the whole
    # way-side term was silently skipped and the best-clearing seat won even with the tread between
    # the caption and its own board. Sawada shipped exactly that three passes running: board at -12.0
    # to -7.0 off the connector's axis, tread -3.0 to +3.0, caption +6.0 to +14.5, with the board's
    # own side measurably clear. A rule that cannot fire on the path most boards take looks exactly
    # like a rule that passes.
    #
    # Same degradation as above, deliberately: prefer the unblocked seats, and drop the term entirely
    # when none of them is - never leave the map captionless for it.
    _legal_unblocked = [q for q in legal if not (blocked and blocked(q))]
    return max(_legal_unblocked or legal, key=box_clearance)


KOSATSUBA_ENTRANCE_REACH_FT = 100.0
"""How near a dwelling the approach must come before it counts as having ARRIVED at the settlement.

THE ENTRANCE IS THE FIRST BUILDINGS, NOT A RADIUS (settlement-review, feature 154). The first version
measured arrival against the cluster's own reach - the greatest distance from any house to the house
centroid - which is isotropic, and a settlement is not. On Sawada, a ribbon cluster of drawn aspect
4.06, that radius is set by the ribbon's HALF-LENGTH: 382 ft. The approach crossed that circle 148 ft
from the nearest house, out in the woodland and 3 ft above the top edge of the drawn sheet, so the
board was sited off the page, `stage_notice`'s frame guard threw the seat away, and the map recorded
an `entrance` placement it had not drawn.

100 ft is not a new figure: it is the reach `farmhouses_reach_a_way` uses to decide whether a dwelling
is served by a way at all. Where the approach first comes within serving distance of a house is where
a walker would say the hamlet begins, and it is the same measure the rest of the engine already makes."""

KOSATSUBA_ANCHOR_BAND_FT = 60.0
"""How far from the best seat at an anchored placement another seat may stand and still compete.

Not a new figure: it is `place_kosatsuba`'s own siting band, the ~60 real feet within which a board
counts as belonging to the way it stands on (`kosatsuba_by_the_road`'s fallback tolerance). Reused
here so an anchored placement admits the seats that genuinely front the entrance or the gate, and no
others, and then hands the choice to the caption and roadside preferences that already existed.
Making it TIGHTER would let a caption-blocked seat win on a foot of proximity; making it LOOSER would
let the traffic term drag the board off the anchor, which is the defect this feature exists to fix."""


def kosatsuba_affordances(M: Any) -> dict[str, bool]:
    """Which board placements this map can SITE, read from the manifest the validator reads.

    The same-source doctrine: a guard against a placement asks the question the checks ask. An
    approach is a recorded road or a connector track; an official's gate is a house carrying
    `role == "headman"`, which every pool VILLAGE records exactly once and no hamlet records at all.
    """
    lanes = M.get("lanes") or []
    has_approach = bool(M.get("road") or (M.get("roads") or []) or any(ln.get("connector") for ln in lanes))
    return {
        "has_approach": has_approach,
        "has_headman_house": any(h.get("role") == "headman" for h in (M.get("houses") or [])),
    }


def kosatsuba_anchor(M: Any, placement: str) -> tuple[float, float] | None:
    """The point an anchored placement is measured to, or None when the placement is not anchored.

    `center` returns None ON PURPOSE, and that is the whole reason this function has a null case: the
    settlement center IS the traffic objective - *"the village center ... or the place where villagers
    assembled"* - which `place_kosatsuba` already computes by counting dwellings around each seat, far
    better than a centroid would. Returning the centroid here would replace a measure of where people
    ARE with a measure of where the middle IS, and on a crescent or a ribbon cluster those are not the
    same point. So `center` keeps today's behavior byte for byte, and only the two placements that
    need a landmark get one.

    `entrance` is the MOUTH, not the nearest point: the approach is walked from its far end inward and
    the anchor is where it first reaches the cluster. Taking the nearest point instead would put the
    anchor at the deepest point of the track's run past the houses, i.e. inside the settlement, which
    is the opposite of an entrance.
    """
    houses = [(float(h["x"]), float(h["y"])) for h in (M.get("houses") or []) if "x" in h]
    if not houses or placement == "center":
        return None
    if placement == "frontage":
        gate = next((h for h in (M.get("houses") or []) if h.get("role") == "headman" and "x" in h), None)
        return (float(gate["x"]), float(gate["y"])) if gate else None
    if placement != "entrance":
        return None  # pragma: no cover - the value space holds no other placement

    def _at_the_buildings(q: tuple[float, float]) -> bool:
        """Has the approach arrived? Measured to the nearest DWELLING, never to a centroid radius."""
        return min(math.hypot(q[0] - h[0], q[1] - h[1]) for h in houses) <= KOSATSUBA_ENTRANCE_REACH_FT

    runs: list[list[tuple[float, float]]] = []
    if M.get("road"):
        runs.append([(float(p[0]), float(p[1])) for p in M["road"]])
    runs += [[(float(p[0]), float(p[1])) for p in (r.get("pts") or [])] for r in (M.get("roads") or [])]
    runs += [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or []) if ln.get("connector")]
    best: tuple[float, tuple[float, float]] | None = None
    for run in runs:
        if len(run) < 2:
            continue
        # walk from whichever end is FURTHER out, so "first reach" means arriving rather than leaving
        _far = min(math.hypot(run[0][0] - h[0], run[0][1] - h[1]) for h in houses)
        _near = min(math.hypot(run[-1][0] - h[0], run[-1][1] - h[1]) for h in houses)
        walk = run if _far >= _near else run[::-1]
        # SAMPLED ALONG THE SEGMENTS, NOT AT THE VERTICES. A track is recorded with as few points as
        # its shape needs, so one that runs straight through the cluster can have no vertex inside it
        # at all - the first version of this tested vertices and returned "no entrance" for a
        # two-point track passing right through the houses, caught by its own unit test rather than by
        # a map, because the pool's connectors happen to be densely recorded.
        acc = 0.0
        for u, v in zip(walk, walk[1:], strict=False):
            seg = math.dist(u, v)
            steps = max(1, int(seg / 5.0))
            for k in range(1, steps + 1):
                q = (u[0] + (v[0] - u[0]) * k / steps, u[1] + (v[1] - u[1]) * k / steps)
                if _at_the_buildings(q) and (best is None or acc + seg * k / steps < best[0]):
                    best = (acc + seg * k / steps, q)
                    break
            if best is not None:
                break
            acc += seg
    return best[1] if best else None


class PublicFixturesMixin:
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
            _chw = max(10.0, len(label) * 8 * 0.28)
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

            def _hug(_q: Pt) -> float:
                # MEASURED THE WAY SEGMENT 262 MEASURES IT, which for a TILTED caption is the rotated
                # QUAD and not an axis-aligned box. Getting this wrong cost cohort seed 46 a
                # `label_hugs_its_referent` failure: at a -37 degree tilt the axis-aligned box
                # overstates the gap badly, so every seat looked illegal, the legal pool came out
                # empty, and the fallback took a distant seat that then failed the real check. The
                # placer and its check must read ONE measure - this engine's oldest rule, and the
                # second time I have broken it inside this one function.
                _lb = (_q[0] - _chw, _q[1] - 5.0, _q[0] + _chw, _q[1] + 5.0)
                if not _t:
                    return box_gap(_lb, _board_box)
                _cx, _cy = _q[0], _q[1]
                _ca, _sa = math.cos(math.radians(_t)), math.sin(math.radians(_t))
                _quad = [
                    (_cx + (_px - _cx) * _ca - (_py - _cy) * _sa, _cy + (_px - _cx) * _sa + (_py - _cy) * _ca) for _px, _py in ((_lb[0], _lb[1]), (_lb[2], _lb[1]), (_lb[2], _lb[3]), (_lb[0], _lb[3]))
                ]
                return poly_gap(_quad, [(_board_box[0], _board_box[1]), (_board_box[2], _board_box[1]), (_board_box[2], _board_box[3]), (_board_box[0], _board_box[3])])

            def _blocked(_q: Pt) -> bool:
                """Does this seat lap a solid feature, or sit across a way from the board it names?"""
                _lb = (_q[0] - _chw, _q[1] - 5.0, _q[0] + _chw, _q[1] + 5.0)
                _ca2, _sa2 = math.cos(math.radians(_t)), math.sin(math.radians(_t))
                _quad = [
                    (_q[0] + (_px2 - _q[0]) * _ca2 - (_py2 - _q[1]) * _sa2, _q[1] + (_px2 - _q[0]) * _sa2 + (_py2 - _q[1]) * _ca2)
                    for _px2, _py2 in ((_lb[0], _lb[1]), (_lb[2], _lb[1]), (_lb[2], _lb[3]), (_lb[0], _lb[3]))
                ]
                # THE AABB OF THE ROTATED QUAD IS A PREFILTER, NOT THE VERDICT (feature 157, the GM's
                # reported defect). This built the caption's true quad and then threw it away, deciding
                # on `min/max` of its corners - and for a tilted caption that box is enormous: at
                # -28.1 degrees a 53.8 x 10 px caption boxes to 52 x 34, more than TRIPLING its
                # thickness. Measured on Kuwabata, that is what refused the seat directly below the
                # board, whose true quad clears the nearest structure by 4.43 px, and so drove the
                # caption 35.6 px along its own baseline to the far side of the board - the exact drift
                # the GM saw. The same error is written up twice within a hundred lines of here ("an
                # AABB standoff to a diagonal subject is the caption's own length, not its thickness";
                # "the placer and its check must read one source"), and this call site had it anyway.
                #
                # So the box PRUNES and the QUAD decides - this engine's standing rule for a slow test
                # (skill CLAUDE.md: "when a check is slow, INDEX it - do not coarsen it"). The obstacle
                # keeps the extent the GATE gives it, its rotated corners' AABB, because that is what
                # `labels_clear_of_other_buildings` measures; probing anything tighter would pass here
                # and fail there.
                _qx0, _qx1 = min(_c[0] for _c in _quad), max(_c[0] for _c in _quad)
                _qy0, _qy1 = min(_c[1] for _c in _quad), max(_c[1] for _c in _quad)
                for _fam in ("houses", "gardens", "threshing_yards", "farm_sheds", "byres", "storehouses", "persimmons", "bamboo_stands", "wells"):
                    for _o in self.M.get(_fam) or []:
                        if not isinstance(_o, dict) or "x" not in _o:
                            continue
                        _ow, _oh = float(_o.get("w") or _o.get("r", 0) * 2), float(_o.get("h") or _o.get("r", 0) * 2)
                        if _ow <= 0 or _oh <= 0:
                            continue
                        _orot = float(_o.get("rot") or 0.0)
                        if _orot:  # the gate boxes a rotated victim by its rotated corners' AABB
                            _oc, _os = abs(math.cos(math.radians(_orot))), abs(math.sin(math.radians(_orot)))
                            _ow, _oh = _ow * _oc + _oh * _os, _ow * _os + _oh * _oc
                        _ox, _oy = float(_o["x"]), float(_o["y"])
                        if abs(_q[0] - _ox) >= (_qx1 - _qx0 + _ow) / 2 or abs(_q[1] - _oy) >= (_qy1 - _qy0 + _oh) / 2:
                            continue  # the prefilter: the caption's quad cannot possibly reach this one
                        if poly_gap(_quad, [(_ox - _ow / 2, _oy - _oh / 2), (_ox + _ow / 2, _oy - _oh / 2), (_ox + _ow / 2, _oy + _oh / 2), (_ox - _ow / 2, _oy + _oh / 2)]) <= 0.0:
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
                # EVALUATED LAZILY, CHEAPEST TEST FIRST, and stopped at the first legal seat: the rank
                # IS the preference, so there is nothing to gain by scoring the rest. That is what keeps
                # a ladder of 1,300 seats cheaper than the 30-seat one it replaces on any board that has
                # somewhere good to put its caption - Kuwabata settles on the sixth.
                _seat = next((_q for _, _q in _ranked if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _lane_target), None)
                if label_above:  # a HARD constraint from the caller, unchanged: its seat is named, not searched
                    _lx, _ly = _tilted[15]
                elif _seat is not None:
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
                    _seat = next((_q for _, _q in _ranked if _hug(_q) <= _hug_cap and not _blocked(_q) and _box_clearance(_q) >= _floor), None)
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
                if _ok:
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

    def fixture_clear_of_water(self: Settlement, x: float, y: float, half: float) -> bool:  # type: ignore[misc]
        """Does a point fixture of half-diagonal `half` stand clear of every watercourse?

        THE VERGE PROBES BYPASS THE WATER CLEARANCE, and this buys it back explicitly. A verge-hugging
        fixture must probe with `_fits(..., corridors=False)` - the corridor test is a HOUSE setback
        from the tread, and applying it would refuse every verge there is - but `corridors=False` also
        switches off the watercourse clearance bundled into the same test, so the probe will happily
        seat a board in a stream. Cohort seed 13 did exactly that (`features_do_not_overlap` on
        ('kosatsuba', 'streams') plus `no_structure_on_stream`) once a homestead re-pack changed which
        verges were free: the board sat at (715, 517) on a 7 px stream, INSIDE the house cloud, so the
        hamlet tier's outside-the-cloud re-seat never even looked at it.

        ONE predicate, two callers - `place_kosatsuba` here and `hamletgen.stage_notice`'s re-seat,
        which faces the identical problem for the identical reason. Fixing only the caller that
        happened to fail would have left the other seating boards in water on the next re-roll.

        Reads the DRAWN courses (`drawn_channels`) as well as the recorded ones, because the filleted
        stroke is what a reader sees and what the overlap matrix measures.

        INDEXED (feature 138): `place_kosatsuba` asked this 17,407 times on one polder, each call walking
        all ~720 water segments - 12.5 million `seg_dist`. The segments are filed once in a grid (rebuilt
        when any of the four lists changes length, the same rule `_water_obstacles` uses) with each
        segment's own half-width; a probe measures only its cell's segments. Same predicate, same answer."""
        from l7r.diagram.settlement._geom.water_index import water_index

        return water_index(self).clear(x, y, half)

    def caption_lane_clearance(self: Settlement, qx: float, qy: float, chw: float, size: float = 8.0) -> float:  # type: ignore[misc]
        """Least distance from a caption's BOX to any lane's tread EDGE (negative = standing on it).

        Shared deliberately by the notice board's seat search and by `place_kosatsuba`'s siting
        preference, so the two cannot drift: the siter must rank a board position by the same measure
        the seat search will later optimize, and gate 0617 reads. Every time this quantity has been
        re-derived at a second call site in this file it has come back subtly different - the
        centerline instead of the edge, an axis-aligned box instead of the rotated quad - so it is a
        method now rather than a third closure."""
        # THE WHOLE BOX, NOT FIVE POINTS ON IT. Sampling four corners plus the center is exact against
        # a STRAIGHT tread and quietly wrong against a curved one: a caption spanning a CONCAVE bend
        # can have all five samples clear while the middle of its top or bottom EDGE crosses the arc.
        # Predicted here when the lane skeleton gained curvature, then observed - cohort seed 37 on the
        # architecture session's tree, a caption 2 ft from a tread that this method had scored clear.
        # So the measure is now segment-to-RECTANGLE: zero if the tread enters the box at all, else the
        # least distance between the tread and any of the box's four edges.
        #
        # AND THE BOX IS THE ONE THE TEXT ACTUALLY OCCUPIES. The old +/-5 was symmetric about the
        # ANCHOR, but a caption's record runs from ascent (0.8 x size) ABOVE the anchor to descender
        # (0.25 x size) below - so the old box under-reached the top by 1.4 px and over-reached the
        # bottom by 3. Two different boxes for one caption is how this family of bug keeps arriving.
        _y0, _y1 = qy - 0.80 * size, qy + 0.25 * size
        _x0, _x1 = qx - chw, qx + chw
        _edges = (((_x0, _y0), (_x1, _y0)), ((_x1, _y0), (_x1, _y1)), ((_x1, _y1), (_x0, _y1)), ((_x0, _y1), (_x0, _y0)))
        _best = 1e9
        for _lane in self.M.get("lanes") or []:
            _pts = _lane.get("pts") or []
            _lhalf = float(_lane.get("w") or 3) / 2.0
            for _i in range(len(_pts) - 1):
                _a, _b = _pts[_i], _pts[_i + 1]
                if (_x0 <= _a[0] <= _x1 and _y0 <= _a[1] <= _y1) or (_x0 <= _b[0] <= _x1 and _y0 <= _b[1] <= _y1):
                    return -_lhalf  # the tread's own centerline is inside the caption box
                _d = 1e9
                for _p, _q in _edges:
                    if segments_cross(_a, _b, _p, _q):
                        _d = 0.0
                        break
                    _d = min(_d, seg_dist(_p[0], _p[1], _a, _b), seg_dist(_q[0], _q[1], _a, _b), seg_dist(_a[0], _a[1], _p, _q), seg_dist(_b[0], _b[1], _p, _q))
                _best = min(_best, _d - _lhalf)
        return _best

    def place_kosatsuba(self: Settlement, label: str = "notice board") -> Pt | None:  # type: ignore[misc]
        """AUTO-SITE the settlement kosatsuba on a lane/road verge at the busiest clear node -
        the village/hamlet tiers' procedural sibling of the town/city hand placement (GM
        2026-07-24: EVERY settlement tier carries the board; the ofuregaki circulars reached
        the peasantry through it via the settlement's one required-literate reader - the
        headman, or a hamlet's senior farmer answering to the village headman - and officials
        also read notices aloud, so even a 50-inhabitant hamlet's board works). Deterministic:
        draws NO RNG, so calling it inside `roll_village` cannot perturb a rolled map's seed
        stream. Reads the SAME manifest route fields the validator's siting checks read (the
        dev-loop same-source doctrine): MAIN ways only (`roads`/`M['road']` + `main: True`
        town streets - kosatsuba_on_a_main_way, GM 2026-08-02) when the map declares any,
        else the whole network (`M['lane']` + `M['lanes']` + `town_streets`), and probes
        candidate verge spots with `_fits`, scoring for the most dwellings within ~260 px
        (siting is a TRAFFIC decision - the state talks at everyone who passes) while
        hugging the verge. Call LAST - after the crop, not before it (GM 2026-08-29). This said
        "BEFORE the crop, so the frame contains the board", which inverted the dependency: the
        board is sited against `meta.view` now, so the frame constrains the board rather than the
        board holding the frame open (`crop_not_held_open_by_one_feature`). No-op under meta(kosatsuba=False); returns the spot, or
        None when no verge inside the validator's ~60-real-ft siting band fits (the
        settlement-tier check would then fire - place by hand or widen the lane network)."""
        if not self.M["meta"].get("kosatsuba", True):
            return None
        ftpx = float(self.M["meta"].get("ftpx") or 1)
        lim = 60.0 / ftpx  # kosatsuba_by_the_road: ~60 REAL feet from a route, in px
        # probe with the DRAWN marker box, not the true footprint (village grain floors the glyph
        # to ~11x4.6 px - see kosatsuba): the spot has to hold the pixels that get drawn there
        w = max(self.px(12), KOSATSUBA_MARKER_MIN_PX)
        h = w * 5 / 12
        # (pts, tread width) per route; road/lane manifest fields carry no width, so assume
        # a generous tread for the bed-avoidance test below.
        # MAIN WAYS ONLY, where the map declares any (GM 2026-08-02, from Ubame: the siter put
        # the board a legal 49 ft off a side lane while the high street ran 200 ft away - "it
        # should be along the main road, in order to be more noticed"). The candidate tiers
        # mirror kosatsuba_on_a_main_way exactly (the same-source doctrine): every road and
        # every main: True town street is a MAIN way, and when the map has at least one, ONLY
        # main-way verges are sampled - a side lane's busiest node is still a side lane, so
        # scoring must never see it. A map with no declared hierarchy (village/hamlet lane
        # webs, towns whose streets are all unflagged) falls back to the whole network, where
        # the busiest-node scoring below stands in for "main". The fallback still needs TOWN
        # STREETS TOO: this probe was written for the lane/lanes tiers, and the omission was
        # invisible until Hirameki - no road, no lanes, all town_streets - gave it not one
        # candidate seat and it returned None (GM 2026-07-27).
        routes: list[tuple[list[Pt], float]] = []
        if self.M.get("road"):
            routes.append(([(p[0], p[1]) for p in self.M["road"]], 18.0))
        routes.extend(([(p[0], p[1]) for p in r["pts"]], 18.0) for r in (self.M.get("roads") or [])[1:])
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [] if st.get("main"))
        if not routes:
            # A ROUTE CARRIES ITS OWN WIDTH, AND THIS BLOCK USED TO GIVE THEM ALL THE SAME ONE (feature
            # 134 T50, 2026-08-29). `street_runs` returns EVERY drawn lane, and they were all added at a
            # nominal 8 ft - so the seater measured the tread edge 4 ft from the centerline on a lane
            # that is 3 or 5 ft wide, and placed the board `(8 - w) / 2` too far out while believing it
            # had put it exactly on the verge. Gate seed 44's board landed at 12.5 ft from a 5 ft lane's
            # centerline - which is 6 (the verge) + 4 (half of the imagined 8) + 2.5 (half the board),
            # to the foot - and `kosatsuba_by_the_road` measures against 12.0 and refused it.
            #
            # It also quietly undid the rule the note below states. `_main` exists to keep the state's
            # notice off a SERVICE lane, and this loop had already put every web lane into `routes`
            # before that filter ran, so the filter decided nothing. The per-lane extend below covers
            # exactly the same ways with their real widths, so this is now only the last-ditch case
            # where the manifest has runs but no lane records to read a width from.
            if not (self.M.get("lanes") or []):
                for _st in street_runs(self.M):  # every lane; `M["lane"]` is only the last one drawn
                    routes.append((_st, 8.0))
            # A SERVICE LANE IS NOT A PLACE TO POST THE STATE'S NOTICE. The fallback takes the whole
            # network when no way declares itself main, which a hamlet never does - so when the lane
            # web arrived it put ~1,000 ft of 3 ft footpaths into the candidate list on equal footing
            # with the 5 ft spine, and the board re-seated onto one: a settlement-review measured it
            # 34.9 ft off the spine where it had been 9.0, now facing a way the engine itself calls
            # SERVICE. This function's own docstring already states the rule it was breaking - "a
            # side lane's busiest node is still a side lane, so scoring must never see it" - and
            # `web` is exactly the hierarchy flag the hamlet tier lacked. Web lanes are used only if
            # there is nothing else to stand beside.
            _ways = self.M.get("lanes") or []
            # TRIED AND REVERTED (feature 140, 2026-08-28): admitting every web lane as a route on a hamlet, to let the
            # board reach the frontage. It moved nothing on Inashiro - the frontage has no verge seat that `_fits` a
            # board after the re-seat (4 of 60 probes around the houses fit), so the choice of routes was never the
            # constraint; the room is. Recorded so the lever is not pulled again (`research.md` R6).
            _main = [ln for ln in _ways if not ln.get("web")] or _ways
            routes.extend(([(p[0], p[1]) for p in ln["pts"]], float(ln.get("w", 8))) for ln in _main)
            routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [])
        spots = [(b["x"], b["y"]) for b in self.M["houses"]] + [(b["x"], b["y"]) for b in self.M["buildings"]]

        beds = way_beds(self.M)  # EVERY way bed, not just the routes candidates were sampled from

        def off_every_bed(x: float, y: float) -> bool:
            # the board hugs the verge, so the lane corridor's no-build clearance (a HOUSE
            # setback: homesteads must not crowd the tread) is deliberately bypassed
            # (_fits corridors=False) - but the board must still stand off the TREAD of
            # every route, including ones it was not sampled from (a junction spot offset
            # from lane A can land on lane B, or on a town street or alley this tier's
            # candidate list does not carry at all - see way_beds)
            return all(seg_dist(x, y, bp[k], bp[k + 1]) >= bhw + h / 2 + 3 for bp, bhw in beds for k in range(len(bp) - 1))

        tw_lab = self.label_caption_hw(label, 8.0) if label else 0.0  # the caption half-width the seat must also hold, as RECORDED
        kb_boxes = self.label_blockers("kosatsuba")  # built once: the probe tests many seats against the same map
        _siting = str((self.M.get("meta") or {}).get("kosatsuba_siting") or "frontage")
        _wells = [(float(_w["x"]), float(_w["y"])) for _w in (self.M.get("wells") or []) if "x" in _w]
        cands: list[tuple[int, float, float, float, float, int | None, float]] = []  # (busy, score, x, y, rot, label_above|None, gap from tread edge to board edge)
        for pts, _rw in routes:
            for i in range(len(pts) - 1):
                (ax, ay), (bx, by) = pts[i], pts[i + 1]
                seg = math.hypot(bx - ax, by - ay)
                if not seg:
                    continue
                ux, uy = -(by - ay) / seg, (bx - ax) / seg  # verge normal
                # long axis ALONG the route: the board's face is broadside to the traffic that
                # reads it, never edge-on (kosatsuba_faces_the_road; see kosatsuba's docstring)
                rot = math.degrees(math.atan2(by - ay, bx - ax))
                for t in range(int(seg // 12) + 1):
                    f = t * 12 / seg
                    mx, my = ax + (bx - ax) * f, ay + (by - ay) * f
                    for side in (1.0, -1.0):
                        off = _rw / 2 + h / 2 + 4
                        while off <= lim:
                            x, y = mx + ux * off * side, my + uy * off * side
                            if off_every_bed(x, y) and self.fixture_clear_of_water(x, y, math.hypot(w, h) / 2) and self._fits(x, y, w, h, corridors=False):
                                # BUSY IS WHERE THE FEET ARE (feature 140's Inashiro review, 2026-08-28): counting dwellings within 260 px
                                # could not tell the frontage (11 within 150 ft) from the exit throat (5 within 150 ft) - both had ~16-21
                                # within 260 - and a re-roll sat the board at the throat. The near count is weighted double.
                                busy = sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 260) + 2 * sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 150)
                                # WHERE THE BOARD STANDS IS A KNOB (feature 152 T21, constitution XII).
                                # The takafuda stood at crossroads and bridgeheads AND at the village
                                # well - both attested, so this is two supportable answers rather than one
                                # right one, and picking either permanently throws away a way two hamlets
                                # can honestly differ. `frontage` is the busiest built ground, which is
                                # what this score has always measured. `waterside` is the drawing-water
                                # place: a settlement-review measured Mizuguchi's board at the wellhead,
                                # 7 of 12 households within 250 ft against 11 of 12 at the frontage
                                # optimum, and called it defensible - which it is, on the other answer.
                                if _siting == "waterside" and _wells:
                                    _dw = min(math.hypot(x - wx2, y - wy2) for wx2, wy2 in _wells)
                                    busy += 14 if _dw < 40.0 else (8 if _dw < 90.0 else 0)
                                # THE CAPTION IS PART OF THE SEAT (GM 2026-07-27). The glyph is 11 px
                                # and fits almost anywhere; its caption does not, and the busiest
                                # frontage is exactly where there is least room for one - so a siter
                                # that hunts for ground big enough to hold BOTH walks away from the
                                # traffic and out to the quiet end of the road, which is how Ubame's
                                # board came to stand across the bridge from its own town.
                                lab = 0 if self.label_seat_clear(x, y + h / 2 + 11, tw_lab, 8.0, kb_boxes) else (1 if self.label_seat_clear(x, y - h / 2 - 11, tw_lab, 8.0, kb_boxes) else None)
                                cands.append((busy, busy * 10 - off / 3, x, y, rot, lab, off - _rw / 2 - h / 2))  # last: the gap from tread edge to board edge
                            off += 5.0
        if not cands:
            return None
        # ROADSIDE FIRST (GM 2026-08-26): at the lane tiers, if any seat stands within KOSATSUBA_VERGE_FT
        # of a tread, only those seats compete - the caption and traffic preferences below then choose
        # AMONG roadside seats instead of trading the roadside away for a clearer caption.
        _scale = str((self.M.get("meta") or {}).get("scale") or "")
        if _scale in ("hamlet", "village"):
            roadside = [c for c in cands if c[6] <= KOSATSUBA_VERGE_FT / ftpx + 1e-6]
            if roadside:
                cands = roadside

        # THE PLACEMENT IS A KNOB, NOT ONE OBJECTIVE (feature 154, GM 2026-08-29). The record attests
        # several sites for the board and this siter used to know one of them - the busiest node -
        # so every hamlet answered the same way a question the record answers three ways, and Sawada's
        # board ended up 9.0 ft off an 81.7 ft DEAD-END SPUR (7 of 19 dwellings within 250 ft against
        # 13 at the busiest stretch). A cul-de-sac head is not a center, an entrance or an official's
        # gate; it is outside what the record attests, not at one end of a supported range.
        #
        # Principle XII: where the record supports distinct FORMS, the rule is a knob rolled from the
        # map's own seed. `_kosatsuba_seat_ok` carries the value space, the evidence and the reason two
        # attested placements are withheld at these tiers.
        #
        # TIER-SCOPED (FR-009), and this is a requirement rather than an assumption because the code
        # says so: `pool/towns/hirameki.gen.py` calls `place_kosatsuba()`, so a TOWN comes through here.
        # Towns and cities keep the traffic objective they were sited under.
        placement = "center"
        if _scale in ("hamlet", "village"):
            placement = str(resolve_knob("kosatsuba_seat", int(self.seed), kosatsuba_affordances(self.M), (self.M["meta"].get("knobs") or {})))
        self.M["meta"]["kosatsuba_seat"] = placement
        anchor = kosatsuba_anchor(self.M, placement)
        if anchor is not None:
            # AN ANCHORED PLACEMENT CHOOSES THE GROUND; the preferences below then choose among the
            # seats on it. `center` returns no anchor on purpose - its objective IS the traffic count
            # already computed, which measures where people ARE rather than where the middle is.
            _near = min(math.hypot(c[2] - anchor[0], c[3] - anchor[1]) for c in cands)
            _band = KOSATSUBA_ANCHOR_BAND_FT / ftpx
            cands = [c for c in cands if math.hypot(c[2] - anchor[0], c[3] - anchor[1]) <= _near + _band] or cands
        # ON THE TRAFFIC IS THE RULE; A FITTING CAPTION IS ONLY THE PREFERENCE WITHIN IT. Scoring the
        # caption as a flat bonus large enough to outrank traffic was tried first and re-committed the
        # original sin at one remove: where no seat on a tight village frontage has a clear caption,
        # EVERY caption-clear seat is out in the fields, so all three village boards walked off the
        # frontage and their captions ran off the cropped frame. Open ground for a caption is abundant
        # exactly where nobody is - the same trap as open verge for the board. So the busiest node
        # sets a floor (60% of the best count available), and the caption chooses only among the seats
        # that already stand on the traffic. A board with nowhere to put its caption is still placed,
        # so labels_clear_of_other_buildings reports it rather than the siter hiding it.
        # ...and the traffic floor applies only where traffic is the objective. Keeping it under an
        # anchored placement would drag the board back toward the busy node the anchor just declined.
        floor = 0.0 if anchor is not None else 0.6 * max(c[0] for c in cands)

        # A BOARD POSITION IS ONLY AS GOOD AS THE CAPTION IT CAN CARRY (cohort seed 14, 2026-08-20).
        # `lab` above asks only whether the two DEFAULT seats clear STRUCTURES. It never asks about
        # lanes - so the siter happily chose a board that is hemmed: instrumented on seed 14, all
        # eleven structure-clear seats of the forty-eight sit west and south where the lanes run
        # (best clearance 1.0 ft against a 2 ft bar) while every seat with real clearance - 14.3,
        # 14.2, 8.6, 5.8 ft - is blocked by a building. No seat search can fix that, because the
        # board is in the wrong PLACE to be captioned, and nine attempts inside the search is what it
        # cost to see that.
        #
        # So feasibility joins the ranking, ahead of the old structure-only term. The probe is the
        # NEAR RING (four axes and four diagonals at zero standoff) rather than the full
        # forty-eight, and that is sound because the full candidate set is a SUPERSET of the ring:
        # near-ring-feasible implies search-feasible, which is exactly the one-way guarantee a
        # PREFERENCE needs. It is 8 probes per board position against the 2 already spent, and it
        # cannot promise a seat where the ring finds none - it only stops the siter preferring a
        # position that demonstrably has one over a position that demonstrably does not.
        def _sitable(_x: float, _y: float, _hw: float, _hh: float) -> bool:
            _chw2 = max(10.0, len(label) * 8 * 0.28) if label else 0.0
            if not label:
                return True
            # THE RING MUST BE A SUBSET OF WHAT THE SEARCH ACTUALLY TRIES, or the one-way guarantee
            # above is worthless. The first cut used 45-degree diagonals (0.7, 0.7) while the seat
            # search's annulus runs 30/60/120/150/210/240/300/330 - so a board could be ranked
            # sitable on a seat the search never offers, and seed 14 did not move. These are exactly
            # the twelve zero-standoff members of `_cands`: four axes plus those eight bearings.
            _ring = [(0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)]
            _ring += [(math.cos(math.radians(_a)), math.sin(math.radians(_a))) for _a in (30, 60, 120, 150, 210, 240, 300, 330)]
            for _dx, _dy in _ring:
                _qx = _x + (_hw + _chw2 + 8.0) * _dx
                _qy = _y + (_hh + 11.0) * _dy
                if self.label_seat_clear(_qx, _qy, tw_lab, 8.0, kb_boxes) and self.caption_lane_clearance(_qx, _qy, _chw2) >= CAPTION_LANE_TARGET_FT:
                    return True
            return False

        _b, _s, x, y, rot, lab, _gap = max((c for c in cands if c[0] >= floor), key=lambda c: (_sitable(c[2], c[3], w / 2, h / 2), c[5] is not None, c[1]))
        # `lab` NO LONGER DECIDES THE CAPTION'S SIDE, and that was the last thing keeping two cohort
        # seeds notched. It is computed above by testing `label_seat_clear` at the DEFAULT distance
        # only - `y +/- h/2 + 11` - so it reports "below is blocked" for a board whose below seat is
        # blocked at 11 px and perfectly clear at 35. Passing that verdict on as `label_above` forced
        # the caption to the far side and skipped the lane search entirely; instrumented on seed 14,
        # the seat it forced had -1.2 ft of lane clearance while an outward below seat had 7.8.
        #
        # `kosatsuba` now asks the structure question itself, of every candidate in its outward walk,
        # so the narrow precomputed verdict is strictly worse information. `lab` is still used ABOVE,
        # to prefer a BOARD POSITION where some caption seat exists at all - that is a different
        # question and a good one. The parameter stays on `kosatsuba` for external callers who know
        # something the manifest does not (the gate-adjacent case its docstring describes).
        # RECORD WHAT WAS DRAWN, NOT ONLY WHAT WAS ROLLED (settlement-review, feature 154). Two knobs
        # decide this seat and they can disagree: `kosatsuba_siting` (feature 152 - frontage or the
        # drawing-water place) bids through the `busy` score, while `kosatsuba_seat` (feature 154 -
        # center, entrance or the official's gate) culls the candidates to the ground around its
        # anchor. Where the anchor's ground holds no wellhead, every surviving candidate earns the
        # waterside bonus of zero, so the siting knob decides nothing - and the manifest went on
        # saying `waterside` anyway. Measured on Kashikawa: `kosatsuba_siting: waterside` on a board
        # 276 ft from the nearest of three wells, which the interactive page would have told a
        # clicking reader was the drawing-water place.
        #
        # That is this feature's own defect one field over - a placement recorded and not drawn - so
        # the fix is the same: state the achieved fact beside the rolled one. Neither knob is
        # overwritten; a reader can see what was asked for and what the ground allowed.
        # A MEASUREMENT, NOT A SECOND LABEL. Recording a drawn "waterside"/"frontage" was tried and
        # discarded in the same breath: a board that happens to land 60 ft from a well did not choose
        # the drawing-water place, and labelling it `waterside` would assert an intent the seat never
        # had - the same overstatement this field exists to catch. The distance claims nothing and
        # settles the question either way: on the five scripted hamlets the rolled siting and the
        # ground disagree on four, which is what says the two knobs are not composing.
        if _wells:
            self.M["meta"]["kosatsuba_well_ft"] = round(min(math.hypot(x - _wx3, y - _wy3) for _wx3, _wy3 in _wells) * float(self.M["meta"].get("ftpx") or 1), 1)
        self.kosatsuba(x, y, rot, label=label)
        return (x, y)

    def place_punishment_spot(self: Settlement, label: str | None = "punishment ground", label_xy: Pt | None = None) -> Pt | None:  # type: ignore[misc]
        """AUTO-SITE the punishment ground on a street verge at the busiest clear node - the notice
        board's sibling, and for the same reason: both institutions are sited by FOOT TRAFFIC, so
        both want the same probe rather than a hand-picked rect. (Hand rects were tried first on
        three maps and all three failed `punishment_spot_by_the_traffic` the same way: `open_seat`
        ties toward the rect's CENTER, which is the open ground behind the frontage, precisely where
        this feature must not be.) Deterministic - draws no RNG.

        Reads the SAME manifest route fields the validator reads (the dev-loop same-source doctrine),
        including `town_streets`, which the board's village-tier probe does not need. Keeps the spot
        inside the rampart where there is one - the display faces the town, not the road out; that is
        the execution ground's job. No-op under meta(punishment_spot=False). Returns the spot, or
        None when no verge fits (the presence check then fires - place by hand)."""
        if not self.M["meta"].get("punishment_spot", True):
            return None
        ftpx = float(self.M["meta"].get("ftpx") or 1)
        lim = 60.0 / ftpx  # punishment_spot_by_the_traffic: ~60 REAL feet from a street
        w, h = self.px(PUNISHMENT_SPOT_FT[0]), self.px(PUNISHMENT_SPOT_FT[1])
        routes: list[tuple[list[Pt], float]] = []
        if self.M.get("road"):
            routes.append(([(p[0], p[1]) for p in self.M["road"]], float(self.M.get("road_width") or 18)))
        routes.extend(([(p[0], p[1]) for p in st["pts"]], float(st.get("w", 18))) for st in self.M.get("town_streets") or [])
        routes.extend(([(p[0], p[1]) for p in ln["pts"]], float(ln.get("w", 8))) for ln in self.M.get("lanes") or [])
        if not routes:
            return None
        wall = self.M.get("wall")
        spots = [(b["x"], b["y"]) for b in self.M["houses"]] + [(b["x"], b["y"]) for b in self.M["buildings"]]
        beds = way_beds(self.M)  # see way_beds: EVERY bed, including the alleys and the ring road
        # this list does not sample candidates from - a display bypasses the lane CORRIDOR
        # deliberately (it is a house setback), never the roadbed itself

        def off_every_bed(x: float, y: float) -> bool:
            return all(seg_dist(x, y, bp[k], bp[k + 1]) >= bhw + h / 2 + 3 for bp, bhw in beds for k in range(len(bp) - 1))

        best: tuple[float, float, float, float] | None = None  # (score, x, y, rot)
        # ...and the best seat that is ALSO out from under the captions already on the map. A
        # PREFERENCE, not a filter (2026-08-08): landing under someone else's caption is a real
        # defect - Minami's ground auto-sited onto the burakumin quarter's label when a reflow moved
        # the busiest node 24px north - but it is the caption's problem to solve, and refusing the
        # seat outright would let a densely-captioned quarter drive the whole probe to None, i.e.
        # turn "the label wants moving" into "the city has no punishment ground at all". So: take a
        # clear seat when one exists at any score, and fall back to the busiest seat when none does.
        best_clear: tuple[float, float, float, float] | None = None
        for pts, _rw in routes:
            for i in range(len(pts) - 1):
                (ax, ay), (bx, by) = pts[i], pts[i + 1]
                seg = math.hypot(bx - ax, by - ay)
                if not seg:
                    continue
                ux, uy = -(by - ay) / seg, (bx - ax) / seg
                rot = math.degrees(math.atan2(by - ay, bx - ax))
                for t in range(int(seg // 12) + 1):
                    f = t * 12 / seg
                    mx, my = ax + (bx - ax) * f, ay + (by - ay) * f
                    for side in (1.0, -1.0):
                        off = _rw / 2 + h / 2 + 4
                        while off <= lim:
                            x, y = mx + ux * off * side, my + uy * off * side
                            if (not wall or len(wall) < 3 or point_in_poly(x, y, wall)) and off_every_bed(x, y) and self._fits(x, y, w, h, corridors=False):
                                busy = sum(1 for sx, sy in spots if math.hypot(x - sx, y - sy) < 260)
                                score = busy * 10 - off / 3
                                if best is None or score > best[0]:
                                    best = (score, x, y, rot)
                                if not self._under_a_caption(x, y, w, h, rot) and (best_clear is None or score > best_clear[0]):
                                    best_clear = (score, x, y, rot)
                            off += 5.0
        best = best_clear or best
        if best is None:
            return None
        _, x, y, rot = best
        if label and label_xy is None:
            # A verge-hugging feature's DEFAULT below-label lands on the frontage it hugs - that is
            # not bad luck, it is what "hugging the frontage" means, and it fired on all three maps.
            # So probe the label too: below, above, then left/right, first clear box wins.
            label_xy = self.clear_label_seat(x, y, w, h, label, skip_key="punishment_spots")
        self.punishment_spot(x, y, rot, label=label, label_xy=label_xy)
        return (x, y)
