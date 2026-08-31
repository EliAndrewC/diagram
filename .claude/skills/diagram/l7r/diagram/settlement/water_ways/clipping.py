"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any, cast

from .._geom import (
    Pt,
    fillet_polyline,
)

if TYPE_CHECKING:
    from ..core import Settlement


class WaterClipMixin:
    def _clip_to_pond(self: Settlement, pts: Any) -> Any:  # type: ignore[misc]
        """Snap a channel's leading endpoint ONTO the pond rim - trim a run that lies inside the pond, or
        extend one that sits just outside (the sluice foot) - so its bed straddles the rim and COVERS it at
        the mouth: a clean JOIN, without the channel drawing a colored line across the open water. No-op
        when there is no pond. (The rim renders in the water EDGE layer, below every bed, so the covering
        works.)"""
        p = self.M.get("pond")
        if not p:
            return pts
        ex, ey, erx, ery = p

        def rad(q: Pt) -> float:
            return cast(float, ((q[0] - ex) / erx) ** 2 + ((q[1] - ey) / ery) ** 2)  # <1 inside, 1 on the rim, >1 outside

        def rim(inside_pt: Pt, outside_pt: Pt) -> Pt:  # the rad==1 crossing on the segment
            lo, hi = 0.0, 1.0
            for _ in range(24):
                m = (lo + hi) / 2
                q = (inside_pt[0] + (outside_pt[0] - inside_pt[0]) * m, inside_pt[1] + (outside_pt[1] - inside_pt[1]) * m)
                lo, hi = (m, hi) if rad(q) < 1.0 else (lo, m)
            return (inside_pt[0] + (outside_pt[0] - inside_pt[0]) * hi, inside_pt[1] + (outside_pt[1] - inside_pt[1]) * hi)

        def snap_front(seq: Any) -> list[Any]:  # snap a leading endpoint that connects to the pond onto the rim
            out = list(seq)
            if rad(out[0]) < 1.0:  # inside: drop the run inside the pond, start AT the rim
                i = 0
                while i + 1 < len(out) and rad(out[i + 1]) < 1.0:
                    i += 1
                if i + 1 < len(out):
                    out = [rim(out[i], out[i + 1])] + out[i + 1 :]
            elif rad(out[0]) < 1.35:  # just outside (the sluice foot): prepend the rim point
                out = [rim((ex, ey), out[0])] + out
            return out

        out = snap_front(pts)  # a comb channel meets the pond at its head (leading end)...
        out = snap_front(out[::-1])[::-1]  # ...a feeder brook meets it at its mouth (trailing end): clip both
        return out

    def _clip_to_moat(self: Settlement, pts: Any, capr: float = 0.0) -> Any:  # type: ignore[misc]
        """Snap a channel endpoint that meets the MOAT onto the moat bed's edge - trim any run that
        lies within the bed, restarting the channel at the bed's rim with a ~3px inset so its mouth
        covers the rim stroke - the same clean JOIN `_clip_to_pond` gives a pond-fed channel, so a
        moat tap (or a drain emptying into the moat) never draws its bed as a colored line across
        the open moat water. `capr` is the stroke's CAP RADIUS (half the drawn width): the round
        linecap inks that far PAST the endpoint, so the inset must back off by it - without this a
        7px tap's mouth plunged to ~4px of the moat centerline and read as a foreign line crossing
        half the band (GM 2026-07-23, Tango). No-op when there is no moat."""
        moat = self.M.get("moat")
        if not moat or len(pts) < 2:
            return pts
        hw = self.M.get("moat_width", 22) / 2

        def foot(q: Pt) -> tuple[Any, Any]:
            best: Any = None
            bd: Any = None
            for i in range(len(moat) - 1):
                ax, ay = moat[i]
                bx, by = moat[i + 1]
                vx, vy = bx - ax, by - ay
                ll = vx * vx + vy * vy or 1.0
                t = max(0.0, min(1.0, ((q[0] - ax) * vx + (q[1] - ay) * vy) / ll))
                fx, fy = ax + vx * t, ay + vy * t
                d = math.hypot(q[0] - fx, q[1] - fy)
                if bd is None or d < bd:
                    bd, best = d, (fx, fy)
            return best, bd

        def snap_front(seq: Any) -> list[Any]:
            out = list(seq)
            if foot(out[0])[1] >= hw:
                return out  # the end is clear of the bed - nothing to snap
            i = 0  # drop any leading run inside the bed
            while i + 1 < len(out) and foot(out[i + 1])[1] < hw:
                i += 1
            if i + 1 >= len(out):
                return out  # the whole channel lies in the moat - leave it
            f, _d = foot(out[i])
            nxt = out[i + 1]
            ux, uy = nxt[0] - f[0], nxt[1] - f[1]
            ul = math.hypot(ux, uy) or 1.0
            return [(f[0] + ux / ul * (hw - 3 + capr), f[1] + uy / ul * (hw - 3 + capr))] + out[i + 1 :]

        out = snap_front(pts)
        out = snap_front(out[::-1])[::-1]
        return out

    def _clip_to_river(self: Settlement, pts: Any, capr: float = 0.0) -> Any:  # type: ignore[misc]
        """Snap a channel endpoint that meets the RIVER onto the river bed's edge - the same clean
        confluence `_clip_to_moat` gives a moat tap (added 2026-07-23 with the mouths-not-crossings
        rule: Nagahara's fne1 tap started ON the Hayakawa centerline and drew across the half-band).
        No-op when there is no river."""
        rv = self.M.get("river")
        if not rv or not rv.get("pts") or len(pts) < 2:
            return pts
        rp = rv["pts"]
        hw = rv.get("w", 40) / 2

        def foot(q: Pt) -> tuple[Any, Any]:
            best: Any = None
            bd: Any = None
            for i in range(len(rp) - 1):
                ax, ay = rp[i]
                bx, by = rp[i + 1]
                vx, vy = bx - ax, by - ay
                ll = vx * vx + vy * vy or 1.0
                t = max(0.0, min(1.0, ((q[0] - ax) * vx + (q[1] - ay) * vy) / ll))
                fx, fy = ax + vx * t, ay + vy * t
                d = math.hypot(q[0] - fx, q[1] - fy)
                if bd is None or d < bd:
                    bd, best = d, (fx, fy)
            return best, bd

        def snap_front(seq: Any) -> list[Any]:
            out = list(seq)
            if foot(out[0])[1] >= hw:
                return out
            i = 0
            while i + 1 < len(out) and foot(out[i + 1])[1] < hw:
                i += 1
            if i + 1 >= len(out):
                return out  # pragma: no cover - defensive: a tap never lies wholly in the river
            f, _d = foot(out[i])
            nxt = out[i + 1]
            ux, uy = nxt[0] - f[0], nxt[1] - f[1]
            ul = math.hypot(ux, uy) or 1.0
            return [(f[0] + ux / ul * (hw - 3 + capr), f[1] + uy / ul * (hw - 3 + capr))] + out[i + 1 :]

        out = snap_front(pts)
        out = snap_front(out[::-1])[::-1]
        return out

    def _clip_to_stream(self: Settlement, pts: Any, capr: float = 0.0) -> Any:  # type: ignore[misc]
        """Snap a channel endpoint that reaches INTO a stream bed onto the bed's edge (~2px inside
        the bank, so the mouth covers the bank stroke) - the same clean CONFLUENCE `_clip_to_pond`
        and `_clip_to_moat` give: a drain culvert JOINS the receiving stream without drawing its own
        bed as a colored tongue across the current. Trim-only: an end short of the bank is left
        alone (the `channels_join_streams_at_confluence` check requires the RECORDED polyline to
        reach the bed, so the gen extends the record to the centerline and this trims the DRAWING).

        `capr` IS THE CAP RADIUS, and it was missing here while both siblings had it (settlement-review
        2026-08-29, on Sawada's brook mouth and head intake and again on Kashikawa's head join). A round
        stroke cap bulges half the stroke's width PAST its endpoint, so a channel trimmed exactly to the
        bank still printed a rounded plug of its own bed colour inside the receiving stream - a bead across
        the joint, which is the opposite of the GM's "water just flows". `_clip_to_moat` and `_clip_to_river`
        have pulled their endpoints back by `capr` since they were written; a stream confluence simply never
        got the argument, and the caller passed it to those two and not to this one."""
        streams = self.M.get("streams", [])
        if not streams or len(pts) < 2:
            return pts

        def foot(q: Pt) -> tuple[Any, float, float]:
            best: Any = None
            bd, bhw = 1e9, 4.5
            for st in streams:
                sp = st["poly"]
                hw = st.get("w", 9) / 2
                for i in range(len(sp) - 1):
                    ax, ay = sp[i]
                    bx, by = sp[i + 1]
                    vx, vy = bx - ax, by - ay
                    ll = vx * vx + vy * vy or 1.0
                    t = max(0.0, min(1.0, ((q[0] - ax) * vx + (q[1] - ay) * vy) / ll))
                    fx, fy = ax + vx * t, ay + vy * t
                    d = math.hypot(q[0] - fx, q[1] - fy)
                    if d < bd:
                        bd, best, bhw = d, (fx, fy), hw
            return best, bd, bhw

        def snap_front(seq: Any) -> list[Any]:
            out = list(seq)
            f0, d0, hw0 = foot(out[0])
            if f0 is None or d0 >= hw0 - 2:
                return out  # the end is clear of the bed (or right at its edge) - nothing to trim
            i = 0  # drop any leading run inside the bed
            while i + 1 < len(out):
                _fn, dn, hwn = foot(out[i + 1])
                if dn >= hwn - 2:
                    break
                i += 1
            if i + 1 >= len(out):
                return out  # the whole channel lies in the stream - leave it
            f, _d, hw = foot(out[i])
            nxt = out[i + 1]
            ux, uy = nxt[0] - f[0], nxt[1] - f[1]
            ul = math.hypot(ux, uy) or 1.0
            return [(f[0] + ux / ul * (hw - 2 + capr), f[1] + uy / ul * (hw - 2 + capr))] + out[i + 1 :]

        out = snap_front(pts)
        out = snap_front(out[::-1])[::-1]
        return out

    @staticmethod
    def _pond_anchored(frm: Any, to: Any) -> bool:
        """True if a watercourse connects TO the pond at either end (frm/to kind == 'pond') - the cue to snap
        that end onto the rim so it JOINS the open water instead of drawing its bed/sheen across it."""
        return any(a and a.get("kind") == "pond" for a in (frm, to))

    def field_channel(self: Settlement, pts: Any, col: str, w0: float, w1: float, late: bool = False) -> None:  # type: ignore[misc]
        """Draw a comb-net irrigation channel (from the waterfields engine) THROUGH the water block, so it
        JOINS the pond + the other channels cleanly: its bed sits in the shared bed group (composited as one
        confluence, no dark seam), OVER the pond's rim edge (so its bed covers the rim where it meets the
        pond -> a clean gap, not the rim cutting across). `col` is the bed color (supply vs drain); the width
        tapers `w0 -> w1` along the run (split into pieces). The sluice end is snapped onto the rim by
        `_clip_to_pond`, and an end meeting the MOAT is snapped onto the moat bed's edge by
        `_clip_to_moat` (the same clean-mouth join, for a moated city's taps and drain culverts).
        An end reaching into a STREAM bed is snapped onto that bed's edge by `_clip_to_stream`
        (the confluence mouth for a drain culvert emptying into a stream).
        The field_ditches are recorded separately (gen-side) for the topology checks; the DRAWN
        stroke - post-clip geometry, STROKE WIDTHS, bed draw position, late flag - is recorded in
        M['drawn_channels'] so pond_fill_covers_channel_mouths can verify the pond fill paints over
        every joining mouth (and finish() can see whether a LATE stroke joins the pond and relocate
        the fill). The widths ride along because water_channels_join_not_cross judges a junction by
        whether the joining stroke's tip lands inside the OTHER stroke's drawn band - which needs
        that band's width, and needs it from the post-clip record rather than the pre-clip
        field_ditches/channels (the two diverge wherever a mouth was snapped onto open water)."""
        pts = self._clip_to_stream(self._clip_to_river(self._clip_to_moat(self._clip_to_pond(pts), capr=max(w0, w1) / 2), capr=max(w0, w1) / 2), capr=max(w0, w1) / 2)
        # ROUND THE BENDS: an earthen ditch turns on a swept curve, never a mitred corner (see
        # fillet_polyline for the why and the ~2.5-widths radius). Applied AFTER the mouth clips so a
        # snapped pond/moat/stream junction keeps its exact endpoint, and the DRAWN geometry recorded
        # below is the filleted line, which is what the mouth-cover and join checks measure.
        pts = fillet_polyline(pts, 2.5 * max(w0, w1))
        rec: dict[str, Any] = {"pts": [[round(x, 1), round(y, 1)] for x, y in pts], "late": late, "w0": round(w0, 2), "w1": round(w1, 2)}
        self.M.setdefault("drawn_channels", []).append(rec)  # ONE rec per call: flush writes bedz per piece, so the last (topmost) piece's z sticks
        if abs(w1 - w0) < 0.2:
            dd = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            self._water(f'<path d="{dd}" fill="none" stroke="{col}" stroke-width="{w0:.1f}" stroke-linejoin="round" stroke-linecap="round"/>', rec, late=late, cls="field ditch")
            return
        from l7r.diagram.waterfields import taper_pieces  # local: the engine packages are peers, imported lazily

        # One piece per SEGMENT, each at its arc-correct width - `taper_pieces` owns both halves of
        # that (the sqrt law, and arc-length rather than vertex-index parameterization) and is shared
        # with `_watercourse_segs`, so the drawn stroke and the corridor protecting it cannot drift.
        for piece, wk in taper_pieces(pts, w0, w1):
            dd = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in piece)
            self._water(f'<path d="{dd}" fill="none" stroke="{col}" stroke-width="{wk:.1f}" stroke-linejoin="round" stroke-linecap="round"/>', rec, late=late, cls="field ditch")
