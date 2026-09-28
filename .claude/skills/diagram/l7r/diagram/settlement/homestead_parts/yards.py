"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly, turn_about

if TYPE_CHECKING:
    from ..core import Settlement

# THE STRAW MAT, 3 x 6 ft (feature 282): the mushiro was woven about 3 shaku by 6 (90 x 180 cm; tobunken-mushiro), and a
# yard at harvest was a floor of them - "mats were spread to fill the yard" (Kitamoto). Laid long side across the yard's
# width, in rows (a GUESS: no page read says how they lay), the rows sized inside a 1 ft inset; what keeps the outer row
# off the floor's outline stroke is the edge clearance below (settlement-review, Kashikawa, 2026-09-28).
MAT_FT = (6.0, 3.0)
MAT_INSET_FT = 1.0
# ...and every mat corner at least this far inside the floor's DRAWN outline, which `_quad` pulls in at its corners: the
# rect inset alone left outer mats 0.1 ft off a pulled-in edge (measured on the pool's SVGs, 2026-09-28).
MAT_EDGE_CLEAR_FT = 1.0
MAT_SQ_FT = MAT_FT[0] * MAT_FT[1]
# THE GAP LEFT BETWEEN DRAWN MATS, widest first (feature 282, a CONVENTION): a real yard's mats lay edge to edge, and drawn
# so they read as a textured floor. A 2 ft gap on every side leaves each mat on its own - the 2 ft pitch alone is 45% of a
# full cover - and a yard too small or too clipped (by its pulled-in corners and the rack) to reach a third of one at that
# gap closes it a step at a time, never below 1 ft; a step that overshoots two thirds is thinned back evenly (FR-004).
MAT_GAPS_FT = (2.0, 1.5, 1.0)
# EACH MAT LAID BY HAND, NOT SET IN A PATTERN (settlement-reviews of 2026-09-28): every REGULAR layout read as paving - a
# checkered half as pavers meeting at their corners (Sawada), square rows as a tiled grid (Inashiro), rows set over by half
# a mat as brick bond (Kashikawa). So each mat is nudged off its row by up to this much and turned by up to this many
# degrees, a positional draw from its row and column (never the map's random stream), and kept at its row position
# wherever the nudge would carry it off the floor or onto the rack.
MAT_JITTER_FT = 0.4
MAT_STROKE_FT = 0.2  # half the mat outline's drawn width (0.4 at a hamlet's 1 ft to the px)
MAT_INK_CLEAR_FT = 0.1  # bare ground left between two mats' drawn outlines, at the least
MAT_JITTER_DEG = 6.0


def _mat_hash(r: int, c: int, salt: float) -> float:
    """A deterministic draw in [0, 1) for the mat in row `r`, column `c` - positional, like `Settlement._hjit`."""
    v = math.sin(r * 12.9898 + c * 78.233 + salt * 37.719) * 43758.5453
    return v - math.floor(v)


def _mat_corners(x: float, y: float, mw: float, mh: float, a: float) -> list[tuple[float, float]]:
    """The four corners of a mat whose unturned rect is (x, y, mw, mh), turned `a` degrees about its center."""
    cx, cy, t = x + mw / 2.0, y + mh / 2.0, math.radians(a)
    return [(cx + dx * math.cos(t) - dy * math.sin(t), cy + dx * math.sin(t) + dy * math.cos(t)) for dx, dy in ((-mw / 2, -mh / 2), (mw / 2, -mh / 2), (mw / 2, mh / 2), (-mw / 2, mh / 2))]


# THE RACK BY THE HOUSE (feature 282): a line of posts and poles hung with sheaves, drawn 2.5 ft wide so it reads - a
# map drawing CONVENTION (the real poles are inches thick) - and inset 2 ft from the yard's front edge and 1 ft from its side. It is
# drawn as a straw-gold LINE of hung sheaves with dark post dots and no box: drawn first as an outlined box, it read as
# the woodpile beside the same houses (settlement-review, Sawada, 2026-09-28).
RACK_WIDTH_FT = 2.5
RACK_INSET_FT = 2.0  # from the yard's front (house-facing) edge
# ...but only 1 ft from its SIDE, so the rack stands in the slack the centered mat rows leave at the yard's flanks and does
# not take a column of mats: at 2 ft it cost the smallest yards a third of their floor (Sawada's 20 x 14 ft yard drew 4 mats
# of a floor of 6, the gate, 2026-09-28).
RACK_SIDE_INSET_FT = 1.0
RACK_MIN_FT = 4.0  # shorter than this and it is not drawn: a side clipped by the map-south rule to a stub reads as litter
RACK_CLEAR_FT = 0.25  # the rack stops this far north of the yard's midline (the manifest rounds to 0.1 px)
RACK_POST_FT = 6.0  # a post every ~6 ft (a GUESS within the attested racks: posts at even spacing, kotobank-hasa-nipponica)


def mat_cells(w: float, h: float, poly: list[tuple[float, float]], ftpx: float, keep_out: tuple[float, float, float, float] | None = None) -> list[tuple[float, float, float, float, float]]:
    """The mats one yard draws, as (x, y, w, h, angle) in the yard's LOCAL, unturned frame (its center at 0,0): the
    unturned rect and the degrees it is turned about its own center.

    The real yard was covered edge to edge (40-60 mats), which at map scale reads as a textured floor rather than as mats,
    so the drawing lays them in rows across the whole yard with a gap around each, each nudged and turned a little as if
    laid by hand, a third to two thirds of a full cover - the GM's drawing convention (2026-09-28: "at this scale, we
    can't render dozens of mats and have that be legible. So our threshing yard glyphs show a smaller number to give the
    impression that there are many of them"). The rows are centered inside a 1 ft inset; a mat is kept only if its
    four corners lie at least `MAT_EDGE_CLEAR_FT` inside the yard's quad `poly` (local coords) and miss `keep_out` (the
    rack's footprint, x0, y0, x1, y1). The count is held to at least a third of the yard's full cover (area / 18 sq ft;
    spec 282 FR-004) by closing the gap (`MAT_GAPS_FT`), at the widest gap that reaches it; where none does, the gap that
    holds the most."""
    mw, mh, inset, clear = MAT_FT[0] / ftpx, MAT_FT[1] / ftpx, MAT_INSET_FT / ftpx, MAT_EDGE_CLEAR_FT / ftpx
    floor = math.ceil((w * ftpx) * (h * ftpx) / MAT_SQ_FT / 3.0)

    def fits(corners: list[tuple[float, float]]) -> bool:
        if not all(point_in_poly(px, py, poly) and edge_dist(px, py, poly) >= clear for px, py in corners):
            return False
        xs, ys = [p[0] for p in corners], [p[1] for p in corners]
        return keep_out is None or not (min(xs) < keep_out[2] and max(xs) > keep_out[0] and min(ys) < keep_out[3] and max(ys) > keep_out[1])

    best: list[tuple[float, float, float, float, float]] = []
    for gap_ft in MAT_GAPS_FT:
        g = gap_ft / ftpx
        cols, rows = int((w - 2 * inset + g) // (mw + g)), int((h - 2 * inset + g) // (mh + g))
        gx0, gy0 = -(cols * (mw + g) - g) / 2.0, -(rows * (mh + g) - g) / 2.0
        base = []
        for r in range(rows):
            for c in range(cols):
                x, y = gx0 + c * (mw + g), gy0 + r * (mh + g)
                if fits(_mat_corners(x, y, mw, mh, 0.0)):
                    base.append((r, c, x, y))
        mats = _lay_by_hand(base, mw, mh, ftpx, fits)
        if len(mats) > len(best):
            best = mats
        if len(mats) >= floor:
            break
    # A YARD THAT CANNOT HOLD A THIRD WITH ROOM ROUND EVERY MAT DRAWS AS MANY AS FIT AT 1 FT (spec 282 FR-004, amended
    # 2026-09-28): the narrower steps were tried and each read as paving in the settlement-reviews - edge to edge (rounds 2
    # and 3), and 0.5 ft (rounds 4 to 6: no room to lay a mat askew, even thinned). At 1 ft every mat keeps bare ground and
    # room to lie askew; eleven yards of the pool fall short of a third there, by up to half, the fewest drawing 3.
    return thin_evenly(best, max(1, math.floor((w * ftpx) * (h * ftpx) / MAT_SQ_FT * 2.0 / 3.0)))


def _quad_gap(a: list[tuple[float, float]], b: list[tuple[float, float]]) -> float:
    """The gap between two convex quads: the least corner-to-edge distance either way, 0 where a corner of one is inside
    the other."""
    if any(point_in_poly(px, py, b) for px, py in a) or any(point_in_poly(px, py, a) for px, py in b):
        return 0.0
    return min(min(edge_dist(px, py, b) for px, py in a), min(edge_dist(px, py, a) for px, py in b))


def _lay_by_hand(base: list[tuple[int, int, float, float]], mw: float, mh: float, ftpx: float, fits: Any) -> list[tuple[float, float, float, float, float]]:
    """Set each mat of the lattice `base` (row, column, x, y) down by hand: nudged up to `MAT_JITTER_FT` and turned up to
    `MAT_JITTER_DEG` by a positional draw, and kept so only where its corners still fit the floor (`fits`) and its drawn
    outline stays `MAT_INK_CLEAR_FT` clear of every neighbor's - the mats already laid and the lattice spots still to come.
    Where the full draw does not fit, the same turn with no nudge, then half the turn, then the lattice spot unturned.

    ONE BUDGET PER MAT, NOT A FORMULA PER GAP (settlement-reviews of round 6, 2026-09-28): a turn limit derived from the
    gap and the nudge fell to nothing at the 1 ft step as well as the 0.5 ft one, and six to eleven yards a map drew a rigid
    grid again; asking each mat whether its own turn fits beside its own neighbors keeps the turn wherever there is room."""
    need = (MAT_INK_CLEAR_FT + 2 * MAT_STROKE_FT) / ftpx
    laid: list[tuple[float, float, float, float, float]] = []
    quads: list[list[tuple[float, float]]] = []
    for k, (r, c, x, y) in enumerate(base):
        dx, dy = (2 * _mat_hash(r, c, 1.0) - 1) * MAT_JITTER_FT / ftpx, (2 * _mat_hash(r, c, 2.0) - 1) * MAT_JITTER_FT / ftpx
        a = (2 * _mat_hash(r, c, 3.0) - 1) * MAT_JITTER_DEG
        ahead = [_mat_corners(bx, by, mw, mh, 0.0) for _r, _c, bx, by in base[k + 1 :]]
        for jx, jy, ja in ((x + dx, y + dy, a), (x, y, a), (x, y, a / 2.0), (x, y, 0.0)):
            q = _mat_corners(jx, jy, mw, mh, ja)
            if ja == 0.0 or (fits(q) and all(_quad_gap(q, o) >= need for o in quads + ahead)):
                laid.append((jx, jy, mw, mh, ja))
                quads.append(q)
                break
    return laid


def thin_evenly(items: list[Any], cap: int) -> list[Any]:
    """`items` cut to `cap`, dropping evenly across the list rather than from one end (centered picks, so the drops fall
    mid-yard). The mats' two-thirds ceiling (spec 282 FR-004): a step that closes the gap can more than double a small
    yard's count, and this is what holds it under two thirds whatever the step."""
    if len(items) <= cap:
        return items
    step = len(items) / cap
    return [items[int((i + 0.5) * step)] for i in range(cap)]


def rack_segment(w: float, h: float, rot: float, ftpx: float, side: int) -> tuple[float, float, float, float] | None:
    """The rack by the house, as (x, y0, y1, half width) in the yard's LOCAL frame, or None where no side takes one.

    It runs along one of the yard's two side edges (local x = +/-), from the edge facing the house (local north) toward
    the middle, and never past it: the half nearest the house (505's GUESS - the sources are silent on the side). It must
    also stay out of the yard's MAP-south half, because the drying floor needs the sun from the south (entry 030) - and
    that is solved in MAP coordinates, after the house's rake `rot`, so it holds for any turn (a quarter-turned homestead
    included): a local point (x, y) lies map-south of the yard's center by x sin(rot) + y cos(rot), and every corner of the
    rack's footprint must keep that at or below zero. `side` (+1 east, -1 west, in the local frame) is tried first.

    THE HALF NEAREST THE HOUSE YIELDS BEFORE THE KNOB DOES (plan review, 2026-09-28): it is our guess, while the knob is
    the research's - where the weather is changeable EVERY farmstead gathers its rack by the house - so where neither side's
    near half leaves `RACK_MIN_FT`, the whole side is tried, still held off the map-south half. Some part of one side edge
    always lies map-north of the center, so a yard of the sizes the roll makes always takes a rack."""
    th = math.radians(rot)
    s, c = math.sin(th), math.cos(th)
    hw, inset, minlen = RACK_WIDTH_FT / 2.0 / ftpx, RACK_INSET_FT / ftpx, RACK_MIN_FT / ftpx
    for far, sd in ((0.0, side), (0.0, -side), (h / 2.0 - inset, side), (h / 2.0 - inset, -side)):
        x = sd * (w / 2.0 - RACK_SIDE_INSET_FT / ftpx - hw)
        lo, hi = -h / 2.0 + inset, far
        for xp in (x - hw, x + hw):  # each long edge of the footprint: y * c <= -xp * s
            k = -xp * s - RACK_CLEAR_FT / ftpx  # a hair north of the midline, so the manifest's rounding cannot carry it over
            if abs(c) < 1e-9:
                if k < 0.0:
                    hi = lo - 1.0  # this side lies map-south of the center along its whole length
            elif c > 0.0:
                hi = min(hi, k / c)
            else:
                lo = max(lo, k / c)
        if hi - lo >= minlen:
            return (x, lo, hi, hw)
    return None


class ThreshingYardsMixin:
    def _draw_threshing_yard(self: Settlement, cx: float, cy: float, w: float, h: float, poly: Any, rot: float = 0.0) -> dict[str, Any]:  # type: ignore[misc]
        """Draw one tamped earthen threshing yard as the harvest leaves it (feature 282): a floor of straw mats, and a
        rack by the house where the settlement's harvest weather is changeable. The outer footprint is a
        slightly-irregular quad (`poly`, absolute corner coords, UNTURNED); the interior is laid out in the local (w,h)
        frame and the whole group turned by `rot`, its farmhouse's rake. Returns what it drew for the manifest: `mats`
        (the count) and, with a rack, `rack` (its footprint's four corners in MAP coordinates)."""
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
        local = [(px - cx, py - cy) for px, py in poly]
        pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in local)
        g.append(f'<polygon points="{pts}" fill="#D2BE94" stroke="#A98E54" stroke-width="1.5"/>')  # tamped earthen floor
        rack = rack_segment(w, h, rot, self.ftpx, 1 if self._hjit(cx, cy, 53.0) < 0.5 else -1) if self._house_racks else None
        pad = 0.25 / self.ftpx  # the mats keep a quarter foot off the rack - a wider margin cost the smallest yards a column
        keep = (rack[0] - rack[3] - pad, rack[1] - pad, rack[0] + rack[3] + pad, rack[2] + pad) if rack else None
        mats = mat_cells(w, h, local, self.ftpx, keep)
        for mx, my, mw, mh, ma in mats:  # straw mats (mushiro), a third to two thirds of those that covered the floor, each laid by hand - a CONVENTION
            turn = f' transform="rotate({ma:.1f} {mx + mw / 2:.2f} {my + mh / 2:.2f})"' if ma else ""
            g.append(f'<rect x="{mx:.2f}" y="{my:.2f}" width="{mw:.2f}" height="{mh:.2f}"{turn} fill="#E4CC86" stroke="#C4A45E" stroke-width="0.4"/>')
        out: dict[str, Any] = {"mats": len(mats)}
        if rack:
            x, y0, y1, hw = rack
            g.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="#D9B64A" stroke-width="{2 * hw:.2f}"/>')  # hung sheaves
            g.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="#6B4A22" stroke-width="0.5"/>')  # the pole
            n = max(1, round((y1 - y0) * self.ftpx / RACK_POST_FT))
            for i in range(n + 1):  # the posts, as dots
                g.append(f'<circle cx="{x:.2f}" cy="{y0 + (y1 - y0) * i / n:.2f}" r="{hw * 0.55:.2f}" fill="#5A3F1E"/>')
            th = math.radians(rot)
            out["rack"] = [
                [round(cx + px * math.cos(th) - py * math.sin(th), 2), round(cy + px * math.sin(th) + py * math.cos(th), 2)] for px, py in ((x - hw, y0), (x + hw, y0), (x + hw, y1), (x - hw, y1))
            ]
        g.append('</g>')
        self.add(''.join(g), cls="threshing yard")
        return out

    def _yard_fits(self: Settlement, x: float, y: float, w: float, h: float, hx: float, hy: float) -> bool:  # type: ignore[misc]
        """A threshing yard fits where it is in-bounds, on DRY ground (clear of paddies / blocks),
        off any lane, and clear of every placed footprint EXCEPT its own farmhouse (it abuts that)."""
        if x < 55 or x > self.W - 55 or y < 88 or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):
            return False
        if self._in_blocked(x, y) or self._near_corridor(x, y):
            return False
        if self._rect_hits((x, y, w, h), self.dry_polys):  # hem strips / garden tracts are cropland too -
            return False  # the yard footprint stays off them, same as the house test in _fits (GM, Tango hems)
        r = math.hypot(w, h) / 2
        for poly in self.field_polys:  # keep the whole DRY footprint out of every paddy
            if point_in_poly(x, y, poly) or edge_dist(x, y, poly) < r + 4:
                return False
        # ...AND ASK THE QUESTION THE CHECK ASKS, OF THE SOURCE THE CHECK READS (cohort seed 31,
        # 2026-08-18). The loop above is a CENTRE-and-circle test against `field_polys`, which holds
        # the smoothed ENVELOPE; `harvest_yards_clear_of_paddies` is a CORNER test against each
        # paddy's own recorded `outline`. Two sources and two geometries, so they can disagree - and
        # on seed 31 they did: a yard cleared the envelope by its circle and still put a corner at
        # (2024, 1908) inside a drawn basin. This is the same defect shape as the woodland scan
        # mirroring its check's formula but not its window, fixed earlier the same day; the standing
        # rule is that placement and its check read ONE source.
        _fo = [f["outline"] for f in self.M.get("fields", []) if f.get("kind") == "paddy" and f.get("outline")]
        if _fo:
            _cn = [(x + sx * w / 2, y + sy * h / 2) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
            for _ol in _fo:
                if any(point_in_poly(_px, _py, _ol) for _px, _py in _cn):
                    return False
                if any(-w / 2 <= _vx - x <= w / 2 and -h / 2 <= _vy - y <= h / 2 for _vx, _vy in _ol):
                    return False  # ...and the other direction: a basin vertex inside the yard, which the check also tests
        for px, py, pw, ph, *_ in self.placed:
            if px == hx and py == hy:  # the yard abuts its OWN farmhouse - allowed
                continue
            if math.hypot(x - px, y - py) < r + math.hypot(pw, ph) / 2 + 2:
                return False
        return True

    # THE WORK YARD IS ROLLED FROM A LOGNORMAL, CORRELATED WITH THE HOUSEHOLD (GM 2026-08-28, feature
    # 134 T49; research/homesteads.html "How big was the work yard, and how did the sizes spread").
    #
    # The record, in one line: Kitamoto's households stated their yard in straw mats - 40-60 mats
    # usually, over 100 for a few, two mats to the tsubo - so 20-30 tsubo (66-99 sq m) ordinarily and
    # past 50 tsubo (165 sq m) at the top. No survey tabulates yards, so the SHAPE comes from what the
    # cadastres do tabulate, and every one of those is right-skewed: Kamikanai 1771's 31 commoner main
    # houses fit a lognormal of median 22.5 tsubo, sigma_ln 0.46, its headman detached at 3.1x; Kikoba's
    # lots run 15-100 bu about a mode of 30. Kitamoto's own band-and-tail implies sigma 0.35-0.45 - that
    # convergence is what these numbers rest on. Hence median 25 tsubo, sigma_ln 0.40, floored at 8.
    #
    # CORRELATED, NOT PROPORTIONAL (the GM: "overwhelmingly likely that a large household has a large
    # threshing yard", a mismatch "possible but rare"). Kamikanai measures the coupling as ADDITIVE -
    # five more koku of holding buys about ten more tsubo of built area - so a 20x holder does not get a
    # 20x yard. The household enters as its house footprint's deviation from the map's ordinary minka,
    # damped by YARD_HOUSE_BETA; an independent positional draw supplies the rest of the spread.
    # THE MEDIAN IS THE WET-RICE FIGURE, THE SHAPE IS KITAMOTO'S (GM 2026-08-28, option 2). Kitamoto's
    # 20-30 tsubo is the one directly-stated yard size, but it is a BARLEY district - its yard is sized
    # by the mugi crop the household spreads whole. Wet rice is field-dried on hazakake racks for 10-14
    # days before it reaches the yard, and is threshed in batches over days, so a paddy household needs
    # less standing floor: the crop derivation (1.3 koku/tan -> 247 kg momi -> mats at a 2.5 cm spread,
    # batched) gives 55-100 sq m for a full cho, 35-65 for five tan. Hence 18 tsubo (59.5 sq m) as the
    # median for a rice hamlet, with Kitamoto's 25 tsubo kept as YARD_MEDIAN_TSUBO_DRYFIELD for the
    # barley village this generator does not yet draw. The SHAPE - lognormal, sigma 0.40 - is Kitamoto's
    # and Kamikanai's and applies to both.
    YARD_MEDIAN_TSUBO = 18.0  # wet rice, crop-derived (59.5 sq m); the map's `yard_sizes` knob may name the dry-field figure instead
    YARD_SIGMA_LN = 0.40  # Kamikanai 0.46; Kitamoto's band-and-tail 0.35-0.45
    YARD_MEDIAN_TSUBO_DRYFIELD = 25.0  # Kitamoto's 50 mats - a barley/wheat household spreads the whole crop
    YARD_MIN_TSUBO = 8.0  # nobody is yardless (by Genroku every peasant held a homestead); the landless sit at the small end
    YARD_HOUSE_BETA = 2.2  # how much of the household's own deviation the yard inherits (the drawn house varies only ~+-15% about the ordinary minka, so the household needs this much amplification to dominate the roll - measured on Inashiro: r = 0.17 at 0.55, r = 0.6-0.7 here, which is the GM's "overwhelmingly likely" without making it a rigid ratio)
    YARD_ASPECT = 1.45  # a work apron is near-square, a little wider than deep (the drawn ratio, unchanged)
    TSUBO_FT2 = 35.583  # 1 tsubo = 3.306 sq m

    def _yard_area_ft2(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> float:  # type: ignore[misc]
        """This household's work-yard area in square FEET - the lognormal roll above, correlated with the
        house. Position-seeded like every other homestead attribute, so it never ripples placement."""
        import math as _m

        base = self.px(46.0) * self.px(28.0)  # the ordinary minka footprint in this map's pixels
        house = max(hw * hh, 1.0)
        # the household's own deviation, in log space, damped: a house 1.5x the ordinary lifts the yard
        # 1.5**0.55 = 1.25x before the independent draw - a strong correlation, not a rigid ratio
        tilt = _m.log(house / base) * self.YARD_HOUSE_BETA
        # THE NORMAL DRAW IS A SUM OF SIX POSITIONAL DRAWS, not Box-Muller (measured 2026-08-28): the two
        # salted `_hjit` values a Box-Muller pair needs are not independent enough - one salt pair gave a
        # population mean of -0.93 sigma across Inashiro's fifteen houses, dragging every yard a full sigma
        # small, and a different pair gave +0.28. Six draws summed (Irwin-Hall, standardized) is
        # near-normal by the central limit theorem, stable across salt choices, and has no runaway tail.
        z = (sum(self._hjit(hx, hy, k) for k in (23.0, 29.0, 31.0, 37.0, 43.0, 47.0)) - 3.0) / _m.sqrt(0.5)
        median = self.YARD_MEDIAN_TSUBO_DRYFIELD if self.M["meta"].get("yard_sizes") == "dryfield" else self.YARD_MEDIAN_TSUBO
        tsubo = median * _m.exp(tilt + self.YARD_SIGMA_LN * z)
        if self.M["meta"].get("yard_sizes") == "allotted":
            # THE PLANNED-COLONY FORM, the second attested shape: a shinden colony issued every settler
            # an identical homestead (Santome 1696), so its yards are uniform. Principle XII's knob rule:
            # two attested forms become a per-settlement knob, never a preference.
            tsubo = median
        return max(tsubo, self.YARD_MIN_TSUBO) * self.TSUBO_FT2

    def _yard_dims(self: Settlement, hw: float, hh: float, hx: float = 0.0, hy: float = 0.0) -> tuple[float, float]:  # type: ignore[misc]
        """The yard's drawn width and depth: the rolled area at the apron's near-square aspect.
        PREVIEW AND PLACEMENT MUST AGREE - `rolling/bundle.py` reserves what this returns, so changing
        one without the other makes the placer clear a different rect than the map draws."""
        import math as _m

        area_px = self._yard_area_ft2(hx, hy, hw, hh) / (self.ftpx * self.ftpx)  # sq ft -> sq px
        depth = _m.sqrt(area_px / self.YARD_ASPECT)
        return depth * self.YARD_ASPECT, depth

    def _find_yard_spot(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> tuple[float, float, float, float] | None:  # type: ignore[misc]
        """The first fitting threshing-yard position for a farmhouse: the sunny SOUTH/front side (+y) is
        the maeniwa; fall back to the E/W sides if the paddy blocks due-south, but NEVER the shady north
        back. Returns (ox, oy, yw, yh) or None if the farmstead is boxed in on all three sides."""
        yw, yh = self._yard_dims(hw, hh, hx, hy)
        for dx, dy in ((0, 1), (1, 0), (-1, 0)):
            ox = hx + dx * (hw / 2 + yw / 2 - 2)
            oy = hy + dy * (hh / 2 + yh / 2 - 2)
            if self._yard_fits(ox, oy, yw, yh, hx, hy):
                return ox, oy, yw, yh
        return None

    def _attach_yard(self: Settlement, hx: float, hy: float, spot: Any, rot: float = 0.0) -> None:  # type: ignore[misc]
        """Draw a farmstead's threshing/drying yard (it is drawn BEFORE its house, so the house renders on
        top of the overlap) and record it. The work yard was UNIVERSAL, so every farmhouse gets one. Its
        footprint is a SLIGHTLY-irregular quad (a swept work surface stays near-square: small jitter),
        inscribed in the reserved rect.

        THE YARD TAKES ITS HOUSE'S RAKE (`rot`, GM 2026-09-26: the yards sat square to the map while the
        houses were turned up to 5 degrees, *"I think that they would always be in [line] with the
        farmhouses because that's just how they would be naturally laid out"*). The maeniwa is the ground
        before the house's front, so its edges run with the front wall. The homestead turns as ONE piece:
        `_rake_parts` has already carried the yard's center round the house's center, and the placer
        cleared the ground there, so this turns the yard in place about that center. Turning it about its
        own center alone, as first shipped, slid it up to 3 ft along the front wall."""
        ox, oy, yw, yh = spot
        # THE EDGE THAT FACES THE HOUSE IS LEVEL (GM 2026-09-26): north on every bundled homestead, where the yard
        # is the south front; the legacy fallback may seat it east or west, and the facing edge follows it
        _dx, _dy = ox - hx, oy - hy
        _facing = ("N" if _dy >= 0 else "S") if abs(_dy) >= abs(_dx) else ("W" if _dx > 0 else "E")
        flat = self._quad(ox, oy, yw, yh, 0.10, 41.0, level=_facing)
        poly = turn_about(flat, ox, oy, rot)
        # A NO-RICE HAMLET DRAWS NO THRESHING FLOOR (feature 150, GM 2026-08-28: "thrashing yards on a
        # no-rice hamlet seem bad and should be eliminated"). The ground is still RECORDED, as a
        # `forecourt`: the open ground before a farmhouse is what the lane web threads around, what
        # trees, scrub and wells keep out of, and what a silk-and-fish household works its leaf and
        # nets on - dropping the record (measured) re-packed the web and the belt, which was not the
        # ask. Only the ink goes: no swept floor, no bordered frame. `harvest_yards_present` reads
        # `meta.work_yards` and stands aside; the interactive class `threshing yard` has no ink here.
        _fore = not getattr(self, "_work_yards", True)
        drawn = {} if _fore else self._draw_threshing_yard(ox, oy, yw, yh, flat, rot)  # its mats and rack, for the manifest (feature 282)
        self.M["threshing_yards"].append(
            {
                "x": round(ox, 1),
                "y": round(oy, 1),
                "w": yw,
                "h": yh,
                "rot": round(rot, 2),
                "of": [hx, hy],
                "poly": [[round(px, 1), round(py, 1)] for px, py in poly],
                **({"kind": "forecourt"} if _fore else {}),
                **drawn,
            }
        )
        self.placed.append((ox, oy, yw, yh))
