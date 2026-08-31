"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import (
    Poly,
    kido_bar_deg,
    lane_runs,
    lane_through_gate,
    sat_overlap,
    seg_dist,
    stroke_quads,
    tower_quad,
    wall_runs,
)
from ..city.knobs import machi_mouths

if TYPE_CHECKING:
    from ..core import Settlement


class KidoMixin:
    _Rect = tuple[float, float, float, float]

    def _kido_rects(self: Settlement, x: float, y: float, rot: float, guard_side: int, hw: float, fences: Sequence[Poly] = ()) -> tuple[_Rect, list[_Rect], _Rect, Callable[[_Rect], Poly]]:  # type: ignore[misc]
        """The local rects a kido glyph at (x, y) is built from - (roof, posts, guard, to_corners) -
        with the guard box already slid clear of the roadbed. Local frame: the gateway bar spans the
        X axis and rotate(rot) turns it onto the bar angle, so local +x is ACROSS the lane and local
        +y along it. Factored out because two callers need the SAME geometry: kido() draws it, and
        kido_reservation() reserves the ground it will stand on long before it is drawn."""
        roof = (-hw, -7.0, 2 * hw, 14.0)
        posts = [(-hw - 1, -8.0, 4.0, 16.0), (hw - 3, -8.0, 4.0, 16.0)]
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))

        def to_corners(rect: Settlement._Rect) -> Poly:
            """The rect's four corners in map coords, in WINDING order (so a caller may use the
            result as a polygon, not merely as a point cloud for a bbox)."""
            rx0, ry0, rw, rh = rect
            return [(x + a * cr - b * sr, y + a * sr + b * cr) for a, b in ((rx0, ry0), (rx0 + rw, ry0), (rx0 + rw, ry0 + rh), (rx0, ry0 + rh))]

        # THE GUARD BOX TAKES THE NEAREST CLEAR SPOT BESIDE THE OPENING, on the ward-interior flank
        # (the `guard_side` +/-y set by the caller). It starts just beyond the bar's end and walks
        # OUTWARD, trying the near side of the opening first and the far side at the same distance,
        # until it stands clear of two things:
        #   - every LANE BED, by a verge of ~12 real ft. Straight-line arithmetic is not enough: the
        #     ring road CURVES as it passes the gate, so a box set back along the road walks into a
        #     bed it started clear of (Tango's east ward gate, GM 2026-07-26).
        #   - every WALL TOWER already standing. The rampart is drawn long before s.ward, and the
        #     ward fence meets the wall exactly where the last kido hangs, so the box can slide onto
        #     a mural bastion (Nagahara's west ward gate). The kido cannot move and the tower will
        #     not (a coverage-thin curtain needs it), so the BOX is what yields - it simply stands on
        #     the other flank of its own gateway, which is as plausible a spot for a watch shack.
        #   - the RAMPART and any compound wall it could be pushed onto.
        #   - THE WARD FENCE ITSELF (GM 2026-07-27: "ward gates seem to sometimes overlap with
        #     neighborhood walls"). The gateway - roof and posts - stands ON the fence, because the
        #     gate IS the opening in it; the guard box does NOT. It is a small building on the verge
        #     beside the gate, and a fence line drawn through the middle of it reads as a mistake,
        #     which is what it is. This was excluded on the reasoning that "the fence runs through
        #     the gate by construction", which is true of the GATEWAY and was over-applied to its
        #     furniture. Perpendicular crossings were fine either way (the box sits along the lane,
        #     off the fence line); it is the OBLIQUE crossings that cut the box, and two of the
        #     pool's fourteen gates were cut. Tested with SAT against the stroked fence, not by
        #     corner distances: a line through the CENTER of a 15x16 box leaves every corner ~8px
        #     clear, so the corner test the lane beds use would have reported it clear.
        y0 = 12.0 if guard_side >= 0 else -28.0
        verge = max(self.px(12), 4.0)
        runs = [(pts, half + verge) for pts, half in lane_runs(self.M)]
        runs += [(pts, half) for lbl, pts, half in wall_runs(self.M) if "ward fence" not in lbl]
        towers = [tower_quad(t) for t in list(self.M.get("wall_towers") or []) + [g for g in (self.M.get("gate_structs") or []) if g.get("kind") == "tower"]]
        # 4.0 = the fence's 2.5px drawn half-width plus a hair: the box may stand hard against its
        # own fence (that is where a gate watch belongs), it may not be cut by it
        fq = [q for f in fences for q in stroke_quads(f, 4.0)]
        guard: Settlement._Rect = (-hw - 13, y0, 15.0, 16.0)
        for step in range(24):  # bounded: 24 x 1.5px is far more walk than any real crossing needs
            for cand in ((-hw - 13 - 1.5 * step, y0, 15.0, 16.0), (hw - 2 + 1.5 * step, y0, 15.0, 16.0)):
                gc = to_corners(cand)
                blocked = any(seg_dist(cx, cy, pts[i], pts[i + 1]) < clear for pts, clear in runs for i in range(len(pts) - 1) for (cx, cy) in gc)
                if not blocked and not any(sat_overlap(gc, tq) for tq in towers) and not any(sat_overlap(gc, q) for q in fq):
                    return roof, posts, cand, to_corners
        return (
            roof,
            posts,
            guard,
            to_corners,
        )  # pragma: no cover - nowhere clear within 36px of the opening on either flank; keep the traditional seat [174: KEPT, not deletable - a terminal return of the four values the caller unpacks]

    def kido_seat(self: Settlement, x: float, y: float, boundary: Any) -> tuple[float, int]:  # type: ignore[misc]
        """The (bar angle, guard flank) a kido seated at (x, y) on the ward fence `boundary` will
        take: square to the lane running through it, else along the local fence tangent, with the
        guard box on the ward-interior side. s.ward calls this for every gate it draws; a gen calls
        it (via kido_reservation) to reserve that ground BEFORE the packs run."""
        i = min(range(len(boundary) - 1), key=lambda j: seg_dist(x, y, boundary[j], boundary[j + 1]))
        fence = math.degrees(math.atan2(boundary[i + 1][1] - boundary[i][1], boundary[i + 1][0] - boundary[i][0]))
        lane = lane_through_gate(self.M, x, y, fence)
        rot = kido_bar_deg(lane[0], fence) if lane else fence
        nx, ny = -math.sin(math.radians(rot)), math.cos(math.radians(rot))  # the local +y flank, in map coords
        icx = sum(p[0] for p in boundary) / len(boundary)  # the fence polyline's centroid sits toward the ward interior
        icy = sum(p[1] for p in boundary) / len(boundary)
        return rot, (1 if (icx - x) * nx + (icy - y) * ny >= 0 else -1)

    def kido_reservation(self: Settlement, x: float, y: float, boundary: Any, margin: float = 17.0) -> Poly:  # type: ignore[misc]
        """The no-build rect a gen should `block_polys.append(...)` for a ward gate at (x, y), sized
        to the glyph that will actually be drawn there. THE ORDERING TRAP this solves (it is why the
        helper exists rather than a hand-written rect in each gen): s.ward runs near the END of a
        city gen, long after the packs, so the gates' ground must be reserved up front - but the
        glyph's extent is NOT symmetric (it reaches ~36px on the guard-box flank and ~10px on the
        other) and its angle now depends on the lane it bars, so a hand-tuned rect goes stale the
        moment a fence or a road moves, and a square big enough to be safe at any angle costs real
        housing (Tango lost its merchant band and a well to one). `margin` inflates the rect by a
        large dwelling's half-diagonal, since block_polys are CENTER-tested for urban packs.
        Call it AFTER the lanes through the gates are drawn, so kido_seat sees them."""
        rot, side = self.kido_seat(x, y, boundary)
        # the fence goes in explicitly: at reservation time s.ward has not run, so M['wards'] is
        # still empty and the drawn call's wall_runs lookup would find nothing to agree with
        roof, posts, guard, to_corners = self._kido_rects(x, y, rot, side, self.lw(18) / 2 + 5, fences=[[(float(p[0]), float(p[1])) for p in boundary]])
        cs = [c for rect in (roof, *posts, guard) for c in to_corners(rect)]
        x0, y0 = min(c[0] for c in cs) - margin, min(c[1] for c in cs) - margin
        x1, y1 = max(c[0] for c in cs) + margin, max(c[1] for c in cs) + margin
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def kido_mesh(self: Settlement) -> int:  # type: ignore[misc]
        """Bar every machi mouth with a kido (research 021 item 6: the ward MESH - Edo's
        machi-kido and Qing's zhalan; no ward walls, the block's own gate closes at night).
        Reads the SAME machi_mouths source the validator reads, so the two sides cannot
        disagree. Call AFTER streets + districts are declared and BEFORE the packs (each
        kido reserves its ground). The bar runs ACROSS its street. Returns the count."""
        n = 0
        for mx, my in machi_mouths(self.M):
            best, bd = 0.0, 1e9
            for st in self.M.get("town_streets", []):
                pts = st["pts"]
                for i in range(len(pts) - 1):
                    d = seg_dist(mx, my, tuple(pts[i]), tuple(pts[i + 1]))
                    if d < bd:
                        bd = d
                        best = math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
            # reserve the gate + guard-box ground BEFORE the packs run (a kido drawn
            # without a reservation had rows seated against its guard box)
            self.block_polys.append([(mx - 30, my - 30), (mx + 30, my - 30), (mx + 30, my + 30), (mx - 30, my + 30)])
            self.placed.append((mx, my, 48, 48))  # the guard box hangs W/N of the bar; the frontage rows now GAP the mouths, so the reserve only needs the gate's own ground
            self.kido(mx, my, rot=best + 90)
            n += 1
        return n

    def kido(self: Settlement, x: float, y: float, horizontal: bool = True, sw: float | None = None, rot: float | None = None, guard_side: int | None = None) -> None:  # type: ignore[misc]
        """A kido - a wooden WARD GATE barring a street at a quarter boundary, manned and shut at
        night to keep the samurai quarter apart from the commoners. A small city seals its wards
        with GATES, not internal ramparts (the walled-ward / fang system was a great-capital, Tang-
        era thing). Drawn OVER the street (a roofed gateway + posts + a guard box); records M['kido'].
        THE GATE SQUARES TO WHAT IT BARS (GM 2026-07-26): a kido exists to shut a WAY, so where a
        street, alley, road or the ring road runs through the seat, the roofed bar stands SQUARE
        ACROSS THAT LANE and the fence meets it at whatever angle the fence happens to run; only
        where no lane passes through does the bar fall back to the LOCAL FENCE TANGENT (the earlier
        GM 2026-07-24 rule, which is still what a gate in open fence wants). The two agree wherever
        a lane meets its fence squarely, which is most crossings; they diverge on an oblique one -
        Tango's SW ring-road gate sat 38 degrees off square to the road it barred, and read as a
        stamp dropped on the roadbed. Pass `rot` (degrees) for the bar angle; s.ward computes it via
        lane_through_gate/kido_bar_deg, and kido_aligned_with_ward_fence grades it the same way.
        The guard box rotates with the group; `guard_side` (+1 = the local +y flank, -1 = the -y
        flank) picks which side it stands on - s.ward passes the WARD-INTERIOR side (the gate watch
        belongs to the ward it seals). It is then NUDGED clear of any lane bed it would otherwise
        stand in: the box is a small building on the verge, not an obstruction in the road, and a
        ring road that CURVES past the gate walks under a box placed on straight-line arithmetic
        (Tango's east ward gate, GM 2026-07-26). Legacy `horizontal` (True = an E-W street through
        a N-S fence) remains the fallback when rot is omitted, reproducing the old drawings."""
        if sw is None:
            sw = self.lw(18)  # the barred opening spans a real ~18 ft street
        hw = sw / 2 + 5
        if rot is None:
            rot = 90.0 if horizontal else 0.0
        if guard_side is None:
            guard_side = -1 if horizontal else 1  # the legacy flanks (E of a N-S gate, S of an E-W one)
        # the ward fences only, NOT their wall-caps: kido_reservation reserves ground against the
        # bare boundary polyline (the caps do not exist yet then), and the two must agree
        roof, posts, guard, _corners = self._kido_rects(x, y, rot, guard_side, hw, fences=[pts for lbl, pts, _hw in wall_runs(self.M) if lbl.endswith("ward fence")])
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        g = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{roof[0]:.0f}" y="{roof[1]:.0f}" width="{roof[2]:.0f}" height="{roof[3]:.0f}" rx="1.5" fill="#8A6E3E" stroke="#3F3018" stroke-width="1.5"/>')
        for px, py, pw, ph in posts:
            g.append(f'<rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" fill="#3F3018"/>')
        g.append(f'<rect x="{guard[0]:.0f}" y="{guard[1]:.0f}" width="{guard[2]:.0f}" height="{guard[3]:.0f}" rx="1" fill="#CDB890" stroke="#5A4326" stroke-width="1.2"/>')
        g.append('</g>')
        z = self.add_top(''.join(g))
        corners = [c for rect in (roof, *posts, guard) for c in _corners(rect)]  # the gate's full drawn footprint, rotated (for the labels-on-top check)
        bbox = [round(min(c[0] for c in corners), 1), round(min(c[1] for c in corners), 1), round(max(c[0] for c in corners), 1), round(max(c[1] for c in corners), 1)]
        self.M.setdefault("kido", []).append(
            {
                "x": round(x, 1),
                "y": round(y, 1),
                "horizontal": abs(sr) >= abs(cr),
                "rot": round(rot % 180.0, 1),
                "z": z,
                "bbox": bbox,
                "guard": [
                    [round(cx, 1), round(cy, 1)] for cx, cy in _corners(guard)
                ],  # the watch box's own footprint, so kido_guard_box_clear_of_lanes can grade it (the bbox alone cannot tell box from bar)
                # ...and the TRUE (rotated) footprint of every part. The bbox is an axis-aligned box
                # round the whole group - honest while every kido was axis-aligned, badly overstated
                # now that they turn onto their lane: Nagahara's SW gate at 115deg has a bbox ~60%
                # larger than the glyph, and the keep-clear checks read it as overlapping a mural
                # tower the gate in fact clears (GM 2026-07-26). bbox stays for the label-occlusion
                # pass, where over-stating is the safe direction.
                "parts": [[[round(cx, 1), round(cy, 1)] for cx, cy in _corners(rect)] for rect in (roof, *posts, guard)],
            }
        )
