"""The deferred farmstead flush: what actually gets DRAWN, and in what order. This is the module the DRAW ORDER contract is about.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: draw-order and footprint plumbing - NONE: the order things are drawn in and the footprints they are tested by decide nothing
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from .._geom import Indexed
from ..farm_fixtures import PERSIMMON_CROWN_FT
from ..homestead_parts.groves import GROVE_BAMBOO_PATCH_FT, GROVE_CLUMP_CROWNS, HOUSEHOLD_BAMBOO_PREVALENCE, bamboo_patch, band_clumps, grove_crown_px2
from ..homestead_parts.tree_shade import BAMBOO_SHADE_FT, CANOPY_SHADE_FT, crown_shades
from .dispersed import THIN_BAND_FT
from .fit import part_box

if TYPE_CHECKING:
    from ..core import Settlement


def beds_sun_clear(beds: Any, crowns: Any, trees: Any, marks: Any, reach: float, bamboo_reach: float) -> bool:
    """Is the sun ground of every bed in `beds` (drawn boxes, center x, center y, w, h) clear of every standing crown (`crowns`, the
    flat [x, y, r, ...] run of `tree_crowns`), every tree promised a seat (`trees`, (x, y, r)) and every bamboo mark (`marks`,
    [x, y, r]) - the trees at `reach`, the bamboo at `bamboo_reach`? (Feature 315: a garden nudged south after the groves stand
    must not move its sun ground over a tree the sun rule already kept off its old place - cohort seed 14.)

    Research: bed sun ground clear of crowns and promised trees at reach, bamboo at bamboo_reach - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no crown, promised tree or bamboo within 50 ft east, west or south of a bed"""
    discs = [(float(crowns[i]), float(crowns[i + 1]), float(crowns[i + 2])) for i in range(0, len(crowns) - 2, 3)] + [tuple(t) for t in trees]
    return not any(crown_shades(x, y, r, b, reach) for b in beds for x, y, r in discs) and not any(crown_shades(float(m[0]), float(m[1]), float(m[2]), b, bamboo_reach) for b in beds for m in marks)


def thinned(cx: float, cy: float, w: float, h: float, face: Sequence[int], depth: float) -> tuple[float, float, float, float]:
    """A grove band cut to `depth` across its face, keeping its inner edge - the side toward its house - where it stood: a row
    farm the grove row across its street shelters draws its windward grove one tree deep on the ground its full band was
    seated with (feature 374 wave 153; seated and laid as every farm, so the seating and the ways are the full form's).

    Research: a thin windward grove - research/questions/0033-row-villages-resson.drawing.html: Ogawa's farm, its road on the north, kept its north grove "rather thin"; one tree deep, the thin band's depth (`THIN_BAND_FT`), a GUESS"""
    fx, fy = float(face[0]), float(face[1])
    if abs(fy) >= abs(fx):  # a north or south band: cut across its height, its edge toward the house kept
        d = min(depth, h)
        return (cx, cy - fy * (h - d) / 2, w, d)
    d = min(depth, w)
    return (cx - fx * (w - d) / 2, cy, d, h)


class FarmsteadFlushMixin:
    def farmsteads(self: Settlement) -> int:  # type: ignore[misc]
        """Draw every farmstead: the reserved homestead BUNDLES (the house-first path a map not drawn to scale took went with
        the frozen maps' code, feature 392). Call once every homestead is seated - a hamlet's homestead stage -
        so the bundles are final. Returns the farmhouse count."""
        with self.rng_scope("farmsteads"):
            # ONE scope for the whole rural flush: yards, gardens, groves and kura sides are one
            # phase, and splitting them would only make a change to one perturb the others.
            return self._farmsteads_bundle()

    def _farm_rolls_bamboo(self: Settlement, hx: float, hy: float) -> bool:  # type: ignore[misc]
        """Does the farm at (hx, hy) keep a household bamboo stand (feature 291)? The same positional roll the household
        bamboo pass makes (`hamletgen/homesteads/bamboo.py`), under the settlement's `bamboo` knob as the generator sets
        it (`_household_bamboo`); a map that never set it - the hand-drawn tiers - keeps the windbreak's bamboo as before.

        Research: farms keeping their own bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html: about three in five, rolled per position, under the settlement's bamboo knob
            its salts, guards and sentinels - NONE: they decide nothing about the place - 95 (jitter salt (bamboo prevalence))
        """
        on = getattr(self, "_household_bamboo", None)
        return True if on is None else bool(on) and self._hjit(hx, hy, 95.0) < HOUSEHOLD_BAMBOO_PREVALENCE

    def _farmsteads_bundle(self: Settlement) -> int:  # type: ignore[misc]
        """Draw every reserved homestead bundle: grove (back) -> yard -> garden -> house (on top). The hard
        work (fitting each whole bundle without overlap) already happened in try_place, one at a time, so
        this pass is pure drawing. Abandoned ruins (no bundle) draw as a lone house. Call LAST. Returns the
        farmhouse count.
        Two sub-passes so the garden EAST-shade nudge can see every neighbor's grove: (1) draw all per-house
        GROVES (the back layer), (2) after a south-nudge relaxation, draw the yards/gardens/houses on top.

        Research:
            no tree over a building - NONE: the grove bands drawn last, so `_draw_grove`'s keep-outs (0071's drawing page) see the houses
            thin band's lesser trees - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: fruit and flowering broadleaf, no conifer (the mix labeled a GUESS)
            band drawn at one density - NONE: a band cut along its length into pieces of 28 crowns' ground; the density is `GROVE_CROWN_SQFT`'s (0080), not the cut's
            canopy edge at the band's inner edge - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the drawn band gives up one crown radius on the house's side, keeping the service strip clear
            bamboo patch in the windward bands - research/questions/0075-bamboo-groves-chikurin.drawing.html: 22 x 16 ft on the house side of each windward band
            a sheltered row farm's grove - research/questions/0033-row-villages-resson.drawing.html, research/questions/0075-bamboo-groves-chikurin.drawing.html: its windward bands drawn one tree deep (`thinned`, a GUESS) and no bamboo in them - its bamboo is its band to the south
        """
        survivors: list[Any] = []
        bundled: list[Any] = []
        arms: list[tuple[float, float, float, float, tuple[int, int], str, bool]] = []
        for rec in self._pending_farmsteads:
            geom = rec.get("geom")
            if geom is None:  # abandoned ruin / dispersed headman: lone house
                self.house(rec["x"], rec["y"], rec["w"], rec["h"], rec["kind"], rec["rot"])
                survivors.append(rec)
                continue
            # EVERY BAND OF THE FARM'S OWN GROVE, on every side its settlement rolled (feature 291); a nucleated bundle
            # carries none. `depth` says which is the windward stand and which a thin band of lesser trees.
            # ...BUT A ROW FARM THE GROVE ROW ACROSS ITS STREET SHELTERS keeps its bamboo along its south side, not in its thin
            # windward grove (feature 374 wave 153, 0033: Ogawa's farm, its north grove thin, its bamboo all along its south)
            _bamboo = not rec.get("sheltered") and self._farm_rolls_bamboo(rec["x"], rec["y"])
            for (cx, cy, w, h), (face, depth) in zip(geom.get("groves") or (), geom.get("grove_faces") or (), strict=True):
                if rec.get("sheltered") and depth == "deep":
                    cx, cy, w, h = thinned(cx, cy, w, h, face, self.px(THIN_BAND_FT))
                arms.append((cx, cy, w, h, face, depth, _bamboo))
                self.M["groves"].append(
                    {"x": round(cx, 1), "y": round(cy, 1), "w": w, "h": h, "rot": 0, "of": [rec["x"], rec["y"]], "face": list(face), "depth": depth, "bamboo": _bamboo and depth == "deep"}
                )
                self.grove_rects.append((cx, cy, w, h))
            bundled.append(rec)
            survivors.append(rec)
        self._relax_gardens_south(bundled)  # nudge east-shaded gardens a little S (all groves now known)
        for rec in bundled:
            geom = rec["geom"]
            if geom.get("yard") is not None:
                self._attach_yard(rec["x"], rec["y"], geom["yard"], rec["rot"])
            self._attach_garden(rec["x"], rec["y"], geom["gardens"], rec["rot"])
            self.house(rec["x"], rec["y"], rec["w"], rec["h"], rec["kind"], rec["rot"], shed=rec["shed"], shed_side=rec.get("shed_side", "W"))
        # The yashikirin arms DRAW LAST, after every house/shed of this pass is down (GM 2026-07-25).
        # They used to draw first, as a back layer the house painted over - which hid the overlap
        # rather than preventing it, and left crowns geometrically under roofs. Drawing them after
        # means _draw_grove's keep-out sees the houses, so the belt THINS off the walls instead: no
        # tree is drawn over a building anywhere on the map, by one rule rather than by z-order.
        # (The arm rects themselves are recorded above, before _relax_gardens_south, which needs them.)
        # A THIN BAND draws as lesser trees - fruit and flowering broadleaf, no conifer (`dooryard`; Tonami's sides away
        # from the wind carried flowering trees, persimmon and fig, and hackberry and alder): the mix a GUESS (feature 291).
        # ...AND A BAND IS DRAWN AS CLUMPS OF ONE CLUMP'S SIZE (feature 291, the settlement-review of Kashikawa): `_draw_grove`
        # once capped a clump at 28 crowns, so a deep band drew at 0.57 of its box under canopy against the thin band's 0.78.
        # The cap is gone (each clump throws one crown to ~180 sq ft, `GROVE_CROWN_SQFT`, 0080), so the density is the
        # constant's; the cut into pieces of 28 crowns' ground is kept as plumbing - each piece its own scoped roll.
        _cap = GROVE_CLUMP_CROWNS * grove_crown_px2(self.ftpx)
        # ...WITH ITS CANOPY'S EDGE, NOT ITS TRUNKS, AT THE BAND'S INNER EDGE: a clump seats its crowns' centers inside its box,
        # so a crown overhung the service strip by its radius, and once the bands drew at their full density a wood shed's
        # seat there was under a crown (Mizuguchi seated 4 of 5). The drawn box gives up one crown radius on the house's side.
        _inset = self.px(self.CANOPY_R_FT)
        for cx, cy, w, h, face, depth, has_bamboo in arms:
            fx, fy = (float(face[0]), float(face[1])) if face else (0.0, 0.0)
            cx, cy = cx + fx * _inset / 2, cy + fy * _inset / 2
            w, h = max(4.0, w - abs(fx) * _inset), max(4.0, h - abs(fy) * _inset)
            # ...AND A FARM THAT ROLLED BAMBOO KEEPS A PATCH OF IT IN EACH WINDWARD BAND (`GROVE_BAMBOO_PATCH_FT`)
            _patch = bamboo_patch(cx, cy, w, h, (fx, fy), self.px(GROVE_BAMBOO_PATCH_FT[0]), self.px(GROVE_BAMBOO_PATCH_FT[1])) if has_bamboo and depth == "deep" else None
            for px_, py_, pw, ph in band_clumps(cx, cy, w, h, _cap):
                self._draw_grove(px_, py_, pw, ph, face, mix="windbreak" if depth == "deep" else "dooryard", cls="homestead grove", bamboo=has_bamboo, bamboo_box=_patch)
        self.M["houses"] = Indexed(
            [h for h in self.M["houses"] if h.get("on_dike")] + survivors
        )  # dike-top houses (dike_top_houses) are not pending farmsteads - keep them; Indexed for the fit rules' index
        return len(survivors)

    def _east_trees(self: Settlement, gx1: float, own: Any) -> list[Any]:  # type: ignore[misc]
        """The y-intervals (y0, y1) of every per-house grove arm standing hard against a garden's EAST - west
        edge within a shade band east of the garden's east edge `gx1`. `own` is the garden's OWN grove arms
        (which sit N/W, never east), excluded. The garden's x is fixed as it shifts S, so this set is stable.

        Research:
            east shade band - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a neighbor's grove just east of a garden shades it
            east shade band width - research/questions/0038-sunlight-and-shade-on-the-farm.html: a tree shades the ground to its east one tree's height (the Qimin Yaoshu), about 33 ft, and the drawing page 50 ft - the band is 22 ft, a departure the code keeps until feature 417 T33; the reach 22 px (`bscale`) east of the garden's east edge, a figure 0038 does not give
            its salts, guards and sentinels - NONE: they decide nothing about the place - 1.5 (tolerance for matching the garden's own grove arms)
        """
        band = 22 * self.bscale
        out: list[Any] = []
        for tx, ty, tw, th in self.grove_rects:
            if any(abs(tx - ox) < 1.5 and abs(ty - oy) < 1.5 for ox, oy, _, _ in own):
                continue  # skip the garden's own grove arms
            west = tx - tw / 2
            if gx1 - 2 <= west < gx1 + band:
                out.append((ty - th / 2, ty + th / 2))
        return out

    def _garden_beds_clear(self: Settlement, beds: Any, others: Any) -> bool:  # type: ignore[misc]
        """Whether a set of shifted garden beds land on clear ground: each bed off blocks/fields/water/lanes
        (`_rect_blocked`), and clear of every ACTUAL footprint in `others` (neighbors' houses/yards/gardens/
        groves + the garden's own house + yard). Tests real footprints, NOT the loose reserved bundle bboxes -
        a garden may shift into a neighbor's empty bbox margin, it just may not touch a drawn structure."""

        def hit(a: Any, b: Any) -> bool:
            return cast(bool, abs(a[0] - b[0]) < (a[2] + b[2]) / 2 and abs(a[1] - b[1]) < (a[3] + b[3]) / 2)

        for bed in beds:
            if self._rect_blocked(bed, fields=True):
                return False
            if any(hit(bed, r) for r in others):
                return False
        return True

    def _relax_gardens_south(self: Settlement, recs: Any) -> None:  # type: ignore[misc]
        """OPTION (villages where each house has its own windward grove and the garden goes on the E/lee side):
        once every yashikirin is drawn, a garden left with a NEIGHBOR'S grove hard against its EAST loses the
        morning sun. Where there is open ground, nudge that garden a little SOUTH so the tree falls to its NE
        and the eastern sky opens - the GM's 'move it a bit south' remedy. Best-effort: a garden boxed in to the
        south stays put (gardens_unshaded_from_east flags only the AVOIDABLE ones). See research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html ('gardens'.

        Research: east-shaded garden nudged south - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: best effort, 4 px steps up to the bed's height plus the house's plus 6 px
            own deep windward stand exempt from the east test - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the nudge is for a NEIGHBOR's grove hard against a bed's east, the windbreak standing on the wind's side; the farm's own thin grove band east of the bed is tested too - GUESS (feature 291)
            nudged bed off every footprint - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: nudged south into open ground - no house, yard, bed or grove of any homestead under the bed once nudged (`_garden_beds_clear`)
            nudged bed's sun ground clear of crowns, promised persimmons and bamboo - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 50 ft clear (CANOPY_SHADE_FT, BAMBOO_SHADE_FT)
        """
        step = 4 * self.bscale

        def footprints(exclude: int) -> list[Any]:
            """Every homestead's real house/yard/garden/grove rects, minus the rec at index `exclude`."""
            out: list[Any] = []
            for j, r in enumerate(recs):
                if j == exclude:
                    continue
                g = r["geom"]
                out.append(tuple(part_box(g, "house")))  # every footprint as drawn, turned with its house (269 B18)
                if g.get("yard") is not None:
                    out.append(tuple(part_box(g, "yard")))
                out += [tuple(b) for b in part_box(g, "gardens") or []]
                out += [tuple(b) for b in g.get("groves") or ()]
            return out

        def overlaps(a: Any, b: Any) -> bool:
            return cast(bool, a[0] < b[1] and b[0] < a[1])

        for i, rec in enumerate(recs):
            geom = rec["geom"]
            beds = geom.get("gardens")
            if not beds:
                continue
            # ONLY THE OWN WINDWARD STAND is exempt from the east test: it stands on the wind's side, off the garden by
            # construction. A thin band of its own grove may stand east of it, and is tested like a neighbor's (feature 291).
            own = [r for r, (_f, depth) in zip(geom.get("groves") or (), geom.get("grove_faces") or (), strict=True) if depth == "deep"]
            gx1 = max(b[0] + b[2] / 2 for b in beds)
            gcy = sum(b[1] for b in beds) / len(beds)
            gh = max(b[1] + b[3] / 2 for b in beds) - min(b[1] - b[3] / 2 for b in beds)
            trees = self._east_trees(gx1, own)
            if not any(overlaps((gcy - gh / 2, gcy + gh / 2), t) for t in trees):
                continue  # not currently east-shaded - nothing to do
            maxshift = gh + rec["h"] + 6  # 'a little' - stays a dooryard garden near the house
            reach, bamboo_reach = self.px(CANOPY_SHADE_FT), self.px(BAMBOO_SHADE_FT)
            # the trees near enough to matter, gathered once per garden: within the shift, the reach and the largest crown
            span = maxshift + max(reach, bamboo_reach) + 3.0 * self.px(PERSIMMON_CROWN_FT)
            bx0, bx1 = min(b[0] - b[2] / 2 for b in beds) - span, max(b[0] + b[2] / 2 for b in beds) + span
            by0, by1 = min(b[1] - b[3] / 2 for b in beds) - span, max(b[1] + b[3] / 2 for b in beds) + span
            tc = self.M.get("tree_crowns") or []
            near_crowns = [v for i in range(0, len(tc) - 2, 3) if bx0 <= tc[i] <= bx1 and by0 <= tc[i + 1] <= by1 for v in tc[i : i + 3]]
            near_marks = [m for m in self.M.get("bamboo_marks") or () if bx0 <= m[0] <= bx1 and by0 <= m[1] <= by1]
            promised = [(t[0], t[1], self.px(PERSIMMON_CROWN_FT + 1.0)) for r in recs if (t := (r["geom"].get("fixtures") or {}).get("persimmon")) is not None]
            others = footprints(i) + [tuple(part_box(geom, "house"))] + ([tuple(part_box(geom, "yard"))] if geom.get("yard") is not None else []) + [tuple(b) for b in geom.get("groves") or ()]
            dy = step
            while dy <= maxshift:
                lane = (gcy + dy - gh / 2, gcy + dy + gh / 2)  # clear of EVERY east tree (a small shift can slip INTO a taller arm)
                if not any(overlaps(lane, t) for t in trees):
                    shifted = [(b[0], b[1] + dy, b[2], b[3]) for b in beds]
                    drawn = [(b[0], b[1] + dy, b[2], b[3]) for b in part_box(geom, "gardens")]
                    # ...and its new sun ground clear of every crown already drawn, every persimmon promised a seat and every bamboo
                    # mark (feature 315; cohort seed 14: a bed nudged 8 ft south took a neighbor's persimmon into its sun)
                    if self._garden_beds_clear(drawn, others) and beds_sun_clear(drawn, near_crowns, promised, near_marks, reach, bamboo_reach):
                        geom["gardens"] = shifted
                        if "boxes" in geom:
                            geom["boxes"]["gardens"] = drawn  # the beds' drawn boxes move with them
                        houses = self.M.get("houses")
                        if hasattr(houses, "touch"):  # the beds moved inside a record: the plots' sun boxes are keyed on this version (feature 387)
                            houses.touch()
                        break
                dy += step
