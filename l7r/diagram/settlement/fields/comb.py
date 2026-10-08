"""The comb-field builder, its base fill, its bund junctions, and its furrows.

Split from settlement/fields.py by feature 112 - see settlement/fields/CLAUDE.md for the index.

Research: plumbing - NONE: geometry, indexing, tolerances and manifest records
"""

import hashlib
import math
import random
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from l7r.diagram.interactive.tags import Split
from l7r.diagram.overlap.registry import refuse_unadmitted

from .._geom import (
    Poly,
    Pt,
    point_in_poly,
    point_quad_dist,
    quad_hits_seg,
    seg_closest,
    seg_dist,
    seg_reach_index,
    within_reach,
)
from .._knobs import _centroid, _sharp_corners, _toward, resolve_knob
from ..land.wet import pond_fringe_ring
from ..water_ways.water import ditch_style
from .grain import SQ_FT_PER_ACRE, dry_need_acres, poly_area, top_up
from .landuse import line_cuts

if TYPE_CHECKING:
    from ..core import Settlement


class WetLines:
    """The `(polyline, half-width)` pairs `hem_on_water` asks, each segment filed once by its box widened by its half-width
    (`seg_reach_index`), so a plot asks only the segments whose widened box meets its own box (feature 287 perf: the
    coarse-grain top-up asks the whole wild middle, 558 plots on the reference seed 4, and each walked every ditch segment
    on the map - 35,000 `quad_hits_seg`). EXACT: a stroke that meets a plot has a point within its half-width of the
    plot, so its widened box meets the plot's box; a segment it skips could not have hit, and `any` does not care about
    order."""

    __slots__ = ("grid",)

    def __init__(self, wet: Sequence[tuple[Any, float]]) -> None:
        self.grid = seg_reach_index([([(float(q[0]), float(q[1])) for q in pl], float(hw)) for pl, hw in wet], 0.0)

    def hit(self, poly: Poly) -> bool:
        x0, y0 = min(q[0] for q in poly), min(q[1] for q in poly)
        x1, y1 = max(q[0] for q in poly), max(q[1] for q in poly)
        for a, b, hw, bx0, by0, bx1, by1 in self.grid.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2):
            if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
                continue
            if quad_hits_seg(poly, a, b, hw):
                return True
        return False


def hem_on_water(poly: Poly, wet: Sequence[tuple[Any, float]] | WetLines, pond: Any) -> bool:
    """Does this dry-hem plot lie across a watercourse or over the pond?

    LIFTED OUT OF `_comb_draw_hem` (feature 146, GM 2026-08-28 on inner functions and testability). The
    hem yields to standing water because `build_comb` lays the fan from pure geometry and `draw_comb_field`
    used to render it blind - it was the ONLY placer that consulted nothing, so a hem plot could be drawn
    straight across a stream that had been authored earlier (Ubame's). The stream arm and the pond arm are
    different geometry and want asking separately, which through the method meant building a whole comb net.

    Research: hem off water - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a dry plot across a watercourse or over the pond is not a field
    """
    if (wet if isinstance(wet, WetLines) else WetLines(wet)).hit(poly):  # a caller asking many plots hands the index in
        return True
    return bool(pond is not None and point_quad_dist(pond[0], pond[1], poly) < max(pond[2], pond[3]))


STREAM_JOIN_TOL = 13.0  # px: a channel declaring a stream end has that end within this of the stream's drawn bed - the gate's TRUNK_TOL (feature 287, labels L16)


def channel_end_on_stream(end: Sequence[float], stream: Sequence[Sequence[float]], tol: float = STREAM_JOIN_TOL) -> bool:
    """THE RULE (feature 287, labels L16; `channels_join_streams_at_confluence`): a channel end that declares a stream lies
    within `tol` of that stream's centerline - the mouth reaches INTO the water, never dying in the grass beside it. The
    intake that declares it and the test of it read this one predicate.

    Research: mouth reaches the water - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a channel end declaring a stream lies within 13 px of its centerline"""
    pts = [(float(q[0]), float(q[1])) for q in stream]
    return any(seg_dist(float(end[0]), float(end[1]), a, b) <= tol for a, b in zip(pts, pts[1:], strict=False))


DOWNHILL_FRACTION = 0.2
#: How much of a watercourse's net travel must run down the fall (water:W10, `channels_flow_downhill`): a delivery may take
#: an oblique line, but not one whose net travel is level or uphill. The retired gate test's own figure.
"""Research: downhill share - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a fifth of a course's length net down the fall"""


def runs_downhill(course: Sequence[Sequence[float]], fall: Sequence[float], frac: float = DOWNHILL_FRACTION) -> bool:
    """Does `course`'s net displacement, first point to last, run down `fall` by at least `frac` of its length - the
    channel rule (water:W10), ONE predicate for every writer of `M['channels']`: the sink's routes (`hamletgen/sink.py`)
    and the hairline feed (`_comb_source_channel`). A course that ends where it starts has no direction to judge.

    Research: water runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: net travel down the fall, at least DOWNHILL_FRACTION of the length"""
    vx, vy = float(course[-1][0]) - float(course[0][0]), float(course[-1][1]) - float(course[0][1])
    L = math.hypot(vx, vy)
    return L == 0 or vx * float(fall[0]) + vy * float(fall[1]) >= frac * L


def feed_stub(race: Sequence[Sequence[float]], envelope: Sequence[Pt]) -> list[Sequence[float]]:
    """The drawn inlet stub of a pond-fed race (feature 294 B1): its points from the last one inside the crop's `envelope` - the
    ring's corner, where the feed meets the field - to its end on the reservoir's rim (`inlet_to_rim`). With no envelope to ask, or
    no point of the race inside it, the race's last leg."""
    for i in range(len(race) - 1, -1, -1):
        if len(envelope) >= 3 and point_in_poly(float(race[i][0]), float(race[i][1]), list(envelope)):
            return list(race[i:])
    return list(race[-2:])


def outfall_run(b0: Sequence[float], b1: Sequence[float], fall: Sequence[float], lead: float = 70.0, reach: float = 520.0) -> list[Pt]:
    """The village and city comb's drain-outfall run (water:W10): `lead` px on along the drain's own exit (`b0` toward
    `b1`) for a smooth junction, then `reach` px straight down the unit `fall` off the map - taken only where it
    `runs_downhill`, which at the drawn 70 and 520 it always does (the lead can take back at most 70 of 520 px down the
    fall, so the run's net descent never drops under three quarters of its length). Where it would not, the run goes
    straight down the fall from the drain's end, which runs downhill by construction.

    Research: drain outfall - research/questions/0060-field-drains-akusuiro.drawing.html: 70 px on along the drain's exit, then 520 px straight down the fall off the map"""
    ex, ey = float(b1[0]) - float(b0[0]), float(b1[1]) - float(b0[1])
    el = math.hypot(ex, ey) or 1.0
    start = (float(b0[0]), float(b0[1]))
    mid = (start[0] + ex / el * lead, start[1] + ey / el * lead)
    run = [start, mid, (mid[0] + float(fall[0]) * reach, mid[1] + float(fall[1]) * reach)]
    if runs_downhill(run, fall):
        return run
    return [start, (start[0] + float(fall[0]) * (lead + reach), start[1] + float(fall[1]) * (lead + reach))]


def bead_drowned(q: Pt, water: Any, ellipses: Sequence[tuple[float, float, float, float]]) -> bool:
    """THE RULE (feature 287, water W33; `bund_beans_on_bunds`): an azemame bead stands on water paint - inside a pond's rim
    (`ellipses`, each grown by the rim stroke and a bead radius) or nearer than a ditch's or channel's half-width to its
    stroke (`water`, a `seg_reach_index` of (run, half) pairs). The bead drop and the test of it read this one predicate.

    Research: beads off water - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: no bean bead on a pond's rim or under a ditch's stroke"""
    if any(((q[0] - ex) / erx) ** 2 + ((q[1] - ey) / ery) ** 2 <= 1.0 for ex, ey, erx, ery in ellipses):
        return True
    return any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and seg_dist(q[0], q[1], a, b) < half for a, b, half, x0, y0, x1, y1 in water.near(q[0], q[1]))


def recorded_water(M: Mapping[str, Any]) -> Any:
    """Every recorded ditch and channel as the bead rule reads them: (run, half-width) filed once in a `seg_reach_index`.
    A ditch's half is its WIDEST - the tail of a tapered collector - since that is what the painter reaches."""
    runs = [([(float(q[0]), float(q[1])) for q in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0))) / 2.0) for d in (M.get("field_ditches") or []) if len(d.get("poly") or ()) >= 2]
    runs += [([(float(q[0]), float(q[1])) for q in c["poly"]], float(c.get("w", 3.0)) / 2.0) for c in (M.get("channels") or []) if len(c.get("poly") or ()) >= 2]
    return seg_reach_index(runs, 0.0)


class CombMixin:
    # Held between `_comb_draw_source` and `draw_comb_field` (see both): the source pond's reed fringe
    # and the no-build rect that must follow it. `Settlement.__init__` gives them their value; declared
    # here too because a mixin cannot see the composed class's own `__init__` (pyrefly, feature 142).
    _pending_fringe: Poly | None
    _pending_block: Poly | None

    def comb_base_fill(self: Settlement, net: dict[str, Any], name: str, color: str = "", full_envelope: bool = False) -> None:  # type: ignore[misc]
        """Draw a FIELD FLOOR under a build_comb net's plots and record it (M['comb_floors'][name]),
        so the parchment BACKGROUND never shows through as bare 'white' at the canal junctions the
        carve cannot tessellate (the head-race fork, the outfall corner where a supply canal dies at
        the drain, the confluence wedges - the 'blank bits on the paddies' the GM circled repeatedly,
        2026-07-22). Call BEFORE drawing the plots. `full_envelope` fills the whole envelope (cities:
        tight crop, no surrounding scrub, so edge junctions must be covered too); otherwise the fill is
        clipped to the PLOTS' union bbox (villages/hamlets: hides the nucleated map's harmless phantom
        tail - the over-declared field_fall - and the scrub matrix covers the rest). Gated by
        paddy_fan_has_floor. Villages default to a paddy-green floor, cities pass a soil tan.

        Research: field floor - CONVENTION: a paddy-green or soil-tan wash under the plots so no parchment shows"""
        from l7r.diagram.waterfields import _RICE_GREEN

        pv = [v for p in net["plots"] for v in p["poly"]]
        if not pv:
            return
        env = net["envelope"]
        epts = " ".join(f"{x:.1f},{y:.1f}" for x, y in env)
        col = color or _RICE_GREEN
        # a POLDER supplies an explicit `floor` = the ring-canal INTERIOR (the outermost irrigated channels),
        # so the green greenery is bounded exactly by the ring rather than by the dike-boundary envelope
        # rectangle that drifts in and out of the wavering ring (GM 2026-07-22). Fill it as-is; the ring canal
        # draws on top. Comb nets carry no `floor`, so they keep the envelope/bbox behavior byte-for-byte.
        floor = net.get("floor")
        if floor:
            fpts = " ".join(f"{x:.1f},{y:.1f}" for x, y in floor)
            self.add_paddy(f'<polygon points="{fpts}" fill="{col}" stroke="none"/>', cls="paddy")
            self.M.setdefault("comb_floors", {})[name] = [[round(x, 1), round(y, 1)] for x, y in floor]
            return
        if full_envelope:
            self.add_paddy(f'<polygon points="{epts}" fill="{col}" stroke="none"/>', cls="paddy")
        else:
            cid = self._cid("padbase")
            px0, px1 = min(v[0] for v in pv), max(v[0] for v in pv)
            py0, py1 = min(v[1] for v in pv), max(v[1] for v in pv)
            self.add(f'<clipPath id="{cid}"><rect x="{px0:.1f}" y="{py0:.1f}" width="{px1 - px0:.1f}" height="{py1 - py0:.1f}"/></clipPath>')
            self.add_paddy(f'<polygon points="{epts}" fill="{col}" clip-path="url(#{cid})"/>', cls="paddy")  # the field floor reads as paddy (feature 134)
        self.M.setdefault("comb_floors", {})[name] = [[round(x, 1), round(y, 1)] for x, y in env]

    def bund_junctions(self: Settlement, plots: Sequence[Mapping[str, Any]], name: str) -> None:  # type: ignore[misc]
        """Pile earth into every bund CROSSING (GM 2026-07-25; research/questions/0022-parcels-and-bunds-inside-a-polder-aze.html). Same rule as the polder's organic parcels -
        hand-piled mud has no sharp corners - but a SHARED-BARRIER field needs the opposite operation to
        express it. A polder's parcels are separate polygons with a real gap between them, so rounding is
        SUBTRACTIVE: each parcel gives up its corners and the bund, being the space between, just widens.
        A comb/terrace/ribbon carve has no gap - the bund IS the shared line, and the carve is required to
        tessellate (`paddy_fan_gapless`) - so shrinking the cells would tear holes in the field. The
        correct operation is ADDITIVE: leave the carve untouched and pile material into the junction, so
        the crossing stops being two hairlines meeting at a point and becomes a lumpy node of bund, and
        the four basin corners read rounded because the earth has taken them.

        This is the truest part of the whole rule. A bund junction is the most-worked point in a field:
        four basins push water at it, it carries the crossing foot traffic, it is where someone stands to
        open and close the water, and it is the first thing to slump and get re-piled - so it genuinely
        carries more earth than the runs between. TRUE SCALE: a plain aze runs ~1.5 ft (`AZE_FT`) and a
        junction node widens to ~4-6 ft, which is 4-6 px at hamlet scale and honestly sub-2 px at city
        scale. It is floored at the stroke width so it never disappears, but never inflated past the
        attested node - a legibility-sized dot here would be a fake 15 ft earthwork at every crossing.

        A junction is found from the DRAWN geometry, not declared: wherever >=3 plot corners coincide,
        bunds cross. That makes the pass self-selecting - a polder's parcels are inset away from each
        other and share no corner at all, so nothing is drawn on the archetype that must not get it.

        NOT A DISC AT THE CROSSING (GM 2026-07-25, on the first version): a blob centered on the node
        reads as a stamped circle, and a stamp is LESS natural than the sharp cross it replaced - at
        4-6 px no amount of jitter on a 7-gon's radius survives rasterization, and every junction gets
        the same mark. Earth does not arrive symmetrically anyway. So the node is built the way it is
        actually piled: as a separate FILLET IN EACH QUADRANT - one per plot corner meeting here, each
        with its own two independently-drawn legs and its own outward bulge, and roughly a quarter of
        quadrants left bare (nobody re-piles all four corners of a crossing in the same season). The
        irregularity is then structural rather than cosmetic: a junction can be piled heavily on one
        side and untouched on the other, and no two crossings on a map carry the same mark.

        Research:
            junction pile size - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: about 5 ft of earth, floored at the drawn aze
            pile by quadrant - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a fillet per corner, legs 0.5-2x, a quarter of corners left bare"""
        from l7r.diagram.waterfields import AZE, aze_w

        cells: dict[tuple[int, int], list[list[tuple[float, float] | list[tuple[int, int]]]]] = {}
        for pi, p in enumerate(plots):
            for vi, (x, y) in enumerate(p["poly"]):
                node = None
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for cand in cells.get((int(x // 1) + dx, int(y // 1) + dy), []):
                            cxy = cast("tuple[float, float]", cand[0])
                            if abs(cxy[0] - x) < 0.75 and abs(cxy[1] - y) < 0.75:
                                node = cand
                                break
                        if node:
                            break
                    if node:
                        break
                if node:
                    cast("list[tuple[int, int]]", node[1]).append((pi, vi))
                else:
                    cells.setdefault((int(x // 1), int(y // 1)), []).append([(x, y), [(pi, vi)]])
        rng = random.Random(int(hashlib.md5(name.encode()).hexdigest()[:8], 16))  # str hash() is salted per process - a map must redraw identically
        base = max(2.5 / self.ftpx, aze_w(self.ftpx) * 1.1)  # ~5 ft of piled earth, floored at the drawn aze
        out = []
        for bucket in cells.values():
            for _xy, members in bucket:
                corners = cast("list[tuple[int, int]]", members)
                if len(corners) < 3:
                    continue  # a run, a T-stub, or a field-edge corner - only real crossings get piled
                for pi, vi in corners:
                    if rng.random() < 0.25:
                        continue  # this quadrant has not been re-piled lately
                    poly = plots[pi]["poly"]
                    n = len(poly)
                    v = poly[vi]
                    a = _toward(v, poly[(vi - 1) % n], base * rng.uniform(0.5, 2.0))  # each leg of the fillet
                    b = _toward(v, poly[(vi + 1) % n], base * rng.uniform(0.5, 2.0))  # is piled on its own
                    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                    bulge = rng.uniform(0.15, 0.45)  # how far the pile swells past the chord into the basin
                    cx_, cy_ = mx + (mx - v[0]) * bulge, my + (my - v[1]) * bulge
                    arc = " ".join(
                        f"{(1 - f) ** 2 * a[0] + 2 * (1 - f) * f * cx_ + f * f * b[0]:.1f},{(1 - f) ** 2 * a[1] + 2 * (1 - f) * f * cy_ + f * f * b[1]:.1f}" for f in (0.0, 0.25, 0.5, 0.75, 1.0)
                    )
                    out.append(f'<polygon points="{arc} {v[0]:.1f},{v[1]:.1f}"/>')
        if out:
            self.add(f'<g fill="{AZE}" stroke="none">{"".join(out)}</g>', cls="bund")

    def draw_comb_field(self: Settlement, net: dict[str, Any], name: str, source: dict[str, Any], inwall_drain_moat_bias: Pt | None = None) -> list[Pt]:  # type: ignore[misc]
        """Draw a `build_comb` net (dry hem + flooded paddies + bunds + channels) AND register the field's
        manifest + water topology, in one call - the ~50 lines every comb gen otherwise repeats inline. Feeds
        the roll-from-seed entrypoint (which cannot hand-place any of it) but is reusable by any comb gen.
        `source` describes where the water comes from: {"kind":"pond", "pond":(cx,cy,rx,ry)} draws a tameike at
        the sluice and feeds from it; {"kind":"stream", "stream":[(x,y),...]} runs a brook in from a canvas edge
        to the sluice, and with `to` on past it and off the map (the scripted hamlet's case). Records the field
        envelope/bbox/vis_bbox, every channel as a field_ditch, and a hairline SOURCE->field feed channel, so the
        manifest's water topology names the field's source. Returns the field envelope polygon. `inwall_drain_moat_bias` marks an
        IN-WALL city fan: the drain is trimmed through inwall_drain_outfall (cut off short of the ring road,
        sluice-gated, underground conduit to the moat) before anything is drawn or recorded."""

        if inwall_drain_moat_bias is not None:
            _idr = next(c for c in net["channels"] if c["role"] == "drain")
            _idr["pts"] = self.inwall_drain_outfall(_idr["pts"], moat_bias=inwall_drain_moat_bias, field_name=name)
            _idr["trimmed"] = True  # a TRIMMED in-wall drain is a conduit stub, not a contour collector - drain_runs_cross_slope exempts it

        # BASE FILL (feature 012, now via the shared helper): a paddy-green wash under the plots so the
        # imperfect tessellation never shows the parchment background as bare "white" gaps (research.md D5).
        self.comb_base_fill(net, name)

        # THE WATER IS RECORDED BEFORE THE GROUND THAT ASKS AGAINST IT (feature 287, water W53). The ditch net is the field's
        # skeleton - the plots are cut between its threads - so its records stand before any plot is offered: the dry hem
        # then refuses a plot one of the field's own ditches crosses (`dry_plots` on `field_ditches` is forbidden), where it
        # used to be recorded first and leave the ditch to be refused on it. Recording draws nothing; the net is still
        # painted below, where it always was. (The feed from the source is recorded after the source is drawn, since it
        # snaps to the brook; it names its field, and a field's own water may lie on its own resting basin.)
        self._comb_record_ditches(net, name)
        self._comb_draw_hem(net, source, name)
        # THE IN-FIELD FEATURES ARE SEATED BEFORE THE PADDIES ARE DRAWN, AND INKED AFTER THEM (feature 287, water W28): a
        # grave carves the rings the paddies are drawn from, so the paddies must be drawn from the carved rings; the
        # features' own ink is held and emitted where it always was, over the paddies.
        _feature_ink: list[tuple[str, str]] = []
        self._paddy_features(net, _feature_ink)
        self._comb_draw_paddies(net, name)
        self.bund_junctions(net["plots"], name)
        for _svg, _cls in _feature_ink:
            self.add(_svg, cls=_cls)
        # WATER-HONEST BEADS, the draw-site half (GM 2026-08-15: "fix the water-buried beads so
        # the record stays honest"; settlement-review found 40 of Inashiro's 727 recorded beads
        # invisible under water paint). `_bund_beans` already drops plot-buried beads and beads
        # under the ditch net's late strokes; the POND paint is only known here. The flavor pass
        # runs first (moved up from the tail of this method - its pocket ponds paint over a plot's
        # interior, so their geometry must exist before the bead line commits; it draws from its
        # own seeded rng, so the move ripples no stream), then every bead inside the source pond
        # or a pocket pond is dropped BEFORE drawing and recording, so dots and manifest agree.
        sluice = net["channels"][0]["pts"][0]
        pond_rec = self._comb_draw_source(net, source, sluice)
        self._comb_draw_ditches(net)
        # ...AND THE HAIRLINE FEED IS RECORDED BEFORE THE BEADS ARE DROPPED (feature 287, water W33): it is water the bead
        # drop reads (`M["channels"]`), and recorded after the drop it could lay a bead under its own stroke.
        self._comb_source_channel(net, name, source, sluice, pond_rec)
        # ...AND THE DITCHES ARE RECORDED BEFORE THE FIELD IS (feature 230). The field record carries the bead
        # POINTS, so a bead dropped after it is dropped from the picture and not from the manifest - which is
        # the drift `bunds_and_dikes` exists to catch, and which is how a bead under a drain's wide tail came
        # to be recorded on a map that does not draw it. The drop reads the ditch records, so they go first.
        self._comb_drop_drowned_beads(net, source)
        self._comb_record_field(net, name)
        # THE BEADS GO LAST OF THE FIELD'S INK, because the thing they have to keep out of does not exist until
        # the line above (feature 230). A drawing method sees only what is in `self.M` when it runs, and the
        # bead pass ran BEFORE the ditches were recorded, so its water test had nothing to read and a bead sat
        # under a drain's wide tail on the reference hamlet. Drawn here it clears the pond, the pocket ponds and
        # every recorded ditch alike; nothing is painted over, because a bead that would be is dropped first.
        self._comb_draw_beads(net)
        # a hairline SOURCE -> field feed carrying the topology (winds a little into the paddy interior). It
        # STARTS at the source (the pond center, or the sluice for a stream) so channel_source_anchored /
        # pond_connected_to_field see it, and carries a gentle perpendicular KINK so channel_winds_gently passes.
        # source kind "cascade" = the field is fed plot-to-plot from an UPSTREAM field (the caller
        # records its own connector channel with to={"kind":"field",...}), so no hairline is added -
        # its frm={"kind":"stream"} anchor would dangle with no stream at the sluice.
        _fringe = self._pending_fringe  # see `_comb_draw_source`: the reeds keep off water that exists
        if _fringe:
            self._pending_fringe = None
            self.marsh(_fringe, role="pond_fringe")
            # ...AND THE POND'S NO-BUILD RECT FOLLOWS THE REEDS, exactly as it did before the fringe was
            # deferred (settlement-review 2026-08-29). `block_polys` stops a BUILDING standing on the water;
            # the reed scatter reads it too, so deferring the fringe past it silently fed the reeds a
            # keep-out covering the pond's bbox + 10 px - the shore band itself. Measured: 32 of 54 tufts
            # gone, 45% of the annulus, three sectors empty, the tameike reading as a bare plate. That was
            # 92% of the ink this fix actually changed, against the 3 tufts the channel rule intends.
            self.block_polys.append(self._pending_block)
            self._pending_block = None
        return cast("list[Pt]", net["envelope"])

    def _comb_draw_hem(self: Settlement, net: dict[str, Any], source: dict[str, Any] | None = None, name: str = "") -> None:  # type: ignore[misc]
        """Draw the dry upslope hem, skipping any plot that falls on an earlier fan's rice or on standing water -
        including the brook the field is being cut around, which `source` carries and the manifest does not yet.

        Research:
            hem placement - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the dry plots upslope of the supply canal, as the net lays them
            hem off rice and water - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a plot on an earlier fan's rice, on water or on the field's own ditch is dropped
            bank beside the source brook - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a bund's width, 3 px, past the brook's bank
            plot size and crop - NONE: taken from the net as build_comb laid them
            dry plot ink - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the crop's own fill, furrowed, a tan edge"""
        from l7r.diagram.waterfields import hem_on_paddy

        # a fan's hem is generated blind to the OTHER fans on a multi-fan map, so drop any hem plot
        # that lands on a previously recorded fan's rice (this fan's own field record is appended
        # below, AFTER this loop, so a hem's legitimate berm-kiss against its own envelope never
        # tests). Same predicate as the dry_plots_clear_of_paddies gate - see hem_on_paddy's
        # docstring (waterfields.py) for the why and the motivating Tango incident.
        _prior_paddies = [fld["outline"] for fld in self.M["fields"] if fld.get("kind") == "paddy"]
        # WHAT IS ALREADY ON THE MAP (GM go-ahead 2026-07-26). build_comb lays the fan from pure
        # geometry, and draw_comb_field used to render it blind - it was the ONLY placer that
        # consulted nothing - so a hem plot could be drawn straight across a watercourse that had
        # been authored earlier (Ubame's stream). Now the hem yields to standing water. Maps whose
        # hems touch no water are unaffected, byte for byte, because nothing is skipped there.
        _wet: list[tuple[Any, float]] = []
        for _wk, _wdw in (("streams", 9.0), ("channels", 2.5), ("canals", 14.0)):
            for _wr in self.M.get(_wk, []) or []:
                _wpl = _wr.get("poly") or _wr.get("pts")
                if _wpl:
                    _wet.append((_wpl, float(_wr.get("w") or _wdw) / 2))
        _wpond = self.M.get("pond")
        # ...AND THE BROOK THIS FIELD IS BEING FITTED AROUND, which is not in `M["streams"]` yet (feature 230).
        # The source hands its own course in, and the hem is drawn before the source is - so reading the
        # manifest alone made the hem blind to the one watercourse the field was cut around, and
        # `settlement-review` measured 34 ft of Mizuguchi's brook drawn across a soy plot's corner with the
        # water ink over the plow boundary. The geometry is in hand; take it from the caller rather than from
        # a record that does not exist yet.
        _src_brook = (source or {}).get("stream") if isinstance(source, dict) else None
        if _src_brook and len(_src_brook) >= 2:
            # ...with a BUND'S WIDTH of margin beyond the bank (settlement-review, feature 230 pass 11). At the bare half-width a
            # hem plot 5.9 ft from Mizuguchi's centerline was kept, which leaves about half a foot between the water's bank and
            # the plot's plow boundary - the crop stops at the bank, and a bund is the thing that stops it.
            _wet.append(([(float(q[0]), float(q[1])) for q in _src_brook], 9.0 / 2 + 3.0))

        _wet_lines = WetLines(_wet)  # filed once: every hem and reserve plot asks it

        def _hem_on_water(poly: Poly) -> bool:
            return hem_on_water(poly, _wet_lines, _wpond)

        def _refused(poly: Poly) -> bool:
            # the crop stops at the bank - and a plot the registry of what stands refuses is not offered (feature 287, water
            # W53): the field's own ditch net is recorded before the hem, so a plot one of its ditches crosses is refused here
            return any(hem_on_paddy(poly, _pol) for _pol in _prior_paddies) or _hem_on_water(poly) or not self.admits("dry_plots", {"poly": [[round(x, 1), round(y, 1)] for x, y in poly]})

        drawn = [p for p in net["dry_plots"] if not _refused(p["poly"])]  # the dry upslope hem
        drawn += self._coarse_grain_top_up(net, sum(poly_area(p["poly"]) for p in drawn), _refused)
        for p in drawn:
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p["poly"])
            self.add_paddy(f'<polygon points="{pts}" fill="{p["fill"]}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>', cls=p["crop"])  # each dry crop is its own class (feature 134)
            self._draw_furrows(p["poly"], p["furrow"], p["theta"], cls=p["crop"])
            # ...with its TRACT (269 B06), named by field so two fans' tracts never share a name: `dry_plot_furrows_vary` judges the
            # plots of one tract to share a row direction and the plots across a seam to differ.
            self.M["dry_plots"].append(
                {"poly": [[round(x, 1), round(y, 1)] for x, y in p["poly"]], "crop": p["crop"], "theta": round(p["theta"], 3), **({"tract": f"{name}:{p['tract']}"} if "tract" in p else {})}
            )
            # A HEM PLOT GOES IN BOTH REGISTRIES, and the second one is the fix (2026-08-11).
            # `block_polys` is the no-build list, which keeps a farmstead off the crop. `dry_polys`
            # is the list the GROVE clump filter, the lane/tree fringe, the threshing-yard and
            # garden nudges and the ground-cover scatters read - so a map that registered only the
            # first had hem plots that stopped a house and not a tree. Every hand-authored comb gen
            # compensates with its own `s.dry_polys.append(...)` line (hoshigaoka, ueda, hikari,
            # hoshizora, hirameki, ubame all carry one); the maps built THROUGH this method never
            # did, and passed only because their clusters happened to sit away from the hem. Found
            # by the scripted-generation experiment, whose clusters do not (dev/lessons.md, "Four lessons from the scripted-hamlet experiment").
            # Registering here is the same discipline as everywhere else in this file: placement and
            # its check must read the SAME source, and the source is what was actually drawn.
            self.block_polys.append(p["poly"])
            self.dry_polys.append(p["poly"])

    def _coarse_grain_top_up(self: Settlement, net: dict[str, Any], drawn_px2: float, refused: Callable[[Poly], bool]) -> list[dict[str, Any]]:  # type: ignore[misc]
        """The reserve plots a wild fan middle adds to the drawn strip so it holds the coarse-grain need (feature 287, W36;
        `grain.py`, research/contents.json#fields 0011): none where the hamlet grows its barley on its drained paddy over the
        winter and that covers the need, the middle's plots nearest the toe first where it does not. The winter crop is
        rolled only among the forms this ground can feed (`WINTER_CROP`'s typing rule), so the band returned holds the
        need by construction. A generated comb hamlet only - it alone rolls `fan_middle`; the form and the acreage go in the meta.

        Research:
            top-up scope - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: a generated comb hamlet whose fan middle is wild
            drained acres - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: every plot not painted as wet paddy counts as drained
            need and count - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the winter crop rolled among the site's forms, the band topped up to the need"""
        from l7r.diagram.waterfields import FLOODED

        meta = self.M["meta"]
        if meta.get("generated_by") != "hamletgen" or "fan_middle" not in meta or "dry_reserve" not in net:
            return []
        ft2 = float(meta.get("ftpx") or 1.0) ** 2 / SQ_FT_PER_ACRE
        drained = sum(poly_area(p["poly"]) for p in net.get("plots", []) if p.get("fill") != FLOODED) * ft2
        offered = [p for p in net["dry_reserve"] if not refused(p["poly"])]
        households = int(meta.get("households") or 0)
        room = (drawn_px2 + sum(poly_area(p["poly"]) for p in offered)) * ft2
        form = resolve_knob("winter_crop", self.seed, {**self.knob_context(), "grain_households": households, "grain_drained_acres": drained, "grain_room_acres": room}, self.knob_pins)
        self._resolved_knobs["winter_crop"] = form
        need = dry_need_acres(households, drained, form)
        added = top_up(drawn_px2, offered, need / ft2, refused)
        meta.update(
            winter_crop=form,
            coarse_grain_room_acres=round(room, 2),
            coarse_grain_dry_need_acres=round(need, 2),
            coarse_grain_dry_acres=round((drawn_px2 + sum(poly_area(p["poly"]) for p in added)) * ft2, 2),
        )
        return added

    def _comb_draw_paddies(self: Settlement, net: dict[str, Any], name: str = "") -> None:  # type: ignore[misc]
        """Draw the flooded paddy plots, and write the topography record and the paint record the overlay
        and flooded-wedge checks read.

        Research:
            resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: whole basins neither low nor blue, along the fan's fall; none on a dike-pond block
            blue plot class - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html, research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: every
                FLOODED-fill plot classed wet paddy, the random freshly flooded plot of `fields/paddy.py` included, though the tint marks ground, not season"""
        from l7r.diagram.waterfields import AZE  # noqa: I001 - FLOODED is aliased for the picture record below
        from l7r.diagram.waterfields import FLOODED as _WF_FLOODED
        from l7r.diagram.waterfields import aze_w

        # THE RESTING PLOTS (269 B01, `PADDY_REST` in paddy.py): whole basins, chosen from the plots that are neither low
        # (the wet ground the pocket pond and the overlays take) nor painted blue, along this fan's own fall. A dike-pond
        # block rests none: its open water is the fabric (`_paddy_features` stands off it for the same reason).
        _ddp = math.radians(float(net.get("down_deg") if net.get("down_deg") is not None else self.M["meta"].get("down_deg", 90)))
        _may = [i for i, p in enumerate(net["plots"]) if not p.get("low") and p["fill"] != _WF_FLOODED and len(p["poly"]) >= 3]
        if self.M["meta"].get("field_archetype") == "mulberry_dike_fishpond":
            _may = []
        _cands = [(p["poly"], sum(v[0] * math.cos(_ddp) + v[1] * math.sin(_ddp) for v in p["poly"]) / len(p["poly"])) for p in (net["plots"][i] for i in _may)]
        _rest = {_may[k] for k in self.resting_plots(name, _cands)}
        for i, p in enumerate(net["plots"]):  # the flooded paddies
            if i in _rest:
                p["rest"] = True
                self.rest_basin(p["poly"], aze_w(self.ftpx), name)
                continue
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p["poly"])
            # ONE polygon, TWO classes (feature 134 `Split`): the fill is the flooded paddy, the stroke is
            # the bund - the HTML target emits a fill-only and a stroke-only copy so they highlight apart
            # THE BLUE PLOT IS ITS OWN KIND (feature 159, GM 2026-08-29: "that is its own type of thing,
            # and it deserves its own explanation"). It is the wet paddy - shitsuden, ground too poorly
            # drained to dry out - and it is decided HERE, from the fill about to be drawn, so the class
            # and the color cannot disagree. The bund half is untouched: a blue plot's stroke is a bund
            # like every other, and hovering one still lights the whole fabric.
            plot_cls = "wet paddy" if p["fill"] == _WF_FLOODED else "paddy"
            self.add_paddy(f'<polygon points="{pts}" fill="{p["fill"]}" stroke="{AZE}" stroke-width="{aze_w(self.ftpx):.2f}" stroke-linejoin="round"/>', cls=Split(plot_cls, "bund"))
            # Record the LOW/WET plots (feature 010). This is the topographic ELIGIBILITY set the
            # plot-based land-use overlays draw from. It is written HERE, by the field pass, so that
            # `overlays_on_wet_ground_only` compares two INDEPENDENTLY-produced records rather than
            # reading back the overlay's own self-report - a check that reads one source has no teeth.
            if p.get("low"):
                self.M.setdefault("wet_plots", []).append(_centroid(p["poly"]))
            if p["fill"] == _WF_FLOODED:
                # ...and the PAINTED tint (2026-08-16): `wet_plots` is the topography record
                # (which plots are LOW), this is the picture record (which are BLUE) - the
                # flooded-wedge check judges what the paint reads as, and a check that cannot
                # see the paint cannot judge it (the azemame water-honesty precedent).
                self.M.setdefault("flooded_plots", []).append(_centroid(p["poly"]))

    def _comb_drop_drowned_beads(self: Settlement, net: dict[str, Any], source: dict[str, Any]) -> None:  # type: ignore[misc]
        """Drop every azemame bead that water would bury - pond paint or a ditch's own stroke - then draw the
        rest, so the dots and the manifest agree.

        THE DITCH HALF IS THE TAIL'S WIDTH, NOT THE HEAD'S (feature 230). A drain collector is recorded with
        `w` at its head and `w_tail` where it leaves, and it is painted as a taper between them - so a bead
        sitting 2.2 ft off a ditch recorded at 1.5 ft was still under ink, because that ditch ends at 5.5.
        Measured on the reference hamlet the day the brook moved the field under it. The painter's own widest
        figure is what the bead has to clear, which is the same figure `bunds_and_dikes` judges it by: a check
        and the code it checks must read the SAME number, or the map and the rule drift apart quietly.

        THE DROP IS PER RUN, AND A RUN LEFT WITH ONE BEAD LOSES IT (feature 247, GM 2026-09-14: at least two
        glyphs on any bund segment that has beans). The net's `bund_bean_runs` are `_bund_beans`' contiguous
        lines; each is split where a bead drowns and judged part by part by `bead_runs`, the one place the
        rule lives, and the flat `bund_beans` list the draw and the record read is re-flattened from what
        survives, so the three - the runs, the dots and the manifest - agree.

        Research: beads on bunds - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a bead on water or a grave mound is dropped, a run left with one bead loses it"""
        from l7r.diagram.waterfields import bead_runs

        _bw: list[tuple[float, float, float, float]] = []
        if source.get("kind") == "pond":
            _bwx, _bwy, _bwrx, _bwry = source["pond"]
            _bw.append((_bwx, _bwy, _bwrx + 3.0, _bwry + 3.0))  # +3: the rim stroke and a bead radius
        _bw += [(fp["x"], fp["y"], fp["rx"] + 3.0, fp["ry"] + 3.0) for fp in self.M.get("field_ponds") or []]
        net["bead_ponds"] = _bw  # ...and kept with the net, for `settle_beads` to judge the same beads against the same ponds
        # THE WATER LINES FILED ONCE (feature 284, FR-009): every bead measured every segment of every ditch and channel. A
        # bead nearer than `half` to a segment stands inside that segment's box widened by `half`, so the segments whose
        # widened box holds the bead are every one that can drown it, and the same `seg_dist` decides - `bead_drowned`,
        # the one predicate (feature 287, water W33).
        _water_idx = recorded_water(self.M)
        # A GRAVE CARVED INTO THE FIELD (feature 287, water W28) takes its mound's ground out from under the bunds the beads
        # were laid along, and may weld or bare a carved piece: a bead on the mound, or on a stretch of bund no ring now
        # has, is dropped. Only where a grave was carved, so every other field's beads are judged exactly as before.
        _graves = net.get("grave_discs") or []
        _bunds = seg_reach_index([([*p["poly"], p["poly"][0]], 1.0) for p in net["plots"] if len(p["poly"]) >= 3], 0.0) if _graves else None

        def _dry(q: tuple[float, float]) -> bool:
            return (
                not bead_drowned(q, _water_idx, _bw)
                and all(math.hypot(q[0] - gx, q[1] - gy) >= gr for gx, gy, gr in _graves)
                and (_bunds is None or any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and seg_dist(q[0], q[1], a, b) <= tol for a, b, tol, x0, y0, x1, y1 in _bunds.near(q[0], q[1])))
            )

        net["bund_bean_runs"] = [part for run in net["bund_bean_runs"] for part in bead_runs(run, _dry)]
        net["bund_beans"] = [q for run in net["bund_bean_runs"] for q in run]

    def _comb_draw_beads(self: Settlement, net: dict[str, Any]) -> None:  # type: ignore[misc]
        """Draw what survived `_comb_drop_drowned_beads` - the ink, after the record it agrees with.

        Research: bead glyph - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: r 1.4 px, BEAN_GREEN at 0.85"""
        from l7r.diagram.waterfields import BEAN_GREEN

        beads = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{BEAN_GREEN}"/>' for x, y in net["bund_beans"])
        z = self.add(f'<g opacity="0.85">{beads}</g>', cls="bund beans")
        # THE SLOT IS KEPT ON THE SETTLEMENT (`_bead_slots`), so a re-roll's deep copy of it carries its beads' slots with it
        self._bead_slots.append((z, net["bund_bean_runs"], self.M["fields"][-1] if self.M.get("fields") else None, list(net.get("bead_ponds") or [])))

    def settle_beads(self: Settlement) -> int:  # type: ignore[misc]
        """Drop every bead water recorded AFTER its field now lies under, from the ink and the record together; return
        how many were dropped (feature 287, water W33).

        The field drops its drowned beads over the water recorded when it is drawn, and a later stage can record more -
        the sink's drain run (`hamletgen/sink.py` `drain_run`) leaves the field over its bunds. So the rule is held
        where the LAST water writer has run: each field's bead ink is rewritten in its own slot from the runs that
        survive `bead_drowned` over every ditch and channel then recorded, each run re-split by `bead_runs` (a run left
        under two beads goes), and the field's record re-flattened from the same runs - the dots and the manifest agree.

        Research: beads off later water - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the drowned-bead rule re-run after the last water writer"""
        from l7r.diagram.waterfields import BEAN_GREEN, bead_runs

        water = recorded_water(self.M)
        # ...and every pond recorded by now: the tameike `stage_sink` digs below the field, a field pond laid after it
        now = [(float(p[0]), float(p[1]), float(p[2]) + 3.0, float(p[3]) + 3.0) for p in [self.M.get("pond")] if p]
        now += [(float(fp["x"]), float(fp["y"]), float(fp["rx"]) + 3.0, float(fp["ry"]) + 3.0) for fp in self.M.get("field_ponds") or []]
        dropped = 0
        for k, (z, runs, rec, ponds) in enumerate(self._bead_slots):
            kept = [part for run in runs for part in bead_runs(run, lambda q, _p=ponds + now: not bead_drowned(q, water, _p))]
            before, after = sum(len(r) for r in runs), sum(len(r) for r in kept)
            if after == before:
                continue
            dropped += before - after
            flat = [q for run in kept for q in run]
            self.out[z] = '<g opacity="0.85">' + "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{BEAN_GREEN}"/>' for x, y in flat) + "</g>"
            if rec is not None:
                rec["bund_beans"] = [[round(x, 1), round(y, 1)] for x, y in flat]
            self._bead_slots[k] = (z, kept, rec, ponds)
        return dropped

    def _comb_draw_source(self: Settlement, net: dict[str, Any], source: dict[str, Any], sluice: Any) -> Any:  # type: ignore[misc]
        """Draw the water SOURCE - a tameike with its fringe and no-build block, or a feeder stream.

        Returns the pond center when a pond was drawn, else None: the hairline topology channel
        anchors on whichever of the two it was.

        Research:
            source pond - research/questions/0061-reservoir-ponds-tameike.drawing.html: a tameike at the sluice, a reed fringe and a no-build block round it
            fringe and margin widths - UNRESEARCHED: 40 px of reed fringe, a 10 px no-build margin
            pond feeder width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the feeder stream drawn 6 px wide
            planted pond bank - research/questions/0061-reservoir-ponds-tameike.drawing.html: every bank drawn bare; the bank planted sparsely with mulberry and cudrania is never rolled
            feeder brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a stream from the map's edge to the sluice, on past it where `to` says
            feeder brook width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html, research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the brook drawn 7 px wide, in px rather than feet"""
        pond_rec: Any = None
        if source.get("kind") == "pond":
            pcx, pcy, prx, pry = source["pond"]
            self.stream([(sluice[0], sluice[1]), (pcx, pcy)], frm={"kind": "offmap"}, to={"kind": "pond"}, width=6) if source.get("feeder") else None
            self.pond(pcx, pcy, prx, pry)
            # THE FRINGE WAITS FOR THE WATER (feature 151, found by the overlap audit (retired 2026-09-06, feature 193) the day it was
            # written). The reed scatter keeps off every drawn watercourse - but this ran BEFORE the field's
            # channels were inked or recorded, so on a polder, whose inlet hairline runs straight through the
            # reservoir's fringe, the keep-out had nothing to keep off: measured on Kuwabata, one tuft 4.6 px
            # from the hairline with three of its blades drawn across the water. The ring is handed back and
            # scattered once the channels exist. Its own rng is seeded from its bbox, so the scatter's draw
            # order is unchanged - only the keep-out now sees what it is supposed to avoid.
            fringe_ring = pond_fringe_ring(pcx, pcy, prx, pry, 40.0)  # the shared ring - its docstring carries the two ordering rules this call site owes
            pond_rec = (pcx, pcy)
            self._pending_fringe = fringe_ring  # drawn by `draw_comb_field` once every channel is recorded
            self._pending_block = [(pcx - prx - 10, pcy - pry - 10), (pcx + prx + 10, pcy - pry - 10), (pcx + prx + 10, pcy + pry + 10), (pcx - prx - 10, pcy + pry + 10)]
        elif source.get("kind") == "stream" and source.get("stream"):
            # no "stream" polyline = an existing on-map stream already runs at the sluice (the town
            # pattern: the comb taps the map's stream via a weir); nothing extra is drawn, the
            # hairline topology channel below still anchors to that stream
            self.stream(source["stream"], frm={"kind": "offmap"}, to=source.get("to"), width=7)  # `to`: where a brook that runs on past the sluice leaves (feature 287, water:W07)
        return pond_rec

    def _comb_draw_ditches(self: Settlement, net: dict[str, Any]) -> None:  # type: ignore[misc]
        """Draw the ditch net into the LATE water block, then the drain-outfall brook.

        Research:
            ditch net over the paddies - CONVENTION: drawn in the late block, ring trunk last
            drain outfall - research/questions/0060-field-drains-akusuiro.drawing.html: a dug drain run straight down the fall off the map at the collector's tail width
            outfall corridor - research/questions/0058-ground-too-wet-to-build-on.drawing.html: 33 px no-build either side of the outfall run on every map (the record gives it for town and city maps)
            outfall recorded width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: recorded at w 2.5 while inked at the drain's tail width (~5.5)"""
        # The ditch net ALWAYS goes to the LATE water block (GM 2026-07-21: Hoshizora's canals
        # "rendering below the rice paddies"). In the shared block - anchored at the FIRST water
        # call - the net composites UNDER any plots painted after that anchor: a town/city stream
        # or moat drawn before the field anchors it early (the whole net invisible), and even on
        # a village a SECOND comb's plots covered the first comb's net (Hikari-no-sato). The late
        # block re-anchors at every call (see _water), so the net lands after the LAST field's
        # plots and draws OVER every paddy, exactly as the hand-drawn maps intend. The cities
        # discovered the early-anchor half of this and patched it per-gen (tango/nagahara
        # `late=True`); this makes it automatic and closes their residual multi-fan hole too.
        # the POLDER RING trunk (feeder / drain / toe collectors) draws LAST, ON TOP of the laterals that feed
        # it, so every lateral-to-trunk junction is a clean T covered by the trunk - not a lateral end poking a
        # stub past the trunk into the dike corridor (GM 2026-07-22). Comb nets set no `seg`, so their draw
        # order (widest-first) is unchanged and byte-identical; only the polder ring re-sorts.
        _ring_last = {"feeder", "drain", "e_toe", "w_toe"}
        for c in sorted(net["channels"], key=lambda c: (c.get("seg") in _ring_last, -c["w"])):
            col, cls = ditch_style(c["role"], self.M["meta"].get("field_archetype"))  # ONE read decides both the hue and the hover class (feature 230)
            self.field_channel(c["pts"], col, c["w"], c.get("w_tail", c["w"]), late=True, cls=cls)
        if net["brook"]:
            # the drain-outfall brook shoots STRAIGHT downhill off-map (a fan field's own wiggly brook can
            # re-enter the paddy and trip streams_avoid_fields; a straight downhill exit never does)
            ddb = self.M["meta"].get("down_deg", 90)
            bdx, bdy = math.cos(math.radians(ddb)), math.sin(math.radians(ddb))
            b0 = net["brook"][0]
            b1 = net["brook"][1] if len(net["brook"]) > 1 else (b0[0] + bdx, b0[1] + bdy)
            # (first segment = drain direction -> smooth junction; then straight downhill AWAY from the field ->
            # clears a fan envelope's concave lobe without an acute turn, since the drain already runs downhill)
            # A DRAINAGE DITCH, not a stream (feature 230): the collector's dug continuation, drawn at the
            # collector's tail width with the drain's hue and class, recorded in `channels` like the pond run
            # - the same stroke `hamletgen/sink.py` `drain_run` draws, so every sink carries one kind of thing.
            # ...AND IT RUNS DOWNHILL BY THE CHANNEL RULE'S OWN PREDICATE (feature 287, water W10): `outfall_run` asks
            # `runs_downhill`, as the hamlet's sink routes do
            _run = outfall_run(b0, b1, (bdx, bdy))
            _dw = next((float(_c.get("w_tail", _c["w"])) for _c in net["channels"] if _c.get("role") == "drain"), 5.5)
            col, cls = ditch_style("drain")
            # ...INTO THE LATE BLOCK WITH THE NET (feature 287, water W38): drawn into the shared early block it was spliced
            # at the FIRST water call, before every plot painted after it - a second fan's paddies, or this fan's own where
            # the run's middle lies over the toe - so the plots covered it. The late block re-anchors after the last field.
            _rec = {"poly": [[round(x, 1), round(y, 1)] for x, y in _run], "frm": {"kind": "drain"}, "to": {"kind": "offmap"}, "w": 2.5}
            refuse_unadmitted(self.M, "channels", _rec)  # asked before it is drawn: the straight run is the only one (W53)
            self.field_channel(_run, col, _dw, _dw, late=True, cls=cls)
            self.M["channels"].append(_rec)
            self.corridors.append((list(_run), 33.0))

    def _comb_record_field(self: Settlement, net: dict[str, Any], name: str) -> None:  # type: ignore[misc]
        """Assemble and append this fan's M['fields'] record: envelope, per-plot dims, drain-hem rings,
        plot rings in draw order and the bead points."""
        env = [[round(x, 1), round(y, 1)] for x, y in net["envelope"]]
        exs, eys = [p[0] for p in env], [p[1] for p in env]
        pvx = [v[0] for p in net["plots"] for v in p["poly"]]
        pvy = [v[1] for p in net["plots"] for v in p["poly"]]
        # Per-plot [along-fall span, cross-fall span, centroid x, centroid y, vertex count, count of
        # still-square corners], so parcel-fabric checks (polder_parcels_vary, polder_parcels_front_water,
        # polder_parcels_are_organic) measure the DRAWN geometry from the manifest rather than trusting
        # a builder self-report. The last two are the OUTLINE shape: a ruled quad is 4 vertices with all
        # 4 corners square, while a hand-piled parcel carries a densely sampled, wandering outline on
        # which most - not all - corners have eased. The pair separates earth from CAD without recording
        # every vertex (the full outlines would roughly double a polder manifest for no extra teeth).
        ddp = float(self.M["meta"].get("down_deg", 90))
        pdx, pdy = math.cos(math.radians(ddp)), math.sin(math.radians(ddp))
        pdims = []
        for p in net["plots"]:
            al = [vx * pdx + vy * pdy for vx, vy in p["poly"]]
            cr = [vx * pdy - vy * pdx for vx, vy in p["poly"]]
            pcx, pcy = _centroid(p["poly"])
            pdims.append([round(max(al) - min(al), 1), round(max(cr) - min(cr), 1), round(pcx, 1), round(pcy, 1), len(p["poly"]), _sharp_corners(p["poly"])])
        # THE BUNDS ALONG THE COLLECTOR, recorded so the gate can actually see them (2026-08-08).
        # `pdims` above is extents-and-a-centroid: it cannot express "this bund is drawn ACROSS the
        # drainage ditch", which is precisely the defect the GM caught on Hoshizora - the hem plots
        # were laid on the contour while the collector runs at up to ~19 deg to it, so every hem
        # bund started above the ditch and ended below it. `paddy_bunds_clear_the_collector` needs
        # the real outlines to judge that, so the SMALL SET of plots that actually border this fan's
        # drain carries its polygon into the manifest - a dozen-odd rings per fan, not a second copy
        # of the field. Band is generous (a plot merely NEAR the ditch is cheap to record and a plot
        # the band misses is invisible to the check, which is the failure that matters).
        _dch = next((c for c in net["channels"] if c["role"] == "drain" and len(c["pts"]) >= 2), None)
        _hem_rings: list[list[list[float]]] = []
        if _dch is not None:
            _dpp = _dch["pts"]
            _band = 30.0 + max(_dch["w"], _dch.get("w_tail", _dch["w"]))
            _dx0, _dy0 = min(q[0] for q in _dpp) - _band, min(q[1] for q in _dpp) - _band
            _dx1, _dy1 = max(q[0] for q in _dpp) + _band, max(q[1] for q in _dpp) + _band
            # THE DRAIN'S SEGMENTS FROM AN INDEX (feature 306, the GM: a check against many things means a line was not
            # drawn to stay beside). Each vertex of each plot near the drain measured its distance to EVERY drain segment -
            # 12,263 `seg_dist` a call on the pool - for a yes/no that only the segments within `_band` can answer. Each
            # segment is filed by its box widened by the band (and a pixel, so a rounding cannot drop one), the vertex asks
            # the ones whose widened box holds it, and `seg_dist <= _band` decides as before: the minimum over every
            # segment is within the band exactly when some segment is.
            _hem = seg_reach_index([(_dpp, 1.0)], _band)
            for p in net["plots"]:
                if any(_dx0 <= vx <= _dx1 and _dy0 <= vy <= _dy1 for vx, vy in p["poly"]) and any(within_reach(_hem, vx, vy, _band) for vx, vy in p["poly"]):
                    _hem_rings.append([[round(vx, 1), round(vy, 1)] for vx, vy in p["poly"]])
        _fld: dict[str, Any] = {
            "name": name,
            "kind": "paddy",
            "outline": env,
            "bbox": [min(exs), min(eys), max(exs), max(eys)],
            "vis_bbox": [min(pvx), min(pvy), max(pvx), max(pvy)],
            "plots": pdims,
            "drain_hem": _hem_rings,
            # THE PLOT RINGS, IN DRAW ORDER, plus the azemame bead points (GM 2026-08-15). `pdims`
            # above deliberately compacts each plot to extents-and-a-centroid, but that record
            # cannot express "this plot is painted OVER that one's bund" - `_fill_wedges`' fillers
            # lap up to ~12 real ft onto a neighbor and paint last, and the bead line laid along
            # the buried stretch surfaced as green dots floating mid-paddy on Inashiro. A check can
            # only judge bead-on-visible-bund from the real rings in paint order, so they are
            # recorded in full (bund_beans_on_bunds reads both; draw order IS list order).
            #
            # THIS IS A PAINT-ORDER STACK, NOT A PARTITION - DISSOLVE BEFORE YOU MEASURE ANYTHING
            # (GM decision 2026-08-17). Rings LAP: a filler painted later covers part of its
            # neighbor, which is exactly why the pair reads as the one shared aze a real fan has,
            # and the stack is the honest record of the INK. It is NOT an area record. Summing
            # these areas double-counts the lapped ground (0.4-2.5% of the fabric, measured over
            # the scripted hamlets and a 48-seed cohort), and treating two rings as adjacent
            # because they touch says nothing about
            # which of them the reader can see. So anything computing acreage, per-field yield or
            # basin-to-basin adjacency must dissolve the stack first (later ring wins) rather than
            # trusting the list. Trimming each ring to its visible extent here - which would make
            # this a true partition - was priced and DECLINED: it would re-derive
            # `bund_beans_on_bunds`, which is built ON the burial, and put polygon booleans on the
            # gate's path. The ceiling that keeps the lap small enough for this note to stay true
            # is `paddy_plot_rings_overcount_stays_marginal`; the full decision, with both declined
            # alternatives, is in future-work/.
            "plot_rings": [[[round(vx, 1), round(vy, 1)] for vx, vy in p["poly"]] for p in net["plots"]],
            "bund_beans": [[round(bx, 1), round(by, 1)] for bx, by in net["bund_beans"]],
        }
        if net.get("cell") is not None:
            # THE DESIGN CELL this fan was carved to, in px^2 (build_comb only - the terrace, ribbon
            # and polder engines record none, and the size floor is deliberately comb-only). Carried
            # so `paddy_basins_are_worth_their_bund` measures each basin against the reference the
            # PLACER used instead of re-deriving one from `meta.ftpx`, which `plot_texture` makes
            # wrong. Legacy manifests lack it and the check skips them.
            _fld["cell"] = round(float(net["cell"]), 1)
        if net.get("down_deg") is not None:
            _fld["down_deg"] = net["down_deg"]  # this fan's LOCAL fall (see build_comb)
        if net.get("fork") is not None:
            # the bunsuiguchi division point (build_comb only - a polder net records none), read by
            # comb_supply_commands_both_flanks; legacy manifests lack it, so the check skips them
            _fld["fork"] = [round(net["fork"][0], 1), round(net["fork"][1], 1)]
        self.M["fields"].append(_fld)

    def _comb_record_ditches(self: Settlement, net: dict[str, Any], name: str) -> None:  # type: ignore[misc]
        """Record one field_ditch per channel, carrying the trimmed and polder-side tags.

        A RECORD DOES NOT CARRY A POINT TWICE (settlement-review, feature 230 pass 12). The head race is traced to the
        fork it ends at, and where the trace already stood there the fork was appended again - so three pool maps
        shipped a ditch whose last two points are identical, and on two of them the whole record WAS that duplicate
        plus a lead: Inashiro's was 3.2 ft of "main" and Mizuguchi's 21.9, each drawn as its own stroke, each a hover
        region a reader could meet, each reading on the sheet as a blunt stub of ditch stopping in the bare hem. What
        is dropped here is only ink nothing is losing: a run under a foot has no course to show."""
        for c in net["channels"]:
            _pts = [q for i, q in enumerate(c["pts"]) if i == 0 or math.dist(q, c["pts"][i - 1]) > 0.05]
            rec = {"poly": [[round(x, 1), round(y, 1)] for x, y in _pts], "role": c["role"], "field": name, "w": round(c["w"], 1), "w_tail": round(c.get("w_tail", c["w"]), 1)}
            if c.get("trimmed"):  # a TRIMMED in-wall drain is a conduit stub, not a contour collector
                rec["trimmed"] = True
            if c.get("seg"):  # a polder ring-side tag (feeder/e_toe/w_toe/drain/lateral), so footbridge placement can be side-aware
                rec["seg"] = c["seg"]
            refuse_unadmitted(self.M, "field_ditches", rec)  # the skeleton, recorded before the ground that asks against it (W53)
            self.M["field_ditches"].append(rec)

    def _comb_source_channel(self: Settlement, net: dict[str, Any], name: str, source: dict[str, Any], sluice: Any, pond_rec: Any) -> None:  # type: ignore[misc]
        """Record the hairline SOURCE -> field feed channel that carries the water topology.

        Keeps its own `kind != 'cascade'` guard: a cascade field is fed plot-to-plot from an
        upstream field and its caller records that connector itself.

        Research:
            feed joins the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the intake snapped onto a brook within 30 px, else sourced at the sluice
            feed recorded width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: recorded at w 2.5 while it traces the 6.0 ft head race"""
        if source.get("kind") != "cascade":
            hr = net["channels"][0]["pts"]
            fork = hr[-1]
            dd = self.M["meta"].get("down_deg", 90)
            dx, dy = math.cos(math.radians(dd)), math.sin(math.radians(dd))
            din = (fork[0] + dx * 70, fork[1] + dy * 70)
            # ...AND IT MUST LAND INSIDE THE CROP, whatever the field's shape (2026-08-15).
            #
            # `channel_field_anchored` wants this end inside the outline and >= 10 px clear of its
            # edge, "so the field paints over the end". Stepping 70 px downhill from the main
            # channel's last point is a COMB's geometry: a head-race ends at the field's head, so
            # downhill goes into the crop. A POLDER's main is the perimeter ring running ALONG the
            # high edge, so its last point is a corner and the same step skims the boundary - the
            # mouth landed 2.6 px inside on two scripted seeds in three, and no amount of moving the
            # SLUICE changed it, because this end is constructed here rather than taken from the
            # anchor. Fixed by asking the envelope: if the downhill step is already well inside,
            # nothing moves (every comb map is byte-identical); otherwise the end is pulled in along
            # the nearest edge's inward normal until it clears.
            _env_in = net.get("envelope") or []
            # ...and near a CORNER the pull runs again (feature 150 T51): pulled 14 px off the top edge, the
            # polder's mouth stood 9 px from the west edge. Up to three rounds, each on the now-nearest edge;
            # a comb's first round does not fire, so every comb map is still byte-identical.
            for _pull_round in range(3 if len(_env_in) >= 3 else 0):
                _n_in = len(_env_in)
                _din_d = min(seg_dist(din[0], din[1], _env_in[_k], _env_in[(_k + 1) % _n_in]) for _k in range(_n_in))
                if point_in_poly(din[0], din[1], _env_in) and _din_d >= 12.0:
                    break
                _best_in = min(
                    ((seg_closest(din[0], din[1], _env_in[_k], _env_in[(_k + 1) % _n_in]), _env_in[_k], _env_in[(_k + 1) % _n_in]) for _k in range(_n_in)),
                    key=lambda t: math.hypot(t[0][0] - din[0], t[0][1] - din[1]),
                )
                _q_in, _a_in, _b_in = _best_in
                _ex_in, _ey_in = -(_b_in[1] - _a_in[1]), _b_in[0] - _a_in[0]
                _el_in = math.hypot(_ex_in, _ey_in) or 1.0
                _nx_in, _ny_in = _ex_in / _el_in, _ey_in / _el_in
                _cx_in = sum(q[0] for q in _env_in) / _n_in
                _cy_in = sum(q[1] for q in _env_in) / _n_in
                if _nx_in * (_q_in[0] - _cx_in) + _ny_in * (_q_in[1] - _cy_in) > 0:  # point it INWARD
                    (
                        _nx_in,
                        _ny_in,
                    ) = (  # pragma: no cover - the winding-order guard; build_polder winds its envelope so the raw edge normal already points inward [174: KEPT, not deletable - it flips a normal - removing it changes geometry, not just a skip]
                        -_nx_in,
                        -_ny_in,
                    )
                din = (_q_in[0] + _nx_in * 14.0, _q_in[1] + _ny_in * 14.0)
            start = pond_rec if pond_rec else (sluice[0], sluice[1])
            frm = {"kind": "pond"} if pond_rec else {"kind": "stream"}
            _fdd = math.radians(float(net["down_deg"]) if net.get("down_deg") is not None else float(dd))
            _feed_fall = (math.cos(_fdd), math.sin(_fdd))  # the field's own fall, as the channel rule reads it (its record's `down_deg`)
            if not pond_rec:
                # snap the intake's START onto the nearest stream centerline (within the 30px anchor
                # band): an offtake JOINS its stream at a confluence like any junction - the symmetric
                # case of the drain-culvert rule (channels_join_streams_at_confluence) - rather than
                # beginning in the grass beside it. A comb fed by its OWN feeder brook ending AT the
                # sluice is already joined (distance ~0) and is left alone.
                nearest: Any = None
                for st_ in self.M.get("streams", []):
                    sp_ = st_["poly"]
                    for si_ in range(len(sp_) - 1):
                        fq = seg_closest(start[0], start[1], sp_[si_], sp_[si_ + 1])
                        dq = math.hypot(start[0] - fq[0], start[1] - fq[1])
                        if nearest is None or dq < nearest[0]:
                            nearest = (dq, fq)
                # ...ONLY WHERE THE FEED STILL RUNS DOWNHILL FROM IT (feature 287, water:W10): the record runs from `start` to the
                # fork, so a snap that left its net travel level or uphill is not taken and the feed keeps the sluice
                if nearest and 0.5 < nearest[0] <= 30 and runs_downhill([nearest[1], fork], _feed_fall):
                    start = nearest[1]
                # ...AND IT DECLARES A STREAM ONLY WHERE IT REACHES ONE (feature 287, labels L16): beyond the anchor band
                # the intake is not snapped, so its mouth stood in the grass while the record said it joined the brook.
                # Such a feed is sourced from the sluice itself, and says so.
                if not any(channel_end_on_stream(start, st_["poly"]) for st_ in self.M.get("streams", []) if len(st_.get("poly") or ()) >= 2):
                    frm = {"kind": "sluice"}
            vx, vy = din[0] - start[0], din[1] - start[1]
            vl = math.hypot(vx, vy) or 1.0
            midx, midy = (start[0] + din[0]) / 2 - vy / vl * 20, (start[1] + din[1]) / 2 + vx / vl * 20
            # THE RING HEAD IS TOUCHED, not merely passed near (2026-08-15).
            #
            # `watercourse_ends_reach_water` lets a main/drain end outside the crop stand only if it
            # JOINS another watercourse, within ~12 px. On a comb that is free: the sluice IS the
            # head-race's end, so this channel starts on it. On a POLDER the ring canal's end is a
            # corner of the block and the reservoir sits uphill of it, so the run passes NEAR the
            # head - measured 17.6 px - and the ring's end reads as dangling. The bow is what does
            # it: the polyline kinks 20 px off the chord at its midpoint, and the head lies ON the
            # chord, so the drawn line bends away from exactly the point it needs to meet.
            #
            # Straightening the bow is not available - `channel_winds_gently` requires 5-50 px of
            # deviation, and a dead-straight cut fails it. So the head is INSERTED as a vertex when
            # the drawn run does not already reach it. On every comb map the run starts on the head,
            # the distance is ~0, and nothing is inserted: the pool is byte-identical.
            _ch_poly = [[round(start[0], 1), round(start[1], 1)], [round(midx, 1), round(midy, 1)], [round(din[0], 1), round(din[1], 1)]]
            if not pond_rec:
                # THE RECORD TRACES THE HEAD RACE THAT IS DRAWN (settlement-review, feature 230 pass 10). Before the brook was
                # tapped this bowed line WAS the drawn feed; since the head race is carved at its offtake angle (`hr`, the
                # net's own first channel) the bow traced a course 50 px from any ink, and the site boundary kept houses off
                # water that was not there. Sluice, the race's own vertices to the fork, then the step into the field that
                # anchors the topology.
                _ch_poly = [[round(start[0], 1), round(start[1], 1)], *[[round(float(q[0]), 1), round(float(q[1]), 1)] for q in hr[1:]]]
                # ...and it ENDS AT THE FORK, where the drawn race ends. An extra step into the field was kept to anchor the topology,
                # and it was a record of water that is not there - a 70 ft tail past the ink on the reference hamlet and Sawada
                # (pass 11); nothing reads the channel's field end as more than the field it names.
            else:
                # THE POND'S FEED TRACES ITS DRAWN STUB TOO (feature 294 B1, record against ink). The bowed line above was the
                # polder's record while the drawn inlet is the feeder's stub, run onto the reservoir's rim (`inlet_to_rim`): on
                # Kuwabata the record jogged 20 ft west of the stub for 101 ft (the record-against-ink class the reviews caught
                # five times). The pond's center, then the stub from the rim back down to the first point inside the crop - the
                # ring's corner - where the drawn feed meets the field.
                _ch_poly = [[round(start[0], 1), round(start[1], 1)], *[[round(float(q[0]), 1), round(float(q[1]), 1)] for q in reversed(feed_stub(hr, _env_in))]]
            # THE RING HEAD IS TOUCHED BY CONSTRUCTION NOW (feature 294 B1). The head used to be INSERTED as a vertex when a
            # polder's bowed record passed near the ring's corner without meeting it (2026-08-15, feature 150 T51: `join_head`,
            # passed by the polder path alone). Both records now trace what is drawn - the race to its fork, the pond's stub to
            # the ring's corner (`feed_stub`) - so the record ends on the head and the insertion never fired on the pool or the
            # gate's cohort rolls; it was removed rather than kept as a repair with nothing to repair.
            # THE FEED RUNS DOWNHILL OR IS NOT RECORDED (feature 287, water:W10): from the sluice the race leaves at the offtake
            # angle (35 degrees off the fall, so its net travel runs 0.82 of its length down it) and a polder's reservoir
            # stands above the block's high corner, so by construction it always does; a feed that climbs is refused by
            # name here, never recorded as water running uphill
            if not runs_downhill(_ch_poly, _feed_fall):
                raise ValueError(f"{name}: the feed from its {frm['kind']} to the field runs level or uphill ({_ch_poly[0]} -> {_ch_poly[-1]})")
            # ...AND IT NAMES THE FIELD IT FEEDS (feature 287, water W53): it traces the head race, and a field's own water may
            # lie along its own resting basin (`_MATRIX_SAME_PARENT_OK`); a stranger's may not. Asked before it is recorded.
            _feed = {"poly": _ch_poly, "frm": frm, "to": {"kind": "field", "name": name}, "w": 2.5, "field": name}
            refuse_unadmitted(self.M, "channels", _feed)
            self.M["channels"].append(_feed)

    def _draw_furrows(self: Settlement, poly: Any, color: str, theta: float, cls: str | None = None) -> None:  # type: ignore[misc]
        """Stylised ridge/furrow lines within a dry-field plot (dry crops are row-cultivated).

        Research:
            furrowed rows - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: every dry plot drawn in ridged rows
            furrow spacing - GUESS: 5 px between rows
            furrow ink - CONVENTION: 0.8 stroke at 0.8 opacity"""
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        dx, dy = math.cos(theta), math.sin(theta)
        nx, ny = -dy, dx
        # THE ROWS ARE CUT TO THE PLOT AT WRITE TIME (feature 225 FR-004): each row is a line at `theta` and the plot a
        # convex quadrilateral, so the row's ends are its two crossings of the plot's edges (`line_cuts`) and the
        # `<clipPath>` the rows sat in - a layer per plot in resvg, 29 on Inashiro, a quarter tile 0.74 -> 0.44 s
        # without them (specs/225 research R1) - is not needed; a plot a row meets other than twice keeps the clip.
        rows: list[tuple[float, float, float, float]] = []
        ts = -diag / 2
        clip = False
        while ts <= diag / 2:
            mx, my = cx + nx * ts, cy + ny * ts
            cut = line_cuts(poly, mx, my, dx, dy)
            if cut is None:
                clip = True
                break
            rows += [(mx + dx * t0, my + dy * t0, mx + dx * t1, my + dy * t1) for t0, t1 in cut]
            ts += 5
        if clip:
            cid = self._cid("dry")
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
            g = [f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>', f'<g clip-path="url(#{cid})">']
            t = -diag / 2
            while t <= diag / 2:
                mx, my = cx + nx * t, cy + ny * t
                g.append(
                    f'<line x1="{mx - dx * diag / 2:.1f}" y1="{my - dy * diag / 2:.1f}" x2="{mx + dx * diag / 2:.1f}" y2="{my + dy * diag / 2:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>'
                )
                t += 5
            g.append("</g>")
            self.add("".join(g), cls=cls)
            return
        self.add("".join(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>' for ax, ay, bx, by in rows), cls=cls)
