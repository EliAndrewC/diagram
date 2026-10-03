"""The hard no-build ground a footprint may not touch - crop, pond, bog, a field's own ditches - and the test against it.

Split out of `houses.py` by feature 278, when the index of the hard polygons' boxes (`_hard_index`, FR-009) took that
file past the 1,000-line bar. The methods are unchanged and still reach everything through `self.`; `HardGroundMixin` is
one more base of `Settlement` (`core.py`).

Research: footprint test and its index - NONE
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from ._geom import PointGrid, quad_hits_poly

if TYPE_CHECKING:
    from .core import Settlement


class HardGroundMixin:
    def _hard_ground(self: Settlement) -> list[Any]:  # type: ignore[misc]
        """Every HARD no-build polygon, read from the MANIFEST plus anything a gen registered by hand.

        Manifest-sourced on purpose. The first cut kept a `hard_polys` registry that `draw_comb_field`
        populated - and it was EMPTY on any map whose field is drawn by a different path (the polder
        and contour archetypes have their own), so the rule silently did nothing there. Reading the
        drawn record instead makes it order-independent and impossible for a gen to forget: the same
        placement-and-check-read-the-same-source doctrine the footbridges taught us. Cached on the
        record counts, since this is called once per placement candidate.

        Research:
            marsh is no-build - research/questions/0058-ground-too-wet-to-build-on.html: every drawn marsh polygon is hard ground
            crop and ditches are no-build - UNRESEARCHED: a footprint may not touch a dry plot, nor come within the ditch's half-width plus 2 px
        """
        dp, fd = self.M.get("dry_plots", []) or [], self.M.get("field_ditches", []) or []
        key = (len(dp), len(fd), len(self.hard_polys), len(self.wet_polys))
        if self._hard_cache_key == key:
            return self._hard_cache
        out: list[Any] = [list(self.hard_polys)[i] for i in range(len(self.hard_polys))]
        out += [list(wp) for wp in self.wet_polys if len(wp) >= 3]  # every drawn marsh (feature 150 T50)
        out += [[(q[0], q[1]) for q in d["poly"]] for d in dp if d.get("poly") and len(d["poly"]) >= 3]
        for ch in fd:
            pts = ch.get("poly") or ch.get("pts")
            if not pts:
                continue
            hw = float(ch.get("w") or 1.5) / 2 + 2.0
            for k in range(len(pts) - 1):
                ax, ay = pts[k]
                bx, by = pts[k + 1]
                ln = math.hypot(bx - ax, by - ay) or 1.0
                nx, ny = -(by - ay) / ln * hw, (bx - ax) / ln * hw
                out.append([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])
        self._hard_cache_key: tuple[int, ...] | None = key
        self._hard_cache = out
        return out

    def _hard_clear(self: Settlement, x: float, y: float, w: float, h: float) -> bool:  # type: ignore[misc]
        """Is this footprint clear of HARD no-build ground (crop, pond, bog, a field's own ditches)?

        Factored out of `_fits` because placement is not the only moment that needs it:
        `_solve_homestead` NUDGES a farmstead after it has already passed `_fits`, to make room for
        its yard, garden and grove - and nothing re-tested the moved position, so a steading that
        genuinely cleared every keep-out where it was placed could be shifted onto a ditch or a hem
        plot afterwards. That was the last root cause behind the overlap matrix's residue.

        Research: tilt allowance - NONE: the footprint is swept by the farmhouse's 5 degree tilt, which is decided elsewhere"""
        hard = self._hard_ground()
        if not hard:
            return True
        # ROTATION ALLOWANCE. `_fits` is called before a farmhouse is given its small random tilt
        # (+/-5 deg), so the box tested here is axis-aligned while the box DRAWN and RECORDED is
        # rotated - and a rotated rect reaches further on both axes than its unrotated self. Testing
        # the swept extent closes that gap; without it a steading clears at placement and laps a hem
        # plot once tilted, which is exactly one of the defects the overlap matrix kept reporting.
        _th = math.radians(5.0)
        # BOTH AXES FROM THE ORIGINAL SIDES (feature 226, a spec-fidelity aside): this inflated `h` from the already-swept
        # `w`, so one axis was wider than the tilt's extent; `w0` keeps the sweep what it claims to be.
        w0 = w
        w = w0 * math.cos(_th) + h * math.sin(_th)
        h = w0 * math.sin(_th) + h * math.cos(_th)
        fp = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
        fx0, fy0, fx1, fy1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
        # THE HARD POLYGONS FROM AN INDEX OF THEIR BOXES (feature 278, FR-009): every hard polygon's box was compared per
        # call - the notice board's verge probe alone makes thousands. A polygon whose box misses the footprint's cannot
        # meet it, so the index returns every one the test could find; the answer is any-of, so the order is immaterial.
        for hp, hx0, hy0, hx1, hy1 in self._hard_index(hard).near((fx0 + fx1) / 2, (fy0 + fy1) / 2, max(fx1 - fx0, fy1 - fy0) / 2):
            if fx1 < hx0 or fx0 > hx1 or fy1 < hy0 or fy0 > hy1:
                continue
            if quad_hits_poly(fp, hp):
                return False
        return True

    def _hard_index(self: Settlement, hard: list[Any]) -> PointGrid:  # type: ignore[misc]
        """A grid of `_hard_ground()`'s polygons by box, rebuilt when that list is rebuilt (it is cached on its record
        counts and handed back as the same list object until they change)."""
        held = self._hard_grid
        if held is None or held[0] is not hard:
            grid = PointGrid()
            grid.extend((hp, *bb) for hp, bb in zip(hard, self._poly_bboxes(hard), strict=False))
            self._hard_grid: tuple[list[Any], PointGrid] | None = (hard, grid)
            return grid
        return held[1]
