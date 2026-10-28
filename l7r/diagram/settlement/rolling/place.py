"""FIND a spot and commit to it: the spiral searches, the two compaction slides, the nucleated garden-side choice, the legacy per-house solver.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: search and prefilter plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.work_counts import OPS

from .._geom import Pt, point_in_poly
from .access import seat_reaches_tree
from .fit import part_box
from .passage import landlocked

if TYPE_CHECKING:
    from ..core import Settlement


class PlacerMixin:
    def _nearest_field_point(self: Settlement, cx: float, cy: float) -> Pt | None:  # type: ignore[misc]
        """The closest point on any paddy outline to (cx, cy) - the bund the grove will hug."""
        best: Pt | None = None
        bd = float("inf")
        for poly in self.field_polys:
            n = len(poly)
            for i in range(n):
                qx, qy = self._closest_on_seg(cx, cy, poly[i][0], poly[i][1], poly[(i + 1) % n][0], poly[(i + 1) % n][1])
                d = (qx - cx) ** 2 + (qy - cy) ** 2
                if d < bd:
                    bd, best = d, (qx, qy)
        return best

    @staticmethod
    def _closest_on_seg(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> Pt:
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return ax, ay
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return ax + t * dx, ay + t * dy

    def _nearest_placed_point(self: Settlement, cx: float, cy: float) -> Pt | None:  # type: ignore[misc]
        """The center of the nearest already-placed homestead/house - the neighbor to pack against."""
        best: Pt | None = None
        bd = float("inf")
        for px, py, _pw, _ph, *_ in self.placed:
            d = (px - cx) ** 2 + (py - cy) ** 2
            if d < bd:
                bd, best = d, (px, py)
        return best

    def _seat_refused(self: Settlement, x: float, y: float, hw: float, hh: float) -> bool:  # type: ignore[misc]
        """Would `_bundle_fits` refuse a DISPERSED bundle whose house stands at (x, y) - answered from the free ground,
        before its bundle is built (feature 276, FR-003, plan D9/D9a)?

        Three of `_bundle_fits`' own conjuncts, each of which reads only the house rectangle `_bundle_geom` gives the
        bundle - `(x, y, hw, hh)`, exactly: one of the house's nine points on surely-taken static ground (the house-ground
        conjunct refuses that point); the house within the 2 px margin of a placed box (the bundle's bbox holds the house,
        and the side fit refuses any placed box within that margin of the bbox); the eave gap to a neighbor. The
        conjunction is order-independent, so a YES here is the fit test's NO. The dispersed path only: on the nucleated
        path one overlapping box is a computed move, not a refusal."""
        house = (x, y, hw, hh)
        fg = getattr(self, "_free_ground", None)
        if fg is not None and fg.rect_refused(house):
            return True
        for it in self._reach_index(self.placed, "placed_reach").near(x, y, max(hw, hh) / 2 + 2):
            if abs(x - it[0]) < (hw + it[2]) / 2 + 2 and abs(y - it[1]) < (hh + it[3]) / 2 + 2:
                return True
        return bool(self._house_too_near_a_neighbor(house) or self._house_unreachable(house))

    def _bundle_refused(self: Settlement, geom: Any) -> bool:  # type: ignore[misc]
        """Would `_bundle_fits` refuse this DISPERSED bundle, by one of the conjuncts the indexes answer cheaply (feature
        276, plan D9a)? Behind `_seat_refused`, once the bundle is built (moved from its template, so building is cheap):
        a part's nine points on surely-taken static ground (with a site boundary installed, `_rect_blocked` IS the
        nine-point test, whichever `fields` it is asked with), the bbox off the canvas or the bounding ring, the bbox within
        the 2 px margin of a placed box, and the three sun rules. Each is a conjunct of the order-independent
        `_bundle_fits`, so a YES here is its NO; what survives gets the whole test, as before.

        Research:
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (sheet-edge margin)
            its least gap - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 2 (2 px least gap between a homestead's bbox and a placed box)
        """
        fg = getattr(self, "_free_ground", None)
        if fg is not None:
            parts = [part_box(geom, k) for k in ("yard", "shed")] + list(geom.get("groves") or ()) + list(part_box(geom, "gardens"))  # as drawn (269 B18)
            if any(r is not None and fg.rect_refused(r) for r in parts):
                return True
        cx, cy, W, H = geom["bbox"]
        if cx - W / 2 < 6 or cx + W / 2 > self.W - 6 or cy - H / 2 < 6 or cy + H / 2 > self.H - 6:
            return True
        if self.bound and any(not point_in_poly(vx, vy, self.bound) for vx, vy in self._rect_corners(geom["bbox"])):
            return True
        for it in self._reach_index(self.placed, "placed_reach").near(cx, cy, max(W, H) / 2 + 2):
            if abs(cx - it[0]) < (W + it[2]) / 2 + 2 and abs(cy - it[1]) < (H + it[3]) / 2 + 2:
                return True
        if not self._sun_corridor_ok(geom) or not self._gardens_sun_ok(geom):
            return True
        return bool(geom.get("yard") is not None and self._yard_sun_conflict(geom))

    def _slide(self: Settlement, cx: float, cy: float, hw: float, hh: float, target_fn: Any, grove_off_field: bool) -> Pt:  # type: ignore[misc]
        """Greedily shove the bundle toward target_fn (a field bund, then a neighbor) in small steps, as
        far as it still fits - the 'pack as close as the rules allow' step.

        Research:
            dispersed farm packed toward field and neighbor - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the first slide, 2 px steps up to 48 toward the bund, while it fits
            dispersed farm packed against its nearest neighbor - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each homestead keeps its own spacing, and 0285 has scattered farms 100 to 200 m apart - a dispersed farm is slid against its neighbor, a departure the code keeps until feature 417 T33; the second slide, toward the nearest neighbor, where 0031 has a scattered homestead keep its own spacing
            its salts, guards and sentinels - NONE: they decide nothing about the place - 1.5 (stop tolerance (arrived at the target))
        """
        for _ in range(48):
            if __debug__:
                OPS["candidate@_slide"] += 1
            tgt = target_fn(cx, cy)
            if tgt is None:
                break
            dx, dy = tgt[0] - cx, tgt[1] - cy
            dist = math.hypot(dx, dy)
            if dist < 1.5:
                break
            ncx, ncy = cx + dx / dist * 2.0, cy + dy / dist * 2.0
            # THE FREE GROUND FIRST (feature 276, plan D9): a step it refuses is a step `_bundle_fits` refuses, and the
            # slide stops at the first refusal either way.
            if self._seat_refused(ncx, ncy, hw, hh):
                break
            geom = self._bundle_geom(ncx, ncy, hw, hh)
            if not self._bundle_refused(geom) and self._bundle_fits(geom, grove_off_field=grove_off_field):
                cx, cy = ncx, ncy
            else:
                break
        return cx, cy

    def _place_bundle(self: Settlement, x: float, y: float, hw: float, hh: float, shed: bool = False) -> Any:  # type: ignore[misc]
        """Place a homestead bundle one-at-a-time: find the nearest fitting spot to the seed, then COMPACT it
        - shove the grove up against the nearest paddy bund (without entering it), then pack the whole
        complex against its nearest neighbor, each as far as the rules allow. `shed` reserves a north kura in
        the bundle. Returns (cx, cy, geom) or None."""
        # THE HOUSEHOLD'S SEAT, for the rolls of its bundle's parts (feature 276, plan D10): the seat it is sought from,
        # wherever the search moves it - so its yard and garden are the household's, not each candidate's.
        prior = getattr(self, "_household_seat", None)
        # ...AND KEYED ON THE SEAT OFFERED, NOT ON THE HOUSEHOLD - TRIED AND WITHDRAWN (feature 297, plan C, research R9): keyed on
        # the household, its yard's lognormal size was rolled once, and the per-seat rolls had been the seating's only way to fit
        # a large-yard household into a tight spot - seed 3 seated 9 of 10 and its site was refused.
        self._household_seat = (float(x), float(y))
        try:
            if getattr(self, "_nucleated", False):
                return self._place_bundle_nucleated(x, y, hw, hh, shed)
            return self._place_bundle_dispersed(x, y, hw, hh)
        finally:
            self._household_seat = prior

    def _place_bundle_dispersed(self: Settlement, x: float, y: float, hw: float, hh: float) -> Any:  # type: ignore[misc]
        """The dispersed spiral: the nearest seat that fits, then the two slides (see `_place_bundle`).

        Research:
            row farm kept on its lot - research/questions/0033-row-villages-resson.drawing.html: within a row the seat is nudged at most one step and never slid
            nearest seat that fits - NONE: a spiral of offsets to 91 px from the seed
            its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N8, 2026-10-25) - 7 (spiral ring step 7 px, out to 91 px (one ring for an exact row seat)); 15 (spiral ring step 7 px, out to 91 px (one ring for an exact row seat)); 92 (spiral ring step 7 px, out to 91 px (one ring for an exact row seat)); 12 (12 directions per ring); 6 (pi/6 step between those directions)
        """
        offsets = [(0, 0)]
        # A ROW'S SEAT IS EXACT (feature 291 plan D15, `hamletgen/homesteads/rows.py`): the row planned each frame one lot
        # along its street, and the two slides below - toward the field, then against the neighbor - carried the far row
        # onto the street itself (Kashikawa: 10 of 20 frames on the planned line). Within a row the seat is nudged at most
        # one step and never slid.
        exact = bool(getattr(self, "_exact_seat", False))
        for r in range(7, 15 if exact else 92, 7):
            for k in range(12):
                a = k * math.pi / 6
                offsets.append((round(r * math.cos(a)), round(r * math.sin(a))))
        for nx, ny in offsets:
            if __debug__:
                OPS["candidate@_place_bundle_dispersed"] += 1
            # THE FREE GROUND PROPOSES, THE FIT TEST DECIDES (feature 276, plan D9): an offset whose house the index
            # refuses is one `_bundle_fits` would refuse, so it is dropped without building its bundle.
            if self._seat_refused(x + nx, y + ny, hw, hh):
                continue
            geom = self._bundle_geom(x + nx, y + ny, hw, hh)
            if self._bundle_refused(geom) or not self._bundle_fits(geom):
                continue
            cx, cy = x + nx, y + ny
            if not exact:
                cx, cy = self._slide(cx, cy, hw, hh, self._nearest_field_point, grove_off_field=True)  # grove hugs the bund
                cx, cy = self._slide(cx, cy, hw, hh, self._nearest_placed_point, grove_off_field=True)  # pack against neighbor
            return cx, cy, self._bundle_geom(cx, cy, hw, hh)
        return None

    _NUC_SIDES = ("SE", "SW", "E", "W")  # garden-side preference: sunny south strip first, walls as fallback
    """Research: garden side preference - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the sunny south corners first, the east and west walls after"""

    def _place_bundle_nucleated(self: Settlement, x: float, y: float, hw: float, hh: float, shed: bool = False) -> Any:  # type: ignore[misc]
        """Nucleated placement, THE ENVELOPE FIRST (feature 227, GM 2026-09-12: *"I thought that what we were doing
        when we were placing homesteads was essentially drawing a rectangle around what would be within the homestead.
        And then once we definitely have enough space, we decide things like whether the garden is on the left or the
        right side or both, and whether or not there is an attached shed"*).

        ONE rectangle is tested before anything else about a configuration: its envelope - the box around the house
        at its rolled size, the yard south of it, the garden on that side, the kura north when the household has one
        (`_bundle_geom`'s bbox) - against the site boundary at its nine points and against the placed boxes
        (`_envelope_blocked`). Only when the envelope fits are the parts inside it judged - the rules that read the
        PARTS, asked once at that spot (`_parts_fit`: the wall rule against the paddy, the eave gap, the tread, the sun
        corridors, the corridor to the access tree, the wood share) - and among the configurations that fit, the sun rules
        choose (fewest shaded beds, then the preference order: the sunny south corners, then the walls). The envelope's
        nine points clear the ground for every part; only what they can miss is asked of a part exactly (`_parts_fit`: the
        yard and fixtures off the paddy, the beds off the ditches). Four configurations at most, one rectangle each.

        WHAT THIS REPLACES, measured (specs/227 research R1): a spiral of up to 73 offsets with the full battery at
        each, then two 2 px slides - toward the paddy and along the neighbors - re-running the battery at every
        step: 26-60 positions and 100-220 rectangles per call, 70-85% of them on calls that failed outright because
        a house-sized pre-test had passed a seat the whole homestead could not use. The slide had no recorded
        reason (commit ed0e884e): it stepped because the stop was whichever of eight rules fired first. Now the
        seat arrives where its proposer computed it - a grown seat where the two homesteads' footprints part
        (`growth.seat_toward`, feature 308) - and the one move a call may make is COMPUTED: an envelope overlapping exactly
        one placed box is shifted once by the measured overlap, away from that neighbor, and tested once more (the GM:
        *"measuring the distance to the neighbor and then moving however much the correct amount is"*) - never nearer a
        grown seat's source than the growth's distance (`growth.keeps_its_distance`). Anything else is refused and the
        proposer offers the next seat.

        Research:
            garden side chosen by the sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: fewest shaded beds, then the south corners before the walls
            left or right garden - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); within a tier the side is decided by position, about even
            one computed move off a neighbor - NONE: the measured overlap plus 2 px, once
            a tight seat only on landlocked land - research/questions/0081-village-lanes.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: taken only where some layout walks to the neighbor's yard and none has a way of its own (`passage.landlocked`)
            a seat refused unless its yard opens onto lane ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no way is sought for a household while it is seated; its dooryard must open onto the ground the lanes are laid in (`SeatRegion.opens`)
            the village roll's corridor - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a roll with no seat region (a village's) asks for a corridor candidate instead (`seat_reaches_tree`)
            its salts, guards and sentinels - NONE: they decide nothing about the place - 12 (jitter salt (which hand the garden goes on))
        """
        self._seat_search["placer_calls"] += 1
        # THE UNION FIRST, ONE RECTANGLE: the box around every configuration (`_bundle_envelope`). Where it fits - the
        # open ground of most seats - every configuration's box fits inside it and no other rectangle is tested; the
        # parts alone decide the side. Where the union is refused, each configuration's OWN box is tried in turn (the
        # sun-preferred side first): the union alone over-refused on tight ground - the pockets between a dike mosaic's
        # ponds hold a one-sided homestead and not the both-sided box (Kuwabata 11 of 16) - and the GM's rectangle is the
        # one the homestead will occupy, garden on the left OR the right, not both at once. At most five rectangles.
        self._seat_search["positions"] += 1
        # THE FREE GROUND FIRST, WHERE THE LOOP ITSELF JUDGES GROUND (feature 276, plan D9): the whole envelope here; a
        # side's own box only below, when this envelope was refused (only then does the loop test that box); a moved box
        # at its moved position. A box the static ground refuses is one `_envelope_blocked` refuses (True, before any
        # placed box is read), so asking it first changes no verdict and never removes a move.
        _fg = getattr(self, "_free_ground", None)
        # THE HOUSE'S OWN BOX FIRST, BEFORE ANY LAYOUT (feature 287 perf): every configuration's box, and the union, holds the
        # house's box as drawn (`_house_box`), so a refusal of the house's box that only grows with the box - past the canvas
        # margin, over a reserved corridor, on two placed homesteads - refuses every one of them before the placed-box move
        # is ever offered (`_envelope_blocked` returns True, not the one box, on any of the three). The four layouts, each
        # laying the household's fixtures, were built for nothing on a third of the exhaustive pass's offers.
        if self._house_box_refused(self._house_box(x, y, hw, hh)):
            return None
        # THE SEAT'S OWN QUESTIONS, ONCE (feature 297, FR-002, plan C, amended by research R10): the corridor to the access tree
        # depends on the house and its yard, common to all four garden sides (558 of 558 seats measured, research R6) - asked ONCE
        # per seat below, after the envelope (the cheaper refusal: asked first, it ran the costliest search on every offered seat,
        # R10). No seat is refused for its water (feature 374 wave 155): the wells are seated after the houses, with the reach.
        # THE FOUR CONFIGURATIONS BUILT ONCE (dev/performance.md): the envelope is their union, and the loop below judges
        # each at this seat - it built all four again (seed 17: 25,000 bundles, half of them rebuilt)
        _at = {side: self._bundle_geom(x, y, hw, hh, side, shed) for side in self._NUC_SIDES}
        _env = self._bbox_of([g["bbox"] for g in _at.values()])
        _union_clear = not (_fg is not None and _fg.rect_refused(_env)) and self._envelope_blocked(_env) is None
        # A TIGHT SEAT IS JUDGED BY ITS LAND, NOT ONE LAYOUT (feature 317, `passage.landlocked`): the custom is for land with no
        # way of its own, and a household lays its beds where its way can run - so the seat is taken only where some layout here
        # has a walk to the neighbor's yard and none has a corridor of its own
        if getattr(self, "_tight_of", None) is not None and not landlocked(self, list(_at.values())):
            return None
        best: Any = None
        _reaches: bool | None = None
        for rank, side in enumerate(self._NUC_SIDES):
            if __debug__:
                OPS["candidate@_place_bundle_nucleated"] += 1
            cx, cy = x, y
            geom = _at[side]
            hit = None
            if not _union_clear:
                self._seat_search["positions"] += 1
                hit = True if _fg is not None and _fg.rect_refused(geom["bbox"]) else self._envelope_blocked(geom["bbox"])
            if isinstance(hit, tuple):
                # THE ONE COMPUTED MOVE: the overlap with that neighbor's box on each axis, plus the 2 px the placed-box
                # test keeps; move along the axis that needs the smaller push, away from the neighbor's center
                env = geom["bbox"]
                px, py, pw, ph = hit[0], hit[1], hit[2], hit[3]
                ox = (env[2] + pw) / 2 + 2.0 - abs(env[0] - px)
                oy = (env[3] + ph) / 2 + 2.0 - abs(env[1] - py)
                if ox <= oy:
                    cx += ox if env[0] >= px else -ox
                else:
                    cy += oy if env[1] >= py else -oy
                geom = self._bundle_geom(cx, cy, hw, hh, side, shed)
                self._seat_search["positions"] += 1
                hit = True if _fg is not None and _fg.rect_refused(geom["bbox"]) else self._envelope_blocked(geom["bbox"])
                # ...NEVER NEARER A GROWN SEAT'S SOURCE THAN THE GROWTH'S DISTANCE (feature 308, FR-004): the move off a third
                # homestead carried one 2.6 px from the house it grew from (research R10); `_grown_keep` is the growth's
                # test of the moved box (`growth.keeps_its_distance`)
                keep = getattr(self, "_grown_keep", None)
                if hit is None and keep is not None and not keep(geom["bbox"]):
                    hit = True
            if hit is not None:
                continue
            if (cx, cy) == (x, y):  # the seat's corridor, asked once for all its unmoved sides (a moved side is another seat)
                if _reaches is None:  # ...its yard onto lane ground where a seat region stands (feature 318), else a corridor candidate
                    region = getattr(self, "_seat_region", None)
                    _reaches = region.opens(geom) if region is not None else seat_reaches_tree(self, geom)
                if not _reaches:
                    continue
            self._seat_search["parts"] = self._seat_search.get("parts", 0) + 1
            if not self._parts_fit(geom):
                continue
            # FEWEST SHADED BEDS, THEN THE DOCTRINE'S TIER, THEN THE MAP'S OWN HAND (feature 227, the review's
            # second pass). `_NUC_SIDES` is (SE, SW, E, W): the sunny south strip before the walls is the researched
            # preference and it is kept as the tier (rank // 2), but WITHIN a tier the left and the right are equally
            # good and the choice is positional. It has to be: the envelope now clears the ground for every
            # configuration before any is judged, so with nothing to break the tie the fixed order won every time and
            # the west side went to 0 of 82 homesteads across the pool - in exactly the axis the GM asked to see vary
            # (*"whether the garden is on the left or the right side or both"*).
            _hand = (rank % 2) ^ (1 if self._hjit(cx, cy, 12.0) < 0.5 else 0)
            score = (sum(self._garden_shaded(g) for g in part_box(geom, "gardens")), rank // 2, _hand)
            if best is None or score < best[0]:
                best = (score, cx, cy, geom)
        if best is None:
            return None
        return best[1], best[2], best[3]

    def _house_box(self: Settlement, x: float, y: float, hw: float, hh: float) -> tuple[float, float, float, float]:  # type: ignore[misc]
        """The house's box as `_bundle_geom` records it at (x, y) (`boxes["house"]`): its rect, turned by the seat's rake."""
        _th = math.radians(self._turn_at(x, y))
        _c, _s = abs(math.cos(_th)), abs(math.sin(_th))
        w, h = float(hw), float(hh)
        return (float(x), float(y), w * _c + h * _s, w * _s + h * _c)

    def _house_box_refused(self: Settlement, box: tuple[float, float, float, float]) -> bool:  # type: ignore[misc]
        """Is a box refused on the grounds that only grow with it - the canvas margin, a reserved corridor, two or more placed
        boxes (`_envelope_blocked`'s own tests and margins)? Then so is every box that holds it.

        Research:
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (sheet-edge margin)
            its least gap - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 2 (2 px least gap between a house box and placed boxes)
        """
        cx, cy, w, h = box
        if cx - w / 2 < 6 or cx + w / 2 > self.W - 6 or cy - h / 2 < 6 or cy + h / 2 > self.H - 6:
            return True
        tree = getattr(self, "_access", None)
        if tree is not None and tree.covers_box(box):
            return True
        seen: set[int] = set()
        for it in self._reach_index(self.placed, "placed_reach").near(cx, cy, max(w, h) / 2 + 2):
            if id(it) not in seen and abs(cx - it[0]) < (w + it[2]) / 2 + 2 and abs(cy - it[1]) < (h + it[3]) / 2 + 2:
                seen.add(id(it))
                if len(seen) >= 2:
                    return True
        return False
