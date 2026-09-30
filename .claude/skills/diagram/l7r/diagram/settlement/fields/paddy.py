"""Wet and dry field bodies, and the plot geometry they quilt themselves from.

Split from settlement/fields.py by feature 112 - see settlement/fields/CLAUDE.md for the index.
"""

import math
import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.tags import Split

from .._geom import (
    FLOODED_SHADES,
    PADDY_SHADES,
    RICE_GREENS,
    RIPE_SHADES,
    Poly,
    Pt,
    edge_dist,
    organic_bbox,
    organic_poly,
    point_in_poly,
    smooth_closed,
    smooth_points,
)
from .._knobs import Knob, knob_rng, register_knob

if TYPE_CHECKING:
    from ..core import Settlement


# THE WATER FRAME of a water-first field: f = downhill (NW->SE, the fall line), u = contour.
# Orthonormal, so xy <-> uf is exact and lossless in both directions.
#
# These were nested closures inside `water_field` until feature 112. They capture nothing from its
# frame but the rotation constant, so they are pure functions of their arguments - which is exactly
# the kind of thing that should not be re-created per call inside a 194-line body.
_UF_RT = 0.70710678


def _uf_u(px: float, py: float) -> float:
    """The CONTOUR coordinate of a point - constant along the slope."""
    return _UF_RT * (px - py)


def _uf_f(px: float, py: float) -> float:
    """The FALL coordinate of a point - increasing downhill."""
    return _UF_RT * (px + py)


def _uf_xy(u: float, f: float) -> Pt:
    """Back to canvas coordinates from a (contour, fall) pair."""
    return (_UF_RT * (u + f), _UF_RT * (f - u))


# IS ANY PADDY LEFT TO REST? (269 B01; research/fields.html 'Paddies left to rest (kataarashi)' and
# research/rendering/fields.html 'How our maps place paddies left to rest (kataarashi)', fields/250). The record attests
# two forms of a village's paddy, so it is a KNOB rolled per settlement:
#   settled    - cropped every year, no plot rests: the nucleated village on stable ground, and the setting's canon (a
#                paddy once made crops for centuries, and what limits rice is hands, not soil) sides with it.
#   unsettled  - this year a few whole plots rest (kataarashi), each scattered among the cropped plots, never a block,
#                and grazed rather than planted: the early medieval estate, where water or soil could not carry every
#                plot every year.
# The record reads the settled form as the commoner and gives no figure, so the 4:1 weighting is a GUESS. A resting plot
# is a whole basin inside its own bunds, never a patch within one - the blighted sub-region with its red crosses this
# replaced drew exactly that.
PADDY_REST = register_knob(Knob("paddy_rest", ["settled", "unsettled"], default="settled", weights={"settled": 0.8, "unsettled": 0.2}))
# HOW MANY REST, AND HOW FAR APART - liberties the record leaves the map, kept within it:
#   REST_COUNT        "a few plots of a hamlet's paddy", per field; the estate of 1102, with nearly a third resting, is the
#                     record's upper bound, not a hamlet's norm. 2-4 is a GUESS.
#   REST_APART_SIDES  scattered, not side by side: two resting plots stand at least this many plot sides apart,
#                     center to center, so no two share a bund - a map drawing convention for "scattered".
#   REST_FAR_POWER    they favor the far end of the water's run (the record's reading of "short water", a GUESS): a
#                     plot's chance grows as the square of how far down the fall it lies.
REST_COUNT = (2, 4)
REST_APART_SIDES = 3.0
REST_FAR_POWER = 2.0
REST_GRASS, REST_TUFT = "#C8CF92", "#8FA05E"  # the pasture's grass and tuft inks (`pasture`): a resting plot is grazed


def _ring_area(poly: Sequence[Pt]) -> float:
    n = len(poly)
    return abs(sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))) / 2


def _ring_center(poly: Sequence[Pt]) -> Pt:
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def rest_plots(cands: Sequence[tuple[Sequence[Pt], float]], rng: random.Random, count: int) -> list[int]:
    """Which of `cands` - `(ring, fall position)` pairs, the plots that may rest - rest this year: `count` of them at most,
    whole basins no smaller than the median candidate (a scrap of fabric is not a holding), drawn with a chance that grows
    toward the far end of the fall (`REST_FAR_POWER`) and kept `REST_APART_SIDES` mean plot sides apart. Indices into
    `cands`, ascending."""
    if not cands:
        return []
    areas = [_ring_area(r) for r, _f in cands]
    floor = sorted(areas)[len(areas) // 2]
    pool = [i for i, a in enumerate(areas) if a >= floor]
    side = (sum(areas[i] for i in pool) / len(pool)) ** 0.5
    fs = [f for _r, f in cands]
    f0 = min(fs[i] for i in pool)  # the fall is measured over the plots that may rest, so a stray scrap cannot stretch it
    span = (max(fs[i] for i in pool) - f0) or 1.0
    cents = [_ring_center(r) for r, _f in cands]
    chosen: list[int] = []
    while pool and len(chosen) < count:
        pick = rng.choices(pool, weights=[0.05 + ((fs[i] - f0) / span) ** REST_FAR_POWER for i in pool])[0]
        pool.remove(pick)
        if all(math.dist(cents[pick], cents[c]) >= REST_APART_SIDES * side for c in chosen):
            chosen.append(pick)
    return sorted(chosen)


class PaddyMixin:
    def paddy_field(  # type: ignore[misc]
        self: Settlement, shape: Any, label: Any, name: str, amp: float = 52, taxfree: int = 0, label_xy: Any = None, plot: float = 46, kind: str = "paddy"
    ) -> None:
        """shape: a bbox (x0,y0,x1,y1) OR a list of base polygon vertices (e.g. a V).
        `plot` is the target plot (sub-paddy) size in px: the field is quilted into jittered
        bunded plots at roughly this grain. Smaller -> a finer patchwork of more, smaller paddies.
        Default 46 is the fine grain that reads as intensively-worked premodern paddy (a 1-cho
        holding was subdivided into dozens of small irregular bunded plots). VERIFIED HONEST at the
        declared scales (audit 2026-07-21): the village grain (plot=34 at 2 ft/px -> ~435 m2) sits
        inside the real 130-600 m2 basin band, and the default (46 -> ~785 m2 at 2 ft/px) is within
        the real parcel range (mean ~1 mu = ~600 m2, merged holdings larger) - no legibility
        inflation is in play, and the houses are true-scale too. The bund stroke draws at near-true
        aze width for the map scale. See research/rendering/fields.html 'How our maps draw rice paddies and their plots (suiden)'."""
        from l7r.diagram.waterfields import AZE, aze_w

        bund = aze_w(self.ftpx)  # near-true-scale aze stroke (~1.5 real ft; the why lives at waterfields.AZE)
        if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape):
            bbox = tuple(shape)
            outline = organic_bbox(bbox, amp)
        else:
            base = list(shape)
            outline = organic_poly(base, amp)
            xs = [p[0] for p in outline]
            ys = [p[1] for p in outline]
            bbox = (min(xs), min(ys), max(xs), max(ys))
        x0, y0, x1, y1 = bbox
        smoothed = smooth_points(outline)
        self.M["fields"].append({"name": name, "bbox": list(bbox), "kind": kind, "outline": [[x, y] for (x, y) in smoothed]})
        self.field_polys.append(smoothed)
        d = smooth_closed(outline)
        cid = self._cid('fld')
        self.add(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        ex0, ey0, ex1, ey1 = x0 - amp, y0 - amp, x1 + amp, y1 + amp

        # PADDY PATCHWORK: pre-modern paddies were an IRREGULAR patchwork of odd-sized bunded plots fitted
        # together by piecemeal reclamation and inheritance - NOT the regular grid of modern (Meiji/Showa)
        # land consolidation. Build it by recursively splitting the field with straight, slightly-angled aze
        # (bund) lines that cut the LONG axis of each plot at a jittered fraction, down to the target grain
        # (with size variation), so bunds meet at T-junctions like real cadastral paddy. See research/fields.html 'Bunds between the paddies (aze)'.
        _fillstate = random.getstate()  # ISOLATE the paddy fill RNG: the patchwork, crop
        random.seed(int(abs(x0) * 7 + abs(y0) * 13 + abs(x1) * 3 + len(name)))  # roll, growth stage and mottle
        plots = self._paddy_plots((ex0, ey0, ex1, ey1), plot)  # are decorative and must NOT shift
        self.add(f'<g clip-path="url(#{cid})">')  # downstream house placement
        self.add(f'<rect x="{ex0:.0f}" y="{ey0:.0f}" width="{ex1 - ex0:.0f}" height="{ey1 - ey0:.0f}" fill="{AZE}"/>')
        interior: list[Any] = []
        rice: list[Poly] = []  # the whole, dry-surfaced rice basins inside the outline - the plots that may rest (`PADDY_REST`)
        for poly in plots:
            pts = ' '.join(f'{q[0]:.0f},{q[1]:.0f}' for q in poly)
            cx = sum(q[0] for q in poly) / len(poly)
            cy = sum(q[1] for q in poly) / len(poly)
            # CROP MIX: an irrigated valley exists to grow RICE (~85% of the watered common). Dry upland crops
            # (barley/veg, soy) cluster on the MARGINS - the higher, harder-to-water rim - while the well-watered
            # interior is all paddy. So dry/soy probability rises toward the field edge. See research/rendering/fields.html 'How our maps show the paddy through the rice year' ('Crop mix'.
            edge = max(0.0, 1.0 - edge_dist(cx, cy, smoothed) / (2.4 * plot))  # 1 at the rim, 0 deep interior
            r = random.random()
            dry_p, soy_p = 0.05 + 0.24 * edge, 0.03 + 0.11 * edge
            crop = 'dry' if r < dry_p else ('soy' if r < dry_p + soy_p else 'rice')
            if crop == 'rice':
                # a district transplants within a short window set by the crop before the rice, so its paddies are largely
                # ONE stage - here high-summer green - with only minor spread (early/late rice varieties, the odd
                # low flooded plot); NOT a rainbow of stages. See research/rendering/fields.html 'How our maps show the paddy through the rice year'.
                st = random.random()
                if st < 0.06:
                    fill, flooded = random.choice(FLOODED_SHADES), True
                elif st > 0.95:
                    fill, flooded = random.choice(RIPE_SHADES), False
                else:
                    fill, flooded = random.choice(PADDY_SHADES), False
                self.add(f'<polygon points="{pts}" fill="{fill}" stroke="{AZE}" stroke-width="{bund:.1f}" stroke-linejoin="round"/>')
                self._paddy_surface(poly, pts, flooded)
                if not flooded and point_in_poly(cx, cy, smoothed):
                    rice.append(poly)
            else:
                fill = 'url(#drycrop)' if crop == 'dry' else '#9CB36A'
                self.add(f'<polygon points="{pts}" fill="{fill}" stroke="{AZE}" stroke-width="{bund:.1f}" stroke-linejoin="round"/>')
                self._rows(poly, pts, crop)  # dryland crops ARE ridge/row-cultivated
            if point_in_poly(cx, cy, smoothed):
                interior.append((poly, cx, cy))
        # A RESTING PLOT is painted over its basin whole (`PADDY_REST`), and is no tax-free holding's plot.
        rested = [rice[i] for i in sorted(self.resting_plots(name, [(poly, _uf_f(*_ring_center(poly))) for poly in rice]))]
        for poly in rested:
            self.rest_basin(poly, bund)
        if label and taxfree:
            self._taxfree_plots([t for t in interior if not any(t[0] is poly for poly in rested)], taxfree)
        self.add('</g>')
        random.setstate(_fillstate)  # end fill-RNG isolation
        self.add(f'<path d="{d}" fill="none" stroke="#A98A52" stroke-width="3.5"/>')
        if label:
            # QUEUED FOR THE LABEL PHASE like every other caption (feature 157). This is one of the two
            # paths that emit a caption's `<text>` directly rather than through `label()`, so the
            # general deferral there does not reach it; `field_name_label` carries this exact markup
            # into the phase. Found by the round-2 spec review of feature 157 - dormant (no pool map
            # passes `label=` to either field), which is why it is a call swap and not a reflow.
            self.field_name_label(label, (x0, y0, x1, y1))

    @staticmethod
    def _split_convex(poly: Poly, px: float, py: float, nx: float, ny: float) -> tuple[Poly, Poly]:
        """Split a convex polygon by the line through (px, py) with normal (nx, ny) into (pos, neg) polygons."""

        def side(v: Pt) -> float:
            return (v[0] - px) * nx + (v[1] - py) * ny

        pos: Poly = []
        neg: Poly = []
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            sa, sb = side(a), side(b)
            if sa >= 0:
                pos.append(a)
            if sa <= 0:
                neg.append(a)
            if (sa > 0) != (sb > 0):
                t = sa / (sa - sb)
                pos.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
                neg.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        return pos, neg

    def _paddy_plots(self: Settlement, bbox: Any, grain: float) -> list[Poly]:  # type: ignore[misc]
        """Recursively split a field into an irregular patchwork whose plots share a coherent GRAIN aligned to
        the water and slope - the bunds run along the CONTOUR (NE-SW, for the default NW-uphill tilt) and down
        the FALL LINE (NW-SE), with plots mildly elongated along-contour and stepping downhill - so the paddy
        reads as ORGANIZED BY THE WATER, not randomly diced. Still irregular (jittered split fractions +
        slightly non-parallel bunds), just coherent. Tiles the bbox; clipped to the field outline."""
        ux, uy = 0.7071, -0.7071  # contour (along-slope) = a plot's LONG axis
        fx, fy = 0.7071, 0.7071  # fall line (downhill SE) = a plot's SHORT axis
        aspect = 1.7
        tvf, tvu = grain * 0.78, grain * 0.78 * aspect  # target extents across the fall line / along the contour
        x0, y0, x1, y1 = bbox
        stack: list[Poly] = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
        out: list[Poly] = []
        guard = 0
        while stack and guard < 24000:
            guard += 1
            poly = stack.pop()
            cx = sum(q[0] for q in poly) / len(poly)
            cy = sum(q[1] for q in poly) / len(poly)
            us = [q[0] * ux + q[1] * uy for q in poly]
            fs = [q[0] * fx + q[1] * fy for q in poly]
            u_ext, f_ext = max(us) - min(us), max(fs) - min(fs)
            over_f = f_ext > tvf * random.uniform(0.72, 1.45)
            over_u = u_ext > tvu * random.uniform(0.78, 1.6)
            if not over_f and not over_u:
                out.append(poly)
                continue
            if over_f and (not over_u or f_ext / tvf >= u_ext / tvu):
                nx, ny, lo, hi, cen = fx, fy, min(fs), max(fs), cx * fx + cy * fy  # contour bund (normal = fall line)
            else:
                nx, ny, lo, hi, cen = ux, uy, min(us), max(us), cx * ux + cy * uy  # cross bund (normal = contour)
            d = lo + (hi - lo) * random.uniform(0.36, 0.64)  # jittered split position
            px, py = cx + (d - cen) * nx, cy + (d - cen) * ny  # a point on the cut line
            ang = random.uniform(-0.12, 0.12)  # slight wobble - bunds not ruler-parallel
            ca, sa = math.cos(ang), math.sin(ang)
            nnx, nny = nx * ca - ny * sa, nx * sa + ny * ca
            a, b = self._split_convex(poly, px, py, nnx, nny)
            if len(a) >= 3 and len(b) >= 3:
                stack.append(a)
                stack.append(b)
            else:
                out.append(
                    poly
                )  # pragma: no cover - defensive: a line cutting a convex polygon yields two >=3-gons except the measure-zero exact-tangent case [174: KEPT, not deletable - it appends the polygon the caller receives]
        return out + stack

    def _taxfree_plots(self: Settlement, interior: Any, taxfree: int) -> None:  # type: ignore[misc]
        """Mark `taxfree` scattered interior paddy plots vermilion (a priestess's / temple's tax-free land)."""
        if not interior:
            return
        interior = sorted(interior, key=lambda t: (round(t[2] / 40), t[1]))  # spread them across the field
        n = len(interior)
        for i in sorted(set(min(n - 1, int(n * (k + 0.5) / (taxfree + 1))) for k in range(taxfree))):
            poly, cx, cy = interior[i]
            pts = ' '.join(f'{q[0]:.0f},{q[1]:.0f}' for q in poly)
            self.add(f'<polygon points="{pts}" fill="#A03020" fill-opacity="0.22" stroke="#A03020" stroke-width="4"/>')
            self.M["taxfree"].append([round(cx, 1), round(cy, 1)])

    def _paddy_surface(self: Settlement, poly: Poly, pts: str, flooded: bool, cap: int = 22, pitch: float | None = None) -> None:  # type: ignore[misc]
        """A WET paddy: a flooded, mottled sheet (irregular hand-transplanted shoots, plus a faint water sheen
        for a freshly-flooded plot) - NOT ruled rows. Premodern rice was transplanted irregularly; crisp
        checkrow planting (seijoue) is a Meiji improvement, so ruled rows on a paddy read as modern (the same
        era-tell as the consolidation grid). See research/rendering/fields.html 'How our maps show the paddy through the rice year'.

        Two mottle modes. Default (pitch=None): the sparse random scatter every comb map has always drawn
        (byte-stable). `pitch` (GM 2026-07-23, the polder-leftover repaint): a JITTERED GRID - dot centers
        ~pitch apart with alternate-row half-offset, +-pitch/3 jitter and ~10% dropout, so spacing lands
        irregular in the ~2/3..4/3 pitch band and no row or column ever rules through. That is the truer
        read of traditional transplanting (roughly EVEN density - density drives yield - but never ruled;
        real hills sit ~1/sq ft, one per PIXEL at 1 ft/px, so any drawable mottle is a sample regardless)."""
        xs = [q[0] for q in poly]
        ys = [q[1] for q in poly]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        rcid = self._cid('ps')
        g = [f'<clipPath id="{rcid}"><polygon points="{pts}"/></clipPath>', f'<g clip-path="url(#{rcid})">']
        if flooded:  # faint sheen lines = standing water catching the light
            for _ in range(2):
                yy = random.uniform(y0 + 2, y1 - 2)
                g.append(f'<line x1="{x0:.0f}" y1="{yy:.0f}" x2="{x1:.0f}" y2="{yy:.0f}" stroke="#CFDFD3" stroke-width="1.5" opacity="0.4"/>')
        if pitch is None:
            n = min(cap, max(3, int((x1 - x0) * (y1 - y0) / 80)))  # sparse irregular shoots (the transplant mottle); cap=22 suits ~0.05-ac comb cells
            for _ in range(n):
                g.append(f'<circle cx="{random.uniform(x0, x1):.1f}" cy="{random.uniform(y0, y1):.1f}" r="1.0" fill="#6F9061" opacity="0.5"/>')
        else:
            row = 0
            yy2 = y0 + random.uniform(0, pitch)
            while yy2 < y1:
                xx = x0 + random.uniform(0, pitch) + (pitch / 2 if row % 2 else 0.0)
                while xx < x1:
                    if random.random() > 0.1:
                        g.append(f'<circle cx="{xx + random.uniform(-pitch / 3, pitch / 3):.1f}" cy="{yy2 + random.uniform(-pitch / 3, pitch / 3):.1f}" r="1.0" fill="#6F9061" opacity="0.5"/>')
                    xx += pitch
                yy2 += pitch
                row += 1
        g.append('</g>')
        self.add(''.join(g))

    def _rows(self: Settlement, quad: Poly, pts: str, crop: str) -> None:  # type: ignore[misc]
        xq = [p[0] for p in quad]
        yq = [p[1] for p in quad]
        cx0, cx1, cy0, cy1 = min(xq), max(xq), min(yq), max(yq)
        ccx, ccy = (cx0 + cx1) / 2, (cy0 + cy1) / 2
        diag = math.hypot(cx1 - cx0, cy1 - cy0)
        theta = random.uniform(-0.6, 0.6)  # per-plot row angle
        dxu, dyu = math.cos(theta), math.sin(theta)
        nx, ny = -dyu, dxu
        rcid = self._cid('rc')
        self.add(f'<clipPath id="{rcid}"><polygon points="{pts}"/></clipPath>', cls="paddy")
        # _rows is only ever called for dry/soy plots (rice paddies get _paddy_surface, no rows), so the
        # styling here is the dryland one - dashed, olive, wider spacing
        spacing, stroke, wdt, dash, op = 13, '#7E9B54', 0.8, ' stroke-dasharray="1,3"', 0.85
        g = [f'<g clip-path="url(#{rcid})">']
        s = -diag / 2
        while s <= diag / 2:
            mx_, my_ = ccx + nx * s, ccy + ny * s
            g.append(
                f'<line x1="{mx_ - dxu * diag / 2:.0f}" y1="{my_ - dyu * diag / 2:.0f}" '
                f'x2="{mx_ + dxu * diag / 2:.0f}" y2="{my_ + dyu * diag / 2:.0f}" '
                f'stroke="{stroke}" stroke-width="{wdt}"{dash} opacity="{op}"/>'
            )
            s += spacing
        g.append('</g>')
        self.add(''.join(g))

    def resting_plots(self: Settlement, field: str, cands: Sequence[tuple[Sequence[Pt], float]]) -> set[int]:  # type: ignore[misc]
        """Which of a field's candidate plots rest this year (`PADDY_REST`): none on a settled paddy, `rest_plots`' pick on
        an unsettled one, from the field's own substream so one field's pick never moves another's. The form goes in
        `meta.paddy_rest`."""
        form = self.resolve("paddy_rest")
        self.M["meta"]["paddy_rest"] = form
        if form == "settled":
            return set()
        rng = knob_rng(self.seed, f"paddy_rest:{field}")
        return set(rest_plots(cands, rng, rng.randint(*REST_COUNT)))

    def rest_basin(self: Settlement, poly: Sequence[Pt], bund: float) -> None:  # type: ignore[misc]
        """A resting paddy plot: the whole basin inside its own bunds, grass where the rice would be, a few tufts of the
        grazing on it (`PADDY_REST`). Recorded in `fallow_patches` with its ring, and counted in `meta.paddy_rested`."""
        from l7r.diagram.waterfields import AZE

        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
        self.add(f'<polygon points="{pts}" fill="{REST_GRASS}" stroke="{AZE}" stroke-width="{bund:.2f}" stroke-linejoin="round"/>', cls=Split("fallow", "bund"))
        cx, cy = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
        rng = random.Random(int(abs(cx) * 7 + abs(cy) * 13))  # positional: the tufts are decoration and move nothing else
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        tufts = []
        for _ in range(max(3, int(_ring_area(poly) / 900))):
            tx, ty = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
            if point_in_poly(tx, ty, list(poly)):
                tufts.append(f'<path d="M{tx - 3:.1f},{ty + 2:.1f} L{tx:.1f},{ty - 4:.1f} L{tx + 3:.1f},{ty + 2:.1f}" fill="none" stroke="{REST_TUFT}" stroke-width="0.8"/>')
        self.add("".join(tufts), cls="fallow")
        self.M["fallow_patches"].append({"outline": [[round(p[0], 1), round(p[1], 1)] for p in poly], "form": "rested_basin"})
        self.M["meta"]["paddy_rested"] = self.M["meta"].get("paddy_rested", 0) + 1

    def water_field(  # type: ignore[misc]
        self: Settlement, shape: Any, label: Any, name: str, source: Any, drain: Any, amp: float = 52, taxfree: int = 0, plot: float = 34, label_xy: Any = None, drain_anchor: Any = None
    ) -> None:
        """A rice field built WATER-FIRST: the irrigation network is the generative skeleton, and the plots,
        crops, and colors are all DERIVED from it, so the map actually communicates the hydrology. Water
        enters from `source` (the high NW side, fed from the pond) and drains to `drain` (the low SE side). A
        HEAD ditch runs along the high edge; LATERALS run down the fall line, dividing the field into strips;
        paddies stack between them; a DRAIN ditch collects at the low edge and leaves toward `drain`. Crop
        FOLLOWS the water (rice hugging the ditches, dry upland crops where the network doesn't reach - wide-
        strip middles and the margins); the paddy is ~ONE green (a rice field, not a color mix). Records a
        feed channel (pond->field) and a drain channel (field->drain) so the checks see the supply. See
        research/fields.html 'Where does a field's water come from, and how is it shared out?'."""
        if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape):
            bbox = tuple(shape)
            outline = organic_bbox(bbox, amp)
        else:
            outline = organic_poly(list(shape), amp)
            xs = [q[0] for q in outline]
            ys = [q[1] for q in outline]
            bbox = (min(xs), min(ys), max(xs), max(ys))
        x0, y0, x1, y1 = bbox
        smoothed = smooth_points(outline)
        self.M["fields"].append({"name": name, "bbox": list(bbox), "kind": "paddy", "outline": [[x, y] for (x, y) in smoothed]})
        self.field_polys.append(smoothed)
        d = smooth_closed(outline)
        cid = self._cid('fld')
        self.add(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        from l7r.diagram.waterfields import AZE, aze_w

        bund = aze_w(self.ftpx)

        ex0, ey0, ex1, ey1 = x0 - amp, y0 - amp, x1 + amp, y1 + amp
        ous = [_uf_u(px, py) for px, py in smoothed]
        ofs = [_uf_f(px, py) for px, py in smoothed]
        umin, umax = min(ous) - plot, max(ous) + plot
        fmin, fmax = min(ofs) - plot, max(ofs) + plot
        fhi, flo = min(ofs), max(ofs)  # the field's real high (source) / low (drain) edges
        fh, fd = fhi + plot * 1.4, flo - plot * 1.4  # the MAIN canal (near the high edge) + DRAIN (near the low)

        stt = random.getstate()  # ISOLATE the fill RNG (decorative; must not shift houses)
        random.seed(int(abs(x0) * 7 + abs(y0) * 13 + abs(x1) * 3 + len(name)))

        # LATERALS: strip boundaries in u, spaced 1.4-3.2 plots apart (varied width). Each is a continuous
        # wobbly line down f (so both neighboring strips follow the SAME lateral -> a real ditch, T-junctions).
        # u-grid: plot-wide columns (all wobble down f). Every 2-4 columns carries a LATERAL DITCH; a plot is
        # watered from an adjacent lateral or by cascade from the plot above, so the plots FAR from any lateral
        # (wide-gap middles) and at the field MARGINS are the hard-to-water ground -> dry crops go there.
        ub = [umin]
        while ub[-1] < umax - plot * 0.55:
            ub.append(ub[-1] + plot * random.uniform(0.9, 1.35))
        ub.append(umax)
        phase = [random.uniform(0, 6.28) for _ in ub]

        def uline(i: int, f: float) -> float:
            if i == 0 or i == len(ub) - 1:
                return ub[i]
            return ub[i] + 5.0 * math.sin(f / 66.0 + phase[i]) + 3.0 * math.sin(f / 29.0 + phase[i] * 1.7)

        laterals: list[int] = []
        i = random.randint(1, 2)
        while i < len(ub) - 1:
            laterals.append(i)
            i += random.randint(4, 6)

        self.add(f'<g clip-path="url(#{cid})">')
        self.add(f'<rect x="{ex0:.0f}" y="{ey0:.0f}" width="{ex1 - ex0:.0f}" height="{ey1 - ey0:.0f}" fill="{AZE}"/>')
        interior: list[Any] = []
        ndry, nrice = 0, 0
        for k in range(len(ub) - 1):
            rows = [fmin]
            while rows[-1] < fmax - plot * 0.6:
                rows.append(rows[-1] + plot * random.uniform(0.85, 1.5))
            rows.append(fmax)
            for j in range(len(rows) - 1):
                fa, fb = rows[j], rows[j + 1]
                fm = (fa + fb) / 2
                quad = [_uf_xy(uline(k, fa), fa), _uf_xy(uline(k + 1, fa), fa), _uf_xy(uline(k + 1, fb), fb), _uf_xy(uline(k, fb), fb)]
                pts = ' '.join(f'{q[0]:.0f},{q[1]:.0f}' for q in quad)
                cx = sum(q[0] for q in quad) / 4
                cy = sum(q[1] for q in quad) / 4
                edgef = max(0.0, 1.0 - edge_dist(cx, cy, smoothed) / (1.4 * plot))
                un_irrig = fm < fh or fm > fd  # above the main canal / below the drain: gravity can't flood it
                if un_irrig or edgef + random.uniform(-0.08, 0.08) > 0.6:
                    crop = 'dry' if random.random() < 0.62 else 'soy'
                    fill = 'url(#drycrop)' if crop == 'dry' else '#9CB36A'
                    self.add(f'<polygon points="{pts}" fill="{fill}" stroke="{AZE}" stroke-width="{bund:.1f}" stroke-linejoin="round"/>')
                    self._rows(quad, pts, crop)
                    ndry += 1
                else:
                    near_ditch = abs(fm - fh) < plot * 1.4 or abs(fm - fd) < plot * 1.4  # water pools at the canal/drain
                    ro = random.random()
                    if near_ditch and ro < 0.3:
                        fill, flooded = random.choice(FLOODED_SHADES), True
                    elif ro > 0.975:
                        fill, flooded = random.choice(RIPE_SHADES), False
                    else:
                        fill, flooded = random.choice(RICE_GREENS), False
                    self.add(f'<polygon points="{pts}" fill="{fill}" stroke="{AZE}" stroke-width="{bund:.1f}" stroke-linejoin="round"/>')
                    self._paddy_surface(quad, pts, flooded)
                    nrice += 1
                if point_in_poly(cx, cy, smoothed):
                    interior.append((quad, cx, cy))
        if label and taxfree:
            self._taxfree_plots(interior, taxfree)
        self.add('</g>')

        # THE WATER NETWORK, drawn ON TOP and clipped to the field: laterals down the fall line, a head ditch
        # along the high edge, a drain ditch along the low edge - the plots were carved to these, so they align.
        # CONTINUOUS main + drain along the field's true HIGH / LOW boundaries - sampled only where the field
        # actually exists (bnd returns None otherwise), so no junk endpoints jutting outside. Then LATERALS
        # whose ends SNAP onto the nearest main / drain node - so every lateral provably meets both, and the
        # main/drain read as continuous canals (not a sparse dotted line). Paddies between laterals cascade.
        main_pts, drain_pts = self._wf_main_drain(ous, fmin, fmax, plot, smoothed)
        self.add(f'<g clip-path="url(#{cid})">')
        if len(main_pts) >= 2:
            self._wf_ditch(name, main_pts, 3.3, "main")  # continuous MAIN canal along the high edge
            self._wf_ditch(name, drain_pts, 3.0, "drain")  # continuous DRAIN along the low edge
            for li in laterals:
                if not (0 < li < len(ub) - 1):
                    continue  # pragma: no cover - defensive: laterals are built strictly inside (0, len(ub)-1) [174: KEPT, not deletable - removing it would index out of range rather than skip]
                ut = ub[li]
                t, bt = self._wf_bnd(smoothed, fmin, fmax, ut, fmin, 6), self._wf_bnd(smoothed, fmin, fmax, ut, fmax, -6)
                if t is None or bt is None:
                    continue
                tf, bf = t + plot * 0.7, bt - plot * 0.7
                if bf - tf <= plot * 0.7:
                    continue
                mid = [_uf_xy(uline(li, f), f) for f in [tf + i * 14 for i in range(1, int((bf - tf) / 14) + 1)] if f < bf]
                self._wf_ditch(name, [_uf_xy(ut, tf)] + mid + [_uf_xy(ut, bf)], 2.0, "lateral")  # ends on the continuous main/drain line
        self.add('</g>')
        random.setstate(stt)

        # feed the MAIN at a single point from the pond; empty the DRAIN to the outlet (anchors safely inside).
        safe = [(t[1], t[2]) for t in interior if edge_dist(t[1], t[2], smoothed) >= 14] or [((x0 + x1) / 2, (y0 + y1) / 2)]
        msafe = [q for q in main_pts if edge_dist(q[0], q[1], smoothed) >= 11] or main_pts or safe
        dsafe = [q for q in drain_pts if edge_dist(q[0], q[1], smoothed) >= 11] or drain_pts or safe
        head_pt = min(msafe, key=lambda q: (q[0] - source[0]) ** 2 + (q[1] - source[1]) ** 2)
        drain_pt = min(dsafe, key=lambda q: (q[0] - drain[0]) ** 2 + (q[1] - drain[1]) ** 2)
        self.channel(source, head_pt, {"kind": "pond"}, {"kind": "field", "name": name}, amp=8, width=2.6)
        self.channel(drain_pt, drain, {"kind": "field", "name": name}, drain_anchor or {"kind": "offmap"}, amp=8, width=2.6)

        self.add(f'<path d="{d}" fill="none" stroke="#A98A52" stroke-width="3.5"/>')
        if label:
            # QUEUED FOR THE LABEL PHASE like every other caption (feature 157). This is one of the two
            # paths that emit a caption's `<text>` directly rather than through `label()`, so the
            # general deferral there does not reach it; `field_name_label` carries this exact markup
            # into the phase. Found by the round-2 spec review of feature 157 - dormant (no pool map
            # passes `label=` to either field), which is why it is a call swap and not a reflow.
            self.field_name_label(label, (x0, y0, x1, y1))

    def _wf_ditch(self: Settlement, name: str, pairs: Any, w: float, role: str) -> None:  # type: ignore[misc]
        """Draw a water-first field's ditch AND record it, so the checks can validate what was drawn."""
        pts = " ".join(f"{px:.0f},{py:.0f}" for px, py in pairs)
        self.add(f'<polyline points="{pts}" fill="none" stroke="#9CB4C8" stroke-width="{w}" opacity="0.9" stroke-linejoin="round" stroke-linecap="round"/>')
        self.M["field_ditches"].append({"poly": [[round(px, 1), round(py, 1)] for px, py in pairs], "role": role, "field": name})

    def _wf_bnd(self: Settlement, smoothed: Poly, fmin: float, fmax: float, u: float, lo: float, step: float) -> float | None:  # type: ignore[misc]
        """The first fall-coordinate INSIDE the field scanning from `lo`; None where the field is absent."""
        f = lo
        while f <= fmax if step > 0 else f >= fmin:
            if point_in_poly(_uf_xy(u, f)[0], _uf_xy(u, f)[1], smoothed):
                return f
            f += step
        return None

    def _wf_main_drain(self: Settlement, ous: list[float], fmin: float, fmax: float, plot: float, smoothed: Poly) -> tuple[Poly, Poly]:  # type: ignore[misc]
        """Sample the CONTINUOUS main and drain lines along the field's true high / low boundaries.

        Sampled only where the field actually exists (`_wf_bnd` returns None otherwise), so no junk
        endpoints jut outside, then smoothed to kill the acute turns a sharply bending boundary
        would otherwise put in them."""
        us = [min(ous) + i * 11 for i in range(int((max(ous) - min(ous)) / 11) + 1)] + [max(ous)]
        main_pts: list[Pt] = []
        drain_pts: list[Pt] = []
        for u in us:
            t, bt = self._wf_bnd(smoothed, fmin, fmax, u, fmin, 6), self._wf_bnd(smoothed, fmin, fmax, u, fmax, -6)
            if t is not None and bt is not None and bt - t > plot * 1.4:
                main_pts.append(_uf_xy(u, t + plot * 0.7))
                drain_pts.append(_uf_xy(u, bt - plot * 0.7))

        def smooth(pts: Poly) -> Poly:  # kill acute turns where the boundary bends sharply
            if len(pts) < 3:
                return pts  # pragma: no cover - defensive: a real field spans many u-columns, so main/drain always have >=3 sampled points [174: KEPT, not deletable - a terminal return]
            for _ in range(3):
                pts = [pts[0]] + [((pts[i - 1][0] + pts[i][0] + pts[i + 1][0]) / 3, (pts[i - 1][1] + pts[i][1] + pts[i + 1][1]) / 3) for i in range(1, len(pts) - 1)] + [pts[-1]]
            return pts

        return smooth(main_pts), smooth(drain_pts)

    def fallow_field(self: Settlement, bbox: Any, name: str, amp: float = 34) -> None:  # type: ignore[misc]
        outline = organic_bbox(bbox, amp)
        d = smooth_closed(outline)
        self.add(f'<path d="{d}" fill="url(#fallow)" stroke="#9C7A40" stroke-width="1.8" stroke-dasharray="6,4"/>')
        sm = smooth_points(outline)
        self.M["fields"].append({"name": name, "bbox": list(bbox), "kind": "fallow", "outline": [[x, y] for (x, y) in sm]})
        self.field_polys.append(sm)
