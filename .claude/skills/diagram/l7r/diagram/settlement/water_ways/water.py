"""Split from settlement/water_ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import (
    winding,
)

if TYPE_CHECKING:
    from ..core import Settlement


class WaterBodiesMixin:
    def _flow_record(self: Settlement, rec: dict[str, Any], pts: Any, flow: str) -> None:  # type: ignore[misc]
        """Tag one watercourse record with its flow direction and the derived downstream bearing.

        `flow_deg` is the bearing of the NET upstream->downstream vector, in the map's angle
        convention (the same one `down_deg` uses: 0 = east, 90 = south, y-down screen space). The
        net vector, not the last segment, because a winding stream's local heading says nothing
        about where its water is going - and every rule that cares ("is the tannery downstream of
        the town?") is about the net journey."""
        if flow not in ("forward", "reverse", "level"):
            raise ValueError(f"watercourse flow must be 'forward', 'reverse' or 'level', got {flow!r}")
        if flow == "level":
            # A NAVIGABLE cut (the cargo canal) is not a drainage course and gets NO bearing. It is
            # dug at the level of the water it joins - which is exactly what lets barges pole both
            # ways along it - so its gradient is nil, the water gate's sluice holds it at river
            # level, and a dead-end dock basin has no through-flow at all. Claiming a downstream
            # direction for it would be a fiction, so it declares "level" instead and the
            # drainage-bearing check skips it.
            rec["flow"] = flow
            rec["flow_deg"] = None
            return
        p = [(float(x), float(y)) for x, y in pts]
        ux, uy = (p[0], p[-1]) if flow == "forward" else (p[-1], p[0])
        vx, vy = ux[0] - uy[0], ux[1] - uy[1]
        rec["flow"] = flow
        # upstream -> downstream is (downstream - upstream); we built (upstream - downstream) above
        rec["flow_deg"] = round(math.degrees(math.atan2(-vy, -vx)) % 360, 1)

    def stream(self: Settlement, pts: Any, frm: Any = None, to: Any = None, width: float = 9, flow: str = "forward", cls: str = "stream") -> None:  # type: ignore[misc]
        """A natural watercourse. If frm/to anchors are given (e.g. a forest brook
        feeding a pond), it is recorded and the gate checks it actually connects
        them - just like an irrigation channel. `width` is the water's drawn width
        (a stream FEEDING A MOAT should be as wide as the moat, by conservation of flow).

        FLOW DIRECTION (GM 2026-07-24). Every watercourse declares which way the water runs,
        because "downstream" is a real constraint on siting - tanneries, dyers' rinse water,
        the burakumin quarter, the moat's flushing current - and it was previously carried only
        in gen docstrings, where no check could read it. CANONICAL CONVENTION: `pts` is authored
        UPSTREAM-FIRST, so poly[0] is the source end. This formalizes the convention s.moat's
        `river=` already relied on. `flow="reverse"` marks a polyline stored the other way round
        (reversing point order renders identically, so the tag is for the rare case where the
        drawing code wants the other order). The derived bearing is recorded as `flow_deg`, so
        checks read ONE number rather than re-deriving direction from anchor semantics."""
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        # always recorded so the gate can check it (anchors optional - only some streams connect things)
        rec = {"poly": [[x, y] for x, y in pts], "frm": frm, "to": to, "w": width}
        self._flow_record(rec, pts, flow)
        self.M["streams"].append(rec)
        bed_t = f'<path d="{{dd}}" fill="none" stroke="#9CB4C8" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'
        # lighter mid-current highlight (NOT a dashed lane line - this is water, not a road)
        # THE SHEEN IS BUTT-CAPPED (settlement-review 2026-08-29, Mizuguchi error 2 and Kashikawa's bead).
        # A sheen is the highlight ALONG a course, not the course itself, and a round cap makes it bulge
        # half its own width past the end of its own bed. Since feature 150 T53 put every watercourse in
        # ONE block, every sheen draws above every bed, so that bulge prints INSIDE whatever the course
        # runs into: at Mizuguchi's intake - the join the hamlet is named for - it printed a pale blob on
        # the head-race, measured in the PNG. Measured across the pool, a stream sheen lies under a later
        # bed for 0.1 to 4.3 ft per map: cap-sized at joins, never a long run, which is why the cap is the
        # fix and the block order is not. A butt cap ends the highlight where its bed ends.
        sheen_t = f'<path d="{{dd}}" fill="none" stroke="#B6CAD8" stroke-width="{max(2, width * 0.35):.0f}" stroke-linejoin="round" stroke-linecap="butt"/>'
        clip = {"pts": [(x, y) for x, y in pts], "bed_t": bed_t, "sheen_t": sheen_t} if self._pond_anchored(frm, to) else None
        self._water(  # opacity comes from the shared bed/sheen groups, so crossings don't stack into a dark seam
            bed_t.format(dd=dd), rec, sheen=sheen_t.format(dd=dd), clip=clip, cls=cls
        )
        self.corridors.append(([(x, y) for x, y in pts], max(30, width / 2 + 20)))  # no-build: keep houses off the stream

    def river(self: Settlement, pts: Any, width: float | None = None, flow: str = "forward") -> float:  # type: ignore[misc]
        """A RIVER - the trunk waterway a river-bank city sits on (most provincial cities do;
        the moat taps it upstream and returns downstream, and the river itself serves as the
        water defense on its flank - Xiangyang/Pingyao/Okayama pattern, see settlements.md).
        Drawn as a wide stream (off-map to off-map) and recorded in M['river'] so the checks
        that compare watercourse weights know this one legitimately outweighs the dug moat."""
        if width is None:
            width = self.px(120)  # a serious provincial river ~120 ft across
        self.stream(pts, frm={"kind": "offmap"}, to={"kind": "offmap"}, width=width, flow=flow)
        self.M["river"] = {"pts": [[x, y] for x, y in pts], "w": width}
        self._flow_record(self.M["river"], pts, flow)  # the trunk river's own record carries it too
        return width

    def channel(self: Settlement, start: Any, end: Any, frm: Any, to: Any, amp: float = 15, width: float = 2.5, pts: Any = None) -> None:  # type: ignore[misc]
        """frm/to are anchor dicts: {'kind':'pond'|'offmap'|'field','name':...}. `width` is the drawn
        bed: a field-level irrigation ditch is the THINNEST line on the map (in reality ~0.3 m, ~1/300
        of the 1-cho paddy it feeds), so it sits at the legibility floor (~2.5 px) - a hairline, clearly
        finer than any natural watercourse. See the water-width ladder in settlements.md historical
        grounding. `pts` (optional): an explicit polyline used verbatim instead of the auto-winding -
        for culverts routed by hand (a drain outfall reaching its stream confluence, a field-to-field
        cascade connector) whose waypoints are load-bearing; drawing through THIS method (not a flat
        field_channel stroke) is what puts the bed in the shared water group at the standard bed hue,
        so the mouth merges into the receiving stream like any confluence (GM, Hirameki 2026-07)."""
        poly = [(p[0], p[1]) for p in pts] if pts else winding(start, end, amp=amp)
        dd = 'M' + ' L'.join(f'{x},{y}' for x, y in poly)
        rec = {"poly": [[x, y] for x, y in poly], "frm": frm, "to": to, "w": width}
        self.M["channels"].append(rec)
        bed_t = f'<path d="{{dd}}" fill="none" stroke="#9CB4C8" stroke-width="{width}"/>'  # a channel is a thin bed, no sheen
        clip = {"pts": [(x, y) for x, y in poly], "bed_t": bed_t, "sheen_t": None} if self._pond_anchored(frm, to) else None
        self._water(bed_t.format(dd=dd), rec, clip=clip, cls="field ditch")
        # 33 px keeps even a plain farmhouse's FOOTPRINT (half-diagonal ~26) clear of the
        # channel, not just its center - 22 left corners clipping the channel (see
        # no_structure_on_channel). Matches the stream corridor's footprint-aware spacing.
        self.corridors.append((poly, 33))
