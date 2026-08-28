"""Unbuilt GROUND SURFACES that reserve placement rather than structures that occupy it.

Split from settlement/structures.py by feature 114 - see settlement/structures/CLAUDE.md for the index.
"""

import math
import random
from typing import TYPE_CHECKING, Any

from .._geom import (
    label_quad,
    linear_tilt,
    organic_bbox,
    organic_poly,
    point_in_poly,
    seg_closest,
    seg_dist,
    smooth_closed,
    smooth_points,
)

if TYPE_CHECKING:
    from ..core import Settlement


#: the trunk road's default real width, feet - 5 ken (the 1604 Tokaido standard) drawn at 30 (feature 144)
ROAD_W_FT = 30.0


class GroundMixin:
    def road(self: Settlement, pts: Any, label: Any = None, width: float | None = None, label_xy: Any = None) -> None:  # type: ignore[misc]
        """A major road (e.g. an Imperial road) - a bordered roadbed. No-build corridor.
        Default real width ROAD_W_FT = 30 ft (an Imperial trunk highway), converted at the
        map's ftpx and linework-floored. WHY 30 (GM 2026-08-28, feature 144): the Tokaido's
        width was standardized at 5 ken in 1604 ("街道の幅員を5間とし", ja.wikipedia 東海道 -
        `tokaido-jawiki` in research/SOURCES.md), 5 ken = 29.5 ft; drawn at the round 30 the
        GM asked for. The earlier 26 ft ("the Tokaido's own width") and the "~18-24 ft" this
        docstring once claimed were both unsourced - research/cities/capitals.md "Street
        widths" carries the read and the correction.
        label_xy overrides the label anchor (default: the polyline midpoint). For a city the
        midpoint is the city CENTER, but the road label names the *Imperial* road, which is an
        Imperial responsibility only OUTSIDE the walls - inside, the same roadway is a city
        street the city maintains - so a city must pass label_xy a point beyond the gates."""
        if width is None:
            width = self.lw(ROAD_W_FT)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        self.corridors.append((pts, width / 2 + max(32 * self.bscale, 17)))  # wide road -> larger building setback (at the map's grain, floored)
        if "road" not in self.M or self.M["road"] is None:
            self.M["road"] = [[x, y] for x, y in pts]  # the FIRST road stays the main road (back-compat
            self.M["road_width"] = width  # for the single-road checks/projections)
        self.M.setdefault("roads", []).append({"pts": [[x, y] for x, y in pts], "w": width})
        self.M["road_z"] = None
        self._ground(
            width,
            self.M,
            "road_z",
            edge=f'<path d="{dd}" fill="none" stroke="#9C7A40" stroke-width="{width}" opacity="0.9"/>',
            bed=f'<path d="{dd}" fill="none" stroke="#D8C49A" stroke-width="{width - 8}" opacity="1"/>',
            top=f'<path d="{dd}" fill="none" stroke="#8A6E3E" stroke-width="1.2" stroke-dasharray="12,10" opacity="0.6"/>',
        )
        if label:
            mid = pts[len(pts) // 2]
            lx, ly = label_xy if label_xy else (mid[0] + 46, mid[1] - 22)
            # DEFERRED to finish(): the label picks its side of the road by what is actually
            # built around it, and at road-draw time the map is still empty (GM label doctrine:
            # a label that can sit in empty ground, should; otherwise cover as little as possible)
            self._road_label: Any = (label, lx, ly)

    def pasture(self: Settlement, shape: Any, label: Any = None, amp: float = 40, label_xy: Any = None) -> None:  # type: ignore[misc]
        """Hayfield / grazing land (pastureland, around the barns) - open grass with
        the odd hay bale, distinct from the cultivated paddy fields. Blocks placement."""
        # SCOPED (2026-08-08): the pasture OUTLINE is stream-drawn (organic_bbox), and the fill
        # block below re-seeds only itself - so an upstream change reshaped the paddock, which
        # moved which sample points land inside it, which changed the draw sequence for
        # everything after. It was the FIRST divergence in a town, at draw #70 of 24,615.
        # Keyed on the shape, so a pasture re-rolls when the GM moves it and never otherwise.
        with self.rng_scope("pasture", *(shape if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape) else (len(shape), shape[0][0], shape[0][1]))):
            outline = organic_bbox(shape, amp) if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape) else organic_poly(shape, amp)
            sm = smooth_points(outline)
            d = smooth_closed(outline)
            cid = self._cid('past')
            self.add(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
            self.add(f'<path d="{d}" fill="#C8CF92" stroke="#9CA86A" stroke-width="2" stroke-dasharray="7,5"/>')
            xs, ys = [p[0] for p in sm], [p[1] for p in sm]
            st = random.getstate()
            random.seed(15)
            self.add(f'<g clip-path="url(#{cid})">')
            yy = min(ys) + 14
            while yy < max(ys):
                xx = min(xs) + 14
                while xx < max(xs):
                    tx, ty = xx + random.uniform(-7, 7), yy + random.uniform(-7, 7)
                    if point_in_poly(tx, ty, sm):
                        if random.random() < 0.10:
                            self.add(f'<rect x="{tx - 6:.0f}" y="{ty - 4:.0f}" width="12" height="8" rx="3" fill="#D8C47E" stroke="#A98E54" stroke-width="0.7"/>')
                        else:
                            self.add(f'<path d="M{tx - 3:.0f},{ty + 2:.0f} L{tx:.0f},{ty - 4:.0f} L{tx + 3:.0f},{ty + 2:.0f}" fill="none" stroke="#8FA05E" stroke-width="0.8"/>')
                    xx += 26
                yy += 24
            self.add('</g>')
            random.setstate(st)
            self.block_polys.append(sm)
            self.M.setdefault("pastures", []).append([[round(p[0], 1), round(p[1], 1)] for p in sm])
            if label:
                lx, ly = label_xy if label_xy else ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
                self.label(lx, ly, label, 12, italic=True, color="#5C6B3A")

    def _finish_road_label(self: Settlement) -> None:  # type: ignore[misc]
        """Seat and draw the Imperial road's caption at finish time (feature 145: extracted from `finish()`, which every map executes, so the module-level floor sees this town/city branch where it belongs)."""
        text, lx, ly = self._road_label
        rd = self.M.get("road") or []
        # The caption names the ROAD, so its subject is the nearest STRETCH of roadway: box
        # that segment out to the corridor half-width and run the standard standoff ladder
        # against it. The authored label_xy stays a HINT - which flank, and where along the
        # road - and no longer sets the distance. That was the defect the GM caught on Tango
        # (2026-07-26): the old candidates were generated at the anchor's own perpendicular
        # offset, mirrored across the roadline and slid along it, so a hand anchor 102px out
        # produced a label 55px clear of the roadway with nothing but bare ground between.
        half = float(self.M.get("road_width") or 26) / 2
        i_ = min(range(len(rd) - 1), key=lambda i: seg_dist(lx, ly, rd[i], rd[i + 1]))
        (ax_, ay_), (bx_, by_) = (rd[i_][0], rd[i_][1]), (rd[i_ + 1][0], rd[i_ + 1][1])
        # The subject is the roadway's CROSS-SECTION at the point the anchor pointed at, plus
        # the tangent there - NOT the segment's bounding box, which for a diagonal road is a
        # huge square whose edges are hundreds of px from the roadway (Hoshizora: a 486x256 box
        # for a road running through it at 27 degrees). Cross-section + axis is right at any angle.
        px_, py_ = seg_closest(lx, ly, (ax_, ay_), (bx_, by_))
        seg_ = math.hypot(bx_ - ax_, by_ - ay_) or 1.0
        axis_ = ((bx_ - ax_) / seg_, (by_ - ay_) / seg_)
        # ...and the caption RUNS ALONG that tangent (GM 2026-08-08): "Imperial Road" set level
        # beside Hoshizora's -27deg roadbed named the road the way a caption beside a diagonal
        # building named the building - which is the defect the 2026-08-02 tilt fixed for
        # glyphs and stopped short of fixing for the linear features. A road is a LINE, so this
        # takes linear_tilt's clamp, NOT label_tilt's fold: past 45deg the caption goes level
        # (the GM's own north-south convention), where the fold would tilt it to the road's
        # cross direction, which is an axis of nothing. Tango (due N-S) and Nagahara (72deg)
        # therefore stay exactly as they were; only genuinely diagonal roads move.
        tilt_ = linear_tilt(math.degrees(math.atan2(axis_[1], axis_[0])))
        box = (px_ - half, py_ - half, px_ + half, py_ + half)
        lx, ly = self._best_label_spot(box, text, 12, hint=(lx, ly), slides=(-45.0, 45.0, 90.0, -90.0), axis=axis_, tilt=tilt_)
        # RE-SEAT the recorded subject on the roadway beside where the caption actually landed.
        # `label_hugs_its_referent` measures an axis-aligned gap between two recorded boxes, so a
        # cross-section pinned at the ANCHOR reads the along-road distance as drift once the
        # ladder slides the caption - Tango measured 45px for a caption sitting 29px off the
        # roadway. Boxing the roadway nearest the caption's own box makes the recorded gap the
        # clearance a reader sees, at any road angle.
        # A TILTED caption re-seats on the quad it actually DRAWS, not its pre-tilt box - the
        # recorded gap has to be the clearance a reader sees. At tilt 0 label_quad returns that
        # box corner-for-corner in the same order, so every level road's referent is unchanged.
        lb_ = self._label_box(lx, ly, text, 12)
        qs_ = label_quad([*lb_, 0, text, None, tilt_])
        cq_ = ((qs_[0][0] + qs_[2][0]) / 2, (qs_[0][1] + qs_[2][1]) / 2)
        px_, py_ = min(
            (seg_closest(qx, qy, (ax_, ay_), (bx_, by_)) for qx, qy in (*qs_, cq_)),
            key=lambda c: min(math.hypot(c[0] - qx, c[1] - qy) for qx, qy in qs_),
        )
        box = (px_ - half, py_ - half, px_ + half, py_ + half)
        self.label(lx, ly, text, 12, italic=True, weight="bold", color="#5A4326", ref=box, rot=tilt_, linear=True)
        self.M["road_label"] = [lx, ly]
