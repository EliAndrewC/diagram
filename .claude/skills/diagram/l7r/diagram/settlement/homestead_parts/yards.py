"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly, turn_about

if TYPE_CHECKING:
    from ..core import Settlement

# THE STRAW MAT, 3 x 6 ft (feature 282): the mushiro was woven about 3 shaku by 6 (90 x 180 cm; tobunken-mushiro), and a
# yard at harvest was a floor of them - "mats were spread to fill the yard" (Kitamoto). Laid long side across the yard's
# width, in rows (a GUESS: no page read says how they lay), inset 1 ft from the edge.
MAT_FT = (6.0, 3.0)
MAT_INSET_FT = 1.0
MAT_SQ_FT = MAT_FT[0] * MAT_FT[1]
# THE GAP LEFT BETWEEN DRAWN MATS, widest first (feature 282, a CONVENTION): a real yard's mats lay edge to edge, and drawn
# so they read as a tiled floor (seen on Sawada, 2026-09-28, with a checkered half: mats meeting at their corners made
# pavers, not mats). A 2 ft gap on every side leaves each mat on its own and draws 18 / (8 x 5) = 45% of a full cover; a
# yard too small or too clipped (by its pulled-in corners and the rack) to reach a third of one at that gap closes it a
# step at a time, down to edge to edge on the smallest yards, and is thinned back evenly if that overshoots two thirds.
MAT_GAPS_FT = (2.0, 1.5, 1.0, 0.5, 0.0)
# THE RACK BY THE HOUSE (feature 282): a line of posts and poles hung with sheaves, drawn 2.5 ft wide so it reads - a
# map drawing CONVENTION (the real poles are inches thick) - and inset 2 ft from the yard's side and front edges.
RACK_WIDTH_FT = 2.5
RACK_INSET_FT = 2.0
RACK_MIN_FT = 4.0  # shorter than this and it is not drawn: a side clipped by the map-south rule to a stub reads as litter
RACK_CLEAR_FT = 0.25  # the rack stops this far north of the yard's midline (the manifest rounds to 0.1 px)
RACK_POST_FT = 6.0  # a post every ~6 ft (a GUESS within the attested racks: posts at even spacing, kotobank-hasa-nipponica)


def mat_cells(w: float, h: float, poly: list[tuple[float, float]], ftpx: float, keep_out: tuple[float, float, float, float] | None = None) -> list[tuple[float, float, float, float]]:
    """The mats one yard draws, as (x, y, w, h) rects in the yard's LOCAL, unturned frame (its center at 0,0).

    The real yard was covered edge to edge (40-60 mats), which at map scale reads as a textured floor rather than as mats,
    so the drawing lays them in rows across the whole yard with a gap around each, about half of a full cover - the GM's
    drawing convention (2026-09-28: "at this scale, we can't render dozens of mats and have that be legible. So our
    threshing yard glyphs show a smaller number to give the impression that there are many of them"). The rows are
    centered inside a 1 ft inset; a mat is kept only if its four corners lie inside the yard's quad `poly` (local coords)
    and it misses `keep_out` (the rack's footprint, x0, y0, x1, y1). The count is held to at least a third of the yard's
    full cover (area / 18 sq ft; spec 282 FR-004) by closing the gap (`MAT_GAPS_FT`); at the widest gap that still
    reaches it; where the last, edge-to-edge step overshoots two thirds, it is thinned back evenly."""
    mw, mh, inset = MAT_FT[0] / ftpx, MAT_FT[1] / ftpx, MAT_INSET_FT / ftpx
    floor = math.ceil((w * ftpx) * (h * ftpx) / MAT_SQ_FT / 3.0)
    mats: list[tuple[float, float, float, float]] = []
    for gap_ft in MAT_GAPS_FT:
        g = gap_ft / ftpx
        cols, rows = int((w - 2 * inset + g) // (mw + g)), int((h - 2 * inset + g) // (mh + g))
        gx0, gy0 = -(cols * (mw + g) - g) / 2.0, -(rows * (mh + g) - g) / 2.0
        mats = []
        for r in range(rows):
            for c in range(cols):
                x, y = gx0 + c * (mw + g), gy0 + r * (mh + g)
                if not all(point_in_poly(px, py, poly) for px, py in ((x, y), (x + mw, y), (x + mw, y + mh), (x, y + mh))):
                    continue
                if keep_out is not None and x < keep_out[2] and x + mw > keep_out[0] and y < keep_out[3] and y + mh > keep_out[1]:
                    continue
                mats.append((x, y, mw, mh))
        if len(mats) >= floor:
            break
    cap = max(1, math.floor((w * ftpx) * (h * ftpx) / MAT_SQ_FT * 2.0 / 3.0))
    if len(mats) > cap:  # only edge to edge can overshoot: drop evenly across the yard, never from one end
        step = len(mats) / cap
        mats = [mats[int((i + 0.5) * step)] for i in range(cap)]  # centered picks: the drops fall mid-yard, not at its end
    return mats


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
        x = sd * (w / 2.0 - inset - hw)
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
        keep = (rack[0] - rack[3] - 0.5, rack[1] - 0.5, rack[0] + rack[3] + 0.5, rack[2] + 0.5) if rack else None
        mats = mat_cells(w, h, local, self.ftpx, keep)
        for mx, my, mw, mh in mats:  # straw mats (mushiro), about half of those that covered the floor, each on its own - a CONVENTION
            g.append(f'<rect x="{mx:.2f}" y="{my:.2f}" width="{mw:.2f}" height="{mh:.2f}" fill="#EBDDAE" stroke="#9A7C45" stroke-width="0.5"/>')
        out: dict[str, Any] = {"mats": len(mats)}
        if rack:
            x, y0, y1, hw = rack
            g.append(f'<rect x="{x - hw:.2f}" y="{y0:.2f}" width="{2 * hw:.2f}" height="{y1 - y0:.2f}" fill="#C9AE62" stroke="#7A5A30" stroke-width="0.6"/>')  # hung sheaves
            g.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="#7A5A30" stroke-width="0.8"/>')  # the pole
            n = max(1, round((y1 - y0) * self.ftpx / RACK_POST_FT))
            for i in range(n + 1):  # the posts
                py = y0 + (y1 - y0) * i / n
                g.append(f'<line x1="{x - hw - 0.6:.2f}" y1="{py:.2f}" x2="{x + hw + 0.6:.2f}" y2="{py:.2f}" stroke="#5A3F1E" stroke-width="1.0"/>')
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
