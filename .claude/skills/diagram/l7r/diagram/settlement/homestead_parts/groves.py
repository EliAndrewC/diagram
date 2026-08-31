"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import random
from typing import TYPE_CHECKING, Any

from .._geom import _union_area, point_in_poly, seg_dist

if TYPE_CHECKING:
    from ..core import Settlement


class GrovesMixin:
    # the windward faces a homestead grove (yashikirin) shelters, by where the prevailing cold wind comes
    # FROM (its compass key). The grove is an L-BELT: a deep stand on each windward face (for a diagonal
    # like NW, an N arm + a W arm wrapping the corner; for a cardinal, one deep band). Default NW - the
    # East Asian winter monsoon (the Siberian high) blows NW across China AND Japan, so N+W is windward and
    # the S/E is the sheltered, sunny side. A map keys it off its geography with meta(windward=...). Each
    # arm is (face, perp): `face` is the cardinal it sits on; `perp` is the sign the N/S arm extends along
    # to wrap the corner (0 for a lone cardinal arm). See settlements.md 'Homestead groves'.
    _GROVE_ARMS = {
        "NW": [((0, -1), -1), ((-1, 0), 0)],
        "NE": [((0, -1), 1), ((1, 0), 0)],
        "SW": [((0, 1), -1), ((-1, 0), 0)],
        "SE": [((0, 1), 1), ((1, 0), 0)],
        "N": [((0, -1), 0)],
        "S": [((0, 1), 0)],
        "E": [((1, 0), 0)],
        "W": [((-1, 0), 0)],
    }

    def _windward(self: Settlement) -> str:  # type: ignore[misc]
        """The map's prevailing-wind compass key (where the cold wind blows FROM), default NW."""
        w = str(self.M["meta"].get("windward", "NW")).upper().strip()
        return w if w in self._GROVE_ARMS else "NW"

    def _windward_x(self: Settlement) -> int:  # type: ignore[misc]
        """The horizontal sign of the windward direction: -1 if the wind is from the W (NW/W/SW), +1 if from
        the E (NE/E/SE), 0 for a due N/S wind. Used to keep the garden off the windward wall (the grove's side)."""
        wk = self._windward()
        return -1 if "W" in wk else (1 if "E" in wk else 0)

    def _grove_candidate(self: Settlement, hx: float, hy: float) -> bool:  # type: ignore[misc]
        """Whether this farmhouse is a grove candidate. UNIVERSAL by default (the yashikirin ringed every
        dispersed farmstead, so a grove is drawn wherever there is windward room); meta(grove_prevalence=N<1)
        dials it down for an atypical/sheltered microclimate. Deterministic in the house position (stable
        across regenerations, RNG-independent)."""
        rate = float(self.M["meta"].get("grove_prevalence", 1.0))
        return rate >= 1.0 or int(abs(hx) * 31 + abs(hy) * 17) % 100 < rate * 100

    def _grove_arm_rect(self: Settlement, hx: float, hy: float, hw: float, hh: float, fdx: float, fdy: float, perp: float, d: float, gap: float, lf: float = 1.0) -> tuple[float, float, float, float]:  # type: ignore[misc]
        """One belt ARM's footprint (cx, cy, w, h), depth `d`, just outside the house wall it shelters. An
        N/S arm runs E-W as wide as the house plus `d` (extending `perp` toward the windward corner so the
        two arms wrap it); an E/W arm runs N-S as tall as the house. The depth `d` is how many trees deep the
        stand is - sized so the whole grove is the LARGEST homestead appurtenance (bigger than the house);
        `lf` shortens the arm's run to slip a partial belt past a close neighbor. See settlements.md 'Homestead
        groves' (Historical scale)."""
        if fdy:  # N or S arm (runs E-W); wraps `perp` toward the windward corner
            return hx + perp * d / 2, hy + fdy * (hh / 2 + d / 2 + gap), (hw + d) * lf, d
        return hx + fdx * (hw / 2 + d / 2 + gap), hy, d, hh * lf  # E or W arm (runs N-S)

    def _grove_fits(self: Settlement, x: float, y: float, w: float, h: float, own: Any) -> bool:  # type: ignore[misc]
        """A grove fits where it is in-bounds, on DRY ground (trees do not grow IN a flooded paddy - but a real
        homestead grove HUGS the paddy bund, so the footprint may abut a field, it just may not overlap it),
        off any lane, and clear of every placed footprint EXCEPT its OWN house. Axis-aligned, so an exact AABB
        test serves - not the conservative half-diagonal circle, which would over-reject the elongated bands."""
        if x < 55 or x > self.W - 55 or y < 88 or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):
            return False
        if self._near_corridor(x, y):  # NOT `_in_blocked`: a grove may sit right at the
            return False  # paddy edge (the 14px field set-back is for buildings, not the windbreak)
        if self._rect_hits((x, y, w, h), self.field_polys):  # the whole grove stays OUT of the flooded paddy
            return False  # (same corner/vertex/edge test, with the bbox pre-filter)
        if self._rect_hits((x, y, w, h), self.dry_polys):  # ...and out of the dry crop strips (hems / garden
            return False  # tracts): trees do not grow in the barley either
        for px, py, pw, ph, *_ in self.placed:  # clear of every footprint but its OWN homestead
            if any(abs(px - ox) < 1.5 and abs(py - oy) < 1.5 for ox, oy in own):
                continue
            if abs(x - px) < (w + pw) / 2 + 2 and abs(y - py) < (h + ph) / 2 + 2:
                return False
        # the town RAMPART blocks a belt arm at the FOOTPRINT level: the corridor test above is
        # center-only, so a wide arm centered clear of the wall could still lap the stroke
        # (first hit: a Hirameki farm's west arm crossing the east face, 2026-07)
        wallp = self.M.get("wall")
        if wallp and any(
            seg_dist(gx, gy, wallp[k], wallp[k + 1]) < 12 for gx, gy in ((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)) for k in range(len(wallp) - 1)
        ):
            return False
        # a threshing yard needs clear sky to its SOUTH (the drying sun); a grove squarely in that sun-corridor
        # would shade it, so keep the grove out of the narrow strip directly south of any yard. (Its OWN grove
        # is N/W, far from its own yard's southern corridor, so this only steers it off a NEIGHBOR's yard.)
        for yd in self.M.get("threshing_yards", []):
            cyx, cyy = yd["x"], yd["y"] + yd["h"] / 2 + 11  # corridor center: a ~22px-deep strip south of the yard
            if abs(x - cyx) < (w + yd["w"]) / 2 and abs(y - cyy) < (h + 22) / 2:
                return False
        return True

    GROVE_RATIO = 6.0  # target grove footprint as a multiple of the house (~6:1 - see settlements.md Historical scale)

    def _find_grove_arms(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> list[Any]:  # type: ignore[misc]
        """The windward grove's belt arms, AREA-TARGETED to ~GROVE_RATIO x the house footprint (the historical
        ~6:1). Each windward face (N + W for an NW wind) is grown to the deepest belt that fits; if the total
        still falls short of target - because a paddy or neighbor blocks one face - the OTHER, open arm is
        deepened to compensate, so a typical farm's grove still reaches the full ~6:1 and reads as ~40 trees.
        A farm boxed in on BOTH windward faces gets only what fits (a small grove - the genuinely cramped
        minority). Arms are NOT in `placed`, so adjacent groves abut into one continuous windbreak. Returns a
        list of (cx, cy, w, h, face)."""
        target = self.GROVE_RATIO * hw * hh
        own = [(hx, hy)]
        d0 = 1.4 * hh  # base belt depth; the loop deepens to hit the area target
        dcap = 3.6 * hh  # an open arm may deepen this far to cover a blocked one
        dmin = 12 * self.bscale
        step = max(2.0, 0.16 * hh)
        depths: list[Any] = []  # [[(fdx,fdy), perp, depth], ...]
        for (fdx, fdy), perp in self._GROVE_ARMS[self._windward()]:
            d = d0
            placed_arm = False
            while d >= dmin:  # deepest full-width arm <= d0 that fits this face
                cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5)
                if self._grove_fits(cx, cy, w, h, own):
                    depths.append([(fdx, fdy), perp, d, 1.0])
                    placed_arm = True
                    break
                d -= step
            if not placed_arm:  # tight face: a NARROW clump still reads as a windbreak
                d = d0
                while d >= dmin:
                    cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, 0.55)
                    if self._grove_fits(cx, cy, w, h, own):
                        depths.append([(fdx, fdy), perp, d, 0.55])
                        break
                    d -= step

        def total_area() -> float:
            rects = [self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, lf) for (fdx, fdy), perp, d, lf in depths]
            return _union_area([(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2) for cx, cy, w, h in rects])

        guard = 0
        while depths and total_area() < target and guard < 300:  # compensate: deepen the open arm(s)
            grew = False
            for arm in depths:
                if arm[2] >= dcap:
                    continue
                nd = min(dcap, arm[2] + step)
                cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, arm[0][0], arm[0][1], arm[1], nd, 1.5, arm[3])
                if self._grove_fits(cx, cy, w, h, own):
                    arm[2] = nd
                    grew = True
                    if total_area() >= target:
                        break
            if not grew:
                break
            guard += 1
        return [(*self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, lf), (fdx, fdy)) for (fdx, fdy), perp, d, lf in depths]

    def _grove_room(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> bool:  # type: ignore[misc]
        """Whether at least a MINIMAL grove clump fits on the windward side - used by the homestead solver to
        prefer a house position that leaves room for a grove (the actual, possibly larger, grove is placed in
        the second pass). Mirrors the minimal footprint the `_find_grove_arms` ladder falls back to."""
        for (fdx, fdy), perp in self._GROVE_ARMS[self._windward()]:
            cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, 13 * self.bscale, 1.5, 0.5)
            if self._grove_fits(cx, cy, w, h, [(hx, hy)]):
                return True
        return False

    def _draw_grove(self: Settlement, cx: float, cy: float, w: float, h: float, face: Any, mix: str = "windbreak", cls: str | None = None) -> None:  # type: ignore[misc]
        """Draw one windbreak/grove clump as a DENSE MIXED STAND - overlapping canopies packed into a real
        grove (not a few scattered trees), of three species: tall EVERGREEN conifer (dark, dense apex - the
        windbreak backbone, cedar/pine), DECIDUOUS broadleaf (mid green - timber and fruit, zelkova/persimmon),
        and (nominally) a BAMBOO clump - see the note at the item loop: `b_th` is 0.0 in both mixes, so no
        clump has ever drawn one. `mix` picks the species blend: 'windbreak' is
        conifer-backed (the sheltering wall - the yashikirin and the fengshui back belt); 'dooryard' is bamboo
        + fruit broadleaf with NO conifer (the leafy bamboo/fruit greenery scattered among village houses).
        Distinct from the big s.forest area feature and the striped kitchen-garden bed. Species and placement
        are seeded by position (stable across regenerations). Canopy count scales with footprint area."""
        # SCOPED (2026-08-08): a homestead grove's crowns are decoration keyed to the grove itself.
        with self.rng_scope("grove", cx, cy, w, h):
            bs = self.bscale / 0.82  # render scale relative to the town grain
            st = random.getstate()
            random.seed(int(abs(cx) * 5 + abs(cy) * 3 + round(w)))
            n = max(5, min(28, round(w * h / (bs * bs * 48))))  # ~ one crown per ~48 px^2 at 2 ft/px (a ~5 m crown); ~40 across the 6:1 L-grove
            # BAMBOO LEFT THE MIX (feature 133 T47, GM 2026-08-27). It used to be 20% of a windbreak's
            # crowns and 45% of a dooryard copse's, drawn one culm at a time - 315 six-foot glyphs on
            # Inashiro that no one could see as bamboo, and not how bamboo grows: a stand is a clonal
            # thicket with a hard edge, not a seasoning through a cedar belt. Bamboo is now its own
            # feature (`bamboo_stand`, the `bamboo` knob). The windbreak is cedar-backed with broadleaf;
            # the dooryard copse is fruit broadleaf. The culm glyph below is kept for the record and is
            # unreachable at these thresholds.
            b_th, c_th = (0.0, 0.38) if mix == "windbreak" else (0.0, 0.0)  # dooryard = fruit broadleaf, no conifer
            items: list[Any] = []
            for _ in range(n):
                px = random.uniform(-w / 2 + 2, w / 2 - 2)
                py = random.uniform(-h / 2 + 2, h / 2 - 2)
                roll = random.random()
                kind = "bamboo" if roll < b_th else ("conifer" if roll < c_th else "broadleaf")
                size = random.uniform(1.25, 1.7) if random.random() < 0.25 else random.uniform(0.72, 1.05)  # a few emergent crowns over many small
                items.append((px, py, kind, size))
            # ORDER-SENSITIVE: this reads M, so it can only avoid structures that ALREADY EXIST when the
            # grove is drawn. That is why the yashikirin arms draw after their farmstead's house and why
            # village_grove() is called late in a gen (see "DRAW ORDER" in CLAUDE.md before moving either).
            # NO CROWN ON A ROOF OR A WELLHEAD (GM 2026-07-25). A yashikirin belt is drawn hard against the
            # house it shelters and a village copse threads between the dwellings, so the stand is filtered
            # tree-by-tree rather than pushed back as a whole: it THINS where it would cover a building and
            # keeps its shape everywhere else. Crown centers below are relative to (cx, cy); keep-outs absolute.
            # THE PREFILTER MUST REACH AS FAR AS A CROWN DOES (feature 134 T50, 2026-08-29). Both lists
            # below are PREFILTERED to this box, and the pad was a flat `9 * bs` while a crown's own
            # radius is `px(CANOPY_R_FT) * s * 1.15` with `s` as high as 1.7 - about 14.5 px on a hamlet.
            # So a building standing 10-14 px outside the stand's box was not in `krect` at all, and
            # `_crown_covers` then cleared a crown that plainly covered it: cohort seed 9's farmhouse at
            # (1938, 2655) sat under a 14.4 ft crown from a copse whose box ended 10.7 px short of it,
            # and `structures_clear_of_trees` read it correctly. A prefilter that prunes a candidate the
            # test would have rejected is not an optimization, it is a silent wrong answer - the same
            # rule this engine states for every other index ("the index prunes; it never decides").
            _cpad = max(9.0 * bs, self.px(self.CANOPY_R_FT) * 1.7 * 1.15 + 1.0)
            krect, kcirc = self._canopy_keepouts((cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad))
            _near = self._crowns_near(cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad)  # the crowns of earlier clumps and stands (GM 2026-08-28)
            drawn: list[tuple[float, float, float]] = []
            g = [f'<g transform="translate({cx:.0f},{cy:.0f})">']
            # Draw back-to-front so the stand layers with depth. Each CROWN is one tree at real size (~5-6 m; a few
            # emergents larger) - that is the to-scale reading, and it is unchanged. We deliberately DROP two kinds
            # of detail that cost ~half the stand's SVG elements without buying scale accuracy: the per-tree trunk
            # (hidden under the closed canopy anyway), and the 6-culm bamboo clump - a real *take* is DOZENS of
            # culms, so any handful is already symbolic, and one compact culm+top reads the same. See the foliage
            # comparison (the 'to scale, compact bamboo' option) for the before/after; groves stay to scale, the
            # SVG + rsvg raster roughly halve.
            for px, py, kind, s in sorted(items, key=lambda t: t[1]):
                # THE BAMBOO ITEM WAS UNREACHABLE (feature 146). `b_th` is 0.0 for BOTH mixes above, so
                # `roll < b_th` never held and no grove clump has ever drawn a culm - while the comment above
                # still described bamboo as one of the stand's three species. Six lines of code the maps could
                # not reach, removed rather than tested. If the bamboo IS wanted in the blend the fix is a
                # non-zero `b_th`, which moves every grove on every map and belongs to a feature that owns the
                # look; recorded in future-work/farming-communities.md so the intent is not lost with the code.
                # ONE CROWN AT THE RESEARCHED SIZE (GM 2026-08-28, feature 134 T36). This was `(4.6 | 4.0) * s * bs`,
                # a pixel radius calibrated at the village's 2 ft/px ("a ~5-6 m canopy") and never rescaled by ftpx:
                # at the hamlet's 1 ft/px the belt drew 9 ft crowns beside the commons' 18 ft ones (measured on
                # Inashiro: belt median r 4.5 ft, commons 9.0). Now the same CANOPY_R_FT the woods and the commons
                # use, in real feet (research/vegetation.md 'Forest density and crown size'); a conifer 15% wider,
                # the old ratio. A village (ftpx 2, bscale 1) gets 4.25 px, within a pixel of what it drew before.
                rr = self.px(self.CANOPY_R_FT) * s * (1.15 if kind == "conifer" else 1.0)
                col = "#496733" if kind == "conifer" else random.choice(["#7C9A4E", "#6E8B43"])
                if self._crown_covers(cx + px, cy + py - 3 * bs, rr, krect, kcirc, self.CANOPY_PAD):
                    continue
                if not self._crown_seat_clear(cx + px, cy + py - 3 * bs, rr, _near) or not self._crown_seat_clear(cx + px, cy + py - 3 * bs, rr, drawn):
                    continue  # a crown centered under an already-drawn crown is an understory stem, not canopy (GM 2026-08-28; woods._crown_seat_clear)
                drawn.append((cx + px, cy + py - 3 * bs, rr))
                g.append(f'<circle cx="{px:.1f}" cy="{py - 3 * bs:.1f}" r="{rr:.1f}" fill="{col}" stroke="#3C5526" stroke-width="0.8"/>')
                if kind == "conifer":
                    g.append(f'<circle cx="{px:.1f}" cy="{py - 3 * bs:.1f}" r="{rr * 0.4:.1f}" fill="#364D22" opacity="0.55"/>')  # dense dark apex
            g.append('</g>')
            self.add(''.join(g), cls=cls)
            self._record_crowns(drawn)
            random.setstate(st)
