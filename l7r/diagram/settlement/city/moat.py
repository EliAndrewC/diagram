"""The wet defense and every opening through it - water gates, sluices, the inwall drain.

Split from settlement/city.py by feature 113 - see settlement/city/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any

from l7r.diagram.overlap.registry import refuse_unadmitted

from .._geom import (
    Pt,
    seg_dist,
)

if TYPE_CHECKING:
    from ..core import Settlement


class MoatMixin:
    def sluice_gate(self: Settlement, x: float, y: float, rot: float = 0.0, label: str | None = None, label_xy: Pt | None = None, span: float | None = None) -> int:  # type: ignore[misc]
        """A field-channel SLUICE GATE (the intake/outfall control board the comb doctrine's "sluice-fed
        head-race" always implied but no map drew - GM 2026-07-23, the mouths-are-confluences pass): two
        timber posts flanking the channel and a lifted board between them. Drawn wherever a channel
        CHANGES WATER - a moat/river tap handing off to the comb's own canal (the palette seam sits
        exactly here, and the gate is what makes it read as engineered rather than two strokes crossing)
        or a field drain handing off to its outfall culvert. `rot` degrees turns the board ACROSS the
        channel (pass the channel's heading + 90). The span is true - 20 ft where none is given, a ~16-24 ft timber intake
        structure with wing posts at the village/city grains. Top layer, above the water. Records
        M['sluice_gates'] for `channel_gates_at_water_junctions`, asked of the registry of what stands before anything is drawn
        (feature 287, water W53): its seat is the junction its caller found, so a gate the matrix forbids there - a fixture is
        mounted on water alone - is refused by name.

        Research:
            a sluice where a channel changes water - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html
            board, posts, crossbeam and windlass - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html
            frame span - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: the drawing page's GUESS, a field sluice about 16 to 24 ft - 20 ft at the map's scale where no span is given; a wider channel bank to bank; the span drawn true
            timbers and drum at the glyph floor - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: posts, board and drum at fixed pixel thicknesses, larger than life (CONVENTION)
            caption - CONVENTION: 9 pt italic
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 10.8 (glyph normalizer (span is 0179's 20 ft)); 9.2 (board inside the span); 4.4 (crossbeam); 13 (label offset); 4.6 (board inside the span); 5.4 (label reference box); 4.2 (label reference box)
        """
        span = self.px(20.0) if span is None else span  # a field sluice about 16 to 24 ft (0179): 20 ft at the map's scale
        rec: dict[str, float] = {"x": round(x, 1), "y": round(y, 1), "rot": round(rot, 1), "span": round(span, 1)}  # the matrix sizes the gate's box from its span
        refuse_unadmitted(self.M, "sluice_gates", rec)
        wc = '#3A352C'
        # `span` stretches the frame ACROSS its channel so the posts stand on the BANKS (GM
        # 2026-08-09: on the capital's 66 ft leats the default field-channel frame floated
        # mid-water, reading as detached - a real frame spans abutment to abutment, and the
        # operator walks the crossbeam). With no span given the frame is 20 ft (feature 328: it was a fixed 10.8 px,
        # about 11 ft at a hamlet's scale and 32 ft at a city's), drawn at its span at every scale - no glyph floor widens it
        # (to scale, never inflated).
        _sk = span / 10.8
        g = [f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.1f})">']
        g.append(f'<rect x="{-4.6 * _sk:.1f}" y="-1.4" width="{9.2 * _sk:.1f}" height="2.8" fill="#8A7050" stroke="{wc}" stroke-width="1.0"/>')  # the lifted board
        g.append(f'<rect x="{-5.4 * _sk:.1f}" y="-2.0" width="2.0" height="4.0" fill="{wc}"/>')  # posts, ON the banks when span is given
        g.append(f'<rect x="{5.4 * _sk - 2.0:.1f}" y="-2.0" width="2.0" height="4.0" fill="{wc}"/>')
        # THE LIFTING FRAME (GM 2026-08-09, researched): a hi/suimon board was raised by hand -
        # or by windlass on the larger gates - from a timber crossbeam spanning the posts ABOVE
        # the water, the operator standing on the beam walkway or the bank abutment. The beam
        # and its windlass drum are real above-water structure, drawn at the glyph floor (the
        # wells' vr convention): the crossbeam bridges the posts and the drum sits at its center.
        g.append(f'<line x1="{-4.4 * _sk:.1f}" y1="-3.1" x2="{4.4 * _sk:.1f}" y2="-3.1" stroke="{wc}" stroke-width="1.2"/>')  # the crossbeam walkway
        g.append(f'<rect x="-1.1" y="-4.2" width="2.2" height="2.2" fill="#B0905E" stroke="{wc}" stroke-width="0.8"/>')  # the windlass drum
        g.append('</g>')
        z = self.add_top(''.join(g), cls="sluice gate")  # feature 150: its own highlight class
        self.M.setdefault("sluice_gates", []).append({**rec, "z": z})
        if label:
            # a sluice reads as a bare black bar at fit zoom (GM 2026-08-09) - most of a real
            # gate IS in the water, so the word does the explaining, not the drawing
            lx_, ly_ = label_xy if label_xy else (x, y - 13)
            self.label(lx_, ly_, label, 9, italic=True, color="#3A352C", ref=(x - 5.4 * _sk, y - 4.2, x + 5.4 * _sk, y + 2.0))
        return z

    def inwall_drain_outfall(self: Settlement, drain_pts: Any, moat_bias: Pt = (0.0, 0.0), field_name: str = "") -> list[Pt]:  # type: ignore[misc]
        """A walled city's IN-WALL drain handoff (GM 2026-07-23, generalizing Tango's nw1; gated by
        inwall_drains_gated_at_cutoff): the visible runoff ditch CUTS OFF short of the patrol ring
        road and drops through a SLUICE GATE into an implied underground stone culvert beneath road,
        rampart and moat - never draw a ditch running through the city wall (the water gate itself
        is underground and invisible; the control gate at the drop is the one visible piece of the
        plumbing, and is what tells the reader the water drains into engineered works connected to
        the moat). Takes the drain polyline BEFORE it is drawn, TRIMS its moat-side end back to
        half the ring-road width + 10px clear of the ring-road centerline (the glyph's ~5.4px
        half-span + the check's 4px margin, so the gate itself stays off the road bed), places the
        gate ACROSS the ditch at the cut, and records the undrawn drain->moat conduit (cut point ->
        the moat vertex nearest cut+`moat_bias`, with the standard gentle wind channel_winds_gently
        expects) plus its no-build corridor. Returns the trimmed polyline in the caller's original
        orientation - assign it back BEFORE drawing, so the drawn ditch, the field_ditches record,
        and the conduit all share the same cut geometry (placement and check read the same source).

        Research:
            drain drops through a sluice into a culvert - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: cut short of the patrol road, never through the wall
            cut clearance - NONE: half the road width plus 10 px, the glyph's own margin
            undrawn conduit to the moat - NONE: to the nearest moat vertex, a 12 px wind
            conduit corridor - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 33 px
            its salts, guards and sentinels - NONE: they decide nothing about the place - 20 (ring-road fallback (unit dead)); 24 (bisection count); 2.5 (undrawn conduit width (unit dead))
        """
        ring = self.M.get("ring_road") or []
        moat = self.M.get("moat") or []
        pts: list[Pt] = [(float(p[0]), float(p[1])) for p in drain_pts]
        rev = False
        if moat:

            def moatd(q: Pt) -> float:
                return min(math.hypot(q[0] - p[0], q[1] - p[1]) for p in moat)

            if moatd(pts[0]) < moatd(pts[-1]):  # normalize: the outfall (moat-side) end LAST
                pts, rev = pts[::-1], True
        cl = self.M.get("ring_road_width", 20) / 2 + 10.0
        if ring:

            def ringd(q: Pt) -> float:
                return min(seg_dist(q[0], q[1], ring[i], ring[i + 1]) for i in range(len(ring) - 1))

            i = len(pts) - 1
            while i > 0 and ringd(pts[i]) < cl:
                i -= 1  # walk back off the road's clearance zone
            if ringd(pts[i]) >= cl and i < len(pts) - 1:
                a, b = pts[i], pts[i + 1]  # the clearance crossing lies on this segment - bisect it
                lo, hi = 0.0, 1.0
                for _ in range(24):
                    m = (lo + hi) / 2
                    lo, hi = (m, hi) if ringd((a[0] + (b[0] - a[0]) * m, a[1] + (b[1] - a[1]) * m)) >= cl else (lo, m)
                pts = pts[: i + 1] + [(round(a[0] + (b[0] - a[0]) * lo, 1), round(a[1] + (b[1] - a[1]) * lo, 1))]
            # else: the whole drain hugs the road - leave it untrimmed and let the check flag it
        cut = pts[-1]
        prev = pts[-2] if len(pts) > 1 else cut
        self.sluice_gate(cut[0], cut[1], rot=math.degrees(math.atan2(cut[1] - prev[1], cut[0] - prev[0])) + 90)
        if moat:
            tx, ty = cut[0] + moat_bias[0], cut[1] + moat_bias[1]
            mv = min(moat, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)
            ux, uy = mv[0] - cut[0], mv[1] - cut[1]
            ul = math.hypot(ux, uy) or 1.0
            mid = ((cut[0] + mv[0]) / 2 - 12 * uy / ul, (cut[1] + mv[1]) / 2 + 12 * ux / ul)
            poly = [[round(cut[0], 1), round(cut[1], 1)], [round(mid[0], 1), round(mid[1], 1)], [round(mv[0], 1), round(mv[1], 1)]]
            _frm: dict[str, Any] = {"kind": "drain"}
            if field_name:  # NAME the field so the drain->outfall attribution is exact, not by proximity
                _frm["name"] = field_name
            self.M["channels"].append({"poly": poly, "frm": _frm, "to": {"kind": "moat"}, "w": 2.5, "drawn": False})
            self.corridors.append(([(p[0], p[1]) for p in poly], 33))
        return pts[::-1] if rev else pts
