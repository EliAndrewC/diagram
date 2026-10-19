"""Where the candidate house seats COME FROM - the settlement-form seed generators and the perimeter ring.

Split from settlement/rolling.py by feature 118 - see settlement/rolling/CLAUDE.md for the index.

Research: seed plumbing - NONE
"""

import math
import random
from typing import TYPE_CHECKING, Any

from .._geom import Pt

if TYPE_CHECKING:
    from ..core import Settlement


class SeedFormsMixin:
    def line_seeds(self: Settlement, p0: Pt, p1: Pt, n: int, half_band: float, rng: random.Random, form: str = "linear", record: bool = True) -> list[Pt]:  # type: ignore[misc]
        """House seeds strung ALONG a line (feature 005 `settlement_form` = 'linear'): a RIBBON of homesteads
        fronting a road / field-margin / dike instead of a nucleated blob - historically the cheapest big
        structural difference between two same-region villages (research.md D5; a levee, a valley-edge track,
        or a canal bank strings the houses out). Distributes `n` seeds along the segment `p0`->`p1` (uniform
        along its length) with a perpendicular jitter up to +/-`half_band`; the bundle solver then hugs each
        homestead to the field edge as usual. Records `meta.settlement_form` when `record=True`.

        Research: farms strung along a line - research/questions/0033-row-villages-resson.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: seeds uniform along the segment, jittered up to +-half_band across it
        """
        if record:
            self.M["meta"]["settlement_form"] = form
        (x0, y0), (x1, y1) = p0, p1
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1.0
        px, py = -dy / length, dx / length  # unit perpendicular to the line
        out: list[Pt] = []
        for _ in range(n):
            t = rng.random()
            b = rng.uniform(-1.0, 1.0) * half_band
            out.append((x0 + dx * t + px * b, y0 + dy * t + py * b))
        return out

    def scatter_seeds(self: Settlement, cx: float, cy: float, rx: float, ry: float, n: int, rng: random.Random, form: str = "dispersed", record: bool = True) -> list[Pt]:  # type: ignore[misc]
        """House seeds scattered LOOSELY and evenly over a BROAD area (feature 005 `settlement_form`
        = 'dispersed'): scattered farmsteads, each its own yashikirin-groved homestead, rather than a tight
        nucleus - the kainyo / Tonami dispersed-farmstead pattern of the well-watered plains. Area-uniform
        over the ellipse so the farms spread out; `try_place`'s field-adjacency + no-build blockers then
        filter them onto the dry margins, leaving them dotted along the field edges instead of clumped.
        Records `meta.settlement_form`. Pair with `s._nucleated = False` so each farm draws its OWN grove.

        Research: scattered farmsteads - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: area-uniform over an ellipse, then filtered onto the dry margins
        """
        if record:
            self.M["meta"]["settlement_form"] = form
        out: list[Pt] = []
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.random() ** 0.5  # area-uniform: an even scatter, not center-clumped
            out.append((cx + math.cos(a) * r * rx, cy + math.sin(a) * r * ry))
        return out

    def waterfront_seeds(self: Settlement, canal: Any, n: int, offset: float, rng: random.Random, form: str = "water_town", record: bool = True) -> list[Pt]:  # type: ignore[misc]
        """House seeds strung along BOTH banks of a canal (feature 005 `settlement_form` = 'water_town'): a
        Jiangnan-style water town where the houses FRONT the water, offset `offset` px to either side of the
        canal polyline. Records `meta.settlement_form`. (Per GM canon canals are a Lion-lands feature, so this
        form is typing-gated to Lion lands / a declared canal.) `try_place` then keeps each seed field-adjacent
        and off blockers, so the row packs cleanly along the waterfront.

        Research: water town fronting a canal - UNRESEARCHED: houses on alternate banks at a fixed offset, evenly spaced along the canal
        """
        if record:
            self.M["meta"]["settlement_form"] = form
        segs = [(canal[i], canal[i + 1]) for i in range(len(canal) - 1)]
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs) or 1.0
        out: list[Pt] = []
        for k in range(n):
            d = total * (k + 0.5) / n
            acc = 0.0
            for a, b in segs:
                ln = math.hypot(b[0] - a[0], b[1] - a[1])
                if acc + ln >= d:
                    t = (d - acc) / (ln or 1.0)
                    px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                    nx, ny = -(b[1] - a[1]) / (ln or 1.0), (b[0] - a[0]) / (ln or 1.0)  # canal normal
                    side = 1.0 if k % 2 == 0 else -1.0  # alternate banks
                    out.append((px + nx * offset * side + rng.uniform(-10, 10), py + ny * offset * side + rng.uniform(-10, 10)))
                    break
                acc += ln
        return out
