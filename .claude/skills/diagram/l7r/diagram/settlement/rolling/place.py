"""FIND a spot and commit to it: the spiral searches, the two compaction slides, the nucleated garden-side choice, the legacy per-house solver.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.
"""

import math
from typing import TYPE_CHECKING, Any

from .._geom import Indexed, Pt

if TYPE_CHECKING:
    from ..core import Settlement


class PlacerMixin:
    def headman(self: Settlement, x: float, y: float, w: float = 92, h: float = 56) -> Any:  # type: ignore[misc]
        # `w`, `h` are in FEET (drawn at the map's ftpx, px(92) = 46px at 2 ft/px). A nanushi/shoya house is
        # the grandest in the village but still a house - ~92x56 ft, clearly larger than a plain 46x28 ft
        # farmhouse without the old fortress-sized 216x136 ft. headman_is_largest holds.
        if self._toscale():
            # the headman is just a LARGER PLAIN farmhouse - placed through the standard collision-checked
            # bundle path with a tunable SIZE, so it gets its yard + garden and cannot overlap a neighbor.
            # BOTH homestead styles route here (GM 2026-07-21, caught on Hikari no Sato): this guard used to
            # test _nucleated, so a DISPERSED to-scale village's headman fell through to the legacy rec below,
            # which _farmsteads_bundle draws as a LONE house (the abandoned-ruin path) - the grandest
            # farmstead in the village with no threshing yard and no garden. In the dispersed style the
            # bundle also brings the per-house grove when room allows; the solver drops it gracefully in a
            # dense cluster (neighbor tree cover shelters the house), which is the wanted behavior.
            # NO special reservation or "big"-glyph storeroom wing (that wing was drawn outside
            # the reserved footprint and overlapped the north neighbor's yard).
            return self.try_place(x, y, "plain", role="headman", size=(w, h))
        # non-to-scale tiers have no headman (a hamlet falls under the district headman, towns are run by
        # the magistrate - the *_has_no_headman checks), so the old legacy rec branch here was dead code
        # once the Hikari fix routed every to-scale style through the bundle; removed 2026-07-21.
        raise ValueError("headman() is a to-scale village feature - this map is not toscale")

    @staticmethod
    def _closest_on_seg(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> Pt:
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return ax, ay
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return ax + t * dx, ay + t * dy

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

    def _nearest_placed_point(self: Settlement, cx: float, cy: float) -> Pt | None:  # type: ignore[misc]
        """The center of the nearest already-placed homestead/house - the neighbor to pack against."""
        best: Pt | None = None
        bd = float("inf")
        for px, py, _pw, _ph, *_ in self.placed:
            d = (px - cx) ** 2 + (py - cy) ** 2
            if d < bd:
                bd, best = d, (px, py)
        return best

    def _slide(self: Settlement, cx: float, cy: float, hw: float, hh: float, target_fn: Any, grove_off_field: bool) -> Pt:  # type: ignore[misc]
        """Greedily shove the bundle toward target_fn (a field bund, then a neighbor) in small steps, as
        far as it still fits - the 'pack as close as the rules allow' step."""
        for _ in range(48):
            tgt = target_fn(cx, cy)
            if tgt is None:
                break
            dx, dy = tgt[0] - cx, tgt[1] - cy
            dist = math.hypot(dx, dy)
            if dist < 1.5:
                break
            ncx, ncy = cx + dx / dist * 2.0, cy + dy / dist * 2.0
            if self._bundle_fits(self._bundle_geom(ncx, ncy, hw, hh), grove_off_field=grove_off_field):
                cx, cy = ncx, ncy
            else:
                break
        return cx, cy

    def _place_bundle(self: Settlement, x: float, y: float, hw: float, hh: float, shed: bool = False) -> Any:  # type: ignore[misc]
        """Place a homestead bundle one-at-a-time: find the nearest fitting spot to the seed, then COMPACT it
        - shove the grove up against the nearest paddy bund (without entering it), then pack the whole
        complex against its nearest neighbor, each as far as the rules allow. `shed` reserves a north kura in
        the bundle. Returns (cx, cy, geom) or None."""
        if getattr(self, "_nucleated", False):
            return self._place_bundle_nucleated(x, y, hw, hh, shed)
        offsets = [(0, 0)]
        for r in range(7, 92, 7):
            for k in range(12):
                a = k * math.pi / 6
                offsets.append((round(r * math.cos(a)), round(r * math.sin(a))))
        start: Pt | None = None
        for nx, ny in offsets:
            if self._bundle_fits(self._bundle_geom(x + nx, y + ny, hw, hh)):
                start = (x + nx, y + ny)
                break
        if start is None:
            return None
        cx, cy = start
        cx, cy = self._slide(cx, cy, hw, hh, self._nearest_field_point, grove_off_field=True)  # grove hugs the bund
        cx, cy = self._slide(cx, cy, hw, hh, self._nearest_placed_point, grove_off_field=True)  # pack against neighbor
        return cx, cy, self._bundle_geom(cx, cy, hw, hh)

    _NUC_SIDES = ("SE", "SW", "E", "W")  # garden-side preference: sunny south strip first, walls as fallback

    def _field_dist(self: Settlement, cx: float, cy: float) -> float:  # type: ignore[misc]
        """Distance from a point to the nearest paddy edge (inf if there are no fields)."""
        p = self._nearest_field_point(cx, cy)
        return math.hypot(cx - p[0], cy - p[1]) if p else float("inf")

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
        corridors) - and among the configurations that fit, the sun rules choose (fewest shaded beds, then the
        preference order: the sunny south corners, then the walls). The ground is not asked again for a part: every
        part lies inside a box the ground already admitted. Four configurations at most, one rectangle each.

        WHAT THIS REPLACES, measured (specs/227 research R1): a spiral of up to 73 offsets with the full battery at
        each, then two 2 px slides - toward the paddy and along the neighbors - re-running the battery at every
        step: 26-60 positions and 100-220 rectangles per call, 70-85% of them on calls that failed outright because
        a house-sized pre-test had passed a seat the whole homestead could not use. The slide had no recorded
        reason (commit ed0e884e): it stepped because the stop was whichever of eight rules fired first. Now the
        seat arrives at its standoff and its pitch (`_front_row_from_chains`), and the one move a call may make is
        COMPUTED: an envelope overlapping exactly one placed box is shifted once by the measured overlap, away from
        that neighbor, and tested once more (the GM: *"measuring the distance to the neighbor and then moving
        however much the correct amount is"*). Anything else is refused and the proposer offers the next seat."""
        self._seat_search["placer_calls"] += 1
        _avoid = getattr(self, "_avoid_seats", None)
        # THE UNION FIRST, ONE RECTANGLE: the box around every configuration (`_bundle_envelope`). Where it fits - the
        # open ground of most seats - every configuration's box fits inside it and no other rectangle is tested; the
        # parts alone decide the side. Where the union is refused, each configuration's OWN box is tried in turn (the
        # sun-preferred side first): the union alone over-refused on tight ground - the pockets between a dike mosaic's
        # ponds hold a one-sided homestead and not the both-sided box (Kuwabata 11 of 16) - and the GM's rectangle is the
        # one the homestead will occupy, garden on the left OR the right, not both at once. At most five rectangles.
        self._seat_search["positions"] += 1
        _union_clear = self._envelope_blocked(self._bundle_envelope(x, y, hw, hh, shed)) is None
        best: Any = None
        for rank, side in enumerate(self._NUC_SIDES):
            cx, cy = x, y
            geom = self._bundle_geom(cx, cy, hw, hh, side, shed)
            hit = None
            if not _union_clear:
                self._seat_search["positions"] += 1
                hit = self._envelope_blocked(geom["bbox"])
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
                hit = self._envelope_blocked(geom["bbox"])
            if hit is not None:
                continue
            if _avoid and any(math.hypot(cx - _ax, cy - _ay) <= 50.0 for _ax, _ay in _avoid):
                continue
            self._seat_search["parts"] = self._seat_search.get("parts", 0) + 1
            if not self._parts_fit(geom):
                continue
            score = (sum(self._garden_shaded(g) for g in geom["gardens"]), rank)  # fewest shaded beds first, then preference
            if best is None or score < best[0]:
                best = (score, cx, cy, geom)
        if best is None:
            return None
        return best[1], best[2], best[3]

    def _solve_homestead(self: Settlement, rec: Any) -> Any:  # type: ignore[misc]
        """Find the best position for a farmhouse so its WHOLE homestead fits - threshing yard + dooryard
        garden + room for a windward grove. Searches the placed spot first, then a widening spiral, and stops
        as soon as the home spot already leaves grove-room (no churn). Prefers a spot WITH grove-room, then the
        least displacement; falls back to a yard+garden-only spot if no grove-room is reachable nearby. Updates
        rec's position + reservation. Returns (yard_spot, garden_spot), or None if even yard+garden won't fit."""
        x0, y0, w, h = rec["x"], rec["y"], rec["w"], rec["h"]
        self.placed: list[Any] = Indexed(
            p for p in self.placed if p != (x0, y0, w, h)
        )  # lift own reservation while searching (Indexed, not a plain list - a rebind must not silently drop _fits' index into the uncached fallback)
        best: Any = None  # (has_grove_room, -displacement, cx, cy, spot)
        for nx, ny in self._farmstead_nudges():
            cx, cy = x0 + nx, y0 + ny
            if not self._fits(cx, cy, w, h) or not self._field_adjacent(cx, cy):
                continue
            spot = self._find_appurtenances(cx, cy, w, h, rec["rot"], rec["kind"], rec["shed"], rec["wealth"])
            if spot is None:
                continue
            wf = rec["wealth"]  # the grove is drawn at the WEALTH size, so reserve room for THAT
            cand = (self._grove_room(cx, cy, w * wf, h * wf), -(abs(nx) + abs(ny)), cx, cy, spot)
            if best is None or cand[:2] > best[:2]:
                best = cand
            if cand[0] and nx == 0 and ny == 0:
                break  # already perfect at the home spot
        cx, cy = (best[2], best[3]) if best else (x0, y0)
        rec["x"], rec["y"] = cx, cy
        self.placed.append((cx, cy, w, h))  # re-reserve at the chosen (or original) spot
        return best[4] if best else None
