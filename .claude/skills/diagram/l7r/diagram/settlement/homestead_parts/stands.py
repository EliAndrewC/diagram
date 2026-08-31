"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly, seg_dist
from ._helpers import _BELT_GAP_FT, _belt_axis

if TYPE_CHECKING:
    from ..core import Settlement


class StandsMixin:
    def bamboo_stand(self: Settlement, poly: Any, role: str = "homestead") -> int:  # type: ignore[misc]
        """A BAMBOO STAND - a take-yabu: a clonal thicket with a hard edge, drawn as a STAND-LEVEL glyph
        (feature 133 T47, GM 2026-08-27; research/vegetation.md "Bamboo: how common, where it stood, and
        how to show it").

        THE GLYPH IS A DELIBERATE DEVIATION FOR LEGIBILITY, recorded like the oversized wellhead: a culm is
        inches across and cannot be drawn at 1 px = 1 ft, so the stand's POSITION and EXTENT (`poly`) are to
        scale and the marks inside it are symbolic - the convention Japan's own GSI topographic legend uses,
        a distinct bamboo-grove symbol beside the broadleaf and conifer ones, so a reader can tell the three
        apart at map scale. Each mark is a pair of culm strokes with a leafy fork, in bamboo's pale
        yellow-green, on a jittered grid dense enough to read as one block at fit zoom; nothing is filled,
        per the no-solid-fill rule for cover. `role` is "homestead" (the damp N/W strip of the cluster) or
        "thicket" (the take-yabu at the field margin). Recorded in M['bamboo_stands'] (bbox + role + poly);
        the marks are decoration keyed to the stand (positional randomness)."""
        pts = [(float(a), float(b)) for a, b in poly]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        bs = self.bscale
        g = ['<g class="bamboo">']
        step = 7.0 * bs
        n = 0
        y = y0 + step * 0.5
        row = 0
        while y < y1:
            x = x0 + step * (0.5 if row % 2 == 0 else 1.0)
            while x < x1:
                jx, jy = x + (self._hjit(x, y, 91.0) - 0.5) * step * 0.6, y + (self._hjit(x, y, 92.0) - 0.5) * step * 0.6
                if point_in_poly(jx, jy, pts):
                    h = (5.0 + 3.0 * self._hjit(x, y, 93.0)) * bs  # a mark 5-8 ft tall: legible, not a tree
                    lean = (self._hjit(x, y, 94.0) - 0.5) * 1.6 * bs
                    # two culms leaning together, and a leafy fork at the top of the taller one
                    g.append(
                        f'<path d="M{jx - 1.2 * bs:.1f},{jy:.1f} l{lean:.1f},{-h:.1f} M{jx + 1.2 * bs:.1f},{jy:.1f} l{-lean * 0.6:.1f},{-h * 0.8:.1f}" stroke="#9AAE3C" stroke-width="{0.9 * bs:.2f}" fill="none" stroke-linecap="round"/>'
                    )
                    tx, ty = jx - 1.2 * bs + lean, jy - h
                    g.append(
                        f'<path d="M{tx:.1f},{ty:.1f} l{-2.2 * bs:.1f},{-1.6 * bs:.1f} M{tx:.1f},{ty:.1f} l{2.4 * bs:.1f},{-1.2 * bs:.1f} M{tx:.1f},{ty:.1f} l{0.4 * bs:.1f},{-2.6 * bs:.1f}" stroke="#B9CC5A" stroke-width="{0.8 * bs:.2f}" fill="none" stroke-linecap="round"/>'
                    )
                    n += 1
                x += step
            y += step * 0.86
            row += 1
        g.append("</g>")
        if n == 0:
            return 0
        z = self.add("".join(g), cls="homestead bamboo" if role == "homestead" else "shared bamboo grove")  # feature 150
        self.M.setdefault("bamboo_stands", []).append(
            {
                "x": round((x0 + x1) / 2, 1),
                "y": round((y0 + y1) / 2, 1),
                "w": round(x1 - x0, 1),
                "h": round(y1 - y0, 1),
                "rot": 0,
                "role": role,
                "z": z,
                "marks": n,
                "poly": [[round(a, 1), round(b, 1)] for a, b in pts],
            }
        )
        return n

    def village_grove(self: Settlement, poly: Any, role: str = "windbreak", dense: bool = True, within: tuple[float, float, float, float] | None = None, face_margin: float | None = None) -> int:  # type: ignore[misc]
        """A COMMUNAL village grove - the Chinese *fengshui* forest (风水林). Unlike the per-house *yashikirin*,
        a NUCLEATED village shelters behind ONE village-scale grove, in three roles (see settlements.md 'Village
        windbreak'):
          - `windbreak` - the dense belt on the WINDWARD/high BACK edge (后龙林 back-village grove); the winter-
            monsoon wall and the LARGEST vegetation feature. Nestles against and EMBRACES the cluster.
          - `water_mouth` - a smaller cluster of big old trees at the LOW entrance / water-mouth (水口林);
          - `copse` - the leafy bamboo / fruit-tree greenery scattered through the OPEN gaps among the houses.
        `poly` is the grove's FOOTPRINT - an IRREGULAR, terrain-following outline, NOT a rectangle (real groves
        hug the land and wrap the settlement, they are not ruled walls). It is FILLED with dense mixed-stand
        clumps on a jittered grid; a clump is SKIPPED wherever it would land on a HOUSE / threshing YARD /
        GARDEN / PADDY (so the wood settles into the open ground and hugs the cluster without ever drawing trees
        on a building or out in the crops - this is what lets the belt nestle right up to the village edge).
        `dense=True` packs overlapping clumps into a continuous belt/cluster; `dense=False` scatters them for the
        leafy fringe among houses. role tunes the species mix (windbreak/water_mouth = conifer-backed forest;
        copse = bamboo + fruit, no conifer). Recorded in M['village_groves'] (bbox + role + poly) IF any clump
        is drawn (a footprint entirely over houses/crops draws nothing and records nothing). Returns the count."""
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        mix = "windbreak" if role in ("windbreak", "water_mouth") else "dooryard"
        bs = self.bscale
        # 32, NOT 52, FOR A SPARSE STAND (feature 152 T09). A copse's job is to fill the gaps AMONG the
        # homesteads, and a 52 ft grid cannot see a 30 ft gap: Inashiro drew 2 clumps in a 98 x 313 ft
        # record and Mizuguchi 2 in a 205 x 58 one - two stray bushes recorded as a wood. The grid is the
        # only thing that decides where a clump is even TRIED, so a stand that has to thread a dense
        # cluster needs a finer one. It stays well coarser than the belt's 20 ft, which is what keeps a
        # copse reading as scattered trees rather than the canopy the windbreak draws.
        step = (20 if dense else 32) * bs
        clump = (28 if dense else 22) * bs
        # never draw a clump ON a home/yard/garden/byre/kura: keep the clump CENTER clear by the footprint's
        # circumscribing radius PLUS the clump's own drawn radius (clump/2) and a hair - so the tree blob settles
        # BESIDE the building, touching at most (grove_clumps_clear_of_structures gates it). (A grove may still hug
        # the eaves visually; the blob edge just may not cross the wall.) Was 0.35*clump - too small by ~0.15*clump,
        # which let a blob corner clip a small house.
        occ = [(o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.5 + 2) for k in ("houses", "threshing_yards", "gardens", "byres", "farm_sheds") for o in self.M.get(k, [])]
        # a WELL is a clean draw-point: no tree CANOPY may reach the wellhead (a well lost under the grove reads
        # wrong - wells_clear_of_trees gates it). Keep-out = the well's DRAWN half-size (vr) + the canopy reach
        # (~0.9*clump, as for a shrine), NOT the tight 0.35*clump a homestead eave gets. (o["r"] is the recorded
        # clearance radius; the DRAWN wellhead is vr, which is what a crown must not overhang.)
        occ += [
            (o["x"], o["y"], o.get("vr", o["r"]) + clump * 1.05 + 1.0) for o in self.M.get("wells", [])
        ]  # 1.05, not 0.90 (feature 145): a DRAWN crown runs to ~1.03 x clump (Kashikawa: 14.4 on a 14 clump reached a well 25.4 px away, vr 12.4), and the check measures the drawn crown
        # ...and NOT the notice board, which no longer exists when this runs (GM 2026-08-29). This
        # list used to give the kosatsuba a `30.0 + clump * 0.90` keep-out - about 55 ft, larger than
        # a well's and larger than a shrine's - so that a clump could not swallow the board or pierce
        # its caption. Two things retired it. The board is now the LAST thing placed on a hamlet, so
        # `M["kosatsuba"]` is empty here and the entry could only ever have matched nothing; and the
        # GM has ruled the clearing itself wrong: "it would be very easy to put the notice board at
        # the edge of the forest. We could even display it as being underneath the canopy because I
        # think in many cases it would be ... humans would not need to clear any amount of space in
        # order to put up a notice board at the side of a path." A village drives a plank in beside a
        # way; it does not fell 9,500 sq ft of its own shelter wood to do it. What protects the board
        # now is that it is sited last and can see the trees, not that the trees were kept off it.
        # A SHRINE and its TORII sit in a CLEAN clearing: no tree CANOPY may reach them (a hall/arch lost in the
        # wood reads wrong - shrine_clear_of_grove_trees / torii_clear_of_grove_trees gate it). The DRAWN canopy
        # overhangs the nominal clump radius (crowns spill past clump/2), reaching ~0.85*clump from the clump
        # center - so the keep-out uses that reach + a hair (0.90*clump), NOT the 0.35*clump a homestead uses
        # (there a grove may hug the eaves). A torii is recorded as [x, y, z]; glyph spans x +/-19, y -10..+18.
        occ += [(o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.90) for k in ("religious", "shrines") for o in self.M.get(k, [])]
        occ += [(t[0], t[1] + 4, math.hypot(19, 14) + clump * 0.90) for t in self.M.get("torii", [])]
        # ... and OFF the fengshui CRESCENT POND (GM 2026-07-21): no tree canopy may cross the half-moon
        # pond's water (trees_clear_of_fengshui_ponds gates it). The keep-out circle spans the FULL disk
        # (radius r + canopy reach) even though the water is only the away-facing half - the flat side toward
        # the village is the pond's open FORECOURT (the banyuetang fronted the settlement's ceremony/work
        # ground), so keeping the copse fringe off that band too is the historically right reading, not slack.
        occ += [(cp["cx"], cp["cy"], cp["r"] + clump * 0.90) for cp in self.M.get("crescent_ponds", [])]
        # ... and OFF THE POND - the tameike or a polder's header reservoir (feature 150: the first
        # scripted dike-pond seated its village at the block's head, so the windbreak's band ran
        # over the reservoir and 15 clumps stood in open water; nothing in this list knew the pond).
        # `M["pond"]` is [cx, cy, rx, ry]; the keep-out is the longer semi-axis + the canopy reach,
        # the same reading as the crescent pond above. `trees_clear_of_water` gates it.
        _pnd = self.M.get("pond")
        if _pnd:
            occ.append((float(_pnd[0]), float(_pnd[1]), max(float(_pnd[2]), float(_pnd[3])) + clump * 0.90))
        # ... and OFF A GROVE THAT IS ALREADY PLANTED (settlement-review x1, 2026-08-19). Nothing here
        # kept one grove out of another, and the copse is seated AFTER the windbreak, so it simply
        # planted itself in the belt: measured on Inashiro, clump-to-nearest-belt-clump distances of
        # 9, 8, 6, 4, 6, 4, 11, 9, 26, 30 and 83 ft against a belt clump radius of 14 - **10 of 11
        # copse clumps inside the belt's own canopy**, spanning x 1096-1188 while the houses span
        # 1108-1331. So the dooryards east of the front rank got no greenery at all and a whole
        # feature was invisible, while `settlements/vegetation.md` says outright that "the copse, not
        # the belt, fills the inner gaps".
        #
        # Sum of the two canopy reaches, so neither stand's ink laps the other. This also protects the
        # reverse order (a belt seated after a copse) without needing to know which ran first, and it
        # is why the keep-out is built from the RECORDED clumps rather than the grove's bbox - a belt's
        # bbox is a long rectangle whose corners are open ground the copse may legitimately use.
        # (the radius lives on the GROVE record, not the clump - a clump is a bare [x, y] pair)
        # Kept in its OWN list, not folded into `occ`, because `_reseat` has to tell this blocker
        # apart from the others - see the note there. (the radius lives on the GROVE record, not the
        # clump - a clump is a bare [x, y] pair)
        occ_grove = [(cl[0], cl[1], float(g.get("r") or 0.0) + clump * 0.90) for g in self.M.get("village_groves", []) for cl in (g.get("clumps") or [])]
        occ += occ_grove
        corr = self._corridor_buffers(clump * 0.45 + 4)  # ... and keep trees OFF the lanes / streets / road
        cr = clump / 2
        # ... and OUT of the SOUTHERN sun-corridor of every threshing yard + garden (a tree just south of them
        # blocks the drying/growing sun - +y is south). A touch wider than the check so it stays strictly clear.
        sun = [(o["x"], o["y"] + o["h"] / 2, o["w"] / 2 + cr + 2) for k in ("threshing_yards", "gardens") for o in self.M.get(k, [])]
        # ... and OUT of the EASTERN sun-lane of every kitchen GARDEN: a tree just east blocks the MORNING sun
        # (the sun rises in the E; +x is east), so a garden on a house's lee/E side keeps clear sky to its east.
        # Entry = (garden east edge, garden cy, half-height + reach). See gardens_unshaded_from_east.
        east = [(o["x"] + o["w"] / 2, o["y"], o["h"] / 2 + cr + 2) for o in self.M.get("gardens", [])]
        # ... and OUT of the WESTERN / SOUTHWESTERN sun-lane of every yard and garden - the AFTERNOON
        # sun (feature 133 T10, GM 2026-08-25). A belt is the tallest thing on the map: a working
        # igune measures ~10 m, and at 3pm in the shoulder month (sun at 28 deg, azimuth ~232) a
        # 33 ft belt throws ~63 ft of shadow to the NORTHEAST - ~50 ft of it eastward. So a
        # belt clump within `_west_sun_ft` of a plot's west edge, from the plot's north edge down to
        # `_west_sun_ft` below its south edge (the southwest, where the 3pm shadow starts), takes the
        # afternoon. Measured as a SQUARE, not a solar wedge, the same knowing departure the yard's
        # south corridor takes. WINDBREAK MIX ONLY: a copse clump is the dooryard's persimmon or
        # bamboo (3-10 m in the Sendai igune classes), and the record puts exactly those IN the
        # sunlit yard ("a persimmon in the yard center", Tonami model homestead) - so a dooryard
        # scatter is not held to a lane that a 10 m belt is. Opt-in via `west_sun_lane` (off on the
        # frozen pool); `village_trees_unshade_from_west` gates it. Derivation: research/homesteads.md.
        wl = float(getattr(self, "_west_sun_ft", 0.0)) if mix == "windbreak" else 0.0
        west = [(o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["y"] + o["h"] / 2) for k in ("threshing_yards", "gardens") for o in self.M.get(k, [])] if wl else []
        water_lines = [(st_["poly"], st_.get("w", 9) / 2) for st_ in self.M.get("streams", [])]
        water_lines += [(c_["poly"], c_.get("w", 2.5) / 2) for c_ in self.M.get("channels", [])]
        if self.M.get("moat"):
            water_lines.append((self.M["moat"], self.M.get("moat_width", 22) / 2))

        def _hard_blocked(qx: float, qy: float) -> bool:
            """Reasons a clump may not stand here that MOVING IT A FEW FEET DOES NOT CHANGE - the crop,
            open water, the dike bank. These are the edges a belt is supposed to stop at, so a clump
            refused for one of them is simply dropped; it never re-seats."""
            return (
                any(point_in_poly(qx, qy, f) or edge_dist(qx, qy, f) < 12 + cr for f in self.field_polys)
                or any(point_in_poly(qx, qy, d) or edge_dist(qx, qy, d) < 12 for d in self.dry_polys)
                or any(point_in_poly(qx, qy, dk["outline"]) for dk in self.M.get("dikes", []))
                or any(seg_dist(qx, qy, wl[k], wl[k + 1]) < whw + cr for wl, whw in water_lines for k in range(len(wl) - 1))
            )

        def _lane_blocked(qx: float, qy: float) -> bool:
            """A LANE only. Kept apart from the other local obstacles because the interior test below
            exists for exactly this case and for no other: a lane that ENDS at the belt is an edge the
            belt stops at, while one that RUNS THROUGH it is an obstacle to plant around, and
            interior-vs-rim is what separates them."""
            return any(seg_dist(qx, qy, lp[k], lp[k + 1]) < buf for lp, buf in corr for k in range(len(lp) - 1))

        def _local_blocked(qx: float, qy: float) -> bool:
            """LOCAL obstacles standing in the belt's line - a house, a yard, a wellhead's wide keep-out,
            a lane, a threshing yard's southern sun corridor, a garden's eastern light lane. A real
            planted belt is planted AROUND these, so an interior clump refused by one re-seats."""
            return (
                any((qx - ox) ** 2 + (qy - oy) ** 2 < rr * rr for ox, oy, rr in occ)
                or any(abs(qx - sx) < shw and se - cr - 2 < qy < se + 24 + cr for sx, se, shw in sun)
                or any(ex - cr - 2 < qx < ex + 24 + cr and abs(qy - ey) < ehh for ex, ey, ehh in east)
                # +1 ft of slack on the west sun-lane: the check reads clumps rounded to 0.1 with a strict `<`, and a
                # clump seated exactly on the window's edge (cohort seed 16: 1793.9 against 1794) read as shading
                or any(wx0 - wl - cr - 3 < qx < wx0 + cr + 1 and wy0 - cr - 1 < qy < wy1 + wl + cr + 1 for wx0, wy0, wy1 in west)
            )

        def _reseat(qx: float, qy: float, placed: list[Any], require_interior: bool) -> tuple[float, float] | None:
            """A DENSE belt flows around a local obstacle instead of losing the column.

            Which obstacles, and why this is not "re-seat around everything": a clump refused by the
            CROP, by open WATER or by a lane it merely abuts is refused for a reason that moving it a
            few feet does not change, and those are the edges where a belt is supposed to stop. What
            it DOES flow around is a local keep-out standing IN its line - a house, a yard, a
            wellhead (whose keep-out is the widest of the lot), a lane that CROSSES rather than
            abuts, and a threshing yard's southern sun corridor.

            The sun corridor is the case that motivated folding these three ad-hoc nudges into one
            helper (cohort seed 10, 2026-08-19). A yard's no-tree strip ran straight through the
            belt and left a 40 ft hole with a farmhouse directly downwind of it - the wall breached
            at the one place it was sheltering someone. It is not a crop edge and not a page edge;
            it is a local obstacle, and a real planted belt is planted around it. NOTE the earlier
            ledger entry blamed a pinch in `belt_polygon`; that was wrong - the band is a
            constant-depth ribbon, and the clumps were being filtered out, not left outside.

            Interior-only: a clump blocked near the polygon's own rim is at the belt's edge, where
            stopping is correct."""
            # INTERIOR ONLY FOR A LANE, and this cost seed 10 a round. The rule reads "a clump blocked
            # near the polygon's own rim is at the belt's edge, where stopping is correct" - true of a
            # lane, false of everything else. A belt is 110 px deep and a clump is 28, so demanding
            # `edge_dist > clump` leaves only the middle 54 px eligible: measured on seed 10, every
            # sun-corridor clump sat 2-27 px from a face and the search never ran. A yard's sun
            # corridor crosses the whole depth of the belt; where in that depth a given clump sits
            # says nothing about whether the belt should plant around it.
            # A SPARSE GROVE RE-SEATS TOO (settlement-review, Inashiro 2026-08-20). This used to read
            # `if not dense or (...)`, so only a belt flowed around an obstacle and a scatter's blocked
            # clump was dropped. That guard was written FOR the belt - the docstring above says so, "a
            # DENSE belt flows around a local obstacle instead of losing the column" - and the sparse
            # case was never considered. It is also backwards for what a copse is: the copse fills the
            # open gaps among the houses, so a clump refused because a house is there should try the
            # next gap. Finding the next gap IS the job; dropping the clump is the one response that
            # defeats the feature.
            #
            # Measured cost of the old behavior: Inashiro's copse collapsed to ONE clump inside a
            # declared 255 x 741 ft footprint once gate 0616 reserved ground around the belt's 227
            # clumps, and Mizuguchi's went 11 -> 4 earlier for the same reason (homesteads.py:248).
            # `village_groves_visibly_stocked` now fails a grove in that state.
            #
            # ONLY local obstacles reach here. `_hard_blocked` (crop, open water, the dike bank) still
            # drops the clump outright and must - those are the edges a stand is supposed to stop at,
            # and moving a few feet does not change them.
            # A SPARSE GROVE RE-SEATS ONLY WHEN ANOTHER STAND DISPLACED IT, and the narrowness is the
            # point. Blanket `not dense` re-seating was tried first and OVERSHOT badly: Inashiro's
            # copse went 1 -> 55 clumps and density across the four hamlets jumped to 10-15 per 100k
            # against a historical 3.9-4.4, which turns a dooryard scatter into a stand and defeats
            # the `dense` flag's whole purpose. A scatter is SUPPOSED to leave gaps; a clump refused
            # because a house is there has found one of them.
            #
            # What is NOT a gap is ground another grove's canopy is standing on. That blocker did not
            # exist until gate 0616's keep-out added it, and it deletes clumps for a reason that has
            # nothing to do with the settlement's own texture - measured, it cost Inashiro 10 of its
            # 11 copse clumps. So exactly that class relocates, and every other refusal still drops.
            # This repairs the harm the keep-out did without redesigning the scatter.
            if not dense and not any((qx - ox) ** 2 + (qy - oy) ** 2 < rr * rr for ox, oy, rr in occ_grove):
                return None
            if require_interior and edge_dist(qx, qy, poly) <= clump:
                return None
            # THE RADII REACH PAST THE WIDEST LOCAL OBSTACLE, which is the sun corridor: a yard's
            # no-tree strip is ~25 px half-width across and ~31 px deep, so a search capped at
            # step*1.4 = 28 px could not clear one and seed 10 kept its hole. step*2.2 = 44 px can.
            # A DEAD END, MEASURED AND REVERTED (feature 134 T50, 2026-08-28). When T49's rolled yard
            # sizes opened a 197 ft hole in cohort seed 8's wind wall, the obvious suspect was this
            # ladder: its top rung `step * 2.2` = 44 px is a number measured against the widest local
            # obstacle OF ITS DAY, and a rolled 52 x 36 ft yard stands in `occ` with a keep-out near
            # 57 px, so no rung could clear one. Deriving the top rung from the blocker actually
            # standing at the point (`rr - dist`, capped at `step * 5`) was implemented and rolled:
            # seed 8 came back with the SAME 65 clumps and the SAME 197 ft gap, and seeds 32 and 40
            # were unchanged too. Instrumenting the seating loop's rejections said why - of the grid
            # points in the hole, 166 were refused by `point_in_poly` and 39 by `within`, and NOT ONE
            # reached `_reseat`. The belt's eastern arm had swung north OFF THE PAGE as the cluster
            # repacked, so there was nothing there to re-seat around; the lone clump at (1423, 324) is
            # the only column of that arm the frame still shows. Do not re-derive this radius to chase
            # a belt hole - measure the rejection reasons first, because a hole in the ink and a hole
            # in the ribbon look identical from the manifest.
            for _nr in (step * 0.6, step * 1.0, step * 1.4, step * 1.8, step * 2.2):
                for _na in range(0, 360, 45):
                    ax, ay = qx + _nr * math.cos(math.radians(_na)), qy + _nr * math.sin(math.radians(_na))
                    if not point_in_poly(ax, ay, poly):
                        continue
                    if within is not None and (ax + clump * 0.9 < within[0] or ax - clump * 0.9 > within[2] or ay + clump * 0.9 < within[1] or ay - clump * 0.9 > within[3]):
                        continue
                    if _hard_blocked(ax, ay) or _local_blocked(ax, ay) or _lane_blocked(ax, ay):
                        continue
                    if any((ax - qx2) ** 2 + (ay - qy2) ** 2 < (step * 0.55) ** 2 for qx2, qy2 in placed):
                        continue
                    return (ax, ay)
            return None

        nx, ny = max(1, round((x1 - x0) / step)), max(1, round((y1 - y0) / step))
        clumps: list[Any] = []
        seated: list[tuple[float, float]] = []  # unrounded seats, inked after the face trim below
        for iy in range(ny + 1):
            for ix in range(nx + 1):
                gx = x0 + ix * (x1 - x0) / nx
                gy = y0 + iy * (y1 - y0) / ny
                jx = gx + (self._hjit(gx, gy, 21.0) - 0.5) * step  # jitter the grid so the stand + its edge read ragged
                jy = gy + (self._hjit(gx, gy, 22.0) - 0.5) * step
                if not point_in_poly(jx, jy, poly):
                    continue
                # ...AND NOT WHOLLY OFF THE PAGE, when the caller gives a `within`. ONLY wholly - a
                # clump whose crown merely CROSSES the frame edge is kept, and that is doctrine, not
                # leniency: `settlements/presentation.md` (GM 2026-07-20) says the belt CLIPS at the
                # view edge and "a partially visible belt reads as 'the wood continues'", which is
                # why `hard_features_within_frame` demands partial visibility of a village grove
                # rather than containment. Only a clump with NO visible ink is waste.
                #
                # THE FIRST VERSION INSET THE WINDOW INSTEAD, AND THAT WAS BACKWARDS - recorded
                # because it shipped and two independent reviews caught it. Requiring the whole crown
                # inside (`within[2] - 0.9*clump`) deleted every clump the edge merely touched, and on
                # Mizuguchi that traded 3 invisible clumps for 40 dropped ones - 37 of them at least
                # partly visible, 12 not touching the frame at all - punching a ~100 ft bare channel
                # through the middle of the wind wall on the windward side. Sawada lost 46% of its
                # canopy the same way. The earlier review that asked for "58 clumps touching the
                # frame" to be fixed was itself against the presentation doctrine above; the only
                # real defect was the 23 with no ink on the page.
                if within is not None and (jx + clump * 0.9 < within[0] or jx - clump * 0.9 > within[2] or jy + clump * 0.9 < within[1] or jy - clump * 0.9 > within[3]):
                    continue
                # A DENSE BELT FLOWS AROUND AN OBSTACLE INSTEAD OF LOSING THE COLUMN (settlement-review,
                # Inashiro 2026-08-18). `occ` keeps a clump off a house, a yard, a byre and - the case
                # that bit - a WELLHEAD, whose keep-out is the widest of the lot (`vr + 0.9*clump`,
                # because a well lost under the canopy reads wrong). A wellhead seated inside the belt
                # therefore deleted every clump around it, and the belt acquired a zero-canopy latitude
                # on its WINDWARD side - a hole straight through the wind wall, which is the one thing
                # a windbreak exists not to have. Measured on Inashiro: the 40 ft band at y1360-1400
                # went 8 clumps -> 1, in a 930 ft run that had never had a gap.
                #
                # Fixing it at the WELL was tried first and is the wrong lever - recorded because it
                # shipped for a moment. Ranking "not in the belt" ahead of coverage in the well
                # tie-break closed Inashiro's hole and cost Mizuguchi 61 ft of worst walk, on a map
                # whose own belt hole turned out not to be well-caused at all. The belt is what should
                # give: a real planted windbreak is not laid out on a grid and abandoned where a shed
                # stands, it is planted around the shed.
                #
                # So a blocked clump in a DENSE grove gets a short re-seat search before it is
                # dropped, and only for `occ` - a clump refused by the CROP, open WATER or a LANE is
                # refused for a reason that re-seating does not change, and those are the edges where
                # a belt is supposed to stop. The nudge re-asks every other test, and keeps its
                # distance from the clumps already down so a re-seat cannot just pile up on its
                # neighbor.
                # ONE rejection chain, three nudge blocks folded into it (2026-08-19). A HARD blocker
                # (crop, water, dike) drops the clump - those are edges a belt stops at. A LOCAL one
                # (a house, a yard, a wellhead, a lane, a sun corridor) gets a short re-seat search,
                # because a planted belt is planted AROUND a shed rather than abandoned at it. Three
                # separate causes have now punched holes in a wind wall here - a wellhead inside the
                # belt, a peer session's lane crossing it, and a threshing yard's sun corridor - and
                # each was fixed with its own ad-hoc nudge until the third made the pattern obvious.
                if _hard_blocked(jx, jy):
                    continue
                if _local_blocked(jx, jy) or _lane_blocked(jx, jy):
                    _alt = _reseat(jx, jy, clumps, require_interior=not _local_blocked(jx, jy))
                    if _alt is None:
                        continue
                    jx, jy = _alt
                seated.append((jx, jy))
                clumps.append([round(jx, 1), round(jy, 1)])
        # AND CLOSE THE INTERIOR HOLES (feature 152, acceptance review; the GM's own complaint in its
        # last form - "it's not clear that it will, in fact, be breaking much wind"). The grid decides
        # where a clump is TRIED, and where a try is refused the belt carries a hole: Kuwabata shipped
        # gaps of 73, 67 and 34 ft at 29%, 88% and 79% of the way ALONG its belt, and
        # `village_windbreak_is_continuous` failed on it - identically on main, so this is old.
        #
        # The rejection chain above deliberately does NOT re-seat a clump refused by the crop, open water
        # or a lane, on the grounds that those "are the edges where a belt is supposed to stop". That is
        # right at an END and wrong in the MIDDLE: a hole 29% of the way along is not the belt stopping.
        # So the run is walked once more along its own axis and each interior gap over `_BELT_GAP_FT` is
        # offered a seat at its midpoint, re-asking every test the loop asks. Nothing is relaxed - a gap
        # the ground truly refuses stays a gap.
        # ...and it SUBDIVIDES until the gap closes or the ground refuses. One clump at the midpoint turns
        # a 94 ft hole into two 47 ft holes, which is still a hole - measured on Kuwabata's first pass.
        if role == "windbreak" and len(seated) >= 2:
            _wv = _belt_axis(seated)
            for _ in range(6):  # a 94 ft gap needs three rounds; six is headroom, and it stops when nothing lands
                _order = sorted(range(len(seated)), key=lambda _k: seated[_k][0] * _wv[0] + seated[_k][1] * _wv[1])
                _added = 0
                # A DEAD END, MEASURED AND REVERTED (2026-08-29, the acceptance re-check's ERROR 2).
                # The review read Kuwabata's belt as stopping before its polygon did, and the obvious
                # repair was to bracket this run by the polygon's own across-wind extent so the END
                # stretches were offered seats like any interior gap. Implemented and rolled: it bought
                # ONE clump, on ONE map, at (2273.9, 393.6) on the page edge - because the unplanted
                # tail is off the page. Kuwabata's belt polygon runs 693..1440 along its own axis, the
                # view holds only 790..1327 of that, and the planting already covers 734..1330. The
                # honest fix was in the CHECK, which was demanding canopy on ground no reader can see;
                # `_column_in_belt` now clips its columns to the view. Do not re-add the end bracket to
                # chase a belt that "stops short" - measure whether the short end is on the page first.
                for _a, _b in zip(_order, _order[1:], strict=False):
                    _pa, _pb = seated[_a], seated[_b]
                    if math.dist(_pa, _pb) <= _BELT_GAP_FT:
                        continue
                    # FILL UP TO THE OBSTACLE FROM BOTH SIDES, not only at the midpoint. Where a lane
                    # crosses the belt the midpoint IS the lane, so a midpoint-only fill gives up and
                    # leaves the whole 40-50 ft hole - when what the record and the agronomy both want is
                    # the wall resuming on each side of the crossing. Purdue NCR-191, on a windbreak that
                    # must be crossed: an access gate is built "the same height and porosity as the rest
                    # of the windbreak fence", never left as a bare opening, because "when high-velocity
                    # air passes through a constriction, its velocity increases". So the gap is offered
                    # seats across its span and takes whichever the ground allows.
                    # ...AND ACROSS THE BELT'S DEPTH, not only along the straight line between the two
                    # clumps. `village_windbreak_is_continuous` walks COLUMNS of the belt's own span and
                    # asks whether each has canopy; a belt that bows around a plot has columns whose
                    # midpoint-between-neighbors lies outside its own polygon, so a fill that only tried
                    # that line refused every seat and left the column bare - measured on Kuwabata, where
                    # the run leaves the polygon after 14 of its 40 ft. So each fraction along the gap is
                    # also tried at several depths across the band, which is where the belt actually is.
                    # ...AT THE BELT'S OWN DEPTH FOR THAT COLUMN. The continuity check walks COLUMNS
                    # across the wind and asks whether each carries canopy, so a fill has to answer in
                    # the same terms: find where the belt's polygon actually lies at the bare column and
                    # seat there. Offsetting from the straight chord between two clumps does not do it -
                    # a belt that bows leaves that chord entirely, and measured on Kuwabata the polygon's
                    # depth at the bare columns sits in a band the chord never reaches.
                    _took = False
                    _perp = (-_wv[1], _wv[0])
                    _pd = [(q[0] * _perp[0] + q[1] * _perp[1]) for q in poly]
                    _d0, _d1 = min(_pd), max(_pd)
                    for _f in (0.5, 0.34, 0.66, 0.22, 0.78):
                        _col = (_pa[0] * _wv[0] + _pa[1] * _wv[1]) + ((_pb[0] * _wv[0] + _pb[1] * _wv[1]) - (_pa[0] * _wv[0] + _pa[1] * _wv[1])) * _f
                        _inside = []
                        for _k in range(33):
                            _d = _d0 + (_d1 - _d0) * _k / 32
                            _qx, _qy = _col * _wv[0] + _d * _perp[0], _col * _wv[1] + _d * _perp[1]
                            if point_in_poly(_qx, _qy, poly):
                                _inside.append((_qx, _qy))
                        for _qx, _qy in _inside[len(_inside) // 2 :] + _inside[: len(_inside) // 2]:  # the band's middle outward
                            if within is not None and (_qx + clump * 0.9 < within[0] or _qx - clump * 0.9 > within[2] or _qy + clump * 0.9 < within[1] or _qy - clump * 0.9 > within[3]):
                                continue
                            if _hard_blocked(_qx, _qy) or _local_blocked(_qx, _qy) or _lane_blocked(_qx, _qy):
                                continue
                            # ...AND NEVER ON TOP OF A CLUMP THAT IS ALREADY THERE (settlement-review
                            # 2026-08-29, acceptance re-check). The depth search is deterministic, so a gap
                            # that survives one round is offered the SAME point on the next and the fill
                            # piled crowns instead of converging. Measured by rolling Kuwabata with this
                            # clause disabled: 246 recorded windbreak clumps at 211 distinct positions,
                            # five of them at (1695.8, 576.9) alone, and 46 off-page clumps at 41
                            # positions. Refusing a seat within half a crown of one already taken brings
                            # the same belt in at 101 on-page clumps with nothing stacked. A stacked crown
                            # is invisible in ink and inflates every count taken off the record - including
                            # the one I first quoted for this feature.
                            if any((_qx - _sx) ** 2 + (_qy - _sy) ** 2 < (clump * 0.5) ** 2 for _sx, _sy in seated):
                                continue
                            seated.append((_qx, _qy))
                            clumps.append([round(_qx, 1), round(_qy, 1)])
                            _took = True
                            break
                        if _took:
                            break
                    if _took:
                        _added += 1
                if not _added:
                    break
        # THE FACE TRIM, then the ink (GM 2026-08-26, feature 133 T10). With `face_margin` the
        # caller says the frame will follow this belt's INNER FACE by that margin (`crop_boxes`
        # reads the same `windbreak_face`), so a clump whose whole crown lies deeper than
        # face + margin has no page to be seen on and is not inked - the same "only wholly off the
        # page" rule the `within` window applies on the other edges. Seating first and drawing
        # after is what makes this possible: the face is known only once every clump is down.
        # Draw order and positions are those of the seating loop, so nothing else moves.
        # THE PAGE IS THE PAGE, NOT A PROXY FOR IT (feature 152 T02, GM 2026-08-29: "it's not clear that
        # it will, in fact, be breaking much wind. Given how many houses appear uncovered"). A trim used to
        # run HERE, against the belt's own inner face plus `face_margin` - 48 ft - as a stand-in for the
        # page's windward edge. That proxy is right only when the belt is what sets that edge; whenever
        # other content (fields, marsh, a pond) holds the frame open wider, it under-estimates the page and
        # deletes canopy a reader can see. Measured over the pool against each map's FINAL `meta.view`:
        # Kashikawa discarded 61 clumps of which ALL 61 were wholly inside the rendered view, Kuwabata 21
        # of 45, Sawada 30 of 84 - and those three are exactly the maps with houses standing beyond their
        # belt's ends (8 of 20, 3 of 16, 8 of 19). Inashiro and Mizuguchi discarded only genuinely off-page
        # clumps and have no house beyond the belt. The belt was not too short: a third of it was being
        # thrown away on the page it belongs to.
        #
        # The trim is not gone - it MOVED to `Settlement.set_view`, the first moment the real page is
        # known. Everything the `within` window admits is drawn here (ink past the page is clipped by the
        # render, which is the documented behavior for a communal grove - see the note at `set_view`'s
        # frame list), and the RECORD is partitioned against the actual view once there is one.
        _offpage: list[Any] = []
        for jx, jy in seated:
            # feature 150: the belt and the copse are two highlight classes; a water_mouth grove has no
            # class in the vocabulary yet and stays unclassed so the census reports it
            self._draw_grove(jx, jy, clump, clump, face=(0, -1), mix=mix, cls={"windbreak": "windbreak", "copse": "copse"}.get(role))
        if clumps:
            # A COPSE IS RECORDED AT THE SIZE IT WAS DRAWN, not at the size it was asked for.
            #
            # The copse's requested footprint is the bounding box of the whole house cloud, and the
            # clumps inside it are skipped wherever they would land on a house, yard, garden or
            # crop - so the DECLARED area and the PLANTED area are two different things, and the
            # gap between them widens whenever the cluster spreads. Feature 126 spread it (houses
            # are no longer seated against pre-laid lanes), and `village_groves_visibly_stocked`
            # started firing: "copse 307x443px holds 1 clump (0.73/100k), floor 1.5". The trees had
            # not gone anywhere; the box around them had grown.
            #
            # The check is right and the record was wrong - a map that declares a feature it did not
            # draw is the defect, which is the same rule `M["lane"]` breaks when it keeps an untrimmed
            # spine. So a COPSE reports the extent of its own clumps. The WINDBREAK deliberately does
            # not: its position IS its meaning (`village_windbreak_on_windward_side` judges the
            # recorded center) and shrinking it to the leaves would walk that center off the windward
            # side - a defect this file already records having caused on cohort seeds 19 and 28.
            if role == "copse":
                _cxs = [cl[0] for cl in clumps]
                _cys = [cl[1] for cl in clumps]
                _pad = clump / 2 + 4.0
                x0, x1 = min(_cxs) - _pad, max(_cxs) + _pad
                y0, y1 = min(_cys) - _pad, max(_cys) + _pad
                poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            self.M["village_groves"].append(
                {
                    "x": round((x0 + x1) / 2, 1),
                    "y": round((y0 + y1) / 2, 1),
                    "w": round(x1 - x0, 1),
                    "h": round(y1 - y0, 1),
                    "rot": 0,
                    "role": role,
                    "r": round(clump / 2, 1),
                    "clumps": clumps,
                    "clumps_offpage": (_offpage if face_margin is not None and clumps else []),  # actual drawn clump centers + radius, for groves_clear_of_lanes
                    "poly": [[round(px, 1), round(py, 1)] for px, py in poly],
                }
            )
        return len(clumps)
