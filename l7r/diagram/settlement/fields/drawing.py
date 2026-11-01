"""The field's DRAWING functions, moved unchanged from the old field modules (feature 444 T16, the round arbiter's ruling on
ask:444-T16-move-drawing, route (a)): each paints records the Rust stage returns and places nothing - the comb's floor, its beads,
a dry plot's furrows, the pond glyph and a feature's ink. `ink.py` and the free modules (the sink's tameike, the row village's
furrows) draw through them.

Research:
    the field's drawing - NONE: drawing; each record's claims are at the Rust that places it
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.overlap.registry import refuse_unadmitted

from .landuse import line_cuts

if TYPE_CHECKING:
    from ..core import Settlement


class FieldDrawingMixin:
    def comb_base_fill(self: Settlement, net: dict[str, Any], name: str, color: str = "", full_envelope: bool = False) -> None:  # type: ignore[misc]
        """Draw a FIELD FLOOR under a comb net's plots and record it (M['comb_floors'][name]),
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

    def _comb_draw_beads(self: Settlement, net: dict[str, Any]) -> None:  # type: ignore[misc]
        """Draw what survived `_comb_drop_drowned_beads` - the ink, after the record it agrees with.

        Research: bead glyph - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a round bead about 3 ft across (`ink.BEAD_R_FT`), BEAN_GREEN at 0.85"""
        from l7r.diagram.waterfields import BEAN_GREEN

        from .ink import BEAD_R_FT

        beads = "".join(f'<circle cx="{x}" cy="{y}" r="{self.px(BEAD_R_FT):.2f}" fill="{BEAN_GREEN}"/>' for x, y in net["bund_beans"])
        z = self.add(f'<g opacity="0.85">{beads}</g>', cls="bund beans")
        # THE SLOT IS KEPT ON THE SETTLEMENT (`_bead_slots`), so a re-roll's deep copy of it carries its beads' slots with it
        self._bead_slots.append((z, net["bund_bean_runs"], self.M["fields"][-1] if self.M.get("fields") else None, list(net.get("bead_ponds") or [])))

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

    def pond(self: Settlement, cx: float, cy: float, rx: float, ry: float, stream_curve: Any = None) -> None:  # type: ignore[misc]
        """A pond / irrigation reservoir. Routed through the WATER block (not drawn inline) so a stream or
        channel MEETING it JOINS at the rim instead of the rim cutting across its mouth: the RIM is an EDGE
        below every water bed (a feeder's bed covers it at the junction -> a clean gap), the FILL joins the
        shared bed group as the TOPMOST bed (`pond_fill=True`) - so it paints OVER any feeder's inside-the-rim
        overshoot (an irrigation channel's round end-cap bulging past the rim, whichever order it was drawn),
        while the shore rim still shows and the mouths stay clean; the inner highlight is a sheen.

        ASKED BEFORE ANYTHING IS DRAWN (feature 287, water W53): its placer has walked its alternatives (the sink's pond
        falls back to an off-map run, `hamletgen/sink.py`), so a pond the matrix still forbids is refused by name here.

        Research:
            pond glyph - CONVENTION: blue fill, a dark rim and an inner sheen
            pond feeder width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: about 3 ft at the map's scale, twice the 1.5 ft floor
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 12 and 10 (the inner sheen's inset across and down), 2.4 (the rim)
        """
        refuse_unadmitted(self.M, "pond", [cx, cy, rx, ry])
        if stream_curve:
            # the pond's feeder runs at the lateral/ditch tier - a thin line near the channel weight,
            # NOT the heftier natural-stream weight (see the water-width ladder in research/contents.json#water).
            self._water(
                f'<path d="{stream_curve}" fill="none" stroke="#9CB4C8" stroke-width="{self.px(3.0):.1f}"/>', {}, cls="irrigation ditch"
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

    def _field_feature_ink(self: Settlement, ink: list[tuple[str, str]] | None, svg: str, cls: str) -> None:  # type: ignore[misc]
        """Emit one in-field feature's ink now, or hold it in `ink` for the caller to emit later: `draw_comb_field` seats
        the features BEFORE the paddies are drawn (a grave carves the rings the paddies are drawn from, water W28) and
        draws their ink after the paddies, where it always was."""
        if ink is None:
            self.add(svg, cls=cls)
        else:
            ink.append((svg, cls))
