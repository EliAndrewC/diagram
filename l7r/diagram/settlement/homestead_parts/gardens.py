"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index.

Research: plumbing - NONE
"""

from typing import TYPE_CHECKING, Any

from .._geom import turn_about

if TYPE_CHECKING:
    from ..core import Settlement


class GardensMixin:
    def _draw_garden(self: Settlement, cx: float, cy: float, w: float, h: float, poly: Any, rot: float = 0.0) -> None:  # type: ignore[misc]
        """Draw one small dooryard KITCHEN GARDEN (saien): a tilled earthen bed with tidy planted rows
        of greens. Distinct from the tan threshing yard (bare swept earth) and the blue-green paddy quilt.
        The bed's outer footprint is an irregular quad (`poly`, absolute corner coords, UNTURNED) - a
        hand-worked plot bent to paths and soil, not surveyed square; the rows are laid out in the local
        (w,h) frame, and the whole group is turned by `rot`, its farmhouse's rake.

        Research:
            bed glyph - CONVENTION: a tilled fill with three rows of greens
            turned with its house - UNRESEARCHED: the bed takes the farmhouse's rake
        """
        x0, y0 = -w / 2, -h / 2
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
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

    def _attach_garden(self: Settlement, hx: float, hy: float, beds: Any, rot: float = 0.0) -> None:  # type: ignore[misc]
        """Draw a farmstead's dooryard kitchen garden BED(S) (before its house, so the house wins any abutment)
        and record them. The kitchen garden was a household staple, so every farmhouse gets one - but the plot
        is occasionally FRAGMENTED into two beds (`_garden_beds` decides where: flanking opposite walls, stacked,
        or side-by-side). `beds` is the reserved-and-collision-checked list of (cx,cy,w,h) rects from the bundle
        geometry; all beds of one house carry the same `of` parent, so `gardens_present` counts one garden per
        house and `garden_area_within_norms` sums their areas. Each bed is drawn as a slightly-irregular hand-
        worked quad (real dooryard beds were bent to paths and soil, not surveyed square); a lone bed can be more
        irregular than a split strip. Each bed takes its house's rake (`rot`) about its own center, for the
        reason `_attach_yard` gives.

        Research:
            every farmhouse a garden - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.html: one per house
            split into beds - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: one or two
                beds, measured as one garden
            hand-worked outline - CONVENTION: an irregular quad, jitter 0.18 for one bed and 0.13 for a split
            turned with its house - UNRESEARCHED: each bed takes the farmhouse's rake
        """
        jit = 0.18 if len(beds) == 1 else 0.13
        for i, (bx, by, bw, bh) in enumerate(beds):
            flat = self._quad(bx, by, bw, bh, jit, 71.0 + i * 5.0)
            poly = turn_about(flat, bx, by, rot)
            self._draw_garden(bx, by, bw, bh, flat, rot)
            self.M["gardens"].append({"x": round(bx, 1), "y": round(by, 1), "w": bw, "h": bh, "rot": round(rot, 2), "of": [hx, hy], "poly": [[round(px, 1), round(py, 1)] for px, py in poly]})
            self.placed.append((bx, by, bw, bh))
