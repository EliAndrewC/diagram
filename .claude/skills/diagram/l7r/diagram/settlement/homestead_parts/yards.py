"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly

if TYPE_CHECKING:
    from ..core import Settlement


class ThreshingYardsMixin:
    def _draw_threshing_yard(self: Settlement, cx: float, cy: float, w: float, h: float, poly: Any) -> None:  # type: ignore[misc]
        """Draw one small tamped earthen threshing/drying yard (a straw mat + a little hazakake rack). The
        outer footprint is a slightly-irregular quad (`poly`, absolute corner coords) - a swept work surface
        stays NEAR-square; interior detail is laid out in the local (w,h) frame."""
        x0, y0 = -w / 2, -h / 2
        g = [f'<g transform="translate({cx:.0f},{cy:.0f})">']
        pts = " ".join(f"{px - cx:.1f},{py - cy:.1f}" for px, py in poly)
        g.append(f'<polygon points="{pts}" fill="#D2BE94" stroke="#A98E54" stroke-width="1.5"/>')  # tamped earthen floor
        g.append(f'<rect x="{x0 + 3:.0f}" y="{y0 + 3:.0f}" width="{w - 6:.0f}" height="{h - 6:.0f}" rx="1.5" fill="none" stroke="#BBA06E" stroke-width="0.7" opacity="0.6"/>')  # swept rim
        g.append('<rect x="-7" y="-6" width="14" height="9" rx="1" fill="#E2D2A2" stroke="#A98E54" stroke-width="0.6" opacity="0.9"/>')  # a straw drying mat
        ry = h / 2 - 3  # a little drying rack (hazakake) along the floor's lower edge
        g.append(f'<line x1="{x0 + 4:.1f}" y1="{ry:.1f}" x2="{-x0 - 4:.1f}" y2="{ry:.1f}" stroke="#7A5A30" stroke-width="1.2"/>')
        g.append(f'<line x1="{x0 + 4:.1f}" y1="{ry - 3:.1f}" x2="{-x0 - 4:.1f}" y2="{ry - 3:.1f}" stroke="#7A5A30" stroke-width="1.0"/>')
        for px in (x0 + 4, 0.0, -x0 - 4):  # posts + a few hung sheaves
            g.append(f'<line x1="{px:.1f}" y1="{ry - 5:.1f}" x2="{px:.1f}" y2="{ry + 3:.1f}" stroke="#5A3F1E" stroke-width="1.2"/>')
        g.append('</g>')
        self.add(''.join(g), cls="threshing yard")

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
    # 134 T49; research/homesteads.md "How big was the work yard, and how did the sizes spread").
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

    def _attach_yard(self: Settlement, hx: float, hy: float, spot: Any) -> None:  # type: ignore[misc]
        """Draw a farmstead's threshing/drying yard (it is drawn BEFORE its house, so the house renders on
        top of the overlap) and record it. The work yard was UNIVERSAL, so every farmhouse gets one. Its
        footprint is a SLIGHTLY-irregular quad (a swept work surface stays near-square: small jitter),
        inscribed in the reserved rect so it can never breach the collision the rect already cleared."""
        ox, oy, yw, yh = spot
        poly = self._quad(ox, oy, yw, yh, 0.10, 41.0)
        # A NO-RICE HAMLET DRAWS NO THRESHING FLOOR (feature 150, GM 2026-08-28: "thrashing yards on a
        # no-rice hamlet seem bad and should be eliminated"). The ground is still RECORDED, as a
        # `forecourt`: the open ground before a farmhouse is what the lane web threads around, what
        # trees, scrub and wells keep out of, and what a silk-and-fish household works its leaf and
        # nets on - dropping the record (measured) re-packed the web and the belt, which was not the
        # ask. Only the ink goes: no swept floor, no bordered frame. `harvest_yards_present` reads
        # `meta.work_yards` and stands aside; the interactive class `threshing yard` has no ink here.
        _fore = not getattr(self, "_work_yards", True)
        if not _fore:
            self._draw_threshing_yard(ox, oy, yw, yh, poly)
        self.M["threshing_yards"].append(
            {"x": round(ox, 1), "y": round(oy, 1), "w": yw, "h": yh, "rot": 0, "of": [hx, hy], "poly": [[round(px, 1), round(py, 1)] for px, py in poly], **({"kind": "forecourt"} if _fore else {})}
        )
        self.placed.append((ox, oy, yw, yh))
