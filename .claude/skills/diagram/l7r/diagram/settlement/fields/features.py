"""Non-rice features the paddy tiles around (feature 012), and every standing-water glyph.

Split from settlement/fields.py by feature 112 - see settlement/fields/CLAUDE.md for the index.
"""

import math
import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.overlap.registry import refuse_unadmitted

from .._geom import (
    Poly,
    Pt,
    point_in_poly,
    ring_meets_ellipse,
)
from .._knobs import CITY_TIER_SCALES, _centroid

if TYPE_CHECKING:
    from ..core import Settlement


#: The salt of the field grave's FORM substream (feature 267): its own stream, so the roll of the form draws nothing
#: from the flourish stream and a hamlet that keeps the island draws it exactly as before.
_GRAVE_FORM_SALT = 0x6A5E


def grave_form(seed: int) -> str:
    """The field grave's form on this hamlet - the knob research/fields.html 'Are there really graves out in the
    middle of the fields?' records: "island" (inside a plot, the Chinese form) or "corner" (in a plot's corner
    against its bunds, the Japanese form), even odds, since no source weighs one against the other."""
    return "island" if random.Random((seed ^ _GRAVE_FORM_SALT) & 0xFFFFFFFF).random() < 0.5 else "corner"


def turning_corners(poly: Sequence[Pt], min_deg: float = 45.0) -> list[int]:
    """The vertices of `poly` where its outline turns through more than `min_deg` - its real corners. A comb plot
    carries extra vertices ALONG its sides where a neighbor's bund meets it, and a grave seated at one of those stood
    mid-edge beside a ditch, reading as no corner at all (Kashikawa, 2026-09-27). Every vertex if none turns."""
    n = len(poly)
    out = []
    for i in range(n):
        ax, ay = poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]
        bx, by = poly[(i + 1) % n][0] - poly[i][0], poly[(i + 1) % n][1] - poly[i][1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        if la and lb and math.degrees(math.acos(max(-1.0, min(1.0, (ax * bx + ay * by) / (la * lb))))) > min_deg:
            out.append(i)
    return out or list(range(n))


CORNER_MAX = 16.0
"""A corner grave's step in from its vertex, px - see `corner_seat`."""
CORNER_MIN = 12.0
"""The least step: the mound's reach and the stone's rise off a right-angled corner. The step points at the plot's
centroid, not the corner's bisector, so on an oblong plot the mound can stand hard against one bund - which the
research's "against its bunds" allows (settlement-review, Kashikawa 2026-09-27: 0.3 px off the SE bund, nothing crossed)."""


def corner_seat(poly: Sequence[Pt], at: int) -> tuple[float, float]:
    """Where a corner grave stands in `poly`: 16 px in from vertex `at` toward the plot's centroid, never less than
    12 px (and never past half-way on a tiny plot) - in the corner, against its two bunds, and inside the plot, clear of
    whatever runs along the plot's edge. 16 px sets a 6.5 px mound ~5 px off each bund of a right-angled corner (14
    grazed the bund's beads); a fixed third of the way put the grave mid-plot on a large one (Kashikawa, 2026-09-27),
    where it no longer read as a corner grave; and a third on Kashikawa's typical 25 px plot was 8.7 px, which stood
    the tall stone on the bund's corner junction (settlement-review, 2026-09-27). 12 px is the mound's reach plus the
    stone's rise plus a clearance at a right-angled corner."""
    cx, cy = _centroid(poly)
    vx, vy = poly[at % len(poly)]
    dist = math.hypot(cx - vx, cy - vy)
    step = min(CORNER_MAX, max(CORNER_MIN, dist / 3.0), dist / 2.0) / dist if dist else 0.0
    return vx + (cx - vx) * step, vy + (cy - vy) * step


GRAVE_BANK_PX = 1.0
"""How far the basins stand back from a grave mound's reach, px: the mound's own stroke (1.2 px) and a bund's half-stroke
meet there, so the paddy runs UP to the mound rather than under it (water W28)."""

_CUT_SIDES = 64
"""The polygon the mound's disc is cut with. A 64-gon's edges run inside its circle by up to cos(pi / 64) of the radius,
so the cut is taken at the radius over that (plus the manifest's 0.1 px rounding) and no carved bund comes nearer the
mound's center than the rule's radius."""


def carve_around_grave(plots: list[dict[str, Any]], disc: tuple[float, float, float], corner: Pt | None, ctx: Any) -> None:
    """Carve the paddy AROUND a grave in the field (water W28): no plot ring runs under the mound, in place.

    The registry entry says "the flat paddy tiling around it", and until this the lattice was drawn straight through
    (three rings and nine bund junctions under Kashikawa's mound, `future-work` 'Carve the paddy around an in-field grave
    island'). Every ring the rule finds under the mound (`ring_rules.under_island`, the finished-map test's predicate) is
    cut back to the ground outside it:

    - AN ISLAND stands inside its host basin, and a basin with a hole in it is not a ring, so the host is first split in
      two along its own long axis through the mound - the bund a farmer would run to the island - and each half bitten.
    - A CORNER GRAVE stands against its host's bunds, so the bite is carried out to the corner (`corner`): the basin's
      bund goes round the grave, which is the Japanese form the research names ("in a corner of a field").

    Every piece is then judged by every ring rule in `ctx` - the grave among them - and one that fails goes the scrap
    path (`seams.close.hold_ring_rules`): welded into a neighbor, or left bare under the fan floor."""
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import split

    from l7r.diagram.waterfields.ring_rules import under_island
    from l7r.diagram.waterfields.seams.close import hold_ring_rules
    from l7r.diagram.waterfields.seams.pockets import _parts, _ring

    cx, cy, r = disc
    cut = Point(cx, cy).buffer(r / math.cos(math.pi / _CUT_SIDES) + 0.2, quad_segs=_CUT_SIDES // 4)
    if corner is not None:  # carried out PAST the corner, so the bite opens onto the bunds rather than touching them at a point
        d = math.hypot(corner[0] - cx, corner[1] - cy) or 1.0
        cut = cut.union(Point(corner[0] + (corner[0] - cx) / d * r, corner[1] + (corner[1] - cy) / d * r)).convex_hull
    touched: list[int] = []
    added: list[dict[str, Any]] = []
    gone: list[int] = []
    for k, p in enumerate(plots):
        if len(p["poly"]) < 3 or not under_island(p["poly"], disc):
            continue
        ground = Polygon(p["poly"]).buffer(0)
        if corner is None and ground.contains(cut):  # the island's host: halved along its long axis through the mound, so neither half holds it
            box: Any = ground.minimum_rotated_rectangle
            c = list(box.exterior.coords)
            e = max(((c[i], c[i + 1]) for i in range(2)), key=lambda ab: math.dist(*ab))
            reach = 2.0 * math.dist(*e) + 2.0 * r
            ux, uy = (e[1][0] - e[0][0]) / math.dist(*e), (e[1][1] - e[0][1]) / math.dist(*e)
            knife = LineString([(cx - reach * ux, cy - reach * uy), (cx + reach * ux, cy + reach * uy)])
            ground = split(ground, knife)  # through an interior point, so always in two at least
        pieces = [q for part in getattr(ground, "geoms", [ground]) for q in _parts(part.difference(cut)) if len(_ring(q)) >= 3]  # each half alone: a collection differences as its union
        if not pieces:
            gone.append(k)
            continue
        p["poly"] = _ring(pieces[0])
        touched.append(k)
        added += [{**p, "poly": _ring(q)} for q in pieces[1:]]
    for k in reversed(gone):
        del plots[k]
        touched = [j - 1 if j > k else j for j in touched]
    plots += added
    hold_ring_rules(plots, ctx, only=[*touched, *range(len(plots) - len(added), len(plots))])


def _mound_meets_pond(disc: tuple[float, float, float], ponds: Sequence[dict[str, Any]]) -> bool:
    """Whether a grave's mound (its disc) would stand in a field pond: the disc's outline meets the pond's rim, or either
    center lies inside the other - an island is dry ground, never drawn in open water."""
    cx, cy, r = disc
    ring = [(cx + r * math.cos(a * math.pi / 16), cy + r * math.sin(a * math.pi / 16)) for a in range(32)]
    return any(
        ring_meets_ellipse(ring, fp["x"], fp["y"], fp["rx"], fp["ry"]) or math.hypot(fp["x"] - cx, fp["y"] - cy) < r or ((cx - fp["x"]) / fp["rx"]) ** 2 + ((cy - fp["y"]) / fp["ry"]) ** 2 <= 1.0
        for fp in ponds
    )


class FieldFeaturesMixin:
    def pond(self: Settlement, cx: float, cy: float, rx: float, ry: float, stream_curve: Any = None) -> None:  # type: ignore[misc]
        """A pond / irrigation reservoir. Routed through the WATER block (not drawn inline) so a stream or
        channel MEETING it JOINS at the rim instead of the rim cutting across its mouth: the RIM is an EDGE
        below every water bed (a feeder's bed covers it at the junction -> a clean gap), the FILL joins the
        shared bed group as the TOPMOST bed (`pond_fill=True`) - so it paints OVER any feeder's inside-the-rim
        overshoot (an irrigation channel's round end-cap bulging past the rim, whichever order it was drawn),
        while the shore rim still shows and the mouths stay clean; the inner highlight is a sheen.

        ASKED BEFORE ANYTHING IS DRAWN (feature 287, water W53): its placer has walked its alternatives (the sink's pond
        falls back to an off-map run, `hamletgen/sink.py`), so a pond the matrix still forbids is refused by name here."""
        refuse_unadmitted(self.M, "pond", [cx, cy, rx, ry])
        if stream_curve:
            # the pond's feeder runs at the lateral/ditch tier - a thin line near the channel weight,
            # NOT the heftier natural-stream weight (see the water-width ladder in research/water.html).
            self._water(
                f'<path d="{stream_curve}" fill="none" stroke="#9CB4C8" stroke-width="5"/>', {}, cls="irrigation ditch"
            )  # no record behind it: the feed INTO a reservoir is supply (spec 230 FR-001, the third clause)
        self._water(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#9CB4C8"/>',  # FILL -> shared bed group (topmost bed)
            self.M.setdefault("pond_layer", {"late": False}),  # flush records the fill's bedz/sheenz here, and flips
            # `late` if it relocates the fill to the late block. bedz values are offsets within their OWN splice
            # block, so cross-block draw order is carried by the (late, bedz) PAIR - the late block always renders
            # after the whole shared block (pond_fill_covers_channel_mouths compares the pairs lexicographically)
            sheen=f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 12}" ry="{ry - 10}" fill="none" stroke="#B6CAD8" stroke-width="1"/>',  # inner highlight
            edge=f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#5C7488" stroke-width="2.4"/>',  # RIM -> edge layer, below beds
            pond_fill=True,
            cls="pond",
        )
        self._pond_entry: dict[str, Any] | None = self.water[-1]  # so flush can relocate the fill+sheen into the late block (see finish)
        self.M["pond"] = [cx, cy, rx, ry]
        self.ellipses.append((cx, cy, rx, ry))

    # ---- feature 012: deliberate non-rice features the paddy tiles around --------------------------------
    # Placed automatically from the field geometry per the ARCHETYPE MATRIX (specs/012-.../research.md). Only
    # the genuinely NEW in-field glyphs live here - a low-pocket POND, a bedrock ROCK outcrop, and (a disclosed
    # CALIBRATED LIBERTY the GM approved) a rare in-field GRAVE island. The matrix's MARGIN graves + feng-shui
    # knolls are already the village burial ground + back-grove (the research warns a standalone knoll usually
    # IS the back-grove), so they are not redrawn here. Seeded from self.seed so it never ripples other RNG.
    _PADDY_POND_KINDS = ("valley_paddy", "contour_terraces", "polder_grid", "ribbon_valley")
    _PADDY_ROCK_KINDS = ("contour_terraces", "ribbon_valley")  # bedrock ground; alluvial valley/polder + delta dike-pond have none
    _PADDY_GRAVE_KINDS = ("valley_paddy", "contour_terraces", "ribbon_valley")

    def _field_feature_ink(self: Settlement, ink: list[tuple[str, str]] | None, svg: str, cls: str) -> None:  # type: ignore[misc]
        """Emit one in-field feature's ink now, or hold it in `ink` for the caller to emit later: `draw_comb_field` seats
        the features BEFORE the paddies are drawn (a grave carves the rings the paddies are drawn from, water W28) and
        draws their ink after the paddies, where it always was."""
        if ink is None:
            self.add(svg, cls=cls)
        else:
            ink.append((svg, cls))

    def _paddy_features(self: Settlement, net: dict[str, Any], ink: list[tuple[str, str]] | None = None) -> None:  # type: ignore[misc]
        if self.M.get("meta", {}).get("scale") in ("town", *CITY_TIER_SCALES):
            # the in-field flourishes (low-pocket pond, rock outcrop, rare grave island) are VILLAGE-scale
            # features from the feature-012 archetype matrix. On a town/city map the combs are a SLICE of
            # county farmland, and at the 1 ft/px grain the glyphs read literally - the GM read the grave
            # island as a pauper ossuary on the paddy and the pocket pond as a pond overlapping the rice
            # (Hoshizora, 2026-07) - so a town/city comb stays plain.
            return
        arch = self.M.get("meta", {}).get("field_archetype") or "valley_paddy"
        if arch == "mulberry_dike_fishpond":
            return  # open water IS its fabric - no obstacle tiles among it (research D4)
        rng = random.Random((self.seed ^ 0x9AD1) & 0xFFFFFFFF)
        plots = net["plots"]
        low = [p for p in plots if p.get("low")]
        # POND: a low pocket held as open water - and it is the ONE in-field feature the feature-012
        # research puts in the flat wet MIDDLE rather than at the margin. Its organizing finding:
        # "these features live at the paddy-to-slope MARGIN ... not free-floating in the flat wet
        # center. The one thing that genuinely belongs in the flat wet middle is an open-water POND
        # (a low pocket too deep for rice)." That is why a rock outcrop or grave island mid-paddy is
        # a defect on flat valley ground while this is not (research D4 + the matrix).
        #
        # THE ~55% IS NOT RESEARCHED, and saying so is the point (GM 2026-08-16, asking whether the
        # pond belongs at all): D4's only hard quantitative anchor is tameike density in Japan, and
        # its own honesty flags call every per-map count interpolated. So the prevalence is a
        # disclosed calibrated liberty (constitution XII) - chosen so a pocket pond reads as an
        # occasional feature of a valley floor rather than a fixture of every field. The SITING is
        # the researched half and it is enforced: `field_ponds_on_low_ground` demands the host plot
        # be one the field pass independently recorded as low/wet.
        #
        # Tried across the low plots in random order until one takes a legible pond, because a plot
        # can REFUSE (a comb fan toe is all thin wedges; Inashiro 2026-08-16). A field whose low
        # pockets are all wedges honestly carries none.
        # NOTE a disclosed coupling (settlement-review, Mizuguchi 2026-08-16): rng.sample consumes
        # a different number of draws than the old rng.choice, so the rock/grave rolls below sit
        # on a shifted stream and re-rolled once. Accepted - the blast radius is this one field's
        # own flourishes, nothing map-level. If it ever bites again, the refinement is one
        # sub-stream per sub-feature: random.Random(seed ^ 0x9AD1 ^ <per-feature salt>) for pond,
        # rock and grave each, at the cost of one more pool-wide flourish re-roll.
        if arch in self._PADDY_POND_KINDS and low:
            # the ring list the gate's check will scan: plot_rings is recorded from net["plots"]
            # and drain_hem is a SUBSET of those same polys, so this list is exactly the check's
            # coverage. Rings can OVERLAP each other at the fan/grid seams, so fitting against the
            # host plot alone is not enough (cohort seeds 5/19/21, 2026-08-16).
            rings: list[Poly] = [p["poly"] for p in net["plots"]]
            # A ROLLED POND IS ALWAYS DRAWN (feature 287, plan D9, water W29): the knob is rolled only over a field where
            # some low plot can hold a legible pond, so its value space is narrowed to what the site affords rather than a
            # rolled pond silently not drawn. Where none can, the roll and the order are still DRAWN and discarded, so
            # the rock and grave rolls after it sit on the stream they always did.
            takes = any(self._pond_fit(p, rings) is not None for p in low)
            rolled = rng.random() < 0.55
            order = rng.sample(low, len(low)) if rolled else []
            for cand in order if takes else []:
                if self._plot_pond(cand, rings, ink):
                    break
        # ROCK: bedrock outcrops the risers/bunds wrap around (research D3) - terraces always, ribbon ~half.
        if arch == "contour_terraces" or (arch == "ribbon_valley" and rng.random() < 0.5):
            for _ in range(rng.randint(1, 3)):
                self._plot_rock(rng.choice(plots), rng, ink)
        # A GRAVE IN THE FIELD (research/fields.html 'Are there really graves out in the middle of the fields?', feature
        # 267): graves inside working fields are attested in China ("graves were in every field"), and every Japanese
        # placement read is BESIDE the plot - at the bund edge or in a field's corner. Two placements of one thing, so
        # the FORM is a knob rolled per hamlet: an island inside a plot, or a grave in a plot's corner against its
        # bunds. The 0.3 is how often a map draws one at all - a degree chosen for the maps (calibrated liberty), since
        # no source gives a rate and the record argues they were common where the custom held, not rare. The form
        # comes from its OWN substream, so a map keeping the island draws it exactly as before.
        # THE GRAVE IS SEATED ON DRY GROUND AND THE PADDY CARVED AROUND IT (feature 287, water W28): the chosen plot is the
        # first candidate, and one whose mound would stand in a field pond is passed for the next in order - the placer's
        # own candidate loop. Seating it carves the rings (`carve_around_grave`).
        if arch in self._PADDY_GRAVE_KINDS and rng.random() < 0.3:
            start = plots.index(rng.choice(plots))
            seat = self._plot_grave_island if grave_form(self.seed) == "island" else self._plot_corner_grave
            for k in range(len(plots)):
                if seat(plots[(start + k) % len(plots)], rng, net, ink):
                    break

    @staticmethod
    def _plot_center_span(poly: Sequence[Pt]) -> tuple[float, float, float, float]:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        return (sum(xs) / len(xs), sum(ys) / len(ys), (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2)

    def _plot_pond(self: Settlement, plot: dict[str, Any], rings: list[Poly], ink: list[tuple[str, str]] | None = None) -> bool:  # type: ignore[misc]
        """A small OPEN-WATER pond sunk into one low plot - a low pocket / header tameike the paddy rings.
        Distinct from the reed/lotus BOG (blue-green, choked) and from the main village reservoir at the
        source. Drawn OVER the plot (so it carries no bund grid) with a reed fringe; recorded in
        M['field_ponds']. Returns False - drawing and recording nothing - when no legible pond fits (`_pond_fit`)."""
        fit = self._pond_fit(plot, rings)
        if fit is None:
            return False
        cx, cy, rx, ry = fit
        self._field_feature_ink(
            ink, f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#9CB4C8" stroke="#5C7488" stroke-width="1.8"/>', "field pond"
        )  # feature 134: its own class, beside `pond`
        self._field_feature_ink(ink, f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx - 5:.1f}" ry="{ry - 4:.1f}" fill="none" stroke="#B6CAD8" stroke-width="0.9"/>', "field pond")
        reeds = "".join(
            f'<line x1="{cx + rx * math.cos(a):.1f}" y1="{cy + ry * math.sin(a):.1f}" x2="{cx + rx * math.cos(a):.1f}" y2="{cy + ry * math.sin(a) - 5:.1f}" stroke="#7C9A4E" stroke-width="1.1"/>'
            for a in [i * math.pi / 4 for i in range(8)]
        )
        self._field_feature_ink(ink, f'<g opacity="0.8">{reeds}</g>', "field pond")
        self.M.setdefault("field_ponds", []).append({"x": round(cx, 1), "y": round(cy, 1), "rx": round(rx, 1), "ry": round(ry, 1)})
        return True

    def _pond_fit(self: Settlement, plot: dict[str, Any], rings: list[Poly]) -> tuple[float, float, float, float] | None:  # type: ignore[misc]
        """Where `_plot_pond` would sink a legible pond into `plot` - `(cx, cy, rx, ry)`, as recorded - or None where the
        plot takes none. Asked alone by the pond's roll (plan D9), so a field rolls a pond only where one fits."""
        poly = [(float(x), float(y)) for x, y in plot["poly"]]
        _, _, hx, hy = self._plot_center_span(poly)
        cx, cy = _centroid(poly)
        # capped so a wide TERRACE band gives a POND, not a field-spanning lake (a low pocket, not a reservoir)
        rx, ry = min(max(10.0, hx * 0.82), 46.0), min(max(7.0, hy * 0.82), 32.0)
        # FIT TO THE PLOT POLYGON, NOT ITS BBOX (Inashiro 2026-08-16). A comb fan's toe plots are
        # WEDGES whose bounding box is several times the wedge itself, so a bbox-sized ellipse
        # spilled across three neighboring plots and the drain hem, spoke bunds drawn straight
        # through open water. Center on the CENTROID (a wedge's bbox center can sit outside it) and
        # shrink until every rim point sits inside the plot and NO ring in `rings` meets the pond -
        # `ring_meets_ellipse`, the ONE predicate the finished-map test (`crosses_pond_rim`) calls too
        # (feature 287, FR-003: this used to ask a core 3 px inside the rim while the test read the full
        # ellipse, so the two disagreed; the full rim is the rule - see the predicate). `rings` is every
        # ring that test will scan (rings can OVERLAP at the fan/grid seams, so testing the host plot
        # alone is not enough - cohort seeds 5/19/21). JUDGED AS RECORDED: the rings and the pond are
        # rounded to the manifest's 0.1 px before they are asked, and the pond is drawn and recorded at
        # the values that were judged, so the test reads exactly what the placer cleared. Below the
        # legible floor (10 x 7 px) the plot takes no pond and the caller tries another low plot.
        rim = [(math.cos(a), math.sin(a)) for a in [i * math.pi / 12 for i in range(24)]]
        recorded = [[(round(float(q[0]), 1), round(float(q[1]), 1)) for q in r] for r in rings]
        boxed = [(min(q[0] for q in r), min(q[1] for q in r), max(q[0] for q in r), max(q[1] for q in r), r) for r in recorded]
        cx, cy = round(cx, 1), round(cy, 1)
        while rx >= 10.0 and ry >= 7.0:
            rx, ry = round(rx, 1), round(ry, 1)
            ok = all(point_in_poly(cx + rx * ux, cy + ry * uy, poly) for ux, uy in rim)
            if ok:
                for bx0, by0, bx1, by1, ring in boxed:
                    if bx1 < cx - rx or bx0 > cx + rx or by1 < cy - ry or by0 > cy + ry:
                        continue  # bbox prefilter only - the exact test below decides
                    if ring_meets_ellipse(ring, cx, cy, rx, ry):
                        ok = False
                        break
            if ok:
                return cx, cy, rx, ry
            rx, ry = rx * 0.9, ry * 0.9
        return None

    def _plot_rock(self: Settlement, plot: dict[str, Any], rng: random.Random, ink: list[tuple[str, str]] | None = None) -> None:  # type: ignore[misc]
        """A bedrock OUTCROP the terrace risers wrap around - a cluster of gray boulders. Recorded in
        M['field_rocks']. Small (a few plot-fractions), off-center so it reads as a natural obstacle."""
        cx, cy, hx, hy = self._plot_center_span(plot["poly"])
        cx += rng.uniform(-hx * 0.3, hx * 0.3)
        cy += rng.uniform(-hy * 0.3, hy * 0.3)
        boulders = ""
        for _ in range(rng.randint(2, 4)):
            bx, by = cx + rng.uniform(-7, 7), cy + rng.uniform(-5, 5)
            r = rng.uniform(3.5, 6.5)
            boulders += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="#9C948A" stroke="#5C544A" stroke-width="1"/>'
            boulders += f'<path d="M{bx - r * 0.5:.1f},{by - r * 0.2:.1f} q{r * 0.4:.1f},{-r * 0.5:.1f} {r:.1f},{-r * 0.1:.1f}" fill="none" stroke="#C6BEB2" stroke-width="0.8"/>'  # a lit crown
        self._field_feature_ink(ink, f'<g>{boulders}</g>', "field rock")  # feature 134
        self.M.setdefault("field_rocks", []).append({"x": round(cx, 1), "y": round(cy, 1)})

    def _grave_context(self: Settlement, net: dict[str, Any], disc: tuple[float, float, float]) -> Any:  # type: ignore[misc]
        """The ring rules' context for carving round a grave: the fan's channels as recorded (its supply strokes only
        where the carve hemmed onto them, `supply_banks`), the grain the gate reads (`2 / ftpx`), the design cell, the
        field ponds already sunk, and the grave itself."""
        from l7r.diagram.waterfields.ring_rules import fan_context

        chans = [c for c in net.get("channels") or [] if net.get("supply_banks") or c.get("role") == "drain"]
        ponds = [(fp["x"], fp["y"], fp["rx"], fp["ry"]) for fp in self.M.get("field_ponds") or []]
        return fan_context(chans, 2.0 / float(self.ftpx), net.get("cell"), ponds=ponds, graves=[disc])

    def _plot_corner_grave(self: Settlement, plot: dict[str, Any], rng: random.Random, net: dict[str, Any] | None = None, ink: list[tuple[str, str]] | None = None) -> bool:  # type: ignore[misc]
        """The Japanese form of the field grave: a small mound with one or two stones in a plot's CORNER, against its
        bunds (research/fields.html 'Are there really graves out in the middle of the fields?': "in a corner of a
        field", and beside the bunds). Set 12-16 px in from the corner toward the plot's middle (`corner_seat`) so it
        stays inside the plot, clear of the ditch or lane that may run along its edge. Recorded in M['field_graves'] with
        its form. The grave is the last draw on `rng` in the pass, so its one extra draw shifts nothing after it.

        Given the comb's `net`, the basin is carved round it - its bund carried round the grave to the corner (water W28,
        `carve_around_grave`) - and a corner whose mound would stand in a field pond is refused (False, nothing drawn)."""
        at = rng.choice(turning_corners(plot["poly"]))
        cx, cy = (round(v, 1) for v in corner_seat(plot["poly"], at))
        disc = (cx, cy, 6.5 + GRAVE_BANK_PX)
        if _mound_meets_pond(disc, self.M.get("field_ponds") or []):
            return False
        if net is not None:
            carve_around_grave(net["plots"], disc, tuple(plot["poly"][at % len(plot["poly"])]), self._grave_context(net, disc))
            net.setdefault("grave_discs", []).append(disc)
        self._field_feature_ink(ink, f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="6.5" ry="4.5" fill="#CFC6B4" stroke="#8C8470" stroke-width="1.1"/>', "grave island")
        markers = ""
        # the second stone stands IN FRONT of the first, lower and to one side - two stones abreast read as a pair of
        # eyes (the island's rule, feature 230 pass 11)
        for i in range(rng.randint(1, 2)):
            sx, base, h = ((-2.2, -1.0, 6.5), (1.6, 2.2, 3.5))[i]
            markers += f'<rect x="{cx + sx:.1f}" y="{cy + base - h:.1f}" width="2.4" height="{h:.1f}" rx="1" fill="#9AA1A4" stroke="#5A584F" stroke-width="0.5"/>'
        self._field_feature_ink(ink, f'<g>{markers}</g>', "grave island")
        self.M.setdefault("field_graves", []).append({"x": cx, "y": cy, "form": "corner"})
        return True

    def _plot_grave_island(self: Settlement, plot: dict[str, Any], rng: random.Random, net: dict[str, Any] | None = None, ink: list[tuple[str, str]] | None = None) -> bool:  # type: ignore[misc]
        """An in-field grave island, the Chinese form of the field grave - a small raised earthen mound with a couple
        of stone markers. Recorded in M['field_graves'].

        CARVED OUT OF THE LATTICE, NOT DRAWN OVER IT (feature 287, water W28). The registry entry says "the flat paddy
        tiling around it", and the plots used to be drawn through it - three plot rings and nine bund junctions inside
        Kashikawa's mound, recorded then as a map drawing convention with the carve as its honest fix. Given the comb's
        `net`, `carve_around_grave` now cuts every ring back off the mound (the host halved through it), so the basins
        run up to the island and the manifest says what the ink shows. The mound stays OPAQUE, as the Kashikawa review
        asked. A plot whose mound would stand in a field pond is refused (False, nothing drawn)."""
        cx, cy, hx, hy = self._plot_center_span(plot["poly"])
        cx, cy = round(cx, 1), round(cy, 1)
        rx, ry = max(9.0, hx * 0.55), max(6.0, hy * 0.55)
        disc = (cx, cy, max(rx, ry) + GRAVE_BANK_PX)
        if _mound_meets_pond(disc, self.M.get("field_ponds") or []):
            return False
        if net is not None:
            carve_around_grave(net["plots"], disc, None, self._grave_context(net, disc))
            net.setdefault("grave_discs", []).append(disc)
        self._field_feature_ink(ink, f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#CFC6B4" stroke="#8C8470" stroke-width="1.2"/>', "grave island")  # feature 134
        markers = ""
        # THE STONES ARE STAGGERED AND UNEQUAL, NEVER A MATCHED PAIR (settlement-review, feature 230 pass 11). Two equal stones
        # side by side in the upper half of an egg-shaped mound read, at every zoom, as a pair of eyes - a face on Mizuguchi's
        # field. A family's grave markers are set one behind another as they were added, and differ in size, so each stone
        # steps back and to one side of the last and none repeats the height of the first.
        for i in range(rng.randint(2, 3)):
            mx = cx - 4.0 + i * 4.5
            h = (8.0, 5.0, 6.5)[i]
            markers += f'<rect x="{mx - 1.3:.1f}" y="{cy - 3.0 - i * 3.5 - h:.1f}" width="2.6" height="{h:.1f}" rx="1" fill="#9AA1A4" stroke="#5A584F" stroke-width="0.5"/>'
        self._field_feature_ink(ink, f'<g>{markers}</g>', "grave island")
        self.M.setdefault("field_graves", []).append({"x": cx, "y": cy})
        return True

    @staticmethod
    def _rounded_pond(poly: Sequence[Pt], inset: float, reach: float, rng: random.Random) -> tuple[str, Poly]:
        """A dug fish-pond within its mulberry-dike parcel: homothetically INSET the parcel (so a green bank
        shows all round - the pond never reaches the parcel edge) and ROUND every corner with a quadratic
        fillet of slightly irregular reach (erosion). Returns (svg path `d`, sampled water polygon) - the
        sample carries the rounding into the manifest so the checks can see the pond is inset + rounded."""
        n = len(poly)
        cx = sum(q[0] for q in poly) / n
        cy = sum(q[1] for q in poly) / n
        mids = [((poly[i][0] + poly[(i + 1) % n][0]) / 2, (poly[i][1] + poly[(i + 1) % n][1]) / 2) for i in range(n)]
        apo = sum(math.hypot(mx - cx, my - cy) for mx, my in mids) / n  # centroid->edge-midpoint (the apothem)
        scale = max(0.4, 1.0 - inset / max(1.0, apo))
        ins = [(cx + (q[0] - cx) * scale, cy + (q[1] - cy) * scale) for q in poly]

        def toward(frm: Pt, to: Pt, dist: float) -> Pt:
            vx, vy = to[0] - frm[0], to[1] - frm[1]
            ln = math.hypot(vx, vy) or 1.0
            dd = min(dist, ln * 0.45)
            return (frm[0] + vx / ln * dd, frm[1] + vy / ln * dd)

        a_in: Poly = []
        b_out: Poly = []
        for i in range(n):
            r = reach * rng.uniform(0.8, 1.15)
            a_in.append(toward(ins[i], ins[(i - 1) % n], r))
            b_out.append(toward(ins[i], ins[(i + 1) % n], r))
        d = f"M {b_out[0][0]:.1f} {b_out[0][1]:.1f} "
        sample: Poly = [b_out[0]]
        for i in range(1, n + 1):
            j = i % n
            d += f"L {a_in[j][0]:.1f} {a_in[j][1]:.1f} Q {ins[j][0]:.1f} {ins[j][1]:.1f} {b_out[j][0]:.1f} {b_out[j][1]:.1f} "
            mid = (0.25 * a_in[j][0] + 0.5 * ins[j][0] + 0.25 * b_out[j][0], 0.25 * a_in[j][1] + 0.5 * ins[j][1] + 0.25 * b_out[j][1])
            sample += [a_in[j], mid, b_out[j]]
        return d + "Z", sample

    def crescent_pond(self: Settlement, cx: float, cy: float, r: float, facing_deg: float = 270.0) -> None:  # type: ignore[misc]
        """A fengshui CRESCENT / half-moon pond (半月塘), a focal feature of Huizhou / Hakka single-lineage
        villages (feature 005): a half-disk of water IN FRONT of the cluster, its flat diameter facing the
        houses and the arc bulging away, DISTINCT from the irrigation pond.

        WHAT IT IS (GM asked, 2026-07-21 - labeled "geomantic pond" at his direction): GEOMANTIC, not
        religious - no deity, no rites; cosmological engineering, the same category as orienting a house
        south. The village wants "mountain behind, water in front" (背山面水): the back half is the hill +
        fengshui grove (the windbreak belt these maps already draw), and where no river obliges, the village
        DIGS the front half. Still water gathers and holds qi/wealth where flowing water carries it away;
        the HALF shape leaves the lineage room to grow (a full circle is complete, and what is complete can
        only wane). Grove-arc behind + water-arc in front cradle the village as ONE system. It also earns
        its keep practically - drawn UNCONNECTED to the irrigation network, a recorded DEVIATION (the one page
        read feeds it by a channel of field water: homesteads.html#why-is-there-a-crescent-pond-in-front-of-some-villages-and-why-is-it-labeled),
        fire water beside thatch, fish/ducks/washing, and the flat-side bank doubles
        as the open threshing/ceremony forecourt. The shrine is where religion happens; this is just how a
        well-sited village should be shaped.

        `facing_deg` is the screen direction the FLAT edge faces (toward the village); default 270 = up / N.
        Draws through the shared water block (so it composites cleanly), records the footprint + the
        `crescent_pond` focal feature on the manifest, and reserves a placement keep-out - so call it BEFORE
        `farmsteads()` and the cluster packs around it."""
        fa = math.radians(facing_deg)
        fx, fy = math.cos(fa), math.sin(fa)  # unit vector toward the village (the flat side)
        perp = (-fy, fx)  # along the flat diameter
        n = 26
        pts = []
        for i in range(n + 1):
            t = math.pi * i / n  # sweep the arc across the diameter, bulging AWAY from the village
            px = cx + r * (math.cos(t) * perp[0] - math.sin(t) * fx)
            py = cy + r * (math.cos(t) * perp[1] - math.sin(t) * fy)
            pts.append((round(px, 1), round(py, 1)))
        poly = " ".join(f"{x},{y}" for x, y in pts)
        self._water(
            f'<polygon points="{poly}" fill="#9CB4C8"/>',
            {},
            sheen=f'<polygon points="{poly}" fill="none" stroke="#B6CAD8" stroke-width="1" opacity="0.6"/>',
            edge=f'<polygon points="{poly}" fill="none" stroke="#5C7488" stroke-width="2.4"/>',
            pond_fill=True,
        )
        self.M.setdefault("crescent_ponds", []).append({"cx": cx, "cy": cy, "r": r, "facing": facing_deg, "poly": [[x, y] for x, y in pts]})
        self.note_focal("crescent_pond")
        # keep-out over the bulge half-disk (its centroid sits ~0.42r off center, away from the village)
        self.ellipses.append((cx - fx * r * 0.45, cy - fy * r * 0.45, r * 0.95, r * 0.95))
        # LABELED (GM 2026-07-21): the pond is a culturally specific feature that does not read by
        # itself (the GM asked "what is that?" of an unlabeled one - the don't-label-the-obvious rule cuts the
        # OTHER way here). Placed off the arc side, away from the village (crescent_pond_labeled gates it).
        self.label(cx - fx * (r + 16), cy - fy * (r + 16) + 4, "geomantic pond", 11, italic=True, color="#4C6478", ref=(cx - r, cy - r, cx + r, cy + r))
