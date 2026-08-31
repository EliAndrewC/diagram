"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly

if TYPE_CHECKING:
    from ..core import Settlement


class GardensMixin:
    def _draw_garden(self: Settlement, cx: float, cy: float, w: float, h: float, poly: Any) -> None:  # type: ignore[misc]
        """Draw one small dooryard KITCHEN GARDEN (saien): a tilled earthen bed with tidy planted rows
        of greens. Distinct from the tan threshing yard (bare swept earth) and the blue-green paddy quilt.
        The bed's outer footprint is an irregular quad (`poly`, absolute corner coords) - a hand-worked plot
        bent to paths and soil, not surveyed square; the rows are laid out in the local (w,h) frame."""
        x0, y0 = -w / 2, -h / 2
        g = [f'<g transform="translate({cx:.0f},{cy:.0f})">']
        pts = " ".join(f"{px - cx:.1f},{py - cy:.1f}" for px, py in poly)
        g.append(f'<polygon points="{pts}" fill="#B49A62" stroke="#6E5A30" stroke-width="1.3"/>')  # tilled bed
        nrows = 3
        for i in range(nrows):  # rows of greens running along the bed
            ry = y0 + h * (i + 0.5) / nrows
            g.append(f'<line x1="{x0 + 3:.1f}" y1="{ry:.1f}" x2="{-x0 - 3:.1f}" y2="{ry:.1f}" stroke="#6E9A40" stroke-width="2.4" stroke-linecap="round"/>')
            for k in range(3):  # a few leafy plants dotted along each row
                px = x0 + 4 + (w - 8) * (k + 0.5) / 3
                g.append(f'<circle cx="{px:.1f}" cy="{ry:.1f}" r="1.7" fill="#83B255"/>')
        g.append('</g>')
        self.add(''.join(g), cls="garden")

    def _garden_dims(self: Settlement, hw: float, hh: float) -> tuple[float, float]:  # type: ignore[misc]
        """PREVIEW: garden scaled to the (now smaller) house, capped."""
        return min(0.55 * hw, 24 * self.bscale), min(0.55 * hh, 16 * self.bscale)

    def _farm_shed_rect(self: Settlement, hx: float, hy: float, hw: float, hh: float, rot: float, kind: str, shed: Any) -> tuple[float, float, float, float] | None:  # type: ignore[misc]
        """The footprint of a plain farmhouse's attached STOREHOUSE/shed (kura), drawn as a sub-glyph on
        the house's WEST side (local -x), or None if it has none. Derived here (the shed is not a separate
        recorded struct) so the garden can be kept OFF it - shed and garden sit on opposite sides."""
        if not (shed and kind == "plain"):
            return None
        th = math.radians(rot)
        lx = -0.64 * hw  # shed center in the house's local frame (west side)
        return (hx + lx * math.cos(th), hy + lx * math.sin(th), 0.32 * hw, 0.56 * hh)

    def _garden_fits(self: Settlement, x: float, y: float, w: float, h: float, hx: float, hy: float, yard: Any, shed_rect: Any = None) -> bool:  # type: ignore[misc]
        """A garden fits where it is in-bounds, on DRY ground (clear of paddies / blocks), off any lane,
        clear of every placed footprint EXCEPT its own farmhouse, clear of that farmhouse's YARD, and clear
        of its SHED (the yard, shed, and garden all sit on different sides of the house, never overlapping)."""
        if x < 55 or x > self.W - 55 or y < 88 or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):
            return False
        if self._in_blocked(x, y) or self._near_corridor(x, y):
            return False
        r = math.hypot(w, h) / 2
        for poly in self.field_polys:  # a kitchen garden is dry ground, off the paddies
            if point_in_poly(x, y, poly) or edge_dist(x, y, poly) < r + 4:
                return False
        if math.hypot(x - yard[0], y - yard[1]) < r + math.hypot(yard[2], yard[3]) / 2 + 2:
            return False  # not on top of this house's own threshing yard
        if shed_rect and math.hypot(x - shed_rect[0], y - shed_rect[1]) < r + math.hypot(shed_rect[2], shed_rect[3]) / 2 + 2:
            return False  # not on top of this house's own storehouse/shed (its west side)
        for px, py, pw, ph, *_ in self.placed:
            if px == hx and py == hy:  # the garden abuts its OWN farmhouse - allowed
                continue
            if math.hypot(x - px, y - py) < r + math.hypot(pw, ph) / 2 + 2:
                return False
        return True

    def _find_garden_spot(self: Settlement, hx: float, hy: float, hw: float, hh: float, yard: Any, shed_rect: Any = None, wealth: float = 1.0) -> tuple[float, float, float, float] | None:  # type: ignore[misc]
        """The first fitting kitchen-garden position: a sunny SIDE, preferring the EAST (the kitchen/doma
        end, where the cook steps out to it), then the sunny SE/SW corners, and the windward WALL itself
        LAST - NEVER the shady north back, and never the south front (the threshing yard's apron) nor the west
        shed. The grove's belt sits on the windward WALL (the W face for the default NW wind), so the garden
        takes that wall only as a last resort - the windward CORNER (SW) is still fine, it tucks below the
        grove's arm. Keeping the garden off the windward wall is what frees it for the grove (a garden there
        was the #1 reason a windward arm went missing - e.g. a farm whose EAST faces the paddy). Spot or None."""
        gw, gh = self._garden_dims(hw * wealth, hh * wealth)  # PREVIEW: richer farm -> bigger garden
        wx = self._windward_x()  # windward horizontal sign (-1 W / +1 E / 0)
        wall = (wx, 0) if wx else None  # the windward wall the grove's belt wants
        sides = [(1, 0), (-1, 0), (1, 1), (-1, 1)]
        # try EVERY non-windward-wall side first - flush AND a little further out (to slip the garden past the
        # south yard into the windward CORNER) - and the windward wall itself only as a last resort, so an
        # E-paddy farm puts its garden in the SW corner and leaves the W wall free for the grove
        cands = [(dx, dy, e) for dx, dy in sides if (dx, dy) != wall for e in (0, 15 * self.bscale, 30 * self.bscale)]
        if wall:
            cands += [(wall[0], wall[1], e) for e in (0, 15 * self.bscale)]
        for dx, dy, extra in cands:
            ox = hx + dx * (hw / 2 + gw / 2 - 2 + extra)
            oy = hy + dy * (hh / 2 + gh / 2 - 2)
            if self._garden_fits(ox, oy, gw, gh, hx, hy, yard, shed_rect):
                return ox, oy, gw, gh
        return None

    def _attach_garden(self: Settlement, hx: float, hy: float, beds: Any) -> None:  # type: ignore[misc]
        """Draw a farmstead's dooryard kitchen garden BED(S) (before its house, so the house wins any abutment)
        and record them. The kitchen garden was a household staple, so every farmhouse gets one - but the plot
        is occasionally FRAGMENTED into two beds (`_garden_beds` decides where: flanking opposite walls, stacked,
        or side-by-side). `beds` is the reserved-and-collision-checked list of (cx,cy,w,h) rects from the bundle
        geometry; all beds of one house carry the same `of` parent, so `gardens_present` counts one garden per
        house and `garden_area_within_norms` sums their areas. Each bed is drawn as a slightly-irregular hand-
        worked quad (real dooryard beds were bent to paths and soil, not surveyed square); a lone bed can be more
        irregular than a split strip."""
        jit = 0.18 if len(beds) == 1 else 0.13
        for i, (bx, by, bw, bh) in enumerate(beds):
            poly = self._quad(bx, by, bw, bh, jit, 71.0 + i * 5.0)
            self._draw_garden(bx, by, bw, bh, poly)
            self.M["gardens"].append({"x": round(bx, 1), "y": round(by, 1), "w": bw, "h": bh, "rot": 0, "of": [hx, hy], "poly": [[round(px, 1), round(py, 1)] for px, py in poly]})
            self.placed.append((bx, by, bw, bh))
